"""edge_kinds/imports.py — edge kind 'imports' · face=knowledge.

Seen in: ledger.edge. Inverse 'imported_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'imports',
    "directed": True,
    "inverse": 'imported_by',
    "face": 'knowledge',
    "endpoints": ['code://', 'code://'],
    "needs_review": False,
}
