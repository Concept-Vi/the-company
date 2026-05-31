"""C1 — addresses + provenance (Pydantic). See build-prep/contracts/C1.

Grammar:
  run://<domain>/<intent>/<node>@<branch>#run=<id>   mutable pointer
  cas://<algo>:<hash>                                 immutable content
  blob://<algo>:<hash>                                large binary (addressed, not inlined)
  vec://<source-address>#emb=<model>                  an embedding of a source
Schema-additive: add optional fields + bump schema_ver; never break an existing one.
"""
from __future__ import annotations
from pydantic import BaseModel, Field

SCHEMES = ("run", "cas", "blob", "vec")


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
