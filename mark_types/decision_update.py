"""mark_types/decision_update.py — INTERACTION mark-type: decision_update (the RHM PROPOSES a card refinement).

L5 (the card-update wire — Tim greenlit 2026-06-22: "I want the assistant to update whatever is on screen";
the decision card is the FIRST instance, the mechanism generalizes). The RHM proposes a refinement to a
decision card — sharpen the meaning, edit an option, tighten legibility. Like `decision_take` it is a MARK on
the canonical decision address; the ROW never mutates; `compose_definition` folds the ACCEPTED updates onto
the row (registry-is-truth on the DEFINITION, exactly as `compose_state` applies it to STATE).
  • `target`    = the canonical decision://global/<id> (contracts.address.decision_address).
  • `value`     = {field, value} — `field` ∈ the CONTENT whitelist (meaning·options·legibility·dimensions·
                  device); NEVER subtype/id/address/scope (the structural blast-radius). `value` = the proposed
                  new field value.
  • `by`        = "rhm" (the proposer — the actor discriminator; an RHM proposal is NOT an operator decide).
  • `rationale` = (optional) why the RHM proposes it — shown on the card beside the proposal.

INERT until accepted: a decision_update ALONE does NOT compose (it is the visible PROPOSAL). An operator
`decision_update_accept` (the LIGHT operator-confirm — A/#1b held, so no security-token) makes the matching
update compose. MODEL A by construction: the AI proposes, the operator applies — the AI never silently
rewrites what Tim decides ON. direction `surface` (operator-facing input); id MUST equal the file stem.
"""

MARK_TYPE = {
    "id": "decision_update",
    "value_shape": "free",
    "direction": "surface",
    "desc": "the RHM's PROPOSED refinement of a decision card — value = {field, value} (field in the content "
            "whitelist meaning/options/legibility/dimensions/device), by=rhm, target = the canonical "
            "decision://global/<id>. INERT until a decision_update_accept; compose_definition folds the "
            "accepted updates onto the row (the row never mutates; Model A — the AI proposes, the operator applies).",
}
