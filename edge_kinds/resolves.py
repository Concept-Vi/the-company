"""edge_kinds/resolves.py — edge kind 'resolves' · face=knowledge.

Seen in: cvi.type_instance_edges. Inverse 'resolved_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'resolves',
    "directed": True,
    "inverse": 'resolved_by',
    "face": 'knowledge',
    "needs_review": False,
}
