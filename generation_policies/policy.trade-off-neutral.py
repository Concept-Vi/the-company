"""generation_policies/policy.trade-off-neutral.py — the trade-off-neutral EXPLANATION regime (decision-subtype trade-off).

Authored 2026-06-21 (fork) to meet decision_subtypes/trade-off.py's explanation_policy id (meet-at-the-
contract). The SAMPLING regime for the RHM's explanation of a trade-off decision; the explanation FRAMING
is the resolved-slots prompt_slot's job (resolved by the subtype coordinate), NOT this policy. id MUST
equal the file stem ('policy.trade-off-neutral').
"""

GENERATION_POLICY = {
    "id": "policy.trade-off-neutral",
    "rep_penalty_ladder": [1.1],        # single light rung — explanation prose, not the grammar-constrained loop surface
    "diff_against_source": False,       # prose, not enumerative — the diff guard does not apply
    "json_schema": False,               # free-prose explanation (not structured)
    "temperature": 0.2,
    "desc": 'trade-off-subtype explanations: lay out the axes NEUTRALLY + a recommendation, no prejudging. A touch of temperature for readable neutral prose; light rep-penalty, prose (framing via prompt_slot).',
}
