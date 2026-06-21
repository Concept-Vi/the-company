"""decisions/line-language.py — a DESIGN-LANGUAGE decision (surfaced by the source critical-comparison pass).

Raised by DNA from the default-to-reject verification: dashed vs solid lines carry meaning in the company's
diagrams, but the source decks are INCONSISTENT (some dashed=movement/solid=structure, others flip it — a
verified cross-collection tension). This decides one fixed line-language vs context-dependent. RECOMMENDED:
one fixed rule (the mono-dialect spine — consistency is a system value; flag any deck that needs its own as an
explicit exception). Copy may be refined by recollection. Resolved as decision://global/line-language.
"""

DECISION = {
    "id": "line-language",
    "meaning": (
        "Lines in the company's diagrams come dashed or solid, and which one means what carries meaning. Across "
        "the source decks it isn't consistent — some use dashed for movement and solid for structure, others "
        "flip it. Should there be one fixed rule everywhere, or can each context use its own?"
    ),
    "options": [
        {
            "label": "One fixed line-language",
            "implication": (
                "Dashed always means one thing (movement, flow, what's planned), solid always means another "
                "(structure, what's fixed) — everywhere, every diagram. One rule the whole company reads the "
                "same way; a deck that genuinely needs a different meaning becomes a named, deliberate exception."
            ),
            "recommended": True,
        },
        {
            "label": "Let it vary by context",
            "implication": (
                "Each deck or surface picks its own dashed/solid meaning. More flexible per context, but a "
                "reader can't carry one rule across — the same kind of line can mean different things in "
                "different places."
            ),
        },
    ],
    "scope": "global",
    "subtype": "trade-off",  # design-language law, owner=tim (DNA leans 'one fixed', Tim decides). card_variant may want line-sample previews — DNA render refinement (follow).
    "legibility": {
        "name": "One line-language, or context-dependent",
        "is": "Reversible · sets how every diagram reads",
        "why": (
            "Dashed and solid lines are how the company's diagrams show relationships — movement vs structure, "
            "planned vs fixed. The source decks aren't consistent about which is which. This decides whether to "
            "lock one meaning everywhere, so every diagram reads the same way, or let each context choose. One "
            "rule is clearer to read across the whole company; varying is more flexible but can confuse. "
            "Recommended: one fixed language, with exceptions named deliberately."
        ),
    },
}
