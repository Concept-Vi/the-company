"""edge_kinds/part_of.py — edge kind 'part_of' · face=containment.

Seen in: cvi.type_instance_edges, ledger.edge. Inverse 'has_part' is COMPOSED AT READ (never stored — law 4). """
EDGE_KIND = {
    "id": 'part_of',
    "directed": True,
    "inverse": 'has_part',
    "face": 'containment',
    "needs_review": False,
}
