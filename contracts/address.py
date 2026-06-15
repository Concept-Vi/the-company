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
"""
from __future__ import annotations
from pydantic import BaseModel, Field

SCHEMES = ("run", "cas", "blob", "vec", "ui", "code", "skill", "context", "session", "cap", "board", "clone", "mind", "exchange", "file", "project")


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
