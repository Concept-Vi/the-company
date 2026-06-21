# Subtype-coverage gap — 10 of 24 decisions were silently absent from Tim's queue

**Found:** 2026-06-21 (composition), while verifying the theorem-fork `ai_uncertainty_caveat` change.
**Severity:** CRITICAL — real pending decisions Tim must make were invisible on the LIVE operator surface.
**Status:** CLOSED — all 24 rows tagged (queue 14 → 24), schema gate landed (subtype now required, all 24
validate, no C5 break), authoring contract written. One residual: theorem-fork `grounding_source` (below).

> **Correction (after reading all 10, not just filenames):** the first pass labeled 7 rows "visual" and
> deferred their owner to DNA. Reading them overturned that — only 4 are design-language; 3
> (`form-taxonomy`, `file-identity`, `cluster-identity`) are **held-substrate** decisions in
> substrate-home's frame, never DNA's. And all 7 self-declare **owner=tim** in their own docstrings
> ("your call" / "an OPEN conflict for Tim" / "genuinely Tim's"), so none carried a DNA-owned *owner*
> question — DNA's only stake is the *card_variant* (a render refinement). Lesson: classify by reading the
> row, never by the filename (the exact trap `event-streams` had already sprung).

## The defect

The decision-surface resolves a row's **owner** (whose queue) and its **card_variant** (how it
renders) and now (per the lead) its **required_elements** — all keyed on `decision.subtype` via the
`decision_subtypes` registry. The owner-fallback was deliberately deleted ("pure registry-true").

But `subtype` is **NOT required** by the decision contract. Evidence:
- `schemas/vi-vision/v1/decision.schema.json` → `required: ["id", "meaning", "options"]` (no `subtype`).
- There is **no `owner` property** on the decision schema at all — owner resolves ONLY via subtype.

So a row authored without `subtype` is fully schema-conformant, resolves **no owner**, and — with the
fallback gone — is **silently excluded** from Tim's `owner==tim` queue. It also can't render (no
`card_variant`) and resolves no `required_elements` (no caveat, no grounding).

**Result:** 24 real decision rows exist; only 14 carried a subtype; **10 were absent from Tim's queue.**
The operator surface showed "Tim's 14-queue" — it was really 14 of 24. This is the exact silent-drop
the decision surface exists to prevent: a decision Tim needs to make, dropped without a trace.

## The untagged 10 (all authored by other lanes, none of which the subtype contract reached)

**Architectural / Tim's master-scope direction calls — FIXED (tagged `trade-off`, owner=tim, n-panel):**
- `substrate-home` — declares itself "Tim's master-scope #75 call… render-order is FRAME-FIRST: this
  card, then the 5." A frame-first KEYSTONE that was invisible. ← worst instance.
- `event-streams` — a held-substrate address-model decision meant to render after substrate-home.
- `rerank-loadout` — "the 7th card, on the decision surface itself"; Tim's "figure it out." NOTE:
  option-2 carries an embedded load-authorization (picking it IS the consult-satisfied authorize) —
  `trade-off` fits the 4-option n-panel direction shape; flag if a capability/authorize-hybrid subtype
  is later wanted.

These three are in-class with `substrate-spine` (already `trade-off`), unambiguously Tim's, and tagging
is purely additive (cannot affect the 14 already showing). Tim's queue is now **17**.

**The other 7 — all now TAGGED `trade-off`/owner=tim (queue 17 → 24):**
- *Held-substrate (NOT visual — substrate-home's frame):* `form-taxonomy` (content-kind taxonomy),
  `file-identity` + `cluster-identity` (address-model identity). In-class with `event-streams`.
- *Design-language (DNA-raised, but owner=tim by their own docstrings):* `core-shape`,
  `figure-gold-value`, `line-language`, `opacity-meaning`. **DNA's remaining stake is the card_variant
  only** — these 4 may want a design-specific render (gold swatches, shape/line/opacity previews) rather
  than text n-panel. That's a render refinement (a follow), NOT an owner question and NOT blocking.

## Root-cause fix (coordinated — done)

1. **Tag all 10** — DONE. All 24 rows now carry a subtype; all owner=tim in the current set.
2. **Make `subtype` required** in `decision.schema.json` — DONE (tag-then-require: all 24 tagged first,
   then `required` gained `subtype`; re-validated all 24 PASS → no C5-class break). Rides the lead's
   next bounce alongside the tags.
3. **Propagate the rule** — DONE. `decisions/AGENTS.md` now states every row MUST set subtype, with the
   why. Any lane authoring a row against the live gate must include subtype (fail-loud otherwise).

## Residuals (flagged, not composition's to close alone)

- **`decided` ≠ `pending` for the 4 design-language rows** (core-shape→octagon · figure-gold→#B29135 ·
  line-language→context-dependent · opacity→multi-use): these are DECIDED. State resolves from a
  `decision_take` mark, NOT the row — so they need their decided marks written (DNA's split) BEFORE the
  bounce, else the subtype-tag resolves them as PENDING and resurfaces settled calls. (Couldn't
  self-verify the marks: the `marks` tool currently fails loud on an unrelated `explain_role` role-schema
  error — `prompt_slot` not in the C2.1 field set — flagged to fork.)
- **theorem-fork `grounding_source` has no source** on `cube-3d` + `dimension-meaning` (both set no
  `explanation_source`; the only named recollection constant is the caveat). When fork resolves
  required_elements onto the feed, `grounding_source` resolves to NOTHING on the 2 cards projection
  verifies by-sight — the same silent-gap class. Needs recollection to supply a theorem-fork grounding
  (same server-side pattern as the caveat) OR a real `explanation_source` set on both rows.
- **`form-taxonomy` stays `trade-off`, NOT `theorem-fork`** (the lead asked): theorem-fork is a fork in
  TIM'S MATHS (his bedrock); form-taxonomy is a coverage/discovery direction over CONTENT kinds — its
  AI-guess nature is honestly in the option text already, and theorem-fork's caveat ("grounded in Tim's
  maths") would mis-apply. Note: the "this rests on an AI inference" caveat-need is GENERAL (not maths-
  specific) — if wanted for form-taxonomy, that's a row-level caveat flag, a separate enhancement, not
  stretching theorem-fork.

## Why this matters to the work in flight

Fork is wiring `required_elements` onto the `/api/decisions` feed keyed on `subtype` (same resolve-on-feed
as owner). That wiring + the theorem-fork caveat resolve correctly ONLY for rows that carry a subtype.
The untagged rows would resolve nothing. Tagging closes the gap at the source.
