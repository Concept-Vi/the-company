"""decisions/file-identity.py — file identity (GATHER #1 / UNION ID1; KIND: identity).

A held substrate decision (names part of the address-model within the substrate-home frame — renders
AFTER substrate-home). At Tim's altitude (no machine names — never file:// / cas://). Lean = BOTH
(content-resolved identity, the with-derivation/FRD frame the lead modelled). Resolves
decision://global/file-identity; STATE from the latest decision_take mark (pending until Tim chooses).
"""

DECISION = {
    "id": "file-identity",
    "meaning": (
        "Is a saved file the same thing as the content in it, or its own thing that points at "
        "content? — it decides whether two files with identical content are one thing or two."
    ),
    "options": [
        {
            "label": "Identity is the CONTENT — identical content is one thing",
            "implication": (
                "Two saved things with the same content are recognised as one (no duplication); changing "
                "the content makes a new identity. Clean and deduplicated — but a file's own name and "
                "history matter less than what it currently holds."
            ),
        },
        {
            "label": "Identity is the FILE — each saved thing is its own thing",
            "implication": (
                "Each file is itself — it keeps its own name, history, and place even if its content "
                "matches another's; content is what it holds, not what it IS. Preserves every file's own "
                "story — but identical content can sit in two separate places."
            ),
        },
        {
            "label": "Both — a file is its own thing that resolves to shared content",
            "implication": (
                "A file has its own identity AND points at content that can be shared underneath — the "
                "most expressive, and the same 'a stable thing resolving to live content' shape the "
                "company's foundational thinking already uses. The remaining detail to settle: is the "
                "shared-content layer one identity, or two kinds of reference? (My lean here — "
                "your call.)"
            ),
            "recommended": True,
        },
    ],
    "scope": "global",
    "explanation_source": "code://build-prep/the-one-application/UNION-DIVERGENCE-LEDGER.md",
    "legibility": {
        "name": "How a saved file's identity works",
        "is": "Reversible · your latest answer wins",
        "why": (
            "It matters when two saved things hold identical content — one thing, or two that happen to "
            "match? And when content changes — a new thing, or the same thing changed? This is the "
            "foundation for how the company recognises things."
        ),
    },
}
