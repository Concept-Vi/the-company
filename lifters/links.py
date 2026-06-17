"""lifters/links.py — SEED lifter: extract links (a `produced_by:"code"` projection).

A deterministic structural EXTRACTOR — reads a markdown unit and returns the list of links it
contains (both `[[wikilinks]]` and `[md](targets)`). NO model call. A PARSE is a READ (the floor
holds). See runtime/lifter_registry.py + lifters/AGENTS.md. Its `id` MUST equal the file stem (`links`).
"""
from __future__ import annotations

import re

_WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:[#|][^\]]*)?\]\]")
_MDLINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def _extract(text: str, *, meta: dict | None = None) -> list[str]:
    """Return the deduplicated, order-preserving list of link targets (wikilinks + markdown links).
    Deterministic; no model. An empty unit → [] (a structural absence, not an error)."""
    if not isinstance(text, str):
        return []
    seen: list[str] = []
    for m in _WIKILINK.finditer(text):
        t = m.group(1).strip()
        if t and t not in seen:
            seen.append(t)
    for m in _MDLINK.finditer(text):
        t = m.group(1).strip()
        if t and t not in seen:
            seen.append(t)
    return seen


LIFTER = {
    "id": "links",
    "extract": _extract,
    "desc": "the outbound links ([[wikilinks]] + [md](targets)) as a list (structural; deterministic)",
}
