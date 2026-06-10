"""dials/anticipation.py — how much idle compute becomes foresight (Track-1 round 2)."""
DIAL = {
    "id": "anticipation",
    "label": "Anticipation (how far ahead the brain thinks)",
    "governs": ("the resolver's pre-retrieval: whether memory/context is fetched only on demand, "
                "pre-resolved as the now shifts (mode/surface/activity changes), or speculatively "
                "staged ahead of need (e.g. overnight chains warming tomorrow's context). "
                "CONSUMERS (named honestly): the now-organ + resolver when built (GC14/Track-1); "
                "nothing reads this yet — the dial is their configuration seam, adjustable from day one."),
    "positions": [
        {"name": "reactive", "meaning": "retrieve only when asked — no idle compute spent on foresight"},
        {"name": "warm", "meaning": "pre-resolve as the now shifts — surfaces and context are warm on arrival"},
        {"name": "hot", "meaning": "speculate — run retrieval/analysis chains ahead of need and stage the results"},
    ],
    "default": "warm",
}
