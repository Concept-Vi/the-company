"""projections/principles.py — the SEED `principles` lens (Cognition Engine K1 · render-not-judge).

A `meaning`-level lens that embeds → the PRINCIPLE space (the one corroboration runs over: high
recurrence-across-SESSIONS in principle-space = a corroboration mark, M3 — which is exactly why the
corpus-record carries cross-SESSION lineage from the start). produced_by a model; an array (a file
MAY express several principles — render each). render-NOT-judge: render the principle it EXPRESSES,
do not assess whether it is correct.

See runtime/projections.py + projections/AGENTS.md. Its `id` MUST equal the file stem (`principles`).
"""

PROJECTION = {
    "id": "principles",
    "level": "meaning",
    "produced_by": "model",
    "embeds": True,
    "field": "array",
    "desc": "the underlying principles/intents this file expresses (MAY be several; render each, do not judge)",
    "stage": "legibility",
}
