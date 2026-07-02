"""edge_kinds/restarted_from.py — edge kind 'restarted_from' · face=lineage.

Seen in: cvi.graph_edges. Inverse 'restarted_into' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'restarted_from',
    "directed": True,
    "inverse": 'restarted_into',
    "face": 'lineage',
    "needs_review": False,
}
