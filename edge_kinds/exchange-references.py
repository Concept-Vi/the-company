"""edge_kinds/exchange-references.py — edge kind 'exchange-references' · face=knowledge.

//,exchange://:an exchange references another (mechanical mention). From the recollection move (0024): the mechanical conversation graph landing in
ledger.assertion (provenance='derived'). Inverse 'referenced-by' is COMPOSED AT READ (never stored — law 4)."""
EDGE_KIND = {
    "id": 'exchange-references',
    "directed": True,
    "inverse": 'referenced-by',
    "face": 'knowledge',
    "endpoints": ['exchange', 'exchange'],
    "needs_review": False,
}
