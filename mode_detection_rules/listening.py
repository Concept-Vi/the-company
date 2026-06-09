"""mode_detection_rules/listening — the work-is-piling-up → listening presence rule.

When items are awaiting the operator (inbox > 0), be present and conversational. Fires LAST (priority
30) so a long idle (background) or active-and-clear deep work (focus) win first; a non-empty inbox is the
fallback "the operator should be engaged" signal. `inbox` is always an int (0 default) in the
activity_signal snapshot, so no not-None guard is needed.
"""

MODE_DETECTION_RULE = {
    "id": "listening",
    "candidate": "listening",
    "why": "items are awaiting the operator — be present and conversational",
    "priority": 30,
    "when": {
        "op": "gt",
        "args": [
            {"op": "field", "path": "inbox"},
            {"op": "lit", "value": 0},
        ],
    },
}
