ITEM_TYPE = {
    "id": "note",
    "label": "note",
    "desc": "A note/annotation attached to an address (an image, a doc, any addressed content) — lighter "
            "than a tip, distinct from a comment: an observation/annotation. Threadable (replies link "
            "reply_to it). Evergreen, archivable.",
    "initial": "posted",
    "states": ["posted", "archived"],
    "transitions": {
        "posted": ["archived"],
        "archived": ["posted"],
    },
}
