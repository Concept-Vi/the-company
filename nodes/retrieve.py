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


def run(inputs: dict, config: dict):
    query = inputs.get("query") or []
    corpus = inputs.get("corpus") or []
    k = int(config.get("k", 5))
    scored = [{"id": item.get("id"), "score": _cosine(query, item.get("vector") or [])}
              for item in corpus]
    scored.sort(key=lambda r: r["score"], reverse=True)    # highest cosine first
    return scored[:k]
