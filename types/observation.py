"""types/observation.py — the Observation type, RECONSTRUCTED (④ L3 · HOLLOW-TYPES.md).

DISPOSITION: RECONSTRUCT (the note.py/signal.py overlap check RESOLVED — recorded in types/_fusion_map.py).
Observation was the HEAVIEST hollow type (61 posts) with a new→validated lifecycle: THINGS NOTICED BEFORE
THEY'RE CONFIRMED — raw noticing kept SEPARATE from accepted knowledge. The verdict RECONSTRUCT (not FUSE)
turns on the 61-vs-0 evidence split (the FUSE set were all zero-post, redundant-at-birth) AND on the
lifecycle: item_types/note.py is the EVERGREEN ANNOTATION (states posted/archived) and item_types/signal.py
is an ACT-SIGNAL (raised/consumed/superseded) — NEITHER models the new→validated VALIDATION GATE that IS
observation's glow. Observation is the validation-lifecycle type; note stays the annotation. They differ by
LIFECYCLE (law 11), not by fields. Its `id` MUST equal 'observation'."""

TYPE = {
    "id": "observation",
    "label": "Observation",
    "data_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "priority": {"type": "string"},
            "issue_number": {"type": "integer"},
            "resolution": {"type": "string"},             # ×5 — how the noticing was validated/closed
            "resolved_by": {"type": "string"},            # ×3
        },
        "required": ["description"],                       # an observation is a noticing — the note is the point
    },
    "faces": {
        "tool": {"verbs": ["create", "list", "get", "update"]},
        "board": {"status_values": ["new", "validated"],
                  "renderer": "ObservationCard", "icon": "search", "color": "#10b981"},
        "address": {"template": "vi.{user}.observation.{id}"},
    },
    # law 11 — the new→validated GATE (the glow neither note.py nor signal.py provides)
    "states": ["new", "validated"],
    "initial": "new",
    "transitions": {
        "new": ["validated"],
        "validated": [],                                   # terminal — validated→new is ILLEGAL (raw≠accepted)
    },
    "state_requirements": {
        "validated": ["resolution"],                       # accepted knowledge carries its validation
    },
    "version": 1,
    "provenance": "reconstructed:HOLLOW-TYPES.md (61 posts — heaviest hollow type; new→validated gate; "
                  "note.py/signal.py overlap checked → RECONSTRUCT, see types/_fusion_map.py)",
    "desc": "Observation — a thing noticed, kept separate from accepted knowledge until validated (RECONSTRUCT).",
}
