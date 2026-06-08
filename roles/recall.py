"""roles/recall.py — the RECALL role (Concurrent Cognition G2 · C2.3 listening cast).

The cognition's MEMORY: utterance (+ memory) → a past-context snippet + whether it is relevant enough
to inject. MIGRATED from cognition.py's `RECALL_ROLE`/`RecallOut` (canonical def now lives here).
Fireable; part of the `listening` cast.
"""
from pydantic import BaseModel


class RecallOut(BaseModel):
    """`recall` reads the utterance → a memory snippet + whether it is relevant enough to inject."""
    snippet: str
    relevant: bool


ROLE = {
    "id": "recall",
    "label": "Recall (memory)",
    "description": "Utterance (+ memory) → a recalled past-context snippet + whether it is relevant.",
    "prompt_template": (
        "You are the RECALL role — the cognition's memory. Read the operator's utterance and return "
        "ONLY JSON with two fields:\n"
        '  "snippet": a short (one or two sentence) recalled note that would help answer the utterance,\n'
        '  "relevant": a boolean — true if the snippet is genuinely useful for THIS utterance, false if not.\n'
        'Example: {"snippet": "We decided the storage layer stays content-addressed on ext4.", "relevant": true}'
    ),
    "output_schema": RecallOut,
    "input_addresses": ("utterance", "memory"),
    "trigger": "fires in the listening cast when focus.which_roles includes 'recall' (a memory turn).",
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    "mode_scope": {"listening", "walkthrough"},
    "rules": [
        # DECLARED injection rule (DATA; the rule ENGINE is G3, the staged-part injection is G4). The
        # recalled snippet injects into a later reply part iff recall.relevant AND ground.in_scope —
        # the multi-field pure rule the G0 spike proved (cognition.injection_rule).
        {"id": "recall-injects", "reads": ["recall.relevant", "ground.in_scope"],
         "effect": "inject recall.snippet into a later part", "kind": "inject"},
    ],
    "render_hint": {"shape": "snippet", "lane": "recall"},
}
