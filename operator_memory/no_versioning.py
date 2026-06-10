"""operator_memory/no_versioning.py — MIGRATED from the harness notes (B5 batch 1; awaits Tim's
confirmation — the rule is his, stated 2026-06-01; the migration makes it ALL agents' knowledge)."""
MEMORY = {
    "id": "no_versioning",
    "rule": "Never create v2 / Round-N / dated / '-updated' copies of content — update the SAME canonical file in place every pass; the event log is the history.",
    "why": "AI versioning content is a named frustration: parallel copies strand truth across sessions and nobody knows which file is real.",
    "evidence": [{"quote": "Tim does NOT want versioned content. Never create 'v2', 'Round 2', '-updated', dated copies, or parallel pass-files. Update the SAME canonical file in place on every iteration.",
                  "source": "standing harness note, encoded 2026-06-01 from his correction"}],
    "scope": {"when": "writing or updating any document/artifact"},
    "status": "proposed",
}
