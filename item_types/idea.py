ITEM_TYPE = {
    "id": "idea",
    "label": "idea",
    "desc": "A seed / thought (the kind of thing a transmission starts as). May be PROMOTED to a request "
            "(the promotion is a `promoted_from` typed edge, so the new item keeps the idea's provenance).",
    "initial": "captured",
    "states": ["captured", "discussing", "promoted", "dropped"],
    "transitions": {
        "captured": ["discussing", "promoted", "dropped"],
        "discussing": ["promoted", "dropped", "captured"],
        "promoted": [],
        "dropped": ["captured"],
    },
}
