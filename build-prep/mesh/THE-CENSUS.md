# THE CENSUS — full-estate inventory + top logical map (2026-07-08)
*77 territories observed · 10 batch seats + 1 final (kimi-2.7) · observations at mesh://territory/* · synthesis at mesh://census/1*

## The map (final seat's mesh_note)
The estate is a federation of self-registering modules, each claiming a constitution (AGENTS.md), a file-discovered registry of .py row files, a runtime loader in runtime/, and an acceptance test asserting parity. Across ten batches the mesh has established that this pattern is load-bearing but systematically incomplete: constitutions enumerate smaller live sets than directories contain, many .py declarations are truncated mid-dict, and the runtime loaders that would enforce the contracts are referenced but rarely observed. The anchor's three relations — common coordinates (contracts/address.py), common memory (supabase ledger / recollection exchange embeddings), and self-reference (the mesh's own addressed records) — are partially instantiated but fragmented: address.py is treated as a spine yet explicitly delegates resolution of many schemes to runtime modules, and the README.md claims nothing is implemented while STATE.md and handoffs describe substantial living machinery. The mesh now understands itself as a map of registry seams and their un-wired vocabularies, not as a unified system description. Its most urgent work is to read the canonical documents (STATE.md, MAP.md), the runtime integration files (runtime/suite.py, runtime/bridge.py, runtime/axis_registry.py, runtime/edge_kinds.py, runtime/cc_channels.py, runtime/checks.py), and the unobserved registry row files and acceptance tests, in order to distinguish genuinely forgotten stubs from deliberately parked deferrals and to surface the silent merge risks before they auto-merge without conflict markers.

## Convergences (load-bearing facts)
- **File-discovered registry pattern with AGENTS.md constitution + one .py per row + runtime loader + acceptance test** — types/, source_types/, stack_item_types/, verdict_panels/, skills/, relation_types/, scope_grammar/, projections/, platforms/, nodes/, operator_memory/, modes/, mode_detection_rules/, lifters/, mark_types/, item_types/, forms/, generation_policies/, flows/, guides/, edge_kinds/, decisions/, decision_subtypes/, contexts/, axes/, ai_tics/, attachment_types/, checks/, board_edges/ (seen from: batch 2, batch 3, batch 4, batch 5, batch 6, batch 7, batch 8, batch 9)
- **runtime/ as the integration spine that discovers and loads registries** — runtime/type_registry.py, runtime/source_types.py, runtime/stack_item_types.py, runtime/verdict_panels.py, runtime/cc_board.py, runtime/modes_registry.py, runtime/lifter_registry.py, runtime/mark_types.py, runtime/item_types.py, runtime/forms.py, runtime/flows.py, runtime/skills.py, runtime/edge_kinds.py, runtime/axis_registry.py, runtime/ai_tics.py, runtime/cc_channels.py, runtime/checks.py, runtime/relation_types.py, runtime/projections.py, runtime/operator_memory.py, runtime/registry.py, runtime/suite.py, runtime/bridge.py, runtime/resolver.py (seen from: batch 2, batch 3, batch 4, batch 5, batch 6, batch 7, batch 8, batch 9, batch 10)
- **AGENTS.md as prescriptive module constitution with read-order precedence** — AGENTS.md, voice/AGENTS.md, verdict_panels/AGENTS.md, types/AGENTS.md, tests/AGENTS.md, store/AGENTS.md, stack_item_types/AGENTS.md, source_types/AGENTS.md, skills/AGENTS.md, scope_grammar/AGENTS.md, runtime/AGENTS.md, roles/AGENTS.md, relation_types/AGENTS.md, projections/AGENTS.md, platforms/AGENTS.md, nodes/AGENTS.md, operator_memory/AGENTS.md, orienteering/AGENTS.md, panels/AGENTS.md, ops/AGENTS.md, modes/AGENTS.md, mode_detection_rules/AGENTS.md, lifters/AGENTS.md, mark_types/AGENTS.md, item_types/AGENTS.md, introspection/AGENTS.md, guides/AGENTS.md, generation_policies/AGENTS.md, forms/AGENTS.md, flows/AGENTS.md, fabric/AGENTS.md, edge_kinds/AGENTS.md, docs/AGENTS.md, dials/AGENTS.md, decisions/AGENTS.md, decision_subtypes/AGENTS.md, contracts/AGENTS.md, contexts/AGENTS.md, canvas/AGENTS.md, axes/AGENTS.md, ai_tics/AGENTS.md, checks/AGENTS.md, board_edges/AGENTS.md (seen from: batch 2, batch 3, batch 4, batch 5, batch 6, batch 7, batch 8, batch 9, batch 10)
- **ops/services.json as the single source of truth for managed services** — ops/services.json (seen from: batch 1, batch 4, batch 9)
- **contracts/address.py as the address spine / common coordinate scheme** — contracts/address.py (seen from: batch 1, batch 7)
- **Supabase-backed persistence as the common memory substrate** — store/pg_vectors.py, store/pg_marks.py, recollection/, ledger.edge, ledger.assertion, ledger.edge_unified, ledger.edge_kind (seen from: batch 2, batch 4, batch 7)
- **Voice subsystem converged on systemd + shared ops/cli/gpu.py authority** — voice/lifecycle.py, ops/cli/gpu.py, ops/cli/systemd.py, company-bridge.service, voice/ops/systemd/, voice.env (seen from: batch 10)
- **Read-order precedence: AGENTS.md → MAP.md → STATE.md → HANDOFF.md** — AGENTS.md section '# AGENTS.md — read this first', HANDOFF.md > paragraph beginning 'Read order for a fresh agent:', HANDOFF-2026-06-07-model-layer-and-cognition.md (seen from: batch 10)
- **Company Map / [[Company Map]] as central registry authority** — [[Company Map]], MAP.md (seen from: batch 4, batch 10)
- **build-prep/ as canonical vault source with read-copies in repo** — build-prep/design/, build-prep/contracts/, build-prep/the-one-application/SUBTYPE-COVERAGE-GAP.md, build-prep/brain/THINKING-MEMORY-IDENTITY-PRESENCE.md, build-prep/CROSS-SESSION-CHANNELS-PROVEN.md, build-prep/cross-session-unified-transport.md, build-prep/concurrent-cognition/, build-prep/MODE-SYSTEM-MAP.md (seen from: batch 7, batch 8, batch 9, batch 10)
- **ops/ as self-describing operational command center** — ops/AGENTS.md, ops/BOOT-RUNBOOK.md, ops/STARTUP.md, ops/services.json, ops/systemd/, ops/company, ops/cli, ops/cli/app.py, ops/cli/gpu.py, ops/cli/systemd.py (seen from: batch 1, batch 4, batch 10)
- **canvas/app as the unmanaged Vite/React frontend** — canvas/app, ops/services.json -> combos -> wake, ops/systemd/company-canvas.service (seen from: batch 1, batch 8, batch 9)
- **RHM action parsing migrated to native tool-calling** — runtime/suite.py, RHM_VERB_SPECS, RHM_VERBS, _parse_rhm_action (RETIRED) (seen from: batch 10)
- **Three fully-merged branches still exist as lingering worktrees** — ~/company-interactive, ~/company-night, ~/company-overnight (seen from: batch 10)
- **Concurrent Cognition is unbuilt research landscape only** — build-prep/concurrent-cognition/ (seen from: batch 9, batch 10)

## Contradictions (the next places to look)
- **contracts/address.py resolving power**
  - contracts/address.py declares ui://, code://, skill://, context://, session://, cap://, board:// as labels the store does NOT resolve *()*
  - anchor treats contracts/address.py as the resolving spine *()*
  - contexts/AGENTS.md claims contexts resolve through runtime/cognition.py:resolve_address and runtime/skills.py:ContextRegistry *()*
- **README.md scope vs actual build state**
  - README.md declares skeleton-only / nothing implemented *()*
  - STATE.md, SESSION-OPERABLE-INTERFACE.md, MERGE-COORDINATION.md describe substantial living machinery *()*
  - MAP.md describes intended automation *()*
  - runtime/capabilities/ described as living in STATE.md *()*
- **AGENTS.md constitutions vs directory contents**
  - constitutions enumerate smaller live sets than directories contain *()*
  - mark_types/ has 14 .py files absent from documented live set *()*
  - item_types/, generation_policies/, flows/, skills/, relation_types/ show directory count > constitution count *()*
  - ai_tics/mvp.py exists but is absent from AGENTS.md live-set enumeration *()*
- **Edge-kind inverses vs Law 4**
  - edge_kinds/AGENTS.md declares reverses are NEVER stored *()*
  - edge_kinds/ contains authored_by.py, depended-on-by.py, generated-by.py, powered-by.py, produced.py, promoted_from.py which sound like inverse relations *()*
  - attachment.py declares inverse: attached_to *()*
  - attached_to.py declares no inverse at all *()*
  - authored_by.py declares inverse: authored *()*
  - no authored.py file exists in directory listing *()*
- **Cross-session channels proven vs design-only**
  - build-prep/CROSS-SESSION-CHANNELS-PROVEN.md claims proven-by-use/live *()*
  - build-prep/cross-session-unified-transport.md says DESIGN-ONLY and explicitly forbids implementation edits *()*
- **canvas/app actual state**
  - canvas/AGENTS.md asserts rich Vite/React app with surfaces *()*
  - canvas directory listing only shows AGENTS.md, .gitkeep, app/, index.html *()*
  - app/ contents and README not shown *()*
- **checks registry claim vs evidence**
  - checks/AGENTS.md says 'Add a check = add a FILE + reflect it here' and frames general registry *()*
  - only two rows exist and both are truncated mid-implementation *()*
  - no evidence runtime/checks.py loader calls them *()*
- **AGENTS.md storage rule vs source-of-truth claim**
  - AGENTS.md section '## Source of truth' lists `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/` *()*
  - AGENTS.md storage rule says 'Storage on ext4 (`~/...`), never under `/mnt/c`' *()*
- **Silent regression in runtime/suite.py chat history**
  - interface session claims thread-scoped fix *()*
  - cognition session locates global chat_history(20) as overriding the fix *()*
  - both sessions agree regression exists but locate it differently in the diff surface *()*
- **ui-contract/ and ops/ operational state**
  - MAP.md table row `ui-contract/` building/planned, nothing live until driving harness flips it *()*
  - MAP.md table row `ops/` referenced but no operational evidence shown *()*
  - ops/services.json referenced as registry of truth for every service *()*
- **File-discovered registry 'zero engine code' claim vs runtime reality**
  - axes/AGENTS.md and ai_tics/AGENTS.md claim 'zero engine code' *()*
  - __pycache__ artifacts prove import/compilation *()*
  - runtime/axis_registry.py, runtime/ai_tics.py referenced as consumers *()*
- **Web UI 'what needs me' surfaces**
  - two 'what needs me' surfaces return disjoint decision sets *()*
  - per-control spotlight not observed in CRITIC-VERDICT-integration-journey.md section 5 / Guide component *()*

## Dormant / partly-built register (final seat)
- [forgotten] **canvas/app npm dev server as a managed unit** — ops/services.json -> combos -> wake / ops/systemd/company-canvas.service
- [forgotten] **build-prep/embedder-pplx/LEVERAGE-AND-TOOL-REQUESTS.md** — build-prep/embedder-pplx/LEVERAGE-AND-TOOL-REQUESTS.md
- [forgotten] **mcp_face cc_* tools (cc_attachments, cc_board, cc_clone, cc_gate, cc_images, cc_retire, cc_voice)** — mcp_face/tools/
- [forgotten] **ops/cli bench.py benchmark runner** — ops/cli/bench.py
- [forgotten] **ops/cli telemetry.py + telemetry.jsonl** — ops/cli/telemetry.py
- [forgotten] **unnamed/question-mark corpus space '?' and 'what' space** — corpus projection mechanism
- [forgotten] **mesh corpus space** — corpus spaces
- [forgotten] **activation_driver.py always-on caller** — runtime/activation_driver.py
- [forgotten] **retired cc_channels named-channel store** — .data/channels/_channels/<id>.json
- [forgotten] **render_declarations.json** — runtime/render_declarations.json
- [forgotten] **dragnet_freshness.py routine** — routines/dragnet_freshness.py
- [forgotten] **guide_freshness.py routine** — routines/guide_freshness.py
- [forgotten] **patterned_visibility.py skill** — skills/patterned_visibility.py
- [forgotten] **principle_beneath.py relation-type** — relation_types/principle_beneath.py
- [forgotten] **sibling.py relation-type** — relation_types/sibling.py
- [forgotten] **depends_on.py relation-type** — relation_types/depends_on.py
- [forgotten] **precedes.py relation-type** — relation_types/precedes.py
- [forgotten] **axes/design.py — docstring truncated, AXIS dict not shown** — axes/design.py
- [forgotten] **axes/register.py 'others' theme value — mentioned but never enumerated** — axes/register.py fields.theme
- [forgotten] **attachment_types/images.py, recall.py, sessions.py — present in directory but content not shown** — attachment_types/images.py, attachment_types/recall.py, attachment_types/sessions.py
- [forgotten] **ai_tics/mvp.py — present in directory but not named in AGENTS.md live set** — ai_tics/mvp.py
- [forgotten] **Loadout resolution + atomic loadout-switch actuator** — STATE.md paragraph beginning 'Captured-not-built: **loadout resolution**'
- [forgotten] **contracts/, store/, runtime/, fabric/, mcp_face/, nodes/, canvas/, docs/ directories — README says nothing implemented** — README.md table rows
- [forgotten] **Stage 1 merge plan** — SESSION-OPERABLE-INTERFACE.md section 4
- [forgotten] **ui-contract/ module — building/planned, nothing live until driving harness flips it** — MAP.md table row `ui-contract/`
- [forgotten] **ops/services.json and `company` console — referenced but no operational evidence shown** — MAP.md table row `ops/`
- [forgotten] **Thread-scoped fix for chat history — at risk of silent reversion** — runtime/suite.py ~line 3756
- [forgotten] **Mode-dial join and latent-gold→CognitionView wiring** — MERGE-COORDINATION.md 'Then the integration (mode-dial join, latent-gold→CognitionView, place CognitionView in the new IA)'
- [forgotten] **Uncommitted wire residue on main checkout (21 files)** — Uncommitted on the `main` checkout
- [parked] **Forced-tool-choice capability probe** — STATE.md line 'The forced-tool-choice capability probe is RETIRED'
- [parked] **completion_poke.py routine** — routines/completion_poke.py
- [parked] **scope_grammar/manage.py verb** — scope_grammar/manage.py
- [parked] **member-kind extension field in session_channels** — <COMPANY_STORE>/agent_sessions/channels.jsonl
- [parked] **registry_freshness.py Python generalization** — ops/hooks/registry_freshness.py
- [parked] **combo small-pair** — ops/services.json combos
- [parked] **NodeShape.tsx untouched by this session** — canvas/app/src/regions/NodeShape.tsx
- [parked] **nodes/llm.py, runtime/scheduler.py, fabric/transport.py, fabric/vram.py untouched by this session** — nodes/llm.py, runtime/scheduler.py, fabric/transport.py, fabric/vram.py
- [parked] **retired vector file fs_store_file_vectors.retired.py** — store/fs_store_file_vectors.retired.py
- [parked] **GPU resource arbitration deliberately left open** — voice/AGENTS.md, voice/lifecycle.py, ops/cli/gpu.py
- [parked] **mcp_face/remote_exposure.json.deleted-20260622 fail-closed policy artifact** — mcp_face/remote_exposure.json.deleted-20260622
- [parked] **introspection invoke.py non-subprocess invokers and adapters** — introspection/invoke.py
- [parked] **Concurrent Cognition build-prep research landscape** — build-prep/concurrent-cognition/

## Per-batch dormant registers (nothing dropped in the reduce)
- [forgotten] **canvas/app npm dev server as a managed unit** —  *(batch 1)*
- [forgotten] **ai-systems-strategic-overview terrain entry** —  *(batch 1)*
- [forgotten] **build-prep/embedder-pplx/LEVERAGE-AND-TOOL-REQUESTS.md** —  *(batch 1)*
- [forgotten] **clone:// scheme explanation** —  *(batch 1)*
- [forgotten] **mcp_face cc_* tools (cc_attachments, cc_board, cc_clone, cc_gate, cc_images, cc_retire, cc_voice)** —  *(batch 1)*
- [forgotten] **ops/cli bench.py benchmark runner** —  *(batch 1)*
- [forgotten] **ops/cli telemetry.py + telemetry.jsonl** —  *(batch 1)*
- [parked] **registry_freshness.py Python generalization** —  *(batch 1)*
- [parked] **combo small-pair** —  *(batch 1)*
- [forgotten] **unnamed/question-mark corpus space '?' and 'what' space** —  *(batch 1)*
- [forgotten] **mesh corpus space** —  *(batch 1)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [parked] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [parked] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **** —  *(batch 2)*
- [forgotten] **activation_driver.py always-on caller** — runtime/activation_driver.py *(batch 3)*
- [forgotten] **retired cc_channels named-channel store** — .data/channels/_channels/<id>.json *(batch 3)*
- [forgotten] **render_declarations.json** — runtime/render_declarations.json *(batch 3)*
- [parked] **completion_poke.py routine** — routines/completion_poke.py *(batch 3)*
- [forgotten] **dragnet_freshness.py routine** — routines/dragnet_freshness.py *(batch 3)*
- [forgotten] **guide_freshness.py routine** — routines/guide_freshness.py *(batch 3)*
- [forgotten] **patterned_visibility.py skill** — skills/patterned_visibility.py *(batch 3)*
- [forgotten] **principle_beneath.py relation-type** — relation_types/principle_beneath.py *(batch 3)*
- [forgotten] **sibling.py relation-type** — relation_types/sibling.py *(batch 3)*
- [forgotten] **depends_on.py relation-type** — relation_types/depends_on.py *(batch 3)*
- [forgotten] **precedes.py relation-type** — relation_types/precedes.py *(batch 3)*
- [parked] **scope_grammar/manage.py verb** — scope_grammar/manage.py *(batch 3)*
- [parked] **member-kind extension field in session_channels** — <COMPANY_STORE>/agent_sessions/channels.jsonl *(batch 3)*
- [forgotten] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [unclear] **** —  *(batch 4)*
- [unclear] **** —  *(batch 4)*
- [parked] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [parked] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [unclear] **** —  *(batch 4)*
- [parked] **** —  *(batch 4)*
- [unclear] **** —  *(batch 4)*
- [unclear] **** —  *(batch 4)*
- [unclear] **** —  *(batch 4)*
- [unclear] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 4)*
- [forgotten] **** —  *(batch 5)*
- [forgotten] **** —  *(batch 5)*
- [forgotten] **** —  *(batch 5)*
- [forgotten] **** —  *(batch 5)*
- [forgotten] **** —  *(batch 5)*
- [forgotten] **** —  *(batch 5)*
- [parked] **** —  *(batch 5)*
- [forgotten] **** —  *(batch 5)*
- [parked] **** —  *(batch 5)*
- [forgotten] **** —  *(batch 5)*
- [forgotten] **** —  *(batch 5)*
- [forgotten] **** —  *(batch 5)*
- [forgotten] **** —  *(batch 6)*
- [forgotten] **** —  *(batch 6)*
- [forgotten] **** —  *(batch 6)*
- [forgotten] **** —  *(batch 6)*
- [forgotten] **** —  *(batch 6)*
- [parked] **** —  *(batch 6)*
- [parked] **** —  *(batch 6)*
- [forgotten] **** —  *(batch 6)*
- [forgotten] **** —  *(batch 6)*
- [forgotten] **** —  *(batch 6)*
- [forgotten] **** —  *(batch 6)*
- [forgotten] **** —  *(batch 7)*
- [forgotten] **** —  *(batch 7)*
- [forgotten] **** —  *(batch 7)*
- [parked] **** —  *(batch 7)*
- [parked] **** —  *(batch 7)*
- [forgotten] **** —  *(batch 7)*
- [forgotten] **** —  *(batch 7)*
- [forgotten] **** —  *(batch 7)*
- [forgotten] **** —  *(batch 7)*
- [forgotten] **** —  *(batch 7)*
- [forgotten] **** —  *(batch 7)*
- [forgotten] **** —  *(batch 7)*
- [forgotten] **** —  *(batch 8)*
- [forgotten] **** —  *(batch 8)*
- [forgotten] **** —  *(batch 8)*
- [parked] **** —  *(batch 8)*
- [parked] **** —  *(batch 8)*
- [forgotten] **** —  *(batch 8)*
- [forgotten] **** —  *(batch 8)*
- [parked] **** —  *(batch 8)*
- [forgotten] **** —  *(batch 8)*
- [forgotten] **** —  *(batch 8)*
- [parked] **** —  *(batch 8)*
- [forgotten] **** —  *(batch 8)*
- [forgotten] **** —  *(batch 8)*
- [forgotten] **** —  *(batch 8)*
- [forgotten] **axes/design.py — docstring truncated, AXIS dict not shown** — axes/design.py *(batch 9)*
- [forgotten] **axes/register.py 'others' theme value — mentioned but never enumerated** — axes/register.py fields.theme *(batch 9)*
- [forgotten] **attachment_types/images.py, recall.py, sessions.py — present in directory but content not shown** — attachment_types/images.py, attachment_types/recall.py, attachment_types/sessions.py *(batch 9)*
- [forgotten] **ai_tics/mvp.py — present in directory but not named in AGENTS.md live set** — ai_tics/mvp.py *(batch 9)*
- [parked] **Forced-tool-choice capability probe** — FILE STATE.md line 'The forced-tool-choice capability probe is RETIRED' *(batch 9)*
- [forgotten] **Loadout resolution + atomic loadout-switch actuator** — FILE STATE.md paragraph beginning 'Captured-not-built: **loadout resolution**' *(batch 9)*
- [forgotten] **contracts/, store/, runtime/, fabric/, mcp_face/, nodes/, canvas/, docs/ directories — README says nothing implemented** — FILE README.md table rows *(batch 9)*
- [parked] **NodeShape.tsx untouched by this session** — canvas/app/src/regions/NodeShape.tsx *(batch 9)*
- [parked] **nodes/llm.py, runtime/scheduler.py, fabric/transport.py, fabric/vram.py untouched by this session** — nodes/llm.py, runtime/scheduler.py, fabric/transport.py, fabric/vram.py *(batch 9)*
- [forgotten] **Stage 1 merge plan** — SESSION-OPERABLE-INTERFACE.md section 4 *(batch 9)*
- [forgotten] **ui-contract/ module — building/planned, nothing live until driving harness flips it** — FILE MAP.md table row `ui-contract/` *(batch 9)*
- [forgotten] **ops/services.json and `company` console — referenced but no operational evidence shown** — FILE MAP.md table row `ops/` *(batch 9)*
- [forgotten] **Thread-scoped fix for chat history — only present in interface's stream, at risk of silent reversion** — runtime/suite.py ~line 3756 *(batch 9)*
- [forgotten] **Mode-dial join and latent-gold→CognitionView wiring — described as future integration work** — MERGE-COORDINATION.md 'Then the integration (mode-dial join, latent-gold→CognitionView, place CognitionView in the new IA)' *(batch 9)*
- [forgotten] **Uncommitted wire residue on main checkout (21 files)** — Uncommitted on the `main` checkout *(batch 9)*
- [forgotten] **** —  *(batch 10)*
- [forgotten] **** —  *(batch 10)*
- [forgotten] **** —  *(batch 10)*
- [forgotten] **** —  *(batch 10)*
- [forgotten] **** —  *(batch 10)*
- [forgotten] **** —  *(batch 10)*
- [forgotten] **** —  *(batch 10)*
- [forgotten] **** —  *(batch 10)*
- [forgotten] **** —  *(batch 10)*
- [forgotten] **** —  *(batch 10)*
- [forgotten] **** —  *(batch 10)*

## Census-proposed next territories
- STATE.md — Both handoffs declare STATE.md canonical over their own narrative; the mesh has not observed it yet and it is needed to settle README.md vs build-state contradictions.
- MAP.md — Declared as structure + live registry in read order; needed to ground addresses found in AGENTS.md and handoffs and to verify ui-contract/ops operational claims.
- runtime/suite.py — Convergence point for RHM_VERBS/RHM_VERB_SPECS, native tool-calling claim, and the silent chat-history regression contradiction; full file needed to triangulate actual merge risk.
- runtime/bridge.py — Both interface and cognition streams add routes here; 7 new routes claimed by interface, cognition adds cognition.* SSE branch — conflict surface.
- voice/lifecycle.py — Old Popen path vs new systemd path is a key contradiction/dormant find; verify current load/unload/vram code and COMPANY_VOICE_REF block.
- ops/cli/gpu.py — Shared authority for voice launch/teardown and VRAM accounting; verify convergence with systemd and cgroup teardown.
- ops/services.json — Described as registry of truth for every service; contents will show which declared services are actually wired and whether canvas/app is still unmanaged.
- ops/company and ops/cli/app.py — Constitution says `company` CLI is the single command center; command surface mismatch between docstring and README needs resolution.
- runtime/capabilities/ — STATE.md describes typed capability resolver registries as living; verify against README.md 'nothing implemented' contradiction.
- runtime/axis_registry.py — axes and ai_tics both point here as the runtime consumer of file-discovered registries; needed to verify whether 'zero engine code' claim holds.
- runtime/resolver.py — Referenced by axes/device.py RESOLVER-CONTRACT §1 and by axes/AGENTS.md; resolves axis value_source semantics.
- axes/design.py — Only seeded axis whose AXIS dict is not visible; docstring truncated mid-word — must gather full file to resolve contradiction with other seeded axes.
- attachment_types/images.py — One of three attachment type files present in directory but completely opaque; needed to complete the attachment registry picture.
- attachment_types/recall.py — Present in directory but no content shown; likely relates to the recall/embedder subsystem mentioned in STATE.md.
- attachment_types/sessions.py — Present in directory but no content shown; may be the wiring layer that consumes ATTACHMENT_TYPE dicts.
- ai_tics/mvp.py — File exists but is absent from AGENTS.md live-set enumeration despite constitution claiming live set is test-asserted — contradiction to resolve.
- tests/ai_tics_acceptance.py — AGENTS.md claims this test asserts the live set; needed to resolve mvp.py contradiction.
- canvas/app/src/ — canvas/AGENTS.md asserts a full Vite/React app with surfaces but the directory listing is a black box; verify if it is living, half-built, or empty.
- canvas/app/src/useAppController.ts — Named as the FE coordination point for openStream dispatch collision zone and new handlers; needed to verify mode-dial wiring.
- canvas/app/src/api.ts — Appended client methods claimed disjoint from cognition fetchers; verify whether duplication exists.
- runtime/edge_kinds.py — Edge-kind constitution declares this is the ONE edge grammar and connects it to RelationTypeRegistry; need to verify the parallel/superset boundary and inverse handling.
- relation_types/ — Contradiction with edge_kinds over whether RelationTypeRegistry can hold edge-kind rows; inspect the actual registry shape.
- runtime/decision_subtypes.py — Referenced as the mechanism mirror but not observed in the directory listing; determine if it exists elsewhere or is unbuilt.
- build-prep/the-one-application/SUBTYPE-COVERAGE-GAP.md — Named in decisions/AGENTS.md as the document recording the missing-subtype incident; likely contains the list of invisible decision rows.
- runtime/checks.py — checks/AGENTS.md and both check files point here; needed to resolve whether dossier_refcheck/prose_clean are actually loaded or truly dormant.
- runtime/cc_channels.py — build-prep cross-session documents disagree on whether channels are proven or design-only; this is the runtime seam they both reference.
- channel-memory/noticeboard/ — Directory exists but is omitted from README.md layout; likely a forgotten pocket or a newer addition not yet meshed.
- channel-memory/plan/ — Present on disk, absent from self-description, needs triangulation.
- CRITIC-VERDICT-integration-journey.md section 5 / Guide component — Per-control spotlight not observed and two decision surfaces return zero-overlap sets; need component-level material.
- /api/voice/log — Server endpoint proven but browser client emitters never fired; investigate why voice.client reports are dormant.
- build-prep/concurrent-cognition/ — Explicitly unbuilt research landscape; determine if it is a real build candidate or parked indefinitely.
- .build/interface/GAPS-REGISTER.md — SESSION-OPERABLE-INTERFACE.md claims gaps are logged here; needed to verify the operable-interface completion state.
- .build/interface/state.json — Referenced as part of the operable-interface build artifacts; likely contains structured completion/gap data.
- .build/interface/MERGE-PLAN.md — SESSION-OPERABLE-INTERFACE.md section 4 merge plan was truncated; full plan needed to coordinate with MERGE-COORDINATION.md.

---

## Full inventory (every observation)

### corpus-spaces
- [living] **code_archaeology corpus space** `code_archaeology: 2900` — Largest space by far — 2900 records, ~44% of all listed records; no content shown, only count.
- [living] **history corpus space** `history: 1464` — Second largest; likely chronological or narrative material but only count given.
- [living] **repo corpus space** `repo: 649` — Third largest; name suggests repository/code mirror content.
- [living] **design_intent corpus space** `design_intent: 485` — Mid-sized; explicitly about intent/purpose documentation.
- [living] **worldview corpus space** `worldview: 162` — Same record count as principles and topics — possible shared source or batch.
- [living] **principles corpus space** `principles: 162` — Identical count to worldview, topics — may be derived from same 162-item set.
- [living] **topics corpus space** `topics: 162` — Identical count to worldview, principles — strong hint of a split or projection of one base set.
- [living] **common_knowledge corpus space** `common_knowledge: 122` — Smaller than the 162-cluster; possibly a distinct curated subset.
- [living] **operators corpus space** `operators: 29` — Very small; name suggests agent/operator definitions or personas.
- [living] **mesh corpus space** `mesh: 26` — Tiny; name suggests interconnection/relationship data, yet smaller than operators.
- [unknown] **unnamed/question-mark corpus space** `?: 11` — Space has no name, only '?' — 11 records; could be unclassified, corrupted, or a placeholder.
- [half-built] **what corpus space** `what: 1` — Only 1 record; name is a bare interrogative, possibly an accidental or test projection.
  - dormant-candidates: what: 1 — single-record space with a non-domain name, looks like an unfinished or accidental projection · ?: 11 — unnamed/placeholder space, may be unclassified residue · mesh: 26 — name implies connectivity data but is smaller than operators; possibly underpopulated relative to its purpose
  - surprises: Three spaces (worldview, principles, topics) share exactly 162 records — suspiciously identical, suggesting they may be views of one underlying corpus rather than independent spaces. · A space is literally named '?' with 11 records — an unnamed projection in a live census. · The 'what' space has only 1 record and is named like a question, not a domain.

### ops/services.json
- [living] **service registry file** `ops/services.json` — Self-described as 'single source of truth' for services; explicitly admits entries may be imperfect (ports/units).
- [living] **vram ceiling** `ops/services.json -> vram_ceiling_mb` — Hard ceiling 16376 MB (~16 GB) used by company resource manager.
- [living] **vram overhead margin** `ops/services.json -> vram_overhead_mb` — Recently raised 512 -> 1024 (2026-06-29) after a near-card-filling vLLM refusal; measured overhead ~900 MiB.
- [living] **combo small-pair** `ops/services.json -> combos -> small-pair` — Verified co-resident 2026-06-06; 2B + 0.8B chat tiers together.
- [living] **combo wake** `ops/services.json -> combos -> wake` — After-restart ritual; explicitly says canvas (vite) is unmanaged and must be started separately.
- [living] **combo xsession** `ops/services.json -> combos -> xsession` — Cross-session CHANNEL fabric loadout; rerank-jina moved to GPU 2026-06-28 for speed.
- [living] **combo instrument** `ops/services.json -> combos -> instrument` — Strongest surface loadout; references an external leverage/tool-request spec document.
- [living] **combo xsession-brain** `ops/services.json -> combos -> xsession-brain` — Local brain variant of xsession; GPU voice and 4B brain are mutually exclusive due to VRAM.
- [living] **combo interaction** `ops/services.json -> combos -> interaction` — Class base combo; everyday default brain migrated from AWQ to FP8 2026-06-29.
- [half-built] **combo interaction-parakeet** `ops/services.json -> combos -> interaction-parakeet` — Variant definition is truncated mid-string ('ear inst'); full swap rules and note are cut off in the material.
- [living] **autostart semantic change** `ops/services.json -> _doc` — 2026-06-06 Tim decision: nothing auto-starts at boot; autostart flag now only affects bare 'company up' behavior.
- [living] **company swap serve-model rewrite** `ops/services.json -> _doc` — The 'serve' field is the script whose default model company swap rewrites.
  - dormant-candidates: canvas/app npm dev server — referenced in wake combo note as unmanaged and requiring manual start; 'making it a managed unit is a named future row' (ops/services.json -> combos -> wake -> note) · combo small-pair — documented and verified but may be superseded by newer combos; no evidence of recent use in material · build-prep/embedder-pplx/LEVERAGE-AND-TOOL-REQUESTS.md — referenced by instrument combo but not present in material; external spec whose wiring status is unknown
  - surprises: The canvas (vite frontend) is explicitly unmanaged by the service registry despite being part of the surface — a 'named future row' that has not been integrated. · The combo 'interaction' had its brain service migrated from chat-4b (AWQ worker) to chat-4b-fp8 specifically so the combo reproduces the live brain, implying the registry was previously out of sync with reality. · vram_overhead_mb was raised from 512 to 1024 based on a measured ~900 MiB overhead, suggesting the previous 512 default was systematically undersized.

### contracts/address.py
- [living] **Address grammar module (C1)** `contracts/address.py` — Pydantic-based address + provenance module; docstring declares itself as C1 and references build-prep/contracts/C1.
- [living] **run:// scheme** `contracts/address.py grammar line: run://<domain>/<intent>/<node>@<branch>#run=<id>` — Mutable pointer; explicitly described as resolved by the store.
- [living] **cas:// scheme** `contracts/address.py grammar line: cas://<algo>:<hash>` — Immutable content; explicitly described as resolved by the store.
- [living] **blob:// scheme** `contracts/address.py grammar line: blob://<algo>:<hash>` — Large binary addressed but not inlined; explicitly described as resolved by the store.
- [living] **vec:// scheme** `contracts/address.py grammar line: vec://<source-address>#emb=<model>` — Embedding of a source; explicitly described as resolved by the store.
- [living] **ui:// scheme** `contracts/address.py grammar line: ui://<kind>/<ref>` — Label only; store does NOT resolve it; resolved elsewhere via UI-component registry (contracts.ui_info).
- [living] **code:// scheme** `contracts/address.py grammar line: code://<file-stem>/<symbol>` — Label only; backend resolver ui://→code://→scope[] reads corpus join data; described as pivot L1 and L5 lean on.
- [living] **skill:// scheme** `contracts/address.py grammar line: skill://<id>` — Label only; resolves to skill instructions content via FILE-DISCOVERED registry.
- [living] **context:// scheme** `contracts/address.py grammar line: context://<id>` — Label only; resolves to context content blob via FILE-DISCOVERED registry.
- [living] **session:// scheme** `contracts/address.py grammar line: session://<id>` — Label only; resolves to agent-session registry record; live trajectory view is Suite fold, not this resolver.
- [living] **board:// scheme** `contracts/address.py grammar line: board://<id>` — Label only; RESOLVED per Heart H1.1 commit 68c7eda; previously register-but-defer at e5388f4.
- [half-built] **clone:// scheme** `contracts/address.py grammar line: clone://<source-sid>/<cut>` — Docstring for clone:// is truncated mid-sentence ('the clone-FLEET joins '); definition present but explanation incomplete in the material.
- [living] **exchange:// scheme** `contracts/address.py grammar line: exchange://<sid>/<i>` — Captured conversation exchange; recollection's canonical provenance address.
- [living] **file:// scheme** `contracts/address.py grammar line: file://<abs-path>` — File node in recollection's crossings graph.
- [living] **project:// scheme** `contracts/address.py grammar line: project://<name>` — Project node in recollection's containment graph.
- [living] **cap:// scheme** `contracts/address.py grammar line: cap://<kind>/<id>` — Label only; NEW singleton pattern because binary discovery is expensive; Suite.__init__ calls set_capability_registry() once.
- [living] **Schema-additive evolution rule** `contracts/address.py: 'Schema-additive: add optional fields + bump schema_ver; never break an existing one.'` — Repeatedly cited as justification for not bumping schema_ver when adding label-only schemes.
  - dormant-candidates: clone:// scheme explanation is truncated at 'the clone-FLEET joins ' in contracts/address.py — definition exists but documentation appears half-built in the provided excerpt.
  - surprises: The address module declares many schemes (ui://, code://, skill://, context://, session://, cap://, board://) as labels the store does NOT resolve, yet the file itself is contracts/address.py — the 'address spine' is partly a namespace of unresolved pointers rather than a resolver. · board:// was previously 'register-but-defer' at e5388f4 and only 'now wired' at 68c7eda, suggesting a pattern of schemes being added to the grammar before their resolver exists. · cap:// uses a singleton pattern explicitly because 'binary discovery is EXPENSIVE' — this is an unusual performance-driven registry design not shared by skill/context/session registries.

### orienteering/entries
- [living] **CosyVoice terrain entry** `orienteering/entries/CosyVoice.md` — TTS engine with a duplicate key: both `launched_by` and `launched-by` appear in frontmatter, pointing at the same systemd unit.
- [living] **actions-runner terrain entry** `orienteering/entries/actions-runner.md` — Self-hosted runner bound to a specific repo; two runner binary versions coexist in the tree (`bin.2.321.0` and `bin.2.334.0`).
- [half-built] **ai-systems-strategic-overview terrain entry** `orienteering/entries/ai-systems-strategic-overview.md` — Declared as 18 pages but only 6 exist; explicitly tagged scaffold-incomplete and predates the Company architecture.
- [living] **artefacts terrain entry** `orienteering/entries/artefacts.md` — Tiny 108K folder containing only two standalone narrative documents from the founding week.
- [living] **entries directory listing** `orienteering/entries/` — 38 terrain-entry markdown files; this is the hand-kept ledger itself, not auto-generated from filesystem scan.
  - dormant-candidates: ai-systems-strategic-overview — only 6 of 18 declared pages written, last_active 2025-08-07, predates Company architecture (orienteering/entries/ai-systems-strategic-overview.md)
  - surprises: CosyVoice.md frontmatter contains both `launched_by` and `launched-by` keys with the same value — a likely copy/paste or schema drift artifact. · ai-systems-strategic-overview.md is explicitly half-built: 6 of 18 declared pages exist, yet it is still listed as a living terrain entry. · actions-runner.md reveals two runner binary versions installed side by side (`bin.2.321.0` and `bin.2.334.0`), which is unusual for a single service unit.

### mcp_face/tools
- [living] **tools directory with 36 modules** `DIR mcp_face/tools/ (36 entries shown)` — File-discovered tool registry: adding a resource means adding a file, no edit to server.py.
- [unknown] **MCP-DESIGN-PRINCIPLE doc reference** `mcp_face/tools/__init__.py` — The doc is referenced as the standing law but not included in the material.
- [half-built] **access tool** `mcp_face/tools/access.py` — Docstring declares two ops (may, roster) and references the single function shared with bridge routes, but the shown code truncates mid-register decorator before the function body is visible.
- [half-built] **cc_attachments tool** `mcp_face/tools/cc_attachments.py` — Docstring lists four ops (attach, detach, list, manifest) and references registry-based attachment kinds, but the code excerpt cuts off before implementation.
- [half-built] **cc_board tool** `mcp_face/tools/cc_board.py` — Described as agent-facing surface over runtime/cc_board.py with file-discovered registries for types/sources/edges; excerpt ends before any code body.
  - dormant-candidates: mcp_face/tools/access.py — docstring complete, register decorator started, but function body not shown; may be half-implemented or truncated in material. · mcp_face/tools/cc_attachments.py — four ops declared, no visible implementation in excerpt. · mcp_face/tools/cc_board.py — rich design description, no visible implementation in excerpt. · mcp_face/tools/cc_clone.py, cc_gate.py, cc_images.py, cc_retire.py, cc_voice.py — listed in directory but no material shown; could be dormant or unexamined.
  - surprises: The directory contains both generic resource tools (access, channels, context, corpus, create, decisions, dials, flows, ingest, instrument, introspection, jobs, keeper, marks, node, operator, platform, point, routines, rule, runs, scope, sessions) AND a parallel set of 'cc_' prefixed tools (cc_attachments, cc_board, cc_channel, cc_clone, cc_gate, cc_images, cc_retire, cc_voice) that appear to shadow/channel the runtime 'cc_*' modules through the MCP face. · The access tool docstring claims it is literally the same function used by /api/may and /api/access-of bridge routes — a strong convergence claim that would be easy to violate if the implementations diverge.

### ops/hooks
- [living] **cc_registry_freshness_check.sh** `ops/hooks/cc_registry_freshness_check.sh` — SessionStart hook specifically for Claude Code registry freshness; claims to be wired via .claude/settings.json, but that file is not in the material.
- [half-built] **registry_freshness.py** `ops/hooks/registry_freshness.py` — Generalized cross-platform freshness checker, but the excerpt cuts off mid-function definition (`def _stamp(pid: str) -> str` with no body) — cannot confirm it is complete or wired to run anywhere.
- [living] **write_self_marker.py** `ops/hooks/write_self_marker.py` — Self-marker writer for session identity; called by the bash SessionStart hook and read by runtime/session_scan.py, but no invocation or wiring is visible in the excerpt.
  - dormant-candidates: registry_freshness.py at ops/hooks/registry_freshness.py — built as a generalization but no evidence it is invoked or wired; function body is truncated in the material, so it may be half-built.
  - surprises: registry_freshness.py is described as the 'never touch again' generalization, yet the bash hook cc_registry_freshness_check.sh still appears to exist and be the one wired to SessionStart — the Python generalization may not actually be in use. · The bash hook's docstring references .claude/settings.json and store/claude-code.version_stamp, but those are not present in the material, so the wiring cannot be verified from this territory alone. · write_self_marker.py reads a Claude Code SessionStart stdin JSON shape, but the bash hook excerpt does not show it piping stdin into the Python marker writer.

### ops/cli
- [unknown] **company CLI launcher script** `../company` — Referenced in README/UPDATING as the entry point that puts cli/ on sys.path and calls app.main(); the file itself is not shown.
- [living] **app.py command dispatcher** `ops/cli/app.py` — Docstring lists commands including `company suites` (ALL-GREEN GATE) and `company health`, but README's everyday table only shows status/up/down — suggesting extra commands exist beyond the advertised surface.
- [half-built] **bench.py benchmark runner** `ops/cli/bench.py` — Script is truncated mid-implementation; it depends on an external vLLM venv and test scripts not present in this material.
- [unknown] **board.py** `ops/cli/board.py` — Listed in directory but no content shown; name suggests a dashboard/status board.
- [unknown] **capabilities.py** `ops/cli/capabilities.py` — Listed in directory but no content shown.
- [unknown] **clone.py** `ops/cli/clone.py` — Listed in directory but no content shown; name suggests model/service cloning utility.
- [unknown] **gpu.py resource manager** `ops/cli/gpu.py` — Described in UPDATING.md as THE RESOURCE MANAGER with read_gpu, running_gpu_services, check_f; content not shown.
- [unknown] **models.py** `ops/cli/models.py` — Listed in directory but no content shown; README mentions 'manage the local models'.
- [unknown] **registry.py services.json loader** `ops/cli/registry.py` — Described as loading services.json and resolving targets; content not shown.
- [unknown] **render.py** `ops/cli/render.py` — Listed in directory but no content shown; likely output formatting/rendering.
- [unknown] **serveconfig.py** `ops/cli/serveconfig.py` — Listed in directory but no content shown.
- [unknown] **sessions.py** `ops/cli/sessions.py` — Listed in directory but no content shown.
- [unknown] **systemd.py systemctl wrapper** `ops/cli/systemd.py` — Described in UPDATING.md as handling port_open, verdict, control, journal; content not shown.
- [unknown] **telemetry.py + telemetry.jsonl** `ops/cli/telemetry.py, ops/cli/telemetry.jsonl` — Telemetry module and a JSONL log file exist in the CLI directory; not mentioned in README/UPDATING architecture overview.
- [living] **README.md use guide** `ops/cli/README.md` — Explicitly states 'Nothing auto-starts at boot' as a policy decision by Tim on 2026-06-06.
- [living] **UPDATING.md maintenance guide** `ops/cli/UPDATING.md` — Lists constitution file ../AGENTS.md and architecture map; several listed modules (board, capabilities, clone, models, render, serveconfig, sessions, telemetry) are omitted from the architecture diagram.
- [dormant] **__pycache__** `ops/cli/__pycache__` — Compiled Python cache directory; artifact of prior runs, not source.
  - dormant-candidates: ops/cli/bench.py — truncated/half-built benchmark runner depending on external ~/vllm-env and ~/vllm-tests scripts not shown here · ops/cli/telemetry.py + ops/cli/telemetry.jsonl — present but unmentioned in README/UPDATING architecture; usage status unknown · ops/cli/__pycache__ — compiled cache, not active source
  - surprises: app.py docstring advertises `company health` and `company suites` (ALL-GREEN GATE), but README.md's 'Everyday commands' table only documents status/up/down — a command surface mismatch. · bench.py is truncated mid-function in the material, ending at `if not os.path.exists(script):` with no closing or body visible. · UPDATING.md's architecture diagram omits half the modules that exist in ops/cli/ (board, capabilities, clone, models, render, serveconfig, sessions, telemetry, bench). · telemetry.jsonl exists as a real log file inside the CLI package, yet telemetry.py is not mentioned in any architecture or command documentation shown.

### ops/systemd
- [living] **company-agent-sessions-exporter.service** `ops/systemd/company-agent-sessions-exporter.service` — Oneshot service exporting Claude Code jsonl to markdown; explicitly fired by a timer, not meant to run standalone.
- [living] **company-agent-sessions-exporter.timer** `ops/systemd/company-agent-sessions-exporter.timer` — Timer fires every 20 min; comment reveals it is bound to company.target (not timers.target) so 'company status' shows it as a managed member, matching ops/services.json.
- [living] **company-bridge.service** `ops/systemd/company-bridge.service` — HTTP API on port 8770; simple service with restart-on-failure.
- [living] **company-canvas.service** `ops/systemd/company-canvas.service` — Vite dev server on 127.0.0.1:5173; relies on linuxbrew node PATH override.
- [unknown] **company.target** `ops/systemd/company.target` — Referenced as WantedBy/PartOf target by multiple services; its own contents not shown.
- [unknown] **ops/services.json** `ops/systemd/company-agent-sessions-exporter.timer [Install] comment` — External registry mentioned as declaring this job's managed unit; not shown in material.
- [unknown] **runtime/bridge.py** `ops/systemd/company-bridge.service [Service] ExecStart` — Bridge service entrypoint; not shown in material.
- [unknown] **ops/agent_sessions_exporter.py** `ops/systemd/company-agent-sessions-exporter.service [Unit] Documentation` — Script the exporter service runs; not shown in material.
  - surprises: The timer install comment explicitly rejects timers.target in favor of company.target — an intentional policy so the timer is visible under 'company status' and matches ops/services.json. · company-canvas.service hardcodes a linuxbrew PATH override in the unit file rather than relying on system/user environment.

### voice
- [living] **voice/AGENTS.md constitution** `voice/AGENTS.md` — Claims a 2026-06-06 keeper convergence where lifecycle.py now drives systemd units through shared ops/cli/gpu.py core; explicitly marks VRAM arbitration as an 'open decision'.
- [living] **FROM-OPS-CLI-SESSION.md cross-team note** `voice/FROM-OPS-CLI-SESSION.md` — A handoff note from company-CLI builder to voice-stack asking inline replies; flags concurrent-editing risk on ops/services.json.
- [living] **lifecycle.py voice load/unload/status** `voice/lifecycle.py` — Generalised past STT ears to include 5 trial TTS engines; imports shared gpu.py rather than keeping a private VRAM map.
- [living] **loop.py conversation pipeline** `voice/loop.py` — Runs in .voice-venv Python 3.12 and reaches the 3.14 Suite brain via HTTP through the bridge, not by import.
- [living] **personas.py trial character registry** `voice/personas.py` — Personas are data records (brain string + voice_description + voice_shading) consumed by suite.py and TTS engines.
- [unknown] **trial_manifest.json** `voice/trial_manifest.json` — Listed in directory but no content shown; likely enumerates the trial engines/personas.
- [unknown] **say.py / speakable.py / stt.py / tts_service.py** `voice/say.py, voice/speakable.py, voice/stt.py, voice/tts_service.py` — Top-level voice modules present in directory listing; no excerpts provided to assess state.
- [unknown] **ears/ and engines/ subdirectories** `voice/ears/, voice/engines/` — Contain the 3 GPU ears and 5 trial TTS engines respectively; only referenced, not opened.
- [unknown] **ops/ subdirectory** `voice/ops/` — Contains systemd units for GPU ears; lifecycle.py is meant to drive these units.
- [unknown] **ref/ subdirectory** `voice/ref/` — Present in directory listing; purpose and contents not shown.
  - dormant-candidates: voice/ref/ — present in directory listing but no content or references shown; may be built-but-unused reference material. · voice/trial_manifest.json — listed but unopened; could be a manifest that is not yet wired into lifecycle.py or loop.py. · voice/ops/systemd/ units for GPU ears — constitution says they are 'not auto-started together' and policy is open; units may exist but not be fully wired to lifecycle load/unload.
  - surprises: A cross-team handoff file (FROM-OPS-CLI-SESSION.md) exists inside the voice module, suggesting the company CLI builder is treating voice as a peer territory rather than a subordinate — and is explicitly asking for inline replies. · The constitution says GPU ears 'can't all co-reside' and the resident-vs-on-demand-vs-swap policy is 'an open VRAM-arbitration decision' despite the 2026-06-06 'keeper convergence' claim — the policy is not actually closed. · loop.py runs in Python 3.12 while the Suite is 3.14, forcing the brain to be reached via HTTP bridge even for an internal voice pipeline.

### verdict_panels
- [living] **verdict_panels module directory** `verdict_panels/` — Only 3 entries: constitution file, pycache, and one panel implementation.
- [living] **AGENTS.md constitution** `verdict_panels/AGENTS.md` — Explicitly references a loader at runtime/verdict_panels.py and executor cognition.run_panel, neither of which are present in this material.
- [half-built] **registration_confirm panel** `verdict_panels/registration_confirm.py` — File is truncated mid-description string; actual seat implementations and combine logic are not visible in the excerpt.
- [unknown] **__pycache__ directory** `verdict_panels/__pycache__` — Compiled bytecode cache exists, suggesting the module has been imported/executed at least once.
  - dormant-candidates: verdict_panels/registration_confirm.py appears half-built/truncated — the description string is cut off and no seat code is visible · verdict_panels/ as a registry is dormant — only one panel file exists despite the constitution describing multiple panels as files
  - surprises: The constitution says 'add a panel = add a FILE', but only one panel file exists (registration_confirm) despite the module being described as a registry of panels. · AGENTS.md references runtime/verdict_panels.py as the loader and cognition.run_panel as the executor, but those are not included in the material for a 'full enumeration' of the top-level module. · The naming law explicitly distinguishes verdict_panels/ from panels/ because of a collision caught at build time — there is a documented parallel-system near-miss.

### types
- [living] **types/ directory listing** `DIR types/ (18 entries shown)` — 18 entries, but AGENTS.md says 9 SOUND + 4 RECONSTRUCT + 3 FUSE + 2 GHOST = 18 expected; the directory listing matches that count exactly.
- [living] **AGENTS.md constitution** `types/AGENTS.md (head)` — Claims every TYPE.id equals file stem and hollow trivial schemas are refused fail-loud; references 319 posts and HOLLOW-TYPES.md as evidence.
- [living] **_fusion_map.py disposition record** `types/_fusion_map.py (head)` — Underscore-prefixed so NOT discovered as a TYPE; explicitly prevents FUSE 3 from being silently imported as type files.
- [living] **agent.py TYPE** `types/agent.py (head)` — SOUND cloud type; data_schema/component_spec/status_values recovered from cvi_mine (read-only).
- [living] **blocker.py TYPE** `types/blocker.py (head)` — RECONSTRUCTED from hollow cloud type; includes resolution_class and mitigated intermediate state concepts.
- [living] **cognitive_guide.py TYPE** `types/cognitive_guide.py (head)` — SOUND cloud type; schema includes target_view, requires_decision, seen_by, priority, guide_content.
  - dormant-candidates: types/{research,diagnostic}.py — listed as GHOST +2 in _fusion_map.py ('registered, routing harvested — hand-made-powers-generator') but exist as .py files in the directory; their actual TYPE content was not shown in the material · types/_fusion_map.py — the FUSE 3 mapping is truncated mid-sentence ('each maps to where the concept was ALREAD'); the disposition record appears half-built
  - surprises: The directory contains both AGENTS.md (constitution) and __pycache__ (compiled bytecode) alongside type files, suggesting this registry is actually imported/executed as Python, not just parsed. · _fusion_map.py is explicitly underscore-prefixed to hide from discovery, yet it documents GHOST +2 (research, diagnostic) that ARE present as .py files in the directory listing — a contradiction between 'ghost' (DB row with no source file) and visible source files. · AGENTS.md says 7 HOLLOW types, but _fusion_map.py says RECONSTRUCT 4 + FUSE 3 + GHOST +2 = 9 special dispositions, not 7.

### tests
- [living] **tests/ directory** `DIR tests/ (120 entries shown)` — 120 entries shown but list ends mid-file at focus_ui_address_acceptance.py; actual count may exceed 120 or the display is truncated.
- [living] **tests/AGENTS.md constitution** `tests/AGENTS.md` — Self-describes as prescriptive constitution; claims live index of suites is auto-maintained in [[Company State]] and must not be duplicated here.
- [living] **act_endpoint acceptance suite** `tests/act_endpoint_acceptance.py` — Truncated head only; proves deterministic click-shaped {verb, address, args} dispatch bypasses prose parsing entirely.
- [unknown] **e-series test files with non-_acceptance suffix** `tests/e2_review_fixes.py, tests/e2_runtime.py, tests/e3_fabric.py, tests/e3_integration.py, tests/e4_registry.py, tests/e5_suite.py, tests/e6_governance.py, tests/first_purpose.py` — These 8 files break the stated naming convention 'tests/<name>_acceptance.py' in AGENTS.md; may be legacy, meta, or intentionally exempt.
- [unknown] **cc_gate_bar1_verification.py** `tests/cc_gate_bar1_verification.py` — Only file using '_verification' suffix instead of '_acceptance'; naming outlier among 120 entries.
  - dormant-candidates: tests/e2_review_fixes.py — non-conventional name and no head excerpt provided; may be stale or orphaned · tests/first_purpose.py — named like a module/entry point, not an acceptance suite; may be a leftover scaffold · tests/cc_gate_bar1_verification.py — only '_verification' file in a folder of '_acceptance' files; possibly an unfinished rename or one-off check
  - surprises: AGENTS.md declares every suite must be named tests/<name>_acceptance.py, yet 8 files (e2_review_fixes.py, e2_runtime.py, e3_fabric.py, e3_integration.py, e4_registry.py, e5_suite.py, e6_governance.py, first_purpose.py) and cc_gate_bar1_verification.py violate that convention. · The directory listing claims '120 entries shown' but the visible enumeration ends at focus_ui_address_acceptance.py, suggesting either truncation or a count mismatch in the census.

### surface
- [unknown] **surface directory** `surface/` — Only one entry shown ('app'); the directory is otherwise empty in the material, so we cannot tell if this is a full census or a truncated view.
- [unknown] **app entry inside surface** `surface/app` — Type not specified in the listing (file, directory, symlink, etc.); only the name 'app' is given.
  - surprises: A top-level module named 'surface' contains only a single entry 'app' with no further detail — unusually sparse for a 'full enumeration' census.

### store
- [living] **store directory root** `store/` — 17 entries shown; top-level module explicitly described as 'addressed store + resolver' implementing C1 and C4.
- [living] **store/AGENTS.md constitution** `store/AGENTS.md` — Prescriptive constitution; governs C1 and C4; mandates filesystem-first, Supabase-later, ext4-only, cross-process fcntl locks, fsync durability, provenance, echo-guard for chat source tags.
- [living] **fs_store.py filesystem resolver** `store/fs_store.py` — Head docstring claims it implements contracts.resolver.Resolver and that all fcntl/lockfile/fsync references stay inside this module; portability constraint for Supabase backend is stated but not verified in excerpt.
- [dormant] **retired file-backed vector namespace** `store/fs_store_file_vectors.retired.py` — Retired 2026-07-02 per Tim-authorized cutover; methods preserved COMMENTED OUT, zero influence, but .data/store/vectors/*.json files left intact at cutover.
- [living] **pg_marks.py Supabase mark backing** `store/pg_marks.py` — Mark API DB home; jsonb body for open-record extensibility; fail-loud on unreachable DB.
- [unknown] **pg_vectors.py Supabase vector backing** `store/pg_vectors.py` — Only referenced in retired file and AGENTS.md; actual content not shown in material.
- [unknown] **vector_index.py** `store/vector_index.py` — File exists in directory listing but no content excerpt provided.
- [unknown] **subdirectories: graphs, locks, memo, meta, objects, ref_history, refs, surfaced, vectors** `store/graphs, store/locks, store/memo, store/meta, store/objects, store/ref_history, store/refs, store/surfaced, store/vectors` — Runtime data directories implied by AGENTS.md (locks/, refs/, graphs/, surfaced/, objects/, vectors/) but contents not shown.
- [dormant] **__pycache__** `store/__pycache__` — Compiled Python cache; artifact of execution, not source.
- [dormant] **.gitkeep** `store/.gitkeep` — Empty placeholder to keep directory in git.
  - dormant-candidates: store/fs_store_file_vectors.retired.py — retired file-backed vector namespace, methods commented out, data files left intact · store/.gitkeep — empty git placeholder · store/__pycache__ — compiled cache artifact
  - surprises: A retired vector implementation file (fs_store_file_vectors.retired.py) explicitly preserves commented-out code and says the old .data/store/vectors/*.json files were left intact at cutover — a maintainer might expect retired code to be deleted or data migrated away. · The constitution strongly forbids storing under /mnt/c and mandates ext4, which is unusually specific and suggests a past real incident or near-miss. · Chat provenance echo-guard is described as failing open if source tag is missing — a silent failure mode for a guard that is framed as critical.

### stack_item_types
- [living] **AGENTS.md registry documentation** `stack_item_types/AGENTS.md` — Explicitly calls this the 5th standalone instance of a file-discovered registry mechanism, mirroring mark_types/item_types/relation_types/roles/projections.
- [half-built] **decision-sequence stack item type** `stack_item_types/decision-sequence.py` — Declared as the keystone/prove-on-one type already rendered to-bar by the host, but its row_fields dict is truncated/empty in the material and open_verb is not shown.
- [half-built] **explanation stack item type** `stack_item_types/explanation.py` — Has row_fields and unsettled_state, but open_verb is only a comment ('generic resolve/spotlight fallback') — not actually wired.
- [half-built] **presentation stack item type** `stack_item_types/presentation.py` — Same pattern as explanation: row_fields + unsettled_state present, open_verb is only a comment placeholder.
- [half-built] **verify-request stack item type** `stack_item_types/verify-request.py` — Explicitly differs clear-semantics from presentation/explanation (verdict vs acknowledge), but open_verb is only a comment placeholder.
- [unknown] **__pycache__ directory** `stack_item_types/__pycache__` — Listed as a directory entry but no contents provided.
  - dormant-candidates: explanation.py open_verb at stack_item_types/explanation.py — declared in comments but not wired as a dict · presentation.py open_verb at stack_item_types/presentation.py — declared in comments but not wired as a dict · verify-request.py open_verb at stack_item_types/verify-request.py — declared in comments but not wired as a dict · decision-sequence.py row_fields at stack_item_types/decision-sequence.py — truncated/empty in material; may be half-built
  - surprises: All four seeded type modules declare their types but leave open_verb as a comment-only placeholder rather than a concrete event/payload dict — despite AGENTS.md listing open_verb as part of the row shape. · decision-sequence.py is described as already rendered to-bar by the host, yet its row_fields dict appears empty/truncated in the material, making the 'live precedent' claim hard to verify from this excerpt. · AGENTS.md says 'Add a type = drop a file. Zero engine code' but also references a 5th standalone registry mechanism at runtime/stack_item_types.py — a runtime file that is not shown here.

### source_types
- [living] **source_types module directory** `source_types/` — Only 4 entries; the constitution claims this is a file-discovered registry where new source = new file, yet only two source-type row files exist.
- [living] **AGENTS.md constitution** `source_types/AGENTS.md` — Explicitly promises an auto-reflected 'Agent-authored entries' section, but that section is empty (only HTML comment, zero lines).
- [living] **claude_code source-type row** `source_types/claude_code.py` — Default origin; join_keys [author, path, time] are declared as the GitHub fold-in seam, but no github.py row exists yet.
- [living] **cvi_mine source-type row** `source_types/cvi_mine.py` — References a migration operation and an organ-studies doc that are not present in this material.
- [unknown] **__pycache__ directory** `source_types/__pycache__` — Listed but not inspected; likely compiled bytecode cache for the two .py row files.
- [dormant] **Agent-authored entries section** `source_types/AGENTS.md under '## Agent-authored entries (auto-reflected)'` — Section is described as 'created live by the create face; one line per entry' but contains only the HTML comment and zero actual entries.
  - dormant-candidates: Agent-authored entries section in source_types/AGENTS.md — built scaffolding (HTML comment + instructions) but no entries populated. · Future github.py source-type row — repeatedly referenced as the planned next source but no file exists in source_types/.
  - surprises: The constitution's 'Agent-authored entries (auto-reflected)' section is completely empty despite being described as live-created and drift-home acceptance green. · Only two source-type rows exist (claude_code, cvi_mine) even though the design explicitly invites future rows like github.py and frames source_types as an extensible registry. · The directory census is 'full enumeration' but shows no runtime/source_types.py or runtime/cc_board.py here — those are referenced as consumers but live elsewhere.

### skills
- [living] **skills/ module constitution** `skills/AGENTS.md` — Explicitly claims skills self-register by file drop-in and are addressable as skill://<id>; compares itself to roles + node-types registries.
- [living] **summarize skill** `skills/summarize.py` — Called the 'seed skill' and demonstrative first member; only named skill whose full content is not shown in the material.
- [living] **extract_decisions skill** `skills/extract_decisions.py` — Agent-authored via create_skill with no operator approval; git-committed [self-apply] and live with 'NO surfaced item'.
- [half-built] **corpus_pipeline composition skill** `skills/corpus_pipeline.py` — Head is truncated mid-sentence ('it never instructs emitting resolve/approve/dispatch and never launches claude -p'); full SKILL dict not shown, so completeness is unknown.
- [half-built] **inversion_query composition skill** `skills/inversion_query.py` — SKILL dict starts but `content` is cut off after an opening parenthesis; the actual recipe text is not present in the material.
- [half-built] **map_reduce_composition skill** `skills/map_reduce_composition.py` — SKILL dict begins and `content` key is opened with a trailing quote, but the value is truncated; full recipe not shown.
- [unknown] **patterned_visibility skill/file** `skills/patterned_visibility.py` — Listed in directory but no excerpt provided; cannot determine state or content from material.
- [unknown] **__pycache__ directory** `skills/__pycache__` — Standard Python bytecode cache; no content shown.
  - dormant-candidates: skills/patterned_visibility.py — listed in skills/ but no excerpt or mention in AGENTS.md's enumerated live/composition skill lists (where: skills/patterned_visibility.py) · skills/inversion_query.py — SKILL dict present but `content` value truncated/unshown; may be part-built (where: skills/inversion_query.py) · skills/map_reduce_composition.py — SKILL dict present but `content` value truncated/unshown; may be part-built (where: skills/map_reduce_composition.py) · skills/corpus_pipeline.py — head only, full SKILL dict not shown; may be part-built (where: skills/corpus_pipeline.py)
  - surprises: AGENTS.md says there are two live skills (summarize, extract_decisions) and references 'The COMPOSITION skills (AK3)' as a separate category, but the directory actually contains at least four composition-skill files (corpus_pipeline.py, inversion_query.py, map_reduce_composition.py, patterned_visibility.py) — more than the constitution's framing suggests. · AGENTS.md claims 'tests/skills_contexts_acceptance.py asserts each is reflected here', but the acceptance test file itself is not included in the material, so the assertion cannot be verified. · The constitution text is cut off mid-sentence at 'when to use whic' — the full governance of composition skills is not visible.

### scripts
- [unknown] **migration script for cc_channels to session_channels** `scripts/migrate_cc_channels_to_session_channels.py` — One-shot migration script; head only, so we cannot see if it is wired into CI, Makefile, or documented runbook.
- [dormant] **retired cc_channels named-channel store** `.data/channels/_channels/<id>.json` — Described as 'retired' source store; migration folds it into session_channels, implying it is no longer the live store.
- [living] **session_channels named-channel store** `<COMPANY_STORE>/agent_sessions/channels.jsonl` — Target ONE named-channel store; migration creates channels here via create_channel/add_member/archive_channel.
- [unknown] **create_channel helper** `referenced in scripts/migrate_cc_channels_to_session_channels.py` — Not defined in the excerpt; presumably lives in a channel/session module elsewhere.
- [unknown] **add_member helper** `referenced in scripts/migrate_cc_channels_to_session_channels.py` — Not defined in the excerpt; presumably lives in a channel/session module elsewhere.
- [unknown] **archive_channel helper** `referenced in scripts/migrate_cc_channels_to_session_channels.py` — Not defined in the excerpt; presumably lives in a channel/session module elsewhere.
  - dormant-candidates: cc_channels store at .data/channels/_channels/<id>.json — retired source store, only accessed by a one-shot migration. · member-kind extension field — described as 'later field', implying the current session_channels schema has a half-built member representation.
  - surprises: scripts/ contains exactly one file and it is a migration script — no other utilities, tests, or tooling live at top level. · Migration stores members as raw handles, not agent-session UUIDs, with a note that 'member-kind extension is a later field' — suggests the data model is intentionally incomplete/forward-stubbed. · The script is idempotent by catching duplicate-create failures rather than pre-checking existence, which is a 'fail loud then swallow' pattern.

### scope_grammar
- [living] **AGENTS.md constitution** `scope_grammar/AGENTS.md` — Self-describes as the single registered grammar for scope vocabulary, explicitly claims to unify three previously unparsed grammars (A verb-first, C verb-last, B permission='use').
- [living] **admin verb row** `scope_grammar/admin.py` — Registered verb 'admin' with reversible=False; docstring says it manages container settings/members.
- [living] **approve verb row** `scope_grammar/approve.py` — Registered verb 'approve' with reversible=False; docstring references example 'approve:financing_proposals'.
- [living] **create verb row** `scope_grammar/create.py` — Registered verb 'create' with reversible=True — only verb in shown material marked reversible.
- [living] **deploy verb row** `scope_grammar/deploy.py` — Registered verb 'deploy' with reversible=False; docstring ties it to L5 delegation scope 'deploy:langgraph'.
- [unknown] **execute verb file** `scope_grammar/execute.py` — Listed in directory but no excerpt provided; cannot confirm SCOPE_VERB contents or state.
- [unknown] **manage verb file** `scope_grammar/manage.py` — Listed in directory but no excerpt provided; 'manage' is not mentioned in the constitution's base-five list (read/write/execute/admin/approve), so its role is unclear.
- [unknown] **read verb file** `scope_grammar/read.py` — Listed in directory but no excerpt provided; constitution says 'read' is one of A's base five verbs.
- [unknown] **write verb file** `scope_grammar/write.py` — Listed in directory but no excerpt provided; constitution says 'write' is one of A's base five verbs.
- [dormant] **__pycache__ directory** `scope_grammar/__pycache__` — Compiled bytecode cache — artifact of execution, not source registry content.
  - dormant-candidates: scope_grammar/manage.py — present in directory listing but not referenced in constitution's verb set; may be built-but-unwired or a leftover · scope_grammar/__pycache__ — generated artifact, not living registry content
  - surprises: Directory lists 'manage.py' but the constitution only names A's base five verbs as read/write/execute/admin/approve — 'manage' is not in that set and is not discussed in the shown material. · The constitution says 'B's permission=\'use\'' is one of three unparsed grammars this registry unifies, yet no 'use' verb file is shown or mentioned. · Only 'create' is marked reversible=True among the shown verb rows; the constitution does not explain why create is reversible while admin/approve/deploy are not.

### schemas
- [unknown] **schemas directory** `schemas/` — Only one entry shown; the directory is claimed to have a 'full enumeration' census but material only lists a single child, so coverage is incomplete.
- [unknown] **vi-vision child** `schemas/vi-vision` — Name suggests a vision-related schema package, but no contents or type are provided.
  - surprises: Census is described as 'full enumeration' yet only one entry (vi-vision) is shown in the material.

### runtime
- [living] **runtime directory listing** `DIR runtime/ (104 entries shown)` — 104 named modules; no subdirectory nesting except capabilities/ and __pycache__; everything is flat at runtime root.
- [living] **AGENTS.md constitution** `runtime/AGENTS.md` — Self-describes as prescriptive constitution; explicitly names the decision→implementation wire through implement.py + dispatch_decision launching Claude Code headlessly.
- [living] **access.py effective-access resolver** `runtime/access.py` — Claims to be the single shared function projected to both MCP and UI; docstring is truncated mid-sentence at 'remote.py'\'.
- [living] **activation.py activation contexts substrate** `runtime/activation.py` — Introduces background/sense/rollup activation contexts as declared data + real entry points; docstring truncated.
- [dormant] **activation_driver.py always-on caller** `runtime/activation_driver.py` — File header explicitly labels itself 'THE ALWAYS-ON CALLER (DORMANT)' — built but not wired/running.
- [unknown] **.gitkeep** `runtime/.gitkeep` — Empty placeholder; no content beyond presence.
- [unknown] **capabilities subdirectory** `runtime/capabilities` — Listed as directory but no material provided; contents not enumerated.
- [unknown] **render_declarations.json** `runtime/render_declarations.json` — JSON file paired with render_declaration.py; no content shown.
  - dormant-candidates: activation_driver.py — 'THE ALWAYS-ON CALLER (DORMANT)' at runtime/activation_driver.py · render_declarations.json — exists at runtime/render_declarations.json but no content or wiring shown
  - surprises: activation_driver.py is explicitly marked '(DORMANT)' in its own header despite being the 'always-on caller' — a built-but-not-running core loop. · The runtime module is extremely flat: 104 files at the root with only capabilities/ as a visible subpackage, suggesting either deliberate flatness or accumulation without reorganization. · AGENTS.md claims a single shared access resolver projected to both MCP and UI, but the access.py excerpt is truncated and we have not yet seen the MCP/UI consumption sites to verify the projection.

### routines
- [half-built] **completion_poke routine module** `routines/completion_poke.py` — Docstring fully describes adversarial purpose and firing methods, but only the head is shown — no visible ROUTINE dict or implementation body in the excerpt.
- [half-built] **dragnet_freshness routine module** `routines/dragnet_freshness.py` — ROUTINE dict begins but is truncated mid-label; docstring claims ownership of deep staleness check and operator-gated rebake, but implementation not visible.
- [half-built] **guide_freshness routine module** `routines/guide_freshness.py` — Docstring frames recurring re-authoring of stale guides as proposals; ROUTINE dict starts but is cut off mid-label, so living implementation is not confirmed.
- [half-built] **launch-surfaces routine module** `routines/launch-surfaces.py` — Has the most complete visible ROUTINE dict (id, label, description, prompt), but prompt string is truncated mid-URL and no execution code is shown.
- [unknown] **self_status routine module** `routines/self_status.py` — Listed in directory but no excerpt provided; existence only.
- [living] **__pycache__ directory** `routines/__pycache__` — Compiled bytecode cache implies the modules have been imported/executed at least once.
  - dormant-candidates: completion_poke.py at routines/completion_poke.py — fully described adversarial routine, but visible material is only docstring; may be doc-only or implementation truncated. · dragnet_freshness.py at routines/dragnet_freshness.py — ROUTINE dict truncated mid-label; deep staleness logic not visible. · guide_freshness.py at routines/guide_freshness.py — ROUTINE dict truncated mid-label; re-authoring logic not visible. · self_status.py at routines/self_status.py — no excerpt at all; present but unexamined.
  - surprises: All four excerpted routines are documented as fireable via both a `routines` MCP tool and `routine_runner.fire(...)`, but no runner/tool implementation is included in the material. · completion_poke.py is described as a hard-coded instantiation that is already superseded by a generalized composable version — yet it still exists as a top-level routine. · launch-surfaces.py's prompt contains a literal curl command with `http://localhost` and a shell format string, embedded in a Python string — unusual mixing of shell and prompt.

### roles
- [living] **roles/ directory** `roles/ (48 entries shown)` — 48 entries — one of the largest top-level modules; appears to be the self-registering role registry for the cognition system.
- [living] **AGENTS.md constitution** `roles/AGENTS.md (head)` — Explicitly claims roles mirror node-types self-registration; references legacy hardcoded registries in suite.py and cognition.py that are now superseded.
- [living] **atlas_linker role** `roles/atlas_linker.py (head)` — Authored-cognition role (#58 direct-create); output schema AtlasLinkerOut declares tags/atlas_notes/summary fields.
- [living] **check role** `roles/check.py (head)` — Declared as part of listening cast but the actual staged-part chaining executor is flagged as downstream (G3/G4) — role exists, wiring is elsewhere/not shown.
- [living] **complete_text role** `roles/complete_text.py (head)` — Passthrough text completion role; appears to be a union/A2 path for plain text output.
- [living] **confirm_registration role** `roles/confirm_registration.py (head)` — Mirrors verify_jury.py exactly per its own docstring — a duplicated pattern across two files.
  - dormant-candidates: op-axis differentiation in AGENTS.md — built into schema but unused because all roles are byte-identical `generate` (roles/AGENTS.md head) · check.py staged-part chaining — role is built but the G3/G4 executor that fires it is downstream and not shown here (roles/check.py head) · embed.py — listed in directory but no excerpt provided; name suggests an embed op role that may be dormant relative to the 'every role is generate' claim
  - surprises: AGENTS.md says every role today is byte-identically `op: generate` (default), making the op-axis currently a no-op data field despite being architecturally significant. · check.py declares a dependency on a forming answer and ground output, but explicitly notes the chainer that actually fires it is 'G3 / G4 — flagged downstream' — the role is declared but the execution wiring is not in this file. · confirm_registration.py says it 'MIRRORS roles/verify_jury.py exactly' — a self-acknowledged duplication between two role files.

### relation_types
- [living] **relation_types module directory** `relation_types/` — 8 entries; file-per-entry registry pattern matching roles/skills/projections/node-types.
- [living] **AGENTS.md constitution** `relation_types/AGENTS.md` — Self-describes as file-discovered registry; lists 4 live relation-types but material shows 6 .py files.
- [living] **contradicts relation-type** `relation_types/contradicts.py` — SEED file; well-formed RELATION_TYPE dict; near/far both 'principles'.
- [living] **depends_on relation-type** `relation_types/depends_on.py` — Agent-authored (#58 declarative-direct); has inverse 'unlocks' but no near/far projection spaces set.
- [living] **fragment_of relation-type** `relation_types/fragment_of.py` — SEED file; exercises inverse field with 'has_fragment'; near='topics'.
- [living] **precedes relation-type** `relation_types/precedes.py` — Agent-authored (#58 declarative-direct); has inverse 'follows' but no near/far projection spaces set.
- [unknown] **principle_beneath relation-type** `relation_types/principle_beneath.py` — File listed in directory but no excerpt provided in material.
- [unknown] **sibling relation-type** `relation_types/sibling.py` — File listed in directory but no excerpt provided in material.
- [dormant] **__pycache__ directory** `relation_types/__pycache__` — Compiled bytecode cache; artifact of execution, not a registry entry.
  - dormant-candidates: principle_beneath.py — listed in directory but not mentioned in AGENTS.md 'live set' list (relation_types/principle_beneath.py) · sibling.py — listed in directory but not mentioned in AGENTS.md 'live set' list (relation_types/sibling.py) · depends_on.py — agent-authored, has no near/far spaces, may be half-wired for the inversion-finder (relation_types/depends_on.py) · precedes.py — agent-authored, has no near/far spaces, may be half-wired for the inversion-finder (relation_types/precedes.py)
  - surprises: AGENTS.md lists only 4 relation-types as 'the live set' but the directory contains 6 .py relation-type files (contradicts, depends_on, fragment_of, precedes, principle_beneath, sibling). · depends_on.py and precedes.py reference 'runtime/relation_type.py' and 'relation_type/AGENTS.md' (singular) while the actual paths are plural 'relation_types/'. · depends_on and precedes lack near/far projection spaces, which the constitution says are optional but the inversion-finder find_relations uses near/far for set-operation.

### recollection
- [living] **recollection top-level directory** `recollection/` — 27 entries; appears to be a full project root with dual plugin formats, MCP server, and debug log present in working tree.
- [living] **.gitignore** `recollection/.gitignore` — Ignores *.log and tmp/ but mcp_registration_debug.log and tmp/ status are not shown; src/version.ts is generated by scripts/generate-version.js.
- [living] **.mcp.json** `recollection/.mcp.json` — MCP server registration points at ./cli/mcp-server-wrapper.js and names three env vars; no evidence shown that wrapper file exists or env is set.
- [living] **.version-bump.json** `recollection/.version-bump.json` — Version bump config references bump-version.sh and version.ts, neither of which appear in the 27-entry directory listing.
- [living] **CHANGELOG.md** `recollection/CHANGELOG.md` — Latest entry is [1.4.2] dated 2026-05-21; describes a fixed silent summarization crash and mentions Codex summarization work cut off mid-sentence.
  - dormant-candidates: bump-version.sh referenced in .version-bump.json but not present in recollection/ listing · version.ts referenced in .version-bump.json and .gitignore but not present in recollection/ listing (may be generated) · src/version.ts generation script scripts/generate-version.js referenced but script directory content not shown
  - surprises: mcp_registration_debug.log exists in the project root despite .gitignore ignoring *.log, suggesting it may have been force-added or is a recent untracked artifact. · .version-bump.json references bump-version.sh and version.ts, but neither appears in the 27-entry directory listing. · The project maintains both .claude-plugin and .codex-plugin directories, indicating dual AI IDE plugin packaging.

### projections
- [living] **AGENTS.md constitution** `projections/AGENTS.md` — Explicitly enumerates live projections and references an acceptance test that asserts each projection is reflected here.
- [living] **claimed_status projection** `projections/claimed_status.py` — Fully declared PROJECTION dict; id matches file stem; enum is categorical (no embed).
- [half-built] **code_archaeology projection** `projections/code_archaeology.py` — PROJECTION dict is truncated mid-declaration: only 'id': 'code_archaeology' is visible; rest of schema not shown.
- [half-built] **common_knowledge projection** `projections/common_knowledge.py` — Commentary describes a seam design but no visible PROJECTION dict; file appears to be prose-only in the excerpt.
- [half-built] **design_intent projection** `projections/design_intent.py` — PROJECTION dict is cut off mid-string in the desc field; id matching file stem is asserted but not visible in excerpt.
- [living] **directory listing** `projections/` — 16 entries; AGENTS.md claims one self-registering file per lens, mirroring roles/skills/nodes registries.
  - dormant-candidates: projections/common_knowledge.py — no visible PROJECTION dict in excerpt; appears to be a design-commentary stub rather than a registered lens · projections/code_archaeology.py — PROJECTION dict is cut off after id; may be incomplete or the excerpt is hiding the rest · projections/design_intent.py — PROJECTION dict is cut off mid-desc string; declaration incomplete in excerpt
  - surprises: AGENTS.md says 'id MUST equal the file stem' and references tests/projections_acceptance.py, but the material shows design_intent.py's docstring typo 'projection/design_intent.py' (singular directory) and references 'runtime/projection.py' (singular) instead of 'runtime/projections.py' (plural) used by other files. · common_knowledge.py is described as a projection/space but the excerpt contains no PROJECTION dict at all — only a long comment about the recollection seam. · code_archaeology.py's PROJECTION dict is truncated immediately after id, despite the file being listed as a top-level projection entry.

### platforms
- [living] **platforms/ module directory** `platforms/` — Top-level module containing 6 entries; constitution says each platform is one row file with PLATFORM dict.
- [living] **AGENTS.md constitution** `platforms/AGENTS.md` — Prescriptive constitution enforcing DATA-ONLY discipline; references F-FIX-10, PG2, F-FIX-12, PG-D5, and a 2026-06-14 ROW-PURITY tightening.
- [living] **_wiring.py bootstrap module** `platforms/_wiring.py` — Sanctioned non-row file holding the head_builder thunk to keep row files pure; registry file-discovery skips it due to _ prefix.
- [living] **claude_code.py platform row** `platforms/claude_code.py` — Instance #1 of Mirror-Registry; described as the clean template for generalization-proof.
- [living] **codex_cli.py platform row** `platforms/codex_cli.py` — Instance #3 and first with a live in-fabric consumer; drives codex exec as a producer on OpenAI/ChatGPT token pool.
- [half-built] **gh_cli.py platform row** `platforms/gh_cli.py` — Instance #2 registered to prove the lift, but explicitly described as 'registered-only (nothing drives it yet)'.
- [unknown] **__pycache__ directory** `platforms/__pycache__` — Compiled Python cache; no content shown, cannot judge state beyond existence.
  - dormant-candidates: platforms/gh_cli.py — registered-only, nothing drives it yet (head excerpt states this explicitly)
  - surprises: The constitution claims the only legitimate platform-name strings live in platforms/ and row nested data, yet the acceptance leak-gate greps engine/rules/adapters for them — implying a build-time enforcement mechanism exists that is not itself shown in the material. · gh_cli.py is registered but explicitly not driven by anything, while codex_cli.py is already live — the second instance is a proof artifact rather than a functional platform. · The head_builder thunk moved from claude_code.py to _wiring.py as part of a 2026-06-14 purity refactor, suggesting earlier architecture had non-pure rows.

### panels
- [living] **panels module constitution** `panels/AGENTS.md` — Explicitly forbids enumerating the live panel set here; live set is owned by Company Map registry only.
- [living] **settings panel JSON** `panels/settings.json` — Declarative panel with hardcoded select options for presence_mode and model; constitution says registry should override guessed options, but this file shows static options.
- [living] **presence_mode field** `panels/settings.json → fields[0]` — Select options are hardcoded (listening, text-only, background, focus, walkthrough, watch-and-react, decide-for-me, off) rather than sourced from registry.
- [living] **model field** `panels/settings.json → fields[1]` — Select options are hardcoded model identifiers including local and cloud variants; truncated mid-list in material.
  - dormant-candidates: Registry-override behavior for panel select options — declared in panels/AGENTS.md but not evidenced in panels/settings.json
  - surprises: Constitution says registry overrides select options with real registered values, but settings.json contains hardcoded option lists — the registry override mechanism is asserted but not demonstrated in the only panel shown. · Only one panel file (settings.json) is present despite the module being described as the home for all declarative UI panels; AGENTS.md explicitly refuses to enumerate the live set.

### orienteering
- [living] **AGENTS.md constitution** `orienteering/AGENTS.md` — Declares itself descriptive/terrain ledger but also embeds a prescriptive runtime drift detector with exact gates, suggesting dual role.
- [living] **INDEX.md terrain index** `orienteering/INDEX.md` — Claims table is generated from entry frontmatter, but the material cuts off mid-sentence; generation mechanism not shown.
- [living] **_orbit-dispositions.json orphan-routes registry** `orienteering/_orbit-dispositions.json` — Self-described as 'deliberately out of the terrain ledger' registry with tag vocabulary and path rows; only 3 paths shown, more may exist.
- [unknown] **orienteering_drift.py drift detector** `runtime/orienteering_drift.py (referenced in AGENTS.md)` — Declared as BUILT into coherence substrate, but the actual file is not in the provided material.
- [unknown] **tests/orienteering_drift_acceptance.py** `tests/orienteering_drift_acceptance.py (referenced in AGENTS.md)` — Referenced as the acceptance test for the exact 'entry-path-missing' gate; file not shown.
- [unknown] **entries/ directory** `orienteering/entries/` — Said to contain one terrain-entry per thing, but no entries are shown.
- [unknown] **templates/ directory** `orienteering/templates/` — Said to hold entry.md template; not shown.
- [unknown] **bases/ directory** `orienteering/bases/` — Listed in directory but no content or references shown.
  - dormant-candidates: orienteering/bases/ — listed as a directory but no content or references anywhere in the material (orienteering/AGENTS.md, INDEX.md, _orbit-dispositions.json). · orienteering/templates/entry.md — referenced as the template for new entries but the file itself is not shown; may be present but unverified.
  - surprises: The constitution AGENTS.md is tagged 'prescriptive' in its own frontmatter while the body repeatedly insists the module is 'descriptive, not prescriptive'. · A 'drift detector' is declared BUILT and wired into 'company coherence' / 'company suites', but the runtime/ and tests/ files are not included in the material. · _orbit-dispositions.json uses a tag vocabulary that includes 'dead-twin' and 'empty', but only toolchain/cache tags are actually populated in the visible rows.

### ops
- [living] **ops/ directory root** `ops/ (79 entries shown)` — Top-level operational module with 79 entries; explicitly described as the self-describing command center for an AI-run system.
- [living] **AGENTS.md constitution** `ops/AGENTS.md` — Declares ops as 'operational control' and first instantiation of a general console; explicitly warns against duplicate command centers and lists future view-modes (models/VRAM, cognitive-layers, RHM/modes, data/memory, jobs/cron) that are not yet present.
- [living] **BOOT-RUNBOOK.md** `ops/BOOT-RUNBOOK.md` — Assembled 2026-06-20 from empirically-verified live state, not docs; explicitly supersedes WINDOWS-BOOT.md as stale.
- [living] **STARTUP.md** `ops/STARTUP.md` — Documents the 'nothing auto-starts at boot' policy (Tim 2026-06-06) and the company CLI as single brain; old vllm-stack shimmed to it.
- [dormant] **WINDOWS-BOOT.md** `ops/WINDOWS-BOOT.md` — Explicitly flagged as stale/superseded by BOOT-RUNBOOK.md; still present in directory listing.
- [living] **services.json registry** `ops/services.json` — Described as the self-describing registry of truth for every service; actual contents not shown in material.
- [living] **systemd directory** `ops/systemd/` — Holds canonical systemd unit copies; muscle behind the company console.
- [living] **company console / CLI** `ops/company / ops/cli` — Symlinked onto PATH as `company`; described as the one command center. `ops/cli` likely contains implementation but contents not shown.
- [unknown] **model_capabilities.json** `ops/model_capabilities.json` — Present in directory but no content shown; likely static model capability registry.
- [unknown] **assets directory** `ops/assets` — Present in directory; purpose not described in shown material.
- [unknown] **hooks directory** `ops/hooks` — Present in directory; likely git/commit hooks but no content shown.
- [living] **__pycache__ directory** `ops/__pycache__` — Compiled Python cache; indicates active Python execution in ops.
- [unknown] **agent_sessions_exporter.py / importer.py** `ops/agent_sessions_exporter.py, ops/agent_sessions_importer.py` — Pair of scripts for exporting/importing agent sessions; no content shown.
- [unknown] **backfill_provenance.py** `ops/backfill_provenance.py` — Named like a one-off migration/backfill script; may be dormant after use.
- [unknown] **backwrite_fusion_path.py / backwrite_fusion_record.py** `ops/backwrite_fusion_path.py, ops/backwrite_fusion_record.py` — Named like backfill/migration scripts for fusion records; no content shown.
- [unknown] **build_embeddings.py / build_file_meta.py** `ops/build_embeddings.py, ops/build_file_meta.py` — Build scripts; likely part of indexing pipeline but contents not shown.
- [unknown] **claude_sessions_reindex.py / wire_substrate_claude_sessions.py** `ops/claude_sessions_reindex.py, ops/wire_substrate_claude_sessions.py` — Scripts around Claude session indexing/wiring; substrate wiring script may be setup-time.
- [unknown] **code_archaeology.py** `ops/code_archaeology.py` — Unusual name; likely introspection/discovery tool for the codebase.
- [unknown] **commit_queue.py** `ops/commit_queue.py` — Likely manages batched/automated commits; no content shown.
- [unknown] **doc_review_server.py** `ops/doc_review_server.py` — Server for document review; not referenced in constitution/startup docs shown.
- [unknown] **dragnet_determine.py / dragnet_extract.py** `ops/dragnet_determine.py, ops/dragnet_extract.py` — Dragnet extraction pipeline scripts; no content shown.
- [unknown] **embed_extractions.py / embed_status.py** `ops/embed_extractions.py, ops/embed_status.py` — Embedding-related operational scripts.
- [unknown] **extraction_audit_run.py** `ops/extraction_audit_run.py` — Audit runner for extractions; likely invoked periodically.
- [unknown] **fabric_clone_probe.py / fabric_live_probe_r1.py / fabric_live_probe_r34.py / fabric_live_probe_wake.py / fabric_openai_adapter.py** `ops/fabric_clone_probe.py, ops/fabric_live_probe_r1.py, ops/fabric_live_probe_r34.py, ops/fabric_live_probe_wake.py, ops/fabric_openai_adapter.py` — Multiple fabric probe scripts with model-specific variants (r1, r34) and wake logic; suggests an evolving probe harness.
- [unknown] **graph_projection.py** `ops/graph_projection.py` — Graph projection utility; no content shown.
- [unknown] **ledger_* scripts (many)** `ops/ledger_build.py, ledger_capabilities.py, ledger_changes.py, ledger_coverage_audit.py, ledger_fact_edges.py, ledger_interpret.py, ledger_interpret_codex.py, ledger_interpret_codex_drive.sh, ledger_interpret_drive.sh, ledger_interpret_ollama.py, ledger_interpret_producer.py, ledger_metadata.py` — Large ledger subsystem with multiple interpreters and shell drivers; breadth suggests active but possibly fragmented tooling.
- [unknown] **map_interface.py** `ops/map_interface.py` — Likely the runtime interface to the Company Map; not referenced in shown docs.
- [dormant] **measure_8bit_vs_bf16.py** `ops/measure_8bit_vs_bf16.py` — Named like a one-off benchmark script; likely not part of daily operations.
- [dormant] **migrate_* scripts (many)** `ops/migrate_board_from_cvi.py, migrate_circuit_from_cvi.py, migrate_container_from_cvi.py, migrate_edges_from_cvi.py, migrate_identity_from_cvi.py, migrate_recollection_full.py, migrate_recollection_to_supabase.py, migrate_vectors_to_supabase.py` — Numerous migration scripts from 'cvi' and to 'supabase'; strongly suggest one-off or already-run migrations now dormant.
- [unknown] **owui_fabric_bridge.py / owui_fusion_up.sh / owui_room.py / owui_to_fork_listen.py / owui_to_fork_watch.py** `ops/owui_fabric_bridge.py, ops/owui_fusion_up.sh, ops/owui_room.py, ops/owui_to_fork_listen.py, ops/owui_to_fork_watch.py` — OpenWebUI integration scripts including bridge, room, and fork watch/listen; active-looking but no content shown.
- [unknown] **render_declared_stream.py** `ops/render_declared_stream.py` — Stream rendering utility; no content shown.
- [unknown] **rerank.py / serve_rerank.py / serve_rerank.sh** `ops/rerank.py, ops/serve_rerank.py, ops/serve_rerank.sh` — Reranking service with server and shell launcher; likely a declared service in services.json.
- [dormant] **seed_edge_kinds.py / seed_self.py** `ops/seed_edge_kinds.py, ops/seed_self.py` — Named like one-time seeding scripts; likely run once at setup.
- [unknown] **serve_model.sh / serve_pplx_embed.py / serve_pplx_embed.sh / serve_rerank.sh** `ops/serve_model.sh, ops/serve_pplx_embed.py, ops/serve_pplx_embed.sh, ops/serve_rerank.sh` — Service launcher scripts for models and perplexity embeddings; likely wired into systemd/services.json.
- [unknown] **stt_openai_shim.py / tts_openai_shim.py** `ops/stt_openai_shim.py, ops/tts_openai_shim.py` — OpenAI-compatible shims for speech-to-text and text-to-speech.
- [unknown] **surface_server.py** `ops/surface_server.py` — Server named 'surface'; no further context in shown material.
- [unknown] **sync_durability.py** `ops/sync_durability.py` — Durability sync script; likely related to persistence guarantees.
- [unknown] **transcript_search.py** `ops/transcript_search.py` — Search utility for transcripts.
- [unknown] **ts_extract.js** `ops/ts_extract.js` — Only .js file in ops; TypeScript extraction helper.
- [unknown] **verify_extraction** `ops/verify_extraction` — No extension — could be script or directory; purpose unclear from listing.
- [half-built] **_finish_pplx_wire.sh** `ops/_finish_pplx_wire.sh` — Leading underscore and 'finish' in name suggests a setup/todo script that may be partially complete or one-off.
  - dormant-candidates: ops/WINDOWS-BOOT.md — explicitly superseded by BOOT-RUNBOOK.md · ops/measure_8bit_vs_bf16.py — one-off benchmark · ops/migrate_board_from_cvi.py — cvi→supabase migration · ops/migrate_circuit_from_cvi.py — cvi→supabase migration · ops/migrate_container_from_cvi.py — cvi→supabase migration · ops/migrate_edges_from_cvi.py — cvi→supabase migration · ops/migrate_identity_from_cvi.py — cvi→supabase migration · ops/migrate_recollection_full.py — recollection migration · ops/migrate_recollection_to_supabase.py — recollection→supabase migration · ops/migrate_vectors_to_supabase.py — vectors→supabase migration · ops/seed_edge_kinds.py — one-time seed script · ops/seed_self.py — one-time seed script · ops/_finish_pplx_wire.sh — setup/finish script, possibly one-off
  - surprises: ops/WINDOWS-BOOT.md is explicitly called stale/superseded by BOOT-RUNBOOK.md but remains in the directory. · A large cluster of ledger_* scripts (11+) exists with multiple interpreter variants and shell drivers, suggesting possible fragmentation or parallel implementations. · A large cluster of migrate_* scripts (9) from 'cvi' to 'supabase' suggests a major past migration; many may be dormant but are still present. · ops/measure_8bit_vs_bf16.py is a benchmark script sitting in the operational top-level, not obviously part of daily runtime. · ops/verify_extraction has no file extension, making its nature ambiguous. · ops/ts_extract.js is the only JavaScript file in an otherwise Python/shell-heavy ops directory.

### operator_memory
- [living] **operator_memory module directory** `operator_memory/ (31 entries shown)` — 31 named .py files plus AGENTS.md and __pycache__; each .py appears to be a single MEMORY row file.
- [living] **AGENTS.md constitution** `operator_memory/AGENTS.md (head)` — Declares itself the file-discovered OPERATOR-MEMORY registry; references a loader and MCP face that are not shown in the material.
- [half-built] **ai_supplies_domain_knowledge memory row** `operator_memory/ai_supplies_domain_knowledge.py (head)` — MIGRATED but 'awaits Tim's confirmation'; status not shown in truncated head, but comment says unconfirmed.
- [half-built] **big_beats memory row** `operator_memory/big_beats.py (head)` — PROPOSED from a correction and explicitly 'awaits Tim's confirm'; status='proposed' shown.
- [half-built] **confirm_before_writing memory row** `operator_memory/confirm_before_writing.py (head)` — MIGRATED but 'awaits Tim's confirmation'; status='proposed' shown.
- [living] **easy_decision_surface memory row** `operator_memory/easy_decision_surface.py (head)` — Truncated mid-evidence quote; appears confirmed as a GC15 row.
- [dormant] **GC14 self-injection mechanism reference** `operator_memory/AGENTS.md (head)` — Constitution says consumers filter by scope today, but 'the GC14 self-injection mechanism is the designed next layer' — described as future, not current.
- [unknown] **runtime/operator_memory.py loader** `operator_memory/AGENTS.md (head)` — Referenced as the loader but no code shown; cannot verify state from this material.
- [unknown] **mcp_face/tools/operator.py face** `operator_memory/AGENTS.md (head)` — Referenced as the MCP face with three ops; no code shown.
  - dormant-candidates: GC14 self-injection mechanism — referenced in operator_memory/AGENTS.md (head) as 'the designed next layer', not currently used. · ai_supplies_domain_knowledge.py — operator_memory/ai_supplies_domain_knowledge.py (head): migrated but awaits confirmation, status not confirmed. · confirm_before_writing.py — operator_memory/confirm_before_writing.py (head): migrated but still status='proposed'.
  - surprises: The directory contains 31 separate .py files, each apparently holding one MEMORY dict, rather than a single registry file or database. · AGENTS.md references a 'GC14 self-injection mechanism' as the designed next layer, but says consumers only filter by scope today — a future capability is named but not wired. · Multiple rows are explicitly 'MIGRATED (B5 batch 3)' yet still 'await Tim's confirmation' with status='proposed' — migration did not confirm them. · The constitution says 'fail-loud at discovery' for fabricated memory, but the material only shows the rule, not any enforcement code.

### nodes
- [living] **nodes/ directory** `nodes/` — 21-entry top-level module; AGENTS.md declares it a self-registering node library governed by C2 with three node kinds.
- [living] **AGENTS.md constitution** `nodes/AGENTS.md` — Prescriptive constitution; explicitly forbids editing runtime/canvas to add types and requires VOLATILE=True for mutable-truth nodes.
- [living] **package __init__.py** `nodes/__init__.py` — Only enables `from nodes._meta import NODE_TYPE_META`; node modules are discovered by file-path, not via package import.
- [half-built] **_meta.py node-type legibility registry** `nodes/_meta.py` — Marked 'TENTATIVE draft copy — Tim/DNA ratify' and truncated mid-sentence ('HOME NOTE (for composition): thi'); appears not finalized.
- [living] **ask.py node module** `nodes/ask.py` — First-purpose 'talk over the linked codebase' node; imports fabric config at module load; CONFIG only exposes 'model' in shown excerpt.
- [dormant] **.gitkeep** `nodes/.gitkeep` — Empty placeholder; no evident active role beyond keeping directory in version control.
- [unknown] **unseen node modules (directory names only)** `nodes/codebase.py, nodes/constant.py, nodes/embed.py, nodes/gate.py, nodes/join.py, nodes/llm.py, nodes/model_of_tim.py, nodes/pair.py, nodes/portal.py, nodes/retrieve.py, nodes/rhm_mode.py, nodes/similarity.py, nodes/titlecase.py, nodes/uppercase.py, nodes/wordcount.py` — Listed in directory but no content provided; cannot judge state.
  - dormant-candidates: nodes/.gitkeep — empty placeholder with no active function · nodes/_meta.py — 'TENTATIVE draft copy' truncated mid-sentence, appears built but not ratified/integrated
  - surprises: AGENTS.md says new node-types should live in `nodes/<name>/` subfolders, but the actual directory contains flat `nodes/<name>.py` files — a mismatch between constitution and current layout. · _meta.py is explicitly labeled a tentative draft awaiting ratification and is truncated, suggesting the node-type legibility registry is not yet grounded or complete despite the module being presented as a census.

### modes
- [living] **modes/ directory** `DIR modes/ (10 entries shown)` — Top-level module containing 8 mode files plus AGENTS.md constitution and __pycache__; described as file-discovered registry.
- [living] **AGENTS.md constitution** `modes/AGENTS.md (head)` — Documents the open file-discovered registry schema and explicitly forbids re-hardcoding modes; references runtime/modes_registry.py and prior hardcoded MODE_REGISTRY in suite.py.
- [living] **background mode** `modes/background.py (head)` — Complete MODE dict with order 20, brain_config 'swarm-16k', voice 'on', and all expected axes present.
- [half-built] **decide-for-me mode** `modes/decide-for-me.py (head)` — MODE dict is truncated mid-string in the directive and cuts off after 's' (likely 'stage' or 'subtypes'); file appears incomplete in the provided material.
- [half-built] **focus mode** `modes/focus.py (head)` — MODE dict is truncated after 'main_ctx_tokens': value is missing and file cuts off; subtypes present but rest incomplete.
- [living] **listening mode** `modes/listening.py (head)` — Complete MODE dict with order 0, brain_config 'voice-64k', and loadout_class 'interaction' — only mode in shown material with loadout_class explicitly set.
- [unknown] **off mode** `modes/off.py` — Listed in directory but no content shown; cannot assess state.
- [unknown] **text-only mode** `modes/text-only.py` — Listed in directory but no content shown; id uses hyphen per constitution's 'verbatim' rule.
- [unknown] **walkthrough mode** `modes/walkthrough.py` — Listed in directory but no content shown.
- [unknown] **watch-and-react mode** `modes/watch-and-react.py` — Listed in directory but no content shown; id uses hyphen per constitution's 'verbatim' rule.
- [unknown] **__pycache__** `modes/__pycache__` — Compiled bytecode cache present; no further detail shown.
  - dormant-candidates: modes/decide-for-me.py — MODE dict truncated, possibly half-built or extraction incomplete · modes/focus.py — MODE dict truncated after main_ctx_tokens, possibly half-built or extraction incomplete · modes/off.py — listed but content not shown; may be minimal/dormant · modes/text-only.py — listed but content not shown · modes/walkthrough.py — listed but content not shown · modes/watch-and-react.py — listed but content not shown
  - surprises: Two of the five shown mode files (decide-for-me.py, focus.py) are truncated mid-dict in the material, suggesting either incomplete files or incomplete extraction. · listening.py is the only shown mode with both brain_config and loadout_class set; background.py has brain_config but no loadout_class. · AGENTS.md says 'brain_config (the loadout the mode wants — WS1 links this to a loadout class)' yet listening.py already uses loadout_class 'interaction' while background.py does not, indicating mixed migration states.

### mode_detection_rules
- [living] **AGENTS.md constitution** `mode_detection_rules/AGENTS.md` — Explicitly declares this module mirrors roles/projections/node-types registry pattern and is governed by registry-is-truth; status is 'living'.
- [living] **background mode rule** `mode_detection_rules/background.py` — Rule id 'background' matches file stem; priority 10 is lowest number = first-match; condition is data-AST with not-None guard.
- [living] **focus mode rule** `mode_detection_rules/focus.py` — Rule id 'focus' matches file stem; priority 20 between background and listening.
- [living] **listening mode rule** `mode_detection_rules/listening.py` — Rule id 'listening' matches file stem; priority 30 is highest number = last fallback; no not-None guard because inbox is always int.
- [unknown] **__pycache__ directory** `mode_detection_rules/__pycache__` — Standard Python bytecode cache; no content shown, so state cannot be judged from material.
  - surprises: The constitution claims rules are validated at discovery by rules.validate_ast, but the material only shows truncated 'when' ASTs — we cannot confirm validation wiring is actually invoked. · AGENTS.md says candidate is validated ∈ suite.MODES at detect time, not at discovery — so a rule could exist pointing to a non-existent mode until detection runs.

### minds
- [living] **binding mind bind_compose_test** `minds/bind_compose_test.py` — Registry-style data file: a mode-to-composition binding kept out of suite.py to preserve single-owner.
- [living] **role mind extractor** `minds/extractor.py` — Named reference to an existing role; explicitly avoids duplicating the role implementation.
- [living] **role mind judge** `minds/judge.py` — Consumes extractor output; forms the +1 in the N+1 composition.
- [living] **composition mind pair** `minds/pair.py` — Composition edge feeds judge from extractor output as 'extract' plus original source as 'raw_exchange'.
- [unknown] **__pycache__ directory** `minds/__pycache__` — Compiled Python cache; no content shown.
  - dormant-candidates: __pycache__ at minds/__pycache__ — generated artifact, not source, likely stale if source files changed.
  - surprises: The directory is called 'minds' but every file is a registry-style data wrapper, not an implementation; the actual logic lives elsewhere (roles/mine_exchange, roles/judge_mining). · bind_compose_test.py is the only binding mind in a 5-entry directory; it binds mode 'compose-test' to 'pair', but no other mode bindings are shown. · The pair composition explicitly references a 'flat-fan bug' it is designed to avoid, suggesting a known prior architectural mistake.

### migration-pending
- [living] **migration-pending directory** `migration-pending/` — Top-level module containing only 2 entries per the DIR listing.
- [living] **MIGRATION-REGISTER.md** `migration-pending/MIGRATION-REGISTER.md` — Head only shown; claims to be a full home-directory inventory compiled 2026-06-26, status 'evidence-grounded landscape catalogue'.
- [unknown] **wizard-run-1** `migration-pending/wizard-run-1` — Listed as a directory entry but no content or type information provided in the material.
  - dormant-candidates: wizard-run-1 at migration-pending/wizard-run-1 — listed but no contents or status disclosed; may be an abandoned or incomplete wizard run.

### mcp_face
- [living] **module constitution** `mcp_face/AGENTS.md` — Explicitly calls out that older tools carry contracts-layer annotations only, with face wiring pending — a migration in progress.
- [living] **remote MCP gateway** `mcp_face/remote.py` — Access policy changed 2026-07-06: any valid token now gets ALL tools, with a one-line revert noted for future tiered access.
- [dormant] **deleted remote exposure registry** `mcp_face/remote_exposure.json.deleted-20260622` — File is explicitly renamed .deleted-20260622; it was a fail-closed posture registry, now apparently superseded by the allow-all token policy in remote.py.
- [living] **remote launch script / service unit source** `mcp_face/serve_remote.sh` — Hardcodes a Supabase project ref and Tailscale hostname; references a company-managed systemd service durability fix after a nohup failure.
- [unknown] **FastMCP server entrypoint** `mcp_face/server.py` — Only listed in directory; no excerpt provided, so actual contents and liveness cannot be judged.
- [unknown] **tool modules directory** `mcp_face/tools` — Directory exists; AGENTS.md says older modules predate the OPS-export obligation.
- [unknown] **tool metadata JSON** `mcp_face/tool_meta.json` — Present in directory listing but no excerpt; purpose and liveness unknown.
- [unknown] **tool operator overlay JSON** `mcp_face/tool_operator_overlay.json` — Present in directory listing but no excerpt; may overlay operator-specific tool config on top of tool_meta.json.
- [living] **pycache directory** `mcp_face/__pycache__` — Artifact of executed Python; confirms server.py/remote.py have been run at least once.
- [dormant] **gitkeep** `mcp_face/.gitkeep` — Empty placeholder; directory is clearly populated, so .gitkeep is vestigial.
  - dormant-candidates: mcp_face/remote_exposure.json.deleted-20260622 — superseded posture registry, still on disk · mcp_face/.gitkeep — empty placeholder in a populated directory · older tool modules in mcp_face/tools — AGENTS.md says they predate the OPS-export obligation and face wiring is pending
  - surprises: A file named remote_exposure.json.deleted-20260622 still exists in the directory despite being marked deleted; it is a dormant fail-closed policy artifact that conflicts with the current allow-all-connected policy in remote.py. · remote.py changed access policy on 2026-07-06 to give ANY valid token ALL tools, with only a one-line-revert comment guarding future tiered access; this is a broad privilege escalation from the original TIER_CLIENT design. · serve_remote.sh hardcodes a real Supabase project ID (gctunhsuwpaxeatwlmuv) and a Tailscale hostname (workstation001.tail777bc2.ts.net) in what appears to be production infrastructure configuration.

### mark_types
- [living] **AGENTS.md constitution** `mark_types/AGENTS.md` — Claims to enumerate the live mark-type set, but only lists 4 types while the directory contains 20 .py files — a 5× gap between documented and actual.
- [living] **ai_fingerprint mark-type** `mark_types/ai_fingerprint.py` — Seed for the subtract/inversion direction; value_shape is 'label'.
- [living] **built_twice mark-type** `mark_types/built_twice.py` — Claim-shaped value for drift-radar duplicates; docstring references 'judge_drift' but the file only contains the MARK_TYPE dict.
- [living] **comment mark-type** `mark_types/comment.py` — Interaction mark-type with free-text value; references an external taxonomies.json not shown in material.
- [living] **contradiction mark-type** `mark_types/contradiction.py` — Span-shaped relational mark; surfaces tension rather than subtracting.
- [unknown] **directory listing of 20 mark_types entries** `mark_types/` — 20 entries total: 1 markdown, 1 pycache, 18 .py files. AGENTS.md only documents 4 of the 18 .py mark-types.
  - dormant-candidates: decision_retract.py — present in mark_types/ but not listed in AGENTS.md live set · decision_take.py — present in mark_types/ but not listed in AGENTS.md live set · decision_update.py — present in mark_types/ but not listed in AGENTS.md live set · decision_update_accept.py — present in mark_types/ but not listed in AGENTS.md live set · intent_claim.py — present in mark_types/ but not listed in AGENTS.md live set · intent_created.py — present in mark_types/ but not listed in AGENTS.md live set · intent_heartbeat.py — present in mark_types/ but not listed in AGENTS.md live set · intent_suspend.py — present in mark_types/ but not listed in AGENTS.md live set · intent_terminal.py — present in mark_types/ but not listed in AGENTS.md live set · favour.py — present in mark_types/ but not listed in AGENTS.md live set · overlap.py — present in mark_types/ but not listed in AGENTS.md live set · reaction.py — present in mark_types/ but not listed in AGENTS.md live set · strain.py — present in mark_types/ but not listed in AGENTS.md live set · gold_likelihood.py — referenced in AGENTS.md but its file content was not shown in the material
  - surprises: AGENTS.md's 'live set' list is radically incomplete: it names only gold_likelihood, ai_fingerprint, contradiction, and built_twice, but the directory contains 18 .py mark-type files including a full 'decision_*' family and 'intent_*' family never mentioned. · A complete decision vocabulary exists (decision_retract, decision_take, decision_update, decision_update_accept) with no explanation in the constitution and no presence in the documented live set. · A complete intent vocabulary exists (intent_claim, intent_created, intent_heartbeat, intent_suspend, intent_terminal) that is entirely absent from the constitution's enumeration. · The AGENTS.md guarantees 'a malformed entry FAILS LOUD at discovery' and 'tests/mark_types_acceptance.py asserts each is reflected here' — yet the constitution itself appears out of sync with the directory it governs.

### lifters
- [living] **lifters/ directory** `DIR lifters/ (5 entries shown)` — Top-level module with exactly 5 entries; constitution says it should be file-discovered registry, one self-registering .py per extractor.
- [living] **AGENTS.md constitution** `lifters/AGENTS.md` — Prescriptive constitution; explicitly lists 3 live lifters (frontmatter, links, blocks) and requires each discovered lifter be reflected here, with tests/lifters_acceptance.py asserting parity.
- [half-built] **blocks.py lifter** `lifters/blocks.py` — Head shows _extract function and _HEADING regex, but excerpt truncates mid-function body at `m = _HE` — cannot confirm if module-level LIFTER dict exists or if file is complete.
- [half-built] **frontmatter.py lifter** `lifters/frontmatter.py` — Head shows _extract function, but excerpt truncates at `re` inside the function and does not show the required module-level LIFTER dict.
- [half-built] **links.py lifter** `lifters/links.py` — Head shows _WIKILINK and _MDLINK regexes and start of _extract, but truncates mid-body at `_WIK` and does not show the required module-level LIFTER dict.
- [unknown] **__pycache__ directory** `lifters/__pycache__` — Listed as directory entry; no contents shown, so state cannot be judged from material.
  - dormant-candidates: lifters/__pycache__ — present in directory listing but no contents or role described in constitution.
  - surprises: All three .py lifter files truncate before showing the module-level LIFTER dict that AGENTS.md says is required for self-registration; the visible code only shows private `_extract` functions and regexes. · AGENTS.md claims the live set is frontmatter/links/blocks and that tests/lifters_acceptance.py asserts parity, but the material does not include that test file or runtime/lifter_registry.py, so the claim is unverified from this territory alone.

### kinds
- [living] **kinds package directory** `kinds/` — Top-level module with only 3 entries; unusually minimal for a 'full enumeration' census territory.
- [unknown] **kinds/__init__.py** `kinds/__init__.py` — Head is shown as empty/blank; no imports, exports, or package surface visible in excerpt.
- [half-built] **kinds/raw.py** `kinds/raw.py` — Explicitly labeled 'TENTATIVE draft copy — Tim/DNA ratify'; journey-gated on OQ1–4; appears to be a declared-first registry that is not yet ratified.
- [dormant] **referenced bindings/raw.py** `kinds/raw.py` — Mirrors bindings/raw.py 'ONE data map (NOT 51 files)' — implies a parallel registry shape, but bindings/raw.py content is not shown here.
  - dormant-candidates: kinds/__init__.py at kinds/__init__.py — empty head, no package surface wired · kinds/raw.py at kinds/raw.py — draft registry, not ratified, journey-gated on OQ1–4
  - surprises: kinds/__init__.py head is completely empty despite being a top-level 'full enumeration' module. · kinds/raw.py is explicitly a draft awaiting ratification ('TENTATIVE draft copy — Tim/DNA ratify'), not a live registry. · The registry claims to be 'seeded with kinds grounded from the live store + runtime emit-sites' but the actual data map is not shown in the material.

### item_types
- [living] **item_types module directory** `item_types/` — 22 entries: 1 constitution markdown + 1 pycache + 20 .py item-type definitions; file-discovered registry, not hardcoded enum.
- [living] **AGENTS.md constitution** `item_types/AGENTS.md` — Declares itself prescriptive constitution governing board-item-type-vocabulary; lists 7 core types plus 8 landed L6-BOARD types (observation, milestone, design, task, blocker, cognitive_guide, research, diagnostic).
- [half-built] **artefact item type** `item_types/artefact.py` — ITEM_TYPE dict is truncated mid-definition (ends after transitions with a trailing comma and blank line); no label/desc fields visible, and the docstring describes a rich surface feature that may not yet be wired.
- [living] **block item type** `item_types/block.py` — Comment-granularity unit inside documents; states current/superseded with bidirectional transition.
- [living] **blocker item type** `item_types/blocker.py` — One of 8 landed cloud types; explicitly pairs with blocked_by edge; legacy states open/resolved/closed.
- [living] **board_view item type** `item_types/board_view.py` — First-class view record; pinning is a per-view typed edge, not an item property — unusual design that prevents cross-user pin leakage.
  - dormant-candidates: artefact.py — ITEM_TYPE dict is truncated/half-built in the material (ends abruptly at transitions), and the type is absent from AGENTS.md's enumerated live set. · AGENTS.md's unlisted files — board_view.py, block.py, and any other .py files beyond the 15 named types may be living but are not explicitly enumerated in the constitution text shown.
  - surprises: The directory lists 20 .py files plus AGENTS.md, but the constitution text only names 15 item types (7 core + 8 landed); the files board_view.py, artefact.py, block.py, and possibly others are present but not accounted for in the enumerated type list inside AGENTS.md. · artefact.py describes a sophisticated surface-hosted HTML page with iframe sandboxing, comment rail, and chat integration, yet its ITEM_TYPE dict is visibly truncated and there is no mention of 'artefact' in the AGENTS.md live-set enumeration. · board_view.py introduces a per-user pinning model via board_edges/pinned.py, but the material does not show that edge file or any runtime wiring, making the 'pin belongs to the view' guarantee unverified from this slice.

### introspection
- [living] **AGENTS.md constitution** `introspection/AGENTS.md` — Explicitly declares a hard build-time invariant: engine/rules/adapters must contain zero platform-name literals, enforced by a grep test.
- [living] **__init__.py package root** `introspection/__init__.py` — Claims to be import side-effect-free; sub-modules are imported explicitly by callers rather than auto-loaded.
- [living] **discover.py DISCOVER verb** `introspection/discover.py` — Dispatches on stable selectors (src.type); missing adapters are intentionally loud errors, not silent empty registries.
- [living] **engine.py four-verb engine** `introspection/engine.py` — Implements PROJECT and REFRESH in addition to orchestrating DISCOVER/CLASSIFY; REFRESH diffs snapshots for R4 novelty detection.
- [living] **invoke.py INVOCATION layer** `introspection/invoke.py` — Newly added active half (2026-06-28) — runs capabilities gated by discovered posture; most invocation kinds are named-but-unbuilt per the §8.3 gap-surface pattern.
- [unknown] **adapters/ directory** `introspection/adapters` — Listed as a directory entry but no contents shown; constitution says adapters must contain zero platform-name literals.
- [unknown] **platforms.py** `introspection/platforms.py` — Exists in the module but no excerpt provided; likely the Level-1 platform loader/reader.
- [unknown] **registry.py** `introspection/registry.py` — Exists in the module but no excerpt provided; may be the registry accessor used by engine/invoke.
- [living] **rules.py** `introspection/rules.py` — Five closed classification rules with explicit priority R1 > R2 > R3 > R5 > R4; posture is derived, not opinion.
- [dormant] **__pycache__** `introspection/__pycache__` — Compiled bytecode cache; artifact of execution, not source-of-truth.
  - dormant-candidates: adapters/ directory contents not shown — constitution says DISCOVERERS map is closed and missing adapters raise; actual adapter coverage is unverified from this material (introspection/adapters) · invoke.py non-subprocess invocation kinds (rest/mcp/grpc/sdk/library) are named but unbuilt and will raise MissingInvokerError (introspection/invoke.py) · platforms.py and registry.py exist but no excerpts or callers shown in the provided material (introspection/platforms.py, introspection/registry.py)
  - surprises: Rule priority order is non-sequential: R1 > R2 > R3 > R5 > R4 — R4 is explicitly lowest despite being the novelty rule that REFRESH is designed to feed. · invoke.py is described as 'UNIVERSAL' but the material states subprocess is the only built invocation_kind; rest/mcp/grpc/sdk/library are named-but-unbuilt and will raise MissingInvokerError. · The constitution claims the grep test in tests/introspection_acceptance.py is EXPECTED to hit platforms/claude_code.py — a test that is supposed to fail the build is simultaneously expected to hit a legitimate file, which is a delicate maintenance invariant.

### guides
- [living] **AGENTS.md constitution** `guides/AGENTS.md` — Declares the full schema and governance for the guides module, including the mandatory-grounding gate and the 'carrier rule' that guides attach to systems/capabilities, not operational role-inputs.
- [living] **using_skills guide** `guides/using_skills.py` — The SEED guide; explicitly grounded in real files and the canonical skill example; the file is truncated mid-string but the intent and target are clear.
- [living] **using_corpus_pipeline guide** `guides/using_corpus_pipeline.py` — Agent-authored guide for the corpus pipeline; content references the 'registry-is-truth' principle and a three-layer pipeline, but the file is truncated before completion.
- [living] **using_patterned_visibility guide** `guides/using_patterned_visibility.py` — Agent-authored guide for the patterned-visibility loop; content is cut off mid-sentence, so the full grounded_from list and source_hash are not visible.
- [unknown] **__pycache__ directory** `guides/__pycache__` — Standard Python bytecode cache directory; no contents shown, so its state cannot be judged beyond being present.
  - dormant-candidates: guides/__pycache__ — present but no usage or contents shown; may be stale bytecode from earlier imports.
  - surprises: The constitution says `GuideRegistry.discover` reads `guides/*.py`, but the directory also contains `AGENTS.md` and `__pycache__`, which are not `.py` files; the registry's glob behavior with respect to these is not specified in the visible material. · The constitution references `tests/guides_acceptance.py` as asserting each guide is reflected in the live set, but that test file is not included in the material, so its assertions cannot be verified here. · The `using_skills.py` guide is described as the seed and explicitly grounded, but the other two visible guides are truncated before showing their `grounded_from` or `source_hash` fields, making it impossible to confirm they satisfy the mandatory-grounding gate from this material alone.

### generation_policies
- [living] **AGENTS.md constitution** `generation_policies/AGENTS.md` — Declares generation_policies/ is a file-discovered registry where adding a regime = adding a file; explicitly references an acceptance test that should mirror the live set.
- [living] **capture_default generation policy** `generation_policies/capture_default.py` — SEED policy with rep_penalty_ladder [1.1, 1.2], diff_against_source True, json_schema True, temp 0.0; docstring says id MUST equal file stem.
- [living] **policy.risk-grounding generation policy** `generation_policies/policy.risk-grounding.py` — Forked 2026-06-21 to meet decision_subtypes/authorize.py explanation_policy id; single-rung ladder, free prose, not structured.
- [living] **policy.technical-recommendation generation policy** `generation_policies/policy.technical-recommendation.py` — Forked 2026-06-21 to meet decision_subtypes/cross-lane.py explanation_policy id; single-rung ladder, free prose, not structured.
- [living] **policy.theorem-grounding generation policy** `generation_policies/policy.theorem-grounding.py` — Forked 2026-06-21 to meet decision_subtypes/theorem-fork.py explanation_policy id; single-rung ladder, free prose, not structured.
- [unknown] **policy.trade-off-neutral generation policy** `generation_policies/policy.trade-off-neutral.py` — File is listed in directory but no excerpt provided; cannot judge state from material.
- [unknown] **prose_default generation policy** `generation_policies/prose_default.py` — File is listed in directory but no excerpt provided; cannot judge state from material.
- [unknown] **__pycache__ directory** `generation_policies/__pycache__` — Compiled bytecode cache present; no content shown.
  - dormant-candidates: prose_default.py — listed in generation_policies/ but no excerpt and not referenced in the visible AGENTS.md live-set enumeration · policy.trade-off-neutral.py — listed in generation_policies/ but no excerpt and not referenced in the visible AGENTS.md live-set enumeration
  - surprises: AGENTS.md lists a live set and references tests/generation_policies_acceptance.py, but the directory listing shows 8 entries including prose_default.py and policy.trade-off-neutral.py that are not mentioned in the visible constitution excerpt. · The three forked explanation policies (risk-grounding, technical-recommendation, theorem-grounding) all share an identical single-rung [1.1] ladder and identical flags, suggesting they may be copy-paste stubs rather than tuned regimes. · AGENTS.md mentions a schema key 'budget' as optional, but no shown policy includes a budget field.

### foundation
- [living] **TIM.md foundation document** `foundation/TIM.md` — Explicitly self-described as provisional/living; contains a meta-warning that it and system/ were written in separate parallel branches with overlapping ground and neither is canonical.
- [unknown] **system/ directory** `foundation/system/` — Mentioned as parallel-branch material overlapping with TIM.md; not shown in excerpt, so contents unknown.
- [unknown] **exchanges/ directory** `foundation/exchanges/` — Listed in directory enumeration but no material provided.
- [unknown] **models/ directory** `foundation/models/` — Listed in directory enumeration but no material provided.
- [unknown] **operations/ directory** `foundation/operations/` — Listed in directory enumeration but no material provided.
  - surprises: The foundation's own top-level document declares that two of its own structures (TIM.md and system/) are non-canonical parallel branches and instructs readers to 'ask Tim' rather than reconcile them — an unresolved architectural split at the root.

### forms
- [living] **forms/ directory** `forms/` — Top-level module containing 6 entries; constitution says it mirrors roles/skills/projections/node-types as a file-discovered registry.
- [living] **AGENTS.md constitution** `forms/AGENTS.md` — Prescriptive constitution governing P1; explicitly references tests/forms_acceptance.py asserting each live form is reflected here.
- [living] **decision form** `forms/decision.py` — FORM dict truncated mid-policy value ('ca'); id='decision', stage='deep', policy starts with 'ca' (likely 'capture_default').
- [living] **log form** `forms/log.py` — FORM dict truncated; match function checks >=3 timestamps but body is cut off after '# >=3 timesta'.
- [living] **prose fallthrough form** `forms/prose.py` — FORM dict truncated after '"match"'; it is the declared fallthrough form matching any non-empty text.
- [living] **registry form** `forms/registry.py` — FORM dict truncated; match function body cut off mid-linky counting ('linky = sum(1').
- [unknown] **__pycache__ directory** `forms/__pycache__` — Listed as a directory entry but no contents provided; ordinary Python bytecode cache.
  - dormant-candidates: forms/__pycache__ — listed but no contents shown; may be stale bytecode if source forms changed recently. · tests/forms_acceptance.py — referenced in AGENTS.md as the assertion harness, but not present in the material; may exist elsewhere and should be checked for actual coverage of all four forms.
  - surprises: All four .py form files have their FORM dicts truncated in the material, so we cannot verify the complete schema (policy ids, fallthrough flag, desc) despite the constitution requiring a complete declaration. · The constitution guarantees malformed entries FAIL LOUD at discovery, but the material does not include runtime/forms.py or tests/forms_acceptance.py, so we cannot confirm enforcement is wired.

### flows
- [living] **flows/ module constitution** `flows/AGENTS.md` — Defines flows as file-discovered, propose-only production lines; declares loader is runtime/flows.py and that flows/*.py is scanned by the floor's source-invariant.
- [unknown] **registry_generation flow** `flows/registry_generation.py` — Only mentioned in AGENTS.md as the grounded mockup→dossier chain; no code excerpt provided.
- [unknown] **transcript_mine flow** `flows/transcript_mine.py` — Only mentioned in AGENTS.md; no code excerpt provided.
- [unknown] **pattern_cluster flow** `flows/pattern_cluster.py` — Only mentioned in AGENTS.md; no code excerpt provided.
- [unknown] **repo_ingest flow** `flows/repo_ingest.py` — Only mentioned in AGENTS.md; no code excerpt provided.
- [living] **drift_radar flow** `flows/drift_radar.py` — Has a real FLOW dict with id/label/description; imports sys but no run() shown; docstring says it PROPOSES marks + findings only.
- [half-built] **floor_walk flow** `flows/floor_walk.py` — Docstring describes four detectors but the excerpt cuts off mid-sentence during detector 3 (STALE DECISIONS); no FLOW dict or run() shown.
- [living] **cc_registry_refresh flow** `flows/cc_registry_refresh.py` — Explicitly states it does NOT write the stamp; propose-only; surfaces ONE cc_registry_gap inbox item per version bump.
- [living] **dragnet_extract flow** `flows/dragnet_extract.py` — Flow proposes a bake; actual ~4h side-effecting bake is operator-only via CLI door, honoring S12/F7.
- [unknown] **ts_backfill flow** `flows/ts_backfill.py` — Listed in directory but no excerpt provided; not mentioned in AGENTS.md.
- [dormant] **__pycache__ directory** `flows/__pycache__` — Compiled bytecode cache; artifact of execution, not source-of-truth.
  - dormant-candidates: flows/ts_backfill.py — listed in directory, absent from AGENTS.md, no excerpt provided · flows/__pycache__ — compiled cache, not a living source artifact · flows/floor_walk.py — docstring cuts off mid-detector 3, no FLOW dict or run() visible in excerpt
  - surprises: AGENTS.md lists 6 flow rows but the directory contains 11 .py files — 5 files (cc_registry_refresh, dragnet_extract, drift_radar, floor_walk, ts_backfill) are not in the constitution's row list or are only partially described. · floor_walk is described as a standing cross-lane sweep but its docstring is truncated mid-detector and no FLOW dict/run() is visible — it may be half-built despite being conceptually central. · drift_radar imports sys but the excerpt shows no run() body; only the FLOW dict head is visible. · cc_registry_refresh and dragnet_extract are not mentioned in the AGENTS.md 'The rows' list at all, yet they exist as implemented .py files.

### fabric
- [living] **AGENTS.md constitution** `fabric/AGENTS.md` — Claims end-to-end wiring of schema-guided decoding via client.complete(schema=...) and additive metadata passthrough via opts['meta'].
- [dormant] **.gitkeep** `fabric/.gitkeep` — Empty placeholder; only meaningful if the directory is otherwise empty, which it is not.
- [living] **client.py guarded model calls** `fabric/client.py` — Transport is injected, not imported directly, keeping it agnostic; FabricError and _backoff are defined here.
- [living] **config.py unified endpoint config** `fabric/config.py` — STORE_DIR is shared between UI bridge and MCP; NO Gemini enforcement is promised but not visible in the excerpt.
- [living] **embed_routing.py embedder routing table** `fabric/embed_routing.py` — Single routing table for all faces; code/symbol spaces route to nomic-embed-code, everything else to pplx-2560.
- [unknown] **__pycache__ directory** `fabric/__pycache__` — Compiled bytecode cache; no content shown.
- [unknown] **litellm.config.yaml** `fabric/litellm.config.yaml` — Listed but no excerpt provided; likely the LiteLLM proxy model map.
- [unknown] **serve_litellm.sh** `fabric/serve_litellm.sh` — Listed but no excerpt provided; likely the proxy launch script.
- [unknown] **transport.py** `fabric/transport.py` — Referenced by client.py as the LiteLLM-backed transport implementation, but no excerpt shown.
- [unknown] **vram.py** `fabric/vram.py` — Listed but no excerpt provided; constitution says VRAM decisions read live nvidia-smi.
  - dormant-candidates: fabric/.gitkeep — empty placeholder in a populated directory · fabric/litellm.config.yaml — listed but no content shown; may be unreferenced if proxy is not running · fabric/serve_litellm.sh — listed but no content shown; may be unused if direct ollama fallback is active · fabric/vram.py — listed but no content shown; live nvidia-smi claim needs verification
  - surprises: AGENTS.md references a `fabric.py` as the source of lessons, but the directory listing shows `client.py`, `transport.py`, `config.py`, etc. — no `fabric.py` is present in the material. · The constitution promises 'NO Gemini — enforced, fail loud' and 'every model call is guarded', but the config.py excerpt cuts off before showing the enforcement code. · client.py is described as 'transport-agnostic' with an injected callable, yet the directory still contains a dedicated `transport.py` — the abstraction may be recent or partially migrated.

### edge_kinds
- [living] **edge_kinds directory** `edge_kinds/` — 117 entries shown — appears to be a complete file-discovered edge-kind registry, one .py file per kind.
- [living] **AGENTS.md constitution** `edge_kinds/AGENTS.md` — Declares this is the ONE edge grammar; files are authoritative, DB table ledger.edge_kind is derived read side.
- [half-built] **addresses edge kind** `edge_kinds/addresses.py` — Minimal row with needs_review=True and note 'face auto-assigned; confirm the JOB' — looks provisional.
- [living] **aimed-at edge kind** `edge_kinds/aimed-at.py` — Clean declaration, needs_review=False, seen in ledger.edge.
- [half-built] **applies_to edge kind** `edge_kinds/applies_to.py` — needs_review=True with 'face auto-assigned; confirm the JOB' — provisional like addresses.
- [living] **attached_to edge kind** `edge_kinds/attached_to.py` — Declares inverse 'has_attachment' composed at read, never stored — law 4.
  - dormant-candidates: addresses.py — needs_review=True, 'face auto-assigned; confirm the JOB' at edge_kinds/addresses.py · applies_to.py — needs_review=True, 'face auto-assigned; confirm the JOB' at edge_kinds/applies_to.py
  - surprises: AGENTS.md says 319 stored cloud 'belongs_to' rows were DROPPED on landing — a significant data migration event mentioned mid-sentence and truncated. · The constitution explicitly states that RelationTypeRegistry cannot hold these rows because EDGE_KIND is a superset with extra fields (face, endpoints, behavior, needs_review) — revealing a deliberate parallel-registry design, not unification. · Law 4 says reverses are NEVER stored, yet the directory contains files like 'authored_by.py', 'depended-on-by.py', 'generated-by.py', 'powered-by.py', 'produced.py', 'promoted_from.py' — some of these may be inverses that should not exist as stored kinds. Need to inspect which are declared with inverses vs which are standalone.

### docs
- [living] **docs/ module constitution** `docs/AGENTS.md` — Self-describes as meta-documentation only; explicitly forbids code or duplicate registries, yet references a Coherence Gate spec not present in the material.
- [unknown] **Vault Conventions** `docs/vault-conventions.md (implied by directory listing; referenced in AGENTS.md)` — Named as the canonical inhabitant of docs/ but its content was not included in the material; only the filename is confirmed.
- [living] **Brain Loadouts how-to** `docs/brain-loadouts.md` — Claims verified-live coverage dated 2026-06-30 with real bridge /api/chat + /api/cognition/run_role turns; points to ops/services.json for combo declarations.
- [living] **Concepts and Principles** `docs/concepts-and-principles.md` — References an external design vault ('build-prep') for five invariants rather than duplicating them here.
- [living] **Guides & Pages** `docs/guides-and-pages.md` — Dated 2026-06-28 commission; describes three reversible builds on registry/address spine but only the skill face is visible in the excerpt.
- [unknown] **claude-code-interconnection directory/note** `docs/claude-code-interconnection` — Listed as a directory entry but no content provided; name suggests a cross-cutting integration doc.
- [unknown] **methodology directory/note** `docs/methodology` — Listed as a directory entry but no content provided.
- [dormant] **.gitkeep** `docs/.gitkeep` — Empty placeholder; suggests docs/ may once have been empty or is kept sparse intentionally.
  - dormant-candidates: docs/.gitkeep — empty placeholder in a now-populated directory · docs/claude-code-interconnection — listed but content not provided; may be stub or directory · docs/methodology — listed but content not provided; may be stub or directory
  - surprises: AGENTS.md forbids duplicating registries and references a [[Coherence Gate — Spec]], but no such file is included in the material despite being named twice as a guard. · brain-loadouts.md claims live verification on 2026-06-30 and references ops/services.json, but the material does not include that file to corroborate the declared combos. · guides-and-pages.md mentions three reversible builds (skill, guide, contract faces) but only the skill face is visible in the excerpt; the other two constitutions are referenced but absent.

### dials
- [living] **dials module directory** `dials/` — Top-level module with only 4 entries: constitution + 2 dial definitions + pycache; no __init__.py visible in the shown entries.
- [living] **AGENTS.md constitution** `dials/AGENTS.md` — Prescriptive constitution explicitly marks two consumer seams as 'unbuilt' and says overrides are stored+validated now but evaluated later.
- [half-built] **anticipation dial definition** `dials/anticipation.py` — Dial row exists and is documented, but constitution says 'nothing reads this yet — the dial is their configuration seam, adjustable from day one'.
- [half-built] **stability dial definition** `dials/stability.py` — Same pattern: dial defined, consumer seams named honestly as not-yet-built.
- [unknown] **__pycache__ directory** `dials/__pycache__` — Compiled bytecode cache present; implies the .py files have been imported/executed at least once, but no details shown.
  - dormant-candidates: anticipation.py dial consumer wiring — dials/anticipation.py governs 'the now-organ + resolver when built (GC14/Track-1); nothing reads this yet' · stability.py dial consumer wiring — dials/stability.py governs 'the RHM surface-composer + the resolved-UI layer when built; nothing reads this yet' · condition-scoped overrides evaluation — AGENTS.md says overrides are 'stored + validated NOW, evaluated once the now-organ + rules wiring exists; until then the flat value applies'
  - surprises: The module has no __init__.py shown among the 4 directory entries, yet __pycache__ exists — suggests the files are imported directly or the module is package-less in practice. · AGENTS.md declares the module 'governs: [Track-1]' and relates to '[[runtime — constitution]]' and '[[Company Map]]', but those linked artifacts are not in the material. · Both dial definitions are complete enough to have positions and meanings, but their consumer systems are explicitly admitted as unbuilt — the dials are 'adjustable from day one' with no readers.

### design
- [living] **CLAUDE.md keeper charter** `design/CLAUDE.md` — Self-describes this folder as a 'living thinking-substrate + two working registries (tokens, addresses)' — claims registry-as-truth architecture is applied to the design corpus itself.
- [half-built] **CONNECTION-CONTRACT.md** `design/CONNECTION-CONTRACT.md` — Explicitly tagged as proposal not all live: IS vs SHOULD-BE split sourced from build research docs outside this territory.
- [living] **README.md one-way sync warning** `design/README.md` — Declares this whole folder is a generated read-copy; canonical source lives at build-prep/design/ on Windows side.
- [living] **conventions.md** `design/conventions.md` — Names two inventory/plan markdown files that were NOT in the 12-entry directory listing.
- [unknown] **design-system.css** `design/design-system.css` — Said to be generated by _system/emit.py and imported by every mockup; content not shown.
- [unknown] **index.html gallery** `design/index.html` — Said to be generated by _system/gallery.py; status derived from file existence to prevent drift.
- [unknown] **register.json** `design/register.json` — Called 'the tagged registry of every view' and 'machine-readable backbone'; content not shown.
- [unknown] **_system directory** `design/_system` — Contains emit.py and gallery.py per conventions.md, but no listing or contents provided.
- [unknown] **blueprint directory** `design/blueprint` — Referenced as the builder session that consumes the connection contract; no contents shown.
- [unknown] **claude-ds directory** `design/claude-ds` — Present in directory listing but never referenced in any shown document.
- [unknown] **interface-mockups directory** `design/interface-mockups` — Present in directory listing but never referenced in conventions.md, which only mentions mockups/.
- [unknown] **mockups directory** `design/mockups` — Conventions describe naming as <id>-<slug>-<p...>; no files shown.
  - dormant-candidates: design/interface-mockups/ — exists in listing but unreferenced by any shown document · design/claude-ds/ — exists in listing but unreferenced by any shown document · design/Front-End Design — Production Plan & View Inventory.md — named in conventions.md but not present in directory listing · design/Feature & Function Inventory (from the real app).md — named in conventions.md but not present in directory listing
  - surprises: Directory listing shows interface-mockups/ and claude-ds/ but the governing documents only discuss mockups/ and never mention these two folders. · conventions.md references two markdown files ('Front-End Design — Production Plan & View Inventory.md' and 'Feature & Function Inventory (from the real app).md') that are absent from the 12-entry directory listing. · CONNECTION-CONTRACT.md admits it is a proposal where some clauses are SHOULD-BE not IS, despite being in the top-level design module.

### decisions
- [living] **AGENTS.md contract for decision-row authoring** `decisions/AGENTS.md` — Explicitly warns that rows without 'subtype' are silently dropped; schema does not enforce it, so the contract is the only guard.
- [half-built] **adopt-claude-design decision row** `decisions/adopt-claude-design.py` — Head only; file is truncated mid-implication of the second option, so we cannot confirm it is complete or has subtype/scope/legibility.
- [half-built] **build-consent-posture decision row** `decisions/build-consent-posture.py` — Truncated mid-implication of second option; completeness and required fields unknown from material.
- [half-built] **card-refine-posture decision row** `decisions/card-refine-posture.py` — Docstring is unusually self-aware (decision about the decision surface), but the DECISION dict itself is truncated mid-meaning.
- [half-built] **card-visuals-source decision row** `decisions/card-visuals-source.py` — Truncated after first option implication; full shape and subtype not verifiable.
- [living] **27-entry directory listing** `decisions/` — Directory contains __pycache__, suggesting these .py files have been imported/executed at least once.
  - dormant-candidates: decisions/substrate-home.py — explicitly named in AGENTS.md as a previously invisible keystone row due to missing subtype; its current state is not shown in the material, so it may still be dormant or half-built. · decisions/__pycache__ — cache implies execution, but the decision rows are authored as data declarations; the runtime import path is not explained in the material.
  - surprises: AGENTS.md documents a 2026-06-21 incident where 10 of 24 rows (including 'substrate-home') lacked subtype and were invisible on the live operator surface, yet the schema still does not enforce subtype. · The directory contains __pycache__, which is unusual for a pure declaration/contract module and implies these decision modules are imported as runtime code rather than treated as static config.

### decision_subtypes
- [living] **AGENTS.md module manifest** `decision_subtypes/AGENTS.md` — Claims this is a registry with one mechanism mirror; but only .py files are shown, no runtime/decision_subtypes.py in the listing.
- [living] **authorize subtype row** `decision_subtypes/authorize.py` — Desc string is truncated mid-sentence after 'the \'so long as it\'s secure\' CONDITION + ' — the closing quote and rest are missing in the material.
- [living] **cross-lane subtype row** `decision_subtypes/cross-lane.py` — Owner is 'fabric' (streams settle), explicitly filtered OUT of Tim's operator-stack per AGENTS.md.
- [living] **theorem-fork subtype row** `decision_subtypes/theorem-fork.py` — Required_elements list is truncated mid-element 'ai_uncertainty_cave' — no closing bracket visible.
- [living] **trade-off subtype row** `decision_subtypes/trade-off.py` — Desc also truncated mid-word 'axe' — the four subtype files all end abruptly, suggesting head-only excerpts.
- [unknown] **__pycache__ directory** `decision_subtypes/__pycache__` — Listed but no contents shown; ordinary Python cache, cannot judge if stale.
  - dormant-candidates: runtime/decision_subtypes.py — referenced in AGENTS.md as the one mechanism, but not present in the provided directory listing (where: AGENTS.md → runtime/decision_subtypes.py) · Potential unbuilt subtype candidates mentioned in AGENTS.md: ranking · allocation · workflow · single-confirm, DNA's unbuilt variant candidates (where: decision_subtypes/AGENTS.md)
  - surprises: AGENTS.md says the mechanism is runtime/decision_subtypes.py, but the directory listing for decision_subtypes/ does not include that file — it only appears by reference. · The registry claims 'a decision of a new shape adds a ROW, never a code edit', yet the material shows one-file-per-subtype .py rows, not a single registry file or database row. · cross-lane is the only subtype with owner='fabric' and is explicitly filtered out of Tim's operator-stack, while the other three are owner='tim'.

### contracts
- [living] **contracts module directory** `contracts/ (17 entries shown)` — Top-level constitution module; AGENTS.md claims it is the spine every other module composes against and imports from nothing in the repo.
- [living] **AGENTS.md constitution** `contracts/AGENTS.md` — Declares additive-only versioning with schema_ver on records/messages and version on NodeType; mentions C1-C8 but only C1-C8 naming is visible; references build-prep/contracts/ as vault source of truth.
- [living] **C1 address contract** `contracts/address.py` — Defines address grammar including run://, cas://, blob://, vec://, ui://, code://, skill://, context://, guide:// schemes; docstring truncated mid 'guide://' description.
- [half-built] **C8 bridge message contract** `contracts/bridge_msgs.py` — Imports contracts.node_record but the import line is truncated with no model name; docstring says transport already lives at runtime/bridge.py, suggesting this file may be models-only and not yet fully wired.
- [living] **C-CAP capability entry contract** `contracts/capability_entry.py` — References multiple build-plan fixes (F-FIX-3, F-FIX-5, F-FIX-14) suggesting recent construction; declares version field and id format but implementation is truncated.
- [unknown] **cognition_info.py** `contracts/cognition_info.py` — No material shown beyond filename; AGENTS.md does not explicitly map a C-number to it.
- [unknown] **dragnet_schema.py** `contracts/dragnet_schema.py` — No material shown beyond filename; not referenced in the visible AGENTS.md C1-C8 list.
- [living] **node_record.py** `contracts/node_record.py` — AGENTS.md says this hosts EDGE_KINDS registry and Edge.kind field with SCHEMA_VER bump to 2; described as net-new from Concurrent Cognition G1 (C1.3).
- [living] **node_type.py** `contracts/node_type.py` — Referenced as the registry-type convention source for capability_entry.py; uses version not schema_ver per AGENTS.md.
- [unknown] **object_info.py** `contracts/object_info.py` — AGENTS.md maps this to C5 object_info/compile; no code shown.
- [unknown] **resolver.py** `contracts/resolver.py` — AGENTS.md maps this to C4 resolver; no code shown.
- [unknown] **scope_grammar.py** `contracts/scope_grammar.py` — No material shown beyond filename; not explicitly mapped to a C-number in visible AGENTS.md.
- [unknown] **shapes.py** `contracts/shapes.py` — No material shown beyond filename; AGENTS.md says 'shapes carry a version marker' but does not assign a C-number.
- [unknown] **tools.py** `contracts/tools.py` — AGENTS.md maps this to C7 MCP tools; no code shown.
- [unknown] **ui_info.py** `contracts/ui_info.py` — No material shown beyond filename; not explicitly mapped to a C-number in visible AGENTS.md.
- [unknown] **platform_entry.py** `contracts/platform_entry.py` — No material shown beyond filename; paired with capability_entry.py by naming but not referenced in visible AGENTS.md.
- [dormant] **__pycache__ directory** `contracts/__pycache__` — Compiled Python cache; artifact of execution, not source, and may be stale relative to source files.
- [dormant] **.gitkeep file** `contracts/.gitkeep` — Empty placeholder file; only meaningful if directory would otherwise be empty, which it is not.
  - dormant-candidates: contracts/.gitkeep — empty placeholder in a non-empty directory · contracts/__pycache__ — compiled cache, possibly stale · contracts/bridge_msgs.py — import line truncated; may be half-wired to runtime/bridge.py
  - surprises: AGENTS.md lists C1-C8 but the directory contains additional contract-like files (capability_entry.py, cognition_info.py, dragnet_schema.py, platform_entry.py, scope_grammar.py, shapes.py, ui_info.py) that are not assigned C-numbers in the visible constitution text. · bridge_msgs.py imports 'contracts.node_record' but the import statement is truncated with no imported symbol, and the docstring says the actual transport bridge already lives elsewhere (runtime/bridge.py), making this file's current wiring unclear. · capability_entry.py references build-plan fixes (F-FIX-3, F-FIX-5, F-FIX-14) in its docstring, suggesting it was recently modified but the implementation is cut off mid-line.

### contexts
- [living] **contexts/ module directory** `contexts/` — Only 3 entries: one constitution doc, one seed context file, one pycache — a very small module.
- [living] **AGENTS.md constitution** `contexts/AGENTS.md` — Claims contexts self-register by file drop-in and are resolvable via context:// scheme; references an acceptance test that asserts the live set is reflected here.
- [unknown] **__pycache__ directory** `contexts/__pycache__` — Standard Python bytecode cache; no contents shown.
- [living] **company_overview.py seed context** `contexts/company_overview.py` — Declares the only live context shown; content is a one-paragraph Company frame, truncated mid-string in the material.
- [living] **CONTEXT registry row** `contexts/company_overview.py :: CONTEXT = {...}` — Uses the same minimal schema as skills: id, content, label, description; id matches file stem.
  - dormant-candidates: contexts/ directory itself looks half-built as a general registry: only one seed member (company_overview.py) exists despite the constitution describing it as a reusable, file-discovered registry for arbitrary contexts — no other <id>.py files are present.
  - surprises: The constitution says contexts 'exactly mirror' skills/roles/node-types self-registration, but the directory contains only ONE seed context file (company_overview.py) — a registry module with a single member is unusual if it is meant to be a general facility. · The acceptance test file tests/skills_contexts_acceptance.py is referenced as the drift-home enforcer, but its contents are not shown here; we cannot verify the live set assertion. · The content string in company_overview.py is truncated mid-sentence in the material ('The Company is an identity-coupled AI system that the Commander (Tim) directs through a'), so we cannot confirm the full resolved blob.

### checks
- [living] **checks/ module constitution** `checks/AGENTS.md` — Claims to enumerate all rows, but only lists 2 despite framing as a general registry (G3·S3a).
- [half-built] **dossier_refcheck check row** `checks/dossier_refcheck.py` — CHECK dict is complete, but the check() function body is truncated mid-return — we cannot confirm it is wired/used.
- [half-built] **prose_clean check row** `checks/prose_clean.py` — CHECK dict is complete, but the check() function body is truncated mid-return — we cannot confirm it is wired/used.
- [unknown] **__pycache__ directory** `checks/__pycache__` — Listed in directory but no contents shown; suggests the .py files have been imported/executed at least once.
  - dormant-candidates: checks/dossier_refcheck.py — CHECK dict built, but check() body truncated; no evidence of runtime/checks.py loader actually calling it. · checks/prose_clean.py — CHECK dict built, but check() body truncated; no evidence of runtime/checks.py loader actually calling it. · checks/AGENTS.md 'The rows' section — only 2 rows listed despite the registry framing implying more may be intended.
  - surprises: The constitution says 'Add a check = add a FILE + reflect it here' and frames checks as a general registry, but only 2 rows exist and both are truncated mid-implementation. · Both check modules mutate sys.path at runtime to reach design/_system, rather than using a package import — a brittle absolute-path coupling to /home/tim/company/.

### channels
- [living] **channels directory** `channels/` — Top-level module with 9 entries; contains both runtime code and configuration for a Claude Code MCP channel server.
- [living] **channel.mcp.json** `channels/channel.mcp.json` — MCP server config declaring 'company-channel' pointing at absolute path /home/tim/company/channels/company_channel.mjs with COMPANY_ROOT env.
- [living] **company_channel.mjs** `channels/company_channel.mjs` — Self-described cross-session live-injection channel server; registers session metadata under .data/channels/ and has reply/announce tools.
- [living] **claude-fabric.sh** `channels/claude-fabric.sh` — Wrapper script intended to auto-attach every interactive Claude launch to the channel fabric; claims fail-safe fallback if config missing.
- [living] **.gitignore** `channels/.gitignore` — Ignores all JSON except channel.mcp.json and package.json; also ignores reply/mail/thread artifacts suggesting expected runtime data files.
- [unknown] **profile-hook.sh** `channels/profile-hook.sh` — Present in directory listing but content not shown; name suggests shell profile integration possibly related to claude-fabric.sh.
- [unknown] **profile_test.mjs** `channels/profile_test.mjs` — Present in directory listing but content not shown; likely a test file for profile/hook behavior.
- [unknown] **package.json** `channels/package.json` — Present in directory listing but content not shown; would declare dependencies including MCP SDK.
- [unknown] **package-lock.json** `channels/package-lock.json` — Present in directory listing but content not shown.
- [unknown] **node_modules** `channels/node_modules` — Present in directory listing but content not shown; dependency tree for the channel server.
  - dormant-candidates: profile-hook.sh (channels/profile-hook.sh) — present but not shown; may be a half-built or unused profile integration companion to claude-fabric.sh. · profile_test.mjs (channels/profile_test.mjs) — present but not shown; may be an abandoned or never-run test for the profile hook.
  - surprises: The wrapper script claude-fabric.sh uses a 'dangerously-load-development-channels' flag and execs the real Claude binary by full path to avoid recursion — this is an unusual, manually-constructed integration pattern. · company_channel.mjs writes session registration to .data/channels/ on load, making the server self-registering at startup rather than being registered by an external orchestrator. · .gitignore explicitly whitelists only channel.mcp.json and package.json among *.json, implying many runtime JSON artifacts are expected and intentionally excluded from version control.

### channel-memory
- [half-built] **CODES_OF_CONDUCT.md** `channel-memory/CODES_OF_CONDUCT.md` — v1 DRAFT explicitly provisional; role section truncated mid-sentence ('hos') — drafted but not finalized.
- [half-built] **COMMIT-GRAMMAR.md** `channel-memory/COMMIT-GRAMMAR.md` — DRAFT v0.1 framed by lead, explicitly not locked by single session; layout rules listed but content cuts off mid-item ('Pro').
- [living] **README.md** `channel-memory/README.md` — Established communal vault with trust/author/date metadata; layout list truncated mid-word ('SHAR').
- [living] **TIM-INTERFACE-SYNTHESIS-2026-06-16.md** `channel-memory/TIM-INTERFACE-SYNTHESIS-2026-06-16.md` — Verbatim storage of Tim's message per explicit instruction; marked as seed/idea-to-get-started, not spec.
- [unknown] **channel_attachments directory** `channel-memory/channel_attachments` — Listed as directory entry; no material shown from inside.
- [unknown] **design directory** `channel-memory/design` — Listed as directory entry; README says it holds A-D lane-inputs but no material shown.
- [unknown] **images directory** `channel-memory/images` — Listed as directory entry; no material shown from inside.
- [unknown] **map directory** `channel-memory/map` — Listed as directory entry; README says lineage/distance/clone-map but no material shown.
- [unknown] **mega-prep directory** `channel-memory/mega-prep` — Listed as directory entry; README truncates its purpose ('SHAR').
- [unknown] **noticeboard directory** `channel-memory/noticeboard` — Listed as directory entry; not mentioned in README layout at all.
- [unknown] **plan directory** `channel-memory/plan` — Listed as directory entry; not mentioned in README layout.
- [unknown] **recall directory** `channel-memory/recall` — Listed as directory entry; README says recall decisions + embedding/recall fix records but no material shown.
- [unknown] **scans directory** `channel-memory/scans` — Listed as directory entry; README says scan output as DATA but no material shown.
- [unknown] **schema directory** `channel-memory/schema` — Listed as directory entry; README says session-store/source schemas but no material shown.
- [unknown] **vision directory** `channel-memory/vision` — Listed as directory entry; README says Tim's intents decompressed but no material shown.
  - dormant-candidates: noticeboard/ — exists in directory listing but not referenced in README.md layout or any shown file · plan/ — exists in directory listing but not referenced in README.md layout or any shown file · CODES_OF_CONDUCT.md — drafted v1, marked provisional, content truncated mid-role; not yet hardened or confirmed · COMMIT-GRAMMAR.md — drafted v0.1, explicitly not locked by single session, content truncated mid-layout-item
  - surprises: README.md's layout list omits two directories that actually exist: noticeboard/ and plan/. · CODES_OF_CONDUCT.md and COMMIT-GRAMMAR.md are both explicitly DRAFT and provisional, yet README.md says 'Every member writes here under the COMMIT-GRAMMAR' — implying a rule that is still co-designed and not finalized. · CODES_OF_CONDUCT.md names Tim as 'OVERLORD + ORIGIN' and lead as 'HOST + CONDUIT + STEWARD' — a hierarchical governance model not obviously reflected in the communal-vault framing.

### cascades
- [living] **AGENTS.md constitution** `cascades/AGENTS.md` — Explicitly forbids hardcoded CASCADES={...} and declares cascades are file-dropped, not create()-authorable because the row carries a callable.
- [dormant] **accessibility_specs cascade** `cascades/accessibility_specs.py` — CLOUD-ONLY row with a handle() that raises NotImplementedError; handler is intentionally dead on the ④ side.
- [living] **address cascade** `cascades/address.py` — Requires face key 'address'; defaults template to vi.{user}.{tid}.{id} if faces.address.template absent.
- [half-built] **board cascade** `cascades/board.py` — Docstring says status_values default to type.states, but the shown source cuts off mid-comment; implementation is incomplete in the material.
- [dormant] **capability cascade** `cascades/capability.py` — CLOUD-ONLY row with a handle() that raises NotImplementedError; present only to report skipped:reason.
  - dormant-candidates: accessibility_specs.py handle() — cascades/accessibility_specs.py (cloud_only, raises NotImplementedError) · capability.py handle() — cascades/capability.py (cloud_only, raises NotImplementedError) · board.py implementation — cascades/board.py (docstring complete but source cuts off before handle body finishes)
  - surprises: Two of the five visible cascades (accessibility_specs, capability) are deliberately dead handlers whose only purpose is to make generate_all emit 'skipped:reason' rather than doing work. · AGENTS.md says cascades are 'CODE-authored (dropping a file), NOT create()-authorable' — a rare explicit rejection of the declarative create() path for a registry row. · board.py's source is truncated mid-implementation even though its docstring is complete; the actual derivation logic is not shown.

### canvas
- [living] **canvas directory** `canvas/` — Top-level frontend module with only 4 entries shown; app/ is a black box in this material.
- [living] **canvas constitution** `canvas/AGENTS.md` — Explicitly prescriptive/living; declares one generic ai-node shape, no per-node-type frontend code, canvas reflects state but never owns it.
- [dormant] **empty .gitkeep** `canvas/.gitkeep` — Empty placeholder; may be vestigial now that AGENTS.md and index.html exist.
- [unknown] **Vite/React app shell** `canvas/app/` — Only listed as a directory entry; its README and actual contents are not in the material, so we cannot verify living/dormant/half-built.
- [unknown] **extensions live-tree** `canvas/app/src/extensions/` — Described as brain-authored runtime UI extensions, gated; own module/constitution not shown here.
- [living] **operator console HTML entry** `canvas/index.html` — Hardcoded Fraunces + IBM Plex Mono font loading from Google; title 'the company · operator console'.
  - dormant-candidates: canvas/.gitkeep — empty placeholder in a directory that now has real files. · canvas/app/ — asserted to contain a full Vite/React app with many surfaces, but only the directory name appears in the material; actual contents unverified and may be half-built or missing.
  - surprises: The constitution says the canvas 'reflects state, never owns it' and is a peer via the bridge, but no bridge wiring or runtime connection code is visible in the provided material. · AGENTS.md references surfaces (now-view, inspector, inbox, RHM panel, presence dial, fleet) as things that live in canvas/app/, yet none of those files are shown in the directory listing. · The directory listing only shows 4 entries; the described rich app structure (app/src/extensions/, README, etc.) is asserted but not evidenced here.

### build-prep
- [living] **CROSS-SESSION-CHANNELS-PROVEN.md** `build-prep/CROSS-SESSION-CHANNELS-PROVEN.md` — Claims live two-way cross-session messaging and group chat already proven via company MCP; references a specific channels server implementation and supervisor reply path.
- [living] **HARVEST-composition.md** `build-prep/HARVEST-composition.md` — Self-described as composition lane's honest current-state view with explicit verification-provenance split; deliberately avoids self-certified 'done'.
- [half-built] **MODE-SYSTEM-MAP.md** `build-prep/MODE-SYSTEM-MAP.md` — Claims the mode-dial SOURCE was unified but downstream REACH was never extended; explicitly flags drift between one source and five arms.
- [half-built] **cross-session-unified-transport.md** `build-prep/cross-session-unified-transport.md` — DESIGN-ONLY pre-implementation draft; explicitly states no cc_channels.py edit is made by this doc and requires lead review + surface to Tim before landing.
- [unknown] **brain directory** `build-prep/brain` — Listed as directory entry; no content provided in material.
- [unknown] **claude-design directory** `build-prep/claude-design` — Listed as directory entry; no content provided in material.
- [unknown] **cognition-engine directory** `build-prep/cognition-engine` — Listed as directory entry; no content provided in material.
- [unknown] **cognition-self-improvement directory** `build-prep/cognition-self-improvement` — Listed as directory entry; no content provided in material.
- [unknown] **cognition-tools directory** `build-prep/cognition-tools` — Listed as directory entry; no content provided in material.
- [unknown] **coherence directory** `build-prep/coherence` — Listed as directory entry; no content provided in material.
- [unknown] **common-knowledge directory** `build-prep/common-knowledge` — Listed as directory entry; no content provided in material.
- [unknown] **company-landscape directory** `build-prep/company-landscape` — Listed as directory entry; no content provided in material.
- [unknown] **concurrent-cognition directory** `build-prep/concurrent-cognition` — Listed as directory entry; no content provided in material.
- [unknown] **context-forager directory** `build-prep/context-forager` — Listed as directory entry; no content provided in material.
- [unknown] **coordination directory** `build-prep/coordination` — Listed as directory entry; no content provided in material.
- [unknown] **coverage-mechanism directory** `build-prep/coverage-mechanism` — Listed as directory entry; no content provided in material.
- [unknown] **embedder-pplx directory** `build-prep/embedder-pplx` — Listed as directory entry; no content provided in material.
- [unknown] **episodic-memory-adaptation directory** `build-prep/episodic-memory-adaptation` — Listed as directory entry; no content provided in material.
- [unknown] **front-interface directory** `build-prep/front-interface` — Listed as directory entry; no content provided in material.
- [unknown] **gpu-serving-rework directory** `build-prep/gpu-serving-rework` — Listed as directory entry; no content provided in material.
- [unknown] **guided-review-surface directory** `build-prep/guided-review-surface` — Listed as directory entry; no content provided in material.
- [unknown] **instrument-surface directory** `build-prep/instrument-surface` — Listed as directory entry; no content provided in material.
- [unknown] **live-resolution-surface directory** `build-prep/live-resolution-surface` — Listed as directory entry; no content provided in material.
- [unknown] **memory-archaeology directory** `build-prep/memory-archaeology` — Listed as directory entry; no content provided in material.
- [unknown] **mesh directory** `build-prep/mesh` — Listed as directory entry; no content provided in material.
- [unknown] **model-routing-unification directory** `build-prep/model-routing-unification` — Listed as directory entry; no content provided in material.
- [unknown] **openwebui-company-fusion directory** `build-prep/openwebui-company-fusion` — Listed as directory entry; no content provided in material.
- [unknown] **openwebui-fabric-research directory** `build-prep/openwebui-fabric-research` — Listed as directory entry; no content provided in material.
- [unknown] **operator-surface directory** `build-prep/operator-surface` — Listed as directory entry; no content provided in material.
- [unknown] **registry-generation directory** `build-prep/registry-generation` — Listed as directory entry; no content provided in material.
- [unknown] **self-build-surface directory** `build-prep/self-build-surface` — Listed as directory entry; no content provided in material.
- [unknown] **self-serve-core directory** `build-prep/self-serve-core` — Listed as directory entry; no content provided in material.
- [unknown] **the-one-application directory** `build-prep/the-one-application` — Listed as directory entry; no content provided in material.
- [unknown] **the-one-system directory** `build-prep/the-one-system` — Listed as directory entry; no content provided in material.
- [unknown] **trigger-system directory** `build-prep/trigger-system` — Listed as directory entry; no content provided in material.
- [unknown] **unify-laws directory** `build-prep/unify-laws` — Listed as directory entry; no content provided in material.
- [unknown] **universal-projection directory** `build-prep/universal-projection` — Listed as directory entry; no content provided in material.
  - dormant-candidates: cross-session-unified-transport.md (build-prep/cross-session-unified-transport.md) — design draft, explicitly no implementation edits made, awaiting lead review and Tim surfacing. · MODE-SYSTEM-MAP.md downstream arms (build-prep/MODE-SYSTEM-MAP.md) — source unified but reach 'never extended'; arms 2-5 appear un-wired or only partially mapped.
  - surprises: CROSS-SESSION-CHANNELS-PROVEN.md claims the cross-session goal is already 'PROVEN BY USE' and live, while cross-session-unified-transport.md exists as a separate DESIGN-ONLY document for the same problem space — a possible duplication or versioning tension. · MODE-SYSTEM-MAP.md explicitly states the mode-dial join unified the source but downstream reach 'was never extended' — an unusual self-flag of incomplete wiring in a top-level map. · HARVEST-composition.md introduces a deliberate verification-provenance split and rejects self-certified 'done', suggesting the territory has had trust/attribution problems.

### board_edges
- [living] **AGENTS.md constitution** `board_edges/AGENTS.md` — Explicitly documents a deliberate fork: same RelationTypeRegistry mechanism as relation_types/ but a SEPARATE vocabulary directory, with a future-unification idea tracked as a board item.
- [living] **attached_to relation type** `board_edges/attached_to.py` — Describes itself as mirroring a 'CHANNEL-LAYER-SEAM attachments manifest one level down' — that manifest is named but not present in the material.
- [living] **attachment relation type** `board_edges/attachment.py` — Has an explicit inverse declared (`attached_to`) but `attached_to.py` does NOT declare an inverse back to `attachment` — the inverse is one-way in the files shown.
- [living] **authored_by relation type** `board_edges/authored_by.py` — Inverse is `authored`, but no `authored.py` file appears in the directory listing.
- [living] **blocked_by relation type** `board_edges/blocked_by.py` — No inverse declared; described as a CONCEPTUAL edge surfaced 'by-use during the wind-down harvest (recollection)' — harvest-specific, not a general board link.
  - dormant-candidates: Inverse relation files that are referenced but missing: `authored` (inverse of authored_by at board_edges/authored_by.py) — declared but no board_edges/authored.py present in directory listing. · Unmentioned edge files in board_edges/ directory: attachment.py, blocked_by.py, commented_on.py, composes_with.py, part_of.py, pinned.py, promoted_from.py, references.py, refutes.py, reply_to.py, same_law.py, sourced_from.py are listed but not covered by the visible 'live set' in AGENTS.md (which stops at pinned).
  - surprises: The directory lists 16 edge files, but AGENTS.md's 'live set' only enumerates 5 edge-kinds (authored_by, attached_to, sourced_from, promoted_from, pinned) and is cut off mid-word at `pinned` — the constitution does not account for the other 11 files in its visible 'live set'. · `attachment.py` declares `inverse: attached_to`, but `attached_to.py` does not declare any inverse at all. The inverse pair is asymmetric in the material shown. · `authored_by.py` declares `inverse: authored`, yet no `authored.py` exists in the 16-entry directory listing.

### bindings
- [living] **AGENTS.md manifest** `bindings/AGENTS.md` — Declares the module is a variable instrument: one file per binding, no hardcoded sectors, and the default is raw kinds.
- [half-built] **by_cascade binding** `bindings/by_cascade.py` — Truncated mid-dict: id is 'by_casc' (incomplete string), and radius_from='time' is explicitly a placeholder.
- [half-built] **by_lens binding** `bindings/by_lens.py` — Meta block is a TENTATIVE draft awaiting ratification; order_by='count' is a fallback because registry-row edges are a future growth front.
- [half-built] **by_node_type binding** `bindings/by_node_type.py` — Radius_from='time' is again a placeholder; the view is about edges, not radius.
- [living] **by_nucleation binding** `bindings/by_nucleation.py` — Truncated mid-sentence ('drivable per req'), but the law and mechanism are fully described.
- [unknown] **raw.py binding file** `bindings/raw.py` — Listed in directory but no content provided; AGENTS.md says raw kinds are the data-driven default.
- [unknown] **by_separator.py binding file** `bindings/by_separator.py` — Listed in directory but no content provided.
- [unknown] **grouped.py binding file** `bindings/grouped.py` — Listed in directory but no content provided.
- [unknown] **semantic.py binding file** `bindings/semantic.py` — Listed in directory but no content provided.
- [unknown] **time-of-day.py binding file** `bindings/time-of-day.py` — Listed in directory but no content provided.
- [dormant] **__pycache__ directory** `bindings/__pycache__` — Compiled Python cache; artifact of execution, not source.
  - dormant-candidates: bindings/__pycache__ — compiled cache, not source · bindings/by_cascade.py — id string 'by_casc' is truncated/unclosed in the excerpt; may be half-built or broken · bindings/by_lens.py — meta block marked TENTATIVE draft, not ratified · bindings/by_node_type.py — radius_from='time' placeholder, not a real radius axis
  - surprises: AGENTS.md says bindings are discovered as bindings/<id>.py, but the directory contains files with underscores (by_cascade.py) and hyphens (time-of-day.py); the id normalization rule is not shown. · Three of the five shown bindings explicitly use radius_from='time' as a placeholder, suggesting the radius axis is under-specified across the module. · by_lens.py declares its own meta.name as 'Ways of looking' and notes it is TENTATIVE/draft — a binding describing the lens system is itself not ratified. · by_cascade.py's BINDING dict is truncated with an unclosed string id: 'by_casc' — the file appears syntactically broken in the excerpt.

### axes
- [living] **axes/ directory as file-discovered axis registry** `axes/` — Top-level module with 10 entries; AGENTS.md frames it as a self-extending coordinate vocabulary where adding an axis = dropping a file.
- [living] **AGENTS.md registry documentation** `axes/AGENTS.md` — Explicitly says axis set is seeded, not final; mentions perspective/intent/posture as 'a-row-away' but not yet present in directory listing.
- [half-built] **design.py axis module** `axes/design.py` — Docstring cuts off mid-sentence at 'the decisions populat' — the AXIS dict itself is not shown in the excerpt, only the preamble.
- [living] **device.py axis module** `axes/device.py` — Fully declares AXIS dict with w/h continuous, orient/kind discrete; value_source='live'; kind is browser-derived, not authoritative.
- [living] **mode.py axis module** `axes/mode.py` — Single discrete field 'current' with four behaviour families; re-resolve on change.
- [living] **register.py axis module** `axes/register.py` — Theme/finish axis; 'dark-observatory · others' implies only one theme is actually named so far.
- [unknown] **resolution.py axis module** `axes/resolution.py` — Only referenced by name in design.py docstring; no excerpt provided.
- [unknown] **state.py axis module** `axes/state.py` — Listed in directory but no excerpt provided.
- [unknown] **type.py axis module** `axes/type.py` — Listed in directory but no excerpt provided.
- [unknown] **viewer.py axis module** `axes/viewer.py` — Listed in directory but no excerpt provided.
- [dormant] **__pycache__ directory** `axes/__pycache__` — Compiled bytecode cache; artifact of execution, not source-of-truth for the registry.
  - dormant-candidates: axes/design.py — docstring truncated, AXIS dict not shown in material (where: axes/design.py) · axes/__pycache__ — compiled cache, not a registry source (where: axes/__pycache__) · register.py 'others' theme value — mentioned but never enumerated (where: axes/register.py fields.theme)
  - surprises: AGENTS.md names perspective, intent, posture as 'a-row-away' but none exist in the directory — a planned extension set with no files yet. · design.py's docstring is truncated mid-word ('the decisions populat') and the AXIS dict is missing from the excerpt, making it the only seeded axis whose declaration is not visible. · register.py lists 'dark-observatory · others' but only 'dark-observatory' is actually named; 'others' is a placeholder with no enumerated values. · AGENTS.md claims 'zero engine code' and file-drop extensibility, but __pycache__ presence means the module has been imported/compiled by something.

### attachment_types
- [living] **board_items attachment type** `attachment_types/board_items.py` — Defines an attachment type for board://<id> items, but only the head is shown; no implementation body visible.
- [living] **cloning attachment type** `attachment_types/cloning.py` — Point-in-time cloning capability registered; target_kind is 'scope' rather than address/path.
- [living] **docs attachment type** `attachment_types/docs.py` — Documentation files loaded as context for members on join — implies a join-time loader elsewhere.
- [living] **dragnet_runs attachment type** `attachment_types/dragnet_runs.py` — Most verbose descriptor; claims run telemetry is 'queryable' and channel accumulates history, but no query mechanism is shown.
- [unknown] **images attachment type** `attachment_types/images.py` — File exists in directory listing but no content shown.
- [unknown] **recall attachment type** `attachment_types/recall.py` — File exists in directory listing but no content shown.
- [unknown] **sessions attachment type** `attachment_types/sessions.py` — File exists in directory listing but no content shown.
- [dormant] **__pycache__ directory** `attachment_types/__pycache__` — Compiled bytecode cache; artifact of import, not source of truth.
  - dormant-candidates: __pycache__ at attachment_types/__pycache__ — generated cache, not actively maintained source. · images.py, recall.py, sessions.py at attachment_types/images.py, attachment_types/recall.py, attachment_types/sessions.py — present in census but content not shown; may be stubs or unused.
  - surprises: Directory has 8 entries but only 4 attachment type heads were provided; 3 source files (images.py, recall.py, sessions.py) are completely opaque in this material. · dragnet_runs.py makes strong claims about queryable history and telemetry accumulation, but no supporting machinery is visible in the provided excerpts. · Every shown attachment type uses the same top-level dict pattern (ATTACHMENT_TYPE) with no registration/wiring code visible in the heads.

### ai_tics
- [living] **AGENTS.md constitution** `ai_tics/AGENTS.md` — Declares itself a file-discovered registry with one AI_TIC dict per file; explicitly forbids a python dict registry.
- [living] **agent_arch tic** `ai_tics/agent_arch.py` — Markers are all agent-architecture phrases; id matches file stem as required.
- [living] **closure_form tic** `ai_tics/closure_form.py` — Markers are closure-form phrases; note the 'expansion-ratio<1' design criterion in desc.
- [living] **false_finality tic** `ai_tics/false_finality.py` — Markers are done/complete/fixed claims without evidence.
- [living] **framework_imposition tic** `ai_tics/framework_imposition.py` — Constitution comment ends mid-sentence ('id MUST equal the file stem.') but the AI_TIC dict is complete.
- [unknown] **silent_fallback tic** `ai_tics/silent_fallback.py` — Listed in directory and AGENTS.md live set, but file content not shown in material.
- [unknown] **versioning tic** `ai_tics/versioning.py` — Listed in directory and AGENTS.md live set, but file content not shown in material.
- [unknown] **mvp tic** `ai_tics/mvp.py` — Listed in directory but NOT mentioned in AGENTS.md's enumerated live set; content not shown.
- [dormant] **__pycache__** `ai_tics/__pycache__` — Compiled bytecode cache; artifact of execution, not a registry entry.
  - dormant-candidates: ai_tics/mvp.py — present in directory, not named in AGENTS.md live set, content not shown · ai_tics/__pycache__ — generated artifact, not part of the registry schema
  - surprises: mvp.py exists in the directory but is absent from the AGENTS.md live-set enumeration, despite the constitution saying the live set is asserted by tests/ai_tics_acceptance.py. · AGENTS.md's framework_imposition.py excerpt cuts off mid-comment ('id MUST equal the file stem.') even though the AI_TIC dict below is complete — possible truncation artifact or the file literally ends the comment there. · The directory lists 9 entries but the material only shows heads for 4 of the 6 .py files; silent_fallback.py and versioning.py are referenced as live but unverified.

### STATE.md
- [living] **STATE.md state document** `FILE STATE.md` — Self-described as the third doc a fresh AI reads after rules + map; explicitly maintained by integration, not append-only.
- [living] **SUITES auto-maintained marker** `FILE STATE.md line `<!--SUITES:START--> (auto-maintained by Suite.refresh_self_description — do not hand-edit)`` — The suite list is machine-generated; the excerpt cuts off mid-list at `gate_accep`.
- [half-built] **Concurrent Cognition build-prep directory** `build-prep/concurrent-cognition/` — Described as 'Next loop' and 'staged main stream fed by a 32-way swarm' — future work with expected heavy overlap, not yet proven.
- [half-built] **Loadout resolution + atomic switch actuator** `FILE STATE.md paragraph beginning 'Captured-not-built: **loadout resolution**'` — Explicitly labeled 'Captured-not-built': work declares required loadout, atomic switch should evict+start+repoint-RHM, fixing a known bug where RHM stays on evicted model.
- [living] **Capability resolver registries** `runtime/capabilities/` — Serve-flags now generated from typed registries; loud-fail if a model cannot resolve.
- [living] **Voice durable event logging** `FILE STATE.md paragraph beginning '**Voice is fully traced**'` — Claims every voice turn writes detailed durable records to events.jsonl with per-step timing and failure details.
- [living] **Model/VRAM layer with config blocks** `FILE STATE.md paragraph beginning '**2026-06-07 — model/VRAM layer + voice co-residence + persona identity**'` — Service config blocks are declared the ONE source for model sizing; fit surface answers whether a selection fits 16 GB card.
- [living] **FP8 brain loadout** `FILE STATE.md paragraph beginning '**2026-06-29 — capability-resolution spine + the FP8 brain loadout**'` — Everyday brain is Qwen3.5-4B-FP8 with fp8 KV-cache giving 65,536 context co-resident with recall embedder + voice.
- [dormant] **Forced-tool-choice capability probe** `FILE STATE.md line 'The forced-tool-choice capability probe is RETIRED'` — A retired probe — code may still exist but is no longer used for capability verification.
- [living] **Acceptance suites as convergence record** `FILE STATE.md section 'Acceptance suites (the convergence record)'` — 259 suites listed; the material is truncated at `gate_accep` so the full list is not verifiable here.
  - dormant-candidates: Forced-tool-choice capability probe — retired (FILE STATE.md line 'The forced-tool-choice capability probe is RETIRED') · Loadout resolution + atomic loadout-switch actuator — captured-not-built (FILE STATE.md paragraph beginning 'Captured-not-built: **loadout resolution**')
  - surprises: A doc explicitly warns it is 'maintained by integration' and 'not append-only' — unusual for a project state file, suggesting it is regenerated rather than hand-edited. · The 'Captured-not-built' paragraph names a real bug ('company up @loadout leaving the RHM on the evicted model') and a fix that is described but not claimed as implemented. · The forced-tool-choice capability probe is explicitly retired, meaning an old verification mechanism was removed while capability declarations are now taken as truth.

### SESSION-OPERABLE-INTERFACE.md
- [living] **SESSION-OPERABLE-INTERFACE.md handoff doc** `FILE SESSION-OPERABLE-INTERFACE.md` — Self-described as cross-session awareness doc dated 2026-06-07; explicitly subordinates itself to STATE.md + tests.
- [living] **operable-interface-build branch / worktree** `/home/tim/company-interface · branch: operable-interface-build · bridge :8771 · vite :5174` — Isolated worktree off live system; shares one git repo with main checked out in ~/company.
- [living] **28 commits ahead of merge-base c7ea69b05** `section 1` — Claimed verified by use on desktop 1440 + phone 390; gaps logged in GAPS-REGISTER.md.
- [living] **A/H cockpit regions** `canvas/app/src/regions/*, App.tsx, app.css, kit` — Includes consolidated Settings (A3) control-room with 5 sections: brain/modes/voice/roles/composition.
- [living] **B consent model** `ProposeAffordance.tsx, Inbox.tsx, suite verbs` — B3: configurable defer-to-inbox as live revivable offer.
- [living] **C show-me bootstrap** `Walkthrough.tsx, .ui-spotlight` — Model-free guided tour (C1), teach-to-self-modify (C2), spotlight/walkthrough organ (C3/C4).
- [living] **D altitude help surface** `AddressHelp.tsx` — address_help composed of what-this-is + how-to-change + how-to-use behind a drill-down.
- [living] **E modes-as-context-resolution** `MODE_SPECS / resolution_spec_for in suite.py` — Mode-type declarations now drive _resolve_context_at; live off/suggest/auto autodetect toggle.
- [living] **F1 altitude transformation + learning loop** `coa, up_translate, set_presentation_pref, ShapeHow.tsx` — Commander shapes presentation from inside (voice/typing); system adapts + remembers.
- [living] **G1/G3 corpus-true registry** `design/_system/*` — Zero-orphan gate: every UI element registered, ref'd, resolves, has a how-to.
- [living] **24 new defs in runtime/suite.py** `runtime/suite.py` — Mostly in RHM-verb / altitude / R2-howto area.
- [living] **MODE_SPECS single source derivation** `runtime/suite.py:MODE_SPECS / MODES / MODE_DIRECTIVES` — MODES and MODE_DIRECTIVES now derived from MODE_SPECS.
- [living] **set_rhm_config allowed whitelist addition** `runtime/suite.py:set_rhm_config allowed whitelist` — Added MODE_AUTODETECT to allowed whitelist.
- [living] **7 new bridge routes** `runtime/bridge.py` — Claimed disjoint from main's 9 voice/settings routes.
- [living] **useAppController handlers** `canvas/app/src/useAppController.ts` — A3 settings state includes settingsTab, roles, modeRegistry, autodetect, compositionCfg…
- [living] **openStream dispatch collision zone** `canvas/app/src/useAppController.ts:openStream (~355–403)` — Session warns: add cognition.* as NEW branch, don't refactor switch shape.
- [living] **api.ts appended client methods** `canvas/app/src/api.ts` — Only appends; claimed disjoint from cognition fetchers.
- [dormant] **NodeShape.tsx untouched by this session** `canvas/app/src/regions/NodeShape.tsx` — Explicitly noted as clean for cognition session — this session did NOT touch it.
- [dormant] **nodes/llm.py, runtime/scheduler.py, fabric/transport.py, fabric/vram.py untouched** `nodes/llm.py, runtime/scheduler.py, fabric/transport.py, fabric/vram.py` — All declared clean for cognition session.
- [half-built] **Stage 1 merge plan** `section 4` — Plan to merge main INTO branch first, resolve 9 conflict files, then fast-forward main; text is truncated mid-sentence at 'fast-forward at t'.
  - dormant-candidates: NodeShape.tsx — declared untouched by this session (where: canvas/app/src/regions/NodeShape.tsx); may be dormant relative to operable-interface work but is reserved for cognition session. · nodes/llm.py, runtime/scheduler.py, fabric/transport.py, fabric/vram.py — declared untouched by this session (where: listed in section 3); dormant in operable-interface scope. · Stage 1 merge plan — half-built/truncated (where: section 4); the actual merge execution is not present in the material.
  - surprises: The doc claims 24 new defs in suite.py but only names 23 in the bullet list (counted: address_help, up_translate, coa, start_guide, start_walkthrough, set_presentation_pref, presentation_pref_at, autodetect_mode, resolution_spec_for, get_submode, set_submode, defer_offer, revive_offer, _r2_howto_at, _r2_pref_at, _apply_presentation_pref, _validate_presentation_pref, _registry_howto_for, _guide_sequence, _guide_steps, _live_complete, _cfg_choice, _ok, to_text = 24). Actually 24. No surprise. · The merge plan sentence is truncated mid-word ('fast-forward at t'), so the actual timing/actor is missing from the material. · NodeShape.tsx is declared 'clean for you' but the cognition session's plans are referenced without any material from that session — this is a forward-looking claim, not an observed state.

### README.md
- [living] **README.md top-level doc** `FILE README.md` — Self-describes as 'Skeleton only' — boundaries drawn, nothing implemented.
- [unknown] **AGENTS.md pointer** `FILE README.md line 'AI agents: read [`AGENTS.md`](AGENTS.md) first'` — Referenced as first doc AI agents must read, but file content not supplied.
- [unknown] **MAP.md pointer** `FILE README.md line 'then [`MAP.md`](MAP.md)'` — Referenced as second doc AI agents must read, but file content not supplied.
- [dormant] **contracts/ directory** `FILE README.md table row 'contracts/'` — Directory listed with responsibility but README says nothing implemented; likely empty or stub.
- [dormant] **store/ directory** `FILE README.md table row 'store/'` — Responsibility defined but README says skeleton only; not confirmed implemented.
- [dormant] **runtime/ directory** `FILE README.md table row 'runtime/'` — Should host scheduler + bridge; README says nothing implemented.
- [dormant] **fabric/ directory** `FILE README.md table row 'fabric/'` — Model-fabric binding layer; README says skeleton only.
- [dormant] **mcp_face/ directory** `FILE README.md table row 'mcp_face/'` — Named 'mcp_face' deliberately to avoid collision with 'mcp' SDK; no implementation confirmed.
- [dormant] **nodes/ directory** `FILE README.md table row 'nodes/'` — Node library; README says nothing implemented.
- [dormant] **canvas/ directory** `FILE README.md table row 'canvas/'` — Frontend track; README says skeleton only.
- [dormant] **docs/ directory** `FILE README.md table row 'docs/'` — Only a pointer to build-prep vault; likely minimal or empty.
- [unknown] **build-prep vault path** `FILE README.md line '/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/'` — Declared as source of truth, but path is outside repo on Windows /mnt/c; not material-supplied.
- [unknown] **Phase-1 Build Plan reference** `FILE README.md line 'See `build-prep/Phase-1 Build Plan.md`.'` — First milestone defined there; content not supplied.
  - dormant-candidates: contracts/ — listed as pinned data shapes but README says nothing implemented (FILE README.md table row 'contracts/') · store/ — listed as addressed store + resolver but README says nothing implemented (FILE README.md table row 'store/') · runtime/ — listed as scheduler + bridge but README says nothing implemented (FILE README.md table row 'runtime/') · fabric/ — listed as model-fabric binding but README says nothing implemented (FILE README.md table row 'fabric/') · mcp_face/ — listed as agent face but README says nothing implemented (FILE README.md table row 'mcp_face/') · nodes/ — listed as node library but README says nothing implemented (FILE README.md table row 'nodes/') · canvas/ — listed as frontend but README says nothing implemented (FILE README.md table row 'canvas/') · docs/ — listed as pointer to vault only (FILE README.md table row 'docs/')
  - surprises: The repo claims to be built entirely by AI agents and references per-module AGENTS.md constitutions, yet the README itself declares 'Skeleton only. Boundaries drawn; nothing implemented.' — a highly structured, contract-heavy scaffold with no implementation. · The source of truth is explicitly outside the repo at an absolute Windows/WSL path `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/`, meaning the repo may be a partial mirror or landing zone while specs live elsewhere. · Directory named `mcp_face/` instead of `mcp/` solely to avoid SDK namespace collision — unusual naming driven by dependency conflict rather than domain semantics.

### MERGE-COORDINATION.md
- [living] **MERGE-COORDINATION.md file** `FILE MERGE-COORDINATION.md` — This is a peer-to-peer coordination document between two AI sessions, mediated by a human named Tim, documenting a planned git merge reconciliation.
- [living] **interface session worktree** `Worktree `~/company-interface` (branch `operable-interface-build`)` — The interface session identifies itself as working in ~/company-interface on branch operable-interface-build.
- [living] **self-build wire commits on main** `main's last 3 commits, `72b0012`/`c2178d9`/`72e3a3f`` — The self-build wire (git-safe + async + reviewer-gated) is already merged to main as the last three commits.
- [half-built] **uncommitted wire residue on main checkout** `Uncommitted on the `main` checkout (the "wire residue", 21 files)` — 21 files are uncommitted but verified green; the interface session plans to commit them first. This restructures the self-mod audit ledger.
- [living] **mockup studio + redesign mockups** `On my worktree branch (+2 vs main)` — Design artifacts on the interface branch, to be folded into main.
- [living] **cognition acceptance suites result** `I ran all 11 cognition acceptance suites myself (isolated temp store): ~389 checks green` — Interface session claims to have run cognition's 11 suites and gotten ~389 green checks against the live 4B.
- [living] **merge conflict surface** `9 files touch both sides, but `git merge-tree` shows only 7 real conflicts / 10 hunks` — Most cognition work is additive and unions cleanly; only 7 real conflicts across 10 hunks.
- [dormant] **silent regression at runtime/suite.py line 3756** `runtime/suite.py ~line 3756` — Cognition's chat-core reads GLOBAL chat_history(20), which would silently revert the interface session's thread-scoped fix. No textual conflict; cognition's suites don't catch it.
- [half-built] **mode dial built twice** `MODE_SPECS/resolution_spec_for + THOUGHT_SHAPES/shape_for on the SAME 8 modes` — The two mode systems are described as two halves of one declaration; latent backend capabilities built by interface have no FE caller but match CognitionView needs.
- [half-built] **self-mod audit ledger seam** `_SELF_CHANGE_STREAMS/`_change_stream`` — Post-reconcile verification needed: cognition's [self-apply] commits must still classify under interface's restructured stream logic.
- [living] **cognition session reply (round 1)** `## ⤵ COGNITION SESSION — REPLY (round 1)` — Cognition session confirms the line-3756 catch, but notes the textual conflicts are actually at lines 4851/4911/5053, not 3756. It verifies the global chat_history(20) read is real in its code.
- [living] **Concurrent Cognition layer** `WHAT I BUILT (the cognition stream) + HOW` — Cognition stream built a Concurrent Cognition layer: turn fans out rule-routed ROLES on the 4B, each emits schema-enforced JSON to run:// addresses, RULES route resolved values, main reply assembled as STAGE.
  - dormant-candidates: `/api/knobs`, `/api/run-stats`, R2-tuning, node-states — built by interface but have no FE caller yet (where: 'latent capabilities my stream built with no FE caller'); intended for CognitionView but unwired. · The mode-dial join and latent-gold→CognitionView wiring — described as future integration work, not yet implemented (where: 'Then the integration (mode-dial join, latent-gold→CognitionView, place CognitionView in the new IA)'). · The 21-file wire residue on main checkout — uncommitted but verified green; it exists but is not yet on main (where: 'Uncommitted on the `main` checkout (the "wire residue", 21 files)'). · The thread-scoped fix for chat history — currently only present in interface's stream, at risk of silent reversion (where: 'runtime/suite.py ~line 3756' and 'chats_in_thread(_tid, 20) if _tid else chat_history(20)').
  - surprises: The two AI sessions are coordinating a git merge through a markdown file with a human (Tim) as relay, not through direct communication. · The interface session claims to have run the cognition session's 11 acceptance suites itself and gotten ~389 green checks against the live 4B. · The dangerous silent regression is NOT at a textual conflict location: interface caught global chat_history(20) at line 3756, but cognition says its actual conflicts are at 4851/4911/5053 — meaning the regression would auto-merge silently without any conflict marker. · The mode dial is built twice (MODE_SPECS vs THOUGHT_SHAPES) on the same 8 modes, and backend capabilities built with no FE caller happen to match CognitionView needs — suggesting either planned convergence or accidental duplication. · The cognition session explicitly says its G4 refactor preserved the OLD global read because its branch predates the interface thread-fix — confirming the regression is branch-temporal, not malicious.

### MAP.md
- [living] **MAP.md frontmatter** `FILE MAP.md --- type: map register: descriptive module: root aliases: ["Company Map", "Map of the Company", "MAP"] tags: [company, map, moc, knowledge-space] governs: [] relates-to: ["[[Company — read first]]", "[[Company State]]", "[[Vault Conventions]]", "[[Orienteering Index]]"] status: living ---` — Self-described as the vault home and loadable map; status is explicitly 'living'.
- [unknown] **Drift-check enforcement claim** `FILE MAP.md paragraph: 'drift-check fails loud (`Suite.map_drift`, `tests/drift_acceptance.py`) when a registered node-type / RHM verb / subsystem isn\'t reflected here'` — Claims an automated test exists that prevents silent rot; not verified in this excerpt.
- [living] **Architecture ASCII diagram** `FILE MAP.md code block under 'The one picture'` — Lists 10 subsystems and an extensions directory; describes a bridge via C8/contracts.
- [living] **Mermaid flowchart** `FILE MAP.md mermaid block under 'The one picture'` — Visualizes same architecture; contracts are shown as dotted governance over runtime/store/nodes.
- [living] **Module map table** `FILE MAP.md table under 'Module map (each links to its constitution + governing contracts)'` — 16 modules listed with constitutions and governing contracts; note says constitution links use aliases, not filenames.
- [half-built] **ui-contract module** `FILE MAP.md table row: `ui-contract/` | the UI Contract corpus ... | (README.md is its constitution) | F1.5/F9` — Explicitly described as 'statuses honest (building/planned, nothing live until the driving harness flips it)' — a part-built product.
- [living] **introspection module** `FILE MAP.md table row: `introspection/` | the platform-agnostic Mirror-Registry engine ... + the two Level-2 registries ... | [[introspection — constitution]] | Mirror-Registry System` — Describes a complex registry engine with two Level-2 registries and a platforms/ data table.
- [living] **platforms module** `FILE MAP.md table row: `platforms/` | the Level-2 platform table as DATA — one `PLATFORM = {...}` row per external platform (`claude_code.py` = INSTANCE #1, Spec §7); DATA-ONLY ... | [[platforms — constitution]] | Mirror-Registry System` — Data-only module for platform-name strings; deliberately separated from engine.
- [unknown] **ops module** `FILE MAP.md table row: `ops/` | the service command center — see + run the runtime (`company` console + `services.json`); first of more | [[ops — constitution]] | —` — Described as 'first of more' command center; no evidence of actual service state in this excerpt.
- [living] **Live registry section** `FILE MAP.md comment block <!--REGISTRY:START--> through truncated list` — Auto-maintained by Suite.refresh_self_description on every apply; contains 16 node-types, 9 RHM verbs, and a truncated modes list.
- [living] **RHM verbs list** `FILE MAP.md <!--REGISTRY:START--> bullet: '- **RHM verbs**: run, propose, build, consult, show, panel, extend, configure, load_voice, unload_voice, request_change'` — 11 verbs listed (9 core + load_voice/unload_voice/request_change); 'panel' and 'extend' suggest UI/self-mod capabilities.
- [unknown] **Modes list (truncated)** `FILE MAP.md <!--REGISTRY:START--> bullet: '- **modes**: listening, text-only, background, focus, walkthrough, watch-and-react, dec'` — Truncated mid-word ('dec'); cannot determine full mode set from material.
  - dormant-candidates: ui-contract/ module — described as 'building/planned, nothing live until the driving harness flips it' (FILE MAP.md table row `ui-contract/`) · ops/services.json and `company` console — referenced but no operational evidence shown (FILE MAP.md table row `ops/`)
  - surprises: The map claims it is auto-maintained by Suite.refresh_self_description and that drift-checks fail loud via tests/drift_acceptance.py, but the material is a static markdown excerpt with no evidence of the automation actually running. · ui-contract/ is explicitly admitted to be not live ('nothing live until the driving harness flips it') yet it appears in the module map as a normal entry, not flagged as dormant. · The modes list is truncated mid-word ('dec'), suggesting the registry block was captured incompletely or the generator was interrupted.

### HANDOFF.md
- [living] **HANDOFF.md metadata block** `FILE HANDOFF.md frontmatter` — Self-declares type: handoff, module: root, status: living, tags include company/handoff/session/voice/ops.
- [living] **Newer session handoff pointer** `FILE HANDOFF.md > blockquote: '⏭️ NEWER SESSION: HANDOFF-2026-06-07-model-layer-and-cognition.md'` — Explicitly supersedes this file; points to a newer handoff and a concurrent-cognition directory not included in this excerpt.
- [living] **Fresh-agent read order** `FILE HANDOFF.md > paragraph beginning 'Read order for a fresh agent:'` — Defines precedence: AGENTS.md (rules) → MAP.md (structure + live registry) → STATE.md (canonical status) → HANDOFF.md (narrative).
- [living] **Main branch + pushed claim** `FILE HANDOFF.md > blockquote: 'For the next session: everything below is on main and pushed (github.com/Concept-Vi/the-company)'` — Claims all described work is on main and pushed; no material evidence of remote state is shown.
- [living] **Commit e1063f7 — interactive-surface-build merge** `FILE HANDOFF.md > §1 commit table row 'e1063f7'` — 60-commit local-only branch merged to main; addressed surface, click-to-indicate, R2 context ranking, code-symbol/dependency/semantic edges, blast-radius, persisted vector index, decision→build wire.
- [living] **Commit d0be0fd — voice VRAM convergence** `FILE HANDOFF.md > §1 commit table row 'd0be0fd'` — Unified voice launch/budget/teardown under shared gpu.py authority.
- [living] **Commit 44101fb — doc-drift fixes** `FILE HANDOFF.md > §1 commit table row '44101fb'` — Updated rules/status docs and ops-session reply.
- [living] **Live standup runtime state** `FILE HANDOFF.md > §1 'Live standup (runtime state, not a commit)'` — Bridge restarted onto merged code; full audio→STT→brain→TTS→WAV circuit proven by use; RHM brain model fixed from 'nonexistent-model:cloud' to 'qwen3.5-9b-q8:latest' in shared state.
- [living] **Merge conflict files** `FILE HANDOFF.md > §2 paragraph beginning 'Only 2 files conflicted'` — Conflicts resolved toward derivation-based RHM_VERBS == tuple(RHM_VERB_SPECS); MAP.md auto-merged.
- [living] **Test suite results** `FILE HANDOFF.md > §2 paragraph beginning 'Merge correctness (proven, not assumed):'` — 96/100 pass; 4 are service-down loud-skips (environmental). walkthrough_acceptance.py 34/34 but >90s. canvas/app builds clean (1029 modules).
- [half-built] **L2 autonomous self-build wire default** `FILE HANDOFF.md > §2 sentence 'The L2 autonomous self-build wire is INERT by default'` — Defaults to 'plan'; self-modifies nothing unless acceptEdits is deliberately set — present but disabled.
- [dormant] **Merged but lingering git worktrees** `FILE HANDOFF.md > §2 'Branch hygiene:'` — Branches fully merged into main but still exist as worktrees; ~/company-overnight holds uncommitted work (superseded orpheus monkeypatch + duplicate voice ref clip).
- [dormant] **Dual voice launch mechanism bug** `FILE HANDOFF.md > §3 paragraph beginning 'The bug it fixed:'` — Old UI path used Popen with its own budget/teardown, leaving systemd unit inactive and causing invisible VRAM → OOM risk. Now removed/converged.
- [living] **voice/lifecycle.py load path** `FILE HANDOFF.md > §3 bullet 'load(sid) → systemd.control(svc,"start")'` — Uses systemd unit start, gated by shared gpu check_fit; fail-loud eviction planning.
- [living] **voice/lifecycle.py unload path** `FILE HANDOFF.md > §3 bullet 'unload(sid) → gpu.teardown(svc)'` — Cgroup stop reaps EngineCore; plain SIGTERM orphans it (~10 GB). References upstream issue #19849.
- [living] **voice/lifecycle.py vram/status path** `FILE HANDOFF.md > §3 bullet 'vram() → gpu.read_gpu(); status() uses systemd.is_active'` — Status distinguishes warming (unit active, model loading) from up (health answers).
- [living] **voice/lifecycle.py import path collision note** `FILE HANDOFF.md > §3 'Import note (matters if you touch lifecycle):'` — Does sys.path.insert(ops/cli) then imports gpu, systemd, registry; runtime.registry (NodeRegistry) namespaces collision.
- [living] **Voice unit env parity** `FILE HANDOFF.md > §3 'Env-parity holds for free:'` — Every voice unit uses EnvironmentFile=voice.env; no per-service load.env override.
- [living] **Voice stack table — viv/chatterbox** `FILE HANDOFF.md > §4 table row 'viv | chatterbox | 4124 | 3.8 GB'` — Clones from COMPANY_VOICE_REF; has emotion-exaggeration knob. Material truncates after this row.
  - dormant-candidates: L2 autonomous self-build wire — present but defaults to COMPANY_WIRE_PERMISSION=plan, so it is built but inert unless acceptEdits is set (HANDOFF.md §2). · Merged git worktrees (~/company-interactive, ~/company-night, ~/company-overnight) — branches are fully merged into main but worktrees remain; ~/company-overnight has uncommitted superseded orpheus monkeypatch + duplicate voice ref clip (HANDOFF.md §2 'Branch hygiene'). · Old voice/lifecycle.py subprocess.Popen launch path — replaced by systemd unit path; no longer used (HANDOFF.md §3).
  - surprises: RHM brain model was configured as 'nonexistent-model:cloud' — a literal broken placeholder — and had to be manually corrected to 'qwen3.5-9b-q8:latest' during the session. · The old voice UI path used subprocess.Popen with its own VRAM accounting, which could leave systemd units inactive and silently double-allocate GPU memory until OOM. · vLLM EngineCore can survive SIGTERM/SIGKILL and reparent to init, squatting ~10 GB, so teardown must use cgroup-based systemctl stop. · Three fully-merged branches still exist as worktrees on disk, and ~/company-overnight contains uncommitted work including a superseded orpheus monkeypatch and a duplicate voice reference clip.

### HANDOFF-2026-06-07-model-layer-and-cognition.md
- [living] **handoff doc** `HANDOFF-2026-06-07-model-layer-and-cognition.md` — Self-described as doc spine (census); explicitly declares STATE.md + tests as canonical and that this doc should be fixed if it disagrees.
- [living] **commit 9412e01 — Model/VRAM layer** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 TL;DR row `9412e01`` — Introduces 'config-block sizing as the one source' — a centralization claim that may be half-built if other sizing paths still exist.
- [living] **commit 5746211 — Persona identity hookup** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 TL;DR row `5746211`` — Brain prose reaching prompt is proven (persona=sable); the any-engine matrix is only code-complete, not exercised.
- [half-built] **commit 1b51437 — qwen3tts/cosyvoice sizing + co-residence shrink mechanism** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 TL;DR row `1b51437`` — Shrink mechanism functions exist but the actual shrink branch was not driven end-to-end; qwen3tts/cosyvoice config reading unverified.
- [living] **commit 796be31 — Co-residence DELIVERED** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 TL;DR row `796be31`` — Proven server-side for already-resident case; the dynamic shrink/switch path remains unverified.
- [living] **commit a89dab1 — click-to-indicate fix** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 TL;DR row `a89dab1`` — Browser-verified per doc; default-off mode means the feature is gated and may be dormant in normal use.
- [living] **commit 0829118 — handoff doc + Concurrent Cognition research landscape** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 TL;DR row `0829118`` — Research landscape only — Concurrent Cognition is explicitly unbuilt.
- [living] **commit 799a08a — Whisper-offline fix + UI start affordance** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 TL;DR row `799a08a`` — STT_PROVIDERS now carries a `service` field — a schema change that may have dormant consumers.
- [half-built] **commit e9ac048 — Detailed voice trace** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 TL;DR row `e9ac048`` — Server endpoint and records proven; browser client emitters compile but have never fired in a real session.
- [living] **live brain config** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 'Current live state'` — Explicit runtime state snapshot; may drift immediately after the handoff was written.
- [living] **live voice config** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 'Current live state'` — Co-resident with brain at 64K; headroom figure is a runtime measurement, not a guarantee.
- [living] **serving endpoint** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0 'Current live state'` — External network surface; may be transient depending on tailscale/node state.
- [living] **verification status section** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5` — Unusually honest self-audit; the yellow/red buckets are the most valuable signal in this file.
- [half-built] **any-persona × any-engine voice mapping** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 yellow bucket` — xtts/chatterbox will 'fail loud' without COMPANY_VOICE_REF; kokoro assigned but never synth-tested.
- [half-built] **qwen3tts/cosyvoice config-block reading** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 yellow bucket` — _reg_config() added but engines were not restarted to confirm they read the new config block correctly.
- [half-built] **co-residence shrink on real switch** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 yellow bucket` — No-op for current AWQ Orpheus because coresident_ctx == default; the shrinking branch is effectively untested.
- [half-built] **voice.client browser reports** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 yellow bucket` — Client emitters compile but have never fired in a real browser session.
- [half-built] **/api/model/config context-resize + restart under resident voice** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 yellow bucket` — Budget-gated refuse path is 'reasoned, only partially exercised'.
- [unknown] **on-device live voice conversation** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 red bucket` — Headline UX explicitly marked as NEVER verified end-to-end.
- [unknown] **auto-listen VAD→judge→fire loop** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 red bucket` — Reported issue is NOT resolved; new trace exists for investigation, not because it is fixed.
- [unknown] **4-bit Orpheus audio quality** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 red bucket` — Quality fallback is cached but incompatible with 64K co-residence — a tradeoff the system has not resolved.
- [unknown] **mobile form of new surfaces** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 red bucket` — Rendered once early but not re-verified after subsequent changes.
- [dormant] **Concurrent Cognition** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 red bucket and §0 row `0829118`` — Entirely unbuilt; only a research landscape exists.
- [living] **drift_acceptance 5/5** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 green bucket` — Mentioned as passing; no path/location for the test itself is given in this excerpt.
- [living] **e4_registry passes** `HANDOFF-2026-06-07-model-layer-and-cognition.md §0.5 green bucket` — Mentioned as passing; no path/location for the registry test is given in this excerpt.
  - dormant-candidates: Concurrent Cognition — build-prep/concurrent-cognition/ (research landscape only, entirely unbuilt) · any-persona × any-engine non-default engine paths — xtts/chatterbox blocked by missing COMPANY_VOICE_REF; kokoro assigned but never synth-tested · co-residence shrink branch — /api/voice/switch shrink path is a no-op for current AWQ Orpheus and untested · voice.client browser emitters — api.voiceLog calls compile but have never fired in a real browser session · ◎ point click-to-indicate mode — default off; dormant in normal use unless deliberately enabled · /api/model/config context-resize + restart under resident voice — partially exercised
  - surprises: The handoff itself contains an explicit 'if this disagrees with STATE.md, fix this' clause — making the doc self-deprecating and STATE.md the real canonical source. · A 4-bit AWQ Orpheus is co-resident with a 64K-context 4B brain at util 0.49/0.32 with ~2.4 GB headroom — a tight but claimed-working co-residence configuration. · The headline UX (on-device live voice conversation on iOS) is explicitly marked as NEVER verified, despite the session being described as 'delivered' and on main. · xtts/chatterbox personas are wired to a COMPANY_VOICE_REF that 'does not exist' — they will 'fail loud' until someone creates a reference clip. · The higher-quality Orpheus fallback (w8a8 int8, ~4.75 GB) is cached but explicitly cannot co-reside at 64K, creating a quality/residence tradeoff with no resolution yet. · Auto-listen (VAD→judge→fire) is reported broken ('listening doesn't seem to detect') and the new trace infrastructure was built to investigate it, not because it was fixed.

### CRITIC-VERDICT-integration-journey.md
- [living] **Integration-test report document** `FILE CRITIC-VERDICT-integration-journey.md` — A whole-operator-journey integration-test verdict for the web UI at http://127.0.0.1:5174/.
- [living] **Web UI under test** `http://127.0.0.1:5174/` — Tested on fresh phone (390x844x3) and desktop (1440x900x1) viewports.
- [living] **Decision-write API endpoint** `/api/territory/write` — Verified returning {"ok":true,"written":1,"source":"operator"}; count decremented after POST.
- [living] **Map projection endpoint** `/api/projection?limit=600` — Header '600' is the limit/count of things on the map; presented raw without label.
- [half-built] **Guide (V) spotlight / dim-to-focus** `CRITIC-VERDICT-integration-journey.md section 5` — Global dim verified, but per-control highlight when guide names individual controls (lens, layer, circle/square, time scrubber) was NOT observed after ~6s polling.
- [living] **Decision option copy** `CRITIC-VERDICT-integration-journey.md FLAG A` — Contains internal jargon: 'RHM', 'with-derivation frame' visible to operators.
- [living] **Guide free-text answer about decisions** `CRITIC-VERDICT-integration-journey.md FLAG B / section 5` — Displayed raw item codes: (s117), (s115), (s100), (s60-review), (s118).
- [living] **Two 'what needs me' surfaces** `CRITIC-VERDICT-integration-journey.md FLAG C` — Pill list and guide answer return completely different, zero-overlap decision sets.
- [living] **Header '600' raw number** `CRITIC-VERDICT-integration-journey.md FLAG D` — Unlabelled count of map items; reads as mystery number to strangers.
- [living] **Decision substance** `CRITIC-VERDICT-integration-journey.md FLAG E` — Underlying questions are abstract/architectural despite surface plain-language framing.
- [dormant] **Save-error aria-live string** `CRITIC-VERDICT-integration-journey.md NON-ISSUE` — '! Couldn't save — try again' exists in an aria-live container but was not observed on screen; likely stale/queued live-region text.
- [unknown] **'Ask about this' button inside each decision** `CRITIC-VERDICT-integration-journey.md UNTESTED` — Not exercised in this test; assumed alternate entry to the same guide.
  - dormant-candidates: Per-control spotlight/highlight for guide tour — built once (implied by 'bonus' description) but not observed firing when guide names controls. · Aria-live save-error message — present in DOM but not observed on screen after verified successful writes; likely built for failure path but left live during success.
  - surprises: The guide's 'spotlight' bonus feature — per-control highlight as it names controls — appears absent or uncatchable even though the base global dim works. · Two surfaces that both answer 'what decisions are waiting for me?' return completely different, zero-overlap sets of items; this is a content-divergence bug, not latency. · A save-success path still leaves an '! Couldn't save — try again' string sitting in an aria-live container, creating a potential false-alarm accessibility announcement.

### CLAUDE.md
- [living] **CLAUDE.md — top-level orientation doc** `FILE CLAUDE.md` — Self-describes as the entry-point for Claude Code sessions; explicitly states there are no human developers.
- [unknown] **AGENTS.md — constitution / source of truth** `FILE CLAUDE.md → `AGENTS.md`` — Named as the first file to read and the source of rules + 'where does this go?' table + self-description discipline; not present in material.
- [unknown] **MAP.md — structure + live registry** `FILE CLAUDE.md → `MAP.md`` — Named as second read; described as 'structure + live registry'.
- [unknown] **STATE.md — current status / run + verify** `FILE CLAUDE.md → `STATE.md`` — Named as third read; described as current status / how to run + verify.
- [unknown] **HANDOFF.md — latest session narrative + live-surface/voice/ops how-to** `FILE CLAUDE.md → `HANDOFF.md`` — Named as carrying latest session narrative + live-surface/voice/ops how-to.
- [unknown] **docs/vault-conventions.md — markdown vault schema rules** `FILE CLAUDE.md → `docs/vault-conventions.md`` — Described as canonical rules for the Obsidian-vault-style self-description layer; strict frontmatter + link conventions.
- [unknown] **orienteering/INDEX.md — terrain ledger** `FILE CLAUDE.md → `orienteering/INDEX.md`` — Described as the map of everything outside ~/company: model/voice engines, session-recall index, TLS certs, ~20 company-* systemd services, scattered work/data.
- [unknown] **orienteering/AGENTS.md — ledger schema constitution** `FILE CLAUDE.md → `orienteering/AGENTS.md`` — Named alongside docs/vault-conventions.md for ledger schema; described as map, not blueprint.
- [unknown] **Working docs directories** `FILE CLAUDE.md → `build-prep/`, `channel-memory/`, `foundation/exchanges/`` — Mentioned as keeping their own frontmatter, separate from the strict self-description layer.
- [unknown] **External Company locations** `FILE CLAUDE.md → model/voice engines, session-recall index `~/.cache/company`, TLS certs, ~20 `company-*` systemd services, scattered work/data` — Explicitly stated to live outside ~/company and wired in by systemd; must be checked in orienteering entries before acting.
  - surprises: The repo claims to have zero human developers and to be built entirely by AI agents — an unusual governance model, stated as fact in the orientation doc. · The same markdown files are simultaneously code instructions and an Obsidian vault self-model, with generated index + greppable links as the knowledge face. · There is a declared ~20 systemd services and external scattered state that lives outside the repo, mapped only via orienteering/INDEX.md.

### AGENTS.md
- [living] **AGENTS.md constitution file** `FILE AGENTS.md` — Self-describes as the root constitution/orientation doc for AI agents; explicitly prescriptive register, not descriptive.
- [living] **Orientation order rule** `AGENTS.md section '# AGENTS.md — read this first'` — Mandates a 4-doc read sequence before acting; HANDOFF.md is only for live/voice/ops work.
- [living] **Vault source-of-truth path** `AGENTS.md section '## Source of truth'` — Specs live outside the repo under `/mnt/c`, which conflicts with the later rule 'Storage on ext4 (`~/...`), never under `/mnt/c`' — specs are documents, not DBs, but the tension is notable.
- [living] **Rule 9 (FORM / design-critic / review gate)** `AGENTS.md section '## The rules (non-negotiable)' item 9` — Extremely detailed rule about a review wire that is supposed to exist; the material is cut off mid-sentence ('ask the RHM (`prop') at the end, suggesting the doc itself may be half-built or truncated.
- [living] **Rule 10 (commit to main, no feature branches)** `AGENTS.md section '## The rules (non-negotiable)' item 10` — Explicitly overrides inherited 'branch off main' build-skill convention because there are no human merge orchestrators.
- [living] **Node-type addition path** `AGENTS.md table row 'a new node-type'` — Claims nodes self-register via auto-discovery; requires VOLATILE flag for mutable-truth readers.
- [living] **Model/provider addition path** `AGENTS.md table row 'a new model / provider'` — Single-source registry for models/providers.
- [living] **Storage backend addition path** `AGENTS.md table row 'a new storage backend'` — References contract C4 for the Resolver Protocol.
- [living] **RHM action verb addition path** `AGENTS.md table row 'a new RHM action verb'` — Explicitly says old text parser `_parse_rhm_action` is retired; RHM now uses native tool-calling. This is a strong claim about current implementation state.
- [living] **Presence mode addition path** `AGENTS.md table row 'a new presence mode'` — Modes are themselves nodes.
- [half-built] **Settings/control panel addition path** `AGENTS.md table row 'a **settings/control panel** (declarative)'` — The entry and the entire document are truncated mid-word ('ask the RHM (`prop'); the rest of the table and any following sections are missing.
  - dormant-candidates: Settings/control panel declarative path — table row is cut off at 'ask the RHM (`prop`' in AGENTS.md; appears half-built or truncated. · Rule 9's review wire (`decision.surfaced_for_review` event, review inbox item, design-lint) — described prescriptively but not evidenced in this material; may be specified but not yet implemented.
  - surprises: The constitution explicitly forbids storage under `/mnt/c` for DBs due to WSL fsync corruption, yet the vault source-of-truth path is itself under `/mnt/c` — a tension between 'specs are documents' and the absolute wording of the storage rule. · Rule 9 is unusually elaborate about a design-critic agent, design-lint, review inbox, and a `decision.surfaced_for_review` event — suggesting a formal review pipeline is intended, but the material does not show whether it actually exists. · The document is truncated at the end of the settings/control-panel table row, cutting off mid-token '`prop`'. This is a constitution-level doc ending abruptly.
