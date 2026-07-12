# DIAGRAMS — type system for the diagram generator

> The decks lean heavily on diagrams (and on **icons inside them**). They are not drawings —
> each is an instance of a **diagram type** with a valid **content schema**, rendered in the
> diagram vocabulary (`tokens/diagram.css`) under the DNA rules. The generator selects a type
> (+ subtype), validates content against that type's schema, and lays it out deterministically.
> Goal (per REQUIREMENTS north-star): generate NEW diagrams that still obey the DNA.

## Hierarchical type system
`DiagramType → subtype → content-schema (valid node/edge/axis/center kinds) → layout rule`

### Shared content vocabulary (what any diagram is made of)
- **Node** `{ id, label, shape, icon?, tint, state }`
  - `shape`: circle · rounded-rect · **octagon (Vi-Hub)** · **hexagon (Property-Wizard)** · person-glyph · logo-card
  - `tint`: a position on the **gold→bronze→tan ramp** (often mapped to sequence/position) or zone wash
  - `state`: active · ghosted · rejected (dashed) · default
  - `icon`: a glyph from the **icon language** (see "Icons" below) — MANY nodes carry one
- **Edge** `{ from, to, kind, routing, label? }`
  - `kind`: flow ▶ · dependency · reference (dotted) · rejected · **bidirectional (↔)**
  - `routing`: organic · radial · elbow · dashed-orthogonal
- **Axis** (positioning/timeline only) `{ dimension, scale, endLabels }`
- **Center** (hub only) `{ shape, label }`

## The diagram types observed across the corpus (distinct, with subtypes)
1. **Network / mesh** — many nodes, organic edges, **opacity-depth** (fg solid → bg faint). *State = "chaos".* Sub: scatter, clustered-mesh, **disconnection** (stakeholders).
2. **Hub-and-spoke / radial** — N nodes around a central **octagon/hex hub**; clean radial edges. *State = "order".* Sub: ring-gradient nodes (ramp-coloured), bidirectional spokes, **orbital verb-ring** (the central node ringed by *verb* labels on concentric arcs — Upload·Configure·Update·Output — the process *around* the node, capital-raise p5).
3. **State-morph pair** ★ — **type 1 → type 2 of the SAME node-set**, shown as two frames + ▶. A deterministic transform ("re-route N×N edges through a hub"); **inherently animatable** (edges retract tangle→radial). The hero "chaos→order" rhyme.
4. **Flow / pipeline / stepper** — left→right sequence; arrow or chevron between steps; octagon/`+` join nodes. Sub: **chevron stepper** (Design▸Marketing▸Sales▸Construction, active filled, accent slides along ramp) · pipeline (Networks→…→Sales) · fan-out (hub → many user-glyphs) · **stacked/expandable node** (a pipeline node with category-member cards peeking above & below behind 〈/⌬ chevrons — the node is a *collapsed set*, capital-raise p4/p9) · **progressive-fidelity stepper** (a *vertical* pill stepper with interstitial mini-nodes — durations / "Revision" — and dashed elbow connectors to a paired media set that **escalates in render fidelity** stage by stage; ties to the LOD/loading/provenance axes — capital-raise p22).
5. **Timeline** — axis (Months) + outlined-rect nodes + dashed connectors; staggered placement.
6. **Quadrant / positioning map** — 2 axes (e.g. Value × Time) + plotted **logo-cards** + axis end-labels (High Revenue, Low Volume). Sub: **2-axis quadrant** (Accessibility×Versatility, brand top-right) · **value×time staircase** (cards plotted on banded Y × time X with **dashed-orthogonal staircase routing** + dual *directional* value axes — capital-raise p8) · **1-D spectrum axis** (a single gold→bronze *gradient directional* axis — Technical→Non-Technical — with plotted cards, segment labels, and a hatch zone marking a sub-range — capital-raise p13).
7. **Tree / hierarchy / org** — icon-flow row → plug → fan-out; or team/advisory org grid. Sub: **phased-expansion graph** (entry ★ nodes → adjacency arrows, bounded by **time-phase zones** — gold "3-18mo" | bronze "18-48mo" — capital-raise p9) · **manifold / converging-summation** (several branches → a **dashed horizontal manifold** → a single drop to one total chip — N inputs sum to one figure, capital-raise p12/p28).
8. **Compare / two-pane** — current vs solution panels + dashed connector + plug; italic synthesis below.
9. **Layered stack** — translucent panels receding in z ("user-relevant layers"); depth = message.
10. **Relationship / value-flow** — small node↔node with a `$`/role badge (Architects←Clients, B2B2B).

## Icons are a first-class content type
- Icons appear **inside nodes**, as **icon-flow rows** (icon-only nodes on a shared dashed baseline → converging to a plug/browser node — the "tools → platform" motif), and as **fan-out leaves** (user-glyph nodes).
- They obey the **icon language** (`tokens/icons.css`): single thin weight, 24-grid, rounded caps, two-tone gold accent, boxed-in-circle/square variants.
- → In the type system, `node.icon` and the **icon-flow** layout are valid content; the generator pulls from the icon set, never ad-hoc.

## Generator contract (spec → diagram)
```
{ type, subtype?, nodes[], edges[], axes?, center?, state? }
→ validate content kinds against the type's schema
→ layout rule for that type (radial / mesh / pipeline / quadrant / timeline / …)
→ render in diagram vocabulary + icon language, tinted via ramp/zone, under DNA rules
→ (optional) state-morph + entrance = animatable transforms
```
Same spec + different `state` = the morph (type 1↔2). Same spec + different `surface` = reflow
(per-container collapse). Same spec + different `tint` = variant theming.

## → Feeds
REQUIREMENTS D4 (upgraded), SYNTHESIS-PLAN §6/§3 (diagram generator = a container/component family
built on `tokens/diagram.css` + `tokens/icons.css` + the motion grammar).
