"""decisions/real-v-symbol.py — trade-off: when/with-what the real V replaces the placeholder (gather P2)."""

DECISION = {
    "id": "real-v-symbol",
    "meaning": (
        "The right-hand-man's icon is a placeholder. When do you put the real V symbol in, and with what?"
    ),
    "options": [
        {
            "label": "You provide the real V → swap it in",
            "implication": "The slot's ready; drop your real V in whenever you have it and it swaps cleanly.",
        },
        {
            "label": "A fuller interim V now",
            "implication": "A better stand-in goes in now, the real one later.",
        },
        {
            "label": "After the main faces are built",
            "implication": "Focus the faces first; bring the V in once they're landed.",
        },
    ],
    "scope": "global",
    "subtype": "trade-off",
    "legibility": {
        "name": "Put the real V in for the right-hand-man",
        "is": "Your symbol — a swap when ready",
        "why": (
            "The right-hand-man shows a placeholder icon; the slot is built to swap the real V in cleanly (and "
            "later the brain's living V). This is just timing and what — your real V now, a fuller interim, or "
            "after the faces. Nothing's blocked; the swap seam waits for you."
        ),
    },
}
