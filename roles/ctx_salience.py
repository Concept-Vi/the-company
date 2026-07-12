"""roles/ctx_salience.py — the resolved-context LEDGER judge (SLICE-JUDGES C3.1).
Classifies one conversation span (a ctx.unit body) for the context ledger: what KIND of unit it is,
how SALIENT it remains for future turns, and at what LOD it should render into a resolved context
(full text / a gloss / omitted-but-addressed). Fired via run_role; verdicts land in ctx.unit.meta.verdict.
Declared role: output_schema is a real BaseModel subclass (fail-loud); file-discovered fresh per call.
Part of build-prep/the-one-system/glyphic/resolved-context (Tim's resolved-context direction)."""
from typing import Literal
from pydantic import BaseModel, Field


class CtxSalienceOut(BaseModel):
    kind: Literal['decision', 'fact', 'preference', 'question', 'scaffold', 'noise'] = Field(
        default='fact', description='what kind of conversation unit this span is')
    salience: float = Field(
        default=0.5, ge=0.0, le=1.0,
        description='how important this span remains for FUTURE turns (0=inert, 1=load-bearing)')
    lod: Literal['full', 'gloss', 'omit'] = Field(
        default='gloss', description='render level in a resolved context: full text, a one-line gloss, or omitted (address only)')


ROLE = {'id': 'ctx_salience',
 'label': 'Context ledger: span salience judge',
 'description': 'Judges one conversation span for the resolved-context ledger: kind '
                '(decision|fact|preference|question|scaffold|noise), forward salience 0-1, and '
                'render LOD (full|gloss|omit).',
 'prompt_template': 'You are judging ONE span of a working conversation for a context ledger.\n'
                    'Classify it:\n'
                    '- kind: decision (a made call), fact (a truth/finding), preference (how the human '
                    'wants things), question (open ask), scaffold (process/tooling chatter), noise.\n'
                    '- salience: how much FUTURE turns need this (1.0 = load-bearing standing truth, '
                    '0.0 = inert).\n'
                    '- lod: how it should render into a resolved context — full (verbatim), gloss '
                    '(one line), omit (address only).\n'
                    '\n'
                    'Span: {utterance}',
    'output_schema': CtxSalienceOut,
}
