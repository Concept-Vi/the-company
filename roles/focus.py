"""roles/focus.py — the FOCUS role (Concurrent Cognition G2 · C2.3 listening cast).

The SELECTOR of the cast: reads the operator's utterance → the turn's intent + which auxiliary roles
to run + the part-1 shape. The cast's "afferent nerve" — what the rest of the cast is gated on.

MIGRATED from cognition.py's `FOCUS_ROLE`/`FocusOut` (the G0 spike defined it inline). The CANONICAL
definition now lives HERE (file-discovered); cognition.py imports it from the registry (no duplicate
definition). Fireable (declares prompt_template + output_schema), part of the `listening` cast.
"""
from pydantic import BaseModel, Field


class FocusOut(BaseModel):
    """`focus` reads the utterance → the turn's intent + which auxiliary roles to run."""
    intent: str
    which_roles: list[str] = Field(default_factory=list)


ROLE = {
    "id": "focus",
    "label": "Focus (selector)",
    "description": "Reads the utterance → the turn's intent + which auxiliary roles to fire + part-1 shape.",
    "prompt_template": (
        "You are the FOCUS role. Read the operator's utterance and return ONLY JSON with two fields:\n"
        '  "intent": a short phrase naming what the operator wants,\n'
        '  "which_roles": a JSON array of auxiliary role names to run for this turn.\n'
        'Available auxiliary roles: ["recall", "ground", "connect", "check", "voice"]. Include a role '
        "when the utterance calls for it (recall→past context; ground→live facts; connect→a related "
        "thread; check→verify a forming answer; voice→tone). Otherwise omit it.\n"
        'Example: {"intent": "recall a past decision", "which_roles": ["recall", "ground"]}'
    ),
    "output_schema": FocusOut,
    "input_addresses": ("utterance",),
    "trigger": "every listening turn — focus fires FIRST, gating the rest of the cast (the selector).",
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    "mode_scope": {"listening"},
    "rules": [
        # DECLARED routing rule (DATA; the rich rule ENGINE is G3). focus.which_roles selects the
        # cast members that fire this turn — a pure read of focus's resolved output.
        {"id": "focus-selects-cast", "reads": "focus.which_roles",
         "effect": "the named roles join this turn's wave", "kind": "route"},
    ],
    "render_hint": {"shape": "selector", "lane": "focus"},
}
