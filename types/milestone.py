"""types/milestone.py — the Milestone type, RECONSTRUCTED (④ L3 · HOLLOW-TYPES.md).

DISPOSITION: RECONSTRUCT. Hollow in the cloud; de-facto schema from the 58 posts. Intention: not a date on a
plan — a COMPLETION RECORD (closure attaches what changed + what was learned). `missed` is a first-class
honest outcome (law-11 state). The open evidence map holds the one-off proof keys per milestone
(schema_change, bugs_fixed_count, key_insight, remaining_work, first_intent_id…). Its `id` MUST equal 'milestone'."""

TYPE = {
    "id": "milestone",
    "label": "Milestone",
    "data_schema": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
            "priority": {"type": "string"},
            "issue_number": {"type": "integer"},
            "resolved_note": {"type": "string"},          # ×37 — the closure narrative
            "evidence": {"type": "object"},               # the open per-milestone proof map (key_insight, …)
        },
        "required": ["title"],
    },
    "faces": {
        "tool": {"verbs": ["create", "list", "get", "update"]},
        "board": {"status_values": ["planned", "in_progress", "achieved", "missed"],
                  "renderer": "MilestoneCard", "icon": "flag", "color": "#8b5cf6"},
        "address": {"template": "vi.{user}.milestone.{id}"},
    },
    "states": ["planned", "in_progress", "achieved", "missed"],
    "initial": "planned",
    "transitions": {
        "planned": ["in_progress", "achieved", "missed"],
        "in_progress": ["achieved", "missed"],
        "achieved": [],                                    # terminal
        "missed": ["planned"],                             # a missed milestone may be re-planned
    },
    "state_requirements": {
        "achieved": ["resolved_note"],                     # closure attaches what changed/was learned
        "missed": ["resolved_note"],                       # missed is honest — it still records why
    },
    "version": 1,
    "provenance": "reconstructed:HOLLOW-TYPES.md (58 posts; completion-record intention; `missed` first-class)",
    "desc": "Milestone — a completion record (not a date); `missed` is a first-class honest outcome (RECONSTRUCT).",
}
