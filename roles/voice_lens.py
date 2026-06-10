"""roles/voice_lens.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from pydantic import BaseModel, Field


class VoiceLensOut(BaseModel):
    grounded: bool = False
    reason: str = ''


ROLE = {'id': 'voice_lens',
 'description': "Panel seat (GC7): judges whether a registry dossier reads at the OPERATOR'S "
                'altitude — plain language, no HTML/code-speak, the voice of the existing entries. '
                'One lens of the registration panel.',
 'prompt_template': 'You are the VOICE LENS of a review panel. You are given a PROPOSED registry '
                    "dossier (JSON). Judge ONE thing only: is its language at the OPERATOR'S "
                    'altitude — plain, non-technical prose a non-developer reads at a glance (like '
                    "'The primary action button on the Inbox dashboard'), with NO HTML tags, "
                    'selectors, code identifiers, or developer jargon leaking into '
                    'what/what_you_can_do? grounded=true if the voice is right; false if technical '
                    'residue or unclear phrasing leaks through. Return JSON: {"grounded": '
                    'true|false, "reason": one short clause}.',
 'mode_scope': ['registration'],
    'output_schema': VoiceLensOut,
}
