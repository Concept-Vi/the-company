"""edge_kinds/produced.py — edge kind 'produced' · face=lineage.

Seen in: cvi.type_instance_edges, ledger.edge. Inverse 'produced_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'produced',
    "directed": True,
    "inverse": 'produced_by',
    "face": 'lineage',
    "needs_review": False,
}
