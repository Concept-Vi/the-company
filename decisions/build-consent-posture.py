"""decisions/build-consent-posture.py — authorize: build-freely vs ask-first (gather R-corpus-2; likely-resolved to AUTO, confirm)."""

DECISION = {
    "id": "build-consent-posture",
    "meaning": (
        "Should the company keep building on its own and rely on undo if something's off — or check with you "
        "before each build?"
    ),
    "options": [
        {
            "label": "Keep building freely",
            "implication": (
                "The company builds without stopping to ask, and anything wrong can be rolled back — fast, which "
                "is how it's been working. You stay in control by direction and review, not per-build approval."
            ),
            "recommended": True,
        },
        {
            "label": "Ask before each build",
            "implication": "Every build waits for your go — more control per step, much slower, and you're back in the loop constantly.",
        },
    ],
    "scope": "global",
    "subtype": "authorize",
    "explanation_source": "code://build-prep/the-one-application/DECISION-GATHER.md#R-corpus-2",  # provenance: gather §R-corpus-2 (verbatim-verified by recollection, section-anchored)
    "legibility": {
        "name": "Build freely, or check with you first each time",
        "is": "How the company works — reversible",
        "why": (
            "In practice the company has been building autonomously with undo as the safety net, and it's what "
            "lets it move at the pace you've seen. This confirms that posture explicitly — keep building freely "
            "(roll back if needed), or shift to asking you before each build. It's been operating as 'build "
            "freely'; this just makes it your deliberate call."
        ),
    },
}
