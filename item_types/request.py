ITEM_TYPE = {
    "id": "request",
    "label": "request",
    "desc": "An ask to add or change the Company / MCP / CLI / a channel — the inward-facing half's "
            "first-exercised story-type (a session asks; a channel picks it up).",
    "initial": "open",
    "states": ["open", "picked-up", "building", "done", "declined"],
    "transitions": {
        "open": ["picked-up", "declined"],
        "picked-up": ["building", "open", "declined"],
        "building": ["done", "declined"],
        "done": [],
        "declined": ["open"],
    },
}
