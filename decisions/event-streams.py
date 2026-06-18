"""decisions/event-streams.py — event-stream addressability (GATHER #4 / UNION TH2 Shape-B; KIND: addressability).

A held substrate decision (names part of the address-model; renders AFTER substrate-home). At Tim's
altitude (no machine names — never "addressable"/"references"). Lean = MIX (first-class for the events
that get referenced/decided-on; references-only for the raw high-volume stream; both-plus-others). The
lean is the RHM's READ — explicitly Tim's call, override-friendly. Resolves decision://global/event-streams.
"""

DECISION = {
    "id": "event-streams",
    "meaning": (
        "The company's highest-volume live data — the running history log, and the marks, notes, and pins "
        "people leave — should each one of those become a first-class thing you can point AT directly "
        "(refer to, recall, or decide on any single one), stay as references only (pointed at indirectly, "
        "by time or source), or a mix?"
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
                "settle: the rule for which stream is which. (The RHM's read — your call.)"
            ),
            "recommended": True,
        },
    ],
    "scope": "global",
    "explanation_source": "code://build-prep/the-one-application/UNION-DIVERGENCE-LEDGER.md",
    "legibility": {
        "name": "How the live streams are held",
        "is": "a decision to make",
        "why": (
            "It decides whether each event, mark, and note can be pointed at directly, stays bulk data, or "
            "a mix — how the company's highest-volume live data is addressed."
        ),
    },
}
