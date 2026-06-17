"""lifters/blocks.py — SEED lifter: extract blocks (a `produced_by:"code"` projection).

A deterministic structural EXTRACTOR — reads a markdown unit and returns its heading-delimited
block structure (a list of {level, heading} for each `#`-heading). NO model call. A PARSE is a READ
(the floor holds). See runtime/lifter_registry.py + lifters/AGENTS.md. Its `id` MUST equal the file stem
(`blocks`).
"""
from __future__ import annotations

import re

_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*#*\s*$")


def _extract(text: str, *, meta: dict | None = None) -> list[dict]:
    """Return the heading-block structure: one {level:int, heading:str} per `#`-heading, in order.
    Deterministic; no model. A unit with no headings → [] (a structural fact, not an error)."""
    if not isinstance(text, str):
        return []
    blocks: list[dict] = []
    for line in text.splitlines():
        m = _HEADING.match(line)
        if m:
            blocks.append({"level": len(m.group(1)), "heading": m.group(2).strip()})
    return blocks


LIFTER = {
    "id": "blocks",
    "extract": _extract,
    "desc": "the heading-block structure ({level, heading} per #-heading) as a list (structural; deterministic)",
}
