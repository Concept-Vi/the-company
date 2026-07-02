"""edge_kinds/serves-endpoint.py — edge kind 'serves-endpoint' · face=knowledge.

Seen in: ledger.edge. Inverse 'endpoint-served-by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'serves-endpoint',
    "directed": True,
    "inverse": 'endpoint-served-by',
    "face": 'knowledge',
    "needs_review": False,
}
