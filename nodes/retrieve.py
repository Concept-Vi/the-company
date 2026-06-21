"""retrieve — query Vector + corpus → top-K ranked by cosine (E1–E5). See nodes/AGENTS.md.

A process node: a query Vector + a corpus → a ranked list of the K nearest corpus items.
This is the escape hatch nodes/codebase.py hands off to (context-stuffing → retrieval): once
the repo outgrows the 400k-char whole-context read, embed the corpus and retrieve the relevant
slices instead.

  - PORTS_IN: query (Vector), corpus (Any) — corpus is a list of {id, vector(, text)}.
  - PORTS_OUT: ranked (Any) — a list of {id, score}, highest cosine first, length <= k.
  - CONFIG: k (number, default 5) — how many to return.

NOT VOLATILE: the corpus arrives as a WIRED INPUT, so it is part of the memo signature — given
the same query + corpus the ranking is identical, a pure transform (the memo gate may reuse it).
(Distinct from a node that reads an index off disk; that hypothetical WOULD be volatile.) Cosine
is inlined per the self-contained-C2 rule (no cross-node import). A zero-magnitude vector raises
ZeroDivisionError — fail-loud, no silent fallback.
"""
import math

VERSION = "1"
KIND = "process"
PORTS_IN = {"query": "Vector", "corpus": "Any"}
PORTS_OUT = {"ranked": "Any"}

CONFIG = {
    "k": {"type": "number", "label": "Top K", "default": 5, "min": 1, "max": 100},
}


def _cosine(a, b):
    if len(a) != len(b):                                   # zip() would TRUNCATE to the shorter vector,
        raise ValueError(                                  # yielding a wrong-but-plausible cosine — FAIL
            f"vector dim mismatch: {len(a)} vs {len(b)} "  # LOUD instead (query + corpus may be embedded
            "(cannot compute cosine of vectors of different dimension)")  # by different models -> different dims)
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return float(dot / (na * nb))                          # zero vector → ZeroDivisionError (fail loud)


def _ranked_numpy(query, corpus, k):
    """VECTORIZED cosine (numpy) — one matmul over the whole corpus instead of the per-item Python loop.
    ~100x on a large space (the 44k extractions space: ~10s warm → ~0.1s; friction-found-by-use 2026-06-21 —
    the per-item `sum(x*y ...)` is O(n·dim) in pure Python = ~112M mults for 44k×2560 = the decision-surface
    memory-leg timeout). RESULTS-IDENTICAL to the Python path: same cosine (float64), same descending sort
    (numpy stable argsort on -score = Python's stable reverse sort → equal scores keep original order).

    Returns None — so run() FALLS BACK to the per-item Python path (never a wrong-but-fast answer) — when
    numpy is unavailable OR an edge the Python path must handle with its EXACT fail-loud semantics:
      • a vector whose dim != query dim → the Python path raises the dim-mismatch ValueError.
      • a zero-magnitude vector (query or any item) → the Python path raises ZeroDivisionError.
    Detecting these and deferring keeps the contract byte-identical (additive optimisation, no behaviour change)."""
    try:
        import numpy as np
    except Exception:
        return None
    if not corpus:
        return []
    qdim = len(query)
    vecs, ids = [], []
    for item in corpus:
        v = item.get("vector") or []
        if len(v) != qdim:
            return None                                    # dim mismatch → Python path raises the exact ValueError
        vecs.append(v)
        ids.append(item.get("id"))
    if qdim == 0:
        return None                                        # empty query → let the Python path fail loud
    M = np.asarray(vecs, dtype=np.float64)                 # (n, dim)
    q = np.asarray(query, dtype=np.float64)                # (dim,)
    qn = float(np.linalg.norm(q))
    mn = np.linalg.norm(M, axis=1)                         # (n,) per-row magnitude
    if qn == 0.0 or bool((mn == 0.0).any()):
        return None                                        # zero vector → Python path raises ZeroDivisionError
    scores = (M @ q) / (mn * qn)                           # (n,) cosine, one matmul
    kk = min(int(k), len(ids))
    order = np.argsort(-scores, kind="stable")[:kk]        # desc, stable on ties (matches Python's stable sort)
    return [{"id": ids[i], "score": float(scores[i])} for i in order]


def run(inputs: dict, config: dict):
    query = inputs.get("query") or []
    corpus = inputs.get("corpus") or []
    k = int(config.get("k", 5))
    fast = _ranked_numpy(query, corpus, k)                 # vectorized fast-path (~100x on large spaces)
    if fast is not None:
        return fast
    # FALLBACK — the original per-item Python cosine (numpy absent, or an edge that must fail loud here):
    scored = [{"id": item.get("id"), "score": _cosine(query, item.get("vector") or [])}
              for item in corpus]
    scored.sort(key=lambda r: r["score"], reverse=True)    # highest cosine first
    return scored[:k]
