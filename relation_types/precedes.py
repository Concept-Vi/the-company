"""relation_type/precedes.py — an agent-authored relation_type (create_relation_type, #58 declarative-direct).
A declared registry ROW. See runtime/relation_type.py + relation_type/AGENTS.md.
Its `id` MUST equal the file stem ('precedes')."""

RELATION_TYPE = {   'desc': 'SEQUENCE axis (substrate lift): this unit comes before the target '
            'in a declared order — stage/step/round; logical order, not the '
            'wall-clock (that is the temporal axis)',
    'directed': True,
    'id': 'precedes',
    'inverse': 'follows',
    'label': 'precedes (sequence)'}
