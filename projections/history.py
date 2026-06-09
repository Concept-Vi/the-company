"""projection/history.py — an agent-authored projection (create_projection, #58 declarative-direct).
A declared registry ROW. See runtime/projection.py + projection/AGENTS.md.
Its `id` MUST equal the file stem ('history')."""

PROJECTION = {   'desc': 'the session-history lens (③/⑨ — G23): one mined exchange-extract '
            'per unit — decisions, corrections, failures, patterns from the '
            'conversation record; embedded so failure-patterns cluster and '
            'past context retrieves (durable cross-session memory on the '
            'corpus, NOT episodic-memory)',
    'embeds': True,
    'field': 'string',
    'id': 'history',
    'level': 'meaning',
    'produced_by': 'model'}
