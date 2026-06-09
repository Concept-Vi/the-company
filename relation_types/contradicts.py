"""relation_types/contradicts.py — SEED relation-type: contradicts (DIRECTED — a tension).

A directed edge: unit A CONTRADICTS unit B. Directed because the contradicting claim has a source and a
target (A makes a claim against B's claim). The inversion-finder reads it over the `principles` space
(NEAR) but flags B in the FAR/opposed sense — the contradiction surfaces a tension for review
(render-not-judge: the operator decides). The relation that the `contradiction` mark-type stamps. See
runtime/relation_types.py + relation_types/AGENTS.md. Its `id` MUST equal the file stem (`contradicts`).
"""

RELATION_TYPE = {
    "id": "contradicts",
    "label": "contradicts",
    "directed": True,
    "near": "principles",
    "far": "principles",
    "desc": "A contradicts B (a tension surfaced for review; directed A→B; render-not-judge)",
}
