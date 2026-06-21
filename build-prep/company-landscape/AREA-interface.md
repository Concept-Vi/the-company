---
type: landscape-dragnet
area: interface-layer
covers: mcp_face/ · contracts/ · ui-contract/ · schemas/vi-vision/v1/ · store/
captured: 2026-06-21
status: exhaustive-first-pass
---

# AREA: Interface Layer — Exhaustive Dragnet

Covers: `mcp_face/` (MCP server + tool definitions), `contracts/` (structured-output/IO contracts),
`ui-contract/` (UI contracts corpus), `schemas/vi-vision/v1/` (canonical decision-surface schemas),
`store/` (addressed storage layer).

---

## 1. MCP FACE — `mcp_face/`

### 1.1 Server Architecture (`mcp_face/server.py`, 1115 lines)

**What it is:** The FastMCP server. Single entry-point for every agent-facing tool. Wires the `_LazySuite` proxy pattern, the `build_mcp()` factory, all direct `@mcp.tool()` definitions, and the pkgutil file-discovered tool modules.

**Core patterns:**
- `_LazySuite` proxy — defers `Suite` construction to first attribute access; `build_mcp(suite)` binds a caller-supplied suite before any tool fires. Solves two-Suite-instances problem.
- **MCP-DESIGN-PRINCIPLE** (stated at line 30-36): one parameterized tool per resource with `op` selector, never a flat tool per operation.
- `_guard_tools()` wraps all tools: passes `ValueError`/`KeyError` (teaching errors; deliberate "what did you mean" discipline), re-raises anything else as `INTERNAL ERROR`.
- Floor constraint: NO tool emits `resolve_surfaced`/`dispatch_decision`/launches `claude -p`.

**Direct `@mcp.tool()` definitions in server.py:**

| Tool | Purpose |
|------|---------|
| `object_info` | Object-info for all node types (C5 Part 1) — title/ports/schemas |
| `list_by_type` | List nodes of a given type |
| `list_graphs` | List all graphs in the store |
| `connect` | Connect two nodes (edge creation) — LOCKED posture |
| `set_config` | Set a node's config — LOCKED posture |
| `run_graph` | Execute a graph — LOCKED posture |
| `get_state` | Read a graph's current execution state |
| `get_results` | Read execution results (outputs) for a graph |
| `list_surfaced` | List surfaced items (build-approval inbox; DISTINCT from decisions inbox) |
| `self_change_log` | Read the system's own change log |
| `get_events` | Read events from the event log |
| `now` | Return current timestamp |
| `chat` | Chat/conversation endpoint |
| `inbox` | Session inbox shortcut |
| `capabilities` | List all capabilities (plural listing surface) |
| `cognition_info` | Full cognition-engine introspection (C5 Part 2 — roles/rules/edge_kinds/etc.) |
| `models_for_role` | Which models are eligible for a named role |
| `cognition_inputs` | What inputs a cognition role expects |
| `field_types` | Field-type vocabulary for the cognition engine |
| `list_skills_contexts` | Enumerate available skills and contexts |
| `inspect_address` | Resolve and inspect any address (all 18 schemes) |
| `run_role` | Execute a single cognition role — reuses `runtime.cognition` engine |
| `run_draft` | Execute a draft (a staged role) |
| `run_items` | Execute role over a list of items |
| `run_draft_items` | Execute draft over a list of items |
| `run_reduce` | Reduce a list with a role |
| `reduce_rule_names` | Enumerate available reduce rule names |
| `save_cascade` | Persist a cascade definition |
| `list_cascades` | List all saved cascades |
| `run_cascade` | Execute a saved cascade |
| `preview_turn` | Preview what a cognition turn would do without executing |
| `propose_role` | Propose a new role definition |
| `edit_role` | Edit an existing role |
| `delete_role` | Delete a role |
| `capture` | Capture/ingest a source into the corpus |
| `find_relations` | Find typed relations between addressed items |
| `mark` | Append a mark (finding, annotation) to an address — LOCKED posture |

**Pkgutil-discovered submodules (each exports `register(mcp, suite)`):**

| Module | Tool(s) | Key Notes |
|--------|---------|-----------|
| `tools/sessions.py` | `sessions` | CQRS READ half: op=list/inbox/watch/describe/search/timeline |
| `tools/sessions.py` | `session_post` | CQRS WRITE half: to/message/verb=auto|deliver|wake|consult |
| `tools/channels.py` | `channels` | CQRS READ: op=list/describe/history/edges |
| `tools/channels.py` | `channel_act` | CQRS WRITE: action=create/gather/add/remove/status/post/mode/promote/disperse/archive |
| `tools/corpus.py` | `corpus` | op=query/list/find/read/neighbours/determine; includes jina-v3 rerank |
| `tools/decisions.py` | `decisions` | Pending operator decisions; reads same canonical set as /api/decisions. Never returns ids/codes. |
| `tools/create.py` | `create` | Consolidated 8→1; kind=role/skill/context/projection/mark_type/generation_policy/relation_type/ai_tic |
| `tools/introspection.py` | `capability` | op=list/get/search/describe/snapshot; CapabilityRegistry lazy-populated (~14s binary discovery) |
| `tools/instrument.py` | `project` | Radial universal projection instrument |
| `tools/instrument.py` | `layers` | Multi-layer embedder self-description |
| `tools/session_recall.py` | `session_recall` | op=find/decisions/open_loops/catch_up/timeline/directives/spin_up_points/drift; bridge-free |
| `tools/cc_clone.py` | `cc_clone` | op=clone/msg/onboard/list/end/prepare/resolve; supports ollama provider |
| `tools/cc_gate.py` | `cc_gate` | op=gate/resume/abort/rewind/list/get; observer on native per-step gate |
| `tools/cc_board.py` | `cc_board` | op=file/list/get/transition/types; company noticeboard (request/issue/tip/guide/idea) |
| `tools/cc_attachments.py` | `cc_attachments` | op=attach/detach/list/manifest/types; binds targets to channels |
| `tools/verdict_panels.py` | `panel` | op=list/describe/run; diverse lens-jury panels for reviewing content |
| `tools/runs.py` | `runs` | Run history/management |
| `tools/marks.py` | `marks` | Read-side marks tool (op-based; DISTINCT from `mark` write tool) |
| `tools/dials.py` | `dials` | System dials/settings |
| `tools/flows.py` | `flows` | Flow management |
| `tools/node.py` | `node` | Node CRUD (LOCKED; not run from tool list) |
| `tools/point.py` | `point` | Pointable catalog / radial surface navigation |
| `tools/routines.py` | `routines` | Routine enumeration/management |
| `tools/rule.py` | `rule` | Rule management |
| `tools/context.py` | `context` | Context variable management |
| `tools/ingest.py` | `ingest` | File ingest into corpus |
| `tools/capability.py` (introspection.py) | `capability` | See above |
| `tools/project.py` | (merged into instrument.py) | — |
| `tools/layers.py` | (merged into instrument.py) | — |
| `tools/session_recall.py` | `session_recall` | See above |
| `tools/cc_board.py` | `cc_board` | See above |
| `tools/cc_clone.py` | `cc_clone` | See above |
| `tools/cc_gate.py` | `cc_gate` | See above |
| `tools/cc_attachments.py` | `cc_attachments` | See above |
| `tools/verdict_panels.py` | `panel` | See above |

**Total live tool count:** ~66+ tools (server.py direct: ~35; pkgutil submodules: ~31+).

---

### 1.2 Access Control Registries

#### `mcp_face/remote_exposure.json`

**What it is:** `_schema: remote-posture-registry-v1`. Fail-closed / deny-by-default. Governs the CONNECTOR (untrusted remote clients — Claude Design, etc.). Two-door architecture: this door is the CONNECTOR door, `tool_operator_overlay.json` is the OPERATOR door. **Never widen the connector to widen the operator.**

**Postures:** safe (read, no side effects), design (Face Pipeline, reversible), consent (deferred, writes state), hazard (destructive, never remote), locked (operator-only, never remote).

**Remote-exposed tools (safe/design):** capability, object_info, list_by_type, list_graphs, cognition_info, models_for_role, cognition_inputs, field_types, list_skills_contexts, reduce_rule_names, list_cascades, corpus (list/find/read/query only), instrument, territory (read only), territory_label, chat, operator (rules only), sessions (list/inbox/watch/describe/search/timeline), channels (list/describe/history/edges), cc_board, cc_channel (send only), marks (read ops), claude_design (ingest_bundle/submit_seed/walk_decision)

**Explicitly denied/locked:** node, connect, set_config, run_graph, cc_clone, cc_gate, session_post, resolve_surfaced, approve, dispatch, checkpoint, revert, self_change_log, mark, channel_act

#### `mcp_face/tool_operator_overlay.json`

**What it is:** `_schema: tool-operator-overlay-v1`. Governs the OPERATOR FACE (Tim, trusted, local). PHASE 1 (reads only widened) fully classified. PHASE 2 (consequential writes) deferred until unified-floor attribution goes live.

**PHASE 1 operator_posture=safe:** capabilities, capability, cognition_info, cognition_inputs, field_types, list_skills_contexts, object_info, find_relations, session_recall, layers, models_for_role, sessions, channels, get_state, get_results, now, inspect_address, get_events, marks, list_surfaced, operator, reduce_rule_names, list_cascades, list_graphs, list_by_type, runs, inbox, preview_turn, project, chat (29 tools)

**Deferred (PHASE 2, not yet widened):** run_role/create/capture/save_cascade/ingest/dials/context-compact and the consequential writes. The explicitly_denied set (node/connect/set_config/run_graph/cc_clone/cc_gate/session_post/resolve_surfaced/approve/dispatch/checkpoint/revert/mark/channel_act/self_change_log) NEVER rides this door.

---

### 1.3 Tool Metadata Registry (`mcp_face/tool_meta.json`)

**What it is:** `_schema: tool-meta-registry-v1`. Human-layer registry for operator UI. Fields: `human_name`, `human_description`, `op_labels`, `op_params`, `param_labels`, `enum_sources`. Covers all major tools with friendly labels and op param hints.

**Flagged tools (not run from tool list):** node, connect, set_config, run_graph, cc_clone, cc_gate, session_post, self_change_log, channel_act

---

### 1.4 Module Constitution (`mcp_face/AGENTS.md`)

Key claims:
- Verbs generic over node-type
- `ToolAnnotations` wired to SDK hints for `sessions.py` (F10.1) and `channels.py` (R2)
- Consolidated tool modules export closed `OPS` constant (CONTRACT-FORMAT §9.2)

---

### 1.5 Remote Gateway (`mcp_face/remote.py`)

**What it is:** Remote MCP gateway (Claude Design connector inlet). Localhost/tailnet only (:8772). Two non-negotiable guards: (1) fail-closed deny-by-default; (2) mandatory audit — every remote call logged before execution. Reuses the SAME Suite as the stdio face (no second engine). Dispatches through the FastMCP tool manager.

**Scopes:** SCOPE_READ (`company:design:read` — safe tools only), SCOPE_WRITE (`company:design:write` — safe + design), OPERATOR_SCOPE (`company:operator:*` — NEVER issued remotely).

**Status:** skeleton — posture-filter + audit + auth stubs wired; tool-dispatch proxy pending.

---

## 2. CONTRACTS — `contracts/`

The **spine**: C1–C8 shapes, one file per contract. The seam every module composes against. This imports nothing in the repo; everything imports from here.

### C1 — `contracts/address.py`

**What it is:** Address grammar, Provenance, and address parsers/canonicalizers.

**SCHEMES (18):**
```
"run", "cas", "blob", "vec", "ui", "code", "skill", "context", "session", "cap",
"board", "clone", "mind", "exchange", "file", "project", "vi-vision", "decision"
```

**Provenance fields:** `address`, `content_hash`, `type`, `produced_by`, `inputs`, `agent`, `created_at`, `schema_ver=1`

**Address parsers/helpers:**
- `parse_session_address(addr)` → session id
- `parse_clone_address(addr)` → clone id
- `parse_decision_address(addr)` → frame + id
- `decision_address(frame, id)` → canonicalized `decision://` address
- `parse_composition_step_address(addr)` → composition step
- `run_address(...)`, `scheme(addr)`, `is_cas(addr)`, `is_step_address(addr)`, `is_composition_step_address(addr)`

---

### C2 — `contracts/node_type.py`

**What it is:** NodeType Pydantic model — the contract every node-type file obeys.

**NodeType fields:** `name`, `title`, `category`, `kind`, `extends`, `ports`, `config_schema`, `output_schema`, `render_set`, `inspector_schema`, `actions`, `layout_hints`, `version=1`

**Kind:** `Literal["process", "content", "presentation"]`

**RenderMode:** `Literal["collapsed", "expanded", "full", "workshop"]`

---

### C3 — `contracts/node_record.py`

**What it is:** Node instance, edge, and graph record contracts. SCHEMA_VER=2 (v2 adds optional `Edge.kind`).

**Status:** `Literal["idle", "ready", "running", "ran", "cached", "done", "failed", "surfaced"]`

**EDGE_KINDS:** `{data, injection, gate, fan_in}` — declared vocabulary. `EdgeKind = Literal["data", "injection", "gate", "fan_in"]`. Default: `data`.

**NodeInstance fields:** `id`, `type`, `config`, `position`, `size`, `render_state`, `layer`, `status`, `outputs`

**Edge fields:** `from_node`, `from_port`, `to_node`, `to_port`, `kind=EDGE_KIND_DEFAULT`

**Graph fields:** `id`, `nodes`, `edges`

**ExecNode fields:** `id`, `type`, `inputs`, `config`, `outputs`

---

### C4 — `contracts/resolver.py`

**What it is:** The Resolver Protocol. The ONLY thing that changes filesystem → Supabase. `store/fs_store.py` implements it.

**Protocol methods:**
- `put_content(data)` → str (cas://)
- `get_content(cas)` → Any
- `exists(cas)` → bool
- `set_ref(logical, cas)` → None (run://)
- `head(logical)` → str | None
- `write_provenance(prov)` → None
- `provenance(address)` → Provenance | None
- `lineage(address)` → list[str] (walk inputs toward source)
- `memo_get(sig)` → str | None
- `memo_set(sig, cas)` → None

---

### C5 Part 1 — `contracts/object_info.py`

**What it is:** ObjectInfo serialization. SCHEMA_VER=1. Converts NodeType entries to operator-facing shape.

**ObjectInfoEntry.from_node_type(nt)** — factory from a NodeType.

**build_object_info(node_types)** returns: `{name: {title, category, kind, ports, config_schema, output_schema, render_set, inspector_schema, actions, version}}`

---

### C5 Part 2 — `contracts/cognition_info.py`

**What it is:** CognitionInfo serialization. SCHEMA_VER=2.

**COGNITION_EVENT_KINDS (6):** `cognition.turn.start`, `cognition.role.fire`, `cognition.role.ran`, `cognition.inject`, `cognition.part`, `cognition.turn.done`

**build_cognition_info(roles, rules, edge_kinds, thought_shapes, activation_contexts, rule_ops, destination_kinds, casts, node_states, projections, lifters, mark_types, generation_policies, relation_types, ai_tics, forms)** returns serialized dict with: `schema_ver`, `roles`, `rules`, `edge_kinds`, `thought_shapes`, `activation_contexts`, `rule_ops`, `destination_kinds`, `casts`, `node_states`, `event_kinds`, `projections`, `spaces`, `lifters`, `mark_types`, `generation_policies`, `relation_types`, `ai_tics`, `forms`

---

### C6 — `contracts/ui_info.py`

**What it is:** UI address/component registry. C1. SCHEMA_VER=2.

**UiComponentEntry fields:** `ref`, `kind`, `title`, `capabilities`, `dom_handle`, `camera_ref`, `version=1`

**Capabilities fields:** `pointable`, `spotlit`, `presentable`, `openable`, `drivenReadOnly`

**ADDRESS_KINDS:** `("chrome", "field", "canvas", "panel", "ext")`

**UnionAddressRecord fields:** `address`, `kind`, `region`, `capabilities`, `represents`, `code`, `states`, `tier`, `title`, `howto`
- `from_corpus()` classmethod — from corpus element-form ui:// records
- `from_live()` classmethod — from live kind-form ui:// entries

**Helpers:** `parse_ui_address()`, `normalize_capabilities()`, `validate_address_record()`, `conform_corpus()`, `conform_live()`

---

### C7 — `contracts/tools.py`

**What it is:** Tool surface contract. SCHEMA_VER=1. Defines ToolAnnotations, ToolSpec, and the TOOLS dict.

**ToolAnnotations(readonly, destructive, idempotent)** — coherence check: readonly∧destructive raises.

**ToolSpec(name, params_model, result_model, summary, annotations)**

**TOOLS dict (25 contract-layer verbs):**
GetTypeGraph, ListByType, ObjectInfo, Search, ListSources, RegisterSource, SurveySource, ListGraphs, CreateNode, Connect, SetConfig, DeleteNode, ValidateGraph, RunGraph, WatchRun, PauseRun, Retry, BranchRun, Reprioritise, GetResults, GetTrace, Feedback, ListSurfaced, ResolveSurfaced

NOTE: These are the CONTRACT-layer verbs (original design). The live FastMCP server has grown well beyond this (66+ tools). The contracts/tools.py TOOLS dict represents the original architectural contract; it has NOT been updated to match the live tool count. **GAP: contract-layer and live server diverged; TOOLS dict is stale/incomplete.**

---

### C8 — `contracts/bridge_msgs.py`

**What it is:** Bridge message contracts. SCHEMA_VER=1.

**ActionRequest fields:** `id`, `verb`, `params`, `schema_ver=1`

**ActionResponse fields:** `id`, `ok`, `result`, `error`, `schema_ver=1`

**NodeState fields:** `id`, `type`, `status`, `address`, `content_hash`, `output`, `config`, `schema_ver=1`

**GraphState fields:** `id`, `nodes`, `edges`, `schema_ver=1`

**Helpers:** `ok(id, result)`, `err(id, message)`

---

### C-CAP — `contracts/capability_entry.py`

**What it is:** CapabilityEntry contract. Mirror-Registry System LANE-CONTRACTS.

**EntryKind (13):** `flag`, `slash_command`, `subcommand`, `tool`, `mcp_tool`, `setting`, `permission`, `hook_event`, `sdk_event`, `enum_value`, `mcp_server`, `skill`, `plugin`, `agent`

**CapabilityEntry fields:** `id` (kind/name with -- prefix for flags), `kind`, `name`, `aliases`, `description`, `takes_value`, `value_type`, `choices`, `default_value`, `visible`, `posture`, `posture_rule`, `axis`, `assembler_kind`, `locked_reason`, `args_schema`, `input_schema`, `server_name`, `setting_path`, `setting_type`, `hook_trigger`, `platform_id`, `source`, `source_url`, `fetched_at`, `status`, `retired_in_version`, `discovered_at`, `raw_extra`, `version=1`, `verbs`

**CapabilityVerbs fields:** `readable`, `searchable`, `projectable`, `configurable`

---

### C-PLAT — `contracts/platform_entry.py`

**What it is:** PlatformEntry contract + all nested sub-models. Mirror-Registry System LANE-CONTRACTS.

**PlatformEntry fields:** `id`, `display_name`, `executable_locator`, `invocation_kind`, `discovery_sources`, `version_source`, `signal_sets`, `consumer_reserved_invariants`, `invocation_binding`, `permission_model`, `tool_surface`, `tool_server_wiring`, `projection_targets`, `resource_governance`, `version=1`

**Sub-models and their key fields:**

| Sub-model | Key fields |
|-----------|-----------|
| ExecutableLocator | name, env_override, which_fallback, known_paths |
| DiscoverySource | type (DiscoverySourceType), command, format (DiscoverySourceFormat), floor_guard, field_kind_map, metadata_fields |
| SignalSets | transport_invariants (DERIVED, never hand-typed), hazard_name_vocabulary, capability_axes |
| ConsumerReservedInvariants | session_mode_flag (-p), injection_protocol, output_protocol, verbosity_flag, body_key_overrides |
| VersionSource | command, strip_suffix, format |
| InvocationBinding | invocation_kind, inject_transport (InjectTransport typed), output_protocol_format (typed), session_state_machine |
| PermissionModel | flag, default, values, hazard_flag, profiles |
| ToolSurface | allow_flag, deny_flag, floor_tool_set, capability_to_tool_grant, rail_boundary_set |
| ToolServerWiring | config_flag, config_format, server_entry_shape |
| ResourceGovernance | concurrency_cap, turn_timeout, init_wait |

**F-FIX-12 Typed Literals (closed sets — novel value FAILS LOUD):**
- `InjectTransport`: `"stdin-ndjson"`
- `OutputProtocolFormat`: `"stream-json"`
- `DiscoverySourceFormat`: `"commander-options-text"`, `"json-init"`
- `DiscoverySourceType`: `"cli-help"`, `"stream-init"`, `"rest-openapi"` (unbuilt), `"mcp-list-tools"` (unbuilt), `"graphql-introspect"` (unbuilt)
- `InvocationKind`: `"subprocess"`, `"rest"` (unbuilt), `"graphql"` (unbuilt), `"mcp"` (unbuilt), `"library"` (unbuilt)

---

### `contracts/shapes.py`

**What it is:** Compat shim re-exporting from `contracts/node_record`. Note: "Prefer importing from contracts.node_record directly in new code." STALE/LEGACY: exists only for backward compatibility.

---

## 3. UI CONTRACT — `ui-contract/`

### 3.1 Format and Architecture (`CONTRACT-FORMAT.md`)

**What it is:** The FROZEN (at P0.3) format spec for the purpose-free, machine-checked, embedding-ready contract a UI-building AI consumes instead of reading the repo. Resource-oriented spine (defeated event-sourced and capability-verbs lenses). Grafts from both other lenses incorporated.

**Key rules:**
- One file per resource noun, kebab-case, in `resources/`
- Uniform op verbs: `list · get · create · update · delete · act · watch · search` — nothing else
- Field table with `volatile?` + `changed-by (event)` + `address? → resource` + `reality` columns
- Machine-checked (validator V1–V26 enforces schema, refs, event chains)
- `coverage.json` (contracted vs demonstrated), `reality.json` (live snapshot), `load.jsonl`, `drops.jsonl` — all GENERATED
- No-versioning law: canonical docs update in place, never append/version

**Entry format key fields (frontmatter):**
`type: contract-entry`, `resource:`, `summary:`, `schemes:`, `status: planned|building|live|broken|retired`, `relates-to:`

---

### 3.2 Resource Files (`ui-contract/resources/`, 31 files)

All resource noun files in the corpus:

`agent-team.md`, `auth.md`, `checkpoint.md`, `ci.md`, `claude-memory.md`, `code-intel.md`, `code-review.md`, `computer-use.md`, `context-window.md`, `cost-usage.md`, `diagnostics.md`, `events.md`, `extensibility-patterns.md`, `extensions.md`, `fabric-config.md`, `git.md`, `headless-control.md`, `hooks.md`, `knowledge-corpus.md`, `mcp-servers.md`, `model.md`, `output-style.md`, `permission.md`, `platform.md`, `remote.md`, `routines.md`, `session-message.md`, `session.md`, `settings.md`, `surfaces.md`, `transcript.md`, `voice.md`, `workflows.md`

**Coverage breadth:** Session Fabric (session/session-message/transcript/events), platform (platform/permission/model), extensibility (extensions/hooks/mcp-servers/extensibility-patterns), operational (ci/git/code-review/code-intel/diagnostics), user surfaces (surfaces/output-style/voice).

---

### 3.3 Tooling (`ui-contract/tools/`)

- `validate_contract.py` — validator rules V1–V26; reality join; repo test, fails loud
- `coverage.py` — builds `coverage/coverage.json` from op declarations
- (extract_reality.py, rename.py also present)

---

### 3.4 Atlas (`ui-contract/atlas/`)

- `FEATURE-ATLAS.md` — 35 classes (CC-01…CC-35) with affordances (CC-05.1 etc.) — coverage grain is the affordance
- `OUT-OF-SCOPE.md` — affordance-grain exclusions with reason/decided-by/date
- `INVENTORY-EXCLUSIONS.md` — endpoint-grain exclusions (the disposable harness routes) with reasons

---

### 3.5 Coverage (`ui-contract/coverage/`)

- `coverage.json` — GENERATED two-layer map (contracted vs demonstrated)
- `reality.json` — GENERATED live snapshot of registries + bind config + tool inputSchemas, timestamped
- `load.jsonl` — harness file reads + substrate hits log
- `drops.jsonl` — reached-for-but-missing ledger → gap adoption (F10.1)

---

### 3.6 Journeys and Index

- `journeys/` — canonical cross-resource flows (e.g. `message-and-read-reply.md`, `render-a-conversation-live.md`)
- `TASKS.md` — GENERATED task index: intent phrase/alias → (op, params) rows
- `INDEX.md` — GENERATED: resource table + SCHEMES table + journey list
- `CONVENTIONS.md` — uniform op verbs, error envelope, cursor law, address grammar, purpose-free vocabulary
- `TRANSPORTS.md` — transport ids → protocol/base URL/auth/caller identity model per transport

---

## 4. SCHEMAS — `schemas/vi-vision/v1/`

**What it is:** The company's canonical decision-surface + render-type (archetype) contracts. Migrated from vi-visual-dev factory island (islands-join). 14 files. Addressed as `vi-vision://global/schemas/v1/<name>`.

### 4.1 `decision.schema.json`

**Title:** Vi Vision Decision. The DECISION type.

**Required fields:** `id`, `meaning`, `options`, `subtype`

**All fields:**

| Field | Type | Notes |
|-------|------|-------|
| id | string | Stable; leaf of `decision://<frame>/<id>` |
| address | string | Optional: the thing this decision decides ON (any vi address) |
| meaning | string | The decision in HUMAN terms (Tim's words). Never a machine name. |
| options | array of option | The choices (option.schema.json). minItems 1. |
| explanation_source | string | Address grounding the RHM's live explanation. HOLE-2-safe provenance pointer. Absent if no verbatim-match. |
| scope | enum | global/project/user/session. Default global. |
| channel | string | Optional: channel address this decision is attached to (FACE-2 operator-stack). |
| subtype | string | decision_subtypes registry id (authorize/trade-off/theorem-fork/cross-lane/…). Resolves card_variant + explanation_policy + required_elements. |
| legibility | $ref legibility.schema.json | The meaning-fields (name/is/fills/why). |
| dimensions | object | Named trade-off axes: {id: {label, meaning?}}. Required for a data-bound device to render. |
| device | object | Data-bound visual device: {type (bars/matrix/hub/duo/taxonomy), encodes: {channel → data-path}}. Decoration ban: device with no real data MUST NOT render. |
| steps | array of string | Flow-parent role: ORDERED child decision addresses. Present → sequence render. |
| flow_intro | string | Flow-parent framing line. Only on flow parents. |
| step_index | integer | Flow-step 0-based position. Only on flow children. |
| bridge | string | Flow-step connecting line. Only on flow children. |

**State is NOT authored** — resolved from a `decision_take` mark on the address (registry-is-truth).

---

### 4.2 `option.schema.json`

**Title:** Vi Vision Decision Option. One choice within a decision.

**Required:** `label`

| Field | Type | Notes |
|-------|------|-------|
| label | string | The choice in HUMAN terms (Tim's words). The decided_value the take records. |
| description | string | Optional fuller explanation. RENDERS AS PROSE (not inside chip). |
| implication | string | Consequence of choosing. RENDERS AS TERSE MONO CHIP. |
| recommended | boolean | Whether this is the recommended choice. Default false. |
| dimensions | object | This option's VALUES on the decision's named trade-off axes. {axis_id → number or string}. Real per-option values only — no hardcoded render values. |

---

### 4.3 `legibility.schema.json`

**Title:** Vi Vision Legibility (meaning-fields). Reusable field-set for any addressable type.

**Required:** `name`, `is`

| Field | Type | Notes |
|-------|------|-------|
| name | string | THIS thing's human name. Never a machine id. |
| is | string | What KIND of thing it is (what-kind one-liner). |
| fills | string | Optional: what fills it / what it accepts. |
| why | string | Optional: why you'd look at it / what it's for. |

---

### 4.4 `archetype.schema.json`

**Title:** Vi Vision Archetype (render-type). The general RENDER-TYPE.

**Required:** `id`, `archetype_of`, `render_kind`, `slot_map`

| Field | Type | Notes |
|-------|------|-------|
| id | string | Stable archetype id. Convention: `archetype.<name>`. |
| archetype_of | string | The TYPE this archetype renders (e.g. 'decision', 'session'). |
| render_kind | string | Surface form + host lifecycle key. Catalog: slide/sequence/graph/diagram/selector/instrument/spatial-material/unit/lanes/zones. |
| slot_map | object | Render SLOT → SOURCE bindings. Key = slot name (renderer-owned); value = field path or `resolve:<x>` directive. |
| legibility_fields | array | Which legibility fields the surface leads with. Default `["name","is"]`. |
| take | object | Optional interactive write: {from_slot, writes}. Absent = read-only. |
| language | object | Optional: references to specific DNA language elements {grammar, layout, voice, motion, tokens}. Absent = inherit active DNA language. Fail-loud if referenced element doesn't resolve. |

**SLOT-SHAPE LAW:** every slot_map source resolves to the slot's DECLARED shape in the adapter/host BEFORE render. Renderer accepts only declared shape, never raw data.

---

### 4.5 `decision-card.schema.json`

**Title:** Vi Vision Decision-Card Archetype. The FIRST archetype instance.

**Required:** `id`, `archetype_of`, `render_kind`, `slot_map`

**archetype_of:** const `"decision"`. **render_kind:** default `"slide"`.

**card_kinds** (three roles within ONE decision):
- `present`: slots showing what's being decided — default `["question","kicker","kind","shape"]`
- `explain`: the RHM's grounded explanation — default `["explanation"]`
- `choose`: decide-in-surface — default `["options","state","decided"]`

**take:** default `{from_slot: "options", writes: "decision_take"}`

**Hard gate:** at 390px (Tim's phone), decision + options visible together without scrolling — VERIFIED IN THE OPERATOR MODAL.

---

### 4.6 `graph.schema.json`

**Title:** Vi Vision Graph Archetype. Extends `archetype.schema.json`. render_kind=`"graph"`.

**Required slot_map keys:** `nodes` (the node-set source), `edges` (LOCKED with DNA: explicit slot — field 'edges' array `{from,to,kind?}` OR `resolve:relations` host-resolved to that array before render).

**Design:** REAL resolved relations (substrate edges via find_relations), NOT authored. Edge-binding LOCKED: renderer always receives resolved edges from this explicit slot — never resolves from node data itself.

---

### 4.7 `diagram.schema.json`

**Title:** Vi Vision Diagram Archetype. Extends `archetype.schema.json`. render_kind=`"diagram"`.

**Required slot_map keys:** `nodes`, `edges` (authored relations — same `{from,to,kind?}` array binding as graph, LOCKED with DNA). Optional: `flow`.

**Design:** AUTHORED relations (flow/sequence/hierarchy). Same edge-binding shape as graph — graph=substrate-resolved, diagram=authored, SAME binding.

---

### 4.8 `selector.schema.json`

**Title:** Vi Vision Selector Archetype. Extends `archetype.schema.json`. render_kind=`"selector"`.

**Required slot_map keys:** `options` (choices source), `current` (current selection source). Optional: `groups`.

---

### 4.9 `instrument.schema.json`

**Title:** Vi Vision Instrument Archetype. Extends `archetype.schema.json`. render_kind=`"instrument"`.

**Required slot_map keys:** `reading` (live reading source), `controls` (dials/verb-fan source). Optional: `state`.

**Design:** LIVE reading + STEERING surface. Controls drive re-resolve. Consequential drives are GATED (floor).

---

### 4.10 `spatial-material.schema.json`

**Title:** Vi Vision Spatial-Material Archetype. Extends `archetype.schema.json`. render_kind=`"spatial-material"`.

**Required slot_map keys:** `materials` (substance source — socket-materials: animation/glow/effect/palette). Optional: `reveals`, `asset`.

**Design:** Interactive visual/spatial substance — DNA artefact organisms + socket-materials. Grounded in DNA's ARTEFACT ORGANISM family (built 2026-06-21).

---

### 4.11 `lanes.schema.json`

**Title:** Vi Vision Lanes Archetype. Extends `archetype.schema.json`. render_kind=`"lanes"`.

**Required slot_map keys:** `lanes` (entity per lane), `marks` (event marks source). Optional: `axis`, `now`.

**Design:** TIME × ENTITY as horizontal lanes with event marks. FACE-1 surface archetype. Honest empty-state (no-silent-failure when no timeline yet).

---

### 4.12 `zones.schema.json`

**Title:** Vi Vision Zones Archetype. Extends `archetype.schema.json`. render_kind=`"zones"`.

**Required slot_map keys:** `zones` (sections as spatial regions). Optional: `index`.

**Design:** Structured thing's SECTIONS as navigable spatial regions (almanac renderer). Anti-markdown-wall archetype. FACE-1 surface. Bound to live /api/board.

---

### 4.13 `session-card.schema.json`

**Title:** Vi Vision Session-Card Archetype. Extends `archetype.schema.json`. render_kind=`"unit"`.

**archetype_of:** const `"session"`.

**Required slot_map keys:** `header` (legibility.name + lane), `focus` (current focus from /api/sessions), `recall` (`resolve:recall` — session_recall). Optional: `kind`, `state`, `transcript`, `actions`.

**Design:** FACE-1 unit/detail surface for one session. Sibling of decision-card. First FACE-1 render proof. Live data from /api/sessions + session_recall + supervisor verbs.

---

### 4.14 `AGENTS.md`

Module constitution for the schemas directory. Lists all canonical schemas; explains migration from vi-visual-dev factory island. Notes `recommended_label` is a DERIVED field on the resolved record (fork 0273792), not authored here.

**GAP noted:** Migration still in progress — vi-visual-dev copies are deprecated island mirrors. The factory-composition schemas (atom/molecule/organism/template/pack/mode/variant/slot/tokens/animation/icon/layout/behavior) stay in vi-visual-dev — they are the factory's own, not company-face contracts.

---

## 5. STORE — `store/`

### 5.1 Store Architecture (`store/AGENTS.md`)

**What it is:** The addressed store + resolver. Implements C1 (grammar/provenance) + C4 (Resolver Protocol). Filesystem-first; Supabase later. Everything durable flows through here by address.

**Guarantees:**
- `cas://` is IMMUTABLE — never mutated, never lost
- Lives on ext4 (`~/…`), NEVER `/mnt/c`
- Every write records provenance (`inputs[]` → lineage to source)
- Cross-process safe (S4): bridge + MCP face = two processes on ONE store dir; `fcntl` OS advisory locks layered with threading RLocks (`graph_lock(gid)`, `dispatch_lock(seq)`) — outermost-only flock via depth-count so re-entrant calls don't self-deadlock
- Hot writes fsync'd before atomic rename (crash-durable)
- Chat turns carry provenance: `source` (operator | twin) + `grade` (gold | working); twin's training signal filtered to operator-gold — echo-guard against model-collapse

**Space-keyed vectors (GROUP L):** A source item embeds in MANY projection spaces. Address shape: `vec://<item>#space=<projection>` via `FsStore.space_address()`. Default/unspaced = bare source address (back-compat). Per-space filter is a clean field match (`space`, `source` explicit record fields); a spaced entry NEVER leaks into the default corpus.

**Marks store (GROUP M):** A MARK generalizes the coherence finding record along two axes: (1) a TARGET (claim/span/address); (2) a `mark_type` (opaque id from mark-types registry). Lives in `marks.jsonl` sibling leaf. NEVER in `findings.jsonl` (would inflate burn-down). Fail-loud: a mark with missing/empty `target` or `mark_type` is REFUSED.

**Agent-session REGISTRY (Session Fabric F1.2):** `save_agent_session`/`load_agent_session`/`list_agent_sessions`/`agent_session_mtimes` over `agent_sessions/*.json`. Record (open, schema-additive): `{id, name, cwd, state, started, last_activity, title, title_source, summarizer, envelope, schema_ver}`. Fail-loud: missing/empty `id` REFUSED.

**Agent-session MAILBOX (Session Fabric §C):** `agent_sessions/mail.jsonl`. Append-only open-record `{seq, id, ts, to, from, verb, cas, thread, …}`. Cross-process seq uniqueness via `graph_lock("agent_sessions:mail")`. Consumption = per-consumer cursor refs (`set_agent_mail_cursor`), NEVER status-field RMW. Regression REFUSED.

---

### 5.2 FilesystemResolver (`store/fs_store.py`)

**What it is:** Implements C4 Resolver Protocol. Cross-process + in-process locking. Content-addressed immutable objects, mutable refs, typed provenance, lineage walk, memo index.

**Portability constraint:** `fcntl`/lockfile/fsync references MUST NOT leak outside this module. A Supabase backend implements the same methods with backend-native concurrency/durability. The engine calls `store.graph_lock(gid)` and never knows the backend.

**`_CrossProcessLock`:** Re-entrant lock serializing both threads AND processes. Composition: threading RLock (in-process re-entrancy) + `fcntl.flock` on outermost acquire only (depth tracked per-thread). Depth-count prevents self-deadlock on re-entrant calls.

**`_fsync_path(path)`:** fsync a directory entry for crash-durability. Best-effort (some filesystems refuse directory fd fsync; file-content fsync is the primary guarantee).

---

### 5.3 Vector Index (`store/vector_index.py`)

**What it is:** X12 — persisted vector index build + query path.

**What it solves:** repo outgrew whole-repo context-stuffing (codebase node fails loud at 600k; repo is 865k). X12 persists the index; retrieval reads it instead of recomputing.

**Substrate:** `vectors/` namespace in the addressed store (sibling of objects/refs). Same ext4 store, no new DB.

**`build_index(store, corpus, *, embed_fn, dim, model, base_url, space, emb)`:**
- INCREMENTAL: re-embeds only NEW or content_hash-CHANGED items
- Per-entry: `(address, text) → content_hash → embed if changed → store.put_vector(address, vector, content_hash, space, source)`
- Degrade-with-warning on embed failure (endpoint down): LOUD warning event, NO fabricated vectors, does NOT crash
- Space-keyed: `space=None` = default/unspaced; named space = composed address `vec://<item>#space=<projection>`

**`content_hash(text)`:** blake2b, digest_size=16. Mirrors `fs_store._hash` for consistency.

**`_default_embed(transport, inputs, model, dim)`:** Exact fabric path `nodes/embed.py` uses. Test-injectable seam.

**DEGRADE constraint:** when embed raises (endpoint unreachable), NO fabricated vectors, NO fallback to chat endpoint, NO silent zero-vector. Query over empty index returns empty + honest note.

---

## 6. NOTABLE GAPS, SURPRISES, AND INCOMPLETE ITEMS

### 6.1 contracts/tools.py TOOLS dict — STALE

**Gap:** The C7 TOOLS dict has 25 verbs representing the original design contract. The live FastMCP server has 66+ tools. No mechanism maintains the TOOLS dict against the live tool inventory. The TOOLS dict appears to be an orphaned/stale artifact — the live server does NOT reference it for its tool registration.

### 6.2 remote.py — Skeleton Status

**Incomplete:** `mcp_face/remote.py` is explicitly a skeleton. The tool-dispatch proxy to the stdio face's registered tools is pending ("pending oracle reply on reuse shape"). The posture-filter + audit + auth stubs are wired but the actual dispatching is not complete. The gateway is described as localhost-only and public deploy is GATED on security verify.

### 6.3 contracts/shapes.py — Legacy Shim

**Stale/legacy:** `contracts/shapes.py` is a compat shim re-exporting from `contracts/node_record`. The module-level comment explicitly says "Prefer importing from contracts.node_record directly in new code." This file exists only for backward compat.

### 6.4 schemas/vi-vision/v1/ Migration — In Progress

**Incomplete:** The canonical migration of schemas from vi-visual-dev to company is in progress but not complete. The vi-visual-dev copies are the deprecated island mirrors. Fork's `decision_registry.py` is not yet wired to this in-company copy. Until migration completes there is a dual-source ambiguity.

### 6.5 tool_operator_overlay.json PHASE 2 — Pending

**Deferred:** Consequential writes (run_role/create/capture/save_cascade/ingest/dials/context-compact) are NOT widened yet. They wait for the unified-floor attribution (#1b operator-token) to go live, then PHASE 2 classifies them deliberately. 37 tools remain deny-by-default for the operator until PHASE 2 lands.

### 6.6 decision.schema.json — `channel` field multi-channel note

**Flagged in schema (FACE-2):** Multi-channel placement of a decision would become an edge, NOT a list on the row — described as flagged but not built. Current: one decision, one home channel.

### 6.7 archetype.schema.json — DNA `language` field addressing scheme not yet typed

**Open:** The `language.*` field values reference DNA rule-book elements, but the exact addressing scheme is not yet typed/validated (pending DNA confirmation). The schema notes this will be typed once DNA confirms its addressing — a typed $ref/pattern/registry to the DNA rule-books.

### 6.8 Contracts C6 `ui_info.py` — Context Variable contract not shown

**Gap in my coverage:** The contracts AGENTS.md lists C6 as context-variable, but `ui_info.py` seems to be the UI address contract. There may be a separate C6 context-variable file not read in this pass. The naming split warrants verification.

### 6.9 ui-contract/resources/ — Not individually read

**Coverage gap:** Individual resource .md files (31 files) were listed but not read in this pass. Content of each resource entry (its fields, state model, ops) was not captured exhaustively. The CONTRACT-FORMAT.md format is documented above but the actual contracted surfaces are not individually enumerated.

### 6.10 InvocationKind — 4 of 5 adapters unbuilt

**Structural gap:** Only `"subprocess"` adapter is built. `"rest"`, `"graphql"`, `"mcp"`, `"library"` are declared Literals but their adapters don't exist yet. A platform registering any of these will FAIL LOUD at PlatformEntry.model_validate() time — this is the deliberate gap-surface path, not a silent failure.

### 6.11 store/fs_store.py — Only first 100 lines read

**Coverage gap:** The full FsStore implementation was not read past line 100 (the _CrossProcessLock and _fsync_path section). The full method inventory (put_content/get_content/set_ref/head/write_provenance/provenance/lineage/memo_get/memo_set + all the higher-level domain methods: save_graph/save_surfaced/save_session/append_event/append_chat/put_vector/get_vector/index_addresses/index_corpus/append_mark/marks_for/marks_by_type/all_marks/save_agent_session/load_agent_session/list_agent_sessions/agent_session_mtimes/append_agent_mail/agent_mail_since/agent_mail_cursor/set_agent_mail_cursor) was reconstructed from the AGENTS.md and vector_index.py but not verified directly from the implementation.

---

## 7. CROSS-REFERENCES

- **`mcp_face/server.py` ↔ `contracts/tools.py`**: contracts/tools.py TOOLS dict is the ORIGINAL architectural contract; server.py's live tool set has grown significantly beyond it.
- **`mcp_face/remote.py` ↔ `mcp_face/remote_exposure.json`**: remote.py is the gateway; remote_exposure.json is its allow-list.
- **`mcp_face/tools/sessions.py` ↔ `contracts/tools.py:ToolAnnotations`**: sessions.py wires SDK-level ToolAnnotations (F10.1) directly from contracts.
- **`store/vector_index.py` ↔ `store/fs_store.py`**: vector_index.py ORCHESTRATES over fs_store.py; fs_store.py is the dumb substrate (never calls models); vector_index.py is the only layer calling the model fabric.
- **`contracts/address.py:SCHEMES` ↔ `mcp_face/tools/corpus.py`**: corpus op='read' handles extraction://, code://, and run:// addresses; all 18 SCHEMES are resolvable through inspect_address.
- **`schemas/vi-vision/v1/decision.schema.json` ↔ `mcp_face/tools/decisions.py`**: decisions tool reads from the same canonical set as /api/decisions (runtime/decision_registry); the schemas are the contract the registry validates against.
- **`contracts/capability_entry.py` ↔ `mcp_face/tools/introspection.py`**: introspection.py's capability tool lazy-populates the CapabilityRegistry using CapabilityEntry contract; binary discovery ~14s, cached.
- **`contracts/platform_entry.py` ↔ `contracts/capability_entry.py`**: PlatformEntry is the platform-level registry; CapabilityEntry is per-capability; `platform_id` FK links them.
- **`ui-contract/` ↔ `contracts/address.py`**: ui-contract/CONVENTIONS.md uses the address grammar from C1; the SCHEMES table in INDEX.md is sourced from contracts/address.py:SCHEMES.
- **`store/AGENTS.md:echo-guard` ↔ `append_chat`**: every chat-persist path MUST tag `source` or the echo-guard silently fails open; this is a cross-module behavioral constraint spanning store + any layer that calls append_chat.
