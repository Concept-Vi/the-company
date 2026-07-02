"""types/task.py — the Task type, RECONSTRUCTED (④ L3 · HOLLOW-TYPES.md).

DISPOSITION: RECONSTRUCT. A's row was hollow ({"type":"object"}); the de-facto schema is recovered from the
31 board posts' lived usage. The GLOW (HOLLOW-TYPES synthesis #5): the unprompted EVIDENCE HABIT — a work
item is finished only when it CARRIES ITS OWN PROOF (who verified, when, what bugs, whether partial). Made
first-class here as the closure/verification block, gated by law-11 state (done REQUIRES it). Routing face
harvested from the hand-authored @build decorator (hand-made-powers-the-generator).
Its `id` MUST equal the file stem ('task')."""

TYPE = {
    "id": "task",
    "label": "Task",
    "data_schema": {
        "type": "object",
        "properties": {
            # shared core (×31 — the one schema every used type converged on)
            "title": {"type": "string"},
            "description": {"type": "string"},
            "priority": {"type": "string"},
            "issue_number": {"type": "integer"},
            # the verification/closure family (the glow — Tim's evidence law grown from lived usage)
            "resolution": {"type": "string"},
            "resolved_by": {"type": "string"},
            "verified_at": {"type": "string"},
            "verified_by": {"type": "string"},
            "verified_working": {"type": "boolean"},
            "partial_verification": {"type": "boolean"},
            "bugs_found": {"type": "array"},
            "deployed_at": {"type": "string"},
        },
        "required": ["title"],
    },
    "faces": {
        "tool": {"verbs": ["create", "list", "get", "update"]},
        "board": {"status_values": ["todo", "in_progress", "blocked", "done"],
                  "renderer": "TaskCard", "icon": "check-square", "color": "#3b82f6"},
        "address": {"template": "vi.{user}.task.{id}"},
        # ROUTING harvested from the hand-authored @build decorator (richer than @task's auto-stub):
        # a task's work IS implementation → routes to keeper in execution mode.
        "routing": {"mode": "execution", "affinity_bucket": "coordination",
                    "agent": "keeper (execution mode)", "event": "type.task.created"},
    },
    # law 11 — the declared lifecycle (never enforced in the cloud; enforced here at the write door)
    "states": ["todo", "in_progress", "blocked", "done"],
    "initial": "todo",
    "transitions": {
        "todo": ["in_progress", "blocked"],
        "in_progress": ["blocked", "done"],
        "blocked": ["in_progress", "done"],
        "done": [],                                        # terminal — done→todo is ILLEGAL (proof for C3.5)
    },
    # the state-varying resolver read (law 11): closure REQUIRES the verification block; open states don't.
    "state_requirements": {
        "done": ["resolution", "verified_by", "verified_at"],
    },
    "version": 1,
    "provenance": "reconstructed:HOLLOW-TYPES.md (31 posts; de-facto schema + verification glow + declared 4-state lifecycle)",
    "desc": "Task — a work item finished only when it carries its own proof (RECONSTRUCT; the evidence habit).",
}
