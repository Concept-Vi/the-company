# ONE LENS (a declared grouping — explicitly a choice, never the default). The earlier 7 sectors,
# now demoted from "the instrument" to "one binding among many" per Tim's correction.
BINDING = {
    "id": "grouped",
    "label": "Activity — grouped into families",
    # human meaning (registry-true, declared-first; TENTATIVE draft — Tim/DNA ratify; never machine names)
    "meta": {
        "name": "Activity",
        "is": "Everything that's happening, gathered into a few bigger families.",
        "fills": "Like the live activity view, but the many kinds are grouped into a handful of families so it's easier to read at a glance.",
        "why": "To see activity at a calmer, coarser grain.",
    },
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
