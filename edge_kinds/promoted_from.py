"""edge_kinds/promoted_from.py — edge kind 'promoted_from' · face=lineage.

Seen in: ledger.edge. Inverse 'promoted_to' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'promoted_from',
    "directed": True,
    "inverse": 'promoted_to',
    "face": 'lineage',
    "needs_review": False,
}
