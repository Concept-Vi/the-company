"""roles/glyph_extract.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from typing import Literal
from pydantic import BaseModel, Field


class GlyphExtractOutNodes(BaseModel):
    word: str = Field(default='', description="the thing's noun exactly as spoken (singular, lowercase, no articles)")
    kind: Literal['thing', 'person', 'place', 'action', 'concept'] = Field(default='thing', description='the rough kind of thing')


class GlyphExtractOutRelations(BaseModel):
    from_word: str = Field(default='', description="the source thing's word (must match a node word)")
    to_word: str = Field(default='', description="the target thing's word (must match a node word)")
    phrase: str = Field(default='', description="the relation as spoken, e.g. 'is part of'")
    mood: Literal['is', 'could', 'not'] = Field(default='is', description='asserted / potential / negated')


class GlyphExtractOut(BaseModel):
    nodes: list[GlyphExtractOutNodes] = Field(default_factory=list, description='the distinct things, in order of mention')
    relations: list[GlyphExtractOutRelations] = Field(default_factory=list, description='the relationships between the things, as expressed')


ROLE = {'id': 'glyph_extract',
 'label': 'Glyph: extract meaning-structure',
 'description': 'A5 of the Glyphic AI fusion — the EXTRACT half of the NL→glyphgraph engine: pulls '
                'the things and their relationships out of a spoken/typed utterance, exactly as '
                'said, for the writer to resolve into glyphics (words→symbols via the '
                'glyph_meaning space) and compose into a graph. Extraction only — the '
                "judging/composition is glyph_compose's job (extraction-vs-judgment).",
 'prompt_template': 'Extract the meaning-structure from the utterance: the THINGS and the '
                    'RELATIONSHIPS between them, exactly as expressed — never invent, never add '
                    'things that are not said.\n'
                    '\n'
                    'Each distinct thing → one node, word = the noun exactly as spoken (singular, '
                    'lowercase, no articles).\n'
                    'Each relationship → from_word/to_word (matching node words) + phrase = the '
                    "relation as spoken (e.g. 'is part of', 'leads to', 'is the face of') + its "
                    'mood: is (asserted fact), could (potential/conditional/tentative), not '
                    '(negated).\n'
                    '\n'
                    'If the utterance describes no relationship, return the nodes with an empty '
                    'relations list.',
    'output_schema': GlyphExtractOut,
}
