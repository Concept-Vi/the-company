"""similarity — two Vectors → cosine similarity (a Number). See nodes/AGENTS.md.

A process node: two Vector inputs → one Number output (the cosine of the angle between them,
in [-1, 1]). Cosine = dot(a,b) / (norm(a)*norm(b)) — pure python/math, no AI, no fabric call
(the pattern is in ~/vllm-tests/test_embed.py: cat/feline should score higher than cat/stocks).

NOT VOLATILE: a pure deterministic transform of its inputs — same vectors, same score, so the
memo gate may reuse the cached result. Cosine is inlined (nodes are self-contained C2 modules —
no cross-node import, no fabric/ helper). A zero-magnitude vector raises ZeroDivisionError —
that is fail-loud (no silent 0.0 fallback), the correct behaviour.
"""
import math

VERSION = "1"
KIND = "process"
PORTS_IN = {"a": "Vector", "b": "Vector"}
PORTS_OUT = {"score": "Number"}


def run(inputs: dict, config: dict):
    a = inputs.get("a") or []
    b = inputs.get("b") or []
    if len(a) != len(b):                                   # zip() would TRUNCATE to the shorter vector,
        raise ValueError(                                  # yielding a wrong-but-plausible cosine — FAIL
            f"vector dim mismatch: {len(a)} vs {len(b)} "  # LOUD instead (different embedders -> different
            "(cannot compute cosine of vectors of different dimension)")  # dims; the Vector port carries none)
    dot = sum(x * y for x, y in zip(a, b))                 # dot(a, b)
    na = math.sqrt(sum(x * x for x in a))                  # ||a||
    nb = math.sqrt(sum(y * y for y in b))                  # ||b||
    return float(dot / (na * nb))                          # cosine; zero vector → ZeroDivisionError (fail loud)
