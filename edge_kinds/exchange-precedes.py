"""edge_kinds/exchange-precedes.py — edge kind 'exchange-precedes' · face=knowledge.

//,exchange://:conversational order — this exchange comes before that one. From the recollection move (0024): the mechanical conversation graph landing in
ledger.assertion (provenance='derived'). Inverse 'follows' is COMPOSED AT READ (never stored — law 4)."""
EDGE_KIND = {
    "id": 'exchange-precedes',
    "directed": True,
    "inverse": 'follows',
    "face": 'knowledge',
    "endpoints": ['exchange', 'exchange'],
    "needs_review": False,
}
