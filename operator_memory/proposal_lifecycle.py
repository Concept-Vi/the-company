"""operator_memory/proposal_lifecycle.py — Tim's articulated propose->accept->build->Real circuit (GC15 row)."""
MEMORY = {
    "id": "proposal_lifecycle",
    "rule": "Proposals of every kind (ideas, changes, refinements, features) accumulate as registry rows pointing at where they're proposed; Tim's acceptance is the trigger that fires the backend build; completion flips the row Real.",
    "why": "This is the system's growth circuit as he intends it — the registries are the queue, his gate is the ignition, the build machinery is the engine, Real status is the proof.",
    "evidence": [{"quote": "they can be all sorts of ideas and proposals and changes and refinements and once they get accepted or submitted by me, that then runs the process of the backend build and the registries end making them Real", "source": "2026-06-10, Decision 3"}],
    "scope": {"when": "designing any propose/approve/build flow"},
    "status": "confirmed",
    "confirmed": "2026-06-10 (first instances: 8 status='proposed' features with proposed_at addresses in design/register.json)",
}
