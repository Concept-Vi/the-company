"""roles/dragnet_coarse.py — the dragnet stage-1 NEUTRAL coarse extraction role (unify-exercise 2026-06-26).

Was constructed in-code as ops/dragnet_extract._coarse_role(); now a first-class file-discovered registry
row so the dragnet is configurable/composable through the same registry as every other role. The schema is
the FROZEN contracts.dragnet_schema.Coarse (imported, never authored here) and the prompt carries the
non-authorable NEUTRAL_FRAGMENT verbatim — the _build_role dragnet-family freeze door enforces both, so
this row CANNOT fork the locked superset (D1) or smuggle relevance/topic into the neutral coarse pass (D3).
PROTECTED (suite._SUITE_OWNED_PROTECTED_ROLES): edit_role/delete_role refuse.
"""
from contracts.dragnet_schema import Coarse, NEUTRAL_FRAGMENT

ROLE = {
    'id': 'dragnet_coarse',
    'label': 'Dragnet: coarse extraction (neutral, stage-1)',
    'description': 'Stage-1 of the dragnet extract-once bake: describes a chunk NEUTRALLY into the coarse '
                   'superset facet {about, kind, touches}. No relevance/topic judgement (D3). The step-gate '
                   'decides which chunks deepen to fine.',
    'prompt_template': (
        f"Read the content and {NEUTRAL_FRAGMENT}.\n"
        "Content:\n{utterance}\n\n"
        "Return ONLY JSON: {\"about\": \"what this is in one phrase\", "
        "\"kind\": \"decision|spec|discussion|digest|log|reference|other\", "
        "\"touches\": [\"topic tags\"]}"
    ),
    'output_schema': Coarse,
}
