---
type: constitution
module: ops
aliases: ["ops — constitution"]
tags: [company, constitution, ops, command-center]
governs: []
relates-to: ["[[Company Map]]", "[[runtime — constitution]]"]
status: living
---

# ops/ — AGENTS.md (constitution)

**What it is.** The Company's **operational control** — how the *running system* is seen and operated. Because there are no human developers and no human reads or writes these files, the operating layer must be **one self-describing place an AI can read cold and run**, not config scattered across `~/.config`, ad-hoc `start.sh` scripts, and tribal memory. This folder is that place.

**What it guarantees.**
- **One console to see + operate the runtime.** `ops/company` (symlinked onto `PATH` as `company`) shows every service grouped, its live state (▶ running · ◐ active-no-port-yet · ✖ failed · · stopped), and **drift** (e.g. "RUNNING (unmanaged)" when something is up by hand instead of under its unit). It starts/stops/restarts any service, group, or `all`. See `STARTUP.md` for the command table.
- **One self-describing registry of truth.** `ops/services.json` declares every service (group · title · port · how-managed · health · autostart). The AI reads this to know the whole machine. **Adding a service = adding one entry here.**
- **systemd is the muscle; this is the map + the console.** Reliable execution, `Restart=on-failure`, and start-at-boot (user **linger** is on) live in systemd units (`ops/systemd/` holds the canonical copies). The console *drives* systemd; it never replaces it. The substrate must always be able to bring the console's own services up — including the bridge/canvas the console reports on.
- **Honest over complete.** It declares everything reasonably knowable, accepting some entries (dormant model ports/units) may be imperfect — *visible-and-operable-but-slightly-wrong beats invisible scatter.* A wrong detail is a one-line fix in the registry, never a hunt.
- **Fail loud / no hiding.** Status shows reality (incl. drift and failures), never a flattering fiction. Control actions report ✓/✗ with the error.

**This is the FIRST *instantiation* of one general console — more TYPES, not more tools (open-future).**
Do **not** build duplicate command centers. The right shape (Tim, "one substrate, per-type view-modes" — D3) is **one** console/registry mechanism **instantiated per type**: services are one type-view; **models/VRAM** (which model is live, swap what's in VRAM — the operable face of "it's all resource management"), **cognitive-layers**, **the RHM/modes**, **data/memory**, **jobs/cron** are *other view-modes of the same mechanism*, not separate apps. The service console is the first type this general thing renders; over time the type-views surface together on the canvas (the commander's bridge). Treat this folder as the seed of one generalising console, never as one of many parallel tools.

**Where new things go / how to extend.**
- **Add a service to the command center** → edit `ops/services.json`: add an entry `{ "key": { group, title, port?, manage: {type: "user-unit"|"system-unit"|"manual", unit?}, health?, autostart? } }`. If it needs a *new* systemd unit, add the unit to `ops/systemd/`, then install it (`cp ops/systemd/<x> ~/.config/systemd/user/ && systemctl --user daemon-reload && systemctl --user enable <x>`); to pull it into the core boot set, `WantedBy=company.target` (new units) or `systemctl --user add-wants company.target <unit>` (existing). Then `company status` to confirm it appears. System services (sudo to control) are status-only from the console.
- **Add a new TYPE-view to the console** (NOT a new tool) → generalize the registry + console over the new type (its entries declare their own kind), reusing the same see/operate mechanism over the real substrate. Document it here; (eventually) it becomes another view-mode on the canvas. Same mechanism, more types — never a parallel command center.

**Its seam.** The console reads `services.json` and shells out to `systemctl`/`journalctl`/socket-checks — it owns no state of its own; the registry + systemd are the truth. Anything wanting to know "what runs here" reads `services.json`; anything wanting to operate it calls `company` (or systemd directly).

**What would violate it.** A service started in a way the registry doesn't know about (invisible scatter — the exact anti-pattern this replaces). A console that hides failures or drift. Hand-maintained duplicate truth (two places that both claim what runs). A "command center" that only an informed human could operate — it must be plain enough for a fresh AI session.

## Status of the type-views (open-future, growing)
- **services** — the first type-view (live since 2026-06-04).
- **models/VRAM (the resource manager)** — instantiated 2026-06-06 as the SAME console's
  GPU view: `company gpu`/`models`/`swap`, VRAM cost in `status`, and a hard budget gate on
  `company up` (refuses an over-capacity start, always shows what's holding the card; `--force`
  overrides). Lives in `cli/gpu.py`, not a separate tool. Next growth = telemetry → scheduling
  (see `cli/UPDATING.md`). [[project-native-model-layer]]
  - **Config-block sizing is the ONE source (2026-06-07).** A GPU service's `config.gpu_util` ×
    `vram_ceiling_mb` IS its budget (`gpu.budget_vram`) AND what it launches with. Voice engines that
    aren't `serve_model.sh`-launched (e.g. `tts-orpheus` — own unit + `orpheus.py`) now carry a `config`
    block too; `orpheus.py` reads `config.gpu_util/max_model_len/model` (env is fallback) so the fit-gate
    and the launch never drift. **Size by measurement, never arbitrarily** (Tim): a model carries a
    measured `config._profile` `{fixed_mb, kv_kb_per_token}`, so `/api/model/config` auto-sizes `gpu_util`
    from a new `max_model_len` (and `max_model_len_ceiling` records the model's real capacity, reachable solo).
  - **The fit-surface (`gpu.fit_report` → `/api/fit`).** "Tell me if my selection won't fit" (Tim):
    given selected GPU service keys (brain + voice), returns each budget, the sum vs the card ceiling,
    measured free, and fit/no-fit + what to unload — config-derived, so it tracks a resize. The settings
    window renders it as a bar. Measured on the 16GB card: the 4b (hybrid, KV ~31.7KB/tok) does 256K
    **solo** and co-resides with light voices at 64K, but **Orpheus (~8.5GB) + 64K brain is over by
    ~0.6GB** — a switch-on-demand pair (the gate refuses, never OOMs).
- **model-TYPE capabilities (the capability CATALOG — `cli/capabilities.py` + `services.json`-sibling data file `model_capabilities.json`, G8/C8.1–C8.4 + C2.5, 2026-06-08/09).**
  The THIRD keying (B4): intrinsic capability **by model-id** (tool-calling · json_schema · thinking ·
  context-ceiling · concurrency-knee · speed), each with explicit provenance `declared|probed|measured|served`
  (live/served wins). **The catalog is FILE-DISCOVERED DECLARED DATA (C2.5):** the rows live in
  `ops/model_capabilities.json` — the single source ops + cognition both read (registry-is-truth, rule 8) —
  NOT a hardcoded python dict; `capabilities.py:_load_catalog` reads it into `MODEL_CAPABILITIES` at import
  (FAIL LOUD on missing/malformed/empty — never a silently-empty catalog), so **adding a model's capabilities
  = adding ONE entry to that file (no code edit)**, mirroring how `services.json` declares what RUNS. It now
  spans the **FULL declared model set** keyed by model-id (the resident 4B · the local chat workers
  2B/0.8B/nemotron · the served embedders bge/jina-v5/qwen3-8b · the **on-disk-not-yet-served retrieval
  fleet** added 2026-06-12: code embedders nomic-embed-code/LateOn-Code · the MULTIMODAL embedders
  Qwen3-VL-Embedding-2B + jina-v4 (provide `embed`+`vision`) · the RERANKERS ms-marco/jina-reranker-v3 +
  the matched Qwen3-VL-Reranker-2B (provide `rerank`[+`vision`]) · pplx-embed-0.6b/context-4b · granite-97m ·
  all-MiniLM · the model-id voice engines orpheus/qwen3tts · the cloud reasoner) — every `provides`
  GROUNDED in a hard signal (`--runner pooling`→embed · `--tool-call-parser`→tools · `chat_template_nothink`→
  no-think · for the not-yet-served fleet: the model card + `build-prep/brain/embedding-research-2026-06.md`,
  source `declared`), never fabricated. The `rerank` tag was added 2026-06-12 (cross-encoder/late-interaction
  scorers); `vision` flipped from negative-only to real-provider the same day. **2026-06-12 the catalog was
  completed to the FULL on-disk + reachable fleet** (Tim: "all of those other ones actually need to be added"):
  the voice TTS engines (chatterbox·cosyvoice·xtts·orpheus-variants·qwen3tts-CustomVoice → `tts`), the STT
  ears (whisper·parakeet·canary·granite → `stt`), the OLLAMA local chat workers + embedder and the OLLAMA
  CLOUD reasoners (grounded in `ollama show` capabilities), and support models (snac codec → provides `[]`;
  yolo_x_layout → `vision`). The previously-keyless voice/STT `services.json` rows were given `config.model`
  (the verified on-disk HF id) so the gpu.py JOIN/residency view resolves them — identity metadata, safe for
  their non-vLLM custom launchers. `embed-jina-v4`/`embed-pplx` got identity but their serve flags + launch
  remain UNVERIFIED (marked in the row `_note`); `tts-kokoro`'s on-disk id is still unconfirmed (flagged).
  It owns ONLY model-intrinsic facts — it NEVER stores gpu_util/vram (rule 3); for those
  it **JOINs to `gpu.py`** (`service_key_for(model_id)` matches `config.model`, then `budget_vram`/residency —
  REUSED, never duplicated). Queries: `capabilities_for(model_id)` (the row + the JOIN), `role_can_bind(requires,
  model_id)` / `suitable_models(requires)` (the `requires ⊆ provides` binding query — projecting REAL
  capabilities across ALL models: an embed role → the embedders, a vision role → `[]` fail-loud-by-empty, a tts
  role → the voice engines; the `provides` TAG vocab matches `suite.py`'s `capability_providers()`
  chat·json·tools·fast·no-think + the catalog's other TYPES embed·tts·vision), `placement_for(track)` +
  `swarm_survives_cloud_brain()` (C8.3 cloud-decoupling policy as DATA), `is_resident`/`require_resident` (C8.4
  fail-loud, loud `OFFER_LOAD` on a miss, NEVER auto-loads), and **`ensure_resident(model_or_service, *, evict=False)`**
  (#50, 2026-06-08) — the **gated launch/select/evict ACTUATOR**: the deliberate sibling of the fail-loud
  `require_resident`. No-op if resident; loads if it fits; `evict=True` makes room via the EXISTING largest-first
  `gpu.plan_eviction` then loads; **needs-eviction WITHOUT pre-authorization (`evict=False`) RETURNS the G14
  swap-approval ASK** (Tim's design, 2026-06-09: `{swap_needed, would_load, would_evict, free_gb, needed_gb,
  approve:"re-call with ensure_evict=true"}` — never a hard-block, never a silent evict; the agent/operator
  approves at call time); **RAISES `EnsureResidentError`** only on the genuinely impossible — no local service,
  can't fit even after the FULL eviction plan, or a failed start (no silent half-load). It REUSES the ONE resource-manager primitives (`check_fit`/`plan_eviction`/`teardown`/
  `systemd.control(...,"start")`/`budget_vram`) — it does NOT call `app.py:_act` (the CLI front that `sys.exit`s)
  and is NOT a second start path. Reachable as **`company ensure MODEL|SERVICE [--evict] [--no-wait]`** and called
  by the cognition engine (the embed-op's opt-in `run_role(..., ensure=True)`). `ensure_loadout_for_mode(mode, ...)`
  is the B/mode-loadout consumer (reads `mode_registry(mode)["brain_config"]`, ensures the brain service resident,
  surfaces the gpu_util-variant gap loudly — never a hardcoded loadout→service map). GATED/operator-AUTO class:
  reversible/internal, does NOT bypass the operator-only floor. **Self-description / DRIFT HOME (C9.4):** this section
  + the `cli/capabilities.py` module docstring + `model_capabilities.json`'s `_doc` are the registry's
  self-description home; the drift assertions are `tests/model_capabilities_acceptance.py` (the resident row +
  JOIN + residency — the no-regression base) AND `tests/model_catalog_acceptance.py` (C2.5 — the width, the
  capability-discrimination query, the data-driven add-a-row bar, the fail-loud loader). It COMPLEMENTS `suite.py`'s `MODEL_KNOBS` (per-request knobs, also by
  model-id) — knobs = "dials a request turns"; capabilities = "what the model can do." The DOWNSTREAM consumer is
  `suite.py:capability_providers()` (C2.5), which the lead wires to read this catalog (the one suite-side wire).
- **jobs/cron (timers)** — SEEDED 2026-06-11 with the `jobs` group: a timer-managed service is just a registry entry whose `manage.unit` is the `.timer` (the oneshot `.service` is what fires; `company up <key>` arms the timer; ◐ active = armed). First instance: `agent-sessions-exporter` (`ops/agent_sessions_exporter.py` — Claude session jsonl → `~/corpora/claude-sessions/` markdown under the Session Fabric filter law + secret redaction, READ-ONLY on `~/.claude`, every 20 min, quiesce >15 min; proven by `tests/agent_sessions_exporter_acceptance.py` + a clean full-corpus leak audit). Same mechanism, one more type — never a parallel scheduler.
- **sessions (the supervised Claude Code fleet)** — SEEDED 2026-06-12 (Session Fabric F1): `company session` is the type-view (`cli/sessions.py`), the `session-supervisor` service row is the muscle (`runtime/session_supervisor.py`, 127.0.0.1:8771, unit in `systemd/`). The console talks HTTP to the service; it NEVER spawns claude itself — one spawn path for every face.
- **cognitive-layers · RHM/modes · data/memory** — not yet instantiated; same mechanism when they are.

## Files
- `company` — launcher (stdlib-only; runs the `cli/` package; `company help`).
- `cli/` — the console package, one job per module:
  - `app.py` (dispatch + the `up` resource gate) · `registry.py` (reads services.json) ·
    `systemd.py` (start/stop/status/logs) · `gpu.py` (**the resource manager**) ·
    `models.py` (inventory + swap) · `capabilities.py` (**the model-TYPE capability registry**, by model-id; JOINs to gpu.py) · `bench.py` · `render.py` (status/health views) ·
    `sessions.py` (**the supervised-fleet type-view** — `company session [list|new|send|stop]`, a thin stdlib HTTP face on the session-supervisor service at 127.0.0.1:8771; the SERVICE is the one launcher of claude subprocesses — the console never spawns one itself).
  - `README.md` — use guide.   `UPDATING.md` — how to extend the CLI + the registry schema.
- `services.json` — the registry (the source of truth; now also carries `vram_mb`, `serve`, `vram_ceiling_mb`).
- `agent_sessions_exporter.py` — the transcript-memory exporter (jobs group; jsonl → markdown corpus under the filter law; its units are `company-agent-sessions-exporter.{service,timer}` in `systemd/`).
- `agent_sessions_importer.py` — the registry-catalog backfill (Session Fabric F1.2): one run scans `~/.claude/projects/*/*.jsonl` READ-ONLY (never writes/touches the catalog, never emits events — single-writer law) → one whole-record file per main session in `<store>/agent_sessions/` via `FsStore.save_agent_session`, with the exact title fallback chain + summarizer marking + coverage stats. Idempotent (skip-unchanged; `--force` to re-read; a non-closed record — the live supervisor's — is never stomped). On-demand, not a timer: re-run after catalog growth, or let the supervisor register sessions live. Proven by `tests/agent_sessions_registry_acceptance.py` + the real 1,065-record backfill.
- `model_capabilities.json` — the model-TYPE capability CATALOG (declared data, keyed by model-id; the file-discovered source `cli/capabilities.py` loads; add-a-model-capability = add-an-entry). Intrinsic facts only — NO vram (gpu.py JOINs that).
- `serve_pplx_embed.py` + `serve_pplx_embed.sh` — the **pplx-embed-context-v1-4b** custom embedder server (service key `embed-pplx`, MODELS group, port 8007, unit `company-embed-pplx.service`). NOT config-driven: this model's arch `PPLXQwen3Model` / `model_type bidirectional_pplx_qwen3` is remote-code (`trust_remote_code`, `auto_map`→`modeling.PPLXQwen3ContextualModel`); vLLM 0.21 has no such arch (verified absent from its 356 supported archs — `vllm serve` fails at `load_model`), so it runs via raw `transformers` behind FastAPI, exactly like the jina-v4 precedent (`serve_jina_v4.py`). Reuses `~/vllm-env` (torch 2.11+cu130, transformers 5.9.0). OpenAI-compat `POST /v1/embeddings`; dim **2560**; output is **INT8 + UNNORMALIZED → compare via COSINE** (model card). Contextual late-chunking model: flat `input` strings embed as single-chunk docs; optional `documents` (list[list[str]]) gives native per-chunk contextual embeddings. dtype bfloat16 (~8GB). INTERIM (throwaway — a real memory system is being built elsewhere).
- `transcript_search.py` — INTERIM semantic search over the Claude-session transcript corpus (`~/corpora/claude-sessions/**/*.md`, written by `agent_sessions_exporter.py`). Embeds via the `embed-pplx` endpoint (registry-is-truth), stores L2-normalized vectors + JSONL meta under `~/.cache/company/transcript-search/`, searches by cosine. `python transcript_search.py index` then `... search "query" [-k N]`. Fails loud if the embedder is down (no fake results). Throwaway interim — the standalone numpy fallback path.
- `wire_substrate_claude_sessions.py` (+ `_finish_pplx_wire.sh`) — INTERIM transcript-search wired into the **obsidian-overlord SUBSTRATE** instead of standalone numpy (the substrate-backed sibling of `transcript_search.py`). Configures an ISOLATED substrate state dir (`~/.cache/company/substrate-claude-sessions`, never touches the existing ollama/bge substrate — pplx is its own 2560-d int8 search space by design), points it at `embed-pplx` (provider `openai`, base_url `:8007/v1`), registers the `claude-sessions` vault over `~/corpora/claude-sessions`, and indexes it — giving the transcripts the full substrate query surface (`search_semantic`, `traverse_links`, addresses, type-graph) via the same MCP. Cosine integrity: Chroma `hnsw:space=cosine` (scale-invariant) so int8/unnormalized vectors need no pre-normalization. `setup`/`index`/`status`/`search`/`all`; fail-loud. `search` takes an OPTIONAL rerank toggle (`--rerank`/`--reranker {jina-v3,ms-marco}`/`--fetch N`) and a `--json <path>` candidate-dump for the lean 2-stage rerank (see `rerank.py`). `_finish_pplx_wire.sh` is the gated tail (wait weights → up embedder → index → verify-search → rerank BEFORE/AFTER on the real corpus) that runs once the download lands. Throwaway interim.
- `rerank.py` — the Company's **reusable cross-encoder RERANK step** (built to OUTLIVE this throwaway; the real memory system will reuse it). After a bi-encoder semantic search returns top-N candidates, the reranker re-scores each (query, candidate) pair with a model that reads both together and re-orders by deeper relevance (the standard EMBED+ANN → RERANK two-stage). Model-agnostic `Reranker(backend, device="cpu").rerank(query, candidates, top_n)` → re-ordered items annotated with `rerank_score` + `orig_rank` (so a caller can show BEFORE vs AFTER). Registry-is-truth backends (`RERANKERS`): **jina-v3** = `jinaai/jina-reranker-v3` (0.6B Qwen3 listwise, SOTA multilingual, trust_remote_code; verified ~139 ms/doc amortized on CPU); **ms-marco** = `cross-encoder/ms-marco-MiniLM-L-6-v2` (88 MB cross-encoder FALLBACK, ~56 ms/doc warm — use when jina-v3 is too slow). Runs on **CPU by default** (`device="cpu"`, CUDA hidden) — Tim's call: keep the GPU for the embedder + voice; runs in `~/vllm-env` (torch+transformers). SEAM choice: a standalone Company capability, NOT bolted onto the substrate (the overlord venv has no torch; keeping it separate keeps both venvs lean and makes it reusable). CLI: `selftest` (verify-by-run on a controlled probe), `rerank "q" doc...`, `rerank-file <pool.json>` (stage 2 of the 2-stage seam — consumes the `--json` dump from the substrate search; bridges chromadb-venv↔torch-venv without polluting either). Fail-loud: a requested backend that won't load raises; no silent skip. Throwaway interim (but the step is reuse-grade).
- `STARTUP.md` — the command table + boot behaviour + open items.
- `systemd/` — canonical unit + target files (the muscle).
