"""design/_system/prose_check.py — the DETERMINISTIC voice floor (the re-jury's lesson, 2026-06-10:
two prompt calibrations could not make a 4B reliably scope its judgment to two fields — so the voice
judgment moves to the floor, where field-scoping is a dict access and leakage is a pattern match.
The same arc as refcheck: don't rest correctness on the model; the model raises, the floor decides).

check_prose(dossier) inspects ONLY howto.what + howto.what_you_can_do (the two fields the operator
reads at a glance) for CODE LEAKAGE — the closed, mechanical definition of jargon:
  · file paths / extensions (suite.py, App.tsx, runtime/…)
  · HTML/markup (tags, </, selectors like .class #id)
  · address schemes mid-prose (ui://, run://, code://)
  · feature-id shapes (INB-coa, RUN-run — UPPER-dash-lower)
  · code identifiers (snake_case_calls(), camelCase beyond common English, dunder)
Domain vocabulary (activity feed, node, diff, inbox, wire, canvas) is the operator's language and
NEVER flagged — the deny-list is structural code shapes, not words. Returns {passed, hits:[...]}.
Deterministic: same dossier, same verdict."""
import re

_PATTERNS = (
    ("file-path", re.compile(r"\b[\w./-]+\.(py|tsx?|jsx?|json|md|css|html)\b")),
    ("markup", re.compile(r"</?[a-z]+[^>]*>|&[a-z]+;")),
    ("selector", re.compile(r"(?<![\w])[.#][a-z][\w-]*\s*\{|\[data-[\w-]+\]")),
    ("address-scheme", re.compile(r"\b(ui|run|cas|code|vec|skill|context)://")),
    ("feature-id", re.compile(r"\b[A-Z]{2,}-[a-z][\w-]*\b")),
    ("identifier", re.compile(r"\b\w+_\w+\(|\b__\w+__\b|\b[a-z]+[A-Z][a-z]+[A-Z]\w*\b")),
)


def check_prose(dossier: dict) -> dict:
    howto = dossier.get("howto") or {}
    text = " ".join(str(howto.get(f) or "") for f in ("what", "what_you_can_do"))
    hits = []
    for name, pat in _PATTERNS:
        m = pat.search(text)
        if m:
            hits.append({"kind": name, "match": m.group(0)[:40]})
    return {"passed": not hits, "hits": hits}
