"""edge_kinds/subscribes-event.py — edge kind 'subscribes-event' · face=knowledge.

Seen in: ledger.edge. Inverse 'event-consumed-by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'subscribes-event',
    "directed": True,
    "inverse": 'event-consumed-by',
    "face": 'knowledge',
    "needs_review": False,
}
