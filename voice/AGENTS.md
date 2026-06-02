---
type: constitution
module: voice
aliases: ["voice — constitution"]
tags: [company, constitution, voice]
governs: []
relates-to: ["[[Company Map]]", "[[runtime — constitution]]"]
status: living
---

# voice/ — AGENTS.md (constitution)

**What it is.** Two-way voice for the `listening` mode: **STT** (speech→text, a swappable provider) + **TTS** (text→speech, local). The conversational organ's ears and mouth.

**What it guarantees.**
- **STT is a provider** (`voice/stt.py`): default **AssemblyAI** (cloud; top accuracy/latency; key from `~/company/.secrets`), with **local faster-whisper** as a config-flag alternative (`COMPANY_STT`). Cloud STT means audio leaves the machine — a deliberate, *configurable* trade of the fully-local path; never silently. Stdlib-only for the cloud path, so it runs in the 3.14 runtime.
- **TTS is local** (`voice/tts_service.py`, Kokoro via `kokoro-onnx`, CPU, ~no VRAM) — runs in `.voice-venv` (3.12), an HTTP service the bridge proxies. No good reason to send text out for speech; keeps the Company's voice on-machine.
- **Fail loud.** Missing key / model / service → an error surfaced, never a silent no-op.

**Where new things go.**
- a new **STT provider** → `voice/stt.py`: add a `_provider(audio)->{text}` fn + a branch in `transcribe()` + a flag in `available()`. The UI/RHM reads `available()` — never guesses which providers exist.
- a different **TTS voice/engine** → `COMPANY_TTS_VOICE` (Kokoro voices) or a new engine in `tts_service.py`; voices are a registry (`GET /voices`), not hardcoded in the UI.

**Its seam.** The bridge ([[runtime — constitution]]): `POST /api/stt` (raw audio → `{text}`), `POST /api/tts` (`{text,voice?}` → wav), `GET /api/voice` (status + the provider registry). The [[canvas — constitution]] `listening` mode drives the mic→STT→chat→TTS→speaker loop.

**Never.** Hardcode an API key (use `~/company/.secrets`, gitignored). Commit a key or a model file (`.secrets`, `voice/models/` are gitignored). Load STT/TTS onto the GPU without checking VRAM headroom (the LLM stack owns it).

**Boundary (honest).** The endpoints are verifiable headlessly (round-trip TTS→STT, file checks). The live **mic capture + speaker playback** is browser hardware — only the operator can confirm that loop.

## What's in here

Two-way voice — the conversational organ's ears and mouth, two halves that meet at one
seam. The **ear** is a *swappable* STT provider: a single `transcribe()` whose default
reaches **AssemblyAI** in the cloud (top accuracy/latency) and whose config flag swaps in a
**local faster-whisper** path — same shape, the audio either leaves the machine or doesn't,
always by an explicit choice. The **mouth** is local-only **TTS** (Kokoro, CPU, ~no VRAM),
which lives in its own `.voice-venv` (Python 3.12, isolated from the 3.14 runtime) and runs
as a small HTTP service on its own port. Provider-set and voice-set are each a *registry the
UI reads*, never a hardcoded list — so adding a provider or a voice is a drop-in, not a
frontend edit. Where this organ sits in the whole body is the picture in [[Company Map]].

## Relates to

- **Reached via** [[runtime — constitution]]'s bridge — the `/api/stt`, `/api/tts`, and
  `/api/voice` endpoints are the only door in; they **proxy to the voice service** rather
  than embed it, so the local TTS process and its venv stay isolated from the runtime.
- **Provider keys live in `.secrets`** (gitignored) — the cloud STT path reads its key from
  there; nothing voice-related is ever committed (keys, `voice/models/`).

## Read next
[[Company Map]] (where this organ sits in the whole) · [[runtime — constitution]] (the bridge that fronts these endpoints) · [[Concepts and Principles]] (the language this constitution speaks).
