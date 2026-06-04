"""fabric/client.py — guarded model calls (S6). See fabric/AGENTS.md.

Transport-agnostic: a `transport(model, messages, **opts) -> str` callable is INJECTED
(the LiteLLM-backed one lives in fabric/transport.py). The guards are the fabric.py
lessons made into tested logic — non-empty + JSON-repair + schema-validate + retry/backoff,
**fail loud**: never return empty or unvalidated content silently.
"""
from __future__ import annotations
import json
import random
import time
from typing import Any, Callable, Type

from pydantic import BaseModel


class FabricError(RuntimeError):
    """Raised when a model call cannot produce valid content after retries (fail loud)."""


def _backoff(attempt: int, base: float = 1.0, cap: float = 30.0) -> float:
    """Exponential + jittered backoff for retry `attempt` (replaces the old linear un-jittered
    0.5*(attempt+1)). base*(2**attempt) capped at `cap`, + random.uniform(0,base) jitter so
    concurrent cloud callers don't thunder-herd the same retry instant."""
    return min(cap, base * (2 ** attempt)) + random.uniform(0, base)


def _retry_sleep(sleep: Callable, attempt: int, retries: int) -> None:
    """Backoff BETWEEN attempts only — the final attempt (retries-1) raises without sleeping
    (the old code burned a dead ~base-sec wait before raising). Earlier attempts back off."""
    if attempt < retries - 1:
        sleep(_backoff(attempt))


def _balance_json(s: str) -> str:
    """Best-effort repair of truncated JSON: strip code fences, balance brackets."""
    s = s.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if "{" in s:
            s = s[s.find("{"):]
    opens = s.count("{") - s.count("}")
    obrk = s.count("[") - s.count("]")
    return s + ("]" * max(0, obrk)) + ("}" * max(0, opens))


def _parse(content: str):
    try:
        return json.loads(content)
    except Exception:
        return json.loads(_balance_json(content))   # may still raise -> caller treats as failure


def complete(transport: Callable, messages: list, model: str,
             schema: Type[BaseModel] | None = None,
             retries: int = 4, sleep: Callable = time.sleep, **opts) -> Any:
    """Call `transport` with guards. Returns text (schema=None) or a validated model.

    Retries on: transport error · empty content · unparseable JSON · schema mismatch.
    Backs off exponential+jittered between attempts (`_retry_sleep`), never after the last.
    Default `retries`=4 (bumped from 3 — ollama-cloud queues). Exhausted → raises FabricError.
    """
    last: FabricError | None = None
    for attempt in range(retries):
        try:
            content = transport(model, messages, **opts)
        except Exception as e:                                   # transport/network/backoff
            last = FabricError(f"transport error: {e!r}")
            _retry_sleep(sleep, attempt, retries); continue

        if not content or not str(content).strip():              # empty (kimi/glm lesson)
            last = FabricError("empty content from model")
            _retry_sleep(sleep, attempt, retries); continue

        if schema is None:
            return content

        try:
            data = _parse(content)                               # parse (+ repair)
        except Exception as e:
            last = FabricError(f"unparseable JSON: {e!r}")
            _retry_sleep(sleep, attempt, retries); continue
        try:
            return schema.model_validate(data)                   # validate
        except Exception as e:
            last = FabricError(f"schema validation failed: {e!r}")
            _retry_sleep(sleep, attempt, retries); continue

    raise last or FabricError("no attempts made")


def complete_embeddings(transport: Callable, inputs: list, model: str,
                        dim: int | None = None, retries: int = 3,
                        sleep: Callable = time.sleep) -> list:
    """SIBLING of complete() for embeddings — vector guards, NOT text/JSON guards.

    complete()'s empty/JSON-parse/schema guards are text-shaped and meaningless on a float
    list (they'd break or false-pass). So this is a separate guarded path with the SAME
    "every call guarded, fail loud — never return partial/empty" guarantee.

    transport: `(model, inputs: list[str]) -> list[list[float]]` (openai_embeddings_transport).
    Guards (each failure → backoff + retry; retries exhausted → raise FabricError):
      - transport/network error
      - empty result (no vectors)
      - count mismatch: len(vectors) != len(inputs)  (a vector must come back per input)
      - dim mismatch (only if `dim` given): each vector length must == dim
    Returns list[list[float]] (one vector per input), aligned to `inputs`. Never partial/empty.
    """
    last: FabricError | None = None
    n = len(inputs)
    for attempt in range(retries):
        try:
            vectors = transport(model, inputs)
        except Exception as e:                                   # transport/network
            last = FabricError(f"embeddings transport error: {e!r}")
            _retry_sleep(sleep, attempt, retries); continue

        if not vectors:                                          # empty (fail loud)
            last = FabricError("empty embeddings response from model")
            _retry_sleep(sleep, attempt, retries); continue

        if len(vectors) != n:                                    # one vector per input
            last = FabricError(f"embeddings count mismatch: got {len(vectors)} vectors for {n} inputs")
            _retry_sleep(sleep, attempt, retries); continue

        if dim is not None:                                      # dim contract, if asserted
            bad = next((i for i, v in enumerate(vectors) if len(v) != dim), None)
            if bad is not None:
                last = FabricError(f"embeddings dim mismatch at {bad}: got {len(vectors[bad])}, expected {dim}")
                _retry_sleep(sleep, attempt, retries); continue

        return vectors

    raise last or FabricError("no attempts made")
