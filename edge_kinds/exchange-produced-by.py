"""edge_kinds/exchange-produced-by.py — edge kind 'exchange-produced-by' · face=lineage.

//,exchange://:a file/artifact was produced by that exchange (recollection's crossing). From the recollection move (0024): the mechanical conversation graph landing in
ledger.assertion (provenance='derived'). Inverse 'produced' is COMPOSED AT READ (never stored — law 4)."""
EDGE_KIND = {
    "id": 'exchange-produced-by',
    "directed": True,
    "inverse": 'produced',
    "face": 'lineage',
    "endpoints": ['file', 'file'],
    "needs_review": False,
}
