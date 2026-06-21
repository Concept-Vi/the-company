# AREA: tests/ — Comprehensive Landscape

**Extractor:** subagent (sonnet 4.6) · **Date:** 2026-06-21
**Scope:** 234 files in `/home/tim/company/tests/` — all Python acceptance suites
**Additional test files outside tests/:** `canvas/app/voice_autolisten_controlflow.test.mjs`, `minds/bind_compose_test.py`

---

## Test Framework + Conventions

**Framework:** Custom `check(label, cond)` + `main()` pattern (dominant — ~189 of 234 files), NOT pytest.
- Each file runs standalone: `.venv/bin/python tests/<name>_acceptance.py`
- All run-all loop: `for t in tests/*.py; do ./.venv/bin/python "$t"; done`
- Entry: `check()` accumulates pass/fail; most exit non-zero on any fail
- **Minority** use pytest `def test_()` style (5 files: `conversational_build_acceptance.py`, `json_schema_transport_acceptance.py`, `generate_mockup_acceptance.py`, `render_declaration_acceptance.py`, `transport_rep_penalty_acceptance.py`)
- No `pytest.mark.skip`, no `xfail` markers found anywhere — the project does not use pytest skip decorators

**Skip/Conditional pattern:** Tests that require a live model (`:8000` resident 4B or `:8001` embed endpoint) print a loud notice and return partial pass — "needs-live-dep" in `suite_health_acceptance.py` vocabulary. 40 files have this pattern.

**Guard gate:** `suite_health_acceptance.py` — runs ALL `*_acceptance.py` suites as subprocesses, fails loud if any red. Pre-merge / pre-deploy gate.

---

## Test Inventory by Subsystem

### ENGINE STAGES (E-series) — Core runtime spine

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `walking_skeleton.py` | Stage 0: reactive firing, memoize, change-propagation, resume after restart | scheduler + FsStore + nodes (constant, uppercase) end-to-end |
| `e1_acceptance.py` | E1: typed spine + all contracts compose, store hardened | All C1–C8 contracts import; store put/get/exists/set_ref/head; provenance lineage; FsStore conforms to Resolver Protocol |
| `e2_runtime.py` | E2: real runtime — compile in run path, branching graphs, pause/retry/branch | compile + scheduler (fanin graphs, pause/retry/branch operations) |
| `e2_review_fixes.py` | Regression: 3 findings from E2 adversarial review | Three specific bug fixes |
| `e3_fabric.py` | E3: fabric reliability guards + VRAM semaphore (transport-agnostic) | vram semaphore, fabric retry, timeout |
| `e3_integration.py` | E3 integration smoke — REAL model call through guarded fabric | Live ollama required; fail-loud if not up |
| `e4_registry.py` | E4: live node-type registry (TDD — red before runtime/registry.py exists) | NodeRegistry.discover(), runtime/registry.py |
| `e5_suite.py` | E5: shared Suite + MCP agent face (one brain, two faces, one substrate) | Suite + MCP face tools registered |
| `e6_governance.py` | E6: act-unwatched policy + surfaced-decision inbox | governance unwatched, inbox S7/D4/D7 |

### STORE — Content-addressing, durability, concurrency

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `concurrency_acceptance.py` | S4: cross-process safety (REAL subprocesses, not threads) | fcntl OS file lock serializes load→mutate→save across bridge+MCP processes; double-dispatch prevention |
| `cross_process_lock_acceptance.py` | REAL cross-process T-LOCK | fsync lock semantics |
| `durability_acceptance.py` | T-FSYNC: durability / fsync | store write durability |
| `set_ref_atomic_acceptance.py` | set_ref is ATOMIC (no torn/empty read) | hardening FIX 1 |
| `volatile_acceptance.py` | VOLATILE nodes never memo-frozen | hardening red-team F1 fix |
| `fs_session_guard.py` | review-session storage methods cannot silently vanish | T3-SESSION-CHURN |

### RUNTIME — Scheduler, registry, compile, modes, suite

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `scheduler_isolation_acceptance.py` | Per-node error isolation | hardening FIX 2 |
| `mode_autodetect_acceptance.py` | Concurrent Cognition Group I: mode AUTO-DETECTOR | auto-detect slot |
| `autodetect_setter_acceptance.py` | GC6/E2-live: MODE_AUTODETECT is a runtime-settable slot | settable at runtime |
| `modes_acceptance.py` | RHM modes / presence dial (slice 2, D1-D3) | mode registry |
| `modes_typeregistry_acceptance.py` | E1 mode TYPE-REGISTRY + E2-BACKEND auto-detect toggle | type registry |
| `settings_surface_acceptance.py` | A3 settings consolidated + E2-FE/GC3 mode surface | settings surface |
| `spawn_flags_crosscheck_acceptance.py` | Spawn-flag posture cross-check (F-FIX-9) | spawn flags |
| `config_writer_acceptance.py` | (exists in __pycache__ — file itself not listed in py files) | |

### CONTRACTS — Address grammar, object_info, bridge_msgs

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `address_grammar_acceptance.py` | S0: ONE canonical ui:// grammar | parse + canonical normalization |
| `address_scope_acceptance.py` | S3: backend ui://→code://→scope[] resolver | scope resolution |
| `clone_address_grammar_acceptance.py` | clone:// joins ONE addressed state | A+B unify |
| `session_address_grammar_acceptance.py` | ONE shared session:// sub-address grammar | session grammar |
| `event_address_acceptance.py` | S2: event-address-stamp (keystone) | event address |
| `ui_registry_acceptance.py` | S1: element-level addresses in live registry | registry addresses |
| `bridge_routes_acceptance.py` | BRIDGE_ROUTES as SINGLE SOURCE of bridge routes | route sourcing |
| `bridge_session_acceptance.py` | RAIL R1-prime SERVICE-LEVEL proof | capability fabric |
| `blueprint_acceptance.py` | B1: importable blueprint COMPLETE + CONSISTENT | blueprint integrity |
| `node_states_render_acceptance.py` | S5: node_states `render` field | render field |
| `json_schema_transport_acceptance.py` | json_schema transport branch (L-transport · C1.4 / R1-FOLD F9) | json schema in transport |

### FABRIC — Model transport, retry, VRAM, tools

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `fabric_retry_acceptance.py` | Model layer robust to ollama-cloud high-variance latency | retry logic |
| `fabric_tools_acceptance.py` | NATIVE TOOL-CALLING fabric path | native tool calling |
| `embeddings_acceptance.py` | Embedding chain by USE against live BGE-M3 endpoint (:8001) | T2-EMBED-GATE; loud skip if endpoint down |
| `transport_rep_penalty_acceptance.py` | Sampling-family passthrough (FABRIC-2 / O2) | rep_penalty ladder |
| `reachability_acceptance.py` | THE REACHABILITY GATE | reachability |
| `model_capabilities_acceptance.py` | G8/L-model (C8.1–C8.4): model-TYPE capability registry | model capabilities |
| `model_catalog_acceptance.py` | C2.5: model CATALOG widened to full declared model set | catalog completeness |

### COGNITION ENGINE — Corpus, marks, registries, cascade

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `corpus_acceptance.py` | D1: corpus-record WITH LINEAGE (sequencing gate) | corpus record lineage |
| `marks_acceptance.py` | GROUP M: marks store (finding store GENERALIZED) | marks API |
| `cascade_acceptance.py` | GROUP N: CASCADE RUNNER (N1-N3) | cascade runner |
| `reduce_acceptance.py` | C 2/4: cross-unit REDUCE | reduce |
| `run_items_acceptance.py` | C 3/4: run_items + address resolver | run_items |
| `disposition_acceptance.py` | C1-C2: finding store + disposition overlay | findings |
| `dispose_policy_acceptance.py` | C4: findings are agent-disposable; ESCALATES by design | escalation policy |
| `registry_authoring_marks_acceptance.py` | WIRING P2 create_* + M1 marks API | create/mark API |
| `reconcile_acceptance.py` | C3: (kind,address) reconcile + burn-down rollup (C5) | reconcile |
| `finding_flow_acceptance.py` | C6: substrate flows END-TO-END on REAL data | end-to-end finding |
| `richer_types_acceptance.py` | B2: RICHER output-field types | output types |
| `edge_kinds_acceptance.py` | Edge-kind registry + drift home (C1.3 / R2-FOLD H5) | edge kinds |
| `ai_tics_acceptance.py` | AI-tics as FILE-DISCOVERED registry (M4/P1) | ai_tics registry |
| `forms_acceptance.py` | Forms as FILE-DISCOVERED registry (P1 effort-routing) | forms registry |
| `generation_policies_acceptance.py` | Generation-policies as FILE-DISCOVERED registry | gen policies |
| `generation_policy_ladder_acceptance.py` | O2: rep_penalty LADDER wired into cognition engine | policy ladder |
| `lifters_acceptance.py` | Lifters as FILE-DISCOVERED registry (P1 · K2) | lifters registry |
| `mark_types_acceptance.py` | Mark-types as FILE-DISCOVERED registry (M1/M4/P1) | mark types |
| `projections_acceptance.py` | Projections as FILE-DISCOVERED registry (K1/P1) | projections registry |
| `relation_types_acceptance.py` | Relation-types as FILE-DISCOVERED registry (L3/P1) | relation types |
| `roles_acceptance.py` | File-discovered ROLE registry (G2) | roles registry |
| `state_types_acceptance.py` | STATE-TYPE REGISTRY (Possibility Space Block 19) | state types |
| `chunk_compose_acceptance.py` | F3: chunk-and-compose for over-context units | chunking |
| `no_confidence_acceptance.py` | G16: NO-CONFIDENCE INVARIANT (Tim's law) | no-confidence |
| `space_embed_acceptance.py` | SPACE-KEYED EMBED, end-to-end (GROUP L · L1/D2 + O3) | space embeddings |
| `conv_index_space_acceptance.py` | SPACE-KEYED vectors + per-space query (GROUP L) | per-space query |

### CONCURRENT COGNITION — Activation, chat, roles, governance

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `activation_caller_acceptance.py` | Group H/I: ALWAYS-ON CALLER | activation caller |
| `activation_contexts_acceptance.py` | G5: ACTIVATION CONTEXTS | activation contexts |
| `activation_drivers_acceptance.py` | Group H + I: activation drivers | activation drivers |
| `authoring_acceptance.py` | AUTH (C7.4/C7.5): authoring BACKEND (has live-dep skip for dry_run_role) | authoring |
| `calibration_acceptance.py` | D: calibration harness (experiment → measure → save) | calibration |
| `cast_beyond_listening_acceptance.py` | C 4/4 | cast mechanism |
| `chat_parts_acceptance.py` | G4: staged-response queue | staged response |
| `cognition_governance_acceptance.py` | G9: governance + safety, binds all | governance |
| `cognition_info_acceptance.py` | L-fe-be: cognition VIEW backend (has live-dep skip for lifecycle) | cognition view |
| `cognition_info_registries_acceptance.py` | 6 corpus registries projected into live cognition view | registry projections |
| `cognition_resolution_loop_acceptance.py` | GROUP J: cognition↔resolution loop | resolution loop |
| `locus_acceptance.py` | R1: backend current-locus (persisted ui:// locus) | locus persistence |
| `rules_acceptance.py` | G3: RULE ENGINE (L2 core) | rules engine |
| `voice_parts_acceptance.py` | G6: voice coupling — PART is the TTS unit | voice parts |

### SESSION FABRIC — Session tracking, search, export, mailbox

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `agent_sessions_channels_acceptance.py` | R2.2–R2.5: cross-session organs | cross-session |
| `agent_sessions_exporter_acceptance.py` | F1.4: FILTER LAW has teeth; QUIESCE law; idempotent | export filter law |
| `agent_sessions_mailbox_acceptance.py` | §C: MAILBOX leaf + MCP face verbs | mailbox |
| `agent_sessions_registry_acceptance.py` | F1.2: agent-session REGISTRY | session registry |
| `session_pointintime_acceptance.py` | R3.3/R3.4 unit + structural guarantees, without live dep | point-in-time |
| `session_search_acceptance.py` | SEARCH→HANDLE→ACT chain teeth | search chain |
| `session_search_mcp_stdio_probe.py` | R4.4 + R4.5: AGENT-NATIVE chain proof | MCP stdio probe |
| `session_supervisor_acceptance.py` | F1.1: session supervisor service-level guarantees | supervisor SLA |
| `session_supervisor_params_acceptance.py` | FAMILY 1 cost/usage + FAMILY 2 params | supervisor params |
| `resolve_own_session_acceptance.py` | Self-serve-memory SAFETY keystone: resolve_own_session | safety |
| `journey_recording_acceptance.py` | L9: reverse journey-recording (§21.7#2-reverse, ISSUE-5) | journey recording |
| `commit_queue_acceptance.py` | Concurrent-append/commit QUEUE (fork, 2026-06-20) | commit queue |

### WIRE — Decision→Implementation wire, dispatch, governance

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `wire_acceptance.py` | Group W / S8: Decision→Implementation Wire — launch, dispatch, verify, requeue | full wire path |
| `wire_adversarial.py` | Adversarial red-team of the wire | security/edge cases |
| `wire_async_dispatch_acceptance.py` | WIRE-ASYNC: build dispatch decoupled from UI | async dispatch |
| `wire_commit_acceptance.py` | Wire's GIT CHECKPOINT (Tim's safety mandate before arming) | git safety |
| `wire_harden_acceptance.py` | WIRE-HARDEN H1–H8: definition-of-done == wire hardening | hardening |
| `wire_loop_acceptance.py` | W6/W7 / S8 part 1+7: UNATTENDED trigger | unattended loop |
| `wire_trigger_acceptance.py` | L2: WIRE TRIGGER (resolve→dispatch production caller) | wire trigger |
| `decisions_acceptance.py` | Decision-surface resolver (D1–D7) — grammar, registry, resolve, normalization, territory | full decision |
| `decision_lineage_acceptance.py` | Audit must not silently truncate | fail-loud |
| `feedback_to_wire_acceptance.py` | L1: addressed-feedback → wire (§21.4#2) | feedback wire |

### CONVERGENCE — Convex build, payload, index, blast, consent

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `conv_payload_acceptance.py` | X1+X2: launch-context truth reaches DISK | payload |
| `conv_context_acceptance.py` | X3: ATTACHED CONTEXT reaches payload (R2 gather at mint) | context |
| `conv_compose_acceptance.py` | X4: build_instruction composes RICH prompt | prompt composition |
| `conv_consent_acceptance.py` | X5: CONSENT-TIME RESOLUTION (trust property) | consent |
| `conv_bridge_acceptance.py` | X6: ui://↔run:// bridge | bridge |
| `conv_pin_acceptance.py` | X7: pin override works | pin |
| `conv_dedup_acceptance.py` | X8: dedup R2 gather | dedup |
| `conv_blast_acceptance.py` | X9: blast_radius(address) Seam 2 | blast radius |
| `conv_index_acceptance.py` | X12: PERSISTED VECTOR INDEX | vector index |
| `conv_index_staleness_acceptance.py` | X12: READ-ONLY index STALENESS check | staleness |
| `conv_semantic_rank_acceptance.py` | X13: R2 SEMANTIC ranking term | semantic rank |
| `conv_blast_both_acceptance.py` | X14: blast_radius spans BOTH edge kinds | edge blast |
| `conv_constitution_acceptance.py` | X15: build_instruction names GOVERNING CONSTITUTION | constitution |
| `conv_reach_acceptance.py` | X16: operator-approves-the-reach | operator reach |
| `conv_configurable_acceptance.py` | X17: composition is configurable (D2) | configurability |
| `conv_freshstart_acceptance.py` | V-A: new conversation actually starts FRESH | fresh start |
| `convergence_signoff_acceptance.py` | F: coherence's structural half of convergence sign-off | sign-off |
| `conversational_build_acceptance.py` | Conversational → SELF-BUILD bridge | self-build bridge |

### RHM (Right-Hand-Man) — Chat, grounding, actions, modes

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `rhm_acceptance.py` | I2: RHM panel first cut | rhm panel |
| `rhm_action_acceptance.py` | Slice 1 C1: RHM action-through-the-gate | action via gate |
| `rhm_action_parse_acceptance.py` | NATIVE TOOL-CALLING dispatch + affordances | tool dispatch |
| `rhm_completion_acceptance.py` | RHM reliably COMPLETES and SHOWS actions | completion |
| `rhm_grounding_acceptance.py` | RHM grounded in the WHOLE interface | grounding |
| `walkthrough_acceptance.py` | T2-RHM-COVERAGE: RHM walkthrough/review organ end-to-end | end-to-end RHM |
| `consult_acceptance.py` | Q1: RHM knows the design (slice 10) | design knowledge |
| `configs_acceptance.py` | E1-E2: RHM configs (slice 3) | configs |
| `modes_acceptance.py` | D1-D3: RHM modes / presence dial (slice 2) | modes |
| `copresence_acceptance.py` | G1+H1: co-presence (slice 4) | co-presence |
| `inbox_acceptance.py` | F1-F2, C2-C3: inbox lanes + COA drillability (slice 6) | inbox |
| `twin_acceptance.py` | B1, B3: twin mechanism (slice 7) | twin |
| `trajectory_acceptance.py` | I1-I2: trajectory as training signal (slice 8) | trajectory |
| `react_acceptance.py` | Q2: watch-and-react ambient commentary (slice 12) | react |
| `selfmod_acceptance.py` | Q3: update app through interface safely (slice 13) | selfmod |
| `panel_acceptance.py` | Add panel through interface (slice 14) | panel |
| `extension_acceptance.py` | Self-coding subsystem BUILD-GATE (slice 15) | build gate |

### SURFACE / INTERFACE — UI, canvas, panels, forms

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `act_endpoint_acceptance.py` | I2: /api/act emission seam (RELOCATION) | act endpoint |
| `annotate_vs_operate_acceptance.py` | I5: annotate vs operate routing distinction | routing |
| `annotation_acceptance.py` | I6: annotation-at-an-address (annotation:// branch) | annotation |
| `addr_chat_acceptance.py` | I7: chat-thread at an address (chat:// branch) | chat addr |
| `addr_context_acceptance.py` | R2: address-keyed context resolution (keystone) | context resolution |
| `addr_history_acceptance.py` | L3: addressed history/audit (§21.7#1) | history |
| `address_help_surface_acceptance.py` | D2: COMPOSED address-help / altitude SURFACE | help surface |
| `click_tier_acceptance.py` | I4: governance-tiered clicks (ADDRESS-KEYED) | tiered clicks |
| `focus_ui_address_acceptance.py` | I1: click-to-indicate (focus vocabulary widening) | focus |
| `forms_acceptance.py` | P1 effort-routing: forms as FILE-DISCOVERED registry | forms |
| `inputs_selects_acceptance.py` | INPUT-WIRING + COMPOSITION select ADVERTISES full | inputs |
| `interactive_consent_acceptance.py` | B2: ON-SCREEN INTERACTIVE BUILD consent surface | consent UI |
| `interactive_inbox_acceptance.py` | B3: configurable interactive-inbox (§6B QUEUE mode) | inbox UI |
| `panel_acceptance.py` | Add panel through interface (slice 14) | panel UI |
| `portal_acceptance.py` | Portals: one artefact, many live views (I4) | portals |
| `propose_affordance_acceptance.py` | OFFER-WITH-OPTIONS consent affordance ("shall I?") | offer affordance |
| `show_acceptance.py` | Q2: attention-direction (slice 11) | attention |
| `showme_backend_acceptance.py` | C3+C4: SHOW-ME / guided-operation BACKEND | showme |
| `showme_c2_acceptance.py` | C2: TEACH-TO-REQUEST-CHANGE (bootstrap) | teach |
| `showme_guided_acceptance.py` | C1: SYSTEM-INITIATED GUIDED SEQUENCES + G-43 | guided |
| `generate_mockup_acceptance.py` | Generate-for-mockups ENGINE CORE | mockup engine |
| `design_gate_acceptance.py` | F9: FORM gate is LIVE (stub graduated) | form gate |
| `render_declaration_acceptance.py` | R1.2 render-declaration layer (pytest-style) | render decl |
| `coherence_cli_acceptance.py` | C5 CLI FORM: `company coherence` read face | coherence CLI |

### CC (Cross-session / Claude Code interfaces)

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `cc_attachments_acceptance.py` | Structural gate for runtime/cc_attachments.py | attachments |
| `cc_board_acceptance.py` | Company NOTICEBOARD acceptance | noticeboard |
| `cc_board_reverse_acceptance.py` | H1.2 gate: reverse_traverse + relations on cc_board | reverse traverse |
| `cc_channels_acceptance.py` | Cross-session CHANNEL router (runtime/cc_channels.py) | channels |
| `cc_clone_acceptance.py` | Structural regression gate for runtime/cc_clone.py | clone |
| `cc_clone_reflection_persist_acceptance.py` | Reflection-PERSISTENCE bug + clone:// addressing | reflection persist |
| `cc_gate_acceptance.py` | R15 gate: per-step gate/abort/rewind | gate/rewind |
| `cc_gate_bar1_verification.py` | R15 BAR 1, on REAL data: opaque step_address resolves | real data gate |

### VOICES — STT, TTS, circuit, speakable

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `voice_circuit_acceptance.py` | V-PTT (push-to-talk) CIRCUIT end-to-end by USE | PTT circuit |
| `voice_parts_acceptance.py` | G6: voice coupling (PART is the TTS unit) | TTS parts |
| `speakable_acceptance.py` | V-C strip + V-D expression SPEAKABLE LAYER by USE | speakable |
| `stt_models_acceptance.py` | GPU STT ears transcribe + VRAM measured (lane: stt, step 4) | STT VRAM |
| `stt_whispercpp_acceptance.py` | Swappable STT ear registry works by USE | STT ears |

### PROJECTIONS + INTROSPECTION — Mirror registry, drift, layer

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `introspection_acceptance.py` | LANE-REFRESH full acceptance suite (Mirror-Registry System) | mirror refresh |
| `introspection_core_acceptance.py` | LANE-INTROSPECTION-CORE | mirror core |
| `cap_wire_acceptance.py` | LANE-CAP-WIRE (Mirror-Registry System Stage 2) | cap wire |
| `projection_instrument_acceptance.py` | THE UNIVERSAL PROJECTION teeth | projection |
| `projection_multilayer_acceptance.py` | MULTI-LAYER embedding model + MRL RESOLUTION teeth | multilayer |
| `projection_scale_acceptance.py` | GROUP 11 MULTI-SCALE EMBEDDING PYRAMID teeth | scale pyramid |
| `projection_semantic_acceptance.py` | GROUP 6 CIRCLE / semantic radius teeth | semantic radius |
| `layers_acceptance.py` | Provenance layers (I4, context-13 "Layers") | layers |
| `drift_acceptance.py` | PoLR-3: map self-maintains | drift |
| `territory_acceptance.py` | address→territory composer OPERATOR-LAW + DEGRADE contract | territory |

### MINDS — Composition, seams, binding

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `minds_acceptance.py` | R13: composable-mind (runtime/minds.py) | minds |
| `minds_composition_acceptance.py` | R13 bar 3: run_composition EXECUTES feeds edge | composition |
| `minds_seam_acceptance.py` | R13 seams A+B: REAL resolve_address→mind→traverse | seams |

### HEARTS + RESOLUTION — Core resolution laws

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `heart_resolution_acceptance.py` | H1.1: "follow one typed edge across two registries" | typed edge |
| `polr_acceptance.py` | AI-path-of-least-resistance: registry as truth + ask-don't-fabricate | PoLR |

### ROUTINES — Scheduling, goal-loop, routines registry

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `routines_acceptance.py` | S-R9.1: routine registry + runner + tool acceptance | routines |
| `routine_goal_loop_acceptance.py` | S-R9.1: goal-loop CC-22 BOUNDED loop logic | goal loop |
| `routine_schedule_acceptance.py` | S-R9.1: schedule arm (no systemctl, no arming) | schedule arm |
| `scheduler_isolation_acceptance.py` | Per-node error isolation | error isolation |

### MCP FACE + AGENT INTERFACES

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `mcp_engine_acceptance.py` | #53 MCP engine-exposure (AGENT face) VERIFY BY USE | MCP agent face |
| `mcp_use.py` | ACTUAL USE: real MCP client connects, composes+runs a graph | end-to-end MCP |
| `context_ops_acceptance.py` | S-R10.1: context ops + tool acceptance (no real claude) | context ops |
| `supervisor_routes_acceptance.py` | F1.5: contract corpus MACHINE INVENTORY teeth | machine inventory |

### SELF-MODIFICATION + AUDIT

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `selfmod_acceptance.py` | Q3: update app through interface safely (slice 13) | safe selfmod |
| `selfmod_audit_acceptance.py` | Self-modification AUDIT LEDGER + safe revert | audit ledger |
| `self_change_locating_acceptance.py` | L5: self-change-locating (§21.7#5) | change locating |
| `self_growth.py` | SELF-GROWTH: system writes itself a new capability, governed | self-write |
| `hardening_acceptance.py` | Red-team remediations F2/F4/F6 | hardening |
| `brain_env_acceptance.py` | Loadable-brain subprocess runs LEAST-PRIVILEGE (fork, 2026-06-17) | least privilege |

### FIRST PURPOSE / INTEGRATION

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `first_purpose.py` | System answers question about its OWN codebase, grounded (LIVE model) | full first purpose |
| `self_growth.py` | Self-writes a new capability end-to-end | self-growth |
| `mcp_use.py` | Real MCP client end-to-end | MCP E2E |

### MISC / HEALTH / INFRASTRUCTURE

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `suite_health_acceptance.py` | ALL suites pass (pre-merge gate); classifies green/needs-dep/red | standing gate |
| `drift_acceptance.py` | PoLR-3: map self-maintains | map drift |
| `ci_scaffold_acceptance.py` | S-R9.1 CI scaffolder (CC-30): GitHub/GitLab workflow generation | CI scaffolding |
| `genproof_second_platform_acceptance.py` | C-GENPROOF (LIFT GATE) | gen proof |
| `AGENTS.md` | Constitution (not a test file) | |

### SPECIALIZED / LESS OBVIOUS

| File | What it tests | Key contracts |
|------|--------------|---------------|
| `agency_acceptance.py` | Symmetric agency + NL→graph (slice 5, G2+G3) | agency |
| `twin_located_gold_acceptance.py` | L4: twin's LOCATED gold label (§21.7#7) | twin gold |
| `presentation_learning_acceptance.py` | F1: presentation-feedback LEARNING LOOP | learning |
| `memo_stale_acceptance.py` | L10: "stale at this address" memo derivation (§21.7#10) | stale memo |
| `version_history_acceptance.py` | L6: live-history / versions at an address (§21.7#6) | versioning |
| `inbox_target_acceptance.py` | L8: inbox-target click-to-thing (§21.7#9) | inbox target |
| `navgraph_acceptance.py` | B3: filesystem-as-graph reconstructs register.json journeys | navgraph |
| `coa_acceptance.py` | F1: coa up-translate ORGAN (#1 foundation shore-up) | up-translate |
| `uptranslate_acceptance.py` | F1: GENERALIZED up-translate move ("present-this-at-altitude") | uptranslate |
| `run_discovery_acceptance.py` | #54 STORAGE-DISCOVERY: run INDEX + outputs→inputs loop | discovery |
| `run_index_incremental_acceptance.py` | E2: run index is INCREMENTAL | incremental index |
| `route_run_output_acceptance.py` | E4: run-output DESTINATION | output dest |
| `suite3_wiring_acceptance.py` | SUITE-3: wiring that makes new substrate LIVE | substrate wiring |
| `suite_corpus_relations_acceptance.py` | SUITE-lane FACE over corpus pillar | corpus relations |
| `direct_create_acceptance.py` | #58 DIRECT autonomous create VERIFY BY USE | autonomous create |
| `detectors_acceptance.py` | Structural coherence detectors (round-1 layer) | detectors |
| `vi_vision_branch_acceptance.py` | resolve_address vi-vision:// DISPATCH branch (fork, 2026-06-17) | vi-vision |
| `skills_contexts_acceptance.py` | Skills + contexts as addressable registries (C 3b) | skills/contexts |
| `conv_howto_acceptance.py` | D1: FOUNDATIONAL HOW-TO / AFFORDANCE stratum | how-to |
| `conv_index_acceptance.py` | X12: PERSISTED VECTOR INDEX | vector index |
| `gate_acceptance.py` | T2-EMBED-GATE: gate node per-port selective branching routes | gate routing |
| `gate_composition_step_acceptance.py` | R13 bar 4: R15 gate/rewind fires on COMPOSITION-STEP | gate compose |

---

## Files WITHOUT `def test_()` or `def main()` — Non-standard or placeholder

These 5 files lack a `def test_()` or pytest-style functions AND have no `def main()` — they may be structural/data:
- `actions_acceptance.py` — docstring exists, but structure unclear
- `addr_chat_acceptance.py`
- `address_help_surface_acceptance.py`
- `blueprint_acceptance.py`
- `cc_board_reverse_acceptance.py`
- `actions_acceptance.py`, `agency_acceptance.py`, `calibration_acceptance.py`, `addr_history_acceptance.py`, `configs_acceptance.py`, `annotation_acceptance.py`, `cc_gate_acceptance.py`, `coherence_cli_acceptance.py`, `conv_freshstart_acceptance.py`, `corpus_acceptance.py`, `e2_review_fixes.py`

(Note: absence of `def test_` is expected — most use `check()` + `main()` pattern. The 5 genuinely without `def main()` are uncertain.)

---

## Skip / Stale / Conditional Tests

**No `pytest.mark.skip` or `xfail` markers exist in the entire codebase** — confirmed by exhaustive grep.

**Live-dependency skip pattern (40 files):** Tests print a loud notice and pass with a note when a required live service is down (resident 4B at `:8000`, BGE-M3 at `:8001`). This is documented design ("needs-live-dep"). Files:

```
activation_drivers_acceptance.py    agency_acceptance.py
authoring_acceptance.py             calibration_acceptance.py
capture_lenses_acceptance.py        cascade_acceptance.py
cc_channels_acceptance.py           cc_gate_bar1_verification.py
chat_parts_acceptance.py            coa_acceptance.py
cognition_info_acceptance.py        consult_acceptance.py
context_ops_acceptance.py           conv_index_acceptance.py
conv_semantic_rank_acceptance.py    convergence_signoff_acceptance.py
direct_create_acceptance.py         embeddings_acceptance.py
event_address_acceptance.py         fabric_tools_acceptance.py
json_schema_transport_acceptance.py  minds_composition_acceptance.py
mcp_engine_acceptance.py            model_capabilities_acceptance.py
reduce_acceptance.py                rhm_action_acceptance.py
rhm_completion_acceptance.py        rhm_grounding_acceptance.py
run_discovery_acceptance.py         scheduler_isolation_acceptance.py
space_embed_acceptance.py           speakable_acceptance.py
stt_models_acceptance.py            stt_whispercpp_acceptance.py
suite_health_acceptance.py          transport_rep_penalty_acceptance.py
twin_located_gold_acceptance.py     uptranslate_acceptance.py
voice_circuit_acceptance.py         voice_parts_acceptance.py
```

**Full live-only tests (require live services, no offline path):**
- `e3_integration.py` — fails LOUD if ollama not up (no skip path)
- `first_purpose.py` — requires live model
- `self_growth.py` — requires live model
- `mcp_use.py` — requires running MCP server

---

## Coverage Map

### WELL-TESTED (dedicated suites + indirect exercise)

| Area | Assessment |
|------|-----------|
| Store (FsStore) — put/get/exists/set_ref/head, atomicity, durability, cross-process lock | **Strong** — 6+ dedicated files |
| Runtime scheduler — reactive firing, memo, branching, per-node error isolation | **Strong** — E-series + scheduler_isolation |
| Contracts (address grammar, object_info, bridge_msgs) | **Strong** — 6+ dedicated files |
| Wire (Decision→Implementation) — dispatch, async, commit, hardening, adversarial | **Strong** — 7 dedicated files + adversarial |
| Convergence — payload, context, compose, consent, bridge, blast, index | **Strong** — 17 dedicated files |
| Cognition engine — corpus, marks, cascade, reduce, registries | **Strong** — 20+ dedicated files |
| Session fabric — supervisor, mailbox, registry, export, search | **Strong** — 8 dedicated files |
| RHM — chat, grounding, action, completion, modes | **Strong** — 10+ dedicated files |
| CC board/channels/clone/gate | **Moderate** — 8 dedicated files |
| Voice — STT, circuit, speakable, parts | **Moderate** — 5 dedicated files (live-dep-heavy) |
| Fabric transport — retry, tools, embedding, rep_penalty | **Moderate** — 5 dedicated files |
| Self-modification — selfmod, audit, hardening | **Moderate** — 5 dedicated files |
| Interface (surface, clicks, forms, panels) | **Moderate** — scattered across many slices |
| Routines — registry, goal-loop, schedule | **Moderate** — 3 dedicated files |

### GAPS — No or thin test coverage

#### ZERO COVERAGE — No test file, not mentioned in any test

| Module | Path | What it does |
|--------|------|-------------|
| `axis_registry` | `runtime/axis_registry.py` | Axis registry (device, mode, etc.) |
| `brain_router` | `runtime/brain_router.py` | RHM supervisor-as-loadable-brain backend |
| `cc_voice` | `runtime/cc_voice.py` | Give text a VOICE through TTS engine |
| `channel_boundary` | `runtime/channel_boundary.py` | Channel boundary logic |
| `channel_boundary_run` | `runtime/channel_boundary_run.py` | Channel boundary run |
| `corpus_neighbours` | `runtime/corpus_neighbours.py` | Corpus neighbour queries |
| `corpus_rerank` | `runtime/corpus_rerank.py` | Corpus re-ranking |
| `decision_memory` | `runtime/decision_memory.py` | Decision memory |
| `decision_subtypes` | `runtime/decision_subtypes.py` | Decision subtype registry |
| `model_routing` | `runtime/model_routing.py` | Model routing logic |
| `recall_determine` | `runtime/recall_determine.py` | Recall determination |
| `session_lens` | `runtime/session_lens.py` | Lenses over scanned sessions |
| `session_lineage` | `runtime/session_lineage.py` | Session fork tree + distance map |
| `session_recall` | `runtime/session_recall.py` | Semantic recall over sessions |
| `stack_item_types` | `runtime/stack_item_types.py` | Stack item types registry |
| `supabase_principal` | `runtime/supabase_principal.py` | Supabase principal authentication |
| `axes/device` | `axes/device.py` | Device axis |
| `tts_service` | `voice/tts_service.py` | TTS service (the actual service layer) |
| `_stt_service` | `voice/ears/_stt_service.py` | STT service base |
| `verify_voice` | `voice/ops/verify_voice.py` | Voice verification ops |
| `test_ears` | `voice/ops/test_ears.py` | Ear testing ops |
| `titlecase` | `nodes/titlecase.py` | Titlecase node |
| `common_knowledge` | `projections/common_knowledge.py` | Common knowledge projection |
| `extractions` | `projections/extractions.py` | Extractions projection |
| `claude_sessions_reindex` | `ops/claude_sessions_reindex.py` | Session reindex ops |
| `dragnet_determine` | `ops/dragnet_determine.py` | Dragnet determination |
| `dragnet_extract` | `ops/dragnet_extract.py` | Dragnet extraction |
| `embed_extractions` | `ops/embed_extractions.py` | Embed extractions |
| `fabric_live_probe_r34` | `ops/fabric_live_probe_r34.py` | Fabric live probe R3-R4 |
| `fabric_live_probe_wake` | `ops/fabric_live_probe_wake.py` | Fabric wake probe |
| `seed_self` | `ops/seed_self.py` | Self-seeding ops |
| `serve_pplx_embed` | `ops/serve_pplx_embed.py` | PPLX embedding server |
| `serve_rerank` | `ops/serve_rerank.py` | Rerank server |
| `transcript_search` | `ops/transcript_search.py` | Transcript search |
| `wire_substrate_claude_sessions` | `ops/wire_substrate_claude_sessions.py` | Wire substrate |
| `drift_radar` | `flows/drift_radar.py` | Drift radar flow |
| `floor_walk` | `flows/floor_walk.py` | Floor walk flow |
| `pattern_cluster` | `flows/pattern_cluster.py` | Pattern clustering flow |
| `registry_generation` | `flows/registry_generation.py` | Registry generation flow |
| `repo_ingest` | `flows/repo_ingest.py` | Repository ingestion flow |
| `transcript_mine` | `flows/transcript_mine.py` | Transcript mining flow |
| `ts_backfill` | `flows/ts_backfill.py` | Timestamp backfill flow |

#### CANVAS / SURFACE FRONTEND — No Python tests; one JS test exists

| Area | Gap |
|------|-----|
| `canvas/app/src/` (React/tldraw canvas) | **No Python tests.** One JS test: `voice_autolisten_controlflow.test.mjs` proves voice PTT re-arm + barge-in control flow (headless, no real audio). Explicitly notes tldraw, real mic, iOS audio not covered. |
| `surface/app/src/` (React surface — App.tsx, channels, sessions, gallery, rhm, etc.) | **No tests at all** — not Python, not JS. The surface frontend is entirely untested at the unit/integration level. |
| `ui-contract/` | **Not mentioned in any test** |
| `canvas/app` TypeScript/React component logic | **Not tested** — no vitest/jest setup found |

#### DECISIONS/ — Design decisions as data

24 Python files in `decisions/` — these are data/registry files (DECISION = {...} dict records), not executable logic. Not tested as code; the `decisions_acceptance.py` tests the RESOLVER against the schema, but individual decision records have no dedicated validation.

#### FLOWS/ — 7 of 8 have no coverage

`flows/cc_registry_refresh.py` appears in test content (indirect). The other 7 (`drift_radar`, `floor_walk`, `pattern_cluster`, `registry_generation`, `repo_ingest`, `transcript_mine`, `ts_backfill`) have no test coverage. These are background data-pipeline flows.

#### SESSION RECALL SUBSYSTEM — Three key modules uncovered

`session_recall.py`, `session_lens.py`, `session_lineage.py` form Tim's recall substrate (announced 2026-06-14 directive). No acceptance suites yet.

#### OPS/ PROBE + SERVICE SCRIPTS — Largely uncovered

The ops/ scripts that serve/probe live services (`serve_pplx_embed`, `serve_rerank`, `dragnet_*`, `embed_extractions`) are infrastructure scripts with no acceptance coverage. Intentional — they're operational tools, not logic modules.

---

## Surprising / Notable Findings

1. **No pytest skip decorators anywhere.** The convention is "loud skip with a note inside main()" not decorator-based skipping — this is deliberate and architectural.

2. **`suite_health_acceptance.py` is the master gate** — it discovers and runs ALL `*_acceptance.py` suites as subprocesses. Its backstory (3 reds slipped main undetected before it existed) is documented in the file itself. It's slow by design — pre-merge only.

3. **5 files outside the `tests/` directory:** `minds/bind_compose_test.py` (a data binding record, not a test), `canvas/app/voice_autolisten_controlflow.test.mjs` (JS control-flow proof), and `.data/store/ref_history/` entries (corpus data artifacts referencing external test files from `/home/tim/recollection/test/`, which is a different project's test suite entirely — not part of this codebase).

4. **`e2_review_fixes.py` is named "review_fixes" not "acceptance"** — it won't be picked up by the `*_acceptance.py` glob in `suite_health_acceptance.py`. Same for `e2_runtime.py`, `e3_fabric.py`, `e3_integration.py`, `e4_registry.py`, `e5_suite.py`, `e6_governance.py`, `first_purpose.py`, `self_growth.py`, `mcp_use.py`, `walking_skeleton.py`, `wire_adversarial.py` — these 11 non-`_acceptance` files are EXCLUDED from the standing gate.

5. **The surface frontend (`surface/app/`) has zero tests.** The canvas has one JS test for voice control flow only. The React component tree, channel panels, gallery, session views, RHM panel, and decision display are entirely untested at any automated level.

6. **40/234 files (17%) require live services** — the resident 4B model at `:8000` and/or the BGE-M3 embedder at `:8001`. These pass in "offline" mode with a documented skip notice. The actual by-use proof for these capabilities requires the live stack.

7. **`session_recall.py`, `session_lens.py`, `session_lineage.py`** — the session recall substrate Tim directed to be built (2026-06-14) has no acceptance suites yet. Given the emphasis on recall in the MEMORY.md notes, this is a notable gap.

8. **Decisions/ Python files** — 24 design-decision records stored as Python dicts. No structural validation suite exists for the decision record schema itself (only the resolver is tested).

---

## Summary Statistics

- **Total test files in tests/:** 234
- **Framework:** Custom `check()/main()` (dominant), pytest `def test_` (5 files)
- **Total `check()` assertion calls:** ~5,809
- **Total `def test_` functions:** 32
- **Files with live-dep conditional skips:** 40 (17%)
- **Files NOT picked up by `*_acceptance` gate:** 11 (e-series, first_purpose, self_growth, mcp_use, walking_skeleton, wire_adversarial)
- **Source modules with ZERO test coverage:** ~40 (across runtime, ops, flows, voice/ops)
- **Source modules with NO COVERAGE at all (not even indirect):** ~15 critical modules (session_recall/lens/lineage, brain_router, cc_voice, channel_boundary, model_routing, corpus_neighbours/rerank, decision_memory, supabase_principal)
- **Frontend (canvas/surface) coverage:** Near-zero (1 JS headless test for voice PTT logic)
