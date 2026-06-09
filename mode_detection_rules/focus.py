"""mode_detection_rules/focus — the sustained-activity-and-clear-inbox → focus presence rule.

When the operator is actively working (idle < 90s) AND nothing is piling up (inbox == 0), protect deep
work with a tight focus window. Fires AFTER background (priority 20 > 10) so a long idle wins, but
BEFORE listening — an actively-working operator with a clear inbox should focus, not be drawn into
conversation. The not-None guard is FIRST inside the `and` so the `lt` short-circuits at startup.
"""

MODE_DETECTION_RULE = {
    "id": "focus",
    "candidate": "focus",
    "why": "sustained operator activity with nothing piling up — protect deep work with a tight window",
    "priority": 20,
    "when": {
        "op": "and",
        "args": [
            # GUARD FIRST: idle_seconds is None at startup; short-circuit before the comparison.
            {"op": "ne", "args": [
                {"op": "field", "path": "idle_seconds"},
                {"op": "lit", "value": None},
            ]},
            {"op": "lt", "args": [
                {"op": "field", "path": "idle_seconds"},
                {"op": "lit", "value": 90},        # the 90s DEFAULT_IDLE_SECONDS
            ]},
            {"op": "eq", "args": [
                {"op": "field", "path": "inbox"},
                {"op": "lit", "value": 0},
            ]},
        ],
    },
}
