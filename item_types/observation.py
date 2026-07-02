ITEM_TYPE = {
    "id": "observation",
    "label": "observation",
    "desc": "A noticed fact / finding about the Company or its work — the discourse an agent records while "
            "working. LANDED from the cloud notice_board_posts (④ L6 BOARD pour, 61 posts). States honour the "
            "legacy open/resolved/closed the cloud actually used (open 51 · resolved 9 · closed 1).",
    "initial": "open",
    "states": ["open", "resolved", "closed"],
    "transitions": {
        "open": ["resolved", "closed"],
        "resolved": ["closed", "open"],
        "closed": ["open"],
    },
}
