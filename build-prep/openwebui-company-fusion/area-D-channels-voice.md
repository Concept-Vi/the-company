---
type: map
area: channels + voice
coverage: {channels: 6/6 source files, voice: 40+ source files, systemd: 10 units, venvs: 7}
status: complete
last_read: 2026-06-28
---

# Area D: Channels + Voice — Complete Terrain Map

## CHANNELS (Cross-Session Fabric)

### Core Source
- **`channels/company_channel.mjs`** (line 1–173) — MCP server (company-channel).  
  Single port: dynamic (COMPANY_CHANNEL_PORT env, default 0 = OS-assigned).  
  What it IS: receives inbound POST /channel-reply notifications via HTTP, injects them as `notifications/claude/channel` events into live session. Registers each session under `.data/channels/<handle>.json` (session handle auto-assigned or from COMPANY_CHANNEL_HANDLE env). Exposes three tools: `reply` (sends text back to asking session), `announce` (one-line description), `profile` (writes agent's self-described identity: model/role/focus/expertise). Two-way: sessions POST back to supervisor (/channel-reply), which records in mailbox + pushes to asking session.  
  Public surface: HTTP POST body `{content, meta}` → 200 "ok", meta coerced to strings (safety guard: lines 151–157).  
  Supervisor address: `COMPANY_SUPERVISOR_BASE` env (default http://127.0.0.1:8771).  
  Claude ancestor PID traced (lines 34–52) — the session's self-id key, used by supervisor to resolve_own_session.  
  Live: YES (verified — .data/channels/ contains active registrations ch-*.json, operator.json, tim.json from 2026-06-28).

- **`channels/channel.mcp.json`** (1–9) — MCP config.  
  Declares company-channel server: node /home/tim/company/channels/company_channel.mjs, env COMPANY_ROOT=/home/tim/company.

- **`channels/company_channel.mjs` imports** —  
  @modelcontextprotocol/sdk (server/stdio), http, fs, path. Stdlib only + MCP SDK. No voice/runtime deps.

- **`channels/package.json`** (1) — @modelcontextprotocol/sdk ^1.29.0 (single dep).

- **`channels/profile-hook.sh`** (1–17) — SessionStart hook.  
  Injects reminder: "If you are a Company cross-session channel fabric member (you have a `profile` tool), call it near the start…"  
  Tim-wired into ~/.claude/settings.json (line 13).  
  Design: SessionStart hook only INJECTS REMINDER — agent writes its own profile (fail-safe: no prompt = agent ignores it).

- **`channels/profile_test.mjs`** (1–88) — End-to-end test.  
  Spawns company_channel.mjs under controlled env, does MCP handshake, calls profile tool, asserts on-disk entry.  
  Verifies: profile.role/focus written, description updated, model/pid/port/handle preserved (transport fields intact).  
  Test data location: spawns from tmp (cleaned up after).

### Data (Registration + Mailbox)
- **`.data/channels/`** — Live registry + mailbox.  
  - **`_channels/`** (dir) — per-session channel dirs (unused in current use; structure reserved).
  - **`ch-*.json`** (e.g., ch-cr4p7uxj.json, 269 bytes, 2026-06-28 14:30) — Session registration entries.  
    Schema: {handle, session_id, cwd, description, model, profile, pid, claude_pid, port, started}.  
    Example (ch-cr4p7uxj.json): handle, session_id, cwd=/home/tim/company, description, model, profile={…}, pid (systemd started), claude_pid (session ancestor), port, started timestamp.  
    *Note*: Multiple registrations suggest parallel sessions.
  - **`operator.json`** (255 bytes, 2026-06-28) — Operator profile (if one exists).
  - **`tim.json`** (231 bytes, 2026-06-28 19:10) — Tim's session profile.
  - **`_mail.jsonl`** (6.4 MB, 2026-06-28 13:28) — Durable mailbox (every reply is logged).  
    Append-only; survives session restarts.
  - **`_threads.json`** (93 KB, 2026-06-28 13:28) — Thread index (UUID → reply log position mapping).
  - **`_chat_lead.txt`** (11 bytes, 2026-06-24) — Simple marker/state (contents: "11 bytes").

### Source Structure
- **Minimal source footprint**: 6 files (company_channel.mjs + channel.mcp.json + package.json + profile-hook.sh + profile_test.mjs + node_modules).  
- **node_modules**: Express stack (@hono/node-server, express, cors, zod + deps). Used for: HTTP server (http module is stdlib; node_modules are for future/optional middleware).  
- **Build**: Node.js mjs (ESM). No build step; runs as child process (systemd or supervisor-launched).  
- **Config-driven**: port, handle, supervisor address, root dir all from env.

---

## VOICE (Trial: Five Characters, Six Engines, Six STT Ears)

### Voice-Scoped Ports (All 127.0.0.1, Shared Contract)

| Service | Port | Engine/Ear | What | Venv | Live/Dormant | VRAM / Compute |
|---------|------|-----------|------|------|--------------|-----------------|
| tts_service (Kokoro) | 4123 | kokoro-onnx | TTS baseline: CPU, ~no VRAM | `.voice-venv` (3.12) | Active | ~0 VRAM, CPU |
| company-voice-chatterbox | 4124 | chatterbox-tts | TTS: warm-realness ref-clip-based | `~/.voice-venvs/chatterbox` (3.12) | Systemd (on-demand) | ~6–8 GB GPU |
| company-voice-orpheus | 4125 | Orpheus-TTS (vLLM) | TTS: LLM-backbone (Llama-3.2), cued emotion | `~/.voice-venvs/orpheus` (3.12) | Systemd (on-demand) | ~9–10 GB GPU (vLLM resident) |
| company-voice-cosyvoice | 4126 | CosyVoice2 | TTS: instruct-coachable + ref-clip clone | `~/.voice-venvs/cosyvoice` (3.10) | Systemd (on-demand); import fails (see notes) | ~6–8 GB GPU |
| company-voice-xtts | 4127 | XTTS-v2 (Coqui) | TTS: realism ceiling, ref-clip-driven | `~/.voice-venvs/xtts` (3.12) | Systemd (on-demand) | ~6–8 GB GPU |
| company-voice-qwen3tts | 4128 | Qwen3-TTS VoiceDesign | TTS: TRIAL STARTER, voice-from-description | `~/.voice-venvs/qwen3tts` (3.12) | Systemd (on-demand) | ~5–7 GB GPU |
| (whisper.cpp) | 2022 | whisper.cpp | STT baseline: local HTTP, zero-install, on-machine | external (not in company/) | External | CPU (verified) |
| company-stt-parakeet | 2031 | Parakeet-TDT 0.6B v3 (NeMo) | STT: multilingual workhorse, 6% WER | `~/.voice-venvs/parakeet` (3.12) | Systemd (on-demand) | ~3.05 GB GPU |
| company-stt-canary | 2032 | Canary-Qwen 2.5B (NeMo) | STT: English-max + understanding (LLM) | `~/.voice-venvs/canary` (3.12) | Systemd (on-demand) | ~10.06 GB GPU (peak) |
| company-stt-granite | 2033 | Granite Speech 4.0 1B (transformers) | STT: compact, top-accuracy cross-check | `~/.voice-venvs/granite` (3.12) | Systemd (on-demand) | ~1.5–2 GB CPU (COMPANY_GRANITE_DEVICE=cpu) |
| company-stt-moonshine | 2034 | Moonshine (ONNX) | STT: compact realtime, <1 GB, no VRAM | `~/.voice-venvs/moonshine` (3.12) | Systemd (on-demand) | ~0 VRAM, CPU (9× realtime) |
| company-stt-parakeet-onnx | 2035 | Parakeet-TDT int8 ONNX (sherpa-onnx) | STT: lean, 25 languages, hotword-biasing | `~/.voice-venvs/parakeet-onnx` (3.12) | Systemd (on-demand) | ~1–1.5 GB CPU default |

**Boot Default Ear**: COMPANY_STT=moonshine (env, line 76 in voice.env; was whispercpp before 2026-06-28).

### TTS Engines — Source Files

| File | What | Public Surface | Warm | Notes |
|------|------|-----------------|------|-------|
| `voice/tts_service.py` (1–91) | Kokoro (baseline) | POST /tts {text,voice?,speed?} → audio/wav; GET /voices → {voices,default}; GET / → {ok:true} | Downloads kokoro-v1.0.onnx + voices-v1.0.bin on first run | CPU, ~no VRAM; runs in .voice-venv (3.12); default voice af_heart (env override) |
| `voice/engines/_service.py` (1–84) | Shared HTTP shell | (reused by all 5 trial TTS wrappers) | Calls warm(optional) before serving | Stdlib-only (json, sys, http.server); no heavy imports here; synth/voices/warm supplied by wrapper |
| `voice/engines/orpheus.py` (1+) | Orpheus-TTS wrapper | POST /tts {text,voice,speed} | warm() loads OrpheusModel, downloads model on first run | vLLM (Llama-3.2 backbone), 8 named voices (tara/leah/jess/leo/dan/mia/zac/zoe), cued emotion tags <laugh>/<chuckle>/<sigh>/…; FLASH_ATTN backend; vLLM ninja PATH fix (line 25–27); VLLM_USE_FLASHINFER_SAMPLER=0 (line 29) disables sampling FlashInfer (nvcc-JIT blocker); registry config block fallback to env (gpu_util/max_model_len read from ops/services.json config) |
| `voice/engines/chatterbox.py` | Chatterbox-TTS wrapper | POST /tts | warm() loads ChatterboxTTS | Reference-clip-driven; COMPANY_CHATTERBOX_EXAGGERATION=0.5 (dial); COMPANY_VOICE_REF required (fails loud if absent) |
| `voice/engines/cosyvoice.py` | CosyVoice2 wrapper | POST /tts | warm() loads AutoModel (repo path from COMPANY_COSYVOICE_REPO/COMPANY_COSYVOICE_DIR env) | Instruct-coachable + ref-clip; deepspeed JIT checks CUDA ops at import → CUDA_HOME must be set (line 56 in voice.env: /home/tim/vllm-env/lib/python3.12/site-packages/nvidia/cu13); repo clone (not pip); import still fails due to openai-whisper build issue (REQUIREMENTS.md note) |
| `voice/engines/xtts.py` | XTTS-v2 wrapper | POST /tts | warm() loads TTS model (non-commercial) | Reference-clip-driven; COQUI_TOS_AGREED=1 (env, line 59); COMPANY_VOICE_REF required; numeric speed support |
| `voice/engines/qwen3tts.py` | Qwen3-TTS VoiceDesign wrapper | POST /tts | warm() loads Qwen3TTSModel | Voice-from-description (no ref-clip needed); model already in HF cache (COMPANY_QWEN3TTS_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign); TRIAL STARTER (should be brought up first post-restart) |

### STT Ears — Source Files

| File | What | Public Surface | Warm | Model / Notes |
|------|------|-----------------|------|---------------|
| `voice/stt.py` (1–435) | Speech-to-text provider registry + transcription | available_stt() → {id→{label,kind,available,detail,…}}; transcribe(audio,provider) → {text,provider} | Lazy per-engine (_engine() guards imports) | Registry-is-truth: STT_PROVIDERS (dict[str,dict], lines 68–119) declares all ears: kind (cloud/local_lib/local_http), url/route/field, or lib/secret. Aliases (STT_ALIASES): whisper↔whisper_local, whisper.cpp↔whispercpp. boot default STT_DEFAULT=moonshine (env override COMPANY_STT, line 134). Cloud (assemblyai) audio leaves machine (deliberate choice). No silent fallback on down ear — raises naming provider+endpoint (AGENTS.md rule 4). _to_wav16() normalises browser webm/mp4 → 16k mono wav (ffmpeg; line 25–44). |
| `voice/ears/_stt_service.py` (1–100+) | Shared HTTP shell (STT twin of engines/_service.py) | POST /inference multipart file=@clip.wav → {text}; GET / → {ok:true,ear:<name>}; fail-loud 500 {error} | Calls warm(optional) before serving | Stdlib-only (json, sys, http.server, io); _parse_multipart_file() (stdlib multipart parsing, no `cgi`). Same contract as whisper.cpp so stt.py's _http_transcribe reaches all ears uniformly (route+field per ear's catalog row). |
| `voice/ears/parakeet.py` | Parakeet-TDT 0.6B v3 (NeMo) on :2031 | POST /inference → {text} | warm() loads NeMo ASRModel | from nemo.collections.asr; model=nvidia/parakeet-tdt-0.6b-v3; device=cuda; 25 languages; ~3.05 GB resident; CUDA-13 hazard (warm() fails loud if GPU path won't load) |
| `voice/ears/canary.py` | Canary-Qwen 2.5B (NeMo) on :2032 | POST /inference → {text} | warm() loads SALM-based ASR | NeMo, English-max + understanding (LLM-based); ~10.06 GB peak; on-demand (don't enable alongside parakeet+granite) |
| `voice/ears/granite.py` | IBM Granite Speech 4.0 1B (transformers) on :2033 | POST /inference → {text} | warm() loads PretrainedSpeechRecognitionModel | transformers, COMPANY_GRANITE_DEVICE=cpu (dodges CUDA-13, no GPU room under loadout); ~1.5 GB |
| `voice/ears/moonshine.py` (1–50+) | Moonshine (ONNX) on :2034 | POST /inference → {text} | warm() loads MoonshineOnnxModel + tokenizer | ONNX-runtime (no torch, no NeMo), <1 GB, CPU default (0 VRAM). Built for live conversation. ~9× realtime (34 s clip in 3.7 s). English. Built-in IntentRecognizer (speech→action). COMPANY_MOONSHINE_MODEL (default moonshine/base; moonshine/tiny available; v2-medium checkpoint swappable via env). Does NOT pad short clips → short commands transcribe fast (STA payoff). Quality ~6.6% WER (base/medium). |
| `voice/ears/parakeet_onnx.py` | Parakeet-TDT 0.6B v3 int8 ONNX (sherpa-onnx) on :2035 | POST /inference → {text} | warm() loads OfflineRecognizer | sherpa-onnx, ~1–1.5 GB, CPU default. 25 European languages. Hotword/context biasing (strongest STA customization). ~6.3% WER. Distinct from parakeet (:2031, heavy NeMo/GPU build). |

### Voice Support Modules

| File | What | Notes |
|------|------|-------|
| `voice/personas.py` (1–149) | Five trial personas (data registry) | PERSONAS dict: viv/tess/sable/pip/wren. Per persona: name, shading (voice character), voice_shading, engine (suggested), voice (voice arg default), brain (system prompt), voice_description (for engines that design voice from text), voices (named-voice mappings per engine: orpheus/kokoro). VOICE_BASE constant (refined Australian woman, early 40s, clear mid-low pitch, dry wit). list_personas() → UI list; get_persona(name) → full record. Order array: viv/tess/sable/pip/wren (cast-doc spread). No fabricated voice data — ref-clip engines fail loud if COMPANY_VOICE_REF missing. |
| `voice/speakable.py` (1–259) | Pre-TTS speech clean + engine-aware expression | speakable(reply, engine, *, warn=None) → str. Strips markdown (fences, inline code, links, headings, blockquotes, tables, lists, emphasis, bare URLs, emoji). Maps canonical expression tags (<laugh>, <sigh>, <chuckle>, <cough>, <sniffle>, <groan>, <yawn>, <gasp>, <breath>) to engine-native syntax (orpheus <tag>, chatterbox [tag], cosyvoice [laughter]/[breath]) or strips if engine can't speak it (qwen3tts/xtts/kokoro → no inline expression). Fail loud: non-string reply raises; non-empty reply that cleans to EMPTY raises (never hand engine silence). Unknown engine: warns but doesn't break (strips all expression + markdown). Stdlib-only (regex); runs in both 3.14 runtime and 3.12 .voice-venv. Applied at pre-TTS seam (bridge /api/voice/stream, /api/voice/turn via loop.loop_turn, /api/tts). |
| `voice/loop.py` (1–80+) | Conversation loop: STT → brain → TTS, with barge-in + turn-detection | WHY HTTP for brain: loop runs in .voice-venv (3.12), Suite is 3.14 → can't import Suite here. Brain reached via POST bridge /api/chat {message, graph_id, focus} → {reply, action, mode, history}. Three steps (injectable): ear (stt.transcribe), brain (bridge /api/chat), mouth (engine /tts). Barge-in + semantic turn-detection exposed as hooks (browser audio stream lives there). ENGINE_PORTS derived from ops/services.json at import time (lines 38–77 _load_engine_ports() → services.json entries `tts-*` with `port` field; fails loud if missing). BRIDGE_URL env (default http://127.0.0.1:8770). |
| `voice/lifecycle.py` (1–100+) | Load/unload/status for all loadable voice services | Unified VRAM authority: drives systemd units (not Popen), budgets through shared ops/cli/gpu.py core. _loadable() reads ops/services.json for group:voice entries with load block. is_up() probes service health endpoint (GET, 3 s timeout). vram() reads nvidia-smi via shared core. Fail loud on VRAM unreadable. Systemd unit launch = is-active (console sees it, counts VRAM). cgroup teardown reaps orphan processes (vLLM EngineCore). Convergence 2026-06-06: unified with console's authority (no dual-authority OOM bug). |

### Voice Config + Ops

| File | What |
|------|------|
| `voice/ops/voice.env` (1–90) | Shared env for all voice services. Sourced by units + launcher. Ports (4123–4128, 2022/2031–2035). COMPANY_BRIDGE_URL=http://127.0.0.1:8770. COMPANY_VOICE_REF=/home/tim/company/voice/ref/company_voice_ref.wav (doesn't exist yet; clone engines fail loud if absent). TTS device (cuda). Per-engine tuning: chatterbox exaggeration/cfg, orpheus model/voice/maxlen/gpu_util/eager/attn, cosyvoice repo/dir/CUDA_HOME, xtts model/lang/TOS, qwen3tts model/device/attn/lang, granite device (cpu). STT ear defaults: whisper model/device/compute/lang, VAD/boot ear (COMPANY_STT=moonshine). Venv roots: COMPANY_VOICE_VENVS=~/.voice-venvs, COMPANY_LOOP_VENV=~/company/.voice-venv. HF_HUB_DISABLE_XET=1 (line 89, Xet backend stalls). |
| `voice/ops/voice-stack` | Launcher: install/start/stop/restart/status/health/logs/ports/enable-boot. Mirrors ~/.local/bin/vllm-stack. Systemd user-unit control (systemctl --user). |
| `voice/ops/make_reference_clip.sh` | Post-restart: mint COMPANY_VOICE_REF from Qwen3-VoiceDesign using personas.VOICE_BASE. Clone engines (chatterbox/xtts/cosyvoice) reuse that one wav. |
| `voice/trial_manifest.json` (1–83) | Concrete persona → engine → voice mappings. voice_arg_semantics per engine (qwen3tts=description, cosyvoice=description+clip, orpheus=named_voice, chatterbox/xtts=ref_clip). needs_ref_clip per persona. Engine ports 4123–4128 declared. |
| `voice/ops/README.md` (1–84) | Post-restart finish (short path): install units → start qwen3tts → mint ref clip → start rest → verify. Per-engine install status table (2026-06-04): ears ✅ imported; qwen3tts ✅; xtts ✅; chatterbox ✅; orpheus ✅; cosyvoice ❌ (repo build blocker, openai-whisper wheel fail, deepspeed timeout). |

### Models (Pre-Downloaded)

| Path | Model | What | Size |
|------|-------|------|------|
| `voice/models/kokoro-v1.0.onnx` | Kokoro (ONNX) | TTS baseline, CPU | ~200 MB |
| `voice/models/voices-v1.0.bin` | Kokoro voices | Voice data | ~100 MB |
| `voice/models/parakeet-tdt-v3-int8/` | Parakeet-TDT 0.6B v3 int8 ONNX | STT (sherpa-onnx), encoder/decoder/joiner + tokens.txt | ~670 MB |

### Reference Clip

- **COMPANY_VOICE_REF** = `/home/tim/company/voice/ref/company_voice_ref.wav`  
  Does NOT exist yet. Will be minted post-restart from Qwen3-VoiceDesign (voice/ops/make_reference_clip.sh) using personas.VOICE_BASE. Clone engines (chatterbox/xtts/cosyvoice) fail loud if absent.

### Systemd Units (10 Total)

| Unit | Port | Venv | TimeoutStartSec | Notes |
|------|------|------|-----------------|-------|
| company-voice-chatterbox | 4124 | ~/.voice-venvs/chatterbox | default | Warm-realness benchmark |
| company-voice-orpheus | 4125 | ~/.voice-venvs/orpheus | 900 s | Heaviest (vLLM cold-start on GPU) |
| company-voice-cosyvoice | 4126 | ~/.voice-venvs/cosyvoice | default | deepspeed + repo (import fails per ops/README) |
| company-voice-xtts | 4127 | ~/.voice-venvs/xtts | default | Non-commercial license |
| company-voice-qwen3tts | 4128 | ~/.voice-venvs/qwen3tts | 600 s | TRIAL STARTER; model in HF cache |
| company-stt-parakeet | 2031 | ~/.voice-venvs/parakeet | 600 s | ~3.05 GB; do not enable all 3 GPU ears together |
| company-stt-canary | 2032 | ~/.voice-venvs/canary | default | ~10.06 GB (peak); on-demand |
| company-stt-granite | 2033 | ~/.voice-venvs/granite | default | CPU (COMPANY_GRANITE_DEVICE=cpu avoids CUDA-13) |
| company-stt-moonshine | 2034 | ~/.voice-venvs/moonshine | 600 s | <1 GB, 0 VRAM, default boot ear |
| company-stt-parakeet-onnx | 2035 | ~/.voice-venvs/parakeet-onnx | default | int8 ONNX, 25 languages, hotword-biasing |

All units: WorkingDirectory=/home/tim/company, EnvironmentFile=%h/company/voice/ops/voice.env, Type=simple, Restart=on-failure RestartSec=10, StandardOutput=journal StandardError=journal, WantedBy=default.target.

### Virtual Environments (7 + Bridge)

| Venv | Location | Python | Primary | Status |
|------|----------|--------|---------|--------|
| .voice-venv | ~/company/.voice-venv | 3.12 | Kokoro + faster-whisper + Silero VAD (loop runs here) | ✅ (loop source) |
| ears | ~/.voice-venvs/ears | 3.12 | faster-whisper + Silero VAD | ✅ (import-verified) |
| qwen3tts | ~/.voice-venvs/qwen3tts | 3.12 | Qwen3-TTS-VoiceDesign | ✅ (import-verified) |
| xtts | ~/.voice-venvs/xtts | 3.12 | coqui-tts 0.25.3 | ✅ (import-verified) |
| chatterbox | ~/.voice-venvs/chatterbox | 3.12 | chatterbox-tts 0.1.7 + torch 2.6.0+cu124 | ✅ (import-verified) |
| orpheus | ~/.voice-venvs/orpheus | 3.12 | orpheus-speech 0.1.0 + vllm 0.22.0 + torch 2.11.0 + snac 1.2.1 | ✅ (import-verified) |
| cosyvoice | ~/.voice-venvs/cosyvoice | 3.10 | CosyVoice2 git clone | ❌ (repo build blocker: openai-whisper wheel, deepspeed timeout) |
| parakeet | ~/.voice-venvs/parakeet | 3.12 | NeMo ASR (nemo_toolkit[asr]) | (not status-checked pre-restart) |
| canary | ~/.voice-venvs/canary | 3.12 | NeMo ASR (SALM) | (not status-checked pre-restart) |
| granite | ~/.voice-venvs/granite | 3.12 | transformers (Granite Speech) | (not status-checked pre-restart) |
| moonshine | ~/.voice-venvs/moonshine | 3.12 | moonshine-onnx + onnxruntime | (not status-checked pre-restart) |
| parakeet-onnx | ~/.voice-venvs/parakeet-onnx | 3.12 | sherpa-onnx + onnxruntime | (not status-checked pre-restart) |

**Note**: All venvs on ext4 (NOT /mnt/c, NOT production venvs). HF model cache shared (COMPANY_QWEN3TTS_MODEL already cached; Parakeet int8 model dir voice/models/).

### Secret Handling

- **STT keys**: ~/company/.secrets (gitignored). Line parsing (key=value, # comments). stt.py reads via secret(key, default) function (lines 151–163).  
  ASSEMBLYAI_API_KEY (assemblyai STT provider).  
  Env override: secret(key) checks os.environ first, then .secrets file.

- **No TTS keys**: All local engines (Kokoro, Orpheus, CosyVoice, XTTS, Chatterbox, Qwen3-TTS are model weights in HF cache or local repos). STT keys only.

---

## NOTABLE + SURPRISING FINDINGS

1. **Unified VRAM Authority Convergence (2026-06-06)** — voice/lifecycle.py now drives the SAME systemd units the console does (systemctl --user start) + budgets through shared ops/cli/gpu.py core, closing the old dual-authority bug where UI-Popen-launched voice services were invisible to the budget and could OOM a second start. This is a keeper-pass design.

2. **TTS Engine FLASK_ATTN Backend + Ninja PATH Fix (Orpheus)** — Disables FlashInfer sampler (VLLM_USE_FLASHINFER_SAMPLER=0, line 29 orpheus.py) to avoid nvcc-JIT compilation on first synth (would crash with "Could not find nvcc"). Also prepends venv bin to PATH so Triton ninja is found (lines 25–27). These are proven fixes, not speculative.

3. **CUDA_HOME Requirement for CosyVoice2** — deepspeed JIT-checks CUDA ops at import and FAILS LOUD if CUDA_HOME is unset. Solution: point env to real CUDA toolkit (line 56 voice.env: /home/tim/vllm-env/lib/python3.12/site-packages/nvidia/cu13). CosyVoice import still fails due to openai-whisper build blocker (REQUIREMENTS.md), but this is separately documented.

4. **Moonshine as New Boot Default (2026-06-28)** — Replaced whispercpp as COMPANY_STT=moonshine (voice.env line 76). Moonshine is ONNX-runtime (no torch/NeMo), <1 GB, 0 VRAM, CPU default ~9× realtime. Built for live conversation + STA (no padding short clips). This is the new "interaction loadout" ear.

5. **Reference Clip Does Not Exist Yet** — COMPANY_VOICE_REF (/home/tim/company/voice/ref/company_voice_ref.wav) doesn't exist. Three clone engines (chatterbox/xtts/cosyvoice) FAIL LOUD if absent. Post-restart, voice/ops/make_reference_clip.sh mints it from Qwen3-VoiceDesign using personas.VOICE_BASE. No fabricated clip; voice is designed from text.

6. **No Silent Fallback on Down Ear** — If selected ear is down (e.g., service not running or network unreachable), transcribe() raises LOUD naming the provider + endpoint (AGENTS.md rule 4). The registry lists it as available:false, but the voice path does NOT silently flip to another ear — it fails, forcing operator awareness.

7. **Speakable Layer is Universal** — One speakable() function called by every reply→speech path (bridge /api/voice/stream, /api/voice/turn via loop, /api/tts, and any future read-back channel). Engine-aware expression mapping is centralized (ENGINE_EXPRESSION dict in speakable.py), so adding an engine's expression support is a row, not a code edit.

8. **Canonical Expression Tags Mapped Per Engine** — Brain emits <laugh>/<sigh>/… (canonical, one syntax). Speakable maps to engine-native: orpheus <tag>, chatterbox [tag], cosyvoice [laughter]/[breath]. Engines without expression (qwen3tts/xtts/kokoro) get tags stripped (never read aloud literally). Unknown engine: warns but doesn't crash (worst outcome: reads [sigh] aloud).

9. **GPU Ears Cannot Co-Reside** — 16 GB card. Granite ~4.66 GB, Parakeet ~3.05 GB, Canary ~10.06 GB (~15 GB peak). They compete with brain (~13 GB) + embeddings (~5 GB). NO auto-start of all three together. Resident-vs-on-demand-vs-swap policy is open (model layer owns it). Boot default whisper.cpp (:2022) is zero-install, on-machine; flip only after chosen ear is verified.

10. **two Parakeet Variants** — parakeet (:2031, NeMo/GPU, ~3.05 GB, heavy) for bulk/accuracy. parakeet-onnx (:2035, int8 ONNX on sherpa-onnx, ~1–1.5 GB, CPU default). The ONNX variant is leaner + supports hotword biasing (STA payoff). Different capabilities, different venvs, different registries.

11. **Channel Supervisor @ http://127.0.0.1:8771** — Assumed to be running, receives /channel-reply POST + pushes back to asking session. company_channel.mjs best-efforts POST (catches errors, logs to supervisor without crashing the session). Durable mailbox (_mail.jsonl) is the backstop.

12. **Service Registry (ops/services.json) is the Single Source** — TTS engine ports are derived from services.json at loop.py import time (lines 38–77). Missing or malformed entries fail loud at module load. Never hardcoded. Same for voice-scoped loadable services (lifecycle.py reads it for load blocks). Mirror-Registry Law: registry is truth; code projections fail loud if the registry is incomplete.

13. **Claude Ancestor PID Tracing** — company_channel.mjs traces the ancestor Claude process PID (lines 34–52) by walking /proc/stat/cmdline up the tree, looking for 'claude' basename or version pattern. Fail-safe (any /proc error → null, never throws). Used by supervisor's resolve_own_session to map sessions.

14. **Fail-Safe Channel Launch** — claude-fabric.sh wrapper (lines 19–24) falls through to plain claude if channel config missing or real binary missing. Never blocks a launch (fail-safe, not fail-closed).

---

## SUMMARY: COVERAGE + LIVE STATUS

### Channels
- **Source**: 6 files (company_channel.mjs, channel.mcp.json, package.json, profile-hook.sh, profile_test.mjs, node_modules)
- **Data**: .data/channels/ (registry ch-*.json, mailbox _mail.jsonl 6.4 MB, threads.json)
- **Port**: Dynamic (OS-assigned, registered in .data/channels/<handle>.json)
- **Live**: YES (registrations from 2026-06-28, mailbox active)

### Voice
- **TTS Engines**: 6 (Kokoro + 5 trial wrappers); 5 systemd units on-demand, 1 HTTP service (tts_service.py)
- **STT Ears**: 7 providers registered; 5 systemd units on-demand (parakeet/canary/granite/moonshine/parakeet-onnx), 1 external (whisper.cpp :2022), 1 cloud (assemblyai)
- **Venvs**: 7 + bridge (all 3.12 except cosyvoice 3.10); 5 ✅ import-verified, 1 ❌ (cosyvoice repo build fail), 1 bridge source (.voice-venv for loop)
- **Ports**: 4123–4128 (TTS), 2031–2035 (STT ears), 2022 (whisper.cpp external)
- **Live**: Kokoro :4123 (tts_service.py), whisper.cpp :2022 (external). Others: systemd on-demand, not auto-started post-boot. Post-restart verification pending (ops/README.md finish-checklist).
- **VRAM**: Unified authority via ops/cli/gpu.py + lifecycle.py. Boot default ear is moonshine (0 VRAM, CPU). GPU ears on-demand, VRAM-gated.

### Secrets
- **.secrets** (gitignored): ASSEMBLYAI_API_KEY for cloud STT. Env-override capable.
- **No hardcoded keys** anywhere.

