# ANGLE-FROM-A-REGISTRY (Group 10) — sectors = the rows of the `projections` registry (the corpus lenses:
# topics/principles/worldview/repo/history/...), NOT the data-driven kinds. Each event maps to its lens via
# the EVENT→ROW edge (a corpus.record carries `projection`); an event naming no lens → the '—' remainder.
# order_by='count' is the HONEST fallback: the projection rows have no inter-row edges yet, so there is no
# real sequence to order by (edges-between-registry-rows is the SEED §95 growth front — never a faked order).
# This is the registry-is-truth proof: drop a projections/<id>.py → it appears as a sector with no code edit.
BINDING = {
    "id": "by_lens",
    "label": "Ways of looking — the lenses themselves",
    # human meaning (registry-true, declared-first; TENTATIVE draft — Tim/DNA ratify; never machine names)
    "meta": {
        "name": "Ways of looking",
        "is": "The different ways you can look at things, laid out as their own map.",
        "fills": "Each slice is one way of looking (a lens); this view shows the set of ways themselves, not the things.",
        "why": "To see the ways of looking you can switch between.",
    },
    "angle_from": "projections",
    "radius_from": "time",
    "order_by": "count",
}

# HUMAN MEANING for the SECTORS of this lens — the corpus SPACES (the rows of the projections/ registry).
# Same legibility-type as kinds/raw.py + nodes/_meta.py + bindings/grouped.py — {id: {name, is}} — and kept
# HERE (next to the binding that renders these sectors) rather than in a projections/_meta.py, because the
# bridge puts runtime/ on sys.path where `import projections` resolves to runtime/projections.py (the
# ProjectionRegistry MODULE), so a `projections._meta` import silently fails — bindings/ has no such collision
# (mirrors GROUP_META living in bindings/grouped.py). projection.py reads this for the "projections" sector
# domain (was unmapped → humanize-only, no meaning). Each entry is GROUNDED in that space's own `desc` in
# projections/<id>.py, TRANSLATED to operator language (operator-law: never "lens / embed / vector space").
# "operators" displays as "Roles" on purpose — a sector literally called "Operators" would read to a human
# OPERATOR as being about THEM (name≠id). A space present in projections/ but absent here (e.g. lineage) falls
# back to a humanized id — composition's validate/backfill set-diff flags it. "—" = events naming no space.
# TENTATIVE draft — Tim/DNA ratify (field-set journey-gated, OQ1–4).
PROJECTION_SPACE_META = {
    "common_knowledge": {"name": "Common knowledge", "is": "What the Company has come to understand about things across the whole system."},
    "history":          {"name": "History",          "is": "What past conversations taught — decisions, corrections, failures and patterns."},
    "principles":       {"name": "Principles",       "is": "The underlying principles and intents something expresses."},
    "topics":           {"name": "Topics",           "is": "The subjects and areas something covers."},
    "worldview":        {"name": "Worldview",        "is": "The stances and values something takes for granted — often unstated."},
    "repo":             {"name": "Code",             "is": "What a piece of the system's own code is for, and the ideas it covers."},
    "operators":        {"name": "Roles",            "is": "What each of the system's built-in roles does."},
    "what":             {"name": "What it is",       "is": "A short, plain statement of what something is."},
    "claimed_status":   {"name": "Claimed status",   "is": "What something claims about its own state — shown as-is, not judged."},
    "—":                {"name": "Unfiled",          "is": "Things not filed under any way of looking yet."},
}
