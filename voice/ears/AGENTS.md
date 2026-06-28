---
type: constitution
register: prescriptive
module: voice/ears
aliases: ["voice/ears — constitution"]
tags: [company, constitution, voice, ears, stt]
governs: []
relates-to: ["[[voice — constitution]]", "[[voice/engines — constitution]]", "[[Company Map]]"]
status: living
---

# voice/ears/ — AGENTS.md (constitution)

**What it is.** The **speech-IN twin of `voice/engines/`**: one **HTTP STT service per ear**, each a
thin wrapper around a real ASR model, **mirroring `voice/ears/_stt_service.py`'s contract exactly** (which
is itself the STT mirror of `voice/engines/_service.py`). Two lanes:
- **The heavy GPU/accuracy ears** beside the whisper.cpp baseline (:2022): Parakeet-TDT NeMo (:2031),
  Canary-Qwen (:2032), Granite-Speech (:2033) — for bulk/accuracy/translation jobs.
- **The compact realtime ears (lane 5, 2026-06-28):** Moonshine (:2034) and Parakeet-TDT int8-ONNX
  (:2035) — ONNX-runtime, no torch/NeMo, sub-1–1.5 GB, CPU by default (0 VRAM), built for live
  conversation + Speech-To-Action. These are the **interaction-loadout** ears (see the `interaction`
  combo class + its `interaction-parakeet` variant).

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

## The compact realtime ears — capability writeups (lane 5)

Both run on the **ONNX-runtime** (no torch, no NeMo) in their own venvs (`~/.voice-venvs/moonshine`,
`~/.voice-venvs/parakeet-onnx`), CPU by default → **0 VRAM**, so they co-reside with the brain + embedder
in the interaction loadout. Measured on this box (RTX 4080 / i7-12700KF), verified by use 2026-06-28.

**`moonshine` (:2034) — the leanest realtime ear.**
- *What:* Moonshine (useful-sensors), `MoonshineOnnxModel`. Model via `COMPANY_MOONSHINE_MODEL` (default
  `moonshine/base`; `tiny` is smaller/weaker; a v2-medium ≈Whisper-large checkpoint is a drop-in env swap).
- *Good at / qualities:* lowest latency + smallest footprint (<1 GB). **Doesn't pad short clips** to a fixed
  window the way Whisper does → short commands transcribe in a fraction of the time (ideal for STA). Quality
  ~6.6% WER (base/medium), ≈ Whisper-large on English. English-focused.
- *Measured:* CPU ~9× realtime (a 34 s clip in 3.7 s; a ~4 s turn in ~0.34 s), ~0 GPU.
- *Tuning dials:* a built-in **IntentRecognizer** (maps spoken commands → registered intents by meaning,
  with a 0–1 confidence — a native speech→action layer); `vad_threshold`, `vad_max_segment_duration`,
  `max_tokens_per_second` (hallucination guard). Vocabulary biasing is weak (needs fine-tune).
- *Use:* the **default interaction-loadout ear** — live conversation + a fixed core of STA commands.

**`parakeet-onnx` (:2035) — the accurate, multilingual, tunable realtime ear.**
- *What:* NVIDIA Parakeet-TDT 0.6B v3 exported to **int8 ONNX**, run on **sherpa-onnx** (`OfflineRecognizer`
  transducer). Model dir `voice/models/parakeet-tdt-v3-int8/` (~670 MB). `COMPANY_PARAKEET_ONNX_DEVICE`
  (default cpu; `cuda` for the GPU provider), `_THREADS`, `_HOTWORDS` (future).
- *Good at / qualities:* keeps full-Parakeet quality (~6.3% WER) + **25 European languages** (auto-detect)
  at ~1–1.5 GB instead of the NeMo build's ~5 GB. **Supports hotword / context biasing** — boost UI terms,
  filter names, command words (up to thousands of phrases) — the strongest customization story for STA.
- *Tuning dials:* context-biasing / hotword lists (the dictionary mechanism), greedy/beam decode, threads,
  device. The accurate-multilingual sibling of Moonshine; the `interaction-parakeet` variant ear.
- *Distinct from* `parakeet` (:2031), the heavy NeMo/GPU build kept for bulk/GPU work.

**Its seam.** Only `voice/stt.py` reaches these — the bridge (`/api/stt`) and the loop (`voice/loop.py`)
go through `transcribe(audio, provider=...)`, which routes by the catalog row's `kind`. The ears never
touch the Suite or the store; they are pure audio→text services behind the registry.

**Never.** Import NeMo/transformers at module top (breaks the guard + the stdlib-only `_stt_service`).
Run two ears in one venv (their pins conflict — service-per-port is exactly why). Return a fabricated
transcript on failure (fail loud 500). Load an ear onto the GPU without checking VRAM headroom (the LLM
stack owns it — measured 654 MiB free 2026-06-05; the GPU ears do NOT fit until the card is freed).
Silently fall back to another ear when the selected one is down.

**Boundary (honest).** The **compact realtime ears (lane 5) ARE run + verified by use** (2026-06-28):
`moonshine` and `parakeet-onnx` both start via `company up`, serve `/inference` with correct transcripts,
on CPU at 0 VRAM — footprints/latencies above are measured, not estimated. The **three heavy GPU ears
(:2031–2033) remain run-once/estimated** — Granite was loaded on CPU this session (~9.3 GB RAM, fp32);
Parakeet/Canary on GPU still want a measured VRAM-delta when the card is free. The lane-5 ears are the
ones wired into the live `interaction` loadout. See
`[[voice — constitution]]` for the wider organ and `[[voice/engines — constitution]]` for the mouth twin.
```
