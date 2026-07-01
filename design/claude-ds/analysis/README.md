# ConceptV — Material Analysis (DNA extraction)

> 🟢 **NEW SESSION? READ `analysis/HANDOFF.md` FIRST** — it is the complete, seamless briefing
> (mission, mindset, full repo map, conventions, traps, what's done, what's next). This file is
> just the analysis-method reference.

This folder is the **analysis layer**. It does not change the design system. It
reconstructs the *generative rules* behind the source material in `ingest/` so
that confirmed universals can later be promoted into the system as tokens,
pattern primitives, and components.

> Principle: the images are **evidence of a system**, not a style to copy.
> We extract rules as **ratios & relationships**, never fixed pixels, so they
> recompute at any screen size and can drive both static visuals and
> interactive components.

## Workflow (one folder at a time)

1. **Ingest** — copy the folder's images into `_ingest/<folder>/` (downsample huge ones if needed).
2. **Analyse** — fill in `analysis/<folder>.md` from `_TEMPLATE.md`, applying the 9-level lens. Sample real pixel values for colour/zoning. Measure positions as % of frame.
3. **Diff** — check every rule against what's already documented. Mark each: ✅ confirms · ➕ new · ✏️ generalises · ⚠️ contradicts.
4. **Log gaps** — append anything not yet in the design system to `SYSTEM-GAPS.md`.
5. **Update progress** — tick the folder in `PROGRESS.md`.
6. **Synthesise (only after evidence)** — promote *confirmed universals* into the system: recalibrated tokens → pattern primitives → components.

## The 9-level lens

| # | Level | Captured as |
|---|---|---|
| 0 | **Frame** | dims, ratio, medium, coordinate basis |
| 1 | **Grid & spatial structure** | margins/columns/positions as **% of frame** |
| 2 | **Tonal zoning** | sampled near-white washes, hatch textures, blueprint ghost |
| 3 | **Type** | fonts, scale ratios, weights, roles, special treatments |
| 4 | **Colour & brand** | sampled palette + the gold→bronze→brown gradient range |
| 5 | **Atoms** | bullets, stat callouts, numbers, icons, hotspots, pills, photo blocks |
| 6 | **Layout patterns** | recurring page archetypes |
| 7 | **Sequence & rhythm** | flow + density rise/fall across the set |
| 8 | **Construction** | structural recipe per pattern |
| 9 | **Responsive rules** | how each pattern reflows native ratio → desktop/mobile/portrait/landscape |

## Folder order (proposed)

Start with the **cleanest canonical deck** to set the baseline vocabulary, then
test denser/other-ratio dialects against it, then the web + one-pager families.

1. `pitch-deck` *(or `deck1-2026` if that's the definitive one)* — baseline 16:9
2. `deck1-2026` — current canonical, confirm/extend
3. `company-info`, `presentation-15p` — mid-density variants
4. `capital-raise`, `recent-pitches` — high-density + 3:2 ratio dialects
5. `vt-*` family (architects / gatehouse / property / residential) — print one-pagers
6. `landing-mockups` — web surface (tall scroll), maps language onto a screen
7. `vi-onepager` — compact summary

## Key findings so far (from first 5 samples — provisional)

- Zoning is **near-imperceptible** warm-white tonal separation (≈2–6% tints), sometimes a **diagonal hatch texture** instead of flat tint. NOT semantic colour blocks. The current `--zone-*` system is too saturated / too hot-coded and will be **recalibrated**, not kept as-is.
- A faint **blueprint / architectural line ghost** recurs in backgrounds.
- Gold is the single accent: brand **V** mark (often substituted into headlines), **triangle/play bullets**, **hairline gold outline** callouts, the bottom **hatch rule**, and a **gold→bronze→brown tonal gradient** used for sequence/relationship.
- Premium warm photographic real-estate imagery; thin single-weight iconography.
- Decks carry interactive affordances already: **hotspot dots, MENU pill, account icon, info markers** — the intended path to components.
- Real surface ratios in play: 16:9 (1930×1085), 3:2 (1893×1287), A4 portrait (910×1287), tall web (1223×4630). Rules must be ratio-based to survive translation.
