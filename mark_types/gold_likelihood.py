"""mark_types/gold_likelihood.py — SEED mark-type: gold-likelihood (the surface direction).

The disposition a mark-pass writes to SURFACE a unit as likely-gold (the MEANING the corpus reframe
chases, not surface artifact). The gold-likelihood PROFILE is a READ over findings composed with
evidence (never a stored opaque score — the operator sees-why + can overrule). A `score`-shaped value,
direction `surface` (positive signal). See runtime/mark_types.py + mark_types/AGENTS.md. Its `id` MUST
equal the file stem (`gold_likelihood`).
"""

MARK_TYPE = {
    "id": "gold_likelihood",
    "value_shape": "score",
    "direction": "surface",
    "desc": "likelihood this unit is gold (meaning, not surface) — a READ over findings+evidence, operator-overrulable",
}
