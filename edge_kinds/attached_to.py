"""edge_kinds/attached_to.py — edge kind 'attached_to' · face=containment.

Seen in: ledger.edge. Inverse 'has_attachment' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'attached_to',
    "directed": True,
    "inverse": 'has_attachment',
    "face": 'containment',
    "needs_review": False,
}
