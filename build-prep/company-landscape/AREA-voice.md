---
type: landscape
area: voice
files_surveyed: 66
surveyed_by: landscape-dragnet-agent
date: 2026-06-21
---

# Voice Subsystem — Exhaustive Landscape

## Overview

The `voice/` directory is the Company's two-way conversational organ — STT (ears) and TTS (mouth) — structured as a registry-driven, swappable, fail-loud pipeline. The subsystem is architecturally complete and well-documented. Most engines are installed and import-clean; generation-verified state varies. The big-ticket pending item is the `COMPANY_VOICE_REF` reference clip (not fabricated; needed by three of five TTS engines).

---

## File Inventory (all 66 files)

### Root — `voice/`

| File | What it is | What it does | What it holds |
|---|---|---|---|
| `AGENTS.md` | Constitution (type: constitution) | Governs entire voice module; defines contracts, invariants, registry laws, and seam with the bridge | All key laws: swappable STT registry, ONE VRAM authority, speakable layer, fail-loud rules, "where new things go" directives |
| `FROM-OPS-CLI-SESSION.md` | Inter-session coordination note | A 3-reply exchange between the ops/CLI session and the voice-stack session (2026-06-06) resolving the dual-VRAM-authority convergence | The decision log: Q1–Q5 answers, the EngineCore-cgroup-reap finding, the convergence plan, FLAG1 (litellm broken unit), FLAG2 (branch merged) |
| `lifecycle.py` | VRAM resource manager, voice-scoped | Load/unload/status/switch for all loadable GPU voice services; imports shared core (ops/cli/gpu.py, systemd.py, registry.py) | `_loadable()` reads services.json; `load()` starts systemd user-units; `unload()` uses cgroup teardown; `switch_to()` evicts prior TTS; `poll_wake()` measures load times |
| `loop.py` | Headless voice conversation loop | The three-step circuit: ear → brain → mouth; hooks for VAD/barge-in; injectable `think_fn`; `loop_turn()` | `ENGINE_PORTS` derived from services.json; `BRIDGE_URL`; `SILENCE_MS`; `listen/think/speak/loop_turn/utterance_ended/barge_in` functions |
| `personas.py` | Five-character persona registry | Holds all persona data records; `list_personas()` / `get_persona()` for UI and loop | `VOICE_BASE` (the shared Australian base); 5 personas: viv/tess/sable/pip/wren with brain text, voice_description, engine assignment, voice mappings |
| `speakable.py` | Pre-TTS text transform layer | Strips markdown from brain replies; maps canonical expression tags to engine-native syntax | `CANONICAL_TAGS`, `ENGINE_EXPRESSION` map (orpheus/chatterbox/cosyvoice), `speakable(reply, engine)` function; stdlib-only (regex, no markdown lib) |
| `stt.py` | STT ear registry and dispatcher | Probes all ears; routes `transcribe()` by kind (cloud/local_lib/local_http); VAD helpers | `STT_PROVIDERS` catalog (6 ears), `STT_ALIASES`, `STT_DEFAULT`, `available_stt()`, `transcribe()`, `transcribe_partial()`, `vad_speech_timestamps()`, `vad_has_speech()`, `_to_wav16()` |
| `tts_service.py` | Kokoro TTS HTTP service (base, CPU) | Runs Kokoro ONNX; POST /tts → wav; GET /voices | `MODEL` / `VOICES` paths at `voice/models/`; `DEFAULT_VOICE` from env; `ThreadingHTTPServer` on port 4123 |
| `trial_manifest.json` | Trial configuration | Maps personas → engines → ports → voice-arg semantics for the 5-engine trial | Engine ports, voice_arg_semantics per engine, 5 persona records with notes, COMPANY_VOICE_REF plan |

### `voice/models/` — Local model files

| File | What it is |
|---|---|
| `kokoro-v1.0.onnx` | 325 MB ONNX model for Kokoro CPU TTS |
| `voices-v1.0.bin` | 28 MB voice bank for Kokoro |

### `voice/ref/`

| File | What it is |
|---|---|
| `company_voice_ref.wav` | **EXISTS** — the shared reference clip for the clone engines (chatterbox/xtts/cosyvoice). Source unknown — it's present in the repo but the trial notes say "does NOT exist yet / no clip was fabricated." |

### `voice/ears/` — GPU STT ears

| File | What it is | What it does | What it holds |
|---|---|---|---|
| `__init__.py` | Package stub | One-line docstring pointing to AGENTS.md | Empty otherwise |
| `_stt_service.py` | Shared HTTP shell for STT ears | Handles multipart POST /inference; liveness GET /; stdlib-only | `serve(name, port, transcribe, warm)`, `_parse_multipart_file()`, `wav_bytes_to_float32()` |
| `parakeet.py` | NVIDIA Parakeet-TDT 0.6B v3 ear service | GPU STT on port 2031; NeMo; ~3 GB VRAM | `PORT=2031`; `MODEL=nvidia/parakeet-tdt-0.6b-v3`; `_engine()`; `transcribe()`; mounts `_stt_service.serve` |
| `canary.py` | NVIDIA Canary-Qwen 2.5B ear service | GPU STT on port 2032; NeMo SALM; ~6-7 GB VRAM | `PORT=2032`; `MODEL=nvidia/canary-qwen-2.5b`; SALM + ASR fallback path; explicit GPU placement |
| `granite.py` | IBM Granite Speech 4.0 1B ear service | GPU STT on port 2033; transformers; ~1.5 GB VRAM | `PORT=2033`; `MODEL=ibm-granite/granite-4.0-1b-speech`; chat-template + generate path |
| `REQUIREMENTS.md` | Install reference for GPU ears | Per-ear install commands, VRAM estimates, CUDA-13 hazards, boot-default notes | Measured VRAM: parakeet ~3 GB, canary ~6-7 GB, granite ~1.5 GB. HF cache confirmed present for all three. Current blocker: 654 MiB free (WSL GPU allocation issue) |
| `AGENTS.md` | (Does NOT exist as a separate file — only the root AGENTS.md governs) | — | — |

### `voice/engines/` — TTS engine wrappers

| File | What it is | What it does | What it holds |
|---|---|---|---|
| `__init__.py` | Package stub | Shared engine contract documentation | Port map (4123–4128); contract spec |
| `_service.py` | Shared HTTP shell for TTS engines | POST /tts; GET /voices; GET /health; stdlib-only | `serve(name, port, synth, voices, warm)`, `wav_bytes_from_array()` |
| `chatterbox.py` | Chatterbox-TTS service on :4124 | Warm-realness benchmark; ref-clip driven | `PORT=4124`; `VOICE_REF=COMPANY_VOICE_REF`; `EXAGGERATION=0.5`; `CFG_WEIGHT=0.5`; sys.path shadow fix |
| `orpheus.py` | Orpheus-TTS (vLLM) service on :4125 | LLM-backbone TTS; named voices; inline emotion cues | `PORT=4125`; reads registry config (model/max_model_len/gpu_util/attn_backend); persistent event loop fix; SIGTERM→sys.exit for EngineCore reap |
| `cosyvoice.py` | CosyVoice2 service on :4126 | Instruct+clone; description-driven voice | `PORT=4126`; git-clone repo (not pip); `COMPANY_COSYVOICE_REPO`; `_prompt_wav()` takes path (NOT tensor) — version-difference bug documented |
| `qwen3tts.py` | Qwen3-TTS VoiceDesign service on :4128 | Text-description voice design; no ref clip needed | `PORT=4128`; `MODEL_ID=Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign`; `ATTN=sdpa` (default); `generate_voice_design(text, language, instruct)` |
| `xtts.py` | XTTS-v2 (Coqui) service on :4127 | Realism ceiling; clip-driven; non-commercial | `PORT=4127`; `COQUI_TOS_AGREED=1`; `VOICE_REF=COMPANY_VOICE_REF`; `speed` arg wired (only engine that applies numeric speed) |
| `REQUIREMENTS.md` | Per-engine install reference | Exact install commands, pinned versions, known blockers | chatterbox: pip; orpheus: vLLM; cosyvoice: git clone blocker (openai-whisper build fail); xtts: coqui-tts 0.25.3 (0.27.5 broken); qwen3tts: pip, model in HF cache |
| `AGENTS.md` | (Same as root — no separate engines AGENTS.md) | — | — |

### `voice/ops/` — Operations harness

| File | What it is | What it holds / does |
|---|---|---|
| `README.md` | Ops-layer guide | Post-restart steps; per-engine status table (honest); venv locations; install-unit detail |
| `voice.env` | Shared environment file | All ports (4123–4128, 2031–2033); `COMPANY_BRIDGE_URL`; `COMPANY_VOICE_REF` path; all engine tunables; `HF_HUB_DISABLE_XET=1` |
| `voice-stack` | Bash launcher/manager | install/start/stop/restart/status/health/logs/ports/enable-boot/disable-boot; mirrors vllm-stack pattern |
| `make_reference_clip.sh` | Reference clip generator | POST qwen3tts :4128 → save as `COMPANY_VOICE_REF`; uses `personas.VOICE_BASE` description; idempotent |
| `test_ears.py` | STT round-trip test | Kokoro → transcribe → VAD; verified 2026-06-04 on CPU in both venvs |
| `verify_voice.py` | Post-restart verify harness | Checks: /api/voice reachable, Kokoro byte-identical, per-engine /api/tts synth, down-engine fail-loud, debrief quotes transcript |

### `voice/ops/systemd/` — Service units (8 files)

| File | Port | Venv | Notes |
|---|---|---|---|
| `company-voice-chatterbox.service` | 4124 | `~/.voice-venvs/chatterbox` | TimeoutStartSec=600 |
| `company-voice-cosyvoice.service` | 4126 | (cosyvoice venv) | — |
| `company-voice-orpheus.service` | 4125 | `~/.voice-venvs/orpheus` | TimeoutStartSec=900 (heaviest) |
| `company-voice-qwen3tts.service` | 4128 | `~/.voice-venvs/qwen3tts` | — |
| `company-voice-xtts.service` | 4127 | `~/.voice-venvs/xtts` | COQUI_TOS_AGREED=1 |
| `company-stt-parakeet.service` | 2031 | `~/.voice-venvs/parakeet` | VRAM note: ~3.05 GB; don't enable all 3 STT ears together |
| `company-stt-canary.service` | 2032 | `~/.voice-venvs/canary` | Heaviest STT ear (~6-7 GB) |
| `company-stt-granite.service` | 2033 | `~/.voice-venvs/granite` | transformers; most likely to load clean |

All units: `EnvironmentFile=%h/company/voice/ops/voice.env`; `WorkingDirectory=/home/tim/company`; `Restart=on-failure`; `WantedBy=default.target`.

---

## The Pipeline

### Audio In → STT → Cognition → TTS → Audio Out

```
[Browser mic / push-to-talk]
        │ audio bytes (webm/mp4/wav — browser MediaRecorder)
        ▼
  POST /api/stt  OR  /api/voice/stream  OR  /api/voice/turn
        │
  voice/stt._to_wav16()   ← ffmpeg: normalize to 16kHz mono WAV
        │
  voice/stt.transcribe(audio, provider=<selected-ear>)
        │  dispatch by kind:
        ├─ whispercpp    → HTTP POST :2022/v1/audio/transcriptions  (boot default; zero-install)
        ├─ whisper_local → in-process faster_whisper (CPU int8 / GPU int8_float16)
        ├─ parakeet      → HTTP POST :2031/inference  (GPU NeMo; ~3 GB)
        ├─ canary        → HTTP POST :2032/inference  (GPU NeMo SALM; ~6-7 GB)
        ├─ granite       → HTTP POST :2033/inference  (GPU transformers; ~1.5 GB)
        └─ assemblyai    → cloud API (key from .secrets; audio leaves machine)
        │
  {text, provider}
        │
  POST /api/chat  (the ONE Suite brain — HTTP to bridge :8770)
  OR   think_fn(text) → injected in-process when loop runs inside bridge
        │
  {reply, action, mode}
        │
  voice/speakable.speakable(reply, engine)
  ├─ _strip_markdown()       ← strip headings/**bold**/`code`/fences/links/URLs/emoji
  ├─ _apply_expression()     ← map <canonical-tag> → engine-native syntax OR drop
  └─ _normalise_whitespace_punct()
        │
  cleaned_spoken_text
        │
  voice/loop.speak(cleaned_text, engine, voice=voice_arg) OR bridge._stream_parts()
        │  POST <engine-url>/tts {text, voice?, speed?}
        ├─ kokoro       → :4123  (CPU ONNX; always up; Kokoro v1.0 models on disk)
        ├─ chatterbox   → :4124  (GPU; ref-clip driven; EXAGGERATION knob)
        ├─ orpheus      → :4125  (GPU vLLM; named voices + inline emotion cues)
        ├─ cosyvoice    → :4126  (GPU; instruct+clone; description-driven)
        ├─ xtts         → :4127  (GPU; ref-clip; non-commercial; only engine with numeric speed)
        └─ qwen3tts     → :4128  (GPU; VoiceDesign; description-only; no ref clip)
        │
  wav bytes
        │
[Browser speaker playback]
```

### Streaming variant (`/api/voice/stream`)

The bridge's `_voice_stream()` runs a streaming path: brain replies in parts via `SUITE.chat_parts()`, each part is cleaned via `speakable`, sentence-split, and spoken part-by-part — overlapping brain thinking with TTS synthesis (reduces latency vs whole-reply-then-speak).

### Turn variant (`/api/voice/turn`)

The bridge's `_voice_turn()` calls `voice/loop.loop_turn()` with an injected `think_fn` = the in-process Suite.chat (not an HTTP self-call back to /api/chat). One turn: audio → transcript → reply → wav.

---

## Engine Catalog

### TTS Engines

| Engine | Port | VRAM | Voice Input Type | Speed | Expression | Status |
|---|---|---|---|---|---|---|
| kokoro | 4123 | ~0 (CPU ONNX) | named voice (af_heart default) | yes (numeric) | none (strip all) | **ALWAYS UP** — models on disk, no GPU |
| chatterbox | 4124 | ~2-4 GB (est) | ref-clip path | no (pace from clip) | [laugh] [sigh] [gasp] [cough] | import-clean; needs COMPANY_VOICE_REF + GPU |
| orpheus | 4125 | ~10.4 GB (measured) | named voice (tara/leah/jess/leo/dan/mia/zac/zoe) | no (LLM token stream) | `<laugh>` `<chuckle>` `<sigh>` `<cough>` `<sniffle>` `<groan>` `<yawn>` `<gasp>` | import-clean; generation verified 2026-06-06 |
| cosyvoice | 4126 | ~5 GB (est) | description text + ref-clip path | no (encode in description) | [laughter] [breath] | **BLOCKED** — repo deps incomplete (openai-whisper build fail) |
| xtts | 4127 | ~2 GB (est) | ref-clip path | yes (numeric, 1.0=natural) | none | import-clean; needs COMPANY_VOICE_REF + GPU; NON-COMMERCIAL |
| qwen3tts | 4128 | ~5 GB (est) | description text (instruct) | no | none | import-clean; model in HF cache; TRIAL STARTER |

### STT Ears

| Ear | Port | Kind | VRAM | Notes |
|---|---|---|---|---|
| whispercpp | 2022 | local_http | ~0 (CPU) | **BOOT DEFAULT**; OpenAI-compat route; zero-install |
| whisper_local | — | local_lib | ~0 (CPU int8) / GPU | in-process faster-whisper; verified round-trip 2026-06-04 |
| parakeet | 2031 | local_http | ~3 GB | NVIDIA CC-BY-4.0; ~2000x RT; intended next default; HF cached |
| canary | 2032 | local_http | ~6-7 GB | NVIDIA CC-BY-4.0; LLM-ASR (SALM); heaviest ear |
| granite | 2033 | local_http | ~1.5 GB | IBM Apache-2.0; transformers; most likely clean load; HF cached |
| assemblyai | — | cloud | n/a | Key from .secrets; audio leaves machine; must be deliberate choice |

---

## Config Knobs (voice.env + rhm_config slots)

### voice.env knobs

```
COMPANY_KOKORO_PORT=4123
COMPANY_CHATTERBOX_PORT=4124  ...  COMPANY_QWEN3TTS_PORT=4128
COMPANY_BRIDGE_URL=http://127.0.0.1:8770
COMPANY_VOICE_REF=/home/tim/company/voice/ref/company_voice_ref.wav
COMPANY_TTS_DEVICE=cuda
COMPANY_CHATTERBOX_EXAGGERATION=0.5 / CFG=0.5
COMPANY_ORPHEUS_MODEL=canopylabs/orpheus-3b-0.1-ft
COMPANY_ORPHEUS_VOICE=tara / MAXLEN=8192 / GPU_UTIL=0.6 / EAGER=0 / ATTN=FLASH_ATTN
COMPANY_COSYVOICE_REPO=/home/tim/CosyVoice / DIR=...pretrained_models/CosyVoice2-0.5B
CUDA_HOME=... (cosyvoice deepspeed requirement)
COQUI_TOS_AGREED=1 (xtts)
COMPANY_QWEN3TTS_MODEL=Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign / DEVICE=cuda:0 / ATTN=sdpa / LANG=English
COMPANY_WHISPER_MODEL=large-v3-turbo / DEVICE=cuda / COMPUTE=int8_float16 / LANG=en
COMPANY_VOICE_VENVS=/home/tim/.voice-venvs
COMPANY_LOOP_VENV=/home/tim/company/.voice-venv
HF_HUB_DISABLE_XET=1
```

### rhm_config slots (set via POST /api/rhm-config)

| Slot | Default | Meaning |
|---|---|---|
| `stt` | STT_DEFAULT (`whispercpp`) | Active ear selection — the one source for both bridge + loop |
| `tts_engine` | `""` | Override persona's default engine (G4.2) |
| `tts_voice` | `""` | Override persona's default voice arg |
| `voice_enabled` | `"on"` | Per-mode voice gate (G4.4): `"off"` → hear+think but no TTS |
| `voice_path` | `"pipeline"` | Swappable path slot: `"pipeline"` (the live path) or `"s2s"` (stub) |
| `persona` | — | Sets brain sketch via Suite.set_rhm_config |
| `voice_input_mode` | — | Undocumented slot present in set_rhm_config allowlist |

---

## Bridge Routes (all voice-related)

| Route | Method | Handler | What |
|---|---|---|---|
| `/api/voice` | GET | `do_GET` | Status: STT registry, stt_active, per-engine TTS availability + voices, voice_enabled |
| `/api/stt` | POST | `do_POST` | Transcribe raw audio → {text}; routes via stt.transcribe to the configured ear |
| `/api/tts` | POST | `do_POST` | Text → wav; optional `engine` param routes to engine-port; no engine = Kokoro; speakable applied |
| `/api/voice/stream` | POST | `_voice_stream` (SSE) | Streaming turn: audio → transcript → brain parts → per-part TTS → streamed wav |
| `/api/voice/turn` | POST | `_voice_turn` | One-shot turn: audio → transcript → brain → TTS → wav; injectable think_fn |
| `/api/voice/load` | POST | `do_POST` | Boot a voice service (ear OR engine) via lifecycle.load(); returns warming/up |
| `/api/voice/ear/load` | POST | alias of above | Back-compat alias |
| `/api/voice/services` | GET | `do_GET` | Lifecycle status: per-service up/warming/down + VRAM; also polls wake-times |
| `/api/voice/ears` | GET | alias of above | Back-compat alias |
| `/api/voice/switch` | POST | `do_POST` | Persona switch: set active persona + auto-load its TTS engine via lifecycle.switch_to |
| `/api/voice/stt-partial` | POST | `do_POST` | Tier-2 streaming STT: partial transcript of growing audio buffer |
| `/api/voice/finished-thought` | POST | `do_POST` | Semantic endpoint judge (brain-side) — is this utterance a finished thought? |
| `/api/voice/log` | POST | `do_POST` | Client-side voice trace log (diagnostics) |
| `/api/voice/engine-knobs` | GET | `do_GET` | Per-TTS-engine knob catalog |
| `/api/voice/paths` | GET | `do_GET` | Swappable voice-path registry (pipeline vs s2s) |
| `/api/personas` | GET | `do_GET` | Five-cast registry the picker UI reads (from personas.list_personas()) |

---

## VRAM Architecture

**ONE VRAM AUTHORITY**: `ops/cli/gpu.py` (the shared resource manager core). `voice/lifecycle.py` imports it. No dual-authority race (that was the pre-2026-06-06 bug — fixed and verified).

**Budget gate**: `lifecycle.load()` calls `gpu.check_fit(reg, [service_id])` which counts EVERY GPU service (brain + models + voice) — not just resident voices. A voice load that won't fit on the card names what to unload.

**Teardown**: `gpu.teardown(svc)` → `systemctl stop` → cgroup kills the entire unit tree including vLLM's EngineCore (which a bare SIGTERM/SIGKILL cannot reach — upstream #19849). Verified: orpheus unload freed 11.5 GB → 0.95 GB, zero orphan.

**Co-residency constraint**: 16 GB card. Cannot hold all five engines at once. `lifecycle.switch_to()` evicts the previous TTS engine before loading a new one.

Approximate VRAM picture:
- Chat brain: ~13 GB
- Embeddings: ~5 GB
- Orpheus: ~10.4 GB (measured)
- Canary: ~6-7 GB
- Parakeet: ~3 GB
- Granite: ~1.5 GB
- Qwen3TTS: ~5 GB (est)
- CosyVoice: ~5 GB (est)
- Chatterbox: ~2-4 GB (est)
- XTTS: ~2 GB (est)
- Kokoro: ~0 (CPU)

→ The brain + ONE GPU TTS engine is the practical co-residency limit for most engines. Orpheus cannot co-reside with a fully-loaded brain (10.4 + 13 = 23.4 GB).

---

## Venv Architecture

| Venv | Python | Contents | Used by |
|---|---|---|---|
| `~/company/.voice-venv` | 3.12 | kokoro-onnx, faster-whisper, silero-vad, soundfile, numpy | Loop in-process STT; Kokoro TTS service |
| `~/.voice-venvs/ears` | 3.12 | faster-whisper, silero-vad, soundfile, numpy, torch (CPU) | Dedicated ears venv |
| `~/.voice-venvs/chatterbox` | 3.12 | chatterbox-tts, soundfile, torch+CUDA | Chatterbox engine |
| `~/.voice-venvs/orpheus` | 3.12 | orpheus-speech, vLLM 0.22.0, torch 2.11.0, snac, flash-attn | Orpheus engine |
| `~/.voice-venvs/cosyvoice` | 3.10 | incomplete — repo build blocked | CosyVoice engine |
| `~/.voice-venvs/xtts` | 3.12 | coqui-tts 0.25.3, transformers<4.50, soundfile, torch | XTTS engine |
| `~/.voice-venvs/qwen3tts` | 3.12 | qwen-tts, soundfile, torch | Qwen3TTS engine |
| `~/.voice-venvs/parakeet` | 3.12 | nemo_toolkit[asr], soundfile | Parakeet ear |
| `~/.voice-venvs/canary` | 3.12 | nemo_toolkit[asr], soundfile | Canary ear |
| `~/.voice-venvs/granite` | 3.12 | transformers, peft, soundfile, torchaudio, torch | Granite ear |

**3.14 bridge cannot import heavy libs** (faster-whisper has no 3.14 wheel). Bridge imports only `voice/stt.py`, `voice/lifecycle.py`, `voice/loop.py`, `voice/speakable.py`, `voice/personas.py` — all stdlib-only modules. Heavy imports are lazy-guarded behind `_engine()` calls that only fire inside the engine's own venv.

---

## Personas (Five Trial Characters)

| ID | Name | Shading | Engine | Voice Arg | Ref Clip Needed |
|---|---|---|---|---|---|
| viv | Viv | composed & dry | chatterbox | None → COMPANY_VOICE_REF | YES |
| tess | Tess | warm & playful | cosyvoice | persona.voice_description + COMPANY_VOICE_REF | YES |
| sable | Sable | cool & enigmatic | qwen3tts | persona.voice_description | NO — TRIAL STARTER |
| pip | Pip | bright & a bit wacky | orpheus | "tara" (named voice) | NO |
| wren | Wren | curious co-explorer | xtts | None → COMPANY_VOICE_REF | YES |

All five share `VOICE_BASE` (refined, mature Australian woman). `_voice_arg_for(persona, engine)` maps any persona to any engine (any persona × any engine — Tim's requirement 2026-06-07).

---

## Wired vs Stubbed

### WIRED (code complete, some verified by execution)

- STT registry (all 6 ears registered, dispatching by kind, fail-loud on down ear) — **WIRED + VERIFIED** (whisper_local round-trip 2026-06-04)
- `_to_wav16()` webm/mp4 → 16kHz WAV normalization — **WIRED + VERIFIED** (root-caused silent empty transcript bug 2026-06-06)
- `available_stt()` / `available_stt_registry` — **WIRED** (probes each ear, never raises)
- Kokoro TTS service on :4123 — **WIRED + RUNNING** (models on disk)
- speakable layer — **WIRED** (all markdown strip + expression map); `tests/speakable_acceptance.py` exists
- `lifecycle.py` with shared VRAM core — **WIRED + VERIFIED** (xtts + orpheus load/unload cycle 2026-06-06)
- `loop.py` conversation circuit — **WIRED** (headless; browser mic/speaker = lane G)
- All 5 TTS engine wrappers (orpheus/chatterbox/cosyvoice/xtts/qwen3tts) — **WIRED**; orpheus generation **VERIFIED** (first synth 2026-06-06 after 3-layer crash fix)
- All 3 GPU STT ear wrappers — **WIRED**; parakeet load **VERIFIED** by `company up stt-parakeet` (2026-06-06, ~5.2 GB)
- Systemd units for all 8 voice services — **INSTALLED** (cp + daemon-reload done 2026-06-06)
- ENGINE_PORTS derived from services.json at import time — **WIRED** (Mirror-Registry Law enforced)
- Bridge routes: /api/voice, /api/stt, /api/tts, /api/voice/stream, /api/voice/turn, /api/voice/load, /api/voice/switch, /api/voice/services — **WIRED**
- Per-mode voice gate (voice_enabled) — **WIRED** (G4.4 in loop_turn; SUITE.voice_enabled() in bridge)
- Engine override slots (tts_engine/tts_voice in rhm_config) — **WIRED** (G4.2)
- `_stream_parts()` streaming brain→TTS — **WIRED** (concurrent cognition G6 integration)
- `boot-on-demand` (auto-load engine if down when voice_enabled) — **WIRED** in bridge._voice_stream()
- `switch_to()` persona switch with VRAM eviction — **WIRED**
- `poll_wake()` load-time telemetry — **WIRED**

### STUBBED / INCOMPLETE

- **cosyvoice engine**: repo deps incomplete (openai-whisper==20231117 build fails); `from cosyvoice.cli.cosyvoice import AutoModel` does NOT import. **The only engine not import-clean.**
- **COMPANY_VOICE_REF**: File EXISTS at `voice/ref/company_voice_ref.wav` (present on disk) but the trial notes say "no clip was fabricated" — origin unclear. The `make_reference_clip.sh` script exists to generate it from qwen3tts. Should be verified/re-generated post-restart using the script.
- **GPU STT ears load**: Cannot currently verify because only 654 MiB free on the card (WSL-side unattributed allocation — parakeet load verified once via `company up stt-parakeet` on 2026-06-06 but card state varies)
- **STT whisper_local status in bridge**: The bridge runs Python 3.14; faster-whisper has no 3.14 wheel → `/api/voice` reports `whisper_local: false` even though the 3.12 loop transcribes correctly. The function works; the status registry is cosmetically wrong.
- **Live mic/speaker capture** (lane G): browser hardware — only the operator can confirm. The headless circuit is proven; the browser push-to-talk loop is operator-verified by assertion.
- **s2s voice_path**: The `voice_path` slot accepts `"s2s"` but it's a fail-loud stub ("no S2S runner/model exists yet") — no s2s model is present.
- **Debrief host narration** via speakable: The architecture says speakable is the universal transform for all read-back channels including the debrief host — but verify_voice.py's check 3.7 requires a real session to test it.
- **`voice_input_mode` slot**: Present in set_rhm_config allowlist but not documented in AGENTS.md or rhm_config defaults — unclear what it does.
- **cosyvoice `_prompt_wav()` bug**: Documented in cosyvoice.py — inference_instruct2 has a soundfile/tensor API mismatch in the installed version vs the documented example. Engine fails warm pre-fetch synth but stays up for debugging.

---

## Notable Gaps / Surprises

1. **COMPANY_VOICE_REF exists on disk** (`voice/ref/company_voice_ref.wav`) despite the trial notes saying it was not fabricated. Its origin should be verified — if it was generated correctly from qwen3tts, three engines (viv/tess/wren) are unblocked. If it's a placeholder, it would silently produce wrong audio.

2. **No `AGENTS.md` in `voice/ears/`**: The ears REQUIREMENTS.md references AGENTS.md but `voice/ears/` has no AGENTS.md file. The root `voice/AGENTS.md` governs by extension.

3. **ENGINE_PORTS in bridge.py is HARDCODED** (line 240-241: `ENGINE_PORTS = {"chatterbox": 4124, ...}`). The `voice/loop.py` MODULE correctly derives ENGINE_PORTS from services.json. But **bridge.py has its own hardcoded map** — a violation of the Mirror-Registry Law documented in loop.py's docstring (`F-FIX-11`). This is a live inconsistency gap: if services.json port changes, loop.py picks it up, bridge.py does not.

4. **cosyvoice is the only install blocker**. The other four GPU engines (chatterbox/orpheus/xtts/qwen3tts) are all import-clean. Fixing cosyvoice requires `pip install -r ~/CosyVoice/requirements.txt` with a buildable openai-whisper (drop ==20231117 pin or `--no-build-isolation`).

5. **Orpheus persistent event loop fix** — this was a real bug found by use: orpheus_tts's `generate_tokens_sync` runs `asyncio.run()` in a new thread per call, closing the engine's background loop after the first synth, causing all subsequent requests to hang. The fix (one persistent loop in a daemon thread) is non-obvious and required code surgery on top of the library.

6. **Chatterbox sys.path shadow fix** — when chatterbox.py is launched as a file, the script's own directory (`voice/engines/`) lands on sys.path[0] ahead of site-packages, causing `from chatterbox.tts import ChatterboxTTS` to resolve to the script file itself (no `.tts` submodule) → ImportError. The fix removes `_self_dir` from sys.path at startup. Without this fix `company up tts-chatterbox` silently fails with a misleading "not installed" message.

7. **Silero VAD is a stream helper in stt.py but installed in voice venv** — VAD is consumed by `loop.utterance_ended` and `loop.barge_in`, but the functions `vad_speech_timestamps` / `vad_has_speech` live in `voice/stt.py`. This is correct by design (stdlib-only stt.py stays importable; heavy VAD import is lazy-guarded).

8. **The `voice/ears/AGENTS.md` referenced in REQUIREMENTS.md does NOT exist** as a file. REQUIREMENTS.md says "see AGENTS.md" — it means the root `voice/AGENTS.md`.

9. **litellm-proxy.service is broken** (from FLAG1 in FROM-OPS-CLI-SESSION.md): its WorkingDirectory points at a non-existent `%h/claude-gateway` dir and port disagrees with registry (4000 vs 4100). Not a voice issue per se, but noted since it's in ops/systemd.

10. **stt-parakeet/canary/granite manage type was flipped to `user-unit`** by the ops/CLI session (2026-06-06). The services.json entries should have `manage.type: "user-unit"` for these ears now. Verified by the ops session: `company up stt-parakeet` ran via the unit in 24s, VRAM measured ~5.2 GB.

---

## Cross-References

- **`ops/services.json`**: Single source for ENGINE_PORTS (voice/loop.py reads it); VRAM budgets; unit names; config blocks for orpheus/cosyvoice/qwen3tts
- **`ops/cli/gpu.py`**: Shared VRAM authority imported by lifecycle.py
- **`ops/cli/systemd.py`**: systemctl --user wrapper used by lifecycle.load/unload
- **`ops/cli/registry.py`**: Service registry loaded by lifecycle.load for budget gate
- **`runtime/bridge.py`**: All bridge-side voice routes; hardcoded ENGINE_PORTS (gap vs services.json)
- **`runtime/suite.py`**: `rhm_config()`, `voice_enabled()`, `set_rhm_config()`, `available_stt()`, `voice_engine_knobs()`, `voice_paths()`
- **`tests/speakable_acceptance.py`**: Acceptance tests for the speakable layer
- **`~/company/.secrets`**: AssemblyAI key (gitignored; KEY=VALUE format)
- **`~/.cache/huggingface/hub`**: HF model cache — parakeet, canary, granite, qwen3tts all present
