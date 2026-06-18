"""decisions/file-identity.py — file identity (GATHER #1 / UNION ID1; KIND: identity).

A held substrate decision (names part of the address-model within the substrate-home frame — renders
AFTER substrate-home). At Tim's altitude (no machine names — never file:// / cas://). Lean = BOTH
(content-resolved identity, the with-derivation/FRD frame the lead modelled). Resolves
decision://global/file-identity; STATE from the latest decision_take mark (pending until Tim chooses).
"""

DECISION = {
    "id": "file-identity",
    "meaning": (
        "When the company saves something, is the saved file 'the same thing' as the content written in "
        "it — or its own separate thing that points at the content? It matters when two saved things hold "
        "identical content: are they one thing, or two things that happen to match? And when content "
        "changes: is it a new thing, or the same thing changed?"
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
                "shared-content layer one identity, or two kinds of reference? (The RHM leans here, in "
                "the with-derivation frame — your call.)"
            ),
            "recommended": True,
        },
    ],
    "scope": "global",
    "explanation_source": "code://build-prep/the-one-application/UNION-DIVERGENCE-LEDGER.md",
    "legibility": {
        "name": "How a saved file's identity works",
        "is": "a decision to make",
        "why": (
            "It decides whether identical content is one thing or two, and whether changing content makes "
            "a new thing or the same thing changed — the foundation for how the company recognises things."
        ),
    },
}
