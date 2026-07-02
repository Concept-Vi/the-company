"""edge_kinds/capability-of.py — edge kind 'capability-of' · face=knowledge.

Seen in: ledger.edge. Inverse 'has-capability' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'capability-of',
    "directed": True,
    "inverse": 'has-capability',
    "face": 'knowledge',
    "needs_review": False,
}
