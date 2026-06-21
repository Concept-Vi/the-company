# AREA: ops / platforms / docs / skills / contexts — Exhaustive Landscape

> Extraction date: 2026-06-21. Read-only pass; no source files edited.
> Every file in scope is listed. Volume is the goal — nothing filtered or judged away.

---

## 1. THE `company` CLI

### 1a. Entrypoint

**`ops/company`** (the PATH binary, symlinked to `~/.local/bin/company`)
- WHAT IT IS: thin Python shim, 14 lines
- WHAT IT DOES: resolves its own directory, inserts `ops/cli/` into sys.path, imports and calls `cli/app.py:main()`
- CROSS-REF: everything flows through `ops/cli/app.py`
- GAP: none — intentionally minimal

### 1b. `ops/cli/app.py` — the command dispatcher (the ONE console)

WHAT IT IS: the Company's single control surface for the whole running system.  
WHAT IT HOLDS: full command dispatch, GPU resource-manager integration, service lifecycle.

**Every subcommand** (from actual dispatch code):

| Command | What it does |
|---|---|
| `company` / `company status` | Renders `render.status(reg)` — groups all services, live state symbols (▶ ◐ ✖ ·), ~VRAM cost, GPU budget line |
| `company gpu` | Renders `gpu.format_state(reg)` — measured VRAM used/free/total + what's holding the card (all running GPU services, sorted by mb desc) |
| `company health` | Renders `render.health(reg)` — port ping ✓/✗ for every service with a port |
| `company suites` | Runs `tests/suite_health_acceptance.py` in a temp COMPANY_STORE env. THE ALL-GREEN GATE — every acceptance suite standalone, pre-merge/pre-deploy. Propagates exit code. |
| `company coherence` | Runs `runtime/coherence_detect.format_scan(scan(repo))` — structural gap detection. Fast (AST/registry, no subprocess). |
| `company models` | `models.inventory()` — HF cache + Ollama models on disk |
| `company telemetry` | `telemetry.rollups()` — per-service: loads, avg load time, measured VRAM vs registry estimate |
| `company session [sub]` | Routes to `cli/sessions.py:run(args[1:])` — the supervised Claude Code fleet |
| `company board [sub]` | Routes to `cli/board.py:run(args[1:])` — the Company NOTICEBOARD |
| `company clone [sub]` | Routes to `cli/clone.py:run(args[1:])` — the clone-fleet distributed-memory read |
| `company combos` | Lists all `services.json combos` entries (name, services, note) |
| `company config SERVICE [KEY VAL]` | Show or edit a service's `config` block (edits via `registry.set_config`, then prompt to restart) |
| `company swap SERVICE MODEL_ID` | `models.swap(reg, svc, model)` — rewrites config.model or serve-script MODEL default, restarts |
| `company ensure MODEL\|SERVICE [--evict] [--no-wait]` | `capabilities.ensure_resident(...)` — the gated launch/select/evict actuator |
| `company up [TARGET] [--evict] [--force] [--wait]` | Calls `_act(reg, "up", keys, ...)` — GPU budget gate (refuses / evicts / forces), then `systemd.control(svc, "start")` |
| `company down TARGET` | `_act(reg, "down", keys)` — calls `gpu.teardown(svc)` — orphan-safe (cgroup for units, pgroup for manual) |
| `company restart TARGET [--evict] [--force] [--wait]` | `_act(reg, "restart", keys, ...)` |
| `company logs SERVICE [-f]` | `systemd.journal(svc, follow)` — journalctl last 60 lines |
| `company help` | Prints the module `__doc__` string |

**TARGET resolution** (from `registry.resolve`):
- None/"default" → `autostart:true` services only (currently: canvas + bridge)
- "all" → all services
- group name (core|brain|voice|models|reach|jobs) → all services in that group
- `@<combo>` → combo's service list
- a service key → just that service

**`--wait` flag**: after `up`/`restart`, blocks polling port_open/is_active for each GPU service (up to 420s), then records measured VRAM + load time to `cli/telemetry.jsonl` (solo GPU loads only — concurrent loads don't attribute VRAM per-service).

**`_act` resource-manager gate**:
1. Always shows `gpu.format_state(reg)` (what's holding the card)
2. `gpu.check_fit(reg, keys)` — measured free vs sum of budgets for not-yet-running GPU services
3. If doesn't fit: `--evict` → `gpu.plan_eviction` → stop evictees (models→brain→voice, largest first) then proceed; `--force` → proceed over budget with warning; else REFUSE + exit(2)

**CROSS-REF**: `cli/gpu.py` (the ONE VRAM authority), `cli/registry.py` (reads services.json), `cli/systemd.py` (start/stop/status), `cli/capabilities.py` (ensure_resident), `ops/services.json` (the registry)

### 1c. `ops/cli/registry.py` — the registry reader

- WHAT IT IS: loads and queries `services.json`. Stdlib-only, no state.
- KEY FUNCTIONS:
  - `load()` → reads `ops/services.json` as dict
  - `save(reg)` → writes back (pretty JSON, used by `config`/`swap`)
  - `resolve(reg, target)` → target → list of service keys (see above)
  - `vram_of(svc)` → the VRAM estimate for a service (top-level or load.vram_mb)
  - `ceiling_mb(reg)` → the card ceiling (default 16376 MB)
  - `combos(reg)` → named service-sets (filters `_doc` key)
  - `set_config(reg, key, field, value)` → edits a config block field, saves
  - `serve_script(svc)` → path to the service's serve script (for `swap`)
  - `shared_ports(reg)` → ports used by >1 service (so port-open can't distinguish siblings)
- CROSS-REF: `ops/services.json` (the source), `cli/gpu.py` (imports vram_of, ceiling_mb)

### 1d. `ops/cli/gpu.py` — the ONE VRAM resource manager

- WHAT IT IS: the shared VRAM authority for BOTH the `company` CLI AND `voice/lifecycle.py`. Stdlib-only.
- WHAT IT HOLDS:
  - NVSMI path: `/usr/lib/wsl/lib/nvidia-smi`
  - Eviction priority order: models(0) → brain(1) → voice(2), largest-first within each
- KEY FUNCTIONS:
  - `read_gpu()` → dict(used, free, total, util) or None (uses nvidia-smi)
  - `budget_vram(reg, key)` → priority: 1. config.gpu_util × ceiling, 2. learned telemetry, 3. registry vram_mb estimate
  - `running_gpu_services(reg)` → [(key, mb)] for services that are UP and GPU-occupying (per-unit is-active, NOT port, to handle shared ports)
  - `check_fit(reg, to_start)` → (ok, need_mb, free_mb, gpu_present)
  - `fit_report(reg, keys)` → full dict for the settings fit-surface (selection × fits_card × fits_now × evict)
  - `plan_eviction(reg, to_start, need, free)` → (evict_keys, projected_free) — models→brain→voice, largest first
  - `teardown(svc)` → orphan-safe stop: unit services → `systemctl stop` (cgroup kills EngineCore); manual → pgroup SIGTERM then SIGKILL
  - `format_state(reg)` → the "what's holding the card" block
  - `committed_mb(reg)` → sum of budgets across running GPU services
- CROSS-REF: `cli/telemetry.py` (learned_vram), `cli/systemd.py` (port_open, is_active, control), `cli/registry.py` (vram_of, ceiling_mb)
- SURPRISING: GPU detection falls back to registry estimates when nvidia-smi unreadable (WSL2 sometimes flaky)

### 1e. `ops/cli/systemd.py` — systemd driver

- WHAT IT IS: drives systemd/journald for the registry's services. Stdlib-only.
- KEY FUNCTIONS:
  - `_scope(svc)` → ["--user"] or [] (user-unit vs system-unit)
  - `port_open(port, timeout=0.4)` → socket TCP connect test
  - `is_active(svc)` → "active"|"inactive"|"failed"|"not-managed"|"unknown" (via `systemctl is-active`)
  - `verdict(svc, shared_ports)` → (label, symbol) — AUTHORITATIVE via per-unit is-active, NOT port (shared-port safety); infers "RUNNING (unmanaged)" when port unique and open but unit inactive
  - `control(svc, action)` → (ok, message) for start/stop/restart; manual services always return False
  - `journal(svc, follow)` → streams journalctl last 60 lines; manual services raise ValueError

### 1f. `ops/cli/render.py` — status + health views

- `status(reg)` → full service table grouped by group, with live state symbols, port, VRAM, GPU budget line
- `health(reg)` → ✓/✗ port ping per service

### 1g. `ops/cli/models.py` — model inventory + swap

- `inventory()` → lists HF cache (`~/.cache/huggingface/hub/models--*`) + Ollama store
- `swap(reg, key, model_id)` → for config-driven services: sets config.model in registry, saves, restarts; for legacy script-based: rewrites `MODEL="${1:-...}"` in serve script, restarts
- CROSS-REF: `cli/registry.py` (serve_script), `cli/systemd.py` (control)

### 1h. `ops/cli/sessions.py` — the supervised Claude Code fleet type-view

- WHAT IT IS: `company session` commands. Pure stdlib HTTP client against the supervisor at 127.0.0.1:8771.
- SUBCOMMANDS:
  - `company session` / `list` → GET /sessions → print fleet rows
  - `company session new [--cwd D] [--resume ID] [--fork] [--name L] [--prompt "..."]` → POST /spawn
  - `company session send <id> <msg...>` → POST /inject
  - `company session stop <id>` → POST /teardown
  - `company session cap` → GET /health → shows COMPANY_FABRIC_CONCURRENCY cap + live count
  - `company session fleet` → GET /sessions → filters clone- sessions
- FAIL LOUD: if supervisor is down, exits with `✖ the session supervisor is not up`. Never spawns claude itself.

### 1i. `ops/cli/board.py` — the Company NOTICEBOARD type-view

- WHAT IT IS: `company board` commands. Talks directly to `runtime/cc_board.py` (no service — pure file I/O).
- SUBCOMMANDS:
  - `company board` / `list [--type T] [--state S] [--source SRC] [--author A]` → filtered list
  - `company board file --type T --title "..." [--body "..."] --author A [--source SRC] [--channel C] [--thread TH] [--link kind:target ...]` → file a typed item
  - `company board get <id>` → read one item (full)
  - `company board transition <id> <to_state> [--by WHO] [--note "..."]` → move along lifecycle
  - `company board types` → print registries (valid item-types/sources/edge-kinds)
- CROSS-REF: `runtime/cc_board.py` (the actual logic)

### 1j. `ops/cli/clone.py` — the clone-fleet read surface

- `company clone` / `list` → list all clone:// records from `.data/clones/`
- `company clone get <clone://addr>` → read one clone record + its persisted reflection
- CROSS-REF: `runtime/cc_clone.py`

### 1k. `ops/cli/capabilities.py` — the model-TYPE capability registry (the full thing)

- WHAT IT IS: the third keying in the model machinery (B4). Intrinsic capability by MODEL-ID (not service-key). JOINs to `gpu.py` for VRAM. File-discovered catalog from `ops/model_capabilities.json`.
- CAPABILITY TAGS: chat, json, tools, fast, no-think, vision, thinking, reasoning, embed, rerank, tts, stt
- PROVENANCE VOCABULARY: declared, probed, measured, served
- KEY FUNCTIONS:
  - `_load_catalog()` → reads `model_capabilities.json`, FAIL LOUD on missing/malformed/empty
  - `MODEL_CAPABILITIES` → the live catalog loaded at import
  - `reload_catalog()` → re-reads disk into the live dict (for the "add a row → it appears" verification)
  - `service_key_for(reg, model_id)` → JOIN: finds service whose config.model == model_id
  - `capabilities_for(model_id, reg, live_probe)` → full capability row + deployment/VRAM JOIN + resident status. Unknown model → structured ASK result, never fabricated.
  - `catalog(reg)` → whole capability catalog, every model-id JOINed
  - `provides_for(model_id)` → the provides TAG set (what the weights can do)
  - `role_can_bind(requires, model_id)` → requires ⊆ provides? True/False
  - `suitable_models(requires, reg)` → all model-ids whose provides ⊇ requires
  - `placement_for(track)` → policy for 'swarm'|'main_brain'|'background' (the C8.3 cloud-decoupling DATA)
  - `swarm_survives_cloud_brain()` → invariant: choosing cloud brain NEVER removes resident swarm
  - `is_resident(model_id, reg)` → is the backing service currently active?
  - `require_resident(model_id, reg)` → LOUD OFFER_LOAD if not resident, NEVER auto-loads
  - `ensure_resident(model_or_service, *, evict, reg, wait, timeout)` → THE GATED ACTUATOR (#50): no-op if resident; loads if fits; if needs eviction + evict=False → G14 swap-approval ASK (returns structured dict with would_evict, would_load, approval hint); evict=True → executes eviction plan then loads; RAISES EnsureResidentError on genuinely impossible. Reuses gpu.check_fit / gpu.plan_eviction / gpu.teardown / systemd.control — NOT _act.
  - `ensure_loadout_for_mode(mode, ...)` → B/mode-loadout consumer: reads mode.brain_config, ensures brain service resident, surfaces gpu_util-variant gap loudly
  - `EnsureResidentError` exception class
- CROSS-REF: `ops/model_capabilities.json` (the catalog data), `cli/gpu.py` (all VRAM math — REUSED), `cli/registry.py`, `cli/systemd.py`

### 1l. `ops/cli/serveconfig.py` — vLLM args emitter

- WHAT IT IS: called by `serve_model.sh`. Reads a service's `config` block from `services.json` and prints args one-per-line for the shell launcher.
- `args_for(key)` → builds vLLM CLI args from config.model, port, host, gpu_util, max_model_len, max_num_seqs, flags (expands ~ paths)
- `env_for(key)` → KEY=VALUE lines from config.env
- Called as `python serveconfig.py <key>` or `python serveconfig.py <key> --env`

### 1m. `ops/cli/bench.py` — stack benchmarks

- WHAT IT IS: thin wrapper. Looks for bench scripts under `~/vllm-tests/` in `~/vllm-env/bin/python`.
- BENCHMARK KINDS: chat (bench.py), embed (bench_embed.py), suite (bench_suite.py), long-ctx (bench_long_ctx.py)
- GAP: requires ~/vllm-tests/ scripts to exist (not in this repo)

### 1n. `ops/cli/telemetry.py` + `telemetry.jsonl`

- WHAT IT IS: append-only JSONL log of real model loads. Keyed by SERVICE KEY.
- `record(service, load_seconds, resident_mb, estimate_mb, model)` → appends to `cli/telemetry.jsonl`
- `learned_vram(service)` → most-recent measured resident MB (used by gpu.budget_vram as the priority-2 estimate)
- `rollups()` → per-service: load count, avg load time, measured VRAM vs registry estimate (flags >1.5 GB divergence)
- `telemetry.jsonl` lives inside `ops/cli/` (alongside the Python module that writes/reads it)

### 1o. `ops/cli/README.md` + `ops/cli/UPDATING.md`

- README.md: the use guide. Comprehensive: all commands + the resource-manager flags + the tunable model config + combos + state symbols + "what's where" section
- UPDATING.md: extension guide — how to add a service to services.json, add a CLI command, add a systemd unit, migrate a script-based service to config-driven

---

## 2. THE SERVICE REGISTRY — `ops/services.json`

WHAT IT IS: the single self-describing source of truth for every service on this machine. The AI reads it cold to know the entire landscape.

### Groups

| Group | Description |
|---|---|
| core | Live interactive Company — the surface + its API (always-on heart) |
| brain | Language model(s) that answer |
| voice | Speech in and out |
| models | On-demand models — started per task, VRAM-budgeted, usually dormant |
| reach | Network + always-on system services |
| jobs | Scheduled timers — derived-data builders (no port) |

### VRAM ceiling: 16376 MB

### All Services

| Key | Group | Port | Unit | VRAM (MB) | Notes |
|---|---|---|---|---|---|
| canvas | core | 5173 | company-canvas.service | 0 | Vite dev server; autostart:true |
| bridge | core | 8770 | company-bridge.service | 0 | Suite UI HTTP API; autostart:true |
| session-supervisor | core | 8771 | company-session-supervisor.service | 0 | The supervised Claude Code fleet owner; 127.0.0.1 ONLY; COMPANY_FABRIC_CONCURRENCY cap (default 3) |
| chat-4b | brain | 8000 | vllm-chat.service | 7000 | Qwen3.5-4B-AWQ (config-driven); gpu_util=0.38; ctx 4096 (ceiling 262144); max_num_seqs=16; tool-calling (qwen3_xml parser); no-think template |
| tts-kokoro | voice | 4123 | company-tts-kokoro.service | 900 | Kokoro TTS; model id UNCONFIRMED (flagged gap) |
| stt-whisper | voice | 2022 | voicemode-whisper.service | 1500 | Whisper.cpp STT; the boot-default ear; OpenAI-compat /v1/audio/transcriptions |
| stt-parakeet | voice | 2031 | company-stt-parakeet.service | 5500 | NVIDIA Parakeet-TDT 0.6B v3; NeMo; own venv |
| stt-canary | voice | 2032 | company-stt-canary.service | 12000 | NVIDIA Canary-Qwen 2.5B; ~10 GB; on-demand only |
| stt-granite | voice | 2033 | company-stt-granite.service | 6500 | IBM Granite 4.0 1B Speech; own venv |
| tts-chatterbox | voice | 4124 | company-voice-chatterbox.service | 3800 | Clone + intensity; persona Viv |
| tts-orpheus | voice | 4125 | company-voice-orpheus.service | 10500 | vLLM-backed 3B; persona Pip; ~10 GB; SWAP-HOSTILE (~17min cold — pin/pre-warm) |
| tts-cosyvoice | voice | 4126 | company-voice-cosyvoice.service | 4200 | CosyVoice2-0.5B; instruct + clone; persona Tess |
| tts-xtts | voice | 4127 | company-voice-xtts.service | 2500 | XTTS-v2; clone; persona Wren; NON-COMMERCIAL license |
| tts-qwen3tts | voice | 4128 | company-voice-qwen3tts.service | 4500 | Qwen3-TTS-12Hz-1.7B-VoiceDesign; describe a voice; persona Sable; ~25s cold |
| embed-bge | models | 8001 | vllm-embed.service | 2500 | BAAI/bge-m3; config-driven; gpu_util=0.3 |
| embed-jina-v4 | models | 8002 | vllm-jina-v4.service | 8000 | jinaai/jina-embeddings-v4; CUSTOM server (transformers, not vLLM); serve_jina_v4.sh |
| embed-pplx | models | 8007 | company-embed-pplx.service | 8200 | pplx-embed-context-v1-4b; CUSTOM server (transformers); 2560-dim; INT8 UNNORMALIZED → cosine; contextual late-chunking |
| embed-jina-v5 | models | 8004 | vllm-jina-v5.service | 2000 | jina-embeddings-v5-text-small; config-driven; gpu_util=0.3 |
| chat-2b | models | 8003 | vllm-2b.service | 7200 | Qwen3.5-2B; config-driven; gpu_util=0.45; max_num_seqs=32 |
| chat-08b | models | 8006 | vllm-08b.service | 3200 | Qwen3.5-0.8B; config-driven; gpu_util=0.30; ultra-concurrency |
| chat-nemotron | models | 8005 | vllm-nemotron.service | 16600 | Nemotron-Nano-30B-A3B-AWQ; ~full card; 6GB cpu-offload |
| embed-qwen3 | models | 8004 | vllm-qwen3emb.service | 9000 | Qwen3-Embedding-8B; gpu_util=0.92 (SHARES port 8004 with embed-jina-v5) |
| llama-swap | models | (none) | llama-swap.service | 0 | model hot-swapper; no port in registry |
| litellm | models | 4100 | MANUAL (fabric/serve_litellm.sh) | 0 | LiteLLM proxy for fabric cognition; NOT for Claude Code (CC uses ollama-native :11434) |
| ollama | reach | 11434 | ollama.service (SYSTEM) | 0 | GGUF runtime; 0 VRAM idle; auto-on-boot |
| tailscale | reach | (none) | tailscaled.service (SYSTEM) | 0 | Tailnet + HTTPS serve to phone; auto-on-boot |
| pipeliner | reach | (none) | github-runner.service | 0 | GitHub Actions self-hosted runner; on-demand (was boot-autostart, changed 2026-06-06) |
| openclaw-gw | reach | (none) | openclaw-gateway.service | 0 | OpenClaw gateway Stage 2; usually dormant |
| agent-sessions-exporter | jobs | (none) | company-agent-sessions-exporter.timer | 0 | Claude session jsonl → ~/corpora/claude-sessions/ markdown; every 20 min |
| claude-sessions-reindex | jobs | (none) | company-claude-sessions-reindex.timer | 0 | Substrate DELTA reindex of claude-sessions vault; *:05/20 cadence |
| rerank-jina | models | 8008 | MANUAL (ops/serve_rerank.sh) | 0 | jina-reranker-v3; CPU only; POST /rerank |

**COMBOS** (named service sets for `company up @<name>`):
- `@small-pair` — chat-2b + chat-08b (verified co-resident ~12.3 GB)
- `@wake` — bridge + chat-4b + embed-bge + stt-whisper + tts-kokoro (the post-restart ritual, ~12GB)
- `@xsession` — embed-pplx + tts-qwen3tts + stt-whisper + rerank-jina (~12.6G cross-session fabric)
- `@instrument` — bridge + embed-pplx (instrument surface loadout)
- `@xsession-brain` — embed-pplx + chat-4b + stt-whisper + rerank-jina (cross-session + local brain, VERIFIED ~13.1G 2026-06-15)

**NOTABLE GAPS/SURPRISES**:
- Port 8004 is shared by `embed-jina-v5` AND `embed-qwen3` (only one can run at a time)
- Port 8000 is shared by `chat-4b` and potentially `chat-nemotron` (both brain group, only one at a time)
- `litellm` and `rerank-jina` are MANUAL services (no unit; `company up` refuses them, just points at the run command)
- `company-embed-pplx.service` has `[Install] WantedBy=default.target` instead of `company.target` (inconsistency flagged in BOOT-RUNBOOK.md)
- `tts-kokoro` model-id UNCONFIRMED (flagged in config._note)
- The 5 voice trial engines (chatterbox/orpheus/cosyvoice/xtts/qwen3tts) each have a systemd unit listed in services.json but their .service files are NOT in ops/systemd/ (they exist in ~/.config/systemd/user/ but are not canonical-copied into the repo)

### 2a. `ops/model_capabilities.json`

WHAT IT IS: The model-TYPE capability CATALOG. Declared data keyed by MODEL-ID. Loaded by `cli/capabilities.py` at import (fail loud on missing/malformed/empty).

WHAT IT HOLDS: Each model row has {tools, json_schema, thinking, context_ceiling, concurrency_knee, speed_profile, provides[...]} each with {value, source} provenance. Never stores vram (gpu.py JOINs that).

MODELS CATALOGED (sample — the full set spans the whole on-disk fleet):
- `cyankiwi/Qwen3.5-4B-AWQ-4bit` — resident worker (chat-4b); tools:served, json_schema:served, concurrency_knee C0.5-measured; provides [chat,json,tools,fast,no-think]
- `Qwen/Qwen3.5-2B`, `Qwen/Qwen3.5-0.8B`, `stelterlab/NVIDIA-Nemotron-3-Nano-30B-A3B-AWQ` — local chat workers
- BAAI/bge-m3, jina-embeddings-v4/v5, Qwen3-Embedding-8B, pplx-embed models — embedders; provides [embed]
- nomic-embed-code, LateOn-Code — code embedders (on disk, not yet served)
- Qwen3-VL-Embedding-2B, jina-v4 multimodal — provides [embed,vision]
- jinaai/jina-reranker-v3, cross-encoder/ms-marco-MiniLM-L-6-v2, Qwen3-VL-Reranker-2B — provides [rerank] (VL variant + vision)
- pplx-embed-context-v1-4b — the interim transcript-search embedder
- orpheus (Hariprasath28/orpheus-3b-4bit-AWQ), Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign — provides [tts]
- whisper/parakeet/canary/granite — provides [stt]
- ollama/cloud reasoners (kimi etc.) — chat models via ollama
- snac codec (0 capabilities), yolo_x_layout (vision)

---

## 3. OPS RUNBOOKS + DOCS

### `ops/AGENTS.md` — the ops constitution

WHAT IT HOLDS: the constitutional framing for ops/. Key laws: one console, one registry of truth, systemd is the muscle, fail loud/no hiding, honest over complete. Documents the type-views (services, models/VRAM, capability catalog, jobs/cron, sessions) and where new things go. Central architectural reference for the whole ops layer.

### `ops/BOOT-RUNBOOK.md` — boot recovery guide

WHAT IT IS: assembled 2026-06-20 from empirically-verified live state. The authoritative post-reboot sequence.

WHAT IT HOLDS:
- THE MINIMAL SEQUENCE (6 steps): `company up` → `company up session-supervisor` → `company up @xsession-brain` → `company up jobs` (optional) → phone surfaces (optional) → `claude` (lead launch)
- Boot truth: only `ollama` and `tailscaled` auto-start; everything else is disabled
- The fabric relaunch mechanism: `~/.bashrc:246` aliases `claude` to `channels/claude-fabric.sh`
- Persists vs Lost after reboot: git tree, .data/store, vaults, transcripts persist; processes, VRAM, agent sessions, armed timers are lost
- FLAGS for Tim: WINDOWS-BOOT.md stale doc (company.target is disabled), phone surface resolution, no one-command fleet relaunch, minor cleanups (embed-pplx WantedBy inconsistency, dangling openclaw-node symlink, transcript index status)
- SURPRISING: main branch is 1339 commits ahead of origin (large uncommitted set)
- OPEN GAP: litellm :4100 not started post-reboot means concurrent cloud models path is DOWN until manually started

### `ops/STARTUP.md` — startup and control reference

WHAT IT IS: the command table and boot behaviour doc.

WHAT IT HOLDS: command table, resource manager explanation (--evict/--force/--wait), jobs group timers (transcript circuit), underlying systemd commands, boot behaviour (nothing auto-starts), phone access (Tailscale + PWA, DONE), canonical unit files, rebuild from repo instructions.

GAP noted: `STARTUP.md` correctly says `company up` → refuses over-budget start; this is enforced in code (app.py exit(2)). The doc says it "surfaces the risk; it does not yet hard-refuse" — this is STALE (the code hard-refuses with exit(2)).

### `ops/WINDOWS-BOOT.md` — Windows-side Task Scheduler setup

WHAT IT IS: Windows Task Scheduler setup to launch WSL at boot (so the Company is reachable without login).
FLAGGED AS STALE in BOOT-RUNBOOK.md: claims linger auto-pulls the whole stack (company.target) — FALSE per live state (company.target is disabled + not wanted). Setup guide may be valid for future use but the auto-start claim is wrong.

---

## 4. OPS PYTHON SCRIPTS (non-CLI)

### `ops/agent_sessions_exporter.py` — transcript exporter

WHAT IT IS: F1.4 Session Fabric transcript-memory exporter. Systemd job (company-agent-sessions-exporter.timer, every 20 min).
WHAT IT DOES: reads `~/.claude/projects/*/<uuid>.jsonl`, applies the FILTER LAW (keep user+assistant text + trace lines; strip tool_result bodies, attachment lines, bookkeeping types, noise-prefix user texts, thinking blocks), applies secret-regex redaction, writes one markdown per session to `~/corpora/claude-sessions/<project>/<uuid>.md`. Idempotent (write-only-if-different). READ-ONLY on `~/.claude`.
FRESHNESS LAW: only exports sessions whose jsonl mtime is older than 15 min (quiesce window — live session not re-exported mid-session).
TITLE FALLBACK CHAIN: ai-title → custom-title → last-prompt → first real user turn → untitled+envelope.
CROSS-REF: company-agent-sessions-exporter.{service,timer}, ops/claude_sessions_reindex.py (the second beat)

### `ops/agent_sessions_importer.py` — session registry backfiller

WHAT IT IS: F1.2 Session Fabric backfill (one-shot, on-demand — not a timer).
WHAT IT DOES: scans `~/.claude/projects/*/*.jsonl` (skips `agent-*.jsonl` sidechains) → creates one whole-record file per main session in `<store>/agent_sessions/<uuid>.json` via FsStore.save_agent_session. READ-ONLY on `~/.claude`. Idempotent (skip-unchanged, --force to re-read). Never emits agent_sessions events (single-writer law). Proven by `tests/agent_sessions_registry_acceptance.py`.
RESULT: 1,065 records backfilled (measured 2026-06-11).

### `ops/claude_sessions_reindex.py` — transcript reindex beat

WHAT IT IS: the second beat of the transcript-search circuit (after the exporter). Systemd job (company-claude-sessions-reindex.timer, *:05/20).
WHAT IT DOES: CHEAP-BY-DESIGN — checks `.reindex_marker.json` (newest .md mtime + file count); exits 0 doing nothing if unchanged (the common case). If changed: triggers substrate DELTA reindex of the `claude-sessions` vault into `~/.cache/company/substrate-claude-sessions` using `embed-pplx` at :8007. FAIL LOUD if embed-pplx down (exits non-zero, marker stays stale for retry).
USES: obsidian-overlord/.venv (chromadb + httpx). ISOLATED state dir (not the bge-m3 substrate).
FLAG: `--ensure-embedder` option to auto-bring-up embed-pplx (default OFF).

### `ops/dragnet_determine.py` — dragnet CLI

WHAT IT IS: thin CLI over `runtime/recall_determine.py`.
WHAT IT DOES: `python ops/dragnet_determine.py --topic "..." [--asset full|visual-dna] [--max-claims 60]` → calls `rd.determine(topic, asset, max_claims)` → prints JSON results (truncated at 3000 chars).
CROSS-REF: `runtime/recall_determine.py` (the actual engine)

### `ops/dragnet_extract.py` — dragnet extract CLI

WHAT IT IS: thin CLI entry (by pattern, similar to dragnet_determine). References `runtime` layer.
NOTE: not fully read — extracts/projects via the dragnet extraction layer.

### `ops/embed_extractions.py` — embedding script

WHAT IT IS: a script to embed extraction outputs (likely from dragnet_extract) via the embed-pplx service.
NOTE: not fully read — part of the dragnet/extraction pipeline.

### `ops/fabric_clone_probe.py` — live clone proof

WHAT IT IS: lead-only live proof of the cc_clone mechanism. Spawns a real supervised claude clone.
WHAT IT DOES: clones a real multi-boundary source at compact:1, DMs the clone, asserts it answers from the past-point context, tears down. Supports PROVIDER/MODEL env vars for company/ollama backend.
ANTI-GREEN-PAINT: checks for model-resolution error text in reply (Claude Code returns non-empty error string on bad model).
CROSS-REF: `runtime/cc_clone.py`

### `ops/fabric_live_probe_r1.py` — Session Fabric R1 live proof

WHAT IT IS: R1 live proof (lead-only — spawns REAL claude sessions). 5 legs: R1.3 session_id pre-assignment + append_system_prompt; R1.1a slash command; R1.1b tool use; R1.1c /rewind (recorded verbatim, honest); R1.2 live stream capture + declaration coverage.
CAPTURES to `.build/fabric-probe/<stamp>-<sid>.ndjson`. Uses Watcher thread to tail /watch ndjson stream. PROOF SUMMARY block printed.

### `ops/fabric_live_probe_r34.py` — Session Fabric R3/R4 live proof

WHAT IT IS: continuation of live probes for R3/R4 spec lines.
NOTE: not fully read.

### `ops/fabric_live_probe_wake.py` — wake probe

WHAT IT IS: live probe for the wake/resume mechanism.
NOTE: not fully read.

### `ops/commit_queue.py` — concurrent-append/commit queue

WHAT IT IS: the fix for the no-branches/commit-to-main concurrent commit race (validated live 2026-06-20 — projection's commit swept DNA's concurrent board append).
WHAT IT DOES: members ENQUEUE (lock-free, O_APPEND); a SINGLE DRAINER holds fcntl.flock(LOCK_EX), applies items FIFO (append→add→commit OR paths→add→commit), advances a cursor after each success (crash-safe).
TWO ITEM KINDS: `append` (file + append_content + message — common case), `commit` (paths + message — already-written files).
LARGE CONTENT: spilled to CAS payload files (tmp+rename), queue line carries only the id (keeps line <4KB, POSIX O_APPEND safe).
FAIL LOUD: git conflict / nothing-to-commit / bad path → moves item to DEADLETTER + writes a (gap) Notice. Cursor advances (queue never wedges). Never a silent drop.
LAWS: commit-to-main only, no Co-Authored-By, fail-loud+no-silent-drop, reuse store's flock+atomic-append patterns.

### `ops/rerank.py` — cross-encoder rerank module

WHAT IT IS: a clean, REUSABLE cross-encoder rerank step. Built to OUTLIVE the throwaway transcript-search.
WHAT IT DOES: after bi-encoder search returns top-N candidates, re-scores each (query, candidate) pair with a model that reads both together.
BACKENDS (RERANKERS registry): `jina-v3` = jinaai/jina-reranker-v3 (0.6B Qwen3, SOTA multilingual, trust_remote_code, ~139ms/doc CPU); `ms-marco` = cross-encoder/ms-marco-MiniLM-L-6-v2 (88MB, ~56ms/doc, faster fallback).
DEVICE: CPU by default (Tim: keep GPU for embedder + voice). Runs in ~/vllm-env (torch+transformers).
SERVED AS: HTTP endpoint via `serve_rerank.py` + `serve_rerank.sh` → POST /rerank {query, candidates, top_n?} → {ranking:[{item,text,rerank_score,orig_rank,rank}]}, GET /health.
CROSS-REF: `ops/serve_rerank.py`, `ops/serve_rerank.sh`, `services.json:rerank-jina`

### `ops/render_declared_stream.py` — render declarations script

WHAT IT IS: a script for rendering/processing declared stream events. Related to the Session Fabric render_declarations.
NOTE: not fully read.

### `ops/seed_self.py` — session self-seeding

WHAT IT IS: a session runs this FROM INSIDE ITSELF to pre-seed its own self-id so it survives compaction (#69/#65).
THE GAP IT FIXES: pre-hook deploy sessions can't auto-self-recall after compaction. The /proc backfill-from-outside is unsafe.
MECHANISM: `--phrase` (nonce grep in transcripts, unambiguous self-id) or `--sid` (known); writes `~/.recollection/self/<claude-pid>.json`; optionally folds `{claude_pid, session_id}` into the session's own fabric registration.
BG-JOB CASE: if no claude ancestor in /proc walk, returns a structured "no_claude_pid_detached_bgjob" result with guidance (use COMPANY_SESSION_ID env or direct sid).

### `ops/transcript_search.py` — standalone transcript search (numpy fallback)

WHAT IT IS: THROWAWAY INTERIM. Standalone numpy semantic search over `~/corpora/claude-sessions/**/*.md`.
WHAT IT DOES: `index` command embeds all transcripts via embed-pplx (:8007), stores vectors.npy + meta.jsonl in `~/.cache/company/transcript-search/`. `search "query"` embeds query, cosine-sorts, returns top-K hits.
FAIL LOUD: if endpoint down or wrong dim, raises. COSINE via L2-normalize + dot.

### `ops/wire_substrate_claude_sessions.py` — substrate-backed transcript search

WHAT IT IS: THROWAWAY INTERIM. Substrate-backed sibling of transcript_search.py.
WHAT IT DOES: configures an ISOLATED substrate state dir (`~/.cache/company/substrate-claude-sessions`), points it at `embed-pplx` (openai provider, base_url :8007/v1), registers `claude-sessions` vault over `~/corpora/claude-sessions/`, indexes it. Gives transcripts the full substrate query surface (search_semantic, traverse_links, addresses, type-graph).
COSINE INTEGRITY: Chroma `hnsw:space=cosine` (scale-invariant for int8 unnormalized vectors).
COMMANDS: setup, index, status, search, all.
OPTIONAL: `--rerank`/`--reranker {jina-v3,ms-marco}`/`--fetch N` for 2-stage rerank; `--json <path>` for candidate dump.
CROSS-REF: `ops/rerank.py`, `ops/_finish_pplx_wire.sh`

### `ops/_finish_pplx_wire.sh` — gated tail script

WHAT IT IS: a gated completion script for the pplx wire. Runs after weights download: up embedder → index → verify-search → rerank BEFORE/AFTER on the real corpus.

### `ops/serve_model.sh` — the ONE registry-driven vLLM launcher

WHAT IT IS: the generic launcher all config-driven model services use.
WHAT IT DOES: reads `<service-key>` arg, exports CUDA_HOME + PATH (vllm-env nvidia/cu13 toolchain), reads per-service env from `serveconfig.py KEY --env`, activates `~/vllm-env`, builds vLLM args from `serveconfig.py KEY`, then `exec vllm serve ...`.
CROSS-REF: `cli/serveconfig.py` (generates the args + env), every vLLM user-unit (ExecStart points here)

### `ops/serve_pplx_embed.py` + `ops/serve_pplx_embed.sh`

- `.py`: FastAPI server for pplx-embed-context-v1-4b. Custom transformers (not vLLM — arch not in vLLM 0.21). Endpoints: POST /v1/embeddings (OpenAI-compat), GET /v1/models, GET /health. 2560-dim INT8 UNNORMALIZED. Optional `documents` field for native contextual late-chunking. bfloat16 (~8GB). Config via env: PPLX_EMBED_MODEL, PPLX_EMBED_PORT, PPLX_EMBED_DTYPE.
- `.sh`: shell wrapper to run serve_pplx_embed.py in ~/vllm-env.

### `ops/serve_rerank.py` + `ops/serve_rerank.sh`

- `.py`: FastAPI HTTP endpoint wrapping `rerank.py:Reranker`. POST /rerank → ranked candidates, GET /health.
- `.sh`: shell launcher. Runs in ~/vllm-env.

### `ops/hooks/cc_registry_freshness_check.sh`

WHAT IT IS: Claude Code SessionStart hook (wired via .claude/settings.json). The FIRST file in ops/hooks/. A NEW pattern (F-FIX-13).
WHAT IT DOES: compares `claude --version` against `store/claude-code.version_stamp`. If stale → warns (injected as additionalContext). Silent on current. NON-BLOCKING (always exits 0).
ALSO DOES (#69 self-marker): calls `write_self_marker.py` on the hook stdin JSON — failure-isolated (`|| true`). The whole self-marker block is wrapped so any error → silent continue.

### `ops/hooks/write_self_marker.py`

WHAT IT IS: the #69 self-marker writer. Called by `cc_registry_freshness_check.sh`. Failure-isolated (never raises).
WHAT IT DOES: reads hook stdin (has session_id, transcript_path, cwd, ...), resolves the claude ancestor PID via /proc, writes `~/.recollection/self/<claude-pid>.json = {session_id, transcript_path, cwd, ts, claude_pid}`. ALSO folds `{claude_pid, session_id}` into the matching fabric registration in `.data/channels/` (best-effort, atomic per-file rewrite).

---

## 5. SYSTEMD UNITS + TIMERS (`ops/systemd/`)

### Company-owned units

| Unit file | Description | ExecStart | Dependencies | Notes |
|---|---|---|---|---|
| `company.target` | The Company target | — | After=network.target | WantedBy=default.target (but DISABLED — boot off by design) |
| `company-bridge.service` | Bridge HTTP API :8770 | `.venv/bin/python runtime/bridge.py 8770` | After=network.target; PartOf=company.target | Restart=on-failure; WorkingDir /home/tim/company |
| `company-canvas.service` | Vite dev server :5173 | `canvas/app/node_modules/.bin/vite --host 127.0.0.1 --port 5173` | After=network.target; PartOf=company.target | Requires node on PATH (linuxbrew) |
| `company-session-supervisor.service` | Session supervisor :8771 | `.venv/bin/python runtime/session_supervisor.py 8771` | After=network.target; PartOf=company.target | |
| `company-embed-pplx.service` | pplx embed :8007 | `ops/serve_pplx_embed.sh` | After=default.target | WantedBy=default.target (INCONSISTENCY — siblings are company.target; noted in BOOT-RUNBOOK.md). TimeoutStartSec=600. |
| `company-tts-kokoro.service` | Kokoro TTS :4123 | `.voice-venv/bin/python voice/tts_service.py 4123` | After=network.target; PartOf=company.target | HF_HUB_DISABLE_XET=1 env |
| `company-agent-sessions-exporter.service` | Exporter oneshot | `.venv/bin/python ops/agent_sessions_exporter.py` | — | Type=oneshot; Nice=10 |
| `company-agent-sessions-exporter.timer` | Fires exporter every 20 min | `OnCalendar=*:00/20` | — | WantedBy=company.target; Persistent=true |
| `company-claude-sessions-reindex.service` | Reindex beat oneshot | `obsidian-overlord/.venv/bin/python ops/claude_sessions_reindex.py` | — | Type=oneshot; uses overlord venv |
| `company-claude-sessions-reindex.timer` | Fires reindex at *:05/20 | `OnCalendar=*:05/20` | — | WantedBy=company.target; Persistent=true |

### Third-party / external units (tracked in ops/systemd/)

| Unit file | Description | ExecStart | Notes |
|---|---|---|---|
| `vllm-chat.service` | vLLM chat-4b :8000 | `ops/serve_model.sh chat-4b` | After=default.target; TimeoutStartSec=300 |
| `vllm-2b.service` | vLLM chat-2b :8003 | `ops/serve_model.sh chat-2b` | (by pattern) |
| `vllm-08b.service` | vLLM chat-08b :8006 | `ops/serve_model.sh chat-08b` | (by pattern) |
| `vllm-embed.service` | vLLM BGE-M3 :8001 | `ops/serve_model.sh embed-bge` | (by pattern) |
| `vllm-jina-v4.service` | jina-v4 embedder :8002 | (custom serve script) | NOT config-driven |
| `vllm-jina-v5.service` | jina-v5 embedder :8004 | `ops/serve_model.sh embed-jina-v5` | (by pattern) |
| `vllm-nemotron.service` | Nemotron :8005 | `ops/serve_model.sh chat-nemotron` | |
| `vllm-qwen3emb.service` | Qwen3-Embedding :8004 | `ops/serve_model.sh embed-qwen3` | SHARES port with jina-v5 |
| `voicemode-whisper.service` | Whisper.cpp STT :2022 | `~/.voicemode/services/whisper/bin/start-whisper-server.sh` | External (voicemode package); v1.2.0; Last updated 2025-12-01 (STALE date in unit) |
| `llama-swap.service` | llama-swap model hot-swapper :9090 | `/usr/local/bin/llama-swap -config ~/llama-swap/config.yaml -listen 127.0.0.1:9090 -watch-config` | Testing phase; no port in services.json |
| `openclaw-gateway.service` | OpenClaw gateway :18789 | `node .../openclaw/dist/index.js gateway --port 18789` | EnvironmentFile=-%h/company/.secrets (the `%h` env file load — note tilde expansion); KillMode=control-group; Restart=always |
| `github-runner.service` | GitHub Actions runner | `/home/tim/actions-runner/run.sh` | KillSignal=SIGTERM; TimeoutStopSec=5min |

### Generated units (`ops/systemd/generated/` — auto-generated by the Company routine system)

| Unit file | Description | Cadence | Notes |
|---|---|---|---|
| `company-routine-self_status.service` | "Self status" routine oneshot | — | ExecStart: `python -m runtime.routine_runner self_status` |
| `company-routine-self_status.timer` | Arms self_status at 09:00 daily | `OnCalendar=*-*-* 09:00:00` | WantedBy=company.target; Persistent=true |
| `company-routine-completion_poke.service` | "Completion poke" routine oneshot | — | ExecStart: `python -m runtime.routine_runner completion_poke` |
| `company-routine-completion_poke.timer` | Arms completion_poke every 30 min | `OnUnitActiveSec=1800s; OnBootSec=1800s` | WantedBy=company.target; Persistent=true |

**GAPS/SURPRISES in systemd:**
- 5 voice trial engine units (chatterbox/orpheus/cosyvoice/xtts/qwen3tts) are in services.json but NOT in `ops/systemd/` — STARTUP.md explicitly says "5 voice trial engines (`company-voice-*`) have no unit yet — install, then add to `ops/systemd/`"
- `voicemode-whisper.service` is external (voicemode package path `~/.voicemode/`), not in the standard company pattern; last-updated comment date is 2025-12-01 (pre-2026)
- `company-embed-pplx.service` has `WantedBy=default.target` instead of `company.target` — an inconsistency flagged in BOOT-RUNBOOK.md

---

## 6. PLATFORMS

### `platforms/AGENTS.md` — platforms constitution

WHAT IT HOLDS: the Level-2 platform table as DATA discipline. DATA-ONLY row files (imports + dict, no def/class). The engine (introspection/) never knows platform identity. Id ↔ filename rule (hyphen ↔ underscore). Fail-loud validation via PlatformEntry.model_validate. Two instances described: claude_code (instance #1) and gh_cli (instance #2 — the generalization-proof).

### `platforms/claude_code.py` — Claude Code platform row (instance #1)

WHAT IT IS: PURE DATA — imports + `PLATFORM` dict + `SPAWN_FLAG_BODY_KEY_MAP` data dict. id="claude-code".

WHAT IT HOLDS:
- `executable_locator`: name="claude", env override COMPANY_CLAUDE_BIN, known_paths ~/.local/bin/claude
- `invocation_kind`: "subprocess"
- `discovery_sources`: two sources — cli-help (commander-options-text, floor_guard=30) and stream-init (extracts tools/slash_commands/mcp_servers/skills/plugins/agents from the init event; throws away session-level metadata)
- `version_source`: `claude --version` → strip " (Claude Code)" → semver
- `signal_sets`: transport_invariants (the post-R6 declared fallback set), hazard_name_vocabulary, capability_axes (tools-builtin, mcp, dirs, permission, plugins)
- `consumer_reserved_invariants`: body_key_overrides for every locked spawn flag (model, effort, fallback, permission_mode, settings, resume, fork, output_format, include_partial, debug, safe_mode, bare, input_format, print, verbose, strict_mcp_config, dangerously_skip_permissions) — each with a teaching-refusal why
- `invocation_binding`: full state machine (starting→idle→busy→closed), message envelopes, turn result shape, usage telemetry block
- `permission_model`: --permission-mode; default "plan"; profiles for default and bridge-session
- `tool_surface`: allow/deny flags, floor tool set [mcp__company], tool specifiers, capability_to_tool_grant
- `tool_server_wiring`: --mcp-config, json-inline, server_entry_shape
- `resource_governance`: COMPANY_FABRIC_CONCURRENCY (default 3), COMPANY_FABRIC_TURN_TIMEOUT_S (default 900), COMPANY_FABRIC_INIT_WAIT_S (default 15)
- `SPAWN_FLAG_BODY_KEY_MAP`: maps all snake_case body keys to their real Claude CLI flag names (the F-FIX-5 cross-check map)

### `platforms/_wiring.py` — head_builder bootstrap

WHAT IT IS: the `_`-prefixed wiring module (skipped by PlatformRegistry discovery). Registers the head_builder thunk for claude-code: `SessionSupervisor._build_spawn_cmd(claude_bin="claude", resume=None, fork=False)`. Registers at import. Idempotent.

### `platforms/gh_cli.py` — GitHub CLI platform row (instance #2, the generalization-proof)

WHAT IT IS: PURE DATA, no def/class. id="gh-cli". Proves the lift: a second CLI of a different tool family (Cobra vs Commander.js) — ZERO engine/adapter edits.
- `executable_locator`: name="gh", env COMPANY_GH_BIN
- `discovery_sources`: cli-help with `gh pr create --help` (floor_guard=10), format commander-options-text. WHY this subcommand: bare `gh --help` is a command-list (2 flags, below floor); per-subcommand help has 21 rows.
- `version_source`: `gh --version` → strip "gh version " prefix → semver-token
- `signal_sets`: transport_invariants ["--json","--jq","--template","--no-color"], hazard_vocabulary ["force","delete","yes","confirm"], capability_axes {repo-target, browser}

---

## 7. DOCS

### `docs/AGENTS.md` — docs constitution

WHAT IT IS: meta-documentation constitution. docs/ holds cross-cutting conventions about the repo as a knowledge space. Never code, never duplicates a live source.

### `docs/concepts-and-principles.md`

WHAT IT IS: the conceptual ground ("the why"). 9 principles as embodied in the repo:
1. Path of least resistance (make correct = easiest)
2. One source (define once, project everywhere)
3. Fail loud (no silent failures)
4. Schema-additive, never breaking
5. Governed self-modification (agent proposes, operator disposes)
6. Self-describing, self-maintaining
7. Relational navigation (knowledge graph is the self-model)
8. One entity across time (coherent voice + memory)
9. Prove by use (acceptance suites are the convergence record)

### `docs/vault-conventions.md`

WHAT IT IS: defines the repo-as-Obsidian-vault dual form. Every .md obeys frontmatter + link conventions. The documentation *is* the navigable self-model. Rules: type/module/aliases/tags/governs/relates-to frontmatter; wiki-links for relations; Obsidian graph shows module structure.

### `docs/claude-code-interconnection/` (4 files)

**ARCHITECTURE.md**: the injection mechanism (Claude Code Channels, the `claude/channel` experimental capability), the company channel server (`channels/company_channel.mjs`), the core router (`runtime/cc_channels.py`), the full data flow loop (send → inject → channel tag → reply → route_reply → push back), group chat, threading model.

**README.md**: (not fully read) — overview of the interconnection system.

**REFERENCE.md**: (not fully read) — reference for the channel protocol.

**ROADMAP.md**: (not fully read) — roadmap for cross-session channel development.

### `docs/methodology/README.md` + 6 recipe files

README: build-loop recipes copied from `~/.claude/skills/` into the repo for durability.

| File | What it recipes |
|---|---|
| `company-build.md` | the operable composition surface (canonical recipe) |
| `rhm-build.md` | RHM walkthrough & review organ |
| `wire-build.md` | decision→implementation wire + product surface |
| `remediation-build.md` | unification/completion/connection loop (fixes cross-layer defects; verifies seams not cells) |
| `loop-prep.md` | three-document prep before a loop (Completion Criteria · Implementation Guide · Research Synthesis) |
| `plan-review.md` | iterative multi-agent plan review before a loop |

GAP noted: "the live, runnable versions remain in `~/.claude/skills/`; these copies are the durable record — when a recipe changes, update both." This is a potential drift: these files may be stale relative to `~/.claude/skills/`.

---

## 8. SKILLS

### `skills/AGENTS.md` — skills constitution

WHAT IT IS: the file-discovered SKILL registry constitution. Skills = declared, reusable instructions (vs contexts = context blobs). Mirror of roles/node-types registry pattern.
Live skill set: summarize, extract_decisions, corpus_pipeline, patterned_visibility, inversion_query, map_reduce_composition.
Drift home: `tests/skills_contexts_acceptance.py` asserts each skill is reflected here.

### Skills as Python modules (one `SKILL = {...}` dict per file)

| File | Skill id | Label | What it is |
|---|---|---|---|
| `skills/summarize.py` | summarize | Summarize | Instructions: condense content faithfully, no loss of load-bearing detail, no added info, no preamble |
| `skills/extract_decisions.py` | extract_decisions | (not read) | Instructions to list every decision a document records. Written LIVE by the agent (DIRECT-CREATE, no approval), then git-committed [self-apply]. |
| `skills/corpus_pipeline.py` | corpus_pipeline | The 3-layer corpus pipeline | Recipe for capture→run_items(extract)→run_items(project)→[engine embed pass]→run_reduce(cluster then synthesize)→marks(by='target'). Each step's output→input wiring. |
| `skills/inversion_query.py` | inversion_query | (not read) | Recipe for find_relations(item, near_space, far_space) — the near∩¬far inversion query. |
| `skills/map_reduce_composition.py` | map_reduce_composition | (not read) | Recipe: when to run_items (MAP, 1 role × N units) vs run_reduce (cross-unit JOIN), and how to chain them. |
| `skills/patterned_visibility.py` | patterned_visibility | (not read) | Recipe for the patterned-visibility loop: run → look/compare → mark the pattern → that reveals the next step → repeat. |

---

## 9. CONTEXTS

### `contexts/AGENTS.md` — contexts constitution

WHAT IT IS: the file-discovered CONTEXT registry constitution. Contexts = reusable context blobs (distinct from skills = reusable instructions). Same registry pattern. `context://<id>` resolves via `runtime/cognition.py:resolve_address`.
Live context set: company_overview.
Drift home: `tests/skills_contexts_acceptance.py`.

### `contexts/company_overview.py`

- id: company_overview
- label: Company overview
- content: "The Company is an identity-coupled AI system that the Commander (Tim) directs through a crew of agents — a multiplier on the Commander's output, not a generic AI framework. It is built recursively: the system understands and grows its own codebase. Everything is addressed and registry-driven (registry-is-truth) — node-types, roles, modes, skills, and contexts are all file-discovered declarations, never literals in code. Cognition is layered: a main stream fed by a cast of rule-routed model roles, each resolving its input from an address."

---

## 10. NOTABLE GAPS / STALE / INCOMPLETE / SURPRISES

### Stale / Incorrect Docs
- `ops/WINDOWS-BOOT.md`: claims linger auto-starts company.target on boot — FALSE per live state. company.target is disabled.
- `ops/STARTUP.md`: says `company up` "surfaces the risk but does not yet hard-refuse" an over-budget start — STALE. Code hard-refuses with exit(2).
- `voicemode-whisper.service`: internal comment says "Last updated: 2025-12-01" — pre-2026 date, may indicate the unit is from an external package and not company-maintained.

### Incomplete / Missing
- 5 voice trial engine systemd units (chatterbox/orpheus/cosyvoice/xtts/qwen3tts) mentioned in services.json but NOT in `ops/systemd/` — they must exist in `~/.config/systemd/user/` but are not canonical-in-repo.
- `tts-kokoro` model-id UNCONFIRMED — config._note says "model-id NOT located on disk (kokoro runs but its weights id is unconfirmed)."
- `litellm` service is MANUAL (no systemd unit). The old `litellm-proxy.service` was removed (served on :4000 — stale). Current litellm (:4100) has no unit.
- `rerank-jina` is MANUAL (no unit). The serve_rerank.sh is the run command.
- `embed-jina-v4`: `serve_jina_v4.sh` references `~/vllm-tests/serve_jina_v4.py` — a file OUTSIDE the repo (~/vllm-tests/). Not self-contained.
- docs/claude-code-interconnection/ README, REFERENCE, ROADMAP not fully read.
- skills/inversion_query.py, map_reduce_composition.py, patterned_visibility.py not fully read (SKILL dict not extracted).

### Surprises / Cross-Refs
- Port 8004 shared by `embed-jina-v5` AND `embed-qwen3` — both registered, only one can run. `company status` would show both but only one is actually up. The per-unit is-active prevents false-running reads.
- `company-embed-pplx.service` `WantedBy=default.target` instead of `company.target` — boot inconsistency.
- `ops/cli/telemetry.jsonl` lives inside `ops/cli/` (not in the store or a data dir) — it's a sibling of the Python code. It's gittracked (implicitly, since the ops/cli/ dir is tracked).
- `llama-swap.service` binds to `127.0.0.1:9090` but services.json has no port for it. Listed as "test."
- The `company` CLI does NOT currently have a `company routine` command (routines are run by the generated systemd units, not a CLI verb). This is a gap relative to the session/board type-views.
- main branch is 1339 commits ahead of origin (noted in BOOT-RUNBOOK.md) — significant uncommitted work that runs from the working tree.
- `ops/commit_queue.py` solves the concurrent-commit race but it's unclear which callers USE it vs still doing direct `git commit` (the fix was just documented as validated live on 2026-06-20).
- The `company coherence` command is mentioned in app.py but NOT listed in the ops/cli/README.md command table — a documentation gap.
- `ops/fabric_live_probe_r34.py` and `ops/fabric_live_probe_wake.py` exist but were not fully read.
- `ops/dragnet_extract.py` and `ops/embed_extractions.py` were not fully read.
- `ops/render_declared_stream.py` was not fully read.

---

## 11. HOW THE SYSTEM IS OPERATED + RUN (summary map)

### Startup sequence (from BOOT-RUNBOOK.md)
1. `company up` → canvas :5173 + bridge :8770
2. `company up session-supervisor` → :8771 (if fleet needed)
3. `company up @xsession-brain` → embed-pplx :8007 + rerank-jina :8008 + chat-4b :8000 + stt-whisper (the standard loadout)
4. `company up jobs` → arms transcript exporter + reindex timers
5. Start phone surfaces manually (not company units): counterpart gallery :8090, operator surface :5174
6. `claude` (the lead) — auto-attaches fabric channel via ~/.bashrc alias

### GPU management
- `company gpu` — the measured state
- `company up <svc> --wait` — loads + records real VRAM to telemetry
- `company up <svc> --evict` — makes room first (models→brain→voice, largest)
- `company telemetry` — learned measurements vs estimates
- `company config <svc> gpu_util <v>` + `company restart <svc>` — resize a model's VRAM slice

### Model management
- `company models` — what's on disk
- `company swap <svc> <model_id>` — point to a different model
- `company ensure <model_or_service>` — gated load-on-demand (engine + CLI share this)
- `company combos` / `company up @<combo>` — run named service sets

### Fleet management  
- `company session new [opts]` → spawn via supervisor (THE ONE spawn path)
- `company session send <id> <msg>` → inject turn
- `company session stop <id>` → teardown
- `company board file/list/transition` → noticeboard items
- `company clone list/get` → clone fleet read

### Logs + diagnostics
- `company logs <svc> [-f]` — journal tail
- `company health` — port ping matrix
- `company suites` — the all-green gate (every acceptance suite)
- `company coherence` — structural gap detection
