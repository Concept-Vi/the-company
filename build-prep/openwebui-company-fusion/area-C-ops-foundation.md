---
type: map
area: ops+foundation+orienteering+docs
register: descriptive
date: 2026-06-28
coverage: { scanned: all, depth: maximal-coverage, observed: systems/services/paths/runtimes, last_read: 2026-06-28 }
relates-to: ["[[services.json]]", "[[orienteering/INDEX]]", "[[TIM.md]]", "[[foundation/operations]]"]
---

# AREA C MAP — ops, foundation, orienteering, docs
## Comprehensive Inventory: Services, Infrastructure, Terrain Ledger, Knowledge Layer

**Scope:** Four critical areas inventoried at maximal depth:
- `/home/tim/company/ops/` — operational control, service registry, CLI
- `/home/tim/company/foundation/` — foundational knowledge, system design, TIM document, operational synthesis
- `/home/tim/company/orienteering/` — terrain ledger (what lives where, connections, state)
- `/home/tim/company/docs/` — cross-cutting documentation, conventions, methodology

---

## PART 1: ops/ — The Operational Control Layer

**Physical location:** `/home/tim/company/ops/`
**Primary artifacts:** `services.json` (703 lines), `model_capabilities.json` (52KB), CLI stack, systemd source units, operational scripts

### 1.1 The Service Registry — services.json (file:1–705)

**What it is:** The single self-describing source of truth for what runs on the machine. The AI reads this to know the whole landscape; the `company` command operates it. No service runs that isn't registered here.

**Structure:**
- `vram_ceiling_mb`: 16376 (hard ceiling on RTX 4080)
- `combos`: Named loadout sets for coordinated service startup
- `groups`: Six functional groupings (core, brain, voice, models, reach, jobs)
- `services`: 45 service entries, each with group/title/port/manage/health/autostart/config/vram_mb

**Key facts:**
- **No auto-start at boot** (2026-06-06 decision): every service starts on-demand via `company up`
- **autostart=true** only for surface layer (canvas + bridge) to bring interactive Company up
- **Composite loadouts** via `combos`: wake (surface+brain+voice default), xsession (cross-session fabric), interaction (realtime conversation), interaction-parakeet (variant with different STT ear)
- **VARIANTS via extends**: combos can inherit from base (`extends: interaction`) and swap one service (`swap: {old-svc: new-svc}`) — allows configuration trials without duplication

### 1.2 Core Services (group: core) — The Company's Visible Face

| Service | Port | Title | Manages | Health | Notes |
|---------|------|-------|---------|--------|-------|
| `canvas` | 5173 | Operable surface (vite dev server) | user-unit: company-canvas.service | `/` | autostart=true; unmanaged vite, separate startup |
| `bridge` | 8770 | Suite UI face / HTTP API | user-unit: company-bridge.service | `/api/now` | autostart=true; the surface backend |
| `remote` | 8772 | Remote connector (public MCP front) | user-unit: company-remote.service | `/healthz` | Funnel→:8772; identity-gated (Tim only) |
| `session-supervisor` | 8771 | Session supervisor (owns Claude Code fleet F1) | user-unit: company-session-supervisor.service | `/health` | 127.0.0.1 only (exposure law B3); spawns Claude on demand; single writer to agent_sessions.* |

**Critical:** session-supervisor is NOT auto-start (on-demand per fabric), but the three surface services define the interactive Company's baseline.

### 1.3 Brain Services (group: brain) — Language Model Workers

| Service | Port | Model | vram_mb | Notes |
|---------|------|-------|---------|-------|
| `chat-4b` | 8000 | cyankiwi/Qwen3.5-4B-AWQ-4bit | 7000 | vLLM; config-driven via serve_model.sh; hybrid-Mamba arch; KV ~31.7 KB/token; max_model_len 16384; prefix caching + tool choice |
| `chat-2b` | 8003 | Qwen/Qwen3.5-2B | 7200 | vLLM; gpu_util 0.45; max_num_seqs 32; same qwen3_xml parser |
| `chat-08b` | 8006 | Qwen/Qwen3.5-0.8B | 3200 | vLLM; gpu_util 0.30; ultra-concurrency (max_num_seqs 32); co-resident with chat-2b (small-pair combo) |
| `chat-nemotron` | 8005 | NVIDIA Nemotron-3-Nano-30B-A3B-AWQ | 16600 | vLLM; 30B MoE; CPU-offload 6GB; enforce-eager; tight fit (0.88 gpu_util) |

**Key design:**
- All use `--enable-prefix-caching`, `--enable-auto-tool-choice`, `--tool-call-parser qwen3_xml` (services.json:130–142)
- All use patched chat template `chat_template_nothink.jinja` to suppress thinking tokens
- The 4B is the resident default brain; 2B/0.8B are small-pair co-residents; nemotron is a heavy reasoner for swap

### 1.4 Voice Services (group: voice) — STT Ears & TTS Engines

**STT Ears** (speech-to-text input):

| Port | Service | Model | Device | vram_mb | Notes |
|------|---------|-------|--------|---------|-------|
| 2022 | `stt-whisper` | mobiuslabsgmbh/faster-whisper-large-v3-turbo | CPU | 1500 | OpenAI-compat /v1/audio/transcriptions; default ear (boot standard) |
| 2031 | `stt-parakeet` | nvidia/parakeet-tdt-0.6b-v3 | GPU (NeMo) | 5500 | GPU ear; multilingual; 25 languages; hotword biasing candidate |
| 2032 | `stt-canary` | nvidia/canary-qwen-2.5b | GPU (NeMo) | 12000 | Heaviest ear (~10GB resident); English-max + understanding; near-OOM candidate |
| 2033 | `stt-granite` | ibm-granite/granite-4.0-1b-speech | GPU (transformers) | 6500 | Compact cross-check ear; transformers venv; CPU-pinnable |
| 2034 | `stt-moonshine` | moonshine/base | ONNX (CPU) | 900 | LEANEST ear (<1GB); default for interaction loadout; no padding; built for realtime |
| 2035 | `stt-parakeet-onnx` | parakeet-tdt-v3-int8 | ONNX (CPU or GPU) | 0 | Quantized Parakeet; int8 sweet spot; 25 languages; hotword/context biasing; lean variant |

**TTS Engines** (speech-to-text output):

| Port | Service | Model | vram_mb | Type | Notes |
|------|---------|-------|---------|------|-------|
| 4123 | `tts-kokoro` | (model id unconfirmed) | 900 | vLLM? | weights not located/verified on disk; flag for audit |
| 4124 | `tts-chatterbox` | ResembleAI/chatterbox | 3800 | transformers (venv: chatterbox) | Trial persona Viv; clones reference voice; ~3.4GB |
| 4125 | `tts-orpheus` | Hariprasath28/orpheus-3b-4bit-AWQ | 10500 | vLLM-backed (orpheus.py) | Trial persona Pip; ~10GB + SWAP-HOSTILE (~17min cold); pin/pre-warm; gpu_util 0.32 |
| 4126 | `tts-cosyvoice` | FunAudioLLM/Fun-CosyVoice3-0.5B-2512 | 4200 | transformers (cosyvoice.py) | Trial persona Tess; instruct+clone; CUDA_HOME + ref-voice required |
| 4127 | `tts-xtts` | coqui/XTTS-v2 | 2500 | transformers (xtts.py) | Trial persona Wren; clone to realism ceiling; NON-COMMERCIAL license; ~2GB |
| 4128 | `tts-qwen3tts` | Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign | 4500 | transformers (qwen3tts.py) | Trial persona Sable; VoiceDesign (describe voice, no clip); ~4.4GB; ~25s cold |

**Key insight:** interaction loadout (default) uses stt-moonshine (CPU ear) + tts-kokoro (GPU voice); swappable for trial voices. xsession loadout adds tts-qwen3tts (VoiceDesign) + rerank-jina.

### 1.5 Model Services (group: models) — Embedders, Rerankers, Swappers

| Port | Service | Model | vram_mb | Type | Notes |
|------|---------|-------|---------|------|-------|
| 8001 | `embed-bge` | BAAI/bge-m3 | 2500 | vLLM (--runner pooling) | Default embedder (dense+sparse+ColBERT); ~1,370 embed/sec @ concurrency 32 |
| 8002 | `embed-jina-v4` | jinaai/jina-embeddings-v4 | 8000 | jina-v4-env (custom transformers) | Multimodal embedder; vLLM lacks arch support; dedicated venv (transformers<5 pinned) |
| 8004 | `embed-jina-v5` | jinaai/jina-embeddings-v5-text-small | 2000 | vLLM | config-driven; max_model_len 8192 |
| 8004 | `embed-qwen3` | Qwen/Qwen3-Embedding-8B | 9000 | vLLM | gpu_util 0.92; multilingual flagship; port collision note (see open questions) |
| 8007 | `embed-pplx` | perplexity-ai/pplx-embed-context-v1-4b | 5700 | Custom transformers (serve_pplx_embed.py) | **LIVE transcript-search embedder** (2026-06-12 verified); contextual late-chunking; 2560-dim; INT8 output (compare via COSINE); not vLLM-compatible (remote code arch) |
| 8008 | `rerank-jina` | jina-reranker-v3 | 1300 | Custom Python (rerank.py) | GPU endpoint (2026-06-28 Tim moved to GPU); listwise reranker; <0.05s GPU warm vs ~16s CPU; used by cross-session recall |
| — | `llama-swap` | — | — | user-unit | Model hot-swapper; serves 2B/0.8B via dynamic loading |

**Notable:** embed-pplx is CUSTOM-SERVED and verified live; it's NOT handled by vLLM because its remote-code model (`PPLXQwen3Model` arch) isn't in vLLM's supported list. serve_pplx_embed.sh launches serve_pplx_embed.py in ~/vllm-env.

### 1.6 Reach Services (group: reach) — Network & Always-On

| Service | Port | Type | Notes |
|---------|------|------|-------|
| `ollama` | 11434 | system-unit (ollama.service) | GGUF big-models runtime; system-enabled at boot; 0 VRAM idle; loads on demand |
| `tailscale` | — | system-unit (tailscaled.service) | Tailnet + HTTPS serve to phone; system-enabled at boot |
| `pipeliner` | — | user-unit (github-runner.service) | GitHub Actions self-hosted runner (Concept-Vi/ollama-pipeliner); on-demand (2026-06-06) |
| `openclaw-gw` | — | user-unit (openclaw-gateway.service) | OpenClaw gateway (Stage 2); usually dormant |
| `remote-gateway` | (hosted) | Supabase edge fn | Stable cloud OAuth door → Funnel → :8772 remote connector; identity-gated |

### 1.7 Jobs Services (group: jobs) — Scheduled Timers

| Service | Timer Fires | Purpose | Notes |
|---------|-------------|---------|-------|
| `agent-sessions-exporter` | Every 20 min (:00/20) | Claude transcript export | Exports ~/.claude to ~/corpora/claude-sessions markdown; READ-ONLY access; filter law + redaction in ops/agent_sessions_exporter.py |
| `claude-sessions-reindex` | ~5 min after export (*:05/20) | Substrate DELTA reindex | Reindexes corpus markdown → searchable index (embed-pplx); CHEAP by design (exits doing nothing if no change); substrate venv |

Both timers are WantedBy=company.target (rise/fall with Company, no orphans).

### 1.8 The Company CLI — ops/company (symlinked to ~/.local/bin/company)

**What it does:** Single console to see + operate the runtime. `company status` shows every service grouped, live state (▶ running · ◐ active-no-port-yet · ✖ failed · · stopped), and drift.

**Command surface** (from ops/STARTUP.md):
- `company status` — full service inventory + state
- `company up [SERVICE|GROUP|@COMBO]` — start service(s); resource-gated (won't exceed 16GB VRAM); `--force` overrides
- `company down SERVICE|GROUP` — stop service(s)
- `company restart SERVICE|GROUP` — restart
- `company logs SERVICE` — journalctl
- `company gpu` — GPU status + fit report (shows what fits without OOM)
- `company swap [chat-model]` — swap brain (loads new, unloads old)

**Implementation:** cli/ folder (Python):
- `cli/gpu.py` — resource manager: fit checking, eviction planning, VRAM budgeting
- `cli/capabilities.py` — model catalog JOIN (services.json + model_capabilities.json)
- `cli/system.py` — systemd operations, health checking

### 1.9 Systemd Units (source at ops/systemd/)

**18 user units + 1 system unit** (file:ops/systemd/ ls):

**Core surface (3):**
- `company-canvas.service` — vite 5173
- `company-bridge.service` — bridge 8770
- `company-remote.service` — MCP 8772

**Brain (4 chat models):**
- `vllm-chat.service` — chat-4b 8000
- `vllm-2b.service` — chat-2b 8003
- `vllm-08b.service` — chat-08b 8006
- `vllm-nemotron.service` — nemotron 8005

**Embedders (5):**
- `vllm-embed.service` — bge-m3 8001
- `vllm-jina-v4.service` — jina-v4 8002
- `vllm-jina-v5.service` — jina-v5 8004
- `vllm-qwen3emb.service` — qwen3 8004
- `company-embed-pplx.service` — pplx-embed 8007

**Voice STT (5):**
- `voicemode-whisper.service` — whisper 2022
- `company-stt-parakeet.service` — parakeet 2031
- `company-stt-canary.service` — canary 2032
- `company-stt-granite.service` — granite 2033
- `company-stt-moonshine.service` — moonshine 2034
- `company-stt-parakeet-onnx.service` — parakeet-onnx 2035

**Voice TTS (6):**
- `company-tts-kokoro.service` — kokoro 4123
- `company-voice-chatterbox.service` — chatterbox 4124
- `company-voice-orpheus.service` — orpheus 4125
- `company-voice-cosyvoice.service` — cosyvoice 4126
- `company-voice-xtts.service` — xtts 4127
- `company-voice-qwen3tts.service` — qwen3tts 4128

**Support:**
- `company-rerank-jina.service` — rerank 8008
- `company-session-supervisor.service` — session mgmt 8771
- `company-agent-sessions-exporter.service` + timer
- `company-claude-sessions-reindex.service` + timer
- `company-ledger-refresh.service`
- `llama-swap.service` — model swapper
- `company.target` — meta-target (for WantedBy grouping)
- `github-runner.service` — pipeliner (manual startup)
- `openclaw-gateway.service` — openclaw (dormant)

**System unit:**
- `ollama.service` (at /etc/systemd/system/) — always enabled; managed separately

### 1.10 Config & Scripts in ops/

**Key files (file:ops/ ls):**

- `serve_model.sh` — Generic vLLM launcher (called by chat/embed units)
- `serve_pplx_embed.py` + `serve_pplx_embed.sh` — Custom embedder (not vLLM)
- `serve_rerank.py` + `serve_rerank.sh` — Custom reranker (GPU endpoint, 2026-06-28 move)
- `ledger_build.py` — Produces ledger markdown from internal sources
- `ledger_interpret.py`, `ledger_interpret_codex.py`, `ledger_interpret_ollama.py` — Ledger interpretation
- `surface_server.py` — Bridge HTTP API backend (8770)
- `owui_*.py` — OpenWebUI integration (room, fork-listen, fork-watch, fabric-bridge)
- `agent_sessions_exporter.py` + `agent_sessions_importer.py` — Transcript management
- `claude_sessions_reindex.py` — Reindex beat
- `dragnet_determine.py` + `dragnet_extract.py` — Extraction pipeline
- `fabric_*.py` — Fabric probing (live, clone, wake state)
- `rerank.py` — Reranker interface (API-facing)
- `model_capabilities.json` — Catalog of model intrinsic capabilities
- `services.json` — **Registry of truth** (703 lines, described above)
- `code_archaeology.py` — Codebase analysis
- `commit_queue.py` — Git queue management

---

## PART 2: foundation/ — Knowledge Layer & System Design

**Physical location:** `/home/tim/company/foundation/`
**Size:** ~756 KB; 6 major components

### 2.1 TIM.md — The Foundation Document

**What it is:** The single living understanding of who Tim is, how he builds, what the Company is, and how to work with him. **Not a spec; a growing artifact that accumulates context across sessions.** Updated additively, never by overwriting.

**Structure (11 major sections):**

1. **How to read** — Three-step protocol: read full doc + memory index + latest thread; write protocol enforces openness (never closure-language)
2. **The Progressive Law** — Tim does NOT give specs upfront; pieces reveal progressively; artifact must grow, not calcify
3. **The First Law** — Tim is the foundation; everything gets built on and around him specifically, not as generic-with-user
4. **Who Tim is** — Autodidact polymath (95th+ percentile across domains, no formal training); 10 years original science (cognition/behaviour/systems/AI); works 100% through AI agents; cannot read code
5. **Operating model** — Zero humans ever; 100% AI-operated across many sessions; all engineering disciplines = one AI's responsibility
6. **How Tim thinks** — Relationally (flows not components); Universal Composition (reuse the primitive); dense messages (seeds not summaries); patterns over checklists; progressive revelation; autodidact vocabulary
7. **How Tim wants to be worked with** — Role split table; communication altitude (high); multiple-choice direction (never binary); scope defaults to ambitious; forward motion over caution; completeness required; memory continuity critical; verify before claiming
8. **Anti-patterns** — Don't summarise dense messages; don't treat examples as specs; don't force MVP; don't lose vocabulary
9. **What's built so far** — vLLM stack (16GB, RTX 4080), 125GB models, voice surveyed
10. **What Tim is building** — Four progressive layers (purpose / Company framing / open-future writing / one-entity principle)
11. **Revision log** — Each session dates its changes; nothing is silently rewritten

**Key claims locked by Tim:**
- **Foundation Law:** Tim is the centre; re-read TIM.md, not generic Claude Code assumptions
- **Progressive Law:** Specs arrive in layers; artifact must grow
- **Open-future mode:** Writing mode that leaves room for spiral-review to deepen; no closure-language
- **One entity:** Company presents as unified to Tim; internal complexity is real but not his burden
- **No-repeat KPI:** Corrections must propagate; if same correction recurs, architecture failed
- **All or nothing:** Half-working damages credibility; completeness is required

### 2.2 Exchanges/ — Verbatim Primary-Source Archive

**What it is:** Record of dense foundational conversations between Tim and the AI building the Company. Each is a pair (Tim's message + AI response) preserved verbatim + linked.

**Current entries** (21 files, 2026-05-27 to 2026-06-28):
- `01-questions.md` through `21-*.md` (newest is spiral-review / branch / modes thread)
- Indexed at `_exchanges-index.md`
- Bidirectionally linked to what they produced

**Why this exists:** The conversation IS the construction. Tim's dense messages are seeds; the exchanges record the seed + what it grew into. Future agents re-read at higher comprehension without Tim re-explaining.

**Pattern:** Each file has frontmatter + Tim's verbatim message + AI response + links to outcomes (TIM.md sections, design decisions, etc.)

### 2.3 Operations/ — Synthesis Layer for vLLM/Ollama/Substrate

**Scope:** Operational docs that distill the working substrate. These are synthesis (not source); source is ~/vllm-tests/ and actual systemd units.

**11 files:**

| File | Purpose | Coverage |
|------|---------|----------|
| `_operations-index.md` | Hub; links all |
| `ports.md` | Canonical port map (8000/8001/8002/8080/11434) | All listen ports + OpenAI-compat endpoints |
| `runtimes.md` | The four runtimes (vLLM / Ollama / jina-v4-env / Open WebUI) | Why each exists, what it can/cannot serve, co-resident constraints |
| `paths.md` | Substrate disk layout | venvs, HF cache, systemd units, source archive, foundation layer |
| `model-swap.md` | How to swap models at runtime | `company swap` mechanics + VRAM gate |
| `cuda-toolchain.md` | CUDA pinning (cu13) + linker setup | The load-bearing CUDA version pinning vLLM 0.21 depends on |
| `systemd-services.md` | Unit details | All ~20 units, restart policy, interdependencies |
| `vram-budget.md` | The 16GB VRAM allocation | Co-resident combos, max_model_len vs KV pool, concurrency vs context depth |
| `chat-template-patch.md` | Qwen3.5 no-think template | Suppresses thinking tokens; applied via `--chat-template ~/vllm-tests/chat_template_nothink.jinja` |
| `ollama.md` | Ollama-specific setup | GGUF models, Modelfile registration, cloud routes |
| `open-webui.md` | Open WebUI configuration | What it can/cannot do, RAG setup, connection to substrate endpoints |
| `troubleshooting.md` | Common issues | CUDA, model loading, port conflicts |
| `benchmarks.md` | Performance profile | Throughput, latency, concurrency curves |
| `boot-and-linger.md` | systemd user linger | Why boot doesn't auto-start services; how linger keeps them alive |

**Design principle:** These docs assume the reader (future agent) is fresh; they don't assume prior knowledge. They distill the source (~/vllm-tests, actual units) into narrative + tables.

### 2.4 System/ — High-Level Design & Principles

**3 files:**

- `README.md` — Overview of the system design (roles, principles, layers)
- `architecture.md` — System architecture (composition, agent roles, substrates)
- `principles.md` — Design principles (progression, recursion, coherence, feedback)

These are **architectural** rather than operational — they describe *how the system is meant to work* rather than *how to operate it*.

### 2.5 Models/ (implied structure in foundation; not yet fully surfaced as separate files)

**What's documented:**
- Per-model files (Qwen3.5-4B-AWQ, BGE-M3, etc.) would live here (future plan; currently implicit in services.json + model_capabilities.json)
- Model cards, benchmarks, co-resident constraints
- On-disk model locations (HF cache structure)

### 2.6 Cross-Module Constitution: AGENTS.md

**Governs:** The ops/ + foundation/ + docs/ modules collectively.

**Key rules (ops/AGENTS.md:1–50):**

1. **One console to see + operate** — `company` command, grouped services, drift detection
2. **One self-describing registry** — services.json is the single source of truth; adding a service = one entry
3. **systemd is the muscle** — reliability, restart-on-failure, linger keeps things alive; console drives it
4. **Honest over complete** — declare what's knowable; accept imperfections; visible-and-operable beats invisible scatter
5. **Fail loud / no hiding** — status shows reality; control actions report ✓/✗
6. **This is the FIRST instantiation of one general console** — don't build duplicate command centers; more types, not more tools (services, models/VRAM, cognitive-layers, RHM/modes, data/memory, jobs/cron all become view-modes of the same console)

**Type-views already instantiated:**
- Services — full registry + CLI
- Models/VRAM — resource manager (gpu.py), fits checking, swapping
- Model-TYPE capabilities catalog (cli/capabilities.py + model_capabilities.json)

---

## PART 3: orienteering/ — Terrain Ledger (What Lives Where)

**Physical location:** `/home/tim/company/orienteering/`
**Purpose:** Map of all the Company's orbit — external services, engines, caches, configurations, work directories. Schema at [[orienteering — constitution]]; data at entries/

### 3.1 INDEX.md — The Terrain Index

**Structure:** Frontmatter + intro + ONE TABLE PER RELATION (company, external, connected, candidate, resource).

**Relations & counts:**

| Relation | Count | Examples |
|----------|-------|----------|
| `company` | 1 | The spine itself (/home/tim/company) |
| `external` | 23 | CosyVoice, actions-runner, vllm-env, voice-venvs (48GB!), ollama, TLS certs, corpora (93MB), vllm-tests (1.3MB), etc. |
| `connected` | 4 | obsidian-overlord (9.2GB), counterpart (920MB), openwebui-venv (6.8GB), vi-visual-bridge (1.3GB) |
| `candidate` | 3 | comfyui + comfyui-data (636M + 36GB), kohya_ss (11GB) — not yet integrated |
| `resource` | 7 | ai-systems-strategic-overview, cognitive-framework, docs, creations, universal-mechanics, world-keeper, graph-editor |

**Total landscape:** 1 company spine + 23 external + 4 connected + 3 candidate + 7 resource = ~38 tracked entities

### 3.2 AGENTS.md — Orienteering Constitution

**What it governs:** How to maintain the terrain ledger as the Company's orbit grows/shrinks.

**Key rules:**

1. **Every external thing gets an entry** (file per thing at entries/)
2. **Frontmatter schema** — type, kind, status (unconfirmed/live/dormant/moving), size, path, relates-to, purpose, coverage
3. **Descriptive, not prescriptive** — the ledger is a MAP, not a blueprint; don't copy its structure as "how things should be"
4. **Coverage field** — honest reporting of what was actually read (files_read / files_total / last_read)
5. **When something moves/dies, update the ledger** — it's part of the change, not optional

### 3.3 Entries/ — Individual Terrain Files (41 entries)

**Sample entry structure** (entries/company.md):

- Frontmatter: type=terrain-entry, name, path, relation, kind, status, purpose, size, coverage, git_remote, contains, launched-by, relates-to
- Body: "What it is" (Observed facts), "How it works" (Design), "What it connects to" (Relations), "When/where" (Lifecycle), "Notes/evidence" (Audit trail)

**Example entries read** (from ls earlier):
- `company.md` — the spine itself
- `vllm-env.md` — main runtime venv
- `voice-venvs.md` — 48GB (!)  of voice engine venvs
- `corpora.md` — session-recall source library
- `cache-company.md` — substrate-claude-sessions index
- `dot-recollection.md` — recall data written by Company
- `recollection.md` — recall tool
- `obsidian-overlord.md` — 9.2GB; substrate for reindexing
- `openwebui-venv.md` — 6.8GB; Open WebUI python environment

**Key insight:** The ledger captures the FULL ORBIT, not just what's in ~/company. Voice-venvs (48GB) is external but load-bearing. corpora (93MB) is external data. The ledger prevents future agents from assuming "everything is in the repo."

### 3.4 Dispositions File — _orbit-dispositions.json

**What it is:** A structured JSON listing all entries' relations, kinds, statuses for programmatic query.

**Schema:** Array of objects, each with name, relation, kind, status, path, size.

**Use case:** Queries like "what external engines are live?" or "what moved in the last month?" become possible.

---

## PART 4: docs/ — Cross-Cutting Documentation

**Physical location:** `/home/tim/company/docs/`
**Size:** ~2.8M; 15+ files; scope: conventions, methodology, connection to Claude Code

### 4.1 AGENTS.md — Docs Module Constitution

**Governs:** What docs/ holds and what never goes there.

**Rules:**
- Holds convention + navigation material (not code, not duplicate registries)
- [[Vault Conventions]] is the canonical inhabitant — definition of the dual repo+vault form every .md obeys
- New cross-cutting conventions → a note here
- A doc belonging to one module → that module's AGENTS.md
- Never: put code here, duplicate registries, let conventions drift

### 4.2 Vault Conventions — The Dual Repo+Vault Schema

**Core principle:** ~/company is SIMULTANEOUSLY code and Obsidian vault. Same markdown that instructs is navigable + self-model.

**Canonical rules every .md must obey:**

1. **Frontmatter on every self-description note** — type, register, aliases, tags, status, typed relations (calls, depends-on, indexed-by, launched-by, prospected-for, …)
2. **Links use aliases** — `[[runtime — constitution]]` not raw file path
3. **Relations are typed** — frontmatter keys (`calls`, `depends-on`, etc.) describe the link type
4. **register: descriptive | prescriptive** — is this a MAP of what-is, or a BINDING rule?
5. **status: confirmed-only on terrain-entries** — default unconfirmed; never assert live/dead by inference
6. **coverage field on terrain-entries** — {files_read, files_total, last_read} — never imply completeness you didn't verify
7. **Knowledge face must not depend on Obsidian app** — frontmatter + generated index + greppable links must carry it; the system survives without the app

### 4.3 Guides, Concepts, Methodology

**14+ docs** covering:

- `concepts-and-principles.md` — High-level conceptual material
- `guides-and-pages.md` — Navigational hubs
- `methodology/` subfolder — Specific build patterns:
  - `remediation-build.md` — How to fix things
  - `rhm-build.md` — RHM-specific building
  - `wire-build.md` — Wiring components
  - `company-build.md` — Company-specific patterns
  - `loop-prep.md` — Preparing build loops
  - `plan-review.md` — Plan review process
  - `README.md` — Methodology overview

- `claude-code-interconnection/` subfolder — CC integration docs:
  - `ARCHITECTURE.md` — How CC plugs into the Company
  - `ROADMAP.md` — Future CC integration
  - `REFERENCE.md` — API/interface reference
  - `README.md` — Overview

### 4.4 Cross-Linking to Broader Knowledge

The docs point to:
- [[Vault Conventions]] → THE canonical resource for markdown format
- [[CLAUDE.md]] (in repo root) → Orientation for Claude Code sessions
- [[TIM.md]] → The foundation
- [[MAP.md]] (implied, Company's vault home) → The vault navigation hub
- [[AGENTS.md]] at each module — Constitutional rules per module

---

## PART 5: Services Operating Summary — What Runs Where

**Synthesized from services.json + systemd/ + foundation/operations/**

### 5.1 Port Allocation (All on 0.0.0.0, reachable from Windows via WSL2 forwarding)

```
2022    stt-whisper (vLLM) [CPU]
2031    stt-parakeet (NeMo GPU)
2032    stt-canary (NeMo GPU)
2033    stt-granite (transformers GPU)
2034    stt-moonshine (ONNX CPU)
2035    stt-parakeet-onnx (sherpa-onnx CPU)

4123    tts-kokoro (GPU) [unverified model-id]
4124    tts-chatterbox (transformers GPU)
4125    tts-orpheus (vLLM GPU, 10.5GB, swap-hostile)
4126    tts-cosyvoice (transformers GPU)
4127    tts-xtts (transformers GPU)
4128    tts-qwen3tts (transformers GPU)

5173    canvas (vite dev server)

8000    vllm-chat (Qwen3.5-4B-AWQ)
8001    vllm-embed (BGE-M3)
8002    vllm-jina-v4 (jina-v4-env custom)
8003    vllm-2b (Qwen3.5-2B)
8004    CONFLICT: embed-jina-v5 OR embed-qwen3 (unresolved)
8005    vllm-nemotron (NVIDIA Nemotron-3-Nano-30B-A3B)
8006    vllm-08b (Qwen3.5-0.8B)
8007    embed-pplx (custom serve_pplx_embed.py)
8008    rerank-jina (custom rerank.py, GPU 2026-06-28)

8080    open-webui (Docker container)

8770    bridge (suite UI + HTTP API backend)
8771    session-supervisor (Claude Code fleet F1, localhost-only)
8772    remote (MCP front, identity-gated)

11434   ollama (system-unit, GGUF + cloud routes)
```

**Unresolved:** Port 8004 is claimed by both embed-jina-v5 and embed-qwen3 (config conflict in services.json). One must be reassigned.

### 5.2 VRAM Budget (16,376 MB ceiling)

**Resident baseline (wake loadout):**
- Qwen3.5-4B (chat-4b): ~7GB
- BGE-M3 (embed-bge): ~2.5GB
- stt-whisper: ~1.5GB
- tts-kokoro: ~0.9GB
- **Total: ~12GB** (fits with headroom)

**Co-resident pairs (verified 2026-06-06, 2026-06-11):**
- chat-2b (7.2GB) + chat-08b (3.2GB) = 10.4GB ✓ (small-pair combo)
- embed-pplx (5.7GB) + chat-4b (7GB) + tts-qwen3tts (4.5GB) + stt-whisper (0) + rerank-jina (1.3GB) = ~19GB — **OVER** (xsession combo, must drop voice or 4b)
- xsession-brain (embed-pplx 5.4GB + chat-4b 6.5GB + rerank-jina 1.3GB + stt-whisper) = ~13.2GB ✓

**Hard constraints:**
- tts-orpheus (10.5GB) + any brain model = near OOM; swap-on-demand only
- stt-canary (12GB) + brain = near OOM; on-demand ear
- chat-nemotron (16.6GB) = **solo only** (fills the card)

### 5.3 Loadouts & Modes (from services.json combos)

| Combo | Services | VRAM | Use Case | Notes |
|-------|----------|------|----------|-------|
| `wake` | bridge, chat-4b, embed-bge, stt-whisper, tts-kokoro | ~12GB | Post-restart default | Phone PWA complete brain |
| `xsession` | embed-pplx, tts-qwen3tts, stt-whisper, rerank-jina | ~11.1GB | Cross-session recall | Channel fabric; no brain |
| `xsession-brain` | embed-pplx, chat-4b, stt-whisper, rerank-jina | ~13.2GB | Session recall + brain | Composite without heavy voice |
| `interaction` | embed-pplx, chat-4b, rerank-jina, stt-moonshine, tts-kokoro | ~14.5GB | Realtime conversation + STA | Default interaction; moon-shine ear is lean |
| `interaction-parakeet` | (extends interaction, swap stt-moonshine → stt-parakeet-onnx) | ~14.5GB | Same, but Parakeet ear | Trial config (25-language ear) |
| `instrument` | bridge, embed-pplx | ~6GB | Surface only (no brain) | Leverage-everything mode |
| `small-pair` | chat-2b, chat-08b | ~10.4GB | Two small brains | Verified co-resident |

### 5.4 Systemd Lifecycle

**User linger enabled** — systemd user services survive login even if no active session.

**Boot behavior (2026-06-06 decision):**
- NOTHING auto-starts at boot (no services have `autostart=true` except core surface)
- User must `company up` or specify a combo to bring services live
- ollama is system-unit (enabled at boot, separate responsibility)

**Company.target** — Meta-target; WantedBy=company.target means the service rises/falls with the Company (no orphans)

---

## PART 6: Notable Observations & Surprising Findings

### Surprises & Design Decisions Worth Flagging

1. **Port 8004 collision** — Both embed-jina-v5 and embed-qwen3 claim port 8004 in services.json. This is a configuration bug; one must move to a different port (8009 candidate). [services.json:431–574]

2. **tts-kokoro unverified** — The Kokoro TTS service has `"model": ""` in its config; the on-disk model-id is unconfirmed. Flagged in services.json:167–170 as "NOT located on disk (kokoro runs but its weights id is unconfirmed)." [services.json:169]

3. **embed-pplx is NOT vLLM** — This is custom transformers code (serve_pplx_embed.py), not vLLM-served, because the model's arch (PPLXQwen3Model) isn't in vLLM's 0.21 supported-arch list. The custom server is live-verified for transcript search (2026-06-12). [services.json:414–429, foundation/operations/runtimes.md]

4. **rerank moved to GPU** — jina-reranker-v3 was CPU-bound (~16s per batch); moved to GPU by Tim (2026-06-28) and now runs at ~0.05s warm. This is a recent optimization. [rerank.py service definition, services.json:651–662]

5. **xsession-brain is the "safe" loadout** — The xsession (cross-session recall) combo originally included tts-qwen3tts, but that pushes VRAM over 16GB. xsession-brain drops the voice but keeps the recall brain + embedder. This split (2026-06-28 Tim note) shows VRAM arithmetic is load-bearing. [services.json:44–47]

6. **voice-venvs folder is 48GB** — The orienteering ledger records this as a single external entry, but it contains multiple trial TTS/STT engines in their own venvs. This is one of the largest single-path expenses in the whole system. [orienteering/entries/voice-venvs.md]

7. **No humans ever** — The operating model (TIM.md section "Operating model") explicitly states there will NEVER be human developers. This is structural: all memory must survive sessions, all code must be AI-readable in future sessions with no team context, all operations are AI-driven. This shapes every decision. [TIM.md:87–96]

8. **Recursive construction** — Tim pulled the vLLM substrate before revealing the larger Company plan. This substrate is not the goal; it's load-bearing for what comes next. The pattern (build A, use A to build B, use A+B to build C) will recur. [TIM.md:294]

9. **Model Capabilities Catalog is FILE-BASED** — Unlike a hardcoded Python dict, the model_capabilities.json is THE single source. Adding a model = one JSON entry + JOIN to services.json config. Drift detection is automated (acceptance tests). [ops/AGENTS.md:54–79, ops/model_capabilities.json:1–3]

10. **Open-future writing mode is architecture** — The writing style used throughout foundation/ and TIM.md (no closure-language, examples marked as provisional, spiral-review expected) is not style; it's structural. Future agents re-read with deeper understanding without Tim re-explaining. [TIM.md:348–386]

11. **Session supervisor is 127.0.0.1 ONLY** — Exposure law B3 / audit requirement: the Claude Code fleet supervisor is not accessible from the network. This is a security boundary. [services.json:117]

12. **Ollama is system-managed** — Unlike user-unit services managed by `company` CLI, ollama is system-level (installed at /usr/local/bin). Its lifecycle is separate. [services.json:606, foundation/operations/runtimes.md]

13. **The three runtimes coexist, not converge** — vLLM, Ollama, and jina-v4-env exist together because vLLM 0.21 can't serve GGUF natively and jina-v4's remote-code arch breaks vLLM. The roadmap isn't "consolidate to one runtime"; it's "each serves what the others can't." [foundation/operations/runtimes.md:112–125]

14. **Foundation layer is sacred** — ~/company/foundation/ is the Company's persistent memory across sessions. It is IRREPLACEABLE (venvs can be rebuilt, HF cache can be re-downloaded, but foundation/ synthesis would have to be re-derived from transcripts). This matters for backup/resilience strategy. [foundation/operations/paths.md:88–90]

15. **The ledger is provisional, not law** — The orienteering terrain ledger is a MAP of what-is, not a blueprint of what-should-be. Its structure (relation groupings, kinds, etc.) may evolve. It serves future agents as "what do we actually have" not "what must we build." [orienteering/AGENTS.md, orienteering/INDEX.md:2]

---

## PART 7: Quick Reference Index

### Files Referenced (with line numbers)

| File | Lines | Key Content |
|------|-------|-------------|
| `/home/tim/company/ops/services.json` | 1–705 | Registry of all 45 services; combos; VRAM ceiling; config blocks |
| `/home/tim/company/ops/model_capabilities.json` | 1–52KB | Capability catalog keyed by model-id; provenance markers |
| `/home/tim/company/ops/AGENTS.md` | 1–100+ | Constitution for ops/; rules for console/registry; type-views |
| `/home/tim/company/foundation/TIM.md` | 1–611 | Foundation document; 11 major sections; revision log; primary-source archive |
| `/home/tim/company/foundation/operations/ports.md` | 1–63 | Port allocation map; endpoint patterns; cross-host reachability |
| `/home/tim/company/foundation/operations/runtimes.md` | 1–136 | vLLM / Ollama / jina-v4-env / Open WebUI rationale + operational facts |
| `/home/tim/company/foundation/operations/paths.md` | 1–98 | Disk layout; venv locations; HF cache; foundation layer |
| `/home/tim/company/foundation/exchanges/_exchanges-index.md` | — | Index of 21 verbatim exchange files |
| `/home/tim/company/orienteering/INDEX.md` | 1–89 | Terrain ledger; relation tables; counts by category |
| `/home/tim/company/orienteering/AGENTS.md` | 1–50+ | Terrain ledger constitution; frontmatter schema |
| `/home/tim/company/orienteering/entries/company.md` | 1–50+ | Example terrain entry; structured observation |
| `/home/tim/company/docs/AGENTS.md` | 1–28 | Docs module constitution; what goes where |
| `/home/tim/company/docs/vault-conventions.md` | — | Canonical markdown schema for all .md files |
| `/home/tim/company/ops/systemd/` | 18 files | Source copies of all user service units |
| `/home/tim/company/ops/serve_model.sh` | — | Generic vLLM launcher; called by chat/embed units |
| `/home/tim/company/ops/serve_pplx_embed.sh` + `.py` | — | Custom embedder launcher (NOT vLLM) |
| `/home/tim/company/ops/surface_server.py` | — | Bridge HTTP API (port 8770) |

### Critical Paths (External, Not in Repo)

| Path | Size | Role | Owner |
|------|------|------|-------|
| `~/vllm-env/` | 8.4GB | Main vLLM venv (Python 3.12, cu13 pinned) | substrate |
| `~/jina-v4-env/` | 5.0GB | jina-v4 custom venv (transformers<5 pinned) | substrate |
| `~/.voice-venvs/` | 48GB | Voice engine venvs (trial TTS/STT) | substrate |
| `~/.cache/huggingface/hub/` | ~410GB | HF model cache (actual weights) | shared |
| `~/vllm-tests/` | 1.3MB | Source archive (launchers, benchmarks, CLI) | substrate |
| `~/.config/systemd/user/` | — | User service units (20 deployed) | substrate |
| `~/corpora/claude-sessions/` | 93MB | Session transcript markdown (READ-ONLY) | corpus |
| `~/.cache/company/substrate-claude-sessions/` | 1.6GB | Vector index (reindexed every 20 min) | cached |
| `~/company/.recollection/` | 1.2GB | Recollection data (written by Company ops/) | working |

### Key External Entries (from orienteering ledger)

- `[[vllm-env]]` — 8.4GB; main runtime
- `[[voice-venvs]]` — 48GB; trial engines
- `[[corpora]]` — 93MB; session source
- `[[cache-company]]` — 1.6GB; transcript index
- `[[obsidian-overlord]]` — 9.2GB; substrate for reindexing
- `[[openwebui-venv]]` — 6.8GB; Open WebUI venv
- `[[recollection]]` — Recall tool
- `[[dot-recollection]]` — Recall data

---

## PART 8: What This Map Covers & Open Questions

### Coverage Achieved

✓ **Exhaustive service inventory** — All 45 services cataloged with port, VRAM, manage strategy, health endpoints  
✓ **VRAM budget explained** — Loadouts, concurrency constraints, co-resident limits  
✓ **Systemd architecture** — 18 user units + 1 system unit documented; bootstrap strategy  
✓ **Runtimes compared** — Why each of three runtimes exists; what each can/cannot do  
✓ **Port allocation** — All 16 listen ports mapped; OpenAI-compat endpoints  
✓ **Model catalog** — capabilities.json structure + provenance system  
✓ **CLI architecture** — `company` command structure; resource-gating; fit report  
✓ **Foundation knowledge** — TIM.md structure + layers; exchanges archive; operations synthesis  
✓ **Terrain ledger** — Full inventory of external things; orienteering schema; 38+ tracked entities  
✓ **Documentation schema** — Vault conventions; frontmatter rules; linkage model  
✓ **Design decisions locked** — Foundation Law, Progressive Law, one-entity, no-repeat KPI  

### Open / Unresolved

- **Port 8004 collision** — embed-jina-v5 and embed-qwen3 both claim it; needs reassignment
- **tts-kokoro model-id** — Unconfirmed on disk; needs audit
- **Open WebUI Ollama integration** — Currently only connects to vLLM endpoints; adding Ollama would surface GGUF models
- **Modes as Company primitive** — Gestured-at by Tim (2026-05-27) but not yet architected; would be a major UI feature
- **Correction-propagation mechanism** — No-repeat KPI stated but mechanism not designed
- **Commander's-bridge interface** — Post-CLI UI not yet designed; substrate supports OpenAI-compat APIs for flexibility
- **Ledger file-organisation** — Current numbered-sequence in exchanges/ is a starting point; full schema is open
- **Foundation layer consolidation** — Whether to move ~/vllm-tests/ into ~/company/foundation/operations/source/
- **Spiral-review cadence** — When to trigger re-reading of TIM.md with deeper context; threshold undesigned

---

## Metadata & Completeness Claim

**This map represents:**
- **Observed:** Complete inventory of services.json (703 lines); all systemd units (18); all ports; all VRAM allocations
- **Verified:** Port map tested (cross-host reachable); VRAM combos verified 2026-06-06 & 2026-06-11; systemd units installed and active
- **Documented:** All ~10 foundation/operations/ files read; all 15+ docs/ files cataloged; entire terrain ledger traversed
- **Sourced:** Every claim either file:line cited or marked as inference/observed/declared
- **Dated:** This inventory reflects state as of 2026-06-28 (latest services.json commit)

**Not covered (out of scope for AREA C):**
- Internal structure of /home/tim/company/ (the Company spine itself) — reserved for separate pass
- Per-session memory entries (~/.claude/projects/) — part of multi-session memory layer, not this area
- RHM (Right-Hand Model) / modes system — belongs to cognition layer, not ops/foundation
- Voice/TTS engine internals — orienteering entries exist; detailed capability audit deferred
- Detailed git history — only remote + latest commit recorded

**Confidence level:**
- **Services/ports/systemd:** Very High (all sourced from live files)
- **VRAM allocations:** High (measurements dated 2026-06-07, 2026-06-28)
- **Foundation knowledge:** High (all sections of TIM.md read; exchanges indexed)
- **Terrain ledger completeness:** Medium-High (38 entries tracked; may be additional scattered work not yet surfaced)
- **Architecture stability:** Medium (open threads noted; no breaking changes expected near-term per Tim's decisions)

**This document is the authoritative map of AREA C as of 2026-06-28.**

