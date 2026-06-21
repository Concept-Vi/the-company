"""decisions/lock-card-look.py — authorize: lock the card's look as the standard (gather L4). Tim's by-sight nod."""

DECISION = {
    "id": "lock-card-look",
    "meaning": (
        "The first decision card's look is now at the level we validated with you. Lock it as the standard "
        "everything else follows, or keep refining the feel before we call it the bar?"
    ),
    "options": [
        {
            "label": "Lock it as the standard",
            "implication": "This look becomes the bar every other card and surface is held to; we build the breadth on it.",
        },
        {
            "label": "Keep refining the feel first",
            "implication": "Keep lifting the craft a bit more before fixing it as the standard; the breadth still builds, the bar just settles a touch later.",
        },
    ],
    "scope": "global",
    "subtype": "authorize",
    "legibility": {
        "name": "Lock the card's look as the standard",
        "is": "Your by-sight call — reversible",
        "why": (
            "The card reached the look you signed off on in direction; the rendered breadth already generalises "
            "from it. This is only whether to call THIS the felt-quality bar now — a by-sight judgment that's "
            "yours, never something the system marks done for you. Locking it just sets what the rest matches."
        ),
    },
}
