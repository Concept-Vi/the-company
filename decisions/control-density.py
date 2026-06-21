"""decisions/control-density.py — trade-off: when expert controls show (gather P1 — the expertise axis)."""

DECISION = {
    "id": "control-density",
    "meaning": (
        "The deeper expert controls — should they appear based on WHO's using it (plain for a newcomer, the full "
        "set for you in pilot mode), always show, or hide behind an 'advanced' toggle?"
    ),
    "options": [
        {
            "label": "Appear by who's viewing",
            "implication": "Plain controls for a newcomer, the full knob-row for you in pilot — the surface adapts to the viewer automatically.",
            "recommended": True,
        },
        {
            "label": "Always show all the knobs",
            "implication": "Everything visible all the time — maximum control, but a wall of knobs for anyone new.",
        },
        {
            "label": "A hidden 'advanced' toggle",
            "implication": "A manual switch reveals the expert set — simple, but it's a fixed toggle, not adaptive.",
        },
    ],
    "scope": "global",
    "subtype": "trade-off",
    "explanation_source": "code://build-prep/the-one-application/DECISION-GATHER.md#P1",  # provenance: gather §P1 (verbatim-verified, section-anchored)
    "legibility": {
        "name": "When the expert controls show up",
        "is": "How the surface adapts to who's using it",
        "why": (
            "Expert controls (the deeper knobs) clutter for a newcomer but you want them in pilot mode. This "
            "decides whether they appear by WHO's viewing (plain↔full automatically), always show, or hide "
            "behind a toggle. The 'by viewer' option fits resolving-to-context — but the viewer-mode signal "
            "isn't built yet, so it's wired and waits for that."
        ),
    },
}
