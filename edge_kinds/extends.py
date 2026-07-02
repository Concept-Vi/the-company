"""edge_kinds/extends.py — edge kind 'extends' · face=knowledge.

Seen in: cvi.graph_edges, cvi.type_instance_edges, ledger.edge. Inverse 'extended_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'extends',
    "directed": True,
    "inverse": 'extended_by',
    "face": 'knowledge',
    "endpoints": ['code://', 'code://'],
    "needs_review": False,
}
