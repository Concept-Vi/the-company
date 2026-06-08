"""roles/connect.py — the CONNECT role (Concurrent Cognition G2 · C2.3 listening cast).

Finds a LINK: topic + thread → a related thread/decision/note worth surfacing. NEW in G2 (part of the
locked `listening` cast — DECISIONS Batch 3 Q1). Fireable; part of the `listening` cast.
"""
from pydantic import BaseModel


class ConnectOut(BaseModel):
    """`connect` reads topic + thread → a related link + whether it is worth surfacing."""
    link: str
    worth_surfacing: bool


ROLE = {
    "id": "connect",
    "label": "Connect (a link)",
    "description": "Topic + thread → a related thread/decision/note worth linking to.",
    "prompt_template": (
        "You are the CONNECT role — you find a RELATED thread or past decision worth linking to the "
        "current topic. Read the operator's utterance and return ONLY JSON with two fields:\n"
        '  "link": a short description of a related thread/decision/note (or an empty string if none),\n'
        '  "worth_surfacing": a boolean — true if the link is genuinely useful to surface now.\n'
        'Example: {"link": "the earlier decision to keep storage on ext4", "worth_surfacing": true}'
    ),
    "output_schema": ConnectOut,
    "input_addresses": ("utterance", "thread"),
    "trigger": "fires in the listening cast when focus.which_roles includes 'connect'.",
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    "mode_scope": {"listening", "walkthrough"},
    "rules": [
        {"id": "connect-surfaces", "reads": "connect.worth_surfacing",
         "effect": "surface connect.link as a related-thread note in a later part", "kind": "inject"},
    ],
    "render_hint": {"shape": "link", "lane": "connect"},
}
