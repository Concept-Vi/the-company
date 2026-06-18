"""decisions/form-taxonomy.py — the form taxonomy (GATHER #5 / UNION COV2; KIND: taxonomy).

A held substrate decision (names the real kinds within the substrate-home frame; renders AFTER it). At
Tim's altitude. v1 = the 3-OPTION approach-pick (lead's call — keeps composition's v1 one-shape, NO
structural variant). Lean = discover-from-open-coverage (Tim's coverage law — the kinds come FROM the
outputs, not a guess). ★ The evidence→author card is a SECOND step, built when discover-from-coverage RUNS
+ produces real kinds. Resolves decision://global/form-taxonomy.
"""

DECISION = {
    "id": "form-taxonomy",
    "meaning": (
        "What are the REAL kinds of things in the company's content? Right now the kinds (decision, log, "
        "registry, prose) are a prior AI's guess, used to route how deeply each thing gets processed. "
        "Should the company look at EVERYTHING first — an open, full-coverage pass that describes what's "
        "actually there — and let the real kinds emerge so you author the true set, keep the current "
        "guess for now, or refine the guess as coverage arrives?"
    ),
    "options": [
        {
            "label": "Discover the real kinds from open coverage, then you author them",
            "implication": (
                "Run the open full-coverage pass — describe what's actually there with no forced labels — "
                "so the natural kinds emerge and get proposed to you to author the true taxonomy. Grounded "
                "in reality, not a guess; the deeper-processing routing stays paused until the real kinds "
                "are recorded. (This IS the company's coverage way applied to its own kinds — your law.)"
            ),
            "recommended": True,
        },
        {
            "label": "Keep the current guess for now",
            "implication": (
                "Use decision / log / registry / prose as-is so the deeper-vs-cheaper routing keeps "
                "working — but it's scaffolding, likely wrong, and routes how much effort each thing gets "
                "on a guess rather than on what's really there."
            ),
        },
        {
            "label": "Refine the guess incrementally as coverage arrives",
            "implication": (
                "Don't block on a full pass — keep the current kinds running and let coverage refine them "
                "as it comes in. Keeps momentum — but the taxonomy stays provisional longer, and the "
                "routing rides a half-real set in the meantime."
            ),
        },
    ],
    "scope": "global",
    "explanation_source": "code://build-prep/the-one-application/UNION-DIVERGENCE-LEDGER.md",
    "legibility": {
        "name": "The real kinds of things in the content",
        "is": "a decision to make",
        "why": (
            "It decides whether the company discovers its real content-kinds from an open coverage pass "
            "(and you author them) or keeps a prior guess — the basis for how deeply each thing is processed."
        ),
    },
}
