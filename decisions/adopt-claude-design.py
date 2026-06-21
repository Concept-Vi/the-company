"""decisions/adopt-claude-design.py — trade-off: adopt Claude Design as the design inlet (gather C3)."""

DECISION = {
    "id": "adopt-claude-design",
    "meaning": (
        "Should the company bring in Claude Design as the place you shape how things look and feel — and have "
        "it talk to the company directly through the channel — or hold off for now?"
    ),
    "options": [
        {
            "label": "Bring it in + wire it to the channel",
            "implication": (
                "You design faces in Claude Design by clicking and describing; the company picks them up through "
                "the channel and wires them into the real system automatically. You design, it connects — no "
                "code from you."
            ),
            "recommended": True,
        },
        {
            "label": "Hold off for now",
            "implication": "Keep designing the way we do now; revisit Claude Design later.",
        },
    ],
    "scope": "global",
    "subtype": "trade-off",
    "explanation_source": "board://item-c0a2d591",
    "legibility": {
        "name": "Bring in Claude Design as your design surface",
        "is": "A tool choice — how you design the faces",
        "why": (
            "Claude Design lets you design look-and-feel by clicking and describing — no code — and a pipeline "
            "can translate what you make into the company's real components on its own. You indicated you're "
            "adopting it and wiring it as a channel connector. This confirms that direction (adopt it as your "
            "design inlet, or hold) — it's what opens the path for your own designs to flow into the system."
        ),
    },
}
