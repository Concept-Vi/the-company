"""roles/dragnet_design.py — the dragnet visual-dna DESIGN-binding extraction role (unify-exercise 2026-06-26).

Was ops/dragnet_extract._design_role(); now a first-class registry row. Schema is the FROZEN
contracts.dragnet_schema.Design (the 2 additive superset fields, visual-dna ONLY — D2 near-lock). The
_build_role dragnet-family freeze door requires output_schema to be exactly Design and forbids schema_slot.
PROTECTED.
"""
from contracts.dragnet_schema import Design, DESIGN_PROMPT

ROLE = {
    'id': 'dragnet_design',
    'label': 'Dragnet: design-binding extraction (visual-dna only)',
    'description': "visual-dna ONLY — extracts DNA's 2 design fields (criteria 2+5). `resolution` is "
                   "DIMENSION-KEYED: each entry EXACTLY '<dim>:<context> -> <value>' with <dim> ∈ "
                   "{line, opacity, colour_role, shape} so the resolver reads it back per-dimension.",
    'prompt_template': DESIGN_PROMPT,    # frozen canonical (exact-match enforced by the _build_role door)
    'output_schema': Design,
}
