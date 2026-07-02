"""edge_kinds/calls.py — edge kind 'calls' · face=knowledge.

Seen in: cvi.type_instance_edges, ledger.edge. Inverse 'called_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'calls',
    "directed": True,
    "inverse": 'called_by',
    "face": 'knowledge',
    "endpoints": ['code://', 'code://'],
    "needs_review": False,
}
