"""generation_policies/policy.theorem-grounding.py — the theorem-grounding EXPLANATION regime (decision-subtype theorem-fork).

Authored 2026-06-21 (fork) to meet decision_subtypes/theorem-fork.py's explanation_policy id (meet-at-the-
contract). The SAMPLING regime for the RHM's explanation of a theorem-fork decision; the explanation FRAMING
is the resolved-slots prompt_slot's job (resolved by the subtype coordinate), NOT this policy. id MUST
equal the file stem ('policy.theorem-grounding').
"""

GENERATION_POLICY = {
    "id": "policy.theorem-grounding",
    "rep_penalty_ladder": [1.1],        # single light rung — explanation prose, not the grammar-constrained loop surface
    "diff_against_source": False,       # prose, not enumerative — the diff guard does not apply
    "json_schema": False,               # free-prose explanation (not structured)
    "temperature": 0.0,
    "desc": "theorem-fork-subtype explanations: ground in Tim's OWN math/relationships (never AI-projected gloss). Greedy (temp 0) — precision on the math; light rep-penalty, prose (framing via prompt_slot).",
}
