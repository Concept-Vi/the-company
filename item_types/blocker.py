ITEM_TYPE = {
    "id": "blocker",
    "label": "blocker",
    "desc": "A blocking condition raised on the board (pairs with the board_edges/blocked_by edge). LANDED "
            "from the cloud notice_board_posts (④ L6 BOARD pour, 7 posts). States honour the legacy "
            "open/resolved/closed (open 3 · resolved 4).",
    "initial": "open",
    "states": ["open", "resolved", "closed"],
    "transitions": {
        "open": ["resolved", "closed"],
        "resolved": ["closed", "open"],
        "closed": ["open"],
    },
}
