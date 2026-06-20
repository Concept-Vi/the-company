"""decisions/opacity-meaning.py — a DESIGN-LANGUAGE decision (surfaced by the source critical-comparison pass).

Raised by DNA from the default-to-reject verification: the source SOMETIMES fades future/planned elements and
keeps realised ones solid — but the unifying "opacity = how realised something is" LAW is DNA's inference, not a
stated source rule (held in still-unverified). So this is genuinely Tim's to make law or not — no recommended
option (the lean shouldn't come from an unproven inference). Copy may be refined by recollection.
Resolved as decision://global/opacity-meaning.
"""

DECISION = {
    "id": "opacity-meaning",
    "meaning": (
        "In the source, faded or see-through elements sometimes mean 'not yet / planned / future', and fully "
        "solid sometimes means the realised thing. Should faded-ness become a fixed rule — meaning how real or "
        "committed something is — or stay just a look used case by case?"
    ),
    "options": [
        {
            "label": "Make faded-ness mean something",
            "implication": (
                "A fixed rule: the more faded an element, the less realised it is (planned, future, tentative); "
                "fully solid means realised and committed. Then any surface can show what's real versus planned "
                "just by how solid it looks — a quiet, consistent signal carried by opacity everywhere."
            ),
        },
        {
            "label": "Keep it just a look",
            "implication": (
                "Opacity stays a visual treatment with no fixed meaning — sometimes faded, sometimes not, by "
                "taste. Simpler and less to enforce, but faded-ness won't reliably tell anyone whether something "
                "is real or only planned."
            ),
        },
    ],
    "scope": "global",
    "legibility": {
        "name": "Does faded-ness mean 'not yet'",
        "is": "Reversible · decides if opacity carries meaning",
        "why": (
            "The source sometimes fades future or planned things and keeps realised things solid — but never as "
            "a stated rule. This decides whether to make it one: opacity = how realised something is, so any "
            "surface can show planned-versus-real at a glance. Powerful if locked in; if not, faded-ness stays "
            "decorative. This one started as a pattern we noticed rather than a rule the decks state, so it's "
            "genuinely your call whether to make it law."
        ),
    },
}
