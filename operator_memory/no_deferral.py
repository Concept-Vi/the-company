"""operator_memory/no_deferral.py — MIGRATED (B5 batch 2; awaits Tim's confirmation). The general
form; no_unconditional_deferrals (confirmed) is the conditional-memory refinement."""
MEMORY = {
    "id": "no_deferral",
    "rule": "Don't defer anything — every flagged gap and small item is in-scope and gets WORKED, never parked as 'minor/later/someday'. Sequencing is fine; deferral is not.",
    "why": "'There should never be any deferrals' — parked items in an AI-driven system are silently lost; the backlog is for ordering, not for shelving.",
    "evidence": [{"quote": "Yes, good, implement all. There should never be any deferrals.",
                  "source": "Tim, 2026-06-09"}],
    "scope": {"when": "triaging flagged items or scoping work"},
    "status": "proposed",
}
