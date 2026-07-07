"""edge_kinds/exchange-contains.py — edge kind 'exchange-contains' · face=containment.

//,exchange://:one session/exchange CONTAINS another exchange (the transcript nesting). From the recollection move (0024): the mechanical conversation graph landing in
ledger.assertion (provenance='derived'). Inverse 'contained-by' is COMPOSED AT READ (never stored — law 4)."""
EDGE_KIND = {
    "id": 'exchange-contains',
    "directed": True,
    "inverse": 'contained-by',
    "face": 'containment',
    "endpoints": ['session', 'session'],
    "needs_review": False,
}
