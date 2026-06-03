"""tests/embeddings_acceptance.py — the embedding chain works by USE against the live BGE-M3 endpoint (T2-EMBED-GATE).

`nodes/embed.py` (text→Vector via the guarded embeddings fabric), `nodes/similarity.py` (two Vectors→cosine),
and `nodes/retrieve.py` (query Vector + corpus → top-K) are well-built (fail-loud, registry-fed) but had ZERO
test coverage. This proves them by use:
  - embed turns text into a real 1024-dim BGE-M3 vector;
  - SEMANTIC ORDERING holds: similarity(cat, feline) > similarity(cat, stocks) — the meaning-distance the
    embedder is for (the assertion in ~/vllm-tests/test_embed.py);
  - retrieve RANKS a small corpus, returning the nearest item first;
  - a dim mismatch FAILS LOUD (similarity/retrieve raise rather than silently truncating to a wrong cosine).

LIVE-ENDPOINT POLICY (fail-loud rule, never a silent/vacuous pass): the embed/similarity/retrieve checks need
the real BGE-M3 endpoint (:8001). If it is unreachable we SKIP those checks with a LOUD notice and return
NON-ZERO — never an "ALL PASS" banner over un-run checks. The dim-mismatch checks are pure (no endpoint) and
always run.

Run: ./.venv/bin/python tests/embeddings_acceptance.py
"""
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from fabric import config as fcfg
from nodes import embed, similarity, retrieve

PASS = 0
ok = True


def check(label, cond):
    global PASS, ok
    ok &= bool(cond)
    if cond:
        PASS += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def embed_endpoint_up() -> bool:
    try:
        urllib.request.urlopen(fcfg.DEFAULT_EMBED_URL.rstrip("/") + "/models", timeout=4)
        return True
    except Exception:
        return False


def main():
    global ok

    # === pure (no endpoint) — dim-mismatch fail-loud, always runs ===
    raised = False
    try:
        similarity.run({"a": [1.0, 0.0, 0.0], "b": [1.0, 0.0]}, {})
    except ValueError:
        raised = True
    check("similarity FAILS LOUD on a vector dim mismatch (no silent wrong-cosine)", raised)

    raised_r = False
    try:
        retrieve.run({"query": [1.0, 0.0, 0.0],
                      "corpus": [{"id": "x", "vector": [1.0, 0.0]}]}, {"k": 5})
    except ValueError:
        raised_r = True
    check("retrieve FAILS LOUD on a query/corpus dim mismatch", raised_r)

    # similarity of identical unit-direction vectors is ~1.0; orthogonal is ~0.0 (the cosine contract)
    check("similarity of identical vectors ≈ 1.0",
          abs(similarity.run({"a": [1.0, 2.0, 3.0], "b": [1.0, 2.0, 3.0]}, {}) - 1.0) < 1e-9)
    check("similarity of orthogonal vectors ≈ 0.0",
          abs(similarity.run({"a": [1.0, 0.0], "b": [0.0, 1.0]}, {})) < 1e-9)

    # === live — needs the BGE-M3 endpoint ===
    if not embed_endpoint_up():
        print(f"\n  [SKIP] embeddings endpoint {fcfg.DEFAULT_EMBED_URL} unreachable — "
              "the live embed/similarity/retrieve checks did NOT run.")
        print("  (Bring up BGE-M3 @ :8001 to run them. Refusing a silent/vacuous pass: returning non-zero.)")
        print(f"\nPARTIAL — {PASS} pure checks passed; LIVE checks SKIPPED (endpoint down). NOT a full pass.")
        return 2

    # embed: text → a real vector (1024-dim for BGE-M3)
    v_cat = embed.run({"text": "cat"}, {})
    check("embed returns a non-empty list[float] vector",
          isinstance(v_cat, list) and len(v_cat) > 0 and all(isinstance(x, float) for x in v_cat))
    check("embed returns the BGE-M3 1024-dim vector", len(v_cat) == 1024)

    v_feline = embed.run({"text": "feline"}, {})
    v_stocks = embed.run({"text": "stock market finance"}, {})
    check("the three embeddings share one dimension (same embedder)",
          len(v_cat) == len(v_feline) == len(v_stocks))

    # THE semantic assertion: cat is closer to feline than to stocks
    sim_feline = similarity.run({"a": v_cat, "b": v_feline}, {})
    sim_stocks = similarity.run({"a": v_cat, "b": v_stocks}, {})
    print(f"      (sim(cat,feline)={sim_feline:.4f}  sim(cat,stocks)={sim_stocks:.4f})")
    check("semantic ordering holds: similarity(cat,feline) > similarity(cat,stocks)",
          sim_feline > sim_stocks)

    # retrieve ranks a small corpus: the query 'kitten' should rank the cat/feline items above stocks
    corpus = [
        {"id": "cat", "vector": v_cat},
        {"id": "feline", "vector": v_feline},
        {"id": "stocks", "vector": v_stocks},
    ]
    q = embed.run({"text": "kitten"}, {})
    ranked = retrieve.run({"query": q, "corpus": corpus}, {"k": 3})
    check("retrieve returns a ranked list of {id, score}",
          isinstance(ranked, list) and len(ranked) == 3
          and all("id" in r and "score" in r for r in ranked))
    check("retrieve ranks highest-cosine first (descending scores)",
          ranked[0]["score"] >= ranked[1]["score"] >= ranked[2]["score"])
    check("retrieve ranks the animal items above 'stocks' for a 'kitten' query",
          ranked[-1]["id"] == "stocks")
    check("retrieve respects k (k=2 → 2 results)",
          len(retrieve.run({"query": q, "corpus": corpus}, {"k": 2})) == 2)

    print("\n" + (f"ALL {PASS} CHECKS PASS — embed→similarity→retrieve work live against BGE-M3; dim-mismatch fails loud"
                  if ok else "EMBEDDINGS ACCEPTANCE FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
