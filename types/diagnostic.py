"""types/diagnostic.py — the Diagnostic type (④ L3 · GHOST type registered · hand-made-powers-the-generator).

A GHOST in the cloud: on the board (1 post) with NO universal_types row, but its decorator @diagnostic is
HAND-AUTHORED and RICHER (mode + affinity_bucket + routing to QA & Verification). Registered so board and
registry AGREE, harvesting the hand-made routing into the routing face. Its `id` MUST equal 'diagnostic'."""

TYPE = {
    "id": "diagnostic",
    "label": "Diagnostic",
    "data_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "root_cause": {"type": "string"},
            "resolution": {"type": "string"},
        },
        "required": ["description"],
    },
    "faces": {
        "board": {"status_values": ["open", "investigating", "resolved"],
                  "renderer": "IssueCard", "icon": "bug", "color": "#ef4444"},
        "address": {"template": "vi.{user}.diagnostic.{id}"},
        "routing": {"mode": "diagnostic", "affinity_bucket": "diagnostic",
                    "agent": "QA & Verification", "event": "type.diagnostic.created"},
    },
    "states": ["open", "investigating", "resolved"],
    "initial": "open",
    "transitions": {"open": ["investigating", "resolved"], "investigating": ["resolved"], "resolved": []},
    "version": 1,
    "provenance": "ghost:agent_decorators (@diagnostic hand-authored, richer than any generated stub; "
                  "registered per hand-made-powers-the-generator so board+registry agree)",
    "desc": "Diagnostic — troubleshooting/system analysis; routes to QA & Verification (ghost type, routing harvested).",
}
