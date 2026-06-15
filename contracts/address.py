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
  exchange://<sid>/<i>                                  a captured conversation exchange (recollection's canonical provenance address)
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

Note on `board://` (the Company NOTICEBOARD — runtime/cc_board.py): like `ui://`/`session://`, a
*label* in the address grammar. `board://<id>` identifies a board item (request/issue/tip/guide/idea);
the canonical id is flat + opaque (`item-`+hex) so a type-change (idea→request promotion) never
re-addresses it — identity holds nothing mutable. RESOLVER DEFERRED (register-as-label, the `ui://`
precedent — a scheme registered but not resolved): the board's consumers resolve directly via
`runtime/cc_board.py:get_item` (strip the scheme → get_item(id)); a `resolve_address` branch is wired
only when a resolver consumer appears. Adding `"board"` to SCHEMES is purely additive (widens the legal
scheme set; mirrors `ui://`), no record-shape or schema_ver change.

Note on `exchange://` (recollection's canonical provenance address — `exchange://<sid>/<i>`): the
re-embed-stable identity of a captured conversation exchange (one user→assistant turn), the join key the
recall/memory system addresses units by. Registered here as a *label* so it is grammar-legal across the
ONE Company address space (Tim's "one addressed state"); its RESOLVER is recollection's lane (the
recall/capture + recall↔board wires own it) — register-but-defer, mirroring `ui://`. Purely additive;
no record-shape or schema_ver change.
"""
from __future__ import annotations
from pydantic import BaseModel, Field

SCHEMES = ("run", "cas", "blob", "vec", "ui", "code", "skill", "context", "session", "cap", "board", "exchange")


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
