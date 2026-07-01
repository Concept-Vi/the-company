# AUDIT · slice 1 — tokens & consumers (scoped)

> Deep audit for the token-recalibration slice. **Vigilance correction recorded — read before
> touching colour.**

## ★ Correction to the synthesis plan (caught in audit)
- **`--accent-gold: #E0C010` is the REAL logo gold** (sampled from the actual ConceptV logo PNG, 234k px). It is a brand ASSET, not a guess. **Do NOT overwrite/soften it.**
- The decks' "softer working gold" (`#d6bf57`) is the **applied** gold (large washes, hero numbers, diagram-ring sequence) — it is a **ramp stop**, not a replacement. → Resolution: **keep `--accent-gold` = `#E0C010`; ADD `--ramp-*`** (bright/working-gold/bronze/tan). Use ramp for sequences/washes; keep the logo gold for the mark + primary decisions.
- Likewise bronze: keep `--accent-bronze #988058` (documented role) but the decks use a **lighter structural bronze `#c09d5d`** for section-headers/captions → add as `--ramp-3` (and optionally `--accent-bronze-warm`), don't overwrite.

## Consumer map for gold/bronze (the de-hardcoding backlog)
Token vars exist, but the hex is **hardcoded** in many consumers (drift risk — fix in a dedicated de-hardcode pass, NOT blindly):
- `app/canvases/Colors.jsx` — BASE_PALETTE + makeTokenMap + prompt strings hardcode `#E0C010`/`#988058`.
- `app/canvases/Patterns.jsx`, `app/canvases/Workshop.jsx` — prompt strings + theme-chip samples.
- `app/canvases/workshop/Export.jsx` — standalone CSS `--gold:#E0C010…` (exported artifacts).
- `app/canvases/workshop/Layouts.jsx` — **blueprint-ghost SVG (#988058) + gold-grid overlay (#E0C010) + diamond watermark** already exist (⇒ system not as "flat" as README says; tension #1/#2 partially already built here — mine this for the texture tokens).
- `assets/icons/CvIcon.jsx` — references `var(--accent-bronze/gold)` ✅ (token-correct).
- `preview/*` cards + `app/services/openai.js` brand-prompt — hardcoded for display/prompt (lower risk).

## Slice-1 action taken
- **Additive only:** add `--ramp-1..4` to `colors_and_type.css` (logo gold + bronze untouched). Annotated `@kind color`. No consumer churn this step.
- Zone ladder: current `--zone-*` already mixes toward `--zone-ground`; sampled targets (`#fdfcf7` etc.) are close at intensity 1 — **defer pigment retune to a measured pass** (compare computed output vs sampled) rather than guess now.

## Next (deliberate, not blind)
1. De-hardcode pass: point the ~10 consumers at `var(--accent-gold)`/ramp (so future recalibration propagates). Highest drift-risk item.
2. Measured zone-ladder retune: compute current `--zone-*-surface` output, diff vs sampled `#fdfcf7/#f8f8f8`, adjust pigment %/values to match, verify.
3. Reconcile status chips (mine) with existing warm status dots (`--status-*` already exist at lines ~59-68 — KEEP, extend).
