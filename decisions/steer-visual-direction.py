"""decisions/steer-visual-direction.py — trade-off: how hands-on Tim steers the visual direction (gather L3)."""

DECISION = {
    "id": "steer-visual-direction",
    "meaning": (
        "The company is building the visual direction you're shaping — material richness, real-feeling "
        "artefacts. Keep it driving against your stated direction, or do you want to steer specific calls as you "
        "see them?"
    ),
    "options": [
        {
            "label": "Keep driving to your stated direction",
            "implication": "The company builds to the direction you've given and the 'feels real' bar; you review the results.",
            "recommended": True,
        },
        {
            "label": "You steer specific calls as renders surface",
            "implication": "You weigh in on particular looks as they appear — more of your hand, more of your time.",
        },
    ],
    "scope": "global",
    "subtype": "trade-off",
    "legibility": {
        "name": "How you steer the visual direction",
        "is": "Your eye — ongoing",
        "why": (
            "You're shaping the visual direction (material density, real-feeling artefacts) and the company is "
            "building to it. This is just how hands-on you want to be — let it keep driving to your stated "
            "direction with your review, or steer specific calls as renders surface. Either way it keeps moving."
        ),
    },
}
