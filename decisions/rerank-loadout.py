"""decisions/rerank-loadout.py — the RERANK LOADOUT decision (the 7th card; KIND: capability/loadout).

Born from Tim's own catch (2026-06-18, board://item-a3844c46): the precision re-sort behind every
decision's explanation was switched OFF to stop a >15s freeze (it ran on the slow processor), leaving
decisions grounded by rough similarity — and the "fix later" had no tracked owner. Tim: "figure it out."
So it becomes a DECIDED decision, on the decision surface itself (self-similar — the rerank decision,
decided through the decision wire).

A capability/loadout decision — the SAME base archetype as merge-sa (composition's v1 one-shape holds;
domain-tuned by content, no structural variant). At Tim's altitude: NO machine names (never "jina /
rerank / cosine / CPU / VRAM / GPU" — say "sharper re-sorting", "rough similarity", "the fast processor",
"the graphics card's memory"). Resolves decision://global/rerank-loadout; STATE resolves from the latest
decision_take mark (pending until Tim chooses).

ON DECIDE: the take writes the per-mode loadout registry ([[mode-loadout-registry]] — per-mode model
loadout is a registry concern), so the chosen posture becomes the live setting, not a code edit.
★ Option 2 (give it the graphics card) is a graphics-card-memory LOAD → consult-before-model-loads:
the card is FRAMED so that Tim PICKING option 2 IS the consult-satisfied authorization for that load.
"""

DECISION = {
    "id": "rerank-loadout",
    "meaning": (
        "When the Company explains a decision to you, it gathers related context from its memory and "
        "orders it by how relevant each piece is. Right now it uses ROUGH similarity to order it. There "
        "is a sharper step that re-sorts that context so the most relevant comes first — but that step is "
        "slow on the current setup (it froze the decision surface), so it's switched OFF for the live "
        "explanation. How should the Company bring the sharper ordering back: leave it off and keep rough "
        "similarity, give the sharper step the fast processor so it's near-instant again, add a lighter "
        "quick version beside it, or sharpen only the top few / quietly in the background?"
    ),
    "options": [
        {
            "label": "Leave it off — order by rough similarity",
            "implication": (
                "Decisions keep getting real context — just ordered by rough similarity rather than the "
                "sharper re-sort. Nothing new runs and it stays instant; but the ordering is rougher, so "
                "the single most relevant piece of context isn't always first. (This is how it works right "
                "now — choosing it makes today's stop-gap the deliberate, settled answer.)"
            ),
        },
        {
            "label": "Give the sharper step the fast processor",
            "implication": (
                "The sharper re-sorting moves onto the graphics card and becomes near-instant — the precise "
                "ordering comes back for every decision, and everywhere else the Company uses it. Choosing "
                "this turns on a tool that uses the graphics card's memory, so picking it is YOU authorizing "
                "that load. (My read: the clean full restore — but whether the graphics card has room "
                "alongside everything else running is your call.)"
            ),
            "recommended": True,
        },
        {
            "label": "Add a lighter, faster sharpener",
            "implication": (
                "A smaller, quicker re-sorter handles the live explanation while the heavier precise one "
                "stays for the highest-stakes uses. Faster than the precise step, sharper than rough "
                "similarity — a middle ground, with a small quality tradeoff and a second tool to keep."
            ),
        },
        {
            "label": "Sharpen fewer, or quietly in the background",
            "implication": (
                "Keep the precise step but only sharpen the top few pieces, or compute the sharper order "
                "quietly AFTER you open the card and reuse it next time. Brings the precision back with no "
                "new load and no freeze — but the very first time you open a card you may still see the "
                "rougher order."
            ),
        },
    ],
    "scope": "global",
    "explanation_source": "board://item-a3844c46",
    "legibility": {
        "name": "The sharpness of the context behind a decision",
        "is": "a decision to make",
        "why": (
            "It decides whether — and how — the Company restores the sharper re-sorting of the context it "
            "uses to explain each decision, now that the precise step is switched off to keep decisions fast."
        ),
    },
}
