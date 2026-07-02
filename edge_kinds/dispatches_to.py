"""edge_kinds/dispatches_to.py — edge kind 'dispatches_to' · face=knowledge.

Seen in: cvi.type_instance_edges. Inverse 'dispatched_from' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'dispatches_to',
    "directed": True,
    "inverse": 'dispatched_from',
    "face": 'knowledge',
    "behavior": 'dispatch',
    "needs_review": False,
}
