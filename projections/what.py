"""projections/what.py — the SEED `what` lens (Cognition Engine K1 · render-not-judge).

A PROJECTION is a declared LENS over a corpus unit (see runtime/projections.py + projections/AGENTS.md).
`what` is the simplest content lens: a <=15-word statement of what the file IS. produced_by a model
(the capture role), does NOT embed (a one-liner, not a space), render-NOT-judge (state what it is,
do not assess it).

Drop a 2nd `projections/<id>.py` to add another lens — it self-registers (the file-discovered,
registry-is-truth path; PART 4.3). Its `id` MUST equal the file stem (`what`).
"""

PROJECTION = {
    "id": "what",
    "level": "content",
    "produced_by": "model",
    "embeds": False,
    "field": "string",
    "desc": "<=15-word statement of what this file IS (describe, do not judge)",
    "stage": "legibility",
}
