# AREA-25 — The Company Sprawl Map (terrain ground-truth)

> **Lens:** descriptive, nothing canonical. Every claim is marked **Observed** (seen directly in a file/command output, with `path` or `file:line`) or **Inferred** (pattern-matched, not verified). Read the Company's own self-map (`MAP.md`, `AGENTS.md`, `orienteering/INDEX.md` + all 38 `orienteering/entries/*.md`, `STATE.md`, `HANDOFF.md`, `CLAUDE.md`) IN FULL, plus live `systemctl`/port probes.
>
> **Purpose:** this is the structural ground the conversational-glyphgraph build fuses into — where every system physically lives, what's live vs dormant, what's relevant to the glyphgraph (models · voice · bridge · recall/corpus · modes · canvas/surface), and the shape of the sprawl (duplicated / scattered / moving).
>
> **Date of live readings:** 2026-06-30. The orienteering ledger entries were last re-read 2026-06-26 (their own `coverage.last_read`), so where I could re-verify live I note the delta.

---

## 0. The one-sentence shape

The Company is **`~/company` (the spine, 5.6G) + a corona of ~20 systemd-wired engines/data/config + a tail of scattered work/data that lives OUTSIDE `~/company`** (venvs on `~`, the recall index in `~/.cache`, certs in `~/.config`, connected repos in `~/repos`, and dormant prototype runs across `~`). The Company's own self-map calls this the **orienteering ledger** (`orienteering/INDEX.md`) and counts: **company:1 · external:23 · connected:4 · candidate:3 · resource:7** (Observed, `orienteering/INDEX.md:77-81`).

The glyphgraph build cares about a specific slice of this: the **bridge** (`:8770`), the **model fabric** (ollama `:11434` + the vLLM family), the **voice circuit** (STT ears + TTS engines + the Suite brain), the **recall/corpus substrate** (the pplx embedder `:8007` + the chroma index + `recollection`), the **modes registry**, and the **canvas/surface** apps. Sections 3–4 isolate that slice.

---

## 1. The spine — `~/company` itself

**Observed** (`orienteering/entries/company.md`, `MAP.md`):
- Path `/home/tim/company`, **5.6G**, git remote `git@github.com:Concept-Vi/the-company.git` (remote `Concept-Vi/the-company`).
- It is "a typed compositional dataflow system (code + AI nodes wired by structured-output contracts) plus its decisions/flows/runtime/RHM layers and an MCP face" (`company.md:28`).
- The one-picture architecture (`MAP.md:19-35`): **`canvas/`** (React+tldraw surface) → **`runtime/`** (scheduler + memo + compile + the **Suite** = the brain) → **`fabric/`** (the models, OpenAI-compatible) ; **`store/`** (addressed store + events + chat + surfaced + panels) ; **`mcp_face/`** (the agent face, generic verbs) ; **`nodes/`** (node library) ; **`voice/`** (STT + TTS) ; **`panels/`** (declarative UI) ; **`contracts/`** (the spine C1–C8) ; **`platforms/`/`introspection/`** (the Mirror-Registry capability system).
- The repo is **simultaneously code and an Obsidian vault** (`CLAUDE.md`) — every folder has an `AGENTS.md` constitution; `MAP.md` is the vault home; frontmatter + typed `[[wikilinks]]` carry the knowledge face without depending on the Obsidian app.

**Observed — the top-level registry folders** (`ls /home/tim/company`, this run): a very large set of typed-registry dirs, each a "declare a row → resolve into the thing" registry. The ones most relevant to a glyphgraph: `modes/`, `mode_detection_rules/`, `roles/`, `minds/`, `nodes/`, `flows/`, `decisions/`, `forms/`, `projections/`, `axes/`, `dials/`, `mark_types/`, `board_edges/`, `relation_types/`, `item_types/`, `schemas/`, `contracts/`, `surface/`, `canvas/`, `voice/`, `fabric/`, `runtime/`, `recollection/`, `mcp_face/`. (The presence of `board_edges/`, `mark_types/`, `relation_types/`, `projections/` is notable — there is already a graph/board vocabulary as typed registries.)

**Live registry snapshot** (`MAP.md:76-82`, auto-maintained by `Suite.refresh_self_description`):
- **node-types (16):** ask, codebase, constant, embed, gate, join, llm, model_of_tim, pair, portal, retrieve, rhm_mode, similarity, titlecase, uppercase, wordcount
- **RHM verbs:** run, propose, build, consult, show, panel, extend, configure, load_voice, unload_voice, request_change
- **modes:** listening, text-only, background, focus, walkthrough, watch-and-react, decide-for-me, off
- **panels:** settings
- **models (from the fabric registry):** kimi-k2.7-code:cloud, qwen3-embedding:0.6b, bge-m3:latest, qwen3.5-9b-q8:latest, qwen3.6-35b-a3b-iq3s:latest, minimax-m3:cloud, gemma4-26b-a4b-q3km:latest, qwen3.6-27b-q3km:latest, nomic-embed-text:latest, gemma4:31b-cloud, nemotron-3-super:cloud, deepseek-v4-flash:cloud, deepseek-v4-pro:cloud, kimi-k2.6:cloud, glm-5.1:cloud, glm-5:cloud, qwen3.5:397b-cloud, kimi-k2.5:cloud

---

## 2. The full terrain — every system in the Company's orbit

Grouped by the ledger's `relation` field. **state** column is my best read combining the entry's evidence with the live `systemctl`/port probe below; the ledger's own `status` is `unconfirmed` by convention (only Tim confirms lifecycle).

### 2a. EXTERNAL — IS the Company but lives outside `~/company` (wired by systemd) — 23 entries

| Thing | kind | path | size | what it is | live? (evidence) |
|---|---|---|---|---|---|
| **company-systemd** | config | `/home/tim/.config/systemd/user` | small | The control layer — ~20 `company-*` units + `company.target`; source copies mirrored at `~/company/ops/systemd/` | **PARTIALLY live.** Live now: bridge + embed-pplx + tts-kokoro + stt-moonshine. `company.target` disabled; **0 active timers** (`company-systemd.md:48`, re-confirmed this run) |
| **config-company** | config | `/home/tim/.config/company` | 20K | TLS cert+key for Tailscale serving host `workstation001.tail777bc2.ts.net` (valid Jun 4 → **Sep 2 2026**) | secrets:true; static credential material (`config-company.md`) |
| **company-cli** | engine | `/home/tim/.local/bin/company` → `~/company/ops/company` | symlink 29B | The `company` control CLI (PATH alias into the repo); `up/down/status/gpu/swap/telemetry/config` | invoked on demand, not a daemon (`company-cli.md`) |
| **vllm-env** | engine | `/home/tim/vllm-env` | 8.4G | The shared vLLM inference venv — serves nearly every local chat/embed model via `serve_model.sh` (sources this venv). Models: Qwen3.5-4B-AWQ, 2B, 0.8B, BGE-M3, jina-v5, Nemotron-30B, Qwen3-Embedding-8B. Ports 8000/8001/8003/8004/8005/8006 | two-hop wire (unit → `serve_model.sh` → venv). `:8000` OPEN this run; `:8001` closed (`vllm-env.md`) |
| **jina-v4-env** | engine | `/home/tim/jina-v4-env` | 5.0G | Dedicated venv for jina-embeddings-v4 (pins `transformers<5.0`); served on **:8002** via `~/vllm-tests/serve_jina_v4.sh` | two-hop via vllm-tests (`jina-v4-env.md`) |
| **vllm-tests** | engine | `/home/tim/vllm-tests` | 1.3M | **NOT scratch** — load-bearing: holds `serve_jina_v4.sh`/`.py` (:8002 embeddings) + `serve_2b.sh` (llama-swap's small-model launcher) + `chat_template_nothink.jinja` + Company UI screenshots | live infra; two production services reach in (`vllm-tests.md`) |
| **llama-swap** | engine | `/home/tim/llama-swap` (binary `/usr/local/bin/llama-swap`) | 8K | Model-router config — swaps Qwen3.5-2B/0.8B in/out behind one OpenAI endpoint **:9090**, TTL 600 | wired+enabled (`llama-swap.md`) |
| **voice-venvs** | engine | `/home/tim/.voice-venvs` | **48G** | One venv per voice engine (incompatible dep stacks). TTS: chatterbox/orpheus/cosyvoice/xtts/qwen3tts (:4124–4128). STT: parakeet/canary/granite (:2031–2033). Engine CODE lives in-repo (`voice/engines/*.py`, `voice/ears/*.py`); venv supplies Python | unit-backed; STT VRAM-arbitrated, load-on-demand (`voice-venvs.md`) |
| **voicemode** | engine | `/home/tim/.voicemode` | 2.9G | Legacy whisper.cpp STT (`voicemode-whisper.service`); oldest voice unit (2025-12) | the baseline CPU ear (`voicemode.md`) |
| **CosyVoice** | engine | `/home/tim/CosyVoice` | 5.3G | Alibaba FunAudioLLM CosyVoice clone + CosyVoice2-0.5B weights; added to `sys.path` by in-repo `voice/engines/cosyvoice.py`; serves :4126 | indirect sys.path wire (`CosyVoice.md`) |
| **corpora** | data | `/home/tim/corpora` | 93M | The "Claude Code Atlas" source library — 811 claude-platform-docs `.md` + 1051 claude-sessions transcripts; the SOURCE TEXT the recall index embeds | **STALE** — last write 2026-06-12; exporter timer inactive (`corpora.md`) |
| **cache-company** | data | `/home/tim/.cache/company/substrate-claude-sessions` | 1.6G | The live session-recall vector index: chroma (1009M) + `substrate.db` (98M) over corpora/claude-sessions; embed model `pplx-embed-context-v1-4b` @ :8007 | **STALE** — chroma 06-22, db 06-20; reindex timer inactive; holds a quarantined `chroma.corrupt-backup-20260620` (`cache-company.md`) |
| **recollection** | engine | `/home/tim/company/recollection` | 1.1G | Refit clone of `episodic-memory` v1.4.2 → the Company recall tool (TypeScript). MEANING-based recall; `board://`/`clone://` units; CLIENT of the :8007 embed lens. Own git, NOT a registered MCP | code lives, consumes :8007 (`recollection.md`) |
| **dot-recollection** | data | `/home/tim/company/.recollection` | 1.2G | recollection's live data store: `conversation-archive/`, `conversation-index/`, `logs/`, **`self/`** (per-session identity markers `<pid>.json` written by `ops/hooks/write_self_marker.py`, read by `runtime/session_scan.py`) | **FRESH** (06-26) — `self/` written every live session (`dot-recollection.md`) |
| **foundation** | data | `/home/tim/company/foundation` | 756K | The Company's memory of its origins — verbatim founding `exchanges/` + synthesized doctrine (`system/principles.md` etc). **Live input** to `nodes/model_of_tim.py` (reads `system/principles.md`). MOVED IN from `~/foundation` 2026-06-26 | live binding (`foundation.md`) |
| **dot-vi** | config | `/home/tim/.vi` | 224K | Cross-session frame — auto-loaded into EVERY Claude session. `CLAUDE.md` names the 4 layers (DNA=identity, FACTORY=type-builder, GALLERY=content/scenes, **THE COMPANY = address-resolution+models+substrate all layers resolve through**); `rules/cross-session-channels.md` launches fabric sessions via `~/company/channels/` | config/frame (`dot-vi.md`) |
| **mcp-mining** | work | `/home/tim/mcp-mining` | 59M | A FINISHED overnight conversation-mining run (2026-05-30/31): local-4B reads all chat history → bge-m3 embed → cluster → name/dialectic → Obsidian "Conversation-Mind" vault (Windows-side). NOT about MCP (misnomer) | **DORMANT** finished run (`mcp-mining.md`) |
| **company-scan** | work | `/home/tim/company-scan` | 9.4M | A FINISHED 2-pass local-4B forensic scan (2026-06-01) of Tim's Windows project tree (19,361 files) that recovered the ElevenLabs Wizard design | **DORMANT** finished run (`company-scan.md`) |
| **artefacts** | work | `/home/tim/artefacts` | 108K | Two founding-week docs: `Vi.md` (vision narrative) + `model-survey-2026-05-26.md` (RTX 4080 model survey across image/video/3D/voice) | **DORMANT** reference docs (`artefacts.md`) |
| **wizard-run-1** | work | `/home/tim/company/migration-pending/wizard-run-1` | 59M | (entry exists; a project→product pipeline prototype run on the Wizard corpus; sibling to mcp-mining/company-scan) | dormant prototype (ledger row) |
| **channel-test** | config | `/home/tim/channel-test` | 8K | (cross-session channel test scaffold) | (ledger row) |
| **build-coordination-docs** | work | `/home/tim` (6 files) | 76K | (loose build-coordination markdown at home root) | (ledger row) |
| **(company)** | — | `/home/tim/company` | 5.6G | the spine itself (§1) | partially live |

### 2b. CONNECTED — separate systems wired to the Company at the fabric/runtime level (not code-imported) — 4 entries

| Thing | kind | path | size | what it is | connection |
|---|---|---|---|---|---|
| **obsidian-overlord** | engine | `/home/tim/repos/obsidian-overlord` | 9.2G | The package IS **`substrate-mcp`** — a local MCP server indexing markdown vaults into 3 stores (address-graph + type-graph + Chroma semantic). 48 tools. **10 vaults registered**; 9,790 addresses, 116,726 chunks. Points at the SAME `pplx-embed-context-4b` @ **:8007** the Company uses | **operational** — loads as an MCP in Company Claude sessions; shares the :8007 embedder; **zero code import** either way (`obsidian-overlord.md`). GENUINELY LIVE — `.state/substrate.db` 5.4G mtime today |
| **counterpart** | work | `/home/tim/repos/counterpart` | 920M | The **Design DNA Pack** / identity layer — "a compositional assembly system, a language" (tokens→registries→templates→dials). The ONLY thing in `~/repos` referencing `~/company` (4 doc/comment path-pointers, NOT imports) | **aimed-at + shared-corpus.** Refs the Company's `runtime/ui_claude_session.py` + `runtime/territory.py` (RHM voice corpus) + `build-prep/.../DECISION-CARD-HOST-CONTRACT.md`. inner `design/` git +93 ahead of origin (`counterpart.md`) |
| **vi-visual-bridge** | work | `/home/tim/vi-visual-bridge` | 1.3G | **"Vi-Wizard"** — a polymorphic visual-interaction bridge (bridge server :7731 + MCP :7732 + embedded Chrome SPA). Re-pointed at "the Company front interface/centre" via company-channel | **fabric-only** (zero code import). islands-join-mainland: good parts built INTO the centre. Code froze 2026-03-29; session activity to 2026-06-22 (`vi-visual-bridge.md`) |
| **openwebui-venv** | engine | `/home/tim/openwebui-venv` | 6.8G | Open WebUI chat playground — Tim's manual surface to exercise local vLLM models; auto-discovers OpenAI servers; :8080 | **NOT systemd/Docker-wired** (verified) — launched manually; client of vLLM chat(:8000)+embed(:8001) (`openwebui-venv.md`) |

### 2c. CANDIDATE — could join the Company but no committed wire today — 3 entries

| Thing | path | size | what it is | link |
|---|---|---|---|---|
| **ComfyUI** | `/home/tim/ComfyUI` | 636M | Node-graph image/video generation app; venv was DELETED 2026-06-06 (reclaim 7.3G) — dormant | zero `~/company` refs (`comfyui.md`) |
| **comfyui-data** | `/home/tim/comfyui-data` | 36G | ComfyUI's model-weights + 13 saved workflows (character gen / IPAdapter-FaceID / upscale / video) | data-of ComfyUI; zero company refs (`comfyui-data.md`) |
| **kohya_ss** | `/home/tim/kohya_ss` | 11G | Gradio GUI for training diffusion models (LoRA/Dreambooth/SDXL) | upstream clone; zero company refs (`kohya_ss.md`) |

### 2d. RESOURCE — idea-sources / corpora prospected for the Company (mine, don't wire) — 7 entries

| Thing | path | size | what it is | relation to Company |
|---|---|---|---|---|
| **universal-mechanics** | `/home/tim/universal-mechanics` | 89M | Tim's upstream **science/framework vault** — the "substrate-environment" theory + the **eight substrate-mechanics** (substrate-store, type-registry, relation-layer, operation-registry, multi-axis-index, projection-layer, interaction-layer, verification-layer) + axes-and-orientations + ConceptV math | **the conceptual genome** the Company instantiates; prospected, NOT wired (`universal-mechanics.md`) |
| **graph-editor** | `/home/tim/repos/graph-editor` | 423M | **RelaTesseract / `rltsrct` MCP** — browser graph viz/editor (vis.js, :8899) for Project Vi memory graphs + a live MCP (234 tools behind a 6-tool JIT facade). Relations first-class; address-based `scheme://` medium | **near sibling-DNA** AND a live registered MCP (in `~/.claude.json`). Directly relevant to MCP-surface + graph design (`graph-editor.md`) |
| **cognitive-framework** | `/home/tim/.cognitive_framework` | 27M | Persisted store of an earlier cognitive-process engine — thought-as-10-typed-blocks wired into flows, run over a corpus; `canonical_flow_graph_v2`; projection_roles; runtime-capability honesty | **conceptual ancestor** of the compositional dataflow engine (`cognitive-framework.md`) |
| **ai-systems-strategic-overview** | `/home/tim/ai-systems-strategic-overview` | 60K | Earliest artifact (2025-08-07) — a Mintlify business-framing site (meta-AI / Agent-MCP / PraisonAI). 6 of 18 pages exist | ancestral business sketch; trajectory measure (`ai-systems-strategic-overview.md`) |
| **creations (VECO)** | `/home/tim/creations` | 112K | Declarative TS engine modeling any process as a "circuit": **Principal→Domain→Intent→Proposal→Approval→Execution** (Tim's relational-systems circuit verbatim). simple/conditional/MCP shapes. Spec/scaffold, no runtime | the universal-circuit ancestor (`creations.md`) |
| **docs** | `/home/tim/docs` | 2.8M | (data corpus, prospected) | resource (ledger row) |
| **world-keeper-profile** | `/home/tim/world_keeper_profile` | 32K | (data — the narrative "World Keeper" profile referenced by creations' fiction) | resource (ledger row) |

### 2e. Not in the ledger but live this run
- **`company-stt-moonshine.service`** (Moonshine ONNX, compact realtime STT, **:2034**) — ACTIVE now, but NOT in any orienteering entry's `service_units` list (the entries predate it; the voice-venvs entry lists parakeet/canary/granite + voicemode/kokoro). **This is sprawl drift the ledger hasn't caught** — a new ear added after 2026-06-26. (Observed: `systemctl --user list-units 'company-*'`.)

---

## 3. The glyphgraph-RELEVANT slice — where each piece sits

The conversational glyphgraph (a live conversational surface rendering meaning as a glyph-graph) fuses into these specific systems. Here is each, with its physical home and live state.

### 3a. The bridge — the single seam between surface and brain
- **`runtime/bridge.py`** → `company-bridge.service`, **HTTP API on :8770**. **LIVE this run** (`:8770` OPEN; unit active running). It is a **SHARED surface** — restart blinks every session on the canvas (`HANDOFF.md:106`).
- It serves the canvas + `/api`. The voice circuit endpoint is `POST /api/voice/stream?persona=<id>` (`HANDOFF.md:78`). The config-lab endpoints (`/api/rhm-config`, `/api/personas`, `/api/voice/services`, `/api/roles`, `/api/knobs`, `/api/models`) are all here (`HANDOFF.md:88-98`).
- The **decision→implementation wire** (`runtime/implement.py` + `dispatch_decision`) and the **production entry seam** `POST /api/build-intent` live here too (`MAP.md:88`) — relevant if the glyphgraph surfaces build-intents.
- **Inferred:** any glyphgraph surface talks to the brain through this one bridge (C8 contract). I have not traced the bridge route table.

### 3b. The models (fabric) — what answers
- **`fabric/config.py`** (Observed, this run): `OLLAMA_DIRECT = http://localhost:11434/v1`; `DEFAULT_BASE_URL` = that ollama endpoint. **`DEFAULT_BRAIN` has NO hardcoded default — resolve-or-fail-loud** (cognition-is-role-resolved; `require_brain()` raises if unresolved — `config.py:21-31`). **`forbid_gemini()`** hard-blocks Gemini (`config.py:74-77`).
- Embeddings have their OWN endpoint: **`DEFAULT_EMBED_URL = http://localhost:8007/v1`**, model **`perplexity-ai/pplx-embed-context-v1-4b`**, 2560-dim INT8 — the LIVE GPU-served embedder. **BGE-M3 @ :8001 is DORMANT** (endpoint down — `config.py:34-40`; confirmed `:8001` closed this run).
- **Live model endpoints this run:** ollama `:11434` OPEN, vLLM chat `:8000` OPEN, embed-pplx `:8007` OPEN. Closed: `:8001` (bge-m3).
- The RHM brain is config (`rhm_config().model`). Production options (`HANDOFF.md:84-86,109`): ollama `qwen3.5-9b-q8:latest` (:11434, tool-capable, warm ~3.8s); the faster `cyankiwi/Qwen3.5-4B-AWQ-4bit` (vLLM :8000); the FP8 everyday loadout `@interaction-fp8` (Qwen3.5-4B-FP8 :8001, recall+voice co-resident) and `@quality-9b` (`docs/brain-loadouts.md`).
- The fabric module: `fabric/{config,client,transport,vram}.py` + `litellm.config.yaml` + `serve_litellm.sh` (Observed `ls fabric/`).

### 3c. The voice circuit — speaking the glyphgraph
- The full circuit (`HANDOFF.md:78-82`): `audio in → STT (rhm_config.stt ear) → SUITE.chat (the ONE brain) → TTS (persona's engine) → ndjson stream out`. Stream events: `transcript` · `reply` · per-sentence `chunk` (with **`wav_b64`** — gotcha, not `audio`/`b64`) · `done`. Sentence-chunked + cancellable.
- **TTS engines** (5 personas, `HANDOFF.md:64-71`): viv/chatterbox :4124 · pip/orpheus :4125 (vLLM) · tess/cosyvoice :4126 · wren/xtts :4127 · sable/qwen3tts :4128 (Qwen3-VoiceDesign — designs a voice from text, the identity source). Code in `voice/engines/*.py`; venvs in `~/.voice-venvs`.
- **STT ears:** parakeet :2031 (~5GB) · canary :2032 (~12GB) · granite :2033 (~6.5GB) — GPU, VRAM-arbitrated load-on-demand. `whisper.cpp` :2022 CPU is boot-default. **Plus moonshine :2034 (ACTIVE now, not in the ledger).** Kokoro TTS :4123 (CPU, ACTIVE now).
- **Voice identity (Tim-open decision, `HANDOFF.md:113-117`):** `COMPANY_VOICE_REF` = an AI-synthesised clip (qwen3tts designs a voice → 3 clone engines clone it → "one woman underneath, five souls on top"). Open: one voice vs a cast of five.
- In-repo: `voice/{lifecycle,loop,personas,say,speakable,stt,tts_service}.py` + `voice/{ears,engines,ops,models,ref}/`. `runtime/cc_voice.py` + `mcp_face/tools/cc_voice.py` are the agent-face voice verbs.
- **Verified boundary (`HANDOFF.md:154`):** backend circuit proven by use; **browser mic-in / speaker-out + listening-mode UI on the phone is NOT verified** (Tim's hardware to confirm) — the front-end half is the open lane.

### 3d. Recall / corpus — the memory the glyphgraph draws on
- **The recall substrate** is a chain: `corpora/claude-sessions` (source text, 93M) → embedded via `:8007` (pplx-embed) → `cache-company` chroma+substrate.db index (1.6G). Driven by the exporter timer (jsonl→corpora, 20min) + reindex timer (delta-embed, ~5min after). **BOTH TIMERS ARE INACTIVE** — the index is stale (corpora 06-12, chroma 06-22). The :8007 embedder itself is LIVE.
- **`recollection/`** (in-repo, own git, TypeScript) is the recall TOOL — MEANING recall, `board://`/`clone://` units, CLIENT of :8007. Its data is `dot-recollection/` (FRESH — `self/` markers written every session).
- **In-repo recall/corpus code:** `runtime/{corpus,corpus_fusion,corpus_neighbours,corpus_rerank,recall_determine,session_recall,session_search,session_lens,session_lineage,session_scan,session_channels}.py` + `mcp_face/tools/{corpus,session_recall,sessions,ingest}.py`. The hybrid-fusion path (`runtime/corpus_fusion.py` → `corpus(op=query,mode=hybrid)`) is PURE-MATH verified but end-to-end unverified pending embedder (per the mission memory).
- **Session search → handle → act** (`runtime/session_search.py`, `MAP.md:98`): a content hit over the session-transcript corpus is a LIVE handle joined at query time to the registry; two modes (lexical always-on, semantic via pplx-embed). Directly relevant if the glyphgraph nodes are session/recall handles.
- **obsidian-overlord / substrate-mcp** shares the SAME :8007 embedder and exposes its own semantic/address/type graph over 10 vaults — a parallel graph substrate the glyphgraph could read OR collide with (see §5).

### 3e. Modes — the presence dial the glyphgraph operates under
- **`runtime/modes_registry.py`** (Observed head): modes are a **FILE-DISCOVERED registry** (`modes/<id>.py`, one `MODE` dict each), made open per Tim 2026-06-28 ("modes are a starter set, open, all in registries, adjustable"). Order-bearing (explicit `order` field). Each mode declares `label, directive, resolution, consent, grain, shape, stage`.
- The 8 starter modes (`MAP.md:79`): listening, text-only, background, focus, walkthrough, watch-and-react, decide-for-me, off. Mode IS a node (`rhm_mode`); behavior comes from the directive.
- Also `runtime/mode_detection_rules.py` + `mode_detection_rules/` (detect which mode from context) and `modes/` dir.

### 3f. The canvas / surface apps — where the glyphgraph renders
- **`canvas/`** (`canvas/AGENTS.md` head): "the frontend — the surface Tim operates (**tldraw + React + Tauri**)." Guarantee: **ONE generic `ai-node` shape, data-driven from `/object_info` (C5)** — not one shape per node-type (new node-types need ZERO frontend code). The canvas **reflects** state, never owns it.
- In-repo: `canvas/{App.tsx, AppContext.ts, NodeShape.tsx, ForagerShape.tsx, api.ts, app.css, main.tsx}` + `canvas/{components, regions, extensions}` + `canvas/app/` (the Vite/React app). Served by `company-canvas.service` (vite :5173) — **:5173 CLOSED this run** (canvas vite not running; bridge serves the built frontend; per `HANDOFF.md:107` the phone path is Tailscale → vite :5173 → proxy :8770).
- **Brain-authored UI tiers** (`MAP.md:102-107`): declarative **panels** (`panels/`, JSON field-defs) + arbitrary **extensions** (`canvas/app/src/extensions/`, build-gated `.tsx`, operator-only). Both governed + git-reversible.
- **`surface/`** and **`forms/`**, **`projections/`**, **`mark_types/`**, **`board_edges/`**, **`relation_types/`** top-level dirs (Observed) — a typed graph/board/mark vocabulary already exists as registries; a glyphgraph likely composes against these rather than inventing.
- **Other surfaces in the orbit:** the `graph-editor` (vis.js graph editor, :8899) and `vi-visual-bridge` (embedded Chrome SPA, :7731) are existing visual surfaces — sibling/connected, candidates to fuse INTO the centre (islands-join-mainland), not parallel apps.

---

## 4. Live service + port state (Observed, 2026-06-30)

`systemctl --user list-units 'company-*'` → **4 ACTIVE units**:
- `company-bridge.service` — :8770 (UI face of the Suite) — **OPEN**
- `company-embed-pplx.service` — :8007 (pplx-embed-context-v1-4b) — **OPEN**
- `company-tts-kokoro.service` — :4123 (CPU TTS)
- `company-stt-moonshine.service` — :2034 (Moonshine ONNX STT) — *not in the ledger*

`systemctl --user list-timers 'company-*'` → **0 active timers** (exporter + reindex both down → recall index stale).

Port probes: **8770 OPEN · 8007 OPEN · 11434 OPEN (ollama) · 8000 OPEN (vLLM chat)** · 5173 closed (canvas vite) · 8001 closed (bge-m3 embed).

**Read:** the live minimum is running — bridge + brain (ollama/vLLM) + the pplx embedder + a light TTS + a light STT. The heavy GPU voice engines, the canvas vite dev server, and the export/reindex timers are all down (load-on-demand / disabled). `company.target` is disabled (manual start).

---

## 5. The shape of the sprawl — duplicated, scattered, moving

**DUPLICATED / overlapping (the union-not-bridges pressure points):**
- **Multiple graph/visual surfaces:** the in-repo `canvas/` (tldraw), the connected `graph-editor`/rltsrct (vis.js, :8899), and `vi-visual-bridge`/Vi-Wizard (Chrome SPA, :7731). Three places to render a graph — the glyphgraph should be ONE surface in `canvas/`, absorbing the good parts (islands-join-mainland), not a fourth island.
- **Multiple semantic/graph substrates over the SAME embedder:** `cache-company` (the Company's own chroma recall index) AND `obsidian-overlord`/substrate-mcp (address-graph + type-graph + chroma over 10 vaults) both point at **:8007**. Two indexes, one embedder — a real convergence candidate (the mission memory flags "interim-chroma retire").
- **Multiple STT ears for the same job:** voicemode/whisper.cpp (:2022), parakeet/canary/granite (:2031-33), and now moonshine (:2034) — the ear is a config slot (`rhm_config.stt`), so this is by-design swappability, but the ledger hasn't caught moonshine.
- **Multiple model-serving paths:** vLLM direct (`serve_model.sh`), llama-swap (small-model TTL router :9090), ollama (:11434), and LiteLLM (`fabric/litellm.config.yaml`/`serve_litellm.sh`). Four ways to reach a model — fabric is meant to be the one OpenAI-compatible face over all.
- **Three Vi layers in three repos** (`vi-visual-bridge.md:282-288`): FACTORY = `vi-visual-dev` (Windows, GH `Concept-Vi/vi-vision`) · DNA = `counterpart` (`~/repos/counterpart`) · Vi-Wizard = `vi-visual-bridge`. The Company is the substrate all three resolve through (per `.vi/CLAUDE.md`).

**SCATTERED (lives outside `~/company`):**
- Venvs at `~` (vllm-env, jina-v4-env, .voice-venvs 48G, openwebui-venv) and `/usr/local/bin` (llama-swap binary). Recall index in `~/.cache/company`. Certs in `~/.config/company`. Service units in `~/.config/systemd/user` (mirrored in-repo at `ops/systemd/`). Cross-session frame in `~/.vi`. Connected repos in `~/repos`. Finished prototype runs scattered at `~` (mcp-mining, company-scan) with deliverables on the Windows side (`/mnt/c/...`).
- The two-hop launch wires (unit → launcher script → venv) mean the venv is never named in the unit — a dependency the ledger had to trace by reading `serve_model.sh`/`serve_jina_v4.sh`.

**MOVING / drift:**
- `foundation` moved IN to `~/company/foundation` from `~/foundation` (2026-06-26, `move_intent: done`) — the worked example of the ledger tracking a migration. `recollection`/`dot-recollection` also `move_intent: done`.
- A **drift detector** now enforces the ledger (`runtime/orienteering_drift.py`, `AGENTS.md:64`): a path-existence gate fails loud if an entry's `path` vanishes; an orbit-coverage check surfaces uncatalogued home-dir things against `orienteering/_orbit-dispositions.json`.
- **Caught drift this run:** `company-stt-moonshine` is live but uncatalogued — exactly the kind of thing the orbit-coverage check is meant to surface; the voice-venvs/voice entries predate it.
- The recall loop is **stalled** (0 timers) — the index can't be assumed fresh; the glyphgraph reading recall must account for staleness or trigger an on-demand reindex (per mission memory, on-demand `ingest(op=reindex)` was added).

---

## 6. What this means for the glyphgraph build (synthesis, Inferred)

- **The fusion seam is the bridge (`:8770`) + the Suite.** A conversational glyphgraph is a `canvas/` surface that reflects Suite state over C8, draws nodes generically from `/object_info`, and speaks/listens through `/api/voice/stream`. It should NOT own state and should NOT be a parallel app.
- **The graph vocabulary already exists as registries** (`board_edges/`, `mark_types/`, `relation_types/`, `projections/`, `nodes/`, `flows/`). The glyphgraph composes against these — resolution-first, declare-rows-not-hand-build (Tim's standing method).
- **The models are role-resolved, never pinned** — the glyphgraph's brain is `rhm_config().model`, swappable live; embeddings are :8007 (live), chat is ollama/vLLM (live). No Gemini, ever.
- **Recall is real but stale** — the substrate (corpora→:8007→chroma) exists and the embedder is live, but the feed timers are down. A glyphgraph that draws on recall must handle staleness explicitly (fail-loud or on-demand reindex), per the no-silent-fallback law.
- **The biggest-version convergence** (Tim's "the two together and with the Company"): the glyphgraph + the recall substrate + the connected graph surfaces (graph-editor, vi-visual-bridge) + counterpart's DNA all fuse INTO `canvas/`/the Company centre — the patchwork IS the problem; everything renders through ONE instrument.

---

## Coverage / honesty
- **Read in full:** `MAP.md`, `AGENTS.md`, `CLAUDE.md`, `HANDOFF.md`, `orienteering/INDEX.md`, all 38 `orienteering/entries/*.md` (via batched cat), `canvas/AGENTS.md` head, `runtime/modes_registry.py` head, `fabric/config.py` (grepped). STATE.md read by section heads + the BUILT/not-built lists (truncated lines — it is 99k/40k-token, too large to read whole; I sampled the relevant capability lines).
- **Live-verified this run (2026-06-30):** `systemctl --user list-units/list-timers 'company-*'`, port probes on 8770/5173/8007/11434/8000/8001.
- **NOT done:** I did not trace the bridge route table line-by-line, did not read the in-repo recall/canvas/voice module bodies (only constitutions + heads + the ledger's traced wires), did not open the STATE.md prose in full. The ledger entries' own `coverage` is thin on many (files_read « files_total) — they are catalogue-level, not exhaustive.
- **Register:** descriptive. `status: unconfirmed` is the ledger's convention; live/dormant reads here are evidence-based but Tim confirms lifecycle.
