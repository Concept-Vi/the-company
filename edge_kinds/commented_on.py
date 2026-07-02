"""edge_kinds/commented_on.py — edge kind 'commented_on' · face=lineage.

Seen in: ledger.edge. Inverse 'has_comment' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'commented_on',
    "directed": True,
    "inverse": 'has_comment',
    "face": 'lineage',
    "needs_review": False,
}
