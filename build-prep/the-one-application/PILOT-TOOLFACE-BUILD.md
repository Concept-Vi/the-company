# The Pilot Tool-Face — dynamic, open-world, chains+graph, resolver-driven (build spec)
*Tim 2026-06-20 (autonomous window, restart-pending). Directive, decompressed: every tool exposed for PILOT mode — NOT handcrafted, NOT static — DYNAMICALLY loaded from what's actually there, auto-IN-SYNC with any backend change. Exposed with INTERACTIVE GAME-DESIGN mentality (like an open-world game). Immediate integrations with the CHAINS + GRAPH-EXECUTION system so he can MAKE then EXECUTE runs on LOCAL MODELS (pilot OR standard mode). Mine the OLD dev UI (still on the company) for the graph/chain pieces → rebuild into the new UI. ALL token/registry/resolver-driven — single-place-dynamic, any company change auto-reflects. Rides [[the-invariant-application]] + RESOLVER-BUILD.md + TOOL-FACE-BUILD.md.*

## THE CONSTRAINT (honest — shapes what's now vs post-reboot)
chrome-devtools is DOWN (no by-sight verify now) + the bridge `/api/tools` is 404 until the reboot. So LIVE build + by-sight verification of the surface is largely POST-REBOOT. This window = RESEARCH (mine the old UI) + DESIGN (the open-world frame) + SPEC + CODE-that-doesn't-need-live-verify (the archetype, the integration wiring). The reboot is the verification enabler — it brings `/api/tools` live + reconnects chrome-devtools.

## THE FOUR REQUIREMENTS (Tim's, mapped to the build)
### 1. DYNAMIC tool-loading — from what's actually there, auto-in-sync
- The tool list resolves from the LIVE FastMCP registry via `/api/tools` (fork's 6471807 — machine truth {name, inputSchema, posture} JOINED with form_meta from mcp_face/tool_meta.json). NEVER a hardcoded list. A new/changed tool in the backend → appears/updates in the UI with ZERO UI-code edit (registry-is-truth). This is the invariant-law applied to the tool surface: the tool SET is content, the UI is list-agnostic.
- ★ The render must go THROUGH the resolver/archetype (NOT bespoke React) so "dynamic + token/registry/resolver-driven" is real: a `tool-card` archetype (TOOL-FACE-BUILD gap 4) renders description+form+result; the form engine (projection's schemaForm, already generic) feeds it. CONTENT through the archetype (the law); the modal HOST stays a thin React frame whose layout computes from the device-axis (the content/host line, RESOLVER-BUILD).

### 2. OPEN-WORLD GAME-DESIGN interface — explorable, spatial, not a menu-wall
The pilot UI realized as a navigable WORLD, not a list of buttons. This is the synthesis of the pilot vision (the-invariant-application: cockpit/chase/orbital perspectives · the interface-is-space · you fly through it) with the game-design mentality:
- **The world = the projection instrument** (the radial map / `project` tool) — the space you navigate. Tools, chains, graphs are OBJECTS positioned in it (by meaning/kind/relation), discovered + interacted-with in-world, not picked from a menu.
- **The camera = the perspectives** (cockpit/chase/orbital — the resolver's perspective axis): zoom from the orbital overview down to a tool/chain object.
- **The companion = the RHM/V** — your guide in the world (it proposes where to go; you pilot).
- **Interaction = in-world** — navigate to a tool → it opens (the tool-card) → run it → result renders in-world. Build a chain = wire objects in the world (node-graph game feel). Execute a run = watch it flow.
- **Resolver-rendered** — the world is RESOLVED from the registries (tools/chains/graphs/results are typed nodes; the instrument resolves them to positions + the archetypes render them). Single-place-dynamic: a backend change re-resolves the world. ★ [DESIGN-HEAVY + product-shape — scope + a first slice now; the full game-world is a Tim-steered design exploration, not a blind build. Connect to the pilot-ideas-board.]

### 3. CHAINS + GRAPH-EXECUTION — make then run, on local models, pilot/standard
- The capability EXISTS as tools NOW (run_cascade · save_cascade · flows · run_graph · node/connect/set_config · get_state/get_results/get_events/now · run_role/run_items/run_reduce · models_for_role/cap:// for local-model binding). The bridge endpoints exist (/api/run, /api/cognition/*, etc. — [pending the old-UI mining agent for the exact surface]).
- ★ MINE THE OLD DEV UI (still on the company — [location pending the mining agent]): it built the make→wire→configure→run→read loop for chains/graphs. REUSE its WIRING (the bridge endpoints + the tool calls), REBUILD its FACE in the new resolver/archetype UI (the old face is the disposable backend-harness — function not form).
- The new UI: build a chain/graph (wire typed objects in the world) → execute on a chosen LOCAL model (models_for_role/cap:// resolution) → watch the run + read results — all in pilot OR standard mode (the mode axis). The graph/chain is itself resolver/registry-driven (nodes are typed; the canvas resolves them).

### 4. SINGLE-PLACE DYNAMIC — any company change auto-reflects
The whole UI is a PROJECTION from the one place (the registries + the live API). No hardcoded list anywhere — tools, chains, graph-node-types, models, all resolve from their registries. Change the company (add a tool/role/model/node-type) → the UI reflects it with no UI edit. This is the invariant-application / resolver, applied to the operate-the-company surface. [[feedback-flag-hardcoding]] + registry-is-truth throughout.

## ★ GROUNDING — the old-UI mining (landed 2026-06-20; the build rests on this)
The OLD dev UI = the React/tldraw SPA at `canvas/app/` (company-canvas) — the disposable backend-harness, vite-served :5173, proxies /api → bridge :8770. What it gives us:
- **THE GRAPH LOOP IS FULLY BUILT + ALREADY REGISTRY/TOKEN-DRIVEN** (the big reuse): make(`/api/node`)→wire(`/api/connect`)→configure(`/api/set`)→run(`/api/run`)→read(`/api/graph·now·events·stream`). The OLD FACE is already registry-driven — node ports from `getOINFO()[type].ports`, config forms generic from `config_schema` (enum/`options_from`→live registry), status colors from `node_states` render-TOKENS, palette from `/api/object_info`. ⟹ REUSE THE ENDPOINTS WHOLESALE; rebuild ONLY the tldraw face into the resolver/archetype. (And the endpoints are multi-graph-ready — the old face just hardcoded the one demo graph; the pilot gets multi-graph free.)
- **★ THE CASCADE/CHAIN IS HEADLESS — no UI exists** (the critical finding): the old UI has a GRAPH builder, NOT a chain builder. A cascade = a saved linear pipeline of role-steps (`save_cascade`/`run_cascade`/`list_cascades` MCP tools + engine; persists to `.data/store/cascades.json`; each step rides run_role/run_items/run_reduce, threading run:// outputs). ⟹ the chain-builder FACE is NET-NEW — and the GRAPH FACE is its UX template (a cascade is essentially a linear graph of role-steps). Reuse the cascade TOOLS/ENGINE, not any old face.
- **LOCAL-MODEL RUNS WORK** — the cognition/cascade path DEFAULTS LOCAL (`cognition.run_role` → resident chat-4b @ :8000); graph nodes default CLOUD but take an explicit `config.model` for local (the registry-driven config form already supports it via `options_from`→`/api/chat-models`). models_for_role/cap:// resolves eligible local models; `/api/model/load` loads-on-demand with a VRAM fit-check. So "make + run on local models" is real today.
- **TWO CHANNELS to the browser (the gate decides which):**
  - **Channel A — dedicated `/api/*` routes (graph mutation):** `node`·`connect`·`set_config`·`run_graph` are `explicitly_denied` on the generic door → they ride their DEDICATED routes ONLY (never the generic invoke). Reuse as-is.
  - **Channel B — the generic `/api/tools/invoke` door:** READS (`list_cascades`·`list_graphs`·`get_state`·`get_results`·`now`·`get_events`·`models_for_role`·`cognition_info`) exposed NOW (safe, post-reboot when `/api/tools` is live); WRITES/RUNS (`run_role`·`run_items`·`run_reduce`·`save_cascade`·`run_cascade`) await Phase-2 operator-token. Note run_role/items/reduce ALSO have dedicated `/api/cognition/*` routes (built).
- **★ THE ONE REAL BACKEND GAP:** `save_cascade`/`run_cascade` have NO dedicated route AND aren't on the generic door yet → to make the chain feature work, EITHER add `/api/cascade/*` routes OR widen those tools onto `/api/tools/invoke` (Phase-2 + the operator-token). fork's lane. This is the single backend build the chains feature needs.

## ANCHOR (do NOT fan out into unproven breadth — advisor's standing caution)
- The tool-card archetype RIDES the decision-card's PROVEN engine (renderArchetype). So the KEYSTONE (C1/merge-sa at-bar) must land FIRST (post-reboot, DNA's round-3) — it proves the engine the whole pilot tool-face inherits. Build the tool-face ON the proven keystone, not in parallel with an unproven one.
- The resolver (RESOLVER-BUILD) is the spine — dynamic-loading + single-place + the open-world all ARE the resolver applied to the tool/chain/graph surface. Build the resolver mechanism (composition's contract + fork's resolve()) as the foundation; the pilot tool-face is its richest consumer.
- PROVE-ON-ONE holds: one tool fully dynamic+resolver-rendered+runnable (corpus, the existing prove-on-one) → then the chains/graph loop on one chain → then the open-world layer. Each proven before scaling.

## SEQUENCING (mostly post-reboot — the reboot is the enabler)
1. [post-reboot, gate] C1 keystone at-bar (DNA round-3) — proves the engine.
2. [now, code] DNA: the `tool-card` archetype (rides the decision-card engine; description+form+result zones). composition: the resolver contract + the chain/graph node-types as typed registry rows. recollection: any human-meaning for the tool/chain labels. [authored now, verified post-reboot]
3. [post-reboot] projection: dynamic-loading wired through the tool-card archetype off live /api/tools; the chains/graph make-run-read loop (mining the old UI's endpoints); verify by use + sight.
4. [design, now→Tim-steer] the open-world game-design frame (the instrument-as-world + perspectives + RHM-companion) — scope + first slice; Tim steers the product-shape.
5. [post-reboot] the chains/graph-execution integration on local models (the make→run→read loop in the new UI), pilot + standard mode.

## LANES
- **lead** — this spec + the old-UI mining (research, running) + the advisor check + coordination + the bar + (post-reboot) sight-verification. Hold the keystone-first anchor + anti-fan-out.
- **DNA** — the tool-card archetype (rides the decision-card engine) + the chain/graph render; post-keystone.
- **composition** — the resolver contract + the chain/graph/node typed registries + the open-world type-schemas.
- **projection** — dynamic-loading off /api/tools through the archetype + the chains/graph make-run-read UI loop + the open-world host; post-reboot live build.
- **fork** — the resolve() engine primitive + the /api/tools + the chain/graph bridge endpoints (already partly built) + the local-model run path; post its theorem-work + the runbook.

## VERIFY (by use + sight, function+form, post-reboot)
DONE = on the live surface (post-reboot, chrome-devtools back, ?verify=1): every tool DYNAMICALLY listed off the live registry (add a backend tool → appears, no UI edit) · each opens + runs through the resolver-rendered tool-card (not bespoke) · a chain/graph can be MADE + EXECUTED on a local model + results read, in pilot AND standard mode · the surface reads as a navigable open-world space, not a menu-wall · all token/registry/resolver-driven (a single-place change auto-reflects). Nothing to Tim until at-bar by our comparison. Relates: TOOL-FACE-BUILD.md, RESOLVER-BUILD.md, OPERATOR-CYCLE-CRITERIA.md, the pilot-ideas-board, [[project-invariant-application]].
