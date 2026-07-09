"""roles/glyph_assist.py — authored cognition role (Concurrent Cognition C7.4/C7.5 · #58 direct-create).
Authored through the cognition surface — DIRECTLY via create_role (the agent authors live, #58)
OR via propose_role→operator-approve→apply_role (surfacing, kept available). Either way validated
by import-in-a-temp-dir (the correctness gate) before it reached the live roles/ tree. A declared
role: the output_schema is a real BaseModel subclass (fail-loud requirement); rules are declared ASTs."""
from typing import Literal
from pydantic import BaseModel, Field


class GlyphAssistOutOps(BaseModel):
    op: Literal['set_state', 'add_edge', 'add_node', 'remove', 'narrate'] = Field(default='set_state', description='the operation')
    ids: list[str] = Field(default_factory=list, description='target node ids (set_state / remove)')
    value: str = Field(default='', description="the state value (set_state) or the new thing's word (add_node)")
    from_id: str = Field(default='', description='source node id (add_edge)')
    to_id: str = Field(default='', description='target node id (add_edge)')
    kind: str = Field(default='', description='the edge kind (add_edge) — one of vocab.relations[].id '
                      '(vocab.edge_kinds is the same list of bare ids, kept for compatibility). A relation '
                      'with directed:true points FROM from_id TO to_id and has a declared inverse telling '
                      '(vocab.relations[].inverse) — to say the opposite direction, swap from_id/to_id and '
                      'keep the same kind (one stored fact, two tellings). directed:false = symmetric.')
    line: Literal['solid', 'dashed'] = Field(default='solid', description='asserted or potential (add_edge)')
    text: str = Field(default='', description='the narration (narrate)')


class GlyphAssistOut(BaseModel):
    ops: list[GlyphAssistOutOps] = Field(default_factory=list, description='the typed graph ops, applied in order')


ROLE = {'id': 'glyph_assist',
 'label': 'Glyph: collaborative graph ops',
 'description': 'A6 of the Glyphic AI fusion — the COLLABORATIVE hand: turns a natural instruction '
                "about the CURRENT glyphgraph (with the human's live selection as shared context) "
                'into TYPED GRAPH-OPS — never free mutation (the one-IR law): the browser '
                'validates every op against the registries and applies them through the same code '
                'paths the mouse uses. Two hands, one graph.',
 'prompt_template': 'The utterance is compact JSON: {"instruction": the human\'s request, '
                    '"selection": [selected node ids — \'these\' refers to them], "nodes": [{id, '
                    'symbol, word, state}], "edges": [{from, to, kind, line}], "vocab": {"states": '
                    'legal state values, "relations": the legal edge kinds as FULL fields [{id, feeling, '
                    'directed, inverse, negates}] — directed:true kinds point from→to and carry a declared '
                    'inverse (swap from/to for the opposite telling, never invent a reversed kind), '
                    '"edge_kinds": the same ids bare (compatibility)}}.\n'
                    '\n'
                    'Translate the instruction into graph ops. Rules:\n'
                    "- 'these/them/it' = the selection. Never touch nodes the instruction doesn't "
                    'refer to.\n'
                    '- set_state: ids = the targets, value = one of vocab.states.\n'
                    '- add_edge: from/to = existing node ids, kind = one of vocab.relations[].id, line '
                    '= solid (asserted) or dashed (potential/could). Respect direction: a directed kind '
                    'points from→to; for the opposite meaning swap from/to (its declared inverse is how '
                    'it will be READ) — never mint a reversed kind name.\n'
                    '- add_node: value = the word for the new thing (the browser resolves its '
                    'glyph by meaning).\n'
                    '- remove: ids = the targets.\n'
                    "- narrate: text = a short answer, for questions ('what is this?') — answer "
                    'from the graph given, never invent.\n'
                    'Use the FEWEST ops that honour the instruction. If the instruction cannot be '
                    'honoured with these ops, return a single narrate op saying why.',
    'output_schema': GlyphAssistOut,
}
