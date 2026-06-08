"""roles/screen_reader.py — the SCREEN_READER role (guided-review walkthrough cast).

Reads the screen/mockup under review (injected into live-state via the `mockup://` focus — cognition's A,
in main) and explains it FOR the operator, who is a NON-DEVELOPER and reads no code: what this screen IS
and what he can do here. This is the comprehension that fixes the detached-studio failure (he opened a
mockup and understood nothing) — now a DECLARED cognition role on the cast-beyond-listening seam (56d42f4),
not ad-hoc injection. Walkthrough-cast only (not `listening`): screen-reading is the guided-review faculty.

It rides cognition's A `mockup://` context-injection (the "MOCKUP UNDER REVIEW" block in live-state), NOT
`resolve_address` (which does not resolve `mockup://`). Fireable; default `generate` op.
"""
from pydantic import BaseModel


class ScreenReaderOut(BaseModel):
    """screen_reader reads the screen under review → a plain-language, at-altitude explanation."""
    screen_present: bool   # was a screen / mockup actually in context to read?
    what_this_is: str      # plain language: what this screen IS + what it is for (NOT code/HTML)
    what_you_can_do: str   # the key things the operator can do here


ROLE = {
    "id": "screen_reader",
    "label": "Screen reader (what am I looking at?)",
    "description": "Reads the screen/mockup under review and explains it at the operator's altitude — what it is + what you can do.",
    "prompt_template": (
        "You are the SCREEN_READER role. The operator is a NON-DEVELOPER reviewing a design — he reads no "
        "code. When a 'MOCKUP UNDER REVIEW' block (its HTML) is in your context, read it FOR him and "
        "explain what he is looking at, in plain language at his altitude. Do NOT describe HTML, tags, or "
        "code — describe the SCREEN as a person sees it. Return ONLY JSON:\n"
        '  "screen_present": boolean — true if a screen/mockup was in context to read,\n'
        '  "what_this_is": a plain-language sentence or two — what this screen IS and what it is for,\n'
        '  "what_you_can_do": the key things the operator can do on this screen.\n'
        "If no screen is in context, set screen_present false and keep the other fields brief.\n"
        'Example: {"screen_present": true, "what_this_is": "This is the Inbox — where the system brings '
        'decisions that need your approval.", "what_you_can_do": "Approve or reject each item; open one for detail."}'
    ),
    "output_schema": ScreenReaderOut,
    "input_addresses": ("utterance", "live_state"),
    "trigger": "fires in the walkthrough cast; reads the 'MOCKUP UNDER REVIEW' block (mockup:// focus, cognition's A) from live-state.",
    "model_binding": {"requires": ["chat", "json"], "default_model": None, "default_base_url": None},
    "mode_scope": {"walkthrough"},
    "rules": [],
    "render_hint": {"shape": "screen", "lane": "screen_reader"},
}
