"""mcp_face/tools/corpus.py — the CORPUS tool (consolidated; MCP-DESIGN-PRINCIPLE instance 1).

ONE resource (the corpus), an `op` selector — replaces the flat list_corpus / find_corpus /
read_corpus_record AND exposes `query` (the ask-the-codebase semantic retrieve, G20, previously
unexposed). `detail` (concise|detailed) + `limit` keep responses token-efficient (concise is the
default — the flat list_corpus returned 65k chars; concise returns only the high-signal fields).
Read-only — no resolve/approve/dispatch (the floor). Reuse-don't-parallel: wraps the existing Suite
methods (list_corpus/find_corpus/read_corpus_record/query_corpus), no new engine.
"""
from typing import Literal

from mcp.types import ToolAnnotations    # posture="safe" → remote.py:_tool_posture reads it (registry-native)



def register(mcp, suite):
    # READ-ONLY across every op (query/list/find/read/neighbours/determine — all reads, no writes). Client-safe.
    @mcp.tool(annotations=ToolAnnotations(posture="safe"))
    def corpus(op: Literal["query", "list", "find", "read", "neighbours", "determine"], project: str = "", kind: str = "", projection: str = "",
               source_address: str = "", address: str = "", text: str = "", space: str = "",
               k: int = 8, rerank: bool = False, top_n: int = 0, emb: str = "pplx", min_score: float = 0.0,
               detail: str = "concise", limit: int = 50, asset: str = "full") -> dict:
        """Read the corpus — the engine's durable, embedded, addressed records (the repo-exocortex's
        'ask the codebase', + every capture pass's output). Pick `op`:

          op="query"  — ASK the corpus a natural-language question; returns the top-k nearest records by
                        meaning. `text` (required) = the question; `space` (optional) = an embeddable
                        space to search (e.g. 'repo' for the codebase — see cognition_info().spaces);
                        `k` = how many. This is the primary 'ask-the-codebase' retrieve.
                        detail="detailed" → each hit carries its record's CONTENT inline (the answer in
                        ONE call); the default stays ids+scores. Every hit id is directly
                        op='read'-able (the round-trip).
                        `rerank` (default OFF, opt-in) → a jina-v3 cross-encoder PRECISION pass over the
                        cosine top-k (ops/rerank.py @ :8008, CPU/0-VRAM): re-orders by deeper
                        (query, digest) relevance, annotating rerank_score + orig_rank (+ the original
                        cosine). FAIL-LOUD if a hit's CAS digest text is unresolvable (never a blank-text
                        rerank). `top_n` caps the reranked count (0 = all k). Single-layer-pplx + rerank
                        is the projection-endorsed proven base (MULTI-LAYER-CONSULT.md) before any
                        cross-layer fusion.
          op="list"   — list records, newest-first; narrow with `project`.
          op="find"   — filter records by `project` / `kind` / `projection` / `source_address`.
          op="read"   — fetch ONE record by its `address` (a run:// from list/find, a code:// source id, OR
                        an extraction://<asset>/<chunk_id> from op='query'/'determine' over the 'extractions'
                        space — reads the dragnet extraction layer's full record: about/summary/claims/…).
                        HONESTY: for an INGESTED FILE the record is a capture DIGEST (a model's one-paragraph
                        summary + metadata), NOT the file's raw text — the corpus stores digests of sources.
                        The source itself lives at the code:// path on disk (outside this face).
          op="determine" — ASK THE DRAGNET EXTRACTION LAYER a topic → GROUNDED themes of REAL, source-traced
                        claims (the full-coverage recall surface). `text` (required) = the topic; `asset`
                        ('full'=session history, 'visual-dna'=the Visual-DNA vault). Pipeline: embed-search the
                        extract-once asset for candidates → re-score them with the served jina-v3 reranker
                        (the relevance pass) → the model CLUSTERS the real claims BY INDEX (theme-labels only —
                        NEVER generates claim text). Every returned claim is a VERBATIM extraction carrying its
                        FULL provenance — chunk_id + rel_path (source file) + anchor (position) + rerank_score —
                        so it traces to where it came from, not just a chunk number (no-fiction by construction;
                        envelope carries no_fiction=true + a rerank note). Distinct from op='query' (cosine
                        top-k): determine is full-coverage grounded-synthesis over the dragnet layer.
          op="neighbours" — the NEIGHBOUR NODE-FIELD: given a unit's `address` (a code:// source id, e.g.
                        a projection:select detail.source), the units AROUND it in `space`, ranked by
                        meaning. Returns {unit, space, emb, neighbours: [{source, score}, ...]}. Each
                        neighbour `source` is itself a code:// address — directly drillable (the relational
                        constellation a unit sits in). `k` = how many to rank (self dropped), `emb`
                        (default 'pplx' — named explicitly), `min_score` thresholds ghosts, `rerank`+`text`
                        runs the jina-v3 precision pass (text=the rerank anchor). FAIL-LOUD honest-empty if
                        the unit has no vector at (address, space, emb) — never a fabricated nearest.

        `detail`: "concise" (default) returns high-signal fields only {source_address, projection, seq,
        address}; "detailed" returns the full records. `limit` (default 50) caps list/find. Read-only."""
        OPS = ("query", "list", "find", "read", "neighbours", "determine")
        if op not in OPS:
            return {"error": f"corpus: unknown op {op!r}. Valid: {list(OPS)} — "
                    "query=ask (text+space) · list=all (project) · find=filter · read=one (address) · "
                    "neighbours=the node-field around a unit (address+space) · "
                    "determine=GROUNDED themes over the dragnet extraction layer (text+asset)."}

        def _shape(rows):
            rows = list(rows)[:limit]
            if detail == "detailed":
                return rows
            return [{"source_address": r.get("source_address"), "projection": r.get("projection"),
                     "seq": r.get("seq"), "address": r.get("address")} for r in rows]

        if op == "query":
            if not text:
                return {"error": "corpus(op='query') needs `text` (the question). Optional: `space` "
                        "(an embeddable space, e.g. 'repo' — cognition_info().spaces), `k`."}
            out = {"op": op, **suite.query_corpus(text, space=(space or None), k=k)}
            # OPT-IN RERANK precision stage (runtime/corpus_rerank.py): cosine top-k → jina-v3
            # cross-encoder reorder (:8008, CPU/0-VRAM). Default OFF (additive, reusable). FAIL-LOUD: a
            # hit with no resolvable CAS digest text RAISES inside rerank_hits → surfaced here as a
            # teaching error, never a silent blank-text rerank. Reordered hits keep id+score
            # (id=address, score=rerank_score) so the detailed-enrich + round-trip note below still work;
            # the original cosine rides along.
            if rerank:
                from runtime import corpus_rerank as _cr
                try:
                    rr = _cr.rerank_hits(suite.store, text, out.get("ranked", []), top_n=(top_n or None))
                except ValueError as e:
                    return {"op": op, "stage": "rerank-failed", "error": str(e)}
                out["ranked"] = [{"id": r["address"], "score": r["rerank_score"], "cosine": r["cosine"],
                                  "orig_rank": r["orig_rank"], "rank": r["rank"]} for r in rr["reranked"]]
                out["stage"] = "rerank"
                out["rerank_backend"] = rr["backend"]
            # P5 — answers, not just pointers (the re-eval: ask→read cost 1+k calls): detailed inlines
            # each hit's record content; a hit whose source was never captured states that honestly.
            if detail == "detailed":
                enriched = []
                for h in out.get("ranked", []):
                    hid = h.get("id")
                    rows = suite.find_corpus(source_address=hid) if hid else []
                    rec = suite.read_corpus_record(rows[0]["address"]) if rows else None
                    enriched.append({**h, "content": (rec or {}).get("output"),
                                     "record_address": rows[0]["address"] if rows else None})
                out["ranked"] = enriched
            out["note"] = (out.get("note") or "") + " · every hit id is corpus(op='read', address=<id>)-able"
            return out
        if op == "determine":
            if not text:
                return {"error": "corpus(op='determine') needs `text` (the topic to determine). Optional: "
                        "`asset` ('full'=session history [default], 'visual-dna'=the Visual-DNA vault), `k`/limit "
                        "→ max claims considered."}
            from runtime import recall_determine as _rd
            # WARM-PATH FIX (2026-06-27): pass the resident `suite` through, not just its store. Without it,
            # determine's semantic step found `suite is None` and COLD-CONSTRUCTED a fresh Suite (re-discover
            # + re-warm the vector cache) on EVERY call — the >60s rebuild/timeout. The MCP face already holds
            # the warm resident suite (register(mcp, suite)); forwarding it reuses the loaded cache.
            return {"op": op, **_rd.determine(text, asset=(asset or "full"), store=suite.store, suite=suite,
                                              max_claims=(limit if limit and limit <= 120 else 60))}
        if op == "neighbours":
            if not address:
                return {"error": "corpus(op='neighbours') needs `address` — a unit's code:// source id "
                        "(e.g. a projection:select detail.source). Optional: `space` (default "
                        "'common_knowledge'), `k`, `emb` (default 'pplx'), `min_score`, `rerank`+`text`."}
            from runtime import corpus_neighbours as _nb
            return {"op": op, **_nb.neighbours(suite.store, address, space=(space or "common_knowledge"),
                    k=k, emb=(emb or "pplx"), min_score=min_score, query=(text or None), rerank=rerank)}
        if op == "list":
            rows = suite.list_corpus(project=(project or None))
            return {"op": op, "project": project or None, "total": len(rows), "detail": detail,
                    "records": _shape(rows)}
        if op == "find":
            rows = suite.find_corpus(project=(project or None), kind=(kind or None),
                                     projection=(projection or None), source_address=(source_address or None))
            return {"op": op, "total": len(rows), "detail": detail, "records": _shape(rows)}
        if op == "read":
            if not address:
                return {"error": "corpus(op='read') needs `address` — a run:// corpus record address "
                        "(from op='list'/'find') OR a SOURCE address (e.g. the code:// ids op='query' "
                        "returns — they round-trip here)."}
            # P8 — ONE file, ONE id regardless of path SPELLING: a code:// address carrying an absolute
            # path under the repo (or a './' prefix) normalizes to the canonical repo-relative id before
            # lookup (the eval: every spelling variant read as 'not ingested' for the same file).
            # extraction://<asset>/<chunk_id> — the dragnet extraction layer's READ path (fork's by-use seam:
            # these are op='query'-able but were not op='read'-able). Resolve from the extraction jsonl so the
            # WHOLE fabric reads a chunk's content (about/summary/claims/…), not just ranks it.
            if address.startswith("extraction://"):
                from runtime import recall_determine as _rd
                rec = _rd.read_extraction(address)
                if rec is not None:
                    return {"op": op, "address": address, "record": rec}
                return {"op": op, "address": address, "record": None,
                        "error": f"no extraction record for {address!r} — expected extraction://<asset>/<chunk_id> "
                        "(asset = 'full' session history | 'visual-dna'). Rank them via corpus(op='query', "
                        "space='extractions') or corpus(op='determine')."}
            if address.startswith("code://"):
                import os as _os
                p = address[len("code://"):]
                repo = _os.getcwd()
                if _os.path.isabs(p) and _os.path.commonpath([repo, _os.path.abspath(p)]) == repo:
                    p = _os.path.relpath(p, repo)
                address = "code://" + _os.path.normpath(p)
            rec = suite.read_corpus_record(address)
            if rec is not None:
                return {"op": op, "address": address, "record": rec}
            # N1 — THE ROUND-TRIP: op='query' returns SOURCE ids (code://…); accept them here by
            # finding their record(s) (newest-first) instead of a silent {record:null}.
            rows = suite.find_corpus(source_address=address)
            if rows:
                rec_addr = rows[0].get("address")
                return {"op": op, "address": rec_addr, "source_address": address,
                        "record": suite.read_corpus_record(rec_addr)}
            # N1 — NO SILENT NULL: nothing found → a TEACHING error, never a bare null.
            return {"op": op, "address": address, "record": None,
                    "error": f"no corpus record found for {address!r} — pass a run://corpus record "
                    "address (from op='list'/'find') or a source address of an INGESTED file (the "
                    "code:// ids op='query' returns). If this source was never ingested, feed it "
                    "first: ingest(paths=[...]) — then it becomes readable + queryable."}
    return corpus
