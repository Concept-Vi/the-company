RELATION_TYPE = {
    "id": "depends_on",
    "directed": True,
    "label": "depends-on",
    "inverse": "unblocks",
    "desc": "This board item DEPENDS ON another — it cannot start/complete until the target is done. "
            "depends_on → board://<item>. THE SWARM-DISPATCH EDGE: a dispatcher computes the buildable "
            "FRONTIER as the items whose depends_on targets are all in a done state, and dispatches teams "
            "over that frontier in parallel (the board as the central tracker none of the sessions can hold "
            "alone). reverse_traverse(item, depends_on) = what waits on this item (its unblocks set). "
            "Tim's collaborative-build design, 2026-06-29.",
}
