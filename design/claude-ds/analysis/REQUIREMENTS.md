# REQUIREMENTS — what the ConceptV design system must achieve & support

> Living spec. Derived from analysis (`pitch-deck`, `deck1-2026`, `recent-pitches`,
> `landing-mockups` + early `vt-*`/`vi` samples). Each new folder APPENDS or upgrades
> requirements here. Pairs with: SYNTHESIS-PLAN.md (how/where to build), AXES.md (the
> model), SYSTEM-GAPS.md (raw findings). Status: 🟢 confirmed ≥3 folders · 🟡 confirmed

## ★ NORTH STAR — rules that compute, not dedicated writes
The system exists to be **computed**, not hand-authored per case. Every requirement must be
expressed as a **rule / ratio / token / parameter** so that:
1. **One source applies across every surface & screen size** (slide ↔ web ↔ print; desktop ↔ mobile;
   any ratio) *without* per-surface writes — design is `f(content, axis-position)`.
2. **Brand-new, never-seen components can be GENERATED and still obey the DNA** — the DNA lives in
   the rules (containment, zoning-as-depth, ramp, colour-role logic, spacing rhythm, collapse rules,
   motion grammar), not in specific layouts. A generator composing typed containers under these
   rules makes on-brand output it has never seen.
- *Example — the **stepper** (`vt-*`):* steps through states, active accent **slides along the ramp**,
  animates between steps, collapses per surface. A generator can instantiate it for *any* sequence and
  it stays on-DNA.
- **Implication:** parameters over variants, ratios over pixels, container-rules over layouts. If a
  finding can only be honoured by a one-off write, it isn't finished — push it back to a rule.
> 2 · 🔵 provisional / needs more evidence.

## A. Foundational fidelity (visual truth)
- A1 🟢 Surfaces are a **near-white tonal ladder** (~1–3% undertone deltas): ground · warm-ivory · warm-cream · neutral-grey · embossed · hatch-ivory. Differentiation is *felt, not seen*.
- A2 🟢 Zoning marks **containment depth**, NOT semantic category. Hue-coded meaning is an opt-in app layer only.
- A3 🟢 Brand colour is a **gold→bronze→tan RAMP** (`#dad364→#d6bf57→#c09d5d→#b98664`), not one gold. Gold softened from the legacy `#E0C010`.
- A4 🟢 **Colour-role logic:** ink = content · gold = active/decision (never body) · bronze = structural/quiet. Contrast is a hierarchy tool (quiet tissue = low-contrast).
- A5 🟢 Textures: diagonal **gold hatch** (bands + bottom rule) · faint **blueprint ghost** (top-weighted) · paper-grain/white. All low-opacity.
- A6 🟢 Depth is **warm, soft, layered** (no hard/dark shadows): z-stack ghost→ground→panel→card→glass→floating→modal. Includes frosted-glass & embossed chips.
- A7 🟢 **Restraint guardrails** (must REFUSE): pure black · gradients outside photography · saturated fills outside charts · heavy rules (hairline only) · left-accent-border cards · all-caps body · emoji · ornamental icons.

## B. Structure & composition
- B1 🟢 **Containment hierarchy:** Deck → Slide/Band → Section → Zone/Panel → Group/Cluster → Atom. Each a typed container with role + spacing rhythm + collapse rule + depth-keyed wash.
- B2 🟢 **Grid (ratio-invariant):** ~12% side margins · title top ~7.5% · ~76% content band · split ~46/54 · bottom **frame signature** (hatch rule + V mark + corner anchors).
- B3 🟢 **Modular type scale** ~1.25/step + ~1.9 display jump; fluid clamps; balanced 2-line titles; hanging-indent bullets.
- B4 🟢 **Number+label convention** (gold tabular number / small grey label; k/M/B/T,+,/unit,x,%; never split on wrap). Numbers are LOD-locked.
- B5 🟢 Everything **rounded**; negative space **non-negotiable** even at peak density.

## C. The parametric axes (must be independent, composable dials)
- C1 🟢 **Surface** spans paged (slide) ↔ scrolling (web) ↔ print; ratio is a free parameter (16:9, 3:2, A4, web all confirmed). Slide = paged-or-stacked **Band**.
- C2 🟢 **Level-of-Detail (LOD)** is its own axis, orthogonal to surface: summary→pitch→full. Operates per-node (prune/grow); enables progressive disclosure. **4 rungs confirmed** (summary `vi-onepager` → terse `deck1-2026` → standard `pitch-deck` → high-detail `recent-pitches`).
- C3 🟡 **Register/pace** (presenter↔reader) drives {LOD, density, space↔time visual mode} together — but must stay separable.
- C4 🟢 **Density** scales spacing uniformly across all container levels (`--density`).
- C5 🟢 **Theme** (light/dim/dark/contrast) — zoning-as-depth survives; only the ground flips.
- C6 🟢 **The system computes output = f(content, axis-position) over an invariant core.** One source → many outputs (read / pitch / summary / web / mobile).

## D. Reuse & generation
- D1 🟢 Slides/sections/zones/atoms are **templates at every tree depth**, and they **compose**.
- D2 🟢 Templates have **typed slots**; content is data. **Audience/client-variant** is a parameter — confirmed across decks (variant slides), web (variant pages + live toggle), AND print (`vt-gatehouse`/`vt-residential` = same template, different client). Variant can also re-tint along the **ramp** (chevron stepper).
- D3 🟢 **Invariant skeleton** (numbers + diagrams) never prunes; prose is LOD-variable. Invariance is a node-TYPE property.
- D4 🟡 **Diagram generator:** diagrams are typed instances, not drawings — a **hierarchical type system** (DiagramType → subtype → content-schema → layout rule) over a shared node/edge/axis/center vocabulary. **10 distinct types** catalogued (network, hub-radial, state-morph, flow/stepper, timeline, quadrant, tree/org, compare, layered-stack, relationship). **Icons are a first-class content type** inside nodes + icon-flow rows. The chaos→order **state-morph is a deterministic, animatable transform**. Generate from `{type, nodes, edges, axes?, center?, state?}`, validated against the type's schema, rendered under DNA rules. → see `DIAGRAMS.md`.

## E. Motion (must support, "nothing teleports")
- E1 🟢 Entrance/exit/move = **temporal traversal of the containment tree**; entrance order = reading order = stagger.
- E2 🟡 **Space↔time trade-off:** a container shows children in space OR plays them over time — one component, a `mode`. Motion/GIF slot is first-class.
- E3 🔵 **Motion-placement rule:** animate only hero concept diagram + immersive product/spatial views; analytical stays still.

## F. Interactivity & the deck→app bridge
- F1 🟡 Interactive = **runtime mutation of the containment tree** (expand/collapse/reveal/raise-LOD). Affordances act on containers (MENU→panel, hotspot→atom, Hide Dashboard→section).
- F2 🔵 The embedded **product UI** (nav→tab bar→table→row→status pills→comment panel→hotspots) is the SAME tree, mutable → app components built on the same container library.
- F3 🟢 Affordance/interaction-state language: hover/press/focus-visible (gold ring)/selected/disabled; status traffic-light (green/amber/red); state-coloured hotspots.

## G. Output surfaces the system must produce
- G1 🟢 Presentation decks (16:9, 3:2) — paged, static or motion-ready.
- G2 🟢 Web landing pages — scrolling bands, persistent nav, CTA bands, comparison tables.
- G3 🟢 Print one-pagers (A4) — **confirmed** (`vt-*`): containment tree, zoning, ramp, frame signature all hold at A4 portrait. Surface axis now complete: slide(16:9,3:2) ↔ web(scroll) ↔ print(A4).
- G4 🟢 Export-native (print/PDF/slide page sizes are surfaces; `@media print`).
- G5 🟡 Interactive prototypes / live components (the motion + interactivity axes).

---

## Append log (each folder adds requirements here)
- *(pitch-deck/deck1-2026/recent-pitches/landing-mockups)* — A1–A7, B1–B5, C1–C6, D1–D3, E1–E2, F1/F3, G1/G2/G4 established.
- *(next)* `vt-*` + `vi-onepager` → expected to confirm G3 (A4 print one-pager), C2 tight-LOD end, and any one-pager-specific requirements.
- *(vt-* + vi-onepager done)* → G3 🟢 (A4 print confirmed), C2 🟢 (4 LOD rungs), D2 reinforced (client-variant across all surfaces). New atoms: **stage/progress chevron stepper** (recolors along ramp per variant), **annotation callout/pointer**, **two-pane one-pager** archetype; **comparison table** = confirmed cross-surface component. Surface axis COMPLETE (slide↔web↔print).
