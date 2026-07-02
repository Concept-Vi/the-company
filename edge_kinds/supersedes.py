"""edge_kinds/supersedes.py — edge kind 'supersedes' · face=lineage.

Seen in: cvi.graph_edges. Inverse 'superseded_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'supersedes',
    "directed": True,
    "inverse": 'superseded_by',
    "face": 'lineage',
    "needs_review": False,
}
