"""decision_subtypes/authorize.py — APPROVE/HOLD a consequential (often security) action.
Derived from the gather: C2 merge-SA-authorize, F3 connector-#1b-flip (also covers the approve/hold shape of any
'enable-this-once-it's-proven-safe' call). Binary, security-framed."""

DECISION_SUBTYPE = {
    "id": "authorize",
    "card_variant": "binary",                       # DNA's two-panel (built) — approve | hold, side-by-side
    "explanation_policy": "policy.risk-grounding",  # fork: explain the security/risk + what-could-go-wrong + the condition
    "owner": "tim",                                 # Tim's queue — the operator-stack surfaces these to him
    "required_elements": ["action", "option_implication", "security_condition", "gate"],
    "desc": "Approve/hold a consequential action (often security) — each side's implication + the 'so long as "
            "it's secure' CONDITION + the gate. Covers: merge-SA-write authorize · connector full-access flip.",
}
