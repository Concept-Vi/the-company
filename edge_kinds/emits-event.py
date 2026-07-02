"""edge_kinds/emits-event.py — edge kind 'emits-event' · face=knowledge.

Seen in: ledger.edge. Inverse 'event-emitted-by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'emits-event',
    "directed": True,
    "inverse": 'event-emitted-by',
    "face": 'knowledge',
    "needs_review": False,
}
