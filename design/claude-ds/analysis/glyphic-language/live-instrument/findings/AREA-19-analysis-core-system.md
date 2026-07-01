# AREA-19 — analysis/ prior-decisions + core/ & system/ graph/render duplicates (WAVE-3 coverage+unification)

> Companion to ANCHOR.md. My charge (WAVE-3): read the UNREAD analysis/*.md (the unification/
> integration/system-map/requirements/axes/diagrams docs) + the remaining core/ (the graph IR + graph
> solver) + system/ (the foundry, the system-map graph surface) **through the lens of the conversational
> glyphgraph**, and catalogue what the prior areas did NOT extract: (a) prior DESIGN DECISIONS / GAPS /
> constraints the live layer must honour, (b) DUPLICATE/parallel render+graph approaches + their unique
> qualities + the FUSION direction, (c) what the synthesis must NOT contradict.
>
> **Lens discipline (Tim):** nothing here is final/canonical/done — I strip "already built." Where a
> thing exists in code I mark it **Observed (file:line)** as a *structural* fact, and separately flag
> whether it is **runtime/visually verified** (the project's own memory index records glyphic as
> "verified headless, not visually"). Duplications are EXPECTED — the value is the unique quality + the
> weld, not the discovery that a thing exists.

---

## 0 · TL;DR (the four things this area changes about the picture)

1. **The conversational glyphgraph already has a target IR and a render path in the engine — but only a
   STATIC one.** `core/cv-nodes.d.ts` defines `CVGraph {type, nodes, edges, axes, center, state}`
   (Observed, cv-nodes.d.ts:95–107); `core/DiagramSolver.jsx` has a **`"glyphgraph"` graph type**
   (Observed, DiagramSolver.jsx:63, :368) whose `glyphGraphView` renders **each node as a FULL glyphic
   via `CV_GLYPHIC.render`** and **each edge's meaning visually** via `CV_SHAPES.edgeSVG`, reading the
   relation out loud through `CV_MEANING.readGraph` into a `<title>` (Observed, DiagramSolver.jsx:279–351).
   This answers *"can a glyphic be a token-pure, CSP-safe, no-external-lib graph node that reads itself
   out"* — **yes, structurally** — but it does **NOT** answer the ANCHOR's hard parts: *stable
   incremental placement during a live conversation* and *an interactive (drag/pan/zoom) canvas*. The
   layout re-ranks on every render (see §3-A). **Not runtime/visually verified** in this read.

2. **The fusion direction is "incremental placer feeding the existing AUTHORED-x/y branch", not "rip
   it out for reactflow".** `glyphGraphView`'s `layout()` already has an **authored-coordinate branch**
   (`nodes.every(nd => nd.x!=null && nd.y!=null)` → honour frozen x/y; Observed DiagramSolver.jsx:68–72).
   The live pipeline can assign-and-FREEZE x/y per node *as it arrives* (the incremental placer the
   ANCHOR asks for), then drive `glyphGraphView` **unchanged** through that branch — reuse, not rewrite.

3. **Two existing precedents are the live layer's spine — and the synthesis must build INTO them, not
   beside them:** (i) the **editor-adapter op-queue** (`SYSTEM-MAP-EDITOR-ADAPTER.md`) — visual edits
   mutate an in-memory graph model + emit a **typed op queue** with one code path per op + a staleness
   guard; this is *exactly* the shape for "no, the buyer's gone cold" → a typed graph-mutation op.
   (ii) the **visual-encoding grammar** (`SYSTEM-MAP-ENCODING-GRAMMAR.md`) — `facet → channel` bindings
   single-sourced in `CV_MEANING.encodings` and **projected** into a graph canvas; this IS the
   data-field→visual-channel grammar the ANCHOR's RESOLVE step needs, already a registry.

4. **There is a real, named, recurring failure mode the synthesis is at high risk of repeating: the
   "fourth parallel strand."** `UNIFICATION.md §4` records, honestly, that `Slide`/`Archetypes` once
   shipped as a *fourth parallel render strand* instead of welding the existing three. **A reactflow
   surface that renders from its own node model instead of being a PROJECTION of the one `CVGraph` IR
   would be the fifth.** This is the single most important "must NOT contradict" (see §4).

---

## (a) PRIOR DESIGN DECISIONS / GAPS / CONSTRAINTS the live layer must honour

### A1 · The one-home / four-registry law is already load-bearing — the live layer is a FIFTH consumer, not a fifth registry
- **Observed (INTEGRATION.md:8–18, CLAUDE.md §1):** four single sources — **Tokens** (`styles.css`+`tokens/*`),
  **Types** (`CV_REGISTRY` + `core/archetype-catalog.js`), **Engine** (`core/` solvers on `cv-nodes.d.ts`),
  **AI** (`CV_AI`, `app/ai/*`) — all sharing one API shape (`register/resolve/lineage/query/subscribe`,
  layers + single-inheritance). AXIS-REFACTOR adds a fifth family, **CV_AXES** (the axis registries).
- **Constraint for the live layer:** the conversational glyphgraph's pieces each resolve FROM these,
  never duplicate them. The provider the ANCHOR wants to add (Company-local fleet) is **a `CV_AI`
  provider**, registered once (`CV_AI.register({layer:'provider'})`) — not a parallel client. The
  icon-on-miss is **`CV_AI.execute('glyphic.generate')` + `glyphic.save`** (already a capability — see
  the foundry, §B1). The graph nodes are **`CVGraph` nodes**. The placement/encoding is **`CV_MEANING.encodings`**.
  (This is also AREA-1/AREA-5's territory; I confirm it from the integration/unification docs as a *hard
  constraint inherited by the live layer*, not re-deriving the provider mechanics.)

### A2 · "Loud fail, never silent" is a stated law, and the engine ALREADY enforces it in the graph path
- **Observed (INTEGRATION.md:90–92, CLAUDE.md §3, UNIFICATION.md:88–92):** missing provider/runtime/
  capability/type/builder → `throw`; "silently returning `[]`/`null`/a fallback is not" acceptable.
  `RenderType`/`Slide`/`buildSlide`/`typeToNode`/`CoreTypes` all throw; the one async gate
  (`SurfaceSlideThumb` waiting on `window.__coreReady`) is **readiness, not a fallback**.
- **Observed in the graph path:** `glyphGraphView` **throws** if `CV_GLYPHIC`/`CV_SHAPES` are absent
  ("the glyphic + geometry single sources", DiagramSolver.jsx:283); the per-edge `lineColor` resolves
  through `CV_MEANING.field("lineColor", v)` which **"throws on unknown (loud-fail law)"**
  (DiagramSolver.jsx:301–302); the one place it *doesn't* throw — an edge-title read-out failure — is
  explicitly **`console.warn`, not a silent swallow** (DiagramSolver.jsx:316–319, comment cites
  "no-silent-failure law").
- **Constraint for the live layer:** the LISTEN→EXTRACT→RESOLVE→GENERATE-ON-MISS→PLACE→RENDER pipeline
  inherits this. A noun that resolves to no glyphic must **either** trigger the foundry **or** fail loud
  with a Notice — never drop the node, never render a placeholder shape. This matches the project memory
  rule *No Silent Failures Or Fallbacks*.
- **Aligns with ANCHOR §5 "GOVERNING LAW"** — and tells the synthesis the law is not aspirational here;
  the graph render *already* obeys it line-by-line, so the live layer must keep that bar.

### A3 · "No external layout lib in the CSP page-face" is an EVIDENCED prior decision (bears directly on reactflow)
- **Observed (DiagramSolver.jsx:66–67 comment):** for the `glyphgraph` layered fallback —
  *"No external layout lib (CSP/bundle) — closed-form, like the siblings."* Every layout in `layout()`
  is closed-form trig/ranking (DiagramSolver.jsx:30–115).
- **Inferred:** this is the code's answer to ANCHOR §6 "reactflow inside the no-script-CSP / bundle
  constraints" and ANCHOR open-what-if "reactflow right, or tldraw?". The page-face render (the static
  SVG glyphgraph, `runtime/page_render.py` per ANCHOR §7) deliberately carries **no JS layout dependency**.
- **Constraint / direction:** reactflow (a heavy JS canvas lib) is legitimate for the **interactive
  authoring surface** the ANCHOR describes (drag/pan/zoom, the "instrument"), but it must **not** become
  the page-face render, and whatever it lays out must round-trip to the **same `CVGraph` IR** that the
  closed-form SVG view consumes (so the static no-script render still works). See §4-C.

### A4 · The shared graph IR (`CVGraph`) — the live layer's actual target shape, with named gaps
- **Observed (cv-nodes.d.ts:69–107):** `CVGraphType = network|hub|morph|pipeline|timeline|quadrant|tree|
  compare|stack|stepper` (and `"glyphgraph"` is handled in the solver though not yet in this union type —
  a small drift to reconcile). `CVGraphNode {id,label,shape,tone,icon,x,y}`; `CVGraphEdge {from,to,kind,
  label}` with `kind = flow|dependency|reference|rejected`. The glyphgraph path extends edges at runtime
  with `line`, `direction`, `lineColor`, `routing` (DiagramSolver.jsx:296–298) — **these are NOT in the
  `.d.ts` yet** (a type-vs-runtime drift the synthesis should close).
- **GAP (Observed, HANDOFF.md:332):** *"The graph solver computes layout but not edge-routing/overlap-
  avoidance — fine for small diagrams, may need refinement for the dense 49pp-style graphs."* A live
  conversation builds an arbitrarily large graph → **overlap-avoidance is a real open problem the live
  layer must solve** (the incremental placer in §3-A is where it lands).
- **Constraint:** the live pipeline emits `CVGraph` (type `"glyphgraph"`), with per-node frozen `x/y`.
  Reconcile the `.d.ts` to include `"glyphgraph"` + the edge facets as part of the synthesis.

### A5 · The axis/no-staleness machinery is DEEPER than the ANCHOR knew — and carries DO-NOT-LOSE scope that overlaps the live layer
- **Observed (AXIS-REFACTOR.md:1–63, STATUS:107–151):** every visual axis (motion/colour/space/size/
  form/texture/depth/fill/symbol/meaning) is its own **typed registry** under a top-level **`CV_AXES`**,
  built + verified at slice 60; a component slot declares a **subscription** (`{axis, values?|groups?,
  default, conditions?}`) resolved live, never a copied value table. **Tokens ARE the value-units** of an
  axis (AXIS-REFACTOR.md:23–29). A **condition evaluator** `CV_COND` exists (slice 61).
- **DO-NOT-LOSE carried scope (Observed, AXIS-REFACTOR.md:86–98) that the live layer overlaps:**
  - *"Foundry conversational UI (propose → feedback → click → iterate → Save panel); capabilities
    `glyphic.generate`/`glyphic.save` + schema already built. Needs §7 value-vocab sign-off + live
    provider."* → **This is precisely the live layer's GENERATE-ON-MISS step.** It is flagged as
    *owed/unfinished* — so the live layer is not greenfield here; it adopts this open thread.
  - *"Event-sockets / addresses / conditions on sockets — declared in spec §05c … full condition engine
    not yet built"* and *"Slot/socket conditions generally … declared as strings; no evaluator yet"*
    (note: a `CV_COND` evaluator landed later at slice 61 — reconcile this status).
- **Constraint:** the live layer's "noun → glyphic" RESOLVE step is an **axis-subscription resolution**
  (form from type, fill/colour from state, symbol from `CV_ICONS`/Symbol-axis), not bespoke mapping
  code. The ANCHOR's "icon tags are a generative pass, not a typed list" is the **Symbol axis** +
  `CV_ICONS.facets` already.

### A6 · The block↔graph duality + the welded bridge — the live layer plugs in at the IR, after the weld
- **Observed (AXES.md:117–127, UNIFICATION.md:42–61, RenderType.jsx:1–16):** *"One type system, one rule
  engine, two layout solvers"* (block = flow/stacking, graph = relational). The weld is
  `typeToNode(type, data, axis)` → `CVNode`/`CVGraph` IR → solvers (`RenderType.jsx`). Confirmed
  signature: `CV_REGISTRY Type → typeToNode → CVNode/CVGraph IR → ContainmentTree/DiagramSolver`
  (RenderType.jsx:11; `blockToNode(key,d)` switch at RenderType.jsx:32–70 is the WS_BLOCKS→core weld).
- **Constraint/direction:** the live pipeline's output is a **`CVGraph` IR** (`kind:"diagram"` host node
  with `graph.type="glyphgraph"`). It enters the engine **at the IR**, *downstream* of the type→IR
  bridge — i.e. the live layer is a **second producer of the same IR** the bridge produces, and both
  feed the one solver. (A glyphgraph could itself be a registered Type whose `typeToNode` is "pass the
  CVGraph through" — worth designing so it is single-sourced like everything else.)

### A7 · The "computed, not hand-authored / vigilance against technical success" mandate
- **Observed (HANDOFF.md:27–42, REQUIREMENTS.md:8–22, AUDIT-INDEX.md:40–43):** the explicit mentality —
  *"the goal is the unified generative thing, NOT the fastest thing"*; *"a thing that compiles/renders/
  passes check is NOT necessarily right … is this computed from the rules, or did I just hand-set it?"*;
  *"the system was documented-deep but applied-flat."*
- **Constraint:** the live layer must resist the same flat read. A glyphgraph node's appearance is
  **computed from facets through the axes**, never hand-styled per node; placement is **computed**
  (incremental placer), never hand-dragged-into-a-pixel and persisted as a literal. (Dragging is fine as
  an *override* — but the override should land as a frozen x/y the placer respects, A4/§3-A, not as a
  bespoke style.)

---

## (b) DUPLICATE / PARALLEL render + graph approaches — unique qualities + FUSION direction

> Five distinct graph/render/authoring surfaces exist or are specified. Each has a unique quality the
> fusion should keep; together they say the live instrument is **mostly an assembly + an incremental
> placer + a voice front-end**, not a greenfield build.

### B1 · The Glyphic Foundry (`system/glyphic-foundry.html`) — the existing CONVERSATIONAL authoring UI
- **Observed (glyphic-foundry.html:106–242):** a two-pane conversational mark-foundry. You type a brief →
  Vi proposes N candidates → candidates **render live as glyphics** (`previewGlyphic` temp-registers the
  candidate svg in `CV_ICONS` `persist:false` then `CV_GLYPHIC.render`) → click to select / refine by
  talking / **Save** to the library. Generation **routes through `CV_AI.execute('glyphic.generate',
  {params:{brief,count,thread}})`** (foundry:192–195) — *"never raw window.claude"* (foundry:24,193).
  Save routes through `CV_AI.execute('glyphic.save')` or `CV_ICONS.add`, then **rebuilds the Symbol
  axis** so the new icon appears instantly in the explorer + axis (foundry:212–224, :218).
  A **live/demo mode flag** keys off `window.claude` presence (foundry:124–126), with a `demoCandidates`
  composer so the surface is always demonstrable without a model.
- **Unique qualities to KEEP:** (1) the **propose→feedback→iterate→save loop already exists**, routed
  through the registry; (2) **candidates live-render as glyphics** (the exact "resolve to a glyphic"
  step); (3) **save → axis-rebuild → instant availability** is the no-staleness loop made real; (4) the
  **thread is passed into the capability** (`params.thread`) — conversational context already plumbed;
  (5) **demo-fallback pattern** for "always demonstrable" without the fleet.
- **This is the closest existing analog to the ENTIRE research premise** and the named DO-NOT-LOSE scope
  (A5). **Not runtime-verified with a live model in this read** — mode flag implies it runs in demo by
  default. The slice-61 status says it was *"verified generate→render→save 126→127"* (AXIS-REFACTOR.md:121)
  — i.e. verified through the capability, demo-side; **live-provider path still owed.**
- **FUSION:** the foundry IS the GENERATE-ON-MISS station of the live pipeline. The live layer adds:
  (a) **STT in front** (the brief comes from transcribed voice, not a textarea); (b) **semantic
  icon-lookup BEFORE generate** (only below-threshold misses call `glyphic.generate`); (c) the candidate,
  once saved, becomes a **node in the live `CVGraph`**, not just a library entry. The foundry's
  conversational thread model + registry routing + demo-fallback are the scaffold; do not rebuild them.

### B2 · The static glyphgraph render (`DiagramSolver.glyphGraphView`) — the existing READ-OUT graph
- **Observed (DiagramSolver.jsx:279–351, :368):** described in §0.1 and §3-A. Unique qualities: **nodes
  are full glyphics** (`GL.render(nd,{size})`, :341); **edges carry meaning visually** (`SH.edgeSVG`,
  line-style=mood, colour=state via `CV_MEANING.field("lineColor")`, routing, arrow=direction, :296–322);
  **edge labels OFF by default** — *"the graph MUST read from the visual facets alone (Tim: 'otherwise
  it's not the language')"* (:274–277); the read-out lives in a `<title>` via `CV_MEANING.readGraph`
  (:312–314); node `title` = `CV_MEANING.referent(nd)` (:342); **size auto-shrinks** for busy graphs
  (n>6→44, n>4→50, :287); **labels-mode** is an opt-in reveal (:329–337).
- **GAP / hard part it does NOT cover:** static, full-graph, recompute-every-render layout (no incremental
  stability, no interaction). **Not visually verified** (memory: glyphic verified headless only).
- **FUSION:** keep `glyphGraphView` as the **CSP-safe page-face render AND a projection target**; the
  live interactive canvas drives the **same `CVGraph`** and (per A3/A4/§3-A) feeds frozen x/y through the
  AUTHORED branch so the two surfaces never diverge.

### B3 · The System-Map graph (`system/system-map.html` + `build-system-map.js`) — a working live graph canvas at scale
- **Observed (build-system-map.js:15–22, :147–167):** a **second, fully-built graph surface** — the
  living-codebase canvas. Model shape v2: `nodes[] {id,name,path,parent,type,ext,role,size,defines[],
  uses[]}`, `edges[] {from,to,kind,type}` where **`type` is a bidirectional-verb edge family**
  (contains↔sits-inside, loads↔loaded-by, resolves-from↔resolves-into, :18–21), `globals[]`. **Single
  source:** `classifyRole()` is *"the one place a file's system-membership is decided"* (:32–34);
  `system-map.json` is OUTPUT, never hand-edited (:5–6). Built by a **parallel BFS walk** with a
  **time budget** (`timeBudgetMs`, :82,116–117) and **incremental size-filling across re-runs** (:131–145).
- **Unique qualities to MINE:** (1) a **bidirectional typed-edge vocabulary** (verb pairs) richer than
  `CVGraphEdge.kind` — the live glyphgraph's relations could adopt this verb-pair shape; (2) a real
  **node-encoding selector** system (size by usedBy/bytes/links; colour by role/ext/heat) — see B4;
  (3) **budget-bounded incremental build** — a pattern for keeping a *growing* graph responsive (relevant
  to the live placer); (4) the **6-second auto-poll** + edit-suppression (editor-adapter, B5).
- **FUSION:** the system-map proves a large, panning, encoded graph canvas already runs in this repo. The
  live instrument is a *sibling surface*; reuse its node-encoding projection (B4) + its edit/op-queue
  pattern (B5) rather than inventing them. (It is NOT itself a glyphgraph — it renders file-nodes, not
  glyphics — so it's a pattern donor, not a merge target. Per memory rule *Not A Replacement*.)

### B4 · The Visual-Encoding Grammar (`SYSTEM-MAP-ENCODING-GRAMMAR.md`) — the facet→channel registry the RESOLVE step needs
- **Observed (SYSTEM-MAP-ENCODING-GRAMMAR.md:9–17, :40–97):** *"A file/folder has facets. The canvas
  turns facets into channels."* An **encoding set** binds `facet → channel` (colour/size/texture/border/
  glow/opacity) with value→appearance maps; single-sourced in **`CV_MEANING.encodings('system-map')`**,
  baked into the json by the generator, and the map is a **projection** (`encSet(id)`, `rc()` resolve
  from `ENC`, :78–86). *"No second home — change a colour in cv-meaning.js, rescan, the map updates."*
  *"If you find yourself writing a colour/size value inside system-map.html, that's drift."* (:99–103).
- **Unique quality:** this is **the existing precedent for data-binding** the ANCHOR §7 flagged
  (`CV_MEANING.encodings`, data→channel). It is *surface-scoped* and *loadable/round-trippable to JSON*
  (authorable without code, :93–97) — exactly the no-staleness shape the ANCHOR's GOVERNING LAW demands.
- **FUSION:** the live glyphgraph's RESOLVE step (state→fill/colour, type→form, magnitude→size) is **an
  encoding set registered for the `glyphgraph` surface** (`CV_MEANING.encodings.register('glyphgraph',
  profile)`), NOT inline mapping in the pipeline. A new live-extracted facet (e.g. `temperature` for
  "buyer gone cold") is **a facet computed on the node + a set referencing it** — the documented
  extension path (:88–97). This keeps the ANCHOR's "meaning deep-linked to its source, not copied."

### B5 · The Editor & Disk-Write Adapter (`SYSTEM-MAP-EDITOR-ADAPTER.md`) — the op-queue mutation pattern for voice corrections
- **Observed (SYSTEM-MAP-EDITOR-ADAPTER.md:10–77):** visual edits **mutate an in-memory model + emit a
  typed operation queue** (`createFolder/createFile/rename/move/archive/duplicate/delete`, :15–28); the
  browser **can't write disk**, so an **adapter** replays the queue (:34–58). Key disciplines: a
  **staleness guard** (`generatedFrom` vs current `generatedAt`, :49–51); **idempotence/refuse-overwrite**
  (:51–53); *"There is **one** code path per op and the op queue is the single record of intent"* (:69);
  *"add an op type here and in the editor's emit calls together — same as every other registry, one home"*
  (:76–77); persistence to `localStorage` with **auto-poll suppressed while edits are pending** so it
  can't clobber them (:62–65); structural mutation goes through one `relocate()` helper that **remaps
  edges/globals + FLIP-morphs survivors** (:66–69).
- **Unique quality:** a **complete, principled spec for mutating a graph via typed, replayable, single-
  path operations with a staleness guard and animated reflow** — the hardest-won part of "talk → graph
  mutates."
- **FUSION (this is the load-bearing reuse):** a voice correction ("no, the buyer's gone cold", "the
  buyer's gone") is **a typed graph-mutation op** (`setState`/`addNode`/`addEdge`/`removeNode`/`relabel`)
  on the in-memory `CVGraph`, applied through **one code path per op**, with FLIP-morph reflow — the
  state-morph the engine already animates (cv-nodes `state:"before"|"after"`, DiagramSolver `morph`).
  Adopt the **op-queue vocabulary + one-home rule + staleness guard** directly. The two-way authoring
  ("your voice and the AI both author the same surface", ANCHOR §2) is the editor's exact model: human
  edits and pipeline edits both append typed ops to one queue against one model.

### B6 · (minor) `RenderType.blockToNode` — a parallel that is the WELD, not a duplicate
- **Observed (RenderType.jsx:32–70):** `blockToNode` re-expresses the whole `WS_BLOCKS` taxonomy in core
  atom roles. **Flagged not as a duplicate to collapse but as the resolution of one** — it is how the app
  composer's parallel block list folds onto the one engine (UNIFICATION W3). I note it so the synthesis
  doesn't mistake it for a fork: it is the *pattern* the live layer copies (one producer → the IR).

---

## (c) What the synthesis MUST NOT contradict (the non-negotiables, with evidence)

### C1 · MUST NOT become a fifth parallel render strand — the named, recorded failure mode
- **Evidence (UNIFICATION.md:122–124):** *"The earlier slice-4 mistake, recorded honestly:
  `Slide`/`Archetypes` shipped as a fourth parallel strand instead of welding the existing three."*
  Three parallel lists existed for every concept (UNIFICATION.md:24–31) and were the symptom of a missing
  weld.
- **Non-negotiable:** the interactive (reactflow/tldraw) canvas and the static CSP-safe SVG glyphgraph
  must BOTH be **projections of the one `CVGraph` IR** (`cv-nodes.d.ts`). Reactflow holds **references**
  to CVGraph nodes, never its own copy of node data; a custom reactflow node renders **through
  `CV_GLYPHIC.render` / `glyphGraphView`'s node logic**, not a bespoke SVG. If the canvas has its own
  node model, it is the fifth strand. This is the single highest-risk contradiction.

### C2 · MUST NOT introduce a second provider / second model client
- **Evidence (INTEGRATION.md:80–83, CLAUDE.md §2):** *"Providers are the only model binding …
  Consumers call `CV_AI.execute(id)` or `CV_AI.complete(prompt)` — never `window.claude.complete` or
  `window.cvOpenAI.generateImage` directly."* The foundry obeys this (foundry:24,193).
- **Non-negotiable:** the Company local fleet enters as **`CV_AI` providers resolved by role/id**
  (ANCHOR §4 my-idea is correct in shape). Every extract/compose/generate model touch goes through
  `CV_AI.execute` / a registered capability. No direct HTTP-to-fleet call sprinkled in the pipeline.

### C3 · MUST NOT put a JS layout dependency in the no-script page-face; MUST keep closed-form render viable
- **Evidence (DiagramSolver.jsx:66–67):** the explicit *"No external layout lib (CSP/bundle) —
  closed-form"* decision, and the page-face render is `runtime/page_render.py` (ANCHOR §7).
- **Non-negotiable:** whatever the interactive surface computes for placement must **serialize to frozen
  `x/y` on the `CVGraph`** so the closed-form `glyphGraphView` (no JS lib) can still render the same graph
  on the page-face. The heavy lib lives only in the live authoring surface, never in the static render.

### C4 · MUST NOT fail silently anywhere in the pipeline
- **Evidence (INTEGRATION.md:90–92, DiagramSolver.jsx:283,301–302,316–319, UNIFICATION.md:88–92).**
- **Non-negotiable:** a resolve-miss → foundry-or-loud-Notice; an unknown facet value → throw (as
  `CV_MEANING.field` already does); a read-out failure → warn, don't blank. No dropped nodes, no
  placeholder shapes standing in for a real resolution. (Project memory: *No Silent Failures Or Fallbacks*.)

### C5 · MUST NOT hand-style nodes or hardcode the facet→appearance maps
- **Evidence (SYSTEM-MAP-ENCODING-GRAMMAR.md:99–103, AXIS-REFACTOR.md:31–36, HANDOFF.md:27–42).**
- **Non-negotiable:** node appearance is **computed from facets through the axes**; the state→colour,
  type→form, magnitude→size maps live in **`CV_MEANING.encodings('glyphgraph')`** (a registered set), not
  inline in the pipeline. A new live facet = compute-on-node + a referencing set, the documented path.

### C6 · MUST NOT churn what is genuinely right
- **Evidence (UNIFICATION.md:116–117 "Do not churn what's right"; AUDIT-INDEX.md:36–38,43):** the shape
  system (circle/hex/octagon/diamond = the four platform entities), the 99-icon library, the voice, the
  ramp/zoning values are confirmed DNA — KEEP. The entity-shape vocabulary is *meaning-bearing* (a
  glyphgraph node's `shape` is not decorative).
- **Non-negotiable:** the live layer reuses the shape/icon/colour-role DNA; it does not re-pick shapes or
  re-tag icons from scratch.

### C7 · MUST NOT version / branch / leave stranded scope (project-memory laws that bind this build)
- **Evidence (this repo's commit law + project memory):** *No Versioning* (update canonical files in
  place, never v2), *No Branches Company* (commit to main), *No Coauthored Trailer*, *Incomplete Work In
  Scope* / *No Deferral* (the foundry's owed live-provider path, A5, is adopted not parked),
  *Resolve Divergence Into Scope* (the `.d.ts`-vs-runtime edge-facet drift A4 + the `"glyphgraph"`
  missing-from-union drift get fixed, not flagged-and-left).

---

## Cross-references (so the synthesis can route)
- IR + static graph render: `core/cv-nodes.d.ts`, `core/DiagramSolver.jsx` (glyphgraph :279–351) — overlaps AREA-6 (reactflow/render), AREA-12 (core).
- The weld + bridge signature: `core/RenderType.jsx`, `analysis/UNIFICATION.md` — overlaps AREA-11, AREA-14.
- Conversational authoring + capabilities: `system/glyphic-foundry.html`, `app/ai/ai-glyphic.js` — overlaps AREA-1 (CV_AI), AREA-4 (foundry/lookup).
- Data-binding precedent: `SYSTEM-MAP-ENCODING-GRAMMAR.md` + `CV_MEANING.encodings` — overlaps AREA-7 (data-binding/prior-art).
- Op-queue mutation + live graph canvas: `SYSTEM-MAP-EDITOR-ADAPTER.md`, `system/build-system-map.js`, `system/system-map.html`.
- No-staleness machinery + owed scope: `analysis/AXIS-REFACTOR.md` (CV_AXES, foundry DO-NOT-LOSE) — overlaps AREA-5.

---

## 3 · Honest hard-parts mapped to existing code (the "yes, but actually the code does X")

### 3-A · "Stable incremental auto-placement" — the existing layout JUMPS; here is exactly why, and the fix
- **Observed (DiagramSolver.jsx:63–100):** `layout()` for `"glyphgraph"` has two branches. **Authored
  branch** (:68–72): if `nodes.every(nd => nd.x!=null && nd.y!=null)`, place each at its authored x/y —
  **stable.** **Auto branch** (:73–100): rank = longest-path-from-a-source via a BFS-relax over *all*
  edges, group by rank into rows, spread each row across the width; flat graphs → ring.
- **The problem, traced:** the auto branch recomputes ranks from the **entire** current edge set every
  render. When a new node+edge arrives mid-conversation, an existing node's longest-path rank can change
  (e.g. a new upstream source lengthens a path) → its row index changes → **it moves**. Rows also
  re-spread as a row's membership count changes. So a graph that *grows during a conversation* does not
  stay still — directly the ANCHOR §6 "stable incremental auto-placement" hard part. **(This contradicts
  any reading that the static render already solves the live case — it does not.)**
- **The fix (reuses the authored branch):** the live **incremental placer** assigns x/y for each node
  **once, when it arrives** (e.g. layered placement among the *then-current* graph, or a force-relax with
  existing nodes pinned), **freezes** it on the node, and thereafter the graph is rendered through the
  **authored branch** (all nodes have x/y) — `glyphGraphView` unchanged. New nodes get a slot near their
  relation without disturbing placed ones; a manual drag writes a new frozen x/y (A7). This is additive:
  a new module (the placer) + reuse of an existing render branch, no rewrite. **Inferred** — needs build +
  visual verification; the existing pieces (authored branch, freeze field) are **Observed**.

### 3-B · "Realtime latency of the extract layer" — out of this area's evidence, flagged for AREA-2/3
- This area saw no extract-layer timing evidence (that's the Company-fleet/voice areas). I only note the
  constraint it imposes here: the placer + render must accept **partial, streaming** `CVGraph` deltas
  (one node/edge at a time), which the op-queue model (B5) and the incremental placer (3-A) are built for.

### 3-D · FINDINGS-LOG.md — the glyphgraph-specific build decisions the distilled docs do NOT carry (gap-closing read)
> Bounded grep of the 217KB build memory surfaced four recorded decisions specific to the glyphgraph that
> change/strengthen the picture above. These are the "running memory" the synthesis must not contradict.

- **A glyphgraph RULEBOOK + validator already exists (Observed, FINDINGS-LOG.md:84–111, slice 79).**
  `assets/icons/glyphgraph.js` → **`window.CV_GLYPHGRAPH.validateGlyphgraph`** checks well-formedness by
  REUSE: resolves each `edge.kind` → a `relationship.${kind}` Type and validates source/target via
  `CV_REGISTRY.accepts` (domain/range) + edge `conditions` via `CV_COND`; **collect-then-throw** on
  untyped edge / dangling endpoint / dup id / bad node-class / failing condition (loud-fail, NOT the
  absent-facet law). The relationship Types are seeded by **`app/registry/relationships-seed.js`** — a
  Type per edge-kind, the id list **reconciled live** from `CV_EDGES.ids()` + `CV_MEANING.valuesFor('edge')`
  (no re-authored meaning). Verified by `_demo/verify_g3.js` (25/25, node shim — **not browser**).
  - **Implication for the live layer:** the pipeline's emitted `CVGraph` should be run through
    `CV_GLYPHGRAPH.validateGlyphgraph` BEFORE render — the JUDGE step (ANCHOR §3 extraction-vs-judgment)
    has a home already. A live-extracted edge with an illegal source/target fails loud here, not silently.
  - **Reconciles A4/§3-C drift note (iii):** there IS a typed home for edge-kinds (relationship Types);
    the `.d.ts` `CVGraphEdge.kind` union and the runtime edge facets should reconcile TO this registry,
    not to a hardcoded list.

- **The read-out already does NEGATION + CONDITIONALS (Observed, FINDINGS-LOG.md:8–42, slice 81).**
  `CV_MEANING.readGraph`/`describeRelation` verbalize `{kind:'not'}`/`negate:true` ("is NOT the face of",
  the relation word survives) and `edge.conditions` ("if … then …", via `CV_COND.normalize` — reused, not
  reinvented), loud-fail on unknowns. Verified by `_demo/verify_g2_4.js` (22/22, node).
  - **Implication:** "no, the buyer's gone cold" (a state change) AND "if the survey clears, the sale
    proceeds" (a conditional relation) are BOTH already expressible + readable in the graph grammar — the
    live layer maps voice → these existing edge markers, it doesn't invent a conditional/negation syntax.

- **There is a G-numbered CRITERIA spec + a `verify_*.js` harness suite driving this (Observed,
  FINDINGS-LOG.md:44,84,8 — G5.1/G5.1b/G5.2/G5.3, G3.2–G3.4, G2.4, G8b; harnesses verify_g2/g3/readgraph/
  language/glyph/g8b).** The live-instrument work is the continuation of this same numbered build, not a
  separate project. **The synthesis should locate itself in / extend that CRITERIA file** (referenced but
  not in this area's territory — flagged for the lead) rather than starting a parallel criteria list
  (project memory: *Resolution-First Compositional*, *No Versioning*).

- **Slice 80 explicitly FLAGGED FORM/taste items for Tim, NOT green-painted (Observed, FINDINGS-LOG.md:
  76–82).** Mixed edge routing is "a first taste-pass, not a settled rule"; curved-edge arrowheads land at
  a slight angle; the live paragraph drops the *file* clause from the SENTENCE though the PICTURE shows all
  3 relations (readGraph's single-source auto-focus walk) — "sentence-coverage + wording are explicitly the
  LIVE-tuning surface (G4.5), not a build gate."
  - **Implication / open thread the live layer inherits:** read-out *coverage* (does the spoken narration
    cover every relation the graph shows?) is a known-open tuning surface — directly the ANCHOR's NARRATE
    step. The live layer must not assume the read-out is complete; closing sentence-coverage is in-scope
    (project memory: *No Deferral* / *Incomplete Work In Scope*). And per *User-Facing Walks Through Tim*,
    the routing/arrowhead taste calls are Tim-gated, not agent-settled.

### 3-C · "The no-staleness discipline holding across providers/tags/renderer" — the rigor area, and the code is mostly on-side
- The strongest evidence for the ANCHOR's optimism: the foundry routes through `CV_AI`, save rebuilds the
  Symbol axis, the encoding grammar forbids inline appearance maps, the graph render throws on unknowns,
  and the editor-adapter enforces one-code-path-per-op. The places staleness could still sneak in, per
  this area: (i) the `.d.ts`-vs-runtime edge-facet drift (A4); (ii) `"glyphgraph"` absent from the
  `CVGraphType` union (A4); (iii) a reactflow surface with its own node model (C1); (iv) hand-styled
  live nodes (C5). The synthesis closes (i)+(ii) as hygiene and designs against (iii)+(iv).
