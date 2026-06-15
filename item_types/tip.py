ITEM_TYPE = {
    "id": "tip",
    "label": "tip",
    "desc": "A discovered better way to use something — a tip / trick. Evergreen (posted), archivable.",
    "initial": "posted",
    "states": ["posted", "archived"],
    "transitions": {
        "posted": ["archived"],
        "archived": ["posted"],
    },
}
