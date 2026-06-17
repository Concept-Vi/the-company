"""lifters/frontmatter.py — SEED lifter: extract YAML frontmatter (a `produced_by:"code"` projection).

A deterministic structural EXTRACTOR — reads the leading `---`-fenced YAML block of a markdown unit
and returns it as a dict. NO model call (the code half of the projection split). A PARSE is a READ
(the floor C9.2 holds — no resolve/dispatch). See runtime/lifter_registry.py + lifters/AGENTS.md. Its `id`
MUST equal the file stem (`frontmatter`).
"""
from __future__ import annotations


def _extract(text: str, *, meta: dict | None = None) -> dict:
    """Return the leading `---`…`---` frontmatter as a dict (best-effort line `key: value`), or {} if
    none. Deterministic; no model. Uses PyYAML if available, else a minimal line parser (fail-soft to
    {} on a non-frontmatter unit — a structural ABSENCE is a valid extraction, not an error)."""
    if not isinstance(text, str):
        return {}
    s = text.lstrip()
    if not s.startswith("---"):
        return {}
    end = s.find("\n---", 3)
    if end == -1:
        return {}
    block = s[3:end].strip("\n")
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(block)
        return data if isinstance(data, dict) else {}
    except Exception:
        out: dict = {}
        for line in block.splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                out[k.strip()] = v.strip()
        return out


LIFTER = {
    "id": "frontmatter",
    "extract": _extract,
    "desc": "the leading YAML frontmatter block as a dict (structural; deterministic)",
}
