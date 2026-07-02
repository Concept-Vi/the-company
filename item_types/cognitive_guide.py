ITEM_TYPE = {
    "id": "cognitive_guide",
    "label": "cognitive guide",
    "desc": "A cognitive/how-to guide steering how a kind of work is approached (the cloud's richer sibling "
            "of the engine `guide`; kept as its own type to land the cloud rows losslessly). LANDED from the "
            "cloud notice_board_posts (④ L6 BOARD pour, 3 posts, all open). States honour the legacy "
            "open/resolved/closed.",
    "initial": "open",
    "states": ["open", "resolved", "closed"],
    "transitions": {
        "open": ["resolved", "closed"],
        "resolved": ["closed", "open"],
        "closed": ["open"],
    },
}
