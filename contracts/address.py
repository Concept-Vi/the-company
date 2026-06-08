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
"""
from __future__ import annotations
from pydantic import BaseModel, Field

SCHEMES = ("run", "cas", "blob", "vec", "ui", "code", "skill", "context")


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
