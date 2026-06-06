---
type: constitution
module: voice/ears
aliases: ["voice/ears — constitution"]
tags: [company, constitution, voice, ears, stt]
governs: []
relates-to: ["[[voice — constitution]]", "[[voice/engines — constitution]]", "[[Company Map]]"]
status: living
---

# voice/ears/ — AGENTS.md (constitution)

**What it is.** The **speech-IN twin of `voice/engines/`**: one **HTTP STT service per GPU ear**, each a
thin wrapper around a real ASR model, **mirroring `voice/ears/_stt_service.py`'s contract exactly** (which
is itself the STT mirror of `voice/engines/_service.py`). The three ears beside the live whisper.cpp
baseline (:2022): Parakeet-TDT (:2031), Canary-Qwen (:2032), Granite-Speech (:2033).

**What it guarantees.**
- **One contract, on its own port** (the SHARED contract `voice/stt.py`'s `local_http` kind reaches by):
  `POST /inference` multipart `file=@clip.wav` → `{"text": ...}` · `GET /` (and `/health`) →
  `{"ok":true,"ear":<name>}` (liveness, never raises). Port map: whispercpp:2022 (external) ·
  parakeet:2031 · canary:2032 · granite:2033.
- **Guarded heavy imports.** NeMo / transformers is imported **inside a lazy `_engine()`**, never at module
  top — importing a wrapper (or `_stt_service.py`) never crashes; a missing lib **fails loud** with a
  precise `pip install X` message only when the model is actually loaded.
- **Fail loud at warm(), no silent fallback.** The CUDA-13 hazard surfaces at startup (`warm()` loads the
  model before serving): if the GPU path won't load, the service fails to come up → `available_stt()`
  probes the port, gets nothing, reports `available:false` + a legible detail. The registry simply shows
  the ear down — it **never** silently routes to whisper.cpp in its place (AGENTS.md rule 4).
- **Registered, never invented.** Each ear is a `STT_PROVIDERS` row in `voice/stt.py` (registry-is-truth).
  The UI/RHM lists ears from `available_stt()`; flipping the active ear is a config change
  (`rhm_config().stt`), never a code edit.

**Where new things go.**
- a **new ear** → `voice/ears/<name>.py`: supply `transcribe(audio_bytes)->{"text"}` and an optional
  `warm`/`_engine()`; call `_stt_service.serve(name, port, transcribe, warm)`. Add a `STT_PROVIDERS` row
  (`kind:"local_http"`, its url+route+field), an `ops/services.json` row, and a `REQUIREMENTS.md` entry.
- the **shared HTTP shell / audio helper** → `voice/ears/_stt_service.py` (stdlib-only; no heavy deps here).
- **per-ear install/run** → `voice/ears/REQUIREMENTS.md` (its own venv per ear — NeMo/transformers conflict).

**Its seam.** Only `voice/stt.py` reaches these — the bridge (`/api/stt`) and the loop (`voice/loop.py`)
go through `transcribe(audio, provider=...)`, which routes by the catalog row's `kind`. The ears never
touch the Suite or the store; they are pure audio→text services behind the registry.

**Never.** Import NeMo/transformers at module top (breaks the guard + the stdlib-only `_stt_service`).
Run two ears in one venv (their pins conflict — service-per-port is exactly why). Return a fabricated
transcript on failure (fail loud 500). Load an ear onto the GPU without checking VRAM headroom (the LLM
stack owns it — measured 654 MiB free 2026-06-05; the GPU ears do NOT fit until the card is freed).
Silently fall back to another ear when the selected one is down.

**Boundary (honest).** As of 2026-06-05 **none of the three has been RUN** — the GPU had only 654 MiB
free (the ~15.4 GB resident allocation is unattributable under WSL), below the smallest model's footprint,
so a live load + measured-VRAM-delta is **environment-blocked (needs_tim)**, not a code gap. The code is
import-clean and the ears are registered (probing `available:false` until their services are up). Each
wrapper's API was researched against the model card (2026-06-05) but **must be verified by running** once
the card is freed: start the service, POST a known clip, confirm the transcript, record the nvidia-smi
VRAM delta — which finally replaces the estimated footprints with measured numbers. See
`[[voice — constitution]]` for the wider organ and `[[voice/engines — constitution]]` for the mouth twin.
```
