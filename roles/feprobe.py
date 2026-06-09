"""roles/feprobe.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from pydantic import BaseModel, Field


class FeprobeOut(BaseModel):
    summary: str = Field(default='', description='the summary')


ROLE = {'id': 'feprobe',
 'description': 'throwaway probe',
 'op': 'generate',
 'prompt_template': 'Summarize: {utterance}',
 'model_binding': {'requires': ['chat', 'json']},
    'output_schema': FeprobeOut,
}
