"""forms/registry.py — SEED form: a REGISTRY/INDEX (structural — route to legibility).

Recognises a registry/index-shaped unit (a table-of-contents / a list of links / a MoC). Structural,
not substance — route to the `legibility` band (extract structure cheaply, don't deep-describe an
index). See runtime/forms.py + forms/AGENTS.md. id MUST equal the file stem (`registry`).
"""
from __future__ import annotations

import re

_INDEXWORD = re.compile(r"\b(map of contents|table of contents|\bMoC\b|registry|index)\b", re.I)


def _match(text: str, *, meta: dict | None = None) -> bool:
    if not isinstance(text, str) or not text:
        return False
    head = "\n".join(text.splitlines()[:8])
    if _INDEXWORD.search(head):
        return True
    # mostly link-lines = an index
    lines = [ln for ln in text.splitlines() if ln.strip()]
    if not lines:
        return False
    linky = sum(1 for ln in lines if "[[" in ln or re.search(r"\]\(", ln))
    return len(lines) >= 5 and linky / len(lines) > 0.6


FORM = {
    "id": "registry",
    "match": _match,
    "stage": "legibility",
    "policy": "prose_default",
    "desc": "a registry/index/MoC (structure, not substance) — extract structure cheaply, no deep describe",
}
