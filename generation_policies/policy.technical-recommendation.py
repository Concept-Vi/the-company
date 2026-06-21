"""generation_policies/policy.technical-recommendation.py — the technical-recommendation EXPLANATION regime (decision-subtype cross-lane).

Authored 2026-06-21 (fork) to meet decision_subtypes/cross-lane.py's explanation_policy id (meet-at-the-
contract). The SAMPLING regime for the RHM's explanation of a cross-lane decision; the explanation FRAMING
is the resolved-slots prompt_slot's job (resolved by the subtype coordinate), NOT this policy. id MUST
equal the file stem ('policy.technical-recommendation').
"""

GENERATION_POLICY = {
    "id": "policy.technical-recommendation",
    "rep_penalty_ladder": [1.1],        # single light rung — explanation prose, not the grammar-constrained loop surface
    "diff_against_source": False,       # prose, not enumerative — the diff guard does not apply
    "json_schema": False,               # free-prose explanation (not structured)
    "temperature": 0.1,
    "desc": 'cross-lane-subtype explanations: the technical trade-off + the recommended option + why. Near-greedy for precise technical prose; light rep-penalty, prose (framing via prompt_slot).',
}
