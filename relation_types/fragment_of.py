"""relation_types/fragment_of.py — SEED relation-type: fragment-of (DIRECTED, with an inverse).

A directed edge: unit A is a FRAGMENT OF unit B (A→B, the part→whole). Carries an `inverse`
(`has_fragment`, the whole→part direction) to exercise the inverse field. Computed over the `topics`
space (a fragment shares its whole's topics). See runtime/relation_types.py + relation_types/AGENTS.md.
Its `id` MUST equal the file stem (`fragment_of`).
"""

RELATION_TYPE = {
    "id": "fragment_of",
    "label": "fragment-of",
    "directed": True,
    "inverse": "has_fragment",
    "near": "topics",
    "desc": "A is a fragment of the whole B (part→whole; directed A→B, inverse has-fragment)",
}
