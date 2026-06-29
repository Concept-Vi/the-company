"""runtime/grants.py — the company-native ACCESS-GRANT store (identity fusion, the GATE-READS-GRANTS organ).

WHAT THIS IS: a company-native store of OWUI's AccessGrant *SHAPE*, NOT a connection to OWUI's DB.
OWUI's `open_webui/models/access_grants.py` is async SQLAlchemy against OWUI's Postgres in a separate
repo/process; the company runtime is sync (FsStore / append-only jsonl / graph_lock). Importing it would
be cross-process async-in-sync and would break the moment OWUI is down — the OPPOSITE of behavior-
preserving. So the harvest is the TABLE SHAPE; the code is ours, native to the company's own store.

THE ROW (verified live against access_grants.py:20-41 — the UNIQUE-constrained shape):
    (resource_type, resource_id, principal_type, principal_id, permission)
  • resource_type  — "tool" covers MCP tools today (OWUI's set: knowledge|model|prompt|tool|note|…).
  • principal_type — the KIND AXIS. OWUI uses "user"|"group"; the type is a free Text column with a
    UNIQUE constraint spanning it, so it EXTENDS BY ADDING VALUES (viewer|agent|group|…) with zero
    migration. (Correction carried from the fusion doc: `*` is a value of principal_ID — public/any —
    NOT of principal_type.)
  • principal_id   — a concrete id, or "*" (wildcard: any principal of that type).
  • permission     — "use" for a tool (read/write in OWUI's resource model).

SEEDED TO CURRENT (the whole point — NOTHING changes yet): the seed reproduces EXACTLY today's
remote.py decision (operator → ALL tools; client → posture=="safe" subset only; none → nothing) as
readable grant rows. The gate becomes able to CONSULT this table; it does not yet OBEY it — see
runtime/grants:tools_for_tier_via_grants + the SHADOW assertion the gate runs. The posture tiers stay
the fail-closed FLOOR; grants are the positive authority on top once the lead flips authority.

  Today's decision, as grants (the seed):
    • operator: a single wildcard grant  (tool, "*", principal_type="viewer", principal_id=OPERATOR,
      permission="use")  — operator sees ALL tools (identity IS the boundary, remote.py:232).
    • client : one grant PER posture-"safe" tool  (tool, <tool_name>, principal_type="viewer",
      principal_id="*", permission="use")  — any valid non-operator user gets the safe subset.
    • none   : no grant → nothing (a no-token request never reaches here; it 401s in _validate_auth).

LEGIBILITY (the naming-collision note, fusion D-2): an "identity role" here is a GRANT/GROUP on a
principal — it is NEVER the company's cognition ROLE (`role://`, roles/*.py = focus/judge/voice, model-
execution units). Zero shared code; do not conflate. (Mirrored in runtime/roles.py's docstring.)
"""
from __future__ import annotations

import os
import json
import time
import uuid

import fabric.config as _fcfg

# principal-type axis (extends OWUI's user|group with the company's identity kinds).
PT_VIEWER = "viewer"
PT_AGENT = "agent"
PT_GROUP = "group"
PRINCIPAL_TYPES = (PT_VIEWER, PT_AGENT, PT_GROUP)
WILDCARD = "*"                       # a principal_ID value (public/any), NEVER a principal_type.

# resource types (OWUI's set + the company capability surface; "tool" is the one this increment seeds).
RT_TOOL = "tool"

PERM_USE = "use"

# the append-only grant leaf (the session_channels.jsonl twin — log-IS-the-index, sync, fsync'd).
LEAF = os.path.join(_fcfg.STORE_DIR, "access_grants.jsonl")

# the operator id — the SAME source remote.py uses (identity IS the boundary). Kept in one place.
OPERATOR_USER_ID = os.environ.get(
    "OPERATOR_USER_ID", "ebe5f9c7-4d66-4717-835f-afc96088facb")


def _now() -> int:
    return int(time.time())


def _grant_key(g: dict) -> tuple:
    """The UNIQUE constraint OWUI declares (access_grants.py:31-40) — the natural identity of a grant."""
    return (g["resource_type"], g["resource_id"], g["principal_type"], g["principal_id"], g["permission"])


# ── the store (append-only jsonl + read-time fold — the company's native pattern) ───────────────
def _append(leaf: str, row: dict) -> dict:
    os.makedirs(os.path.dirname(leaf), exist_ok=True)
    with open(leaf, "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())
    return row


def grant(resource_type: str, resource_id: str, principal_type: str, principal_id: str,
          permission: str = PERM_USE, *, leaf: str | None = None) -> dict:
    """Add ONE access grant (idempotent on the OWUI unique key — a duplicate is a fold no-op).
    Fail-loud on an invalid principal_type (the kind axis is closed to the declared vocabulary; a new
    value is added to PRINCIPAL_TYPES here, registry-is-truth)."""
    if principal_type not in PRINCIPAL_TYPES:
        raise ValueError(
            f"grant: principal_type={principal_type!r} not in {list(PRINCIPAL_TYPES)} — the kind axis "
            f"extends by ADDING a value here (the OWUI free-Text-column pattern), never by a typo.")
    if not (isinstance(resource_id, str) and resource_id):
        raise ValueError("grant: resource_id required (a tool name, or '*' for all).")
    row = {"id": str(uuid.uuid4()), "resource_type": resource_type, "resource_id": resource_id,
           "principal_type": principal_type, "principal_id": principal_id,
           "permission": permission, "created_at": _now()}
    return _append(leaf or LEAF, row)


def fold_grants(*, leaf: str | None = None) -> list[dict]:
    """Project the live grant rows from the leaf — read-time fold, dedup on the OWUI unique key
    (last write wins is irrelevant; the key is the identity, so a dup collapses). Honest empty list."""
    path = leaf or LEAF
    if not os.path.exists(path):
        return []
    rows: dict[tuple, dict] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                g = json.loads(line)
            except ValueError:
                continue
            rows[_grant_key(g)] = g
    return list(rows.values())


# ── the decision (OWUI has_access semantics, sync) ──────────────────────────────────────────────
def has_access(principal_type: str, principal_id: str, resource_type: str, resource_id: str,
               permission: str = PERM_USE, *, leaf: str | None = None,
               group_ids: set[str] | None = None) -> bool:
    """True iff a grant authorizes (principal_type, principal_id) for permission on the resource.
    Mirrors OWUI's has_access (access_grants.py:497): a match is the SPECIFIC principal, OR the
    type-wildcard `principal_id=='*'`, OR (for a viewer) any of the principal's groups. A wildcard
    `resource_id=='*'` grant matches ANY resource of that type (the operator's all-tools grant)."""
    grps = group_ids or set()
    for g in fold_grants(leaf=leaf):
        if g["resource_type"] != resource_type or g["permission"] != permission:
            continue
        if g["resource_id"] not in (resource_id, WILDCARD):
            continue
        pt, pid = g["principal_type"], g["principal_id"]
        if pt == principal_type and pid in (principal_id, WILDCARD):
            return True
        if pt == PT_GROUP and pid in grps:
            return True
    return False


# ── SEED-TO-CURRENT (reproduce exactly today's remote.py decision as grant rows) ────────────────
def seed_current_tool_grants(safe_tool_names, *, operator_id: str | None = None,
                             leaf: str | None = None) -> dict:
    """Write the grant rows that REPRODUCE EXACTLY today's remote.py tool-access decision:
      • operator → ALL tools : one wildcard row (tool, '*', viewer, <operator_id>, use).
      • client   → safe subset: one row per posture-'safe' tool (tool, <name>, viewer, '*', use).
    Idempotent (re-seeding collapses on the unique key). `safe_tool_names` is the LIVE posture-'safe'
    set (the caller derives it from _TOOL_MANAGER via _tool_posture — the seed mirrors the live truth,
    never a hardcoded list). Returns a summary {operator_grants, client_grants, safe_count}."""
    op = operator_id or OPERATOR_USER_ID
    lf = leaf or LEAF
    n_op = n_cl = 0
    grant(RT_TOOL, WILDCARD, PT_VIEWER, op, PERM_USE, leaf=lf); n_op += 1
    for name in sorted(set(safe_tool_names)):
        grant(RT_TOOL, name, PT_VIEWER, WILDCARD, PERM_USE, leaf=lf); n_cl += 1
    return {"operator_grants": n_op, "client_grants": n_cl, "safe_count": len(set(safe_tool_names)),
            "operator_id": op, "leaf": lf}


def tool_allowed_via_grants(tool_name: str, *, principal_type: str, principal_id: str,
                            leaf: str | None = None) -> bool:
    """The GRANT-DRIVEN answer to 'may this principal use this tool' — the shadow authority the gate
    consults. A thin has_access over (tool, <name>). Today this is PROVEN EQUAL to the posture/tier
    decision (the seed); flipping it to be the SOLE authority is a one-line gate change later."""
    return has_access(principal_type, principal_id, RT_TOOL, tool_name, PERM_USE, leaf=leaf)
