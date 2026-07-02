"""edge_kinds/derived-from.py — edge kind 'derived-from' · face=lineage.

Seen in: ledger.edge. Inverse 'derived_into' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'derived-from',
    "directed": True,
    "inverse": 'derived_into',
    "face": 'lineage',
    "needs_review": False,
}
