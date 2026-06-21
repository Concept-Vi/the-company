"""stack_item_types/verify-request.py — a VERIFY-REQUEST stacked for the operator (verify a result/claim).
Cleared by a VERDICT (not a plain acknowledge — the clear-semantics differ from presentation/explanation).
Feed (fork) + renderer + the verdict-mechanism land later; declared NOW for a complete operator-cycle
vocabulary. The operator-cycle: fabric works -> stacks a verify-request -> Tim gives a verdict -> resume."""

STACK_ITEM_TYPE = {
    "id": "verify-request",
    "label": "Verify",
    "desc": "Something the fabric needs you to verify — review it and give a verdict; clears on your verdict.",
    "row_fields": {
        "headline": "identity.headline",   # what to verify, human words
    },
    "unsettled_state": "pending",
    # open_verb: a verify surface (verify:open) lands with the verdict-mechanism; generic fallback meanwhile.
}
