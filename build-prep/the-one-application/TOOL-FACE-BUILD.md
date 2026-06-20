# The Tool Face — interactive MCP front face (build spec)
*Tim 2026-06-19: "make a front face for the actual MCP — click a tool, click the options, enter inputs, receive responses; no developer UI, not text-heavy, no raw anything, rendered beautifully; every tool an embedded informative pleasant description I can fully understand." This IS the pilot palette — the north-star interface (#68) materializing on the real tool surface. Grounded by a read-only research pass (file:line-verified + live-enumerated). Built prove-on-one, then propagated.*

## THE ARCHITECTURE (the unbroken circuit)
```
FastMCP tool registry (66 tools: name · param JSON-Schema)   +   human-meaning descriptions (the inventory translations)
   → /api/tools            (bridge lists name+schema+posture)                         ← FORK
   → ToolsPanel fetches the list, renders each tool via the DNA tool-card archetype   ← DNA authors archetype · PROJECTION consumes
   → operator picks a tool → human description + friendly inputs (form from schema, op-conditional)   ← PROJECTION
   → run → /api/tools/invoke {name,args}, FAIL-CLOSED gated server-side                ← FORK
   → result rendered beautifully via DNA.renderArchetype(toolCard, result) — NEVER raw JSON   ← PROJECTION + DNA
```
ONE source (the FastMCP registry) feeds the list AND invoke; ONE renderer (`renderArchetype`) draws the tool AND its result. It's a real projection on the DNA system, hosted in the operator surface (:8443, already on Tim's phone), wired to the live bridge. NOT an artifact (sandboxed, can't call tools), NOT a hardcoded parallel app (breaks from-DNA + repeats the elegance miss).

## GROUND TRUTH (verified, file:line)
- **66 tools**, each a FastMCP `Tool` with `name` + `description`(docstring) + `parameters`(real JSON-Schema, e.g. corpus = 15 params incl op/text/space/k). Source = `mcp._tool_manager.list_tools()` (mcp_face/server.py:25,33-36,43).
- **No generic invoke endpoint exists** on the bridge yet. Closest: `/api/cognition/run_role` (bridge.py:2490, role-scoped), `/api/act` (bridge.py:2567, the 7-verb RHM whitelist). Need to build the generic door.
- **The generic-invoke + gate pattern ALREADY EXISTS** on the remote gateway: `mcp_face/remote.py:42` reaches `_TOOL_MANAGER`, dispatches via `call_tool` (remote.py:358-394) behind a fail-closed posture filter (remote.py:77 + remote_exposure.json). MIRROR this onto the local bridge.
- **Process boundary:** bridge + MCP server are SEPARATE processes, separate `Suite` instances. The bridge deliberately doesn't import mcp_face (avoids a 2nd Suite). Clean path = refactor server.py registration into `build_mcp(suite)`/`register_all(mcp, suite)` so the bridge binds a tool manager to its OWN Suite — the "one shared layer both faces call" the code already names (bridge.py:851-862).
- **Surface host = surface/app** (React/Vite, :5174→:8443, /api proxied, no router — App-root sibling overlays). Template = DecisionsInbox (data-driven overlay: store + bar + modal, mounted App.tsx:512-518). DNA-render precedent = GalleryMount (stable div, DNA writes via innerHTML).
- **DNA render = `DNA.renderArchetype(archetype, record, opts)`** (surface/runtime/archetype.js:276), archetypes registry in `dna/layouts.json`. The **decision-card** (layouts.json:764-868) is the EXACT precedent (bespoke renderDecision retired 2026-06-19 → now draws through the one generic renderArchetype). Author `tool-card` identically. Propagation = sync-gallery.mjs copies from the design repo, fail-loud.
- **Result render:** a tool result has no address → does NOT go through renderGallery (address-resolved); use the DIRECT `DNA.renderArchetype(toolCard, resultRecord)` into the panel's own container (like pieces/decision-card/card.html:33).

## THE SAFETY GATE (non-negotiable — lead holds)
The generic invoke door is a gate-bypass for every consequential verb. Localhost-trusted ≠ no gate (it's proxied to :8443 on the tailnet). Enforcement is SERVER-SIDE (UI hiding buttons is NOT the gate).
- Reuse `mcp_face/remote_exposure.json` postures (safe/design/consent/hazard/locked) as the denylist on `/api/tools/invoke`.
- **Operator-face distinction:** the operator face is for TIM, so it MAY permit `locked` (operator-only) tools the remote connector can't. BUT: `hazard` (destructive/irreversible) requires explicit confirm, and the truly dangerous — self-modify/dispatch/clone-spawn/graph-mutation — NEVER ride the generic door; they route through their existing dedicated gated routes (/api/resolve, /api/revert, /api/checkpoint, etc.).
- `explicitly_denied` on the generic door (from remote_exposure.json): node, connect, set_config, run_graph, cc_clone, cc_gate, session_post, resolve_surfaced, approve, dispatch, checkpoint, revert, mark, channel_act, self_change_log.

### ★ ONE GATED FLOOR (composition's flag, 2026-06-19 — the unification)
The tool-face's invoke gate is NOT a separate gate — it is the SAME gated floor + operator-attribution that the decision-take and the territory-write ride. A consequential tool-run = a "fire a verb" path, identical in kind to writing a decision_take. So:
- **Reads (safe/design, e.g. corpus op=query) run FREE.** The prove-on-one is a read → free → good first pick.
- **Consequential/write tool-runs require GENUINE-OPERATOR ATTRIBUTION** — the SAME per-session operator-token seam fork has queued as `#1b` for `/api/territory/write`. That one mechanism covers ALL three: the decision-take, the territory-write, AND a consequential tool-run. Build it ONCE, applied at the floor.
- So `/api/tools/invoke` (gap 3) must be designed as that unified floor from the start (posture denylist + operator-attribution for consequential), NOT a direct ungated invoke. Don't let the tool-face become a new ungated fire-path — it inherits the floor, never bypasses it. (Truly dangerous verbs stay off the generic door entirely → dedicated gated routes.)
- **`archetype.take` generalizes** (composition, additive — done when tool-card sequences, doesn't touch decision-card): today take = {from_slot, writes: a mark_type}. It generalizes to an ACTION that is EITHER a mark-write (decision-card) OR an invoke-and-render-result (tool-card), plus a `result` slot.

## THE DESCRIPTIONS (Tim's "embedded, informative, pleasant, fully-understand")
The raw docstrings are AGENT-facing (dev jargon = the "raw" Tim rejected). The tool-card renders the HUMAN-MEANING description — the plain-English translations already authored in the inventory (build-prep/the-one-application/company-mcp-tools.html / the 64-tool pass). These become a description field per tool (a small human-description layer the surface reads), sourced from the inventory; lead owns seeding it. Honors [[feedback-translate-everything-human-meaning]]. Form from schema (real), description from translation (pleasant).

### ★ FORM-META HOME (lead decision, 2026-06-19 — answering projection's "in /api/tools or a separate merge?")
Neither pole — BOTH, resolved (the false binary dissolves): the human layer is its OWN declared registry (the source of truth), and `/api/tools` RESOLVES + merges it into the served descriptor so the surface reads ONE object. Concretely:
- **A tool-meta REGISTRY** — one row per tool: `{human_name, human_description, op_labels (op→friendly name), op_params (curated VISIBLE params per op — hide expert knobs), param_labels (param→human label)}`. A DECLARED registry (JSON, the `_CORPUS_META`/design/_system pattern — data, edited in one place, propagates), NOT hardcoded, NOT authored inside the bridge (fork must not own human-presentation content), NOT a client-side merge (keep the client one-descriptor-simple).
- **`/api/tools` joins it:** returns the machine truth {name, inputSchema, posture} + the RESOLVED form_meta from the registry → the surface's engine reads it from the one descriptor (projection's engine already consumes it either way).
- **Authoring = the mechanism (draft→steer):** AI drafts each tool's meta from the schema + the inventory translations; lead/Tim steer the ones that matter → the registry. That's where the other 65 tools' labels come from. The coverage mechanism populating its own surface (dogfood).
- **For the prove-on-one NOW:** projection's inline AI-draft corpus meta (op names "Ask a question / Browse all / Filter to some / Open one / Find related"; hid emb/top_n/min_score) is good + transitional — it proves the engine now and migrates into the registry as row #1 when the back half lands. Gap 7 = stand up this registry + seed it.

### CORPUS PROVE-ON-ONE INVOKE ENDPOINT (verified bridge.py:1236-1242)
`corpus(op=query)` → `GET /api/corpus-query?text=<q>&space=<space>&k=<k>` → `SUITE.query_corpus(text, space, k)` → ranked records (the SAME query_corpus the MCP corpus tool calls). Read-only/safe → no gate. ★ NOT `/api/cognition/corpus` (bridge.py:1510 = the records LIST/READ, a name-collision). projection wires Run → /api/corpus-query now; swaps onto the generic /api/tools/invoke when gap 3 lands.

## GAP LIST (owner per gap)
| # | Gap | Owner |
|---|---|---|
| 1 | `register_all(mcp, suite)`/`build_mcp(suite)` factory (bridge binds tool manager to its own Suite) | **fork** |
| 2 | `/api/tools` GET — [{name, description, inputSchema, posture}] from list_tools() | **fork** |
| 3 | `/api/tools/invoke` POST — generic call_tool, FAIL-CLOSED posture gate server-side; consequential verbs refused→dedicated routes | **fork** (lead holds the gate review) |
| 4 | `tool-card` archetype in design/dna/layouts.json (+ slotHTML cases if needed) — DESIGN REPO (DNA's lane only) | **DNA** |
| 5 | surface: src/tools/{toolsStore.ts, ToolsPanel.tsx, ToolsBar.tsx} + mount App.tsx:518 + postJSON/invokeTool in api.ts + op-conditional form from schema + result via renderArchetype into a stable container | **projection** |
| 6 | tool-entity shape adapter (FastMCP Tool → tool-card record matching the archetype slot_map) | **projection** (shape) ↔ **DNA** (slot_map contract) |
| 7 | human-description layer (plain-meaning per tool, from the inventory) | **lead** (seed) → a data field the surface reads |

## PROVE-ON-ONE: `corpus` with op="query"
Safe posture (web-OK) · 15 params (stress-tests the op-conditional friendly form from day one) · structured result worth rendering (stress-tests never-raw). ★ Sequencing win: corpus(op=query) maps to the EXISTING `/api/cognition/corpus` GET → projection + DNA build + verify the full click→form→render loop against that NOW, in parallel, while fork builds the generic /api/tools/invoke + gate → then swap onto the generic door. File-disjoint across all three streams. (Avoid zero-arg reads like object_info as the first prove — they exercise neither the form nor a rich result.)

## SEQUENCING (rides the elevation, doesn't fragment it)
The tool-face REUSES the same engine the decision-surface elevation is fixing (renderArchetype + the archetype pattern + the operator-surface host). So:
- **fork**: gaps 1-3 NOW — independent of the render; productive while its RHM-voice wire is gated on DNA's resolve-source.
- **projection**: gap 5/6 scaffold against the existing /api/cognition/corpus endpoint — in parallel as capacity allows alongside the decision-surface host.
- **DNA**: gap 4 (tool-card archetype) rides BEHIND the decision-card prove-on-one — same pattern, so proving merge-sa de-risks tool-card; authored on the same CAP-2/craft foundation. Don't fragment DNA off the decision card; tool-card is next-after (fast, it copies the pattern).
- **lead**: hold the gate (gap 3 review) + the human-description seed (gap 7) + the bar + sequencing.
Blockers: gap 1 precedes 2/3; gap 4 is in the design repo (DNA-only) — the render loop is blocked until tool-card lands (mitigate early with a local pieces/tool-card/*.html specimen on sample data, like the decision-card piece).

## ★ COMPOSITIONALITY AUDIT (lead, 2026-06-19 — Tim's direct question "is the UI built the compositional way?")
Audited the built code directly (file:line). Honest layered verdict:
- **DATA/LOGIC layer = COMPOSITIONAL ✓** — schemaForm.tsx is ONE generic engine consuming any ToolDescriptor (serves all 66; labels/opParams/enum_sources from the registries + tool_meta.json + /api/tools). A registry change propagates. True projection from the one place.
- **RENDER layer (form · list · description) = HALF** — bespoke React (`.tf-*` JSX: select/input/pill) on DNA TOKENS only, NOT through the DNA render system (no renderArchetype). On-token but not archetype-rendered → a design-LANGUAGE change does NOT propagate (you'd edit React). This is the gap vs Tim's standard ("a projection, all from DNA, change-one-place-propagates").
- **RESULT render = reserved for DNA, unbuilt** — ToolsPanel.tsx:12,176 hold the result for DNA.renderArchetype(tool-card) (gap 4); the code refuses to bespoke-render it (honest pending, never raw). No tool-card archetype in dna/layouts.json yet.
- **FULL COMPOSITIONALITY IS PROVEN-REACHABLE** — DNA renders AND wires INTERACTIVE archetypes today: archetype.js:363-380 wires the decision card's option-clicks to the take (archetype.take → decide/skip/retry); unit-view.js bindVee/bindProjectionDrill. So an interactive surface CAN be a true projection; the tool form was built in React for speed, not because DNA can't.
- **THE PATH (held for Tim's steer, NOT auto-fired — it's a unification-level call):** author the `tool-card` archetype to cover description+form+result, generalizing `archetype.take` to form→invoke→render-result (composition already flagged this). Then the whole tool view is a projection like the decision card.
- **★ THE PRINCIPLED LINE (composition's sharpening, 2026-06-19) — "fully compositional ≠ zero React":** CONTENT vs HOST. CONTENT (a decision · a tool's description/form/result · graph · selector) MUST route through an archetype (the law) — the tool face rendering its content as bespoke React = THE gap (= gap 4). HOST/CHROME (modal shell, panels, nav, operator scaffold) legitimately stays a thin React frame over DNA tokens — requiring archetypes there is dogma, not value. So the gap is precisely "content rendered bespoke"; the modal host staying React is correct. The residual Tim-steer choice narrows to: WHERE the live form interactivity lives — DNA take-bound (like the decision take) vs archetype-draws/React-wires. Options A(rec)/B/C in is-the-ui-compositional.html.
- **WHY IT MATTERS (the unification relation):** UI-compositional = UI-is-a-projection = UI-is-part-of-the-one-substrate (not an island). One renderer + N archetypes (decision-card, tool-card, … every surface) = the pilot UI as "all from one place." Proof #2 (after the decision card) that "any surface = an archetype."

## VERIFY (by use, the bar)
Prove-on-one is done when: open the operator surface (:8443, ?verify=1 where it writes), click `corpus` → a pleasant human description + a friendly op-conditional form (no raw schema) → enter a query → run → a beautifully-rendered result (never raw JSON) → all through the live bridge. At-bar by our reference comparison (the craft bar, same as the decision card). THEN propagate the pattern to all 66 (gated). Nothing to Tim until the prove-on-one is at-bar by our own judgment.
Relates: [[the-one-application]], DECISION-SURFACE-BUILD.md (the precedent), ELEGANCE-ELEVATION-WORKLIST.md (the shared render engine), the pilot ideas board.
