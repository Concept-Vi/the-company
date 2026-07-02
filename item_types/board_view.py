ITEM_TYPE = {
    "id": "board_view",
    "label": "board view",
    "desc": "A BOARD-VIEW record (④ L6 BOARD): 'one store, many boards' made first-class. A view is itself an "
            "addressed board item (board://<id>); SALIENCE/PINNING is a typed `pinned` edge FROM the view TO "
            "an item (board_edges/pinned.py). Pinning on MY view therefore does not pin on YOURS — the pin "
            "belongs to the view, never to the item. A view is long-lived; its states are just "
            "active/archived.",
    "initial": "active",
    "states": ["active", "archived"],
    "transitions": {
        "active": ["archived"],
        "archived": ["active"],
    },
}
