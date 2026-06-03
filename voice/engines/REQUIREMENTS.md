---
type: reference
module: voice/engines
aliases: ["voice engines — install reference"]
tags: [company, voice, engines, install]
status: living
---

# voice/engines — install reference (per-engine, exact)

Each engine is its **own HTTP service on its own port**, run from **its own venv** — their deps conflict
(vLLM pins, torch pins, a git-clone repo, a non-pip package), which is exactly why service-per-port is the
shape: one process per engine, isolated. The heavy libraries below **cannot be installed now** (GPU/RAM
restart pending, some still downloading); this documents precisely what each needs before it can run. All
verified against the model repos on **2026-06-03**.

The bridge already proxies the existing Kokoro service on **:4123** (`COMPANY_TTS_URL`). These five extend
that contract on the next ports.

## Shared contract (all five, identical to `voice/tts_service.py`)
- `POST /tts {text, voice?, speed?}` → `audio/wav`
- `GET /voices` → `{"voices":[...], "default":...}`
- `GET /health` → `{"ok":true,"engine":<name>}`
- fail-loud 500 `{"error":"<Type>: <msg>"}` on any error.

## Shared env vars
| Var | Meaning | Used by |
|---|---|---|
| `COMPANY_VOICE_REF` | path to the refined-Australian **reference clip** (a real wav). **Does not exist yet — no clip was fabricated.** Required by the clip-driven engines; they FAIL LOUD if it's absent. | chatterbox, xtts, cosyvoice |
| `COMPANY_TTS_DEVICE` | torch device, default `cuda` | chatterbox, xtts |

A `voice` field in a `/tts` request overrides per engine: a **clip path** (chatterbox/xtts), a **voice description / instruction** (qwen3tts/cosyvoice), or a **voice name** (orpheus). `voice/loop.py` fills this from the selected persona automatically.

**`speed` (per the shared contract):** applied numerically by **xtts** only. **chatterbox / orpheus / qwen3tts / cosyvoice** accept `speed` (contract conformance) but do **not** apply it — those engines have no numeric speed arg; pace is steered by the reference clip (chatterbox), inline cues (orpheus), or the voice description/instruction text (qwen3tts/cosyvoice). This is documented (not silently dropped) so a caller never assumes speed works where it doesn't.

---

## chatterbox — `:4124` (`voice/engines/chatterbox.py`)
```bash
python3.12 -m venv ~/.voice-venvs/chatterbox
~/.voice-venvs/chatterbox/bin/pip install chatterbox-tts soundfile
# torch/torchaudio come in via chatterbox-tts; ensure a CUDA build of torch on this box.
export COMPANY_VOICE_REF=/abs/path/to/refined-australian.wav     # REQUIRED (real clip; none fabricated)
~/.voice-venvs/chatterbox/bin/python /home/tim/company/voice/engines/chatterbox.py 4124
```
- HF model: pulled by `ChatterboxTTS.from_pretrained` (`ResembleAI/chatterbox`). License **MIT** (commercial-OK).
- Tunables: `COMPANY_CHATTERBOX_EXAGGERATION` (default 0.5 — keep LOW for Viv's composed register), `COMPANY_CHATTERBOX_CFG` (0.5).

## orpheus — `:4125` (`voice/engines/orpheus.py`)
```bash
python3.12 -m venv ~/.voice-venvs/orpheus
~/.voice-venvs/orpheus/bin/pip install orpheus-speech soundfile
# If the bundled vLLM build is the buggy one, pin it AFTER:
~/.voice-venvs/orpheus/bin/pip install vllm==0.7.3
~/.voice-venvs/orpheus/bin/python /home/tim/company/voice/engines/orpheus.py 4125
```
- HF model: `canopylabs/orpheus-tts-0.1-finetune-prod` (override `COMPANY_ORPHEUS_MODEL`). License **Apache-2.0**.
- Voices (named): `tara leah jess leo dan mia zac zoe` (default `tara`). Emotion cues inline: `<laugh> <chuckle> <sigh> <cough> <sniffle> <groan> <yawn> <gasp>`.
- Heaviest VRAM (vLLM + a Llama-3B backbone) — mind co-residency with the chat brain on the 16 GB card.

## cosyvoice — `:4126` (`voice/engines/cosyvoice.py`)
NOT a pip package — a git clone with a submodule + a separate model download.
```bash
git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git ~/CosyVoice
cd ~/CosyVoice && git submodule update --init --recursive
conda create -n cosyvoice -y python=3.10 && conda activate cosyvoice   # (or a 3.10 venv)
pip install -r ~/CosyVoice/requirements.txt
pip install soundfile
# model:
python -c "from huggingface_hub import snapshot_download; snapshot_download('FunAudioLLM/CosyVoice2-0.5B', local_dir='/home/tim/CosyVoice/pretrained_models/CosyVoice2-0.5B')"
# run (REPO + the Matcha-TTS submodule must be importable; the wrapper adds them to sys.path from REPO):
export COMPANY_COSYVOICE_REPO=/home/tim/CosyVoice
export COMPANY_COSYVOICE_DIR=/home/tim/CosyVoice/pretrained_models/CosyVoice2-0.5B
export COMPANY_VOICE_REF=/abs/path/to/refined-australian.wav     # REQUIRED prompt clip
python /home/tim/company/voice/engines/cosyvoice.py 4126
```
- License **Apache-2.0**. Style steered by `COMPANY_COSYVOICE_INSTRUCT` (or per-request `voice` = the persona voice_description); the wrapper appends `<|endofprompt|>` if missing.
- If `sox` errors: `sudo apt-get install sox libsox-dev`.

## xtts — `:4127` (`voice/engines/xtts.py`)
```bash
python3.12 -m venv ~/.voice-venvs/xtts
~/.voice-venvs/xtts/bin/pip install coqui-tts soundfile
export COQUI_TOS_AGREED=1                                         # accept the (non-commercial) TOS non-interactively
export COMPANY_VOICE_REF=/abs/path/to/refined-australian.wav     # REQUIRED speaker clip
~/.voice-venvs/xtts/bin/python /home/tim/company/voice/engines/xtts.py 4127
```
- HF model: `coqui/XTTS-v2` via `TTS("tts_models/multilingual/multi-dataset/xtts_v2")`.
- **LICENSE GATE: Coqui Public Model License — NON-COMMERCIAL only.** Trial / by-ear comparison voice ONLY; **must not** enter any commercial/production path. Documented loudly in the wrapper header too.

## qwen3tts — `:4128` (`voice/engines/qwen3tts.py`)
```bash
python3.12 -m venv ~/.voice-venvs/qwen3tts
~/.voice-venvs/qwen3tts/bin/pip install -U qwen-tts soundfile torch
# optional (best latency): a built flash-attn, then set COMPANY_QWEN3TTS_ATTN=flash_attention_2
~/.voice-venvs/qwen3tts/bin/python /home/tim/company/voice/engines/qwen3tts.py 4128
```
- HF model: `Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign` — **already in the local HF cache** (the 13-file snapshot downloaded). License **Apache-2.0**.
- VoiceDesign = **describe a voice in text**: pass the description as the request `voice` (loop.py sends each persona's `voice_description`) or set `COMPANY_QWEN3TTS_DESC`. Default `attn_implementation` is **`sdpa`** (always works); switch to `flash_attention_2` only once `flash-attn` is built.
- Output 24 kHz (config `output_sample_rate`).

---

## Local ears (faster-whisper + Silero VAD) — the existing `.voice-venv` (`/home/tim/company/.voice-venv`, 3.12)
Implemented in `voice/stt.py`; install the two libs into the SHARED voice venv (the loop runs there):
```bash
/home/tim/company/.voice-venv/bin/pip install faster-whisper silero-vad soundfile numpy
```
- faster-whisper model `large-v3-turbo`, `int8_float16` on CUDA (overridable: `COMPANY_WHISPER_MODEL` / `COMPANY_WHISPER_DEVICE` / `COMPANY_WHISPER_COMPUTE` / `COMPANY_WHISPER_LANG`). Pure `int8` is the CPU path.
- Silero VAD via the `silero-vad` package (`load_silero_vad`, `get_speech_timestamps`) — used by `loop.utterance_ended` (endpointing) and `loop.barge_in`.
- `voice/stt.available()` reports `{"whisper_local": True}` only when `faster_whisper` is importable in that interpreter.

## The loop (`voice/loop.py`)
Runs in the SHARED `.voice-venv` (3.12). Reaches the brain over HTTP at `COMPANY_BRIDGE_URL` (default `http://127.0.0.1:8770`, the bridge — the ONE Suite). No extra install beyond faster-whisper + silero above. It does NOT capture the mic/speaker (browser hardware — lane G wires that).
