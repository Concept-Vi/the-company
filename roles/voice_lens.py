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
 # SCOPED to the two PROSE fields (the first panel run flagged a confirmed-control dossier for
 # "leakage" in maps_to_feature/how_to_change — fields that are technical BY DESIGN; the lens judges
 # only what the operator actually reads at a glance).
 'prompt_template': 'You are the VOICE LENS of a review panel. You are given a PROPOSED registry '
                    'dossier (JSON). Judge ONLY these two fields: howto.what and '
                    'howto.what_you_can_do — are THEY plain, non-technical prose a non-developer '
                    "reads at a glance (like 'The primary action button on the Inbox dashboard')? "
                    'IGNORE every other field: maps_to_feature/represents/address are feature ids '
                    'and ALLOWED to be technical; howto.how_to_change names code files BY DESIGN. '
                    "grounded=true if the two prose fields are at the operator's altitude; false "
                    'only if HTML tags, selectors, code identifiers, or developer jargon leak into '
                    'THOSE TWO fields. DOMAIN VOCABULARY IS NOT JARGON: words the operator uses daily '
                    '(activity feed, node, diff, inbox, wire, canvas, walkthrough, build) are his '
                    'language — jargon means CODE identifiers, file paths, selectors, HTML tags, '
                    'function names. Return JSON: {"grounded": true|false, "reason": one short '
                    'clause}.',
 'mode_scope': ['registration'],
    'output_schema': VoiceLensOut,
}
