"""edge_kinds/maps_instance_of.py — edge kind 'maps_instance_of' · face=containment.

Seen in: cvi.graph_edges. Inverse 'instanced_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'maps_instance_of',
    "directed": True,
    "inverse": 'instanced_by',
    "face": 'containment',
    "needs_review": False,
}
