"""edge_kinds/authored_by.py — edge kind 'authored_by' · face=lineage.

Seen in: ledger.edge. Inverse 'authored' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'authored_by',
    "directed": True,
    "inverse": 'authored',
    "face": 'lineage',
    "endpoints": ['code://', 'session://'],
    "needs_review": False,
}
