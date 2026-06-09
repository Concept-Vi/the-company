"""projections/topics.py — the SEED `topics` lens (Cognition Engine K1 · render-not-judge).

A content lens that DOES embed (`embeds:true`) → it becomes a vector SPACE (Group L:
op=embed → put_vector(vec://<item>#space=topics)), so `find_relations` can range over the
topic space. produced_by a model; an array field (subjects/areas). render-NOT-judge.

See runtime/projections.py + projections/AGENTS.md. Its `id` MUST equal the file stem (`topics`).
"""

PROJECTION = {
    "id": "topics",
    "level": "content",
    "produced_by": "model",
    "embeds": True,
    "field": "array",
    "desc": "the subjects/areas this file covers (describe, do not judge)",
    "stage": "legibility",
}
