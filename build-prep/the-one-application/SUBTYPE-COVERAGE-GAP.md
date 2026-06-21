# Subtype-coverage gap — 10 of 24 decisions were silently absent from Tim's queue

**Found:** 2026-06-21 (composition), while verifying the theorem-fork `ai_uncertainty_caveat` change.
**Severity:** CRITICAL — real pending decisions Tim must make were invisible on the LIVE operator surface.
**Status:** 3 fixed (tagged), 7 pending DNA owner-confirm, 1 schema gate proposed (coordinated).

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

**Visual-identity calls — PENDING (owner is DNA's lane to confirm: Tim's taste vs DNA-settled):**
`cluster-identity` · `core-shape` · `figure-gold-value` · `file-identity` · `form-taxonomy` ·
`line-language` · `opacity-meaning`. Most are visual-DIRECTION choices ("look is Tim's") → likely
`trade-off`/owner=tim; some may be DNA-settled tokens → `cross-lane`/owner=fabric. DNA confirms the
owner + variant per row; composition adds/confirms the subtype.

## Root-cause fix (coordinated — NOT a unilateral schema mutation)

1. **Tag all 10** (3 done; 7 with DNA). Must precede #2 or #2 invalidates them (the C5-class break).
2. **Make `subtype` required** in `decision.schema.json` once all rows carry it — so no future row can
   be authored without the discriminator and silently vanish. Sequence with the lead (other lanes
   author rows against this contract; the gate must land with the tagging, not before).
3. **Propagate the rule**: any lane authoring a `decisions/*.py` row MUST set `subtype` (document in
   `decisions/AGENTS.md` / the decision-row authoring contract). The gap exists because the subtype
   contract is composition's and wasn't surfaced to the lanes that author rows.

## Why this matters to the work in flight

Fork is wiring `required_elements` onto the `/api/decisions` feed keyed on `subtype` (same resolve-on-feed
as owner). That wiring + the theorem-fork caveat resolve correctly ONLY for rows that carry a subtype.
The untagged rows would resolve nothing. Tagging closes the gap at the source.
