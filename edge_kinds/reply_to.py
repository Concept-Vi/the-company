"""edge_kinds/reply_to.py — edge kind 'reply_to' · face=lineage.

Seen in: ledger.edge. Inverse 'has_reply' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'reply_to',
    "directed": True,
    "inverse": 'has_reply',
    "face": 'lineage',
    "needs_review": False,
}
