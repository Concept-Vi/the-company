# Episodic-Memory Adaptation — Landscape

**What this doc is.** A cross-system survey of memory architectures, written to inform a real build decision: how to adapt / fork the `obra/episodic-memory` Claude Code plugin into a local-first memory organ for the Company. It maps the design space across three concentric rings, then synthesizes the patterns that actually matter for the fork. The goal is not a single recommended answer — it is a navigable map of trade-offs, so the decision can be made with the whole space visible.

**The three rings.**
- **Ring 1 — Claude Code memory plugins.** Systems built specifically for the Claude Code (and adjacent agent-CLI) harness. These are the nearest neighbours: same transcript source, same hook lifecycle, same MCP surface. Episodic-memory lives here, and these are where a drop-in or near-drop-in reference would come from.
- **Ring 2 — Agent-memory frameworks.** General-purpose memory layers for AI agents (Mem0, Letta/MemGPT, Zep/Graphiti, Cognee, plus emerging academic systems and 2026 entrants MemU/Memobase). Not Claude-Code-shaped, but they hold the deepest thinking on extraction, graphs, temporality, and consolidation.
- **Ring 3 — Major AI product memory.** The closed memory systems shipping inside ChatGPT, Claude.ai, Gemini, and GitHub Copilot. Opaque internals, but they reveal what the largest teams chose when they had to make memory work for millions of users — and what they got criticised for.

**The comparison axis.** Every system is read on seven dimensions:
1. **Storage** — what the canonical store is, and what is derived/disposable.
2. **Embedding + retrieval** — how things are turned into vectors (or not) and how they come back out.
3. **Chunking-or-extraction** — the *form* a memory takes: raw verbatim chunk, LLM-distilled fact, summary, entity/relationship triple, or hierarchy node. This is the single most consequential axis for the fork.
4. **Integration surface** — hooks, MCP, SDK, REST, CLI, UI; how the harness or agent actually touches it.
5. **Local-vs-cloud** — where computation and data live; offline capability.
6. **License** — fork-ability and commercial terms.
7. **Maturity** — production-readiness, adoption signal, and any contested benchmark claims.

**Orientation.** Episodic-memory sits at one extreme of the space: it indexes *raw conversation exchanges verbatim* into a *single embedded SQLite file* with *local embeddings (BGE-small, 384-dim, no API)*, surfaces them through *two MCP tools (search/read) on explicit demand*, and *never consolidates, forgets, or extracts* — memories accumulate monotonically. Almost every other system in this survey moves away from that extreme along one or more axes: toward LLM-distilled facts (Mem0, ChatGPT, Gemini), toward temporal knowledge graphs (Zep/Graphiti, Cognee, Engram), toward proactive session-start injection (claude-mem, ChatGPT, Claude.ai, Copilot), toward progressive-disclosure token budgeting (claude-mem, memsearch), and toward lifecycle features — consolidation, dedup, forgetting, PII redaction (memoirs, ChatGPT's "dreaming", Copilot's 28-day expiry). The fork decision is, fundamentally, *which of these moves to make and which extremes to preserve.*

---

## Verification caveat (read this honestly)

**Ring 1** claims were gathered from primary-source READMEs in a prior run, and the quoted specifics (port numbers, hook names, embedding models, token-savings claims) are quoted **verbatim**. They were **NOT adversarially cross-verified** — the planned verify pass was cut short by a quota exhaustion. Treat Ring 1 as *primary-source-grounded but unaudited*: the sources are real and direct, but vendor self-description has not been independently confirmed against the running code. Where a Ring 1 number is a vendor performance claim (e.g. claude-mem's "~10x token savings", memsearch's "~1% below OpenAI text-embedding-3-small"), it is flagged inline as **[vendor claim, unverified]**.

**Ring 2 and Ring 3** are fresh research this run, drawing on primary sources (GitHub repos, official docs, source files) plus secondary analysis (survey blogs, benchmark write-ups). Benchmark numbers in this space are **actively contested** — the Mem0↔Zep LoCoMo dispute is the prominent example (Zep alleges Mem0's LoCoMo methodology is flawed; Mem0 counters; a GitHub issue puts Zep's own LoCoMo at 58.44% vs a claimed 84%, with Zep counter-claiming 75.14%). **Do not treat any single benchmark figure as settled.** They are included because the *disputes themselves* are informative about where these systems are strong and weak, not because the numbers are trustworthy in isolation.

**Anything marked [inferred] or [vendor claim]** has not been verified by execution. Structural facts read directly from source (file paths, table schemas, tool counts) are the most reliable category here.

---

## Comparison table

| System | Ring | Storage | Embedding + retrieval | Form (chunk/extract) | Integration | Local/Cloud | License | Maturity |
|---|---|---|---|---|---|---|---|---|
| **episodic-memory** (baseline) | 1 | SQLite + sqlite-vec (384-dim) + raw JSONL archive + per-convo summary sidecars | Local Transformers.js (MiniLM→bge-small); vector KNN + LIKE + multi-concept AND | **Raw** user→assistant exchange chunk (truncated 2000 chars) | 2 MCP tools (search/read) + SessionStart hook | Local-first only | MIT | v1.4.2; niche-mature, well-tested for scope |
| claude-mem | 1 | SQLite + Chroma vector DB (hybrid) | Hybrid semantic+keyword; 3-layer progressive disclosure | AI-compressed semantic **summaries** (live, write-time) | 5 hooks + MCP + Express worker :37777 + React viewer; proactive injection | Local-first (needs uv/Python for vectors) | (OSS) | Active; multi-agent expansion |
| claude-qmd-sessions | 1 | Delegates to external qmd engine (markdown) | qmd hybrid semantic+keyword via qmd's MCP | Lossy: user msgs + assistant text only (drops tool/thinking) | 4 hooks; SessionStart re-injects CLAUDE.md + ~50 exchanges | Local-first (delegated) | (OSS) | Bridge/wiring layer |
| memsearch (zilliztech) | 1 | **Markdown daily logs canonical**; Milvus index disposable | Hybrid dense+BM25+RRF (Milvus Lite=SQLite); 3-layer progressive disclosure | haiku-summarized **bullets** w/ HTML-comment anchors back to JSONL | 4 shell hooks + recall skill + CLI + watch; **no MCP** | Local-first (ONNX bge-m3 int8 CPU, no API) | (OSS) | Active; pluggable cloud embeds |
| Basic Memory | 1 | **Markdown canonical** (frontmatter + wikilink graph); SQLite/Postgres index | Hybrid full-text + vector (local FastEmbed) | **Explicit** notes (LLM writes when asked); no transcript indexing | MCP ~18 tools + plugin briefings/checkpoints; many clients | Local-first or Postgres | (OSS) | Mature, broad client support |
| memory-bank-mcp | 1 | Plain markdown files; **no vectors/SQLite/semantic** | File read/list CRUD only | Curated documents (not captured history) | 5 file-CRUD MCP tools | Local-first (files) | (OSS) | Simple, curated-notes model |
| **memoirs** | 1 | SQLite + sqlite-vec single file (optional SQLCipher encryption) | Hybrid BM25(FTS5)+dense **RRF** + optional HippoRAG PageRank graph | Ingests CC transcripts **+ Cursor/ChatGPT/Claude.ai exports** (superset) | Native MCP 22 tools (stdio); many clients | Fully local (GGUF curator ~2GB, local embeds) | (OSS) | **Adds: sleep-time consolidation, PII redaction, ACLs, bi-temporal** |
| sqlite-vec | 1 | Zero-dep C SQLite extension (vec0 tables) | KNN match by distance | N/A (substrate) | SQLite extension | Fully local, portable | (OSS) | The primitive under episodic + memoirs |
| **Mem0** | 2 | Qdrant/pgvector + KV + graph edges | LLM extraction (gpt-5-mini) + BM25 + semantic + entity fusion; single-pass v3 | **LLM-distilled facts** w/ valid_at/invalid_at | SDK (Py/Node/Go) + REST + CLI + agent skills | Dual (lib local; self-host; cloud) | MIT + SaaS | 58K stars; v3 (2026) 91.6 LoCoMo [contested] |
| **Letta (MemGPT)** | 2 | Postgres+pgvector (or SQLite+sqlite-vec/Pinecone/Redis) | Vector over archival; flat "bag + vector search"; agent paging via function calls | Incremental **summaries** + recursive eviction; passages | Agents-as-servers; REST + SDKs + CLI + visual ADE | Hybrid (local CLI; cloud API) | Apache-2.0 + cloud | Production; 11.9K stars; steep curve |
| **Zep/Graphiti** | 2 | Neo4j/FalkorDB/Neptune **temporal KG** (episodes/entities/edges) | Semantic + BM25 + **graph traversal**, no LLM re-rank; sub-200ms | **Entities + relationships** w/ bi-temporal valid_at/invalid_at | Graphiti OSS lib (3-line SDK) + Zep Cloud (SOC2/HIPAA) | Local-capable (self-host Neo4j) or cloud | Graphiti Apache-2.0; Zep proprietary | Production; arXiv-backed; benchmarks contested |
| **Cognee** | 2 | SQLite/Postgres + LanceDB + Kuzu/Neo4j (multi-backend) | Vector + graph traversal + text; auto-routes (NEURAL/ENTITY/HYBRID) | **ECL pipeline** → typed entities + edges | Py SDK + FastAPI + CLI + CC plugin + OpenClaw plugin + MCP | Local-first default (SQLite/LanceDB/Kuzu on-device) | Apache-2.0 + cloud | Beta v1.1.2; 17.8K stars; weak temporal |
| Academic (Engram/HORMA/etc.) | 2 | Topic docs / gist streams / hierarchy / bi-temporal KG / event logs | Semantic nav / gist / hierarchy traversal / temporal KG / log seq | Consolidation, hierarchy, contradiction-resolution | Research PoCs (arXiv) | Fully local | Academic/MIT | Early research; not production |
| MemU | 2 | Postgres+pgvector or in-memory | OpenAI embed-3-small (pluggable); 3-layer (resource→item→category) | Auto-extract facts/skills/preferences (modality-aware) | Py SDK; async memorize/retrieve/forget/improve | Hybrid (cloud memu.so) | Apache-2.0 | Emerging 2026; vendor 92% LoCoMo [claim] |
| Memobase | 2 | Postgres w/ RLS (cloud) or SQLite (local) | Vector + graph hybrid; MCP tool interface | "**Dream phase**" distillation of session logs | MCP-native + HTTP hooks + dashboard | Hybrid | Proprietary SaaS + local SQLite | Funded startup; production MCP |
| **ChatGPT Memory** | 3 | Proprietary cloud | **No embeddings** — 4-layer plain-text context injection | Distilled user facts (~30) + lightweight convo summaries + current session | Closed; web UI only; "dreaming" invisible | Cloud only | Proprietary | Production; recall ~41%→~68% w/ dreaming [vendor] |
| **Claude Memory** | 3 | Proprietary cloud (Anthropic) | Tool-based (conversation_search, recent_chats); vector details undisclosed | 24h synthesis → distilled **summaries** | Web UI + Projects + API memory_20250818 tool (beta) | Cloud only | Proprietary | Prod Sept 2025; all users Mar 2026 |
| **Gemini Memory** | 3 | Google Cloud; user_context distilled doc + session window | Model-driven contextual injection (no documented vectors) | **Distilled facts with rationales** (sectioned: demo/interests/relationships/events) | In-product UI; trigger-phrase gated; enterprise REST/ADK | Cloud only (consumer) | Proprietary | Production, billions of users |
| **GitHub Copilot Memory** | 3 | GitHub cloud (DB undisclosed); separate local VS Code memory tool | Citation-based retrieval; **just-in-time verification** vs current code; session-start injection | Repo-scoped **facts tied to file:line citations** | GitHub-native (cloud agent + review + CLI shared pool); no MCP/API | Hybrid but **not** local-first | Proprietary | Public preview Mar 2026; ~7% PR-merge lift [vendor] |

---

## Ring 1 — Claude Code memory plugins

These are the nearest neighbours. Same transcript source (`~/.claude/projects` JSONL, `~/.codex/sessions`), same hook lifecycle, same MCP delivery channel. If a drop-in or fork-able reference exists, it is in this ring.

### episodic-memory (the baseline)

**Storage.** SQLite via `better-sqlite3` with a `sqlite-vec` `vec0` virtual table at 384 dimensions. Alongside the DB it keeps a raw JSONL archive and per-conversation AI-summary sidecar files under `~/.config/superpowers/`. The DB is the search index; the JSONL archive is the source-of-truth fallback; the summaries are an auxiliary layer.

**Embedding + retrieval.** Fully local — Transformers.js running `all-MiniLM-L6-v2` at v1.0.15, upgraded to `bge-small-en-v1.5` at v1.4.2 (both 384-dim, no API). An `embedding_version` column guards migrations so an encoder change triggers a safe re-embed rather than silently mixing vector spaces. Retrieval is vector KNN, plus plain-text SQLite `LIKE`, plus a hybrid multi-concept AND mode that aggregates several vector queries. It implements the BGE asymmetric query-prefix trick (retrieval prefix on queries only) for a documented retrieval-quality gain.

**Chunking.** The unit is a single `user→assistant` exchange. The user message, assistant message, and tool names are concatenated and truncated to 2000 chars before embedding. There is **no extraction** — text is indexed verbatim.

**Capture.** A SessionStart hook fires `sync --background`, which archives JSONL, embeds the new exchanges, and generates per-conversation haiku summaries (capped at 10 per run). Reentrancy is guarded (`EPISODIC_MEMORY_SUMMARIZER_GUARD`) so the summarizer subprocess doesn't recurse, and concurrency is handled with `proper-lockfile` rather than DB-level locking.

**Integration.** Two MCP tools only: `search` and `read`. A `search-conversations` haiku agent returns a ≤1000-word synthesis. The `remembering-conversations` skill dispatches search when recall is needed. Tightly coupled to the Claude Code / Codex harness.

**What it deliberately lacks.** No progressive-disclosure token budgeting, no proactive session-start injection, no graph/temporal layer, no consolidation/dedup/forgetting, no PII redaction. Memories accumulate monotonically and all exchanges are weighted equally.

**Read this as the philosophy, not just the implementation.** Episodic-memory's identity is *raw fidelity + locality + transparency*: it never loses nuance to a summary, it never phones home, and every stored item is inspectable verbatim. The cost is that it shifts the recall burden onto an explicit search call, grows without bound, and can't reason about contradiction or time. The fork is the question of which of these trades to revisit.

### claude-mem (thedotmack)

**Delta vs episodic-memory.** This is the *opposite write-time philosophy*. Where episodic-memory indexes raw transcript text *after* the fact, claude-mem captures tool-usage observations **live** via the full hook set (SessionStart, UserPromptSubmit, PostToolUse, Stop, SessionEnd) and AI-compresses them into **semantic summaries** that are then proactively re-injected into future sessions. It runs a dual store — SQLite for sessions/observations/summaries plus a Chroma vector DB for hybrid semantic+keyword search — and requires `uv` (Python) for the vector path. Its standout feature is **3-layer progressive disclosure**: `search` returns a compact ID index (~50-100 tokens), `timeline` gives chronological context, and `get_observations` returns full detail (~500-1000 tokens) *only* for filtered IDs — a claimed **~10x token saving [vendor claim, unverified]**. Heavier footprint: 5 JS hooks, MCP tools, an Express worker on port 37777, a React web viewer, and multi-agent expansion (Codex, Gemini, Copilot, OpenCode, OpenClaw). For the fork, claude-mem is the reference for *proactive injection* and *progressive disclosure* — two things episodic-memory entirely lacks.

### claude-qmd-sessions (wbelk)

**Delta vs episodic-memory.** A thin bridge, not a memory engine — it delegates all storage/embedding/search to the external `qmd` engine (`@tobilu/qmd` on Bun) and just converts `~/.claude/projects` JSONL transcripts to markdown plus wires hooks. Its capture is **lossy**: it extracts only user messages and assistant text, discarding tool_use, tool_result, and thinking blocks (episodic-memory keeps tool names). The valuable idea here is the **automatic post-compaction context reload**: on SessionStart (compact/resume/clear/startup) it re-injects CLAUDE.md plus the last ~50 exchanges (100 turns, capped at 14k chars, sorted by cwd match). That cwd-sorted re-injection is a concrete pattern episodic-memory could borrow for session continuity.

### memsearch (zilliztech)

**Delta vs episodic-memory.** Architecturally the most instructive Ring-1 sibling because it inverts the canonical/derived relationship. **Markdown daily-log files are canonical** (`.memsearch/memory/YYYY-MM-DD.md`); the Milvus vector index is a *disposable cache* rebuildable from the markdown. Episodic-memory treats the SQLite index as primary with JSONL as archive; memsearch treats human-readable markdown as primary with the vector store as throwaway. Retrieval is hybrid dense+BM25+RRF (default Milvus Lite is SQLite-based, indexing once at session start; Zilliz Cloud enables realtime watch). It also does **3-layer progressive disclosure inside a forked subagent**, and its summary chunks carry **HTML-comment anchors** (session id, turn uuid, transcript path) to drill back to verbatim JSONL — a clean provenance pattern. Capture: a Stop hook pipes each turn through `claude -p --model haiku` into 2-10 third-person bullet summaries appended to the daily markdown. Notably it is **local-first by default with no API/GPU** (ONNX bge-m3 int8 on CPU, ~558MB HF download, claimed **~1% below OpenAI text-embedding-3-small [vendor claim, unverified]**) and **deliberately ships no MCP server**. For the fork: memsearch is the reference for *human-readable canonical storage with a disposable index* and *provenance anchors*.

### Basic Memory (basicmachines-co)

**Delta vs episodic-memory.** The **inverse** of episodic-memory on the capture axis: it does **not** index transcripts at all. The LLM writes notes only when explicitly asked (`write_note`/`edit_note`). Plain Markdown files are canonical (frontmatter + categorized observations + wikilink relations forming a traversable graph), Obsidian-compatible, with a rebuildable SQLite (or Postgres) index. Retrieval is hybrid full-text + vector with local FastEmbed. The surface is rich — an MCP server with ~18 tools (`write_note`/`read_note`/`edit_note`/`search`/`build_context`, `memory://` URLs, project/schema/cloud tools) plus a Claude Code plugin adding session-start briefings, pre-compaction checkpoints, a capture output-style, and slash commands; clients span Claude Desktop/Cursor/VS Code/Codex/ChatGPT/Obsidian. Basic Memory is the reference for *explicit curated knowledge as a wikilink graph* — relevant if the Company wants intentional notes alongside automatic transcript memory. (It echoes the Company's own substrate/vault thinking.)

### memory-bank-mcp (alioshr)

**Delta vs episodic-memory.** The minimal end of the space — no embeddings, no vectors, no SQLite, no semantic search. Just plain markdown files in project dirs (`MEMORY_BANK_ROOT`) exposed through 5 file-CRUD MCP tools (`memory_bank_read`/`write`/`update`, `list_projects`, `list_project_files`). The agent does all the remembering by reading and writing curated notes. It's a useful floor reference: it shows how much of "memory" can be delivered with pure file CRUD and an agent that knows where to look — no retrieval machinery at all. Not a fork candidate, but a reminder that the simplest viable memory is sometimes "structured files + a convention."

### memoirs (misaelzapata)

**Delta vs episodic-memory — this is the closest functional superset and the strongest drop-in reference.** It uses the *same substrate* (SQLite + sqlite-vec, single portable file, with optional SQLCipher encryption-at-rest) and ingests the *same source* (Claude Code transcripts) — **plus** Cursor `state.vscdb`, ChatGPT zip exports, Claude.ai exports, JSONL, and Markdown via format auto-detect. On retrieval it goes well beyond episodic-memory: hybrid BM25 (FTS5) + dense fused with **Reciprocal Rank Fusion**, plus an optional **HippoRAG-style Personalized PageRank graph** for multi-hop, with `mcp_get_context` as the primary entrypoint. It ships a native MCP server with **22 tools** over stdio. Critically, it *already has the lifecycle features episodic-memory lacks*: **sleep-time consolidation** (dedup/link/prune), **PII redaction** (Presidio), **per-memory ACLs**, and **bi-temporal valid_from/valid_to** — all running fully local with local embeddings and a GGUF curator LLM (~2GB) via sentence-transformers/fastembed, no API. If the fork wants consolidation + temporal + graph + multi-source ingestion *without leaving the local SQLite+sqlite-vec world*, memoirs is the existing implementation closest to that target. **Caveat: per the "found-elsewhere ≠ replacement" rule, this informs the decision; it is not assumed to be a drop-in until its code is read against the Company's actual requirements.**

### sqlite-vec (asg017) — the substrate

**Not a memory system — the storage primitive under both episodic-memory and memoirs.** A zero-dependency pure-C SQLite extension that runs anywhere SQLite runs (including WASM/browser), exposing `vec0` virtual tables (float/int8/binary vectors) and KNN match clauses ordered by distance. It is loaded by the host app, no server. Its presence under both the baseline and the closest superset (memoirs) is the strongest signal in Ring 1: **the local-first SQLite+sqlite-vec foundation is proven for exactly this workload**, and a fork can keep it while changing everything above it (form, retrieval fusion, lifecycle).

---

## Ring 2 — Agent-memory frameworks

General-purpose memory layers. Not Claude-Code-shaped, but they hold the deepest design thinking on the form-of-memory and lifecycle axes — exactly where episodic-memory is thinnest.

### Mem0

**One line.** LLM-driven universal memory with multi-level state, single-pass fact extraction, entity linking, and hybrid (semantic + BM25 + entity) retrieval.

**Architecture.** Hybrid store: vector (Qdrant or pgvector default) + key-value metadata + graph edges for entity relationships. At query time an LLM (gpt-5-mini default) extracts facts and entities from the conversation; retrieval fuses BM25 keyword, semantic vectors (text-embedding-3-small default), and entity-mention matching, scored separately. The v3 algorithm (April 2026) is **single-pass ADD-only**. Each fact is a discrete memory unit with `valid_at`/`invalid_at` metadata for temporal reasoning, and the lifecycle handles update/delete/merge per fact.

**Delta vs episodic-memory.** The fundamental fork in the road: **extraction vs raw indexing.** Mem0 normalizes and deduplicates conversation into discrete structured *facts*; episodic-memory preserves verbatim exchange context. Mem0's memory decays via temporal reasoning; episodic-memory is append-only. Mem0 defaults to the OpenAI API; episodic-memory is local Transformers.js with no keys. Mem0 is multi-user (`user_id`) out of the box and offers a cloud sync path; episodic-memory is single-harness, local-only. Mem0's surface is SDK/API/CLI; episodic-memory is MCP. **What Mem0 contributes to the fork:** the single-pass extraction pattern (cheap, one LLM call) and the per-fact temporal validity model — *if* the fork decides facts are worth the extraction cost and the nuance loss.

**Maturity / contest.** 58K stars, heavy ecosystem integration, production deployments reported. Benchmark claims (91.6 LoCoMo for v3) are **contested by Zep** on methodology; Mem0 counters by emphasizing single-pass efficiency and entity-linking over raw recall. **Treat the number as disputed.**

### Letta (MemGPT)

**One line.** OS-inspired agent memory with a hierarchy (core / archival / recall), self-editing, Postgres+pgvector backend, and an agents-as-servers model for long-running stateful agents.

**Architecture.** Three tiers: core memory lives in the context window (default 128k as of v0.16.6); messages evicted beyond it are preserved in recall storage with **recursive summaries at eviction boundaries**; archival is vector storage. Agents actively *page* between tiers via function calls — they decide what to archive, evict, and summarize. Backends are pluggable (Postgres/pgvector primary, but also SQLite+sqlite-vec, Pinecone, Redis). Embeddings pluggable (OpenAI/Anthropic/Azure/Ollama/Vertex). Surface: REST API + Python/TS SDKs + a local CLI (Letta Code) + a visual Agent Development Environment for memory inspection.

**Delta vs episodic-memory.** Letta treats the *agent as a memory manager* — quota-aware, self-editing, eviction-deciding. Episodic-memory is "retrieve everything applicable, let the in-context LLM rank." Letta is production-multi-agent (Postgres durability, shared memory blocks, supervisor-worker patterns, conversation forking); episodic-memory is session-scoped hooks with no long-running process. **What Letta contributes:** the *recursive-summarization-at-eviction* idea and the *hierarchy* concept — but its own analysis in the research warns the forker explicitly: *don't adopt Letta's Postgres + external-embeddings + active-agent-memory-API complexity if you're building local-first.* Keep SQLite, add lifecycle (age/relevance pruning, session-chunk summaries) and frequency-weighted ranking, and let embedding search + in-context relevance do the work — that path is more aligned to episodic-memory's philosophy.

**Maturity.** Apache-2.0; 11.9K stars; 177+ releases; v0.16.7 (March 2026). Production-ready but a steep (hours-not-minutes) learning curve.

### Zep / Graphiti — temporal knowledge graph

**One line.** A bi-temporal knowledge-graph engine: facts get validity windows (when true, when superseded) in Neo4j/FalkorDB/Neptune, with hybrid (semantic + BM25 + graph-traversal) retrieval at sub-200ms.

**Architecture.** Graph schema: entities as nodes (with time-sensitive summaries), relationships as edges carrying explicit `valid_at`/`invalid_at`, and an episodes table holding raw ingested data for provenance. **Bi-temporal**: it tracks both when an event occurred *and* when it was ingested/updated. Retrieval combines semantic embeddings (pluggable: OpenAI default, Azure/Gemini/Voyage, local via Ollama/vLLM), full-text BM25, and native graph traversal — *with no LLM re-ranking at retrieval time*. Conflict detection uses semantic + keyword + graph search to decide whether new knowledge updates or invalidates an existing edge. FalkorDB backend is claimed 496x lower latency than Neo4j.

**Delta vs episodic-memory.** These solve *different problems*. Episodic-memory makes past developer conversations searchable (tactical: "remember what we discussed about X"). Zep/Graphiti maintains canonical operational memory where facts change over time (strategic: "what is the user's *current* preference, and how did we learn it"). For a forker wanting temporal-local-first, the research lists the concrete deltas: graph vs flat relational (consider SQLite-with-JSON for a lightweight graph rather than a full graph DB); extraction vs raw; conflict-handling (none vs timestamp-driven update-vs-invalidate); consolidation to prevent unbounded growth; provenance traceability from every edge back to its source episode; and real-time edge addition without re-embedding the whole graph.

**Maturity / contest.** Graphiti is Apache-2.0 OSS; Zep Cloud is proprietary (SOC2 Type II, HIPAA BAA). arXiv-backed (2501.13956). **Benchmarks are disputed** — a GitHub issue puts Zep's LoCoMo at 58.44% vs a claimed 84%, with Zep counter-claiming 75.14%. Healthy critical review, but no number here is settled.

### Cognee

**One line.** Open-source Python platform that builds self-hosted knowledge graphs from diverse sources via an ECL (Extract-Cognify-Load) pipeline, combining vector embeddings + typed graph reasoning.

**Architecture.** Hybrid multi-backend with a unified adapter interface: relational via SQLAlchemy (Postgres/SQLite, Alembic migrations), vector via LanceDB (default), graph via Kuzu (default, supports Neo4j), optional pgvector. The **ECL pipeline**: Extract (30+ multimodal connectors — PDF/HTML/images/audio), Cognify (LLM-driven structured extraction into typed nodes+edges via `instructor` validation), Load (normalized into all three stores). Search auto-routes via a `SearchType` enum (NEURAL/ENTITY/HYBRID). Surface: Py SDK (async `remember`/`recall`/`forget`/`improve`/`cognify`), FastAPI server, CLI, **an official Claude Code plugin** (with the full hook set — SessionStart/PostToolUse/UserPromptSubmit/PreCompact/SessionEnd), an OpenClaw plugin, and MCP tools.

**Delta vs episodic-memory.** Cognee extracts typed entities+relationships enabling multi-hop reasoning ("find all projects X worked on with technology Y"); episodic-memory excels at retrieval grounded in human reasoning ("what did we discuss about X?"). Cognee's `improve()` actively refines the graph via LLM feedback (tracked as `FeedbackEntry`); episodic-memory has no active consolidation. Both support local embeddings, but episodic-memory *forces* it (offline by design) while Cognee defaults to OpenAI with optional FastEmbed. **What Cognee contributes:** it is the closest *Ring-2* system that already ships a Claude Code plugin with the full hook lifecycle and a local-first default — a reference for *how a graph-extraction memory wires into the same harness episodic-memory uses.* Gap: weak temporal reasoning (structural-only on LongMemEval) and no SOC2/HIPAA.

**Maturity.** Apache-2.0; Beta v1.1.2 (Jan 2026); 17.8K stars; research paper (Markovic et al., arXiv:2505.24478).

### Academic frameworks (Infini Memory, ActiveMem, HORMA, Engram, ProjectMem)

**One line.** Emerging research (published ~June 2026) on episodic/semantic consolidation, topic hierarchies, distributed cognition, hierarchical organization, temporal KGs, and event-log governance — all fully local-first.

**The research direction, mapped to episodic-memory's gaps.** Every one of these targets something episodic-memory lacks. **Consolidation:** all of them emphasize fact/knowledge consolidation vs episodic-memory's append-only growth. **Hierarchy:** HORMA and Infini Memory organize hierarchically (file-system-like structure with summarized entities; topic-documents with plain-text hierarchy) vs episodic-memory's flat index. **Temporality:** Engram (atomic RDF S-P-O facts with supersession tracking) and ProjectMem (deterministic pre-action gate + event log) track temporal/causal windows vs episodic-memory's timestamp-only. **Governance:** ProjectMem's *pre-action gate* is a novel fail-safe with no episodic-memory analogue. **Topic models:** Infini Memory's topic hierarchy vs episodic-memory's project/session filters. **Contradiction handling:** Engram explicitly resolves fact conflicts; episodic-memory stores all versions. A forker adding HORMA-style hierarchical consolidation would need automatic multi-scale summarization, entity dedup, a hierarchy-construction algorithm, and evolution tracking. **These are the "next generation" — useful as a direction-of-travel signal, not as production code (research-grade Python PoCs, not SDKs).**

### MemU & Memobase (2026 entrants)

**MemU.** Three-layer hierarchical extraction (resource→item→category retrieval), PostgreSQL+pgvector (or in-memory dev), OpenAI embed-3-small (customizable via Voyage/Aliyun/custom). Automatic modality-aware extraction (conversation/document/image/video/audio) into cross-referenced facts/skills/preferences with zero manual tagging; offers both a fast RAG method and a deep LLM-reasoning method. Apache-2.0. Vendor-claimed 92.09% LoCoMo **[claim]**.

**Memobase.** Graph-vector hybrid, MCP-native delivery (Claude Code/ChatGPT/Cursor compatible), PostgreSQL with row-level security (multi-tenant) or local SQLite. Its signature is the **"dream phase"** — a background distillation that converts noisy session logs into high-signal insights — plus HTTP-hook event capture and a management dashboard. Proprietary SaaS with a local SQLite mode.

**Delta vs episodic-memory.** Both extract (vs raw) and lean on PostgreSQL+network for their full form. Memobase's RLS multi-tenancy is the inverse of episodic-memory's single-user-per-SQLite design. **What they contribute:** MemU's three-layer resource→item→category hierarchy is another progressive-disclosure variant; Memobase's "dream phase" is a clean name and pattern for *background distillation as a separate phase* (the same idea ChatGPT calls "dreaming").

---

## Ring 3 — Major AI product memory

The closed systems. Opaque internals, but they reveal what the largest teams chose under real scale pressure — and the public criticism reveals the failure modes.

### ChatGPT Memory

**Architecture.** Strikingly, **no embeddings and no semantic search.** Instead, four fixed context layers are prepended as plain text to *every* user message: (1) session metadata (device/location/account), (2) user memories (explicit facts, ~30-33 per user), (3) lightweight conversation summaries (titles + timestamps + user-message snippets, ~15-40 recent chats), and (4) the current session transcript until token limits. OpenAI traded vector-similarity complexity for speed via full-context injection — *which they can afford because they own both the model and the injection point.* "Dreaming" (automatic background memory synthesis) runs invisibly server-side; OpenAI reports factual recall improving from **~41.5% to ~67.9% [vendor claim]** with the dreaming architecture.

**Delta vs episodic-memory & lessons.** **Borrowable:** the explicit *multi-layer context architecture* (ephemeral metadata / permanent facts / recent summaries / current session — clean separation worth mirroring in any injection design); *automatic salience detection* via background synthesis rather than asking the user; a *"save as memory" toggle* to distinguish high-confidence user-provided facts from inferred patterns; and *proactive session-start injection*. **Inapplicable:** ChatGPT prepends *all* layers to *every* message (only viable because they own the stack and eat the latency/cost); its distilled summaries lose granularity that episodic-memory's raw exchanges preserve; and its memory dossier is *invisible and uneditable* — **Simon Willison criticised exactly this opacity**, which makes episodic-memory's full inspectability a genuine design strength, not a gap.

### Claude Memory (Claude.ai)

**Architecture.** Cloud-only (Anthropic infra). Tool-based retrieval (`conversation_search`, `recent_chats`); embedding/vector internals undisclosed. Automatic 24-hour synthesis compresses history into distilled summaries ("you prefer Postgres"). Memory injects *implicitly* at session start (the user sees no tool calls). Per-project memory isolation is a team feature. There's an Incognito mode to opt out, and the API exposes a `memory_20250818` tool (beta, requires the `context-management-2025-06-27` header).

**Delta vs episodic-memory & lessons.** The foundational trade-off stated plainly: Claude Memory **distills** (compresses, loses nuance) while episodic-memory preserves **raw** exchanges + metadata (richer, larger, captures trade-offs). Claude injects implicitly (transparent-feeling but uncontrollable); episodic-memory's search is explicit and auditable. Claude gates search behind a paid tier with a 24h refresh delay; episodic-memory is instant, local, free. **Borrowable for the fork:** automatic *periodic* (e.g. daily) batch summarization; per-project isolation to avoid cross-context pollution; an incognito/opt-out mode (episodic-memory's "DO NOT INDEX" marker is the local analogue); a user-facing memory view/edit surface (Claude.ai has one; episodic-memory is CLI/MCP only); and exposing memory as an *API tool* (not just MCP). **Doesn't apply:** cloud storage, implicit injection, pay-per-query, auth-gated incognito, server-side summarization — local-first inverts all five.

### Gemini Memory (Google)

**Architecture.** Cloud-native. Two tiers: a `user_context` document (periodic LLM distillation into structured sections — demographics, interests/technologies, relationships, dated events/projects, **each statement carrying a citation rationale**: which conversation, when) plus the current session window. No documented embeddings — retrieval is model-driven contextual injection. Personalization is **trigger-phrase gated** ("based on what you know about me"), with a strict "MASTER RULE: DO NOT USE USER DATA" default-off posture. Enterprise Memory Bank lets admins define custom memory-topics (taxonomies of what to remember).

**Delta vs episodic-memory & lessons.** **Borrowable:** the *distilled-facts-with-rationales* structure (sectioned profile + source citations) makes memory inspectable, trustworthy, debuggable — episodic-memory could adopt this for its summary layer; the *section-based taxonomy* (demo/interests/relationships/events); and *source-citation transparency* (which episodic-memory already half-has via archive_path + line ranges). **Inapplicable:** cloud lock-in, cross-service scraping (Gmail/Drive/Calendar), and PII-via-differential-privacy-in-cloud (local-first sidesteps the transmission problem entirely). **Most design-relevant Google artifact:** the open-source **Always On Memory Agent** reference (MIT) — *not* the consumer product — which deliberately **ditches vector databases**, using SQLite + direct LLM reasoning for continuous consolidation, background processing, and active forgetting-by-connection-finding. That philosophy (consolidation-as-active-thinking, no vector DB) is *closer to episodic-memory's substrate* than the consumer Gemini product is, and is worth studying directly.

### GitHub Copilot Memory

**Architecture.** GitHub-cloud-hosted (DB undisclosed), plus a *separate* local file-based memory tool inside VS Code agents. Stores repo-scoped facts and user preferences as structured observations **tied to file:line citations**. Two patterns stand out: **citation validation** (facts reference specific code locations, verified at runtime against the *current* branch — stale knowledge is caught before injection) and **just-in-time verification** (agents validate facts on-the-fly rather than via an offline curation pipeline). Memory auto-expires after **28 days unused**; usage resets the timer (LRU-style). Distillation happens via *agent self-healing* — agents correct and re-store bad facts, no separate distillation module. The cloud memory is a shared pool across the coding agent, code review, and CLI. Reported ~7% PR-merge-rate lift **[vendor claim]**.

**Delta vs episodic-memory & lessons.** **Borrowable, and several are genuinely novel here:** (1) *citation tying* — associate recalled turns with project/file/decision-point; (2) *automatic expiration with usage-reset* — age-based LRU eviction to prevent the unbounded-growth problem episodic-memory has; (3) *just-in-time verification* — check a fact against current state before injecting it (directly addresses the "stale memory" failure mode); (4) *cross-agent shared pool* — episodic insights flowing between tools; (5) *proactive first-N-lines auto-load at session start*; (6) *distillation via self-healing* rather than a separate pipeline. **Inapplicable:** the cloud assumption, GitHub-org-tied billing/permissions, and the secrets-leakage risk of storing code citations unencrypted in cloud. **Key framing difference:** Copilot's "facts" are repo-wide patterns for *multi-agent learning*; episodic-memory's "memories" are user-specific *continuity* (sessions, decisions, why). For the fork: borrow citation-tying, expiration/LRU, and JIT validation — but keep storage local, give the user control over what's remembered, and make export/import first-class.

---

## Design lessons for Tim's local-first fork

This is the payoff. Not a single recommended architecture — the design space, with the trade-offs made explicit, so the build decision is made with the whole map visible. Each axis below is a genuine fork in the road.

### (a) The form of memory: raw transcript vs LLM-distilled facts vs summaries

This is **the** decision; everything else follows from it.

- **Raw transcript (episodic-memory, memoirs):** verbatim exchanges indexed as-is. *Pro:* zero extraction cost, zero nuance loss, captures trade-offs and the *why* behind decisions, fully inspectable, no hallucination surface (you can only retrieve what was literally said). *Con:* unbounded growth, every exchange weighted equally, no contradiction reasoning, retrieval quality depends entirely on ranking.
- **LLM-distilled facts (Mem0, MemU, ChatGPT, Gemini, Copilot):** an LLM extracts discrete facts/preferences/entities. *Pro:* compact, dedupable, supports update/delete/merge and temporal validity, smaller token footprint at injection. *Con:* extraction cost (LLM call per ingest), *nuance loss* (a fact is a lossy compression of a conversation), and a hallucination/misextraction surface.
- **Summaries (claude-mem, memsearch, Letta, Claude.ai, Memobase "dream"):** a middle ground — AI-compressed prose, not atomic facts. *Pro:* readable, cheaper than full transcript at injection, preserves more narrative than facts. *Con:* still lossy, still a generation cost.

**Opinionated read:** episodic-memory's raw philosophy is *correct for the Company's use case* — the value is in decision rationale and trade-offs ("why we chose X"), which distillation destroys. But raw and distilled are **not mutually exclusive**, and the strongest systems run *both layers*: raw exchanges as the searchable ground truth + a thin distilled/summary layer for cheap proactive injection. This is the "keep raw, *add* a derived layer" path (memsearch's anchored summaries, Claude.ai's daily synthesis, ChatGPT's 4-layer model all do versions of this). **The fork should preserve raw indexing and add a derived summary layer on top — not replace one with the other.**

### (b) The store: single embedded SQLite vs dual-store vs graph/temporal

- **Single SQLite + sqlite-vec (episodic-memory, memoirs):** one portable file, no services, runs anywhere SQLite runs, offline. The fact that *both* the baseline and its closest superset (memoirs) chose this — and that sqlite-vec is the proven primitive under both — is the strongest signal in the survey. **Strong recommendation: keep this.** It is the Company's local-first ethos in storage form.
- **Dual-store (claude-mem SQLite+Chroma, Mem0 vector+KV+graph):** separate vector DB. *Cost:* an extra service/dependency (claude-mem's `uv` requirement, the :37777 worker) for marginal retrieval gains a fused FTS5+sqlite-vec setup can largely match.
- **Graph/temporal (Zep/Graphiti, Cognee, Engram):** Neo4j/FalkorDB/Kuzu for entity-relationship traversal and bi-temporal validity. *Powerful but heavy* — and the research explicitly notes you can get a *lightweight* graph with **SQLite-plus-JSON edges** rather than a full graph DB, if multi-hop reasoning becomes a requirement. **Don't reach for Neo4j; reach for edges-in-SQLite first.**

### (c) Delivery: on-demand search vs proactive session-start injection

Episodic-memory is *pure on-demand* (explicit search call) — transparent and auditable, but the recall burden sits on the agent remembering to search. **Almost every other system injects proactively at session start** (claude-mem, claude-qmd's cwd-sorted re-injection, ChatGPT, Claude.ai, Copilot's first-N-lines, memsearch). The trade-off: proactive injection improves UX and continuity but spends tokens on possibly-irrelevant context and is less transparent. **The mature answer is both:** proactive injection of a *small, high-salience* layer at session start (the distilled/summary layer from (a)), with on-demand deep search (the raw layer) available when the agent needs more. This is precisely the gap episodic-memory flags in itself ("no proactive context injection at session start").

### (d) Progressive-disclosure token budgeting

The single most reusable *retrieval* pattern in Ring 1, and episodic-memory entirely lacks it. claude-mem (~50-100 tok ID index → timeline → full detail only for filtered IDs, claimed ~10x saving), memsearch (3-layer in a forked subagent), and MemU (resource→item→category) all implement the same shape: **return a cheap index first, fetch full detail only for what the agent selects.** This is low-cost to add to episodic-memory (its search already returns IDs) and high-value — it directly attacks the token cost of feeding conversation memory into context. **Strong recommendation: add this regardless of the other decisions.**

### (e) Integration surface: hooks vs MCP vs both

- **Hooks** (SessionStart/Stop/PostToolUse/etc.) drive *capture and injection* — the automatic, harness-native side. Episodic-memory uses SessionStart for sync; claude-mem and Cognee use the full set; memsearch uses 4 shell hooks.
- **MCP** drives *retrieval* — the agent-facing tool surface. Episodic-memory exposes 2 tools (search/read); memoirs 22; Basic Memory ~18.
- **The split is the right model:** hooks for the involuntary nervous system (capture, session-start injection), MCP for the voluntary muscle (agent-initiated search/read). episodic-memory already has both; the fork should *deepen* each (more hooks for proactive injection per (c); richer MCP tools per (d)) rather than pick one. **Note the Company law: every capability through the Company MCP — so the fork's retrieval surface should ultimately route through `mcp__company__`, not stand alone.** Memsearch's deliberate *no-MCP* choice is the outlier and the wrong fit for the Company.

### (f) Lifecycle: consolidation, forgetting, PII

This is episodic-memory's biggest functional gap (it names all of these as missing). The space:
- **Consolidation/dedup/prune:** memoirs (sleep-time consolidation), Letta (recursive eviction summaries), ChatGPT/Claude.ai ("dreaming"/24h synthesis), Memobase ("dream phase"), Cognee (`improve()`). The pattern is universal: *a background phase that compresses, dedupes, and links old memory.*
- **Forgetting / expiration:** Copilot's 28-day-unused LRU with usage-reset is the cleanest concrete mechanism for bounding growth. Episodic-memory grows forever; this is the antidote.
- **Staleness / contradiction:** Copilot's just-in-time citation re-verification and Zep/Engram's temporal invalidation (`valid_at`/`invalid_at`) handle "this used to be true." Episodic-memory stores all versions with no notion of supersession.
- **PII:** memoirs ships Presidio redaction. Local-first sidesteps the *transmission* risk but not the *at-rest* risk — memoirs also offers SQLCipher encryption-at-rest. Worth adopting both if the corpus holds sensitive material.

**Opinionated read:** consolidation and bounded-growth (a background "dream phase" + LRU/age expiration) are the highest-value lifecycle additions; temporal invalidation matters only if the fork moves toward facts (a); PII redaction + at-rest encryption are cheap insurance memoirs already implements.

### (g) Closest drop-in references — what each contributes

- **memoirs** — *the closest functional target.* Same substrate (SQLite + sqlite-vec, single file), same source (Claude Code transcripts) plus multi-source ingestion, and it *already implements* RRF hybrid retrieval, optional HippoRAG graph, sleep-time consolidation, PII redaction, ACLs, and bi-temporal validity — all fully local. If the fork wants episodic-memory's philosophy *plus* the lifecycle and retrieval features it lacks, **memoirs is the existing code to read first.** (Per "found-elsewhere ≠ replacement": this *informs* the decision; only a code-read against the Company's actual requirements confirms drop-in fitness.)
- **claude-mem** — *the reference for the two patterns episodic-memory most lacks:* proactive session-start injection and 3-layer progressive disclosure. Its dual-store and :37777 worker are weight to avoid, but its retrieval-disclosure design is the model to copy.
- **memsearch** — *the reference for human-readable canonical storage* (markdown canonical, vector index disposable) and **provenance anchors** (HTML comments linking summary chunks back to verbatim JSONL). Its no-API local ONNX embedding path also confirms episodic-memory's local-first embedding choice is viable and competitive.
- **Cognee** — *the reference for how a graph-extraction memory wires into the same Claude Code harness* (official plugin, full hook lifecycle, local-first default) — relevant only if the fork moves toward entities/graphs.
- **Google's Always On Memory Agent (MIT)** — *the reference for consolidation-without-vectors* (SQLite + LLM reasoning, active forgetting) — a philosophically aligned, fork-friendly study even though it's not Claude-Code-shaped.

**The shape of the decision.** The fork lives on a spectrum from "episodic-memory exactly as-is" to "memoirs-class system." The minimal high-value move — preserve raw SQLite+sqlite-vec local indexing, *add* progressive disclosure (d), *add* a thin proactive-injection summary layer (c), and *add* bounded-growth lifecycle (f) — gets most of the value without touching the extraction/graph/temporal complexity. The maximal move — adopt facts + a lightweight SQLite-edge graph + bi-temporal validity — is justified only if the Company needs multi-hop "who/what/when" reasoning over memory, which is a separate, later question. **The recommendation is to start from the minimal move and treat extraction/graph as a deliberate second decision, not a default.**

---

## Sources appendix

### Ring 1 — Claude Code memory plugins (primary-source READMEs, unaudited)

- claude-mem: https://github.com/thedotmack/claude-mem
- claude-qmd-sessions: https://github.com/wbelk/claude-qmd-sessions
- memsearch: https://github.com/zilliztech/memsearch
- Basic Memory: https://github.com/basicmachines-co/basic-memory
- memory-bank-mcp: https://github.com/alioshr/memory-bank-mcp
- memoirs: https://github.com/misaelzapata/memoirs
- sqlite-vec: https://github.com/asg017/sqlite-vec
- episodic-memory (baseline): https://github.com/obra/episodic-memory · README, CLAUDE.md, docs/SCHEMA.md, src/{embeddings,search,indexer,db,parser}.ts, package.json (local: /home/tim/episodic-memory/)

### Ring 2 — Agent-memory frameworks (fresh primary + secondary)

- Mem0: https://github.com/mem0ai/mem0 · https://mem0.ai · https://docs.mem0.ai
- Letta (MemGPT): https://github.com/letta-ai/letta · https://docs.letta.com · https://letta.com/ · https://github.com/cpacker/MemGPT · https://arxiv.org/pdf/2310.08560 · https://huggingface.co/papers/2310.08560
- Zep / Graphiti: https://github.com/getzep/graphiti · https://getzep.com · https://www.getzep.com · https://github.com/getzep/zep · https://arxiv.org/abs/2501.13956 · https://help.getzep.com/graphiti/getting-started/overview · https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/ · https://www.falkordb.com/blog/building-temporal-knowledge-graphs-graphiti/ · https://github.com/getzep/zep-papers/issues/5 · https://atlan.com/know/zep-vs-mem0/ · https://codex.danielvaughan.com/2026/03/30/graphiti-agent-memory-store/ · https://callsphere.ai/blog/vw3g-zep-memory-v2-temporal-knowledge-graph-graphiti-2026 · https://medium.com/@whynesspower/complete-guide-to-knowledge-context-graphs-via-zep-graphiti-c6da7ce8b13b
- Cognee: https://github.com/topoteretes/cognee · https://raw.githubusercontent.com/topoteretes/cognee/main/README.md · https://raw.githubusercontent.com/topoteretes/cognee/main/pyproject.toml · https://api.github.com/repos/topoteretes/cognee · (arXiv:2505.24478, Markovic et al.)
- MemU: https://github.com/NevaMind-AI/memU
- Memobase: https://www.memobase.ai
- Academic (Infini Memory / ActiveMem / HORMA / Engram / ProjectMem): https://arxiv.org/search/?query=agent+memory&searchtype=all
- Cross-cutting surveys: https://particula.tech/blog/agent-memory-frameworks-tested-mem0-zep-letta-cognee-2026 · https://graphlit.com/blog/survey-of-ai-agent-memory-frameworks · https://vectorize.io/articles/best-ai-agent-memory-systems · https://stevekinney.com/writing/agent-memory-systems · https://dev.to/agdex_ai/ai-agent-memory-in-2026-mem0-vs-zep-vs-letta-vs-cognee-a-practical-guide-cfa · https://medium.com/tag/agent-memory

### Ring 3 — Major AI product memory (fresh primary + secondary)

- ChatGPT Memory: https://shloked.com/writing/chatgpt-memory-bitter-lesson · https://simonwillison.net/2025/May/21/chatgpt-new-memory/ · https://embracethered.com/blog/posts/2025/chatgpt-how-does-chat-history-memory-preferences-work/ · https://manthanguptaa.in/posts/chatgpt_memory/ · https://llmrefs.com/blog/reverse-engineering-chatgpt-memory · https://openai.com/index/chatgpt-memory-dreaming/ · https://openai.com/index/memory-and-new-controls-for-chatgpt/ · https://pcworld.com/article/3158111/ · https://www.searchenginejournal.com/chatgpt-expands-memory-capabilities-remembers-past-chats/544164/
- Claude Memory: https://www.shloked.com/writing/claude-memory · https://simonwillison.net/2025/Sep/12/claude-memory · https://support.claude.com/en/articles/11817273-use-claude-s-chat-search-and-memory-to-build-on-previous-context · https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool · https://xtrace.ai/blog/claude-memory-2026-limits-and-fixes · https://www.shareuhack.com/en/posts/claude-memory-feature-guide-2026 · https://blog.fsck.com/2025/10/23/episodic-memory/ · https://www.digitalapplied.com/blog/agent-memory-architectures-vector-graph-episodic · https://dev.to/blockmandev/i-built-a-free-self-hosted-memory-system-for-claude-cli-replaces-supermemory-mem0-zep-4dca
- Gemini Memory: https://www.shloked.com/writing/gemini-memory · https://docs.cloud.google.com/gemini/enterprise/docs/configure-personalization · https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/memory-bank · https://medium.com/@rushikeshchavan_99600/inside-geminis-memory-context-user-profiles-and-personalization-87bc1ae4ba18 · https://venturebeat.com/orchestration/google-pm-open-sources-always-on-memory-agent-ditching-vector-databases-for · https://www.welcome.ai/content/googles-always-on-memory-agent-redefines-ai-architecture-and-cost-efficiency · https://github.com/GoogleCloudPlatform/generative-ai/tree/main/gemini/agents/always-on-memory-agent · https://www.anuma.ai/blog/gemini-memory · https://support.google.com/gemini/answer/16598469 · https://knowledge.workspace.google.com/admin/gemini/google-workspace-with-gemini
- GitHub Copilot Memory: https://docs.github.com/en/copilot/concepts/agents/copilot-memory · https://github.blog/ai-and-ml/github-copilot/building-an-agentic-memory-system-for-github-copilot/ · https://github.blog/changelog/2026-03-04-copilot-memory-now-on-by-default-for-pro-and-pro-users-in-public-preview/ · https://github.blog/changelog/2025-12-19-copilot-memory-early-access-for-pro-and-pro/ · https://github.blog/changelog/2026-01-15-agentic-memory-for-github-copilot-is-in-public-preview/ · https://docs.github.com/en/copilot/how-tos/use-copilot-agents/copilot-memory · https://code.visualstudio.com/docs/copilot/agents/memory · https://www.kenmuse.com/blog/understanding-agentic-memory-in-github-copilot/ · https://deepwiki.com/obra/episodic-memory · https://dev.to/mosiddi/memory-is-an-action-not-a-database-reflections-on-github-copilots-new-agentic-system-hpa · https://medium.com/@mrBallistic/how-to-give-github-copilot-a-photographic-memory-and-a-kiro-style-brain-3eafeafa4b85 · https://www.nadcab.com/blog/ai-copilot-memory-systems-automation · https://www.lyzr.ai/blog/ai-agent-memory-types/ · https://pieces.app/blog/best-ai-memory-systems · https://techcommunity.microsoft.com/blog/microsoft365copilotblog/introducing-copilot-memory-a-more-productive-and-personalized-ai-for-the-way-you-work/4432059
