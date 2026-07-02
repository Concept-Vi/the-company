"""mark_types/intent_suspend.py — CIRCUIT mark-type: intent_suspend (paused mid-walk, awaiting something).

④ L5-CIRCUIT (organ-studies/CIRCUIT.md §4): the mark written when an intent's walk PAUSES at a step to
await input (A's wizard seam, generalized). Record fields (open record, beside target/ts):
  • `at_step`  — where the walk paused (a step id/ordinal/address).
  • `awaiting` — what it waits on (human input, an approval, an external event — legible, in words).
compose_state: a suspend NEWER than the latest claim → SUSPENDED (the lease clock stops mattering — the
executor deliberately parked it; no lapse while parked). A LATER claim resumes it (suspended intents stay
re-claimable — the historical wizard rows land this way, pendings stay re-claimable). A terminal still
wins over everything. direction `surface`. id MUST equal the file stem (`intent_suspend`).
"""

MARK_TYPE = {
    "id": "intent_suspend",
    "value_shape": "free",
    "direction": "surface",
    "desc": "an intent's walk paused awaiting something — record fields at_step (where), awaiting (what, "
            "in words); newer-than-claim → composes to suspended; a later claim resumes it",
}
