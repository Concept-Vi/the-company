"""mark_types/intent_created.py — CIRCUIT mark-type: intent_created (the intent's immutable row, as its birth mark).

④ L5-CIRCUIT, C5.3 (the historical pour): "every circuit object is an immutable, addressed row" — and the
row LANDS as a mark on its own `intent://<frame>/<uuid>` address (data=DB: container.mark; vocabulary=this
file). The open record carries the row verbatim-in-spirit: `intent_type`, `by` (actor_id), `user_id`,
`required_autonomy`, `input_params`, `correlation_id` (→ thread://), `source`, `status_at_pour` (what the
mutated column CLAIMED at pour time — provenance, never authority), plus pour provenance
(`source_system`='cvi_mine', `source_uuid`). ts = the original created_at (append_mark honours a carried ts).
compose_state does NOT read this mark (creation isn't a transition — no claim ⇒ pending already); it is the
address's row-of-record + the reconciliation's landing proof. direction `surface`. id MUST equal the file
stem (`intent_created`).
"""

MARK_TYPE = {
    "id": "intent_created",
    "value_shape": "free",
    "direction": "surface",
    "desc": "the intent's immutable row landed as its birth mark on intent://<frame>/<uuid> — carries "
            "intent_type/by/required_autonomy/input_params/correlation_id + pour provenance "
            "(source_system, source_uuid, status_at_pour); not a lifecycle transition (no claim is "
            "already pending)",
}
