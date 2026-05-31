"""fabric/client.py — guarded model calls (S6). See fabric/AGENTS.md.

Transport-agnostic: a `transport(model, messages, **opts) -> str` callable is INJECTED
(the LiteLLM-backed one lives in fabric/transport.py). The guards are the fabric.py
lessons made into tested logic — non-empty + JSON-repair + schema-validate + retry/backoff,
**fail loud**: never return empty or unvalidated content silently.
"""
from __future__ import annotations
import json
import time
from typing import Any, Callable, Type

from pydantic import BaseModel


class FabricError(RuntimeError):
    """Raised when a model call cannot produce valid content after retries (fail loud)."""


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
             retries: int = 3, sleep: Callable = time.sleep, **opts) -> Any:
    """Call `transport` with guards. Returns text (schema=None) or a validated model.

    Retries on: transport error · empty content · unparseable JSON · schema mismatch.
    After `retries` exhausted, raises FabricError (never returns degraded output).
    """
    last: FabricError | None = None
    for attempt in range(retries):
        try:
            content = transport(model, messages, **opts)
        except Exception as e:                                   # transport/network/backoff
            last = FabricError(f"transport error: {e!r}")
            sleep(0.5 * (attempt + 1)); continue

        if not content or not str(content).strip():              # empty (kimi/glm lesson)
            last = FabricError("empty content from model")
            sleep(0.5 * (attempt + 1)); continue

        if schema is None:
            return content

        try:
            data = _parse(content)                               # parse (+ repair)
        except Exception as e:
            last = FabricError(f"unparseable JSON: {e!r}")
            sleep(0.5 * (attempt + 1)); continue
        try:
            return schema.model_validate(data)                   # validate
        except Exception as e:
            last = FabricError(f"schema validation failed: {e!r}")
            sleep(0.5 * (attempt + 1)); continue

    raise last or FabricError("no attempts made")
