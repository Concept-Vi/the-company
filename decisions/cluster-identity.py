"""decisions/cluster-identity.py — cluster identity (GATHER #3 / UNION ID3; KIND: identity).

A held substrate decision (names part of the address-model; renders AFTER substrate-home). At Tim's
altitude. Lean = BOTH (a named handle over a live recomputing result — the same relational shape as
file-identity: a stable address resolving to live content; both-plus-others). The lean is the RHM's
READ — explicitly Tim's call, override-friendly. Resolves decision://global/cluster-identity.
"""

DECISION = {
    "id": "cluster-identity",
    "meaning": (
        "A 'cluster' is a group of related things the company finds. Is a cluster something you NAME once "
        "and return to — a fixed, saved grouping — or a LIVE grouping that recomputes as things change, "
        "or both?"
    ),
    "options": [
        {
            "label": "A named, saved thing",
            "implication": (
                "You name a cluster and it stays put — a stable handle you return to. Predictable and "
                "permanent — but it can go stale as the underlying things change beneath the name."
            ),
        },
        {
            "label": "A live, recomputing result",
            "implication": (
                "A cluster is always the current grouping, recomputed from the latest state — never stale. "
                "Always true to now — but there's no fixed handle for 'the cluster you named last week.'"
            ),
        },
        {
            "label": "Both — a named handle over a live result",
            "implication": (
                "You can name a cluster AND it recomputes underneath: the name stays stable, the contents "
                "stay current — the same shape as how a file resolves to live content. The detail to "
                "settle: the rule for when the named handle and the live result diverge. (My read "
                "— your call, easily changed.)"
            ),
            "recommended": True,
        },
    ],
    "scope": "global",
    "explanation_source": "code://build-prep/the-one-application/UNION-DIVERGENCE-LEDGER.md",
    "legibility": {
        "name": "What a cluster is",
        "is": "a decision to make",
        "why": (
            "It decides whether a group of related things is a fixed name you return to, a live grouping "
            "that recomputes, or both — how the company holds the groupings it finds."
        ),
    },
}
