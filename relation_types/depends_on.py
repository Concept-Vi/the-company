"""relation_type/depends_on.py — an agent-authored relation_type (create_relation_type, #58 declarative-direct).
A declared registry ROW. See runtime/relation_type.py + relation_type/AGENTS.md.
Its `id` MUST equal the file stem ('depends_on')."""

RELATION_TYPE = {   'desc': 'DEPENDENCY axis (substrate lift): this unit requires the target — '
            "a gate; the inverse reading is 'target unlocks this'",
    'directed': True,
    'id': 'depends_on',
    'inverse': 'unlocks',
    'label': 'depends on (dependency)'}
