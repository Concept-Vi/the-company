ITEM_TYPE = {
    "id": "design",
    "label": "design",
    "desc": "A design note / proposal argued on the board (the discourse around a shape, not the decided "
            "value — that lives in the decision registry). LANDED from the cloud notice_board_posts "
            "(④ L6 BOARD pour, 32 posts). States honour the legacy open/resolved/closed (open 27 · resolved 5).",
    "initial": "open",
    "states": ["open", "resolved", "closed"],
    "transitions": {
        "open": ["resolved", "closed"],
        "resolved": ["closed", "open"],
        "closed": ["open"],
    },
}
