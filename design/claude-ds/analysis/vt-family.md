# Analysis · `vt-*` family + `vi-onepager` (one-pagers / tight-LOD)

> Sources: `vt-architects` (4pp, A4 portrait 910×1287), `vt-gatehouse` (3pp), `vt-property` (2pp),
> `vt-residential` (2pp), `vi-onepager` (1pp, 16:9). Status: ☑ analysed (family study).
>
> Verdict: **confirms the A4-print surface and the tight (summary) end of the LOD ladder, and
> gives the strongest proof yet that client/audience is a TEMPLATE PARAMETER.** No new grammar.

## Stress-test results
- **G3 — A4 print one-pager surface: confirmed.** `vt-*` are portrait A4 (910×1287). Same containment tree, zoning ladder, gold ramp, frame signature (V mark, hatch), triangle bullets, thin icons, soft panels — at print ratio. Surface axis now spans **slide(16:9, 3:2) ↔ web(scroll) ↔ print(A4)** with no grammar change.
- **C2 — tight LOD end: confirmed.** `vi-onepager` is the *summary* rung: the deck's "Current Practice | Virtual Hubs" compare archetype (pitch-deck p-05) condensed to **one page**. The LOD ladder now spans summary(1pp) → terse-pitch(16pp) → standard(17pp) → high-detail(49pp). Same template, pruned to claims.

## ★ Strongest proof yet: client/audience is a TEMPLATE PARAMETER
`vt-gatehouse/p-1` and `vt-residential/p-1` are the **same one-pager template** ("Discover the full/our Virtual Tour range" — identical 2-pane layout: left = intro + stage-chevrons + ▶ bullets + italic-bronze caption; right = stacked photo/screenshot tiles with annotation callout), filled with **different client** (Gatehouse Architects vs generic residential) and **different prose**. → audience/client = a **parameter**, content = data. Combined with recent-pitches (variant slides) and landing (variant pages + live toggle), the **{template + audience param}** mechanism is now confirmed across **decks, web, AND print** — truly universal.

## ★ New atom: stage / progress chevron indicator (recolors along the ramp)
A horizontal **chevron stepper** (`Design ▸ Marketing ▸ Sales ▸ Construction`, active step filled) appears on the vt one-pagers. Critically, its accent **slides along the gold→bronze ramp per variant**: gatehouse = gold-filled chevrons, residential = tan/bronze-filled. → confirms (a) a reusable **stepper/progress atom**, and (b) the **ramp is used for variant theming** — an element's ramp-position can be a per-variant parameter, not just a fixed role. → extends `--ramp-*` usage + a `Stepper` component.

## Other confirmations / small adds
- **Comparison table reused across surfaces:** vt-architects p-2 (Industry Resources × 8 capability columns, ✓/✗, ConceptV row highlighted cream+gold) = same atom as landing pricing table. → a genuinely cross-surface component.
- **Section bands within a print page** (white top section → neutral-grey "Find a solution" band) — the band/zoning model works on print too.
- **Annotation callout** (gold curved arrow + bold caption "Make live annotations…") pointing at a screenshot — a reusable annotation/pointer atom (relates to the connector language).
- **Two-pane one-pager layout** (text-left / media-stack-right) — a one-pager archetype (the print analogue of the deck's split).

## Diff vs system / prior folders
- ✅✅✅✅✅ Confirmed across **5 folders**: zoning ladder, gold ramp, frame signature, atoms, containment tree, narrative arc — now across slide + web + **print** surfaces and summary→high-detail LOD.
- ✏️ **Surface axis complete:** slide ↔ web ↔ print all proven. **LOD ladder complete:** 4 rungs summary→high-detail.
- ✏️ **Ramp = also a variant-theming parameter** (chevron recolor), not only a fixed semantic role.
- ➕ **New atoms:** stage/progress **chevron stepper**, **annotation callout/pointer**, two-pane one-pager archetype. Comparison table promoted to confirmed cross-surface component.
- ⚠️ No contradictions.

## → Docs updated
REQUIREMENTS G3 + C2 → 🟢; D2 reinforced; SYSTEM-GAPS + PROGRESS updated; AXES surface axis marked complete (slide↔web↔print).
