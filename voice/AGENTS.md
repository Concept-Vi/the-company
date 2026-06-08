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
- **STT is a swappable registry, not one provider** (`voice/stt.py`): a `STT_PROVIDERS` catalog of *ears* — `whisper.cpp` (local HTTP :2022, the **boot default**, zero-install, on-machine), the 3 GPU ears `parakeet`/`canary`/`granite` (local HTTP :2031/2032/2033, NeMo/transformers, in `voice/ears/`), and `assemblyai` (cloud). `available_stt()` is the live registry the UI/RHM reads — a probe-status read that **never raises** per ear (a down ear is `available:false` with a legible reason). The active ear is a **config slot** like the chat-brain model (`rhm_config().stt`, set via `/api/rhm-config`). Selecting a down ear **fails loud** (names the provider + endpoint) — **NO silent fallback**. Local_http dispatch is stdlib-only HTTP, so `stt.py` stays importable in the 3.14 runtime. Cloud (assemblyai) means audio leaves the machine — a deliberate, *configurable* choice, never silent.
- **The GPU ears can't all co-reside** (16 GB card): granite ~4.66 GB, parakeet ~3.05 GB, canary ~10.06 GB (~15 GB peak), and they compete with the brain (~13 GB) + embeddings (~5 GB). So they are **not auto-started together** — units exist in `voice/ops/systemd/` but the resident-vs-on-demand-vs-swap policy is an open VRAM-arbitration decision (the model-layer owns it). Before flipping the boot-default off whisper.cpp, the chosen ear needs an always-on unit (manual-start + no-fallback = broken voice after reboot).
- **ONE VRAM authority — `voice/lifecycle.py` drives the same systemd units the `company` console does, and budgets/tears-down through the shared `ops/cli/gpu.py` core** (the keeper convergence, 2026-06-06). A UI-driven load (`POST /api/voice/load` → `lifecycle.load`) starts the service's systemd user-unit (not a private `Popen`), so the console SEES it as is-active and counts its VRAM — closing the old dual-authority bug where a UI load was invisible to the budget and could OOM a second start. The budget gate now counts EVERY GPU service (brain + models + voice); unload is the cgroup `systemctl stop` (reaps vLLM's EngineCore — the orphan-safe path a bare kill can't reach). Env-parity holds: every voice unit carries `EnvironmentFile=voice.env` and no voice service declares a `load.env` override. **Verified by use** (xtts + orpheus: load → console sees it → synth → cgroup unload → card fully freed, no orphan).
- **TTS is local** (`voice/tts_service.py`, Kokoro via `kokoro-onnx`, CPU, ~no VRAM) — runs in `.voice-venv` (3.12), an HTTP service the bridge proxies. No good reason to send text out for speech; keeps the Company's voice on-machine.
- **The SPEAKABLE LAYER — ONE transform, every reply→speech path** (`voice/speakable.py`, `speakable(reply, engine)`): a brain reply reads like a TEXT model (markdown headings/`**bold**`/lists/`` `code` ``/```fences```/`[links](url)`/blockquotes/tables/bare URLs/emoji) and a TTS engine reads ALL of it aloud literally. The speakable layer cleans a reply to natural spoken prose BEFORE it reaches the engine (V-C), and is **engine-aware for expression** (V-D): a single canonical paralinguistic vocabulary (`<laugh>` `<sigh>` …) is carried in the reply engine-agnostically, then at synth MAPPED to the SELECTED engine's real syntax (orpheus `<laugh>` · chatterbox `[sigh]` · cosyvoice `[laughter]`) or **stripped** for engines without inline expression (qwen3tts/xtts/kokoro) so an unsupported tag is never read aloud as literal characters. The engine→expression map is the SINGLE SOURCE (registry-is-truth — add an engine = add a row). Applied at the pre-TTS seam in BOTH `/api/voice/stream` (clean the WHOLE reply, THEN sentence-split — never per-chunk, which would split markdown) and `/api/voice/turn` (via `loop.loop_turn`, before `speak()`), and on the generic `/api/tts` text path. The visible/returned text + trial recording stay RAW; only what hits the engine is cleaned. Stdlib-only (regex, no markdown lib) so it imports in BOTH the 3.14 runtime and the 3.12 `.voice-venv`. It is a UNIVERSAL capability — walkthrough narration, the debrief host, and any future read-back channel (phone/notification) call this one function. `tests/speakable_acceptance.py`.
- **Fail loud.** Missing key / model / service → an error surfaced, never a silent no-op. The speakable layer too: a non-string reply raises, and a non-empty reply that cleans to EMPTY (e.g. a pure code-fence) raises rather than handing the engine silence + pretending a turn spoke. An UNKNOWN engine does not hard-raise (that would make the layer a break-point for every new engine) — it strips ALL expression markup + surfaces a warning (markdown still stripped); the worst outcome it guards against is reading `[sigh]` aloud.

**Where new things go.**
- a new **STT ear** → add a row to `STT_PROVIDERS` (id, kind, url/route or lib/secret). `available_stt()`/`transcribe()` iterate the catalog — a `local_http` ear needs no dispatch edit (a GPU model just adds a `voice/ears/<name>.py` wrapper + its unit). The id IS the catalog key (the old `whisper_local`-vs-`whisper` mismatch is structurally gone). The UI/RHM reads `available_stt()` — never guesses which ears exist.
- a different **TTS voice/engine** → `COMPANY_TTS_VOICE` (Kokoro voices) or a new engine in `tts_service.py`; voices are a registry (`GET /voices`), not hardcoded in the UI.
- **inline expression support for an engine** → add a row to `ENGINE_EXPRESSION` in `voice/speakable.py` (`supports`: the canonical tags it can voice; `render`: how to write a canonical tag in that engine's native syntax). No engine row = no inline expression → all tags stripped (the safe default). A new canonical tag goes in `CANONICAL_TAGS`. Never hardcode an engine's tag syntax outside this map.

**Its seam.** The bridge ([[runtime — constitution]]): `POST /api/stt` (raw audio → `{text}`, routed to the config-selected ear `rhm_config().stt`), `POST /api/tts` (`{text,voice?}` → wav), `GET /api/voice` (status + `stt_registry` from `available_stt()` + `stt_active`). `loop.py` defaults its ear from `/api/rhm-config .stt` — one source for both the browser path and the headless loop. The [[canvas — constitution]] `listening` mode drives the mic→STT→chat→TTS→speaker loop (the push-to-talk circuit is proven headlessly; **lane-G** live mic/speaker capture is the browser half, operator-verified).

**Never.** Hardcode an API key (use `~/company/.secrets`, gitignored). Commit a key or a model file (`.secrets`, `voice/models/` are gitignored). Load STT/TTS onto the GPU without checking VRAM headroom (the LLM stack owns it).

**Boundary (honest).** The endpoints are verifiable headlessly (round-trip TTS→STT, file checks). The live **mic capture + speaker playback** is browser hardware — only the operator can confirm that loop.

## What's in here

Two-way voice — the conversational organ's ears and mouth, two halves that meet at one
seam. The **ear** is a *swappable registry* of STT providers: a single `transcribe()` that
dispatches by the active ear's `kind` — local HTTP (whisper.cpp + the 3 GPU ears), local lib,
or cloud (assemblyai) — selected by a config slot, failing loud (no fallback) when the chosen
ear is down; the audio leaves the machine only for the cloud ear, always by explicit choice.
The **mouth** is local-only **TTS** (Kokoro, CPU, ~no VRAM),
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
