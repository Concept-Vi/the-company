"""roles/element_fit_lens.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from pydantic import BaseModel, Field


class ElementFitLensOut(BaseModel):
    grounded: bool = False
    reason: str = ''


ROLE = {'id': 'element_fit_lens',
 'description': "Panel seat (GC7): judges whether a registry dossier's CLAIMS fit the actual "
                "element — the capabilities and feature match what the element's snippet shows. "
                'One lens of the registration panel.',
 'prompt_template': 'You are the ELEMENT-FIT LENS of a review panel. You are given a PROPOSED '
                    'registry dossier (JSON) and the ELEMENT it claims to describe (its HTML '
                    "snippet + visible text). Judge ONE thing only: do the dossier's CLAIMS fit "
                    'this element — the capabilities claimed (e.g. openable/driven) are plausible '
                    'for this kind of element, and what it says the element IS matches what the '
                    'snippet shows? grounded=true if the claims fit; false if a claim has no '
                    'support in the element. Return JSON: {"grounded": true|false, "reason": one '
                    'short clause}.',
 'input_addresses': ['utterance', 'element'],
 'mode_scope': ['registration'],
    'output_schema': ElementFitLensOut,
}
