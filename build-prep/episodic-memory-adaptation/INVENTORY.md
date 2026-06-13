# Episodic-Memory Plugin — Full Inventory (Ground Truth for Adaptation)

> Status of this document: **inventory of what exists**, written from direct file reads and live database queries on this machine (2026-06-11). Statements are marked **Observed** (read in code / queried from the live DB) vs **Inferred** (pattern-matched, not execution-verified). Companion doc: `UPSTREAM-DOCS.md` in this directory (written by a parallel agent).

| Key fact | Value |
|---|---|
| Source repo | https://github.com/obra/episodic-memory (MIT, Jesse Vincent / jesse@fsck.com) |
| Installed version | **1.0.15** (plugin install of record) |
| Local installed clone | `/home/tim/.claude/plugins/cache/superpowers-marketplace/episodic-memory/1.0.15/` |
| Fresh upstream clone | `/home/tim/episodic-memory/` — **v1.4.2** (much newer; structural diffs in §6) |
| Data directory | `/home/tim/.config/superpowers/` (archive + index + search log) |
| Database | `/home/tim/.config/superpowers/conversation-index/db.sqlite` — **10.87 GB** (+23 MB WAL) |
| Archive | `/home/tim/.config/superpowers/conversation-archive/` — **13 GB**, 99 project dirs, 29,678 `.jsonl` files |
| Indexed | 13,270 conversations / 75,374 exchanges / 75,375 vectors / 6,713,952 tool-call rows / 96 projects |
| Embedding model | `Xenova/all-MiniLM-L6-v2` via Transformers.js — **fully local, 384-dim, no API** (v1.4.2 upgraded to `Xenova/bge-small-en-v1.5`, same 384 dims) |
| Plugin enabled via | `/home/tim/.claude/settings.json` line 112: `"episodic-memory@superpowers-marketplace": true` |

**One-paragraph architecture summary.** A `SessionStart` hook fires `episodic-memory sync --background` on every Claude Code startup/resume. Sync copies new/modified conversation JSONL files from `~/.claude/projects/<project>/<session-uuid>.jsonl` into a permanent archive at `~/.config/superpowers/conversation-archive/<project>/`, parses each file into **user→assistant exchanges** (the chunk unit), generates one 384-dim embedding per exchange with a local Transformers.js MiniLM model (user msg + assistant msg + tool names concatenated, truncated to 2,000 chars), and writes everything into a single better-sqlite3 database with a `vec0` virtual table (sqlite-vec extension) for KNN search. Separately, sync generates one **AI summary per conversation** (a `*-summary.txt` sidecar file next to the archived JSONL) by calling the Claude Agent SDK (`haiku` by default, hierarchical chunk-summarize for long conversations, max 10 summaries per sync run). At query time, an MCP server (stdio, two tools: `search` and `read`) embeds the query, runs vector KNN and/or SQL `LIKE` text search, merges, attaches the sidecar summary and a 200-char snippet, and returns results pointing at archive file paths + line ranges; `read` renders any JSONL range back into readable markdown. A shipped `search-conversations` agent (haiku) is the intended consumer: it searches, reads top hits, and returns a ≤1000-word synthesis so the main agent never loads raw conversations.

---

## 1. Full Source Inventory (installed v1.0.15)

Root: `/home/tim/.claude/plugins/cache/superpowers-marketplace/episodic-memory/1.0.15/`
(All paths below relative to this root unless absolute. `node_modules/` = 484 MB of installed deps, excluded. `.git/` internals excluded. `.in_use/` contains empty PID-named lock-marker files — **Inferred**: Claude Code's "plugin in use by session" markers, not part of the package.)

### 1.1 Package + plugin manifests

**`package.json`** — npm identity: `episodic-memory@1.0.15`, ESM (`"type": "module"`), main `dist/index.js`. Four bin entries: `episodic-memory` (unified CLI), `episodic-memory-index`, `episodic-memory-search` (legacy), `episodic-memory-mcp-server`. Runtime deps (load-bearing list): `@anthropic-ai/claude-agent-sdk` ^0.1.9 (summaries), `@modelcontextprotocol/sdk` ^1.20.0 (MCP server), `@xenova/transformers` ^2.17.2 (local embeddings), `better-sqlite3` ^12.6.2 (storage), `sqlite-vec` ^0.1.7-alpha.2 (vector index), `marked` ^16.4.0 (HTML render), `zod` ^3.25.76 (MCP input validation). Build: `tsc` + an esbuild bundle of the MCP server with natives/SDK marked external (line 15). `postinstall: npm rebuild better-sqlite3` (line 16) guards against NODE_MODULE_VERSION mismatches.

**`.claude-plugin/plugin.json`** — the Claude Code plugin manifest. Declares:
- `"agents": ["./agents/search-conversations.md"]` — ships the search agent.
- `"mcpServers": { "episodic-memory": { "command": "node", "args": ["${CLAUDE_PLUGIN_ROOT}/cli/mcp-server-wrapper.js"] } }` — the MCP server registration. This is why the tools appear in sessions as `mcp__plugin_episodic-memory_episodic-memory__search` / `__read`.
- Note: hooks are NOT declared here — Claude Code auto-loads `hooks/hooks.json` (a duplicate declaration was a bug fixed in 1.0.11 per CHANGELOG).

**`.claude-plugin/marketplace.json`** — dev-marketplace self-listing (`episodic-memory-dev`), used for local development installs; not load-bearing at runtime.

**`.gitignore`** — ignores `node_modules/`, `package-lock.json`, `*.db`, `*.db-shm`, `*.db-wal`, `.env`, `tmp/`, `*.log`. (A `package-lock.json` is nonetheless present in this installed copy.)

**`LICENSE`** — MIT, Copyright (c) 2025 Jesse Vincent.

### 1.2 Hook wiring — `hooks/hooks.json`

The ONLY hook the plugin registers (Observed, full file):

```json
{ "hooks": { "SessionStart": [ { "matcher": "startup|resume",
    "hooks": [ { "type": "command",
      "command": "node ${CLAUDE_PLUGIN_ROOT}/cli/episodic-memory.js sync --background",
      "async": true } ] } ] } }
```

- Event: **`SessionStart`** with matcher `startup|resume` (NOT SessionEnd, despite README prose suggesting "session-end indexing" — the README is stale on this point; CHANGELOG 1.0.7 documents the move to SessionStart + `--background`).
- `async: true` + the `--background` flag double-protect Claude startup from blocking. The `--background` implementation (`src/sync-cli.ts:44-59`) spawns a **detached** copy of itself with `stdio: 'ignore'`, `child.unref()`, then exits 0 immediately.
- Consequence (Observed in code, Inferred for runtime behavior): every Claude Code session start on this machine forks a background indexing process. v1.4.2 added a file lock because concurrent sessions racing on the same SQLite DB was a real crash class (#97).

### 1.3 `src/` — the core library (3,612 lines TS; the real subject)

**`src/paths.ts` (101 lines) — ALL filesystem conventions live here.** This is the single most important adaptation file.
- `getSuperpowersDir()` (lines 24-41): precedence `EPISODIC_MEMORY_CONFIG_DIR` env → `PERSONAL_SUPERPOWERS_DIR` env → `$XDG_CONFIG_HOME/superpowers` → `~/.config/superpowers` (default). Auto-creates.
- `getArchiveDir()` (46-53): `<superpowersDir>/conversation-archive` (test override `TEST_ARCHIVE_DIR`).
- `getIndexDir()` (58-60): `<superpowersDir>/conversation-index`.
- `getDbPath()` (65-72): `<indexDir>/db.sqlite` (overrides: `EPISODIC_MEMORY_DB_PATH`, `TEST_DB_PATH`).
- `getExcludeConfigPath()` (77-79): `<indexDir>/exclude.txt`.
- `getExcludedProjects()` (85-100): project-level exclusion list from `CONVERSATION_SEARCH_EXCLUDE_PROJECTS` env (comma-separated) or `exclude.txt` (one per line, `#` comments). Default: no exclusions.

**`src/types.ts` (52 lines) — the data model.** `ConversationExchange` is the atom: `{ id, project, timestamp, userMessage, assistantMessage, archivePath, lineStart, lineEnd, parentUuid?, isSidechain?, sessionId?, cwd?, gitBranch?, claudeVersion?, thinkingLevel?, thinkingDisabled?, thinkingTriggers?, toolCalls? }`. Plus `ToolCall { id, exchangeId, toolName, toolInput?, toolResult?, isError, timestamp }`, `SearchResult { exchange, similarity, snippet }`, `MultiConceptResult { exchange, snippet, conceptSimilarities[], averageSimilarity }`.

**`src/parser.ts` (238 lines) — JSONL → exchanges (the chunking strategy).**
- `parseConversation(filePath, projectName, archivePath)` streams the JSONL line-by-line (readline, lines 33-37).
- Only `type === 'user' | 'assistant'` records are considered (line 102); everything else (file-history-snapshots, system) is skipped. Malformed JSON lines are silently skipped (202-205).
- **Chunk = one exchange = one user message + ALL subsequent assistant messages until the next user message** (state machine at lines 157-201). A new user message finalizes the previous exchange (`finalizeExchange`, 58-93). Multiple assistant text blocks are joined with `\n\n` (line 76).
- Exchange ID = `md5(archivePath + ":" + lineStart + "-" + lineEnd)` (lines 60-63) — deterministic, so re-indexing the same file upserts rather than duplicates (paired with `INSERT OR REPLACE` in db.ts).
- Tool-use blocks in assistant content become `ToolCall` rows with random UUIDs (124-138). **Tool RESULTS are never captured** — there's an explicit TODO at lines 141-149; confirmed live: `SELECT COUNT(*) FROM tool_calls WHERE tool_result IS NOT NULL` → **0** on the 6.7M-row table.
- User messages consisting only of tool_results become `"(tool results only)"` exchanges (line 163).
- Per-line metadata captured into the exchange: `parentUuid, isSidechain, sessionId, cwd, gitBranch, version, thinkingMetadata.{level,disabled,triggers}` (162-176), updated from the latest assistant message (197-200).
- `parseConversationFile()` (218-237): convenience wrapper deriving project from parent dir name.

**`src/embeddings.ts` (47 lines) — the embedding provider (local).**
- `initEmbeddings()` (5-14): lazily builds a singleton Transformers.js `feature-extraction` pipeline with hardcoded model `'Xenova/all-MiniLM-L6-v2'` (line 10). First run downloads the ONNX model to the Transformers.js cache; thereafter fully offline. No provider abstraction, no config hook — **the model ID is a hardcoded string** (the one and only place).
- `generateEmbedding(text)` (16-30): truncates to **2,000 characters** (line 22, comment: 512-token model limit), `pooling: 'mean', normalize: true`, returns `number[]` (384 floats).
- `generateExchangeEmbedding(user, assistant, toolNames?)` (32-46): embeds the literal string `` `User: ${user}\n\nAssistant: ${assistant}` `` + optional `\n\nTools: name1, name2` — i.e. tool names ARE part of the semantic vector (intentional, for tool-based searches). Because of the 2,000-char truncation, long exchanges are embedded on roughly the first ~1,400 chars of user message + start of assistant message — **Observed truncation, Inferred consequence**: late content in big exchanges is invisible to vector search (text mode still finds it).

**`src/db.ts` (224 lines) — storage layer.**
- `initDatabase()` (39-130): opens better-sqlite3 at `getDbPath()`, loads sqlite-vec extension (`sqliteVec.load(db)`, line 51), sets `journal_mode = WAL` (54). Creates three tables:
  - `exchanges` (57-79): all ConversationExchange columns incl. an unused `embedding BLOB` column (line 67 — vestigial; vectors actually live in vec_exchanges. **Observed** it's in the schema; **Observed** insertExchange never writes it).
  - `tool_calls` (82-93): FK to exchanges.
  - `vec_exchanges` (96-101): `CREATE VIRTUAL TABLE ... USING vec0(id TEXT PRIMARY KEY, embedding FLOAT[384])` — **dimension 384 hardcoded here** (second hardcoded coupling to the model).
- `migrateSchema()` (8-37): additive column migrations via `pragma_table_info` + `ALTER TABLE` (idempotent; list at lines 12-23 — last_indexed, parent_uuid, is_sidechain, session_id, cwd, git_branch, claude_version, thinking_level, thinking_disabled, thinking_triggers).
- Indexes (107-127): timestamp DESC, session_id, project, is_sidechain, git_branch, tool_name, tool_exchange.
- `insertExchange()` (132-200): `INSERT OR REPLACE` into exchanges; for the virtual table, DELETE-then-INSERT (169-178) because vec0 doesn't support REPLACE; embedding serialized as `Buffer.from(new Float32Array(embedding).buffer)` (178); tool calls `INSERT OR REPLACE` (181-199).
- Helpers: `getAllExchanges`, `getFileLastIndexed` (MAX(last_indexed) per archive_path), `deleteExchange` (both tables).

**`src/indexer.ts` (363 lines) — bulk/manual indexing paths.**
- Source dir: `getProjectsDir()` = `~/.claude/projects` (line 20, override `TEST_PROJECTS_DIR`) — **the conversation-source convention**.
- Sets `CLAUDE_CODE_MAX_OUTPUT_TOKENS=20000` for SDK summarizer calls (line 12).
- `indexConversations(limitToProject?, maxConversations?, concurrency=1, noSummaries=false)` (40-181): walks every project dir, copies each `.jsonl` to archive if absent (107-110), parses, batch-summarizes missing summaries with bounded concurrency (`processBatch`, 24-38; concurrency 1-16), then embeds + inserts every exchange sequentially (154-176).
- `indexSession(sessionId)` (183-253): finds the single file whose name contains the session ID, archives/parses/summarizes/indexes it (designed for per-session hook use).
- `indexUnprocessed()` (255-362): the `--cleanup` path — skips any file whose archive_path already has rows (`SELECT COUNT(*) ... WHERE archive_path = ?`, 295-298), processes the rest.
- Summary sidecar convention everywhere: `archivePath.replace('.jsonl', '-summary.txt')`.

**`src/sync.ts` (221 lines) — the incremental pipeline (what the hook actually runs).**
- `EXCLUSION_MARKERS` (6-10): `<INSTRUCTIONS-TO-EPISODIC-MEMORY>DO NOT INDEX THIS CHAT</INSTRUCTIONS-TO-EPISODIC-MEMORY>`, `'Only use NO_INSIGHTS_FOUND'`, and `SUMMARIZER_CONTEXT_MARKER` (from constants.ts). `shouldSkipConversation()` (12-20) reads the whole file and skips indexing (but still archives) if any marker appears anywhere.
- `copyIfNewer()` (36-57): mtime comparison; atomic copy via `dest.tmp.<pid>` + rename.
- `syncConversations(sourceDir, destDir, options)` (69-220), three phases:
  1. **Copy** (92-138): walk `~/.claude/projects`, honor excluded projects, copy new/updated `.jsonl`s. Only files copied THIS RUN go on `filesToIndex` (114-117). Files needing summaries are queued independently (122-130) — only files whose basename is a UUID (`extractSessionIdFromPath`, 59-67).
  2. **Index** (141-179): dynamic-imports db/embeddings/parser; for each copied file: skip if exclusion marker, parse, embed each exchange, `insertExchange`.
  3. **Summaries** (182-217): cap of `summaryLimit ?? 10` per run (186-188) — the backlog drains 10 per session start; remainder logged as "will process on next sync".
- **Observed consequence on this machine**: archive holds 29,678 JSONLs but only 13,270 are in the index and only 1,267 have summaries — because (a) sync only indexes files it copies (pre-existing archive backlog needs `index --cleanup`), (b) the 10-per-run summary cap, (c) exclusion markers. This live gap is itself useful adaptation evidence: the incremental design assumes you started from day one.

**`src/summarizer.ts` (203 lines) — AI summaries (the ONLY non-local AI dependency).**
- `callClaude()` (49-85): uses `query()` from `@anthropic-ai/claude-agent-sdk` — i.e. **summaries ride your Claude Code authentication** by spawning a Claude subprocess. Model: `EPISODIC_MEMORY_API_MODEL` env or `'haiku'` (line 50); fallback `EPISODIC_MEMORY_API_MODEL_FALLBACK` or `'sonnet'` on `thinking.budget_tokens` API errors (72-79).
- `getApiEnv()` (16-32): optional rerouting — `EPISODIC_MEMORY_API_BASE_URL` → `ANTHROPIC_BASE_URL`, `EPISODIC_MEMORY_API_TOKEN` → `ANTHROPIC_AUTH_TOKEN`, `EPISODIC_MEMORY_API_TIMEOUT_MS` → `API_TIMEOUT_MS`, merged over process.env. **This is the documented seam for pointing summarization at any Anthropic-compatible endpoint** (README "API Configuration", lines 128-158).
- `summarizeConversation(exchanges, sessionId?)` (95-202): trivial conversations get a stock string (97-106); ≤15 exchanges → single prompt with `<summary></summary>` tag extraction (109-140); >15 → **hierarchical**: chunks of 8 exchanges (chunkExchanges, 87-93), 2-3-sentence summary per chunk, then a synthesis prompt over the part-summaries (179-201), fallback to concatenated chunk summaries on synthesis failure.
- Every summarizer prompt embeds `SUMMARIZER_CONTEXT_MARKER` (`src/constants.ts:6-7`: "Context: This summary will be shown in a list to help users and Claude choose which conversations are relevant") — which doubles as the self-exclusion marker so the summarizer's own SDK-spawned conversations never pollute the index (fix from 1.0.14, #15).

**`src/search.ts` (340 lines) — the query pipeline.**
- `searchConversations(query, {limit=10, mode='both', after, before})` (27-144):
  - Vector branch (47-75): embed query, then `SELECT ... FROM vec_exchanges AS vec JOIN exchanges AS e ON vec.id = e.id WHERE vec.embedding MATCH ? AND k = ? ... ORDER BY vec.distance ASC` — sqlite-vec KNN.
  - Text branch (77-110): `LIKE '%query%'` on user_message OR assistant_message, ordered timestamp DESC. (NOT FTS5 — the MCP-TOOLS.md claim of "SQLite FTS5" is wrong; it's a plain LIKE scan. **Observed**.)
  - `both`: vector results first, text results appended after ID-dedup (99-109).
  - Date filters are interpolated directly into SQL as `e.timestamp >= '...'` (43-45) — validated first by regex+Date (15-25), so injection-safe in practice but string-built (worth tightening in a fork).
  - Result assembly (114-143): loads `-summary.txt` sidecar if present, builds 200-char whitespace-collapsed snippet from the user message, similarity = `1 - distance` (vector) / undefined (text).
- `formatResults()` (175-225): markdown list — `[project, date] - NN% match`, summary if <300 chars, snippet, tool usage counts, and the load-bearing locator line: `Lines <start>-<end> in <archivePath> (<sizeKB>KB, <totalLines> lines)` (changed in 1.0.10 so Claude picks the right read tool for big files).
- `searchMultipleConcepts(concepts[], …)` (227-287) — multi-concept AND: vector-searches each concept with `limit*5`, groups hits by archivePath, keeps only conversations where **every** concept produced a hit, ranks by mean similarity. `formatMultiConceptResults` (289-339) shows per-concept percentages.

**`src/show.ts` (795 lines) — conversation rendering.**
- `formatConversationAsMarkdown(jsonl, startLine?, endLine?)` (26-221): JSONL → readable markdown; metadata header (sessionId/branch/cwd/version), sidechain grouping with `SIDECHAIN START/END` banners (95-105, role relabeled Agent/Subagent), tool_use blocks rendered with inputs and a forward-scan (up to 5 messages) for the matching tool_result by `tool_use_id` (164-193), token-usage footers. The 1-indexed line-range slice (30-35) is what makes MCP `read` paginated.
- `formatConversationAsHTML(jsonl)` (223-755): self-contained styled HTML (Apple-ish CSS), markdown-detection heuristic (`isMarkdown`, 768-785: ≥2 markdown patterns) and `marked` rendering with escape fallback. CLI-only (not exposed over MCP).

**`src/stats.ts` (134 lines)** — `getIndexStats()`: totals (conversations = DISTINCT archive_path, exchanges, projects), summary coverage by probing sidecar files, date range, top-10 projects; `formatStats()` text block. **`src/verify.ts` (186 lines)** — `verifyIndex()`: detects missing summaries, orphaned DB rows (archive file gone), outdated files (mtime > last_indexed), corrupted files (parse throws); `repairIndex()`: delete orphans, re-summarize+re-index missing/outdated. **`src/constants.ts` (8 lines)** — the summarizer marker. **`src/index.ts`** — barrel re-export of everything (public npm API).

**CLI argument shims**: `src/sync-cli.ts` (85 lines; `--background` detach logic at 44-59), `src/index-cli.ts` (122 lines; subcommands index-session / index-cleanup / verify / repair / rebuild / index-all; `--concurrency 1-16`, `--no-summaries`), `src/search-cli.ts` (101 lines; multiple positional args trigger multi-concept), `src/show-cli.ts` (`--format markdown|html`), `src/stats-cli.ts`.

**`src/mcp-server.ts` (307 lines) — the MCP wrapper.**
- `Server({ name: 'episodic-memory', version: '1.0.0' })` over `StdioServerTransport` (106-116, 294-299).
- Tool **`search`** (124-151): query string OR array of 2-5 strings (multi-concept), mode vector/text/both (default both), limit 1-50 (default 10), after/before `YYYY-MM-DD`, response_format markdown|json. Read-only/idempotent annotations. Zod schema `SearchInputSchema` (31-68) re-validates at call time (183-184). Tool description sells it as memory: "Gives you memory across sessions… Use BEFORE every task…".
- Tool **`read`** (152-172): `{ path, startLine?, endLine? }` → `formatConversationAsMarkdown` over the (optionally sliced) file (251-275). No path sandboxing — any absolute JSONL path on disk is readable through it (**Observed**; an adapter may want to constrain to the archive dir).
- Errors returned as `isError: true` text content, never protocol errors (278-289).

### 1.4 `cli/` — entry points (all Node, no bash since 1.0.14)

- `cli/episodic-memory.js` (108 lines) — dispatcher: `sync|index|search|show|stats` → spawns the matching `dist/*-cli.js` (or `cli/index-conversations.js`) with `process.execPath`. This file is what the SessionStart hook invokes.
- `cli/index-conversations.js` (155 lines) — maps `--cleanup/--session/--verify/--repair/--rebuild` (rebuild has an interactive yes-confirmation) onto `dist/index-cli.js` subcommands.
- `cli/search-conversations.js` — thin spawn of `dist/search-cli.js`.
- `cli/mcp-server-wrapper.js` (110 lines) — **self-healing MCP launcher**: if `node_modules/` missing, runs `npm install --prefer-offline --no-audit --no-fund` in the plugin root (Windows `npm.cmd` + `shell:true` handling), then spawns `dist/mcp-server.js` with signal forwarding. This is why the plugin works from a bare git checkout on first MCP connection.
- `cli/episodic-memory`, `cli/index-conversations`, `cli/search-conversations`, `cli/mcp-server` (no extension) — legacy Node shims kept for the npm `bin` names / backward compat.

### 1.5 `dist/` — build output

Compiled JS + `.d.ts` for every src module (908 KB total): constants, db, embeddings, index, index-cli, indexer, mcp-server (the esbuild bundle, externals: better-sqlite3 / sqlite-vec / @xenova/transformers / agent-sdk / sharp / onnxruntime-node / fsevents), parser, paths, search, search-cli, show, show-cli, stats, stats-cli, summarizer, sync, sync-cli, types, verify. **Committed to git deliberately** (CHANGELOG 1.0.2) so the plugin runs without a build step. Runtime always executes `dist/`, never `src/`.

### 1.6 Agent, command, skill, prompt (the LLM-facing surface)

- **`agents/search-conversations.md`** — the shipped subagent (this is the `episodic-memory:search-conversations` agent visible in Tim's agent list). Frontmatter: `model: haiku`, `tools: Read, mcp__plugin_episodic-memory_episodic-memory__search, mcp__plugin_episodic-memory_episodic-memory__show` (note: tool list says `show` but the MCP server registers `read` — **Observed mismatch** in 1.0.15; the harness-rendered agent on this machine lists `search` and `show`… while the live deferred-tool list shows `__read`. An adapter should treat `read` as the real name). Behavior contract: search → read top 2-5 → synthesize 200-1000 words → Sources list with file:line + read-status → For-Follow-Up affordances. Explicit DO NOTs (no raw excerpts, no verbatim results).
- **`commands/search-conversations.md`** — the `/episodic-memory:search-conversations` slash command; thin instruction page ("dispatch a search agent… saves 50-100x context"). (Removed upstream in 1.4.0.)
- **`skills/remembering-conversations/SKILL.md`** — the auto-triggering skill ("Use when user asks 'how should I…' after exploring code, OR stuck, OR unfamiliar workflows, OR references past work"). Core rule: **always dispatch the search-conversations agent via Task tool; never call the MCP tools directly from the main context** (direct use labeled "Discouraged" — context-bloat economics). Trigger description was empirically tuned with subagent tests (CHANGELOG 1.0.12: 5/5 vs 3/5 scenarios).
- **`skills/remembering-conversations/MCP-TOOLS.md`** — full parameter reference for both tools (the FTS5 performance claim therein is inaccurate per §1.3 search.ts).
- **`prompts/search-agent.md`** — templated variant of the agent prompt with `{TOPIC}` / `{SEARCH_QUERY}` / `{FOCUS_AREAS}` placeholders; covered by `test/search-agent-template.test.ts` (placeholders + required sections + word-count requirements asserted).

### 1.7 `docs/`, `scripts/`, `test/`

- **`docs/SCHEMA.md`** — schema reference matching db.ts (exchanges / tool_calls / vec_exchanges FLOAT[384] / indexes / additive-migration policy).
- **`scripts/scrub-fixtures.sh`** — sed-based PII scrubber used to sanitize the real-conversation test fixtures (replaces author paths/names/branches).
- **`test/`** (1,608 lines, vitest, 30s timeout for embedding tests; fixtures are 5 real scrubbed conversation JSONLs from tiny to large):
  - `sync.test.ts` (211) — copy-if-newer, mtime skip/refresh, multi-project, jsonl-only, excluded projects, **DO-NOT-INDEX marker honored**.
  - `parser.test.ts` (141) — short/medium/long real files, metadata extraction, file-history-snapshot handling, malformed-JSONL tolerance.
  - `integration.test.ts` (250) — index fixtures into temp DB via `EPISODIC_MEMORY_DB_PATH`, then end-to-end vector/text/both searches.
  - `multi-concept.test.ts` (45) — AND semantics, low similarity for unrelated concepts, limit, per-concept scores.
  - `db.test.ts` (116) — migration idempotency, last_indexed stamping.
  - `verify.test.ts` (307) — missing-summary / orphan / outdated detection and repair behaviors.
  - `show.test.ts` (136), `stats.test.ts` (135), `api-config.test.ts` (48 — custom endpoint env honored), `search-agent-template.test.ts` (109).
  - Harness: `test-utils.ts`, `test-indexer.ts` (no-summaries indexing helper for tests).
  - **Coverage gaps relevant to a fork (Observed absence)**: no test pins the embedding model/dimension contract; no MCP-server protocol test; no hook test; summarizer tested only via api-config env behavior (actual SDK calls not exercised).

### 1.8 End-to-end data flow (traced through code)

```
Claude Code writes ~/.claude/projects/<flattened-cwd>/<session-uuid>.jsonl   (the source of truth)
        │  SessionStart hook (hooks/hooks.json) — every startup/resume
        ▼
node cli/episodic-memory.js sync --background
        │  dist/sync-cli.js: detach self (sync-cli.ts:44-59), then syncConversations(~/.claude/projects, archiveDir)
        ▼
PHASE 1 copy   sync.ts:92-138   copyIfNewer → ~/.config/superpowers/conversation-archive/<project>/<uuid>.jsonl
PHASE 2 index  sync.ts:141-179  parseConversation (parser.ts state machine: 1 chunk = user msg + following assistant msgs)
                                → generateExchangeEmbedding (embeddings.ts:32: "User:…\n\nAssistant:…\n\nTools:…", ≤2000 chars,
                                  Xenova/all-MiniLM-L6-v2, 384-dim, local ONNX)
                                → insertExchange (db.ts:132: exchanges row + vec_exchanges vector + tool_calls rows)
PHASE 3 summarize sync.ts:182-217  ≤10 per run → summarizer.ts (Claude Agent SDK, haiku→sonnet fallback,
                                  hierarchical for >15 exchanges) → <uuid>-summary.txt sidecar
        ▼
QUERY: MCP server (cli/mcp-server-wrapper.js → dist/mcp-server.js, stdio)
   search → search.ts: embed query → vec0 KNN (k=limit) ∪ LIKE-scan → join sidecar summary + snippet
            → "Lines a-b in <archive path> (KB, lines)" pointers
   read   → show.ts:formatConversationAsMarkdown(file[, startLine, endLine])
        ▼
CONSUMER: search-conversations agent (haiku) — search, read top 2-5, return ≤1000-word synthesis + sources
          (dispatched by the remembering-conversations skill; main context never loads raw JSONL)
```

---

## 2. Runtime / Data Footprint on THIS Machine (all Observed, queried 2026-06-11)

### 2.1 Data directory: `/home/tim/.config/superpowers/`

```
conversation-archive/   13 GB, 99 project directories, 29,678 .jsonl files, 1,267 *-summary.txt sidecars
conversation-index/     db.sqlite 10,869,481,472 bytes (10.87 GB) + db.sqlite-wal 23.4 MB + db.sqlite-shm 64 KB
search-log.jsonl        628 bytes — 11 query-log lines, Oct 2025 only (no code in 1.0.15 writes this; Inferred: older version or sibling tool)
lobe-importer.py        7.4 KB — Tim-custom Python script importing Lobe Chat JSON exports into the archive
                        (writes ~/.config/superpowers/conversation-archive/lobe-chat/<topic>.jsonl) — evidence the
                        archive format has already been used as an ingestion target for non-Claude conversations
```
No `exclude.txt` exists → no project exclusions active. No log files from the plugin itself.
`/home/tim/.claude/plugins/data/episodic-memory-superpowers-marketplace/` exists but is **empty** (the plugin ignores Claude Code's per-plugin data dir convention entirely).

### 2.2 Live database contents (sqlite3 readonly; vec0 count via the plugin's own `node_modules/sqlite-vec-linux-x64/vec0.so`)

| Metric | Value |
|---|---|
| `exchanges` rows | **75,374** |
| `vec_exchanges` rows (384-dim vectors) | **75,375** (one orphan vs exchanges — vec0 DELETE/INSERT non-atomicity; harmless) |
| Distinct conversations (archive_path) | **13,270** |
| Distinct projects | **96** |
| Timestamp range | 2025-11-10T01:17 → 2026-06-11T10:30 (today — sync is live and current) |
| `tool_calls` rows | **6,713,952** (tool_result NULL in 100% of rows — parser TODO) |
| Top projects | `-home-tim` 4,538 convs; `-home-tim-repos-Supabase` 2,443; `-home-tim--claude-plugins-cache-...episodic-memory-1-0-15` 1,580 (the plugin indexing sessions run *inside its own directory*); `-mnt-c-Users-Workstation001` 878; Visual-Designer 803; `-home-tim-company-interactive` 481 |

Live `.schema` matches `src/db.ts` exactly (plus sqlite-vec's internal shadow tables `vec_exchanges_info/_chunks/_rowids/_vector_chunks00`). The 10.87 GB is dominated by message text + 6.7M tool_call input JSONs + ~75K×1.5KB vectors. **Notable gap (Observed)**: 29,678 archived files vs 13,270 indexed — the pre-install backlog was archived by early full-index runs but most files either predate install-time indexing, carry exclusion markers, or were copied without being indexed; only 1,267 summaries exist (10-per-sync drip never caught up). Earliest indexed timestamp (2025-11-10) predates the recorded install (2026-01-28 per `installed_plugins.json`), consistent with an earlier install/rebuild cycle — **Inferred**, not verified.

### 2.3 Enablement / configuration

- `/home/tim/.claude/settings.json:112` — `"episodic-memory@superpowers-marketplace": true` under `enabledPlugins`.
- `/home/tim/.claude/plugins/installed_plugins.json` — `episodic-memory@superpowers-marketplace`: scope user, installPath = the 1.0.15 cache dir, installedAt 2026-01-28, lastUpdated 2026-05-23, gitCommitSha `6feaa5bd8752ae104c88d251e68ce19c30a1bd2f`.
- `/home/tim/.claude.json` — contains `"plugin:episodic-memory:episodic-memory"` (MCP-server enablement record).
- None of the `EPISODIC_MEMORY_*` env vars are set in settings hooks (defaults active: haiku summaries via Claude Code auth, default data dir).
- Tim's own global hooks in settings.json do NOT touch episodic-memory; SessionEnd runs `~/.claude/commands/sync-conversations.sh` — a **separate, parallel** conversation pipeline (→ §3.9).

---

## 3. Related Skills / Agents / References Across Tim's System

The plugin's own surface as it appears in sessions: skill `episodic-memory:remembering-conversations`, skill/command `episodic-memory:search-conversations`, agent `episodic-memory:search-conversations`, MCP tools `mcp__plugin_episodic-memory_episodic-memory__{search,read}`.

References found elsewhere (grep across `~/.claude/skills|commands|agents|CLAUDE.md`, `~/.vi/`, superpowers cache, memory files):

1. **`~/.claude/skills/agent-boot-sequence/SKILL.md`** — Step 2 of required initialization: "Search Episodic Memory" before asking Tim anything; boot report template cites episodic findings ("The episodic memory contains EVERY conversation where the system was designed").
2. **`~/.claude/skills/context-continuity/SKILL.md`** — description and Step 1 both mandate episodic search first; positions it as the cross-session thread-keeper.
3. **`~/.claude/skills/context-discovery/SKILL.md`** — hardest dependency: frontmatter `tools:` list names `mcp__plugin_episodic-memory_episodic-memory__search` and `__read` directly; Step 2 gives multi-concept query examples; includes an episodic-vs-Vi-Memory reconciliation table and query-pattern cheatsheet.
4. **`~/.claude/skills/composition-validator/SKILL.md`** — Step 6/Tools sections: search episodic memory for precedents of law/pattern application.
5. **`~/.claude/skills/locate-and-identify-conversations/SKILL.md`** — Step 1.1 "Use episodic memory search" with fallback to direct `~/.claude/projects` grep; notes "Archive is for episodic memory plugin… may need to stay in sync (unclear)".
6. **`~/.claude/skills/subagent-orchestration/SKILL.md`** — lists episodic memory as a standard subagent tool/source ("conversation timestamps for episodic memory"; Phase-1 discovery source alongside Supabase/docs/Vi graph).
7. **`~/.claude/skills/system-mapping-discovery/SKILL.md`** — Phase A Step 3: search episodic memory for past discussions of the system being mapped; Tools section names remembering-conversations.
8. **`~/.claude/skills/capability-enhancement/SKILL.md` + `future-enhancements.md`** — uses the plugin as the canonical example of capability framing; future-enhancement idea: "Hook: Topic detection and episodic search".
9. **Tim's SessionEnd pipeline (PARALLEL system, not the plugin)** — `~/.claude/settings.json` SessionEnd → `~/.claude/commands/sync-conversations.sh` → `~/.claude/sync-conversations-to-supabase.py`: uploads the same `~/.claude/projects` JSONLs to a Supabase `conversation-archives` Storage bucket + `conversation-sync` Edge Function. Plus skill `~/.claude/skills/sync-conversations/SKILL.md` (manual trigger). Same source, different sink — the Company already has a second conversation-ingestion lane to reconcile with.
10. **`~/.config/superpowers/lobe-importer.py`** — Tim-custom importer proving non-Claude sources can be written into the archive format (§2.1).
11. **Memory directive — `~/.claude/projects/-home-tim/memory/feedback-no-episodic-memory.md`** — **the controlling instruction**: Tim (2026-06-09): "Don't use episodic memory — by comparison it sucks." Do NOT use the plugin's agent/tools for recall; the Company corpus + spaces + transcript-miner + file-memory supersede it. This inventory therefore serves the *clone-and-adapt* purpose (mining its mechanics for the Company substrate), not continued use.
12. **Superpowers plugin cache** (`…/superpowers-marketplace/superpowers/`) — zero references to episodic memory (clean separation; the two plugins only share the `~/.config/superpowers` directory name convention and marketplace).
13. **`~/.vi/`** — no references found.
14. Self-referential: archive/index contain 1,580 conversations from sessions run inside the plugin's own directory (project `-home-tim--claude-plugins-cache-superpowers-marketplace-episodic-memory-1-0-15`), and `~/.claude/projects/-home-tim--claude-plugins-cache-superpowers-marketplace-episodic-memory-1-0-15` exists.

---

## 4. Adaptation Seams (for the Company fork)

### 4.1 Embedding provider — the #1 seam
- **Observed**: the entire embedding surface is `src/embeddings.ts` (47 lines, 3 functions). Model ID is one hardcoded string (line 10); contract is `text → number[384]`. Consumers: indexer/sync call `generateExchangeEmbedding`, search calls `generateEmbedding`. Dimension is duplicated in `db.ts:99` (`FLOAT[384]`).
- **Inferred (not executed)**: swapping in the Company's local embedding server (jina-v4 / the vLLM-embed stack) means replacing one module + parameterizing the vec0 dimension — every other file is agnostic to where vectors come from. A registry-driven model choice (per Tim's registry-is-truth law) would also need a stored-model tag per row to handle mixed indexes; upstream v1.2.0's `embedding-migration.ts` (re-embed in batches of 500 with stale-tagging, lock-guarded) is a ready-made pattern for exactly that and is worth porting wholesale.
- Note the asymmetric-prefix upgrade in v1.4.2 embeddings.ts (query-side instruction prefix for BGE) — the seam grew a query/document asymmetry; an adapter should preserve that split (`generateEmbedding` for docs vs a query-specific function).

### 4.2 Storage — SQLite → anything
- **Observed**: all SQL lives in `db.ts`, `search.ts`, `stats.ts`, plus one `SELECT COUNT(*)` in `indexer.ts:295` and verify.ts helpers. No ORM, no repository layer — a fork to Supabase/pgvector means rewriting ~5 files' queries, not untangling the domain logic (types.ts is storage-free).
- **Observed**: WAL mode + same-DB concurrent background syncs is the known fragility (upstream added a file lock in 1.4.2 #97; 1.0.15 has none — on this multi-session machine that race is live today).
- **Inferred**: the dual-write (exchanges row + vec_exchanges row, DELETE+INSERT) is the consistency hot spot — the live DB's 75,375 vs 75,374 off-by-one confirms it's non-atomic. pgvector would collapse it to one row.

### 4.3 Conversation source — where JSONLs come from
- **Observed**: source dir convention is `~/.claude/projects` in exactly two places — `indexer.ts:20` (`getProjectsDir`, env-overridable via `TEST_PROJECTS_DIR` only) and `sync-cli.ts:61` (hardcoded `path.join(os.homedir(), '.claude', 'projects')`). The JSONL record shape the parser expects is the Claude Code transcript schema (`type/message/timestamp/uuid/parentUuid/isSidechain/sessionId/cwd/gitBranch/version/thinkingMetadata`).
- **Observed**: archive format is just "the same JSONL, copied" — `lobe-importer.py` proves arbitrary sources can be transformed in. Upstream 1.3.0 added a whole second source (Codex rollout transcripts) behind `codex-support.ts`, demonstrating the parser seam is forkable per-source.
- **Inferred**: for the Company, "source" generalizes to any conversation-shaped stream (Vi Chat threads, voice debriefs); the exchange state machine in parser.ts is the part to keep, the JSONL field-mapping the part to swap.

### 4.4 Summarization — already pluggable
- **Observed**: fully env-parameterized (model, fallback, base URL, token, timeout — summarizer.ts:16-32, README table) and architecturally optional (`--no-summaries`, `skipSummaries`); search degrades gracefully (summary only enriches results). Sidecar-file storage means summaries are independent of the DB.
- **Inferred**: pointing `EPISODIC_MEMORY_API_BASE_URL` at a local Anthropic-compatible endpoint (or replacing `callClaude` with a Company role-run) is a one-file change. The hierarchical chunk-then-synthesize pattern (8-exchange chunks) is reusable as-is. Beware the recursion class fixed upstream (1.1.2 `EPISODIC_MEMORY_SUMMARIZER_GUARD`): summarizing via an agent harness that itself fires session hooks is a fork-out cascade — 1.0.15 has no guard.

### 4.5 Hardcoded vs configurable (1.0.15)

| Configurable (env/file) | Hardcoded |
|---|---|
| Data root (`EPISODIC_MEMORY_CONFIG_DIR` etc., paths.ts:24-41) | Embedding model ID (embeddings.ts:10) |
| DB path (`EPISODIC_MEMORY_DB_PATH`) | Vector dim 384 (db.ts:99) |
| Excluded projects (env / exclude.txt) | 2,000-char embed truncation (embeddings.ts:22) |
| Summarizer model/fallback/endpoint/token/timeout | Source dir `~/.claude/projects` (sync-cli.ts:61) |
| Summary cap per sync (code default 10, opt only via API) | Chunk strategy (1 exchange; chunks of 8 for summaries) |
| Concurrency 1-16, `--no-summaries` | Exclusion marker strings (sync.ts:6-10) |
| | Snippet length 200, summary-display cutoff 300 |
| | Archive sidecar convention `-summary.txt` |
| | MCP tool names/descriptions; agent model `haiku` |

### 4.6 Test protection for a fork
- **Observed**: 11 test files / 1,608 lines, real-data fixtures, and clean env-based injection points (`EPISODIC_MEMORY_DB_PATH`, `TEST_ARCHIVE_DIR`, `TEST_PROJECTS_DIR`) — sync, parser, verify, multi-concept semantics, and the agent-prompt template are all regression-protected, which directly covers the riskiest adaptation surfaces (chunking, incremental copy, repair).
- **Observed gaps**: nothing pins the embedding model output (a model swap silently changes all rankings — add a golden-similarity test), no MCP protocol-level test, no hook/integration test, summarizer SDK path untested. Upstream 1.1.1 added version-consistency tests; 1.4.x added doctor + E2E scripts — worth porting.

### 4.7 Misc seams worth knowing
- **MCP `read` has no path guard** (mcp-server.ts:251-275) — reads any file; constrain in a fork.
- **Date filters string-interpolated** into SQL (search.ts:43-45) — regex-validated, but parameterize anyway.
- **Text search is `LIKE '%…%'`**, a full scan on a 75K-row/10 GB table — on this machine that is the slow path; FTS5 (or pg trigram) is the obvious upgrade and the docs already (incorrectly) promise it.
- **tool_calls is 6.7M rows of write-only data** (results never captured, table never queried by search — only formatResults shows counts when toolCalls happen to be populated on the in-memory object, which the search read-path never does. **Observed**: `searchConversations` never loads tool_calls; the "Tools:" line in formatResults is dead in practice for search results). A fork can drop or radically slim this table — likely several GB of the 10.87.
- **Exclusion is marker-in-content** — clever (works from inside any conversation) but a full-file string scan per sync; the Company equivalent likely wants address/tag-based exclusion.
- **The agent/skill layer is the proven UX**: dispatch-cheap-model → synthesize → sources-with-line-pointers is the pattern Tim's own skills already assume (§3) and is independent of all the plumbing above.

---

## 5. Upstream v1.0.15 → v1.4.2 Delta (fresh clone at `/home/tim/episodic-memory/`)

Cheap structural comparison only (tree diff + CHANGELOG + spot reads); the installed 1.0.15 remains this inventory's subject.

- **Size**: src grows 3,612 → 5,719 lines. New modules: `codex-support.ts`, `codex-hook-trust.ts`, `doctor.ts`/`doctor-cli.ts`, `embedding-migration.ts`, `file-lock.ts`, `logging.ts`, `summary-sentinel.ts` (+ generated `version.ts` mechanism).
- **New dirs**: `.codex-plugin/` + `.agents/plugins/` (native OpenAI **Codex** plugin packaging — cross-harness: parses/indexes Codex rollout transcripts alongside Claude's), `docs/superpowers/`, root `CLAUDE.md`.
- **Removed**: `commands/search-conversations.md` (slash command deleted in 1.4.0 — skill+agent auto-dispatch is the only intended path now).
- **Embedding model upgraded (1.2.0)**: `Xenova/bge-small-en-v1.5` replaces all-MiniLM-L6-v2 (same 384 dims; measured rank-1 retrieval 47%→53%, top-10 68%→75% on a 17K-exchange production test). Ships **background self-migration**: each sync re-embeds 500 stale rows (`EPISODIC_MEMORY_MIGRATION_BATCH` to speed up), crash-safe, rollback-safe. Query embeddings get a BGE instruction prefix; document embeddings don't.
- **Hardening fixes a fork should inherit**: single-instance file lock for concurrent syncs (1.4.2 #97 — directly relevant to this multi-session machine); summarizer reentrancy guard `EPISODIC_MEMORY_SUMMARIZER_GUARD` stopping a recursive process explosion (1.1.2 #87/#88); summary error sentinels + retry threshold so failed files can't pin the 10-per-run queue forever (1.4.2 #96 — the exact mechanism behind this machine's 1,267/13,270 summary shortfall class); cross-project cwd summarization fix (1.4.2 #93); partial-node_modules detection in the MCP wrapper (#95).
- **hooks.json** now matches `startup|resume|clear` and uses `${PLUGIN_ROOT:-${CLAUDE_PLUGIN_ROOT}}` (no `async` flag).
- **Version discipline**: package.json as single version source, generated `src/version.ts`, manifest drift tests, `scripts/bump-version.sh`.
- **Inferred recommendation**: if the Company fork starts from code rather than from scratch, start from **v1.4.2** (the locking, sentinel, migration, and guard machinery is precisely the operational hardening a heavily-multi-session machine like this one needs), while treating the on-disk data produced by 1.0.15 (this DB/archive) as the migration corpus.

---

## 6. Loose ends / flags

- **vhdx-relevant**: 24 GB total (13 GB archive + 10.9 GB DB) under `~/.config/superpowers/` — if the plugin stays unused per the no-episodic-memory directive, this is the single biggest reclaimable blob after the Company adaptation harvests what it wants (the archive doubles as a complete, dated, per-project conversation corpus — likely valuable to the Company's own ingestion before any deletion decision).
- The SessionStart hook is **still firing today** (DB max timestamp = this morning) even though recall-side use is forbidden — collection continues, consumption stopped. Whether to keep collecting is a Tim decision once the Company lane covers the same ground.
- `search-log.jsonl` (11 entries, Oct 2025) has no writer in the 1.0.15 codebase — Inferred remnant of an earlier version; harmless.
