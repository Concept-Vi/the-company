# AREA-21 · The SPATIAL / PROPORTION / DEPTH / ZONE substrate (what EXISTS today)

> Coverage agent companion for the live-instrument research wave. **Territory:** how SPACE, SIZE,
> PROPORTION, DEPTH, DENSITY, ZONES, LEVEL-OF-DETAIL, the spatial AXIS model, and any
> proportional/relative-coordinate placement are *defined and resolved* in the design-system repo
> `/home/tim/company/design/claude-ds/` today. **This grounds an incoming spatial-math theorem** —
> it is a *descriptive map of what is there to fuse/confirm/extend*, not a verdict and not a plan.
>
> **Lens:** descriptive only · duplications kept + catalogued by unique quality (fuse-not-pick) ·
> every claim marked **Observed (file:line)** (read directly in the file) or **Inferred** (read from
> a code comment / pattern, not executed). I did not run the build; nothing here is **Verified**.
> Files read in full: all 18 `tokens/*.css`, `tonal-zoning.css` + `Tonal Zoning System.html`,
> the four specimens, `core/containers.css` + `ContainmentTree.d.ts` + `slide-fit.js` +
> `cv-nodes.d.ts` + `core/DiagramSolver.jsx` (layout section) + `generative-core.html` +
> `slide-archetypes.html`, `system/axis-system.html` + `system-atlas.html` + `type-system.html`,
> `axes/axis-core.js` + space/size/depth/motion axes, `analysis/AXES.md` + `mid-lod.md` +
> `AXIS-REFACTOR.md`, `DESIGN-LANGUAGE.md`, and the app spatial CSS.

---

## 0 · The one frame that holds the whole territory together

Everything spatial in this repo resolves through **ONE governing idea, expressed at two levels**:

1. **Tokens are the value-units; an AXIS is the typed dimension those tokens sit on.** Space, Size,
   Depth, Motion are each a first-class `CV_AXES` axis whose values *point at* tokens (never copy
   them). **Observed** `axes/axis-core.js:5-17` (the docstring states "TOKENS ARE THE VALUE-UNITS OF
   AN AXIS … the size axis IS the --size-* tokens"); `:101-107` `resolveCSS()` returns
   `var(--<token>)`.
2. **`design = f(content, axisPosition)` over an invariant core** — a point in the dial-space
   *computes* the concrete spatial layout; the numbers/diagrams/frame-signature never move.
   **Observed** `analysis/AXES.md:30-34`.

So "how is space defined?" has a layered answer everywhere below: **a literal in a token home →
typed onto an axis → consumed by a slot/solver that resolves (not copies) it.** The theorem lands on
this stack.

---

## (a) SPACE · SIZE · PROPORTION · DEPTH · DENSITY — how they are defined + resolved today

### A1 · The spacing rhythm — a fixed 8px scale, plus a density-multiplied scale
- **The strict scale** `--s-*` lives in `colors_and_type.css` (referenced as the home throughout;
  e.g. **Observed** `tokens/sizing.css:42` "the 8px scale (--s-*)"). The **Space axis** is a typed
  view over it: 14 steps `s0..s24` = `0,4,8,12,16,20,24,32,40,48,56,64,80,96` px, grouped
  `inner / between / layout`, default `s4`. **Observed** `axes/space/space-axis.js:13-33`. Each value
  carries `token:'s-N'` and `meta.px` ("informational only — the token remains the source",
  **Observed** `:5-7`).
- **The density scale** `--d-*` is the *same idea multiplied by one knob*: `--d-N = calc(Npx *
  var(--density))`. **Observed** `tokens/density.css:18-30`. `--density` itself: `compact 0.8 ·
  comfortable 1 · spacious 1.25`, set by `[data-density=…]`. **Observed** `:15, :33-35`.
- **Two distinct spacing systems, KEPT (fuse-not-pick note):** the **fixed** `--s-*` (hard
  structural measures) and the **density-aware** `--d-*` (component padding/gaps) coexist
  deliberately — "The fixed 8px scale (--s-*) stays as-is for hard structural measures;
  DENSITY-AWARE tokens (--d-*) are what new components reach for." **Observed** `tokens/density.css:5-9`.
- Density also relaxes **fluid spacing + gutter** at the two ends. **Observed** `tokens/density.css:38-39`.
- Control sizes never drop below a touch floor: `--control-h: max(--touch-min, calc(40px *
  density))`. **Observed** `:28-30`.

### A2 · The proportional / RATIO system (the closest existing thing to a proportion calculus)
Three independent ratio mechanisms exist today:

1. **The modular type scale.** "each step ≈ previous × `--scale-ratio` (1.25), with a ~1.9 display
   jump." `--scale-ratio:1.25; --scale-base:16px`. The clamp pairs `--fs-caption … --fs-display`
   are its responsive expression. **Observed** `tokens/sizing.css:20-33`.
2. **Surface frames as an aspect-ratio TYPE system (height DERIVED, not set).** Each surface
   *declares* `-ar = w/h` (unitless) and `-w`; height is **computed**: `-h = calc(w / ar)`.
   "Adding a new surface = declare its -ar + -w and the -h auto-calculates — nothing hand-set."
   **Observed** `tokens/surfaces.css:31-47`. e.g. `--frame-desktop-ar: calc(1440/900)`,
   `--frame-deck-16x9-ar: calc(16/9)`, with `--frame-web-ar:0` a sentinel for "free-height".
3. **Ratio-invariant % grid types (hold at any frame ratio).** `--grid-margin:12% ·
   --grid-title-y:7.5% · --grid-band:76% · --grid-split:46%`. **Observed** `tokens/surfaces.css:49-53`.
   These are consumed by the Band: `padding-inline: var(--grid-margin)` (12%),
   `padding-block: var(--grid-title-y) …` (7.5%). **Observed** `core/containers.css:40-44`. The frame
   signature hatch uses the same `--grid-margin` as its left inset. **Observed** `tokens/texture.css:104`.
- **Image aspect-ratio tokens** as named proportions: `--ar-square 1/1 · --ar-portrait 3/4 ·
  --ar-landscape 4/3 · --ar-wide 16/9 · --ar-ultrawide 21/9 · --ar-hero 3/2`. **Observed**
  `tokens/imagery.css:10-16`. `.frame-ratio { aspect-ratio: var(--ratio, 16/9) }` is the generic
  proportion-lock primitive. **Observed** `tokens/layout.css:76`.

### A3 · The SIZE ramp (how big a whole element/mark is)
- `--size-xs 16 · sm 24 · md 40 · lg 56 · xl 72 · hero 96` (px). **Observed** `tokens/sizing.css:58-63`.
  This is the canonical "how big a thing is" home, *distinct* from the inline icon sub-scale.
- The **Size axis** is exactly those tokens, typed: groups `inline/standard/feature`, default `md`,
  each value carrying `token:'size-N'` and `meta.px` "for SVG/JS consumers" (a number the renderer
  can use). **Observed** `axes/size/size-axis.js:15-33`, docstring `:6-10`.
- **A separate icon sub-scale**, deliberately kept distinct: `--icon-xs 14 · sm 16 · md 20 · lg 24 ·
  xl 32` ("a glyph WITHIN chrome" vs the `--size-*` "whole element/mark"). **Observed**
  `tokens/icons.css:14-18` and the cross-note `tokens/sizing.css:53-57`.

### A4 · The DEPTH / elevation ramp — defined TWICE, by unique quality (a key fuse-not-pick)
Depth exists in two complementary forms; **both are kept, each does something the other can't**:
- **As a CSS shadow ramp** `--elev-0 … --elev-5` (flush → dragged/floating), each = "ambient + key"
  layer, warm-tinted via `--shadow-c` so palette swaps carry through; plus `--glow-active` (gold, the
  one decision element) and `--elev-inset`. **Observed** `tokens/depth.css:18-42`. Helper classes
  `.e0..e5`, `.glow-active`. **Observed** `:54-60`.
- **As the Depth axis (numeric geometry)** `flat · d1..d6 · normal`, mirroring the ramp but carrying
  `meta:{dy,blur,opacity}` (e.g. d3 `{dy:3,blur:2.6,opacity:0.24}`). **Observed**
  `axes/depth/depth-axis.js:23-31`. The docstring states the **reason both exist**: a CSS box-shadow
  can't follow a polygon, so "The SVG drop-shadow geometry a Glyphic uses lives in CV_GLYPHIC (it
  must follow the polygon, not a CSS box), but the SCALE + tint single-source here / tokens/depth.css."
  **Observed** `axes/depth/depth-axis.js:5-9`. → **The CSS ramp paints boxes; the axis-meta numbers
  drive a shape-accurate SVG shadow.** Same scale, two renderers.
- **Depth ⇄ nesting are explicitly the same gradient** (see C-zoning + AXES below):
  "Elevation and nesting are the same gradient." **Observed** `analysis/AXES.md:92-94`.
- Theme also re-tints depth per ground: `--shadow-c` flips for dim/dark/contrast. **Observed**
  `tokens/theme.css:42, :69, :88`.

### A5 · The Z / stacking system (depth in the layer sense)
- A single legal stacking order: `--z-base 0 · raised 10 · sticky 100 · nav 200 · overlay 300 ·
  modal 400 · popover 500 · toast 600 · command 700 · max 9999`. "the only legal stacking order …
  never hand-pick a z-index." **Observed** `tokens/layout.css:14-25`; rule restated
  `DESIGN-LANGUAGE.md:77`.
- The z-order *tracks containment depth + focus*: `ghost→ground→panel→card→glass→floating→modal`.
  **Observed** `analysis/AXES.md:92-93`.

### A6 · The radius ramp (proportion of corner) and grain/texture depth
- `--r-*` (xs..2xl, pill) is a fixed ramp consumed everywhere (e.g. `--dgm-node-radius:var(--r-md)`).
  Surfaced in the spacing/radius/elevation specimen. **Observed** `specimens/spacing-radius-elevation.html:49-56`.
- **Texture depth** (the felt-not-seen layer): grain `--grain-opacity 0.05 · --grain-scale 180px`
  (SVG fractal-noise), hairlines `--hairline / --hairline-strong` as `color-mix(shadow-c …)`.
  **Observed** `tokens/depth.css:44-50, :64-74`. Blueprint/hatch construction grids:
  `--blueprint-grid-size 24px`, `--hatch-gap 6px`, drawn as `repeating-linear-gradient`. **Observed**
  `tokens/texture.css:13-27, :59-71`.

---

## (b) ZONES — what the zone system IS, how zones are defined + computed

**The core finding: a zone's surface is NOT a chosen colour — it is COMPUTED from how deeply it is
nested.** This is the single most theorem-relevant mechanism in the repo.

### B1 · Zoning = containment depth made visible (the primary definition)
- **Observed** `core/containers.css:13-23` (the docstring): "a Zone's surface is … computed from how
  deeply it is nested. Each step inward adds ~2% pigment over the ground, so you read the structure
  by undertone, not borders."
- The formula, **verbatim**, **Observed** `core/containers.css:76-92`:
  ```css
  .cv-zone {
    --_pct: calc(var(--zone-depth) * 2.1%);      /* ~2% undertone per level */
    background: color-mix(in oklch,
        var(--zone-pigment, var(--pig-content))
        calc(var(--_pct) * var(--zone-intensity)),
        var(--zone-ground, #fff));
    box-shadow: inset 0 0 0 1px color-mix(in oklch,   /* hairline = one depth-step further */
        var(--zone-pigment, var(--pig-content))
        calc(var(--_pct) * 2.2 * var(--zone-intensity)),
        transparent);
  }
  ```
  So **zone surface = mix( pigment, ground, depth·2.1%·intensity )**, and the edge is the same at
  `×2.2`. Mixing *toward `--zone-ground`* is what makes it theme-invariant (works on dark grounds).
  **Observed** `core/containers.css:18-20`; confirmed `tokens/theme.css` flips only the ground.
- `--zone-depth` is a **registered integer custom property** with a safe fallback:
  `@property --zone-depth { syntax:"<integer>"; inherits:false; initial-value:1; }`. **Observed**
  `core/containers.css:28`.

### B2 · Who sets the depth (the computed vs hand-set duality)
- **Inferred (from comment, not executed):** the block solver sets `--zone-depth` *as it walks the
  tree* (+1 per nesting). "The block SOLVER (core/ContainmentTree.jsx) emits this markup and sets
  --zone-depth as it walks the tree." **Observed-as-comment** `core/containers.css:21-23`; restated
  `:94-98`. I read `ContainmentTree.d.ts`, not `ContainmentTree.jsx`, so the walk itself is Inferred.
- **Hand-authored nesting** sets it inline: `style="--zone-depth:2"`. Kept as an inline knob "not a
  descendant rule — so the wash stays a pure function of the supplied depth." **Observed** `:94-98`.

### B3 · The optional semantic-tone LAYER (on top of the depth ladder)
- Beyond depth, a zone can carry a **pigment** = a semantic category. Ten tones, each a pigment
  mixed toward ground at a low %: base 3.5% · content 3% · panel 5% · review 6% · source 5% ·
  package 6.5% · success 6% · warning 7% · reject 6% · vi/gold 9%. **Observed**
  `Tonal Zoning System.html:202-213` and the registry specimen `specimens/surface-zone-registry.html:53-64`.
- In code: `.cv-zone[data-tone="neutral"]{--zone-pigment:var(--pig-panel)}`,
  `[data-tone="review"]{--zone-pigment:var(--pig-review)}`. **Observed** `core/containers.css:102-103`.
- **The explicit ordering rule:** "The primary zoning is *depth* … these are the opt-in category
  layer on top." **Observed** `specimens/surface-zone-registry.html:48`; `Tonal Zoning System.html:27`;
  `analysis/AXES.md:58-64`.
- **One intensity knob** scales the whole language: `--zone-intensity` (the `× intensity` in the
  formula). Default 1; themes raise it (dim 1.5, dark 1.7, contrast 1.45) so washes still read on
  dark grounds. **Observed** `tokens/theme.css:25, :51, :77`. The Tweaks panel drives it live as
  `tintIntensity`. **Observed** `Tonal Zoning System.html:325, :336`.
- **The gold rule** (a zone discipline, not a tone): gold is the only saturated voice, reserved for
  Vi / active decision / selected / key emphasis — never a default background. **Observed**
  `specimens/surface-zone-registry.html:50`; `DESIGN-LANGUAGE.md:54-58`.

### B4 · Zone surfaces are exposed as a flat role-token set too (the consumed form)
- Each tone resolves to `--zone-<k>-surface / -strong / -edge / -ink` role tokens that components
  read directly (e.g. `.ov-block.source { background: var(--zone-source-surface) }`). **Observed**
  `tonal-zoning.css:303-305`; the applied Overview re-skin uses ~6 zones at once
  (`Tonal Zoning System.html:135-164`). So zones appear in **two forms, both kept**: the *computed
  depth wash* (`.cv-zone`) and the *flat semantic role tokens* (`--zone-*-surface`) — the depth form
  is structural/recursive, the role form is hand-placeable per region.

### B5 · The "spatial connective" zone layer (paths between zones)
- A separate visual layer draws **dashed path lines + diamond nodes between zone markers**,
  governed by `--spatial-opacity / --spatial-line / --spatial-faint / --spatial-node` and a faint
  64px construction grid on the body. **Observed** `tonal-zoning.css:28-37, :240, :285`;
  `Tonal Zoning System.html:81-93, :268-291`. Toggled by the Tweaks `spatial` knob. This is the
  "work moves through the system" overlay — proto-spatial, separate from the canvas coordinate model.

---

## (c) LEVEL-OF-DETAIL / ZOOM / NESTING / CONTAINMENT MATH already present

### C1 · The containment ladder (the structural spine)
- Five typed nesting levels: **Band → Section → Zone → Cluster → Atom**. **Observed**
  `core/containers.css:5-14`; the kind enum `cv-nodes.d.ts:19` (`"band"|"section"|"zone"|"cluster"|
  "atom"|"diagram"`). Each level: a ROLE, an inherited spacing rhythm, a collapse rule; only Zones
  paint (depth wash). Sections + Clusters are structural/unpainted. **Observed** `core/containers.css:30-149`.
- The same ladder is documented at deck scale `Deck→Slide→Section→Zone→Group→Atom`. **Observed**
  `analysis/AXES.md:42-53`.

### C2 · LOD = per-node prune/grow (content zoom, INDEPENDENT of surface)
- LOD is `summary | pitch | full`, the **content** zoom; orthogonal to surface. **Observed**
  `core/ContainmentTree.d.ts:6-7`; `cv-nodes.d.ts:10-12`. Rule "LOD ≠ surface … a phone can show
  *high* detail; a desktop can show *low*." **Observed** `analysis/AXES.md:36-40`.
- The prune/grow MATH is **priority + detail flags on nodes**: `priority?:1..n` ("1 always shows;
  higher drops first as LOD lowers") and `detail?: "always" | "support"` ("support atoms hide at low
  LOD"). **Observed** `cv-nodes.d.ts:45-48`. The solver "prunes low-priority / support nodes before
  layout." **Inferred-from-comment** `core/ContainmentTree.d.ts:17-22`.
- LOD operates ON the tree, can be **per-container** → that is progressive disclosure
  (`disclose?:boolean` on a node, **Observed** `cv-nodes.d.ts:41`). **Observed** `analysis/AXES.md:83-87`.
- LOD-locked invariants are *node types*, not a separate concept (numbers/diagrams never prune).
  **Observed** `analysis/AXES.md:98-100`.

### C3 · Nesting math + collapse (the "responsive = per-level fold")
- Reflow is **per-container-level**, not global: `split→stack` at `@container (max-width:640px)`,
  grids drop columns, band margins relax to the mobile gutter. **Observed** `core/containers.css:151-166`.
  Each Band/Zone is its own query container (`container-type: inline-size`). **Observed** `:166`.
- The cluster flows (the layout-only sibling grouping): `row · grid · split(46fr 54fr) · overlay ·
  wall`. **Observed** `core/containers.css:121-146`; the split ratio default `46fr 54fr` ties back to
  `--grid-split:46%`. `cv-nodes.d.ts:36-37` (`flow`, `split` override).

### C4 · The "zoom" / fit math — fixed-design-width content scaled into a frame
There is a real *zoom* mechanism, but for **paged surfaces, not an infinite canvas** — and it exists
in **four near-identical implementations (a prime fuse-not-pick duplication):**
- **The canonical one:** `core/slide-fit.js` (`CV_SLIDE_FIT`). Stage authored at `--cv-stage-w`
  (default 1280); `s = Math.min(fw/designW, fh/h)`; `stage.transform = scale(s)`; letterboxes
  (centres) when `used < fh`. Heartbeat re-fits until the layout signature is stable. **Observed**
  `core/slide-fit.js:29-51, :74-94`. CSS frame/stage in `core/containers.css:179-198`.
- **Three inline re-implementations of the same scale-to-fit:** `Tonal Zoning System.html:294-306`
  (`scale = Math.min(1, avail/DESIGN_W)` on `.ov`, DESIGN_W 1240); `core/generative-core.html:89-96`
  (`s = frame.clientWidth/DESIGN_W`, 1100); `core/slide-archetypes.html:58-59` (same, 1100). **Observed.**
  → **Unique quality each:** `slide-fit.js` adds height-aware letterboxing + a stability heartbeat +
  ResizeObserver/MutationObserver; the three inline ones are width-only and also build their own SVG
  flow overlay (Tonal Zoning). The *idea* "fixed-size content implements its own JS scaling" is the
  stated system rule. **Observed** `core/slide-fit.js:5-9`.
- **No infinite pan/zoom solver is wired** — `tokens/canvas.css` declares the world transform vars
  (next section) but the file header says "The interactive engine (pan/zoom drag, auto-routing, …)
  is a later component." **Observed** `tokens/canvas.css:7-12`.

### C5 · mid-LOD confirmation (the LOD ladder holds)
- The LOD ladder is confirmed complete across the corpus (summary→pitch→full, + a tighter one-pager
  rung), no new structure at mid-detail. **Observed** `analysis/mid-lod.md:8-10, :35-38`;
  resolved-questions `analysis/AXES.md:134-137`.

---

## (d) The AXIS model for spatial axes (space / size / depth / motion)

### D1 · The shared axis foundation
- `CV_AXIS` (factory) + `CV_AXES` (registry of axes) mirror the other registries
  (register/resolve/list/query/subscribe), with a value **hierarchy** (group→value), a `default`,
  `meta`, and `resolveCSS(id)` → `var(--token)` | literal css | a `resolve(fn)` computed payload.
  **Observed** `axes/axis-core.js:43-131`.
- A value's identity: `{ id, label, group, token | css | resolve, zero, meta }`. **Observed** `:62-69`.
- **A SUBSCRIPTION is how a slot consumes an axis:** `{ axis, groups?|values?, default, conditions? }`;
  `candidates(sub)` returns the allowed value ids (what an editor/foundry shows). **Observed**
  `axes/axis-core.js:24-28 (doc), :111-117, :151-160`. Loud-fail on missing axis/value
  (`fail()` throws). **Observed** `:34, :84, :142`.
- The whole set is enumerable and **projected live** (the interface reads the registry, no parallel
  list): the Axis-System page renders every axis + every value from `CV_AXES`. **Observed**
  `system/axis-system.html:60-159`.

### D2 · The nine primary axes (the spatial ones in bold)
Registered set: Colour · **Space** · **Size** · **Motion** · Texture · **Depth** · Fill · Form ·
Symbol, with **Meaning** the contextual/loadable layer over them. **Observed**
  `DESIGN-LANGUAGE.md:131-142`; `analysis/AXIS-REFACTOR.md:49-66`; load order
  `system/type-system.html:10-23`. Build status: "all 9 axes BUILT & verified (slice 60)" with
  spot-checks (size md → `var(--size-md)` + 40px; depth/space token-backed). **Observed-as-log**
  `analysis/AXIS-REFACTOR.md:127-138`.

| Spatial axis | Values (verbatim) | Home / payload | file:line |
|---|---|---|---|
| **Space** | `s0..s24` (14 steps, 0→96px) groups inner/between/layout, default s4 | `token:'s-N'` → `var(--s-N)`; `meta.px` informational | `axes/space/space-axis.js:13-33` |
| **Size** | `xs sm md lg xl hero` (16→96px) groups inline/standard/feature, default md | `token:'size-N'`; `meta.px` for SVG/JS | `axes/size/size-axis.js:15-33` |
| **Depth** | `flat d1..d6 normal` groups flat/raised/system, default normal | `token:'elev-N'` + `meta:{dy,blur,opacity}` | `axes/depth/depth-axis.js:23-31` |
| **Motion** | `none breathe float pulse glow bob tilt spin` groups static/ambient/attention/interactive/process | `css:'mo-*'` class realised in `axes/motion/motion.css` | `axes/motion/motion-axis.js:32-42` |

- **Motion is a spatial-TEMPORAL axis** and is explicitly the place "nothing teleports" lives:
  travel distances `--move-xs 8 · sm 16 · md 32 · lg 64 · off 120%`, stagger step 55ms, easings
  (entrance decel / exit accel). **Observed** `tokens/motion.css:31-41, :25-29`. Motion = "temporal
  traversal of the tree … a container can show all children in space OR play them over time — same
  subtree, two renderings." **Observed** `analysis/AXES.md:79-82`; node knob `mode?: "space"|"time"`
  **Observed** `cv-nodes.d.ts:38-39`.

### D3 · How a consumer reads an axis (the resolution path)
- A component declares each part-slot as a subscription; the foundry/editor shows exactly
  `CV_AXES.candidates(sub)`; nothing hardcodes a value table. **Observed** `DESIGN-LANGUAGE.md:131-142`;
  the universal-component grammar (parts / value-slots / sockets / conditions) `:114-129`.
- Type-System page projects every Type's value-slots as `→ axis` subscriptions live. **Observed**
  `system/type-system.html:121-129`.
- **The anti-drift mandate applied to axes:** "One home per axis. Consumers hold references
  (subscriptions), never copies. No hardcoded per-consumer value tables … Loud fail on missing
  axis/value." **Observed** `analysis/AXIS-REFACTOR.md:31-35`. (The incoming theorem must land *on*
  this discipline — values point at one source.)

### D4 · The dial-space (the input axes the spatial output is computed FROM)
Beyond the visual `CV_AXES`, AXES.md names the **input dials** that compute spatial output:
Surface · LOD · Register/pace · Theme · Density · Tint/gold-intensity — **orthogonal, compose
freely**. **Observed** `analysis/AXES.md:11-18`. Derived spatial outputs (never set directly): type
sizes ← surface; margins/gutters ← surface×density; reflow ← surface; surface tints ← intensity ×
ground × pigment. **Observed** `:20-24`. Two hard rules: keep axes orthogonal (LOD≠surface), and
"correlation ≠ coupling." **Observed** `:35-41`.

---

## (e) Proportional placement · grids · relative coordinates · n/x division

This is where the repo already does the most "spatial math." **There are THREE distinct coordinate
models present (all kept — catalogue, don't pick):**

### E1 · MODEL A — SVG-normalized relational placement (the graph solver) — the richest n/x math
`core/DiagramSolver.jsx` computes node positions **from relationships**, closed-form (no layout lib,
CSP/bundle constraint), into a square viewbox `VB = 320`, radius `R = 130`. **Observed** `:14, :27`.
Verbatim formulas (theorem will ground against these):
- **Ring (radial):** `a = -π/2 + (i·2π / n)`; `x = cx + R·cos a`, `y = cy + R·sin a`. **Observed**
  `core/DiagramSolver.jsx:36-39`. Used by hub (centre at `cx,cy` + ring of the rest), morph
  (before=ring → after=hub), network. **Observed** `:42-53`.
- **Even-spread (n/x division):** `x = 40 + (i · (VB-80)) / Math.max(1, n-1)`. **Observed**
  pipeline `:55`, timeline `:58` (anchored lower), tree leaves `:126`, stack (vertical) `:130`.
- **Normalized 0..1 author coordinates → pixels:** quadrant `x = 40 + (nd.x ?? 0.5)·(VB-80)`,
  `y = VB-40 - nd.y·(VB-80)` (y inverted). **Observed** `:60-61`. Glyphgraph authored case
  `x = 30 + nd.x·(VB-60)`. **Observed** `:68-70`.
- **DAG layering fallback (glyphgraph, no authored coords):** rank = longest-path-from-a-source via a
  relax loop; group by rank into rows; row stride `LAY_ROW_PITCH = (VB - 2·44) / max(1, nR-1)`.
  **Observed** `:73-112`.
- **★ STABLE-SLOT placement (the staged-reveal stability rule — directly theorem-relevant):** a
  node's coordinate is `x = LAY_MARGIN + ci · LAY_PITCH`, where `ci` is its **FIXED author-order slot
  index** and `LAY_PITCH = LAY_SIZE(58) · 1.55` (≈90px) is a **fixed pitch — NEVER the live count**.
  So adding a sibling does **not** move existing nodes (the old even-spread `ci·(VB-88)/(m-1)`
  re-centred the whole row on every addition — "a 116px jump on a 320 canvas, verified"). Growth is
  absorbed by unused slots; rows are **left-anchored**, and the off-centre consequence is *flagged for
  Tim, not papered over* ("no green-paint compression"). **Observed** `core/DiagramSolver.jsx:96-118`.
  → This is the existing precedent for **stable incremental layout as nodes arrive** (the live-graph
  pain point in ANCHOR §6).
- Node shapes are SVG polygon point-strings (proportional 0..100): `hex "25,3 75,3 97,50…"`,
  `octagon`, `diamond`. **Observed** `core/DiagramSolver.jsx:177`. Brand ramp indexes tint onto
  sequence/position. **Observed** `:145`.
- The graph types: `network·hub·morph·pipeline·timeline·quadrant·tree·compare·stack·stepper`
  (+`glyphgraph` in code). **Observed** `cv-nodes.d.ts:70-72`; edge kinds `flow·dependency·reference·
  rejected`. **Observed** `:87-93`.
- Other proportional sub-diagrams use **percent-along-an-axis** coords: orbital ring
  `left/top = (50 + rad·cos a)%` (`:198-200`), spectrum `at ∈ 0..1 → left:(at·100)%` (`:236-242`),
  manifold `grid-template-columns: repeat(n, 1fr)` (`:255`). **Observed** in `core/DiagramSolver.jsx`.

### E2 — MODEL B — world pan/zoom coordinates (the spatial canvas scaffold)
`tokens/canvas.css` declares a **pannable/zoomable plane**: viewport `.spatial-canvas`; world
`.spatial-world { transform: translate(--cv-x, --cv-y) scale(--cv-scale) }`; nodes absolutely placed
at `left:var(--x); top:var(--y)` in world px; edges in one `<svg class="spatial-edges">` spanning the
world. **Observed** `tokens/canvas.css:13-66`. Grid `--cv-grid 28px` painted as crossed linear
gradients offset by the pan. **Observed** `:23, :30-34`. Branch/ghost states
(`--cv-ghost-opacity 0.4`, off-frame mask, a docked memory shelf). **Observed** `:66-82`.
- **Status: scaffold only** — the header states the interactive engine is a later component.
  **Observed** `:7-12`. → This is the existing *world-coordinate* substrate a reactflow-style live
  canvas would either reuse or sit beside.

### E3 — MODEL C — proportional CSS grids + Every-Layout primitives (placement without coordinates)
- **Responsive auto-grids — duplicated twice, kept (fuse-not-pick):** `.auto-grid` (`tokens/sizing.css:147-151`,
  `auto-fill, minmax(min(--col-min 240px,100%),1fr)`) and `.grid-fit` (`tokens/layout.css:81-85`,
  `auto-fit, …`). **Unique quality:** `auto-fill` keeps empty tracks (stable column count);
  `auto-fit` collapses them (items stretch). Both `minmax(min(col-min,100%),1fr)` — the same overflow-
  safe proportion clamp.
- **Composable layout primitives (after Every-Layout), responsive by construction:** `.stack ·
  cluster · sidebar · center · cover · reel · frame-ratio · grid-fit · switcher`. **Observed**
  `tokens/layout.css:27-92`. `.switcher` is the notable proportion trick:
  `flex-basis: calc((var(--threshold,460px) - 100%) * 999)` (all-row-or-all-column). **Observed** `:90-91`.
  `.sidebar` content `flex: 999 1 var(--content-min, 60%)`. **Observed** `:46-48`.
- **The split layout** as a fr-proportion: `grid-template-columns: var(--split, 46fr 54fr)`.
  **Observed** `core/containers.css:130-135`. App shell columns `248px 1fr 360px`. **Observed**
  `app/app.css:17`. Tonal Zoning Overview `232px 1fr 320px`. **Observed** `tonal-zoning.css:229-237`.
- **Data-viz proportions** (number as length/angle): bar `width: calc(var(--val) * 1%)`, gauge
  `conic-gradient(… calc(var(--val)*1%) …)`, sparkline polyline. **Observed** `tokens/dataviz.css:42-64`.

### E4 — The fixed-ratio frame grid (proportional placement on a slide)
- The Band carries the ratio-invariant % grid (`--grid-margin 12%` inline padding, `--grid-title-y
  7.5%` block) so the *same* placement holds at any surface ratio. **Observed** `core/containers.css:40-44`.
  The frame signature places its hatch + V mark inside the 12% margins. **Observed**
  `tokens/texture.css:101-115`. Page/export frames are fixed px grids: A4 `794×1123`, slide-16x9
  `1920×1080`, `--page-margin 64px`. **Observed** `tokens/export.css:17-24`.

---

## Cross-cutting: the DUPLICATIONS catalogued (fuse-not-pick, each by unique quality)

1. **Fixed-width→frame scaler — 4 implementations.** `core/slide-fit.js` (height-aware letterbox +
   stability heartbeat + observers) vs three inline width-only `fit()`s
   (`Tonal Zoning System.html:294-306`, `generative-core.html:89-96`, `slide-archetypes.html:58-59`).
   The inline Tonal-Zoning one additionally rebuilds an SVG flow overlay. **Observed.**
2. **Depth in two forms.** CSS shadow ramp `--elev-*` (paints CSS boxes) vs Depth-axis numeric
   `meta:{dy,blur,opacity}` (drives polygon-accurate SVG shadow). Same scale, different renderer.
   **Observed** `tokens/depth.css:18-42` + `axes/depth/depth-axis.js:23-31`.
3. **Responsive grid utility ×2.** `.auto-grid` (`auto-fill`) vs `.grid-fit` (`auto-fit`).
   **Observed** `tokens/sizing.css:147` + `tokens/layout.css:81`.
4. **Three coordinate models.** SVG-normalized 0..1 + closed-form trig (DiagramSolver) · world-px
   pan/zoom `--x/--y/--cv-scale` (canvas.css) · ratio % + fr grids (containers/layout). Each fits a
   different surface (relational diagram · infinite plane · paged/responsive frame). **Observed.**
5. **Two spacing scales.** Fixed `--s-*` (structural) vs density-multiplied `--d-*` (component).
   **Observed** `tokens/density.css:5-9`.
6. **Two zone forms.** Computed depth wash (`.cv-zone`, recursive) vs flat semantic role tokens
   (`--zone-*-surface`, hand-placed per region). **Observed** `core/containers.css:76-92` +
   `tonal-zoning.css:303-305`.
7. **Two size sub-scales.** `--size-*` (whole element/mark) vs `--icon-*` (glyph within chrome),
   kept distinct on purpose. **Observed** `tokens/sizing.css:53-63` + `tokens/icons.css:14-18`.

---

## What this grounds for the incoming spatial theorem (Inferred framing — not a verdict)

**Inferred.** The theorem will likely speak in terms of *position, proportion, nesting depth, and
how a thing scales/places relative to others.* The repo already supplies, as single sources:
- a **depth→appearance function** (`mix(pigment, ground, depth·2.1%·intensity)`) that is *recursive*
  and *theme-invariant* — a candidate primitive for "nesting depth as a computed quantity";
- a **ratio TYPE system** where height is derived (`h = w/ar`) and a **ratio-invariant % grid**
  (12/7.5/76/46) that holds across surfaces — a candidate "proportional placement that is
  surface-independent";
- **closed-form relational placement** (ring trig, n/x even-spread, 0..1 normalized author coords,
  DAG layering) and a **stable-slot rule** that pins existing nodes when new ones arrive — the exact
  precedent for incremental live-graph layout;
- a **world pan/zoom coordinate scaffold** (`--cv-x/y/scale`, node `--x/--y`) awaiting an engine;
- the **AXIS discipline** (Space/Size/Depth/Motion are typed dimensions whose values point at one
  token home; consumers subscribe, never copy) — the rail any new spatial quantity should sit on so
  it doesn't stale.

Where these are duplicated (the 7 above), the duplication is by *unique quality*, so the theorem can
**fuse** them onto one model rather than choosing one — that variety is itself the finding.

---

### 3-line summary
The repo already defines space/size/proportion/depth/density as **tokens typed onto first-class
`CV_AXES` axes** (values point at one token home, never copies), with **zones computed from nesting
depth** (`mix(pigment, ground, depth·2.1%·intensity)`, theme-invariant) as the primary spatial
mechanism and semantic tones an opt-in layer on top. **Three coordinate models coexist** — closed-form
SVG-normalized relational placement (ring trig + n/x even-spread + 0..1 author coords + a **stable-slot
rule that pins nodes as new ones arrive**), a **world pan/zoom scaffold** (`--cv-x/y/scale`, awaiting
its engine), and ratio-invariant `%`/`fr` CSS grids (`h=w/ar`, 12/7.5/76/46) — alongside LOD as
per-node priority/detail prune-grow and a 4×-duplicated fixed-width→frame fitter. Everything is
captured with verbatim formulas + file:line for the theorem to fuse/confirm/extend; duplications are
kept and catalogued by unique quality, not resolved.

Path: `/home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-21-spatial-proportion-zones.md`
