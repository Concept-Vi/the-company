"""mcp_face/tools/coordinate.py — the COORDINATE QUERY's agent face (L11; file-drop tool).

One question across ALL the ledger's axes at once: "about X (semantic) ∧ mentioning Y (lexical) ∧ under
path P ∧ changed after T ∧ reachable from Z via <kinds> (graph)" — answered by ONE Postgres function,
ledger.query(spec jsonb) (migration 0016), the same definition the UI face calls via PostgREST rpc
(one function → two faces). This tool is the thin agent face: it embeds `semantic.text` through the
fabric's default embedder (pplx-2560 @ :8007 — the desc/docs/history/exchange spaces' lens), passes
everything else through verbatim, and returns the function's results + meta.plan (every leg's counts —
under-recall is never silent).

For the nomic-3584 spaces (code/symbol) pass a pre-computed `vector` in `semantic` instead of `text`
(the code lens embeds via ollama :11434 — a caller with code-lens needs owns that embed).
"""
from __future__ import annotations

import json
import os
import subprocess

OPS = ("query", "vocabulary")

_PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
       "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
       "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
       "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
       "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}


def _call_query(spec: dict) -> dict:
    body = json.dumps(spec)
    tag, i = "$cq$", 0
    while tag in body:
        i += 1
        tag = f"$cq{i}$"
    r = subprocess.run(["psql", "-h", _PG["host"], "-p", _PG["port"], "-U", _PG["user"], "-d", _PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-tA"],
                       input=f"select ledger.query({tag}{body}{tag}::jsonb);",
                       capture_output=True, text=True, timeout=120,
                       env={**os.environ, "PGPASSWORD": _PG["pw"]})
    if r.returncode != 0:
        # surface the function's own teaching RAISE verbatim (it names the bad key/cap + the fix)
        raise ValueError(f"ledger.query refused: {(r.stderr or '').strip()[:500]}")
    return json.loads(r.stdout)


def register(mcp, suite):
    @mcp.tool()
    def coordinate(op: str = "query", spec: dict | None = None) -> dict:
        """Query the ledger's COORDINATE SPACE — every axis in one call, fused (L11: ledger.query, the
        same function the UI reads; one definition, two faces).

          op="vocabulary" — the spec schema + a worked example (self-description).
          op="query"      — `spec` = {project?, filter?{path_under,ext[],node_type[],changed_after},
                            graph?{anchor,kinds[],direction,depth≤3}, semantic?{text|vector,space,emb,k},
                            lexical?{text}, limit?}. `semantic.text` is embedded here via the fabric
                            default (pplx-2560 — desc/docs/history/exchange spaces); pass a raw `vector`
                            for the nomic-3584 code/symbol spaces. Returns results + meta.plan (all
                            legs' counts — nothing silently under-recalls).
        """
        if op == "vocabulary":
            return {"op": "vocabulary",
                    "spec_keys": ["project", "filter", "graph", "semantic", "lexical", "limit"],
                    "example": {"filter": {"path_under": "runtime/", "changed_after": "2026-07-01"},
                                "semantic": {"text": "how the vector store works", "space": "desc", "emb": "pplx"},
                                "lexical": {"text": "supabase cutover"},
                                "limit": 10},
                    "notes": ["semantic.text → embedded via pplx-2560 (spaces: desc/docs/history/exchange/…)",
                              "code/symbol spaces are nomic-3584 — pass semantic.vector instead",
                              "graph.depth caps at 3; unknown spec keys RAISE with the valid set",
                              "meta.plan echoes every leg's counts (under-recall is never silent)"]}
        if op != "query":
            raise ValueError(f"coordinate: unknown op {op!r} — one of {OPS}.")
        if not isinstance(spec, dict) or not spec:
            raise ValueError("coordinate(op='query') requires `spec` (see op='vocabulary').")
        spec = dict(spec)
        sem = spec.get("semantic")
        if isinstance(sem, dict) and sem.get("text") and not sem.get("vector"):
            # embed HERE (the fn is pure SQL): the fabric default path — pplx-2560, the text-space lens
            from fabric import client, transport, config as fcfg
            t = transport.openai_embeddings_transport(base_url=fcfg.DEFAULT_EMBED_URL)
            vec = client.complete_embeddings(t, [sem["text"]], model=fcfg.DEFAULT_EMBED_MODEL,
                                             dim=fcfg.DEFAULT_EMBED_DIM)[0]
            sem = {**sem, "vector": vec}
            sem.pop("text", None)
            spec["semantic"] = sem
        return {"op": "query", **_call_query(spec)}
