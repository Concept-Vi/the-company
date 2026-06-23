"""board_edges/part_of.py — CONTAINMENT edge: this item is a part/block OF a container document.

A block links `part_of` → board://<document>. The inverse ('contains') lets reverse_traverse find a
document's blocks. Pairs with the document item's `order` field (which sequences them) — part_of gives
membership, order gives sequence."""
RELATION_TYPE = {
    "id": "part_of",
    "directed": True,
    "label": "part-of",
    "inverse": "contains",
    "desc": "the source item is a part/block of the target container (e.g. a block part_of a document)",
}
