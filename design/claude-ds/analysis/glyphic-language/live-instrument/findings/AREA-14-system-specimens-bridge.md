# AREA-14 — System specimens (the SPEC) + Company bridge/operator/voice surfaces

> Wave-2 COVERAGE agent. Wave 1 read CV_AI, embedders, voice/STT, icons/foundry, no-staleness,
> reactflow/render, data-binding — but it skipped (1) the design-system's OWN self-documenting
> specimens (the glyphic spec + the in-house interactive graph surface) and (2) the Company
> operator/voice surfaces that actually consume a live conversation. This file fills both.
>
> Evidence marks: **Observed (file:line)** = read directly · **Inferred** = pattern-matched, not run ·
> **My-idea** = proposal. Two repos: design system `~/company/design/claude-ds/`, Company `~/company/`.

---

## 0 · The headline (what wave 1 missed, in one breath)

1. **There is already a glyphic-NATIVE live graph renderer with a live read-out** — `system/language.html`
   builds one `{nodes, edges}` graph object → renders it through `DiagramSolver(type:'glyphgraph')` AND
   narrates it back through `CV_MEANING.readGraph`, all from the SAME graph, edges carrying meaning by
   sight (no labels), with **live authoring** (`CV_MEANING.author.setGloss`). This is the closest existing
   thing to the live instrument's RENDER + NARRATE + LOOP stages — and it reframes DECISION 1 (renderer).
2. **There is already an in-house INTERACTIVE graph surface with a typed-operation edit queue** —
   `system/system-map.html` + `build-system-map.js` + `system-map.json`: a generated `{nodes,edges,globals}`
   codebase model, rendered as a drag/click/zoom/morph map, where edits emit a **typed op queue** consumed
   by a Claude-Code disk-write adapter → rescan. This is the "operator mutates → backend-owns-truth →
   re-project" loop the live canvas needs, already worked once, in this very folder.
3. **The Company bridge's `/api/stream` is a seq-numbered SSE bus tailing `events.jsonl`**, and the existing
   `canvas/app` (tldraw) is a full operator console that already runs the **complete live voice circuit**
   (record → `/api/voice/stream` ndjson → transcript/reply/per-sentence-wav → play, with barge-in) AND
   tails `/api/stream` for the live surface. The live instrument is a sibling of this, not a new system.
4. **The transcript today is emitted ONLY inside the `/api/voice/stream` ndjson response, never onto
   `events.jsonl`** — confirming wave 1's "hardwired to one consumer." The fan-out wire to build is exactly
   the existing `_emit(kind, summary, **meta)` → `events.jsonl` → SSE pattern. (Observed, below.)

---

## (a) · WHAT glyphic-system.html + glyphic-foundry.html SAY the system should be — the SPEC we must honor

The live instrument sits ON the glyphic engine. These two specimens ARE the contract for that engine. The
live layer must not contradict them; every claim here is the spec, with what's already BUILT marked.

### `system/glyphic-system.html` — "The Glyphic System" (the living spec, 75KB, viewport 1180×4400)

**Observed** (`system/glyphic-system.html:144-145`): the unit is a **Glyphic** = "a small stack of
**independent, meaning-bearing facets** (an outer form, an inner symbol, the fill between them, colour,
texture, motion, size) … composed generatively and resolved from single sources. Because the facets are
independent, their meanings **multiply** rather than add."

**The facet model (the data contract the pipeline must produce)** — Observed `:524-549` (live `facets[]`
table, each rendered through the real `CV_GLYPHIC.render`):

| Facet | Single home | Range (incl. zero) | Carries (meaning) |
|---|---|---|---|
| **Form** | `CV_SHAPES.geom` | `0 (no ring) · 3–8 sides · ∞ (circle)` | type-class — Entity / Action / System / Gateway |
| **Symbol** | `CV_ICONS.data + .facets` | ~110 glyphs · faceted taxonomy | the specific thing — house / person / drone |
| **Fill** | token (paper/wash/tint) | `none (α0) · paper · wash · tint` | secondary state / grouping |
| **Colour** | `colors_and_type.css` + tokens | any role token, **per part** | an allocated **value** — state OR type OR category |
| **Texture** | `tokens/texture.css` | `none · hatch · dense · cross · grid · lines · vert · dots` | sub-class / material |
| **Motion** | `tokens/motion.css` | `none · breathe · pulse · bob · tilt · spin · float · glow` | liveness / attention / status |
| **Size** | `tokens/icons.css` | `xs → xl` | hierarchy / emphasis |
| **Depth** | `tokens/depth.css` | `flat (0) → raised → deep` | elevation / focus / layering |

**The Glyphic record shape** — Observed `:463-473` (this is the structured output the EXTRACT/RESOLVE
stages must emit; it IS the schema, single-sourced in `CV_GLYPHIC.facets` / `CV_GLYPHIC.schema`):
```
{ form:"octagon", symbol:"globe", fill:"wash",
  color:{ ring:"gold", symbol:"bronze", fill:"gold-50" },
  texture:"none", motion:"none", size:"md",
  value:"active" }   // optional allocated value that DRIVES bindings (state|type|category)
```
**The Symbol record shape** — Observed `:449-461`: `{ id, svg (24×24 stroke currentColor), name,
description, facets:{ domain, kind(object|action|state), tags[] }, provenance(built-in|user|vi|imported) }`.

**What is BUILT vs proposed** (the spec self-marks · BUILT) — Observed `:408-445`:
- Register the unit `CV_GLYPHIC` (`assets/icons/cv-glyphics.js`) · BUILT
- Form axis `{0,3..8,∞}` incl. `form:'none'` (symbol alone) · BUILT
- Faceted symbol taxonomy in `CV_ICONS.taxonomy` (13 domains + 4 kinds) · BUILT
- Schemas (`CV_GLYPHIC.facets` + `validate()` fails loud on unknown value) · BUILT
- **Loadable meaning profiles** `CV_MEANING` — facet→meaning is contextual/swappable, except the symbol
  (intrinsic); a `value` resolves to colour through the **active profile** · BUILT (`:428-429`)
- Glyphic as a registered **universal-component Type** with parts/slots/sockets · BUILT (`:433-434`)
- Modifier facets wired to token homes (`cv-glyphic.css` motion classes; depth ↔ `tokens/depth.css`) · BUILT
- **The foundry** — `glyphic.generate` + `glyphic.save` capabilities BUILT; the **conversational surface**
  marked `· CAPABILITIES BUILT · UI NEXT` (`:443-444`) — this is what `glyphic-foundry.html` then realised.

**The universal-component grammar (the deepest part — bears directly on the live canvas)** — Observed
`:295-396`: a Glyphic is the **first worked example** of a grammar where *everything in any interface is a
typed component that declares its **slots** (values its parts accept) and **sockets** (attachment points
where typed things — or **events** — plug in)*. Sockets resolve via `CV_REGISTRY.slots + accepts() +
candidatesForSocket()` — so "click a socket → show the library of glyphics that fit" needs **no bespoke
code** (`:323`). Three twists the spec reserves: **event-sockets** (`socket.kind:'slot'|'event'` — "on
click, open X"), **addresses** (every occupant referenced by a stable address, never copied), and
**conditions everywhere** (`:327-329`). The condition-evaluator is declared, `accepts()` seeded, full
engine **pending** (`:508`).

> **Spec consequence for the live instrument** (My-idea, grounded in the above): a live-generated glyphic
> on the canvas is **already a Type with declared sockets**. The voice-correction loop ("no, the buyer's
> gone cold") is not a free-text patch — it should resolve to a **slot change** (the `value` facet) or a
> **socket op** (add/remove an edge), which the meaning profile then re-renders. The grammar gives the LOOP
> a typed target, and the `value`→colour binding through the active profile is the no-bespoke-code path for
> "state changes → colour changes" that the anchor's "buyer's gone cold" example asks for.

**The convergence — universal Axes** — Observed `:493-501`: nine axes are live in `window.CV_AXES`
(`color·space·size·motion·texture·depth·fill·form·symbol`), each with the shared
`register/resolve/list/query/subscribe` API; a component's slot is a **subscription**
`{axis, groups?|values?, default, conditions?}`, and a foundry/editor shows exactly `candidates(subscription)`.
→ the live instrument's RESOLVE stage should read candidates from the **axis**, never a hardcoded value
table (this is the no-staleness law expressed at facet level). Detailed scope: `analysis/AXIS-REFACTOR.md`.

### `system/glyphic-foundry.html` — the conversational mark-foundry (the §8 "UI NEXT", now built)

**Observed** (`system/glyphic-foundry.html:1-245`): a working specimen of the propose→feedback→click→
iterate→Save panel. Key, load-bearing facts for the live instrument:
- **Routes through the registry, never raw model** — `:192-195`: `AI.execute('glyphic.generate',
  {surface:'glyphics', params:{brief, count, thread: thread.slice(0,-1)}})`; results `.map(p => p.record)`.
  Multi-step is done by **threading prior turns** (`thread`). Save: `:216` `AI.execute('glyphic.save',
  {params:{record}})`. This is the same `CV_AI.execute` discipline the live instrument's RESOLVE/GENERATE
  stages must use (matches A1).
- **Live-renders candidates AS glyphics** — `:140-143` `previewGlyphic()` temp-registers a candidate's svg
  into `CV_ICONS.data` (persist:false) then `GL.render({form:'circle', symbol:tmpId, fill:'paper'})`. So a
  freshly-generated symbol renders inside a full glyphic immediately — the GENERATE-ON-MISS → render-live
  path the anchor wants (§3 stage 4) is **demonstrated here**.
- **Save is instantly live** — `:218` after save it rebuilds the Symbol axis (`CV_AXES.resolve('symbol')
  .rebuild()`) so a new mark appears in the explorer + axis with no reload. Confirms A4's "live foundry."
- **Live/Demo mode gate** — `:123-126`: `live = !!(window.claude && window.claude.complete)`. **Observed
  limitation:** liveness is gated on `window.claude` directly — this is the single-`claude` assumption A1
  flagged, surfacing in a specimen. When the live instrument adds the role-resolved/company-http provider
  (A1's G-L1), this `window.claude` check must become a `CV_AI.resolveProvider`-based liveness check, or the
  foundry will report "Demo" even when a Company model is bound. (My-idea: a small fix, but on the critical
  no-staleness path — register it.)

---

## (b) · The in-house interactive graph/spatial surfaces to LEARN FROM (the named deliverable wave-1 missed)

There are **three** in-house interactive-graph precedents, all in this folder, all worth copying shape from.
This is the most important wave-2 correction: the renderer DECISION is **not** binary reactflow-vs-tldraw.

### `system/language.html` — the glyphic-native graph renderer + live read-out (the closest precedent)

**Observed** (`system/language.html:118-198`): ONE real meaning-graph object drives BOTH a drawing and a
paragraph:
```
graph = { type:'glyphgraph',
  nodes:[ {id:'pr', form:'circle', symbol:'folder', fill:'none', x:.50, y:.16}, … ],   // facet spec PER NODE + x/y
  edges:[ {from:'ow', to:'pr', line:'solid', kind:'part-of', lineColor:'active', routing:'curved'}, … ] }
```
- **Render** — `:129-161`: fetches `core/DiagramSolver.jsx` from SOURCE, Babel-transforms it in-browser
  (`Babel.transform(stripped, {presets:['react']})`), then `ReactDOM.createRoot(stage).render(
  React.createElement(DiagramSolver, {graph}))`. The SVG node+edge solver renders **glyphics as nodes** and
  edges that **carry meaning by sight** — line texture = mood (solid=is, dashed=could), colour = state
  (green=approved, gold=active), routing+arrow = direction — **with no text labels** (`:54-61`).
- **Narrate** — `:163-182`: `CV_MEANING.readGraph(graph, {focus})` walks the SAME graph object outward and
  returns a `.sentence`; the page covers every source node so the paragraph matches the picture. Per-mark
  read-out is `GL.describe(spec).sentence` (`:82-84`). **This is the NARRATE stage, already built and proven
  on a real graph.**
- **Live authoring** — `:124-126`: `CV_MEANING.author.setGloss('browser','web page')` re-words the read-out
  live (the "AI **and** user author the dictionary live" requirement, demonstrated).
- **Interaction** — `:184-191`: a labels-mode toggle flips `graph.labels` and re-renders the SAME root; hover
  an edge to hear its clause (`:58`). Interaction here is light (toggle/hover), not drag/pan — see system-map
  for the heavier interactive surface.

> **This directly reframes DECISION 1.** Wave-1/synthesis is CORRECT that **reactflow appears nowhere**
> (Observed: `canvas/app/package.json` deps = `react, react-dom, tldraw@3.13.1`; `surface/app` =
> `framer-motion, react, react-dom`; no reactflow in either — I verified). But the choice is **not**
> reactflow-vs-tldraw. There is a **third, already-glyphic-native path**: `DiagramSolver(type:'glyphgraph')`
> + `CV_MEANING.readGraph`, which is the ONLY one of the three that renders glyphics + speaks them today.
> The real grounded question (My-idea): the live canvas wants glyphics that are **interactive** (drag,
> click-a-socket-to-edit, semantic zoom). Today:
> - `DiagramSolver`/`language.html` = **glyphic-native + auto-read-out, but SVG / light interaction**.
> - `canvas/app` (tldraw) = **rich interaction (drag/zoom/ports/edges/semantic-zoom), but renders a generic
>   `node` card, NOT a glyphic** (Observed `canvas/app/src/NodeShape.tsx:16-19` — props are
>   `nodeId/nodeType/kind/status/output/address/ref/layer/error`, drawn as a 240×130 card, no facet spec).
> - reactflow = doesn't exist.
> So the load-bearing decision is: **(i)** render glyphics INSIDE tldraw (a tldraw custom shape whose
> `component()` calls `CV_GLYPHIC.compose/render` — the NodeShape pattern is the template, just swap the
> draw body), giving rich interaction + glyphic marks in one; OR **(ii)** put an interaction layer (drag/
> pan/zoom + socket-click) OVER the working `DiagramSolver` glyphgraph, keeping the auto-read-out for free;
> OR **(iii)** the system-map approach (below) — a bespoke DOM/SVG interactive surface with an edit-op queue.
> All three are render-from-data + backend-owned-positions, so still swappable; but **(i) is the most reuse**
> (NodeShape + the tldraw operator console already exist) and **(ii) gets NARRATE for free**. This is the
> one decision worth putting to Tim with these three rendered side by side.

### `system/system-map.html` + `build-system-map.js` + `system-map.json` — the interactive graph WITH an edit-op queue

**Observed** (`build-system-map.js:1-22`): `system-map.json` is **generated, never hand-edited** — a
codebase model `{nodes[], edges[], globals[], roleCounts, version:2}`. Node = `{id,name,path,parent,
type:'file'|'folder',ext,role,size,defines[],uses[]}`; edge = `{from,to,kind,type:'contains'|'loads'|
'resolves'}` where **type is the bidirectional-verb edge family** (contains↔sits-inside, loads↔loaded-by,
resolves-from↔resolves-into) — `:17-21`. Globals = every `window.CV_*` → its defining file (`:147-149`).
The model is built by a BFS file walk + regex def/use extraction (`DEF_RE`/`REF_RE`/`SRC_RE`/`IMP_RE`,
`:68-72`), role-classified in ONE place (`classifyRole`, `:35-65` — the single-source grouping).

**The interactive surface** — Observed `system-map.html`:
- **Render** — `:208` `<div id="map"><div id="canvas"></div><svg id="edges">` — DOM chips/boxes for nodes,
  an absolutely-positioned SVG overlay for edges (`:102`, `buildEdges`/`drawEdges` `:628`).
- **Layout registry** — `:510-577`: `LAYOUTS = {nested, sunburst, districts, layers}`, each "a deterministic
  projection of the SAME tree into RECT{x,y,w,h,depth}". Switching layouts is a **FLIP morph** (`applyLayout`,
  `:643-688`) — survivors animate via a transform layered over the real geometry (correctness independent of
  the animation completing, `:631-632`). **Add a layout = one registry entry** (`:517`).
- **Interaction** — click → detail panel (`:218-233`, shows role/what/typed relations), drag-to-reparent
  (`:91-96`, `body.dragging-node`), edge-type legend toggles (`:209`), node tooltips, semantic detail.
- **THE KEY PATTERN — a typed edit-op queue (the operator-mutates → backend-owns-truth loop)** — Observed
  `:670-712`: edit mode collects `EDITS=[]` (typed operations, persisted to `localStorage` key
  `cv-sysmap-edits-v1`), with undo/redo over the in-memory model + op queue, and **Export JSON** of the
  queue. The comment `:670-671`: *"emit typed operations (the schema). A disk-write adapter (Claude Code —
  see `analysis/SYSTEM-MAP-EDITOR-ADAPTER.md`) consumes the queue to apply real fs changes, then rescan."*
  → the surface NEVER writes truth directly; it emits a reviewable typed-op queue; an out-of-band actor
  applies it; the model re-scans and re-projects.

> **Why this is gold for the live instrument** (My-idea): this is the EXACT "reflect-never-own /
> backend-owns-positions / typed-mutation-not-direct-write" discipline the Company canvas also uses
> (NodeShape reflects backend state). The live instrument's voice-correction loop should emit the SAME shape:
> a **typed graph-op** (`add-node`, `set-value`, `connect`, `delete-edge`) that the resolver applies and the
> canvas re-projects — not a direct canvas mutation. system-map already proves this loop end-to-end in the
> browser, including undo/redo and a layout registry the auto-place stage (A6) can reuse the FLIP-morph idea
> from for stable incremental growth (a new node morphs in from its prior rect rather than teleporting).
> **Action:** read `analysis/SYSTEM-MAP-EDITOR-ADAPTER.md` when building the apply-side of the loop — it's
> the prior art for "browser op-queue → Claude/backend applies → rescan."

### `system/system-atlas.html` (`@dsCard group, 24KB`) — sibling overview surface; lower priority, skim if needed.

---

## (c) · The Company bridge's REAL API/SSE surface the live instrument consumes

### `/api/stream` — the live event bus (SSE over `events.jsonl`)

**Observed** (`runtime/bridge.py:2119-2151`): `GET /api/stream` is Server-Sent Events that **tails the
SHARED `events.jsonl`** via `SUITE.events_since(cursor)`, writing each event as
`id: <seq>\ndata: <json>\n\n`. Cursor = `?since=` or the `Last-Event-ID` reconnect header (default -1 = from
start) → **gapless reconnect**. Heartbeat every ~15s. NOT routed through `_send` (it holds the socket open;
the server runs `HTTP/1.1` keep-alive specifically so SSE works — `:1426`). Only client-disconnect is
swallowed; every real error fails loud (`:2150`).

**The event shape** — Observed `runtime/suite.py:725-734`: `_emit(kind, summary, **meta)` →
`self.store.append_event({"kind":kind, "summary":summary, **meta})`. So every event is
`{seq, kind, summary, ...meta}`. `_emit` is **lenient** (telemetry must never break the action it records);
a **durable** claim uses `_emit_durable` which fails loud (`:1377`). `events_since(seq)` reads disk every
call (`suite.py:2019`).

**The whole route table is single-sourced** — Observed `bridge.py:32-139`: `BRIDGE_ROUTES` is "the SINGLE
SOURCE of the bridge route table (registry-is-truth)"; `tests/bridge_routes_acceptance.py` greps the
dispatcher's `path ==` literals and fail-louds if the set drifts (both directions). Adding the live
instrument's route(s) means registering here + dispatching — no second list. (This mirrors the design
system's own single-source discipline; a clean place to add a live-instrument endpoint.)

**Routes the live instrument will consume (Observed in `BRIDGE_ROUTES`):**
- `GET /api/stream` (the SSE bus) · `GET /api/now`, `/api/events`, `/api/graph`, `/api/graphs`,
  `/api/object_info`, `/api/cognition_info`, `/api/context`, `/api/surfaced`.
- **Cognition (the EXTRACT/RESOLVE engine A1/A2 names):** `POST /api/cognition/run_role`, `/api/cognition/
  run_items`, `/api/cognition/run_reduce`, `/api/cognition/embed`, `/api/cognition/preview_turn`,
  `/api/cognition/create_role|skill|context`, `/api/cognition/role/propose|edit|dry_run`;
  `GET /api/cognition/models_for_role`, `/api/cognition/inputs`, `/api/cognition/field_types`,
  `/api/cognition/corpus`, `/api/cognition/neighbours`, `/api/roles`. (These are the role-resolved,
  schema-constrained extract calls — confirms A1/A2's "REUSE run_role.")
- **Graph mutation (the apply-side of the LOOP):** `POST /api/node`, `/api/connect`, `/api/move`,
  `/api/delete-node`, `/api/run`, `/api/set`, `/api/act` (the structured `{verb,address,args}` operator
  click → `_dispatch_rhm_action`, 7-verb whitelist, Observed `canvas/app/src/api.ts:126-132`).
- **Voice (the LISTEN/NARRATE stages):** `POST /api/stt`, `/api/tts`, `/api/voice/stt-partial`,
  `/api/voice/finished-thought`, `/api/say`; streaming: `/api/voice/stream`, `/api/voice/turn`,
  `/api/chat/stream`, `/api/chat`.

### The streaming circuits (the LISTEN→THINK→NARRATE shape, already built)

**Observed** `bridge.py:2338-2479` `_voice_stream` (`POST /api/voice/stream?persona=`): hear → think IN
PARTS → speak part-by-part. Reads the recorded audio body, STT (`voice_stt.transcribe`), then drives
`SUITE.chat_parts()` with a brain↔TTS overlap (`_stream_parts`, the pure producer/consumer driver, `:332`).
Emits ndjson events: `{type:transcript,text,ms}` · `{type:part,idx,text}` · `{type:chunk,idx,text,wav_b64,
ms}` (per sentence) · `{type:reply,text}` (assembled, once) · `{type:done,total_ms,reply,parts,chunks}` ·
`{type:error}` (fail-loud). Barge-in: a client `reader.cancel()` closes the socket; `client_gone()` uses
`select`+`MSG_PEEK` to STOP the next synth (`:2384-2397`). `_chat_stream` (`:2153`) is the TEXT-only sibling
(NOOP speak/emit), same `_stream_parts` driver — incremental `{type:part}` then a canonical `{type:done}`
carrying `reply/proposal/action/thread_id/history`.

> **The missing wire, precisely** (Observed + Inferred): the transcript is emitted **only as a
> `{type:transcript}` ndjson event inside the `/api/voice/stream` response** (`bridge.py:2424`) — it is
> consumed by exactly one client (`canvas/app/src/useAppController.ts:2175`) and is **NOT** written onto
> `events.jsonl`, so it never reaches the SSE bus and no second consumer (an extract swarm) can see it. This
> is wave-1's "hardwired to one consumer," now pinned to a line. **The wire to build (My-idea, matches
> synthesis G-L3):** add a `self._emit("voice.transcript", text, turn_id=…, persona=…)` (or
> `_emit_durable` if the extract pass must be exactly-once) at the transcript point, so the transcript
> rides the existing SSE bus → both the brain AND a fan-out extract role see it. This is purely additive —
> the existing one consumer keeps reading the ndjson; the new consumers read `/api/stream`. No new
> mechanism, the `_emit → events.jsonl → events_since → /api/stream` path already exists.

### The browser↔bridge boundary (how a browser app talks to the bridge — the design-system instrument will too)

**Observed** `canvas/app/src/api.ts` + `useAppController.ts`: the canvas is a Vite/React app that talks to
the bridge over plain `fetch` to relative `/api/*` paths (same-origin — the bridge serves the app), reading
ndjson streams line-by-line (`api.ts:112-124` chatStream, `:168-171` voiceStream) and tailing SSE via
`new EventSource('/api/stream?since=' + seq)` (`useAppController.ts:632-701`, dispatched **by event kind**,
auto-reconnect gapless via Last-Event-ID). There is an **operator-session header** layer
(`canvas/app/src/lib/operatorSession.ts`, referenced `:70`) that wraps fetch to add one header; SSE
(`EventSource`) is noted there as the exception. **Open gate (Observed, matches synthesis DECISION 4):** the
design-system instrument runs on its OWN Vite origin (`surface/app` / a new `glyphic/app`), so unless it is
served same-origin by the bridge, the bridge `:8770` must send cross-origin CORS to it — a yes/no to verify,
not a design choice. The cleanest reuse: serve the live instrument the way `canvas/app` is served (same
origin), and the whole fetch+EventSource pattern works unchanged.

---

## (d) · The operator-surface / RHM organ pattern

There are TWO operator front-ends, both relevant:

- **`canvas/app`** (tldraw 3.13.1) — Observed `canvas/app/src/`: the full operator console. Custom shapes
  (`NodeShape.tsx` — one generic `node` shape; `ForagerShape.tsx`), a registry store reachable from inside
  tldraw (`registryStore.ts` — `getOINFO/CONNECT/DRAG_CONN/FORCE_RUN`, `NodeShape.tsx:10`), regions for
  `RhmChat`, `ClaudeChat`, `Walkthrough`, `LatticeView` (a live-projected graph region tailing
  `/api/stream`, `regions/LatticeView.tsx:180-221`), `Inspector`, `Palette`. **Ports come from the registry
  per node-type → a new node-type gets nubs with zero per-type code** (`NodeShape.tsx:52-55`) — the
  render-from-data discipline A6 wants. The full live voice circuit lives in `useAppController.ts`
  (`runVoiceTurn` `:2139`, `speakReply` `:2123`, EventSource spine `:632`).
- **`surface/app`** (framer-motion + React/Vite) — Observed `surface/app/src/`: the RHM / operator surface.
  `App.tsx:451-494` tails `/api/stream` ("THE LIVE SPINE … live, not a viewer") with two EventSource taps.
  `src/rhm/RightHand.tsx` (44KB) is the RHM organ proper (the right-hand walkthrough/review panel; not read
  in depth — optional). Boards, decisions, channels, tools, toggles, source panels.

**The RHM / walkthrough organ (backend)** — Observed: `modes/walkthrough.py`, `nodes/rhm_mode.py`,
`tests/walkthrough_acceptance.py`; routes `POST /api/walkthrough/start`, `/api/guide/start`,
`/api/review/start|next`, `/api/debrief/start`, `/api/journey/start|step|stop`. **Inferred** (route names +
`canvas/app/src/api.ts:194-195` `startDebrief` reuses the walkthrough organ): the walkthrough/RHM organ is a
**guided, turn-by-turn, narrated walk over a surface** — the brain leads the operator through a sequence,
speaking, with a verdict/finished-thought gate. The "live conversation drives a surface" precedent the
anchor §0 asks for is **exactly** this organ + the voice circuit: the brain speaks, the surface re-projects
on each `/api/stream` event, the operator corrects by voice (`/api/voice/stream`), barge-in cancels.

> **The pattern the live instrument inherits** (My-idea): the live instrument IS a new "organ" of the same
> shape — a conversation (`/api/voice/stream`) drives a surface (the glyphgraph canvas) that re-projects on
> `/api/stream` events, with the brain narrating (`/api/say` / read-out) and the operator correcting by
> voice. It should reuse: the EventSource spine (`useAppController.ts` pattern), the voice circuit
> (`runVoiceTurn`/barge-in), the typed-op apply path (`/api/act` / `/api/node` / `/api/connect`), and the
> render-from-data node discipline (NodeShape's "ports from the registry"). The genuinely-novel part stays
> what the synthesis named: the **integrated voice-corrected live NL→glyphgraph loop** — every transport
> and surface primitive under it already exists in these two apps.

---

## CONTRADICTIONS / corrections to the naive layer-1 picture

1. **DECISION 1 is NOT binary (reactflow vs tldraw).** Synthesis is RIGHT that reactflow appears nowhere
   (verified deps). But there's a third, glyphic-NATIVE path it under-weighted —
   `DiagramSolver(type:'glyphgraph')` + `CV_MEANING.readGraph` (`language.html`) — the only existing surface
   that renders glyphics AND speaks them. The real choice: **glyphics-inside-tldraw** (reuse NodeShape +
   console, gain interaction) vs **interaction-over-the-glyphgraph-solver** (reuse the auto-read-out) vs the
   **system-map bespoke surface + op-queue**. Render all three for Tim; the decision is which interaction
   model, not which library.
2. **"reactflow inside the no-script-CSP" (anchor §6) is a non-issue** the way the existing apps solve it:
   `canvas/app`/`surface/app` are **full Vite apps** (npm deps, real bundler), NOT the no-script Studio CSP.
   The CSP caution applies only to the design-system's static specimen pages (which load deps from `unpkg`
   or Babel-transform from source, e.g. `language.html:71-73,129-134`). A live instrument built as a Vite
   app (the `surface/app` sibling) has no such constraint — matches A6.
3. **The foundry's liveness check is the single-`claude` pin, made visible** (`glyphic-foundry.html:124`
   `live = !!(window.claude…)`). When the role/company-http provider lands (A1 G-L1), this must move to a
   `CV_AI.resolveProvider`-based check or the foundry/instrument will mis-report "Demo" with a Company model
   bound. A small but on-the-no-staleness-path fix — register it as a lane.
4. **The transcript-fan-out wire is smaller than "wiring a bus"** — the bus (`_emit → events.jsonl →
   /api/stream`) already exists and is single-sourced; the wire is one `_emit("voice.transcript", …)` call
   at `bridge.py:2424`, plus an extract role that subscribes to `/api/stream` filtering `kind==
   "voice.transcript"`. Additive, no existing consumer touched.
5. **The "operator mutates → backend owns truth → re-project" loop is already proven twice in-house** —
   `system-map.html`'s typed-op edit queue (browser → op-queue → Claude/backend applies → rescan) and
   `canvas/app`'s reflect-never-own NodeShape. The live instrument's voice-correction loop should emit a
   **typed graph-op**, not mutate the canvas directly. `analysis/SYSTEM-MAP-EDITOR-ADAPTER.md` is the prior
   art for the apply-side.

---

## 3-line summary
The SPEC (`glyphic-system.html` + `glyphic-foundry.html`) is BUILT through the universal-component grammar: a
Glyphic is a typed record of orthogonal facets, single-sourced, with declared slots/sockets and a loadable
meaning profile that turns an allocated `value` into colour — so the voice-correction loop has a typed target
(a slot/socket op), not free-text. The biggest wave-1 miss: **`language.html` already renders a glyphgraph
AND speaks it from one graph object** (reframing DECISION 1 to a 3-way interaction choice, not reactflow-vs-
tldraw), and **`system-map.html` already runs an interactive graph surface with a typed edit-op queue**
(the operator-mutates→backend-owns-truth loop). On the Company side, `/api/stream` is a seq-numbered SSE bus
over `events.jsonl` (`_emit`→`events_since`), the full live voice circuit + EventSource spine already run in
`canvas/app`/`surface/app`, and the only missing wire is one `_emit("voice.transcript", …)` to fan the
transcript (today hardwired into the `/api/voice/stream` ndjson) onto the bus for an extract swarm.

Path: /home/tim/company/design/claude-ds/analysis/glyphic-language/live-instrument/findings/AREA-14-system-specimens-bridge.md
