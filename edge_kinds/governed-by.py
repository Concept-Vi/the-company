"""edge_kinds/governed-by.py — edge kind 'governed-by' · face=knowledge.

Seen in: ledger.edge. Inverse 'governs' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'governed-by',
    "directed": True,
    "inverse": 'governs',
    "face": 'knowledge',
    "needs_review": False,
}
