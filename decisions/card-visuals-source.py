"""decisions/card-visuals-source.py — trade-off: hand-made card visuals vs the reusable family (gather D2)."""

DECISION = {
    "id": "card-visuals-source",
    "meaning": (
        "The card you approved uses hand-made narrative pictures; the company now has a family of reusable "
        "visual building-blocks. Keep the hand-made ones for story-style decisions, rebuild on the family, or both?"
    ),
    "options": [
        {
            "label": "Hand-made for story, the family for data-heavy",
            "implication": "Each screen picks per its content — the bespoke narrative pictures for story decisions, the reusable family for data-dense ones.",
            "recommended": True,
        },
        {
            "label": "Rebuild the card's visuals on the family",
            "implication": "One consistent family everywhere — tidier, but loses the bespoke narrative touch of the approved card.",
        },
        {
            "label": "Both — family underneath, story on top",
            "implication": "The reusable family as the base, a hand-made narrative layer over it where a decision needs the story.",
        },
    ],
    "scope": "global",
    "subtype": "trade-off",
    "legibility": {
        "name": "Hand-made card visuals, or the reusable family?",
        "is": "A look choice — don't lose the approved card",
        "why": (
            "The approved card uses hand-made narrative pictures (the library→authorize→library story); the "
            "company just built a family of reusable visual blocks. This decides whether the decision cards keep "
            "the hand-made narrative, adopt the reusable family, or layer both — without regressing the card you "
            "signed off."
        ),
    },
}
