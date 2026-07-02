# AREA-12 — Tokens · Axes · Core-engine depths (the generative substrate the live layer must resolve through)

> Wave-2 coverage agent. Territory: `tokens/*.css`, `axes/`, `core/`, `colors_and_type.css`,
> `tonal-zoning.css`. Wave-1 read cv-glyphics / cv-meaning / cv-shapes but missed the **token graph**,
> the **CV_AXES generative model**, and the **core render spine** (RenderType / ContainmentTree /
> DiagramSolver / archetype-catalog). This file maps those, with evidence, and answers the governing
> question: **how does the live layer stay token+axis-resolved with no hardcode?**
>
> Marking: **Observed (file:line)** = read directly · **Inferred** = pattern-judgment · **My-idea** =
> proposal for the build. Two-repo scope, but everything here is in `claude-ds/`.

---

## TL;DR (3 lines, the headline correction to LIVE-INSTRUMENT.md)

1. **The glyphgraph render is NOT new — it already exists, token+meaning+axis-resolved.** `DiagramSolver`
   has a first-class `type:"glyphgraph"` (`glyphGraphView`) that lays out a meaning-graph closed-form
   (DAG-layering, ring fallback), renders each node via `CV_GLYPHIC.render` and each edge via
   `CV_SHAPES.edgeSVG` with per-edge colour resolved through `CV_MEANING.field('lineColor').token →
   COLOR_TOKENS → var(--token)`. The synthesis's "build fresh + cola/dagre/elk" overstates the gap.
2. **Only the canvas SHELL is genuinely new** (pan/zoom, incremental/stable placement as nodes stream
   in during a live conversation). The **render path** (node glyph + edge meaning, all token-resolved)
   is reusable as-is — it is `render-from-data` with one generic node + one generic edge **already**.
3. **The sharpest no-staleness risk is a third colour map.** "Gold → `--accent-gold`" is encoded in THREE
   homes (color-axis, `CV_GLYPHIC.COLOR_TOKENS`, CV_MEANING seeds); the glyph renderer resolves through
   COLOR_TOKENS and **bypasses `CV_AXES`**. The live RESOLVE stage must go through `CV_AXES.resolveCSS` +
   `CV_AXES.validate`/`candidates` (the loud-fail gate on LLM-proposed facet values), or it adds a fourth.

---

## A · THE AXIS SYSTEM (CV_AXES) — the generative model the live render must resolve through

### A.1 What an axis IS (Observed)
- **`axes/axis-core.js:43-131`** — `makeAxis(spec)` builds one Axis with the shared registry verbs:
  `register / resolve / tryResolve / has / values / ids / groups / valuesIn / default / setDefault /
  zero / query / candidates / subscribe`. This is the SAME `register/resolve/lineage/query/subscribe`
  shape as `CV_REGISTRY` / `CV_AI` / `CV_MEANING` — by deliberate mirroring (axis-core.js:18-22).
- **`axis-core.js:101-107`** — `resolveCSS(id, ctx)` is the universal value→CSS resolver:
  - `v.resolve` (a fn) → computed payload (ctx passed in), ELSE
  - `v.token` → `'var(--' + token + ')'` (the canonical path — the token is the single source of the literal), ELSE
  - `v.css` → a literal string (only for things with NO token home, e.g. a keyframe class name), ELSE
  - `null` (a pure-semantic value like `none`).
- **`axis-core.js:134-161`** — `window.CV_AXES` is itself a registry-of-axes:
  `register / resolve / has / list / all`, plus the universal entry points:
  - **`CV_AXES.css(axisId, valueId, ctx)`** (axis-core.js:149) — resolve any `{axis,value}` → CSS from anywhere.
  - **`CV_AXES.candidates(sub)`** (axis-core.js:152) — what an editor/foundry shows for a slot.
  - **`CV_AXES.validate(sub, valueId)`** (axis-core.js:155-160) — loud-LIST (never coerce); returns
    `[]` if valid, else an array of human-readable reasons.
- **Subscription model** (axis-core.js:24-27, 111-117): a component slot declares
  `{ axis, groups?, values?, default, conditions? }`; `candidates(sub)` is exactly the allowed-value set.
  **This is the foundry/editor's pick-list with no bespoke per-slot code.** (Inferred from the comment + `candidates` body.)

### A.2 The canonical claim: **tokens ARE the value-units of an axis** (Observed)
`axis-core.js:11-17` states it explicitly: an axis does NOT wrap over the tokens — "the colour axis IS
the colour tokens, typed and organised; the size axis IS the `--size-*` tokens." A value carries `token`
as canonical identity; `resolveCSS()` returns `var(--token)`. **So axis-resolution and token-resolution
are the same act** — resolving a facet value through `CV_AXES` lands on a `var(--token)` whose literal
lives once in `colors_and_type.css`/`tokens/*.css`. This is the spine the governing law wants the live
layer to ride.

### A.3 The ten axes, by payload kind (Observed)
| Axis | File | Payload kind | Notes for the live layer |
|---|---|---|---|
| **color** | `axes/color/color-axis.js` | `token` (e.g. `gold→accent-gold`, :33) | groups brand/semantic/ink/communication/neutral; aliases amber→warning, clay→error, blue→info (:61-63) |
| **size** | `axes/size/size-axis.js` | `token` `--size-*` + `meta.px` for SVG/JS (:29-30) | the computational consumer (glyph width) reads `meta.px` |
| **space** | `axes/space/space-axis.js` | `token` `--s-*` (8px scale) | gaps/padding/margins single-source |
| **depth** | `axes/depth/depth-axis.js` | `token` `--elev-*` + `meta{dy,blur,opacity}` (:25-30) | the polygon-accurate shadow geometry lives in CV_GLYPHIC; the SCALE single-sources here |
| **motion** | `axes/motion/motion-axis.js` | `css` (a class name in `axes/motion/motion.css`, e.g. `mo-breathe`, :34) | **token-free by design** — the animation lives in CSS, the axis names the class |
| **fill** | `axes/fill/fill-axis.js` | `meta.ramp` recipe (none/paper/wash/tint) | the actual ramps live in `CV_GLYPHIC.FILL_RAMPS`; axis = vocabulary only (:7-10) |
| **form** | `axes/form/form-axis.js` | `resolve→null` + `meta{sides,shape}` | references `CV_SHAPES.geom` by id; n-gon progression 0→3..8→∞ (:19-24); render via `CV_SHAPES.markSVG` |
| **texture** | `axes/texture/texture-axis.js` | enum ids (none/hatch/lines/…/dots) | realised by `CV_SHAPES.markSVG` / `tokens/texture.css` |
| **symbol** | `axes/symbol/symbol-axis.js` | `resolve→I.get(id)` (live svg body) | **the live-rebuild axis — see A.4** |
| **depth/etc** | — | — | — |

> **Observed gap (worth the synthesis noting):** the anchor names a **Meaning** axis among the primaries
> (axis-core.js:5), but there is NO `axes/meaning/` module — meaning is governed by `CV_MEANING`
> (loadable profiles), and the symbol axis is explicitly the ONE axis NOT under contextual meaning
> (symbol-axis.js:6-9, `meta.intrinsicMeaning:true`). So "axes" and "meaning profiles" are two registries,
> not one axis list. (Inferred: the anchor's "Meaning, …" in the axis enumeration is aspirational.)

### A.4 The no-staleness pattern ALREADY in the axes — the live layer copies this (Observed)
**`axes/symbol/symbol-axis.js:31-43`** — `rebuild()` walks `CV_ICONS.data` live, registering every icon
(including AI-foundry-added ones) as a symbol value whose payload is `I.get(id)` resolved live; it's
exposed as `symbol.rebuild` so **the foundry calls it after `CV_ICONS.add`**. This is the EXACT
generate-on-miss discipline the live layer needs: a new icon drawn mid-conversation lights up the symbol
axis with no hardcoded symbol list, no copy. **My-idea:** the live RESOLVE→GENERATE-ON-MISS stage should
call `symbol.rebuild()` after a `glyphic.save`, so the just-drawn icon is immediately a valid axis value
the composer can resolve. (This is the precedent the synthesis's "re-runnable icon index" should mirror —
it's a *rebuild verb on the registry*, not a copied table.)

---

## B · THE TOKEN GRAPH (L0 → L1 → L2) — what the live data-binding must resolve through (NOT short-circuit to hex)

### B.1 The three layers, with anchors (Observed)
- **L0 primitives** (raw hex/oklch literals — the ONE home for the literal):
  - `colors_and_type.css:45 --accent-gold:#E0C010` · `:66 --accent-bronze:#988058` ·
    `:31 --ink:#1F1A12` · `:16 --paper:#FCFAF2` · `:23 --bg-surface:#FFFFFF` ·
    `:91 --accent-communication:#7CA85B` · `:95 --status-success:#5A8A4A` · `:99 --status-error:#C24A3C`.
  - the diagram **ramp** the solver indexes: `:76-79 --ramp-1..4` (`#DAD364 #D6BF57 #C09D5D #B98664`).
- **L1 roles** (`var()` an L0 primitive, often via `color-mix` toward the ground):
  - `colors_and_type.css:426-429` — `--vi-surface / --vi-strong / --vi-edge` = `color-mix(... var(--accent-gold) ... var(--zone-ground))`; `--vi-line: var(--accent-gold)`.
  - `:38-40` — `--fg-primary/secondary/muted` (text roles).
  - the **zone family** (`tonal-zoning.css` + colors_and_type.css:370-401) — `--zone-{base,content,panel,review,source,package}-{surface,strong,edge,ink}` all = `color-mix(in oklch, var(--pig-*) calc(N% * var(--zone-intensity)), var(--zone-ground))`. These are the pigments the diagram node fills bottom out in.
- **L2 component tokens** (`var()` an L1 role — the consumer never sees a hex):
  - `tokens/controls.css:47 .cv-btn--primary{background:var(--accent-gold);color:var(--on-gold)}` ·
    `:56 .cv-btn--outline{...border-color:var(--accent-gold)}` · `:64 .cv-btn--soft{background:var(--vi-surface)}`.

### B.2 Proof the propagation is real (Observed)
**`colors_and_type.css:450 & :455`** redefine `--pig-base/--pig-content/--pig-panel` per THEME (the dim
`#8FA0A6…` and dark `#C0964A…` palettes). Because every zone role is `color-mix(var(--pig-*) … var(--zone-ground))`
and every component reads the role, **a theme swap reflows the whole graph from one place** — the L0→L1→L2
chain is not decorative, it's load-bearing. (This is the `data-theme` knob the CLAUDE.md describes, verified.)

### B.3 The data-binding precedent — `CV_MEANING.encodings` (Observed) — AND its hex violation
- **`assets/icons/cv-meaning.js:210-216`** — `CV_MEANING.encodings` is a `register/resolve/has/list`
  registry of **surface-keyed encoding profiles**: each binds one data FACET → one visual CHANNEL
  (colour/size/texture/border/glow/opacity), discrete (value→appearance) or scale (interpolated).
  **This IS the data→visual grammar the live data-binding should extend** (the anchor calls it the precedent).
- **VIOLATION (Observed, the central finding for sub-question b):** the `system-map` profile's
  `role-colour` and `type-colour` sets bind facet→colour as **bare hex literals**:
  `cv-meaning.js:232` (`axis:'#E0C010', meaning:'#7CA85B', registry:'#6BA0E0', …`) and `:235`
  (`js:'#E0C010', css:'#E0A23C', …`). These hex are **copies of L0 primitives** living in a second home —
  exactly the "data-binding short-circuits to hex" the governing law warns against. `#E0C010` is
  literally `--accent-gold` (colors_and_type.css:45) re-typed; `#7CA85B` is `--accent-communication` (:91).
  - **My-idea (the fix the live layer must adopt, not inherit):** an encoding set's `values:` should bind
    facet → **a token name or an axis value id** (e.g. `axis:'gold'`), resolved at paint time through
    `CV_AXES.css('color','gold')` → `var(--accent-gold)`. The `lineColor` seeds already do this correctly
    (`cv-meaning.js:389 {token:'clay'}`, :391 `{token:'gold'}`) — so the right shape exists in the same
    file; `system-map` is the drifted one. The live binding grammar should be token-keyed from day one.
- **Caution (Inferred, NOT a violation):** the `var(--accent-communication, #5A8A4A)` style fallbacks in
  `CV_GLYPHIC.COLOR_TOKENS` (cv-glyphics.js:78-80) are CSS `var()` **fallbacks** (a defensible degrade if
  the token is unloaded), not a second home for the value. Don't conflate these with the `system-map` hex.

---

## C · THE CORE ENGINE — how a Type renders; the render-from-data spine the live canvas must honor

### C.1 The shared node type (Observed)
- **`core/cv-nodes.d.ts`** — ONE type system both solvers consume. A `CVNode` (block side, :21-67) is a
  tree of `kind ∈ band|section|zone|cluster|atom|diagram`; a node of `kind:"diagram"` hands its `graph`
  (a `CVGraph` = `{type, nodes[], edges?}`, :95-107) to the GRAPH solver. **A glyphgraph is a `CVGraph`
  with `type:"glyphgraph"`** — same substrate, different layout strategy.
- The axis dials are DATA on the node/walk, not branches: `CVAxis = {lod, surface, density}` (:10-17).

### C.2 RenderType — the bridge (Observed)
- **`core/RenderType.jsx:104-133 typeToNode`** — resolves a `CV_REGISTRY` Type + instance data → solver
  IR. Dispatch is by `type.layer`/`family` (surface·deck-slide → archetype builder; doc → a sequence;
  graph-bearing → straight to the graph solver, :124; widget → a Zone tile). **A `content.graph` Type
  goes straight to `{kind:"diagram", graph}`** — i.e. a glyphgraph Type already routes to DiagramSolver
  with no new code (:124). This is the live render's entry point.
- **`RenderType.jsx:160-181`** — the React entry; LOUD-fails if `window.__cvContainmentTree` absent
  (:170), composes the axis `{lod, surface, density}` (:176), renders through ContainmentTree.
- **`RenderType.jsx:199-208 CoreTypes`** — the archetypes are read from the SINGLE-SOURCE catalogue
  (`window.CV_ARCHETYPE_CATALOG`, archetype-catalog.js); LOUD-fails if not loaded (:193-196). No parallel stub list.

### C.3 ContainmentTree — atoms are a REGISTRY, not branches (Observed) — the key render-from-data proof
- **`core/ContainmentTree.jsx:111-318 ATOM_RENDERERS`** — atom leaves keyed by `role`
  (metric · hero-number · chart · bullet · chip · badge · note · qr · logo · ramp-card · image · icon · text · headline).
  **`ContainmentTree.registerAtom(role, fn)` (:443)** adds a new atom as DATA — no solver edit. This is
  the existing "render-from-data, one generic dispatch" pattern the synthesis says to BUILD; it's BUILT.
- **Every atom is token-pure** — e.g. `metric` (:113-128) emits `var(--accent-gold)`, `var(--fs-h2)`,
  `var(--font-display)`; the `chart` atom (:134-156) draws sparkline/bar/gauge from `tokens/dataviz.css`
  classes (`.viz-spark/.viz-bar/.viz-gauge`, dataviz.css:42-64) where gold = the key series. No literals.
- **The axis dials thread through as data**: `visibleAtLOD` (:26-31) prunes by `priority`/`detail`;
  `data-density`/`data-motion`/`data-loading` are set on the walk root (:436); `loading` swaps leaves to
  `skeletonFor` (:348-359, shape-matched so layout doesn't jump). **This `loading` skeleton path is the
  staged-reveal the live layer wants** — a node can render as a skeleton while extraction resolves its facets. (My-idea: reuse it.)

### C.4 DiagramSolver — **the glyphgraph already exists** (Observed) — the contradiction of layer-1
- **`core/DiagramSolver.jsx:279-351 glyphGraphView`** — a first-class `type:"glyphgraph"` view (dispatched
  at :368). What it ALREADY does:
  - **Closed-form incremental-friendly layout** (`layout()` :63-101): (1) honour AUTHORED `x/y` in 0..1
    (like quadrant — "the author placed it"); else (2) DAG-LAYERING by longest-path-from-a-source into
    rows spread across width; else (3) ring fallback for a flat/cyclic graph. **No external layout lib**,
    explicitly "(CSP/bundle)" (:67) — closed-form like the siblings.
  - **Node = a FULL glyphic**: `GL.render(nd, {size})` (:341) — facets read at node top-level, sized down
    for busy graphs (:287). LOUD-throws if `CV_GLYPHIC`/`CV_SHAPES` absent (:283).
  - **Edge = meaning, rendered visually**: `SH.edgeSVG({line, direction, ink, routing}, …)` (:321) with
    per-edge colour resolved through `CV_MEANING.field('lineColor', v).token → tokenForName → COLOR_TOKENS
    → var(--token)` (:301-306, 357-363). Edge labels OFF by default — the read sits in a `<title>` from
    `CV_MEANING.readGraph` (:312-314) ("otherwise it's not the language", :277).
  - The node position transition (`DiagramSolver.jsx:448`, the non-glyph SVG path) already animates
    `left/top` with `var(--dur-move) var(--ease-emphasized)` — **"nothing teleports" is already wired for
    moving nodes.** (Observed on the generic graph path; glyphGraphView reuses `layout()` positions.)
- **Contradiction of LIVE-INSTRUMENT.md (the both/and):** the synthesis frames the canvas as "build fresh
  `surface/app` + render-from-data node + cola/dagre/elk seed-then-relax." But the **render path** — node
  glyph + meaning-edge, fully token+meaning-resolved, one generic node + one generic edge, loud-fail —
  **already exists** in `glyphGraphView`. What is genuinely missing is only the **interactive canvas
  SHELL**: pan/zoom, and *stable incremental placement as nodes stream in live* (the current `layout()`
  re-solves the whole graph each render — fine for a static spec, jumpy if nodes arrive one-by-one mid-
  conversation). So:
  - **Reuse as-is:** the per-node glyph render, the per-edge meaning render, the colour/state resolution, the loud-fail contract, the closed-form layout for the *first* paint.
  - **Build new (the real frontier):** an incremental-stable layout (seed new nodes near their relations,
    relax without re-flinging settled ones) + the pan/zoom/select shell. This is a *thinner* build than the synthesis implies, and it must emit the SAME `CVGraph {type:"glyphgraph", nodes, edges}` so it stays render-from-data. (My-idea, grounded in DiagramSolver.jsx:63-101.)

### C.5 archetype-catalog — the single-source pattern (Observed, secondary)
`core/archetype-catalog.js:15-100` — the deck-slide archetype catalogue (META + SAMPLES → registry-shaped
seeds, :79-93). Schema here, RENDERER keyed by the same `key` in `core/Slide.jsx`. "Add an archetype = one
entry here + one builder there" (:11-13). Not directly on the live path, but it's the canonical "schema in
one place, renderer keyed by id" discipline the live composer's NL→glyphgraph mapping should follow (a
glyphgraph node-spec is the analogue of an archetype sample). (Inferred relevance.)

---

## D · ANSWER — how the live layer stays token+axis-resolved (no hardcode)

**The system gives the live layer a ready-made resolution spine; the discipline is to route THROUGH it, not around it.**

1. **RESOLVE every facet value through `CV_AXES`, never through a local map.** (My-idea, grounded.)
   - colour → `CV_AXES.css('color', valueId)` → `var(--token)` (axis-core.js:149 + color-axis.js:33).
   - size → `CV_AXES.resolve('size').resolve(id).meta.px` for the SVG width; `resolveCSS` for CSS.
   - motion → `CV_AXES.css('motion', id)` → the `mo-*` class (motion-axis.js:34).
   - form/symbol/texture/fill/depth → as the axes define (Section A.3).
   - **The current gap to close:** `CV_GLYPHIC.render` resolves colour through its own `COLOR_TOKENS`
     table (cv-glyphics.js:76-82, 210-213) and `CV_MEANING` seeds carry their own `{token:'gold'}` —
     so "gold → `--accent-gold`" lives in THREE homes (color-axis.js:33, COLOR_TOKENS:77, cv-meaning seed:334).
     The glyph renderer **bypasses `CV_AXES`**. (Observed.) **My-idea:** the live RESOLVE stage routes the
     LLM's proposed colour-VALUE through `CV_AXES.resolve('color')` and feeds the resolved `token` into the
     glyph spec — and the COLOR_TOKENS table should become a thin read of the color axis (one home), or the
     live layer will be the FOURTH place "gold" is defined.

2. **VALIDATE every LLM-proposed facet value with `CV_AXES.validate` / `candidates` — the loud-fail gate.**
   (My-idea, grounded in axis-core.js:152-160.) The extract→resolve stage proposes facet values from
   speech; a value not in the axis (or not permitted by a slot's subscription) must `throw`/surface a
   Notice, never coerce. `CV_AXES.candidates(sub)` IS the constrained vocabulary to give the small models'
   structured-output schema (a closed enum per facet), which also keeps extraction cheap and on-language.

3. **GENERATE-ON-MISS stays axis-resolvable via the rebuild verb.** (Observed pattern, symbol-axis.js:42.)
   A drawn-live icon → `CV_ICONS.add` → `symbol.rebuild()` → it's immediately a valid `symbol` axis value.
   No hardcoded symbol list, no copy. The live foundry must call `rebuild()` (and any embed-index re-run)
   so the new symbol is resolvable the same turn.

4. **The data-binding grammar is token-keyed, not hex-keyed.** (Observed precedent + the fix.)
   Extend `CV_MEANING.encodings` (register/resolve, cv-meaning.js:210-216) for the live project surface,
   but bind facet → **token name / axis value id** (the `lineColor`-seed shape, :389), NOT bare hex (the
   `system-map` mistake, :232). Resolve to CSS at paint through `CV_AXES.css`. The live binding should fix
   this class, not copy it.

5. **The render is render-from-data already — keep it that way.** (Observed.) Emit a `CVGraph
   {type:"glyphgraph", nodes, edges}` and let `DiagramSolver.glyphGraphView` paint it; add an atom via
   `ContainmentTree.registerAtom` (:443), an archetype via the catalogue — never a per-type code branch.
   The one generic glyph-node + one generic meaning-edge the synthesis wants to BUILD is what's THERE.

---

## E · Honest corrections to LIVE-INSTRUMENT.md (the wave's own synthesis)

- **"The canvas… build fresh `surface/app`, render-from-data node, server-composes the glyph SVG" (line
  44, 60, 88-89)** — *partially overstated.* The render-from-data node + per-edge meaning is ALREADY
  client-side in `glyphGraphView` (DiagramSolver.jsx:279-351), token+meaning-resolved, loud-fail. Whether
  to move composition server-side is a *backend-owns-truth* choice, but it should not be sold as "the
  node render doesn't exist yet" — it does, and it's the reference for any server port. (Observed.)
- **"cola.js / dagre / elk seed-then-relax" (line 40-41)** — the FIRST-PAINT layout is already closed-form
  (DAG-layering, DiagramSolver.jsx:63-101) with the explicit no-external-lib note for CSP/bundle. An
  external lib is only justified for the *incremental-stable* case (nodes streaming in live); for that, a
  seed-near-relations + bounded relax could even be added to the existing `layout()` without a lib. The
  "deps install fine under Vite" caveat applies only if the canvas shell is a separate Vite app — inside
  the no-script DS bundle the closed-form constraint still holds. (Observed + Inferred.)
- **"one generic node-type + one generic edge-type, render-from-data (kills the per-type branch the SVG
  solver currently has)" (line 44)** — for the *glyphgraph* path this is already true (one `glyphGraphView`,
  one generic node = a glyphic, one generic edge = a meaning-edge). The "per-type branches" in DiagramSolver
  (orbital/stacked/spectrum/manifold/fidelity, :411-415) are the *deck-diagram* grammar, a DIFFERENT surface
  from the live meaning-graph — they don't need killing for the live layer, they're just not on its path.
  (Observed — avoid conflating the two diagram families.)

---

## F · Files read (coverage honesty)
**Fully read:** axis-core.js · all 9 axis modules (color/fill/form/motion/texture/size/space/depth/symbol) ·
styles.css · core/RenderType.jsx · core/ContainmentTree.jsx · core/DiagramSolver.jsx · core/archetype-catalog.js ·
core/cv-nodes.d.ts · tokens/dataviz.css · tokens/diagram.css.
**Targeted (grep + section reads):** colors_and_type.css (L0/L1/L2 chain + theme remap) · tonal-zoning.css
(via zone-role refs) · tokens/controls.css (L2 component tokens) · assets/icons/cv-glyphics.js (COLOR_TOKENS,
FILL_RAMPS, colorForValue, render) · assets/icons/cv-meaning.js (encodings, fields, lineColor seeds).
**Not opened (lower relevance to the 3 sub-questions):** tokens/{canvas,density,depth,export,focus,icons,
imagery,layout,motion,provenance,sizing,states,surfaces,texture,theme}.css individually (covered by the
import manifest + the role refs I traced); core/Slide.jsx · slide-fit.js · generative-core.html ·
slide-archetypes.html · containers.css (the block-layout chrome, off the live graph path). Flag: a deeper
pass on `theme.css` would confirm every L1 role's per-theme remap, but :450/:455 already proves the mechanism.
