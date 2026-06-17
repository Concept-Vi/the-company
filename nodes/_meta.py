# THE NODE-TYPE LEGIBILITY REGISTRY — human meaning for each node TYPE (the sectors of the data-driven
# "Connections" wheel, binding=by_node_type). Mirrors kinds/raw.py EXACTLY: ONE data map, the SAME
# legibility-type shape `{name, is}` (composition's "ONE legibility-type, MANY registries", ch-2mnxl9j0).
# The instrument reads this DECLARED-FIRST for each node-type sector and renders it; un-seeded node types
# fall back to a humanized id (split on . _ - / + title-case) so they stay legible. The meaning lives HERE
# (the data / the registry), NEVER in the instrument.
#
# TENTATIVE draft copy — Tim/DNA ratify; the operator NEVER sees the machine node-id, only `name` + `is`.
# Grounded in each node module's own docstring (nodes/*.py) — NOT invented. composition's validate/backfill
# set-diff finds any node type present in the registry but missing here.
#
# HOME NOTE (for composition): this mirrors the accepted kinds/raw.py pattern (a sibling meta map). The
# declared-at-birth ideal would be a `META = {...}` on each node module read into NodeType (like OUTPUT_SCHEMA)
# — composition's call. Migrating map→per-module is trivial if preferred; this is the safe, reversible seed.
NODE_TYPE_META = {
    "ask":          {"name": "Ask (with context)", "is": "Answers a question using the information you give it alongside it."},
    "codebase":     {"name": "The Company's code", "is": "Reads the system's own code and documents into one place it can work from."},
    "constant":     {"name": "A fixed value",      "is": "Holds a value you set once and gives it back unchanged — no AI."},
    "embed":        {"name": "Make searchable",    "is": "Turns text into a fingerprint of its meaning, so similar things can be found."},
    "gate":         {"name": "A fork in the road", "is": "Sends what comes in down one of two paths, depending on a condition."},
    "join":         {"name": "Join together",      "is": "Combines several inputs into one piece, in order."},
    "llm":          {"name": "An AI step",         "is": "Calls an AI model to transform or generate text."},
    "model_of_tim": {"name": "The model of Tim",   "is": "The system's explicit, written model of Tim — his stated principles and ways of working."},
    "pair":         {"name": "Pair (order kept)",  "is": "Joins two inputs into a pair, keeping the order you gave them."},
    "portal":       {"name": "A live window",      "is": "A live view onto another thing — not computed, just a window that stays in sync."},
    "retrieve":     {"name": "Find the nearest",   "is": "Searches a collection and returns the items closest in meaning to your query."},
    "rhm_mode":     {"name": "Right-hand-man mode", "is": "How your right-hand-man is present and works alongside you — a setting you can change."},
    "similarity":   {"name": "How alike (a score)","is": "Compares two things and returns how close they are in meaning."},
    "titlecase":    {"name": "Title Case",         "is": "Reformats text so each word starts with a capital letter."},
    "uppercase":    {"name": "UPPERCASE",          "is": "Reformats text into all capital letters."},
    "wordcount":    {"name": "Word count",         "is": "Counts how many words are in a piece of text."},
}
