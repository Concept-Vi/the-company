ITEM_TYPE = {
    "id": "task",
    "label": "task",
    "desc": "A unit of work to do. LANDED from the cloud notice_board_posts (④ L6 BOARD pour, 31 posts). "
            "The cloud declared {todo,in_progress,blocked,done} on this type but every live post used "
            "open/resolved/closed (open 16 · resolved 15) — so states honour the LEGACY vocabulary the data "
            "actually carries (registry-is-truth over the cloud's unenforced declaration).",
    "initial": "open",
    "states": ["open", "resolved", "closed"],
    "transitions": {
        "open": ["resolved", "closed"],
        "resolved": ["closed", "open"],
        "closed": ["open"],
    },
}
