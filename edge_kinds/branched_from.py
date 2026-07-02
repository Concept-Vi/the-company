"""edge_kinds/branched_from.py — edge kind 'branched_from' · face=lineage.

Seen in: cvi.graph_edges. Inverse 'branched_into' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'branched_from',
    "directed": True,
    "inverse": 'branched_into',
    "face": 'lineage',
    "needs_review": False,
}
