# Read 4 — Conversation Intelligence (the dormant Supabase project)

**Source repo:** `/home/tim/repos/Supabase/` (project ref `gctunhsuwpaxeatwlmuv`, domain api.vspokes.com)
**Lens:** harvest UNIQUE DESIGNS from Tim's never-shipped "conversation intelligence" Supabase build — structured understanding extracted from Claude Code conversation transcripts. This is the SAME conversation store that is the merge's primary source.
**Evidence convention:** **Observed** = read directly in code/SQL/docs. **Inferred** = pattern-matched, NOT verified by execution. I ran no SQL against the live project; all "live" counts are quoted from the repo's own audit docs and labelled accordingly.

---

## 0. The framing correction (read this first)

The task brief said "built it, never used it." The repo tells a more nuanced story, and the distinction matters for harvesting.

- **Observed** (`docs/conversation-intelligence-current-state-analysis.md`, 2026-02-10): the EXTRACTION half was run and populated — 223 conversations, 37,853 messages, 7,701 tool calls, 1,636 artifacts. But the INTELLIGENCE half was dormant: `title`/`summary`/`topics` all NULL, `ci_entities` empty, `ci_embeddings` had 0 rows. So at that date it was "data structure full, meaning layer empty."
- **Observed** (`docs/CI_IMPLEMENTATION_FRONTIER.md`, 2026-02-12, two days later): the system grew substantially — **1,205 conversations, 257,192 messages, 43,632 tool calls, 3,749 artifacts, 9,833 provenance records, 24,847 turn-context embeddings, 333 conversation embeddings**, and 6 parametric MCP tools reported WORKING incl. active semantic search.
- **Observed:** the CI/Supabase repo's own `CLAUDE.md` lists "CI system: 262 tables, 1205 conversations, semantic search" under "What Works."

So the accurate status for our purposes: **the ingestion + indexing + turn-context semantic search lane reached working state and was populated; the higher-order knowledge layer (entity/decision/pattern extraction, summaries, project spaces, keeper agents, fanout) was DESIGNED in depth but largely NOT executed.** "Never used" is true of the *knowledge/agent* tier and of Tim's day-to-day workflow; it is not true of the raw pipeline. The miner skills (below) reference it as if live, which is consistent with the FRONTIER snapshot.

This is exactly the profile of "dormant production material with unique designs worth their inspiration": a real, deep, partly-running system whose *architecture* is the asset.

---

## 1. The data model (Observed — from the migrations)

Two table-name generations exist in the migrations. The 2026-01-19 founding migration (`20260119000000_conversation_intelligence_system.sql`) uses unprefixed names (`indexed_conversations`, `indexed_messages`, …); later migrations and the live system standardized on a `ci_` prefix (`ci_conversations`, `ci_messages`, …). Same shapes; the `ci_` names are canonical. (Observed: FRONTIER §14 "Naming Inconsistencies" calls this out.)

### Core data spine (the "what was said" layer)

```
ci_raw_data (staging)            JSONL-as-JSONB, one row per uploaded file, file_hash dedup
   │  extraction_status: pending → in_progress → complete
   ▼
ci_conversations                 one per session. project_path, git_branch, working_directory,
   │                             started/ended, message/tool/user/assistant counts,
   │                             title/summary/topics (the generated meaning layer),
   │                             content_hash, UNIQUE(source_id, source_session_id)
   ▼
ci_messages                      sequence_number, role, content, content_type, timestamp,
   │                             source_uuid (orig msg UUID), parent_message_id (THREADING),
   │                             has_tool_calls, token_count, raw_metadata (full JSONB)
   ▼
ci_tool_calls                    tool_name, tool_type, parameters JSONB, result, result_status,
   │                             addresses JSONB[] = [{type,path,operation}], duration_ms
   ▼
ci_artifacts                     UNIQUE(artifact_type, artifact_address). created_by /
   │                             last_modified_by conversation+tool_call, modification_count,
   │                             conversation_count
   ▼
ci_artifact_provenance           the M:N link: artifact ↔ conversation ↔ tool_call,
                                 operation (create/read/update/delete/rename/move),
                                 operation_timestamp, context_summary
```

### Knowledge layer (the "what it means" layer — mostly dormant)

- **`ci_entities`** (`extracted_entities`): `entity_type` (FK to registry), `entity_name` (e.g. `Decision:JWTTokenExpiryStrategy`), **`observations` JSONB** shaped by the type's schema, `source_message_ids[]`, `extraction_confidence`, `verified`/`verified_by`, `embedding vector(3072)`. Empty in the 02-10 snapshot.
- **`ci_relations`** (`extracted_relations`): typed edges between entities — `relation_type` FK, source/target entity, `strength`, `context`, UNIQUE(type, source, target).
- **`ci_embeddings`** (`conversation_embeddings`): polymorphic — `target_type` ∈ {conversation, message, chunk, summary, **turn_context**}, `target_id`, `chunk_index`, `chunk_text`, `embedding` (vector; note dimension drift below), `embedding_model`.

### Pre-built navigation indexes (Observed; "index" tier)

- `index_temporal` — time buckets (hour/day/week/month) → conversation_ids[], aggregated topics/artifact_types/tool_types + counts.
- `index_artifact` — per-artifact rollup: creation conversation, all_conversation_ids[], modification_dates[], **related_artifact_ids[]** (artifacts touched in the same conversations).
- `index_topic` — topic → conversation_ids[] + entity_ids[] + first/last_seen + `topic_embedding`.

### Pipeline state

- `extraction_runs` — audit log per extractor run (items processed/created/updated/failed, triggered_by).
- `sync_state` — per-source cursor (last file/timestamp/session processed).

### Dimension drift worth noting (Observed)

The founding migration declared `vector(3072)` (text-embedding-3-large). The 2026-02-12 turn-context migration runs on **`vector(384)`** via a `generate-query-embedding` Edge Function (`text-embedding-3-small`). So the populated/working embeddings are 384-dim; the original 3072 columns are legacy. This is a real inconsistency to inherit-or-discard, not adopt blindly.

---

## 2. THE FOUR (FIVE) UNIQUE DESIGN IDEAS WORTH HARVESTING

These are the ideas that do NOT appear in episodic-memory (a flat per-conversation semantic store) or the Company corpus (markdown + embeddings). They are CI-specific and they're the reason this project is worth reading.

### ⭐ Idea 1 — Turn-context embeddings (the strongest, and it actually ran)

**Observed** (`20260212000000_ci_turn_context_embeddings.sql`, fn `ci_build_turn_pairs`). Instead of embedding a whole conversation (too coarse — what 02-10 had, returned junk) or every isolated message (too fine, no context), CI embeds the **turn pair**: one *real* user message + the assistant text that answered it + **a compressed summary of the tool calls that happened inside that turn**, assembled as:

```
User: <user text, capped>
Assistant: <combined assistant text, capped>
[Tools: Read(index.ts), Bash(npm run build…), Grep(pattern), mcp__supabase__execute_sql, …]
```

The tool line is built by a CASE that renders each tool compactly — `Read/Edit/Write` show just the filename (regex strips the path), `Bash` shows the first 60 chars of the command, `Grep/Glob` show the pattern, `mcp__*` show the tool name. The function also detects "real" user messages (filters out tool-result echo turns) to find genuine turn boundaries.

**Why it's the gold idea for the merge:** the unit of retrieval is the *intent → response → actions* triple — Tim's `Intent → … → Execution` circuit captured at passage granularity, WITH the tools that were run baked into the embedded text so a semantic query like "how did I fix the timeout" matches the turn where the Bash/Edit actually happened. FRONTIER reports 24,847 of these built and `ci_search` returning real passage text (`chunk_text` populated). This is a far better conversation-retrieval primitive than "embed the file."

### ⭐ Idea 2 — Dual-granularity embedding registry (wayfinding vs. retrieval, in a table)

**Observed** (`ci_embedding_config` table + seed rows). Embedding *strategy* is a registry row, not code. Two seeded layers, explicitly labelled by ROLE:

- `turn_context` — "Primary retrieval layer." Many per conversation. content_function = `ci_build_turn_pairs`.
- `conversation_summary` — "Wayfinding layer." One per conversation, built from first/last turns + metadata (`ci_build_conversation_embed_text`). content_function named in the row.

Each config row carries `source_scope`, `model_id`, `dimensions`, `target_type`, `content_function` (the SQL builder to call), and `chunk_config`. `ci_search` takes an **`embedding_config` parameter** that routes the query to the right layer. So "what to embed, how, at what granularity, with which model" is data — you can add a 3rd or 4th embedding strategy (the docs envision 7+) by inserting a row + a builder function. The two-tier coarse-for-navigation / fine-for-answer split is the harvestable shape, independent of the registry mechanics.

### ⭐ Idea 3 — Artifact provenance graph (conversations ↔ files/tables, bidirectional, with "related artifacts")

**Observed** (`ci_artifacts` + `ci_artifact_provenance` + `record_artifact_provenance()` fn + `navigate_by_artifact`/`ci_trace`). Every tool call's `addresses[]` (extracted file paths, table names, function names, each tagged with an operation) is reified into a first-class **artifact** node, and a provenance edge (operation + timestamp + context) links artifact ↔ conversation ↔ tool_call. This makes the store answer questions episodic-memory and a flat corpus *cannot*:

- "Why does this file exist / who created this table?" → creation conversation.
- "What conversations touched `index.ts`, in what order, doing what?" → modification timeline.
- "What other artifacts are used alongside this one?" → `related_artifact_ids` (co-occurrence within the same conversations).

It inverts the index: from *conversation→content* to *artifact→conversations*. For a self-building Company whose conversations ARE the build log, this is the "how did this code come to be" lane — provenance as a queryable graph, derived automatically from tool-call addresses. 9,833 provenance records existed (FRONTIER).

### ⭐ Idea 4 — Registry-driven, self-describing extraction & navigation (config-as-behaviour)

**Observed** (Part 1 of the founding migration: 6 registry tables). The entire pipeline is declared in tables, changeable by INSERT not by code edit:

- `entity_type_registry` — each extractable knowledge type (Decision, Pattern, VocabularyTerm, Implementation, OpenIssue, Insight) carries its own **`observation_schema`** (required/optional fields + display patterns), its **`extraction_prompt`**, model, few-shot examples, name_prefix. **The schema the LLM extracts to, and the prompt it uses, live in a row.** Add a new knowledge type = add a row.
- `relation_type_registry` — typed edges (supersedes, resolves, implements, conflicts_with, led_to…) with directionality, inverse names, and valid source/target type constraints. This is a *typed knowledge graph schema*, declared.
- `extractor_registry` — the pipeline DAG: each extractor has `execution_order`, `depends_on[]`, input/output type, model, batch_size, rate limit.
- `index_type_registry` + `lens_registry` — navigation as data: indexes (temporal/artifact/topic/semantic/provenance) and **"lenses"** that combine them (Timeline, Artifact History, Concept Explorer, Decision Tracker) with their `typical_queries[]`. A lens is a named, reusable way of looking at the same store — directly resonant with Tim's RHM "looking" and altitude-transformation themes.

The notable thing for harvesting: **extraction is treated as a typed, schema-bearing, prompt-bearing registry**, the same self-declaring-schema pattern the repo's CLAUDE.md says was independently rediscovered in `agent_dev_tracers`. The 6 entity types and their observation schemas ARE Tim's knowledge ontology, sitting in seed data ready to mine.

### ⭐ Idea 5 — Parametric MCP tools with a response envelope + format selector + decorators

**Observed** (`20260210000000_ci_parametric_mcp_tools.sql`, `ci_mcp_config`, FRONTIER §Query Layer). This is the "MCP is the top priority / parameterised not flat-per-op" principle, already built once. 10 narrow tools were collapsed into **6 parametric tools**: `ci_discover` (scopes: projects/conversations/timeline/issues), `ci_read` (views: thread/context/summary/tools), `ci_search` (scopes: messages/tools/artifacts/topics/entities/semantic/issues), `ci_trace` (modes: provenance/creation/related), `ci_manage`, `ci_issues` (8 actions). Key sub-ideas, all directly relevant to the Company MCP:

- **Response envelope on every call**: `{ envelope (the filters/params actually applied), results, stats }` — the tool tells the agent what it did.
- **`return_format` selector** (`summary` | `content` | `stats` | `addresses`) defined in `ci_mcp_config` with `use_when` guidance — same query, agent picks weight: lightweight IDs for browsing, full text for reading, aggregates for overview, **`addresses` explicitly "for programmatic chaining / passing results to another tool"** (grounded-chain ergonomics).
- **Decorators** (`@browse @content @search @temporal @semantic @provenance @system`) tag each tool for agent discovery, defined in config and inspectable at `ci://config/decorators`.
- **Compound filters combine across scopes**: project_path, source_id, date_range, tool_name, tool_type, role, embedding_config — all optional, all stackable (e.g. semantic search restricted to one project + date window + only turns that used `mcp__supabase__execute_sql`).
- **Config is inspectable & writable via the tool itself** (`ci_manage`), not hardcoded — switch providers, enable/disable tools, change defaults as data.

(Honourable mentions, lighter evidence: **polymorphic comments / tokenized enums** in `ci_issues_system` — enum values are config tokens validated at function level, "adding a type = config update not migration"; **decorator-routed agents** `ci_agent_decorators` mapping `@keeper`/`@search`/`@architecture` in a comment to a LangGraph deployment; **project spaces** `ci_project_spaces` using LTREE paths + `ci-space://` addresses + 4-level config inheritance universal<space<project<scope. These are designed, mostly un-run.)

---

## 3. The live conversation-sync lane (Observed — this part works)

There are TWO ingestion lanes into this store. The merge cares about both because they're a second, *already-running* copy of the conversation-store-as-primary-source spine.

### Lane A — SessionEnd → Storage → Edge Function → staging

```
/home/tim/.claude/projects/<project>/<session>.jsonl
   │  (SessionEnd hook OR manual /sync-conversations)
   ▼
~/.claude/commands/sync-conversations.sh   → sources vi_worker/.env for SERVICE_ROLE_KEY,
   │                                           runs the python daemon --once
   ▼
~/.claude/sync-conversations-to-supabase.py
   │  • SHA256 hash, skips unchanged files (incremental)
   │  • SKIPS agent-*.jsonl (sidechains) and history.jsonl (too large)
   │  • FILTERS OUT type:'progress' records before upload (streaming status / embedded
   │    subagent noise) — logs MB saved; this is a real content-curation decision
   │  • uploads to Storage bucket `conversation-archives` at
   │       claude-code/<project-name>/<session>.jsonl   (upsert)
   │  • can run --watch via inotify (IN_CLOSE_WRITE) for continuous sync
   ▼
POST /functions/v1/conversation-sync   (Edge Function, Observed in index.ts)
   │  • downloads file, parses JSONL, hashes
   │  • extractMetadata() → source_id, session_id, project_path, first/last timestamp
   │  • upsert into ci_raw_data keyed on (storage_bucket, storage_path);
   │    if file_hash changed → UPDATE + extraction_status='pending' (re-extract on change)
   ▼
ci_raw_data  → (downstream extractor moves it into ci_conversations/messages/tool_calls)
```

**State (Observed):** the python daemon, the shell command, the `conversation-sync` Edge Function, and the `conversation-archives` bucket are all present and coherent. The daemon persists `conversation-sync-state.json` and reports lifetime totals. Whether the SessionEnd hook is *currently wired* in settings I did not verify (the shell comment says "Called by SessionEnd hook or manually"); the `/sync-conversations` skill exists to force it. So: **the lane is real, incremental, dedup'd, progress-filtered, and re-extract-on-change — a production-grade ingest.** Its design choices (hash dedup, progress-record stripping, project-name foldering, upsert + hash-diff re-trigger) are themselves harvestable for the merge's ingestion.

### Lane B — the in-repo extraction pipeline

`conversation-extract`, `conversation-entity-extract`, `conversation-summarize-batch`, `conversation-summarize-langgraph`, `conversation-embeddings(-batch)`, `conversation-turn-embeddings`, `conversation-summary-reembed`, `generate-query-embedding` Edge Functions (Observed in the functions/ listing). These read `ci_raw_data` → fill the structured tables → build turn pairs → embed. This is the lane that reached the FRONTIER numbers.

---

## 4. What the miner skills expect from it (Observed)

Both skills treat CI as a live, queryable intelligence layer over the same conversation stream — this is *exactly* the merge's "conversation-store-as-primary-source" premise, already given an interface.

**`~/.claude/skills/ci-pattern-miner/SKILL.md`** and **`~/.claude/skills/fleet-miner/SKILL.md`** both:

- Declare CI as "52 projects, ~230K messages, ~370 conversations — 12+ months of continuous thought-to-agent interface" and frame it as **"Tim's intelligence operating as a system… everything came from the same mind, the same stream. Find the pattern, not the instance."** (This is the thesis for why the conversation store is worth mining at all.)
- Call the MCP tools `mcp__conversation-intelligence__ci_search / ci_discover / ci_trace / ci_read` (ci-pattern-miner names these in its `tools:` frontmatter).
- Expect `ci_search` to accept exactly the parametric surface CI built: `scope` ∈ {semantic, messages, tools}, `embedding_config` ∈ {turn_context, conversation_summary}, `source_id` (claude_code vs lobechat), `project_path`, `role`, `return_format: content`, `max_content_chars`, `limit`.
- Mine along **6–7 dimensions** that map onto CI's entity types: Vocabulary, Principles, Decisions, Intent, Frustrations/Anti-patterns, Architecture, Cross-Project patterns. fleet-miner's classification table (Vocabulary/Principle/Decision/Intent/Anti-pattern/Architecture) is essentially `entity_type_registry` used as a lens.
- Require **provenance on every finding** (`SOURCE: ci://<project>/<conversation_id> turn <n>`, Tim's exact words) — they consume the turn-context + addressing design directly.
- Note **source_id matters**: `lobechat` = design thinking, `claude_code` = implementation. CI's multi-source registry is what makes that split queryable.

So the miners are the *consumers* that prove the CI design's intent: a conversation store you query semantically at turn granularity, filtered by project/source/role, to recover Tim's patterns with citations. If CI is dormant, these skills currently have nothing live to call (or call the FRONTIER-era deployment) — which is itself a signal for the merge: **the demand for this interface already exists and is encoded in skills.**

---

## 5. How it relates to the conversation-store-as-primary-source spine

- **Same source, richer target.** Episodic-memory and CI ingest the identical artifact (`~/.claude/projects/**/*.jsonl`). Episodic-memory's target is flat (searchable conversation chunks). CI's target is a **5-layer relational model** (raw → conversation → message → tool_call → artifact + provenance) plus a typed knowledge graph (entities/relations) plus multi-granularity embeddings. The merge can treat CI as "what the rich end of the spectrum looks like."
- **The turn pair is the unit Tim's circuit wants.** `Intent → Proposal → … → Execution` is literally a user-turn + assistant-turn + tool-calls. CI's turn-context embedding captures that triple as the retrieval atom — better aligned to Tim's mental model than message- or file-level chunks.
- **Tool calls and artifacts are not noise — they're the build provenance.** For a Company that builds itself through these very conversations, the artifact-provenance graph turns "the conversation log" into "the causal history of the codebase." That's a capability neither a flat corpus nor episodic-memory has.
- **Registry/parametric/envelope/decorator patterns are the Company-MCP house style, pre-validated.** The Company's stated law is "every capability through the MCP, parameterised/resource-oriented, agent-intuitive, grounded-chain-easiest." CI's 6 parametric tools + response envelope + `addresses` return-format + decorators are a working precedent for that exact bar.
- **The dual lane is a warning and an opportunity.** Two ingestion pipelines (Lane A live, Lane B in-repo) plus episodic-memory = three copies of the same stream. The merge should consolidate to ONE primary lane, but can lift Lane A's curation (hash dedup, progress-stripping, re-extract-on-change) and CI's relational target.

---

## 6. Dormant / incomplete inventory (Observed, from FRONTIER §2 / §9 / §12)

What is DESIGNED in depth but NOT executed (do not assume these run):

- **Knowledge extraction tier** — entity/decision/pattern/relation extraction: registries seeded, extractor functions partly missing; `ci_entities`/`ci_relations` were empty at 02-10; the "Processing Orchestration Layer" has no executor (Gap 1). Summaries/topics were NULL.
- **Embedding modes** — 2 of 7+ envisioned built (turn_context + conversation_summary ran; depth-classified, entity, etc. not).
- **Project Space system** (`20260213000000`) — 12 tables (LTREE spaces/projects/scopes/resources, notice boards, keeper config, taxonomies, workflows, entry points) — **migration written, NOT applied** (Frontier 4).
- **Keeper / LangGraph agents** — 0 of ~16 envisioned deployed; `ci_agent_decorators` routing table exists, agents don't.
- **Fanout/distribution** — 0 of 10+ destinations configured.
- **Queues** — pgmq queues reported "stuck processing" (§12).
- **Design conflicts** — FRONTIER §10 records two design docs with incompatible structural framings and an internal migration conflict; the 3072 vs 384 embedding-dimension drift; unprefixed vs `ci_` naming. **Harvest the ideas, not the schema verbatim.**

---

## 7. Source file map (for follow-up)

- Primary state analysis: `/home/tim/repos/Supabase/docs/conversation-intelligence-current-state-analysis.md`
- Ground-truth frontier map (215KB; the richest single doc): `/home/tim/repos/Supabase/docs/CI_IMPLEMENTATION_FRONTIER.md`
- Founding data model + registries: `/home/tim/repos/Supabase/supabase/migrations/20260119000000_conversation_intelligence_system.sql`
- Turn-context embeddings (Idea 1 & 2): `…/migrations/20260212000000_ci_turn_context_embeddings.sql`
- Parametric MCP tools (Idea 5): `…/migrations/20260210000000_ci_parametric_mcp_tools.sql`
- Issues / polymorphic comments / tokenized enums: `…/migrations/20260211000000_ci_issues_system.sql`
- Project spaces (LTREE + inheritance): `…/migrations/20260213000000_ci_project_space_system.sql`
- Decorator-routed agents: `…/migrations/20260216000000_ci_agent_decorator_registry.sql`
- Live sync lane: `/home/tim/.claude/sync-conversations-to-supabase.py`, `/home/tim/.claude/commands/sync-conversations.sh`, `…/supabase/functions/conversation-sync/index.ts`
- Consumers: `/home/tim/.claude/skills/ci-pattern-miner/SKILL.md`, `/home/tim/.claude/skills/fleet-miner/SKILL.md`
- Parametric enrichment notes: `/home/tim/repos/Supabase/docs/PARAMETRIC_ENRICHMENT_SUMMARY.md`
- CI chat integration plan: `/home/tim/repos/Supabase/docs/CI_CHAT_INTEGRATION_PLAN.md`
