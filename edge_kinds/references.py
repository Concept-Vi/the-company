"""edge_kinds/references.py — edge kind 'references' · face=knowledge.

Seen in: cvi.graph_edges, cvi.type_instance_edges, ledger.edge. Inverse 'referenced_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'references',
    "directed": True,
    "inverse": 'referenced_by',
    "face": 'knowledge',
    "endpoints": ['code://', '*://'],
    "needs_review": False,
}
