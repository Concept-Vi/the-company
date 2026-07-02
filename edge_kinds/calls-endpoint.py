"""edge_kinds/calls-endpoint.py — edge kind 'calls-endpoint' · face=knowledge.

Seen in: ledger.edge. Inverse 'endpoint-called-by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'calls-endpoint',
    "directed": True,
    "inverse": 'endpoint-called-by',
    "face": 'knowledge',
    "needs_review": False,
}
