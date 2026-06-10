"""operator_memory/no_unconditional_deferrals.py — deferrals need a return-condition (GC15 row)."""
MEMORY = {
    "id": "no_unconditional_deferrals",
    "rule": "Tim does not accept deferrals. The ONLY legitimate deferral is condition-addressed: stored in system memory with an explicit return-when, so it comes back by itself when the condition is now.",
    "why": "Parked work in a 100%-AI-driven system is silently lost work — no human re-reads to remember it. A condition makes a deferral a scheduled return instead of a drop.",
    "evidence": [
        {"quote": "I suppose you can defer specifically that, normally I don't accept deferrals. However you will need to put it into system memory", "source": "2026-06-10, Decision 4"},
        {"quote": "it needs to be memory that can be returned to when certain things happen", "source": "2026-06-10, the common-memory directive"}],
    "scope": {"when": "any work is about to be parked or sequenced away"},
    "status": "confirmed",
    "confirmed": "2026-06-10 (the deferred-27 is the first conditional memory: deferred://rg10/static-unverifiable-27)",
}
