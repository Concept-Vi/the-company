"""roles/complete_text.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from pydantic import BaseModel, Field


class CompleteTextOut(BaseModel):
    text: str = Field(default='', description='the completion — the full direct answer to the prompt carried in the utterance')


ROLE = {'id': 'complete_text',
 'label': 'Complete (passthrough text)',
 'description': 'PASSTHROUGH completion — the union path for plain text completion (A2 of the '
                'Glyphic AI fusion): the browser projection (CV_AI) fires this role via run_role '
                'instead of any second engine path. The utterance IS a complete, self-contained '
                'prompt; this role adds no framing of its own.',
 'prompt_template': "The user message after 'Utterance:' is a COMPLETE, self-contained prompt or "
                    'instruction. Respond to it directly and fully. Put your entire answer in the '
                    'text field. Do not summarise the prompt, do not add preamble or '
                    'meta-commentary — the text field is the completion itself.',
 'knobs': {'max_tokens': 2048},
    'output_schema': CompleteTextOut,
}
