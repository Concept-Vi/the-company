"""stack_item_types/explanation.py — an EXPLANATION stacked for the operator (why / what's at stake). Cleared
by ACKNOWLEDGE. Feed (fork) + renderer (projection) land later; declared NOW for a complete operator-cycle
vocabulary (host soft-degrades to `name` + fail-louds `--unready` until its renderer lands)."""

STACK_ITEM_TYPE = {
    "id": "explanation",
    "label": "Explanation",
    "desc": "The right-hand-man explaining something to you — read it; clears when you acknowledge.",
    "row_fields": {
        "headline": "identity.headline",
    },
    "unsettled_state": "pending",
    # open_verb: generic resolve/spotlight fallback until an explanation surface exists.
}
