"""decisions/event-streams.py — event-stream addressability (GATHER #4 / UNION TH2 Shape-B; KIND: addressability).

A held substrate decision (names part of the address-model; renders AFTER substrate-home). At Tim's
altitude (no machine names — never "addressable"/"references"). Lean = MIX (first-class for the events
that get referenced/decided-on; references-only for the raw high-volume stream; both-plus-others). The
lean is the RHM's READ — explicitly Tim's call, override-friendly. Resolves decision://global/event-streams.
"""

DECISION = {
    "id": "event-streams",
    "meaning": (
        "The company's highest-volume live data — the running log, and the marks, notes, and pins "
        "people leave — how directly should you be able to point at any single one?"
    ),
    "options": [
        {
            "label": "First-class — point at any single one",
            "implication": (
                "Every event, mark, and note becomes directly pointable — you can link, recall, or decide "
                "on any single one. The most powerful for memory and recall — but the highest-volume data "
                "becomes a very large space of individually-named things."
            ),
        },
        {
            "label": "References only",
            "implication": (
                "The streams stay bulk data, pointed at indirectly (by time or source), not each one "
                "individually named. Much lighter to hold — but you can't directly reference a single "
                "moment or note."
            ),
        },
        {
            "label": "A mix — the significant ones first-class, the bulk by reference",
            "implication": (
                "Decisions, marks, and notes become directly pointable; the raw high-volume log stays "
                "reference-only. Balances power where it's used against weight for the bulk. The detail to "
                "settle: the rule for which stream is which. (My read — your call.)"
            ),
            "recommended": True,
        },
    ],
    "scope": "global",
    "subtype": "trade-off",  # multi-option address-model direction (owner=tim) — was UNTAGGED → absent from the queue despite being a declared held-substrate decision meant to render after substrate-home.
    "explanation_source": "code://build-prep/the-one-application/UNION-DIVERGENCE-LEDGER.md",
    "legibility": {
        "name": "How the live streams are held",
        "is": "Reversible · your latest answer wins",
        "why": (
            "The company's highest-volume live data — the running history log, and the marks, notes, and "
            "pins people leave. Each one first-class (point at, recall, or decide on any single one), "
            "references-only (pointed at by time or source), or a mix — the significant ones first-class, "
            "the bulk by reference."
        ),
    },
}
