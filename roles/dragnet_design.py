"""roles/dragnet_design.py — the dragnet visual-dna DESIGN-binding extraction role (unify-exercise 2026-06-26).

Was ops/dragnet_extract._design_role(); now a first-class registry row. Schema is the FROZEN
contracts.dragnet_schema.Design (the 2 additive superset fields, visual-dna ONLY — D2 near-lock). The
_build_role dragnet-family freeze door requires output_schema to be exactly Design and forbids schema_slot.
PROTECTED.
"""
from contracts.dragnet_schema import Design

ROLE = {
    'id': 'dragnet_design',
    'label': 'Dragnet: design-binding extraction (visual-dna only)',
    'description': "visual-dna ONLY — extracts DNA's 2 design fields (criteria 2+5). `resolution` is "
                   "DIMENSION-KEYED: each entry EXACTLY '<dim>:<context> -> <value>' with <dim> ∈ "
                   "{line, opacity, colour_role, shape} so the resolver reads it back per-dimension.",
    'prompt_template': (
        "Extract the DESIGN BINDING of this visual/design content (describe only what it specifies).\n"
        "Content:\n{utterance}\n\n"
        "Return ONLY JSON with two fields:\n"
        "  \"resolves_into\": [\"the design element/component/token this maps to — match keys for lookup\"],\n"
        "  \"resolution\": [\"DIMENSION-KEYED context-points. Each entry EXACTLY in the form "
        "'<dim>:<context> -> <value>' where <dim> is one of line|opacity|colour_role|shape, <context> is the "
        "design situation it applies in, and <value> is the design token/treatment it resolves to. "
        "Examples: 'shape:core -> octagon', 'colour_role:recommended -> gold', 'line:emphasis -> solid', "
        "'opacity:less-realised -> 0.5'. Omit a dim if the content does not bind it.\"]}"
    ),
    'output_schema': Design,
}
