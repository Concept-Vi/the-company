"""item_types/block.py — a BLOCK: one addressable piece of a document.

A block is the comment-granularity unit — Tim's comments and the fabric's responses attach to a block's
board:// address (via commented_on / reply_to edges). A block links `part_of` its document; the document's
`order` field sequences the blocks. `current` while live; `superseded` if replaced (no-versioning = edit in
place; supersede only when a block is genuinely retired)."""
ITEM_TYPE = {
    "id": "block",
    "initial": "current",
    "states": ["current", "superseded"],
    "transitions": {"current": ["superseded"], "superseded": ["current"]},
    "label": "Block",
    "desc": "one addressable, commentable piece of a document (the comment-granularity unit)",
}
