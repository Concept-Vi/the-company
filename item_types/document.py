"""item_types/document.py — a DOCUMENT: a container board item holding an ORDERED set of block items.

A structured design/discussion document (e.g. dragnet-development design doc #1). Its `order` field carries the
ordered list of its block addresses; its blocks link back `part_of` it. Reading it = assemble_document (the
ordered blocks, each with its comment thread). Lives in a channel like any board item; commentable at the
document level AND per-block."""
ITEM_TYPE = {
    "id": "document",
    "initial": "draft",
    "states": ["draft", "active", "archived"],
    "transitions": {"draft": ["active", "archived"], "active": ["archived", "draft"], "archived": ["active"]},
    "label": "Document",
    "desc": "a container holding an ordered set of addressable blocks — a structured, commentable document",
}
