"""roles/eval_histogram.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from pydantic import BaseModel, Field


class EvalHistogramOut(BaseModel):
    question: int = Field(default=0, description='number of items labeled question')
    statement: int = Field(default=0, description='number of items labeled statement')
    command: int = Field(default=0, description='number of items labeled command')


ROLE = {'id': 'eval_histogram',
 'label': 'Eval Histogram (per-label count)',
 'description': 'Reduce-role: reads the N eval_classify label-outputs and returns a per-label '
                'count {question,statement,command}.',
 'prompt_template': 'You are given a list of classification outputs, each with a `label` that is '
                    'one of question, statement, command.\n'
                    '\n'
                    'Outputs:\n'
                    '{notes}\n'
                    '\n'
                    'Count how many have each label and return the three integer counts.',
 'op': 'generate',
 'input_addresses': ['notes'],
    'output_schema': EvalHistogramOut,
}
