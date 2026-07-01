"""runtime/corpus_fusion.py — the OPTIONAL hybrid-fusion stage over corpus retrieval (the LATE-FUSION merge).

THE GAP THIS CLOSES (verified live 2026-06-29): the company already has BOTH retrieval legs over its
corpus —
  • VECTOR (meaning): suite.query_corpus → store.vector_index.query_index over the space-keyed index;
  • LEXICAL (substrings): runtime/session_search._search_lexical — BUT that lexical leg searches the
    INTERIM claude-sessions substrate.db, NOT the durable corpus spaces.
What the company lacked is the FUSION STAGE that COMBINES a lexical + a vector ranking over the SAME
corpus spaces into one ranking. This module is that stage — and it lifts the lexical leg onto the
corpus-space digests (so a hybrid query is genuinely two legs over the same records).

WHY RRF, NOT SCORE-BLEND (the projection discipline, corpus_rerank.py:19-20 — verbatim law):
  "when fusion comes, it is LATE FUSION ONLY (RRF / score-blend over ranked LISTS) — bge-1024 and
   pplx-2560 are different models/dims; NEVER concat/avg/cosine across them."
Reciprocal-Rank Fusion needs only the RANK POSITION of an item in each leg, never the raw score — so it
sidesteps the scale mismatch entirely (a term-count lexical score vs a cosine vector score are NEVER
comparable as numbers, but their ranked POSITIONS always are). RRF(item) = Σ_leg weight_leg / (rrf_k + rank_leg).

WHY a standalone reusable stage (reuse-don't-parallel — the corpus_rerank.py sibling pattern): the vector
leg (suite.query_corpus), the lexical scoring (session_search._search_lexical's term-count algorithm), the
digest-text resolve (corpus_rerank._digest_text), and the space enumeration (store.index_addresses) ALL
already exist. This module is the BINDING that fuses them — no cosine reimplemented, no second index built,
no inverted index (RRF only needs ranks). The rerank precision stage (corpus_rerank) composes ON TOP of the
fused list, exactly as it composes on top of the cosine list today.

COST (honest): the lexical leg over a corpus space reads every digest in the space (N CAS reads), unlike
the vector leg (top-k only) and rerank (top-k only). It is CAPPED (LEX_SCAN_CAP, mirroring
session_search.LEX_SCAN_CAP=5000) so a large space degrades to a bounded scan, never an unbounded one. An
inverted index would remove the per-query cost — that is deliberate FUTURE work, out of this stage's scope.

FAIL-LOUD / DEGRADE-HONEST (the no-silent-failure floor): if the embedder is down the vector leg returns an
empty ranked list with its own note (query_corpus's honest empty) — fusion then DEGRADES to lexical-only and
SAYS SO in `legs_used` (never a silent fallback presented as a full hybrid). The lexical leg needs no model.
"""
from __future__ import annotations

import re

# Mirror session_search's bounded lexical scan (do not unbound a large space).
LEX_SCAN_CAP = 5000

# RRF constant — the standard damping that keeps a #1 in one leg from dominating a strong consensus across
# legs. 60 is the canonical RRF default (Cormack et al.); a PARAM on the entry point, never hardcoded at the
# call site (flag-hardcoding law) — exposed so a caller can tune the rank-damping.
DEFAULT_RRF_K = 60

# The lexical stopword set + tokeniser are LIFTED from session_search (one term-ranking definition, not two).
_STOP = {"the", "a", "an", "of", "to", "in", "on", "for", "and", "or", "is", "it",
         "was", "what", "how", "did", "do", "we", "i", "you", "about", "with", "that"}


def _terms(q: str) -> list[str]:
    """The query terms (same tokenise+stopword rule as session_search._search_lexical — honest, simple)."""
    return [t for t in re.findall(r"[a-z0-9_./-]+", q.lower()) if len(t) >= 2 and t not in _STOP]


def _digest_from_cas(store, row) -> str:
    """Resolve a corpus row's digest TEXT directly from the CAS hash the row ALREADY carries (write_record's
    ev_row sets `cas`) — ONE get_content, NO re-scan of the event log (the corpus_rerank._digest_text helper
    re-runs find_corpus → events_since(-1) PER address, an N×log cost; here we already hold the row). Mirrors
    _digest_text's output→text extraction so the same digest shape is matched."""
    cas = row.get("cas")
    if not cas:
        return ""
    rec = store.get_content(cas)
    if not isinstance(rec, dict):
        return str(rec) if rec else ""
    out = rec.get("output")
    if isinstance(out, dict):
        import json as _json
        out = out.get("text") or out.get("summary") or _json.dumps(out)
    return (out or rec.get("text") or rec.get("content") or "") or ""


def lexical_leg(store, text: str, space: str, *, fetch: int, scan_cap: int = LEX_SCAN_CAP) -> list[dict]:
    """The LEXICAL ranking over a corpus SPACE's digests. ONE event-log scan (corpus.find_corpus(projection=
    space) — the same projection the records were embedded under), resolving each row's digest TEXT from the
    `cas` the row already carries (_digest_from_cas — no per-address re-scan), scored by the term-count
    algorithm lifted from session_search._search_lexical (distinct query terms present, ties broken by total
    occurrences). No tf-idf theatre — meaning-ranking is the vector leg's job; this is the substring leg.

    THE ID SHAPE MATTERS (the fusion-correctness pivot): the returned `id` is the row's BARE `source_address`
    (e.g. `code://runtime/suite.py`) — the SAME id shape query_corpus/query_index returns (find_relations
    compares query_index ids to bare source ids — proof they're bare). So RRF fuses the two legs on a COMMON
    key; a keyed vec://…#space=… form would never match and 'hybrid' would silently become concatenation.

    Returns [{id, score, why, n_terms_present}] best-first. Bounded by `scan_cap` (a large space degrades to a
    bounded scan, never unbounded). FAIL-LOUD on an unsearchable query (no terms)."""
    terms = _terms(text)
    if not terms:
        raise ValueError(
            f"corpus_fusion lexical leg: the query {text!r} reduced to no searchable terms — give it at "
            f"least one word of 2+ characters that isn't a stopword (the lexical leg matches substrings).")
    from runtime import corpus as _corpus
    # ONE scan → all rows for the space; dedup by source_address (latest seq wins — find_corpus is already
    # dedup-on-read by corpus address, but two projections of one source share a source_address).
    rows = _corpus.find_corpus(store, projection=(space or None))
    seen, scored = set(), []
    for row in rows[:scan_cap]:
        sa = row.get("source_address")
        if not sa or sa in seen:
            continue
        seen.add(sa)
        digest = _digest_from_cas(store, row)
        if not (isinstance(digest, str) and digest.strip()):
            continue                                    # no digest text → nothing to match (honest skip)
        low = digest.lower()
        present = [t for t in terms if t in low]
        if not present:
            continue                                    # no query term present → not a lexical hit
        occurrences = sum(low.count(t) for t in present)
        score = len(present) * 1000 + occurrences       # distinct terms dominate; occurrences break ties
        scored.append({"id": sa, "score": float(score), "n_terms_present": len(present),
                       "why": f"{len(present)}/{len(terms)} terms, {occurrences} occurrences"})
    scored.sort(key=lambda c: -c["score"])
    return scored[:fetch]


def rrf_fuse(legs: dict[str, list[dict]], *, weights: dict[str, float] | None = None,
             rrf_k: int = DEFAULT_RRF_K, k: int | None = None) -> list[dict]:
    """RECIPROCAL-RANK FUSION over named ranked legs. `legs` = {leg_name: [{id, score, ...}, ...]} each
    ranked best-first. Fuses by RANK POSITION only (never the raw scores — the scale-mismatch law). The
    RRF contribution of an item from a leg at 0-based rank r is `weight_leg / (rrf_k + r + 1)`; an item's
    fused score is the SUM of its contributions across the legs it appears in. So an item ranked decently in
    BOTH legs beats an item ranked #1 in only one — consensus wins (the point of hybrid).

    `weights` (default 1.0 each) tunes per-leg influence — a PARAM, never hardcoded (flag-hardcoding law).
    Returns [{id, rrf_score, legs: {leg_name: {rank, score}}, why}] best-first, capped at `k` (None = all).
    Pure ranking math — no I/O, no model. An empty legs-set returns []."""
    weights = weights or {}
    fused: dict[str, dict] = {}
    for leg_name, ranked in legs.items():
        w = weights.get(leg_name, 1.0)
        for r, item in enumerate(ranked or []):
            iid = item.get("id") or item.get("address")
            if iid is None:
                continue
            contribution = w / (rrf_k + r + 1)          # r is 0-based → +1 for the 1-based RRF rank
            slot = fused.setdefault(iid, {"id": iid, "rrf_score": 0.0, "legs": {}})
            slot["rrf_score"] += contribution
            slot["legs"][leg_name] = {"rank": r + 1, "score": item.get("score")}
    rows = sorted(fused.values(), key=lambda s: -s["rrf_score"])
    for s in rows:
        legs_in = ", ".join(f"{ln}#{d['rank']}" for ln, d in s["legs"].items())
        s["why"] = f"RRF over [{legs_in}] = {s['rrf_score']:.5f}"
    return rows[: (k if k else len(rows))]


def query_hybrid(suite, text: str, *, space: str | None = None, k: int = 10,
                 weights: dict[str, float] | None = None, rrf_k: int = DEFAULT_RRF_K,
                 lex_fetch: int | None = None, vec_fetch: int | None = None) -> dict:
    """THE HYBRID-FUSION RETRIEVE: run BOTH legs over the corpus `space`, fuse by RRF, return the top-k.

      • vector leg — suite.query_corpus(text, space, k=vec_fetch) (meaning; needs the embedder up).
      • lexical leg — lexical_leg(store, text, space, fetch=lex_fetch) (substrings; needs no model).
      • fuse — rrf_fuse({vector, lexical}, weights, rrf_k) → top-k.

    DEGRADE-HONEST (no-silent-failure floor): if the embedder is down the vector leg is empty (query_corpus's
    own honest empty + note) → fusion runs on the lexical leg ALONE and `legs_used` says `['lexical']` with the
    vector note carried in `degraded`. NEVER presents a lexical-only result as a full hybrid silently.

    Returns {query, space, mode:'hybrid', legs_used, ranked:[{id, score(=rrf_score), legs, why}], rrf_k,
    weights, degraded?}. Each `id` is corpus(op='read', address=<id>)-able and rerank-able (the fused list is
    a ranked list of ids+scores, the SAME shape the rerank stage consumes). Read-only computation."""
    fetch = max(k * 4, 20)                                # over-fetch each leg so the fuse has depth to work with
    vec_fetch = vec_fetch or fetch
    lex_fetch = lex_fetch or fetch

    vec_out = suite.query_corpus(text, space=space, k=vec_fetch)
    vec_ranked = vec_out.get("ranked", []) or []
    degraded = None
    if not vec_ranked and vec_out.get("note"):
        degraded = f"vector leg empty: {vec_out['note']}"

    lex_ranked = lexical_leg(suite.store, text, space or "", fetch=lex_fetch)

    legs = {}
    if vec_ranked:
        legs["vector"] = vec_ranked
    legs["lexical"] = lex_ranked
    legs_used = list(legs.keys())

    fused = rrf_fuse(legs, weights=weights, rrf_k=rrf_k, k=k)
    ranked = [{"id": f["id"], "score": f["rrf_score"], "legs": f["legs"], "why": f["why"]} for f in fused]

    out = {"query": text, "space": space, "mode": "hybrid", "legs_used": legs_used,
           "rrf_k": rrf_k, "weights": weights or {}, "ranked": ranked,
           "note": "hybrid = RRF over a vector leg (meaning) + a lexical leg (substrings) over the SAME "
                   "corpus space; fused by RANK (never score); every id is op='read'-able + rerank-able."}
    if degraded:
        out["degraded"] = degraded
    return out


if __name__ == "__main__":
    # verify-by-use self-test (the corpus_rerank.py __main__ pattern): a small hybrid retrieve over a space,
    # showing the fused ranking + which legs answered. Degrades honestly when the embedder is down (lexical-only).
    import sys, os
    sys.path.insert(0, "/home/tim/company"); os.chdir("/home/tim/company")
    from runtime.suite import Suite
    from runtime.registry import NodeRegistry
    from store.fs_store import FsStore
    s = Suite(FsStore(".data/store"), NodeRegistry().discover(["nodes"]), nodes_dir="nodes")
    space = sys.argv[1] if len(sys.argv) > 1 else "common_knowledge"
    q = sys.argv[2] if len(sys.argv) > 2 else "incrementally backfill session transcripts high-water-mark"
    res = query_hybrid(s, q, space=space, k=8)
    print(f"HYBRID over space={space!r}  q={q!r}")
    print(f"  legs_used={res['legs_used']}  rrf_k={res['rrf_k']}" +
          (f"  DEGRADED: {res['degraded']}" if res.get("degraded") else ""))
    for i, h in enumerate(res["ranked"]):
        print(f"  {i+1:2d}. rrf={h['score']:.5f}  {h['why']}  ::  {(h['id'] or '').split('/')[-1]}")
