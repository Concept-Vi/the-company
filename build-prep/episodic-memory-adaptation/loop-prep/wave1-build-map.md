# Wave-1 BUILD-MAP — recollection (the lay of the land for the four codebases)

> **What this is.** The build-level map for *recollection* — Tim's episodic-memory clone/refit. Where the prior `reads/` answered *what each system does and intends*, this answers *where the code is and what we do to it to build*: per codebase, the relevant **file tree**, the **integration points/patterns** (file:symbol), and a **KEEP / MODIFY / REPLACE / HARVEST** disposition for every load-bearing piece. It builds ON `reads/1-5` (the spine, the store, substrate-mcp, conversation-intelligence, the fabric model layer) and the COMPLETE DESIGN in `../EPISODIC-UPGRADE-PLAN.md` — it does not re-explain them.
>
> **Governing frame (from the plan + Tim's standing directives).** recollection is a **clone-as-sibling PLUGIN** named "recollection": standalone NOW (own data dir, own skills/sub-agents, **same MCP tool names** as episodic-memory so it's a drop-in), but **built to be absorbable into the Company later** — so where a choice exists, it should MATCH a Company pattern (§B). Laws it inherits: **registry-is-truth / no-hardcoding** (everything grown), **no versioning** (update in place), **commit to main, no branches**, **fail-loud not silent**, and **bge-m3 has ZERO priority** (one loadout slot, not a ranked winner; embedder/loadout stays open).
>
> **Evidence convention** (Tim's CLAUDE.md): **Observed** = read directly in code/files this wave. **Inferred** = pattern-matched, not executed. **Verified** = ran it (no live execution this wave — no Verified claims). Two subagents supplied §B and §C-exact-locations; their findings are tagged where relied on.

---

## 0. THE FOUR CODEBASES AT A GLANCE (what recollection takes from each)

| Codebase | Path | Role for recollection | One-line disposition |
|---|---|---|---|
| **CLONE BASE** | `/home/tim/episodic-memory` (v1.4.2) | The **chassis** — the TS plugin we fork into "recollection" | KEEP the capture/sync/plugin skeleton; MODIFY the data dir + names + schema; REPLACE the embedder, the summarizer, and the flat-search target |
| **INTEGRATION TARGET** | `/home/tim/company` | The **patterns to match** so it's absorbable | No code lifted now; recollection's registries/MCP/store/model seams MIRROR the Company's (so a later fold-in is a re-point, not a rewrite) |
| **HARVEST: substrate-mcp** | `/home/tim/repos/obsidian-overlord` (`src/substrate_mcp/`) | The **metabolism** — state/temporal layer, reconcile, clustering, chunker | HARVEST (port to recollection's store): the state-asymmetry sensor, the resolver ladder, the k-means, the chunker |
| **HARVEST: conversation-intelligence** | `/home/tim/repos/Supabase` | The **rich target shape** — turn-context unit, provenance graph, parametric MCP | HARVEST (designs, not schema verbatim): turn-pair embedding, artifact-provenance graph, the dual-granularity registry, the parametric-tool/envelope house style |

---

# A. CLONE BASE — `/home/tim/episodic-memory` (v1.4.2)

The thing we fork. **TypeScript** plugin (Node, ESM), compiled `src/` → `dist/` by `tsc + esbuild`; **both committed**. Backend = **SQLite + sqlite-vec** (`better-sqlite3`), **local ONNX embeddings** via `@huggingface/transformers`, **MCP server** over stdio (`@modelcontextprotocol/sdk`), summaries via the **Claude Agent SDK** (cloud). All paths below are absolute under `/home/tim/episodic-memory`.

## A.1 — The file tree (relevant set, with sizes + disposition)

**Observed** (full tree + `wc -l` read this wave). `dist/` (committed build output) and `test/` (28 spec files) omitted from the table — they regenerate / are the executable spec.

```
/home/tim/episodic-memory/
├── package.json                     (2.1KB)  name/bin/deps/build       → MODIFY (rename → recollection)
├── .claude-plugin/
│   ├── plugin.json                  manifest: name, agents[], mcpServers → MODIFY (rename, own data dir)
│   └── marketplace.json             install registry entry             → MODIFY (rename) [or DROP if not published]
├── .codex-plugin/plugin.json        codex variant manifest             → KEEP (or DROP — codex unused by Tim)
├── .mcp.json                        dev MCP launch + env_vars allowlist → MODIFY (env var names → RECOLLECTION_*)
├── hooks/hooks.json                 SessionStart → `sync --background`  → MODIFY (cmd path) + EXTEND (proactive inject, P8)
├── CLAUDE.md                        the repo's own build conventions    → KEEP-as-reference / MODIFY for recollection
├── src/   (5,719 lines TS)
│   ├── paths.ts            (167)  config/index/archive dir resolution   → MODIFY ★ (own data dir survives updates)
│   ├── db.ts               (307)  schema + migrations + insert/query    → MODIFY ★ (extend schema; keep tables)
│   ├── embeddings.ts        (88)  ONNX bge-small-384 encoder pipeline    → REPLACE ★ (→ fabric multi-lens)
│   ├── embedding-migration.ts (137) version-stamped re-embed engine      → KEEP-pattern, MODIFY (drives lens migration)
│   ├── parser.ts           (554)  JSONL → exchanges (Claude + Codex)     → KEEP+MODIFY (boundary rule is load-bearing)
│   ├── indexer.ts          (393)  full/session/unprocessed index flows   → MODIFY (re-point embed + distill)
│   ├── sync.ts             (237)  source→archive copy + index + summarize → MODIFY (the unified capture path, P10)
│   ├── sync-cli.ts         (184)  sync command + reentrancy guard         → KEEP (guard is load-bearing)
│   ├── search.ts           (431)  sqlite-vec KNN + text + multi-concept   → MODIFY/REPLACE (flat→gather/judge, P3/P4)
│   ├── summarizer.ts       (594)  Claude Agent SDK calls (cloud)          → REPLACE ★ (→ local fabric distill, P5)
│   ├── summary-sentinel.ts  (76)  retry/error sentinel for summaries      → KEEP (good resumability pattern)
│   ├── show.ts            (1025)  JSONL → markdown/html render            → KEEP (the `read` tool body)
│   ├── mcp-server.ts       (331)  MCP tool surface (search, read)         → MODIFY ★ (keep names; add P7 axis tools)
│   ├── file-lock.ts         (95)  PID-liveness file lock                  → KEEP (cross-process safety)
│   ├── types.ts             (57)  ConversationExchange / ToolCall shapes  → MODIFY (add unit/link/fingerprint types)
│   ├── verify.ts           (193)  index integrity check                   → KEEP
│   ├── doctor.ts / doctor-cli.ts   integration diagnostics                → KEEP (+ extend for fabric/embedder health)
│   ├── stats.ts / stats-cli.ts     index statistics                       → KEEP
│   ├── codex-support.ts / codex-hook-trust.ts  codex harness glue         → KEEP (or DROP — see A.6)
│   ├── constants.ts / logging.ts / index.ts / *-cli.ts                    → KEEP (plumbing)
│   └── version.ts          GENERATED (gitignored)                         → KEEP mechanism
├── cli/   (492 lines JS — thin Node wrappers, no bash)
│   ├── episodic-memory.js  (112)  umbrella dispatcher (sync/index/search/show/stats/doctor) → MODIFY (rename bin)
│   ├── mcp-server-wrapper.js (124) ensures deps installed, launches dist/mcp-server.js       → KEEP+MODIFY (path)
│   ├── install-check.js     (40)                                          → KEEP
│   └── *.js                 subcommand entry points                       → MODIFY (rename)
├── skills/remembering-conversations/{SKILL.md, MCP-TOOLS.md}              → KEEP+MODIFY (recollection's own skill, P-surface)
├── agents/search-conversations.md  (5.7KB) the deep-recall sub-agent      → KEEP+MODIFY (becomes the P4/P8 looping sub-agent)
├── prompts/search-agent.md  (5.2KB) sub-agent prompt                      → MODIFY
└── scripts/   bump-version.sh, generate-version.js, postinstall.js, *-e2e.js → KEEP (release plumbing)
```

★ = the highest-leverage touch points, detailed below.

## A.2 — The data-dir / naming refit (the "own data dir survives plugin updates" requirement)

**Observed — `src/paths.ts`.** All paths funnel through **`getSuperpowersDir()`** (`paths.ts:91`), which resolves (in precedence order) `EPISODIC_MEMORY_CONFIG_DIR` → `PERSONAL_SUPERPOWERS_DIR` → `$XDG_CONFIG_HOME/superpowers` → `~/.config/superpowers`. Everything else hangs off it:
- `getArchiveDir()` → `<superpowers>/conversation-archive` (`paths.ts:113`)
- `getIndexDir()` → `<superpowers>/conversation-index` (`paths.ts:125`)
- `getDbPath()` → `<indexDir>/db.sqlite` (`paths.ts:132`)
- `getExcludeConfigPath()` → `<indexDir>/exclude.txt` (`paths.ts:144`)

**MODIFY:** introduce a single `getRecollectionDir()` resolving `RECOLLECTION_DATA_DIR` → `~/.recollection` (NOT under `superpowers/`, NOT under the plugin cache). The whole point (Read 1 §D durability risk): episodic-memory's DB lives under `~/.claude/plugins/cache/.../episodic-memory/<version>/` and **a plugin update relocates it**. recollection's own dir under `~/.recollection` makes the corpus survive updates — this is the plan's "own data dir survives plugin updates" requirement. Every `get*Dir()` re-roots there. Env-var names in `.mcp.json:env_vars` and `paths.ts` rename `EPISODIC_MEMORY_*` → `RECOLLECTION_*` (keep test overrides `TEST_*`).

**Manifest renames (MODIFY):** `package.json:name+bin`, `.claude-plugin/plugin.json:name+mcpServers.<key>`, `.claude-plugin/marketplace.json:plugins[0].name`. The MCP server **name string** in `mcp-server.ts:124` (`new Server({name:'episodic-memory'...})`) — DECISION: the plan says "same MCP tool *names*" (the `search`/`read` *tools*), not necessarily the server id; keep tool names identical for drop-in, rename the server id to `recollection`.

## A.3 — The DB schema + where it's defined (MODIFY — extend, don't rebuild)

**Observed — `src/db.ts`.** `initDatabase()` (`db.ts:107`) creates 3 tables + a vec virtual table and runs `migrateSchema()` (the **additive ALTER-TABLE migration list**, `db.ts:9-45`):
- **`exchanges`** (`db.ts:125-152`) — 23 columns incl. `id, project, timestamp, user_message, assistant_message, archive_path, line_start, line_end, embedding BLOB, session_id, cwd, git_branch, is_sidechain, harness, model, thinking_*, embedding_version`.
- **`tool_calls`** (`db.ts:158-169`) — `id, exchange_id FK ON DELETE CASCADE, tool_name, tool_input (JSON str — THE artefact-address field), tool_result (★ 100% NULL today), is_error, timestamp`.
- **`vec_exchanges`** (`db.ts:172-177`) — `vec0(id TEXT PK, embedding FLOAT[384])` — **the 384-dim hard-coded space** (the dim-incompat the merge must resolve, Read 2 §3 / Read 5 §6).
- Indexes (`db.ts:183-206`): `idx_timestamp, idx_session_id, idx_project, idx_harness, idx_sidechain, idx_git_branch, idx_tool_name, idx_tool_exchange`. **No index on `archive_path` or on `tool_input.file_path`** (Read 1 §A.7 join-perf note).

**MODIFY plan (Observed disposition):**
- **KEEP** `exchanges` + `tool_calls` as the **atoms/bedrock** (the plan's "Atoms = events on a timeline — raw bedrock, nothing lost"). The additive-ALTER pattern (`migrations[]`) is exactly the Company's schema-additive law — KEEP it, append new columns rather than rewrite.
- **ADD** the plan's `units` registry (typed multi-scale units), `links` (provenance graph: containment + crossings + semantic edges), and **multi-coordinate fingerprints** (many vectors per unit). The 384-dim `vec_exchanges` becomes **one of N lens spaces**, not the only one — so either widen to per-lens vec tables (`vec_<lens>` with the lens's dim) or move vectors to the Company-style space-keyed store (§B.3). **Tim's directive: no ranking, full lens-set; bge-m3 has zero priority** — so the schema must NOT bake one dim in.
- **`tool_result` stays LAZY** (plan P6: "tool_results kept LAZY — keyed, fetched on demand, not distilled"). Today it's NULL anyway; recollection keys it and fetches on demand rather than distilling it.
- The exchange **id** = `md5(archivePath:userLine-lastAssistantLine)` (`parser.ts:117-120`) — a **content/position hash**, NOT the transcript UUID. This is the join-key reconciliation risk Read 1 §B.1 / Read 2 flagged: the Company addresses by `exchange://<sid>/<i>` (positional `i`). **The bridge is `(session_id, line_start..line_end)`** — both present here (`exchanges.session_id`, `line_start`, `line_end`) — so recollection should carry a canonical `exchange://<sid>/<i>` address alongside the md5 id, computed by its own deterministic walk, to be Company-compatible (§B.3c).

## A.4 — The embedder swap point (REPLACE ★)

**Observed — `src/embeddings.ts` (88 lines, the entire embedder).** Hard-coded: `MODEL_ID='Xenova/bge-small-en-v1.5'`, `MODEL_DTYPE='q8'`, **384-dim**, mean-pooled + normalized, 2000-char truncation, BGE query-prefix asymmetry. Three entry points everything calls:
- `initEmbeddings()` — loads the ONNX pipeline (`embeddings.ts:26`).
- `generateExchangeEmbedding(userMessage, assistantMessage, toolNames?)` — the **document** embed; builds `"User: …\n\nAssistant: …\n\nTools: …"` (`embeddings.ts:75-88`). *(Note: this is already a primitive turn-pair text — CI's turn-context idea, §C-B1, is the richer version of this exact concatenation.)*
- `generateQueryEmbedding(query)` — prepends the BGE prefix (`embeddings.ts:71`).

Callers (the swap blast-radius, Observed): `sync.ts:148,166`, `indexer.ts:6,163,252,382`, `embedding-migration.ts` (via injected `embedFn`), `search.ts` (query side).

**REPLACE:** swap the ONNX in-process encoder for **calls to a model service** (the plan's multi-lens fingerprinting, P2). recollection is a TS plugin and the Company embedder is an **OpenAI-compatible `/v1/embeddings` endpoint** (bge-m3 @ :8001, AND the bigger qwen3-embedding-8B tier — Read 5 §1.5). So `embeddings.ts` becomes a thin **OpenAI-embeddings client** (the exact call shape is in substrate-mcp's `OpenAIEmbedder`, §C-A5 — harvest it). Critically: the plan's fingerprints are **multi-coordinate** (steerable-dense Qwen3-Embedding, sparse bge-m3, code nomic+ColGrep, visual, context-aware), so `embeddings.ts` becomes a **lens dispatcher** keyed by a **registry** (no hardcoded model) — `generateEmbedding(text, lens)` resolving the model per lens. The `embedding_version` mechanism (§A.5) generalizes to per-lens versioning. **The encoder choice is open** (Tim: full lens-set, no winner) — recollection reads the loadout from a registry, matching the Company fabric registry (§B.4).

## A.5 — The version-stamped re-embed engine (KEEP-pattern, MODIFY)

**Observed — `src/embedding-migration.ts`.** `EMBEDDING_VERSION` const (bumped when the pipeline changes) + `pickStaleBatch()` (rows where `embedding_version < EMBEDDING_VERSION`, joined to tool names) + `recordReembedded()` (atomic vec replace + version stamp) + `runMigrationBatch()` (lock-protected, resumable, batch). This is a **clean incremental re-embed engine** and it's exactly what the merge needs to re-embed the ~13k-conv backfill at fabric grade (Read 5 §A: "re-embed is a phase"). KEEP the engine; MODIFY so the "version" is **per-lens** (each lens space has its own version watermark) — re-embedding one lens doesn't touch the others. This is also the **dim-migration lever** Read 5 §6 names.

## A.6 — The capture/sync path (MODIFY — the unified pluggable capture, P10)

**Observed — `src/sync.ts` + `src/indexer.ts` + `src/paths.ts`.** The capture pipeline:
1. `getConversationSourceDirs()` (`paths.ts:39`) → `[~/.claude/projects, ~/.claude/transcripts, ~/.codex/sessions]` (those that exist). **This is the only source list** — P10's "all CC sessions incl. sidechains, all projects, open to non-CC sources" means EXTEND this to be a pluggable source registry.
2. `findJsonlFiles(dir, excludedDirNames)` (`paths.ts:61`) — recursive, can exclude nested `subagents/` dirs. **Sidechain handling:** the parser carries `is_sidechain` (from the transcript), but episodic-memory's live sync **excludes `agent-*.jsonl`** (Read 4 Lane A; and the SessionStart hook). **Plan P10 wants sidechains INCLUDED** → MODIFY to capture them (they're agent-internal turns = build provenance).
3. `syncConversations(sourceDir, destDir, options)` (`sync.ts:71`) — `copyIfNewer` (mtime-gated atomic copy, `sync.ts:37`) → parse → embed → `insertExchange` → optionally summarize. Exclusion markers (`sync.ts:7-11`) let a transcript opt out.
4. `indexUnprocessed()` (`indexer.ts:275`) — the **incremental high-water-mark** flow: `MAX(line_end) WHERE archive_path=?` resumes append-only transcripts (`indexer.ts:319-336`). KEEP — this is the live-streaming backbone.
5. **Reentrancy guard** (CLAUDE.md + `sync-cli.ts`): the SessionStart hook runs `sync --background` which calls the summarizer (a Claude subprocess) which fires SessionStart again → fan-out. Guarded by `EPISODIC_MEMORY_SUMMARIZER_GUARD=1`. **KEEP this guard** (rename env) — and note REPLACING the summarizer with a local fabric call (§A.7) **removes the recursion source entirely** (a local HTTP call doesn't spawn a CC subprocess), which is a side-benefit, but keep the guard for defence-in-depth.

**Disposition: MODIFY** sync/indexer to (a) pluggable source registry, (b) include sidechains, (c) the backfill path bootstraps from episodic-memory's existing ~13k-conv archive (the plan's "head-start"), (d) re-point embed → fabric multi-lens and distill → local fabric.

## A.7 — The summarizer (REPLACE ★ — cloud → local fabric, P5 distill)

**Observed — `src/summarizer.ts` (594 lines).** Calls the **Claude Agent SDK `query()`** (cloud Sonnet, with a `gpt-5`/Codex fallback path) to write a per-conversation summary. This is the single biggest **architectural** mismatch with the Company: the Company's distillation is the **resident local 4B swarm** (`mine_exchange` role via `run_items` map → `run_reduce`, Read 5 §2). **REPLACE** the SDK summarizer with calls into the local fabric (the plan's P5: 3 layers — summary · structured extraction · rollups, all grown/non-hardcoded). For recollection-standalone this is an **OpenAI-compatible chat call to the resident 4B** (services.json `chat-4b` @ :8000); for the absorbed form it becomes `run_items(mine_exchange, …)` directly (§B.5). The structured-extraction layer mirrors `roles/mine_exchange.py`'s `{decision, rationale, tim_correction, my_error, bug_fix, needs_tim, frustration, pattern_tag}` output schema (Read 5 §2.3). **No cloud dependency in the steady state** (matches "everyday lenses co-reside locally").

## A.8 — The MCP server + its tools (MODIFY ★ — keep names, add axis tools, P7)

**Observed — `src/mcp-server.ts` (331 lines).** Stdio server, FLAT two tools: **`search`** (single string OR 2-5 concept array; modes vector/text/both; filters after/before/project/session_id/git_branch; response_format markdown/json) and **`read`** (path + optional startLine/endLine). Zod-validated, `readOnlyHint:true`. `search` delegates to `searchConversations`/`searchMultipleConcepts` (`search.ts`), `read` to `formatConversationAsMarkdown` (`show.ts`).

**Search internals (Observed — `search.ts`):** sqlite-vec KNN — `WHERE vec.embedding MATCH ? AND k = ?` then `ORDER BY vec.distance ASC` (`search.ts:155-191`), L2→cosine via `l2DistanceToCosineSimilarity` (`search.ts:116`), metadata-filter over-fetch (`k = limit*3` when filtered).

**Disposition:** **KEEP the tool names `search` + `read`** (the drop-in requirement — Tim's agents already call these). **MODIFY** the bodies to back onto the new gather→judge machine (P3/P4) instead of flat KNN, and **ADD** the P7 axis-addressed parametric tools. **Per Tim's MCP-is-top-priority + the Company house style (§C-B4), the new tools should be PARAMETRIC** (one resource, an `op`/`scope`/`axis` selector + return-format `summary|content|stats|addresses`), not flat-one-per-op. This is the CI parametric-tool design (§C-B4) applied here. recollection runs its **own MCP server** while standalone; on absorption the tools refold as `mcp_face/tools/recollection.py:register(mcp, suite)` (§B.2).

## A.9 — Clone-base KEEP / MODIFY / REPLACE summary (the headline)

- **KEEP (chassis — works, reuse as-is or with renames):** the **plugin skeleton** (`.claude-plugin/plugin.json` manifest shape, `hooks/hooks.json` SessionStart wiring, `cli/` dispatcher + `mcp-server-wrapper.js`), the **capture incrementality** (`indexer.ts` high-water-mark, `sync.ts` copyIfNewer, `summary-sentinel.ts` retry, `file-lock.ts`), the **`exchanges`+`tool_calls` atom tables** + the additive-ALTER migration pattern (`db.ts`), the **`read`/`show.ts` render**, the **version-stamped re-embed engine** (`embedding-migration.ts`), `verify.ts`/`stats.ts`/`doctor.ts`, the **reentrancy guard**, and **the two MCP tool names** `search`+`read`.
- **MODIFY (refit to recollection + Company shape):** **`paths.ts`** → own data dir `~/.recollection` (survives plugin updates) + `RECOLLECTION_*` env vars; the **manifests/package.json** → rename; **`db.ts`** → ADD units/links/multi-lens-fingerprint schema, demote `vec_exchanges` 384 from sole space to one lens, carry `exchange://<sid>/<i>` addresses; **`sync.ts`/`indexer.ts`** → pluggable source registry, include sidechains, backfill from the ~13k archive; **`mcp-server.ts`** → keep names, add parametric P7 axis tools backed by gather→judge; **`hooks/hooks.json`** → add proactive-injection floor at session-start (P8); the **skill + sub-agent** (`skills/remembering-conversations/`, `agents/search-conversations.md`) → recollection's deep-recall sub-agent.
- **REPLACE (architectural mismatch — rip out and rebuild on local fabric):** **`embeddings.ts`** (in-process ONNX bge-small-384 → registry-driven multi-lens OpenAI-compatible fabric embeddings, no hardcoded model/dim); **`summarizer.ts`** (cloud Claude Agent SDK → local resident-4B fabric distill, the P5 3-layer mining); **`search.ts`** flat KNN target → the P3 gather + P4 judge machine (flat search becomes one degenerate path, not the whole story).
- **DECISION/DROP (open for Tim):** `codex-support.ts`/`.codex-plugin/` (Codex harness — Tim doesn't use Codex; KEEP costs little, DROP simplifies); `marketplace.json` (only if recollection is published to a marketplace — likely DROP for a private sibling).

---

# B. INTEGRATION TARGET — `/home/tim/company` (patterns to MATCH)

No code is lifted from the Company. recollection is standalone, but every extension seam should **mirror** the Company's so a later fold-in is a re-point, not a rewrite. Source: subagent map of the constitutions + bodies (Observed unless tagged). **The Company has NO `.claude-plugin` manifest** — it's file-discovered registries + one MCP server (Observed, negative result), so recollection's "absorb" target is *registry dirs + a `register(mcp, suite)` tool module + a constitution AGENTS.md*, not a plugin manifest.

## B.1 — Node-type registration (the self-modifying registry pattern)
- **Registry:** `/home/tim/company/runtime/registry.py:NodeRegistry` — `discover(dirs)` does file-discovery + `importlib`; a module is a node iff it `hasattr "run"`; **id = filename stem**; `rediscover()` rebuilds (revert a file → it un-registers). **Observed.**
- **Contract:** a `nodes/<id>.py` declares module-level `VERSION, KIND, PORTS_IN, PORTS_OUT, CONFIG, def run(inputs, config)` (+ `VOLATILE=True` if it reads mutable truth). Typed by `/home/tim/company/contracts/node_type.py:NodeType`. `CONFIG` dropdowns pull from the live registry via `"options_from"` (e.g. `embed_models`) — **never hand-typed**. Example: `/home/tim/company/nodes/embed.py`. **Observed.**
- **Self-modification flow:** `runtime/suite.py:9374 propose_node(name, spec, model=None)` — the brain WRITES a new node module from an NL spec, then **surfaces it for operator approval** (`inbox.surface("code_build", …, default="reject")`) — does NOT apply. `suite.py:9410 apply_node(surfaced_id)` — writes the file atomically, `_commit_or_rollback` (git-revertible), `registry.discover()` to make it live; **authorization is READ from the substrate** (`confirmed=self.inbox.is_approved(...)`) — the proposing agent can't self-approve. Generalized to `propose_role`/`apply_role` (`suite.py:9478`). **Observed.**
- **recollection match:** recollection's "the system grows its own memory-node / extraction-lens" path (the plan's "everything grown, non-hardcoded") routes through this propose→surface→approve→commit→rediscover shape, never write-and-activate. **Inferred (the absorption mapping).**

## B.2 — MCP tool/verb exposure (parametric, one verb many ops)
- **Mechanism:** `/home/tim/company/mcp_face/server.py:33-36` — one `FastMCP("company")` server; `pkgutil.iter_modules` over `mcp_face/tools/` and calls each module's **`register(mcp, SUITE)`**. Adding a resource = adding a file. **Observed.**
- **Law:** `mcp_face/AGENTS.md` — *"verbs are generic over node-type — there is no tool-per-node-type… adding a node-type/model/source adds zero tools. Never: add a tool per node-type."* **Observed.**
- **Example:** `mcp_face/tools/node.py:register` defines ONE `node(op: Literal["create","delete","propose","apply"], …)` — the `op` selector replaces 4 flat tools; governance floor stays inside the Suite methods, wrapper just routes. Closest analogs to a recollection tool: `mcp_face/tools/corpus.py` and `mcp_face/tools/marks.py` (**not body-read this wave — flagged for the drafting wave**). **Observed.**
- **recollection match:** recollection exposes its memory ops as **one parametric verb** (e.g. `recall(op=…, scope=…, axis=…, return_format=…)`) — matching this house style AND the CI parametric design (§C-B4). Standalone = its own server; absorbed = `mcp_face/tools/recollection.py:register(mcp, suite)`. **Inferred.**

## B.3 — The store / resolver (the addressed-record contract)
- **(a) Resolver Protocol** a backend must implement — `/home/tim/company/contracts/resolver.py:Resolver` (`@runtime_checkable`): `put_content, get_content, exists, set_ref, head, write_provenance, provenance, lineage, memo_get, memo_set` (10 methods). Vector + mark methods are **FsStore extensions beyond the Protocol**. **Observed.**
- **(b) Address grammar** — `/home/tim/company/contracts/address.py:SCHEMES = ("run","cas","blob","vec","ui","code","skill","context","session","cap")`. `run://<domain>/<intent>/<node>@<branch>#run=<id>` (mutable pointer); `vec://<source>#space=<proj>` (space-keyed embedding); `cas://<algo>:<hash>` (immutable). `Provenance` = `{address, content_hash, type, produced_by, inputs[], agent, created_at, schema_ver}`. **Observed.**
- **(c) Corpus record write** — `/home/tim/company/runtime/corpus.py:write_record(store, *, source_address, output, kind, lineage, model=None, projection=None, **extra)`. `REQUIRED_RECORD_FIELDS=("source_address","output","kind","lineage")`; **`LINEAGE_FIELDS=("session","round","project")` — fail-loud if any missing**. Deterministic logical address `corpus_address(source_address, project, projection)` → `run://corpus/<project>/<source_address>[/<projection>]`. **Observed.** This is the **direct analog of recollection's distilled-unit record** — and the lineage gate is recoverable for the ~13k backfill because episodic-memory archives per-session/per-project (Read 2 §5).
- **(d) Vectors** — `fs_store.py:space_address(source, space)` → `vec://{source}#space={space}` (`:916`); `put_vector(address, vector, content_hash, *, dim, model, space=None, source=None)` (`:927`, fail-loud: spaced entry must pass `source`); `get_vector` (`:965`); `index_corpus(space=None)` → `[{id, vector}]` (`:1004`); `ALL_SPACES` sentinel. **Observed.**
- **recollection match:** recollection's multi-lens fingerprints map **1:1** onto space-keyed vectors (`vec://<exchange>#space=<lens>`) — each lens IS a space; the dim contract is per-space, so **mixed-dim lens coexistence is legal** (Read 2 §3), satisfying Tim's "full lens-set, no winner". Standalone recollection stores these in its own SQLite (per-lens `vec_<lens>` tables); the **schema is written portable-by-field** (explicit `space`/`source`/`dim`/`model` columns) so the absorbed form maps to `put_vector(space=…)` unchanged. Distilled units ride the `write_record` shape with the 3-axis lineage. **Inferred (the mapping).**

## B.4 — Fabric model registry (declare models as data)
- **Declare a model:** a **service row** in `/home/tim/company/ops/services.json` (e.g. `chat-4b`: model/port/gpu_util/max_model_len/max_num_seqs/vram_mb) — owns deployment; **+** a **capability row** in `/home/tim/company/ops/model_capabilities.json` keyed by model-id (provides[]/tools/json_schema/context_ceiling/concurrency_knee) — owns intrinsic capability. Adding a model = ONE row each, no code. **Observed.**
- **Embed entry points:** `fabric/client.py:148 complete_embeddings(transport, inputs, model, dim=None, retries=3)` (dim-guarded, fail-loud); `runtime/cognition.py:386 embed_corpus_to_spaces(store, records, projections, *, embed_fn, dim, model, base_url)` (batch, space-keyed, incremental). Defaults `DEFAULT_EMBED_URL=http://localhost:8001/v1`, `bge-m3`, `dim=1024` (`fabric/config.py`). **Observed.**
- **Capability query:** `ops/cli/capabilities.py:273 suitable_models(requires)` (provides ⊇ requires); `runtime/suite.py:10210 models_for_role(requires)`. **Resource-manager:** `ops/cli/capabilities.py:407 ensure_resident(model_or_service, *, evict=False, wait=True)` → returns `{action: already-resident|loaded|evicted-and-loaded|swap-approval-needed}` (G14 ASK never silent-evicts). **Observed.**
- **recollection match:** standalone recollection talks to the SAME endpoints (bge-m3/qwen3-embed @ :8001, chat-4b @ :8000) as **OpenAI-compatible HTTP** — so its embedder/distiller clients are thin and the **model is read from a registry, never hardcoded** (the §A.4/§A.7 REPLACEs). Absorbed, those calls become `complete_embeddings`/`embed_corpus_to_spaces`/`run_role`. The loadout (which lens-models co-reside) is a registry choice — **Tim's open decision**, matching the mode→loadout registry. **Inferred.**

## B.5 — Cognition map/reduce (the distill/consolidate seams)
- `runtime/cognition.py:1139 run_items(role, items, store, *, turn_id, budget, …)` — MAP: fan ONE role over N units concurrently, per-unit resilient, writes `run://<turn>/<role>/<i>`. **Observed.**
- `cognition.py:203 run_role(role, ctx, …)` — one resident-model request → validated JSON. **Observed.**
- `cognition.py:1933 run_reduce(addresses, store, *, turn_id, mode, …)` — REDUCE: `mode="role"` (synthesize via model), `mode="rule"` (deterministic, no model), **`mode="cluster"`** (embed each + cosine-group, `cluster_threshold=0.85`, reuses `nodes/retrieve._cosine`). **Observed.**
- `cognition.py:736 SlotBudget.from_registry(service_id="chat-4b", …)` — swarm width from live registry. **Observed.**
- **recollection match:** the plan's **DISTILL (P5)** is `run_items(mine_exchange, [..exchanges..])`; **HEALTH/consolidation dream-phase** is `run_reduce(mode="cluster")` (dedup/merge) + `mode="role"` (synthesize). recollection-standalone reimplements a thin map/reduce over its SQLite; absorbed, it **calls these** rather than reimplementing. **This is also where substrate-mcp's k-means (§C-A2) and the Company's `mode="cluster"` converge** — both are the consolidation primitive; recollection picks one (the Company's is already store-integrated). **Inferred.**

## B.6 — Skills, hooks, laws
- **Skills:** `/home/tim/company/skills/<id>.py` with module-level `SKILL = {id, content, …}` (id = file stem), discovered by `runtime/skills.py:SkillRegistry`, addressable `skill://<id>`. Contexts mirror at `/home/tim/company/contexts/`. **Observed.**
- **Hooks:** `/home/tim/company/.claude/settings.json` (standard CC hooks block); scripts in `/home/tim/company/ops/hooks/`. **Observed.** recollection's standalone hooks stay in `hooks/hooks.json` (the clone-base shape, §A.6); absorbed, they move to the settings.json block.
- **Laws to obey (Observed, quoted):** `AGENTS.md:28` *"Author from the registry; never invent… If something you need isn't registered, ASK the operator rather than fabricate."*; `AGENTS.md:23` *"One source. A node-type is defined once → UI, runtime, and tools all project from it."*; `store/AGENTS.md` *"a new backend = a new `*_resolver.py`… The graph never changes."* Plus Tim's standing: no versioning, commit-to-main-no-branches, fail-loud.

## B.7 — The 3 MOST IMPORTANT patterns recollection MUST match (the callback)
1. **Registry-is-truth / no-hardcoding (the spine of everything).** Models (services.json + model_capabilities.json), embedding lenses (projections/spaces), node-types (nodes/<id>.py), skills, MCP tools — all are **discovered data, added by dropping a file/row, never a code edit**, and values are **authored FROM the registry, never invented** (`AGENTS.md:28`). This directly enforces Tim's "bge-m3 has zero priority / full lens-set, no winner": recollection's embedder is a registry slot, the dim is per-space, nothing is baked in.
2. **The addressed-record + space-keyed-vector store contract (`contracts/address.py` + `corpus.py:write_record` + `fs_store.put_vector(space=…)`).** Every distilled memory is a `write_record` with **3-axis lineage (session/round/project) enforced fail-loud**; every fingerprint is a `vec://<source>#space=<lens>`. recollection writes its SQLite **portable-by-field** (explicit space/source/dim/model/lineage columns) so absorption is a backend re-point, exactly the store's designed-for swap.
3. **Parametric MCP verbs + map/reduce cognition (one verb many ops; `run_items`→`run_reduce`).** Recall/distill/consolidate are exposed as **one parametric tool** (op/scope/axis + return_format `summary|content|stats|addresses`) — never tool-per-op — and the distill/consolidation engine is the **`run_items` map → `run_reduce(mode=cluster|role)` reduce** shape, sized by `SlotBudget.from_registry`. This is simultaneously the Company house style AND the CI parametric design (§C-B4), so matching it kills two birds.

---

# C. HARVEST SOURCES — exact code to lift

Subagent-verified file paths, symbols, signatures, line numbers (Observed). **Found-elsewhere ≠ replacement (Tim's law):** these *inform/port into* recollection's own store — they are not bolted on. Substrate-mcp's mechanisms are **pure-SQLite** (Chroma is a disposable projection — Read 3), so porting = re-point at recollection's schema.

## C-A — substrate-mcp (`/home/tim/repos/obsidian-overlord/src/substrate_mcp/`)

**File tree (Observed, `wc -l`):** `server.py` (4613), `db.py` (1295), `parser.py` (1024), `schema_profiler.py` (908), `scanner.py` (633), `cli.py` (445), `docs_gen.py` (440), `report.py` (261), `issues.py` (230), `config.py` (195), `watcher.py` (95), `__init__.py` (24). **★ `embeddings.py` is NOT in the repo tree** — it's imported (`server.py:69`) but missing on disk; the only surviving copy is in CC file-history (see A5).

1. **State/temporal layer — HIGHEST harvest (the crown jewel; the capability the Company most lacks).** Port to recollection's `units`/`links`/`state` tables:
   - **`state_history` table** — `db.py:235-246`: `(id, address_id FK ON DELETE CASCADE, axis, value, observed_at REAL)` + index `(address_id, axis, observed_at DESC)`. Append-only change-log.
   - **`db.py:1032 record_state_transition_if_changed(conn, address_id, axis, value, bootstrap_mtime=None) -> bool`** — appends only on change; **mtime-bootstrap at `db.py:1057-1061`** (`observed_at = min(file.mtime, now)` on first observation only). The "timeline isn't a lie on day one" trick — steal wholesale.
   - **`db.py:1094 backfill_state_history_from_mtime(conn, vault) -> int`** — idempotent retrofit.
   - **`server.py:1446 get_state_history`, `:1484 compare_state_observations` (interpretation-free — raw timestamps), `:1540 find_state_asymmetries(...)`** — the signed-gap sensor; **the asymmetry SQL at `server.py:1606-1634`** joins `wikilinks→referrer→unit→state_history(MAX id each)`, `gap = referrer_observed_at − unit_observed_at` (`:1663`). 8 sort modes, rich filters, `min_abs_gap_seconds`. **No interpretation — the substrate is a SENSOR.**
   - **`schema_profiler.py:42 STATE_AXIS_NAMES`** regex + candidacy logic `:533-619` (auto-detect the lifecycle axis). For recollection this maps onto a unit's `claimed_status`/maturation field.
   - **Maps to the plan's HEALTH layer (temperature scan / resistance) + Tim's Gap-Pressure + common-memory-temporal laws.** Pure-SQLite, small, no model calls.

2. **`cluster_by_embedding` — the k-means (`server.py:3748`, inline NumPy spherical k-means, NO sklearn).** `_CLUSTER_STOPWORDS` at `:3734-3744`; cosine-sim assignment + empty-cluster reseed `:3814-3831`; **centroid-terms labeling** `:3836-3870` (cluster labels without an LLM); sorted-by-size `:3871`. **Harvest as a reference impl** of the plan's pattern_cluster — BUT note the Company's `run_reduce(mode="cluster")` (§B.5) is the already-store-integrated version; recollection picks one (likely the Company's for the absorbed form, this k-means as the standalone fallback). Caveat (Read 3): bulk-loading all vectors into memory needs a cap at scale.

3. **The resolver ladder (the reconcile pattern, `consolidate` reframed).** `server.py:1043 consolidate(vault=None, cross_vault=False)` → `:784 _consolidate` → `db.py:567 resolve_wikilinks_for_vault` + `db.py:346 recount_type_instances`. The multi-strategy ladder: **`db.py:722 _resolve_target`** (5 tiers: exact rel_path → suffix → case-insensitive → basename-only → title) and **`db.py:677 _resolve_target_strict`** (3 tiers, for cross-boundary). **Harvest the pattern** (debounced deferred edge-resolution; ambiguity kept as first-class state, never silent-dropped) for recollection's LINK pass (P6) — references are intent-to-link, resolution is a separate metabolic pass.

4. **The chunker (`parser.py`, stdlib-only, first-class provenance).** `:51 estimate_tokens` (tokenizer-free blend, 4→1.8 chars/tok by struct ratio); `:211 _chunk` (3-pass: block-id → heading-bounded → paragraph-window); `:354 _split_oversized`; `:414 _paragraph_windows`. **chunk_address = `filesystem://<vault>/<relpath>#<anchor>`** (block-id `#^a` > heading `#slug` > `#chunk-N`), with `char_start/char_end/content_hash`. **Harvest as the chunking pattern** for recollection's unit-creation (the address-first, content-hash-delta-gated, structure-aware design). recollection's analog address is `exchange://<sid>/<i>#<span>`.

5. **The embedder adapter (REPLACEs §A.4's blast-radius cleanly).** ★ Recovered from CC file-history (NOT in repo): `/home/tim/.claude/file-history/bda8ce28-6dfb-4a76-b13a-bc016b8574ca/ae22f5e848708178@v2` (246 lines). `OpenAIEmbedder` (line 89): `__init__(base_url="http://localhost:8001/v1", model="BAAI/bge-m3")`, **`/v1/embeddings` call** (`embed`, lines 109-124): `POST {base}/embeddings {"model","input":batch[≤64]}` → sort by `index` → `[float(e) for e in data["embedding"]]`, **fail-loud (no silent empty)**, `health()` GETs `/v1/models`. `make_embedder(provider, model, **kw)` (line 147): `"openai"` → :8001, `"ollama"` → :11434. **Harvest the OpenAIEmbedder call shape directly** — this IS the §A.4 REPLACE for recollection's TS embedder (port the same HTTP contract to TS), and it's the exact endpoint the Company fabric speaks (Read 5 §1.1), so the call path is a near-match.

## C-B — conversation-intelligence (`/home/tim/repos/Supabase/supabase/migrations/`)

Harvest the **designs**, NOT the schema verbatim (the project has 3072-vs-384 dim drift + `ci_` vs unprefixed naming inconsistencies — Read 4 §6).

1. **Turn-context embedding builder (⭐ the gold unit — the plan's "turn-context work units").** `migrations/20260212000000_ci_turn_context_embeddings.sql`: **`ci_build_turn_pairs(p_conversation_id, p_min_content_length=20, p_max_chunk_chars=2000)`** (lines 59-79). Assembles `'User: '||user||E'\nAssistant: '||asst||'[Tools: '||tools||']'` (lines 182-191); **tool-compaction CASE** (lines 143-162: Read/Edit/Write→filename via `regexp_replace '^.*/([^/]+)$'`, Bash→`LEFT(cmd,60)`, Grep/Glob→pattern, `mcp__%`→name). Wayfinding sibling **`ci_build_conversation_embed_text`** (lines 339-347: header + first-3/last-3 turns, `LEFT(…,2000)`). **Harvest the turn-pair-with-baked-in-tools design** — it's the richer version of episodic-memory's `generateExchangeEmbedding` (§A.4) and is the unit Tim's `Intent→…→Execution` circuit wants.

2. **Dual-granularity embedding registry (config-as-behaviour).** Same migration file: table **`ci_embedding_config`** (lines 18-31): `config_name UNIQUE, source_scope, model_id, dimensions, target_type, content_function, enabled, chunk_config JSONB`. Two seed rows (lines 41-49): `turn_context` (the retrieval layer, `content_function='ci_build_turn_pairs'`) + `conversation_summary` (the wayfinding layer, `='ci_build_conversation_embed_text'`). **Harvest the "embedding strategy is a registry row, content-builder named in the row" design** — directly aligns with recollection's registry-is-truth + multi-lens fingerprints + §B.4.

3. **Artifact-provenance graph (⭐ the build-causal-history lane).** ★ **NAME CORRECTION (subagent-verified):** tables are **`indexed_artifacts`** + **`artifact_provenance`** (NOT `ci_`-prefixed), in `migrations/20260119000000_conversation_intelligence_system.sql`. `indexed_artifacts` (lines 452-483): `artifact_id, artifact_type, artifact_address UNIQUE-with-type, created_by_conversation_id/tool_call_id, modification_count, conversation_count`. `artifact_provenance` edge (lines 496-512): `artifact_id FK, conversation_id FK, tool_call_id FK, operation (create/read/update/delete/rename/move), operation_timestamp, context_summary`. Fn **`record_artifact_provenance(p_artifact_type, p_artifact_address, p_conversation_id, p_tool_call_id, p_operation, p_timestamp)`** (line 1334, upsert). **Harvest the design** — this is the plan's LINK pass (P6) reifying `tool_calls.tool_input.file_path` (the spine, Read 1) into a queryable artefact↔conversation graph: "why does this file exist / what touched it, in what order." recollection's `tool_calls` table already has the raw material.

4. **Parametric-tool / return-envelope (⭐ the MCP house style — pre-validated).** ★ **COUNT CORRECTION:** `migrations/20260210000000_ci_parametric_mcp_tools.sql` defines **5** tools; `ci_issues` is the 6th in `20260211000000_ci_issues_system.sql`. Table `ci_mcp_config` (config_key→JSONB) + tool defs in `ci_mcp_tool_registry`. Tools + selectors: `ci_discover`(scope: projects/conversations/timeline), `ci_read`(view: thread/context/summary), `ci_search`(scope: messages/tools/artifacts/semantic/entities/topics), `ci_trace`(provenance), `ci_manage`(action: health/…/switch_provider), `ci_issues`(action: create/…/close). **`return_format` enum `["summary","content","stats","addresses"]`** (`addresses` = "for programmatic chaining" — grounded-chain ergonomics). **Response envelope `{envelope (params applied), results, stats}`** on every call (ci_discover lines 337-351). **Harvest this design wholesale** for §A.8 / §B.2 — it IS the Company's "parameterised/resource-oriented + return-format + grounded-chain" bar, already built once.

5. **The live sync lane (curation to lift into capture, P10).** `/home/tim/.claude/sync-conversations-to-supabase.py` (Observed): SHA256 hash-dedup (`file_hash`, skip-on-unchanged, state in `conversation-sync-state.json`); **skips `agent-*.jsonl` + `history.jsonl`** (NOTE: recollection P10 wants sidechains INCLUDED — so lift the dedup/streaming, invert the sidechain exclusion); **filters `type:'progress'` records** pre-upload (streaming noise). Edge fn `supabase/functions/conversation-sync/index.ts` → staging `ci_raw_data`, dedup by `(bucket,path)` + content-hash, re-extract-on-change. **Harvest the curation decisions** (hash-dedup, progress-strip, re-extract-on-change) for §A.6's unified capture — minus the sidechain exclusion.

---

# D. SYNTHESIS — the build picture in one frame

- **The chassis is sound; the engine is wrong.** episodic-memory's **capture/sync/incremental/plugin/MCP skeleton is excellent and reusable** (KEEP). Its **embedder (ONNX bge-small-384) and summarizer (cloud Claude SDK) are the architectural mismatches** with the Company's local-fabric world — both get REPLACED with registry-driven local-fabric calls (OpenAI-compatible HTTP standalone; `complete_embeddings`/`run_items` absorbed). Its **flat search** becomes the gather→judge machine.
- **The data model grows up.** `exchanges`+`tool_calls` stay as the **atom bedrock** (KEEP); recollection ADDs the typed-unit registry, the provenance link graph (harvested from CI's `indexed_artifacts`/`artifact_provenance` design over the existing `tool_calls.tool_input`), and **multi-coordinate fingerprints** (the 384 `vec_exchanges` demoted from sole space to one lens; per-lens dim; no winner). The exchange carries a Company-compatible `exchange://<sid>/<i>` address (bridge = `session_id`+line-region).
- **The metabolism is harvested, not invented.** The plan's HEALTH/consolidation = substrate-mcp's **state-asymmetry sensor + resolver-ladder reconcile + chunker** (ported pure-SQLite) ∪ the Company's **`run_reduce(mode=cluster)`**. The rich retrieval unit = CI's **turn-context-with-tools** embedding. The MCP surface = CI's **parametric tool + envelope** design = the Company house style.
- **Everything is registry-driven and absorption-ready.** No hardcoded model/dim; portable-by-field SQLite; one parametric MCP verb; map/reduce distill. Standalone now (`~/.recollection` data dir survives plugin updates), a re-point — not a rewrite — to fold into the Company later.

---

*Wave-1 build-map. Observed = read in code this wave (clone-base src directly; Company patterns + harvest locations subagent-verified against the real files). Inferred = the absorption mappings (how recollection's standalone shapes map to Company seams) — tentative, for the loop-prep + Tim's build-order call. No live execution (no Verified). Open decisions surfaced for Tim: the lens loadout (which embedders co-reside; bge-m3 has no priority), Codex-harness keep/drop, marketplace publish or private-sibling, and standalone-vs-absorbed timing of the MCP refold. Build-order remains Tim's to set; §A.9 + the plan's phasing A→B→C→D inform it.*
