"""roles/glyph_symbol_candidates.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from typing import Literal
from pydantic import BaseModel, Field


class GlyphSymbolCandidatesOutCandidates(BaseModel):
    id: str = Field(default='', description='kebab-case stable id, e.g. signed-contract')
    name: str = Field(default='', description='Title Case display name')
    description: str = Field(default='', description='one line: what it depicts + what it means')
    svg: str = Field(default='', description='the 24x24 inner body: path/circle/rect/line elements only, no svg wrapper, stroke=currentColor')
    domain: str = Field(default='', description='the taxonomy domain word (e.g. business, people, property)')
    kind: Literal['object', 'action', 'state'] = Field(default='object', description='what class of thing the symbol denotes')
    tags: list[str] = Field(default_factory=list, description='3-5 lowercase meaning tags for semantic lookup')


class GlyphSymbolCandidatesOut(BaseModel):
    candidates: list[GlyphSymbolCandidatesOutCandidates] = Field(default_factory=list, description='4 distinct symbol candidates')


ROLE = {'id': 'glyph_symbol_candidates',
 'label': 'Glyph: foundry symbol candidates',
 'description': 'A5 of the Glyphic AI fusion — the FOUNDRY role: proposes N candidate ConceptV '
                'line-symbols for a brief, as STRUCTURED records (the schema enforces validity '
                'mechanically — the fix for JSON-in-text-envelope escaping breaks). The '
                'writer/foundry renders the candidates live as glyphics; the human picks one or '
                'gives feedback (the brief carries the running thread); glyphic.save commits the '
                "chosen record with its name/description/tags into CV_ICONS. Tim's flow: choose "
                'from 4, refine until right, store with its values.',
 'prompt_template': 'You draw ConceptV line-symbols for the Glyphic system. The utterance is the '
                    'BRIEF (it may include feedback on earlier attempts — honour it).\n'
                    '\n'
                    "STYLE (strict): each candidate's svg is the INNER BODY ONLY of a 24×24 icon — "
                    '<path>/<circle>/<rect>/<line> elements only, NO <svg> wrapper, fill="none", '
                    'stroke="currentColor", stroke-width="1.5", round caps and joins, ~2px margin, '
                    'clean minimal geometry.\n'
                    '\n'
                    'Propose 4 DISTINCT takes (different visual metaphors, not variations of one). '
                    'Each: a kebab-case id, a Title Case name, a one-line description of what it '
                    'depicts and means, the svg body, a domain word, a kind, and 3-5 lowercase '
                    'meaning tags.',
    'output_schema': GlyphSymbolCandidatesOut,
}
