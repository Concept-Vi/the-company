"""decisions/core-shape.py — a DESIGN-LANGUAGE decision (surfaced by the source critical-comparison pass).

Raised by DNA from the default-to-reject verification: the source uses typed geometry (octagon, hexagon,
diamond, circle), rarer shapes meaning more important things. The octagon = Virtual-Tours output (gold outline,
once per page — rule upheld at source); the hexagon = engine. But which one carries 'the core' (the single most
central mark) is NOT consistent across the decks — a genuine identity fork for Tim, no recommended option.
Copy may be refined by recollection. Resolved as decision://global/core-shape.
"""

DECISION = {
    "id": "core-shape",
    "meaning": (
        "The company's diagrams give each shape a fixed meaning, and the rarer a shape the more important the "
        "thing it marks. The octagon and the hexagon are the two heaviest shapes — but which one is 'the core', "
        "the single most central mark, isn't consistent across the decks. Which shape carries the core?"
    ),
    "options": [
        {
            "label": "The octagon is the core",
            "implication": (
                "The eight-sided shape — the rarest, most faceted — marks the single most central thing, "
                "appearing just once. This makes 'most faceted = most important' the rule, with the octagon at "
                "the centre and the hexagon reserved for the engines around it."
            ),
        },
        {
            "label": "The hexagon is the core",
            "implication": (
                "The engine shape carries the centre instead. The octagon stays as the Virtual-Tours output "
                "mark; the hexagon becomes the central thing everything else orbits."
            ),
        },
    ],
    "scope": "global",
    "legibility": {
        "name": "Which shape is the company's core",
        "is": "Reversible · anchors the whole shape language",
        "why": (
            "The company's shapes are a language — octagon, hexagon, diamond, circle each mean something, and "
            "rarer shapes mean more important things. This sets which shape is THE core: the single most central "
            "mark everything is arranged around. The source decks aren't consistent about it, so it's your call. "
            "It anchors what the most important thing looks like everywhere a diagram appears."
        ),
    },
}
