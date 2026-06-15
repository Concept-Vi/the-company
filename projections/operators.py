"""projection/operators.py — an agent-authored projection (create_projection, #58 declarative-direct).
A declared registry ROW. See runtime/projection.py + projection/AGENTS.md.
Its `id` MUST equal the file stem ('operators')."""

PROJECTION = {   'desc': 'what each registered OPERATOR (role) does — the verb/role '
            'registry embedded as a vector SPACE so content no operator covers '
            'piles up → a candidate new operator (the nucleation types_space; '
            'the GATE/promotion keystone, seed §11)',
    'embeds': True,
    'field': 'text',
    'id': 'operators',
    'level': 'structural',
    'produced_by': 'code',
    'stage': 'legibility'}
