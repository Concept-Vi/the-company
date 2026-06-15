ITEM_TYPE = {
    "id": "guide",
    "label": "guide",
    "desc": "A how-to / documentation entry (e.g. 'how to extend the CLI'). Living — updated in place "
            "(no versioning), archivable when superseded.",
    "initial": "living",
    "states": ["living", "archived"],
    "transitions": {
        "living": ["archived"],
        "archived": ["living"],
    },
}
