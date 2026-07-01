---
name: conceptv-design
description: Use this skill to generate well-branded interfaces and assets for ConceptV, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files. The most important files to load before starting any work:

1. `README.md` — full brand foundation: voice, colours, typography, iconography, visual rules, and the **entity shape system** (circle/hexagon/octagon/diamond).
2. `colors_and_type.css` — source-of-truth design tokens. Import this in every HTML artifact you produce.
3. `assets/logos/` — real ConceptV wordmark and V mark PNGs (light, white, yellow).
4. `assets/icons/` — **the vectorized icon library**. 99 individual SVGs in `svg/`, a single JS module (`cv-icons.js`) with all paths, a React component (`CvIcon.jsx`), and an interactive explorer (`index.html`).
5. `assets/illustrations/` — architecture diagrams, process flows, the Vi AI framework illustration. Mine these for visual patterns (shape system, staged-flow connectors, percentage stat panels).
6. `ui_kits/platform/`, `ui_kits/virtual-hub/`, `ui_kits/vi/` — high-fidelity React component recreations of the three product surfaces. Lift JSX components from these for prototypes.
7. `preview/` — ~35 small design-system cards demonstrating each token, type, and component pattern individually. Useful for quick visual reference.
8. `DESIGN-LANGUAGE.md` — the cross-cutting v2 design rules (multi-surface, containment, motion, zoning-as-depth).
9. `analysis/AXES.md` + `analysis/UNIFICATION.md` — the generative model (axes + containment + the two solvers) and how the type system and engine are welded into one.
10. `core/` — the generative engine: `RenderType`/`Slide` + the block & graph solvers, read via `window.ConceptVDesignSystem_c8f43c`; `templates/` — copyable starting points (e.g. `pitch-deck`).

## The system is generative (v2 — read this)

ConceptV is **one type system + one rule engine + two layout solvers** (block = flow/stacking, graph = relational), computed by orthogonal **axis-dials** (surface · LOD · density · theme) over a fixed **invariant DNA core** — `design = f(content, axisPosition)`. Everything below this is the genuine brand DNA; v2 deepens it and, where they conflict, **v2 wins** (see the README v2 section + `analysis/`).

- **Don't hand-lay-out a layout.** A slide/page is content-as-data run through the engine: `const { Slide, RenderType } = window.ConceptVDesignSystem_c8f43c`. Pick an archetype (cover · split · statement · compare · triptych · metric-band · checklist · timeline · profile · terms · gallery · closing · stepper · diagram) and supply content; the same content recomputes across LOD/density/theme/surface.
- **One catalogue.** Archetypes live in `core/archetype-catalog.js`; every block/atom is a registered Type rendered by the engine (`RenderType`/`typeToNode`). New on-brand components are *generated*, not hand-written.

## Product surfaces

ConceptV consists of three connected platform entities plus an AI framework. **Each has a canonical shape — preserve it when referencing the entity in any visual.**

- **User Portal** → circle — login + role-aware home for stakeholders
- **Property Wizard** → hexagon — configuration engine
- **Virtual Hubs** → octagon — buyer-facing panotour output
- **Vi** → diamond with line-fill — the internal AI framework; wordmark is "V<sub>i</sub>" with the "i" set in gold

## How to design on-brand for ConceptV

- **Type** — Sora (display) + DM Sans (body) + JetBrains Mono (URLs/code). Screen titles are display 700 at ~36 px in **bronze (#988058)**, not gold.
- **Colour** — the brand accent is a **gold→bronze→tan RAMP** (`--ramp-1..4`: `#dad364 → #d6bf57 → #c09d5d → #b98664`), not a single gold. The TRUE logo gold is `#E0C010` (keep for the mark); the *applied* deck gold is the softer ramp. **Colour-role logic: ink = content · gold = active/decision/selected (never a default background) · bronze = the structural/quiet voice** (section headers, connective italic captions) — not only illustrations. Surfaces are a **near-white tonal ladder** where the wash marks **containment depth, not category** (zoning = depth; any semantic hue is an opt-in layer on top). Warm-only — no cool greys.
- **Texture & motion** — decks/marketing/presentation surfaces carry a **low-opacity texture layer** (diagonal gold hatch + faint blueprint ghost) and depth-keyed zone washes; the system has a full **motion language** ("nothing teleports") — calm, not static. Product-UI chrome stays flat and still.
- **Signature moves**: (1) **near-white depth-keyed zone panels** for grouping (the subtle ladder, not one saturated wash); (2) **dashed-gold outlines** for active selection / empty upload states; (3) **inline gold accent** for URL fragments inside helper text; (4) **colour emoji** as platform sidebar nav icons; (5) the **bronze line-icon library** for any diagram-level iconography; (6) the **entity shape system** when referencing the platform's parts; (7) the **ramp-tinted chevron stepper** for staged progressions.
- **Avoid**: pure-white page backgrounds, cool greys, hard cool shadows, emoji in body copy, ALL-CAPS, exclamation marks, bluish-purple gradients, drop shadows with sharp falloff, and — critically — replacing the bronze icon library with Lucide/Feather in diagram contexts.

## How to use this skill

- **Visual artifact request** (slide, mock, throwaway prototype): produce static HTML files that `@import` `colors_and_type.css`. Copy logo PNGs out of `assets/logos/`. Where the user references a real ConceptV screen, lift the matching component from `ui_kits/`. For diagrams, reference the icon sheet images directly or sketch new glyphs in the same bronze line style.
- **Production code request**: read this skill as reference and apply the rules above. The CSS tokens in `colors_and_type.css` are the canonical names.

If the user invokes this skill without other guidance, ask what they want to build, ask a few clarifying questions (audience, surface, fidelity, number of variations), then act as the expert designer.

## Using the icon library

99 icons live in `assets/icons/`. Three ways to use them:

```jsx
// 1. React (load assets/icons/cv-icons.js + CvIcon.jsx)
<CvIcon name="house" />                          // bronze stroke, 24 px
<CvIcon name="house" tone="gold" size={32} />    // gold stroke, larger
<CvIcon name="house" circle />                   // gold-circle entity badge
<CvIcon name="house" circle filled />            // filled gold, ink glyph
<CvIcon name="house" desaturated={0.5} />        // 50% strength (state gradient)
```

```html
<!-- 2. Static HTML — drop in a per-icon SVG -->
<img src="../../assets/icons/svg/house.svg" width="24" height="24" alt=""/>

<!-- 3. Vanilla JS — render programmatically -->
<script src="../../assets/icons/cv-icons.js"></script>
<script>document.body.appendChild(CV_ICONS.svg('house', { size: 32, color: 'var(--accent-gold)' }))</script>
```

**Which icon family for which context?**

- Sidebar nav on the platform → colour emoji (DO NOT swap for SVGs — it's a deliberate brand convention).
- Diagrams, architecture explainers, pitch decks → CvIcon in **bronze** for ambient illustration, **gold-circle** for entity badges.
- In-product UI chrome (filter/sort/search buttons) → CvIcon in **ink** or **gold** to match the button context.
- Status → coloured filled dots, not icons.

To add new icons: open `assets/icons/cv-icons.js`, append to `CV_ICONS.data`, then re-run the SVG-generation script (or simply use the JS data — the explorer + React component pick it up immediately).

## Open questions / flagged substitutions

- **Fonts** are substituted (Sora + DM Sans). The product's actual UI font is unknown — ask the user for `.woff2`/`.ttf` files if a tighter match is required.
- The **conceptv.com.au** website was offline at the time the system was built; tone and copy patterns were inferred from product UI strings and pitch-deck materials alone.
