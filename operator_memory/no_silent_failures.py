"""operator_memory/no_silent_failures.py — MIGRATED from the harness notes (B5 batch 1; awaits Tim's
confirmation)."""
MEMORY = {
    "id": "no_silent_failures",
    "rule": "Operations either succeed or fail LOUD — a visible notice plus a recorded gap. No silent no-ops, no silent fallbacks, no pretending success when something was skipped.",
    "why": "A silent failure reads as success and corrupts trust in everything downstream; loud failures are recoverable, silent ones compound.",
    "evidence": [{"quote": "do NOT allow silent failures or fallbacks", "source": "Tim, 2026-04-22 (mobile parity triage); restated as the standing fail-loud law across the Company"}],
    "scope": {"when": "any operation that could fail, skip, or degrade"},
    "status": "proposed",
}
