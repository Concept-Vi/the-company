"""relation_types/sibling.py — SEED relation-type: sibling (SYMMETRIC).

A SYMMETRIC edge: units A and B are siblings — same level, shared parent/topic, neither beneath the
other (A↔B). The seed that EXERCISES the symmetric (directed=False) branch — find_relations records
both ends, no from/to. Computed over the `topics` space. See runtime/relation_types.py +
relation_types/AGENTS.md. Its `id` MUST equal the file stem (`sibling`).
"""

RELATION_TYPE = {
    "id": "sibling",
    "label": "sibling",
    "directed": False,
    "near": "topics",
    "desc": "A and B are siblings — same level, shared topic, neither beneath the other (symmetric A↔B)",
}
