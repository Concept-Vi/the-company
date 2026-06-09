"""mark_types/contradiction.py — SEED mark-type: contradiction (a relational disposition).

The disposition a mark-pass writes when a unit contradicts another (the `contradicts` relation made a
mark — a unit-level finding the operator reviews). A `span`-shaped value (the contradicting claim/span);
direction `surface` (it SURFACES a tension for review, not noise to subtract). See runtime/mark_types.py
+ mark_types/AGENTS.md. Its `id` MUST equal the file stem (`contradiction`).
"""

MARK_TYPE = {
    "id": "contradiction",
    "value_shape": "span",
    "direction": "surface",
    "desc": "this unit contradicts another (a tension surfaced for review; render-not-judge — the operator decides)",
}
