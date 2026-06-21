"""stack_item_types/presentation.py — a PRESENTATION stacked for the operator (show-the-thing). Cleared by
ACKNOWLEDGE. The feed (fork's stack-feed) + the host renderer (projection) land later; declared NOW so the
operator-cycle vocabulary is COMPLETE and the host soft-degrades/fail-louds it honestly meanwhile (the
host shows `name` + flags it `--unready` until its renderer lands — never blank, never lost)."""

STACK_ITEM_TYPE = {
    "id": "presentation",
    "label": "Presentation",
    "desc": "Something the fabric is showing you — read it; clears when you acknowledge.",
    "row_fields": {
        # the human one-line of what's being shown — source finalizes with fork's stack-feed shape.
        "headline": "identity.headline",
    },
    "unsettled_state": "pending",
    # open_verb: the generic resolve/spotlight fallback until a presentation surface exists (clears by acknowledge).
}
