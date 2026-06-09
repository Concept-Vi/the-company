"""mode_detection_rules/background — the long-idle → background presence rule.

When the operator has been quiet for a long while (>= 900s = 10 × the 90s idle threshold), drop to a
low-noise background presence. Fires FIRST (lowest priority number) so a long idle wins over the other
signals. The not-None guard is FIRST inside the `and` so the comparison short-circuits at startup (when
idle_seconds is None) — `None >= 900` would TypeError, but `ne(idle_seconds, None)` is False first.
"""

MODE_DETECTION_RULE = {
    "id": "background",
    "candidate": "background",
    "why": "the operator has been quiet for a long while — drop to a low-noise background presence",
    "priority": 10,
    "when": {
        "op": "and",
        "args": [
            # GUARD FIRST: idle_seconds is None at startup; short-circuit before the comparison.
            {"op": "ne", "args": [
                {"op": "field", "path": "idle_seconds"},
                {"op": "lit", "value": None},
            ]},
            {"op": "ge", "args": [
                {"op": "field", "path": "idle_seconds"},
                {"op": "lit", "value": 900},      # 10 × the 90s DEFAULT_IDLE_SECONDS
            ]},
        ],
    },
}
