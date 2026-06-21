# AREA: runtime/ — The Engine Core

Survey date: 2026-06-21  
Area scope: `/home/tim/company/runtime/` — 77 .py files + 1 .json  
Surveyor role: EXTRACTOR — capture MORE, filter nothing, central model judges.

---

## PURPOSE

The `runtime/` module IS the Company's cognition engine. It contains every mechanism that makes the system think, decide, remember, and coordinate: the HTTP bridge (the operator console), the cognition engine (run_role/run_items/run_reduce), the reactive scheduler, every file-discovered registry (roles, flows, rules, projections, skills, contexts, decisions, etc.), the session fabric (supervisor, channels, clones, recall, scan), the resolver (4th primitive), the rule engine, the universal projection, and the voice/TTS routing. The module constitution lives in `runtime/AGENTS.md`.

**CONSTITUTION FILE**: `runtime/AGENTS.md` — the module rulebook. Defines: what the module IS, what it guarantees, how to extend it, all seams. Governs S1, C5, C6, S7. Laws: scheduler is generic over node-type; memo gate's only sanctioned re-run is VOLATILE=True; corpus pillar; session supervisor; staged-response queue; rule engine; run-output destinations; Group J cognition↔resolution feedback; decision→implementation wire.

---

## MAJOR SUB-AREAS

### 1. HTTP Bridge (`bridge.py` — 3370 lines)
**The operator console and external face.** Single-file, stdlib-only `ThreadingHTTPServer` on port 8770 (default). One brain (`SUITE = Suite(FsStore(fcfg.STORE_DIR), NodeRegistry().discover([...]))`), two faces: the bridge (HTTP) and the MCP face (shares the same Suite). `BRIDGE_ROUTES` is the single-source route table (registry-is-truth). Tests in `tests/bridge_routes_acceptance.py` drift-guard it.

### 2. Cognition Engine (`cognition.py` — 2778 lines)
**G0 spike + G1 substrate.** `run_role`, `run_items`, `run_reduce`, `run_chunked`, `run_swarm`, `resolve_address`. The loop that fires roles, manages VRAM via `SlotBudget`, and routes outputs through the rule engine.

### 3. Suite (`suite.py` — very large)
**ONE brain, two faces.** The shared core object. Imports scheduler, governance, NodeRegistry, RoleRegistry, ProjectionRegistry, FsStore. Shared by bridge + MCP. Defines `CONTENT_KINDS`, loads corpus element addresses from `design/_system/addresses.json`, provides `chat`, `chat_parts`, `dispatch_decision`, `surface_review`, `surface_build_intent`, `address_help`, `context_at`, `chats_at`, `query_corpus`, `resolve_role_binding`, `capability_providers`, `list_agent_sessions`, `set_dial`, `autodetect_mode`, `_gate_extension` (import-in-temp-dir gating).

### 4. Resolver (`resolver.py` — 80 lines)
**The 4th primitive.** Pure function `resolve(invariant, coordinate) -> dict`. `resolve_slot()` handles relationship-AST, select-dict, or literal. `ResolverError(ValueError)` — fail-loud on malformed slot. Delegates to `rules.evaluate` for continuous slots; uses `rules._get_path` for discrete select.

### 5. Rule Engine (`rules.py`)
**G3/L2 core.** `RULE_OPS` closed grammar, `DESTINATION_KINDS` (5 routing destinations). `evaluate()` is pure — no IO/model-call. Declared rules are dict-AST; NEVER eval/exec/compile. The predicate language all registries and the resolver use.

### 6. Reactive Scheduler (`scheduler.py`)
**Run graph executor.** `run(graph, store, node_types, branch, pause, force)`. Watches store, fires nodes when inputs resolve. `_memo_sig(ex, version, input_map)` — memoization signature using blake2b. Per-node error isolation: `failed: dict = {}`. Only `VOLATILE=True` nodes re-run.

### 7. Governance (`governance.py`)
**Action posture policy.** `AUTO / SURFACE / CONFIRM` per `action_class`. `LOCKED = {"source_data", "external", "frozen_contract"}` — forever CONFIRM. `guard()`, `posture()` functions.

### 8. Session Supervisor (`session_supervisor.py`)
**The fabric's process manager.** Binds 127.0.0.1:8771 ONLY (audit B3). SINGLE WRITER of `agent_sessions.*` events. Verbs: DELIVER / WAKE / CONSULT. `COMPANY_FABRIC_TURN_TIMEOUT_S` (default 900), `COMPANY_FABRIC_CONCURRENCY` (default 3), `COMPANY_FABRIC_PERMISSION` (default "plan"). Mailbox: `<store>/agent_sessions/mail.jsonl`.

### 9. Decision Stack (`decision_registry.py`, `decision_memory.py`, `decision_subtypes.py`)
**The decision lifecycle.** Registry of decisions (file-discovered `decisions/*.py`), compose_state fold, explanation grounding, never-assert law, subtype → card_variant + explanation_policy resolution.

### 10. Session Fabric Organs (`session_channels.py`, `session_lens.py`, `session_scan.py`, `session_recall.py`, `session_pointintime.py`, `session_search.py`, `session_lineage.py`)
**The layer AROUND sessions.** Channels, gatherings, connection edges, coordination modes. Structural + semantic views of past sessions. Point-in-time cloning (R3.4). Search-to-handle join.

### 11. Universal Projection (`projection.py`, `projections.py`, `scale.py`)
**Tim's equation: centre/angle/radius/depth.** `project()` is pure. Lens spaces that embed become vector spaces. Multi-scale pyramid for zoom (Group 11 — cluster-centroid rungs, not lineage).

### 12. Voice (`cc_voice.py`, `activation.py`, `activation_driver.py`)
**The always-on cognitive substrate.** Background / sense / rollup activation contexts. DORMANT by default (env gate `COMPANY_ACTIVATION_LOOP`). Manual tick via `POST /api/activation/tick`. TTS routing by engine (kokoro/chatterbox/orpheus/cosyvoice/xtts/qwen3tts).

### 13. Claude Code Fabric (`cc_board.py`, `cc_channels.py`, `cc_clone.py`, `cc_gate.py`, `cc_attachments.py`)
**Cross-session coordination and the Noticeboard.** Live injection into supervised sessions. Point-in-time clones. Typed board items (request/issue/tip/guide/idea) with per-type lifecycles. Channel attachments as a registry of bindings.

### 14. Implement / Wire (`implement.py`)
**Decision→implementation wire.** Group W. `permission_mode()` reads `COMPANY_WIRE_PERMISSION` call-time. `wire_armed()` — True ONLY when `COMPANY_WIRE_PERMISSION=acceptEdits`. Git checkpoint before close.

### 15. Brain Router (`brain_router.py`)
**Supervisor-as-loadable-brain.** `route_source(question)` → "fleet" | "recall" | "model". `ask()` = THE BRAIN. `recent_channel_context()` — L4 read tool. FAIL-SOFT: any down source degrades to 'model'.

---

## ALL /api ROUTES (from `BRIDGE_ROUTES` — the single-source table)

### Static / Pages
- `/studio` — the design-review portal (served page)
- `/design-system.css` — the generated corpus stylesheet
- `/mockups/` — mockup files served from `design/mockups/`

### GET Routes

| Route | What it does |
|-------|-------------|
| `/api/stream` | SSE event stream (live events from the store) |
| `/api/mockup-feedback` | Get feedback thread for a mockup |
| `/api/mockup-feedback/status` | Feedback status summary |
| `/api/corpus` | List corpus units |
| `/api/graph` | Get a single graph by id |
| `/api/graphs` | List all graphs |
| `/api/object_info` | Get info about an addressed object |
| `/api/cognition_info` | Cognition engine status (roles, nodes, capabilities) |
| `/api/types` | List all node types |
| `/api/layers` | List all projection layers |
| `/api/layer-dims` | Embedding dimensions per layer |
| `/api/models` | List all registered models/services |
| `/api/chat-models` | List chat-eligible models |
| `/api/fit` | Fit score for an address in a space |
| `/api/surfaced` | Currently surfaced items (the operator stack) |
| `/api/events` | Recent events from the store |
| `/api/now` | Current time + mode state |
| `/api/chat` | Chat history |
| `/api/conversations` | List conversations |
| `/api/conversation` | Single conversation by id |
| `/api/rhm-config` | Right-hand-man configuration |
| `/api/inbox` | Decision inbox (fast mark-composed state) |
| `/api/last-change` | Most recent self-change |
| `/api/self-change-log` | Self-build/apply/checkpoint audit log |
| `/api/panels` | Verdict panels registry |
| `/api/capabilities` | Full capabilities map (BRIDGE_ROUTES projection + registries) |
| `/api/capabilities/introspection` | Introspective capabilities |
| `/api/ui_info` | UI metadata at an address |
| `/api/scope` | Current scope/focus |
| `/api/address-help` | Address resolution help + context |
| `/api/context` | Context at an address |
| `/api/territory` | Territory for an address (brain-agnostic context composition) |
| `/api/up-translate` | Translate address up the hierarchy |
| `/api/self-changes-at` | Self-changes at an address |
| `/api/annotations` | Annotations at an address |
| `/api/presentation-pref` | Presentation preferences |
| `/api/chats` | Chats at an address |
| `/api/address-history` | History of an address |
| `/api/stale-at` | Staleness check at an address |
| `/api/ref-versions` | Reference versions for a ref |
| `/api/review/current` | Current review state |
| `/api/review/status` | Review pipeline status |
| `/api/journey/replay` | Replay a journey |
| `/api/journeys` | List journeys |
| `/api/voice` | Voice engine status |
| `/api/personas` | Voice personas |
| `/api/trial/sessions` | Trial session list |
| `/api/trial/transcript` | Trial session transcript |
| `/api/cognition/models_for_role` | Which models can serve a role |
| `/api/cognition/inputs` | Declared inputs for a role |
| `/api/cognition/field_types` | Field types for cognition |
| `/api/cognition/list_runs` | List past runs |
| `/api/cognition/find_runs` | Find runs by criteria |
| `/api/cognition/find_relations` | Find relations between corpus units |
| `/api/cognition/corpus` | Corpus query via cognition |
| `/api/cognition/neighbours` | Neighbours of a corpus unit in embedding space |
| `/api/roles` | List discovered roles |
| `/api/decisions` | List decisions |
| `/api/tools` | Tool face: MCP tool list + resolved human form_meta |
| `/api/run-stats` | Run statistics |
| `/api/knobs` | Current knobs state |
| `/api/voice/engine-knobs` | TTS engine knobs |
| `/api/voice/paths` | Voice capability paths |
| `/api/channels` | Session fabric channels |
| `/api/sessions` | Session fabric sessions |
| `/api/timeline` | Session timeline |
| `/api/board` | Noticeboard items |
| `/api/cascades` | Declared cascades |
| `/api/flows` | Flows registry |
| `/api/routines` | Routines registry |
| `/api/transcript-search` | Search session transcripts |
| `/api/session-recall` | Session recall (semantic) |
| `/api/channel-history` | Channel message history |
| `/api/session-describe` | Describe a session |
| `/api/stack-item-types` | Channel-stack item types |

### POST Routes

| Route | What it does |
|-------|-------------|
| `/api/stt` | Speech-to-text (full utterance) |
| `/api/voice/stt-partial` | Partial/streaming STT |
| `/api/tts` | Text-to-speech synthesis → wav |
| `/api/voice/finished-thought` | Signal end of voice thought |
| `/api/voice/switch` | Switch TTS engine (with co-residence VRAM shrink) |
| `/api/voice/log` | Log a voice event |
| `/api/run` | Run a graph |
| `/api/set` | Set a value in the store |
| `/api/move` | Move an addressed item |
| `/api/node` | Create/update a node |
| `/api/connect` | Connect two nodes (create edge) |
| `/api/delete-node` | Delete a node |
| `/api/conversation/new` | Start a new conversation |
| `/api/model/load` | Load a model service |
| `/api/model/config` | Configure a model (context window, gpu_util) |
| `/api/mode` | Set presence mode |
| `/api/coa` | Course-of-action submission |
| `/api/surface-output` | Surface a run output to the operator stack |
| `/api/surface-review` | Surface an item for Tim's review |
| `/api/capture-idea` | Capture an idea into the board |
| `/api/defer-offer` | Defer an offer |
| `/api/revive-offer` | Revive a deferred offer |
| `/api/build-intent` | Declare build intent |
| `/api/cognition/create_role` | Author and persist a new role |
| `/api/cognition/create_skill` | Author and persist a new skill |
| `/api/cognition/create_context` | Author and persist a new context |
| `/api/act` | Act on a surfaced item |
| `/api/annotate` | Annotate an address |
| `/api/apply` | Apply a proposed change |
| `/api/territory/write` | Write territory at an address |
| `/api/territory/label` | Label an address in the territory |
| `/api/tools/invoke` | Tool face: generic invoke door — FAIL-CLOSED operator gate |
| `/api/propose` | Propose a registry entry |
| `/api/decision` | Submit/update a decision |
| `/api/resolve` | Resolve a decision (surface_resolve) |
| `/api/revert` | Revert to a git checkpoint |
| `/api/checkpoint` | Create a git checkpoint |
| `/api/pin` | Pin an address |
| `/api/react` | React to a surfaced item |
| `/api/attach-chat` | Attach chat context to an address |
| `/api/approve-reach` | Approve a reach (cross-boundary action) |
| `/api/intent-at` | Declare intent at an address |
| `/api/review/start` | Start a review pass |
| `/api/review/next` | Advance review to next item |
| `/api/guide/start` | Start a guided walkthrough |
| `/api/walkthrough/start` | Start a walkthrough |
| `/api/journey/start` | Start a journey |
| `/api/journey/step` | Step through a journey |
| `/api/journey/stop` | Stop a journey |
| `/api/debrief/start` | Start a debrief session |
| `/api/mockup-generate` | Trigger mockup generation (autonomous, plan-by-default) |
| `/api/cognition/embed` | Embed a corpus unit into a space |
| `/api/cognition/preview_turn` | Preview a role turn without committing |
| `/api/cognition/run_role` | Run a single role |
| `/api/cognition/run_items` | Run roles over a set of items |
| `/api/cognition/run_reduce` | Run a reduction pass over items |
| `/api/cognition/role/propose` | Propose a new/edited role |
| `/api/cognition/role/edit` | Edit an existing role |
| `/api/cognition/role/delete` | Delete a role |
| `/api/cognition/role/dry_run` | Dry-run a role (no commit) |
| `/api/cognition/rule/attach` | Attach a rule to a role |
| `/api/cognition/rule/detach` | Detach a rule from a role |
| `/api/cognition/rule/validate` | Validate a rule declaration |
| `/api/cognition/rule/dry_run` | Dry-run a rule |
| `/api/trial/turn` | Run a trial conversation turn |
| `/api/trial/feedback` | Submit trial feedback |
| `/api/trial/reflection` | Request trial reflection |
| `/api/activation/tick` | Manual activation tick (fires background/rollup/mode-detect) |
| `/api/claude/turn` | S1 builder side-panel: one streaming Claude Code session turn |
| `/api/greeting` | S2 greeting: caught-up-in-one-glance morning summary |
| `/api/corpus-query` | S7 forager: semantic corpus query for the canvas |
| `/api/projection` | Universal projection render (Tim's equation) |
| `/api/scale/build` | Group 11: rebuild scale pyramid for a lens space |
| `/api/registry/proposals` | List registry proposals |
| `/api/registry/approve` | Approve a registry proposal |
| `/api/chat/stream` | SSE streaming chat turn |
| `/api/voice/stream` | SSE streaming voice turn |
| `/api/voice/turn` | Voice turn (non-streaming) |
| `/api/brain/ask` | Brain router: ask the RHM mind (fleet/recall/model source) |
| `/api/run-in-channel/propose` | Propose a run-in-channel action |
| `/api/decision/explain` | Grounded decision explanation walk-through |
| `/api/decision/decided-signals` | Signals of decided decisions |

**TOTAL: ~130 routes** (48 GET + 3 static + ~80 POST, including streaming variants)

---

## COMPLETE .py FILE INVENTORY

### Core Engine

#### `bridge.py` (3370 lines)
- **Purpose**: The HTTP bridge / operator console. Serves on port 8770.
- **Singleton**: `SUITE = Suite(FsStore(fcfg.STORE_DIR), NodeRegistry().discover([...]))` at module level. `ACTIVATION_CALLER = activation_driver.ActivationCaller(suite=SUITE)` (DORMANT).
- **Constants**: `ENGINE_PORTS = {"chatterbox":4124, "orpheus":4125, "cosyvoice":4126, "xtts":4127, "qwen3tts":4128}`. `TTS_URL` env-overridable default (kokoro).
- **Key helpers**: `_safe_mockup_path()`, `_feedback_path()`, `_corpus_index()`, `_apply_model_ctx()`, `_local_brain_key()`, `_tts_base_url()`, `_stream_parts()` (brain↔TTS overlap — producer thread + consumer thread pattern, C6.1), `_tool_manager()`, `_tool_meta()`, `_exposure()`, `_operator_overlay()`, `_tool_posture()`, `_tool_gate()` (FAIL-CLOSED), `_tool_is_consequential()`, `_semantic_projection()`, `_separator_projection()`, `_nucleation_projection()`, `build_projection()`, `_cog_emit()`, `_cog_resolve_role()`, `_cog_turn_id()`, `cog_run_role()`, `cog_run_items()`, `cog_run_reduce()`, `seed_demo()`
- **Handler**: `class H(BaseHTTPRequestHandler)` with `do_GET`, `do_POST`, `_stream` (SSE), `_chat_stream`, `_claude_stream`, `_voice_stream`
- **Startup**: `_warm_vector_cache()` daemon thread (X12-FAST warm vector index on startup)
- **Data reads**: `design/_system/corpus-meta.json`, `design/_system/addresses.json`, `remote_exposure.json`, `tool_operator_overlay.json`, `ops/services.json`, store (FsStore at `fcfg.STORE_DIR`)
- **Registries loaded**: NodeRegistry, RoleRegistry, ProjectionRegistry (via Suite)
- **Cross-refs**: suite.py, cognition.py, activation_driver.py, session_supervisor.py, implement.py, territory.py, brain_router.py, cc_board.py, cc_channels.py, cc_clone.py, cc_gate.py, cc_voice.py, cc_attachments.py, generate_mockup.py, ui_claude_session.py, session_channels.py, session_search.py, session_recall.py, session_lens.py, recall_determine.py

#### `cognition.py` (2778 lines)
- **Purpose**: Cognition engine G0 spike + G1 substrate.
- **Public functions**: `run_role()`, `run_items()`, `run_reduce()`, `run_chunked()`, `run_swarm()`, `resolve_address()`, `embed_corpus_to_spaces()`, `chat_parts_spike()`, `concurrency_probe()`
- **Class**: `SlotBudget` — reads `ops/services.json` for max_num_seqs/gpu_util; `_MEASURED_KV_BY_UTIL = {0.49: 66036, 0.63: 135574}`; `SlotBudget.from_registry()` (never hardcoded 32)
- **Constants**: `RESIDENT_BASE_URL = "http://127.0.0.1:8000/v1"`, `RESIDENT_MODEL = "cyankiwi/Qwen3.5-4B-AWQ-4bit"`, `ROLE_TIMEOUT = 60`
- **`INJECTION_RULE`**: the first declared data-AST rule (recall.relevant AND ground.in_scope) — G3 generalization
- **Input axis**: `_declared_inputs()`, `_supplied_extra()`, `_is_default_input()`, `_resolve_input_value()`, `_embed_text_for()`
- **run:// addressing**: every engine output persists to `run://<turn>/<role>` via CAS + set_ref
- **Imports**: `Role`, `RoleRegistry` from `runtime.roles`; `SkillRegistry`, `ContextRegistry` from `runtime.skills`; `decision_registry()`, `generation_policy_registry()`

#### `suite.py` (very large)
- **Purpose**: ONE brain, two faces. Shared core object.
- **`CONTENT_KINDS`**: `("constant", "document", "code", "file", "image", "source", "portal")`
- **`THOUGHT_SHAPES`** / **`PART_GRAIN`**: registered here — linear-stream/reduce-tree/jury-select/scatter-route/scatter-write
- **`_load_corpus_element_addresses()`**: loads from `design/_system/addresses.json`
- **Key methods**: `chat()`, `chat_parts()`, `dispatch_decision()`, `surface_review()`, `surface_build_intent()`, `address_help()`, `context_at()`, `chats_at()`, `query_corpus()`, `resolve_role_binding()`, `capability_providers()`, `list_agent_sessions()`, `set_dial()`, `autodetect_mode()`, `_gate_extension()` (import-in-temp-dir gating for role authoring), `_SELF_CHANGE_STREAMS` (unified ledger: `[self-build]`/`[self-apply]`/`[checkpoint]` git commits)
- **Imports**: scheduler, governance, NodeRegistry, RoleRegistry, ProjectionRegistry, FsStore, implement

#### `scheduler.py`
- **Purpose**: Reactive scheduler — watches store, fires nodes when inputs resolve.
- **`run(graph, store, node_types, branch, pause, force)`**: the main entry point
- **`_memo_sig(ex, version, input_map)`**: blake2b memoization signature
- **`failed: dict = {}`**: per-node error isolation (never aborts the whole run)
- **VOLATILE=True**: the only sanctioned re-run bypass of the memo gate

#### `governance.py`
- **Purpose**: Action posture policy.
- **Constants**: `AUTO, SURFACE, CONFIRM = "auto", "surface", "confirm"`; `LOCKED = {"source_data", "external", "frozen_contract"}`
- **`POLICY`**: dict — action_class → posture
- **`guard()`**, **`posture()`**: the two public functions

#### `rules.py`
- **Purpose**: Rule engine G3/L2. Pure evaluator, no IO.
- **`RULE_OPS`**: closed grammar (AND/OR/NOT/GT/LT/EQ/IN/…)
- **`DESTINATION_KINDS`**: 5 routing destinations
- **`evaluate()`**: pure — never eval/exec/compile
- **`_get_path()`**: for discrete select in resolver

#### `resolver.py` (80 lines)
- **Purpose**: The 4th primitive. Pure.
- **`resolve(invariant, coordinate) -> dict`**: the main function
- **`resolve_slot()`**: handles relationship-AST, select-dict, literal
- **`ResolverError(ValueError)`**: fail-loud on malformed slot
- **Delegates**: to `rules.evaluate` for continuous; `rules._get_path` for discrete

### Decision Stack

#### `decision_registry.py`
- **Purpose**: File-discovered decision registry (`decisions/*.py`).
- **`DECISION_FIELDS`**: `("id", "address", "meaning", "options", "explanation_source", "scope", "legibility", "subtype", "owner")`
- **`DECISION_REQUIRED`**: `("id", "meaning", "options")`
- **`compose_state()`**: pure fold — decision row + decision_take marks → resolved state
- **`decision_inbox()`**: fast mark-composed state (GPU-free)
- **`DecisionRegistry`**: dict-like, file-discovered

#### `decision_memory.py`
- **Purpose**: Explain half's memory retrieve + never-assert law.
- **`explanation_grounding(SUITE, decision)`**: retrieve grounded memory for a decision
- **`DEFAULT_DECISION_SPACES`**: `("common_knowledge", "principles", "worldview", "topics", "history", "repo")`
- **`EXPLAIN_DECISION_SPACES`**: adds "extractions" (not hot-path)
- **`_CTX_FLOOR = 0.5`**: cross-encoder relevance floor (prevents topic-bleed)
- **Theorem-fork texts**: `THEOREM_FORK_CAVEAT_OPERATOR`, `THEOREM_FORK_CAVEAT_BANNER`, `THEOREM_FORK_GROUNDING_SOURCE` — the never-assert law's canonical texts

#### `decision_subtypes.py`
- **Purpose**: File-discovered decision-subtype registry (`decision_subtypes/*.py`).
- **`DecisionSubtype`** dataclass: `id`, `card_variant`, `explanation_policy`, `spec`
- **`DECISION_SUBTYPE_FIELDS`**: `("id", "card_variant", "explanation_policy", "required_elements", "owner", "desc")`
- **`REQUIRED_FIELDS`**: `("id", "card_variant", "explanation_policy")`
- **Chain**: `decision.subtype` → row → (a) `card_variant` (DNA renders), (b) `explanation_policy` (fork's `run_role`), (c) `required_elements` (gate checks)
- **`DecisionSubtypeRegistry`**: dict-like, file-discovered

### Registries

#### `registry.py`
- **Purpose**: `NodeRegistry` — file-discovered node types.
- **`discover(dirs)`**: loads node types from `nodes/*.py`
- **`_read_output_schema()`**, **`_load_module()`**: discovery helpers
- **`CONTENT_KINDS`**: `("constant", "document", "code", "file", "image", "source", "portal")`

#### `roles.py`
- **Purpose**: `RoleRegistry` — file-discovered roles (`roles/*.py`).
- **Role schema fields**: id/label/description/prompt_template/output_schema/input_addresses/op/trigger/model_binding/mode_scope/rules/render_hint/draws/verdict_rule/knobs/thinking/output/tools/context
- **`RoleRegistry`**: dict-like, fail-loud `_build_role` — a malformed role.py takes down ALL discovery

#### `flows.py`
- **Purpose**: `FlowRegistry` — file-discovered flows (`flows/*.py`).
- **`FLOW_FIELDS`**: `("id", "label", "description", "params", "proposes_only")`
- **`proposes_only: True`** required — flows ONLY propose, never execute directly

#### `routines.py`
- **Purpose**: `RoutineRegistry` — file-discovered routines (`routines/*.py`).
- **`ROUTINE_FIELDS`**: frozen set of allowed fields
- **Fire mechanism**: in `routine_runner.py`; trigger via systemd timer or MCP op=fire

#### `projections.py`
- **Purpose**: `ProjectionRegistry` — file-discovered projection lenses (`projections/*.py`).
- **Schema fields**: id/level/produced_by/embeds/field/enum/desc/stage
- **`embeds: True`**: becomes a vector space
- **`produced_by: "model"`**: LLM path; `produced_by: "code"`: lifters

#### `skills.py`
- **Purpose**: `SkillRegistry` + `ContextRegistry` — file-discovered skills (`skills/*.py`) and contexts (`contexts/*.py`).
- **Schema**: id/content/label/description
- **Address scheme**: `skill://<id>` and `context://<id>` resolve to the content
- **Reuse**: same importlib discovery mechanism as `RoleRegistry` — not a new mechanism

#### `axis_registry.py`
- **Purpose**: `AxisRegistry` — file-discovered coordinate axes (`axes/*.py`).
- **Row shape**: id/namespace/fields (sub_field: continuous|discrete)
- **Law**: axes ARE registries; adding a new axis = dropping a file, zero engine code change
- **CAVEAT**: the surface projection axes list (device/viewer/mode/…) is NOT the formal root axes — Tim+fork determine the root set; these are "swappable DATA"

#### `lifter_registry.py` (renamed from `lifters.py` 2026-06-18)
- **Purpose**: File-discovered lifter registry (`lifters/*.py`) — deterministic extractors for `produced_by:"code"` projections.
- **Rename reason**: shadowed the top-level `lifters/` namespace package — caused `from lifters.frontmatter` to bind to THIS module instead of the package.
- **Row shape**: id/match-callable/description
- **Self-contained**: mirrors ProjectionRegistry mechanism

#### `generation_policies.py`
- **Purpose**: File-discovered generation-policy registry (`generation_policies/*.py`).
- **Purpose**: Per-content generation regime (rep_penalty ladder, diff_against_source flag).
- **Core problem it solves**: greedy temp0 + grammar-constrained long arrays → degenerate repetition loop (~20% of real files; `frequency_penalty` is WRONG — it penalises JSON structure). Fix: `repetition_penalty LADDER` as declared data.
- **Row shape**: id/penalty_ladder/diff_against_source/description

#### `verdict_panels.py`
- **Purpose**: File-discovered verdict-panel registry (`verdict_panels/*.py`).
- **Panel fields**: id/label/description/seats (list of role ids)/quorum_rule
- **Purpose**: PERSPECTIVE-DIVERSE jury — each seat = a different lens role (vs `run_jury` which varies ONE role N times). Catches what redundancy can't.
- **Combine**: DETERMINISTIC (grounded-seats >= quorum), no model

#### `mark_types.py`
- **Purpose**: File-discovered mark-type registry (`mark_types/*.py`).
- **Mark shape**: target/mark_type/value/confidence/source_pass/evidence/status
- **Row shape**: id/value_shape/direction/label/description
- **Known mark types**: gold-likelihood, ai-fingerprint, contradiction, corroboration

#### `item_types.py`
- **Purpose**: File-discovered board item-type registry (`item_types/*.py`).
- **Row shape**: id/initial/states/transitions (lifecycle state machine)/label/desc
- **Current types**: request/issue/tip/guide/idea (seeded from gather)

#### `attachment_types.py`
- **Purpose**: File-discovered channel attachment-type registry (`attachment_types/*.py`).
- **Row shape**: id/label/target_kind ("address"|"path"|"scope")/multi (bool)
- **Distinction**: TYPE registry (kinds); BINDINGS are records in `cc_attachments.py`

#### `source_types.py`
- **Purpose**: File-discovered board source-type registry (`source_types/*.py`).
- **Row shape**: id/label/join_keys/desc
- **Design intent**: GitHub + Claude Code transcripts can JOIN on shared keys (author/path/time) — "no migration later"

#### `relation_types.py`
- **Purpose**: File-discovered relation-type registry (`relation_types/*.py`).
- **Known types**: principle-beneath, fragment-of, contradicts, sibling
- **Row shape**: id/directed (bool)/parent_role/child_role/label/desc
- **Used by**: `find_relations` (L3) — the inversion-finder

#### `stack_item_types.py`
- **Purpose**: File-discovered channel-stack item-type registry (`stack_item_types/*.py`).
- **Distinct from `item_types.py`**: board items have LIFECYCLE (states/transitions); stack items have RENDER/DISPATCH contract (row_fields/settled-predicate/open_verb)
- **Types**: presentation/explanation/decision-sequence/verify-request

#### `dials.py`
- **Purpose**: File-discovered dials registry (`dials/*.py`).
- **Row shape**: id/label/governs/positions (ordered {name,meaning})/default
- **Values persist**: on the system graph's dials config node
- **Set via**: `Suite.set_dial` / MCP `dials` tool
- **Overrides**: condition-scoped ({when, value}) — stored+validated today, evaluated when the now-organ + rules wiring exists

#### `ai_tics.py`
- **Purpose**: File-discovered AI-tic registry (`ai_tics/*.py`).
- **Known tics**: framework-imposition, versioning, false-finality, silent-fallback, agent-arch, closure-form, MVP
- **Use**: fingerprint pass (M4) matches coined-vocab projection against this registry → `ai-fingerprint` marks (direction: subtract — denoising)

#### `operator_memory.py`
- **Purpose**: File-discovered operator-memory registry — declared things known about working with Tim.
- **Row shape**: id/rule/why/evidence (list of {quote,source?})/scope?/status (confirmed|proposed)/confirmed?
- **Lifecycle**: transcript mining proposes → Tim confirms → standing
- **Purpose**: memory ALL agents get (RHM, crew, external agents via MCP)

#### `mode_detection_rules.py`
- **Purpose**: File-discovered mode-detection-rule registry (`mode_detection_rules/*.py`).
- **Row shape**: signal condition (a `rules.RULE_OPS` data-AST) + candidate mode
- **Replaced**: hardcoded `MODE_DETECTION_RULES = [{..., "when": lambda s: ...}]` in `activation.py` — lambda = code, not authorable data
- **Used by**: `activation.detect_mode_candidate` — walks rules in priority order, first-match-wins

#### `minds.py`
- **Purpose**: `MindRegistry` — file-discovered composable minds (`minds/*.py`).
- **Mind kinds**: `role` (binds a roles/ id), `model` (binds a cap://), `composition` (ordered list of minds with typed order-edges), `binding` (mode→mind bind as registry data)
- **Four locked signatures**: `mind_registry()`, `.resolve(id)`, `traverse(composition_row, store)`, `binding_for_mode(mode)`
- **Reuse**: mirrors RoleRegistry; `run_swarm` byte-identical

#### `forms.py`
- **Purpose**: File-discovered form registry (`forms/*.py`) — file-shape → effort-routing rules.
- **Known forms**: log/registry/decision/prose/stub
- **Row shape**: id/match (callable: text, meta → bool)/effort_band/generation_policy_hint
- **Purpose**: effort-routing by form made DATA — don't burn full capture depth on logs

#### `checks.py`
- **Purpose**: File-discovered check registry (`checks/*.py`) — deterministic gates.
- **Row shape**: id/label/description + module-level `check(value, **params) -> {passed, reasons}` callable
- **Purpose**: referenceable by name from cascade decls (`{op:'check', check:'<id>'}`); declared chains carry their own floors

#### `context_variables.py`
- **Purpose**: `ContextVariable` registry — per-turn context resolution for the RHM.
- **Cost vocabulary**: `cheap` | `loads-model` | `loads-corpus`
- **Graph**: `Graph`, `NodeInstance` from contracts
- **Purpose**: RHM's context is NOT a fixed prompt — it RESOLVES per turn, same operation as node-inputs

### Session Fabric

#### `session_supervisor.py`
- **Purpose**: Process manager for `claude -p --input-format stream-json` sessions.
- **Binds**: 127.0.0.1:8771 ONLY (audit B3)
- **Verbs**: DELIVER / WAKE / CONSULT
- **Env**: `COMPANY_FABRIC_TURN_TIMEOUT_S` (default 900), `COMPANY_FABRIC_CONCURRENCY` (default 3), `COMPANY_FABRIC_PERMISSION` (default "plan")
- **Mailbox**: `<store>/agent_sessions/mail.jsonl`; per-consumer cursor ref
- **SINGLE WRITER**: of `agent_sessions.*` events

#### `session_channels.py`
- **Purpose**: Cross-session fabric organs (R2.2–R2.5) — channels, gatherings, connection edges, coordination modes.
- **Storage**: `<store>/agent_sessions/channels.jsonl` (twin of `mail.jsonl` — graph-locked, append-only, fsync'd)
- **Closed vocabularies**: `CHANNEL_OPS / KINDS / MODES / PARTICIPATION / ROW_STATUS`
- **Routing law**: NEVER wakes/spawns a broadcast; `supervised-live → "deliver"`, else `→ "queue"`
- **Connection edges**: a PROJECTION of the mail log, folded at read time — not stored separately

#### `session_scan.py`
- **Purpose**: Programmatic session scan — one streaming pass over a transcript → projectable DATA.
- **Outputs**: rows (ndjson, one row per event) + summary (totals, attribution, model distributions, boundary timeline, gaps, dense-message profile)
- **Boundary detection**: STRUCTURAL (compact_boundary event or isCompactSummary==true) — never text-based
- **CLI**: `python3 -m runtime.session_scan <transcript.jsonl> [--out-dir DIR]`
- **API**: `scan_session(path) -> {summary, rows}`; `write_scan(path, out_dir) -> {paths}`

#### `session_recall.py`
- **Purpose**: Semantic recall over a session transcript.
- **Embedder**: POST `:8007/v1/embeddings`, model `pplx-embed-context-v1-4b`, DOCUMENTS-mode, dim 2560, int8/unnormalized
- **Rerank**: `ops/rerank.py Reranker(backend="jina-v3", device="cpu")` — CPU, 0 VRAM
- **Fail-loud**: embedder down → TEACHING error ("company up embed-pplx"), never silent empty
- **CLI**: `python3 -m runtime.session_recall <jsonl> "<query>" [--k N] [--no-rerank]`

#### `session_pointintime.py`
- **Purpose**: Point-in-time session launch (R3.3/R3.4).
- **Mechanism**: prefix-truncate transcript + rewrite sessionId/UUIDs (uuid5 deterministic) + stamp `forkedFrom` provenance → new session file → native `claude --resume <new-id>`
- **Core insight**: JSONL prefix ending at T = file as it existed at T — a state that was resumable then

#### `session_search.py`
- **Purpose**: Search-to-handle join (R4.2/R4.5) — search hit → live session handle.
- **Two modes**: `semantic` (embedding search via venv-bridge to chromadb, GPU needed) and `lexical` (sqlite term search, always available, zero GPU)
- **Handle shape**: session_id + live registry state (joined at query time) + matched point + launch-ready commands

#### `session_lineage.py`
- **Purpose**: Lineage + distance map across sessions (§1.4/§1.5).
- **Mechanism**: discovers fork tree via `forkedFrom` provenance field (STRUCTURAL); computes trunk + divergence distances (time-span, message counts, output tokens)
- **API**: `build_lineage([paths]) -> {nodes, edges, distances, narrative}`

#### `session_lens.py`
- **Purpose**: Lenses over a scanned session — the useful-questions layer.
- **Lenses**: `find(q)`, `decisions(topic)`, `open_loops()`, `catch_up(since)`, `timeline(topic)`, `directives()`
- **Substrates**: structural rows (session_scan) + semantic index (session_recall)
- **CLI**: `python3 -m runtime.session_lens <jsonl> <lens> [arg]`

### Voice and Activation

#### `activation.py`
- **Purpose**: Concurrent Cognition G5 — activation contexts (background/sense/rollup).
- **Three non-turn triggers**: background (idle-loop tick), sense (event-hook), rollup (timer tick → introspective data consolidation)
- **Laws**: activation contexts are DECLARED registry data (L1); a model runs only inside a ROLE (L2); run:// addressing; the FLOOR (G9/C9.2 — no resolve/approve/dispatch from activation); the RESERVE IS SACRED (SlotBudget, global_vram_gate)
- **Entry points**: `fire_activation()`, `consolidate_rollup()`

#### `activation_driver.py`
- **Purpose**: The always-on caller — Group H/I completion.
- **DORMANT by default**: `COMPANY_ACTIVATION_LOOP` env gate (same posture as `wire_armed()`)
- **Manual drive seam**: `activation_tick()` + `POST /api/activation/tick` — LIVE, fires roles
- **Autonomous background loop**: OFF BY DEFAULT — enabling is a behavior change the operator greenlights
- **On each clock tick**: `background_tick()` (idle gate decides), `RollupDriver.tick()`, `propose_mode()`, `sense_tick()` ONLY when a REAL sense event is supplied

#### `cc_voice.py`
- **Purpose**: Text-to-voice via the Company's resident TTS engine.
- **Mechanism**: discovers whichever `tts-*` engine is UP from the registry, POSTs text, saves WAV
- **Playback**: device-side (the operator/UI); this module only renders
- **Output dir**: `.data/voice/`

### Implement / Wire

#### `implement.py`
- **Purpose**: Decision→implementation wire (Group W).
- **Constants**: `DEFAULT_TIMEOUT_S = 900`, `CONCURRENCY_CAP = 3`, `CLAUDE_BIN = "claude"`
- **`permission_mode()`**: call-time read of `COMPANY_WIRE_PERMISSION` (default "plan")
- **`wire_armed()`**: True ONLY when `COMPANY_WIRE_PERMISSION=acceptEdits`
- **`REPO_ROOT`**: the repo root path

### Brain

#### `brain_router.py` (150 lines)
- **Purpose**: Supervisor-as-loadable-brain backend.
- **`route_source(question)`**: deterministic keyword match → "fleet" | "recall" | "model"
- **`_FLEET_HINTS`**, **`_RECALL_HINTS`**: keyword routing tables
- **`ask(question, *, suite, aim, graph_id)`**: THE BRAIN — the backend for `/api/brain/ask`
- **`recent_channel_context(suite, ...)`**: L4 read tool (READ-ONLY, never posts)
- **`_fleet_answer()`**: READ + PROPOSE (describes fabric state, surfaces gated actions — NEVER spawns)
- **`_model_answer()`**: Suite.chat fallback
- **FAIL-SOFT**: any down source degrades to 'model' with a note, never a crash

### Projection and Scale

#### `projection.py`
- **Purpose**: Universal projection engine.
- **Tim's equation**: centre / angle / radius / depth
- **`project()`**: pure function
- **`BINDING_FIELDS`**: `("id", "label", "angle_from", "radius_from")`
- **Legibility registries**: `_KIND_META`, `_NODE_TYPE_META`, `_GROUP_META`, `_PROJECTION_SPACE_META` (loaded defensively)

#### `projections.py`
- **Purpose**: `ProjectionRegistry` — file-discovered lenses.
- **Schema**: id/level/produced_by/embeds/field/enum/desc/stage
- **`embeds: True`**: makes it a vector space; `produced_by: "model"` → LLM; `produced_by: "code"` → lifters

#### `scale.py`
- **Purpose**: Group 11 — multi-scale embedding pyramid (the instrument's ZOOM axis).
- **Mechanism**: cluster-centroid rungs (NOT lineage provenance — proved that the session axis is capture-batch, not semantic nest)
- **Clustering**: Ward hierarchical (NOT per-K k-means) — rungs MUST NEST; dendrogram cut at each rung guarantees nesting
- **Pure read**: over unit vectors Group 8 already persisted — no re-embed, no re-chunk

### Noticeboard and Channels

#### `cc_board.py`
- **Purpose**: Company Noticeboard runtime (Tim's "inward-facing half").
- **Storage**: `channel-memory/noticeboard/<id>.md` (id-keyed flat, md+frontmatter, git-tracked)
- **Address**: `board://<id>` — FLAT (identity holds nothing mutable)
- **Links**: typed edges `[{kind, target}]` — `kind` validated against relation/edge registry
- **Lifecycle**: per-type, lives ON the item-type row; `transition` moves along registry-declared legal states
- **Registries loaded**: item_types, source_types, board_edges

#### `cc_channels.py`
- **Purpose**: Cross-session channel fabric core — live injection transport.
- **Storage**: `.data/channels/<handle>.json` per session
- **`live_sessions()`**: every channel-session whose process is alive
- **`push(handle, content)`**: inject into a live session
- **Thread routing**: reply pushed back into the asker's live session (no polling); every message/reply appended to channel mail log

#### `cc_clone.py`
- **Purpose**: Point-in-time clone → fabric (the safe autonomous path).
- **Mechanism**: materialize at past point (`session_pointintime`) → launch via supervisor (supervised+inject) → register in fabric clones registry
- **Why supervised+inject NOT interactive channel**: interactive `claude --dangerously-load-development-channels` is BLOCKED by the safety classifier for autonomous agents

#### `cc_gate.py`
- **Purpose**: Per-step GATE / ABORT / REWIND as an observer on the native mechanism.
- **GATE**: records gate-state; pause rides the NATIVE `blocks_execution` declaration (claude's own loop)
- **ABORT**: reuses supervisor's existing /interrupt + /teardown (no-orphan law)
- **REWIND**: `session_pointintime.materialize_at_point` (the native fork transform)
- **Step reference**: opaque step-ADDRESS (`session://<sid>/step/<tool_use_id>`) — stored verbatim, NEVER parsed

#### `cc_attachments.py`
- **Purpose**: Channel-attachment bindings registry — {id, channel, attachment_type, target, added}.
- **Design**: a REGISTRY OF BINDING ROWS, NOT a mutable field on the channel record
- **Manifest**: `{sessions, docs, recall_scope, …}` is a PROJECTION of the rows — a VIEW, not stored
- **`target`**: opaque ref (board://<id>, session://<id>) — resolved by address scheme, never parsed here

### Corpus and Memory

#### `corpus.py`
- **Purpose**: Corpus-record wrapper over FsStore.
- **`write_record()`**: refuses missing lineage (fail-loud)
- **Event kind**: `corpus.record` (distinct from `op.run`)
- **Three lineage axes**: corpus (session/round/project), store provenance-lineage, decision-lineage
- **`list_corpus()`**, **`find_corpus()`**: read-time projections

#### `corpus_neighbours.py`
- **Purpose**: Neighbour node-field — given a corpus unit's address, units AROUND it in a space.
- **Mechanism**: unit's persisted per-space vector → `store/vector_index.query_index` over that space → drop self
- **Each neighbour's `source`**: a `code://` address — directly projection:select-able
- **Fail-loud**: unit with no persisted vector → honest note + empty field (never fabricated/zero-vector nearest)

#### `corpus_rerank.py`
- **Purpose**: Optional rerank precision stage over corpus retrieval.
- **Chain**: pplx cosine top-K → jina-v3 cross-encoder reorder (`:8008`, CPU/0-VRAM)
- **Toggle, FAIL-LOUD**: once asked, reranks or raises — never fabricated/blank-text score
- **Proven**: "backfill.ts #1 @0.579 narrow" → "backfill.ts #1 @+0.321 decisive gap" after rerank

#### `recall_determine.py`
- **Purpose**: Grounded determine over the dragnet extraction layer (engine).
- **Asset**: `.data/store/extractions/extractions-<name>.jsonl` (extract-once / determine-many)
- **Anti-confabulation**: NO-FICTION GROUNDED reduce — model CLUSTERS real extraction claims BY INDEX (groups+theme-labels ONLY, never generates claim text); every output claim is verbatim real extraction with chunk_id provenance; no-fiction check verifies every returned index is valid

### Coherence Subsystem

#### `coherence_detect.py`
- **Purpose**: Structural coherence detectors (AST-grounded, model-free).
- **`extract_routes(bridge_src)`**: AST-extract every `/api/...` route literal — structurally immune to regex/comment false positives
- **Design**: static analysis over-calls dead (safe direction — a false orphan is caught downstream); never DECLARES something wired that is dead (the dangerous false-wire direction)

#### `coherence_actions.py`
- **Purpose**: Chains/graphs as configurable saveable ACTIONS (Group E, saving side).
- **`build_action(decl, *, models, roles, ...)`**: ONE validation door — compiled/hand-written/saved all gate here
- **`build_coherence_info()`**: pure projection (reflects-never-owns)
- **`_VALID_OPS`**: `("generate", "embed", "similarity", "retrieve", "detect", "reduce", "check")`

#### `coherence_calibrate.py`
- **Purpose**: Calibration harness (Group D) — turns detector trust from assertion to measured numbers.
- **`load_fixtures(path)`**: labelled eval set from captured incidents
- **`score_reachability(fixtures, classify)`**: per-config measurement
- **Design**: same scorer works for structural (model-free) and semantic (N model/embedding configs)

### Context and Authoring

#### `context_ops.py`
- **Purpose**: Live context-window READ + COMPACT over the session supervisor (S-R10.1).
- **Mechanism**: inject `/context` or `/compact` into a supervised-live session, capture the declared event it emits
- **`/context`**: emits `system/local_command_output` with usage breakdown
- **`/compact`**: emits `system/compact_boundary`; session re-inits + memory survives

#### `authoring.py`
- **Purpose**: Authoring backend (C7.4/C7.5) — the ONE place a role's declared fields become a real `roles/<id>.py` module.
- **Gate**: validates a generated module by importing it in a temp dir (mirrors `Suite._gate_extension`) — a malformed role.py would take down ALL role discovery
- **`render_role_source(fields)`**: fields → Python source string
- **Pure half**: propose→approve→apply lives in Suite; this module is only the renderer and gater

#### `compile.py`
- **Purpose**: C5 (Part 2) — workflow → execution graph compilation.
- **`_addr(graph_id, node_id, branch)`**: logical run-address of a node's output (`run://<graph.id>/<node>`)
- **Design**: runtime recompiles each run, so editable face and runnable face never drift

### Render and Display

#### `render_declaration.py`
- **Purpose**: Render-declaration layer (S-R1.2) — every session event mapped to a typed UI declaration.
- **Registry**: `runtime/render_declarations.json` — placement/component/update-target/stream-accumulator/blocks-execution/field_map
- **Lookup law**: `exact "type/subtype" → family "type/*" → bare "type" → UNDECLARED`
- **NO SILENT DROPS**: unmatched event → `UnknownEvent` declaration, `undeclared: true`, gap recorded
- **`render_declarations.json`**: the data file (also in this directory)

### Model Routing

#### `model_routing.py`
- **Purpose**: `resolve_model(intent)` — the ONE model-selection resolver (unification #71).
- **Unifies**: `roles.resolve_binding()` + `Suite.capability_providers()` + `cc_clone._pick_ollama_model()`
- **Intent shapes**: `{kind:"clone", context_tokens:int, model?:str}`, `{kind:"role", role_id:str}`, `{kind:"capability", capability:str|list}`
- **Returns**: `{model, base_url, provider, why, satisfied, ...}`
- **PHASE**: Phase 1 only — resolver + registry data exist; NOTHING wired through it yet. Phase 2 wires live firing paths.
- **FLOOR NOTE**: `roles.resolve_binding` does NOT raise when no provider matches a role with `default_model` — it SILENTLY FLOORS to the resident 4B. A role re-tier can "look resolved" but actually used the wrong model.

### Session Support

#### `session_supervisor.py` (already covered above)

#### `ui_claude_session.py`
- **Purpose**: Claude Code side-panel session (overnight S1).
- **Permission**: `COMPANY_PANEL_PERMISSION` (default 'plan' — read/investigate; edits need env opt-in)
- **Transport**: claude CLI stream-json (subprocess per turn; `--resume <session_id>` carries conversation)
- **OPERATOR-FACE ONLY**: never imported by mcp_face
- **Cross-import**: `session_supervisor.py` imports `_find_claude` + `_MCP_CONFIG` from here (one source)

### Territory

#### `territory.py`
- **Purpose**: `territory_for(address)` — the address→territory composer.
- **GPU-FREE**: every leg is a registry/structural read; nothing embeds
- **DEGRADE CONTRACT**: (1) non-address → RAISES (fail-loud); (2) non-resolvable scheme → identity noted-absent, relations still tried; (3) nonexistent record → identity noted-absent (NOT propagated crash); `territory_prose` NEVER raises
- **Composes**: `cognition.resolve_address` (9 schemes), `suite.address_help/context_at/chats_at`, `cc_board.relations`

### Supabase and Channel Boundary

#### `supabase_principal.py`
- **Purpose**: Least-privilege Supabase principal (authenticated login → JWT, Bearer).
- **NOT service-role**: grant_type=password OR refresh_token; cached + refreshed
- **Env prefix-parameterized**: `{PREFIX}_SUPABASE_URL`, `{PREFIX}_ANON_KEY`, `{PREFIX}_SA_EMAIL+PASSWORD` or `{PREFIX}_SA_REFRESH_TOKEN`
- **FAIL-LOUD (RAISES)**: never a silent token
- **ONE HOME**: `channel_boundary.py` uses it from birth (prefix "COMPANY_CHANNEL"); `vi_vision.py` migrates onto it (prefix "VI_VISION")

#### `channel_boundary.py`
- **Purpose**: Company-side PUBLISH/READ boundary for shared channels (Supabase single-source).
- **PUBLISH**: company session → Supabase `channel_posts` directly (NOT also injected locally)
- **INJECT**: outbound Realtime subscription → inject into live company member-sessions (skip-by-ORIGIN); BOTH 'session' AND 'client' rows inject
- **Security**: authenticates as dedicated RLS-scoped principal (supabase_principal.py), NEVER service-role

#### `channel_boundary_run.py`
- **Purpose**: Boundary entrypoint — brings the shared-channel edge LIVE.
- **ENV loading**: `.boundary.env` (default `build-prep/claude-design/supabase/.boundary.env`), overridable via `COMPANY_CHANNEL_ENV_FILE`; existing `os.environ` takes precedence
- **Canonical keys**: `COMPANY_CHANNEL_SA_EMAIL + COMPANY_CHANNEL_SA_PASSWORD + COMPANY_CHANNEL_ANON_KEY + COMPANY_CHANNEL_SUPABASE_URL`
- **INJECT primitive**: `cc_channels.push` (PUSH-only — no local `_mail.jsonl` record; Supabase is the store)

#### `vi_vision.py`
- **Purpose**: Factory's address good-part, built INTO the company spine.
- **`resolve_vi_vision(addr)`**: `vi-vision://` READ branch
- **`write_vi_vision(addr, definition, …)`**: WRITE step's factory target
- **RLS**: `vd_component_read` (global or user_id match) + `vd_component_write` (user_id match)
- **Uses**: `supabase_principal.py` (migration from own inline principal code — marked as "named follow-up")

### Miscellaneous Registry-Type Modules

#### `anchors.py`
- **Purpose**: Planted poles for the two-gravity separator (Group 9).
- **`anchor://ai-corner`**: AI's own characterization of AI-deformation — dense prose so it embeds as a direction
- **Run**: `python3 -m runtime.anchors` plants the anchor in the topics lens
- **Fail-loud**: uses bridge embedder (bridge must be live)

#### `minds.py` (already covered in Registries)

#### `mode_detection_rules.py` (already covered in Registries)

#### `ai_tics.py` (already covered in Registries)

#### `operator_memory.py` (already covered in Registries)

### Routine Support

#### `routine_runner.py`
- **Purpose**: Fire a routine through the session supervisor.
- **Mechanism**: POST /spawn → /watch → /teardown; returns a durable RUN RECORD
- **FAIL LOUD**: if the supervisor is unreachable (no silent no-op)
- **Lead-only at fire time**: spawns a real claude session

#### `routine_schedule.py`
- **Purpose**: Generate per-routine systemd .timer + .service.
- **GENERATES, NEVER ARMS**: writes to `ops/systemd/generated/` and emits suggested enable command
- **Cadence grammar**: "OnCalendar=<expr>" (verbatim) or "every:<seconds>" (OnUnitActiveSec)

#### `ci_scaffold.py`
- **Purpose**: S-R9.1 CI scaffolder (CC-30) — generate a CI workflow from a routine's prompt + cadence.
- **GENERATES, NEVER INSTALLS**: returns workflow text + canonical target path
- **Maps**: routine `cadence` → GitHub `schedule: cron` where expressible; else on-demand

### Other

#### `context_variables.py` (already covered)

#### `forms.py` (already covered)

#### `checks.py` (already covered)

#### `compile.py` (already covered)

---

## DATA FILES READ/WRITTEN BY runtime/

### Read at Module Load / Suite Init
- `ops/services.json` — GPU services registry (SlotBudget, model routing, VRAM budget)
- `design/_system/addresses.json` — corpus element-level addresses
- `design/_system/corpus-meta.json` — mockup corpus metadata
- `design/_system/generate-config.json` — mockup generation config (read fresh each call)
- `ops/cli/registry.json` — ops services config (loaded via _apply_model_ctx)

### Store (FsStore at `fcfg.STORE_DIR`)
- `agent_sessions/mail.jsonl` — cross-session mailbox (append-only, fsync'd)
- `agent_sessions/channels.jsonl` — channel fabric (append-only, fsync'd)
- `agent_sessions/*.json` — session registry entries
- `<content-hash>` — CAS content-addressable store
- Refs (`run://…`, `code://…`, `board://…`, etc.)
- Vector indexes per space (pplx-embed-context-v1-4b dim 2560)
- `design/mockups/.feedback/<file>.html.jsonl` — mockup feedback threads

### Discovered Directories (file-discovered registries)
- `roles/*.py`, `nodes/*.py`, `projections/*.py`, `flows/*.py`, `routines/*.py`, `decisions/*.py`
- `skills/*.py`, `contexts/*.py`, `axes/*.py`, `lifters/*.py`, `generation_policies/*.py`
- `decision_subtypes/*.py`, `verdict_panels/*.py`, `mark_types/*.py`, `item_types/*.py`
- `attachment_types/*.py`, `source_types/*.py`, `relation_types/*.py`, `stack_item_types/*.py`
- `dials/*.py`, `ai_tics/*.py`, `mode_detection_rules/*.py`, `minds/*.py`, `forms/*.py`, `checks/*.py`
- `board_edges/*.py`, `operator_memory/*.py`

### Tool Gate Files
- `remote_exposure.json` — which MCP tools are exposed to the bridge tool face
- `tool_operator_overlay.json` — operator-specific tool access overrides

### Channel Boundary
- `build-prep/claude-design/supabase/.boundary.env` (default; overridable)
- `.data/channels/<handle>.json` — channel session registry
- `.data/voice/` — rendered WAV files

### Extractions
- `.data/store/extractions/extractions-<name>.jsonl` — dragnet extract-once layer

---

## NOTABLE SEAMS AND CONTRACTS

### Address Schemes (resolved by `cognition.resolve_address`, 9 schemes)
- `run://` — engine run outputs (CAS + set_ref)
- `code://` — code files
- `board://` — noticeboard items
- `session://` — sessions (and `session://<sid>/step/<tool_use_id>` for gate)
- `skill://`, `context://` — skills and contexts registries
- `ui://` — UI surfaces
- `vi-vision://` — Vi factory asset library
- `mind://`, `cap://` — minds and capabilities
- `anchor://` — planted separator poles
- `chan://` — channels

### Critical Environment Variables
- `COMPANY_ACTIVATION_LOOP` — arm the always-on activation loop (default: OFF)
- `COMPANY_WIRE_PERMISSION` — arm the implement wire (default: "plan"; use "acceptEdits" to arm)
- `COMPANY_PANEL_PERMISSION` — arm the builder side-panel (default: "plan")
- `COMPANY_FABRIC_TURN_TIMEOUT_S` — session supervisor turn timeout (default: 900)
- `COMPANY_FABRIC_CONCURRENCY` — session supervisor max concurrent sessions (default: 3)
- `COMPANY_FABRIC_PERMISSION` — session supervisor permission mode (default: "plan")
- `COMPANY_TTS_URL` — default TTS engine URL (default: http://127.0.0.1:4123)
- `COMPANY_CHANNEL_ENV_FILE` — boundary env file path override
- `COMPANY_CHANNEL_SA_EMAIL`, `COMPANY_CHANNEL_SA_PASSWORD` — channel boundary principal creds
- `COMPANY_SUPERVISOR_BASE` — supervisor base URL (default: http://127.0.0.1:8771)

### Port Map
- `8770` — bridge HTTP (operator console)
- `8771` — session supervisor (127.0.0.1 only)
- `4123` — kokoro TTS (default engine, env-overridable)
- `4124` — chatterbox TTS
- `4125` — orpheus TTS
- `4126` — cosyvoice TTS
- `4127` — xtts TTS
- `4128` — qwen3tts TTS
- `8000` — resident model (Qwen3.5-4B-AWQ-4bit, vLLM)
- `8007` — embedder (pplx-embed-context-v1-4b)
- `8008` — reranker (jina-v3, CPU)

---

## GAPS, STALE, DEAD, INCOMPLETE, SURPRISING

### INCOMPLETE / PHASE-1-ONLY
1. **`model_routing.py` Phase 1**: The `resolve_model()` unification resolver EXISTS but nothing is wired through it yet. Live firing paths (`run_swarm`, cognition) still use the scattered logic. Phase 2 is not built.
2. **`context_variables.py` context-assembly budgeting**: The `Cost` vocabulary (`cheap`/`loads-model`/`loads-corpus`) is declared but the assembly budget mechanism is not built — it's the designed next layer.
3. **`dials.py` condition-scoped overrides**: Overrides with `when` conditions are stored+validated but NOT yet evaluated — the now-organ + rules wiring doesn't exist yet. All dials fall back to flat value until it does. Stated honestly in the module.
4. **`brain_router.py` recall seam**: The `recall` source in `ask()` is a DECLARED HOOK — v1 routes recall questions to the model (tool-grounded). The richer recollection source (`session_search`/`recall_for_decision`) is named but not wired. A seam is named, not faked.
5. **`minds.py` lock signatures**: Four locked signatures declared; the lead owns the two hot seams (resolve_address mind:// branch + cast_for_mode additive bind). Status of those seams in suite.py is not verified in this survey.
6. **`channel_boundary.py` INJECT**: The outbound Realtime subscription is built. But the earlier filter (only `sender_kind='client'` rows) was a MIRROR-design artifact and was WRONG — skip-by-ORIGIN (both session and client rows inject) is the correct single-source model. Confirmed corrected in the module, but not tested against live Supabase here.
7. **`ci_scaffold.py`** maps routine cadence → GitHub Actions, but cadences that aren't cleanly expressible as cron expressions become on-demand (not scheduled). The mapping is best-effort.
8. **`territory.py` lens-union enrichment**: The lens-union / surfaced-neighbour-units enrichment from projection's multi-embedding answer is a declared FAST-FOLLOW, not wired here. The structural board-edge relations leg is lens-independent (fine for the core slice).
9. **`anchors.py` planted anchor**: `anchor://ai-corner` is planted manually (CLI run); the system does not auto-plant/re-plant. The separation_report tells the truth about whether it actually separates (not a verified pollution oracle, honestly stated).

### STALE / REMOVED
10. **`/api/config/*`, `/api/dev/*`, `/api/auto/*` routes**: REMOVED 2026-06-13 (Session Fabric R1.4). They hand-wrapped what a real Claude Code session does natively. Noted in `BRIDGE_ROUTES` comments.
11. **`lifter_registry.py`** was renamed FROM `lifters.py` 2026-06-18 due to namespace shadowing bug — the old name `lifters.py` shadowed the top-level `lifters/` namespace package when bridge.py puts `runtime/` on sys.path. If anything in the codebase still imports `from runtime.lifters import ...` using the old name, that would be broken. Worth checking.

### SURPRISING / NOTABLE
12. **`BRIDGE_ROUTES` drift-gate**: `tests/bridge_routes_acceptance.py` runs `coherence_detect.extract_routes()` against bridge.py to verify no route is in the table that isn't in the code and vice versa. This is the FIRST runtime-enforced drift guard between a declared registry and the actual implementation — a live example of the gap-pressure law.
13. **`SlotBudget._MEASURED_KV_BY_UTIL`**: Hardcoded measurement values `{0.49: 66036, 0.63: 135574}` in cognition.py. These are documented as measured constants (not arbitrary), but they are specific to the RTX 4080 16GB. On a different GPU these would give wrong VRAM budgets. Not a violation (they're documented measurements), but a machine-specific dependency.
14. **`vi_vision.py` migration note**: The module explicitly documents that it should migrate OFF its inline principal code ONTO `supabase_principal.py`, but has not yet done so. Two parallel copies of the principal JWT flow exist until that migration runs.
15. **`generate_mockup.py`** explicitly REPLICATES the tiny JSONL read from bridge.py rather than importing bridge.py, because `bridge.py` instantiates a `Suite` at module import (`bridge.py:362`). This is a conscious duplication to avoid coupling — the format is the contract.
16. **`session_supervisor.py` + `ui_claude_session.py` cross-import**: The supervisor imports `_find_claude` + `_MCP_CONFIG` from `ui_claude_session.py`. This is a ONE-WAY import (ui_claude_session is never imported by mcp_face). The asymmetry is intentional but creates an invisible dependency on the UI module from the supervisor.
17. **`coherence_detect.py`** has dual extraction (AST + regex union) — the AST walk is structurally immune to comment/docstring false positives, but falls back to the regex set ONLY to UNION (never to shrink). This means the regex's latent bug (matching route strings in comments) cannot reduce the route set — it can only add. The safe direction, but means comments mentioning an API route would be false-positives in the regex path.
18. **`scale.py` pyramid design reversal**: The first plan was a LINEAGE pyramid (unit ⊂ session ⊂ project). The per-space probe KILLED it (the session axis is capture-batch provenance, not a semantic nest). The cluster-centroid approach was the evidence-forced correction. The module documents this reversal explicitly — important context for anyone revisiting the design.
19. **`decision_memory.py` `_CTX_FLOOR = 0.5`**: The cross-encoder relevance floor is a hardcoded 0.5. Not a registry value. If this proves too permissive or restrictive, it requires a code edit.
20. **`activation.py` + `activation_driver.py` DORMANT posture**: The always-on caller is DORMANT by default. If `COMPANY_ACTIVATION_LOOP` is never set, the background/sense/rollup cognition never fires in practice — the whole activation substrate (G5, H, I) sits inert. It is only exercisable via the manual `POST /api/activation/tick`. This is by design (operator-greenlight posture), but means the mode auto-detector, background ticks, and rollup consolidation are NOT running in a default deployment.
21. **`recall_determine.py` anti-confabulation proof**: The no-fiction grounded reduce was proved on 2026-06-21. The previous free-synthesis reduce was confirmed to confabulate. This module is a post-fix implementation — the old behaviour (confabulating) may exist in other determine-adjacent code paths not yet updated.
22. **`corpus_rerank.py` critical wiring insight**: "CRITICAL WIRING INSIGHT (cost two false 'rerank degrades' runs before falsify-first caught it)" — the docstring contains an explicit warning about a costly debugging experience. The specific issue (what "green paint" trap it was) is not detailed in the first 60 lines; the full insight is deeper in the file.

---

## CROSS-REFERENCES TO OTHER AREAS

- **`mcp_face/`**: shares `SUITE` with bridge (same Suite instance); `cc_channels.py`, `session_supervisor.py`, `decisions`, `sessions`, `corpus` tools all route through runtime modules
- **`contracts/`**: `compile.py` imports `contracts.node_record.Graph`, `ExecNode`; `context_variables.py` imports `contracts.node_record`
- **`ops/`**: `implement.py` calls `claude` binary; `SlotBudget` reads `ops/services.json`; reranker at `ops/rerank.py` served at `:8008`; `ops/cli/gpu.py`, `ops/cli/systemd.py`, `ops/cli/registry.py` loaded by `_apply_model_ctx`
- **`lifters/`**: `lifter_registry.py` discovers `lifters/<id>.py` files from the top-level `lifters/` package
- **`roles/`, `nodes/`, `projections/`, `flows/`, `routines/`, `decisions/`, `skills/`, `contexts/`, `axes/`, `generation_policies/`, `decision_subtypes/`, `verdict_panels/`, `mark_types/`, `item_types/`, `attachment_types/`, `source_types/`, `relation_types/`, `stack_item_types/`, `dials/`, `ai_tics/`, `mode_detection_rules/`, `minds/`, `forms/`, `checks/`, `board_edges/`, `operator_memory/`**: all discovered by runtime registries
- **`design/`**: bridge serves `design/mockups/`, reads `design/_system/corpus-meta.json`, `design/_system/addresses.json`, `design/_system/generate-config.json`
- **`build-prep/`**: `channel_boundary_run.py` reads `.boundary.env` from `build-prep/claude-design/supabase/`
- **`channel-memory/`**: `cc_board.py` stores items in `channel-memory/noticeboard/`; `cc_attachments.py` stores in `channel-memory/channel_attachments/`
- **`.data/`**: store data, voice WAV output, channel session files, extraction assets

---

## KEY CAPABILITIES SUMMARY

1. **Cognition Engine**: `run_role`, `run_items`, `run_reduce`, `run_swarm` — fires roles, manages VRAM, routes outputs through rules, addresses all output to `run://`
2. **Reactive Scheduler**: watches store, fires nodes when inputs resolve, memo gate prevents re-runs
3. **HTTP Bridge**: 130+ routes serving the operator console, design review, voice, cognition, session fabric
4. **Decision Stack**: declare→surface→explain→resolve lifecycle with never-assert law and grounded explanation
5. **Session Fabric**: cross-session channels, gatherings, connection edges, point-in-time cloning, semantic recall over past sessions
6. **Universal Projection**: Tim's equation (centre/angle/radius/depth), embeddable lens spaces, multi-scale zoom pyramid
7. **Voice**: brain↔TTS overlap via producer thread, multi-engine routing, always-on activation (DORMANT)
8. **Rule Engine**: closed RULE_OPS grammar, pure evaluator, five DESTINATION_KINDS — the predicate language used everywhere
9. **Resolver**: 4th primitive — `resolve(invariant, coordinate)` pure function
10. **File-discovered registries**: ~25 distinct registry types, all with the same mechanism (os.listdir → importlib, fail-loud, id==filename, dict-like, rediscover)
11. **Governance**: AUTO/SURFACE/CONFIRM posture per action class, LOCKED set, guard + posture functions
12. **Implement wire**: Group W — decision→implementation, git checkpoint, wire_armed() gate
13. **Noticeboard**: typed board items (request/issue/tip/guide/idea) with per-type lifecycle state machines
14. **Coherence**: AST-grounded structural detectors + calibration harness + saveable actions
15. **Corpus**: CAS + lineage + neighbours + rerank + dragnet extract-once/determine-many
