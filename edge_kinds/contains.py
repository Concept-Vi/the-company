"""edge_kinds/contains.py — edge kind 'contains' · face=containment.

Seen in: cvi.type_instance_edges, ledger.edge. Inverse 'contained_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'contains',
    "directed": True,
    "inverse": 'contained_by',
    "face": 'containment',
    "endpoints": ['code://', 'code://'],
    "needs_review": False,
}
