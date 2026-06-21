"""decisions/cube-3d.py — theorem-fork: how the cube becomes 3-D in the instrument (gather F2). Shape follows Tim's theorem."""

DECISION = {
    "id": "cube-3d",
    "meaning": (
        "How should the cube become 3-D in the instrument — show it as its flat projection from each viewpoint "
        "(projection IS the math), orbit the existing wheel in 3-D, or build true 3-D?"
    ),
    "options": [
        {
            "label": "Show its flat projection from each vantage",
            "implication": "Render the 2-D shadow of the cube as seen from wherever you're looking — matches 'projection is the maths', no new 3-D engine.",
            "recommended": True,
        },
        {
            "label": "Orbit the wheel in 3-D",
            "implication": "Spin the existing wheel in real 3-D space — a real orbit with little rebuild.",
        },
        {
            "label": "Build true 3-D",
            "implication": "A full new 3-D layer — richest, most work.",
        },
    ],
    "scope": "global",
    "subtype": "theorem-fork",
    "legibility": {
        "name": "How the cube goes 3-D",
        "is": "Your instrument — the shape follows your theorem",
        "why": (
            "The instrument needs the cube to become 3-D, and HOW depends on your theorem (the dimension call): "
            "show its flat projection from each viewpoint (which matches 'projection is the maths'), orbit the "
            "existing wheel in 3-D, or build a true 3-D layer. The lean is the projection one; your call on what "
            "dimension means likely settles which fits — so this pairs with that."
        ),
    },
}
