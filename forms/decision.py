"""forms/decision.py — SEED form: a DECISION note (substance — route to DEEP).

Recognises a decision-shaped unit (a Dn / "decision:" / "decided" / "resolved" header). Decisions are
high-substance (the spine of the build) — route to the `deep` band (the heavier capture pass) with the
`capture_default` policy (the rep_penalty ladder regime). The seed that EXERCISES the deep band. See
runtime/forms.py + forms/AGENTS.md. id MUST equal the file stem (`decision`).
"""
from __future__ import annotations

import re

_DECWORD = re.compile(r"\b(decision|decided|resolved|verdict)\b|\bD\d+\b", re.I)


def _match(text: str, *, meta: dict | None = None) -> bool:
    if not isinstance(text, str) or not text:
        return False
    head = "\n".join(text.splitlines()[:8])
    return bool(_DECWORD.search(head))


FORM = {
    "id": "decision",
    "match": _match,
    "stage": "deep",
    "policy": "capture_default",
    "desc": "a decision note (high-substance, the spine) — the heavier deep capture pass",
}
