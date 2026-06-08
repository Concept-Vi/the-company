# Inventory: Self-Description, Tests, Ops, Docs (Region D)
**As of 2026-06-08 — Fast coverage scan, READ-ONLY**

---

## Directory Structure

### /home/tim/company/tests/
```
tests/
├── AGENTS.md (constitution — acceptance suites as proof record)
├── (130 .py acceptance suites, see "Test Suites by Category" below)
└── .gitkeep
```

### /home/tim/company/docs/
```
docs/
├── AGENTS.md (constitution — repo meta-documentation)
├── .gitkeep
├── concepts-and-principles.md
├── vault-conventions.md
└── methodology/
    ├── README.md
    ├── company-build.md
    ├── loop-prep.md
    ├── plan-review.md
    ├── remediation-build.md
    ├── rhm-build.md
    └── wire-build.md
```

### /home/tim/company/ops/
```
ops/
├── AGENTS.md (constitution — operational control + the `company` CLI)
├── STARTUP.md (command table + boot behaviour)
├── WINDOWS-BOOT.md
├── services.json (the registry of all services + GPU VRAM budgets)
├── company (the CLI launcher, symlinked to PATH)
├── serve_model.sh
├── cli/
│   ├── README.md (use guide)
│   ├── UPDATING.md (how to extend CLI + registry schema)
│   ├── app.py (dispatch + `up` resource gate)
│   ├── registry.py (reads services.json)
│   ├── systemd.py (start/stop/status/logs)
│   ├── gpu.py (the GPU resource manager + VRAM fit-gate)
│   ├── models.py (inventory + swap)
│   ├── capabilities.py (model-TYPE capability registry by model-id)
│   ├── bench.py
│   ├── render.py (status/health views)
│   ├── telemetry.py + telemetry.jsonl
│   └── __pycache__/
└── systemd/ (canonical user-unit files)
    ├── company.target (master unit, WantedBy for all)
    ├── company-bridge.service
    ├── company-canvas.service
    ├── company-tts-kokoro.service
    ├── litellm-proxy.service
    ├── llama-swap.service
    ├── openclaw-gateway.service
    ├── vllm-*.service (8 model-serving units)
    ├── voicemode-whisper.service
    └── github-runner.service
```

### Modules WITHOUT AGENTS.md (exceptions)
- **build-prep/** — staging area for specs (concurrent-cognition/ only; not a code module)
- **design/** — aesthetic/interface specs (CLAUDE.md, conventions.md, blueprint/, _system/) — NOT a code module

---

## Self-Description Files (AGENTS.md, MAP.md, STATE.md)

| Path | Type | Module | Governs | Appears to be | PRIORITY |
|------|------|--------|---------|---------------|----------|
| `/home/tim/company/AGENTS.md` | constitution | root | none | **ROOT SPINE** — the five non-negotiable rules (schema-additive, one source, fail-loud, etc); orientation entry point | **YES** |
| `/home/tim/company/MAP.md` | map | root | none | **LOADABLE MAP** — the picture of what exists (canvas → runtime → fabric → store → mcp_face → nodes → voice); self-maintained by `Suite.refresh_self_description()` | **YES** |
| `/home/tim/company/STATE.md` | state | root | none | **STATUS + ACCEPTANCE SUITES** — what's built+proven, what's not, how to run/verify, 130 suites listed; auto-maintained drift check via `tests/drift_acceptance.py` | **YES** |
| `/home/tim/company/runtime/AGENTS.md` | constitution | runtime | S1, C5, C6, S7 | **THE SCHEDULER + SUITE** — the brain (memo gate, compile, node wiring, RHM); governs core convergence (runtime/suite.py, runtime/scheduler.py, runtime/bridge.py) | **YES** |
| `/home/tim/company/contracts/AGENTS.md` | constitution | contracts | C1-C8 | **THE SPINE SPECS** — 8 contracts define node-schema, storage, address-grammar, RHM verbs, MCP face; vault-ground (build-prep/contracts/C1-C8.md notes); code IMPLEMENTS, doesn't redefine | **YES** |
| `/home/tim/company/store/AGENTS.md` | constitution | store | C1, C4 | **CONTENT-ADDRESSING + PERSISTENCE** — where everything lives by address (fs_store.py, graph_store.py, events.jsonl, chat persistence); C1 node-schema, C4 address-grammar | **YES** |
| `/home/tim/company/nodes/AGENTS.md` | constitution | nodes | C2 | **NODE LIBRARY** — each node-type is C2 one-source-of-truth; governs process·content·presentation nodes (nodes/*.py); used by runtime + canvas + MCP | **YES** |
| `/home/tim/company/fabric/AGENTS.md` | constitution | fabric | S6 | **MODELS + GUARDS** — the Ollama/LiteLLM/OpenAI-compatible layer; guards on token limits, tool safety, model-specific knobs | **YES** |
| `/home/tim/company/canvas/AGENTS.md` | constitution | canvas | S5, D3 | **REACT + TLDRAW SURFACE** — the UI face; S5 is the bridge protocol; D3 "one substrate, per-type view-modes" design decision | **YES** |
| `/home/tim/company/canvas/app/src/extensions/AGENTS.md` | constitution | extensions | none | **SELF-MOD UI LAYER** — generated extensions mechanism; how the system builds its own UI additions (auto-generated, not hand-coded) | **NO** (review on extension changes) |
| `/home/tim/company/roles/AGENTS.md` | constitution | roles | C2.1-C2.5 | **ROLE REGISTRY** — persona+voice+character definitions (judge, synthesizer, tool-caller, etc.); C2 sub-contracts bind roles to node-type capabilities | **YES** (design-gating) |
| `/home/tim/company/mcp_face/AGENTS.md` | constitution | mcp_face | C7 | **MCP AGENT FACE** — generic verbs over the Suite (run_graph, apply_node, propose_node); C7 spec defines the interface; shares Suite with UI | **YES** |
| `/home/tim/company/voice/AGENTS.md` | constitution | voice | none | **TWO-WAY VOICE** — STT (AssemblyAI/local) + TTS (local Kokoro in .voice-venv); event-traced (voice.stream/voice.turn ops in events.jsonl) | **YES** |
| `/home/tim/company/voice/ears/AGENTS.md` | constitution | voice/ears | none | **STT PROVIDERS** — swappable speech-to-text layer (AssemblyAI, local Whisper, etc.); ear-agnostic to engine | **NO** (reference on voice changes) |
| `/home/tim/company/voice/engines/AGENTS.md` | constitution | voice/engines | none | **TTS ENGINES** — swappable speech synthesis (Kokoro, Orpheus, Chatterbox, etc.); engine-agnostic to ear | **NO** (reference on voice changes) |
| `/home/tim/company/panels/AGENTS.md` | constitution | panels | none | **SELF-MOD PANELS** — governance + settings surfaces; how Tim steers the system live | **YES** (governance gate) |
| `/home/tim/company/tests/AGENTS.md` | constitution | tests | none | **ACCEPTANCE SUITES** — 130 converge-proofs; each names a capability; drift-checked in STATE.md; "done" = green suite + use-evidence | **YES** (convention holder) |
| `/home/tim/company/docs/AGENTS.md` | constitution | docs | none | **REPO META-DOCS** — cross-cutting conventions (Vault Conventions, Concepts, methodologies); NOT per-module specs | **YES** (navigation anchor) |
| `/home/tim/company/ops/AGENTS.md` | constitution | ops | none | **OPERATIONAL CONTROL** — the `company` CLI (services, GPU, models, capabilities registries); systemd substrate; one console, multiple type-views (services/GPU/models live; cognitive/RHM/data/jobs pending) | **YES** |

---

## Test Suites by Category (130 total)

### Engine & Convergence (E-series + core runtime)
- `e1_acceptance.py` — E1 (first purpose: the system on its own codebase)
- `e2_runtime.py` — E2 runtime mechanics
- `e2_review_fixes.py` — E2 review/verify fixes
- `e3_fabric.py` — E3 (fabric + model integration)
- `e3_integration.py` — E3 (end-to-end runtime→fabric)
- `e4_registry.py` — E4 (node registry + discovery)
- `e5_suite.py` — E5 (Suite class + orchestration)
- `e6_governance.py` — E6 (governance gates + self-mod rules)
- `drift_acceptance.py` — E-class helper: MAP.md/STATE.md stay in sync with code (PoLR-3 path-of-least-resistance maintenance)
- `walking_skeleton.py` — E0-sketch: minimal runnable system
- `suite_health_acceptance.py` — E-class health: every subsystem callable, no silent failures

### Composition: Graphs, Wiring, Activation
- `compose_acceptance.py` — compose nodes into graphs
- `wire_acceptance.py` — Decision→Implementation Wire (S8, build-intent → dispatch → verify → surface)
- `wire_async_dispatch_acceptance.py` — async dispatch under concurrency
- `wire_commit_acceptance.py` — persisting dispatch commits (commit-log + revertibility)
- `wire_harden_acceptance.py` — wire robustness (exactly-once, forged-refusals)
- `wire_loop_acceptance.py` — wire in a loop (repeated decisions)
- `wire_trigger_acceptance.py` — wire on trigger events
- `wire_adversarial.py` — adversarial wire scenarios (malformed JSON, scope-overrun, etc.)
- `layers_acceptance.py` — graph layers + isolation
- `portal_acceptance.py` — graph portals (cross-graph refs)

### Address Grammar & Navigation
- `address_grammar_acceptance.py` — C3 address-grammar parser (the notation)
- `addr_chat_acceptance.py` — address in chat context (looking-up by name/role)
- `addr_context_acceptance.py` — address context scope (what resolves to what)
- `addr_history_acceptance.py` — address history lookup
- `address_help_surface_acceptance.py` — help text on address-values (user affordance)
- `address_scope_acceptance.py` — scope of address binds (local/graph/global)
- `event_address_acceptance.py` — events keyed by address
- `navgraph_acceptance.py` — the address navigation graph
- `focus_ui_address_acceptance.py` — address in UI context

### Conversation & Chat
- `conv_blast_acceptance.py` — one message → multiple outputs (branching)
- `conv_blast_both_acceptance.py` — blast + recombine
- `conv_bridge_acceptance.py` — bridge protocol (UI ↔ runtime)
- `conv_compose_acceptance.py` — compose nodes from conversation
- `conv_configurable_acceptance.py` — conversation over configurable nodes
- `conv_consent_acceptance.py` — operator consent gates in conversation (C5)
- `conv_constitution_acceptance.py` — constitution applied in conversation
- `conv_context_acceptance.py` — context tracking across turns
- `conv_dedup_acceptance.py` — dedup repeated context
- `conv_freshstart_acceptance.py` — starting fresh graph mid-conversation
- `conv_howto_acceptance.py` — how-to generation in conversation
- `conv_index_acceptance.py` — indexing conversation history
- `conv_index_staleness_acceptance.py` — stale index detection
- `conv_payload_acceptance.py` — payload variants in conversation
- `conv_pin_acceptance.py` — pinning values in conversation
- `conv_reach_acceptance.py` — reach (lookups) in conversation
- `conv_semantic_rank_acceptance.py` — semantic ranking in conversation
- `conversational_build_acceptance.py` — build via conversation

### Activation & Scheduling
- `activation_contexts_acceptance.py` — activation contexts (when nodes fire)
- `autodetect_setter_acceptance.py` — auto-detecting a setter node
- `locus_acceptance.py` — locus (where a node lives in a graph)
- `scheduler_isolation_acceptance.py` — scheduler isolation (one graph doesn't block another)
- `concurrency_acceptance.py` — concurrent node execution (no race conditions)
- `cross_process_lock_acceptance.py` — cross-process locks (if running multi-process)

### Annotation & Governance
- `annotation_acceptance.py` — marking/annotating nodes (metadata)
- `annotate_vs_operate_acceptance.py` — annotation vs actual operation (mock vs real)
- `authoring_acceptance.py` — authoring/editing graphs and nodes
- `cognition_governance_acceptance.py` — cognitive layer rules (RHM restraints)
- `cognition_info_acceptance.py` — cognitive info (RHM state + logs)
- `coa_acceptance.py` — course-of-action (COA) generation from RHM
- `decision_lineage_acceptance.py` — tracing decision history (who decided what when)
- `design_gate_acceptance.py` — design gates (surface-before-modify)
- `gate_acceptance.py` — build gates + safety gates
- `hardening_acceptance.py` — hardening against misuse
- `rules_acceptance.py` — RHM rules (what it can/can't do)
- `selfmod_acceptance.py` — self-modification (system changing itself)
- `selfmod_audit_acceptance.py` — audit trail for self-mods (what changed, by whom, when)
- `self_change_locating_acceptance.py` — finding where self-mods touched (diff locating)

### RHM (Right-Hand Man, Conversational Organ)
- `rhm_acceptance.py` — RHM basics (conversation, state, actions)
- `rhm_action_acceptance.py` — RHM actions (the verbs it can call)
- `rhm_action_parse_acceptance.py` — parsing RHM action directives
- `rhm_completion_acceptance.py` — RHM completions (next steps)
- `rhm_grounding_acceptance.py` — RHM grounding (facts + evidence for claims)

### Fabric & Models
- `fabric_retry_acceptance.py` — retry logic on model failures
- `fabric_tools_acceptance.py` — tool-calling via fabric (LLM → function)
- `model_capabilities_acceptance.py` — model capability registry (tool_call, json_schema, thinking, context-ceiling, speed) by model-id
- `embeddings_acceptance.py` — embedding model calls
- `stt_models_acceptance.py` — speech-to-text model selection
- `stt_whispercpp_acceptance.py` — local Whisper (whispercpp backend)

### Voice & Audio
- `voice_circuit_acceptance.py` — voice request-reply loop (end-to-end)
- `voice_parts_acceptance.py` — voice as parts (listening, generating, playback)
- `speakable_acceptance.py` — which outputs are speakable (no emoji, etc.)

### Data & Persistence
- `durability_acceptance.py` — data survives process restart (fs-backed)
- `events_acceptance.py` — event log integrity + traversal
- `journey_recording_acceptance.py` — journey recording (provenance trail)
- `version_history_acceptance.py` — version history tracking
- `volatile_acceptance.py` — volatile state (not persisted)
- `trajectory_acceptance.py` — trajectory of a node execution

### Presentation & UI
- `node_states_render_acceptance.py` — how nodes render their state on canvas
- `panel_acceptance.py` — panels (governance, settings, etc.)
- `presentation_learning_acceptance.py` — learning how to present (UX feedback loop)
- `uptranslate_acceptance.py` — converting low-level state to high-level presentation
- `show_acceptance.py` — showing/hiding elements on canvas
- `showme_backend_acceptance.py` — backend showme (what can be surfaced)
- `showme_c2_acceptance.py` — C2 showme (node properties surfaced)
- `showme_guided_acceptance.py` — guided showme (step-by-step revelation)
- `propose_affordance_acceptance.py` — proposing affordances to user (UI hints)
- `click_tier_acceptance.py` — click-tier (how UI actions map to operations)

### Misc. / Advanced
- `act_endpoint_acceptance.py` — /act endpoint (API surface for actions)
- `agency_acceptance.py` — agency (AI making decisions autonomously)
- `blueprint_acceptance.py` — blueprint (template graphs)
- `chat_parts_acceptance.py` — chat as multipart (text + code + data)
- `configs_acceptance.py` — configuration persistence
- `consult_acceptance.py` — consulting the system (asking questions)
- `copresence_acceptance.py` — copresence (multiple actors on same graph)
- `edge_kinds_acceptance.py` — edge types in graphs
- `extension_acceptance.py` — extension mechanism (adding new node-types)
- `feedback_to_wire_acceptance.py` — feedback loop → wire trigger
- `fs_session_guard.py` — filesystem session safety (no data loss)
- `inbox_acceptance.py` — inbox (queued decisions/questions for operator)
- `inbox_target_acceptance.py` — inbox targeting (routing to right operator)
- `interactive_consent_acceptance.py` — interactive consent flow (UI → approval)
- `interactive_inbox_acceptance.py` — interactive inbox (responding to items)
- `json_schema_transport_acceptance.py` — JSON schema over the wire
- `memo_stale_acceptance.py` — memo staleness detection (re-run only what changed)
- `modes_acceptance.py` — Vi modes (activity-based dispatch)
- `modes_typeregistry_acceptance.py` — modes + type registry integration
- `mcp_use.py` — MCP (Model Context Protocol) via the agent face
- `polr_acceptance.py` — path-of-least-resistance (PoLR) design principle adherence
- `react_acceptance.py` — React component rendering
- `set_ref_atomic_acceptance.py` — atomic ref-sets (no partial updates)
- `settings_surface_acceptance.py` — settings panel (what can be configured)
- `state_types_acceptance.py` — state type system (what states exist, their schemas)
- `twin_acceptance.py` — twin (learned copy of the system for predictions)
- `twin_located_gold_acceptance.py` — twin accuracy verification (gold ground-truth)
- `ui_registry_acceptance.py` — UI component registry
- `trajectory_acceptance.py` — execution trajectory recording

### Acceptance Suites Organization by Subsystem

| Subsystem | Tests | Purpose |
|-----------|-------|---------|
| **Engine (E1-E6)** | e1_acceptance, e2_runtime, e2_review_fixes, e3_fabric, e3_integration, e4_registry, e5_suite, e6_governance, drift_acceptance, walking_skeleton, suite_health_acceptance | Prove core runtime, memo, compilation, registry discovery, governance |
| **Wire (S8/W1-W4)** | wire_acceptance, wire_async_dispatch, wire_commit, wire_harden, wire_loop, wire_trigger, wire_adversarial | Decision→Implementation loop (build-intent → dispatch → verify → surface) |
| **Address Grammar (C3)** | address_grammar_acceptance, addr_chat, addr_context, addr_history, address_help_surface, address_scope, event_address, navgraph, focus_ui_address | Name-resolution + scope + notation |
| **Conversation** | 16 conv_* tests + conversational_build_acceptance | Chat-driven graph composition + context + consent |
| **RHM (Right-Hand Man)** | rhm_acceptance, rhm_action, rhm_action_parse, rhm_completion, rhm_grounding | Conversational organ (actions, state, reasoning) |
| **Activation & Scheduler** | activation_contexts, autodetect_setter, locus, scheduler_isolation, concurrency, cross_process_lock | When + how nodes fire, isolation, concurrency safety |
| **Governance & Self-Mod** | annotation, annotate_vs_operate, authoring, cognition_governance, cognition_info, coa, decision_lineage, design_gate, gate, hardening, rules, selfmod, selfmod_audit, self_change_locating | Build gates, RHM rules, audit trail, drift prevention |
| **Fabric & Models** | fabric_retry, fabric_tools, model_capabilities, embeddings, stt_models, stt_whispercpp | LLM integration, tool-calling, capability registry |
| **Voice** | voice_circuit, voice_parts, speakable | STT + TTS loop, audio processing |
| **Data & Persistence** | durability, events, journey_recording, version_history, volatile, trajectory | Fsync safety, event log, provenance |
| **Presentation & UI** | node_states_render, panel, presentation_learning, uptranslate, show, showme_backend, showme_c2, showme_guided, propose_affordance, click_tier | Canvas rendering, affordances, user presentation |
| **Misc** | 16+ other tests covering act endpoint, agency, blueprint, chat_parts, configs, etc. | Edge cases, integrations, specialized behaviors |

---

## Docs/ Breakdown

| File | Appears to be | PRIORITY |
|------|---------------|----------|
| `/home/tim/company/docs/concepts-and-principles.md` | Foundational philosophy (why "prove by use" is the standard, PoLR design principle) | NO (reference) |
| `/home/tim/company/docs/vault-conventions.md` | Frontmatter + dual repo+vault markdown format; every .md follows this schema | **YES** (convention anchor) |
| `/home/tim/company/docs/methodology/README.md` | Index of build methodologies | NO (reference) |
| `/home/tim/company/docs/methodology/company-build.md` | How to add a new subsystem | NO (reference) |
| `/home/tim/company/docs/methodology/loop-prep.md` | Prep for a loop (completion criteria + implementation guide + research synthesis) | NO (reference) |
| `/home/tim/company/docs/methodology/plan-review.md` | How to review a plan before build | NO (reference) |
| `/home/tim/company/docs/methodology/remediation-build.md` | How to fix bugs + improve | NO (reference) |
| `/home/tim/company/docs/methodology/rhm-build.md` | How to extend the RHM | NO (reference) |
| `/home/tim/company/docs/methodology/wire-build.md` | How to build the wire (build-intent → dispatch) | NO (reference) |

---

## Ops/ Key Files

| File | Appears to be | PRIORITY |
|------|---------------|----------|
| `/home/tim/company/ops/AGENTS.md` | **CONSTITUTION** — one console (company CLI) for services/GPU/models; systemd substrate; type-views expanding (services live; GPU live as of 2026-06-06; cognitive/RHM/data/jobs pending). **Single source of truth for what runs.** | **YES** |
| `/home/tim/company/ops/STARTUP.md` | Commands, boot order, open items. How to bring the system up. | **YES** |
| `/home/tim/company/ops/WINDOWS-BOOT.md` | WSL-specific boot sequence | NO (reference) |
| `/home/tim/company/ops/services.json` | **REGISTRY** — every service declared once (key, group, title, port, manage type, health, autostart, vram_mb, vram_ceiling_mb). Source of truth. **AI reads this to know the system.** | **YES** |
| `/home/tim/company/ops/company` | Launcher script (stdlib-only) → `cli/app.py` → dispatch | **YES** (entry point) |
| `/home/tim/company/ops/cli/app.py` | Main CLI dispatch + `up` resource gate (refuse over-capacity, show what to unload) | **YES** |
| `/home/tim/company/ops/cli/gpu.py` | **RESOURCE MANAGER** — VRAM fit-gate, budget tracking (config.gpu_util × vram_ceiling = budget), measured free, swap logic. Measured on 16GB: 4B brain solo 256K, co-resides with light voices at 64K (Orpheus blocks). | **YES** |
| `/home/tim/company/ops/cli/models.py` | Model inventory + swap operations | **YES** |
| `/home/tim/company/ops/cli/capabilities.py` | **CAPABILITY REGISTRY** — by model-id (tool_call, json_schema, thinking, context-ceiling, concurrency-knee, speed), provenance (declared|probed|measured|served). JOINs to gpu.py. `role_can_bind(requires, model_id)` binding query. | **YES** |
| `/home/tim/company/ops/cli/registry.py` | Reads/parses services.json | **YES** |
| `/home/tim/company/ops/cli/systemd.py` | Systemctl wrapper (start/stop/status/logs) | **YES** |
| `/home/tim/company/ops/cli/README.md` | Use guide | **YES** |
| `/home/tim/company/ops/cli/UPDATING.md` | How to extend CLI + registry schema | **YES** |
| `/home/tim/company/ops/cli/bench.py` | Benchmarking harness (model perf measurements) | NO (reference) |
| `/home/tim/company/ops/cli/render.py` | Status/health rendering (pretty-print console output) | **YES** |
| `/home/tim/company/ops/cli/telemetry.py` | Resource telemetry collection (VRAM, load, speeds) | **YES** |
| `/home/tim/company/ops/systemd/*.service` | User-unit files; canonical here, installed to `~/.config/systemd/user/`; WantedBy=company.target | **YES** |
| `/home/tim/company/ops/systemd/company.target` | Master unit; all others Wants/WantedBy it | **YES** |

---

## Modules WITH AGENTS.md (Inventory)

```
ROOT (constitution + map + state)
├── contracts/AGENTS.md (C1-C8 spine specs)
├── runtime/AGENTS.md (S1, C5, C6, S7 scheduler + Suite)
├── store/AGENTS.md (C1, C4 persistence)
├── nodes/AGENTS.md (C2 node library)
├── fabric/AGENTS.md (S6 models)
├── canvas/AGENTS.md (S5, D3 React + tldraw)
├── canvas/app/src/extensions/AGENTS.md (self-mod UI)
├── mcp_face/AGENTS.md (C7 agent interface)
├── voice/AGENTS.md (STT + TTS + event-traced)
├── voice/ears/AGENTS.md (STT providers)
├── voice/engines/AGENTS.md (TTS engines)
├── roles/AGENTS.md (C2.1-C2.5 persona registry)
├── panels/AGENTS.md (governance + settings)
├── tests/AGENTS.md (130 acceptance suites)
├── docs/AGENTS.md (repo meta-docs)
└── ops/AGENTS.md (company CLI + systemd)
```

**Total: 16 modules WITH AGENTS.md**

## Modules WITHOUT AGENTS.md

- **build-prep/** — staging (specs live in vault: `build-prep/concurrent-cognition/` etc.) — NOT a code module
- **design/** — aesthetic/interface specs — NOT a code module

**Total: 2 directories without; both are non-code (staging + design)**

---

## Summary Counts

| Category | Count | Notes |
|----------|-------|-------|
| **Self-Description Files (AGENTS.md)** | 16 | Every code module has one. No orphans. |
| **MAP.md instances** | 1 | Root only; auto-maintained by `Suite.refresh_self_description()`. |
| **STATE.md instances** | 1 | Root only; lists all 130 acceptance suites; drift-checked. |
| **Acceptance Test Suites** | 130 | Grouped by subsystem; each proves a capability; run as: `for t in tests/*.py; do ./.venv/bin/python "$t"; done` |
| **Docs Files** | 9 | concepts-and-principles, vault-conventions, 6 methodologies, 1 README |
| **Ops Files** | 44+ | AGENTS.md, STARTUP.md, WINDOWS-BOOT.md, services.json, cli/ (10 modules), systemd/ (13 units) |
| **Code Modules (top-level)** | 14 | contracts, runtime, store, nodes, fabric, canvas, mcp_face, voice, voice/ears, voice/engines, roles, panels, tests, docs, ops |
| **Non-Code Directories** | 2 | build-prep (staging), design (aesthetic specs) |

---

## Top PRIORITY Constitution/Convention Files for Deep-Read

1. **`/home/tim/company/AGENTS.md`** (ROOT SPINE)
   - The five rules that govern everything
   - Schema-additive, one source, fail-loud, storage location, no handoff in code comments
   - Entry point for AI new to the codebase

2. **`/home/tim/company/MAP.md`** (LOADABLE MAP)
   - The picture: canvas → runtime → fabric → store → mcp_face → nodes → voice
   - Self-maintains via `Suite.refresh_self_description()`
   - Live registry of what exists

3. **`/home/tim/company/STATE.md`** (STATUS + ACCEPTANCE SUITES)
   - What's built + proven (130 acceptance suites)
   - What's not built yet
   - How to run + verify
   - Auto-maintained drift check

4. **`/home/tim/company/runtime/AGENTS.md`** (THE SCHEDULER + SUITE)
   - Governs S1, C5, C6, S7
   - The brain of the system (suite.py, scheduler.py, bridge.py)
   - Where memoization + compilation + wiring happens

5. **`/home/tim/company/contracts/AGENTS.md`** (THE SPINE SPECS)
   - C1-C8 define everything (node-schema, storage, address, RHM, MCP)
   - Vault-ground (build-prep/contracts/ notes are the specs)
   - Code IMPLEMENTS, never redefines

6. **`/home/tim/company/tests/AGENTS.md`** (ACCEPTANCE SUITES AS PROOF)
   - Convention: done = green suite + use-evidence, never code-read-only
   - The drift-check mechanism (tests/drift_acceptance.py)
   - How to add a capability (fail-before → implement → pass)

7. **`/home/tim/company/ops/AGENTS.md`** (OPERATIONAL CONTROL)
   - One console (company CLI) for services, GPU, models
   - The resource manager (gpu.py VRAM fit-gate, measured on 16GB card)
   - Capability registry by model-id (tool_call, json_schema, thinking, context-ceiling)
   - Type-views expanding (services/GPU/models live; cognitive/RHM/data/jobs pending)

8. **`/home/tim/company/docs/vault-conventions.md`** (MARKDOWN FORMAT STANDARD)
   - Every .md follows frontmatter + schema
   - Ensures dual repo+vault coherence
   - Navigation + aliasing rules

9. **`/home/tim/company/canvas/AGENTS.md`** (UI/SURFACE DESIGN GATE)
   - Governs S5 (bridge protocol) + D3 (one substrate, per-type view-modes)
   - How the React+tldraw surface relates to runtime
   - Design-gating (what surfaces when)

10. **`/home/tim/company/store/AGENTS.md`** (CONTENT-ADDRESSING + PERSISTENCE)
    - Governs C1 (node-schema) + C4 (address-grammar)
    - Where everything lives (fs_store.py, graph_store.py, events.jsonl)
    - Durability guarantees + ext4-only (no /mnt/c, WSL fsync corruption)

---

## Key Insights for a Refresh Agent

1. **The system describes itself** — AGENTS.md files in every module, auto-maintained registries in MAP.md/STATE.md, and a drift-check that fails loud (`tests/drift_acceptance.py`). No hidden scatter.

2. **Tests ARE the record** — 130 acceptance suites indexed in STATE.md, each proving a capability. Drift-check fails if a suite isn't listed or a registered capability lacks a suite.

3. **Two design decisions anchor everything:**
   - **D3** ("one substrate, per-type view-modes") — the ops console (services/GPU/models) is the FIRST instantiation; cognitive/RHM/data/jobs are other view-modes of the same mechanism, not separate tools.
   - **PoLR-3** (path-of-least-resistance maintenance) — self-description maintained by the system itself (`Suite.refresh_self_description()`), so rot fails loud instead of silently.

4. **Modules by criticality:**
   - **CRITICAL (spine):** contracts, runtime, store, nodes, tests
   - **HIGH (faces):** canvas, mcp_face, ops
   - **HIGH (model layer):** fabric, roles, voice, ops/cli/capabilities.py
   - **SUPPORTING:** panels (governance), docs (meta), ops (command center)

5. **Self-Modification is audited:**
   - `selfmod_acceptance.py` + `selfmod_audit_acceptance.py` prove revertibility
   - `design_gate_acceptance.py` ensures surface-before-modify
   - `wire_adversarial.py` tests scope-overrun detection (build that touches paths outside declared scope → NOT closed)

6. **The Resource Manager (ops/cli/gpu.py) is the bridge between declare (config.gpu_util × vram_ceiling) and execute (actual fit-gate on `company up`):**
   - Measured on 16GB: 4B brain solo 256K context, co-resides with light voices at 64K, but Orpheus (~8.5GB) + 64K brain is over-budget (~0.6GB).
   - `capabilities.py` by model-id (tool_call, json_schema, thinking, context-ceiling, speed) JOINs to gpu.py for placement decisions.

7. **Voice is fully traced:** every turn writes to event log (voice.stream/voice.turn ops + voice.client steps from browser), reconstructable end-to-end from events.jsonl (introspective-data-building).

---

## Gaps / Pending

- **cognitive-layers · RHM/modes · data/memory · jobs/cron type-views** — announced in ops/AGENTS.md as pending; same mechanism when instantiated, not separate tools.
- **build-prep/** staging specs (concurrent-cognition, etc.) — not yet a code module; next TBD.
- **design/** aesthetic refinement — deferred (token-single-source idempotency not yet final).
