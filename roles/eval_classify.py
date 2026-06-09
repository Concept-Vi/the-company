"""roles/eval_classify.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from typing import Literal
from pydantic import BaseModel, Field


class EvalClassifyOut(BaseModel):
    label: Literal['question', 'statement', 'command'] = Field(default='question', description='the speech-act class of the text')


ROLE = {'id': 'eval_classify',
 'label': 'Eval Classify (text speech-act)',
 'description': 'Labels a short text as exactly one of {question, statement, command}.',
 'prompt_template': 'Classify the following text as exactly one of: question, statement, command.\n'
                    '\n'
                    'Text: {utterance}\n'
                    '\n'
                    'Return the single best label.',
 'op': 'generate',
 'input_addresses': ['utterance'],
    'output_schema': EvalClassifyOut,
}
