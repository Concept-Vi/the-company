"""types/blocker.py — the Blocker type, RECONSTRUCTED (④ L3 · HOLLOW-TYPES.md).

DISPOSITION: RECONSTRUCT. Hollow in the cloud; de-facto schema from the 7 posts (the richest resolution
vocabulary in the set). Intention: something in the way, tracked until it isn't — a blocker can be MITIGATED
(worked around) without being resolved, and resolutions have a CLASS (how it got unstuck). The mitigated
intermediate state + resolution_class = a taxonomy of how obstacles die. Its `id` MUST equal 'blocker'."""

TYPE = {
    "id": "blocker",
    "label": "Blocker",
    "data_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "priority": {"type": "string"},
            "issue_number": {"type": "integer"},
            "resolution": {"type": "string"},             # ×3
            "resolved_by": {"type": "string"},            # ×2
            "resolved_at": {"type": "string"},
            "resolution_class": {"type": "string"},       # how it got unstuck (the taxonomy glow)
        },
        "required": ["title"],
    },
    "faces": {
        "tool": {"verbs": ["create", "list", "get", "update"]},
        "board": {"status_values": ["active", "mitigated", "resolved"],
                  "renderer": "BlockerCard", "icon": "shield-alert", "color": "#ef4444"},
        "address": {"template": "vi.{user}.blocker.{id}"},
    },
    "states": ["active", "mitigated", "resolved"],
    "initial": "active",
    "transitions": {
        "active": ["mitigated", "resolved"],
        "mitigated": ["resolved", "active"],               # a mitigation can regress
        "resolved": [],                                    # terminal
    },
    "state_requirements": {
        "resolved": ["resolution", "resolution_class"],    # closure carries how the obstacle died
    },
    "version": 1,
    "provenance": "reconstructed:HOLLOW-TYPES.md (7 posts; resolution_class + mitigated intermediate state)",
    "desc": "Blocker — an obstacle tracked until it dies; can be mitigated without resolving (RECONSTRUCT).",
}
