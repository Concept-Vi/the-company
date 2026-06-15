"""board_items — board items (requests/issues/tips/guides/ideas) attached to a channel."""
ATTACHMENT_TYPE = {
    "id": "board_items",
    "label": "Board items",
    "target_kind": "address",       # target = board://<id> (opaque; resolve by stripping scheme → cc_board.get_item)
    "multi": True,
    "desc": "a noticeboard item (board://<id>) bound to a channel — the channel's requests/issues/etc.",
}
