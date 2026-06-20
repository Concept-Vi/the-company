"""mark_types/decision_retract.py — INTERACTION mark-type: decision_retract (the operator's UN-DECIDE).

The symmetric TWIN of decision_take: the disposition the operator writes to UN-DECIDE an addressed decision —
the retract that returns a `decision://<frame>/<id>` from `decided` back to `pending`. It is the operator-undo /
"Change" primitive AND the safe, append-only way to neutralise a mistaken or contaminated take WITHOUT deleting
the audit trail. Same write-path as decision_take (runtime.territory.territory_write → suite.mark, behind the
SAME #1b genuine-operator-attribution floor) and the same canonical target — a true twin, not a fork.
  • `target` = the decision's CANONICAL address (contracts.address.decision_address — `decision://global/<id>`,
    frame explicit) so a retract written via the bare form and a row resolved via the global form share ONE key.
  • `value`  = empty/optional (a retract carries no chosen option; an optional human `note` may ride a field).
  • `by`     = (optional) who retracted (the operator).
The decision resolver (runtime/cognition.py → runtime.decision_registry.compose_state) folds the LATEST decision
EVENT by ts: a `decision_retract` appended AFTER a take (newer ts) WINS → pending; a still-later `decision_take`
re-decides. registry-is-truth: the retract IS the artifact; the decision row never mutates.

NOTE (registry-is-truth — the id is `decision_retract`, underscore): the registered id MUST equal the file stem
(the mark_types law), and the writer (territory_write / the gated `mark` tool) + the resolver BOTH use the exact
string `decision_retract` — `suite.mark(canonical_addr, "decision_retract", ...)`. A hyphen-form would fail loud
(unknown mark_type). This file is what makes the un-decide a LEGITIMATE gated write: before it existed, the fold
could READ a retract but nothing could WRITE one through the gate (the `mark` tool refuses an unregistered type).

direction `surface` (operator input — a positive operator signal, like decision_take/comment; not a
denoise/subtract). An INTERACTION mark-type beside decision_take/comment/reaction/favour; additive. id MUST
equal the file stem (`decision_retract`).
"""

MARK_TYPE = {
    "id": "decision_retract",
    "value_shape": "free",
    "direction": "surface",
    "desc": "the operator's UN-DECIDE of an addressed decision — the symmetric twin of decision_take; "
            "target = the canonical decision://global/<id>, value empty (optional human note) — the LATEST "
            "retract by ts returns the decision decided→pending (a still-later take re-decides); the "
            "operator-undo, append-only (keeps the audit trail), same write-path + #1b floor as decision_take",
}
