"""roles/voice.py — the VOICE role (Concurrent Cognition G2 · C2.3 listening cast).

The TONE shaper: persona + the answer → the tone/phrasing to deliver it in. NEW in G2 (locked
`listening` cast — DECISIONS Batch 3 Q1). Distinct from the voice/ TTS MODULE — this is the cognition
role that shapes HOW the answer reads (persona-coherent phrasing), not the speech synthesizer.
Fireable; part of the `listening` cast.
"""
from pydantic import BaseModel


class VoiceOut(BaseModel):
    """`voice` reads persona + answer → the toned phrasing + a one-word tone label."""
    toned: str
    tone: str


ROLE = {
    "id": "voice",
    "label": "Voice (tone)",
    "description": "Persona + the answer → the tone/phrasing to deliver it in (cognition role, not the TTS module).",
    "prompt_template": (
        "You are the VOICE role — you shape the TONE and phrasing of a reply so it reads in the "
        "operator's persona, WITHOUT changing its meaning. You are given the persona and the answer. "
        "Return ONLY JSON with two fields:\n"
        '  "toned": the answer rephrased in the persona\'s tone (same meaning),\n'
        '  "tone": a one-word label for the tone applied (e.g. "direct", "warm", "terse").\n'
        'Example: {"toned": "Done — storage stays on ext4.", "tone": "direct"}'
    ),
    "output_schema": VoiceOut,
    "input_addresses": ("persona", "answer"),
    "trigger": "fires in the listening cast when focus.which_roles includes 'voice'.",
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    "mode_scope": {"listening"},
    "rules": [
        {"id": "voice-tones-answer", "reads": "voice.toned",
         "effect": "deliver the toned phrasing as the reply", "kind": "route"},
    ],
    "render_hint": {"shape": "tone", "lane": "voice"},
}
