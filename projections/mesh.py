"""projection/mesh.py — an agent-authored projection (create_projection, #58 declarative-direct).
A declared registry ROW. See runtime/projection.py + projection/AGENTS.md.
Its `id` MUST equal the file stem ('mesh')."""

PROJECTION = {   'desc': "the MESH triangulation lens (2026-07-07, Tim's 'all the equipment "
            "and no mesh' directive): observation + triangulation records from "
            "the self-referencing swarm that maps the Company's own estate — "
            'what exists, where it lives (its address), what state it is in '
            '(living/dormant/half-built), what it connects to. Written by '
            'observe_territory (open lenses over territories) and '
            'triangulate_mesh (the cross-observation synthesis that also '
            'chooses the NEXT territories — triangulation-not-planning). Keyed '
            'mesh-territory addresses; rounds DEEPEN the same territory by '
            "re-capture. The mesh's growing self-model — any agent reads it "
            "via corpus(space='mesh').",
    'embeds': True,
    'field': 'string',
    'id': 'mesh',
    'level': 'meaning',
    'produced_by': 'model',
    'stage': 'deep'}
