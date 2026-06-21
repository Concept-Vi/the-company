"""mark_types/decision_update_accept.py — INTERACTION mark-type: decision_update_accept (operator APPLIES an RHM update).

L5's operator twin to `decision_update`. The RHM PROPOSES (decision_update, inert); the operator ACCEPTS here
→ the matching update composes onto the card definition (compose_definition). MODEL A: the AI never silently
rewrites what Tim decides ON — only an operator accept applies it.

A LIGHT operator-confirm, NOT a security-gate (Tim's fully-open lean 2026-06-22 + the #1b token-enforcement
held OFF → this is just the operator's accept, operator-attributed; no token required). The discriminator that
keeps the AI from self-applying is the ACTOR + the mark-type, not a cryptographic gate.
  • `target` = the canonical decision://global/<id>.
  • `value`  = the accepted `decision_update`'s `ts` (the store-assigned mark ts) — names WHICH proposal this
               accept applies (per-field latest-accepted-by-ts in the fold).
  • `by`     = (optional) the operator.

A `decision_update_reject` twin (operator) drops a pending/applied update (append-only, audit-preserving, like
`decision_retract`). direction `surface`; id MUST equal the file stem.
"""

MARK_TYPE = {
    "id": "decision_update_accept",
    "value_shape": "free",
    "direction": "surface",
    "desc": "the operator APPLIES an RHM decision_update — value = the accepted update's ts, target = the "
            "canonical decision://global/<id>. Makes the matching decision_update compose onto the card "
            "definition (Model A: the AI proposes, the operator applies). A light operator-confirm (A held — "
            "no #1b token); the actor+mark-type is the discriminator, not a security-gate.",
}
