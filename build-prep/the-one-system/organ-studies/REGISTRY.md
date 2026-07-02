# ORGAN REBUILD STUDY — THE GENERATIVE TYPE REGISTRY

*(④ the-one-system · fusion session, 2026-07-02. [O]=Observed, [I]=Inferred, [R]=reported-not-reverified.)*

## (1) EACH SIDE

### SIDE A — three cloud articulations of one latent organ

**A1. universal_types + cascade_registry + generate_all_from_type — deployed, working**
- universal_types (schema.sql L33505; 16 live rows): type_name, display_name, data_schema jsonb NOT NULL, generates text[] NOT NULL, + per-target spec columns tool_spec/component_spec/notice_board_spec/relationship_spec/behavior_spec/extractor_spec/embedding_spec/template_spec [O].
- cascade_registry (L33959; 10 enabled): cascade_name, target_system, handler_function, requires_fields[], enabled, priority. Live, priority-ordered: mcp_tools(10) notice_board_sync(20) theme(30) accessibility(40) agent_decorator(50) capability(60) embedding_flag(70) validation_schema(80) queue_routing(90) address_template(100) [O].
- generate_all_from_type (L13739): loops enabled cascades by priority, EXECUTE per handler, **per-handler EXCEPTION isolation** (error → {"error": msg}, loop continues) [O].
- Fan-out per handler [O]: mcp tools (create_<t>/list_<t>s → mcp_tool_registry, source_type='universal_type', upsert) · sync_type_to_registries (→ notice_board_types; → component_registry with generated card template; → behavior_bindings with honest `not_connected` reasons — rule-8 discipline appearing spontaneously) · theme/accessibility (skip if no component — implicit ordering resolved by priority) · agent_decorator (@<t> — but hardcoded agent UUID+provider [O], place-not-derive) · capability (project.manage_<t>s) · embedding_flag/validation/queue_routing/address_template (ltree vi.{user}.<t>.{id}).
- Demonstrated [O, cvi_mine]: mcp_tool_registry **30 rows source_type='universal_type'**; agent_decorators 20; capabilities 16; address/queue/validation 4 each — real but **unevenly re-run**. 316/319 board-type match is [R].
- The 16 rows' shape [O]: all generate ⊇ {mcp_tool, notice_board_type, ui_component}; **tool_spec/embedding_spec/extractor_spec/template_spec NULL on all 16**; 7 rows have data_schema={"type":"object"} only — **the column vocabulary far richer than any row used**.
- REACHING: one INSERT = a complete citizen; and the fan-out itself registered (enable/disable/priority/add-a-handler-row).

**A2. all_type_registries — the union view (L33561) [O]**
Five UNION arms: universal_types (real generates) + notice_board_types/resource_schemas/content_types/flow_types each with a **constant fake generates**. IS: an admission type registries had proliferated; a read-only attempt to see them as one. REACHING: the registry of registries. PARTIAL: harmonizes only the header, fabricates the facts it unifies, read-only.

**A3. The vi_* facade — designed, never deployed [O: 0 functions in snapshot/cvi_mine; only the vi_mcp_tool_registry table]**
From migrations 20260221 v2 (1494 lines) + compose_domain (684): vi_mcp_tool_registry = row-per-tool with function_name+function_params_map generic routing ("Adding a tool = INSERT a row. No code deployment"), generated_from/auto_generated provenance, transitions/examples/help_text **self-teaching columns**, lifecycle, permissions. Six verbs (orient/discover/operate/query/generate/connect), every branch returning a `_next` array — the conversation teaches itself forward. vi_generate reads BOTH universal_types AND vi_coder.engine_schemas (richer: cascade_behavior/trigger_reactions/ui_hints), generates tools that route through the facade itself, upserts, then only *reports* ui/behaviors/graph specs. vi_type_catalog = a bridge VIEW with honest NULLs. REACHING: the registry as a self-teaching, self-extending conversational surface.

### SIDE B — the engine

- **File-per-row registries** at repo root [O]: roles/(38) projections/(13) mark_types/(14) generation_policies/ decision_subtypes/ ai_tics/ forms/ flows/ relation_types/ item_types/ source_types/ board_edges/ … Each row one .py exporting one dict; **id MUST equal file stem**; per-dir AGENTS.md constitutions; malformed rows FAIL LOUD at discovery.
- **C2 node-types** (nodes/<name>.py): VERSION/KIND/PORTS/CONFIG/OUTPUT_SCHEMA/run(); discovery by file-path never import; rediscover() clears+rescans — **a deleted file un-registers** [O, runtime/registry.py:55].
- **The type-graph**: NodeRegistry.produces(port_type) → Suite.list_by_type [O, suite.py:1762].
- **Suite.capabilities()** (suite.py:1496): ONE snapshot of what exists; api_verbs projected from BRIDGE_ROUTES; "fed into every authoring prompt … so the correct values are the easy path and nothing is guessed" — rule 8 as mechanism [O].
- **RHM_VERB_SPECS** (suite.py:4708): 11 VerbSpec rows; verbs/desc/class + native tool schemas all derive — "no parallel literal to drift" [O].
- **contracts/cognition_info.py**: serializes ALL registries so the UI renders generically; a registry key disagreeing with the row's id RAISES [O].
- **The registration act is a tool**: mcp_face/tools/create.py — ONE create(kind, spec); kind enum derives at server start from live Suite.create_<kind> methods; each create = render → gate-in-tempdir → write → git commit → rediscover, with the drift-home AGENTS.md reflected in the same commit [O].
- Drift enforcement: refresh_self_description + tests/drift_acceptance.py fail loud on unreflected capability [O].
- REACHING: the system's own vocabulary as its only legal material; every face projected from one source; the gap-pressure law (registry misses recorded as data).

## (2) COMMON CORE · UNION'S EDGES · IMPLIED-BUT-ABSENT

**COMMON CORE**: declared once, everything generated/projected from it · the registry of behaviors itself registered · registration mints addressing · per-unit error isolation, honest reporting · add-a-row needs no deployment · the union/meta view.

**UNION'S EDGES** — A only: explicit generates[] per type · priority cascade with isolation · specs for embedding/queue/theme/accessibility/decorator/capability targets · self-teaching _next loop · function_params_map generic routing · ltree address templates. B only: git-native lifecycle (versioned, revertible, same-commit doc reflection) · true deletion semantics · gated authoring · the port/type-graph (produces()) · derived tool signatures · drift tests failing the build · per-registry constitutions · availability predicates.

**IMPLIED-BUT-ABSENT**: (1) re-cascade on change / completeness accounting (30 vs 4 artifact counts prove no run-all-report-holes loop) · (2) the reverse edge generated_from↔generates queryable both ways · (3) spec validation at registration (7/16 empty schemas fanned out happily) · (4) one registry organ spanning files↔DB · (5) de-registration cascade.

## (3) THE REBUILT ONE

**1. The row lives as a FILE; the DB is a derived projection.** The engine's discipline is the stronger registration mechanism (gate/git/revert/drift/deletion); NORTH-STAR's "everything ends up in Supabase" is the read side — served by DERIVING DB rows from the files (file → assemble → DB, one-way). A DB row with no source file is a ghost, fails loud (breadcrumb: "expected types/<name>.py; previously seeded by <migration>; fix: create(kind='type',…)"). Also resolves A's placed values (the hardcoded decorator UUID becomes declared/resolved — derive-never-place at the gate).

**2. types/<name>.py** — one file per universal type, the union of both row shapes:
```python
TYPE = {
  "id": "decision",                      # == file stem
  "label": "Decision",
  "data_schema": {...},                  # REQUIRED non-trivial (fixes A's empties)
  "faces": {                             # generates[] × per-target specs, one nested dict
    "tool":      {"verbs": ["create","list","get","update"]},
    "board":     {"status_values": [...], "renderer": "DecisionCard", "icon": "...", "color": "..."},
    "ui":        {...theme/accessibility...},
    "embedding": {"spaces": [...]},
    "edges":     {"kinds": {...}},
    "address":   {"template": "vi.{user}.decision.{id}"},
    "behaviors": {"on_create": [...], "on_click": [...]},
    "routing":   {"event": "type.decision.created", "intent": "process_decision"},
  },
  "version": 1,
}
```
Face keys ARE the cascade handler ids; presence = generates[] membership.

**3. cascades/<name>.py** — A's cascade_registry re-homed as file-per-row: TARGET, PRIORITY, REQUIRES (ordering deps explicit), handle(type_row) → record(s). Auto-discovered like nodes.

**Mechanics — one act, all faces**: create(kind='type', spec) [zero new tools — the enum picks up Suite.create_type automatically] → gate (schema non-trivial; face specs validate against cascade contracts; referenced values registry-resolved) → file → commit → rediscover → **generate_all(type)**: cascades by priority, per-cascade isolation, honest {ok|error|skipped:reason}; each derives its projection (MCP tool rows; UI face via capabilities()/cognition_info so the generic renderer draws it; address template; embedding policy into projections/ spaces; edge kinds; behaviors into role/routine bindings; queue routing; and ONE sync cascade owning ALL Supabase landing — directive 4 in one seam). **The completeness ledger** (new): generated_from edge per artifact + equal-and-opposite generates→; drift test asserts every type × applicable cascade has an artifact or a recorded skip; deleting a type retracts the fan-out through the same edges. **Suite.type_info()** serializes registry + fan-out state — the honest replacement for all_type_registries (served union of DISCOVERED registries, not fake constants). Self-teaching: _next transitions + errors naming the create path.

**Data landing**: the 16 cloud types → one file each (component_spec→faces.board/ui; behavior_spec→faces.behaviors; status_values→faces.board; generates[]→face keys). **The 7 hollow rows FAIL THE GATE as-is — correct: surfaced to the operator (rule 8: ask, don't fabricate), never re-imported hollow.** The 30 generated tool rows, decorators, capabilities are NOT migrated — they regenerate (generated artifacts are never source). Engine registries unchanged — the type registry is a peer directory; cascades reference INTO them. engine_schemas' richness absorbed as face vocabulary; the bridge view becomes unnecessary.

**A NEW KIND of project (forecast/theorem/document) registers in one act**: create(kind='type', {id:"forecast", data_schema, faces…}) → verbs, card, addresses, embedding policy, routing exist; capabilities() now contains forecast, so **every authoring prompt from that moment can only speak of forecasts in registered terms** (rule 8 closes the loop). A genuinely new FACE = one new cascades/<name>.py row — still not a new system.

## (4) EACH SIDE'S PARTIALITY
**A1** articulated the fan-out, not the discipline: empty schemas accepted; dormant spec columns; placed constants; no re-run accounting; no retraction; no versioning; DB-only, invisible to capabilities(); one-shape card template. **A2** articulated the meta-registry but fabricated the facts and is read-only. **A3** articulated the conversational self-teaching surface, never deployed; generation half-persists; added a third catalog. **B** articulated the discipline — one-source, gated, git-lifecycled, self-describing — but has **no generative fan-out** and no type-of-project registry at all; machine-local files with no DB projection.

**Each side is the other's missing half: A knew what registration should CAUSE; B knew what registration should BE.** The rebuilt organ is B's registration act driving A's cascade, the fan-out's completeness itself registered, tested, and served to both faces from one function.

**Key refs:** schema.sql L33505 L33959 L13739 L33561 L3584–3900 L24007 L41107 · migrations/20260221_vi_universal_mcp_registry_v2.sql + _compose_domain.sql · AGENTS.md · suite.py L1496 L1762 L4708 · runtime/registry.py L55–93 · contracts/cognition_info.py · mcp_face/tools/create.py · mark_types/AGENTS.md · NORTH-STAR.md.
