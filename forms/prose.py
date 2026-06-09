"""forms/prose.py — SEED form: the FALLTHROUGH (free prose — route to deep by default).

The catch-all form (`fallthrough: True`): ANY non-empty unit that no narrower form (log/registry/
decision) claimed is free prose — route to the `deep` band (substance until proven otherwise). It
matches any non-empty string; `route()` checks the narrow forms FIRST and the fallthrough LAST (the
`fallthrough` flag drives the ordering — no hardcoded form name), so prose only claims a unit nothing
narrower did. route()'s fail-loud is reserved for an EMPTY registry / an all-False match set (a
misconfiguration), never a normal unit. See runtime/forms.py + forms/AGENTS.md. id MUST equal the file
stem (`prose`).
"""
from __future__ import annotations


def _match(text: str, *, meta: dict | None = None) -> bool:
    return isinstance(text, str) and bool(text.strip())


FORM = {
    "id": "prose",
    "match": _match,
    "stage": "deep",
    "policy": "capture_default",
    "fallthrough": True,
    "desc": "the fallthrough — free prose, treated as substance (deep) until a narrower form claims it",
}
