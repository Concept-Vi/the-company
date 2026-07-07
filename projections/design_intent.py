"""projection/design_intent.py — an agent-authored projection (create_projection, #58 declarative-direct).
A declared registry ROW. See runtime/projection.py + projection/AGENTS.md.
Its `id` MUST equal the file stem ('design_intent')."""

PROJECTION = {   'desc': 'the memory-archaeology lens (sibling of `history`, 2026-07-07): '
            'one mine_design_intent extract per exchange — {gist, '
            'intents[{subject,kind,statement,reaching_for,special}], '
            'connects_to, design_weight} — WHAT things are, what they were '
            'REACHING FOR, their non-obvious properties, mined from the '
            'conversation record (the sole record: nothing here was touched by '
            'humans). Keyed exchange://<sid>/<i> like history but a SEPARATE '
            'projection so archaeology never supersedes the self-improvement '
            'extracts at the same addresses; embedded so design intent '
            'retrieves by meaning and connects_to feeds the '
            'exchange://↔code:// cross-link.',
    'embeds': True,
    'field': 'string',
    'id': 'design_intent',
    'level': 'meaning',
    'produced_by': 'model',
    'stage': 'deep'}
