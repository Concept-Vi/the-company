# ONE LENS (a declared grouping — explicitly a choice, never the default). The earlier 7 sectors,
# now demoted from "the instrument" to "one binding among many" per Tim's correction.
BINDING = {
    "id": "grouped",
    "label": "Activity — grouped (one lens)",
    "angle_from": "kind-group",
    "radius_from": "time",
    "order_by": "declared",
    "groups": {
        "memory":       ["corpus.record", "corpus.*"],
        "conversation": ["chat", "voice", "voice.*"],
        "making":       ["create", "move", "connect", "delete", "edit", "graph.*"],
        "operations":   ["op.run", "run", "run.*", "flow.*", "activation.*", "cognition.*"],
        "signals":      ["warning", "error", "gap.*", "drift.*"],
        "decisions":    ["decision.*", "approve", "resolve", "proposal.*", "config", "dial.*", "mode"],
        "field":        ["*"],
    },
}
