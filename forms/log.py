"""forms/log.py — SEED form: a LOG (bookkeeping — route to the cheap/skip band).

Recognises a log-shaped unit (timestamped lines / a HANDOFF/STATE/changelog header) — ~half a corpus
is bookkeeping; DON'T burn full capture depth on logs. Routes to the `legibility` band (the cheap broad
pass) with the cheap `prose_default` policy. Effort-routing-by-form made DATA. See runtime/forms.py +
forms/AGENTS.md. id MUST equal the file stem (`log`).
"""
from __future__ import annotations

import re

_TS = re.compile(r"^\s*[\[\(]?\d{4}-\d{2}-\d{2}")           # a leading ISO date
_LOGWORD = re.compile(r"\b(changelog|handoff|session log|build log|status)\b", re.I)


def _match(text: str, *, meta: dict | None = None) -> bool:
    if not isinstance(text, str) or not text:
        return False
    head = "\n".join(text.splitlines()[:5])
    if _LOGWORD.search(head):
        return True
    # >=3 timestamped lines = a log
    ts_lines = sum(1 for ln in text.splitlines() if _TS.match(ln))
    return ts_lines >= 3


FORM = {
    "id": "log",
    "match": _match,
    "stage": "legibility",
    "policy": "prose_default",
    "desc": "a log/changelog/handoff (bookkeeping) — the cheap broad pass, don't burn deep capture on it",
}
