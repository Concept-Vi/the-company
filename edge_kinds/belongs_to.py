"""edge_kinds/belongs_to.py — edge kind 'belongs_to' · face=containment.

Seen in: cvi.graph_edges, cvi.type_instance_edges. Inverse 'has_member' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'belongs_to',
    "directed": True,
    "inverse": 'has_member',
    "face": 'containment',
    "needs_review": False,
}
