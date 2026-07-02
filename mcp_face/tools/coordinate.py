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


def run_query(spec: dict) -> dict:
    """THE shared entry both faces call (the MCP tool below + the bridge's /api/query route): embeds
    semantic.text under the RIGHT lens for the space (fabric/embed_routing — code/symbol → nomic-3584,
    else → pplx-2560), then runs the ONE Postgres function. Teaching refusals surface as ValueError;
    embedder-down as RuntimeError (each face maps them to its own error shape)."""
    if not isinstance(spec, dict) or not spec:
        raise ValueError("run_query requires a non-empty spec dict (see coordinate op='vocabulary').")
    spec = dict(spec)
    sem = spec.get("semantic")
    if isinstance(sem, dict) and sem.get("text") and not sem.get("vector"):
        from fabric.embed_routing import embed_query, lens_for_space
        space = sem.get("space") or "desc"
        vec = embed_query(sem["text"], space=space)
        sem = {**sem, "vector": vec}
        sem.pop("text", None)
        # the lens fixes the emb layer when the caller didn't pin one (read layer == write layer)
        if not sem.get("emb"):
            sem["emb"] = "nomic-code" if lens_for_space(space) == "nomic" else "pplx"
        spec["semantic"] = sem
    return _call_query(spec)


def register(mcp, suite):
    @mcp.tool()
    def coordinate(op: str = "query", spec: dict | None = None) -> dict:
        """Query the ledger's COORDINATE SPACE — every axis in one call, fused (L11: ledger.query, the
        same function the UI reads; one definition, two faces).

          op="vocabulary" — the spec schema + a worked example (self-description).
          op="query"      — `spec` = {project?, addresses?[…], filter?{path_under|[…], not_under,
                            node_type[], ext[], changed_after}, graph?{anchor, kinds[], direction:
                            out|in|both, depth≤3, expand}, paths?{kind|id|through}, scale?{space, rung,
                            top_clusters}, semantic?{text|vector, space, emb, k}, lexical?{text},
                            count?{by}, limit?}. semantic.text embeds under the RIGHT lens per space
                            (code/symbol → nomic-3584; else pplx-2560). Returns results + meta.plan (all
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
        return {"op": "query", **run_query(spec)}
