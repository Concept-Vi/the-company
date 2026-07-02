"""edge_kinds/powered-by.py — edge kind 'powered-by' · face=knowledge.

Seen in: ledger.edge. Inverse 'powers' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'powered-by',
    "directed": True,
    "inverse": 'powers',
    "face": 'knowledge',
    "needs_review": False,
}
