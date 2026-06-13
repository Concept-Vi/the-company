# episodic-memory — Upstream Research Dossier

> Everything published online about Jesse Vincent's (obra) `episodic-memory` Claude Code plugin, gathered 2026-06-11 in preparation for cloning and adapting it. Locally installed: **1.0.15** (via superpowers-marketplace). Upstream latest: **v1.4.2** (2026-05-21).
>
> Evidence basis: GitHub API (repo metadata, tags, all 112 issues/PRs, forks, contributors), raw upstream files (CHANGELOG.md, README.md, docs/SCHEMA.md, docs/CODEX.md, marketplace.json), Jesse's blog (blog.fsck.com), HN Algolia search, Reddit/third-party search via Firecrawl. Statements about code behavior below are **observed from upstream documentation and issue reports**, not execution-verified locally.

---

## 1. Repo Status & Health Signal

- **Repo:** https://github.com/obra/episodic-memory — TypeScript, MIT, default branch `main`
- **Created:** 2025-10-17 · **Last push:** 2026-05-21 (v1.4.2) · as of 2026-06-11 there have been no commits for ~3 weeks, but issue/PR traffic is active (newest issue 2026-06-10, newest PRs 2026-06-07/08)
- **Stars:** 412 · **Forks:** 101 · **Open issues+PRs:** 19 · **Watchers/subscribers:** 9
- **Contributors (commit counts):** obra 113, techjoec 2, minyek 2, then single-commit contributors: andrewcchoi, officialasishkumar, one1zero1one, monsterxz9, mvanhorn, schuyler. This is a **single-maintainer project with a healthy drive-by-fixer community**. The de-facto most active current contributor is **minyek**, who has 4 open PRs (#108–#111) plus 2 merged fixes in 1.4.x.
- **Not on npm** (issue #43 closed as won't-do): install is from GitHub source (`npm install -g github:obra/episodic-memory`) or via the plugin marketplaces.
- **Marketplace distribution:** `superpowers-marketplace` lists episodic-memory at **version 1.4.2** (https://github.com/obra/superpowers-marketplace, `.claude-plugin/marketplace.json`). The marketplace description now reads "Semantic search for **Claude Code and Codex** conversations" — Codex is a first-class harness since 1.3.0.

### Versions (git tags)
`v1.0.0` (2025-10-14) → `v1.0.15` (2025-12-17, **local install**) → `v1.1.0` (2026-05-02) → `v1.1.1`, `v1.1.2`, `v1.2.0` (2026-05-03) → `v1.3.0`, `v1.3.1`, `v1.4.0` (2026-05-13) → `v1.4.1` (2026-05-17) → **`v1.4.2` (2026-05-21, latest)**.

Note the **4.5-month gap** between 1.0.15 (Dec 2025) and 1.1.0 (May 2026), then a burst of nine releases in three weeks. 1.1.0 batched up months of community fixes.

---

## 2. Version Delta: 1.0.15 → 1.4.2 (what the local install is missing)

Source: https://raw.githubusercontent.com/obra/episodic-memory/main/CHANGELOG.md

### v1.1.0 (2026-05-02) — the big catch-up release
**Added**
- **Search metadata filters** (#63, design by @jwk2601): `--project`, `--session-id`, `--git-branch` exact-match filters on both CLI and the MCP `search` tool. Filter values bind as positional SQL parameters; the existing `--after`/`--before` time filters were converted from string interpolation to bound parameters in the same change (an injection-hygiene fix riding along).
- **API configuration env vars for summarization** (#37, @techjoec):
  - `EPISODIC_MEMORY_API_MODEL` — summarizer model (default: haiku)
  - `EPISODIC_MEMORY_API_MODEL_FALLBACK` — fallback on errors (default: sonnet)
  - `EPISODIC_MEMORY_API_BASE_URL` — custom Anthropic-compatible endpoint
  - `EPISODIC_MEMORY_API_TOKEN` — auth token for the custom endpoint
  - `EPISODIC_MEMORY_API_TIMEOUT_MS` — request timeout
  - **Adaptation-relevant:** this is the existing seam for pointing summarization at a different backend (e.g., a local vLLM endpoint). Custom config affects ONLY summarization (≤10 calls per sync); embeddings/search/MCP stay local.

**Changed**
- Bumped `@anthropic-ai/claude-agent-sdk` to 0.2.x (transitively requires zod 4) — needed for `persistSession`.
- `tool_calls` schema now uses `ON DELETE CASCADE` (#81), with an idempotent one-time migration for existing DBs.
- `exclude.txt` matches nested directory names (#80) — `subagents` now also skips `<project>/<session>/subagents/agent-*.jsonl`.

**Fixed (the important ones)**
- **Indexer skipped appended exchanges** (#84): the `COUNT(*) > 0` "already indexed" skip was replaced with a `MAX(line_end)` high-water mark, so transcripts that grow after first indexing (resumed sessions; syncs racing a still-running session) now pick up their tail. Before this, trailing content was **permanently silently lost** from the index.
- **Similarity scores were mathematically wrong** (#55, @gmax111): `1 - row.distance` treated L2 distance as cosine distance. For unit-normalized embeddings the correct conversion is `1 - d²/2`. Ranking order was unaffected (monotonic), but displayed/aggregated scores were wrong.
- **Summarizer session pollution** (#83): `persistSession: false` passed to the SDK so summarization stops creating fake session JSONLs in `~/.claude/projects/<cwd-slug>/` (which had been polluting the session sidebar AND feeding back into the index).
- Windows hook fails on home dirs with spaces (#75) — quote `${CLAUDE_PLUGIN_ROOT}`.
- MCP install `ETARGET` on stale npm cache (#76) — removed `--prefer-offline`.
- **MCP protocol corruption from embedding model output** (#48): embedding model's stdout redirected to stderr (a `console.log` in embeddings.ts was breaking the MCP JSON protocol).
- Orphaned MCP processes (#54): SIGHUP handler + stdin-close detection in the wrapper.
- `exclude.txt` ignored at sync time (#38): now honored by sync and verify.
- Batch of discovery/path fixes (#42, #50, #57, #62, #68, #70, #72): sidechain filtering in search, SessionStart `clear` matcher (archive on `/clear`), `CLAUDE_CONFIG_DIR` support, recursive subagent file discovery, support for **both** `~/.claude/projects` **and** `~/.claude/transcripts` (Claude Code moved transcript location mid-stream — #68), explicit surfacing of summarization failures.

### v1.1.1 (2026-05-03) — version hygiene
- MCP server reports actual plugin version in handshake (was hardcoded `1.0.0`).
- Single source of truth for versions: `package.json` → generated `src/version.ts`; drift test asserting `package.json`, `plugin.json`, `marketplace.json` agree; `scripts/bump-version.sh` with `--check`/`--audit`.

### v1.1.2 (2026-05-03) — CRITICAL: recursive process explosion
- (#87, #88, diagnosis by @kaankoken and @materemias) The 1.1.0 `persistSession: false` fix stopped the SDK-spawned Claude subprocess from *saving* its session, **but not from firing the SessionStart hook**. That hook re-ran `episodic-memory sync --background` → re-summarized → spawned another Claude subprocess → fired the hook again — **fanning out hundreds of detached processes, saturating CPU, and burning API quota** (one user report: system OOM, #89).
- Fix: reentrancy guard env var `EPISODIC_MEMORY_SUMMARIZER_GUARD`, set when calling the SDK's `query()`, inherited by the subprocess; `sync-cli` checks it at startup and exits silently. Unit + integration test coverage.
- **Adaptation lesson:** any design where a hook triggers an LLM call that itself runs inside a hook-bearing harness needs an explicit reentrancy break. This bit them twice (#59 earlier: `index --sync` recursively summarized its own summarization conversations; #66: the recursion plus a backup loop created ~5000 × 30MB `.jsonl.bak` files and filled a disk).

### v1.2.0 (2026-05-03) — embedding model upgrade + live migration
- **Embedding model: `all-MiniLM-L6-v2` → `bge-small-en-v1.5` (BAAI)**. Both 384-dim, so storage layout unchanged. On a 17,000-exchange retrieval test built from real production data: **rank-1 accuracy 47% → 53%, top-10 68% → 75%**.
- **Automatic background migration:** each `sync` re-embeds up to 500 stale exchanges (env `EPISODIC_MEMORY_MIGRATION_BATCH` to raise; ~1 min per 5000 on a recent Mac). Search keeps working on a mixed-model index ("ranking is slightly noisier but never broken"). Concurrent syncs: only one re-embeds. Crash mid-batch: rows stay tagged, next sync resumes. Rollback to 1.1.x is safe.
- First sync after upgrade downloads a new 34 MB model file.
- Side effect: resolves #82 (ONNX runtime crash on Node ≤23 / macOS arm64 protobuf+WASM fallback) via the underlying library upgrade.
- **Adaptation-relevant:** this release is a **complete worked example of swapping the embedding backend on a live index** — stale-tagging, batched re-embedding, mixed-index search, crash recovery, concurrency. If the adaptation changes embedding models (e.g., to jina-v4 or a local served model), this is the migration pattern to copy.

### v1.3.0 (2026-05-13) — Codex becomes a first-class harness
- Native **Codex plugin support**: `.codex-plugin/plugin.json`, Codex MCP config, plugin hook packaging, local dev marketplace entry. Requires `codex-cli 0.130.0+` (floor set by plugin manifests/MCP loading, lifecycle hooks, hook trust in `hooks.state`, app-server `thread/fork` with `ephemeral: true`, rollout JSONL transcripts in `$CODEX_HOME/sessions` — see docs/CODEX.md).
- Codex rollout transcript parsing, display, archiving, indexing, and **cross-harness search across Claude Code and Codex conversations in one index**.
- Codex-native summarization via `codex app-server` ephemeral `thread/fork`, with transcript-text fallback.
- `episodic-memory doctor codex` diagnostic command (checks version, features, MCP registration, hook trust, transcript dir, DB, sync logs).
- Opt-in live E2E scripts: `EPISODIC_MEMORY_RUN_CODEX_E2E=1 npm run test:codex-e2e`, `EPISODIC_MEMORY_RUN_CLAUDE_E2E=1 npm run test:claude-e2e` — isolated environments testing archive → summary → index → recall end-to-end.
- **Adaptation-relevant:** the codebase is now structured for **multiple conversation sources feeding one archive/index** — exactly the shape needed if the adaptation ingests other harnesses or the Company's own conversation streams.

### v1.3.1 + v1.4.0 (2026-05-13) — skill-trigger tuning, slash command removed
- Recall skill descriptions broadened: trigger when the agent needs to remember *anything* learned from prior Claude Code/Codex conversations (decisions, patterns, solutions, pitfalls, workflows, project context), not just explicit user requests.
- 1.4.0 measured the change empirically: against fresh sessions asking a personal-fact question, the previous description fired the skill **0/5 trials; the new one 3/5**.
- **Removed the `/search-conversations` slash command** — natural-language reference now routes through the `remembering-conversations` skill, which dispatches the `search-conversations` agent. (The local 1.0.15 install still has the `commands/` directory.)

### v1.4.1 (2026-05-17)
- Sync no longer gets stuck on zero-content conversations (metadata/stub-only files re-queued forever; ten at queue head blocked everything behind them). Fix by @minyek.

### v1.4.2 (2026-05-21) — queue robustness + Windows/install hardening
- **Cross-project summarization crash** (#93, @minyek): every short (≤15 exchange) conversation whose recorded project cwd differed from sync's cwd silently failed (`Cannot read properties of undefined (reading 'match')`) and re-queued forever. Summarizer now passes the recorded cwd to the SDK, with a non-resume fallback when the project dir no longer exists. Multi-project users were most affected.
- **Codex deprecated-model fix** (#99, @monsterxz9): summarizer stopped forwarding stale model ids (e.g., `gpt-5.2-codex`) from historical data; Codex now picks its default from `~/.codex/config.toml#model`; override via `EPISODIC_MEMORY_CODEX_MODEL`.
- **Failed summaries no longer pin the queue head forever** (#96): structured **error sentinels** written on transient failure; retry after a threshold (default 1h, `EPISODIC_MEMORY_SUMMARY_ERROR_RETRY_HOURS`); verify/stats/indexer distinguish real summaries from sentinels.
- **Single-instance file lock for sync** (#97): concurrent SessionStart hooks from multiple sessions/worktrees previously raced on the same SQLite DB (`SQLITE_BUSY` crashes on macOS/Linux; `STATUS_DLL_INIT_FAILED` heap exhaustion on Windows). Competing workers now print `sync already running (pid X); skipping` and exit.
- MCP wrapper detects **partial node_modules extractions** (#95 Bug 1) — probes each required package's manifest, reruns `npm install` listing what was missing.
- `npm install` exits 0 on Windows (#95) — postinstall's unix-only `2>/dev/null || true` replaced with a cross-platform Node script. (The changelog also documents that #95's "Bug 2", onnxruntime-common-not-hoisted, was a misread of `npm ls` logical-tree output — but see open issue #105 disputing that.)

### Env-var surface accumulated across the delta (full list for adaptation)
`EPISODIC_MEMORY_API_MODEL`, `EPISODIC_MEMORY_API_MODEL_FALLBACK`, `EPISODIC_MEMORY_API_BASE_URL`, `EPISODIC_MEMORY_API_TOKEN`, `EPISODIC_MEMORY_API_TIMEOUT_MS`, `EPISODIC_MEMORY_SUMMARIZER_GUARD` (internal reentrancy), `EPISODIC_MEMORY_MIGRATION_BATCH`, `EPISODIC_MEMORY_SUMMARY_ERROR_RETRY_HOURS`, `EPISODIC_MEMORY_CODEX_MODEL`, `EPISODIC_MEMORY_CLAUDE_CODE_SETTING_SOURCES` (PR #58), `EPISODIC_MEMORY_SAVE_SDK_LOGS` (PR #39, default off), `CLAUDE_CONFIG_DIR` honored (#57), plus the E2E flags.

---

## 3. Design Rationale From the Author

### Primary source: "Fixing Claude Code's amnesia" — blog.fsck.com, 2025-10-23
https://blog.fsck.com/2025/10/23/episodic-memory/

The release post lays out the full design argument:

1. **Memory taxonomy as the design frame.** Jesse explicitly grounds the plugin in the human-memory distinction: his earlier project **private-journal-mcp** (https://github.com/obra/private-journal-mcp, genesis post https://blog.fsck.com/2025/05/28/dear-diary-the-user-asked-me-if-im-alive/) gave Claude *journaling* — but "the problem with the kind of memory formation you get from journaling is that you only get 'memories' when the journaler realizes that what they've just done is worth writing down. It's just one kind of memory." Episodic memory is different: memory of specific things you did, with **total recall rather than curated capture**. The two plugins coexist in his marketplace as complementary memory systems.
2. **Cross-project recall is deliberate.** "My episodic memory isn't firewalled by project. If I've seen an error message before when I was doing something else, I might still be able to pull up the context." The index is global across all projects by design (per-project filtering arrived later as an opt-in search filter in 1.1.0, not as a storage boundary).
3. **The raw material already exists — the system is retrieval, not capture.** Claude Code keeps a perfect record of every conversation/tool call/subagent run in `~/.claude/projects` JSONL — but **deletes them after a month by default** (`cleanupPeriodDays` in `~/.claude/settings.json`; he recommends `99999`). The plugin's first job is simply to archive those files (to `~/.config/superpowers/conversations-archive`) before they're lost, then make them searchable.
4. **Six-part architecture** (his enumeration): (1) SessionStart hook that archives prior conversations; (2) SQLite + vector search DB; (3) CLI that searches and renders conversations as markdown/HTML ("the HTML viewer is actually a pretty nice way to read and share Claude Code session histories all on its own"); (4) MCP tool; (5) a **skill** teaching Claude *how and when* to search its memory; (6) **a specialized haiku subagent "that exists solely to manage the potential context bloat that comes from reading over previous conversations."** That last point is a core design insight: raw conversation history is context-poisonous, so retrieval runs in a sacrificial cheap-model subagent that returns only the distillate.
5. **Empirical validation culture.** He dogfooded 3–4 weeks before release; he cites 2389.ai's research that even the simple journal made Claude measurably more capable (https://2389.ai/posts/agents-discover-subtweeting-solve-problems-faster/); and the changelog shows **skill descriptions being treated as testable artifacts** — 1.0.12: trigger description empirically tested with subagents (5/5 scenarios vs 3/5 for the old wording); 1.4.0: 0/5 → 3/5 on personal-fact lookups. The prompt text that decides *when memory fires* is tuned by measurement, not vibes.
6. **Stated value claim** (via an in-situ Claude "testimonial", Sonnet 4.5, 2025-10-14): semantic search "surfaces conversations about API design patterns even when those exact words weren't used"; the unique payload is **the why** — "trade-offs discussed, alternatives considered, the user's preferences and constraints. Code comments explain what, documentation explains how, but episodic memory preserves why."

### Scope philosophy (from the maintainer's own words in PR #69)
When @jung-wan-kim submitted a large fact-extraction/consolidation system as a PR, obra declined it: "this is a large scope increase that's really **a separate product from episodic memory's core mission of conversation search and archival**. We'd recommend building this as its own plugin… you can have your own hooks, MCP tools, and database without [coupling]." (https://github.com/obra/episodic-memory/pull/69) — The plugin is deliberately *episodic-only*: archive + index + search. Semantic/knowledge-graph memory is out of scope and pushed to the ecosystem (it became memory-bank, §5).

### Surrounding context from his other writing
- **Superpowers** (https://blog.fsck.com/2025/10/09/superpowers/, HN: 435 points / 231 comments, https://news.ycombinator.com/item?id=45547344) is the umbrella methodology — skills as a "binder" for his agentic development style. episodic-memory was announced in the Skills post (https://blog.fsck.com/2025/10/16/skills-for-claude/) as "a new episodic memory plugin I'm [building]" and released a week later.
- He ported skills/Superpowers to **OpenAI Codex** (https://blog.fsck.com/2025/10/27/skills-for-openai-codex/) and **OpenCode** (https://blog.fsck.com/2025/11/24/Superpowers-for-OpenCode/) — the multi-harness instinct that later landed in episodic-memory 1.3.0.
- His MCP design essay — "When it comes to MCPs, everything we know about API design is wrong" (https://blog.fsck.com/2025/10/19/mcps-are-not-like-other-apis/) — explains the tool-shape philosophy behind the minimal two-tool MCP surface (`search`, `read`).
- He now runs an **agent-written blog** (https://blog.fsck.com/2026/02/12/letting-agents-blog/, agent posts under /agent-blog/) and is Founder/CEO of **Prime Radiant**; press bio calls Superpowers "the most-used Claude Code plugin in the world" (https://blog.fsck.com/mentions/).

### Architecture as documented in the README (current main)
https://github.com/obra/episodic-memory README:
- **Pipeline:** (1) **Sync** copies conversation files to the archive → (2) **Parse** extracts user–assistant exchanges from JSONL → (3) **Embed** locally via Transformers.js (offline, no API calls) → (4) **Index** into SQLite + sqlite-vec → (5) **Search** by vector similarity, exact text, or both.
- **Search tool:** single-string queries or arrays of 2–5 concepts for AND-matching; limit 1–50; date-range filters; markdown/JSON output.
- **Summarization:** Claude Code sessions summarize via Claude Code auth (haiku default → sonnet fallback); Codex sessions via `codex app-server` ephemeral threads; ≤10 summarization calls per sync; everything else stays local.
- **CLI:** `sync` (hook-recommended), `search`, `stats`, `show <file>` (markdown/HTML), `index --cleanup/--repair/--verify`, `doctor codex`.
- **Privacy:** conversations containing `<INSTRUCTIONS-TO-EPISODIC-MEMORY>DO NOT INDEX THIS CHAT</INSTRUCTIONS-TO-EPISODIC-MEMORY>` are archived but never indexed; summarizer sessions and meta-conversations auto-excluded; `exclude.txt` for path-based exclusion.
- Indexing is atomic and idempotent ("safe to run concurrently or repeatedly").

### Storage schema (docs/SCHEMA.md, current main)
https://github.com/obra/episodic-memory/blob/main/docs/SCHEMA.md
- **`exchanges`** — one row per user↔assistant exchange: `user_message`, `assistant_message`; location (`project`, `archive_path`, `line_start`, `line_end` — the index points back into the archived JSONL rather than duplicating content for display); timing (`timestamp`, `last_indexed`); structure (`parent_uuid`, `is_sidechain` for subagent chains); session context (`session_id`, `cwd`, `git_branch`, `claude_version`); thinking metadata (`thinking_level`, `thinking_disabled`, `thinking_triggers` JSON).
- **`tool_calls`** — per-exchange tool usage (`tool_name`, `tool_input` JSON, `tool_result`, `is_error`), FK → exchanges (ON DELETE CASCADE since 1.1.0), indexed by tool_name — tool patterns are searchable.
- **`vec_exchanges`** — sqlite-vec virtual table, `FLOAT[384]` embeddings keyed by exchange id.
- Indexes on timestamp DESC, session_id, project, is_sidechain, git_branch.
- Migrations: idempotent, `pragma_table_info()`-checked `ALTER TABLE`s in `src/db.ts`.

---

## 4. Known Issues & Limitations (current, as of 2026-06-11)

### The structural liability: the summarizer's resume-a-full-Claude-session architecture
The summarizer works by spawning a **full Claude Code CLI session** via `@anthropic-ai/claude-agent-sdk` `query({ resume: <sessionId>, cwd: ... })`. A whole family of the project's worst bugs flows from that one decision:
- **#83 (fixed 1.1.0):** spawned sessions wrote session JSONLs → sidebar pollution + index feedback.
- **#87/#88/#89 (fixed 1.1.2):** spawned sessions fired SessionStart hooks → recursive process explosion, OOM, token burn.
- **#106 (OPEN):** spawned sessions **load the user's entire global MCP server fleet — once per conversation summarized**. GUI-opening MCP servers pop windows per conversation; N-conversation backlog ⇒ N × whole-fleet subprocess fan-out. Fix PR #107 (@madorb, isolate MCP servers/settings in the subprocess) is open.
- **#104 (OPEN):** spawned sessions inherit `process.env`, so a globally-exported API key **silently switches background summarization from subscription auth to metered API billing** — no warning, no opt-in, no spend cap. Combined with retry loops (#103: failed summaries still re-queued/re-billed on 1.4.2 despite the #96 sentinel fix) this can produce real unexpected charges.
- **#112 (OPEN, 2026-06-10, well-evidenced with mitmproxy):** the pinned SDK 0.2.x embeds an old CLI (`claude-code/2.1.141`); Anthropic's bootstrap endpoint version-gates model options, so the old embedded CLI receives `additional_model_options: null` and persists `null ?? []` into the **shared** `~/.claude.json` `additionalModelOptionsCache` — **wiping newly released models (e.g., Fable) out of the host Claude Code's model picker** a few seconds after every launch, whenever sync has anything to summarize.
- Open PRs #108 (run summarization tool-less so it can't hijack an active session), #109 (summarize once idle, refresh on growth, bound retries), #110 (handle conversations ending on extended-thinking turns) are all further patches to this same subsystem.
- **Adaptation implication:** if cloning, the summarizer is the subsystem to redesign rather than inherit — e.g., summarize from transcript text via a plain API call (the Codex fallback path already does this) instead of resuming live sessions. That single change dissolves the #83/#87/#104/#106/#112 class.

### Install/native-dependency fragility (the other big class)
The plugin self-installs npm deps at first MCP start via a wrapper, and depends on three native/finicky packages: **better-sqlite3** (native build), **sqlite-vec** (platform-specific optional packages), **transformers.js/onnxruntime** (WASM/native inference). Open issues:
- **#102:** hosts with global libvips make `sharp@0.34.5` postinstall attempt a source build, fail, and leave corrupt node_modules **that traps the wrapper's own recovery loop**.
- **#100:** `npm rebuild better-sqlite3` is a silent no-op on Node 25 — binding never builds; the recovery hint repeats the dead command.
- **#105:** onnxruntime-common not hoisted on Linux/WSL2 — clean-install reproduction of the issue 1.4.2's changelog dismissed as a misread (conflicting versions confirmed by the reporter). **Directly relevant to Tim's WSL2 environment.**
- **#94:** the observability meta-issue — SessionStart sync failures are invisible (`2>/dev/null || true` + `--background`); users see only a vague hook error while archiving silently stops; the real error lives in `~/.config/superpowers/logs/episodic-memory.log`.
- **#49:** MCP server fails to start on Windows with nvm.
- Historic (closed) members of the class: #4/#5 sqlite-vec platform packages, #9 NODE_MODULE_VERSION, #13 exit 127, #19/#23/#41 npm-install loops/resource exhaustion, #64 bundled MCP SDK using newline-delimited JSON vs Content-Length framing, #65 Windows console window flash (missing `windowsHide`).
- **Adaptation implication:** most of this disappears if the adaptation owns its runtime (pinned Node, prebuilt deps, or a server-side embedding service) instead of npm-installing native modules into a plugin cache at session start.

### Feature requests / direction signals (open)
- **#74 — always show summaries + timeline view:** summaries are generated per-conversation (`-summary.txt`) but only displayed when <300 chars, so most are silently wasted; requests a `mode: 'timeline'` for "what did I work on this past week?" chronological recall. (A genuine capability gap: there is **no temporal browse**, only query-driven search.)
- **#46 — use LEANN for local RAG** (https://github.com/yichuan-w/LEANN) — community appetite for a stronger vector backend than sqlite-vec.
- **#44 — AWS Bedrock support** for summarization auth.
- **#45 — more debugging logs.**
- **#111 (PR) — skip copying/indexing sidechain conversations** to cut disk usage (archives currently include all subagent traffic).
- **#101 (PR) — enable `busy_timeout` + `foreign_keys` pragmas** for multi-writer safety (the file lock in 1.4.2 serializes sync, but the MCP server and sync can still co-write).

### Inherent design limitations (from docs + issue history, not bugs)
- **English-centric, small embedding model** (bge-small-en-v1.5, 384-dim) — quality ceiling acknowledged by the author's own benchmark (53% rank-1).
- **Exchange-granularity indexing** — each user↔assistant exchange embeds independently; no conversation-level or topic-level embedding (summaries partially compensate but are display-only today, see #74).
- **No retention/forgetting model** — the archive grows forever; no consolidation, dedup, or decay (deliberately out of scope per PR #69).
- **Search-only recall** — memory is pulled (skill/agent decides to search); nothing is pushed into context proactively at session start beyond the sync hook.
- Behind a proxy/firewall the first-run model download fails (#52, transformers.js proxy support — closed).

---

## 5. Ecosystem & Derivatives

### Position in the obra plugin family (superpowers-marketplace)
Source: https://github.com/obra/superpowers-marketplace `.claude-plugin/marketplace.json` (marketplace v1.0.13):

| Plugin | Version | Relation to memory |
|---|---|---|
| **superpowers** | 5.1.0 | Core skills/methodology library (TDD, debugging, brainstorming, plans). The flagship — repo reports **224,263 stars / 19,928 forks** (GitHub API, 2026-06-11). Notably its README contains **no reference to episodic-memory** — the plugins are independent, composed by users. |
| **episodic-memory** | 1.4.2 | This project — episodic recall over raw conversation history. |
| **private-journal-mcp** | 1.2.0 | The predecessor and complement — *curated* memory: multi-section journal entries (feelings, project notes, technical insights), local embeddings, search. Journaling = capture-on-realization; episodic = total recall. |
| superpowers-chrome | 3.0.1 | Browser control. |
| claude-session-driver | 3.0.2 | Drive other Claude Code sessions via tmux. |
| double-shot-latte | 1.2.0 | Auto-continue evaluation. |
| superpowers-lab / superpowers-developing-for-claude-code / elements-of-style / superpowers-dev | — | Experimental / plugin-dev / writing skills. |

Superpowers itself is on the **official Anthropic marketplace** (Reddit: https://www.reddit.com/r/ClaudeCode/comments/1qgkupf/superpowers_is_now_on_the_official_claude/) plus Codex/OpenCode/Cursor/Gemini-CLI distributions; episodic-memory ships via the superpowers-marketplace (Claude Code) and as a native Codex plugin since 1.3.0.

### Reception & third-party discussion
- **HN:** the episodic-memory release post itself got minimal traction (2 points, 0 comments — https://news.ycombinator.com/item?id=45695245), but rides inside the Superpowers wave (435 points/231 comments — id=45547344; "Dear diary" private-journal post: 46 points/74 comments — id=44129954).
- **Reddit r/ClaudeCode:** repeatedly named in setup/show-and-tell threads as a staple — "Most important plugins are context7, episodic-memory, superpowers" (https://www.reddit.com/r/ClaudeCode/comments/1r79ipp/); cited as prior art in "What I Learned Building a Memory System for My Coding Agent" (https://www.reddit.com/r/ClaudeCode/comments/1r1w397/); referenced in the beads-tracker discussion (https://www.reddit.com/r/ClaudeCode/comments/1ov1z94/); "I was already using Obra's Superpowers plugin… the episodic memory and workflow tools are solid" (https://www.reddit.com/r/ClaudeCode/comments/1sa6ktd/).
- **Blog writeups:** Marco Lancini's "My Claude Code Setup (2026 Edition)" (https://blog.marcolancini.it/2026/blog-my-claude-code-setup/) uses episodic-memory so "past conversations resurface when they are relevant," paired with superpowers, impeccable, agent-browser, context7 — and allowlists `episodic-memory:search-conversations` in permissions. MindStudio published a Claude Code memory-systems comparison that uses the episodic/semantic taxonomy (https://www.mindstudio.ai/blog/claude-code-memory-systems-compared-memarch-hermes/). Evan Schwartz published a rave Superpowers review (indexed at https://blog.fsck.com/mentions/mentions/2026-04-02-emschwartz-rave-review/).
- It was invited into **awesome-codex-plugins** after Codex support landed (issue #90).

### Fork landscape (101 forks)
Almost all forks are passive installs or one-fix staging branches (the pattern: contributor forks, lands a PR — minyek, madorb, techjoec, gmax111, officialasishkumar, monsterxz9, mvanhorn, andrewcchoi, dansunotori, ntroutman, etc.). One fork matters:

- **jung-wan-kim/memory-bank — 73 stars, active (pushed 2026-05-26): the major derivative.** https://github.com/jung-wan-kim/memory-bank — Born directly from rejected PR #69 (obra: build it as your own plugin; author: "Thanks to this project, I found many ideas and answers regarding Claude code context management"). It keeps the episodic substrate (JSONL archiving → 384-dim embeddings → SQLite + sqlite-vec, conversation semantic search) and layers on what obra ruled out of scope: **LLM fact extraction** (Haiku pulls decisions/preferences/patterns at session end), **fact consolidation** (dedup, contradiction handling via merge/replace/evolve at session start), **ontology classification** (Domain → Category), **typed relations** (INFLUENCES/SUPPORTS/SUPERSEDES/CONTRADICTS), **multi-hop graph traversal** (≤3 hops), **scope isolation** (project facts vs shared global facts), **cross-project insights**, **fact provenance back to source conversation**, 9 MCP tools, a web UI, and 3D graph visualization. As the one proven fork-and-extend of this codebase, it is the closest existing analogue to an "adapt episodic-memory into a bigger memory system" project — both a reference and a cautionary scope mirror.
- aaddrick, queirozmarcus, pug-stoic-kennel each have 1 star; nothing else in the fork list shows divergent development.

### Independent neighbors (NOT derivatives — per the found-elsewhere≠replacement rule, these inform, they don't substitute)
GitHub search "episodic-memory claude" surfaces a small genre the plugin effectively named: **CodeAbra/iai-personal-memory-engine** (142★, "best-benchmarked open-source memory system for AI coding assistants"), **cdeust/Cortex** (52★, neuroscience-mechanism framing), **Cantara/kcp-memory** (5★, Go-flavored daemon: SQLite **FTS5** instead of vectors, explicit Working/Episodic/Semantic three-layer model, 10 MCP tools, multi-harness Claude/Gemini/Codex), **gideondk/strata** (episodic/semantic/procedural), **CryptoKrad/open-mem**, **zircote/mnemonic**, **EpisodicRAG** (hierarchical 8-layer long-term memory, listed on claudepluginhub.com). None share code with obra's repo; several share its taxonomy and pipeline shape.

---

## 6. Source Links (everything used)

**Repo & files**
- https://github.com/obra/episodic-memory (API: stars 412, forks 101, created 2025-10-17, pushed 2026-05-21)
- https://raw.githubusercontent.com/obra/episodic-memory/main/CHANGELOG.md
- https://raw.githubusercontent.com/obra/episodic-memory/main/README.md
- https://raw.githubusercontent.com/obra/episodic-memory/main/docs/SCHEMA.md
- https://raw.githubusercontent.com/obra/episodic-memory/main/docs/CODEX.md
- GitHub API: /tags, /contributors, /issues?state=all (112 items reviewed), /forks (89 returned), individual issue bodies #44 #46 #69 #74 #94 #104 #106 #112
- Local install inspected: /home/tim/.claude/plugins/cache/superpowers-marketplace/episodic-memory/1.0.15/ (plugin.json, CHANGELOG.md)

**Jesse Vincent / blog.fsck.com**
- https://blog.fsck.com/2025/10/23/episodic-memory/ (release post — full text captured)
- https://blog.fsck.com/2025/05/28/dear-diary-the-user-asked-me-if-im-alive/ (private-journal genesis)
- https://blog.fsck.com/2025/10/09/superpowers/ · https://blog.fsck.com/2025/10/16/skills-for-claude/ · https://blog.fsck.com/2025/10/27/skills-for-openai-codex/ · https://blog.fsck.com/2025/11/24/Superpowers-for-OpenCode/ · https://blog.fsck.com/2026/03/09/superpowers-5/ · https://blog.fsck.com/agent-blog/2026/02/12/superpowers-v4-3-0/ · https://blog.fsck.com/2025/10/19/mcps-are-not-like-other-apis/ · https://blog.fsck.com/2026/02/12/letting-agents-blog/ · https://blog.fsck.com/mentions/
- https://2389.ai/posts/agents-discover-subtweeting-solve-problems-faster/ (cited research)

**Ecosystem**
- https://github.com/obra/superpowers-marketplace (marketplace.json) · https://github.com/obra/superpowers (README + API stats) · https://github.com/obra/private-journal-mcp

**Discussion / third-party**
- HN: https://news.ycombinator.com/item?id=45695245 (release post) · id=45547344 (Superpowers, 435pts) · id=44129954 (Dear diary) · id=46797274 / 47341827 / 47421863 (Superpowers reposts)
- Reddit: /r/ClaudeCode/comments/1qgkupf (official marketplace) · 1r79ipp (setups) · 1r1w397 (memory-system lessons) · 1ov1z94 (beads) · 1sa6ktd (workflow) · 1r9y2ka (superpowers delivers)
- https://blog.marcolancini.it/2026/blog-my-claude-code-setup/ · https://www.mindstudio.ai/blog/claude-code-memory-systems-compared-memarch-hermes/ · https://www.claudepluginhub.com/plugins/bizuayeu-episodicrag-episodicrag

**Derivatives & neighbors**
- https://github.com/jung-wan-kim/memory-bank (+ PR https://github.com/obra/episodic-memory/pull/69)
- https://github.com/Cantara/kcp-memory · https://github.com/CodeAbra/iai-personal-memory-engine · https://github.com/cdeust/Cortex · https://github.com/gideondk/strata · https://github.com/yichuan-w/LEANN (referenced in #46)
