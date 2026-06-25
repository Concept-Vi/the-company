"""roles/dragnet_fine.py — the dragnet stage-2 NEUTRAL deep extraction role (unify-exercise 2026-06-26).

Was ops/dragnet_extract._fine_role(); now a first-class registry row. Schema is the FROZEN
contracts.dragnet_schema.Fine (fine ⊇ coarse — the one superset, D1). The _build_role dragnet-family
freeze door requires output_schema to be exactly Fine and forbids schema_slot. PROTECTED.
"""
from contracts.dragnet_schema import Fine

ROLE = {
    'id': 'dragnet_fine',
    'label': 'Dragnet: fine extraction (neutral, stage-2)',
    'description': 'Stage-2 of the dragnet bake: a NEUTRAL deep representation into the fine superset facet '
                   '{summary, entities, claims, relations, open_questions}. Only chunks the step-gate marks '
                   'deepen here (decision|spec|discussion).',
    'prompt_template': (
        "Extract a NEUTRAL deep representation of the content (describe only what it says).\n"
        "Content:\n{utterance}\n\n"
        "Return ONLY JSON: {\"summary\": \"1-2 sentence neutral summary\", "
        "\"entities\": [\"named systems/files/concepts/people\"], "
        "\"claims\": [\"assertions or decisions stated\"], "
        "\"relations\": [\"e.g. 'X depends on Y'\"], "
        "\"open_questions\": [\"unresolved threads, [] if none\"]}"
    ),
    'output_schema': Fine,
}
