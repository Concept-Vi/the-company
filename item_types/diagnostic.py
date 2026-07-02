ITEM_TYPE = {
    "id": "diagnostic",
    "label": "diagnostic",
    "desc": "A diagnostic report (a traced problem / health finding). LANDED from the cloud "
            "notice_board_posts (④ L6 BOARD pour, 1 post, open). States honour the legacy "
            "open/resolved/closed.",
    "initial": "open",
    "states": ["open", "resolved", "closed"],
    "transitions": {
        "open": ["resolved", "closed"],
        "resolved": ["closed", "open"],
        "closed": ["open"],
    },
}
