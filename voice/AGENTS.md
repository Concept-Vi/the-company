# voice/ — AGENTS.md (constitution)

**What it is.** Two-way voice for the `listening` mode: **STT** (speech→text, a swappable provider) + **TTS** (text→speech, local). The conversational organ's ears and mouth.

**What it guarantees.**
- **STT is a provider** (`voice/stt.py`): default **AssemblyAI** (cloud; top accuracy/latency; key from `~/company/.secrets`), with **local faster-whisper** as a config-flag alternative (`COMPANY_STT`). Cloud STT means audio leaves the machine — a deliberate, *configurable* trade of the fully-local path; never silently. Stdlib-only for the cloud path, so it runs in the 3.14 runtime.
- **TTS is local** (`voice/tts_service.py`, Kokoro via `kokoro-onnx`, CPU, ~no VRAM) — runs in `.voice-venv` (3.12), an HTTP service the bridge proxies. No good reason to send text out for speech; keeps the Company's voice on-machine.
- **Fail loud.** Missing key / model / service → an error surfaced, never a silent no-op.

**Where new things go.**
- a new **STT provider** → `voice/stt.py`: add a `_provider(audio)->{text}` fn + a branch in `transcribe()` + a flag in `available()`. The UI/RHM reads `available()` — never guesses which providers exist.
- a different **TTS voice/engine** → `COMPANY_TTS_VOICE` (Kokoro voices) or a new engine in `tts_service.py`; voices are a registry (`GET /voices`), not hardcoded in the UI.

**Its seam.** The bridge: `POST /api/stt` (raw audio → `{text}`), `POST /api/tts` (`{text,voice?}` → wav), `GET /api/voice` (status + the provider registry). The canvas `listening` mode drives the mic→STT→chat→TTS→speaker loop.

**Never.** Hardcode an API key (use `~/company/.secrets`, gitignored). Commit a key or a model file (`.secrets`, `voice/models/` are gitignored). Load STT/TTS onto the GPU without checking VRAM headroom (the LLM stack owns it).

**Boundary (honest).** The endpoints are verifiable headlessly (round-trip TTS→STT, file checks). The live **mic capture + speaker playback** is browser hardware — only the operator can confirm that loop.
