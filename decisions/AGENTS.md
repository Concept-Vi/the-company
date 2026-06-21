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

## Set `explanation_source` to the REAL source you gathered it FROM (the grounding provenance)

`explanation_source` is the decision's **traceable provenance pointer** — the grounding RHM traces THROUGH it
to the real content (recollection's genuine-provenance mechanism). When you author/gather a decision (the
Face-Pipeline gather, or by hand), **record the real source it was gathered FROM** into `explanation_source`:
an ADDRESS — `board://…` · `code://…` · `channel-thread://…` · a corpus addr — where the decision's specific
content appears. New decisions are then **born traceable** (no later backfill).

★ THE HOLE-2 GUARD: it must be a POINTER traced through to REAL content, **never a re-stated prose claim** of
the origin (that grounds a claim in a claim). And a **wrong-origin pointer is WORSE than none** — set it ONLY
if the source VERBATIM-contains the decision's specific content; if you can't verify that, leave it ABSENT
(the on-topic fallback grounds honestly). Theorem-forks point at Tim's real maths source (recollection's domain).

**Level-3 vs Level-4 (the honest bar):** pointing at the captured fabric artifact (the board item / gap-note
filed during real operation, whose content is verbatim the fact) = **Level 3**, the grounding bar — label it
honestly "grounded in the captured origin," NEVER "Tim's verbatim words." **Going-forward Level-4 readiness:**
when the gather/capture files that artifact, ALSO record its own **raw source-link** (the channel-msg /
transcript it came from — the board item's `source`/`channel`/`thread`/`links` fields), so grounding can later
trace the extra hop to Tim's raw utterance. New captures born traceable-to-raw — but DON'T retrofit old ones
via session-search (drift-prone bleed); Level 4 is a forward deepening, not a backfill.
