# The Parametric Model — how the system is meant to work

> Discovered by analysing the source decks (see `pitch-deck.md`, `deck1-2026.md`).
> This is the *shape* of the design system: not one master dial, but a small space
> of **orthogonal axes** from which the concrete design is **computed**, over a
> **fixed invariant core**. Read this before synthesising anything.

## The four kinds of thing

### 1. Input axes — the dials you set (orthogonal, compose freely)
| Axis | Range | Notes |
|---|---|---|
| **Surface** | desktop · tablet · mobile-portrait · mobile-landscape · print · slide | screen size + ratio |
| **Level-of-Detail (LOD)** | summary → pitch → full-read | *content* zoom — **independent of surface** |
| **Register / pace** | presenter-paced ↔ reader-paced | who controls the timeline |
| **Theme** | light · dim · dark · contrast | |
| **Density** | compact · comfortable · spacious | the `--density` knob |
| **Tint / gold intensity** | quiet ↔ present | the subtle-zoning knobs |

### 2. Derived outputs — computed from the dials (never set directly)
type sizes (fluid clamps ← surface) · margins & gutters (← surface × density) · reflow
(← surface) · surface tints (← intensity × ground × pigment) · bullet depth: claim-only
vs claim+support (← LOD) · visual mode: dense-static vs simple+motion (← space/time budget,
driven by register) · slide count (← LOD × narrative-priority × time budget).

### 3. Invariants — never computed, never move (the "sacred skeleton")
the **numbers** · the **diagrams** · brand DNA (gold ramp, zoning ladder) · the **frame
signature** · the colour-role logic. No dial touches these.

### 4. The function
`design = f(content, axisPosition)` over the invariant core. Setting a point in the
axis-space *computes* the concrete layout. This is what makes **one source → many
outputs** (a 17-page read, a 16-page pitch, a 1-page summary, a mobile scroll) possible.

## Two rules that keep it powerful (hard-won — see the "too hot-coded" lesson)
1. **Keep axes orthogonal — never collapse them.** LOD ≠ surface: a phone can show *high*
   detail (scroll); a desktop can show *low* detail (a hero summary). Fusing them kills the
   range (e.g. a *verbose mobile leave-behind* becomes impossible).
2. **Correlation ≠ coupling.** Presenter-paced *tends to* pair with terse + motion, but you
   must be able to break that on purpose. Defaults may link axes; the architecture must not.

## The containment hierarchy (the *structural* axis — distinct from the dials)
The dials above tune a design; **containment** is how content is *organised* — a recursive
ladder of nested boxes, each a container with its own spacing rhythm and role:

```
Deck                     the whole artifact — arc, sequence, frame signature
└─ Slide / Frame         one screen — title + content band, 12% margins, footer signature
   └─ Section            a labelled sub-region — bronze section-header + its content
      └─ Zone / Panel    a tinted surface — near-white wash (cream/neutral/embossed), radius, padding
         └─ Group / Cluster   a row/stack of siblings — pill-group, bullet list, stat row, card grid
            └─ Atom       leaf — bullet, number+label, chip, icon, badge, hero-number
```
Each level has consistent, inherited spacing: panel padding ~2.5–3%, inter-panel gutter ~2%,
marker→text ~3%, section rhythm via the modular scale. It's a recursive box model with a
**fixed rhythm at every nesting depth**.

### The unification: **zoning IS the containment hierarchy made visible**
The near-white tonal washes are not decoration and not (primarily) semantic categories — they are
the **container boundaries rendered as ~1–3% undertone shifts**, so you can *read the nesting*
without heavy borders. A Zone/Panel is a wash; a Section groups panels; the Slide is the ground.
This is exactly why the zoning is "universal and subtle" (the original brief): it marks
**containment depth**, not meaning. Any semantic colour mapping is an optional layer *on top* of
this structural ladder.

### How it meets the dials
- **LOD operates on this tree:** higher LOD = more **Sections** per slide + **Atom** depth (claim+support); lower LOD prunes both. (Confirmed: `recent-pitches` adds sections, not clutter.)
- **Templates are subtrees:** a slide archetype = a fixed Section/Zone/Group skeleton with content as data (proven by the duplicate "Our Entry Markets" slides).
- **Density** scales the spacing at every level uniformly (the `--density` knob); **surface** sets the outer frame; the tree is otherwise invariant.

## How the containment model extends along EVERY axis (cross-folder synthesis)
Re-examining all four analysed folders through the containment tree: each parametric axis
turns out to *operate on the tree*. The tree is the spine; the dials act on its nodes.

- **Surface (responsive) = per-container-level collapse.** Reflow isn't global — each container
  level knows how to collapse: Slide→stack, Section holds, Zone/Panel wraps, Group/Cluster wraps
  (`pill-group`, `grid-fit`). The whole "responsive fragility list" (pitch-deck §21) is just
  *container-local collapse rules*. Reflow = the tree re-laying-out at each node.
- **Motion ("nothing teleports") = temporal traversal of the tree.** Entrance order = reading
  order = depth-first traversal (slide → sections → atoms stagger). The **space↔time trade-off**
  (deck1-2026) is precise here: a container can **show all children in space** *or* **play them
  over time** — same subtree, two renderings. Motion enters/exits at container boundaries.
- **LOD = per-node prune/grow (and it can be local).** Higher LOD adds Sections + Atom depth
  (claim+support); lower prunes. Crucially LOD can be set **per container** → that's exactly
  **progressive disclosure** (expand one Section to raise its detail). `recent-pitches` proved
  growth happens at the Section level (more sections, not clutter).
- **Interactive (deck→app bridge) = runtime mutation of the tree.** Every affordance acts on a
  container: MENU pill expands a Panel, hotspot reveals an Atom's detail, "Hide Dashboard"
  collapses a Section. **The embedded product UI (nav → panel → table → row) is the same
  containment tree, just mutable.** Decks render it fixed; the app renders it interactive — *one
  model for both*.
- **Depth / z-stack = elevation encodes nesting + focus.** The z-order (ghost→ground→panel→card→
  glass→floating→modal) tracks containment depth; the focus/dim-the-rest system raises a container
  in z and recedes its siblings. Elevation and nesting are the same gradient.
- **Theme = zoning-as-depth is theme-invariant.** The "undertone shift per nesting level"
  mechanism survives a dark ground (deltas re-computed toward the dark `--zone-ground`); only the
  ground flips. Container-depth legibility holds in every theme.
- **Invariants are node-TYPES, not a separate concept.** The "sacred skeleton" (numbers, diagrams)
  = specific Atom/Group types that are **LOD-locked**; prose Atoms are LOD-variable. Invariance is
  a property of certain nodes in the tree.

## The capstone: everything catalogued is a *template at some tree level*, and they compose
Atoms, components, "layout patterns", and the 13 archetypes are **not separate kinds of thing** —
they are **typed containers at different depths of one tree, parameterised by the dials and made
visible by depth-keyed zoning**:
- Atom templates: number+label, triangle/→ bullet, chip, badge, hero-number chip.
- Group templates: pill-group, stat row, checklist, icon-flow row.
- Zone/Panel templates: stat-card, flow-panel, profile-block, QR card.
- Section templates: compare-pair, metric-band, dual-checklist.
- Slide templates: the 13 archetypes.
- Deck templates: the narrative arc.
Templates **nest and compose** along the hierarchy (a Slide template contains Zone templates
contains Group templates). → **Build the system as a library of typed, composable containers**,
each with a role + spacing rhythm + collapse rule + zone-wash keyed to depth; the axis-dials then
compute any concrete output. This is the whole model in one sentence.

## BLOCK & GRAPH are one generative system (two layout solvers)
The **block side** (containment tree: Band→Section→Zone→Cluster→Atom) and the **graph side**
(diagrams: nodes + edges) are **the same generative substrate** — *typed things + rules that
compute layout* — differing only in their **layout solver**:
- **Block solver = flow/stacking** (containers nest; spacing rhythm; per-container collapse). Position is *implied* by nesting + order.
- **Graph solver = relational placement** (radial / mesh / pipeline / quadrant / timeline). Position is *computed from relationships* (edges, axes, hub).
Everything else is shared: typed nodes, the ramp/zoning tints, the icon language, the DNA rules,
the axis-dials (surface/LOD/density/theme), motion as temporal traversal, state-morph & reflow as
transforms. A node can even host either solver (a Zone contains a diagram; a diagram node contains
a block). → **One type system, one rule engine, two solvers.** Build them on the same core; pick the
solver by content kind (`block` vs `graph`). This is the whole system in one line.

## Key coupled relationships (correlated, but keep separable)
- **Register → {LOD, density, space/time visual mode}** — pace-controller usually sets these together (presenter ⇒ terse + motion; reader ⇒ verbose + dense-static).
- **Space ↔ time** — a slide's complexity budget is spent in *space* (dense static) or *time* (animation); the two visual modes are register-variants of one component.
- **Surface → {type, margins, reflow}** — geometric, deterministic.

## Open questions each new folder tests
- Is **density** truly an independent dial, or secretly coupled to **ratio/surface**? *(→ `recent-pitches`, dense 3:2)* — **RESOLVED: independent.** At 3:2 + high density the margins (12%), zoning, gold, type scale are all unchanged. Ratio is just a surface value; density/LOD composes freely with it.
- Does the **LOD ladder** hold at its tight end? *(→ `vt-*` one-pagers, `vi-onepager`)* — **RESOLVED: yes.** `vi-onepager` = summary rung (compare archetype condensed to 1 page). LOD ladder complete: 4 rungs.
- Does the language survive a **scrolling web surface**? *(→ `landing-mockups`)* — **RESOLVED: yes, intact.** Slide→section band, sequence→scroll, zoning→band backgrounds; zero new grammar, only web-chrome atoms. Surface axis spans **paged↔scrolling**; the "Slide" node generalises to a paged-or-stacked **band**.
- Which **archetypes** are universal vs per-deck?
