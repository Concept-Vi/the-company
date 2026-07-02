"""types/research.py — the Research type (④ L3 · GHOST type registered · hand-made-powers-the-generator).

A GHOST in the cloud: it exists on the board (2 posts) with NO universal_types row — yet its decorator
@research is HAND-AUTHORED and RICHER than any generated stub (mode + affinity_bucket + routing to a real
agent: Research Scout). HOLLOW-TYPES.md: "a type is a ROUTING ADDRESS to the agent that handles that kind of
work." Registered so board and registry AGREE, harvesting the hand-made routing into the routing face. Its
`id` MUST equal 'research'."""

TYPE = {
    "id": "research",
    "label": "Research",
    "data_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "findings": {"type": "string"},
            "sources": {"type": "array"},
        },
        "required": ["description"],
    },
    "faces": {
        "board": {"status_values": ["open", "investigating", "done"],
                  "renderer": "ObservationCard", "icon": "search", "color": "#10b981"},
        "address": {"template": "vi.{user}.research.{id}"},
        # the hand-authored @research decorator, harvested verbatim (mode/affinity_bucket + routing agent)
        "routing": {"mode": "research", "affinity_bucket": "research",
                    "agent": "Research Scout", "event": "type.research.created"},
    },
    "states": ["open", "investigating", "done"],
    "initial": "open",
    "transitions": {"open": ["investigating", "done"], "investigating": ["done"], "done": []},
    "version": 1,
    "provenance": "ghost:agent_decorators (@research hand-authored, richer than any generated stub; "
                  "registered per hand-made-powers-the-generator so board+registry agree)",
    "desc": "Research — deep investigation/data analysis; routes to Research Scout (ghost type, routing harvested).",
}
