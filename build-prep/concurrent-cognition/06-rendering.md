# 06 · Rendering the Concurrent-Cognition Layer — a live thought-graph on the canvas

> **Status: open / provisional / design surface (open-future).** This is the *rendering chapter* of the concurrent-cognition / collective-cognition work. It is grounded in a **code read of `~/company` (file:line cited)** and in the vault spine [[Collective Cognition — the context-resolution spine]] (§9 item 5 "cognition made visible — the commander's bridge", §10 "how the cascade surfaces visually — render-for-cognition"). It is a surface to refine **with Tim**. Epistemic tags follow the repo rule: **Observed** (read in code), **Designed** (intended, not built), **Open** (decide with Tim).
>
> **The one sentence:** because the concurrent-cognition layer is **registry-defined data** (roles, chains, per-turn runs, injections, configs, outputs, destinations), it must — like every other typed thing in the Company — have **render rules** that project it to a **live, interactive cognition view**: roles as nodes, chains as edges, injections as edges into the main conversation stream, lit by the addressed event stream as a turn fires — *not a text wall* (AGENTS.md rule 9 — a navigable visual/spatial surface).

---

## A · Where the series stands (orientation, honest)

This `concurrent-cognition/` directory contained **only this `06-` task** when written — no `01–05` were present in the repo (checked: `build-prep/concurrent-cognition/` was empty). The **conceptual 01–05 lives in the vault** as two notes (Observed by read):
- `Collective Cognition — the context-resolution spine.md` — the layered cognition model (conscious/pre-conscious/subconscious/senses/world), activation spectrum (per-turn · per-activity · background · trigger), the typed-triage law, the write-half, budget=attention, and the **explicit "render-for-cognition" open question (§10)** this doc answers.
- `context-07-the-cognitive-fabric.md` — the cognitive-fabric framing.

So this doc binds its render rules to the **data model those notes + the live `ROLE_REGISTRY` define**, not an invented one. Where the data model is not yet built, that is named as **net-new backend** (§F), and the render rules state their emit-contract dependency explicitly — a render design that binds to event kinds nothing emits would float.

**Assumption (stated, per the evidence rule):** the layer's render-time data model = `ROLE_REGISTRY` (roles) + the C6 `context_variables.REGISTRY` (faculties/injections, each with a `cost`) + the per-turn event trace on the one event log. If a future `01–05` pins a different registry shape, the **reuse spine (§G) still holds** (SSE → dispatch branch → canvas siblings); only the field names in §C/§D rebind.

---

## B · The rendering substrate (Observed — what already exists, file:line)

The canvas is a **generic reflects-never-owns renderer**: it holds no per-type code, it projects from backend registries served over HTTP, and it stays live via one seq-cursored SSE stream. Every piece the cognition view needs is already proven for *nodes*. The work is **a sibling projection**, not new machinery.

### B.1 · The shell + region layout
- `canvas/app/src/App.tsx:116–236` — `Hud()` builds the controller once (`useAppController(editor)`), provides it via `AppContext`, and lays regions into a **CSS-grid shell** (`.app-shell`, areas top/rail/canvas/panel/foot) layered over the tldraw board; the `as-canvas` cell is `pointer-events:none` passthrough so overlays (Walkthrough, OpPanels, Activity, RhmChat) sit *over* the live board (`App.tsx:147–174`). Each region is wrapped in a `PanelErrorBoundary` (`App.tsx:134,148,157,186…`) — a render-throw degrades to a contained card, never a white-screen.
- A new cognition view drops in here as **one more region** (a `as-canvas` overlay or a rail panel), wrapped in its own boundary — zero shell surgery.

### B.2 · How nodes / edges / graphs render (the exact analogy)
- `canvas/app/src/NodeShape.tsx:30–184` — `NodeShapeUtil` is **one generic tldraw shape** for *every* node-type. It reads its draw-truth from the registry store: ports come from `getOINFO()[p.nodeType]?.ports` (`NodeShape.tsx:53`), so a new node-type gets nubs with **zero per-type code** (C1). Status is driven *by sight* from the served registry: `getNODE_STATES()[p.status]` (`NodeShape.tsx:64`) → `def.render.token` colours the dot (`NodeShape.tsx:83–87`), `def.render.shape` (`dot`|`ring`) distinguishes compute vs reference nodes. The card carries its **live instance address** as `data-ui-ref={p.address}` where `p.address` is `run://<graph>/<node>` (`NodeShape.tsx:140`).
- `NodeShape.tsx:194–238` — `loadGraph(editor)` / `refresh()`: update-or-create-or-**prune** shapes from `api.graph()`; **backend `n.position` is the single source of layout truth** (`NodeShape.tsx:201,209`) — the canvas never invents coordinates.
- `NodeShape.tsx:243–278` — `Edges({edges})`: a reactive **screen-space SVG overlay**. Each wire anchors on the exact port (y-offset by port index via `portTop`, `NodeShape.tsx:26–28,249–254`), page→screen via `editor.pageToScreen` (`NodeShape.tsx:264–265`), stroked `var(--acc-dim)`. Edges carry `from_port`/`to_port`, **backend-owned** (`NodeShape.tsx:243`).

### B.3 · The ui_info / object_info registry pattern (one source → UI projects)
- `runtime/registry.py:74` `object_info()` → `contracts/object_info.py:61` `build_object_info(node_types)`: serializes the C2 `NodeType` library to `{ "<name>": {title, category, kind, ports, config_schema, render_set, inspector_schema, actions, version} }`. **Generated from the registry, never hand-written** (`object_info.py:7–10`); fail-loud if a key disagrees with the type's own name (`object_info.py:79–83`, rule 3). The FE is a generic renderer that re-merges this — "add a node-type → it appears live, no FE code" (`object_info.py:8`).
- `runtime/suite.py:5062–5081` `build_ui_info()` is the **sibling of object_info** for UI components: serializes `UI_REGISTRY` (`suite.py:5027–5060`) to `UiComponentEntry` rows `(ref, kind, title, dom_handle|camera_ref, caps)`. Served at `/api/ui_info`. `_load_corpus_element_addresses()` (`suite.py:30–`) projects the 24+ element addresses from `design/_system/addresses.json` — **read, never invented** (rule 8).
- `runtime/suite.py:457–505` `capabilities()` is **the reflective fold**: one snapshot of what exists — `node_types`, `models`, `modes`, `mode_directives`, `rhm_verbs`, **`node_states`** (the status vocabulary the dot reads), `panels`, `composition_config`. This is where a `roles` / `cognition` block belongs (§F).
- `data-ui-ref` handles: every chrome region carries one (`data-ui-ref="activity"` `Activity.tsx:9`; `="walkthrough"` `Walkthrough.tsx:12`), and a node carries its live `run://` address (`NodeShape.tsx:140`). The backend `resolve_scope`/`show` resolver matches these; the orphan check (`tests/ui_registry_acceptance.py`) requires **every used `data-ui-ref` to be a registry entry** (`run://` instances excluded). A cognition view's controls must therefore each be either a registered `ui://cognition/…` entry **or** a live `run://`/`cog://` instance (deliberately bare, like the node card).

### B.4 · How the canvas reflects backend-authoritative state (reflects-never-owns)
- `canvas/app/src/registryStore.ts:1–82` — the 6 module globals → ONE external store (`OINFO`, `MODEL_OPTIONS`, `UI_INFO`, `NODE_STATES`), read via `useSyncExternalStore`, **reachable from inside tldraw** (the shape renders below `<Tldraw>` and can't see Hud React context). **Every field is read-truth from the backend or a controller-installed hook** (`registryStore.ts:10–13`) — the store NEVER becomes a second source of graph truth.
- Backend authority: graph state, node status, edges, positions all come from `api.graph()`; the canvas updates shapes to match and prunes orphans. The cognition view inherits this discipline exactly — it **mirrors** a cognition run, it never owns it.

### B.5 · The SSE event flow (the live engine — G)
- `store/fs_store.py:414–455` `append_event(event)`: appends `{seq, ts, **event}` to the shared `events.jsonl` under a store-level lock (seq atomic+monotonic+unique, T1-SEQ), fsync'd (durable). Events carry an optional **`address`** (the locus) — e.g. `chat` events are emitted `address="ui://chrome/chat"` (`suite.py:3528`).
- `runtime/suite.py:285–294` `_emit(kind, summary, **meta)` (lenient telemetry — narration/visibility); `suite.py:342–351` `_emit_durable(...)` (fail-loud claim — for safety-critical writes). `suite.py:296–306` `emit_run_record(op, duration_ms, **conditions)` → `kind="op.run"` carrying **per-stage timings** (`stt_ms/think_ms/tts_ms/queue_ms/chunks…`, `suite.py:335`). `run_stats()` (`suite.py:308–340`) rolls these into n·median·p95 distributions — the introspective-data read-half.
- `runtime/bridge.py:323–355` `_stream(q)`: `GET /api/stream` SSE. Tails the shared `events.jsonl` (captures BOTH faces), pushes `id:<seq>\ndata:<json>\n\n`, cursor = `?since=` or `Last-Event-ID` (gapless reconnect), 15s heartbeat.
- `canvas/app/src/useAppController.ts:355–409` `openStream()`: ONE `EventSource('/api/stream?since=' + cursor)`. Every event is **merged into the log by seq** (`mergeEvents`, `useAppController.ts:188–193`, dedupe → `key={e.seq}` unique → fixes the render-loop), then **dispatched by kind** to the precise refresh (`useAppController.ts:369–403`): `run/create/connect/delete/move` → `loadGraph`; `mode/config` → now+cfg; **`decision.*` → inbox+now** (the `startsWith('decision.')` branch, `useAppController.ts:384–390`); `chat/react` → chat history (`useAppController.ts:391–393`); `review.*` → walk refresh (`useAppController.ts:394–400`). **This is the exact extension point**: a `cognition.*` branch mirrors the `decision.*` one.

### B.6 · How a graph + its live run-state surfaces today (node states, edges, event stream G)
- A run fires (`POST /api/run`, `bridge.py:616`), the scheduler resolves nodes, the backend emits a `run` event carrying the scheduler's `stuck`/`ran` arrays. The SSE `run` branch calls `loadGraph` + `applyStuckFromEvents` + `paintStuck` (`useAppController.ts:371–376`) so node dots repaint by sight (`idle/ran/cached/stuck/failed/live/empty`, all registry-driven via `NODE_STATES`).
- `Activity.tsx:6–25` — the live feed: `now` summary (`graph · nodes_resolved/total · awaiting`) + the event list keyed by `e.seq`, each row `ev-<kind>`. `now()` (`suite.py:880–904`) gives the presence snapshot.

### B.7 · The RHM / walkthrough organ + modes view (Observed)
- `Walkthrough.tsx:8–62` — the review organ: a card shown while a session is active (`data-ui-ref="walkthrough"`), framing + per-step verdict controls (`approve/reject/comment/skip/decide`), voice/text toggle, `wtBusy` concurrency guard, operator-only verdicts via `/api/resolve`. SSE `review.advance/start` refreshes it (`useAppController.ts:394–400`). **This is the precedent for an interactive, server-authoritative, step-by-step organ** — the debrief flow already reuses it (STATE.md). A cognition view's "inspect a turn step-by-step / replay a cascade" affordance can reuse this session-walk shape.
- Modes: `MODES`/`MODE_DIRECTIVES` (`suite.py:907,1032–`) exposed via `capabilities().modes`/`mode_directives` (`suite.py:463–469`); rendered as the presence dial (Settings/Toolbar). The cognition view should **read the active mode** because the activation spectrum (per-turn / watch-and-react / background, spine §2.5) decides *when* a cascade fires.

---

## C · The cognition data model → render rules (the projection)

The layer is **data**: roles, chains, per-turn runs, injections, configs, outputs, destinations. Render rules are the typed projection from that data to a visual form — exactly as `object_info` projects node-types to palette+cards. The mapping:

| Cognition datum (registry/event) | Visual primitive | Render rule (token-driven, by sight) |
|---|---|---|
| **Role** (`ROLE_REGISTRY[id]`: label/description/trigger/output/tools/context + effective model) | a **cognition node** (NodeShape-sibling: `RoleShape`) | card titled by `label`; sub-line = effective model + base_url; a **status dot** from `node_states`-style tokens (idle/firing/ran/failed); body = last output (truncated); `data-ui-ref` = its live instance address — **either reuse `run://<turn>/<role>` (already a registered shape, preferred) or a new `cog://` scheme (a CONFIRM-level C1 contract decision — see §H, not settled)** |
| **Chain** (role→role dependency: judge gates brain; cascade `focus→embed→recall→rerank→digest→compose`, spine §2.5#5) | an **edge** (Edges-sibling) | a directed wire role→role; stroke `var(--acc-dim)`; animated/brightened while that hop is *firing*; labelled by the hop kind (gate / feed / digest) |
| **Per-turn run** (a turn fires N roles concurrently) | a **turn frame** (a tldraw group / a swimlane band) | the swarm for one turn grouped under a turn header (`turn <seq> · mode · <ms>`); concurrent roles laid side-by-side (concurrency is the point, spine §8) |
| **Injection** (a resolved C6 faculty / role output entering the conscious field; `context_variables.REGISTRY`, each with `cost`) | an **edge into the conscious/brain node** | a wire from the faculty/role shape → the **brain shape** (the conscious is itself a node on the cognition canvas, so this is the `Edges` shape→shape mechanism, reuse genuine); edge weight/colour = `cost` (`cheap`/`loads-model`/`loads-corpus` → thin/med/thick); tooltip = what was injected + char-budget. **(Net-new geometry note:** a wire terminating at the **DOM** `ui://chrome/chat` region — not a tldraw shape — is *not* the `Edges` page-bounds mechanism; that variant is net-new. The design therefore lands injection edges on the **brain shape**, and the brain→voice hand-off to the chat region is a separate visual cue, not a shape-to-shape edge.) |
| **Config** (effective model, knobs, persona, mode) | inline on the role card + a config affordance | rendered from `roles()`/`knobs_for()` with the **same `NodeConfigForm`** the node inspector uses (`suite.py:3158–3221` already shapes knobs in the node config_schema shape) |
| **Output** (the role's JSON / verdict) | the card body + an inspector panel | the raw JSON on click (the History/Inspector pattern) |
| **Destination** (where the injection landed: which turn, which address) | the injection edge's *target* | the edge terminates at the conscious node / the `ui://chrome/chat` lane; the addressed event carries the locus so the canvas knows where to draw it |

**Node-state vocabulary for cognition (Designed, registry-defined like `NODE_STATES`):** `latent` (a role declared but not bound/loaded — the VRAM-latent subconscious, spine §5) · `firing` (the role's model call is in flight) · `ran` (returned) · `injected` (its output entered the field) · `failed` (raised) · `abstained` (the RHM's grounded-abstain). These get a `render.token` each (a corpus design-token), so the dot paints by sight — **register a state engine-side → it paints, no FE edit** (the exact `NODE_STATES` pattern, `NodeShape.tsx:64,83–87`).

---

## D · The live cognition view (the design)

**One picture (the commander's bridge, spine §9#5 — "you see it think"):**
```
   ┌─ turn 412 · listening · 1.84s ───────────────────────────────────┐
   │                                                                   │
   │   [judge ●ran]──gate──▶ [BRAIN ●firing] ◀──inject(loads-corpus)── [recall ●ran]   │
   │     463ms                deepseek-v4-pro      thick edge          vec:// 8 hits     │
   │                              ▲                                                      │
   │             inject(cheap) ───┘                                                      │
   │   [model_of_tim ●injected]   [selection ●ran]   [trajectory ●ran]                  │
   │        thin edge                                                                    │
   └──────────────────────────────────────────────▶ ui://chrome/chat (the one voice) ──┘
```
- **Roles as nodes**: each fired role is a card with a by-sight status dot. The **conscious/brain** is the focal node (visually larger / centered — the one coherent voice, spine §8). Auxiliary roles (judge) and faculties (recall/selection/trajectory/model_of_tim) surround it.
- **Chains as edges**: directed wires show the cascade order (`focus→embed→recall→rerank→digest→compose→inject`, spine §2#5). A hop **brightens while firing** (driven by the SSE `cognition.role.*` events).
- **Injection edges into the brain node**: every faculty/role that fed the brain draws an edge **into the brain shape** (a tldraw shape on this canvas, so the `Edges` page-bounds mechanism genuinely applies) — so the operator literally sees *what got injected*. Edge weight = `cost` (attention/working-memory, spine §5). The brain → the one voice (`ui://chrome/chat`, a DOM region) is shown as a **terminal cue** (a glow/arrow toward the chat lane), **not** a shape-to-shape edge (that geometry would be net-new).
- **Live run status (per turn)**: as a turn fires, dots go `latent→firing→ran→injected`; timings appear (`emit_run_record` per-stage ms); the turn header shows total. A failed/abstained role is loud (red token, the message on the card) — fail-loud at the surface (rule 4).
- **Interactivity** (it IS a view, not a readout): click a role → its **full JSON output + effective config** in the Inspector (reuse `Inspector.tsx`); click the turn header → a **step-by-step replay** of the cascade reusing the **walkthrough session organ** (`Walkthrough.tsx`); click a role's config → live re-bind via `set_rhm_config`/role-binding (the config lab, STATE.md G8) — *operator-gated*; click an injection edge → what was injected (the resolved bundle slice + budget).
- **Driven entirely by the addressed event stream**: no polling. The view subscribes to the same `EventSource`; a `cognition.*` SSE branch (mirroring `decision.*`, `useAppController.ts:384`) folds each role-fire / injection into the turn frame. Events carry a **locus address** so the canvas knows where to paint — `ui://cognition/<turn>` (a registered ui:// row) for the turn, and a per-role instance address that is **either `run://<turn>/<role>` (reuse) or a new `cog://` scheme (CONFIRM-level, §H)**.
- **Also the right-hand-man's own view**: because the thought-graph is itself **addressed data on the event log + registry**, the RHM can *read its own cognition* the same way it reads any context — `ui://cognition/<turn>` is a resolvable address (the I1 click-to-indicate / `_chat_context` path), so "show me what I was thinking on turn N" / self-explanation is the same machinery, not a second surface. The view serves operator **and** RHM from one substrate (rule 3).
- **Modes-aware**: the view reads the active presence mode; in `watch-and-react`/`background` (spine §2.5) cascades fire without an operator turn — the view animates those autonomic runs too ("it already knew", spine §9#1). In `focus`/`off` the view is calm/empty.

**Two zoom altitudes (render-for-cognition, Tim recognises by shape):**
- **Glance** (zoomed out / collapsed): one turn = one band; just dots + the brain + a heat of injection edges. "How much thinking, how parallel, what fired."
- **Inspect** (zoomed in / a turn expanded, semantic zoom like `NodeShape.tsx:49 expanded = zoom>0.5`): full role cards, configs, JSON, timings, the cascade order.

---

## E · Reuse — what already exists (do NOT rebuild)

| Need | Reuse (Observed) | Why it fits |
|---|---|---|
| Live transport | `GET /api/stream` SSE + `openStream()` + `mergeEvents` seq-dedup (`bridge.py:323`, `useAppController.ts:188,355`) | seq-cursored, gapless, both-faces, render-loop-safe — add a `cognition.*` dispatch branch only |
| Registry → UI projection | `build_object_info` / `build_ui_info` / `capabilities()` (`object_info.py:61`, `suite.py:5062,457`) | the cognition registry serializes through a **sibling builder**; FE re-merges generically |
| Role/config truth | `roles()` / `resolve_role()` / `knobs_for()` (`suite.py:3158,3172,3198`) | roles already self-describe (label/trigger/output/tools/context + effective binding) — a render-ready shape exists |
| Node + edge rendering | `NodeShapeUtil` + `Edges` + `portTop` (`NodeShape.tsx:30,243,26`) | `RoleShape`/cognition-`Edges` are **siblings** — one generic shape, registry-driven ports/status |
| Status-by-sight | `capabilities().node_states` + `getNODE_STATES()` + `render.token` (`suite.py:475`, `registryStore.ts:38`, `NodeShape.tsx:64`) | register cognition states engine-side → dots paint, **no FE edit** |
| Per-stage timings | `emit_run_record` / `run_stats` (`suite.py:296,308`) | the turn header + role timings read these; the introspective-data loop already carries `think_ms` etc. |
| Step-by-step inspect | the walkthrough session organ (`Walkthrough.tsx`, `/api/review/*`) | a cascade replay reuses the proven server-authoritative walk |
| Inspector / config form | `Inspector.tsx` + `NodeConfigForm` (`suite.py` knob shape) | role JSON + live re-bind reuse the node inspector |
| reflects-never-owns + boundaries | `registryStore.ts` + `PanelErrorBoundary` (`App.tsx:134…`) | the cognition view mirrors a run; a throw degrades to a card |
| Addressing | `ui://`/`run://`/`cog://` + `data-ui-ref` + `resolve_scope` (`suite.py:5095`) | each role instance is a live address; controls register or stay bare like node cards |

---

## F · Net-new — what must be built (named honestly; backend FIRST)

The layer is **seeded, not built**: `ROLE_REGISTRY` has exactly **one** role (`judge`, `suite.py:929–958`); there are **no chains/runs/injections as data**; `chat()` is a **single primary turn** that assembles context by hand (spine §3 Observed gap) and emits **one** `chat` event addressed to `ui://chrome/chat` (`suite.py:3528`) — it does **not** separately emit the judge fire or the injected faculties. So a render design that binds to `cognition.*` events is **floating until the backend emits them**. Net-new, in dependency order:

**Net-new BACKEND (the render rules' hard dependency — stated as an emit-contract):**
1. **The cognition registry as data** (Designed): more `ROLE_REGISTRY` roles than `judge`; a **chain** declaration (role→role dependencies / the cascade `focus→embed→recall→rerank→digest→compose`, spine §2#5); the C6 faculties (`context_variables.REGISTRY`) treated as injection sources with their `cost`. Serialized via a **`build_cognition_info`** sibling of `build_object_info`, exposed in `capabilities()` as a `roles`/`cognition` block (the reflective-fold home, `suite.py:457`).
2. **Wire the conscious to the resolver** (spine §3 UNBUILT #1 — "step one"): `chat()` resolves its field through `resolve_context(TurnContext, names)` instead of by-hand, so injections are **real data**, not prose.
3. **Per-turn run + injection EMISSIONS** (the emit-contract the view consumes): when a turn fires, emit addressed events on the one event log via `_emit` —
   - `cognition.turn.start` `{turn, mode, roles[]}` address `ui://cognition/<turn>`
   - `cognition.role.fire` / `cognition.role.ran` `{turn, role, model, ms, output_ref}` address = the role instance (`run://<turn>/<role>` reuse, or `cog://…` if that scheme is confirmed — §H)
   - `cognition.inject` `{turn, source, cost, chars, into}` address = the source instance
   - `cognition.turn.done` `{turn, total_ms}`
   These mirror the `run`/`decision.*` event shapes (durable for the run, lenient for narration) and reuse `emit_run_record` for timings. **Without these, §D does not light up.**
4. **Cognition node-states registered** (`latent/firing/ran/injected/failed/abstained`) into a `NODE_STATES`-style set with `render.token` each, exposed in `capabilities()` — so the dot paints by sight with no FE hardcoding.
5. **`ui://cognition/*` registry rows** in `UI_REGISTRY` (read/projected, not invented) so the view's controls pass the orphan check.

**Net-new FRONTEND (the cognition view):**
6. A **`CognitionView` region** (new `regions/Cognition.tsx`), wrapped in `PanelErrorBoundary`, placed in the shell (an `as-canvas` overlay or a rail panel) — reads `cognition` from registry/capabilities, subscribes via the controller's stream.
7. A **`RoleShape`** (NodeShape-sibling) + a **cognition `Edges`** variant for chain + injection wires (sibling of `NodeShape.tsx:243`), or — if the cognition view is a *separate* canvas — its own tldraw instance; **Open (§H)** whether it overlays the node canvas or is its own surface.
8. A **`cognition.*` SSE dispatch branch** in `openStream()` (`useAppController.ts:355`) folding role-fires/injections into turn frames + repainting role dots — mirrors the `decision.*` branch (`useAppController.ts:384`).
9. Registry-store fields for cognition (`COGNITION`/role index) in `registryStore.ts` so the shape (inside tldraw) can read role draw-truth.

**Net-new acceptance (prove by execution, STATE.md bar):** a `cognition_render_acceptance.py` that fires a turn, asserts the `cognition.*` events are emitted with addresses, and (browser/by-use) that the view lights roles + injection edges from the live stream.

---

## G · The reuse spine, asserted crisply

> Backend serializes the **cognition registry** via a `build_object_info`-sibling + emits **per-turn run/injection events** addressed to `ui://cognition/…` + the role instance address (`run://…` reuse, or a confirmed `cog://` — §H) → the existing **SSE `/api/stream`** (seq-cursored, `mergeEvents`) → `openStream` gains a **`cognition.*` dispatch branch** (mirror the `decision.*` one, `useAppController.ts:384`) → the canvas renders **roles via a `NodeShape` sibling** (status dot from `node_states` render-tokens), **chains via an `Edges` sibling**, **injections as `Edges` into the brain shape** (the brain is a node on this canvas, so the shape→shape `Edges` mechanism holds; the brain→chat-region cue is a separate terminal glow, net-new) — all **reflects-never-owns**, each in a `PanelErrorBoundary`.
>
> **Reused:** SSE transport, ui_info/object_info serialization, `NodeShape`+`Edges`, `node_states` tokens, `roles()`/`knobs_for()`, the walkthrough organ, the Inspector/config form, the addressed-event log. **Net-new:** the cognition registry + the per-turn `cognition.*` emissions (backend) and the cognition view region + `RoleShape`/cognition-`Edges` + the SSE branch (frontend).

This is the same law as everywhere (rule 3, one source; rule 9, navigable visual surface not a text wall): the cognition layer is data; render rules project it; the surface reflects it live.

---

## H · Open questions — decide WITH Tim

- **Own surface vs overlay.** Is the cognition view its **own canvas** (a "thinking" board you switch to), an **overlay** on the node canvas (cascade lights up *on the graph*), or a **rail panel**? (Spine §9#5 implies it can be *on* the canvas — the address lighting up its relations.)
- **Persistence / replay.** Does the view show only the **live turn**, the **last N turns** (a scrollback of thought-frames), or a **fully replayable history** (reuse the journey-replay / walkthrough)? Per-turn frames accumulate fast.
- **Cognition node-state vocabulary.** The §C set (`latent/firing/ran/injected/failed/abstained`) is a proposal — the exact states + their render-tokens are a registry decision (mirrors how `NODE_STATES` was settled).
- **What counts as a "role" node vs a "faculty" node.** ROLE_REGISTRY roles (judge, future) and C6 faculties (recall/selection/trajectory/model_of_tim) are both injection sources — render them as one node kind, or visually distinguish conscious/auxiliary/faculty/sense layers (the spine's 5 layers)?
- **Background/proactive runs** (spine §2.5 outbound). When a cascade fires with **no operator turn** (watch-and-react/background) or the RHM **contacts Tim**, how does the view show it — a calm ambient pulse vs the full frame? Ties to the registered-events/triage registry (still open in the spine).
- **Budget visualization.** Show the VRAM working-set (awake vs latent subconscious, spine §5) *in* the view (latent roles greyed), or keep that to the fleet/ops surface?
- **Address scheme — `cog://` vs reuse `run://` (CONFIRM-level).** A role instance / injection needs a live address. Inventing a **new `cog://` scheme is a C1 contract-widening decision** (rule 8 — never invent; AGENTS table — "a new contract → CONFIRM"); the existing schemes are `run:// cas:// blob:// vec:// ui://`. Default lean (cheaper, no new contract): **reuse `run://<turn>/<role>`** for instances + the registered `ui://cognition/<turn>` for the turn. Confirm with Tim before minting `cog://`.
- **Aesthetic / tokens.** The render-tokens for cognition states, edge weights for `cost`, the turn-frame chrome — all on the design system, **design-critic + design-lint gated** (rule 9); the amber-style cues are needs-tim.

---

## I · Sources
- **Code read (Observed), this session:** `canvas/app/src/App.tsx` (shell/regions/boundaries), `NodeShape.tsx` (shape/Edges/loadGraph/status-by-sight), `useAppController.ts` (SSE `openStream`/`mergeEvents`/by-kind dispatch), `registryStore.ts` (reflects-never-owns store), `regions/{Activity,Walkthrough}.tsx`; `runtime/suite.py` (`capabilities`, `build_ui_info`/`UI_REGISTRY`, `ROLE_REGISTRY`/`roles`/`resolve_role`/`knobs_for`, `_emit`/`_emit_durable`/`emit_run_record`/`run_stats`, `chat`/`now`, `MODES`/`MODE_DIRECTIVES`), `runtime/registry.py` + `contracts/object_info.py` (object_info projection), `runtime/bridge.py` (`_stream`), `store/fs_store.py` (`append_event`/`events_since`), `runtime/context_variables.py` (C6 REGISTRY/cost).
- **Vault spine (Observed by read):** `Collective Cognition — the context-resolution spine.md` (esp. §2.5 cascade, §3 EXISTS-vs-UNBUILT, §5 budget=attention, §9#5 commander's-bridge, §10 render-for-cognition), `context-07-the-cognitive-fabric.md`.
- **Governing rules:** AGENTS.md rule 3 (one source), rule 4 (fail loud), rule 8 (author from the registry), rule 9 (navigable visual surface, FORM is half of done, design-critic + design-lint). Memory: [[project-collective-cognition]], [[project-native-model-layer]], [[feedback-render-for-cognition]], [[project-company-one-entity]].
