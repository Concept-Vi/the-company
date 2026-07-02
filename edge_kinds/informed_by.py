"""edge_kinds/informed_by.py — edge kind 'informed_by' · face=lineage.

Seen in: cvi.graph_edges, cvi.type_instance_edges. Inverse 'informs' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'informed_by',
    "directed": True,
    "inverse": 'informs',
    "face": 'lineage',
    "needs_review": False,
}
