"""edge_kinds/continues.py — edge kind 'continues' · face=lineage.

Seen in: cvi.graph_edges. Inverse 'continued_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'continues',
    "directed": True,
    "inverse": 'continued_by',
    "face": 'lineage',
    "needs_review": False,
}
