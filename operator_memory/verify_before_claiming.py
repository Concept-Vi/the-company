"""operator_memory/verify_before_claiming.py — MINED proposal (GC15 grow-circuit; awaits Tim's
confirmation — the claim/commit half of the verify family, 50 occurrences)."""
MEMORY = {
    "id": "verify_before_claiming",
    "rule": "Never claim, record, or commit a status that hasn't been executed-and-checked — no green-painting, no 'addressed' from reading, honest ✅/🟡/🔴 splits always.",
    "why": "50 mined occurrences (11 variants). False 'it's fixed' is a named business harm for Tim — credibility erodes per incident.",
    "evidence": [
        {"quote": "stop sending prose updates or guessing on merge status; instead, investigate the built work first, then merge", "source": "mined exchange"}],
    "scope": {"when": "writing any status, handoff, commit message, or completion claim"},
    "status": "proposed",
}
