"""decisions/figure-gold-value.py — a DESIGN-LANGUAGE decision (surfaced by the source critical-comparison pass).

Raised by DNA from the default-to-reject verification of the 160-image source against the live DNA: the source
decks measure a MUTED gold (~#B29135) for big figures/accents, while the locked v2 mockups use a BRIGHT gold
(#E3C421). The verified ledger flagged this as an OPEN conflict for Tim, not auto-resolvable — so it's a real
pending decision. A true identity fork (no recommended option). Worded at Tim's altitude (the visual stakes,
no hex unless it helps). Copy may be refined by recollection (the voice lane); DNA authored the design content.
Resolved as decision://global/figure-gold-value. STATE is the latest decision_take mark (pending until chosen).
"""

DECISION = {
    "id": "figure-gold-value",
    "meaning": (
        "Big highlighted numbers and the company's accents all use one gold. The original source decks use a "
        "softer, muted gold; the recent mockups you locked in use a brighter, more saturated gold. Which gold "
        "is the company's?"
    ),
    "options": [
        {
            "label": "The bright gold",
            "implication": (
                "The vivid, saturated gold from the mockups you locked in. It reads confident and modern and "
                "it's what your recent work already uses — but it's brighter than the decks the language came "
                "from. Picking it makes the locked mockups the source of truth over the original decks."
            ),
        },
        {
            "label": "The muted gold",
            "implication": (
                "The softer, more restrained gold the original decks actually used. It reads refined and "
                "understated and is faithful to where the language came from — but it's a step back from the "
                "brighter gold in your locked mockups."
            ),
        },
    ],
    "scope": "global",
    "legibility": {
        "name": "Which gold is the company's",
        "is": "Reversible · sets the top note of the whole palette",
        "why": (
            "Gold is the company's single attention colour — the highlight on every key number, the recommended "
            "choice, the accents. This picks which gold the company speaks in: the bright, saturated one from "
            "your locked mockups, or the softer muted one the original decks measured. It ripples to charts and "
            "every gold accent, so it's worth setting deliberately. Not choosing changes nothing — the bright "
            "gold stays in place until you decide."
        ),
    },
}
