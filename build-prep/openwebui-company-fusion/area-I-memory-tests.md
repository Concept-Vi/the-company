---
type: map
area: recollection + operator_memory + channel-memory + tests + migration-pending
register: descriptive
coverage:
  files_read: 47
  files_total: 12329
  last_read: "2026-06-28"
status: confirmed
aliases: ["area-I-memory-tests", "memory-tests-systems"]
---

# Area I Map: Memory, Knowledge, Tests, Migration

## Subsystems at a Glance

1. **Recollection** — Episodic memory: semantic search across sessions (conversations, decisions, patterns)
2. **Operator Memory** — Tim-machine file-discovered registry (rules, preferences, confirmed patterns with evidence)
3. **Channel Memory** — Cross-session fabric vault (shared planning, design, recall, noticeboard)
4. **Tests** — 232 acceptance suites proving each capability (convergence record; "done" = green suite)
5. **Migration Pending** — Home-directory consolidation: evidence-grounded inventory of company-native vs. separate

---

## 1. RECOLLECTION (Episodic Memory System)

**Location:** `/home/tim/company/recollection/` (source) + `/home/tim/company/.recollection/` (data)
**File counts:** 10,430 data files; 544 source files (src/ + cli/ + test/)
**What it is:** Semantic search index over past Claude Code & Codex conversations; extracts exchanges, embeds with Transformers.js, stores in SQLite+sqlite-vec.

### Data Structure

- **Archive:** `~/.recollection/conversation-archive/` (1.0G)
  - Organized by harness (`-home-tim`, `project-a`) → session UUID → subagents
  - Format: JSONL conversation files; one row = one user/assistant exchange pair
  - Metadata: parentUuid, isSidechain, gitBranch, claudeVersion, modelProvider, thinkingLevel, toolCalls

- **Index:** `~/.recollection/conversation-index/db.sqlite` (209M)
  - Schema: `exchanges` table (vector embeddings + metadata)
  - Support tables: `metadata`, migration tracking (`embedding_version`)
  - Supports: semantic search (vector similarity), exact text search, multi-concept AND queries

- **Logs:** `~/.recollection/logs/` (376K)
  - Sync operations, indexing progress, errors

- **Self:** `~/.recollection/self/` (272K)
  - 272+ JSON files; structured introspection/state (metadata about indexed conversations)

### System Components (Source)

**Core Logic** (`src/`):
- `db.ts` — Schema + migrations (incl. embedding_version column for pipeline tracking)
- `embeddings.ts` — Transformers.js encoder pipeline; exchange + query embedding
- `embedding-migration.ts` — Version constant + lock file for re-embedding on pipeline changes
- `search.ts` — Vector + text search; multi-concept aggregation (AND logic for multiple keywords)
- `indexer.ts` — Incremental index from archive to vec_exchanges (file-lock protected)
- `sync.ts` / `sync-cli.ts` — Archive copy + indexing; reentrancy guard (EPISODIC_MEMORY_SUMMARIZER_GUARD=1)
- `parser.ts` — JSONL transcript → exchange extraction
- `summarizer.ts` — Claude Agent SDK calls (with recursion guard for hook reentrancy)
- `types.ts` — Schemas: ConversationExchange, ToolCall, SearchResult

**CLI Wrappers** (`cli/`):
- `episodic-memory.js` — Umbrella dispatcher
- `search-cli.ts`, `index-cli.ts`, `sync-cli.ts` — Subcommand entry points
- `mcp-server-wrapper.js` — Ensures deps installed before MCP boot

**MCP Server** (`src/mcp-server.ts`):
- Tools: `search` (semantic + text, single or multi-concept), `read` (display full conversation)
- Exposed via plugin to Claude Code/Codex

**Infrastructure:**
- `file-lock.ts` — Cross-process lock for concurrent-safe sync
- `paths.ts` — Config dir resolution (EPISODIC_MEMORY_CONFIG_DIR, default ~/.config/superpowers/)
- `logging.ts` — Background sync log writing
- `constants.ts` — Defaults, embedding model info

**Capture Sources** (4 harnesses):
- `claude` — Claude Code conversations
- `codex` — Codex conversations
- `board` — Company Noticeboard captures (recall<->board wire)
- `clone` — Clone-fleet reflections (era-clone captures)

### Load-Bearing Invariants

1. **Reentrancy guard** (file `sync-cli.ts:shouldSkipReentrantSync()`)
   - SessionStart hook → sync --background → summarizer (Claude subprocess)
   - Subprocess's SessionStart would loop without guard
   - Fix: `getApiEnv()` always sets `EPISODIC_MEMORY_SUMMARIZER_GUARD=1`

2. **Embedding versioning** (file `embedding-migration.ts`)
   - `EMBEDDING_VERSION` column tracks which encoder produced each vector
   - Pipeline change (model, dtype, prefix, normalization) → bump version → auto-reembed on upgrade
   - Lock file: `~/.config/superpowers/conversation-index/.embedding-migration.lock`

3. **Test isolation** (test utils)
   - `mkdtempSync`, per-test DB/projects/config paths
   - Never reach for real ~/.config/superpowers/ during tests

**Conversational harnesses indexed:**
- Sessions: user projects (project-a, -home-tim) + cross-session work
- Exchanges: one row = one user Q + assistant A (pair), with line ranges in archive
- Metadata: sessionId, gitBranch, model/version, thinking metadata

---

## 2. OPERATOR_MEMORY (Tim-Machine Registry)

**Location:** `/home/tim/company/operator_memory/`
**File counts:** 60 files (32 .py rules + 1 AGENTS.md + 1 AGENTS.md manifest)
**What it is:** File-discovered registry (GC15); grows via propose→confirm lifecycle; records standing knowledge about working with Tim.

### Structure

**Rules** (as Python files, discovered/loaded):
- `refine_before_gating.py` — Refinement passes run autonomously; gate gets minimum set
- `think_back_with_me.py` — Thinking aloud = co-think, not act/summarize
- `easy_decision_surface.py` — Decision surface never isolated technical doc
- `no_unconditional_deferrals.py` — Deferrals only with explicit return-condition
- `multi_job_elements.py` — Context decides; record contextual faces, don't flatten conflicts
- `proposal_lifecycle.py` — Propose → his accept → build → registry flips Real
- `never_reads_the_files.py` — He never reads files; everything at his altitude
- `leverage_the_fleet.py` — Use cross-session agents
- `investigate_before_coding.py` — Understand before building
- `expand_dont_echo.py` — Add new insight, don't repeat
- `ai_supplies_domain_knowledge.py` — AI provides technical context
- `goal_function_mandates.py` — Goals are binding
- `big_beats.py` — Major patterns/milestones
- `flag_hardcoding.py` — Surface hard-coded values
- `no_deferral.py` — No unconditional deferrals
- `no_versioning.py` — Don't version-control Tim's mem (it's live)
- `make_each_thing_work.py` — Proof before moving on
- `verify_before_claiming.py` — Verify before asserting done
- `verify_by_use.py` — Test in real use, not just tests
- ... and 12 more

**Constitution:**
- `AGENTS.md` — module-note; prescriptive; defines lifecycle, loader, face (mcp_face/tools/operator.py), rules

### Data Format

Each rule = one .py file:
- Plain text (no JSON/YAML)
- Metadata: status (proposed/confirmed), scope.when (activity it matters during), scope.where (ui:// prefix)
- EVIDENCE REQUIRED: verbatim words from Tim; rows without evidence = fabrication (fail-loud)

### Lifecycle

1. Transcript mining PROPOSES rows when patterns recur (status='proposed')
2. TIM'S CONFIRMATION makes standing (status='confirmed')
3. Same circuit as everything else: propose → confirm → build real

### Face/Loader

- **Loader:** `runtime/operator_memory.py`
- **Face:** `mcp_face/tools/operator.py` (verbs: op=rules | describe | proposed)
- **Contract:** pure data; nothing executes

---

## 3. CHANNEL-MEMORY (Cross-Session Fabric Vault)

**Location:** `/home/tim/company/channel-memory/`
**File counts:** 1,535 files (markdown, images, JSON scans, attachments, design docs)
**What it is:** Communal shared-memory working space for cross-session fabric (lead + forks + members); established by lead at Tim's direction; every member writes under COMMIT-GRAMMAR.

### Layout (11 subsystems)

1. **`vision/`** — Tim's intents, decompressed (source-of-truth entries)
2. **`schema/`** — session-store / source schemas (the fork's lane)
3. **`scans/`** — scan output as DATA (rows.ndjson + summary.json), projectable
4. **`map/`** — lineage, distance maps, ranked clone-map (launched-fleet.json, fork-points.md)
5. **`recall/`** — recall decisions, embedding/recall fix records
6. **`design/`** — design inputs (lead's A-D lane-inputs; patches for territory, address, etc.)
7. **`mega-prep/`** — SHARED MEGA-PREP: unified spec, cross-reviews, welded plan (CHANNEL-LAYER-SEAM.md, APPROVAL-STANDARD.md)
8. **`noticeboard/`** — 28K+ files; issue postings, decisions, live working surface
9. **`channel_attachments/`** — 28K+ files; media for channel fabric
10. **`images/`** — 28K+ files; design/asset images
11. **`plan/`** — planning documents, coordination records

### Protocols

**One unified spec first** — the unified seam/spec (mega-prep/) is prerequisite; everyone builds to ONE spec. INNER (session-recall) nests in OUTER (recollection).

**Provenance discipline (load-bearing):**
- `trust: tim-direct(session)` — direct from Tim in that session (proposal to consumers until confirmed)
- `trust: channel-relayed` — relayed through channel from another session
- `trust: fabric-derived` — emerged from fabric; not Tim-direct

**Cross-work:** All sessions read + assess each other's work; use reviews + integration ("welding").

**Each session = team-leader** — runs staggered timed loop; checks channel + agent state for alignment before/while building.

### Key Files

- `COMMIT-GRAMMAR.md` — Rules every member follows (provenance, shared-edit protocol)
- `TIM-INTERFACE-SYNTHESIS-2026-06-16.md` — Session fabric definition, interface contracts
- `CODES_OF_CONDUCT.md` — Channel discipline standards
- `mega-prep/HELD-self-approval.md` — Standing line on self-approval via recorded intent (pending Tim's DIRECT confirmation)

---

## 4. TESTS (232 Acceptance Suites)

**Location:** `/home/tim/company/tests/`
**File counts:** 240 files (232 acceptance suites + config/init)
**What it is:** Convergence record; each suite proves one capability by execution; "done" = green suite (not assertion, not docs).

### Test Coverage (by subsystem)

**Engine & Fabric** (core execution):
- `e1_acceptance.py`, `e2_runtime.py`, `e3_fabric.py`, `e4_registry.py`, `e5_suite.py`, `e6_governance.py` — Staged bootstrap + registry discovery + fabric
- `agent_sessions_channels_acceptance.py` — Cross-session fabric organs (mailbox, channels, registry)
- `agent_sessions_exporter_acceptance.py`, `agent_sessions_mailbox_acceptance.py` — Fabric leaf + MCP verbs
- `agent_sessions_registry_acceptance.py` — Session registry contracts

**Nodes & Operations** (graph structure):
- `direct_create_acceptance.py` — Graph nodes creation
- `edge_kinds_acceptance.py` — Edge semantics
- `event_address_acceptance.py` — Event addressing (ui://)
- `address_grammar_acceptance.py` — Canonical grammar for ui://
- `address_scope_acceptance.py` — Backend resolution (ui:// → code:// → scope[])
- `address_help_surface_acceptance.py` — Composed address-help surface

**Convergence & Consent**:
- `conv_consent_acceptance.py` — Trust property at resolution time
- `conv_dedup_acceptance.py` — Deduplication during composition
- `conv_freshstart_acceptance.py` — Fresh start semantics
- `conv_index_acceptance.py` — Index semantics + staleness
- `conv_reach_acceptance.py` — Reachability contracts
- `conv_semantic_rank_acceptance.py` — Semantic ranking during convergence

**Interactive Surface**:
- `act_endpoint_acceptance.py` — /api/act emission seam (click → dispatch → result, no prose-parse)
- `showme_backend_acceptance.py` — Show-me backend (C2 display logic)
- `showme_c2_acceptance.py` — C2 interactive surface contract
- `showme_guided_acceptance.py` — Guided review surface
- `address_scope_acceptance.py` — Backend address resolution

**Self-Modification & Governance**:
- `selfmod_acceptance.py`, `selfmod_audit_acceptance.py` — Self-mod gates + audit
- `governance_acceptance.py` — Governance contracts (build gate, revertibility)
- `roles_acceptance.py` — Role-based access + actions
- `render_declaration_acceptance.py` — Self-description rendering

**Voice & Audio**:
- `voice_circuit_acceptance.py` — Voice loop
- `voice_parts_acceptance.py` — Voice message structure
- `stt_models_acceptance.py`, `stt_whispercpp_acceptance.py` — STT providers

**Session Fabric**:
- `session_supervisor_acceptance.py`, `session_supervisor_params_acceptance.py` — Supervisor protocol
- `session_address_grammar_acceptance.py` — Session-addressing grammar
- `session_pointintime_acceptance.py` — Point-in-time session access
- `session_search_acceptance.py` — Session search contracts

**Cognition & Intelligence**:
- `cognition_info_acceptance.py`, `cognition_info_registries_acceptance.py` — Cognition input/registries
- `cognition_governance_acceptance.py` — Cognition governance (constraints, approval gates)
- `cognition_resolution_loop_acceptance.py` — Resolution loop contracts
- `activation_caller_acceptance.py`, `activation_drivers_acceptance.py`, `activation_contexts_acceptance.py` — Concurrent Cognition (always-on caller, drivers, contexts)
- `authoring_acceptance.py` — Authoring backend (C7.4/C7.5)

**Capabilities & Flows**:
- `cascade_acceptance.py` — Cascade execution (parallel fan-out)
- `reduce_acceptance.py` — Reduce (aggregation)
- `run_items_acceptance.py` — Run-item semantics
- `run_discovery_acceptance.py` — Run discovery
- `run_index_incremental_acceptance.py` — Incremental run index

**Marks & Registry**:
- `marks_acceptance.py` — Mark types + registry
- `registry_authoring_marks_acceptance.py` — Registry authoring with marks
- `mark_types_acceptance.py` — Mark type contracts

**Decision & Capture**:
- `decisions_acceptance.py` — Decision capture + lineage
- `decision_lineage_acceptance.py` — Lineage contracts
- `capture_one_source_acceptance.py` — Capture-embed one source (final lane)

**Wiring & Composition**:
- `wire_acceptance.py`, `wire_adversarial.py` — Wire protocol
- `wire_async_dispatch_acceptance.py` — Async dispatch contracts
- `wire_commit_acceptance.py` — Commit-queue semantics
- `wire_harden_acceptance.py` — Hardening (idempotency, ordering)
- `wire_loop_acceptance.py`, `wire_trigger_acceptance.py` — Loop + trigger contracts
- `suite3_wiring_acceptance.py` — Full wiring suite

**Modes & Type System**:
- `modes_acceptance.py` — Mode system
- `modes_typeregistry_acceptance.py` — Mode + type registry interaction
- `model_capabilities_acceptance.py` — Model capability contracts
- `model_catalog_acceptance.py` — Model catalog registry
- `richer_types_acceptance.py` — Rich type representations

**Memory & State**:
- `memo_stale_acceptance.py` — Memo staleness contracts
- `state_types_acceptance.py` — State type contracts
- `node_states_render_acceptance.py` — State rendering

**Projection & Visualization**:
- `projection_instrument_acceptance.py` — Projection instrumentation
- `projection_multilayer_acceptance.py` — Multi-layer projection
- `projection_scale_acceptance.py` — Scale + view contracts
- `projection_semantic_acceptance.py` — Semantic projection
- `projections_acceptance.py` — General projection contracts

**Transport & Communication**:
- `transport_rep_penalty_acceptance.py` — Transport representation penalties
- `json_schema_transport_acceptance.py` — JSON Schema transport

**Other Capabilities**:
- `cc_channels_acceptance.py` — Company Channels fabric
- `cc_clone_acceptance.py`, `cc_clone_reflection_persist_acceptance.py` — Clone semantics + persistence
- `cc_gate_acceptance.py`, `cc_gate_bar1_verification.py` — Gate + step-address contracts
- `cc_attachments_acceptance.py`, `cc_board_acceptance.py`, `cc_board_reverse_acceptance.py` — Attachments + board
- `commitment_queue_acceptance.py` — Concurrent append/commit queue
- `guides_acceptance.py`, `guide_author_acceptance.py` — Guide creation + authoring
- `page_face_acceptance.py` — Page UI contract
- `skills_contexts_acceptance.py` — Skills context registry
- `ui_registry_acceptance.py` — UI registry contracts
- ... 50+ more covering RHM, composition, embedding, consent, layout, rules, schema transport

### Assertion

Every test is a runnable proof: `for t in tests/*.py; do ./.venv/bin/python "$t"; done`
- Test passes = capability is proven and live
- Test fails = regression detected; fix required before claiming "done"
- No green suite = capability is not real (no assert-without-proof)

---

## 5. MIGRATION-PENDING (Home-Directory Consolidation)

**Location:** `/home/tim/company/migration-pending/`
**File counts:** 64 files (inventory, action plans, evidence)
**What it is:** Evidence-grounded landscape catalogue of company-native vs. separate; outcome of home-directory sweep (identifies what lives where + constraints for moving).

### High-Level Structure

The company is **deliberately distributed**: source/authored work lives in folders; running substrate (venvs, services, certs) lives in dotdirs and systemd. "Consolidation" = two distinct jobs:

1. **RELOCATABLE** (authored work + data)
   - Can physically move into ~/company with reference fixes
   - 9 original folders (foundation, corpora, recollection, mcp-mining, company-scan, wizard-run-1, ui-contract, runtime, company-cognition)
   - Plus: `.vi`, `repos/counterpart`, handoff docs, recall index, certs

2. **WIRED SUBSTRATE** (running services)
   - "Move" = rewire ~20 systemd unit ExecStart paths + configs
   - vLLM, Jina embedding, voice venvs, CosyVoice, OpenWebUI, CI runners
   - Careless relocation stops the company mid-run

### Company-Native (Relocatable)

**The original 9:**
- **foundation** — persistent memory: founding conversations + doctrine (system/principles.md has 1 live binding at nodes/model_of_tim.py:16)
- **corpora** — shared source corpus: 811 .md docs + 1,051 session transcripts (index at ~/.cache/company; env-var fix + forced reindex needed)
- **recollection** — episodic-memory v1.4.2 refit (own git, 1.1G node_modules; .recollection data = 1.2G; 8218 DB rows with absolute paths → SQL rewrite)
- **mcp-mining** — completed overnight mining run → Obsidian vault (no live refs; prototype)
- **company-scan** — 2-pass scan of Windows project tree (no live refs; island)
- **wizard-run-1** — Project→Product pipeline prototype (no live refs; island)
- **ui-contract** — dead snapshot of ~/company/ui-contract (MD5 matches commit b239f48; zero unique)
- **runtime** — dead snapshot of ~/company/runtime/session_supervisor.py (MD5 matches commit 5e94bfb; pure ancestor)
- **company-cognition** — husk of concurrent-cognition worktree (empty; build is on main)

**Other company-native:**
- **`.vi`** (224K, 31 files) — Project Vi shared context; auto-loaded into every Claude session; **live, load-bearing** (relocation = update ~/.claude/CLAUDE.md pointer)
- **`repos/counterpart`** (920M) — design/spec workspace for operator surface (only thing in ~/repos linking to ~/company; 4 source refs)
- **`.company`** (44K, 0 files) — empty store skeleton (inert; safe to delete)
- **`channel-test`** (8K) — `.mcp.json` launch config for company fabric (abandoned scratch)
- **Handoff docs** — company-bridge.md, MERGE-COORD-cognition.md, ui-handoff.md, etc. (historical build record; relocate as archive)
- **`artefacts`** (108K) — Vi.md vision narrative + model survey (borderline with Vi corpus)

### Company Live-State (Rewire Required)

| What | Where | Evidence | Notes |
|---|---|---|---|
| Session-recall substrate | ~/.cache/company/substrate-claude-sessions/ (1.6G) | vault points here | Move + edit config.json paths |
| Service orchestration | ~/.config/systemd/user/company-* | ~20 units | Rewire ExecStart paths |
| TLS cert + key | ~/.config/company/certs/ | Tailscale cert | Update server config |

### Separate Projects (NOT Company)

**Project Vi:**
- vi-gateway, vi-chat, vi-openwebui, vi-visual-bridge (active to 2026-06-22), vi-voice-agent, etc.
- Zero `/home/tim/company` code refs
- Boundary case: vi-visual-bridge re-pointed at company-channel on 2026-06-22 (separate app tasked toward company goals)

**Other remotes:**
- obsidian-overlord (substrate-mcp; shared infra the company *uses*, but own repo)
- project-vi (8.9G), graph-editor, Supabase, langflow, 27 repos total in ~/repos/
- vaults/ (Obsidian Builder, vi-vault-design)

### Decisions Pending (Tim's Call)

1. **Substrate: move or own-in-place?** 48G+ model/voice venvs run via systemd. Move all or just own the definitions + recall + certs inside?
2. **Project Vi boundary.** Separate organs that *connect* to company, or consolidate too?
3. **Relocatable set homes.** Confirm naming (~/company/<name>) + gitignore data dirs; then action the moves + reference rewires.
4. **Dead/empty.** Delete or archive ui-contract, runtime, company-cognition, .company, .build, tophone empties?

### Evidence Method

- Fully read: 9 folders, `.vi` top-level, handoff docs, systemd units, recall config.json
- Identified by identity files + reference-grep (not exhaustive): repos/* (27 repos), vaults/, vi-*, venvs/caches, recollection node_modules, corpora (5/1863 read)
- Reference determination: per folder, read README/package.json/git-remote/config + grep `/home/tim/company`, `company-channel`, company ports/CLI
- Stated coverage per item (files read / files exist)

---

## Notable / Surprising

1. **The company runs distributed by design.** Not "scattered"; deliberately wired by systemd. The substrate (venvs, services) and the source/data are orthogonal moving targets. Consolidation is a genuine architecture decision, not a tidying task.

2. **Episodic memory has a recursion guard.** Hook → sync --background → summarizer (subprocess) → hook again → spiral. The guard (EPISODIC_MEMORY_SUMMARIZER_GUARD=1) is embedded in every subprocess spawn; subtle, load-bearing, tested.

3. **Operator memory has no execution.** Rules are data (Python files discovered at load-time); the only gate is Tim's confirmation. Auto-confirm = fabrication (fail-loud).

4. **Channel memory is *not* one session's notes.** It's the fabric's communal vault; provenance is tracked (tim-direct vs. relayed vs. fabric-derived); that distinction gates approval (pending vs. standing).

5. **Tests are the convergence record.** A capability is not "real" until its suite is green. The company's claim "we have X" traces back here. 232 suites; 111 explicitly name what they prove (accepts, proves, guarantee); the rest are proven by execution.

6. **Migration is evidence-grounded, not inferred.** Every item: read or reference-grep, with method noted. "No link" ≠ "I didn't look everywhere"; stated coverage per folder. The register is Tim's workspace for deciding (not a directive).

7. **Corpora data is live and large.** 1,863 files, 811 .md docs + 1,051 transcripts; index in ~/.cache/company; env-var split-brain that needs repair (writer ignores EPISODIC_MEMORY_CONFIG_DIR).

8. **Recollection data is absolute-path-heavy.** 8,218 DB rows with hardcoded paths → SQL rewrite on relocation; embedding-version tracking (pipeline changes trigger auto-reembed on upgrade).

9. **The recall index is 1.6G (Chroma + Substrate).** Separate from episodic-memory's local SQLite (209M); part of company live-state, wired by config.json.

10. **Project Vi is integrated-but-separate.** vi-visual-bridge is actively being aimed at company front-end (2026-06-22); the rest (vi-gateway, vi-chat) are deployed apps with their own deployments. Not "company folders scattered"—separate projects wired via fabric.

---

## Acceptance Tests: What They Guard (Sampling)

**Fabric & Sessions:**
- `agent_sessions_channels_acceptance.py` — Cross-session channels don't lose state
- `agent_sessions_registry_acceptance.py` — Session registry lookups never lie
- `session_supervisor_acceptance.py` — Supervisor protocol doesn't deadlock or skip steps
- `session_pointintime_acceptance.py` — Point-in-time access retrieves what was there, not forward refs

**Self-Modification:**
- `selfmod_audit_acceptance.py` — Self-mod changes are always auditable + revertible
- `governance_acceptance.py` — Build gate never auto-approves; revertibility is enforced

**Decision & Consent:**
- `conv_consent_acceptance.py` — Operator consent resolves → decision is bound + never reversed without trace
- `decisions_acceptance.py` — Decision lineage is complete (who decided, when, on what evidence)

**Interactive Seam:**
- `act_endpoint_acceptance.py` — /api/act click → dispatch → result, **no prose-parse, no model**; 7-verb whitelist strictly enforced
- `showme_c2_acceptance.py` — C2 surface renders correctly for all node types

**Concurrent Cognition:**
- `activation_caller_acceptance.py` — Always-on caller never races; one outcome per step
- `authoring_acceptance.py` — Authoring backend (C7) doesn't corrupt graph during parallel edits

**Memory:**
- `memo_stale_acceptance.py` — Memos know when they're stale (timestamp, version)
- `addr_history_acceptance.py` — Addressed history retrieves audit trail in order, never loses entries

**Convergence:**
- `conv_reach_acceptance.py` — What's reachable is guaranteed to converge
- `conv_semantic_rank_acceptance.py` — Ranking is stable (same query, same order)

**Type & Transport:**
- `json_schema_transport_acceptance.py` — JSON schema round-trip doesn't lose type info
- `transport_rep_penalty_acceptance.py` — Transport penalties don't invert signal (worse = worse)

---

## Cited Files

Key configuration/schema files:
- `/home/tim/company/recollection/src/db.ts` (schema)
- `/home/tim/company/recollection/src/embedding-migration.ts` (EMBEDDING_VERSION constant, lock mechanism)
- `/home/tim/company/recollection/src/sync-cli.ts` (reentrancy guard shouldSkipReentrantSync)
- `/home/tim/company/operator_memory/AGENTS.md` (constitution: file-discovered registry, propose→confirm)
- `/home/tim/company/channel-memory/COMMIT-GRAMMAR.md` (provenance rules)
- `/home/tim/company/channel-memory/mega-prep/HELD-self-approval.md` (approval standard)
- `/home/tim/company/migration-pending/MIGRATION-REGISTER.md` (evidence-grounded inventory)
- `/home/tim/company/tests/AGENTS.md` (test constitution)
- `/home/tim/company/.recollection/conversation-archive/` (JSONL by harness/session/subagent)
- `/home/tim/company/.recollection/conversation-index/db.sqlite` (vector index)

