"""C1 — addresses + provenance (Pydantic). See build-prep/contracts/C1.

Grammar:
  run://<domain>/<intent>/<node>@<branch>#run=<id>   mutable pointer
  cas://<algo>:<hash>                                 immutable content
  blob://<algo>:<hash>                                large binary (addressed, not inlined)
  vec://<source-address>#emb=<model>                  an embedding of a source
  ui://<kind>/<ref>                                    a UI component (chrome/field/canvas/panel/ext)
  code://<file-stem>/<symbol>                          a code symbol (the S3 ui://→code:// join)
  skill://<id>                                         a declared reusable unit of instructions (SkillRegistry)
  context://<id>                                       a declared reusable unit of context (ContextRegistry)
  guide://<id>                                          a declared narrative how-to for a target (GuideRegistry)
  session://<id>                                       a Claude Code agent session (the agent-session registry)
  board://<id>                                          a Company Noticeboard item (the cc_board registry)
  clone://<source-sid>/<cut>                            a clone (forked session at a cut-point) — fleet/provenance axis (cc_clone)
  exchange://<sid>/<i>                                  a captured conversation exchange (recollection's canonical provenance address)
  file://<abs-path>                                     a file node (recollection's crossings graph — resolver: whatTouchedFile)
  project://<name>                                      a project node (recollection's containment graph — resolver: containment edges)
Schema-additive: add optional fields + bump schema_ver; never break an existing one.

Note on `ui://`: this scheme is a *label* in the address grammar only. Unlike
run/cas/blob/vec (which the store resolves), `ui://` is resolved elsewhere — its
target lives in the UI-component registry (`contracts.ui_info`), not the store.
Adding it here is purely additive: it widens the legal scheme set, it does not
touch any record shape (e.g. `Provenance`), so no `schema_ver` changes.

Note on `code://` (S3, Interactive Addressed Surface): like `ui://`, this scheme
is a *label* the store does not resolve — it is resolved by the backend
`ui://→code://→scope[]` resolver (`Suite.resolve_scope`), which reads the corpus
join data (`design/_system/{addresses.json, code-symbols.json}`). Its canonical
id is `code://<file-stem>/<symbol>` (e.g. `code://suite/review_verdicts`), matching
the corpus code-symbol registry (`design/_system/symbols.py`). Adding it to SCHEMES
is purely additive (it widens the legal scheme set; mirrors the `ui://` precedent),
so no record shape and no `schema_ver` change. Establishing `code://` in the
backend is the pivot L1 (comment→build-intent scope) and L5 (self-change→element)
both lean on.

Note on `skill://` + `context://` (C 3b — skills/contexts as addressable
registries): like `ui://`/`code://`, these are *labels* the store does not resolve —
they are resolved by `runtime/cognition.py:resolve_address`, which dispatches them to
their FILE-DISCOVERED registries (`runtime/skills.py:SkillRegistry`/`ContextRegistry`,
mirroring `RoleRegistry`). A `skill://<id>` resolves to that skill's instructions
content; a `context://<id>` resolves to that context's content blob. Adding both to
SCHEMES is purely additive (it widens the legal scheme set; mirrors the `ui://`/`code://`
precedent), so no record shape and no `schema_ver` change. This is the FIRST real
extension of the `resolve_address` seam: the schemes that USED to fail loud there now
have a resolver. registry-is-truth — the ids live in their dirs, never a literal here.

Note on `session://` (Session Fabric F1.2 — sessions message sessions): like
`skill://`/`context://`, a *label* resolved by `runtime/cognition.py:resolve_address`,
which reads the agent-session REGISTRY RECORD (`FsStore.load_agent_session` — the
whole-record durable identity under `<store>/agent_sessions/`, backfilled by the
importer + maintained by the session supervisor). `session://<id>` resolves to that
session's registry record (id, name, cwd, title, state, last_activity, envelope);
the LIVE trajectory view is the Suite's `list_agent_sessions` fold (log-IS-the-index),
not this resolver. `<id>` is the Claude Code session uuid (the jsonl basename in
`~/.claude/projects/<project>/<id>.jsonl`). Adding it to SCHEMES is purely additive
(it widens the legal scheme set; mirrors the `skill://`/`context://` precedent), so
no record shape and no `schema_ver` change. NOT `fabric://` (the model fabric owns
that name) and NOT a second "session" noun in the store — the registry dir is
`agent_sessions/`, distinct from the review-session `sessions/` dir (naming ruling,
Session Fabric criteria audit N2).

Note on `cap://` (Mirror-Registry System LANE-CONTRACTS — capability registry address):
like `skill://`/`context://`/`session://`, a *label* resolved by
`runtime/cognition.py:resolve_address`, which dispatches to `CapabilityRegistry` via
the module-level singleton `capability_registry()` (introspection/registry.py). The
singleton is a NEW pattern (not a copy of skill/context fresh-discover); it exists
because binary discovery is EXPENSIVE (spawns a subprocess + a system/init session) —
fresh-discover-on-each-call would spawn a process on every cap:// resolution. Suite.__init__
calls set_capability_registry() once. Grammar: `cap://<kind>/<id>` where id = `kind/name`
with the '--' prefix included for flags: `cap://flag/--debug` (rest = "flag/--debug").
Adding `"cap"` to SCHEMES is purely additive (same seam as skill/context/session); no
record shape change, no schema_ver bump. The dispatch branch is added to cognition.py
after the session:// block by LANE-CAP-WIRE (depends on LANE-REGISTRIES). The gap-surface
path fires on any unknown cap:// address (registry-is-truth, fail loud, never silent empty).

Note on `board://` (the Company NOTICEBOARD — runtime/cc_board.py): like `session://`/`cap://`, a
*label* in the grammar RESOLVED by `runtime/cognition.py:resolve_address`. `board://<id>` identifies a
board item (request/issue/tip/guide/idea); the canonical id is flat + opaque (`item-`+hex) so a
type-change (idea→request promotion) never re-addresses it — identity holds nothing mutable. RESOLVED
(Heart H1.1, commit 68c7eda — was register-but-defer at e5388f4, now wired): the dispatcher lazy-imports
`runtime/cc_board.py` and returns `get_item(id)` (strip the scheme), fail-loud on a missing id (never the
blob/vec silent-empty). board:// now joins session://·cap:// resolving through the ONE resolver, and is a
`cc_board.traverse()` edge-target ACROSS registries (H1.2). Adding `"board"` to SCHEMES was purely
additive (widens the legal scheme set), no record-shape or schema_ver change.

Note on `clone://` (the clone-FLEET joins the one state — `clone://<source-sid>/<cut>`, runtime/cc_clone.py):
like `board://`/`session://`/`cap://`, a *label* RESOLVED by `runtime/cognition.py:resolve_address` (lazy-
imports cc_clone, returns `get_by_address(addr)` = the clone record + its persisted reflection; fail-loud on
an unknown clone). `cut` = the clone record's `at` field VERBATIM (compact:N | uuid:<uuid> | ts:<iso> — a
path-segment colon is address-safe). The address holds PROVENANCE (which-past-self: source × cut), the STABLE
identity — NOT the ephemeral handle (a re-spawn of the same era resolves the SAME address: re-embed-stable,
the board:// rule). clone:// is a SEPARATE axis from `mind://` (fleet/provenance vs thinking-unit; they
COMPOSE, never collapse — board://item-3c324c27). Grammar: `parse_clone_address` (declared once, beside
`parse_session_address`); cc_clone.get_by_address matches by computing `clone_address(rec)` (proven equivalent
to the parse). Adding `"clone"` to SCHEMES is purely additive; no record-shape or schema_ver change.

Note on `exchange://` (recollection's canonical provenance address — `exchange://<sid>/<i>`): the
re-embed-stable identity of a captured conversation exchange (one user→assistant turn), the join key the
recall/memory system addresses units by. Registered here as a *label* so it is grammar-legal across the
ONE Company address space (Tim's "one addressed state"); its RESOLVER is recollection's lane (the
recall/capture + recall↔board wires own it) — register-but-defer, mirroring `ui://`. Purely additive;
no record-shape or schema_ver change.

Note on `file://` + `project://` (recollection's node-id grammar siblings — co-decided with the lead,
2026-06-15): the crossings-graph node addresses recollection mints + populates — `file://<abs-path>` (a
file node) + `project://<name>` (a project node), alongside `exchange://` + `session://`. Registered here
as *labels* so the whole node grammar is ONE Company address space (the Heart's one addressed state);
their RESOLVERS are recollection's lane (file://→whatTouchedFile, project://→containment edges), wired
when its store absorbs — register-but-defer, mirroring `ui://`/`exchange://`. Purely additive; no
record-shape or schema_ver change.

Note on `vi-vision://` (the FACTORY's asset library, built INTO the company — islands-join-mainland,
Tim 2026-06-17): `vi-vision://<frame>/<type>/<id>` addresses the factory's visual-component registry
(frame = global | project/<id> | user/<id> | session/<id>; type = atom|molecule|organism|template;
id = a component_id). A *label* resolved by `runtime/cognition.py:resolve_address`, which lazy-dispatches
to `runtime/vi_vision.py:resolve_vi_vision(addr)` (mirrors cc_board.get_item / cc_clone.get_by_address — a
Python callable that RAISES on unknown, never a silent empty). The factory's Supabase asset library stays
the source of TRUTH; the spine resolves INTO it (separate + bridged, never joined). The resolver +
`parse_vi_vision_address` (the ONE shared grammar) were authored by composition (ch-2mnxl9j0) as the
factory's good-part contributed to the centre. Adding `vi-vision` to SCHEMES is purely additive (mirrors
the `ui://`/`cap://` precedent); no record-shape or schema_ver change. (Register-but-defer until the
resolver module is brought into the company tree + the dispatch branch wired — externally-sourced code,
confirm-first.)

Note on `decision://` (the DECISION-SURFACE — the resolution-first decision-surface's first content type +
the FACE pipeline's reconcile vessel, composition's contract 2026-06-18): `decision://<frame>/<id>` addresses
a DECISION (a typed thing the system needs an owner to decide ON). frame = global | project/<id> | user/<id> |
session/<id>; a BARE `decision://<id>` (no frame keyword) = global. A *label* resolved by
`runtime/cognition.py:resolve_address`, which dispatches to the file-discovered `runtime/decision_registry.py`
(mirrors board://·vi-vision//: a registry read, fail-loud on unknown). The row carried in the registry is the
PENDING DEFINITION only ({id, meaning(human), options[], explanation_source?, scope?, legibility?} — the
schemas/vi-vision/v1/decision.schema.json contract). STATE (pending|decided) and decided_value/by/at are NOT
authored fields — they RESOLVE from the LATEST `decision_take` mark on the decision's CANONICAL address
(registry-is-truth: the take IS the artifact; the resolver COMPOSES the state, the row never mutates). The
canonical mark target is `decision_address(parse_decision_address(addr))` — `decision://global/<id>` always
(frame explicit) — so a take written via the bare form and a row resolved via the global form share ONE mark
key (else the take silently misses → a decided decision reads pending). Adding `decision` to SCHEMES is purely
additive (mirrors the vi-vision precedent); no record-shape or schema_ver change.
"""
from __future__ import annotations
from pydantic import BaseModel, Field

SCHEMES = ("run", "cas", "blob", "vec", "ui", "code", "skill", "context", "guide", "session", "cap", "board", "clone", "mind", "exchange", "file", "project", "vi-vision", "decision", "image", "extraction")


class Provenance(BaseModel):
    address: str                       # the run:// it was written to
    content_hash: str                  # the cas:// — integrity + dedup
    type: str = "Any"                  # a registered type (C2/S4)
    produced_by: str                   # run-address of the node that made it
    inputs: list[str] = Field(default_factory=list)   # addresses it was made FROM (lineage)
    agent: str = "unknown"
    created_at: str | None = None
    schema_ver: int = 1


def run_address(graph: str, node: str, branch: str = "main", run_id: str | None = None) -> str:
    base = f"run://{graph}/{node}@{branch}"
    return f"{base}#run={run_id}" if run_id else base


def scheme(addr: str) -> str | None:
    for s in SCHEMES:
        if addr.startswith(s + "://"):
            return s
    return None


def is_cas(addr: str) -> bool:
    return addr.startswith("cas://")


# ── session:// sub-address grammar — declared ONCE (the shared parser/validator) ──────────────────────
# session://<sid>                       → the whole agent-session record
# session://<sid>/step/<tool_use_id>    → a tool-call STEP (the step-as-node / R15 gate target)
# Declared HERE (the grammar home, beside scheme()/is_cas() — same pattern as contracts/ui_info.py:
# parse_ui_address for ui://) so the resolver (runtime/cognition.py:resolve_address) and the gate
# (runtime/cc_gate.py:_validate_step_address) share ONE definition. Before this, cognition.py used an
# inline `"/step/" in rest` split (permissive: sid could contain '/') and cc_gate used STEP_ADDR_RE
# (strict: `[^/]+`) — two parsers for one shape that already disagreed on `session://a/b/step/c`
# (f1ade750's two-parsers-one-shape flag). This is the canonical parse both call; new sub-structured
# schemes (clone://·member://·mind://) add their own `parse_<x>_address` here as DECLARED grammar, never
# a second inline substring-split. <sid> carries no '/' (real ids are uuids); <tool_use_id> may.
SESSION_STEP_INFIX = "/step/"


def parse_session_address(addr: str) -> dict:
    """session://<sid> → {"sid": <sid>, "step": None}; session://<sid>/step/<tuid> → {"sid", "step"}.
    FAIL-LOUD (ValueError) on anything else under session:// — an unknown sub-path is MALFORMED, never a
    silent-pass / guessed-nearest. The ONE canonical session-address parse (resolver + gate both call it)."""
    if not isinstance(addr, str) or not addr.startswith("session://"):
        raise ValueError(f"parse_session_address: not a session:// address ({addr!r}). Fail loud.")
    rest = addr[len("session://"):]
    if not rest:
        raise ValueError(f"parse_session_address: empty session id (address {addr!r}). Fail loud.")
    if "/" not in rest:
        return {"sid": rest, "step": None}                       # session://<sid> — whole session
    sid, _, tail = rest.partition("/")                           # rest = "<sid>/step/<tuid>"
    kind, infix, step = tail.partition("/")                      # tail = "step/<tuid>"
    if not sid or kind != "step" or not infix or not step:
        raise ValueError(
            f"parse_session_address: malformed session sub-address {addr!r} — the only legal sub-path is "
            f"'session://<sid>/step/<tool_use_id>' (sid has no '/'; got sub-path {tail!r}). Fail loud, "
            f"never a silent-pass.")
    return {"sid": sid, "step": step}


def is_step_address(addr: str) -> bool:
    """True iff addr is the step-as-node form session://<sid>/step/<tool_use_id> — the ONE shape-check the
    resolver and cc_gate's gate share (no second regex). cc_gate keeps raising its own GateError on a
    False result, so its fail-loud is preserved verbatim (the behavior-preserving import-swap)."""
    try:
        return parse_session_address(addr)["step"] is not None
    except ValueError:
        return False


# ── run:// composition-step grammar — a composition LEG as a gate target (R13 bar 4 / R15) ─────────────
# run://<turn>/<member>            → a SOURCE leg's output    (run_swarm address: run://<turn>/<role>)
# run://<turn>/<member>/<index>    → a DOWNSTREAM leg's output (run_items address: run://<turn>/<role>/<i>)
# This is the address run_composition (runtime/minds.py) emits per leg (its `addresses[member]`). R15's
# gate (cc_gate) gates a COMPOSITION leg on it — not only a native session tool-step. The harness payoff:
# run_composition is OUR driver, so a pre-leg pause IS enforceable here (unlike claude's native loop, the
# documented HONEST-LIMIT for session-steps). run:// is already the canonical resolver scheme
# (resolve_run_ref) — this only declares the gate-target SHAPE. ONE parser home (beside is_step_address);
# cc_gate accepts EITHER step form, never a second inline split.
def parse_composition_step_address(addr: str) -> dict:
    """run://<turn>/<member>[/<index>] → {"turn", "member", "index": int|None}. The two legal shapes are a
    SOURCE leg (run://<turn>/<member>, index=None) and a DOWNSTREAM leg (run://<turn>/<member>/<int>).
    FAIL-LOUD (ValueError) on anything else under run:// — never a silent-pass / guessed-nearest."""
    if not isinstance(addr, str) or not addr.startswith("run://"):
        raise ValueError(f"parse_composition_step_address: not a run:// address ({addr!r}). Fail loud.")
    rest = addr[len("run://"):]
    parts = rest.split("/")
    if len(parts) == 2 and all(parts):
        return {"turn": parts[0], "member": parts[1], "index": None}
    if len(parts) == 3 and all(parts[:2]) and parts[2] != "":
        try:
            return {"turn": parts[0], "member": parts[1], "index": int(parts[2])}
        except ValueError:
            raise ValueError(
                f"parse_composition_step_address: index {parts[2]!r} in {addr!r} is not an int. Fail loud.")
    raise ValueError(
        f"parse_composition_step_address: malformed composition-step {addr!r} — expected "
        f"'run://<turn>/<member>' or 'run://<turn>/<member>/<index>'. Fail loud, never a silent-pass.")


def is_composition_step_address(addr: str) -> bool:
    """True iff addr is a run_composition leg address run://<turn>/<member>[/<index>] — a gate-able
    composition-step (R13 bar 4). Sibling of is_step_address (session-step); cc_gate accepts EITHER."""
    try:
        parse_composition_step_address(addr)
        return True
    except ValueError:
        return False


# ── clone:// sub-address grammar — declared ONCE (the fleet/provenance axis joins the one state) ───────
# clone://<source-sid>/<cut>  → a clone (a forked session at a point in time). cut = the clone record's
# `at` field VERBATIM (compact:N | uuid:<uuid> | ts:<iso> — a path-segment colon is address-safe). The
# address holds PROVENANCE (which-past-self: source × cut), the STABLE identity — NOT the ephemeral handle
# (a re-spawn of the same era resolves the SAME address: the re-embed-stable property, the board:// rule).
# clone:// is a SEPARATE axis from mind:// (board://item-3c324c27 — fleet/provenance vs thinking-unit; they
# COMPOSE, never collapse). Declared here beside parse_session_address (one grammar home); the resolver
# (runtime/cognition.py) + cc_clone.get_by_address both ride this shape — get_by_address matches by
# computing cc_clone.clone_address(rec), proven equivalent to this parse (the is_step_address≡regex seam).
def parse_clone_address(addr: str) -> dict:
    """clone://<source-sid>/<cut> → {"source_sid": <sid>, "cut": <cut>}. cut = the clone record's `at`
    verbatim (split on the FIRST '/'; <sid> carries no '/'). FAIL-LOUD (ValueError) on a malformed clone
    address — never a silent-pass. The canonical clone-address parse (one declared grammar)."""
    if not isinstance(addr, str) or not addr.startswith("clone://"):
        raise ValueError(f"parse_clone_address: not a clone:// address ({addr!r}). Fail loud.")
    rest = addr[len("clone://"):]
    source_sid, sep, cut = rest.partition("/")
    if not source_sid or not sep or not cut:
        raise ValueError(
            f"parse_clone_address: malformed clone address {addr!r} — expected 'clone://<source-sid>/<cut>' "
            f"with both segments non-empty (got source_sid={source_sid!r}, cut={cut!r}). Fail loud, "
            f"never a silent-pass.")
    return {"source_sid": source_sid, "cut": cut}


# ── decision:// sub-address grammar + canonicalizer — declared ONCE (the decision-surface joins the spine) ─
# decision://<frame>/<id> → a DECISION. frame = global | project/<id> | user/<id> | session/<id>; a BARE
# decision://<id> (no frame keyword) = global. Declared here beside parse_session/clone (one grammar home);
# the resolver (runtime/cognition.py:resolve_address) + the take-writer (runtime/territory.py:territory_write,
# wildcard's gallery:direction) BOTH ride this shape. The decision's IDENTITY is decision://<frame>/<id>
# (id+frame) — NOT the schema's optional `address` field (which names the thing the decision decides ON). The
# CANONICAL form (decision_address) is the ONE mark key the take is written to + the resolver reads marks off.
def parse_decision_address(addr: str) -> dict:
    """decision://<frame>/<id> → {frame, scope_kind, scope_id, id}. frame = global | project/<id> |
    user/<id> | session/<id>; a BARE decision://<id> (no frame keyword) = global (scope_kind='global',
    scope_id=None). FAIL-LOUD (ValueError) on anything malformed — never a silent-pass / guessed-nearest.
    The canonical decision-address parse (resolver + take-writer both call it). Mirrors
    parse_vi_vision_address's frame grammar; the trailing <id> is one segment (dots ok, no '/')."""
    if not isinstance(addr, str) or not addr.startswith("decision://"):
        raise ValueError(f"parse_decision_address: not a decision:// address ({addr!r}). Fail loud.")
    rest = addr[len("decision://"):]
    if not rest:
        raise ValueError(f"parse_decision_address: empty decision body ({addr!r}). Fail loud.")
    parts = rest.split("/")
    head = parts[0]
    if head in ("project", "user", "session"):
        if len(parts) < 2 or not parts[1]:
            raise ValueError(
                f"parse_decision_address: frame {head!r} needs an id ('{head}/<id>') in {addr!r}. Fail loud.")
        scope_kind, scope_id, tail = head, parts[1], parts[2:]
    elif head == "global":
        scope_kind, scope_id, tail = "global", None, parts[1:]
    else:
        # BARE form: decision://<id> = global (no frame keyword). The single segment IS the id.
        scope_kind, scope_id, tail = "global", None, parts
    if len(tail) != 1 or not tail[0]:
        raise ValueError(
            f"parse_decision_address: malformed {addr!r} — expected 'decision://<frame>/<id>' (one id "
            f"segment after the frame) or bare 'decision://<id>'. Fail loud, never a silent-pass.")
    frame = "global" if scope_kind == "global" else f"{scope_kind}/{scope_id}"
    return {"frame": frame, "scope_kind": scope_kind, "scope_id": scope_id, "id": tail[0]}


def decision_address(parsed: dict) -> str:
    """The CANONICAL decision IDENTITY string → `decision://<frame>/<id>` (frame ALWAYS explicit, 'global'
    written). The ONE form the resolver keys marks off AND the take-writer writes the `decision_take` mark to —
    so a take written via the bare form `decision://<id>` and a row resolved via `decision://global/<id>` share
    ONE mark target (else the take silently misses → a decided decision reads pending; the adversary-verified
    normalization). Mirrors vi_vision's frame normalization. Pass parse_decision_address(addr)."""
    frame = parsed.get("frame") or "global"
    return f"decision://{frame}/{parsed['id']}"


# cap://<platform>[@version]/<kind>/<name> → a CAPABILITY of a registered SOURCE/PLATFORM (Mirror-Registry).
# SOURCE-FIRST nesting (Tim 2026-06-28: "namespace/addresses should have source/platform in there" — the
# general fix to capability-id collisions across platforms, e.g. codex AND claude both having flag/--model).
# Mirrors image://'s structured nesting: <platform> is the hierarchical root, <version> an optional pin
# (capabilities drift per version — the refresh/freshness machinery exists because of this), <kind>/<name>
# the leaf. BACKWARD-COMPAT ALIAS: the legacy bare form cap://<kind>/<name> (where the first segment is a
# KNOWN capability kind — flag/slash_command/tool/…) resolves to platform 'claude-code' (the original
# single-platform surface), so existing cap://flag/--debug addresses keep working through the transition.
DEFAULT_CAP_PLATFORM = "claude-code"


def parse_cap_address(addr: str) -> dict:
    """cap://<platform>[@version]/<kind>/<name>  (or legacy cap://<kind>/<name> → platform=claude-code).
    Returns {platform, version, kind, name, leaf_id ('<kind>/<name>'), full_id ('<platform>/<kind>/<name>')}.
    FAIL-LOUD on a malformed address — never a silent-pass. The ONE canonical cap parse (resolver + the
    registry id construction both call it)."""
    if not isinstance(addr, str) or not addr.startswith("cap://"):
        raise ValueError(f"parse_cap_address: not a cap:// address ({addr!r}). Fail loud.")
    rest = addr[len("cap://"):]
    if not rest:
        raise ValueError(f"parse_cap_address: empty cap body ({addr!r}). Fail loud.")
    from contracts.capability_entry import KNOWN_KINDS  # local: avoid any import-order coupling on the spine
    parts = rest.split("/")
    head = parts[0]
    if head in KNOWN_KINDS:
        # LEGACY bare form: cap://<kind>/<name> — platform defaults to claude-code (the transition alias).
        platform, version, kind, name_parts = DEFAULT_CAP_PLATFORM, None, head, parts[1:]
    else:
        # NESTED form: cap://<platform>[@version]/<kind>/<name>.
        if "@" in head:
            platform, version = head.split("@", 1)
        else:
            platform, version = head, None
        if not platform:
            raise ValueError(f"parse_cap_address: empty platform in {addr!r}. Fail loud.")
        if len(parts) < 3 or not parts[1]:
            raise ValueError(
                f"parse_cap_address: nested form needs '<platform>/<kind>/<name>' in {addr!r} "
                f"(first segment {head!r} is not a known capability kind, so it is read as a platform). "
                f"Fail loud, never a silent-pass.")
        kind, name_parts = parts[1], parts[2:]
    name = "/".join(name_parts)
    if not name:
        raise ValueError(f"parse_cap_address: empty capability name in {addr!r}. Fail loud.")
    return {"platform": platform, "version": version, "kind": kind, "name": name,
            "leaf_id": f"{kind}/{name}", "full_id": f"{platform}/{kind}/{name}"}


def cap_address(platform: str, kind: str, name: str, version: str | None = None) -> str:
    """The CANONICAL nested capability address: cap://<platform>[@version]/<kind>/<name>. The ONE form the
    registry keys on + the ledger stores as a node address. (Legacy bare cap://<kind>/<name> still parses
    via the known-kind alias, but new addresses are always written source-first.)"""
    head = f"{platform}@{version}" if version else platform
    return f"cap://{head}/{kind}/{name}"


# image://<channel>/<path...> → an IMAGE in a channel. STRUCTURED + DEEP, NOT a flat global id (Tim
# 2026-06-22: "the address space needs more structure and depth than just a dump at a global root level").
# The CHANNEL is the hierarchical ROOT (the frame — images live IN channels); <path> is a NESTABLE path
# (collection/sub/name) so the address is NAVIGABLE AT EACH DEPTH: image://<channel> = the channel's whole
# image tree · image://<channel>/<collection> = that group · image://<channel>/<collection>/<name> = one
# image. Mirrors decision://<frame>/<id> + code://<project>/<rel_path>, but the leaf is a multi-segment path.
import re as _re

# A GENERAL VERSION AXIS on addressed content (Tim 2026-06-22: "addressed content will need a version axis
# too"). Convention: <addr>@v<n> — an ORDINAL content version (v1, v2, …). The BARE address = the latest/
# current version. Distinct from run://'s `#run=<id>` (a run-INSTANCE pointer, not an ordinal content
# version). This is a CROSS-SCHEME axis: it applies to ANY addressed content (images are the first instance;
# the convention generalises to docs/decisions/any versioned attachment). split_version is the one parser.
_VERSION_RE = _re.compile(r"@v(\d+)$")


def split_version(addr: str) -> dict:
    """Split a GENERAL version suffix off any address: <addr>@v<n> → {base, version}. A bare address (no
    @v<n>) → {base: addr, version: None} = the latest/current. FAIL-LOUD on a malformed @v suffix (e.g.
    @vfoo) — never silently treat it as part of the path."""
    if not isinstance(addr, str):
        raise ValueError(f"split_version: not a string ({addr!r}).")
    m = _VERSION_RE.search(addr)
    if m:
        return {"base": addr[:m.start()], "version": int(m.group(1))}
    if "@v" in addr and addr.rsplit("@v", 1)[-1] != "":   # there's an @v… that didn't match \d+ = malformed
        bad = addr.rsplit("@v", 1)[-1]
        if not bad.isdigit():
            raise ValueError(f"split_version: malformed version suffix '@v{bad}' in {addr!r} — the version "
                             f"axis is an ordinal '@v<n>' (e.g. @v2). Fail loud, never a silent path-segment.")
    return {"base": addr, "version": None}


def versioned_address(base: str, version: int) -> str:
    """The canonical versioned form → <base>@v<n> (the general content-version axis)."""
    return f"{base}@v{int(version)}"


def parse_image_address(addr: str) -> dict:
    """image://<channel>/<path> → {channel, path, segments, name, is_leaf}. channel = first segment (the
    hierarchical root, REQUIRED); path = the remaining '/'-joined segments (may be deep, may be empty for a
    channel-level/prefix address used for navigation/listing); name = the last path segment; is_leaf =
    there is a path (a specific image) vs a prefix (a group). FAIL-LOUD on a missing channel / bare image://
    (never a flat global dump)."""
    if not isinstance(addr, str) or not addr.startswith("image://"):
        raise ValueError(f"parse_image_address: not an image:// address ({addr!r}). Fail loud.")
    sv = split_version(addr)                              # strip the general @v<n> version axis first
    rest = sv["base"][len("image://"):].strip("/")
    if not rest:
        raise ValueError(
            f"parse_image_address: empty image body ({addr!r}) — an image address needs at least a "
            f"channel (image://<channel>/<path>), never a bare global id. Fail loud.")
    segs = [s for s in rest.split("/") if s]
    channel, tail = segs[0], segs[1:]
    return {"channel": channel, "path": "/".join(tail), "segments": tail,
            "name": tail[-1] if tail else "", "is_leaf": bool(tail), "version": sv["version"]}


def image_address(channel: str, path: str) -> str:
    """The CANONICAL image IDENTITY → image://<channel>/<path>. channel + the in-channel hierarchical path
    (e.g. 'deck1-2026/p-05' or 'generated/my-output'). Both required (no flat/rootless image)."""
    if not channel or not path:
        raise ValueError(
            f"image_address needs both a channel and an in-channel path (got channel={channel!r}, "
            f"path={path!r}) — images are addressed hierarchically image://<channel>/<path>, never flat.")
    return f"image://{channel.strip('/')}/{path.strip('/')}"
