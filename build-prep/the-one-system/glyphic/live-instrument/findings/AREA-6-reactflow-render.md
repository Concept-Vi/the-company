# AREA 6 — reactflow as the live interactive canvas + the realtime render pipeline

> Companion file for the live-instrument research wave (agent 6 of 7). My area: reactflow (xyflow)
> as the interactive canvas, and the realtime render pipeline that drives it from extract→resolve→place.
> Mark legend: **Observed (file:line)** = read directly · **Inferred** = pattern-matched, not run ·
> **External** = reactflow/xyflow docs or general prior-art · **My-idea** = my proposal, verify/replace.
> Expansion-ratio note: the single biggest thing I bring is **the canvas the anchor imagines is already
> built — on tldraw, not reactflow** (`canvas/app`). That doesn't kill the reactflow choice; it reframes
> the whole area as a *both/and* with a real decision to surface. Read §0 first.

---

## 0 · The headline (the "yes, but actually the code does X")

The anchor (§3, §4, §103) frames the interactive canvas as a *new* thing to build on **reactflow**,
distinct from the no-script SVG page. Three findings reframe that:

1. **A mature programmatic graph-instrument already exists — built on tldraw 3.13.1, not reactflow.**
   `canvas/app` (the "Operable surface", vite dev server :5173) is a working canvas where the **backend
   owns a graph** (`/api/graph`), a **custom shape renders each node**, the **store is driven
   programmatically** (update-or-create-or-prune from backend state), positions are **backend-owned**,
   and **edges are a reactive overlay**. This is *exactly* the pattern the anchor describes for the live
   instrument — already proven, just on a different library and a different graph (the run-graph / Suite,
   not the glyphgraph). **Observed** (`canvas/app/package.json`, `canvas/app/src/NodeShape.tsx`,
   `canvas/app/src/App.tsx:436`).

2. **reactflow / @xyflow / react-flow appears NOWHERE in either repo** (design system or Company) — not a
   dependency, not an import. **Observed** (grep across `~/company` `--include=*.tsx,*.ts,*.js`, zero
   hits; only the ANCHOR.md mentions it). So "Tim chose reactflow" is a *forward* choice, not an existing
   fact. It must be *introduced*, and the only place it can live is a vite app (see §4).

3. **The no-script page-face surface can NEVER run reactflow — by construction, not by accident.**
   `PAGE_CSP = "default-src 'none'; … style-src 'unsafe-inline'; …"` with **no `script-src`** and
   `connect-src` absent (→ `'none'`). **Observed** (`runtime/page_face.py:65`). No JS executes, no network
   call leaves a page. The interactive canvas is therefore a *categorically different surface* from the
   page-face — they cannot be the same artifact. (This confirms anchor §4/§68 with hard evidence.)

**Verdict I commit to** (per the both-plus-others law + advocates-verify-not-source): deliver the full
reactflow mapping below as the *assigned target*; surface tldraw/`canvas/app` as **first-class prior-art
+ a candidate host + a named reactflow-vs-tldraw decision** for the synthesis agent and Tim to settle. It
is not my place to overturn the reactflow choice — but it *is* my duty to bring the evidence that there's
already a working instrument of this exact shape, so the wave doesn't reinvent it.

---

## 1 · The three-surface boundary (the spine — answers (d))

This is my most airtight finding. There are **three distinct render surfaces**, and reactflow fits exactly
one. Conflating them is the trap.

| Surface | Where | Tech | Can run reactflow? | Evidence |
|---|---|---|---|---|
| **No-script page-face** | `:8774`, separate origin | Python-rendered HTML+CSS, strict CSP | **No — by construction** | `runtime/page_face.py:65` CSP `default-src 'none'`, no `script-src`; `runtime/page_render.py` is pure server-side HTML |
| **Studio Babel app** | `app/index.html` | React 18.3.1 UMD + Babel-standalone, all from **unpkg.com**, no bundler at runtime | **No (poor fit)** | `app/index.html:100–102` (unpkg UMD), `:108–125` (fetch+`Babel.transform`+`new Function` at runtime); `_ds_bundle.js` is compiled OUTPUT, "never hand-edit" (`CLAUDE.md §5`) |
| **Vite apps** | `canvas/app` :5173, `surface/app` :5174 | React 18.3.1 + Vite 6 + `@vitejs/plugin-react` + TypeScript | **Yes — trivially** | `canvas/app/package.json`, `surface/app/package.json` (both React ^18.3.1, vite ^6.0.7) |

### 1a · Why the no-script page can't and shouldn't
**Observed** (`runtime/page_face.py:9–24`): the CSP is a *load-bearing security mitigation* (separate
origin + no-script) standing in for not-yet-built auth. A page is a static design artifact (HTML+CSS).
**My-idea:** the live instrument's *output* could still get a page-face — e.g. snapshot a finished
glyphgraph to inline SVG (via `CV_GLYPHIC.render` server-side, no JS) and `attach_page` it (the dual-
surface idea, SYNTHESIS §Round-5). But the *interactive, live-mutating* canvas is never the page-face;
it's a scripted vite surface. These are complements, not the same thing.

### 1b · Why the Studio Babel app is a poor host for reactflow
**Observed** (`app/index.html:100–125`): React + ReactDOM + Babel load as UMD globals from unpkg; core
`.jsx` is fetched, `export`-stripped, `Babel.transform`'d, and `new Function`'d at runtime. There is **no
npm install step and no module bundler in the runtime path** — `_ds_bundle.js` is a *compiled* artifact
(`262144` bytes, dated, "stale mid-turn", `CLAUDE.md §5`). reactflow is an ESM npm package with its own
CSS and a Zustand store; shoehorning it into UMD-from-unpkg + Babel-standalone is hostile (you'd need a
UMD build off a CDN, version-pinned, and to wire its store by hand). **Inferred:** technically possible
via `unpkg.com/@xyflow/react/dist/umd/index.js`, but it violates "use existing resources / don't
reinvent" *against* the cleaner vite path — and the no-script-CSP discipline of the page surface makes a
CDN dependency philosophically off-brand. Don't host the live canvas here.

### 1c · Vite apps are reactflow's only real home
**Observed:** both `canvas/app` and `surface/app` are React 18.3.1 + Vite 6 — `npm i @xyflow/react` +
`import '@xyflow/react/dist/style.css'` is the entire integration cost. **External** (reactflow v12 is
distributed as `@xyflow/react`, ESM-first, React 18 peer). **The boundary detail that matters:** the
design system's render primitives (`CV_GLYPHIC`, `CV_SHAPES`, `CV_ICONS`, `CV_MEANING`, the axes) live as
**`window.*` browser globals loaded by `<script>` tags in the Studio app** (`app/index.html:136–151`) and
are **NOT imported by either vite app today** (grep: zero `CV_GLYPHIC`/`markSVG` hits in
`canvas/app/src` or `surface/app/src`). So putting reactflow in a vite app raises the real open question
of §3: *how does the glyph compositor reach the vite bundle?*

---

## 2 · The prior-art that reframes everything: `canvas/app` on tldraw (answers (a)(b)(c)(e) by precedent)

`canvas/app` is the closest thing in the codebase to "the live instrument" — and it's worth reading in
full because **every sub-question in my brief already has a working answer there**, just expressed in
tldraw's API instead of reactflow's. The two libraries map almost 1:1.

### 2a · Custom node = a tldraw `ShapeUtil` (the reactflow analogue is a custom node component)
**Observed** (`canvas/app/src/NodeShape.tsx:30–184`): `class NodeShapeUtil extends ShapeUtil<NodeShape>`
with `static type = 'node'`, a typed `props` schema, `getGeometry`, and a `component(shape)` method that
returns the node's React/HTML body inside `<HTMLContainer>`. The body is **render-from-data** — it reads
`shape.props` and the registry store; there is **one generic node kind** for all node types.

> The load-bearing quote (`NodeShape.tsx:52–53`): *"ports come from the registry (OINFO), so a new
> node-type gets nubs with zero per-type code."* — This is the governing law (§5 of the anchor:
> "NO per-type render branch") **already realized** in the existing instrument. It is the proof-of-
> concept that a single generic node, driven purely by data, scales without branching.

The reactflow equivalent (**External**, verified from xyflow v12 docs):
```jsx
// ONE generic custom node — type maps in nodeTypes, body renders from `data`
function GlyphicNode({ data }) {           // NodeProps: { id, data, selected, … }
  return (
    <div className="cv-rf-node">
      <Handle type="target" position={Position.Left} />
      <span dangerouslySetInnerHTML={{ __html: data.glyphSvg }} />  {/* CV_GLYPHIC output */}
      <Handle type="source" position={Position.Right} />
    </div>
  );
}
const nodeTypes = { glyphic: GlyphicNode };   // ONE entry, defined outside the component
<ReactFlow nodeTypes={nodeTypes} nodes={nodes} edges={edges} />
```
**External** (reactflow.dev/learn/customization/custom-nodes): custom node receives `NodeProps`
(`data`, `id`, `selected`…); `data` carries the payload; you render any HTML/SVG inside; `<Handle
type="source"|"target">` are the connection points. `nodeTypes` is defined *outside* the component (or
memoized) — re-creating it each render is the classic reactflow footgun.

### 2b · Custom edge = the reactflow `edgeTypes` / `BaseEdge` analogue
**Observed** (`canvas/app/src/NodeShape.tsx:243–278`, the `Edges` overlay): tldraw doesn't have a
first-class edge type, so `canvas/app` draws edges as a **separate reactive SVG overlay** in screen-space,
recomputed from camera+zoom, anchoring each wire on its port's y-offset (`portTop`, `portY`). It's a hand-
rolled bezier (`d="M … C …"`). **This is a tldraw limitation reactflow does NOT have** — reactflow has
first-class edges with `edgeTypes`, `EdgeProps`, `BaseEdge`, and path helpers.

The reactflow equivalent for the **glyphic edge** (**External**):
```jsx
function GlyphicEdge({ id, sourceX, sourceY, targetX, targetY, data, markerEnd }) {
  const [edgePath, labelX, labelY] = getBezierPath({ sourceX, sourceY, targetX, targetY });
  return (
    <>
      <BaseEdge id={id} path={edgePath} markerEnd={markerEnd}
                style={{ stroke: data.lineColor, strokeDasharray: data.dash }} />
      <EdgeLabelRenderer>{data.label /* the relation verb */}</EdgeLabelRenderer>
    </>
  );
}
const edgeTypes = { glyphic: GlyphicEdge };
```
**My-idea + reuse:** the edge's facets (`line`, `lineColor`, `direction`, `kind`, the verb label) are
exactly what `CV_EDGES.resolve()` + `CV_MEANING.describeRelation()` already produce
(`cv-glyphics.js:composeRelation`, lines 307–341). The cleanest reactflow custom edge would **reuse
`CV_SHAPES.edgeSVG`** to render the connector body (textured line + arrow) rather than reactflow's plain
bezier — i.e. inject the `edgeSVG` string into a `<BaseEdge>`-less custom edge along a computed path, or
let reactflow draw the path and overlay the texture. This is the one place the reactflow default and the
glyphic vocabulary need reconciling. **Note (Observed, SYNTHESIS §Round-2b line 47):** `edge.label` is in
the `CVGraph` IR but NOT rendered by the existing `DiagramSolver` — a known gap reactflow's
`EdgeLabelRenderer` closes for free.

### 2c · Driving the store programmatically from the pipeline (answers (b))
**Observed** (`canvas/app/src/NodeShape.tsx:194–238`, `loadGraph` + `refresh`): the canonical pattern is
**update-or-create-or-prune** against backend state:
- existing shape → `updateShape` (incl. position from `n.position`)
- missing shape → `createShape` at `n.position`
- orphan shape (id gone from `g.nodes`) → `deleteShapes` (so delete doesn't leave a ghost)
- `zoomToFit` only when the page started empty (never on every mutation — that "wiped operator layout")

> Two load-bearing comments to carry into the reactflow design:
> - (`NodeShape.tsx:188–190`) *"The backend `n.position` is the SINGLE source of truth for layout — so we
>   never invent coordinates and never let tldraw's IndexedDB own the layout."*
> - (`NodeShape.tsx:192–194`) *"All store writes here are PROGRAMMATIC; the drag-listener filters to
>   source:'user', so these do NOT emit spurious /api/move calls (the write-back feedback-loop trap)."*

These are the two hardest-won lessons of a live-driven graph canvas, and they're **already paid for**.
The reactflow equivalent (**External**, verified):
```jsx
const { setNodes, setEdges } = useReactFlow();
// incremental delta from the pipeline (extract→resolve→place):
setNodes(prev => mergeById(prev, deltaNodes));   // update-or-create
setEdges(prev => mergeById(prev, deltaEdges));
// react to user drags WITHOUT clobbering pipeline state:
const onNodesChange = (changes) => setNodes(ns => applyNodeChanges(changes, ns));
```
**External** (reactflow.dev/learn/advanced-use/state-management): controlled flow uses `setNodes`/
`setEdges` + `onNodesChange`/`onEdgesChange`; `applyNodeChanges`/`applyEdgeChanges` apply position/
selection/deletion deltas; `useReactFlow()` exposes instance methods; `useNodesState`/`useEdgesState` are
the local-state convenience hooks; the internal store is Zustand (`useStore`/`useStoreApi`). The
canvas/app "filter to `source:'user'`" lesson maps directly: in reactflow, a *pipeline* update is a
`setNodes` write; a *user* drag is an `onNodesChange` event — keep the two paths distinct or you get the
write-back feedback loop.

### 2d · Realtime transport — what already exists (answers (b), the live half)
**Observed** (`canvas/app/src/api.ts:30–31`): `api.graph()` = `fetch('/api/graph')` (poll). **Observed**
(`canvas/app/src/App.tsx:306`): a *live `cognition.* SSE`* stream already feeds the canvas
(`/api/cognition_info` projection, "reflects-never-owns"). So the Company bridge **already speaks SSE to
this canvas**. **Inferred:** the live instrument needs *pushed graph-deltas* (new node / new edge / state
change) as the pipeline extracts them, not poll-on-interval. The natural fit is an SSE channel carrying
`{op:'add-node'|'add-edge'|'update', …}` deltas → the FE does `setNodes`/`setEdges`. **My-idea:** extend
the existing bridge SSE rather than invent a socket; the precedent (cognition SSE) is right there.
*(Areas 1/5 own the extract/voice transport; I flag the seam: the FE consumer is `setNodes` driven by an
SSE delta, and the bridge already does SSE.)*

### 2e · render-from-data, no per-type branch (answers (e) — the governing law)
The law (anchor §5): **NO per-type render branch.** Two data points:
- **The existing instrument honors it** (`NodeShape.tsx:52`, quoted above): one generic shape, ports from
  the registry, zero per-type code.
- **The existing glyph engine `DiagramSolver` PARTIALLY VIOLATES it** — **Observed**
  (`DiagramSolver.jsx:240–281`): a chain of `if (graph.type === 'stepper'|'orbital'|'stacked'|'spectrum'|
  'manifold'|'fidelity') return <view>(…)` plus a `switch(type)` in `layout()` (`:41–74`). These are
  *curated per-type layout formulas* — fine for a fixed deck vocabulary, but the **opposite** of what a
  live, open-ended glyphgraph needs. SYNTHESIS §Open ("DiagramSolver's closed-form layouts suit small
  structured graphs; a free meaning-graph may need force-directed / DAG") names this exactly.

**My-idea (the render-from-data design for reactflow):** the live glyphgraph canvas should have **exactly
one `nodeTypes` entry (`glyphic`) and one or two `edgeTypes` entries (`glyphic` relation edge)**. The node
body is `CV_GLYPHIC.render(spec)` output — the *facet-spec is the data*, and form/fill/colour/symbol all
resolve inside `CV_GLYPHIC.compose` from single sources. There is no `if (node.kind === …)` branch on the
render path: a new entity type that resolves to a new `form`/`symbol` just *renders*, because the glyph
compositor already resolves it from the facet space (`cv-glyphics.js:232–284`). This is the **glyphgraph
layout case** SYNTHESIS §Round-2b asked DiagramSolver to grow — but reactflow lets you skip the per-type
formula entirely and use a generic layout engine (§3c). The per-type branch dies; the data drives.

---

## 3 · The real open question in my area: how does CV_GLYPHIC reach the vite bundle?

This is the meatiest unanswered thing, and the wave should decide it explicitly. **Observed:** the cv-*.js
chain is browser globals loaded by `<script>` in the Studio app with a strict load order
(`app/index.html:136–151`: `cv-icons → cv-vi-glyph → cv-shapes → cv-edges → axes → cv-meaning →
cv-glyphics`); the vite apps don't touch them. Two forks:

### Fork A — browser-composes (the vite app imports the compositor)
The vite app pulls the cv-*.js chain in (as side-effecting global scripts, or repackaged as ESM) → the
custom node calls `CV_GLYPHIC.render(spec)` → injects via `dangerouslySetInnerHTML`.
- **Pro:** the FE holds the live compositor; re-render on facet change is instant, no round-trip.
- **Con (Observed):** the chain is **window-global + load-order-sensitive + non-ESM** (IIFE `(function(){
  … window.CV_GLYPHIC = … })()`, `cv-glyphics.js:21,355`). Vite ESM doesn't guarantee global-script order
  the way the Studio's hand-ordered `<script>` tags do; you'd import them for side-effects in the right
  sequence (`import '../../assets/icons/cv-icons.js'` …) or wrap them as modules. The axes (`CV_AXES`)
  and `CV_MEANING` are *also* required for full facet resolution (motion/colour value→token), so the
  whole stack has to come along. **Inferred:** doable but it imports a chunk of the design system into the
  Company's FE — a coupling decision.

### Fork B — server-composes (the pipeline pushes ready SVG strings)
The extract→resolve pipeline composes the glyph **server-side** (a Python or node port of `CV_GLYPHIC.compose`,
or by calling the design-system render headlessly) and pushes a **ready SVG string** as the node's `data.glyphSvg`.
The custom node is then trivial — it just injects the string.
- **Pro (Observed precedent):** this is the **shape `canvas/app` already uses** — the backend is the single
  source of truth (`n.position`, node `status`/`output`), the FE "never invents" and "reflects-never-owns"
  (`NodeShape.tsx:188`, `App.tsx:306`). A glyph SVG is just another reflected field, like `output`.
- **Pro:** keeps the heavy compositor + registries server-side (where the local models, embedder, and
  icon foundry already live — anchor §7); the FE stays thin.
- **Con:** a facet tweak needs a round-trip to re-compose (but the pipeline is the author here, so that's
  the normal path anyway); and it requires `CV_GLYPHIC.compose` to be runnable server-side. **Observed:**
  `CV_GLYPHIC.compose` is pure-ish JS that delegates to `CV_SHAPES.markSVG` (also pure string-building,
  `cv-shapes.js:203`) — it has no DOM dependency, so it could run under node headless, OR the design-system
  could expose a headless render endpoint. (SYNTHESIS verified `CV_GLYPHIC.compose` headless already.)

**My recommendation (tentative, for synthesis to weigh):** **Fork B as the spine, Fork A optional later.**
It honors the established backend-owns-truth precedent (the canvas/app law), keeps the registries and
models co-located server-side (anchor §67: "the local models are server-side"), and makes the FE a thin
reflector — the lowest-coupling, most no-staleness-aligned path (the glyph is *resolved from the single
source server-side*, the FE never holds a second copy of the compositor logic). The cost — a round-trip to
re-compose — is a non-issue when the pipeline is the author. Fork A becomes attractive only if direct FE
manipulation (drag-to-change-a-facet) becomes a first-class interaction.

---

## 4 · Where reactflow physically lives (answers (d), the host question)

**Observed:** `canvas/app` is **already tldraw** — putting reactflow *in the same app* means two canvas
libraries in one bundle (odd, heavy, two competing camera/store models). So the host candidates are:

- **`surface/app`** (:5174, "the fresh paper-aesthetic instrument surface … built alongside canvas/app,
  never on top" — `surface/app/package.json` description). **Observed:** React 18.3.1 + Vite 6 +
  framer-motion, with `board/`, `wheel/Nucleation.tsx`, `transcript/`, `channels/` — a *fresh* instrument
  surface with **no canvas/graph lib yet**. This is the cleanest reactflow home: a new app explicitly
  meant to be the instrument, not encumbered by tldraw. **My-idea:** the live glyphgraph canvas is a new
  region in `surface/app` (e.g. `surface/app/src/glyphgraph/GlyphGraphCanvas.tsx`).
- **A new dedicated vite app** (e.g. `glyphgraph/app`) — if the live instrument warrants its own surface.
  Same React/Vite/reactflow stack. Heavier (a third FE app) but maximal isolation.

**Inferred:** `surface/app` is the intended-host signal (its own description positions it as "the
instrument surface"). The tldraw-vs-reactflow decision and the host decision are coupled: if Tim wants the
*freeform whiteboard feel* (anchor §103), `canvas/app`'s tldraw is the precedent and reactflow's
structured node/edge model fights it; if he wants the *structured graph that mirrors a glyphgraph's typed
nodes + typed edges*, reactflow is the better fit and `surface/app` is the home.

### reactflow-vs-tldraw, laid out (no winner declared — for synthesis/Tim)
| Axis | tldraw (`canvas/app`, exists) | reactflow (assigned, to introduce) |
|---|---|---|
| Feel | Freeform whiteboard, infinite canvas, hand-drawable | Structured node-graph; edges are first-class |
| Edges | Hand-rolled SVG overlay (`Edges`, screen-space) — **a gap they had to fill** | First-class `edgeTypes`/`BaseEdge`/`getBezierPath` + `EdgeLabelRenderer` |
| Glyphgraph fit | Node-as-shape works; edges are extra work | typed-nodes + typed-edges **mirrors the glyphgraph IR (`CVGraph`) 1:1** |
| Auto-layout | DIY (no built-in) | dagre/elk ecosystem + examples (§4c) |
| Already wired | **Yes** (mature, backend-driven, SSE) | **No** (zero presence in repo) |
| Glyph injection | `HTMLContainer` + inject string | custom node + `dangerouslySetInnerHTML` |
| render-from-data | Proven (`NodeShape.tsx:52`) | Native (`nodeTypes`/`data`) |

Both support HTML/SVG injection of a `CV_GLYPHIC.render` string, both support render-from-data, both can be
backend-driven. The discriminators are **feel** (whiteboard vs structured) and **edges + layout ecosystem**
(reactflow is stronger). The cost of reactflow is **introducing a second canvas paradigm** when a mature
tldraw instrument already exists — that's the real trade the wave must name.

### 4c · Auto-layout for stable incremental placement (answers (c))
**Observed (the stale caution):** SYNTHESIS §Open said *"No external lib without checking the CSP/bundle."*
That caution was about the **no-script page / Studio Babel** surfaces — **it vanishes in a vite app**:
`dagre` and `elkjs` are npm packages that install and bundle cleanly under Vite 6. So the "no external
lib" constraint does NOT bind reactflow's host.

**External** (reactflow.dev): the standard pattern is `getLayoutedElements(nodes, edges)` — feed the graph
to **dagre** (`@dagrejs/dagre`, fast, layered DAG) or **elkjs** (`elkjs`, richer constraints, slower) to
compute `{x,y}` per node, then `setNodes` with the laid-out positions. reactflow ships official examples
for both.

**The honest hard part (anchor §63): stable incremental placement.** A naive re-layout on every new node
makes the whole graph *jump* — the worst live-instrument experience. **My-idea (three options, for
synthesis):**
1. **Backend/pipeline owns position** (the canvas/app precedent — `NodeShape.tsx:188`, "n.position is the
   SINGLE source of truth"): the *place* step of the pipeline (anchor §3 AUTO-PLACE) computes a stable
   incremental position as each node arrives (e.g. append near its source node, nudge to avoid overlap),
   the FE reflects it. No client-side layout lib at all → maximally stable, and it matches the established
   law. **This is the lowest-risk path and it reuses the proven shape.**
2. **Pin-placed + dagre-on-demand:** newly-arrived nodes get a deterministic incremental slot; a manual /
   debounced "tidy" runs dagre over the whole graph only when the user asks (so it never jumps mid-speech).
3. **Incremental constraint layout (elk):** elk supports fixing existing node positions and only placing new
   ones — closest to "true" stable incremental, but the heaviest and least proven here.

**Recommendation (tentative):** **Option 1** for v1 — it's the established precedent, needs no lib, is
deterministically stable, and the pipeline already has to decide *where a thing relates* (placement-hints
are an extract concern, anchor §3). Reach for dagre/elk (Option 2) as a "tidy" affordance, not the live
path. This keeps `kind.graph`'s `layout` valueSlot (**Observed**, `kinds-type.js:50`:
`['force','tree','radial','flow','grid']`) honest — that enum already anticipates pluggable layouts; the
live default is "pipeline-placed," and dagre/elk fill `force`/`tree`.

> **Note (Observed, gap):** `kinds-type.js:50` declares a `force` layout value, but `DiagramSolver`
> implements no force layout (`DiagramSolver.jsx:41–74` has hub/network/pipeline/timeline/quadrant/tree/
> stack only). The enum over-promises vs the engine — a small drift to flag. reactflow + dagre/elk would
> actually deliver the `force`/`tree` values the registry already advertises.

---

## 5 · The no-staleness law across my area (anchor §5, §64 — the rigor area)

Where would hardcoding sneak into the render layer, and how the design holds it:
- **No per-type node branch** — ONE `nodeTypes.glyphic`, body = `CV_GLYPHIC.render(spec)`; form/fill/
  colour/symbol resolve from single sources inside `compose` (`cv-glyphics.js`). A new entity type that
  maps to a new form/symbol *just renders* — no `if (type===…)`. (Contrast the `DiagramSolver` per-type
  `if`-chain §2e — the live canvas must NOT copy that.)
- **No second edge vocabulary** — the custom edge's facets come from `CV_EDGES.resolve` + the relation's
  meaning via `CV_MEANING.describeRelation` (`composeRelation`, `cv-glyphics.js:307–341`); reactflow draws
  the path, but the *line texture / colour / direction / verb-label* resolve from the registries, never a
  reactflow-side style map. lineColor → token via `CV_MEANING.tokenForValue → COLOR_TOKENS` (the SAME path
  nodes use — `cv-glyphics.js:319–328`), never a parallel colour map.
- **No copied glyph logic in the FE** — Fork B (server-composes, §3) is the most staleness-proof: the FE
  holds *zero* compositor logic, just reflects a resolved SVG string. The glyph is resolved from its single
  source server-side; the FE can't drift because it has nothing to drift *from*.
- **Positions resolved, not invented** — the canvas/app law (`NodeShape.tsx:188`, "never invent
  coordinates"). The FE reflects backend/pipeline positions; layout is a *resolved* property, not a
  client-side free-for-all. This keeps placement deterministic + reproducible (a graph re-opens identically).
- **The trap to name loud:** reactflow *encourages* holding `nodes`/`edges` in React state and mutating
  client-side (the `useNodesState` convenience). If the live instrument lets the *client* own node/edge
  identity or position, that's a **second home** for the graph — drift from the backend truth. The
  discipline (per the canvas/app precedent): **the backend/pipeline owns the graph; reactflow reflects it**
  via `setNodes`/`setEdges`; user gestures round-trip through the API (`/api/move`-style) before they
  become truth. This is the single most important law for my area and it's already been learned once.

---

## 6 · The minimum real demo that proves "talk → live graph" (anchor §105, for my surface)

**My-idea (the render-side slice):** in `surface/app`, a `GlyphGraphCanvas` mounting `<ReactFlow>` with
one `nodeTypes.glyphic` + one `edgeTypes.glyphic`, subscribed to a bridge SSE delta stream. A scripted
sequence (no live STT needed for the render proof) pushes `add-node`/`add-edge` deltas with facet-specs +
server-composed glyph SVGs (Fork B); the canvas grows incrementally with pipeline-placed positions; edges
carry resolved verb-labels. This proves: (a) custom-node renders a real glyphic, (b) programmatic
incremental store-driving, (c) stable placement, (e) zero per-type branch — independent of the voice/
extract layers (areas 1/5), which then plug into the same SSE delta contract.

---

## 7 · Sources / what's Observed vs Inferred vs External
- **Observed (read directly):** `core/DiagramSolver.jsx` (full), `core/cv-nodes.d.ts`,
  `assets/icons/cv-glyphics.js` (full), `app/index.html`, `app/registry/kinds-type.js`,
  `assets/icons/cv-shapes.js:203–250` (markSVG), `runtime/page_render.py`, `runtime/page_face.py:1–90`,
  `canvas/app/package.json`, `surface/app/package.json`, `canvas/app/src/NodeShape.tsx` (full),
  `canvas/app/src/api.ts:1–60`, `canvas/app/src/App.tsx` (grep of mount + SSE), `ops/services.json`
  (canvas/pages services), SYNTHESIS.md (full), grep confirming reactflow absent from `~/company`.
- **External (verified live this session):** reactflow/xyflow v12 docs — custom nodes (`nodeTypes`,
  `NodeProps`, `data`, `Handle`), custom edges (`edgeTypes`, `EdgeProps`, `BaseEdge`, `getBezierPath`,
  `EdgeLabelRenderer`), state mgmt (`setNodes`/`setEdges`, `applyNodeChanges`/`applyEdgeChanges`,
  `useReactFlow`, `useNodesState`/`useEdgesState`, Zustand store), dagre/elk `getLayoutedElements`.
- **Inferred / My-idea:** all marked inline. The Fork B recommendation, the surface/app host pick, the
  three placement options, and the SSE-delta transport are *proposals* — verify against areas 1/5 (voice/
  extract) and let synthesis/Tim settle the reactflow-vs-tldraw + host decisions.

## 8 · The seams I hand to other areas
- **Areas 1/5 (voice/extract):** the FE consumer contract is `setNodes`/`setEdges` driven by a **bridge
  SSE delta stream** (`{op, node|edge}`); the bridge already does SSE to canvas/app — reuse it.
- **Resolve area:** node `data` = a **facet-spec** (`{form,symbol,fill,color,…}`) OR (Fork B) a
  pre-composed `glyphSvg` string; edge `data` = resolved edge facets + verb-label from
  `CV_EDGES`/`CV_MEANING`. The resolve step produces exactly what `cv-glyphics.js:composeRelation` consumes.
- **Synthesis:** the open decisions are (1) reactflow vs tldraw (and whether to reuse `canvas/app`'s
  proven backend-driven shape), (2) host = `surface/app` vs new app, (3) Fork A vs B for the compositor
  boundary, (4) placement = pipeline-owned (recommended) vs dagre/elk.
