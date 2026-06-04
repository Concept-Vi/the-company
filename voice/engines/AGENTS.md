---
type: constitution
module: voice/engines
aliases: ["voice/engines — constitution"]
tags: [company, constitution, voice, engines]
governs: []
relates-to: ["[[voice — constitution]]", "[[Company Map]]"]
status: living
---

# voice/engines/ — AGENTS.md (constitution)

**What it is.** One **HTTP TTS service per voice** for the voice trial — each a thin wrapper around a real
TTS model, **mirroring `voice/tts_service.py`'s contract exactly**. The five trial mouths beside the
existing Kokoro baseline: Chatterbox, Orpheus, CosyVoice2, XTTS-v2, Qwen3-TTS VoiceDesign.

**What it guarantees.**
- **One contract, on its own port** (the SHARED contract the runtime-backend builder routes by `engine`):
  `POST /tts {text, voice?, speed?} → audio/wav` · `GET /voices → {voices, default}` · `GET /health`.
  Port map: kokoro:4123 · chatterbox:4124 · orpheus:4125 · cosyvoice:4126 · xtts:4127 · qwen3tts:4128.
- **Guarded heavy imports.** The model library is imported **inside a lazy `_engine()`**, never at module
  top — importing a wrapper never crashes; a missing lib **fails loud** with a precise `pip install X`
  message only when `/tts` is actually called.
- **Fail loud, never a silent empty wav.** No audio produced → a 500 with the reason, never 44 bytes of
  silence. No reference clip where one is required → a 500, never a wrong default speaker.
- **No fabricated voice data.** The refined-Australian reference clip does not exist yet; the clip-driven
  engines read `COMPANY_VOICE_REF` and fail loud if it's absent. Nothing here invents a clip.

**Where new things go.**
- a **new engine** → `voice/engines/<name>.py`: supply `synth(text, voice, speed)->wav`, `voices()->(list,default)`,
  an optional `warm`/`_engine()`; call `_service.serve(name, port, synth, voices, warm)`. Add it to the
  port map (`loop.ENGINE_PORTS`) and to `REQUIREMENTS.md`. Heavy imports lazy + guarded.
- the **shared HTTP shell / wav helper** → `voice/engines/_service.py` (stdlib-only; don't add heavy deps here).
- **per-engine install/run** → `voice/engines/REQUIREMENTS.md` (its own venv per engine — their deps conflict).

**Its seam.** The bridge proxies `/api/tts`; the voice loop (`voice/loop.py`) selects an engine by name
(`engine_url`) and posts `/tts`. `voice/personas.py` decides what the per-request `voice` arg means for
each engine (clip path / voice description / voice name) — see `loop._voice_arg_for`.

**Never.** Import a model library at module top (breaks the guard). Run two engines in one venv (their pins
conflict — that's why it's service-per-port). Return silence on failure. Use XTTS in a commercial path
(its weights are **non-commercial** — trial-by-ear only). Fabricate a reference clip.

**Boundary (honest).** None of these have been RUN — the models were still downloading and the GPU/RAM
restart was pending when these were written. Every wrapper's API was researched against the model's HF/GitHub
repo (2026-06-03) but **must be verified by running post-restart**: load each, hit `/tts`, confirm an audible
wav in the right voice. See `[[voice — constitution]]` for the wider organ.
