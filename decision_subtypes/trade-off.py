"""decision_subtypes/trade-off.py — a multi-option DIRECTION/architecture choice with trade-offs.
Derived from the gather: C1 substrate-home/#75, C3 Claude-Design-adoption, D1 synthetic-richness-ceiling, D2
keystone-flow-visuals (the 3+-option strategy/architecture decisions). The dominant kind in the set."""

DECISION_SUBTYPE = {
    "id": "trade-off",
    "card_variant": "n-panel",                          # DNA's 3+-option layout — the directions side-by-side
    "explanation_policy": "policy.trade-off-neutral",   # fork: lay out the axes NEUTRALLY + a recommendation (no prejudging)
    "required_elements": ["options", "trade_off_axes", "unblocks"],
    "desc": "A multi-option direction/architecture choice — 3+ options as DIRECTIONS, their trade-off axes, and "
            "what each UNBLOCKS / its blast-radius; axes laid out neutrally + a rec. Covers: substrate-home(#75) · "
            "Claude-Design-adoption · synthetic-richness-ceiling · keystone-flow-visuals.",
}
