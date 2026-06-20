"""projection/extractions.py — the dragnet EXTRACTION-LAYER lens (#65; recollection).
A declared registry ROW (drop-in; id MUST equal the file stem 'extractions'). See runtime/projections.py.

The full-coverage dragnet's extract-once asset (session history + the Visual-DNA vault; 29,425 stepped
coarse→fine meaning-extractions) embedded as a vector SPACE — so the determine candidate-filter becomes
SEMANTIC (concept-match, not keyword/homonym) and the extractions fold into the corpus(op='query') path
(ONE recall surface). The embedded field is each extraction's representative text (about + summary + claims)."""

PROJECTION = {
    'desc': 'the dragnet extraction-layer lens (#65) — one stepped coarse→fine meaning-extraction per '
            'transcript/vault chunk (about/kind/touches + summary/entities/claims/relations), embedded so '
            'the grounded determine filters by MEANING (not keyword) and the extract-once asset is '
            'cosine-queryable via corpus(op=query, space=extractions). Chunk-traced; no-fiction grounded.',
    'embeds': True,
    'field': 'string',
    'id': 'extractions',
    'level': 'meaning',
    'produced_by': 'model'}
