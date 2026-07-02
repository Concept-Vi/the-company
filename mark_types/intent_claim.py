"""mark_types/intent_claim.py — CIRCUIT mark-type: intent_claim (an executor CLAIMS an intent, with a lease).

④ L5-CIRCUIT (organ-studies/CIRCUIT.md §4 "Intent lifecycle = marks only"): the mark an executor writes
when it takes an `intent://<frame>/<id>` to run. The mark record carries (open record, beside target/ts):
  • `by`          — the claiming principal (agent://…, operator://…) — who asserts liveness.
  • `session`     — the live execution handle (session://<sid>/step/<tid> or run://…) — WHERE it runs.
  • `lease_until` — ISO ts; the liveness assertion's EXPIRY. The zombie-killer's heart: a claim is only
                    "running" while `now <= lease_until` (runtime/circuit.compose_state — THE CLOCK IN THE
                    FOLD). Past it, with no terminal, the intent composes to LAPSED — derived, NO reaper.
  • `references_take` — optional; the proposal address whose decision_take AUTHORIZED this claim. The
                    instant a claim references a take, that take becomes non-retractable (C5.4 — the
                    approval-retract window is bounded by the claim).
State is NEVER a stored column: runtime/circuit.compose_state folds claim/heartbeat/suspend/terminal marks
+ the clock into pending|running|suspended|lapsed|terminal. Historical pours may synthesize a claim with a
ZERO-LENGTH lease (lease_until == ts): honest — liveness was never proven, so it lands already LAPSED.
direction `surface` (a lifecycle assertion, positive signal). id MUST equal the file stem (`intent_claim`).
"""

MARK_TYPE = {
    "id": "intent_claim",
    "value_shape": "free",
    "direction": "surface",
    "desc": "an executor claims an intent:// target — record fields by (principal), session (live run "
            "handle), lease_until (liveness expiry; the fold derives running/lapsed from it against the "
            "clock, no reaper), references_take? (the authorizing decision_take's proposal address — "
            "bounds the approval-retract window)",
}
