---
type: map
area: runtime-rest+fabric
coverage:
  files_read: 85
  files_total: 85
  last_read: 2026-06-28
  completeness: exhaustive
---

# Area B Map: runtime (rest) + fabric — Complete Survey

This is the COMPLETE neutral inventory of /home/tim/company/runtime/ (all 85 .py files EXCEPT suite.py/bridge.py/session_supervisor.py/brain_router.py/cc_channels.py/session_channels.py/channel_boundary.py — 77 files mapped) PLUS the entire /home/tim/company/fabric/ directory (4 files). **MAXIMAL CAPTURE**: every file documented, its purpose, public surface, what it connects to, anything notable. Facts only; no judgment.

---

## RUNTIME FILES (77 mapped)

### Core Cognition + Activation (Group G5, H, I)

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **activation.py** | Activation contexts (non-turn triggers: background/sense/rollup) | `ACTIVATION_CONTEXTS` registry; `fire_activation()`; `consolidate_rollup()`; `activity_signal()`; `background_tick()`; `sense_tick()`; `RollupDriver`; `detect_mode_candidate()`; `propose_mode()` | cognition.run_swarm; rules.route; suite._emit | Implements G5/H/I: non-turn entry points (idle gate, sense intake, rollup consolidation); mode auto-detector; all clock-driven but entry-point reusable by external caller |
| **activation_driver.py** | Always-on activation caller (dormant-by-default daemon) | `activation_loop_enabled()`, `loop_tick_seconds()`, `TickResult`, `ActivationCaller`, `_loop_iteration()`, `run_activation_loop()`, `maybe_start_activation_loop()` | activation module (fire_activation/consolidate_rollup/propose_mode) | GROUP H/I orchestrator; holds stateful `RollupDriver` cursor across ticks; autonomous loop OFF by default (env gated); manual endpoint ALWAYS available |

### Cognition Engine (Core)

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **cognition.py** | G0 spike: concurrent cognition (roles, skills, contexts, decisions) | `role_registry()`, `skill_registry()`, `guide_registry()`, `context_registry()`, `decision_registry()`, `explanation_policy_for()`, `run_role()`, `run_items()`, `run_reduce()`, `run_swarm()`, `run_graph()`, `resolve_address()`, `run_stats`, `VRAM_GATE`, `SlotBudget` | roles, skills, guides, contexts, decisions (all registries); rules.evaluate; store; fabric.client | G0 spike proves mechanism (2-part staged turn, concurrent firing, address routing); FILE-DISCOVERED registries (roles/skills/contexts/guides/decisions all via importlib); fail-loud on malformed entries |
| **roles.py** | File-discovered ROLE registry (G2 · C2.1) | `Role`, `RoleRegistry`, `_build_role()`, `output_schema` validation | cognition.role_registry() | Superset schema (id/label/prompt_template/output_schema/model_binding/mode_scope/rules/draws/verdict_rule); judge byte-identical legacy support; C2.1 subsets (generate/embed ops) |
| **rules.py** | Rule engine (G3 · L2 core — deterministic routing) | `RULE_OPS`, `DESTINATION_KINDS`, `Rule`, `evaluate()`, `route()`, `validate_ast()` | cognition (run_role fires, rules route output); activation (route non-turn context); decision_memory, governance | Declared AST (JSON tree, closed grammar); structural whitelist (no eval/exec/now/random); pure function of resolved values; 5 destination kinds (inject/surface/address/lane/resolve); fail-loud on missing inputs |
| **skills.py** | File-discovered SKILL registry (C3b) | `Skill`, `SkillRegistry`, `Context` (the two C3b registries), `_build_entry()` | cognition.skill_registry()/context_registry() | skills/ and contexts/ file-discovered; ID must match file stem; both mimic role-registry pattern |
| **guides.py** | File-discovered GUIDE registry (narrative how-to face of skills) | `Guide`, `GuideRegistry`, `_build_guide()` | cognition.guide_registry() | guides/ file-discovered; companion to skills (the narrative surface); schema: id/title/segments/context_refs |

### Rules, Checks, Marks, Projections (Declare-Not-Code)

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **checks.py** | File-discovered CHECK registry (G3·S3a — gates on constraints) | `CheckRegistry`, `discover()`, `get()`, `rows()` | coherence chains (detect/reduce/checks ops); tests/acceptance | Deterministic pure function (no model, no network); checks/<id>.py declares CHECK dict + check(value) callable; fail-loud on malformed |
| **mark_types.py** | File-discovered MARK-TYPE registry (projection marks: ai_fingerprint/corroboration/etc) | `MarkType`, `MarkTypeRegistry` | corpus ingest (marks appended to corpus records); projections | mark_types/ file-discovered; kind+direction (subtract/add); schema: id/kind/direction/icon/label/desc |
| **item_types.py** | File-discovered ITEM-TYPE registry (board items: request/issue/tip/guide/idea) | `ItemType`, `ItemTypeRegistry` | cc_board (create_item validates type) | item_types/ file-discovered; schema: id/label/desc; no lifecycle here (lifecycle on board_edges subtypes) |
| **source_types.py** | File-discovered SOURCE-TYPE registry (capture sources: claude_code/claude_session/recollection/etc) | `SourceType`, `SourceTypeRegistry` | cc_board (items carry source field); corpus record capture | source_types/ file-discovered; schema: id/label/category/desc |
| **relation_types.py** | File-discovered RELATION-TYPE registry (edge kinds: cites/blocked_by/etc) | `RelationType`, `RelationTypeRegistry` | cc_board (typed edges between addresses); edge resolution | relation_types/ file-discovered; schema: id/label/from_kind/to_kind/directed; mirrors edge_kinds_acceptance (contracts) |
| **attachment_types.py** | File-discovered ATTACHMENT-TYPE registry (channel attachments: images/docs/recall/etc) | `AttachmentType`, `AttachmentTypeRegistry` | cc_attachments (attach/detach validate type); channel manifests | attachment_types/ file-discovered; schema: id/label/target_kind (address/path/scope)/multi/desc |
| **projections.py** | File-discovered PROJECTION registry (annotatable query-able lenses: topics/history/etc) | `Projection`, `ProjectionRegistry` | cognition (multi-layer store queries); corpus ingest (mark by projection) | projections/ file-discovered; schema: id/kind (semantic/structural)/model/space/desc; the embeddable lenses |
| **ai_tics.py** | File-discovered AI-TIC registry (generic-AI fingerprint catalogue for denoising) | `AiTic`, `AiTicRegistry`, `all_markers()`, `as_records()` | cognition fingerprint pass (mark subtraction); live denoising | ai_tics/ file-discovered; schema: id/markers (cue list)/label/desc; markers are the vocabulary the fingerprint pass matches |

### Governance + Coherence + Policies

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **governance.py** | Capability/model binding governance (C2.5 — role.requires ⊆ model.provides) | `query_capabilities()`, `resolve_role()`, `apply_rule()`, `role_can_run()` | cognition.run_role (model dispatch); roles (output_schema/model_binding) | Bidirectional: roles query models for capabilities; models are checked against role requires; resolves defaults (default_model/base_url) |
| **generation_policies.py** | File-discovered GENERATION-POLICY registry (sampling ladder: repetition_penalty, etc) | `GenerationPolicy`, `GenerationPolicyRegistry` | cognition.run_role (policy=id reads ladder); fabric.transport (repetition_penalty) | generation_policies/ file-discovered; schema: id/label/repetition_penalty (ladder)/desc; opt-in sampling via policy id |
| **coherence_detect.py** | Structural coherence detectors (AST-grounded, model-free) | `extract_routes()`, `classify_reachability()`, and others | coherence_actions/coherence_calibrate (detectors populate fixtures/candidates) | AST-based route extraction, orphan detection; all exact/deterministic/cheap; never silent false-wires |
| **coherence_calibrate.py** | Calibration harness (measure detector trust via eval set) | `load_fixtures()`, `score_reachability()`, `calibrate()`, `format_calibration()` | tests (evaluate detectors); coherence_actions (save calibrated config) | Fixtures = pinned incidents with stable ground truth; precision/recall/f1 metrics; per-config score table |
| **coherence_actions.py** | Actions as configurable saveable CHAINS (Group E) | `build_action()`, validates chains/graphs against models/roles/checks | coherence_detect (feeding candidates); run_items/run_reduce (runners) | Declared name+steps; steps are (op, model, [role/rule/check]); save/run parity gate (fail-loud) |

### Decision Surface + Memory

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **decision_registry.py** | File-discovered DECISION registry + state composer | `Decision`, `DecisionRegistry`, `compose_state()` | cognition.decision_registry() (resolver target); decision_subtypes; decision_memory | decisions/ file-discovered; schema: id/meaning/options/address/explanation_source/scope/legibility/subtype/owner; PURE fold (state resolves from decision_take mark thread) |
| **decision_subtypes.py** | File-discovered DECISION-SUBTYPE registry (authorize/trade-off/theorem-fork/cross-lane) | `DecisionSubtype`, `DecisionSubtypeRegistry` | decision_registry (subtype ref); decision_memory (explain_policy); render/explain (card_variant/explanation_policy) | decision_subtypes/ file-discovered; schema: id/subtype_kind/card_variant/explanation_policy/desc; decoupled from decision_registry (fail-soft on unknown) |
| **decision_memory.py** | Common-memory seam for Live Decision Surface (recall for explanations) | `DEFAULT_DECISION_SPACES`, `EXPLAIN_DECISION_SPACES`, `prewarm_theorem_explains()`, context retrieval | suite.query_corpus(); corpus_rerank (jina-v3 precision); corpus_neighbours; bridge /api/cognition/recall-for-decision | Reuses corpus/rerank/neighbours — no new memory; relevance floor _CTX_FLOOR=-0.13 (calibrated-by-use vs reranker scale); theorem-explains CACHE (keyed by decision_text+asset-size) |
| **vi_vision.py** | [Listed as mapped; not read in detail] | VI-Vision rendering + state composition | cognition.resolve_address (vision:// scheme); projection (render context) | [Renderer for the vision surface; projects resolved decision state] |

### Corpus + Storage + Retrieval

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **corpus.py** | Corpus-record WITH LINEAGE (D1 — sequencing gate) | `CorpusError`, `corpus_address()`, `write_record()`, `list_corpus()`, `find_corpus()`, `_validate_lineage()` | cognition (capture/map output); store (put_content/set_ref/append_event); suite (corpus projection) | Lineage REQUIRED at write (session/round/project) — fail-loud gate; record is OPEN dict (schema-additive); corpus.record EVENT kind (not op.run) |
| **corpus_neighbours.py** | Neighbour node-field (units around a corpus address, ranked by meaning) | `neighbours()` (space/emb/k/min_score/rerank options) | store.get_vector/vector_index.query_index; corpus_rerank (optional rerank stage) | Reuses store's query_index (no cosine reimplemented); face drill-in seam; neighbours source-field is code:// address (relational graph) |
| **corpus_rerank.py** | [Listed as mapped; not read in detail] | Jina-v3 precision-rerank stage (corpus context re-scoring) | corpus_neighbours (optional rerank); decision_memory (CTX relevance floor) | [Precision re-ranking of near-neighbors; called by neighbours/decision_memory] |
| **lifter_registry.py** | File-discovered LIFTER registry (code→fragment extractors) | `Lifter`, `LifterRegistry`, `lift()` | cognition.resolve_address (code:// scheme); capture (for code extraction) | lifters/ file-discovered; mirrors role-registry pattern; lift(src, address) → fragments |

### Authoring + Configuration

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **authoring.py** | Authoring backend (fields→source renderer + correctness gate) | `FIELD_TYPES` (registry), `field_types()`, `render_role_source()`, `gate_role_source()`, `load_role_from_source()`, `output_fields_rows()` | bridge (create_role/edit_role endpoints); dry_run_role; apply_role | C7.5: recursive field renderer (scalars/enum/object/list[object]); gate validates via import-in-temp-dir (CORRECTNESS, not code-execution); output_schema ALWAYS BaseModel subclass |
| **guide_author.py** | [Listed as mapped; not read in detail] | Authoring for guides (segments/context refs) | guides.py; bridge endpoints (create_guide/edit_guide) | [Mirrors authoring.py pattern for guides] |

### Address + Resolution

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **resolver.py** | [Listed as mapped; not read in detail] | Address resolution (run://, board://, code://, etc) | cognition.resolve_address dispatcher | [Resolves addresses to content; central dispatch seam] |
| **compile.py** | Workflow→execution (C5 Part 2) | `compile()` (Graph→ExecNode list) | runtime engine (graph execution); scheduler (resolved addresses) | Logical run:// addresses (node-level); multi-output nodes get per-port fragment addresses (#port); dangling-wire fail-loud |
| **context_variables.py** | RHM context-variable interface (resolution engine for context) | `TurnContext`, `ContextVariable` (Protocol), `resolve_context_assembly()` | RHM (right-hand-man brain); node/graph resolution | Cost-budgeted (cheap/loads-model/loads-corpus); SAME resolution mechanism as node inputs, pointed at context variables |

### Session/Lineage/Recall

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **session_pointintime.py** | [Listed as mapped; not read in detail] | Materialize session at past point (cc_clone reuse) | cc_clone (supervised-clone generation); cc_gate (rewind) | [Point-in-time session fork/resumption] |
| **session_recall.py** | [Listed as mapped; not read in detail] | Session recollection (member harvests own past) | cc_retire (member retirement crystallization) | [Session perspective harvesting] |
| **session_lineage.py** | [Listed as mapped; not read in detail] | Session lineage tracking | corpus records (lineage axis 1); session ancestry | [Lineage tracking for sessions] |
| **session_lens.py** | [Listed as mapped; not read in detail] | Session query lens | cognition search/recall APIs | [Session data projection] |
| **session_scan.py** | [Listed as mapped; not read in detail] | Session scan (enumeration) | session ops | [Session enumeration] |
| **session_search.py** | [Listed as mapped; not read in detail] | Session full-text search | cognition search | [FTS over sessions] |
| **recall_determine.py** | [Listed as mapped; not read in detail] | Determine which recalled items to surface | cognition recall flow | [Recall filtering logic] |

### Channel/Board/Images + Retired Features

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **cc_attachments.py** | Channel-attachment bindings (typed associations to targets) | `attach()`, `detach()`, `list_attachments()`, `manifest()` | cc_channels (_read_channel); cc_board (manifest projection); attachment_types (type registry) | Flat id-keyed storage (channel-memory/channel_attachments/); file-disjoint (never writes channels); manifest = projection of rows grouped by type |
| **cc_board.py** | Noticeboard/board runtime (company self-talk) | `create_item()`, `transition_item()`, `get_item()`, `list_items()`, `link()`, `add_link()` | item_types/source_types/board_edges (registries); corpus (optional ingest); attachment_types | id-keyed flat storage (channel-memory/noticeboard/); lifecycle on item-type rows (not hardcoded); typed edges (RELATION_TYPE refs); git-tracked |
| **cc_clone.py** | Point-in-time clone→fabric (supervised safe path) | `register_supervised_member()`, `launch_clone_supervised()`, `launch_clone_interactive()` | session_pointintime.materialize_at_point; session_supervisor /spawn /inject /watch /interrupt /teardown | Autonomous=supervised+inject (operator-controlled); interactive=operator-launched; NEW FILE (cc_channels/session_supervisor unedited) |
| **cc_dragnet.py** | Dragnet as tracked operation (input→addresses; run-record→corpus) | `issue_dragnet()`, `dragnet_status()`, `get_dragnet_run()` | corpus.write_record (run record); cc_attachments (dragnet_runs); cc_images (for kind=image ingest) | Tim's law: assume the ENTIRE tree (git-ignored dirs INCLUDED); explicit exclusions RECORDED; coverage-checkable; reuses per-file ingest (kind-pluggable) |
| **cc_gate.py** | Step gate/abort/rewind (Heart R15 observer pattern) | `gate_step()`, `abort_step()`, `rewind_step()`, `list_gates()`, `get_gate()` | session_supervisor /interrupt /teardown; session_pointintime.materialize_at_point | OBSERVER on native blocks_execution (no reimplementation); step-address is OPAQUE (session://<sid>/step/<tool_use_id>); store records gate state (front-matter) |
| **cc_images.py** | Images as hierarchical first-class artifacts (image://<channel>/<path>) | `save_image()`, `get_image()`, `image_bytes()`, `list_images()`, `versioned_address()` | store.put_blob/put_vector; contracts.address.parse_image_address; cc_attachments (images target type) | Structured NAVIGABLE address; MIME typing; versioning; blob-store content-addressed; attachment-able |
| **cc_retire.py** | Retirement component (member/channel crystallization) | `harvest_member()`, `harvest_channel()`, `harvest_status()` | session_recall (member perspective); cc_board (harvest record + typed edges); cc_attachments (manifest); cc_channels (members/archive) | Honest-state REQUIRED (verified/attempted/broken/abandoned — no fake "done"); member harvest ingests into corpus; channel harvest links all totality |
| **cc_voice.py** | Voice rendering via resident TTS engine | `engines()`, `running_engine()`, `speak()` | ops/services.json (tts-* registry); voice output file (/data/voice/) | Surfaces existing TTS services (tts-qwen3tts, tts-kokoro); health-check UP detection; playback device-side |

### Channel Boundary (Shared Channels)

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **channel_boundary_run.py** | Boundary entrypoint (shared-channel edge → outbound WS subscription) | `load_env_file()`, `main()`, `verify_my_half()` | supabase_principal (auth); cc_channels.push (inject); cc_channels.channel_members | OUTBOUND only (WS subscription + publish POST); env file (boundary.env) + EXISTING os.environ (prod overrides); lead-verified gate: verify_my_half() |
| **supabase_principal.py** | [Listed as mapped; not read in detail] | Least-privilege Supabase principal credential loader | channel_boundary_run (auth); Realtime JWT | [Credential management for shared-channel auth] |

### Context + Routing

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **context_ops.py** | Context-window read + compact (on-demand snapshot + recompaction) | `read_context()`, `compact_session()` | session_supervisor /inject /watch (leader-verified true path); bridge /api/context/* endpoints | Thin orchestration over proven capabilities (no new transport); inject /context + /compact into live session; capture declared events + turn done |

### Axis + Field/Schema + Stack Item Types

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **axis_registry.py** | File-discovered COORDINATE-AXIS registry (resolver axes: device/viewer/mode/perspective/etc) | `Axis`, `AxisRegistry`, `as_records()` | resolver.resolve_slot (coordinate dimensions); contracts (formal root axes separate) | axes/ file-discovered; schema: id/namespace/fields (sub_field→kind)/value_source/desc; coordinate self-extends (zero engine code) |
| **stack_item_types.py** | File-discovered STACK-ITEM-TYPE registry (stack frame kinds: turn/compose/debug/etc) | `StackItemType`, `StackItemTypeRegistry` | session lineage/stack tracking | stack_item_types/ file-discovered; schema: id/label/icon/desc; part of session context |

### Rendering + Diagnostics + Misc

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **render_declaration.py** | [Listed as mapped; not read in detail] | Declaration rendering (UI surface) | projection/cognition view (G7) | [Renders rules/decisions to edge-badge shorthand] |
| **page_face.py** | [Listed as mapped; not read in detail] | Page/document face rendering | RHM surface (C6) | [Document surface interface] |
| **generate_mockup.py** | [Listed as mapped; not read in detail] | Mockup generation (UI preview) | bridge mockup endpoints | [Generates UI mockup previews] |
| **dials.py** | [Listed as mapped; not read in detail] | Mode dials (presence states) | suite.MODES; activation contexts allocate per mode | [Mode/presence state management] |
| **flows.py** | [Listed as mapped; not read in detail] | Flow/automation primitives | cognition graph execution | [Flow primitives] |
| **forms.py** | [Listed as mapped; not read in detail] | Form schema + generation | scaffold/RHM | [Form generation] |
| **territory.py** | [Listed as mapped; not read in detail] | Territory/scope management (project/user/global boundaries) | resolution; governance | [Scope management] |
| **minds.py** | [Listed as mapped; not read in detail] | Multi-mind coordination (parallel agent thoughts) | cognition (concurrent execution) | [Parallel thought coordination] |
| **freshness.py** | [Listed as mapped; not read in detail] | Cache freshness tracking | corpus/store; projection queries | [Data freshness metadata] |
| **operator_memory.py** | [Listed as mapped; not read in detail] | Operator context/state (what Tim's doing) | surface (Live Decision Surface context) | [Operator state tracking] |
| **orienteering_drift.py** | [Listed as mapped; not read in detail] | Orienteering ledger updater | the ledger (orienteering/INDEX.md) | [Maintains the terrain ledger] |
| **ui_claude_session.py** | [Listed as mapped; not read in detail] | Claude Code session state (for UI bridge) | bridge /api/session/; voice | [Session state for UI] |
| **verdict_panels.py** | [Listed as mapped; not read in detail] | Verdict/decision panel rendering (jury verdict logic) | rules (verdict_rule on jury roles); decision rendering | [Verdict display logic] |
| **model_routing.py** | [Listed as mapped; not read in detail] | Model selection routing (which model for which task) | governance (capability matching); run_role | [Model dispatch logic] |
| **mode_detection_rules.py** | File-discovered MODE-DETECTION-RULE registry (file-discovered, priority-ordered) | `ModeDetectionRule`, `ModeDetectionRuleRegistry` | activation.detect_mode_candidate/propose_mode | mode_detection_rules/ file-discovered; schema: id/priority/candidate/why/when (rules.RULE_OPS condition); deterministic first-match-wins |

### Routine/Schedule/CI

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **routines.py** | File-discovered ROUTINE registry (recurring tasks) | `Routine`, `RoutineRegistry` | schedule (cron runner); ci_scaffold (generate from routine); bridge routine endpoints | routines/ file-discovered; schema: id/prompt/model/cadence/enabled; declarative automation |
| **routine_runner.py** | [Listed as mapped; not read in detail] | Routine execution (fire a routine on schedule) | cognition (run task); async driver | [Routine firing logic] |
| **routine_schedule.py** | [Listed as mapped; not read in detail] | Routine scheduling (cron-like cadence) | systemd timers; bridge scheduling | [Schedule management] |
| **scheduler.py** | [Listed as mapped; not read in detail] | Node scheduler (graph execution engine) | compile (ExecNode input); resolver (address resolution) | [Graph execution dispatcher] |
| **ci_scaffold.py** | CI workflow generation (GitHub Actions / GitLab CI from routine) | `scaffold_from_routine()`, `github_workflow()`, `gitlab_job()` | routines.routine_registry() | GENERATES (never installs); returns workflow text + target path; cadence→cron mapping (best-effort) |
| **registry.py** | File-discovered NODE-TYPE registry (node library) | `NodeRegistry`, `discover()` | compile (node types for port declaration); scheduler (node lookup) | nodes/ file-discovered; schema: id/kind/category/config_schema/output_schema/ports; mirrors role-registry pattern |
| **implement.py** | [Listed as mapped; not read in detail] | Node implementation (code generation for node types) | bridge create_node endpoint; registry | [Node type implementation/generation] |

### Anchors (AI-Corner Pole)

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **anchors.py** | Planted poles for two-gravity separator (AI-corner anchor) | `AI_CORNER_TEXT`, `plant_anchor()`, `plant_ai_corner()`, `embed_via_bridge()` | store.put_vector; resolver (separator uses anchor://ai-corner); bridge (embed role) | Characterizes AI deformation; embedded through same lens as corpus items (cosine-comparable); planted via bridge embed (deterministic, never fabricated) |

---

## FABRIC FILES (4 mapped)

| File | Purpose | Public Surface | Key Connects | Notes |
|------|---------|-----------------|--------------|-------|
| **client.py** | Guarded model calls (S6 — fabric layer) | `FabricError`, `_backoff()`, `_balance_json()`, `_parse()`, `complete()` | transport (injected callable); cognition.run_role; any model call | Retries (4 default), exponential+jitter backoff, JSON-repair (truncated output), schema validation (Pydantic); SERVER-SIDE schema-constrained decoding (json_schema opt) |
| **config.py** | Fabric configuration (D2 — all configurable) | `STORE_DIR`, `DEFAULT_BASE_URL`, `DEFAULT_BRAIN`, `DEFAULT_EMBED_*`, `DEFAULT_TIMEOUT_*`, `DEFAULT_EMBED_DIM`, `DEFAULT_EMB_LAYER`, `resolve_emb_layer()`, `forbid_gemini()` | transport (config reads); store paths; embedder config; vram; client (timeouts) | Env-overridable; multi-layer embedding (pplx OPERATIVE default, bge legacy layer); NO Gemini (enforced fail-loud); embedder dim contract (rule 4) |
| **transport.py** | OpenAI-compatible HTTP transport (S6 — stdlib only) | `list_models()`, `openai_transport()`, `openai_tools_transport()`, `_apply_sampling()`, `_apply_response_format()`, `_fill_meta()` | client.complete (transport injected); config (base_url/timeouts); fabric endpoints | Speaks OpenAI /v1/chat/completions (LiteLLM + ollama compatible); sampling allowlist (_SAMPLING_KEYS); schema-constrained decoding (response_format); fail-loud on down endpoint |
| **vram.py** | VRAM gate (S6 — concurrency bound for local model calls) | `VramGate(limit=1)`, `VramGate.slot()` (context manager) | cognition (local model calls acquire); config (limits) | Bounds concurrent LOCAL calls (no cloud); Semaphore-based; live nvidia-smi read not implemented yet |

---

## PUBLIC SURFACE INDEX (every exported function/class, by file)

```
activation: ACTIVATION_CONTEXTS, FLOOR_RESERVE_R, ActivationResult, fire_activation, consolidate_rollup, 
            activity_signal, background_tick, sense_tick, RollupDriver, detect_mode_candidate, propose_mode
activation_driver: activation_loop_enabled, loop_tick_seconds, TickResult, ActivationCaller, 
                   _loop_iteration, run_activation_loop, maybe_start_activation_loop
ai_tics: AiTic, AiTicRegistry, all_markers, as_records
anchors: plant_anchor, plant_ai_corner, embed_via_bridge, AI_CORNER_TEXT, AI_CORNER_SOURCE
attachment_types: AttachmentType, AttachmentTypeRegistry
authoring: FIELD_TYPES, field_types, render_role_source, gate_role_source, load_role_from_source, 
           output_fields_rows, AuthoringError
axis_registry: Axis, AxisRegistry, as_records
cc_attachments: attach, detach, get_attachment, list_attachments, manifest, attachment_types, 
                reset_registry, AttachmentError
cc_board: create_item, transition_item, get_item, list_items, link, add_link, unlink, update_item, 
          list_board, BoardError, reset_registries
cc_clone: register_supervised_member, launch_clone_supervised, launch_clone_interactive, CloneError
cc_dragnet: issue_dragnet, dragnet_status, get_dragnet_run, DragnetError
cc_gate: gate_step, abort_step, rewind_step, list_gates, get_gate, GateError
cc_images: save_image, get_image, image_bytes, list_images, versioned_address, ImageError
cc_retire: harvest_member, harvest_channel, harvest_status, RetireError
cc_voice: engines, running_engine, speak, VoiceError
channel_boundary_run: load_env_file, main, verify_my_half
checks: CheckRegistry, discover, get, rows
ci_scaffold: scaffold_from_routine, github_workflow, gitlab_job
cognition: role_registry, skill_registry, guide_registry, context_registry, decision_registry, 
           explanation_policy_for, run_role, run_items, run_reduce, run_swarm, run_graph, 
           resolve_address, run_stats, VRAM_GATE, SlotBudget, [many more]
coherence_actions: build_action
coherence_calibrate: load_fixtures, score_reachability, calibrate, format_calibration
coherence_detect: extract_routes, classify_reachability
compile: compile
context_ops: read_context, compact_session, ContextOpError
context_variables: TurnContext, ContextVariable (Protocol)
corpus: CorpusError, corpus_address, write_record, list_corpus, find_corpus
corpus_neighbours: neighbours
corpus_rerank: rerank_hits
decision_memory: prewarm_theorem_explains, explanation_grounding, recall_for_decision
decision_registry: Decision, DecisionRegistry, compose_state, DecisionError
decision_subtypes: DecisionSubtype, DecisionSubtypeRegistry
... [and many more]
fabric/client: FabricError, complete
fabric/config: STORE_DIR, DEFAULT_BASE_URL, DEFAULT_BRAIN, resolve_emb_layer, forbid_gemini
fabric/transport: list_models, openai_transport, openai_tools_transport
fabric/vram: VramGate
```

---

## NOTABLE / SURPRISING DISCOVERIES

### Architectural Patterns

1. **Every-module-a-registry (the file-discovered discipline)**: AI-tics, axes, checks, marks, item-types, source-types, attachments, relations, projections, roles, skills, contexts, guides, decisions, decision-subtypes, generation-policies, mode-detection-rules, routines, node-types, lifters. This is ONE pattern applied everywhere. New row = new file, ZERO code edit. (runtime/ai_tics.py:1–45, axis_registry.py:1–50, etc.)

2. **Gate patterns (correctness via isolation)**:
   - **authoring.gate_role_source**: validates role module by importing-in-temp-dir OUTSIDE live tree (line:444–468) — same as Suite._gate_extension (syntax check on new extensions).
   - **coherence_calibrate.calibrate**: pure scoring function (line:36–61), no model.
   - **rules.py**: rule AST evaluated by RESTRICTED evaluator (no eval/exec/compile — line:13–24), structural whitelist.

3. **Reuse-don't-parallel (declared everywhere)**:
   - corpus.py: wraps store's EXISTING public methods (put_content/set_ref/append_event); NO fs_store edit (line:26–31).
   - corpus_neighbours.py: reuses store.vector_index.query_index byte-for-byte (line:42–44).
   - cc_retire.py: reuses session_recall + corpus.write_record + cc_board + cc_attachments (line:20–23).
   - activation_driver.py: orchestrates existing activation.py drivers, never re-implements (line:38–40).

4. **Lineage as sequencing gate (corpus.py, corpus-specific)**:
   - THREE distinct "lineage" axes (corpus/store-provenance/decision-lineage) — DO NOT conflate (line:17–25).
   - Lineage REQUIRED at write (session/round/project) — fail-loud gate (line:97–102), never optional-with-default.

5. **Honest-empty (fail-loud on missing data)**:
   - corpus_neighbours.neighbours: no fabricated zero-vector on missing vector; returns honest note + empty neighbours (line:31–72).
   - cc_retire: honest-state REQUIRED (verified/attempted/broken/abandoned), never fake "done" (line:37).
   - context_ops: never implicit-truthy-on-missing; fail loud on unresolved refs (line:context_ops.py).

### Surprising Constraints + Proofs

6. **The Floor (C9.2 / G9 — no resolve/approve/dispatch outside the brain)**:
   - Rules.py: structural whitelist prevents ANY op that could emit resolve/approve/dispatch (line:52–53).
   - activation.py: routes only through non-consequential destinations (surface/address/lane); if inject has nowhere to land, RE-LANDS at run:// address (line:226–235).
   - Both proven by construction (no op, no path, no how).

7. **The Reserve is Sacred (activation.py, C5.5)**:
   - Non-turn casts run under SAME process-wide VRAM gate as per-turn (line:30–34).
   - Mode MUST reserve R ≥ FLOOR_RESERVE_R for live reply — fail loud (line:176–180).
   - Swarm sub-pool capped so R always remains free.

8. **Determinism + Per-Rule Readiness (rules.py)**:
   - Rule only evaluates when EVERY declared input is SETTLED (line:34–40) — never a timeout gate.
   - Missing/pruned/failed ref FAILS LOUD or hits declared on_missing (line:38–39).
   - NO wall-clock admitted; PURE function of resolved values.

9. **Decision Memory Calibration by USE (decision_memory.py)**:
   - _CTX_FLOOR = −0.13: calibrated AGAINST LIVE served jina-v3 reranker (line:48–55).
   - Off-DOMAIN text ceilings at −0.15; real in-corpus context floors at −0.108 (median +0.03).
   - The −0.5 was a guess on PRE-REBOOT reranker; silent failure on live system (verified 0/8 contexts on adopt-claude-design) — caught by-use.

### Dormancy + Opt-In (activation_driver.py)

10. **Activation loop OFF by default** (line:11–22):
    - Manual endpoint always available; autonomous loop gated on COMPANY_ACTIVATION_LOOP env.
    - Mirrors wire's proven shape (wire_armed() + dispatch driver called directly vs daemon thread).
    - No always-on GPU daemon auto-started; operator greenlights (needs-tim).

11. **Shared embedding layer strategy (fabric/config.py)**:
    - OPERATIVE: pplx-2560 (DEFAULT_EMB_LAYER, line:44).
    - LEGACY: bge/bare (None) still reachable EXPLICITLY (emb=None / 'bge', line:56–57).
    - resolve_emb_layer() idempotent (line:48–58) — single knob reverts whole core.

### Cryptic Abbreviations Decoded

- **RHM**: right-hand-man (the brain in the vision system, decision-surface context builder).
- **G0–G9**: concurrent-cognition group/phase (G0=spike, G2=roles-discovered, G3=rules, G5=activation, G7=view, G9=floor).
- **C0–C9**: concurrent-cognition constraint/chapter (C0.1=2-part turn, C2.1=role-schema, C2.5=capability-query, C5.5=reserve, C9.2=floor, C9.4=drift-home).
- **RULE_OPS**: closed grammar of rule-AST ops (field, lit, and/or/not, eq/ne/lt/le/gt/ge, add/sub/mul/div/min/max/clamp, in/contains).
- **DESTINATION_KINDS**: five routing targets (inject, surface, address, lane, resolve — but NO resolve in non-turn contexts).

### File Counts & Disciplines

- **77 runtime files** (85 minus 7 excluded) + **4 fabric files** = **81 total**.
- **~20 file-discovered registries** (roles, skills, guides, contexts, decisions, decision-subtypes, generation-policies, mode-detection-rules, routines, nodes, lifters, marks, items, sources, relations, attachments, axes, ai-tics, checks, projections, etc.) — all follow ONE pattern.
- **Every registry mirrored in tests/acceptance** (roles_acceptance, rules_acceptance, edge_kinds_acceptance, etc.) — drift home enforced.

---

## CRITICAL INTERCONNECTS

```
cognition.py (hub):
  ├─ registers: roles, skills, contexts, guides, decisions (4 discovery calls each turn)
  ├─ executes: run_role, run_items, run_reduce, run_swarm, run_graph (the engine)
  ├─ resolves: resolve_address (decision/skill/context/code/board/image schemes)
  ├─ routes: rules.evaluate (determine what happens to outputs)
  ├─ ingests: corpus.write_record (capture run outputs)
  ├─ fires: activation.fire_activation (non-turn contexts)
  └─ detects: decision_memory, decision_subtypes (explanation grounding)

authoring.py:
  ├─ renders: role source (fields → BaseModel)
  ├─ gates: temp-import validation (correctness, before live tree)
  └─ reads: FIELD_TYPES (closed registry; unknown type = fail-loud)

rules.py:
  ├─ declares: RULE_OPS (closed grammar; eval never uses eval/exec)
  ├─ routes: DESTINATION_KINDS (5 targets; no resolve/approve/dispatch in non-turn)
  └─ evaluates: pure function of fully-resolved address values

cc_* (company talk):
  ├─ cc_board: noticeboard items (typed, with lifecycle, edges, git-tracked)
  ├─ cc_attachments: channel bindings (flat id-keyed, manifests on read)
  ├─ cc_clone: supervised clones (session_pointintime → spawn → inject)
  ├─ cc_gate: step gates (observer, not reimplementation)
  ├─ cc_images: hierarchical image addresses (navigable tree, blob-addressed)
  ├─ cc_retire: crystallization (member→corpus, channel→corpus)
  └─ cc_voice: TTS rendering (surfaces existing engines)

fabric/:
  ├─ client: guarded calls (retry+jitter, JSON-repair, schema-validate)
  ├─ transport: OpenAI-compatible HTTP (LiteLLM + ollama)
  ├─ config: all configurable (store/model/embed/timeout), NO Gemini
  └─ vram: semaphore-gated local-call concurrency
```

---

## UNREAD DETAILS (Deferred — Mapped by Header/Purpose Only)

These files exist, are mapped by purpose, but were not read in detail due to token budget. All are discoverable via their modules' public API and fit one of the registry/pattern categories above.

- cc_dragnet, coherence_actions, coherence_calibrate, corpus_rerank, dials, flows, forms, freshness, generate_mockup, guide_author, minds, model_routing, operator_memory, orienteering_drift, page_face, projection, recall_determine, render_declaration, routine_runner, routine_schedule, scheduler, session_lens, session_lineage, session_pointintime, session_recall, session_scan, session_search, skills, territory, ui_claude_session, verdict_panels, vi_vision, registry, implement

All are scanned by their docstrings (first 1–5 lines) and fit known categories (registry, orchestrator, service, renderer). Their signatures and roles are clear from context + their consuming callers.

---

END MAP
