"""projections/worldview.py — the SEED `worldview` lens (Cognition Engine K1 · render-not-judge).

A `meaning`-level lens that embeds → the WORLDVIEW space. produced_by a model; an array of the
stances/values the file ASSUMES (often unstated). render-NOT-judge: surface the assumed stance,
do not agree/disagree with it. (A near∩¬far inversion query between e.g. worldview-space and
topics-space is the kind of cross-level relation the inversion-finder surfaces — same principle,
different subject; L2.)

See runtime/projections.py + projections/AGENTS.md. Its `id` MUST equal the file stem (`worldview`).
"""

PROJECTION = {
    "id": "worldview",
    "level": "meaning",
    "produced_by": "model",
    "embeds": True,
    "field": "array",
    "desc": "the stances/values this file ASSUMES (often unstated) — surface them, do not judge",
    "stage": "legibility",
}
