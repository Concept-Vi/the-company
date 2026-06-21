"""decisions/substrate-home.py — the substrate-home decision (#7, the foundation-kind; GATHER #7).

Tim's master-scope #75 call, deepened by recollection from SUBSTRATE-HOME-CONVERGENCE-MAP.md + curated by
the lead. A REAL pending decision: should the company adopt ONE shared address-spine that every piece plugs
into — WHILE each piece keeps its own engine — or keep separate foundations. Worded at Tim's altitude (no
machine names — "pieces", "a shared spine", never "vi-vision:// address-space / Supabase / RLS"). Both of
Tim's refinements baked in: (1) unify at the address SPINE, pieces KEEP their own engines (NOT dissolved into
one store); (2) the existing backend content is read-and-supersede, never migrated as-is (co-location ≠
unification).

Resolved as decision://global/substrate-home. id MUST equal the file stem. STATE resolves from the latest
`decision_take` mark on the canonical address (pending until Tim chooses). Bound to the 5 held substrate
decisions (they NAME the address-model this spine uses) — render-order is FRAME-FIRST: this card, then the 5.
"""

DECISION = {
    "id": "substrate-home",
    "meaning": (
        "The company's pieces each store things their own way, now drifting onto one backend by "
        "accident — should they share one way to address everything, each keeping its own engine?"
    ),
    "options": [
        {
            "label": "One shared spine — each piece keeps its own engine",
            "implication": (
                "Every piece keeps its own engine — the factory its parts, the memory its recall, nothing "
                "flattened. What they share is one model for where things live and how they connect, so the "
                "company can see and decide across everything as one whole. A natural join, not a forced merge."
            ),
            "recommended": True,
        },
        {
            "label": "Keep each piece on its own store for now",
            "implication": (
                "Simplest immediately — nothing to converge, each piece ships where it sits. But it's "
                "four-or-more parallel stores: the company can't see across them as one, they drift apart, "
                "and unifying later costs more. This is the pattern the shared spine exists to avoid."
            ),
        },
        {
            "label": "Adopt the shared spine, but land pieces where they are first — converge as a follow",
            "implication": (
                "Keeps momentum — each piece builds now, the shared spine is adopted next as a deliberate "
                "follow-up. The risk: the separate stores entrench before the convergence happens, making "
                "the fold-in harder. A sequencing bet — move now, unify soon — rather than unify-first."
            ),
        },
    ],
    "scope": "global",
    "subtype": "trade-off",  # multi-option foundation direction (owner=tim) — was UNTAGGED → silently absent from the queue despite being its own declared FRAME-FIRST keystone. Tagged in-class with substrate-spine.
    "explanation_source": "code://build-prep/coverage-mechanism/SUBSTRATE-HOME-CONVERGENCE-MAP.md#candidate",
    "legibility": {
        "name": "Adopt one shared spine for the company's foundation",
        "is": "Reversible · your latest answer wins",
        "why": (
            "The pieces — the design factory, its memory, the design library, the record of decisions, the "
            "live channels — each grew their own way of storing things, and lately drift onto one backend by "
            "accident. One shared way to address everything (each piece keeping its own engine) lets the "
            "whole be seen and steered as one. What's already piled on that backend was a sketch — read it "
            "for what it reached for and rebuild toward it, don't preserve it as-is."
        ),
    },
}
