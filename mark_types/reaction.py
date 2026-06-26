"""mark_types/reaction.py — INTERACTION mark-type: reaction (operator reaction-stamp at an element).

The disposition the operator writes via a reaction-stamp on a rendered gallery element (good/wrong/
explain/remember_this/do_this — wildcard's taxonomies.json reactions) — the route-back of
`gallery:direction` → `territory_write` → `suite.mark`. `value` is the reaction label. direction
`surface` (operator input). An INTERACTION mark-type, beside the analysis types; additive,
registry-is-truth. id MUST equal the file stem (`reaction`).
"""

MARK_TYPE = {
    "id": "reaction",
    "value_shape": "label",
    "direction": "surface",
    "desc": "an operator reaction-stamp at an addressed element (value = good/wrong/explain/remember_this/do_this) — the route-back of gallery:direction",
}
