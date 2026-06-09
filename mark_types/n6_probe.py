"""mark_type/n6_probe.py — an agent-authored mark_type (create_mark_type, #58 declarative-direct).
A declared registry ROW. See runtime/mark_type.py + mark_type/AGENTS.md.
Its `id` MUST equal the file stem ('n6_probe')."""

MARK_TYPE = {   'desc': 'N6 auto-reflect probe (throwaway)',
    'direction': 'surface',
    'id': 'n6_probe',
    'value_shape': 'label'}
