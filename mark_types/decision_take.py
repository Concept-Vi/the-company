"""mark_types/decision_take.py — INTERACTION mark-type: decision_take (the operator's CHOICE on a decision).

The disposition the operator writes when DECIDING an addressed decision — the take that resolves a
`decision://<frame>/<id>` from `pending` to `decided`. The route-back of the decision-card's take
(wildcard's gallery:direction on a decision element) → runtime.territory.territory_write → suite.mark.
  • `target` = the decision's CANONICAL address (contracts.address.decision_address — `decision://global/<id>`,
    frame explicit) so a take written via the bare form and a row resolved via the global form share ONE key.
  • `value`  = the chosen option's LABEL (= decided_value, per option.schema.json — meaning, never a machine id).
  • `by`     = (optional) who decided (the operator).
The decision resolver (runtime/cognition.py → runtime.decision_registry.compose_state) COMPOSES the resolved
state from the LATEST decision_take mark on the canonical address (registry-is-truth: the take IS the artifact;
the decision row never mutates). decided_at = the mark's `ts` (set by the store on append).

NOTE (registry-is-truth — the id is `decision_take`, underscore): composition's contract calls this
"decision-take" (hyphen) INFORMALLY — the REGISTERED id is `decision_take` (it MUST equal the file stem, the
mark_types law), exactly as `ai_fingerprint` is the registered id of the informally-named "ai-fingerprint".
Writers (territory_write / wildcard / DNA's card-take) and the resolver BOTH use the registered string
`decision_take` — `suite.mark(canonical_addr, "decision_take", value=label, ...)`. A hyphen-form would fail loud
(unknown mark_type).

direction `surface` (operator input — a positive signal, like `comment`; not a denoise/subtract). An
INTERACTION mark-type beside comment/reaction/favour; additive. id MUST equal the file stem (`decision_take`).
"""

MARK_TYPE = {
    "id": "decision_take",
    "value_shape": "free",
    "direction": "surface",
    "desc": "the operator's CHOICE on an addressed decision — value = the chosen option label (= decided_value), "
            "target = the canonical decision://global/<id> — resolves the decision pending→decided; the "
            "route-back of the decision-card take",
}
