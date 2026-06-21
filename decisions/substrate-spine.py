"""decisions/substrate-spine.py — trade-off: the company's one foundation (gather C1 / #75). Tim's master shaping call."""

DECISION = {
    "id": "substrate-spine",
    "meaning": (
        "Everything the company keeps — the design library, the decisions, the memory, the channels, the map of "
        "how things connect — could all live in ONE shared foundation, or each piece could keep its own separate "
        "store. Which way?"
    ),
    "options": [
        {
            "label": "One shared foundation",
            "implication": (
                "Everything lives in one place and each part becomes a VIEW of it — nothing stored twice, "
                "everything connects to everything, one source of truth. More to set up once; far cleaner forever."
            ),
            "recommended": True,
        },
        {
            "label": "Keep each piece on its own",
            "implication": (
                "The parts stay in separate stores as they grew — easy to change one in isolation, but they "
                "drift apart and the same thing ends up stored in more than one place."
            ),
        },
        {
            "label": "Your own structure",
            "implication": "You have a shape in mind for how the foundation should be carved — we build to that.",
        },
    ],
    "scope": "global",
    "subtype": "trade-off",
    "legibility": {
        "name": "One shared spine for everything the company stores — or keep each piece on its own?",
        "is": "The company's foundation — a big, shaping call",
        "why": (
            "The company's pieces — the design library, the decisions, the memory, the channels, the "
            "connection-map — each grew their own storage. They're converging on one shared foundation where "
            "each piece is just a view of the one thing: no duplication, everything addressable, one truth. This "
            "decides whether to commit to that one-foundation shape, keep them separate, or carve it your own "
            "way. It shapes how everything else is built — which is why it's yours to call."
        ),
    },
}
