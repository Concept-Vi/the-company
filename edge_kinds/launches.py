"""edge_kinds/launches.py — edge kind 'launches' · face=lineage.

Seen in: ledger.edge. Inverse 'launched-by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'launches',
    "directed": True,
    "inverse": 'launched-by',
    "face": 'lineage',
    "needs_review": False,
}
