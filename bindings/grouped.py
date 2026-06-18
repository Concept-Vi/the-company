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

# HUMAN MEANING for the 7 families (the SECTORS of this lens). Same legibility-type as kinds/raw.py +
# nodes/_meta.py — {id: {name, is}} — kept HERE, beside the `groups` that define what each family GATHERS,
# so a new family + its meaning land together (no drift). projection.py reads this for the "kind-group"
# sector domain (was unmapped → humanize-only, no meaning). GROUNDED in each family's own glob set above
# (NOT invented); operator language — never the machine kind-ids inside. TENTATIVE — Tim/DNA ratify.
GROUP_META = {
    "memory":       {"name": "Memory",          "is": "Things the system saved into its memory — notes and stored content."},
    "conversation": {"name": "Conversation",    "is": "Messages and spoken exchanges."},
    "making":       {"name": "Making",          "is": "Things being made, changed, moved, wired together, or removed."},
    "operations":   {"name": "Operations",      "is": "The system's work running — jobs, runs, flows, and the AI's thinking steps."},
    "signals":      {"name": "Signals",         "is": "Warnings, errors, and gaps worth noticing."},
    "decisions":    {"name": "Decisions",       "is": "Choices, approvals, proposals, and settings."},
    "field":        {"name": "Everything else", "is": "Anything that doesn't fall into one of the other families."},
}
