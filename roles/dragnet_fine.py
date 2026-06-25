"""roles/dragnet_fine.py — the dragnet stage-2 NEUTRAL deep extraction role (unify-exercise 2026-06-26).

Was ops/dragnet_extract._fine_role(); now a first-class registry row. Schema is the FROZEN
contracts.dragnet_schema.Fine (fine ⊇ coarse — the one superset, D1). The _build_role dragnet-family
freeze door requires output_schema to be exactly Fine and forbids schema_slot. PROTECTED.
"""
from contracts.dragnet_schema import Fine, FINE_PROMPT

ROLE = {
    'id': 'dragnet_fine',
    'label': 'Dragnet: fine extraction (neutral, stage-2)',
    'description': 'Stage-2 of the dragnet bake: a NEUTRAL deep representation into the fine superset facet '
                   '{summary, entities, claims, relations, open_questions}. Only chunks the step-gate marks '
                   'deepen here (decision|spec|discussion).',
    'prompt_template': FINE_PROMPT,      # frozen canonical (exact-match enforced by the _build_role door)
    'output_schema': Fine,
}
