"""runtime/corpus_rerank.py — the OPTIONAL rerank PRECISION STAGE over corpus retrieval.

pplx cosine top-K (query_corpus / common_knowledge) → jina-v3 cross-encoder REORDER (ops/rerank.py
served at :8008, CPU / 0-VRAM, no GPU contention). A TOGGLE, FAIL-LOUD: once asked it reranks or
raises — never a fabricated/blank-text score.

WHY a standalone reusable stage (reuse-don't-rebuild): the rerank component (ops/rerank.py) and the
corpus retrieve (suite.query_corpus) and the CAS digest read (corpus.read_record) all already exist;
this is the BINDING that composes them, callable from query_corpus, the consult/R2 retrieve, AND the
FACE drill-in — one stage, no parallel paths.

PROVEN (ch-83e2cque, 2026-06-16, verify-by-use): query "incrementally backfill session transcripts…
high-water-mark" over common_knowledge → BEFORE (cosine) backfill.ts #1 @0.579 (narrow, #2 @0.498);
AFTER (rerank) backfill.ts #1 @+0.321 (decisive gap, #2 @+0.040). Rerank turns a narrow cosine lead
into a clean margin.

PROJECTION DISCIPLINE (build-prep/universal-projection/MULTI-LAYER-CONSULT.md, d53a38e):
  • single-layer-pplx + rerank is the PROVEN BASE — do this BEFORE any cross-layer/lens-union fusion.
  • when fusion comes, it is LATE FUSION ONLY (RRF / score-blend over ranked LISTS) — bge-1024 and
    pplx-2560 are different models/dims; NEVER concat/avg/cosine across them, NEVER MRL-truncate.
  • name emb EXPLICITLY in every read (don't lean on the omit-emb→pplx global default — it silently
    mismatches on bare-only spaces). common_knowledge is pplx-only so omit-emb happens to work, but
    the upstream query_corpus should grow an explicit emb param (flagged to the corpus-face owner).

CRITICAL WIRING INSIGHT (cost two false "rerank degrades" runs before falsify-first caught it): the
cross-encoder needs candidate TEXT, but query_corpus returns only {id, score}. The digest text lives
in CONTENT-ADDRESSED storage (cas://…) — fetch via corpus.read_record(store, run://address), NOT the
bare corpus row (whose `text` is empty). Reranking the bare row reranks the stringified dict = garbage.
"""
from __future__ import annotations

import json
import urllib.request

DEFAULT_RERANK_URL = "http://localhost:8008/rerank"


def _digest_text(store, source_address: str) -> str:
    """The candidate's digest TEXT for the cross-encoder — resolved from CAS via read_record (NOT the
    bare corpus row, whose text is empty). '' if no record/text (caller decides fail-loud)."""
    from runtime import corpus as _corpus
    rows = _corpus.find_corpus(store, source_address=source_address)
    if not rows:
        return ""
    row = sorted(rows, key=lambda r: r.get("seq", 0), reverse=True)[0]
    rec = _corpus.read_record(store, row["address"])
    if not isinstance(rec, dict):
        return str(rec) if rec else ""
    out = rec.get("output")
    if isinstance(out, dict):
        out = out.get("text") or out.get("summary") or json.dumps(out)
    return (out or rec.get("text") or rec.get("content") or "") or ""


def rerank_hits(store, query: str, ranked: list, *, top_n: int | None = None,
                url: str = DEFAULT_RERANK_URL, timeout: int = 90, skip_missing: bool = False) -> dict:
    """Rerank `ranked` (query_corpus's hits: [{id|address, score}, ...]) by the jina-v3 cross-encoder.

    Returns {reranked: [{address, cosine, rerank_score, orig_rank, rank}, ...], stage: 'rerank',
    backend, count, skipped?}. An empty `ranked` returns an empty reranked list (honest, not a crash).

    MISSING-DIGEST policy (two modes — the same-space vs cross-space distinction):
    • `skip_missing=False` (default) — FAIL-LOUD: a hit with no resolvable digest text RAISES. Correct
      for SAME-SPACE callers (e.g. corpus query/neighbours) where every hit MUST have a digest — a blank
      is a real data gap to surface, never silently reranked.
    • `skip_missing=True` — CROSS-SPACE callers (e.g. decision_memory's pooled multi-space bundle, where
      some spaces' sources legitimately lack a CAS digest): SKIP the text-less hits (counted in `skipped`)
      and rerank the rest, so the precision pass actually FIRES on the with-text majority instead of the
      whole call degrading to cosine. Never reranks a blank (skipped, not blanked)."""
    hits = list(ranked or [])
    if not hits:
        return {"reranked": [], "stage": "rerank", "backend": None, "count": 0}

    cands, missing = [], []
    for h in hits:
        addr = h.get("id") or h.get("address")
        text = _digest_text(store, addr)
        if not (isinstance(text, str) and text.strip()):
            missing.append(addr)
            if skip_missing:
                continue                                          # cross-space: drop the text-less hit, rerank the rest
        cands.append({"address": addr, "cosine": h.get("score"), "text": text})
    if missing and not skip_missing:
        raise ValueError(
            f"corpus_rerank: {len(missing)} candidate(s) have no resolvable digest text "
            f"(CAS read returned empty) — fail loud, never rerank a blank. First: {missing[:3]}")
    if not cands:                                                  # all skipped — nothing to rerank (honest empty)
        return {"reranked": [], "stage": "rerank", "backend": None, "count": 0, "skipped": len(missing)}

    body = json.dumps({"query": query, "candidates": cands, "top_n": top_n}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    resp = json.loads(urllib.request.urlopen(req, timeout=timeout).read())

    reranked = []
    for r in resp.get("ranking", []):
        item = r.get("item")
        addr = item.get("address") if isinstance(item, dict) else None
        reranked.append({
            "address": addr,
            "cosine": item.get("cosine") if isinstance(item, dict) else None,
            "rerank_score": r.get("rerank_score"),
            "orig_rank": r.get("orig_rank"),
            "rank": r.get("rank"),
        })
    out = {"reranked": reranked, "stage": "rerank",
           "backend": resp.get("backend"), "count": len(reranked)}
    if missing and skip_missing:
        out["skipped"] = len(missing)
    return out


def query_and_rerank(suite, query: str, *, space: str = "common_knowledge", k: int = 10,
                     top_n: int | None = None, rerank: bool = True) -> dict:
    """Convenience: suite.query_corpus(space, k) → optional rerank stage. `rerank=False` returns the
    bare cosine result (the toggle). NOTE: query_corpus relies on the omit-emb→pplx default; for a
    multi-layer-safe future, the corpus-face owner should add an explicit emb param (projection
    discipline) — common_knowledge is pplx-only so this is correct today."""
    out = suite.query_corpus(query, space=space, k=k)
    if not rerank:
        return {**out, "stage": "cosine"}
    rr = rerank_hits(suite.store, query, out.get("ranked", []), top_n=top_n)
    return {"query": query, "space": space, **rr, "note": out.get("note")}


if __name__ == "__main__":
    # verify-by-use self-test: the proven backfill BEFORE/AFTER over common_knowledge
    import sys, os
    sys.path.insert(0, "/home/tim/company"); os.chdir("/home/tim/company")
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    q = "incrementally backfill session transcripts into the index, resumable via a high-water-mark"
    before = s.query_corpus(q, space="common_knowledge", k=10)
    print("BEFORE (cosine):")
    for i, h in enumerate(before.get("ranked", [])):
        print(f"  {i+1:2d}. {h.get('score'):.3f}  {(h.get('id') or '').split('/')[-1]}")
    after = query_and_rerank(s, q, space="common_knowledge", k=10)
    print(f"\nAFTER (rerank, backend={after.get('backend')}):")
    for r in after.get("reranked", []):
        print(f"  rank {r['rank']:2d} (was #{r['orig_rank']})  {r['rerank_score']:+.4f}  "
              f"{(r['address'] or '').split('/')[-1]}")
