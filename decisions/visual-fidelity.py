"""decisions/visual-fidelity.py — trade-off: how real the visuals get, drawn vs generated (gather D1)."""

DECISION = {
    "id": "visual-fidelity",
    "meaning": (
        "How far should the company DRAW its visuals itself — clean, fast, on-brand — versus GENERATE photoreal "
        "images for the standout moments? Your bar is 'indistinguishable from real'."
    ),
    "options": [
        {
            "label": "Draw everything; generate only hero showpieces",
            "implication": (
                "Most visuals are drawn (sharp, instant, perfectly on-brand); the company generates true "
                "photoreal images only for the big 'look at this' moments where realism really matters."
            ),
            "recommended": True,
        },
        {
            "label": "Push the drawn style further first",
            "implication": "Take the drawn style further — texture, depth, layering — before reaching for generated images at all.",
        },
        {
            "label": "Generate the imagery throughout",
            "implication": "Use generated photoreal images wherever the visual matters; keep drawing only for diagrams.",
        },
    ],
    "scope": "global",
    "subtype": "trade-off",
    "explanation_source": "code://build-prep/the-one-application/DECISION-GATHER.md#D1",  # provenance: gather §D1 SYNTHETIC RICHNESS CEILING (verbatim-verified, section-anchored)
    "legibility": {
        "name": "How real should the visuals get — drawn, or generated?",
        "is": "The visual fidelity bar — your eye",
        "why": (
            "The company can DRAW visuals itself (fast, on-brand, but it plateaus below true photoreal) or "
            "GENERATE photoreal images (real-looking, heavier to make). Your bar is 'indistinguishable from "
            "real'. This sets where the line sits — drawn everywhere with generated hero moments, push the drawn "
            "style first, or generate throughout. It decides how rich the faces feel."
        ),
    },
}
