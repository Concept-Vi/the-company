"""edge_kinds/depends-on.py — edge kind 'depends-on' · face=knowledge.

Seen in: (normalized from 'depends_on'), cvi.graph_edges, cvi.type_instance_edges, ledger.edge. Inverse 'depended_by' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'depends-on',
    "directed": True,
    "inverse": 'depended_by',
    "face": 'knowledge',
    "needs_review": False,
}
