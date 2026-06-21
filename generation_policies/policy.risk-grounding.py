"""generation_policies/policy.risk-grounding.py — the risk-grounding EXPLANATION regime (decision-subtype authorize).

Authored 2026-06-21 (fork) to meet decision_subtypes/authorize.py's explanation_policy id (meet-at-the-
contract). The SAMPLING regime for the RHM's explanation of a authorize decision; the explanation FRAMING
is the resolved-slots prompt_slot's job (resolved by the subtype coordinate), NOT this policy. id MUST
equal the file stem ('policy.risk-grounding').
"""

GENERATION_POLICY = {
    "id": "policy.risk-grounding",
    "rep_penalty_ladder": [1.1],        # single light rung — explanation prose, not the grammar-constrained loop surface
    "diff_against_source": False,       # prose, not enumerative — the diff guard does not apply
    "json_schema": False,               # free-prose explanation (not structured)
    "temperature": 0.0,
    "desc": "authorize-subtype explanations: ground the security/risk + what-could-go-wrong + the condition. Greedy (temp 0) — careful + precise on a security call; light rep-penalty, prose (the FRAMING rides the explain-role's prompt_slot).",
}
