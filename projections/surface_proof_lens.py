"""projections/surface_proof_lens.py — an agent-authored projection LENS (create_projection, #58 direct).
A declared lens over a corpus unit. See runtime/projections.py + projections/AGENTS.md.
Its `id` MUST equal the file stem ('surface_proof_lens')."""

PROJECTION = {   'desc': 'throwaway proof lens',
    'embeds': True,
    'field': 'array',
    'id': 'surface_proof_lens',
    'level': 'meaning',
    'produced_by': 'model',
    'stage': 'legibility'}
