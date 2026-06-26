# Migration Register — Nine Home-Level Folders → `company/migration-pending/`

**Compiled:** 2026-06-26 · **Author:** Lead (Claude Code session)
**Purpose:** Exhaustive accounting of nine scattered folders before they are moved from `/home/tim/<name>` into `/home/tim/company/migration-pending/<name>`. Records what each folder IS, when it was made, what's in it, every outbound dependency, and **every inbound reference that would break on the move.** Stage-1 of a two-stage consolidation; Stage-2 (full company scan + digest + refactor) is separate.

---

## 0. THE MOVE-SAFETY SPINE (read this first)

The move changes each folder's absolute path. Therefore **every absolute-path reference to `/home/tim/<folder>` breaks on move** — whether inbound (from `~/company`, configs, systemd) or between the nine folders. The discriminating question for each folder is: *does anything in the live, running system read this path?*

### Folders that BREAK the running system if moved as-is — DO NOT MOVE without remediation

| Folder | What breaks | Evidence | Fix before/instead of moving |
|---|---|---|---|
| **corpora** | The Claude-session memory circuit — **scheduled every 20 min** by systemd timers bound to `company.target`. Four live code paths default to `~/corpora/claude-sessions`; the env override `CLAUDE_SESSIONS_CORPUS` is **not set anywhere**. Also the `claude-platform-docs` Chroma index path. | `ops/wire_substrate_claude_sessions.py:73`, `ops/claude_sessions_reindex.py:74`, `runtime/session_search.py:73`, `ops/transcript_search.py:38`; `ops/agent_sessions_exporter.py:56` writes here; systemd `company-agent-sessions-exporter.timer` (`OnCalendar=*:00/20`) + reindex timer | Either **exclude corpora from the move** (it's a live data store, not a code module), OR set `CLAUDE_SESSIONS_CORPUS=/home/tim/company/migration-pending/corpora/claude-sessions` in the service units AND repoint the platform-docs index. |
| **foundation** | The `model_of_tim` cognition node — reads `~/foundation/system/principles.md` at run() time, fail-loud (`ValueError`) if missing. Env override `COMPANY_MODEL_OF_TIM` is **not set**. | `nodes/model_of_tim.py:16` | Either **exclude foundation from the move**, OR set `COMPANY_MODEL_OF_TIM=/home/tim/company/migration-pending/foundation/system/principles.md`. |

### Folder that breaks a build-loop (not the always-on system) if moved

| Folder | What breaks | Evidence | Fix |
|---|---|---|---|
| **company-cognition** | The `cognition-build` skill hardcodes `/home/tim/company-cognition` as the worktree REPO + state/lock paths. Cron-invokable; the path goes stale on move. **RESOLVED:** the folder is only an abandoned Vite stub — the real specs live safely in `~/company/build-prep/concurrent-cognition/`; the worktree the skill expects is not currently registered. See §1.6. | `~/.claude/skills/cognition-build/SKILL.md:6,7,9` | Stub is disposable (zero unique content). If the build is to be resumed, point the skill at a fresh worktree; if dormant, retire stub + leave/update skill. |

### Folders SAFE to move (no live-code break) — repairs are cosmetic/doc-only

`wizard-run-1`, `mcp-mining`, `company-scan`, `recollection`, `ui-contract` (home-level), `runtime` (home-level).
- **recollection**: NOT a registered/running MCP server (confirmed absent from all 38 mcpServers in `.claude.json` and from any `.mcp.json`). Its data lives at `~/.recollection` (1.2 GB, separate) and does NOT move with the folder. Only consequence of move: stored corpus addresses `code:///home/tim/recollection/...` in the company store go stale (data, not code).
- **ui-contract / runtime (home-level)**: dead older snapshots shadowing live richer namesakes inside `~/company`. Zero inbound references to the home-level paths. (Details §collisions.)

---

## 1. PER-FOLDER INVENTORY

### 1.1 wizard-run-1 — `/home/tim/wizard-run-1`
- **Created:** 2026-06-04 (earliest file) → 2026-06-09 (last). Single ~5-day prototype run.
- **Size/shape:** 59 MB, 57 files, flat. Not a git repo.
- **What it is:** A by-hand prototype of Tim's "Project→Product pipeline" run against the **ElevenLabs Wizard corpus** on the Windows mount. Self-contained Python toolkit + SQLite substrate (`wizard.db`) + accumulated data artifacts (jsonl/txt aggregates) + 3 narrative docs (`BUILD_PLAN.md`, `FINDINGS.md`, `SESSION_FIELD_REPORT.md`). Explicitly framed as a prototype of capabilities that "should become Company engine node-types / MCP tools."
- **Key files:** `db.py` (SQLite schema), `fleet.py` (local-4B→embed→cloud cascade caller), `capture2.py` (current projection-based orchestrator; `capture.py` superseded), `scan/embed/cluster/dedup/extract/code_extract/form_survey/latent_cluster/target_extract.py` (pipeline passes), `registries/{projections,prompts,markdown_lifters}.json`, `carve.json` (44 sub-system clusters), `embed.jsonl` (46 MB bge-m3 vectors), `wizard.db` (1.6 MB, 99-file calibration sample) + 2 archived db snapshots.
- **Outbound deps:** Reads corpus ROOT `/mnt/c/Users/Workstation001/Documents/Claude/Projects/Visual Designer` (hardcoded in every script). Self-paths via `~/wizard-run-1/...` (expanduser). Model servers: vLLM 4B `:8000`, bge-m3 `:8001`, Ollama `:11434`. Launch scripts in `~/vllm-tests/`. Models: `cyankiwi/Qwen3.5-4B-AWQ-4bit`, `BAAI/bge-m3`, `kimi-k2.6:cloud`.
- **Sibling coupling:** NONE. No references to any of the other 8 folders or to `~/company`.
- **Inbound refs:** Only a comment in `runtime/projections.py:36` (schema was mined from here, then inlined) + 2 plan docs. **No live-code break.**
- **Breaks on move:** Re-running requires fixing `~/wizard-run-1/` hardcodes + corpus present + model servers up. As an archive, the data is fully portable.

### 1.2 mcp-mining — `/home/tim/mcp-mining`
- **Created:** 2026-05-30 22:54 → 2026-05-31 09:53. One overnight run.
- **Size/shape:** 59 MB, 17 files, flat. Not a git repo.
- **What it is:** Despite the name, **nothing to do with MCP** (`orchestrate.py`: "NO MCP framing"). A completed conversation-mining pipeline: reads Tim's entire Claude Code history (`~/.claude/projects/**/*.jsonl`), embeds + clusters it, and writes an emergent Obsidian vault "Conversation-Mind." Dead/completed artifact (`status.json` = `enrich-done`).
- **Key files:** `extract_tim_prose.py` (pulls Tim's messages → `tim_messages.jsonl`, 18.9 MB / 4858 msgs), `orchestrate.py` (6-phase read→embed→cluster→synthesize→self-direct→assemble), `enrich.py`/`enrich2.py`/`regen_dialectics.py` (round-2 dialectics), `embeddings.npy` (39.8 MB), `extracted.jsonl`, `clusters.json`, `sub_meta.json` (151 subtopics, 24 themes).
- **Outbound deps:** Reads `~/.claude/projects` (system-wide history). Writes Windows vault `/mnt/c/Users/Workstation001/Documents/Conversation-Mind`. Self-path `~/mcp-mining` (expanduser, **not** script-relative). Models: vLLM 4B `:8000`, bge-m3 `:8001`, Ollama cloud `:11434` (deepseek-v4-pro/kimi/glm). systemd `--user` vllm services. Deps: numpy, sklearn, sentence-transformers.
- **Sibling coupling:** NONE (it does read the `-home-tim-foundation` project history, but only as one of many `~/.claude/projects` folders, not by folder path).
- **Inbound refs:** ZERO. **Safe to move.**
- **Breaks on move:** Re-run would point back at old `~/mcp-mining` (expanduser hardcode). As data, fully portable.

### 1.3 company-scan — `/home/tim/company-scan`
- **Created:** 2026-06-01, single ~2.5-hour session.
- **Size/shape:** 9.4 MB, 12 files. Not a git repo.
- **What it is:** A forensic discovery/mapping tool. 2-pass local-4B pipeline that inventoried a Windows project tree (19,361 files) and reconstructed the design of the abandoned ElevenLabs Wizard project. Pass 1 (`scan_projects.py`→`build_index.py`) → `PROJECTS-LANDSCAPE.md`; Pass 2 (`extract_design.py`→`synth_design.py`) → `DESIGN-DIGEST.md`.
- **Key files:** `scan_results.jsonl` (8.2 MB / 19,361 recs — the scan corpus), `scan_results.v1-broad.jsonl` (superseded v1 schema), `design_extracts.jsonl` (770 recs), the 4 scripts, 2 .md deliverables, 2 logs.
- **Outbound deps:** Scans `/mnt/c/Users/Workstation001/Documents/Claude/Projects`. Local model `localhost:8000` (`cyankiwi/Qwen3.5-4B-AWQ-4bit`). `extract_design.py` does `sys.path.insert(0, "/home/tim/company-scan")` + 10 hardcoded self-paths.
- **Sibling coupling:** NONE (the name "company-scan" ≠ scanning the company; it scans the Windows Projects tree). Zero references to `~/company` or any sibling.
- **Inbound refs:** ZERO. **Safe to move.**
- **Breaks on move:** 10 hardcoded `/home/tim/company-scan` paths in scripts need rewriting to re-run. Data deliverables portable.

### 1.4 foundation — `/home/tim/foundation`  ⚠️ BREAKS ON MOVE
- **Created:** 2026-05-27 (exchanges migrated in) → 2026-06-12 (exchange 20). mtimes; content dates begin 2026-05-26.
- **Size/shape:** 756 KB, 60 files, 5 dirs. Pure markdown+YAML, no code. Not a git repo.
- **What it is:** **The Company's persistent cross-session memory layer** — itself a Company component, not docs about one. Dual register (CQRS/event-sourcing): immutable verbatim **source layer** (`exchanges/` — Tim's actual dense messages + responses, 20 numbered files) + always-current **synthesis layer** (`system/` doctrine, `models/` model registry, `operations/` substrate ops). Caveat in the data: `TIM.md` and `system/` are parallel branches covering overlapping ground; neither is canonical (Tim hasn't reconciled them).
- **Key content:** `TIM.md` (68 KB root doc, branch A); `exchanges/` (verbatim source incl. 112 KB `20-the-convergence-object.md`); `models/` (18 per-model files + index); `operations/` (16 files: runtimes, cuda, systemd, ports, vram, model-swap…); `system/` (README, architecture, principles — branch B).
- **Outbound deps:** Internal `[[wikilinks]]` (relative). One outbound wire: exchange 20 → `~/company/build-prep/brain/CONVERGENCE-OBJECT.md` ("what this produced"). Absolute refs to `~/vllm-tests/serve.sh` (systemd-referenced launcher archive) and `~/.cache/huggingface/hub/*.gguf`. Describes (doesn't import) vLLM/Ollama/Open-WebUI, substrate-mcp, Qdrant, Chroma.
- **Sibling coupling:** Produced BY the founding conversations, not by a sibling pipeline. It is a SOURCE/SEED the company engine READS — not a consumer. Single concrete outbound wire to `~/company` (the convergence-object pointer).
- **Inbound refs (LIVE — BREAKS):** `nodes/model_of_tim.py:16` reads `~/foundation/system/principles.md` at runtime, fail-loud. Env `COMPANY_MODEL_OF_TIM` not set. Plus many doc/design-json citations (non-breaking).
- **Breaks on move:** (1) `model_of_tim` node — must set `COMPANY_MODEL_OF_TIM` or don't move. (2) Relative wikilink to `~/company/...CONVERGENCE-OBJECT` re-depths. (3) `operations/paths.md` self-description goes stale.

### 1.5 corpora — `/home/tim/corpora`  ⚠️ BREAKS ON MOVE (live, scheduled)
- **Created:** 2026-06-10 (platform-docs scraped) → 2026-06-12 (sessions exported).
- **Size/shape:** 93 MB, 1863 files. Pure data (1862 `.md` + 1 `.exporter_state.json`). Not a git repo.
- **What it is:** A read-only **reference corpus** in two parts — the "Claude Code Atlas." (1) `claude-platform-docs/` (42 MB, 811 .md — curated scraped mirror of platform.claude.com docs, `api/` = 84%). (2) `claude-sessions/` (52 MB, 1051 .md — exported Claude Code session transcripts in 35 project-named subdirs; `-home-tim/` biggest at 24 MB).
- **Outbound deps:** Only `.exporter_state.json` holds absolute paths (source `~/.claude/projects/...` → output `~/corpora/claude-sessions/...` — export bookkeeping). The .md files are self-contained.
- **Sibling coupling:** This is the **shared source corpus** — the INPUT that mcp-mining / company-scan / the dragnet recall-substrate indexer consume. Arrow points outward (corpora → consumers).
- **Inbound refs (LIVE — BREAKS):** 4 company code paths default to `~/corpora/claude-sessions` (see §0); driven by systemd timers every 20 min; `CLAUDE_SESSIONS_CORPUS` not set. `corpora/claude-platform-docs` is a Chroma-indexed path.
- **Breaks on move:** The session-memory circuit silently reads/writes the OLD empty path. **Strongest "don't move, or repoint env" case of all nine.**

### 1.6 company-cognition — `/home/tim/company-cognition`  ⚠️ see discrepancy
- **Created:** 2026-06-08 15:19 (single moment, untouched since).
- **Size/shape:** 28 KB, 2 files, 5 nested dirs. Not a git repo.
- **What it is (on disk NOW):** An **empty, abandoned Vite dependency-cache stub** — only `canvas/app/.vite/deps/{_metadata.json, package.json}`, both auto-generated, optimizing zero deps (`"optimized": {}`, empty-string lockfile hash). No source, no config, no app. Disposable build detritus.
- **✅ DISCREPANCY RESOLVED (2026-06-26):** This folder was **intended to be a git worktree** of the company repo (branch `concurrent-cognition`, own `.venv`, `canvas/app`) for the **Concurrent Cognition build loop** driven by `~/.claude/skills/cognition-build/SKILL.md`. That worktree is **NOT currently registered** — `git -C ~/company worktree list` shows only `main` + three `agent-*` worktrees, none named `concurrent-cognition`, and `~/company` has no `concurrent-cognition` branch. The folder is not a git repo. **Conclusion:** the worktree was never fully materialized (or was cleaned up), leaving only the `canvas/app/.vite/deps` cache the loop generated during a run. **The actual spec content is SAFE and lives at `~/company/build-prep/concurrent-cognition/`** (the binding triad: `Concurrent Cognition — {Completion Criteria, Implementation Guide, Research Synthesis}.md` + `DECISIONS.md` + `00-LANDSCAPE.md` + `01–06` + `broader/` + `review/` + `explore/`, dated 2026-06-07→11). **The home-level stub therefore holds ZERO unique content** — moving or deleting it loses nothing. Open decision for Tim: is the Concurrent Cognition build **dormant/abandoned** (then retire the stub + leave or update the skill), or **to be resumed** (then the loop will recreate a fresh worktree anyway — the stub is still disposable, but the skill's `REPO`/`STATE`/`TRIAD` paths at lines 6,7,9 should point at the new worktree location, not migration-pending).
- **Outbound deps / sibling coupling:** NONE (grep zero hits).
- **Inbound refs:** `~/.claude/skills/cognition-build/SKILL.md:6,7,9` (stale, as above) — breaks that loop when it fires. No always-on system dependency.

### 1.7 recollection — `/home/tim/recollection`
- **Created:** clone laid down ~2026-06-11; recollection refit git history 2026-06-14 22:56 → 2026-06-16 11:27 (18 commits). **Its own git repo** (parent `/home/tim` is not).
- **Size/shape:** 1.1 GB (1.1 GB of which is `node_modules`), 10,430 files.
- **What it is:** A renamed, refit clone of the open-source **episodic-memory** Claude Code plugin (v1.4.2, by Jesse Vincent/`obra`), heavily re-engineered into a Company-integrated recall substrate. Refit replaced in-process ONNX embedding with a **fabric registry-driven served lens**; added a new data model (atoms/units/links/fingerprints/verdicts/candidates), Company capture sources (`board://`, `clone://`, channel-scoped recall), `recall`/`navigate`/`distill` pipelines. **README.md & CLAUDE.md are still the upstream docs — stale, treat as legacy not current truth.**
- **Structure:** `src/` (46 TS files), `dist/` (compiled), `test/` (52, the spec), `cli/` (entry points incl. `mcp-server-wrapper.js`), `node_modules/` (9,642 files, 1.1 GB, not read). `mcp_registration_debug.log` at root is actually a `project-vi-graph` log that happens to sit here (unrelated).
- **DATA LOCATION (critical):** Data lives OUTSIDE the folder. Resolver (`src/paths.ts`) default = **`~/.recollection`** (verified on disk: 1.2 GB, `conversation-archive/index/logs/self/`, last writes Jun 18–22). A separate legacy `~/.config/superpowers/conversation-index/` (12 GB) was deliberately walled off by the refit. **Moving the folder does NOT move the data.**
- **MCP status:** NOT registered (absent from `.claude.json` 38-server block and all `.mcp.json`), NOT running. Intended registration is plugin-based via `${CLAUDE_PLUGIN_ROOT}`. `.mcp.json` uses relative paths (`./cli/...`, `cwd: "."`).
- **Outbound deps:** Served embedding lens `http://127.0.0.1:8007/v1/embeddings` (`pplx-ctx-4b-docs`, 2560-dim INT8; fail-loud, no fallback). `company` CLI on PATH for `board`/`clone` sources (env-overridable). Indexes `~/.claude` + `~/.codex` transcripts (NOT the `corpora/` folder). No sibling-folder references.
- **Inbound refs:** ~21, almost all `code:///home/tim/recollection/...` content-addresses baked into the comprehended company corpus (DATA), plus an example block in `runtime/corpus_neighbours.py:83,87`. **No live code does a filesystem read of the folder.** Move consequence = stored-address staleness only.
- **Breaks on move:** Nothing functional. Cosmetic `local:///home/tim/recollection` label strings go stale. Nested git repo = plain directory move (not a submodule). Needs `:8007` lens + `company` CLI regardless of location.

### 1.8 ui-contract (home-level) — `/home/tim/ui-contract`  [dead snapshot]
- **Created:** 2026-06-12 19:42:03 (all 4 files, identical nanosecond — atomic drop).
- **Size/shape:** 88 KB, 4 files (`resources/{git,model,permission,settings}.md`). Not a git repo.
- **What it is:** A 4-file fragment of the Company's `ui-contract` knowledge corpus (contract-entry markdown). **Shadows the live, 47-file `/home/tim/company/ui-contract`.**
- **COLLISION verdict:** `model.md`, `permission.md`, `settings.md` are **byte-identical** to the company copies. `git.md` is **divergent — the OLDER/superseded version** (the company copy was corrected 2026-06-13: flipped statuses building→planned, deleted `dev_git` MCP rows, downgraded a `live-verified` claim to `unverified`). **Zero unique content worth preserving.** Dead earlier snapshot.
- **Inbound refs:** ZERO to the home-level path (all `ui-contract` refs in company resolve to its own `ui-contract/`). **Safe to move/retire.**

### 1.9 runtime (home-level) — `/home/tim/runtime`  [dead, broken-in-place]
- **Created:** 2026-06-12 19:42:03 (same nanosecond drop as home ui-contract above — laid down together).
- **Size/shape:** 80 KB, 1 file (`session_supervisor.py`). Not a git repo.
- **What it is:** A single stray copy of the Company's **Session Supervisor** service (HTTP service on `127.0.0.1:8771` owning N `claude` subprocesses). **Shadows the live `/home/tim/company/runtime/` engine.**
- **COLLISION verdict:** `/home/tim/company/runtime/session_supervisor.py` exists and is newer/larger (1,711 lines / Jun 16 vs home 1,252 lines / Jun 12). Home copy is the **Jun-12 ancestor**, multiple revisions behind (lacks the R1.2 render_declaration layer + R1.3 SPAWN_FLAG_ASSEMBLY registry). No unique work.
- **Broken-in-place NOW:** imports `store.fs_store`, `fabric.config`, `runtime.ui_claude_session` via `sys.path` = parent-of-its-dir = `/home/tim`, where those packages DO NOT EXIST (only under `~/company`). So it raises `ModuleNotFoundError` at its current location — it only ever worked inside the company tree.
- **Inbound refs:** ZERO real (the one `tests/self_growth.py:56` hit is a rejected path-traversal test string). **Safe to move/retire.**

---

## 2. INTER-FOLDER DEPENDENCY GRAPH

The nine are **not** a tightly-coupled set — most are isolated leaves. The real relationships:

- **corpora** is the shared **source corpus** → consumed (conceptually/historically) by **mcp-mining**, **company-scan**, and the live dragnet recall indexer. Arrow: corpora → consumers.
- **foundation** is a **seed/context** read by the `~/company` engine (`model_of_tim`); it produced one company artifact (CONVERGENCE-OBJECT). Arrow: foundation → company.
- **recollection** indexes `~/.claude`/`~/.codex` transcripts (not the `corpora/` folder) into `~/.recollection`; couples loosely to the company fabric via the `company` CLI + `:8007` lens.
- **wizard-run-1**, **mcp-mining**, **company-scan** all independently target the SAME external Windows corpus (`/mnt/c/.../Claude/Projects/...`) and the SAME local model stack (vLLM `:8000`/`:8001`, Ollama `:11434`) — a shared *environment*, not shared *data between them*.
- **ui-contract** & **runtime** (home-level) are dead snapshots of live `~/company` subdirs — coupled only as superseded duplicates.
- **company-cognition** — isolated stub (see discrepancy).

**Shared external dependencies across the set (must exist to RE-RUN any pipeline, unaffected by the move itself):**
- Windows corpus mount `/mnt/c/Users/Workstation001/Documents/Claude/Projects/`
- Local model servers: vLLM chat `:8000`, vLLM embed `:8001`, served lens `:8007`, Ollama `:11434`
- Launcher archive `~/vllm-tests/`
- `~/.claude/projects` history; `~/.recollection` data store

---

## 3. FOLDERS OUTSIDE `~/company` THAT THESE DEPEND ON (Tim asked to be told)

Beyond the nine, these external locations are referenced and are NOT being moved:
1. **`/mnt/c/Users/Workstation001/Documents/Claude/Projects/`** (+ `.../Visual Designer`) — the Windows source corpus that wizard-run-1, mcp-mining, company-scan all read.
2. **`/mnt/c/Users/Workstation001/Documents/Conversation-Mind`** — Windows Obsidian vault that mcp-mining writes.
3. **`~/vllm-tests/`** — model launcher scripts (`serve.sh` etc.), referenced by systemd units and by foundation's `operations/`.
4. **`~/.recollection`** (1.2 GB) — recollection's actual data store (separate dir, does not move with the folder).
5. **`~/.config/superpowers/conversation-index/`** (12 GB) — legacy episodic-memory store, walled off by recollection's refit.
6. **`~/.claude/projects/`** — Claude Code history that mcp-mining + recollection read.
7. **`~/.cache/huggingface/hub/`** — model blobs referenced by foundation/operations.

---

## 4. WHAT WAS READ vs CHARACTERIZED (coverage honesty)

- **Fully read:** all of wizard-run-1, mcp-mining, company-scan, foundation, company-cognition scripts/docs; the 4 ui-contract files + diffs; both runtime copies + diff; recollection's package.json/.mcp.json/manifests/paths.ts/coupling headers + full git log.
- **Characterized by sampling (not every file read):** corpora (5 files read, 1858 characterized via uniform front-matter — structurally complete tree + counts); recollection `node_modules` (size only), `dist`/`test`/rest of `src` (grep/ls, not full read).
- **Reference greps were exhaustive** across `~/company` (canonical tree) and the full config/dotfile/systemd/cron surface for all nine names.

---

## 5. RECOMMENDED MOVE SEQUENCE (for Stage-1, pending Tim's direction)

1. **Move freely now (no break):** `wizard-run-1`, `mcp-mining`, `company-scan`, `ui-contract`, `runtime`. (The last two are dead snapshots — could even be deleted rather than archived, but moving preserves the audit trail.)
2. **recollection:** safe to move the folder (data stays at `~/.recollection`); accept stored-address staleness, or re-key later. Confirm `node_modules`/git move is acceptable (1.1 GB, own repo).
3. **company-cognition:** resolve the worktree discrepancy first; if it's just the stub, move or delete + fix the stale SKILL.md lines.
4. **corpora & foundation:** **DO NOT MOVE until the env vars are set** (`CLAUDE_SESSIONS_CORPUS`, `COMPANY_MODEL_OF_TIM`) and the platform-docs Chroma index path is repointed — OR consciously decide to leave these two in place as live data/seed. These are the only two that break the always-on system.

---
*End of register. Stage-2 (full company scan, digest, refactor, re-document) is a separate effort to be scoped with Tim.*
