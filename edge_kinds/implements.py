"""edge_kinds/implements.py — edge kind 'implements' · face=knowledge.

Seen in: cvi.graph_edges, cvi.type_instance_edges. Inverse 'implemented_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'implements',
    "directed": True,
    "inverse": 'implemented_by',
    "face": 'knowledge',
    "needs_review": False,
}
