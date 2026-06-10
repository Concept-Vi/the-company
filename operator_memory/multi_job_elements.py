"""operator_memory/multi_job_elements.py — context decides; things legitimately do multiple jobs (GC15 row)."""
MEMORY = {
    "id": "multi_job_elements",
    "rule": "When sources disagree about what a thing is, consider that it legitimately does MULTIPLE jobs depending on context before forcing one winner — record the contextual faces, don't flatten them.",
    "why": "His designs are polymorphic; one surface serving several roles by system state is intent, not inconsistency. 'The winner is based on context.'",
    "evidence": [
        {"quote": "it sounds like there are elements that do multiple jobs depending on what else is happening in the system, so that's something to be aware of and will have to be accounted for", "source": "2026-06-10, Decision 2"},
        {"quote": "yeah the winner I figure is based on context", "source": "2026-06-10"}],
    "scope": {"when": "resolving conflicting descriptions/definitions of one thing"},
    "status": "confirmed",
    "confirmed": "2026-06-10 (first instances: ui://toolbar/layers and ui://chat/walk carry multi-role faces)",
}
