---
type: reference
module: voice/ears
aliases: ["voice ears — install reference"]
tags: [company, voice, stt, ears, install]
status: living
---

# voice/ears — install reference (per-ear, exact)

The three GPU STT ears — the speech-in twins of `voice/engines/`'s TTS engines. Each is **its own HTTP
service on its own port, run from its own venv** (NeMo and transformers deps conflict, and neither may
pollute the 3.14 runtime or the 3.12 voice-venv). They mount `voice/ears/_stt_service.py` (the stdlib
HTTP shell) and expose the SAME contract whisper.cpp's catalog row uses, so `voice/stt.py`'s `local_http`
kind reaches all of them with one transport.

The bridge / loop reach them only through `voice/stt.py` (the registry) — adding/flipping an ear is a
`STT_PROVIDERS` row + a config change, never a code edit.

## Shared contract (all three, the STT twin of the TTS engine contract)
- `POST /inference` multipart/form-data, field `file=@clip.wav` → `{"text": "..."}`
- `GET /` (and `/health`) → `{"ok": true, "ear": <name>}` (liveness; never raises)
- fail-loud 500 `{"error": "<Type>: <msg>"}` on any error.

## The VRAM ceiling (measured 2026-06-05 — the gating fact)
`nvidia-smi` (WSL: `/usr/lib/wsl/lib/nvidia-smi`) reported **654 MiB free of 16376 MiB** — ~15.4 GB was
already resident and **unattributable under WSL** (`--query-compute-apps` returns `[N/A]`; :8000/:8001
were both DOWN at probe, so it is not the chat brain or BGE-M3 by port — likely a Windows-side process or
a leaked allocation). **No GPU STT model fits in 654 MiB** (smallest is Granite ~1.5 GB int8 / Parakeet
~1.0 GB int8). The live load + measured-VRAM-delta is therefore **environment-blocked** and marked
`needs_tim` in the lane report — it is NOT a code gap (the code below ships and is import-clean; the ear
is registered and probes `available:false` until its service is up). Re-run the measured-load step once
the card is freed (kill the unattributed allocation, or after a GPU/WSL restart).

## Shared env vars
| Var | Meaning | Used by |
|---|---|---|
| `COMPANY_PARAKEET_MODEL` / `_CANARY_MODEL` / `_GRANITE_MODEL` | override the HF repo id | each ear |
| `COMPANY_GRANITE_DEVICE` | torch device, default `cuda` (set `cpu` to dodge the CUDA-13 GPU hazard) | granite |
| `COMPANY_PARAKEET_URL` / `_CANARY_URL` / `_GRANITE_URL` | override the base URL the registry probes | voice/stt.py |

All three repos are **already in the local HF cache** (`~/.cache/huggingface/hub`, ext4 — verified
2026-06-05): `nvidia/parakeet-tdt-0.6b-v3`, `nvidia/canary-qwen-2.5b`, `ibm-granite/granite-4.0-1b-speech`.

---

## parakeet — `:2031` (`voice/ears/parakeet.py`) — NeMo
```bash
python3.12 -m venv ~/.voice-venvs/parakeet
~/.voice-venvs/parakeet/bin/pip install -U "nemo_toolkit[asr]" soundfile
# NeMo bundles its own torch+CUDA wheel — but this box is CUDA-13. VERIFY the GPU path loads
# (the same class of issue that forced faster-whisper to CPU). If it won't load on GPU, the ear FAILS
# LOUD at warm() and the registry shows it down (needs_tim) — NO silent fallback to whisper.cpp.
~/.voice-venvs/parakeet/bin/python /home/tim/company/voice/ears/parakeet.py 2031
```
- HF model: `nvidia/parakeet-tdt-0.6b-v3` (~1.0–2 GB). License **CC-BY-4.0** (commercial-OK). 25 languages.
- The live workhorse (~2000x RT) → the boot-default ear once verified up (flip `STT_DEFAULT`/`COMPANY_STT`
  from `whispercpp` to `parakeet`).

## canary — `:2032` (`voice/ears/canary.py`) — NeMo (SALM / speech-LM)
```bash
python3.12 -m venv ~/.voice-venvs/canary
~/.voice-venvs/canary/bin/pip install -U "nemo_toolkit[asr]" soundfile
# Canary-Qwen ships as a SALM (speech-augmented LM) in newer NeMo; the wrapper tries SALM then a
# generic ASRModel fallback. Same CUDA-13 hazard as parakeet. The HEAVIEST of the three (~6-7 GB fp16
# / ~3.5 GB int8) — mind co-residency with the chat brain on the 16 GB card.
~/.voice-venvs/canary/bin/python /home/tim/company/voice/ears/canary.py 2032
```
- HF model: `nvidia/canary-qwen-2.5b`. License **CC-BY-4.0**. English; best-WER + can *understand* audio.

## granite — `:2033` (`voice/ears/granite.py`) — transformers (lands clean)
```bash
python3.12 -m venv ~/.voice-venvs/granite
~/.voice-venvs/granite/bin/pip install transformers peft soundfile torchaudio torch
# transformers path is the standard one ("lands clean") — the ear most likely to load without the NeMo
# hazard. COMPANY_GRANITE_DEVICE=cpu runs it CPU-only (slower, but dodges the GPU hazard entirely).
export COMPANY_GRANITE_DEVICE=cuda     # or cpu
~/.voice-venvs/granite/bin/python /home/tim/company/voice/ears/granite.py 2033
```
- HF model: `ibm-granite/granite-4.0-1b-speech` (~1.5–3 GB). License **Apache-2.0** (commercial-OK).
  Also a GGUF build (`ibm-granite/granite-4.0-1b-speech-GGUF`) for a lean llama.cpp-style path if heavy.
- Compact + leaderboard-topping accuracy → the cross-check ear.

---

## The boot default (today)
`STT_DEFAULT = whispercpp` (the live, zero-install, on-machine ear on :2022). Flip to `parakeet` (env
`COMPANY_STT=parakeet` or the `rhm_config().stt` slot via `/api/rhm-config`) only **once it is verified
up** (service running + a known clip transcribed + VRAM measured). Both stay selectable; the registry
greys out whatever's down. This is the path-of-least-resistance law applied to the ears: the operator
swaps ears from a registry the UI reads, never by editing code.
```
