"""roles/eval_p1probe.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from typing import Literal
from pydantic import BaseModel, Field


class EvalP1probeOut(BaseModel):
    label: Literal['question', 'statement', 'command'] = 'question'


ROLE = {'id': 'eval_p1probe',
 'description': 'P1 regression probe (throwaway)',
 'prompt_template': 'Label the text as question, statement or command. Return JSON: {"label": ...}',
    'output_schema': EvalP1probeOut,
}
