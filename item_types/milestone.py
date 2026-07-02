ITEM_TYPE = {
    "id": "milestone",
    "label": "milestone",
    "desc": "A marked achievement / checkpoint in the work. LANDED from the cloud notice_board_posts "
            "(④ L6 BOARD pour, 58 posts). States honour the legacy open/resolved/closed the cloud actually "
            "used (open 15 · resolved 43).",
    "initial": "open",
    "states": ["open", "resolved", "closed"],
    "transitions": {
        "open": ["resolved", "closed"],
        "resolved": ["closed", "open"],
        "closed": ["open"],
    },
}
