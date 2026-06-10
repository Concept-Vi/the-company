"""operator_memory/investigate_before_coding.py — MIGRATED from the harness notes (B5 batch 2; awaits
Tim's confirmation)."""
MEMORY = {
    "id": "investigate_before_coding",
    "rule": "Never guess at solutions — read the actual code paths, get actual evidence, research the actual problem BEFORE writing any code. Indirect verification (e.g. desktop eval for mobile) is not verification.",
    "why": "His repeatedly-called-out pattern: guess → code → fake-pass → he tests → broken → repeat. Wastes his time, compounds credibility damage.",
    "evidence": [{"quote": "The pattern: guess at the problem → write code → run desktop eval → say 'PASS' → Tim tests → it's broken → repeat. This wastes Tim's time and compounds credibility damage.",
                  "source": "standing harness note from his repeated corrections across sessions"}],
    "scope": {"when": "before writing any fix or feature code"},
    "status": "proposed",
}
