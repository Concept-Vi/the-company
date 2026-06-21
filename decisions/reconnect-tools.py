"""decisions/reconnect-tools.py — authorize: the one-time reconnect that switches on waiting tools (gather L2).
The single action only Tim can do."""

DECISION = {
    "id": "reconnect-tools",
    "meaning": (
        "Some new tools are built and waiting, but they only switch on when you reconnect the connection once. "
        "Do it now, or wait until more are ready so you only reconnect a single time?"
    ),
    "options": [
        {
            "label": "Reconnect now",
            "implication": "The tools that are already built switch on right away; you reconnect once now.",
        },
        {
            "label": "Wait and batch it",
            "implication": (
                "Hold until more tools are ready, then reconnect once for all of them — fewer interruptions, but "
                "the ready ones stay off a bit longer."
            ),
            "recommended": True,
        },
    ],
    "scope": "global",
    "subtype": "authorize",
    "legibility": {
        "name": "Reconnect to switch on the waiting tools",
        "is": "A one-time action — only you can do it",
        "why": (
            "New tools have been built but can't turn on by themselves — they need you to reconnect the "
            "connection once (the rest of the recent work is already live). This is just whether to do that "
            "reconnect now or batch it with more that are nearly ready. Nothing breaks either way."
        ),
    },
}
