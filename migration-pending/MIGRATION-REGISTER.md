# Company Consolidation Register — Full Home-Directory Inventory

**Compiled:** 2026-06-26 · **Author:** Lead session · **Status:** evidence-grounded landscape catalogue. This is the agent workspace (dense/technical); messages to Tim are translated separately.

**Governing principle (Tim):** everything that is *the company* was always meant to live inside `~/company`. Determination of "company-or-not" is made ONLY from evidence inside each folder (does its code/config/data reference, wire into, or share state with `~/company`?) — never from the folder's name or from memory/inference. Coverage is stated per item as **files read / files exist**; large trees were identified from identity files + full reference-greps, not exhaustive reads, and that is marked.

---

## 0. THE REFRAME — the company is a distributed system, not a folder

The home-directory sweep proves the company's *running parts* are deliberately scattered, wired together by systemd. "Consolidate into the folder" is therefore two distinct jobs:

- **RELOCATABLE (authored work + data):** can physically move into `~/company` with reference fixes. (The 9 folders, `.vi`, `repos/counterpart`, handoff docs, the recall index, certs.)
- **WIRED SUBSTRATE (running services):** "moving" = rewiring ~20 systemd unit `ExecStart` paths + configs, not a folder move. Careless relocation stops the company mid-run. (The model/voice venvs, `company-*` units.)

**Company live-state currently OUTSIDE `~/company`:**
| What | Where | Evidence | Type |
|---|---|---|---|
| Session-recall substrate (vector store + index) | `~/.cache/company/substrate-claude-sessions/` (1.6G: chroma 1009M + substrate.db 98M + a `chroma.corrupt-backup-20260620`) | `config.json`: vault `claude-sessions`→`~/corpora/claude-sessions`, embed `pplx-embed-context-v1-4b` @ `:8007` | core data |
| Service orchestration (~20 units) | `~/.config/systemd/user/company-*` + `company.target` | `company-bridge.service` ExecStart=`~/company/.venv/bin/python runtime/bridge.py 8770`; voice units ExecStart=`%h/.voice-venvs/<engine>/bin/python ~/company/voice/engines/...` | config |
| TLS cert + key (Tailscale serving) | `~/.config/company/certs/` | cert for `workstation001.tail777bc2.ts.net` | config + secret |
| Source corpus | `~/corpora/claude-sessions` | the substrate's indexed vault (see §1) | data |

---

## 1. COMPANY-NATIVE — belongs inside, RELOCATABLE

### 1.1 The original nine (full action plans in prior register sections — unchanged, summarized here)
| Folder | What it is (plain) | When | Where→target | Read/Exist | Move reality |
|---|---|---|---|---|---|
| **foundation** | The company's persistent memory layer: verbatim founding conversations (`exchanges/`) + synthesized doctrine (`system/`,`models/`,`operations/`). Markdown. | 2026-05-27→06-12 | `~/foundation` → `~/company/foundation` | all read | 1 live binding (`nodes/model_of_tim.py:16` reads `system/principles.md`, fail-loud) + 2 wikilink re-depths. Commit it (markdown). |
| **corpora** | The shared source corpus — "Claude Code Atlas": scraped platform docs (811 .md) + 1,051 session transcripts. Data. | 2026-06-10→12 | `~/corpora` → `~/company/corpora` | 5 read / 1,863 | Index lives in `~/.cache/company` (rel-path keyed → no re-embed). Fix config.json path + 5 code defaults (writer + transcript_search ignore the env var = split-brain to repair) + forced reindex. Gitignore it (52k files). |
| **recollection** | Refit clone of episodic-memory v1.4.2 → company recall substrate (board://, clone://, served lens). Own git repo, 1.1G (node_modules). NOT a registered/running MCP. | clone 06-11, refit 06-14→16 | `~/recollection` → `~/company/recollection` | source read / node_modules sized only / 10,430 | Data is at `~/.recollection` (1.2G) — moves separately; `self/` inside it is COMPANY data (3 company scripts write/read it). 8218 DB rows hold absolute paths → SQL rewrite. Set `RECOLLECTION_CONFIG_DIR`. Nested git → gitignore. |
| **mcp-mining** | A completed overnight conversation-mining run → emergent Obsidian vault. Despite name, NOT about MCP. | 2026-05-30→31 | `~/mcp-mining` → migration-pending | all read | No live refs. Prototype/island. |
| **company-scan** | Forensic 2-pass local-4B scan of a Windows project tree (19,361 files) + design recovery. | 2026-06-01 | `~/company-scan` → migration-pending | all read | No live refs. Island. |
| **wizard-run-1** | By-hand prototype of the Project→Product pipeline on the ElevenLabs Wizard corpus. | 2026-06-04→09 | `~/wizard-run-1` → migration-pending | all read | No live refs. Island (prototype of would-be engine tools). |
| **ui-contract** (home) | Dead snapshot of `~/company/ui-contract`. | 2026-06-12 | delete or archive | all read | MD5 = company commit `b239f48` (3 files byte-identical to *current* tree; git.md = a past commit). Zero unique content. |
| **runtime** (home) | Dead snapshot of `~/company/runtime/session_supervisor.py`; broken-in-place (can't import its deps at `/home/tim`). | 2026-06-12 | delete or archive | all read | MD5 = company commit `5e94bfb`. Pure ancestor. Zero unique content. |
| **company-cognition** (home) | Husk of the intended `concurrent-cognition` worktree — only a leftover vite cache survives. | 2026-06-08 | delete | 0 files (empty) | See §2-cognition: the build is real and ON MAIN; this husk holds nothing. |

### 1.2 Other company-native scatter (newly found)
- **`.vi`** (`~/.vi`, 224K, 31 files / 9 read, 2026-03-02→**06-17 live**) — Project Vi shared-context dir, **auto-loaded into every Claude session** as active instructions (per `~/.claude/CLAUDE.md`). Its `CLAUDE.md` is the canonical cross-session frame: defines DNA/FACTORY/GALLERY layers and names **`~/company` as "ADDRESS RESOLUTION + MODELS + everything else — the substrate all layers resolve through."** `rules/cross-session-channels.md` launches sessions via `~/company/channels/`. → PART-OF-COMPANY (the connective frame; live, load-bearing — relocating it means updating the `~/.claude/CLAUDE.md` additionalDirectory pointer, not a blind move).
- **`repos/counterpart`** (920M incl. a 433M backup tarball, working dir / NOT a git repo, 2026-06-11→13) — design/spec workspace for the company's operator surface, decision-card host, RHM voice, DNA. **The only thing in `~/repos` (81G, 27 repos) that references `~/company`:** 4 source refs to `/home/tim/company/runtime/{ui_claude_session,territory}.py` + build-prep contracts. → PART-OF-COMPANY (design satellite).
- **`.company`** (`~/.company`, 44K, **0 files**, 2026-06-06) — empty store skeleton mirroring the FsStore layout (`objects/vectors/graphs/refs/surfaced/...`). Unused twin of the live store. → PART-OF-COMPANY (inert; safe to delete or note).
- **`channel-test`** (8K, 1 file, 2026-06-14) — a `.mcp.json` launch config that joins the company fabric (`node ~/company/channels/company_channel.mjs`, `COMPANY_ROOT=~/company`, handle `tim-live-1`). → PART-OF-COMPANY (channel launch config; abandoned scratch — capability lives in `.vi` rules).
- **Loose coordination/handoff docs** (all reference `~/company` runtime/voice/canvas paths + branches; dead correspondence, work merged):
  - `company-bridge.md` (2026-06-02) — spec↔engine reconciliation decision doc.
  - `MERGE-COORD-cognition.md` (2026-06-08) — merge-coordination from the concurrent-cognition session (names the worktree + 7 conflict files).
  - `ui-handoff.md`, `voice-frontend-handoff.md`, `voice-stt-handoff.md` (2026-06-05) — build handoffs for the interactive surface + voice circuit.
  - `round3-grounding-report.md` (2026-06-01) — design-grounding citing company contracts.
  - → PART-OF-COMPANY (historical build record; relocate as archive).
- **`artefacts`** (108K, 2 files, 2026-05-28) — `Vi.md` (vision narrative) + a model survey. Vision/research docs about the project. → PART-OF-COMPANY (narrative artifacts) / borderline with the Vi-vision corpus.

### 1.3 Company live-state in dotdirs (see §0 table) — RELOCATION IS REWIRING
- **`~/.cache/company/substrate-claude-sessions`** (1.6G) — the recall substrate. Moving it = edit `config.json` paths + the corpora move (§1.1) must agree.
- **`~/.config/company/certs`** — TLS material (secret). Move + update whatever serves it.
- **`~/.config/systemd/user/company-*` + `company.target`** — the service definitions themselves. These are config files that *could* live in-repo (company already has `ops/systemd/` source copies) and be symlinked/installed — but the *installed* units in `~/.config/systemd/user` are what systemd actually runs.

---

## 2. COMPANY RUNTIME SUBSTRATE — wired in by systemd (shared infra, "move" = rewire)

Confirmed by reading `ExecStart` lines in the installed `company-*`/`vllm-*` units:
| Folder | Size | Role | Wire evidence |
|---|---|---|---|
| **vllm-env** | 8.4G | vLLM inference runtime | `vllm-*.service` use it; canonical company file refs `~/vllm-env/.../nvidia/cu13` (116 hits) |
| **jina-v4-env** | 5.0G | Jina v4 embedding runtime | `vllm-jina-v4.service` |
| **.voice-venvs** (9 engines) | 48G | STT/TTS engine runtimes | `company-voice-*`/`company-stt-*` ExecStart=`%h/.voice-venvs/<engine>/bin/python ~/company/voice/engines/...` (264 hits) |
| **CosyVoice** | 5.3G | TTS weights+code | company `voice/engines/cosyvoice.py` imports it; refs `~/CosyVoice/pretrained_models/CosyVoice2-0.5B` (224 hits) |
| **.voicemode** | 2.9G | Whisper STT service | `voicemode-whisper.service` runs `~/.voicemode/services/whisper/bin/start-whisper-server.sh` (64 hits) |
| **vllm-tests** | 1.3M | Model serve scripts + benchmarks + company UI screenshots | `llama-swap` config points at `~/vllm-tests/serve_2b.sh`; foundation/operations indexes it; systemd refs (146 hits) |
| **llama-swap** | 8K | Model router config | `llama-swap.service` |
| **openwebui-venv** | 6.8G | OpenWebUI runtime (fabric integration target) | OpenWebUI fabric-research build-prep; service area |
| **actions-runner** | 1.8G | Self-hosted CI runner | `github-runner.service`, bound to repo `Concept-Vi/ollama-pipeliner` |

> Decision implication: physically pulling 48G+ of venvs/models into `~/company` is possible but heavy and rewires the whole service layer. Alternative: keep substrate where it runs, but treat the **systemd unit definitions + the recall index + certs** as the "company state" that gets versioned/owned inside the repo (company already has `ops/systemd/` source copies). This is a genuine architecture call (see §5).

---

## 3. SEPARATE PROJECTS — evidence shows NO `~/company` code link

These are conceptually related (Tim's ecosystem) but, by evidence, are distinct codebases that do not reference/wire into `~/company`. They are NOT "company folders scattered out" — they are their own projects.

### 3.1 Project Vi application family (all: zero `/home/tim/company` code refs)
- **vi-gateway** (738M, remote `Concept-Vi/vi-gateway`) — Vi's OpenClaw deployment on Fly; serves `gateway.vspokes.com`. Vi's brain/backend.
- **vi-chat** (750M) — Next.js PWA chat front-end → the Vi gateway. Deployed Fly app.
- **vi-openwebui** (548K) — Vi-branded Open WebUI → the gateway.
- **vi-visual-bridge** (1.3G, remote `Concept-Vi/vi-wizard`, **active to 2026-06-22**) — "Vi-Wizard" Chrome annotation bridge. **Boundary case:** no `~/company` code import, BUT its `FORMATION_JOURNAL` records the LEAD session (ch-al7jdfdr) re-pointing it on 2026-06-22 at "the Company front interface" via the `company-channel` fabric. A separate app *tasked toward* company goals. `.vi-visual` (868K) is its data store; `vi-worktrees` (5M) are its feature branches.
- **vi-voice-agent / -pipecat / -local** (355M/850M/24K) — three parallel Vi voice pipelines → the Vi gateway/workbench. Stale since April.
- **vi-demo** (12M), **vi-backup** (18M, a Fly-volume snapshot) — old demo + backup.
- → ALL SEPARATE-PROJECT (Project Vi). Security flag: hardcoded OpenClaw token + LiveKit/AssemblyAI/Cartesia/OpenAI keys in `vi-chat/.env.local` and the voice `agent.py`/`.env` files.

### 3.2 `repos/` (81G, 27 repos) — only counterpart (§1.2) is company; rest are SEPARATE
Notable: **obsidian-overlord** (9.2G, `substrate-mcp`) — the live MCP server that indexes vaults; shared infrastructure the company *uses* (its `.state/substrate.db` even names the canonical vault), but own repo, no `~/company` code import → SEPARATE (shared infra). Others: project-vi (8.9G), graph-editor (RelaTesseract), Supabase (architesseract), langflow (33G), slack-dump (26G data), kg-extractor, chameleon, dimension_x (+2 orphan copies), vi-interpreter, vi-cognitive-infrastructure, etc. — all own remotes, no company link. Cleanup-flagged: `graph-viewer` (empty), `dimension_x - Copy`/`Copy (2)`, loose `vi_presentation*.zip`, the 433M tarball in counterpart.

### 3.3 `vaults/` (849M)
- **Obsidian Builder** (598M, 5,245 .md) — the canonical Vi design vault; CONFIRMED by `obsidian-overlord/.state/substrate.db` literal "Canonical vault: /home/tim/vaults/Obsidian Builder/." Operationally superseded by Windows-side vaults (the live `config.json` points at `/mnt/c/.../vi-context-design`, `.../Visual-DNA-Vault`).
- **vi-vault-design** (251M, 3,069 .md) — deprecated older ancestor.
- → SEPARATE-PROJECT (Vi vaults; ecosystem-linked via substrate, not company code).

### 3.4 Other standalone projects
- **universal-mechanics** (89M, Obsidian vault) — Tim's science/framework corpus (substrate theory, axes, math-verification). No company code link → SEPARATE (upstream framework; feeds thinking, not wired).
- **openclaw-deploy** (525M, remote `openclaw/openclaw`) + **.openclaw** (121M, runtime state) — the OpenClaw assistant project. → SEPARATE.
- **brat-release** (119M, remote `Concept-Vi/obsidian-vi-chat`) — built Vi Chat Obsidian plugin v10.1.249; uses Vi Chat's Supabase + `channel_events` (the company↔Vi realtime link is documented as *future*). → SEPARATE (Project Vi).

---

## 4. NOT-COMPANY — generic infra / caches / tooling / pre-company eras

(Evidence: no `~/company` reference; identity confirms generic purpose.)
- **Toolchains/managers:** `.nvm` (1.9G), `.npm` (5.5G), `.npm-global`, `.yarn` (969M), `.deno`, `.bun`, `.pyenv`, `go` (792M), `bin`, `snap`, `google-cloud-sdk`, `Applications` (Obsidian AppImage).
- **Model/ML tools & caches (not company-wired):** `comfyui-data` (36G), `ComfyUI` (venv deleted), `kohya_ss` (11G), `models` (empty), `nltk_data`, `.triton`, `.lhotse`, `.keras`, `.modelscope`, `.nv`, `cpoi-env`.
- **MCP/agent tooling:** `.mcpbundles`+`mcpbundles-venv` (tunnel daemon), `.task_orchestrator`, `.agent-mcp` (empty), `.composio` (empty), `semantic-discovery-mcps`, `mcp-agent-dev` (empty venv), `orchestration`, `mind-dev`.
- **The 26G archive:** `~/.config/superpowers/` (15G transcripts + 12.5G `db.sqlite`) — the **superpowers plugin's** own conversation archive/index. Mirrors company sessions but is plugin-owned, NOT the company substrate (that's `.cache/company`). Largest single artifact after model caches.
- **Other dotdirs:** `.cache/chroma` (Chroma's default ONNX model, not company), `.langflow`, `.langgraph_api` (cloudflared), `.mintlify` (265M), `.crawl4ai`, `.mem0`, `.claude-code-router`, `.vibe-annotations` (empty), `.cursor`, `.pm2` (runs vi/company-adjacent workers but stores no data), `.streamlit`, `.docker`, `.fly` (103M), `.supabase`, `.ollama`, `.codex`, `backups` (1.9G OpenWebUI volume snapshots), `.pki`, `.ssh`.
- **Pre-company-era dirs:** `geepers`, `creations` (VECO), `world_keeper_profile`, `searxng-config`, `.cognitive_framework` (27M flow store), `ai-systems-strategic-overview`, `docs` (archaeology/geepers), `temp`, `cc-loop-logs`+`cc-loop-configs` (target vi-visual-bridge), `xsession-tests` (cross-session R&D test bed — informed the fabric, no company link), `test`/`__pycache__` (stale).
- **Loose files:** Aug-2025 mcp-use experiments; Mar-2026 Vi-Visual-Bridge `recovered_*`/`current_server_*.py`; Quest/Scout reports; ComfyUI guides; Apr-2026 Vi-chat mobile screenshots; OAP/deep-research logs; `episodic-memory` (7M, third-party `obra/episodic-memory`, upstream of recollection).
- **Empty/cache scaffolds:** `.build` (0 files), `tophone` (0 files), `.humming` (Orpheus CUDA build cache).
- **Secrets flagged (not company-scoped, live):** `.ssh/id_ed25519`, `.supabase/access-token`, `.claude-code-router` litellm key, `.vi-mcp-node-identity.json` (Ed25519 private key), and the Vi token/keys in §3.1.

---

## 5. THE GENUINE DECISIONS (Tim's to make; I drive the rest)

1. **Substrate: move or own-in-place?** The 48G+ of model/voice venvs run from fixed home paths via ~20 systemd units. Pulling them physically into `~/company` is heavy and rewires every service. The lighter consolidation: bring the *company-owned definitions* inside (systemd units — already mirrored at `ops/systemd/`; the recall index; the certs) and version them, while the bulk model runtimes stay where they run. Which meaning of "inside the folder" do you want for the running substrate?
2. **Project Vi boundary.** By evidence the Vi codebases are separate (no company code link). Do you want them treated as separate organs that *connect* to the company (leave in place, wire via fabric), or physically consolidated too? `vi-visual-bridge` is the one already being aimed at the company front-end.
3. **The relocatable company-native set** (the 9 + `.vi` + counterpart + `.company` + handoff docs + recall index + certs) — confirm the homes (`~/company/<name>`, gitignore data dirs) and I action the moves + reference rewires + the corpora env-fix in one verified pass.
4. **Dead/empty:** delete the two proven twins + the cognition husk + `.company`/`.build`/`tophone` empties, or archive for trail?

---

## 6. COVERAGE HONESTY
- Fully read: the 9 folders, `.vi` top-level docs, handoff docs, `.company`/`.build`/`tophone` (empty, confirmed), the systemd units, the recall `config.json`.
- Identified by identity-files + reference-grep (NOT every file): `repos/*` (27 repos), `vaults/*`, all `vi-*`, the venvs/caches, `recollection` node_modules, `corpora` (5/1863). Stated per item above.
- Reference determination method: per folder, read README/package.json/git-remote/config + grep for `/home/tim/company`, `company-channel`, company ports/CLI. "No link" = none found in that scope; absence-of-grep-hit is not the same as proof-of-absence for unread files — flagged where it matters.

---
*Prior detailed move action-plans for corpora / foundation / recollection (config edits, env vars, reindex, SQL rewrites) are retained in this file's history and stand. Stage-2 (digest/refactor) remains separate.*
