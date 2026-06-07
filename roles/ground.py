"""roles/ground.py — the GROUND role (Concurrent Cognition G2 · C2.3 listening cast).

GROUNDS the turn in citable facts: live state → whether the utterance is in scope + a one-line
grounding note. MIGRATED from cognition.py's `GROUND_ROLE`/`GroundOut` (canonical def now lives here).
Fireable; part of the `listening` cast. Its `in_scope` is read by recall's injection rule (the
multi-field pure rule the G0 spike proved).
"""
from pydantic import BaseModel


class GroundOut(BaseModel):
    """`ground` reads live state → whether the utterance is IN SCOPE + a one-line citable grounding note."""
    in_scope: bool
    note: str


ROLE = {
    "id": "ground",
    "label": "Ground (citable facts)",
    "description": "Live state → whether the utterance is in scope for the system + a citable grounding note.",
    "prompt_template": (
        "You are the GROUND role — you check whether the operator's utterance is IN SCOPE for the "
        "Company system (a composition/cognition suite the operator builds with AI). Return ONLY JSON "
        "with two fields:\n"
        '  "in_scope": a boolean — true if answering this is a legitimate task for the system,\n'
        '  "note": a one-line grounding note.\n'
        'Example: {"in_scope": true, "note": "A question about a past architecture decision is in scope."}'
    ),
    "output_schema": GroundOut,
    "input_addresses": ("utterance", "live_state"),
    "trigger": "fires in the listening cast when focus.which_roles includes 'ground'.",
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    "mode_scope": {"listening"},
    "rules": [
        {"id": "ground-gates-inject", "reads": "ground.in_scope",
         "effect": "co-determines recall injection (recall.relevant AND ground.in_scope)", "kind": "gate"},
    ],
    "render_hint": {"shape": "fact", "lane": "ground"},
}
