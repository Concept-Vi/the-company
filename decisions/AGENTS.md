# decisions/ — the decision-row authoring contract (READ BEFORE adding a decision)

Each `<id>.py` declares a `DECISION` dict: ONE real pending decision the company surfaces to its operator
(Tim) or settles in-fabric. The decision surface resolves it into a card he can read and decide in. Any
lane may author a row here — but a row authored wrong is **silently dropped**, so follow this exactly.

## The row shape

```python
DECISION = {
    "id": "<must-equal-the-file-stem>",        # required — addressable as decision://<scope>/<id>; fail-loud if mismatched
    "meaning": "<the decision, at the operator's altitude>",   # required
    "options": [                                # required — 2+; each is a real choice
        {"label": "...", "implication": "...", "recommended": True},  # recommended is optional, at most one
        {"label": "...", "implication": "..."},
    ],
    "scope": "global",                          # the address scope
    "subtype": "<a decision_subtypes id>",      # ★ MANDATORY IN PRACTICE — see below
    "explanation_source": "board://... | code://...",   # optional — a pointer the RHM grounds the explain in
    "legibility": {"name": "...", "is": "...", "why": "..."},   # how it reads in the operator surface
}
```

## ★ `subtype` is MANDATORY — omit it and your decision VANISHES

`subtype` is the discriminator the WHOLE resolution chain hangs on:
`decision.subtype` → `decision_subtypes/<subtype>.py` → **owner** (whose queue) · **card_variant** (how it
renders) · **required_elements** (what the card must carry). There is **no `owner` field on the row** and
**no fallback** (deleted — "pure registry-true"). So a row with no subtype resolves **no owner → it is
silently excluded from Tim's queue**, can't render (no variant), and resolves no required_elements.

> This is not hypothetical: on 2026-06-21, 10 of 24 rows were authored without `subtype` and were invisible
> on the LIVE operator surface — including `substrate-home`, a frame-first keystone. See
> `build-prep/the-one-application/SUBTYPE-COVERAGE-GAP.md`. `decision.schema.json` does not (yet) force
> `subtype`, so the schema will NOT catch this for you. You must set it.

**Pick the subtype** from the vocabulary in `decision_subtypes/` (see its AGENTS.md):
- `authorize` — approve/hold a consequential (often security) action → binary card, owner=tim
- `trade-off` — a multi-option direction/architecture choice → n-panel, owner=tim
- `theorem-fork` — a conceptual fork in Tim's math → n-panel + the AI-uncertainty caveat, owner=tim
- `cross-lane` — a technical choice the streams settle (NOT Tim-facing) → n-panel, owner=fabric

If your decision is a genuinely new SHAPE (ranking · allocation · workflow · single-confirm), DERIVE a new
subtype: add a `decision_subtypes/<id>.py` row (never a code edit), then use it. Coordinate the owner call
with composition if it's not obvious.

## The legibility law (operator altitude)

`meaning`, every `option`, and `legibility` are written for Tim — **no machine names** (never
"vi-vision SA / RLS / Supabase / cosine / VRAM"; say "the design library", "the fast processor"). `legibility`
is `{name: the card's title, is: the reversibility/stakes line, why: the grounded one-paragraph context}`.
State (pending/decided) is NOT stored here — it resolves from the latest `decision_take` mark on the address.
