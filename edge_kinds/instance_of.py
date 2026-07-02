"""edge_kinds/instance_of.py — edge kind 'instance_of' · face=containment.

Seen in: cvi.type_instance_edges. Inverse 'has_instance' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'instance_of',
    "directed": True,
    "inverse": 'has_instance',
    "face": 'containment',
    "needs_review": False,
}
