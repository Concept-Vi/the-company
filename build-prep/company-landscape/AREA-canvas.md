# AREA-canvas: Canvas / Nodes / Projections / Bindings / Flows / Axes / Dials — Exhaustive Landscape

Produced: 2026-06-21. Read-only dragnet. Evidence paths included for every claim.

---

## 1. CANVAS/ — The Frontend Surface

### What it is
`canvas/` is the frontend Tim operates: **tldraw + React** (TypeScript, Vite, served at `:8080`). A desktop/mobile web app. The Tauri wrapper mentioned in AGENTS.md is architecturally anticipated but not yet present in this tree — the app is a browser SPA.

### Structure
```
canvas/.gitkeep                    — placeholder; the app lives in canvas/app/
canvas/index.html                  — top-level static entry (symlink or copy for server)
canvas/app/                        — the Vite/React app
  src/App.tsx                      — the root component: <Tldraw> + <Hud> + the CSS grid shell
  src/api.ts                       — the full API client (100+ methods) + pure helpers
  src/registryStore.ts             — the 6-field external store (OINFO/MODEL_OPTIONS/UI_INFO/NODE_STATES/COGNITION_INFO)
  src/AppContext.ts                 — exposes useAppController to every region
  src/NodeShape.tsx                 — the ONE generic node shape (all node-types; never per-type)
  src/ForagerShape.tsx              — the Forager search-result shape (second shape vocabulary)
  src/useAppController.ts           — ALL Hud state + handlers + effects (the state container)
  src/components/*.tsx              — PanelErrorBoundary · PanelView · NodeConfigForm · BuildIntentCard
                                     BlastRadiusReach · ContextBundle · RegistryProposals
                                     ShapeHow · StudioKit · StudioSeams · WireRequest · kit.tsx
  src/regions/*.tsx                 — Toolbar · Palette · Inspector · Inbox · Grow · OpPanels
                                     Activity · RhmChat · ClaudeChat · GreetingCard · MobileTray
                                     Walkthrough · Workshop · Settings · Fleet · CognitionView
                                     Review · ForagerBar · AddressHelp · History · Versions
                                     SelfChanges · LatticeView · ProposeAffordance · LatticeView
  src/extensions/                   — brain-authored extensions live-tree (gated)
    live_clock_widget.tsx           — first extension (ORIGIN='system', self-grown)
  src/app.css                       — styles
  dist/                             — built output (deployed artefact)
```

### Key Contracts / Seams
- **Reflects-never-owns**: canvas reads state from the backend; the runtime is authoritative. Graph, config, edges, outputs all round-trip through `/api/*`.
- **One generic `ai-node` shape** (`NodeShapeUtil`): `canvas/app/src/NodeShape.tsx:30`. Node props include `nodeId, nodeType, kind, status, output, address, ref, layer, error`. A new node-type in `nodes/` needs ZERO frontend code.
- **Registry store** (`registryStore.ts`): 6 fields available module-scope to shapes rendered inside tldraw (cannot consume React context there). OINFO · MODEL_OPTIONS · UI_INFO · NODE_STATES · COGNITION_INFO. Uses React 18 `useSyncExternalStore`.
- **API client** (`api.ts`): ~100 methods covering graph/run/chat/voice/walkthrough/cognition/lattice/journey/version/annotate/address. The `jr()` helper normalises HTTP errors to `{error}` (never throws) to prevent white-screens.
- **SSE live stream**: `/api/stream` — the lattice + activity subscribe. New event → re-projection.
- **Persistence key**: `company-canvas-v4` (IndexedDB). Must bump when NodeShape props schema changes.

### The Canvas Regions (all in `src/regions/`)
Each is a React component mounted in the CSS grid or as a modal. All wrapped in `PanelErrorBoundary`.

| Region | Purpose |
|---|---|
| Toolbar | top bar, RUN, mode, settings gear |
| Palette | node palette, add-node |
| Inspector | selected node config + port wiring |
| Inbox | governance inbox, surfaced items |
| Grow | proposal/growth affordances |
| OpPanels | operator panels |
| Activity | live event feed |
| RhmChat | right-hand-man chat (main conversation) |
| ClaudeChat | Claude Code builder panel (second conversation partner) |
| GreetingCard | arrival greeting — "caught up in one glance" |
| MobileTray | long-press verb tray (phone only) |
| Walkthrough | guided walkthrough modal |
| Workshop | full-viewport builder workshop modal |
| Settings | consolidated settings modal (model/voice/persona/RHM config) |
| Fleet | live model layer surface |
| CognitionView | live cognition pulse/river/nodes (the commander's bridge) |
| Review | design review workspace (the studio, second view) |
| ForagerBar | corpus semantic search bar + circles on canvas |
| AddressHelp | "what can I do here?" — address help at indicated locus |
| History | addressed history — trajectory at a ui:// address |
| Versions | ref-versions at a run:// address |
| SelfChanges | self-change audit log filtered to code scope at address |
| LatticeView | **THE UNIVERSAL PROJECTION** (Tim's equation, full canvas view) |
| ProposeAffordance | propose affordance on canvas |

### View Switch
Three top-level views: `canvas` (tldraw board) · `review` (design studio) · `lattice` (the universal projection). State: `const [view, setView] = useState<'canvas' | 'review' | 'lattice'>('canvas')`. The tldraw board keeps running under all views.

### What LatticeView is
`src/regions/LatticeView.tsx` — the universal projection (Tim's equation). 1154 lines. Renders on a `<canvas>` element with a full draw() loop.

**The equation**: θ (angle) = kind/sector (registry divisions) · r (radius) = time from NOW by default (swappable). Points = every event in every store, projected on the same geometry. Color IS angle (angle-hue).

**The bindings** drive what the projection shows: `raw` (default, data-driven kinds) · `semantic` (meaning-distance from a chosen centre) · `by_node_type` (connections/registry edges) · `by_lens` (projections as sectors) · `by_cascade` (cascade precedence flow) · `by_separator` (two-gravity field) · `by_nucleation` (20/80 type-birth) · `grouped` (activity families) · `time-of-day` (day cycle).

**Groups** mapped in LatticeView:
- Group 6 (THE CIRCLE): `radius_from='semantic'` — meaning-distance from a chosen corpus item
- Group 7 (STRAIN): `showStrain` toggle — radial segment from where filed (r_struct) to where it means to be (r)
- Group 9 (SEPARATOR): two-gravity field — signed lean between two poles, left/right basins
- Group 10 (CONNECTIONS): directional typed edges drawn as directed chords; pick a sector → its in/out edges light up
- Group 11 (SCALE LADDER): rung (null=unit items, k=coarse themes); crossfade between rungs
- NUCLEATION (20/80 water-law): type-birth from the pile; the dial drives the birth threshold client-side (instant, no refetch)

**Live via SSE**: subscribes to `/api/stream` after first projection fetch; re-projects on new events. The lattice is a live organ, not a photograph.

**Gaps in LatticeView**:
- `dial` parameter (20/80 birth threshold) is NOT sent as a query param — computed client-side for instant response. The server returns size/distinct and the client recomputes `born`. This is intentional (documented in the effect comment at line 194).
- `viewer.py` axis `value_source: "pending"` — no operator-mode state built yet; the axis slot is wired, value awaiting.

### Gaps / Stale / Surprising
- `canvas/.gitkeep` exists at the top — the app lives in `canvas/app/` not directly in `canvas/`.
- `canvas/app/src/extensions/AGENTS.md` — extensions constitution present; only one extension built (`live_clock_widget.tsx`, self-grown).
- `canvas/app/voice_autolisten_controlflow.test.mjs` — a test file at the app root (not in a test dir); possible stale placement.
- `persistenceKey="company-canvas-v4"` — the key is at v4. Each schema change requires a bump; easy to forget.
- No Tauri wrapper in the tree; AGENTS.md says "tldraw + React + Tauri" — Tauri is anticipated, not present.

---

## 2. NODES/ — The Node-Type Library

### What it is
`nodes/` is the **compositional dataflow node library**. Each `.py` file is one self-registering C2 node-type. Drop a file → new type appears in the palette, the registry, and the canvas with zero other code changes. Discovered by `runtime/registry.py:NodeRegistry.discover()`.

### Node Contract (C2)
Every node module exposes module-level declarations:
- `VERSION` — schema version string
- `PORTS_IN` — `{port_name: "TypeString"}` (input ports)
- `PORTS_OUT` — `{port_name: "TypeString"}` (output ports)
- `CONFIG` — `{key: {type, label, default, options_from?, options?, min?, max?}}` (inspector fields)
- `VOLATILE = True` (optional) — if the node reads mutable external state (filesystem, live data), disables memo cache
- `RESOLVE = 'reference'` (optional) — portal nodes; scheduler skips firing, output resolved live from config.ref
- `KIND` (optional) — 'process' | 'content' (used in legibility meta)
- `ORIGIN` (optional) — 'system' for brain-written nodes
- `run(inputs: dict, config: dict)` — the execution function; returns either a scalar value OR a `{port_name: value}` dict (for selective emission / multi-output)

### The Node Types (16 total + 2 brain-written)

| Node | Kind | VOLATILE | Notes |
|---|---|---|---|
| `llm` | process | no | Calls model via fabric client. Swappable model/endpoint. `draw` config key = memo-differentiator for jury draws (C1.5). |
| `ask` | process | no | Question + Context → Answer. First-purpose grounded-codebase path. |
| `pair` | process | no | Non-commutative fan-in. A>B. Exists to test port→input binding in memo signature. |
| `constant` | content | no | Emits a fixed configured value. No AI. |
| `codebase` | content | **yes** | Reads repo files into one context blob. Globs configurable. Fails loud if exceeds max_chars (600k). |
| `embed` | process | no | Text → Vector. BGE-M3 @ :8001, 1024-dim. Enforces dim contract. |
| `gate` | process | no | Branches: `value` → `pass` or `fail` based on `verdict`. Selective emission (only the taken port is written). |
| `join` | process | no | Fan-in. Concatenates sorted inputs with separator. |
| `model_of_tim` | content | **yes** | Reads `~/foundation/system/principles.md`. Fails loud if missing. |
| `portal` | content | n/a | RESOLVE='reference'. Scheduler skips it. Live window onto another address. run() always raises. |
| `retrieve` | process | no | query Vector + corpus → top-K by cosine. numpy fast-path (~100x), Python fallback. Dim mismatch fails loud. |
| `rhm_mode` | content | no | The presence dial as a node. 8 modes enum. Also carries `voice_enabled` toggle. |
| `similarity` | process | no | Two Vectors → cosine score. Inlined math. Zero vector raises ZeroDivisionError (fail loud). |
| `titlecase` | process | no | Text → Title Case. Brain-written (ORIGIN='system'). |
| `uppercase` | process | no | Text → UPPERCASE. |
| `wordcount` | process | no | Text → word count as string. Brain-written. |

### The NODE_TYPE_META legibility registry
`nodes/_meta.py` — a `NODE_TYPE_META` dict mapping each node type id to `{name, is}` in human language. Read by the instrument for the "Connections" wheel sector labels. Grounded in each node module's docstring. Declared first, never invented by the surface.

### `nodes/__init__.py`
Makes `nodes` an importable package so `from nodes._meta import NODE_TYPE_META` works. Discovery (runtime/registry.py) uses file-path, never `import nodes.<x>`. Files starting with `_` are skipped by discover().

### Gaps / Stale / Surprising
- `retrieve` has a numpy fast-path added 2026-06-21 (the per-item loop was timing out on 44k×2560 corpus = ~112M mults). The fast-path is additive; falls back on numpy absence or dim mismatch.
- `portal.run()` raises RuntimeError — by design. If it's ever called something is wrong upstream.
- `rhm_mode.voice_enabled` is GLOBAL on the single rhm node, not per-mode. Flagged in the code comment as a known limitation.
- No `similarity` CONFIG — pure functional, no editable fields. Correct.
- `gate` selective emission: the scheduler writes `set_ref` ONLY for ports present in the returned dict (runtime/scheduler.py). This is how branching-as-absence-of-write works — no control flow in the scheduler.

---

## 3. PROJECTIONS/ — The Corpus Lens Registry

### What it is
`projections/` is the **file-discovered projection (lens) registry** (Cognition Engine K1/P1). A projection = a declared LENS over a corpus unit — one named way to DESCRIBE a file/unit. Discovered by `runtime/projections.py:ProjectionRegistry` (mirrors `runtime/roles.py`).

### Why file-discovered (the adversary-verified BAR)
The real test of "registry-is-truth" is: **add-a-row = a FILE, no code edit**. A Python dict still requires a source edit. A `projections/<id>.py` drop-in makes the lens appear everywhere with ZERO code change. This is PART 4.3 of the completion criteria.

### Projection Row Shape
```python
PROJECTION = {
    "id": str,           # MUST equal the file stem
    "level": str,        # abstraction band: content | meaning | epistemic | structural
    "produced_by": str,  # 'model' (4B capture role describes it) | 'code' (lifter extracts it)
    "embeds": bool,      # True → becomes a vector SPACE (Group L); False → no space
    "field": str,        # optional: string | array | text | enum
    "enum": list,        # optional: enum values
    "desc": str,         # the render instruction (render-NOT-judge — K3)
    "stage": str,        # optional: legibility | deep
}
```

### The Projection Set (11 lenses)

| id | Level | Produced by | Embeds | Notes |
|---|---|---|---|---|
| `what` | content | model | no | ≤15-word "what this file IS". The seed lens. |
| `topics` | content | model | **yes** | subjects/areas → topics SPACE |
| `repo` | content | model | **yes** | repo file purpose/summary → repo SPACE (G15 unblock for ① repo-exocortex) |
| `principles` | meaning | model | **yes** | underlying principles/intents → principle SPACE (cross-session M3 corroboration) |
| `worldview` | meaning | model | **yes** | stances/values assumed (often unstated) → worldview SPACE |
| `claimed_status` | epistemic | model | no | file's OWN claimed state (decided/draft/aspirational/stub/unknown). Render-NOT-judge — K3 par excellence. |
| `lineage` | structural | **code** | no | first `produced_by:"code"` seed; deterministic extractor produces it. Excluded from capture-schema. |
| `operators` | structural | **code** | **yes** | what each registered OPERATOR does → operators SPACE. Nucleation: content no operator covers piles up → candidate new operator. Agent-authored. |
| `history` | meaning | model | **yes** | session-history lens (③/G23): one mined exchange-extract per unit → history SPACE. Agent-authored. |
| `common_knowledge` | meaning | **code** | **yes** | recollection's comprehended built-things → common_knowledge SPACE. EMPTY until recollection's pilot publishes. pplx/dim-2560. The recollection↔projection seam (Option A). |
| `extractions` | meaning | model | **yes** | dragnet extraction-layer (29,425 stepped coarse→fine meaning-extractions). Agent-authored. |

### Render-NOT-judge (K3)
A lens DESCRIBES. It does NOT judge. The 4B is a describer; judgement of truth/quality is a LATER reduce pass, never the capture lens itself. `claimed_status` is the clearest example: render the FILE'S OWN CLAIM, do not assess whether it is true.

### The embeddable spaces (Group L)
Projections with `embeds:True` become vector spaces. The embedding key pattern: `vec://<item>#space=<projection_id>`. Spaces: `topics`, `repo`, `principles`, `worldview`, `operators`, `history`, `common_knowledge`, `extractions`.

### PROJECTION_SPACE_META (in `bindings/by_lens.py`)
The human-meaning labels for projection spaces (for the "Ways of looking" lens in the instrument). NOTE: this lives in `bindings/by_lens.py`, NOT in a `projections/_meta.py` — that's because the bridge puts `runtime/` on sys.path where `import projections` resolves to `runtime/projections.py` (the ProjectionRegistry MODULE), so a `projections._meta` import silently fails. Bindings/ has no such collision.

### Gaps / Stale / Surprising
- `common_knowledge` SPACE is DECLARED but EMPTY. Awaits recollection's pilot publish.
- `lineage` has no `field` declared — it's a structural lens and the extractor determines the output shape. No `desc` either.
- `operators` and `history` were agent-authored (via the declarative-direct face). The AGENTS.md has an "Agent-authored entries" section auto-reflecting them.
- `extractions` space holds 29,425 entries (the dragnet) — the largest space. This is the reason `retrieve`'s numpy fast-path was added.
- The acceptance test (`tests/projections_acceptance.py`) asserts every discovered projection is reflected in AGENTS.md — this is the drift-home guard.

---

## 4. BINDINGS/ — The Projection Lens Registry (for the Instrument)

### What it is
`bindings/` is the **file-discovered binding (lens) registry** for the universal projection instrument (the Lattice). A binding = one declared FILLING of the instrument's equation slots (centre/angle_from/radius_from/k). NOT the sectors themselves (those resolve from angle_from against live data + registries at render time).

### Binding Row Shape
```python
BINDING = {
    "id": str,            # == file stem
    "label": str,         # short human description
    "angle_from": str,    # 'kind' | 'kind-group' | <registry-name> | 'node-types' | 'projections' | 'cascade-flow' | 'nucleation'
    "radius_from": str,   # 'time' | 'semantic' | 'nucleation' | 'separator'
    "order_by": str,      # 'count' | 'edge' | 'declared'
    "meta": dict,         # {name, is, fills, why} — human meaning (TENTATIVE draft; Tim/DNA ratify)
    # optional extras per binding:
    "space": str,         # for semantic/separator/nucleation — which embeddable space
    "whole_set": bool,    # True = sectors come from the registry's WHOLE set, not just rows present in event data
    "groups": dict,       # for kind-group only: {group_id: [glob_patterns]}
    "types_space": str,   # for nucleation: the registry of types
    "rung": int,          # for nucleation: how fine the registry of types is
    "dial": float,        # for nucleation: the 20/80 birth threshold
    "pole_a": str,        # for separator: default pole A (cluster:// or vec://)
    "pole_b": str,        # for separator: default pole B
    "pole_a_label": str,  # human label for pole A
    "pole_b_label": str,  # human label for pole B
}
```

### The 9 Bindings

| id | angle_from | radius_from | Notes |
|---|---|---|---|
| `raw` | `kind` (data-driven) | `time` | THE DEFAULT. No hardcoding: sectors = distinct kinds present in the store. "What's happening — the live activity." |
| `semantic` | `kind` | `semantic` | The CIRCLE (Group 6). radius = 1-cosine from the chosen centre. space='topics'. Pick a centre to rank by meaning-distance. |
| `by_node_type` | `node-types` | `time` | THE CONNECTIONS. sectors = every node type. Directional typed edges (A's output → B's input). whole_set=True. order_by='edge'. |
| `by_lens` | `projections` | `time` | WAYS OF LOOKING. sectors = the projections/ registry rows. drop a projections/<id>.py → new sector. |
| `by_cascade` | `cascade-flow` | `time` | FLOW. sectors = roles/op-verbs that saved cascades reference. Precedence edges as directed chords. whole_set=True. |
| `by_separator` | `kind` | `separator` | TWO GRAVITIES. radius = |lean| between two poles. Default poles: two most-distinct clustering-separated regions of topics space (1-cos≈0.19). Left basin = pole A (cool), right basin = pole B (warm). |
| `by_nucleation` | `nucleation` | `nucleation` | NEW KINDS FORMING. The 20/80 water-law. types_space='topics', space='repo' (cross-instance, non-circular). dial=0.2. |
| `grouped` | `kind-group` | `time` | ACTIVITY — grouped into 7 families (memory/conversation/making/operations/signals/decisions/field). Formerly "the instrument" — demoted to one binding among many. |
| `time-of-day` | `kind` | `time` | DAY CYCLE. Same events arranged by time-of-day. The FE cycle-frame switch overrides to day/week. |

### Secondary metadata in binding files
- `bindings/grouped.py` contains `GROUP_META` — human meaning for the 7 activity families. Read by `projection.py` for the "kind-group" sector domain.
- `bindings/by_lens.py` contains `PROJECTION_SPACE_META` — human meaning for each projection space. Read by `projection.py` for the "projections" sector domain.
- `bindings/by_cascade.py` contains `CASCADE_FLOW_META` — human meaning for each step/role in saved cascades. Read by `projection.py` for the "cascade-flow" sector domain.

### Gaps / Stale / Surprising
- `by_lens.py` PROJECTION_SPACE_META maps "operators" as "Roles" (not "Operators") to avoid the name collision with human operators who might read it as "about me".
- All `meta` fields (name/is/fills/why) are TENTATIVE drafts — awaiting Tim/DNA ratification. The field-set is journey-gated (OPERATOR-SURFACE-LOOP.md OQ1–4).
- `by_separator` default poles are hardcoded cluster references (`cluster://topics/k8/6` and `cluster://topics/k8/4`). These are the two most-distinct regions measured at build time. If the pyramid rebuilds, the `separates` field reports the truth (fail-honest, not silent-lie).
- `by_nucleation` uses a cross-instance pair (types from 'topics', items from 'repo') by design — to make the misfit genuine and non-circular.

---

## 5. FLOWS/ — The Production-Line Registry

### What it is
`flows/` is the **file-discovered flow registry** (GC1). A flow = a registered, multi-primitive PRODUCTION LINE — authored code composing engine primitives into a proven, re-runnable chain. Invocable through the company MCP by name (`flows` tool: op=list|describe|run). GC1 evidence: agents rebuild chains ungrounded when the proven chain isn't the easiest path — a flow row makes the grounded chain ONE call.

### The Law
- Flows are **AUTHORED** in the repo (reviewed, committed). Never through the MCP.
- Flows are **INVOKED** through the MCP.
- Flows **PROPOSE ONLY** (`proposes_only: True` enforced at discovery). They compute, write artifacts, write corpus, or surface review items. They NEVER: resolve/approve/dispatch/`claude -p`.
- Declarative chains are NOT flows — they go through `save_cascade`.

### Flow Row Shape
```python
FLOW = {
    "id": str,            # == file stem
    "label": str,
    "description": str,
    "params": {name: {"desc": str, "default": any}},
    "proposes_only": True,  # ENFORCED — never False
}
def run(**params) -> dict: ...
```

### The 8 Flows

| id | GC tag | What it does |
|---|---|---|
| `registry_generation` | GC2 | Grounded mockup→dossier chain. GROUND → MAP (register_element with designed context) → REDUCE (cluster dedup) → CONFIRM (floor + jury). Resume-safe. Artifacts in `.build/rg10/`. param: `time_budget_s`. |
| `transcript_mine` | ③/G23 | Conversation transcripts → distilled exchange extracts → embedded into space='history'. Idempotent at exchange granularity. Exchange key: `exchange://<sid>/<i>`. param: `time_budget_s`, `max_mb`. |
| `pattern_cluster` | ③/G13 | Self-study REDUCE. Tally + embed-cluster every mined `pattern_tag` → named weighted groups. Feeds `G13-PATTERN-REPORT.md`. No params. |
| `repo_ingest` | ①/G21 | Repo-exocortex ingest. Walk → repo_digest MAP → capture+embed into space='repo'. Hash-aware incremental (G25). Floor for drift_radar + ask-the-codebase. params: `max_files`, `root`. |
| `drift_radar` | ② | Built-twice/overlap sweep over repo space. Near-pair clusters → judge_drift confirm → surface-direction marks. Doc-vs-code drift candidates. Zero-results FAIL LOUD (a silent 'all clean' is not a believable radar). No params. |
| `floor_walk` | standing | The standing cross-lane sweep for dead/stranded work: stranded uncommitted files · unmounted canvas components · stale decisions · phantom corpus sources. DETERMINISTIC (no model). params: `stranded_after_s`, `stale_decision_days`, `surface`. |
| `cc_registry_refresh` | F-FIX-4 | Mirror-Registry LANE-REFRESH. Compares live Claude Code binary version vs stored stamp. Re-introspects on mismatch, diffs vs prior snapshot, surfaces ONE `cc_registry_gap` inbox item. Stamp write is POST-APPROVAL ONLY (fail-closed). params: `discover_fn`, `executable`. |
| `ts_backfill` | forager C2 | Deterministic re-stamp of ts_source onto history records lacking it. Idempotent. No model. param: `budget`. |

### Gaps / Stale / Surprising
- `registry_generation.run()` hardcodes `sys.path.insert(0, "/home/tim/company/build-prep/cognition-self-improvement")` — the implementation is in `build-prep/`, not in a proper module. Flags as technical debt (hardcoded path).
- `transcript_mine`, `pattern_cluster`, `drift_radar` similarly sys.path into `build-prep/`. These are "scripts promoted to flows" — the build-prep code is the real implementation; flows are thin wrappers.
- `repo_ingest` and `floor_walk` use `Suite` and `FsStore` directly from `runtime/` — proper module imports.
- `ts_backfill` hardcodes `/home/tim/.claude/projects/-home-tim` as the transcript dir. Should be configurable.
- `floor_walk` detector 2 (unmounted components) searches for BOTH `components/<stem>` AND `./<stem>` import patterns — a previous FP where `BlastRadiusReach` was flagged as dead while actually imported via relative path.
- `cc_registry_refresh` has injectable `discover_fn` for testing — the most carefully tested flow. Has `write_stamp_and_cache()` exported for post-approval handler.

---

## 6. AXES/ — The Coordinate-Axis Registry

### What it is
`axes/` is the **file-discovered coordinate-axis registry** (the resolver's axes-are-registries). Each `<id>.py` declares one orthogonal dimension. DROP AN AXIS = DROP A FILE (zero engine code; the coordinate-space self-extends). Discovered by `runtime/axis_registry.py`.

### Axis Row Shape
```python
AXIS = {
    "id": str,           # == file stem
    "namespace": str,    # the coordinate key
    "fields": {sub_field: "continuous" | "discrete"},  # resolve mechanism per sub-field
    "value_source": str, # 'live' | 'pending' | a ref
    "desc": str,
}
```

### The 7 Axes

| id | namespace | fields | value_source | Notes |
|---|---|---|---|---|
| `device` | device | w/h: continuous, orient/kind: discrete | live | The ROOT of continuous layout derivation (screen size). orient (portrait/landscape) + kind (native-mobile/desktop, size-bucket-derived) are discrete. Tim NAMED this — it's the spoke, not the hub. |
| `mode` | mode | current: discrete | live | pilot · inspect · dev · autopilot. The behaviour/render-family pick. |
| `register` | register | theme: discrete | live | The mood/finish (dark-observatory · others). Driving register re-skins every surface. |
| `resolution` | resolution | grain: discrete | live | coarse · medium · fine. The MRL grain / levels-of-detail. Also the dragnet grain axis (recollection's determine projects fields by this). Also multi-scale embeddings. READ-SIDE: a subset projection of the stored superset (extract-once / determine-many). |
| `state` | state | phase: discrete, frozen: discrete | live | pending vs decided (composed from decision_take mark) · live vs frozen (scrubber / point-in-time). |
| `type` | type | kind: discrete | live | What it IS — the archetype/render_kind. decision-card · graph · selector · instrument · diagram · spatial-material. 'content compositionality' axis. Per Tim's law: type is 'n' not a ranked axis. |
| `viewer` | viewer | expertise: discrete | **pending** | Who's viewing — Tim · RHM · client. Control-density axis: expert knobs resolve against expertise. VALUE-SOURCE PENDING — no operator-mode state exists yet. The slot is wired, value awaits. |

### Key mechanism
The resolver is **list-AGNOSTIC** (`runtime/resolver.py` resolves against whatever coordinate it's handed). This registry is the coordinate's VOCABULARY, not a switch the resolver branches on. Adding an axis adds a new dimension without touching the resolver.

### The FORMAL ROOT axes distinction
AGENTS.md explicitly states: **THIS AXIS SET HERE IS THE SURFACE PROJECTION** (device/viewer/mode/type/resolution/state/register, seeded). The FORMAL ROOT axes (the four-root lock · the 3/1 · time-as-meta · state/scale/frame-one-family) are Tim+fork's vault work, Tim-adjudicated. These rows are DATA (swappable); the mechanism survives any root-set. perspective · intent · posture are a-row-away (seed when they get real resolve-usage).

### Gaps / Stale / Surprising
- `viewer.py` has `value_source: "pending"` — the only axis with no live value source. The axis is structurally wired, but nothing reads it yet. This is the named gap for operator-mode/settings state.
- `axes/__pycache__/` has `.cpython-314.pyc` — Python 3.14 (pre-release). All other pyc files too. The system runs on 3.14.

---

## 7. DIALS/ — The Character Trait Registry

### What it is
`dials/` is the **file-discovered dials registry** — the entity's adjustable CHARACTER TRAITS. Born 2026-06-10 (Track-1 brain conversation). A dial turns a would-be design decision into a knob. Values persist on the system graph's `dials` node (same seam as the presence mode) via `Suite.set_dial` / `Suite.dial_state`. MCP face: `mcp_face/tools/dials.py`.

### Dial Row Shape
```python
DIAL = {
    "id": str,           # == file stem
    "label": str,        # human label
    "governs": str,      # the consumer seams (named HONESTLY — including unbuilt ones)
    "positions": [{"name": str, "meaning": str}],  # ordered, non-empty
    "default": str,      # a position name
}
```

### The 2 Dials

| id | Label | Positions | Default | Consumer seam |
|---|---|---|---|---|
| `anticipation` | Anticipation (how far ahead the brain thinks) | reactive · warm · hot | warm | now-organ + resolver when built (GC14/Track-1). **Nothing reads this yet.** |
| `stability` | Stability (how much the surface rearranges itself) | museum · workshop · stage | workshop | RHM surface-composer + resolved-UI layer when built. **Nothing reads this yet.** |

### Condition-scoped overrides
A value record may carry `overrides: [{when, value}]` — condition data in the rules-engine shape. Stored + validated NOW; evaluated once the now-organ + rules wiring exists. Until then: flat value applies, `dial_state` says `overrides_evaluated: False` (never silently).

### Gaps / Stale / Surprising
- Both dials have **no current consumers** — they are configuration seams declared ahead of the consumers that will read them. This is intentional and honest (the `governs` field names the unbuilt consumer).
- `dials/zz_probe.cpython-314.pyc` exists in `__pycache__` but there is NO `dials/zz_probe.py` source file. This is a stale cache entry — a file that was deleted but whose pyc wasn't cleaned. Minor.

---

## 8. THE MAP-COMPUTATION PIPELINE

How the instrument's map is computed, end-to-end:

```
1. STORE events (the company's operational data — every op, chat, corpus write, decision…)
        ↓
2. PROJECTION endpoint (/api/projection?binding=<id>&center=<addr>&rung=<k>&…)
   reads via runtime/projection.py:
   - Loads the BINDING row (bindings/<id>.py) — resolves angle_from, radius_from, etc.
   - Resolves the SECTORS (angle divisions) from angle_from:
       'kind'         → distinct event kinds present in the store (data-driven, zero hardcode)
       'kind-group'   → declared groups from the binding's `groups` dict (glob-match)
       'node-types'   → NodeRegistry.whole_set() — every registered type, with directional edges
       'projections'  → ProjectionRegistry.discovered() — every projections/<id>.py
       'cascade-flow' → saved cascade steps from the governance store
       'nucleation'   → AxisRegistry types + candidate zones from nucleation compute
   - Resolves the RADIUS for each item from radius_from:
       'time'         → age from NOW (normalised, younger = nearer)
       'semantic'     → 1-cosine from center item's vector in `space` (Group 6)
       'separator'    → signed lean between pole_a and pole_b vectors (Group 9)
       'nucleation'   → membership: inside=r<1 (fits a type), outside=r>1 (piles out)
   - Projects each item onto (θ, r) → a ProjPoint
   - For scale: if rung != null, resolves via the pyramid (cluster centroids become themes)
   - Returns: {now, n, rings, count, binding, bindings, sectors, points, edges?, scale?, nucleation?, separation?}
        ↓
3. LatticeView.tsx renders:
   - Canvas 2D draw loop (RAF-driven when live, static when frozen)
   - θ = sector midpoint (angle in radians, 0 at top, clockwise)
   - r = radial function (time/semantic/separator/nucleation/frame)
   - Color IS angle (hsl(θ_degrees, 55%, 58%)) — except separator (pole hues) and nucleation (state hues)
   - The square/grid is the structural coordinate (dyadic cells = address path = grid position)
   - The circle is the temporal/semantic/separator coordinate (inscribed in the square)
   - Connections: directed chords (quadraticCurveTo toward centre)
   - Nucleation: box at R_BOX_FRAC=0.5 × R; fits inside, piles outside + outer zone blooms
   - Scale crossfade: outgoing rung fades out at last positions while incoming fades in
   - Strain overlay: radial segments from r_struct to r (structure↔meaning divergence)
        ↓
4. AXES coordinate the resolver (runtime/resolver.py):
   - The resolver is list-agnostic
   - axes/ provides the coordinate vocabulary (device/mode/register/resolution/state/type/viewer)
   - An invariant resolves against a coordinate → surface (the RESOLVER-CONTRACT)
```

### The embeddable spaces pipeline (Group L)
```
PROJECTION (embeds:True) → embed_corpus_to_spaces() → put_vector(vec://<item>#space=<id>)
→ semantic radius lookup: store.get_vector(address, space=<id>) → cosine vs centre
```

### The nucleation pipeline (20/80 water-law)
```
items in 'space' (e.g. repo) → embed → cosine vs type-centroids from pyramid('types_space', rung)
→ inside/outside determination → candidate cluster → born (distinct + size ≥ birth_mass)
dial (client-side, instant): born = distinct AND size >= dial × pile_clustered
```

---

## 9. CROSS-CUTTING GAPS AND SURPRISES

### Notable gaps
1. **`viewer` axis `value_source: "pending"`** — no operator-mode state built yet. The axis is wired structurally but nothing reads it. (`axes/viewer.py:10`)
2. **Both dials have NO consumers** — `anticipation` and `stability` are declared configuration seams awaiting the now-organ and RHM surface-composer. (`dials/anticipation.py:8`, `dials/stability.py:8`)
3. **`common_knowledge` space is EMPTY** — declared as a projection space, but recollection's publish pipeline hasn't run yet. (`projections/common_knowledge.py:18-25`)
4. **`floor_walk` hardcodes the canvas component dir** (`canvas/app/src/components`) — if that path changes, the detector breaks. (`flows/floor_walk.py:71`)
5. **Flow implementations in `build-prep/`** — `transcript_mine`, `pattern_cluster`, `drift_radar`, `registry_generation` all sys.path into `build-prep/cognition-self-improvement/`. These are scripts that became flows via thin wrappers. The actual logic hasn't been migrated to proper modules.
6. **`ts_backfill` hardcodes transcript dir** — `/home/tim/.claude/projects/-home-tim`. (`flows/ts_backfill.py:62`)
7. **`zz_probe.cpython-314.pyc` in dials/__pycache__** — source file deleted, stale pyc remains.
8. **No `similarity` CONFIG** — intentional (pure function), but if someone wants a configurable tolerance threshold in the future it'll need adding.
9. **LatticeView `dial` is NOT sent as a query param** — client-side compute. This is a deliberate performance optimisation (instant dial response without a round-trip) but means the server and client must agree on the born formula. Documented at line 194 of LatticeView.tsx.

### Notable design patterns
- **Registry-is-truth everywhere**: every directory (nodes/, projections/, bindings/, flows/, axes/, dials/) uses file-discovered self-registration. Drop a file = add an entry. Remove a file = un-register on rediscover. This is the system's universal law.
- **Render-NOT-judge (K3)**: projections DESCRIBE, never judge. Judgement is a separate reduce pass.
- **Fail-loud everywhere**: zero-vector → ZeroDivisionError (not 0.0). Context overflow → ValueError (not truncation). Version mismatch with empty diff → RuntimeError. Model unreachable → 400 (normalized to `{error}`, not swallowed).
- **Proposes-only (flows floor)**: flows NEVER resolve/approve/dispatch/`claude -p`. Computation + corpus writes + surface items only.
- **Selective emission (gate node)**: a multi-output node's `run()` returns `{port: value}` dict; the scheduler writes `set_ref` ONLY for ports present. Branching = absence-of-write. The scheduler is never control-flow.
- **VOLATILE marking**: nodes that read mutable external state (`codebase`, `model_of_tim`, `portal`) MUST set `VOLATILE=True` or the memo gate serves frozen first results.
- **Color IS geometry (LatticeView)**: hue = midpoint angle of the sector. A new registry row re-colors the screen by geometry, never by hand. The only deliberate non-token color.

---

*Exhaustive dragnet complete. Read-only — no edits to existing files.*
