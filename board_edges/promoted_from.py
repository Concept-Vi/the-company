RELATION_TYPE = {
    "id": "promoted_from",
    "directed": True,
    "label": "promoted-from",
    "inverse": "promoted_to",
    "desc": "This board item was promoted from another board item (e.g. a request promoted-from an idea) "
            "(item -> board://<id>). Promotion keeps provenance via the edge, and the FLAT board://<id> "
            "address means the item's identity survives its type changing.",
}
