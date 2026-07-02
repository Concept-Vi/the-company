ITEM_TYPE = {
    "id": "research",
    "label": "research",
    "desc": "A research note / investigation posted for the discourse. LANDED from the cloud "
            "notice_board_posts (④ L6 BOARD pour, 2 posts, all open). States honour the legacy "
            "open/resolved/closed.",
    "initial": "open",
    "states": ["open", "resolved", "closed"],
    "transitions": {
        "open": ["resolved", "closed"],
        "resolved": ["closed", "open"],
        "closed": ["open"],
    },
}
