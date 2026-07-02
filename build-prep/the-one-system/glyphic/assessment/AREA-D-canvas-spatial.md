# AREA D · The Canvas + The Spatial Theorem Made Real

> Wide-assessment agent D. Territory: renderer decision (tldraw vs reactflow vs the SVG solver vs
> the CSS scaffold), the address algebra as a real placement law, fields-on-canvas, LOD/zoom-as-scale,
> and the one-IR discipline. Lens: citizenship × provision × the fusion map (ANCHOR §2). Evidence
> marked **Observed (file:line)** / **Inferred** / **Your-idea**. Stress-tested against ANCHOR §4's
> hard parts, not confirmed blind.

---

## 0 · The headline finding (read this first)

**There is no renderer decision to make between reactflow and tldraw — reactflow does not exist
anywhere in this codebase, not even in a lockfile.** `grep -rl "reactflow\|@xyflow" --include=package.json`
across `~/company` and `~/repos/counterpart` returns **zero hits**, in source AND in every
`node_modules` tree already installed. **Observed** (direct grep, this session). The ANCHOR's framing
("reactflow-vs-tldraw decision unmade") is **stale** — there is nothing to decide between; tldraw is
the only graph-canvas library actually vendored, in exactly one place (`canvas/app/package.json:9`,
`"tldraw": "^3.13.1"`). **Observed.**

What actually exists is **four candidate substrates that are not competitors — they are different
projections of the same CVGraph IR, already specialised for different jobs**, plus one glaring
absence (an infinite pan/zoom canvas with drag). The real decision is not "which library" but **which
job each substrate keeps, and how the address algebra becomes the placement law inside each.**

---

## 1 · The four substrates, first-hand (citizenship audit)

### 1a · `DiagramSolver.jsx` — the closed-form relational solver (claude-ds, design-side)
**What it is.** A pure function `layout(graph) → {id: {x,y}}` over a fixed 320×320 viewBox, no
external layout library, ten graph types (`network·hub·morph·pipeline·timeline·quadrant·tree·
compare·stack·stepper` + `glyphgraph`). **Observed** `core/DiagramSolver.jsx:14,27,41-133`.

**The stable-slot law (G11) — the existing precedent for incremental live-graph layout, read in full:**
```
x = LAY_MARGIN + ci · LAY_PITCH        // ci = FIXED author-order slot index, never live count
LAY_PITCH = LAY_SIZE(58) · 1.55        // ≈90px, fixed — independent of render-shrink thresholds
LAY_ROW_PITCH = (VB - 2·LAY_MARGIN) / max(1, nR-1)   // row stride; nR grows only on a NEW rank
```
**Observed** `core/DiagramSolver.jsx:96-118`, comment-verified against the AREA-21 finding
(`AREA-21:337-344`) — same formula, same file, cross-confirmed. This is not a general theorem yet —
it is a **left-anchored, single-row, fixed-pitch placement for one glyphgraph render pass**. It solves
exactly the "a 116px jump on a 320 canvas" regression (comment, `:99-100`) but:
- **It has no persistence.** Every call to `layout()` recomputes from scratch off `graph.nodes`'
  *current* array order (`rows[rank].push(nd)` walks `nodes` in whatever order the caller passed them
  — **Observed** `:92`). If the caller's node array order is not itself stable (e.g. re-sorted,
  re-fetched, or re-composed upstream), the "fixed slot index" is fixed *within one call*, not fixed
  *across time*. **Your-idea:** the real stable-slot law needs the slot index derived from an
  **address**, not from array position — see §2.
- **It has no addressed coordinate.** A node's `{x,y}` is a pixel pair inside a 320-unit viewBox; it
  is not resolvable, not referenceable from outside the render, and not derived from the CVGraph IR's
  `x?/y?` fields except in the `authored` branch (**Observed** `:68-71`, 0..1 normalised author
  coordinates → pixels — this IS an address-like span, see §2).
- **Citizenship verdict:** addressed — **partial** (only the authored-coordinate branch is a real
  span; the DAG-layering fallback is array-order-derived, not address-derived). Typed — **yes** (the
  ten graph types are a closed enum, `cv-nodes.d.ts:70-72`, though `glyphgraph` is missing from that
  enum — see §5 drift). Derived — **yes**, closed-form, no placed literals. Two-way — **no**: a node's
  screen position cannot be read back into an authored `x/y` (drag doesn't exist on this substrate at
  all — it renders once per data change, no pointer interaction). Frame-resolved — **no**: one fixed
  320-unit viewBox, no responsive re-layout, no LOD.

### 1b · `tokens/canvas.css` — the world-coordinate scaffold (claude-ds, design-side)
**What it is.** A declared-but-unimplemented pan/zoom coordinate model: `.spatial-canvas` (viewport) →
`.spatial-world` (`transform: translate(--cv-x,--cv-y) scale(--cv-scale)`) → `.spatial-node`
(`left:var(--x); top:var(--y)`, world px). **Observed** `tokens/canvas.css:13-46`. The file's own
header states plainly: **"The interactive engine (pan/zoom drag, auto-routing, spec→diagram
generation) is a later component that builds on this."** **Observed** `:7-12`. There is no JS anywhere
in the repo that sets `--cv-x/--cv-y/--cv-scale` from a pointer event — I grepped the surrounding
system files and found no consumer. This is CSS-only scaffolding, exactly as documented, and it has
sat unbuilt since it was written (no dated commit evidence found, but AREA-21 catalogued it identically
in the prior wave — it hasn't moved).
- **Citizenship verdict:** addressed — **no** (a var, not a resolvable coordinate). Typed — **no**
  (a raw CSS custom property, not a `CV_AXES` axis — this is itself a gap: Space/Size/Depth/Motion are
  first-class axes per AREA-21 §D2, but the *world pan position* is not). Derived — **n/a** (nothing
  computes it). Two-way — **n/a**. Frame-resolved — **no**.
- **What it actually gives, honestly:** a real, already-designed **branch/ghost/memory-shelf
  vocabulary** (`.spatial-ghost` off-frame continuation, `.spatial-memory` a docked rejected-work
  shelf, `.has-branch` opacity dimming for non-active branches — **Observed** `:66-82`) that neither
  tldraw nor DiagramSolver has any equivalent for. This is provision the other two substrates lack —
  it should not be discarded even though the coordinate engine under it never got built.

### 1c · `system/system-map.html` — the one working interactive graph at real repo scale
**What it is.** A **sunburst/radial tree** (not a force graph) rendering `system-map.json` (built by
`system/build-system-map.js`) — a live, editable, pannable, real-file-count visualisation of an actual
repo folder tree, with an **op-queue** for structural edits (create/rename/move/archive/delete) that
batch into `EDITS[]` and require a disk-write adapter (Claude Code) to apply, then rescan. **Observed**
`system/system-map.html:227,671,695-775,879-895`. It supports select/deselect, undo/redo over the
in-memory model + op-queue, a FLIP-style morph animation between layout states
(`el.style.transform = translate(...) scale(...)` captured-before/animated-after, **Observed**
`:631-649`), and a rescan-from-disk poll. This is a **genuinely working, editable, at-scale
interactive graph** — the strongest existing citizen of anything resembling "the interactive canvas."
- **Its scale regime:** hundreds of files/folders (a real repo tree), **not** the 76k-unit corpus
  scale named in ANCHOR §3, and **not** a conversation-sized ~40-node glyphgraph either. It is a third,
  distinct scale point.
- **Its coordinate model:** polar/angular (`arc`, rotation, radial rim labels — **Observed** `:592-597`),
  not Cartesian pan/zoom, and not the address-span algebra (§2) — it is closer to the DiagramSolver's
  `ring()` trig than to `canvas.css`'s world-px model. **A fourth, distinct coordinate scheme, not
  cross-referenced from the address-face doctrine at all.**
- **Citizenship verdict:** addressed — **partial** (each node has an `id`/`path`, but position is
  computed from tree-depth + sibling-count via arc math, not a stored/resolvable address string).
  Typed — **yes** (folder/file kind enum). Derived — **yes**. Two-way — **yes, uniquely**: this is the
  *only* substrate of the four with a real write-back path (the op-queue → adapter → rescan loop).
  Frame-resolved — **partial** (`preserveAspectRatio="xMidYMid meet"`, no semantic zoom/LOD).

### 1d · `canvas/app` — the tldraw operating console (Company-side, backend-owns-positions)
**What it is.** A live, running, multi-panel operator surface built on `tldraw@3.13.1`, wrapping the
tldraw editor with one custom shape type (`NodeShapeUtil`) plus a `ForagerShapeUtil` (a second shape
vocabulary for corpus-search hit circles, coexisting deliberately — comment says "the loaders blind to
each other's shapes", **Observed** `App.tsx:269-271`). **Observed** `App.tsx` (454 lines, the F0-carved
shell), `NodeShape.tsx` (279 lines).

**Backend-owns-positions, verbatim (the load-bearing law of this substrate):**
```ts
// C5-fe: update-or-create-or-PRUNE (mirrors refresh()). The backend `n.position` is the SINGLE source of
// truth for layout — so we never invent coordinates and never let tldraw's IndexedDB own the layout.
```
**Observed** `NodeShape.tsx:187-190`. `loadGraph()` reads `n.position` off the backend graph for every
node; only when the backend gave none does it fall back to `{x: 150+i*300, y: 220}` (**Observed**
`:201`). A drag calls `api.move(node,x,y)` (**Observed** `api.ts:42-43`) which writes back to the
backend — so tldraw's own local store is a *reflection*, never the source, matching the corpus-wide
"reflects-never-owns" law named repeatedly in the file's own comments (`App.tsx:21` PRESERVED list).

**Live-updating via SSE, not polling** — confirmed directly, not inferred: `useAppController.ts:636`
opens `new EventSource('/api/stream?since='+since)`, dispatches by kind, `mergeEvents()` dedupes by
seq, and `es.onerror` relies on auto-reconnect + Last-Event-ID for gapless resume (**Observed**
`useAppController.ts:632-701`). This is a materially more mature live-update mechanism than anything
in claude-ds's three substrates (none of which have a live-update path at all — they render once from
a static `graph` prop).

**Semantic zoom exists, minimally:** `const zoom = useValue('zoom', () => editor.getZoomLevel())`,
`const expanded = zoom > 0.5` — the node card's body/address line hide below 0.5 zoom (**Observed**
`NodeShape.tsx:47-49,150,166`). This is a single threshold, not a graded LOD ladder, but it is a
**real, live-wired semantic-zoom hook** — more than DiagramSolver or canvas.css have.

**Edges are a reactive screen-space overlay**, computed fresh every render off `editor.getShapePageBounds`
+ port index (mirroring the shape's own `portTop()` so wires land exactly on nubs), subscribed to
camera changes via `useValue('edges', ...)` (**Observed** `NodeShape.tsx:243-268`). This is a real,
working port-to-port wiring system with drag-to-connect (pointer-capture based, **Observed** `:95-128`)
— something none of the other three substrates attempt.

- **Citizenship verdict:** addressed — **yes, and the richest of the four**: every node carries
  `p.address` as `data-ui-ref`, the canonical `run://<graph>/<node>` instance address (**Observed**
  `NodeShape.tsx:133-139`), explicitly cross-referenced to the design-substrate `CONTRACT.4` and
  excluded from the `ui://` orphan scanner because `run://` is a *live instance* address, not a
  registry entry — a real, working example of the "glyph = address" law (THE-GENERATIVE-LANGUAGE §1
  root) already in production, just not yet connected to the glyphic vocabulary. Typed — **yes**
  (props schema `T.string`/`T.number` per field, tldraw-validated). Derived — **yes** (every field
  reads from the backend registry: `getOINFO()` for ports, `getNODE_STATES()` for status colour token —
  **Observed** `:53,64-84` — a direct, working instance of "registry-is-truth" that AREA-21's axis
  discipline demands generically). Two-way — **yes** (drag→move, connect→wire, both write back).
  Frame-resolved — **partial** (one zoom threshold, not a reader-frame resolution).

### 1e · `surface/app` — what exists (the fresh paper-aesthetic instrument surface)
**Observed** from its own `package.json` description: *"The fresh paper-aesthetic instrument surface
for the Company (built alongside canvas/app, never on top)."* **Observed** `surface/app/package.json:6`.
It has **no tldraw, no reactflow, no canvas library at all** — dependencies are only
`framer-motion + react + react-dom` (**Observed** `package.json:14-18`). Its structure (`wheel/`,
`toggles/`, `transcript/`, `rhm/`, `board/BoardView.tsx`) is a **radial/wheel-based operator dial**, not
a node-graph canvas. **This is not a fifth graph-canvas candidate — it is a different kind of surface
entirely** (an operator control-wheel + board view), explicitly built to coexist with `canvas/app`
rather than replace it. It is relevant to the glyphic instrument only insofar as the instrument may
need to appear as a mode/panel inside it (ANCHOR §6.5's "mode/loadout entry" gap) — not as a
rendering substrate.

---

## 2 · The address algebra as the placement law (grounding the incoming theorem against live code)

The law, read directly from counterpart's `dna/address.json` (**Observed**, full file read this
session) and cross-confirmed in THE-GENERATIVE-LANGUAGE §1.7:

```
spans_not_points:  child k of n owns [(k-1)/n, k/n)  — a HALF-OPEN SPAN, never a point
derived_not_assigned: address = f(sibling count, position) — never stored, always re-derivable
start(child k of n within parent) = parent_start + (k-1)/n × parent_width
width(child of n within parent)   = parent_width / n
nested example: zone 3-of-5 inside slide 2-of-3 → 7/15 (one decodable number; radices known → decodes back)
```

**What this concretely requires in each candidate substrate — the mechanical fit, not a wish:**

**In DiagramSolver's `glyphgraph` case (1a):** the `authored` branch is *already* this exact algebra,
just not named as such: `x = 30 + nd.x·(VB-60)` where `nd.x ∈ [0,1]` **is** a span-normalised
coordinate (**Observed** `:68-71`). The gap is that the **DAG-layering fallback** (no authored coords)
does NOT derive its slot index from an address — it derives it from **array position** (`nodes.forEach`
order, `:92`). To make the stable-slot law a real instance of `derived_not_assigned`, slot index `ci`
must become `ci = f(node's address within its rank)`, e.g. a node's address = `rank/nR` (row span) ×
`slot/rowSize` (column span) — a **two-level nested fraction, exactly the `zone 3-of-5 inside slide
2-of-3` example**, decoded to one number for stable sort-and-diff. **Your-idea:** this turns "stable
slot" from an accidental property of array order into a *guaranteed* property of the address, which
is what survives node insertion/deletion/reorder — the actual live-growth requirement ANCHOR §4 names
as unsolved ("layout-jump on live growth").

**In canvas.css's world-pan model (1b):** the address algebra maps directly onto `--x/--y` as **world
px = span-fraction × world-extent**, i.e. the same `start()`/`width()` formulas but with `parent_width`
being the *world's* logical extent (chosen, not the viewport) rather than a 320-unit viewBox. This
substrate's only missing piece is *an engine* — the coordinate model it already declares is the correct
shape to receive addressed positions.

**In `canvas/app`'s tldraw substrate (1d):** this is the substrate where the algebra would do the LEAST
work, because tldraw already owns free Cartesian placement and the backend already computes
`n.position` server-side. The value the address algebra adds here is **not initial placement but
STABLE incremental placement under growth** — exactly DiagramSolver's problem, solved the same way:
when the backend adds a new node to a rank/row, its addressed span (not its array index) determines
where it lands, so a re-fetch never reflows siblings. Since positions are already backend-authoritative
(1d's core law), this is a **backend Python change** (wherever `n.position` is computed — not located
in this territory's grep scope, flagged for the backend/glyph-compose seat), not a frontend one.

**In system-map.html's sunburst (1c):** the address algebra is arguably the CLOSEST existing thing to
what the sunburst already does by construction — `node(id,a0,a1,depth)` partitions an angular span
`[a0,a1)` per child exactly like `[(k-1)/n, k/n)` (**Observed** `:539`, the function signature itself
names `a0,a1` as a span). This substrate is already, structurally, running the address algebra in
polar coordinates without naming it as such. **This is the single strongest piece of evidence that the
address algebra is not a new invention but a generalisation already latent in two different places in
the corpus** (DiagramSolver's `nd.x∈[0,1]` and system-map's `a0,a1` angular span) — the theorem's job
is to **name and unify**, not invent from nothing.

---

## 3 · Fields-on-canvas (warmth/ordinal/density gradients) — unbuilt anywhere, the mechanism sketch

**Ground truth on what pieces exist, verified first-hand:**
- **claude-ds's CV_AXES `color` axis** (1c... rather 1a's home) is a flat, ungrouped-by-gradient token
  list (`gold/gold-deep/gold-soft/bronze/bronze-2/tan` + semantic/ink/communication/neutral groups —
  **Observed** `axes/color/color-axis.js:26-58`). It has **no ordinal/ramp semantics built in** — it
  is a *palette*, not a *gradient function*. There is no `warmth(t)` or `ordinal(i,n)` resolver
  anywhere in `axes/`.
- **The zone-depth wash formula** (`AREA-21 §B1`, `core/containers.css:76-92`,
  `mix(pigment, ground, depth·2.1%·intensity)`) IS a real, working, recursive gradient function — just
  keyed on **containment depth**, not on temporal/attention order. This is the closest existing
  *mechanism* (a `color-mix` percentage driven by an integer) to what an ordinal ramp needs.
- **counterpart's `dna/motion.json` `ordinal_axis_as_time`** (**Observed**, verbatim): *"the metal axis
  encodes TEMPORAL DISTANCE: gold = now/near, bronze = later/far"* and `dna/grammar.json:327-332`'s
  `ordinal_axis` invariant: *"ordinal colouring holds to ~7 items; beyond that, CHUNK into groups
  first"* with a build-enforced monotonicity checker (`grammar4_note`: "ordinal guards are BUILD-
  ENFORCED in factory/build.mjs"). **This is a fully-specified, ALREADY-BUILT-in-counterpart law with
  an enforcement mechanism** — it has simply never been ported into claude-ds's `CV_AXES`, and never
  touched a canvas (it exists only for static deck pages today).
- **The Company's `runtime/scale.py`** is a *different* multi-scale mechanism — semantic clustering
  (Ward/kmeans-hybrid dendrograms over embedding vectors, coarsening by meaning-similarity, not by
  visual gradient) for the 76k-unit corpus zoom. **Observed** in full (the file's own docstring is
  explicit that this reversed an earlier lineage-pyramid plan because "capture-batch is not a semantic
  nest"). This is NOT a warmth/ordinal gradient mechanism — it is a resolution-by-clustering mechanism.
  **The two must not be conflated**: `scale.py` answers "which points resolve at this zoom," the
  ordinal-ramp answers "which colour tells you where in the telling's order you are." They compose
  (a coarse cluster centroid could ALSO carry an ordinal-ramp tint by its position in the walk) but are
  different axes.

**The mechanism sketch (Your-idea, built from the three pieces above, none invented):**
1. **Register a `warmth` axis in `CV_AXES`**, mirroring `depth-axis.js`'s shape exactly: values
   `far..near` (or `bronze..gold`), each carrying `meta.t: 0..1` (a normalised ordinal position) and
   `resolve(t)` returning the SAME `color-mix(in oklch, gold t%, bronze)` formula the zone-depth wash
   already proves works theme-invariant. Port counterpart's monotonicity + max-7-then-chunk invariant
   as the axis's own `candidates()`/validation, reusing the "checker: build" classification
   (THE-GENERATIVE-LANGUAGE §1.10) counterpart already assigns it.
2. **Drive `t` from the node's address**, not an authored literal: `t = 1 − (node's position in the
   conversation's growth order) / (total nodes so far)` — i.e. the SAME span-fraction the placement
   algebra computes (§2), reused as a colour input instead of a position input. This is the "everything
   flows both ways" law (§1.18) made concrete: one address, two projections (where AND how-warm).
3. **On canvas**, this renders as a per-node fill-tint (DiagramSolver's `TONE_FILL`/`RAMP` already have
   the `color-mix` plumbing — **Observed** `DiagramSolver.jsx:146-152` — it is genuinely one property
   away from being ordinal-driven instead of hand-set `tone` strings) or, on the world-pan scaffold, as
   a background field gradient behind the node layer (a new `.spatial-world` sub-layer, analogous to
   `.spatial-edges`).
4. **Density gradient** (the "almost imperceptible zones give direction too" line, THE-GENERATIVE-
   LANGUAGE §5.5) is the SAME zone-depth wash mechanism (`AREA-21 §B1`) applied to a canvas region
   instead of a nested DOM containment tree — i.e. `--zone-depth` set not by DOM nesting but by
   **graph distance from the active/focal node** (a BFS depth over edges). No new formula needed, a
   new *input* to the existing formula.

**Honest cost:** none of this exists today. It requires (a) one new `CV_AXES` axis (small, same shape
as four existing ones), (b) porting counterpart's ordinal invariant + its build-enforced checker
(medium — a new lint pass), (c) wiring the axis's `t` from an address in whichever renderer wins
(small in DiagramSolver, larger in canvas/app since positions are backend-owned so the tint math would
need to live backend-side too, to stay "reflects-never-owns" consistent).

---

## 4 · LOD / zoom-as-scale — what the renderer needs, reconciling TWO DIFFERENT ZOOM LAWS

This territory contains **two genuinely different "zoom" concepts that the ANCHOR's phrasing risks
conflating**, and the assessment must not blur them:

**(A) Content LOD (claude-ds, static/paged)** — `summary|pitch|full`, a **per-node prune/grow** driven
by `priority`/`detail` flags on the CVNode tree, **orthogonal to surface/viewport** (`cv-nodes.d.ts:10-17`,
AREA-21 §C2). This answers "how much of THIS node's content shows," independent of camera position.
Confirmed complete/stable across 7 analysed source folders (`mid-lod.md` — no new structure found,
"ready to move analysis → synthesis"). **This LOD ladder is not a zoom-camera concept at all** — it is
a content-detail dial that could be set by a slider, a surface type, or a reading-frame, with no
camera involved.

**(B) The scale pyramid (`runtime/scale.py`, Company-side, the 76k-unit-scale answer)** — a **real
semantic-zoom renderer input**: Ward/kmeans dendrogram cuts produce cluster centroids at descending K,
persisted as queryable vectors (`scale:<space>:k<K>`), so "zooming out" queries a coarser rung and gets
back fewer, larger meaning-regions instead of individual units (**Observed**, full file). This is
architecturally the CORRECT mechanism for "zoom changes which rung resolves" at corpus scale — but it
answers **which points exist at this zoom**, not **how those points are laid out on screen**. It has
no renderer-facing coordinate output at all (`rung_points()` returns `{source, vector, size, exemplar,
members}` — a list of centroids, not `{x,y}` — **Observed**, `rung_points` function body).

**What the renderer needs from these two, concretely:**
1. From (A): a `lod` dial the block solver already threads (`ContainmentTree`) — **irrelevant to the
   canvas substrates** in this territory except insofar as a glyphic node's OWN internal detail
   (its facet count, its label length) should also prune/grow with camera zoom. **This is currently
   missing on ALL FOUR canvas substrates** — none of DiagramSolver/canvas.css/system-map/tldraw thread
   a content-LOD signal into node rendering; tldraw's `zoom > 0.5` threshold (1d) is the only zoom-driven
   render change anywhere, and it's a binary show/hide of the WHOLE card body, not a graded LOD.
2. From (B): a **projection step that does not exist yet** — something must turn `rung_points()`'s
   `{source, vector, size}` list into screen coordinates. None of the four substrates has this wired.
   The natural fit is the **world-pan scaffold (1b)**, because it is the only one of the four designed
   for "infinite" content at varying zoom (the other three are bounded-viewBox or bounded-tree). But
   1b has no engine. **This is the actual missing piece for 76k-unit-scale**, not a renderer choice
   among the four — a *fifth thing*, a projection function `clusterCentroid → {x,y}` (likely reusing
   the "lattice" projection already partially built: `canvas/app/src/regions/LatticeView.tsx` exists
   and is wired into `App.tsx:56,226,244-248` as "the universal projection — the stores as points: kind
   =angle, time=radius from now" — **Observed**, this is a DIFFERENT existing projection (angle=kind,
   radius=time) that could plausibly be extended or forked for the semantic-cluster case, rather than
   built from zero. Flagging this as a concrete reuse candidate, not confirmed to fit — its projection
   law (kind/time) is not the same as scale.py's (meaning-distance/cluster-size), so it would need a
   real adaptation, not a drop-in.

---

## 5 · The one-IR law — cv-nodes.d.ts drift, checked directly

**Observed**, full file read. Findings against the ANCHOR's specific question:
- **`glyphgraph` is NOT in the `CVGraphType` union** (`cv-nodes.d.ts:70-72` lists
  `network|hub|morph|pipeline|timeline|quadrant|tree|compare|stack|stepper` — no `glyphgraph`), **but
  `DiagramSolver.jsx` has a full, working `case "glyphgraph":`** branch (`:63-120`) and a dedicated
  `glyphGraphView()` renderer (`:299-371`) that is dispatched BEFORE the type file's declared union is
  even consulted (`DiagramSolver` function body checks `graph.type === "glyphgraph"` directly, `:388`).
  **This is real, confirmed type-drift**: the implementation outran the declared IR. A TypeScript
  consumer of `cv-nodes.d.ts` today would not know `glyphgraph` is a legal `type` value.
- **Edge facets are thin in the .d.ts vs. what the renderer actually consumes.** `CVGraphEdge` declares
  only `{from, to, kind?, label?}` (`:87-93`, four fields) — but `glyphGraphView()`'s edge rendering
  reads `e.line`, `e.direction`, `e.routing`, `e.lineColor` (**Observed** `DiagramSolver.jsx:316-326`,
  all four consumed with no fallback-to-undefined guard beyond the code's own `||` defaults). **These
  four edge facets exist in the code and NOT in the type file** — a second, more granular instance of
  the same drift. The "edges are a visual language, not text labels" law (§1's root: "meaning is a
  field, not a lookup") is *implemented* in the renderer but *not declared* in the one-IR the ANCHOR
  names as authoritative.
- **`CVGraphNode` also lacks the fields the glyphgraph renderer needs**: no `icon` conflict (icon IS
  declared, `:81`), but no way to declare a node's full glyphic facet-set (colour/form/fill/texture
  beyond `shape`) — the glyphgraph renderer instead reaches for a full external object
  (`GL.render(nd, {size})` where `GL = window.CV_GLYPHIC`, **Observed** `:361`) and treats the CVGraphNode
  as barely more than an id-carrier for that call. **The one-IR is honoured in spirit (one graph
  spec drives all render paths) but the .d.ts is a stale, partial projection of what the actual glyphic
  node needs to carry.**

**Verdict:** the one-IR law (§1.6/ANCHOR) is real as an *architectural intent* and mostly honoured in
practice (nothing forks a parallel graph model), but `cv-nodes.d.ts` needs a same-day fix
(`glyphgraph` added to `CVGraphType`, the four missing edge facets added to `CVGraphEdge`) before any
new substrate consumes it, or the drift compounds.

---

## 6 · The mechanical-fit matrix

| Need | DiagramSolver (1a) | canvas.css scaffold (1b) | system-map.html (1c) | canvas/app tldraw (1d) |
|---|---|---|---|---|
| **Addressed coords** | partial (authored-branch only) | declared, unbuilt | partial (arc, not string address) | yes — `run://` instance address, richest |
| **Stable-slot / no-reflow-on-growth** | built, array-order-keyed (not address-keyed) | n/a (no engine) | n/a (tree edit, not incremental add) | no (backend `n.position` static per-node; growth-stability is a backend concern, untested here) |
| **Live update (SSE/poll)** | none — static prop render | none | poll-on-Rescan (`fetchModel` on button/poll) | **SSE, gapless resume — only real one** |
| **Drag / two-way edit** | none | designed (`.dragging` class exists) but no JS | **yes — full op-queue, undo/redo, disk-write-back** | **yes — drag=move, drag=connect, both API-backed** |
| **Semantic zoom (LOD)** | none | none | none (aspect-fit only) | one threshold (`zoom>0.5`) — real but binary |
| **Infinite pan/zoom** | no (fixed 320 viewBox) | **designed for this**, unbuilt | polar/radial, bounded to tree extent | yes (tldraw's native camera) |
| **Fields/gradients** | plumbing present (`TONE_FILL`, `color-mix`) unused for ordinal | none | none | none |
| **Edge visual grammar** (line=mood, colour=state, routing) | **yes — the most complete**, glyphGraphView | declared vocabulary (branch/ghost) no rendering | flat lines only | port-anchored bezier, status-agnostic styling |
| **Bundle/CSP cost of adopting** | zero (already in claude-ds bundle) | zero (CSS only) | zero (already static, self-contained) | tldraw ~200KB+, already paid in `canvas/app`, would be a NEW cost if pulled into claude-ds |
| **Cross-repo reach** | claude-ds only | claude-ds only | claude-ds only, repo-tree-shaped data | Company only, `run://` addressed, SSE-live |
| **Scale proven at** | ~10 nodes (glyphgraph render-shrink kicks in >6) | untested (no engine) | hundreds (real repo) | tens of graph nodes (operator canvas), not stress-tested to 76k |

**Reading the matrix:** no single substrate wins outright, and the ANCHOR's own hard-parts list
(§4) already anticipated this ("this seat = glyph/meaning stack + edge visual grammar + compose
pipeline; ④ = organs + query-feed"). The evidence supports a **split by scale regime, not a single
renderer choice**:

- **Conversation-scale glyphgraph (~10-40 nodes, the writer's actual current use):** DiagramSolver's
  `glyphGraphView` is already the most complete edge-grammar renderer that exists — it should be KEPT
  and extended with (a) address-derived stable slots (§2), (b) the ordinal/warmth axis (§3), (c) the
  `.d.ts` fix (§5). It does not need tldraw's weight for this scale, and pulling tldraw into claude-ds
  would violate the "one bundle, no parallel heavy dependency" instinct (not a stated law, but the
  CSP/bundle discipline `design/_system/check.py` enforces generally).
- **Operator-canvas scale (the live, editable, backend-driven graph — tens of nodes with real state):**
  `canvas/app`'s tldraw substrate is already the right tool and already does the hard 20% (SSE,
  two-way, addressed, backend-authoritative) that DiagramSolver has none of. If the glyphic instrument
  ever needs to be *placed on the operator's own canvas* (not just the writer page), it should render
  AS a tldraw shape (a third `ShapeUtil`, following `ForagerShapeUtil`'s precedent of a second
  co-existing shape vocabulary) rather than porting DiagramSolver's SVG math into tldraw.
- **76k-unit corpus scale (the ④-owned query-feed territory):** none of the four fit today. The
  world-pan scaffold (1b) is the correct *coordinate shape* to receive `scale.py`'s cluster centroids,
  but needs an actual pan/zoom engine (still nobody's built it) and a projection function from
  meaning-distance to `{x,y}` — `LatticeView.tsx`'s angle/radius projection is the nearest existing
  reuse candidate but is NOT a drop-in (different projection law). **This is ④'s territory per the
  ANCHOR's own ownership split** — flagged here for cross-reference, not solved here.
- **The repo/module tree (system-map.html):** already working, already at real scale, orthogonal to
  the glyphic instrument entirely (it visualises files, not meanings) — no action needed from this
  seat, but its **op-queue → adapter → rescan pattern is the one PROVEN two-way-edit precedent in the
  whole corpus** and should be studied by whoever builds write-back for the glyphgraph writer (the
  ANCHOR's own gap #9: "reindex-after-save has no bridge route").

---

## 7 · Citizenship gaps, named per the three-lens rubric

For "the glyphgraph, live and co-edited, on a real canvas" specifically:

- **Addressed** — the DiagramSolver's authored-branch is real but only when `nd.x/nd.y` are
  hand-supplied; the DAG-fallback and every other substrate lack a resolvable per-node address at all.
  **Missing furniture:** a `glyph://` or `graph://` instance-address scheme (parallel to `run://` which
  1d already proves works) so a glyphgraph node is clickable/citable from outside its own render.
- **Typed** — the `.d.ts` drift (§5) means the glyphgraph is typed in *practice* (the renderer enforces
  a shape) but not in the *declared contract* other tooling would read. Fix is small and concrete.
- **Derived** — strong where the axis discipline is followed (edge colour via `CV_MEANING.field`,
  **Observed** `:321-325`, throws on unknown — real loud-fail); weak where slot position is array-order
  not address-order (§2).
- **Wearing the DNA** — the glyphgraph renderer is genuinely composed from the real registries
  (`CV_GLYPHIC`, `CV_SHAPES`, `CV_MEANING`, `CV_EDGES` — all `window.*` singletons resolved at render
  time, not copied). This is the healthiest citizenship dimension of the four.
- **Two-way** — the weakest dimension across every claude-ds substrate: none can take a drag and write
  an authored override back to `nd.x/nd.y`. Only `canvas/app` (a different substrate) has two-way at
  all, and it doesn't speak glyphic yet.
- **Frame-resolved** — none of the four resolve to "the reader's coordinate" in the RHM/altitude sense
  (THE-GENERATIVE-LANGUAGE §1.8's reader-frame law); all render one fixed frame per call.

**The 80% diagnosis (§1.11, "frames without furniture") applies here exactly as REGROUNDING §3.4
predicted for the writer generally:** DiagramSolver's glyphgraph is a graph of bare positioned glyphics
with no zone/atmosphere layer under it, no field gradient, no evidence-density scaling — the same gap
named for the writer's overall page, present again one level down at the canvas-node level.

---

## 8 · What must fuse (the concrete order)

1. **Fix `cv-nodes.d.ts` first** (§5) — cheap, unblocks everything else declaring against the IR
   truthfully. Add `glyphgraph` to `CVGraphType`; add `line/direction/routing/lineColor` to
   `CVGraphEdge`; consider whether `CVGraphNode` needs a `facets?` passthrough for the full glyphic
   spec rather than routing around the type via `GL.render(nd,...)`.
2. **Derive DiagramSolver's stable-slot index from an address, not array order** (§2) — the concrete,
   scoped fix for ANCHOR §4's "layout-jump on live growth," reusing the exact `dna/address.json`
   arithmetic already proven in counterpart and already half-present in the `nd.x∈[0,1]` authored branch.
3. **Register the ordinal/warmth axis in `CV_AXES`** (§3), porting counterpart's already-built
   monotonicity + max-7-chunk invariant rather than re-deriving it — this is adopt-the-laws-bring-your-
   faces (canon.json's own merge instruction) applied concretely.
4. **Decide the glyphgraph's home is DiagramSolver for writer-scale, and a new tldraw ShapeUtil for
   operator-canvas-scale** — not a rewrite of one into the other, a genuine both/and matching the two
   real scale regimes found (§6), with the `.d.ts` (fixed per #1) as the shared contract between them.
5. **Leave the 76k-unit projection to ④** per the existing ownership split, but hand them this finding:
   `LatticeView.tsx`'s angle/radius projection is the nearest reusable pattern, not a fit as-is, and
   `canvas.css`'s world-pan scaffold is the correct coordinate shape waiting for exactly this engine.

---

### 3-line summary
Reactflow does not exist in this codebase at all (confirmed by grep, zero hits including
node_modules) — the real finding is four already-existing, non-competing projections of one CVGraph IR
(DiagramSolver's closed-form SVG solver with a real but array-order-keyed stable-slot law, an unbuilt
CSS world-pan scaffold with a genuinely useful branch/ghost/memory vocabulary, a working at-scale
editable sunburst for the repo tree, and a live SSE-driven backend-owned tldraw operator canvas) that
should split by scale regime rather than be decided between, with the address-span algebra
(`dna/address.json`, already latent in both DiagramSolver's `nd.x∈[0,1]` and system-map's angular
`a0,a1`) as the concrete fix for incremental-growth stability, an ordinal/warmth axis
(already fully specified in counterpart, unported) as the fields-on-canvas mechanism, and a confirmed,
fixable type-drift in `cv-nodes.d.ts` (`glyphgraph` and four edge facets missing from the declared IR
despite being implemented and consumed) that should be closed before any new substrate builds on it.

Path: `/home/tim/company/build-prep/the-one-system/glyphic/assessment/AREA-D-canvas-spatial.md`
