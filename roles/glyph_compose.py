"""roles/glyph_compose.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from pydantic import BaseModel, Field


class GlyphComposeOut(BaseModel):
    chosen: str = Field(default='', description='the chosen candidate symbol id, or empty when abstaining')
    confident: bool = Field(default=False, description="true only when the chosen symbol genuinely carries the word's meaning")
    why: str = Field(default='', description='one line: the reason for the choice or the abstention')


ROLE = {'id': 'glyph_compose',
 'label': 'Glyph: compose/judge resolution',
 'description': 'A5 of the Glyphic AI fusion — the JUDGE half (extraction-vs-judgment): given a '
                'word and its top-k nearest glyph candidates from the glyph_meaning space (with '
                "scores), choose the symbol that truly carries the word's meaning — or abstain "
                'when none does (the thin-margin law: never trust #1 blindly). The writer '
                'auto-resolves on a confident choice and asks the human only on abstain.',
 'prompt_template': 'The utterance is compact JSON: {"word": the word to resolve, "context": the '
                    'sentence it appeared in, "candidates": [{"id": symbol id, "text": the '
                    'symbol\'s meaning text, "score": cosine}]}.\n'
                    '\n'
                    "Judge which candidate symbol TRULY carries the word's meaning in this "
                    'context. Similar embedding scores can hide opposite meanings — judge by '
                    'MEANING, not by score order.\n'
                    '\n'
                    'If one candidate genuinely fits: chosen = its id, confident = true.\n'
                    'If none genuinely fits (or the fit is a stretch): chosen = "", confident = '
                    'false — abstaining is correct, never force a stretch.',
    'output_schema': GlyphComposeOut,
}
