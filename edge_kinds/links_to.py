"""edge_kinds/links_to.py — edge kind 'links_to' · face=knowledge.

The noticeboard's generic typed-link default (ops/ledger_fact_edges.py emits it when a board item's
links[] entry declares no kind). Registered by the C4.1 adversary fix: this kind was the default of an
ungated writer; now it is a registered row and the writer is gated. Inverse 'linked_from' is COMPOSED
AT READ (never stored — law 4)."""
EDGE_KIND = {
    "id": 'links_to',
    "directed": True,
    "inverse": 'linked_from',
    "face": 'knowledge',
    "endpoints": ['board://', '*://'],
    "needs_review": False,
}
