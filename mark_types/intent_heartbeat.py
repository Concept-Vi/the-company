"""mark_types/intent_heartbeat.py — CIRCUIT mark-type: intent_heartbeat (the lease EXTENDED, liveness re-asserted).

④ L5-CIRCUIT (organ-studies/CIRCUIT.md §4): the mark a live executor appends to EXTEND its claim's lease —
the continuous liveness assertion that makes zombies impossible BY CONSTRUCTION ("dead executors can't lie:
the lie requires continuously asserting liveness"). Record field (open record, beside target/ts):
  • `lease_until` — ISO ts; the NEW expiry. compose_state's effective lease = the max lease_until across
                    the claim and every heartbeat written after it (runtime/circuit.py).
A heartbeat is only legal while the intent composes to RUNNING (its claim's lease still live) — a heartbeat
on an unclaimed or already-LAPSED intent is a grammar violation and FAILS LOUD (a lapsed executor must
RE-CLAIM, never silently resurrect). direction `surface`. id MUST equal the file stem (`intent_heartbeat`).
"""

MARK_TYPE = {
    "id": "intent_heartbeat",
    "value_shape": "free",
    "direction": "surface",
    "desc": "a live executor extends its intent claim's lease — record field lease_until (new expiry); "
            "legal only while the intent composes to running (a lapsed executor re-claims, never "
            "heartbeats back to life)",
}
