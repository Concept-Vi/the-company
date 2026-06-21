"""stack_item_types/decision-sequence.py — the DECISION stack item-type (FACE-2; the operator-cycle's
keystone item + the prove-on-one). A decision stacked on a channel: a sequence of cards (present/explain/
choose) the operator decides IN-surface. Matches projection's LIVE host precedent (STACK-ITEM-HOST-CONTRACT
§2) + fork's decision:// resolver identity. This is the one type already rendered to-bar by the host."""

STACK_ITEM_TYPE = {
    "id": "decision-sequence",
    "label": "Decision",
    "desc": "A decision to make — presented, explained by the right-hand-man, and decided in-surface; "
            "your latest answer wins (reversible).",
    "row_fields": {
        # field -> dot-path on the item's /api/territory record (the decision:// identity).
        "meaning": "identity.meaning",                       # the actual question, human words
        "recommended_label": "identity.recommended_label",   # the Suggested answer (recommended option's label)
                                                             # — projection/fork confirm the exact path if it differs
        "reversibility": "identity.legibility.is",           # e.g. "Reversible · your latest answer wins"
    },
    "unsettled_state": "pending",   # shows while pending; LEAVES the queue when decided (compose_state)
    "open_verb": {"event": "decision:open", "payload": ["address", "id", "fromInbox"]},
}
