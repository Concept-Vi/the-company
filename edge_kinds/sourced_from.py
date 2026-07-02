"""edge_kinds/sourced_from.py — edge kind 'sourced_from' · face=lineage.

Seen in: ledger.edge. Inverse 'source_of' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'sourced_from',
    "directed": True,
    "inverse": 'source_of',
    "face": 'lineage',
    "needs_review": False,
}
