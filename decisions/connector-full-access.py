"""decisions/connector-full-access.py — authorize: full remote access once it's proven you (gather F3).
Operator-altitude wording — no "#1b / OAuth / posture" machine-names."""

DECISION = {
    "id": "connector-full-access",
    "meaning": (
        "When you connect from outside — your phone, or a tool like ChatGPT — the company already does the "
        "safe things. Once it can prove it's really YOU connecting, should that unlock the FULL set, including "
        "the powerful ones, or stay limited until that proof is rock-solid?"
    ),
    "options": [
        {
            "label": "Full access once it's proven you",
            "implication": (
                "Being verified as you unlocks everything, like sitting at your own desk; anyone who can't prove "
                "they're you stays locked out by default. Turned on only after the identity check is shown to be "
                "un-fakeable."
            ),
            "recommended": True,
        },
        {
            "label": "Stay limited until the proof's airtight",
            "implication": (
                "Keep the safe-only set from outside until the identity check has been hardened and you're "
                "satisfied nothing can impersonate you. Full access waits."
            ),
        },
    ],
    "scope": "global",
    "subtype": "authorize",
    "legibility": {
        "name": "Full access from outside once it's proven you",
        "is": "Security — reversible, you set the bar",
        "why": (
            "The outside connection is built and works for safe things; the question is whether proving it's "
            "genuinely you should unlock the full, powerful set (like being at your own machine), with everyone "
            "else denied by default. The condition you set: only once the 'is it really Tim' check is verified "
            "un-spoofable. Until you choose, it stays safe-only."
        ),
    },
}
