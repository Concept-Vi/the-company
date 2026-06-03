# voice/ops — the voice-trial run harness (post-restart "connect + verify")

This directory makes the voice trial a near-zero-build start after the 40 GB WSL restart. The trial
CODE is built (branch `voice-trial`); this is the OPS layer: per-engine systemd units, a stack
launcher, the post-restart verify-by-use script, the trial config, and the reference-clip plan.

Set up + verified **2026-06-04** (pre-restart, CPU-only). See the per-engine status table below for
what is verified vs. what still needs the GPU/models.

## Files here
| File | What |
|---|---|
| `voice.env` | shared env (ports, model ids, `COQUI_TOS_AGREED`, `COMPANY_COSYVOICE_REPO`, `COMPANY_VOICE_REF` path). Sourced by the units + launcher. |
| `systemd/company-voice-<engine>.service` | one `systemd --user` unit per engine (ports 4124–4128), each runs its engine from its own venv. WRITTEN, not installed — see install step. |
| `voice-stack` | launcher: `install` / `start` / `stop` / `restart` / `status` / `health` / `logs` / `ports` / `enable-boot` (mirrors `~/.local/bin/vllm-stack`). |
| `verify_voice.py` | post-restart verify-by-use (finish-checklist STEP 3) as one command. |
| `make_reference_clip.sh` | post-restart: mint `COMPANY_VOICE_REF` from Qwen3-VoiceDesign (no human clip needed). |
| `../trial_manifest.json` | concrete persona → engine → voice mappings + the `COMPANY_VOICE_REF` plan. |

## Venvs (all under `~/.voice-venvs/`, ext4 — NOT `/mnt/c`, NOT the production venvs)
- `~/.voice-venvs/ears` (3.12) — faster-whisper + Silero VAD. **VERIFIED** (see below).
- `~/.voice-venvs/qwen3tts` (3.12) — Qwen3-VoiceDesign. **Imports clean** (lib + wrapper module).
- `~/.voice-venvs/xtts` (3.12) — coqui-tts (pinned 0.25.3). **Imports clean** (lib + wrapper module).
- `~/.voice-venvs/chatterbox` (3.12) — chatterbox-tts. (install state: see table)
- `~/.voice-venvs/orpheus` (3.12) — orpheus-speech (vLLM). (install state: see table)
- `~/.voice-venvs/cosyvoice` (3.10) — CosyVoice2 from the git clone. (install state: see table)
- The EARS were ALSO installed into `/home/tim/company/.voice-venv` so the loop's in-process STT
  works (the loop runs there). Kokoro (:4123) still synthesizes there after the ears install — verified.

## Post-restart finish — the short path
```bash
# 1. install the systemd units (one-time; symlinks + daemon-reload)
/home/tim/company/voice/ops/voice-stack install

# 2. (optional) put voice-stack on PATH like vllm-stack
ln -sf /home/tim/company/voice/ops/voice-stack ~/.local/bin/voice-stack

# 3. bring up the TRIAL STARTER first (no ref clip needed; model already cached)
voice-stack start qwen3tts
voice-stack logs qwen3tts        # watch it load on the GPU

# 4. mint the shared reference clip (designs the refined-Australian voice; clone engines reuse it)
/home/tim/company/voice/ops/make_reference_clip.sh

# 5. start the rest (clone engines now have COMPANY_VOICE_REF)
voice-stack start                # all five
voice-stack health               # /health on 4123-4128 + ears import check

# 6. (after restarting the bridge from current code) verify by use
python3 /home/tim/company/voice/ops/verify_voice.py
```

## Per-engine status (honest — 2026-06-04 pre-restart)
| Engine | Install | Import-check | Notes |
|---|---|---|---|
| ears (whisper+VAD) | ✅ | ✅ **VERIFIED end-to-end on CPU in BOTH venvs** | Kokoro→`stt.transcribe(local)` round-trip returned the text EXACTLY; Silero detected the speech region — verified in `~/.voice-venvs/ears` AND in the loop's `~/company/.voice-venv` (the real loop interpreter, kokoro-onnx coexisting). `large-v3-turbo` downloaded. Kokoro :4123 still synthesizes after the ears install. |
| qwen3tts | ✅ | ✅ lib + wrapper module | `from qwen_tts import Qwen3TTSModel` OK; `generate_voice_design` present. TRIAL STARTER. Generation unverified (needs GPU). |
| xtts | ✅ | ✅ lib + wrapper module | coqui-tts 0.25.3 + transformers<4.50 (the LATEST 0.27.5 is broken — see REQUIREMENTS.md). Generation unverified. NON-COMMERCIAL. |
| chatterbox | ✅ | ✅ lib + wrapper module | `chatterbox-tts 0.1.7` + `torch 2.6.0+cu124` + `transformers 5.2.0`. `from chatterbox.tts import ChatterboxTTS` (`from_pretrained` present) + `voice.engines.chatterbox` both import clean. Generation unverified (needs GPU + `COMPANY_VOICE_REF`). |
| orpheus | ⏳ downloading | pending | `orpheus-speech` is vLLM-based (~2 GB+ torch/vLLM). Still downloading at report time. Resume: `~/.voice-venvs/orpheus/bin/pip install orpheus-speech soundfile`; if its bundled vLLM build is buggy, `pip install vllm==0.7.3` after. Then wrapper import-check. |
| cosyvoice | ❌ documented | wrapper module OK; repo import fails | The cloned repo's `requirements.txt` pins `openai-whisper==20231117` whose legacy `setup.py` FAILS to build the wheel. Relaxing that pin + dropping `tensorrt`/`deepspeed` then TIMED OUT (540 s) before finishing — repo deps (e.g. `tqdm`) not installed, so `from cosyvoice.cli.cosyvoice import AutoModel` fails. The wrapper `voice/engines/cosyvoice.py` itself imports fine. **Exact remaining step:** in the 3.10 venv, install the full `~/CosyVoice/requirements.txt` (with a buildable `openai-whisper`, and `deepspeed`/`tensorrt` re-added for real generation) without the time-box. This is the sanctioned document-and-move-on engine. |

## What still genuinely needs the GPU / models / restart (cannot be done now)
1. **Loading + GENERATION** for all five TTS engines (model load = VRAM). Import-clean ≠ generation-works.
2. **`COMPANY_VOICE_REF`** — minted post-restart by `make_reference_clip.sh` (qwen3tts must be up).
   The clone engines (chatterbox/xtts/cosyvoice) FAIL LOUD until it exists.
3. **A fresh bridge** — the bridge process currently running predates the voice-trial code, so its
   `/api/voice` lacks the `engines[]` array + `voice_enabled`. The restart starts a fresh bridge from
   current code; verify_voice STEP 3.1 expects the new shape.
4. **STT status flag caveat (decision for Tim):** the bridge runs in `.venv` (Python 3.14);
   faster-whisper is NOT installed there (and likely has no 3.14 wheel — the whole reason the loop is
   3.12). So `/api/voice` will report `stt.whisper_local: false` even post-restart, *even though the
   loop transcribes fine* (it runs in 3.12 with the ears installed). The FUNCTION works; the status
   registry just won't reflect it. Options: leave as-is (cosmetic), or have `stt.available()` probe the
   loop venv instead of its own interpreter. Tim's call.
5. **The UI lane + per-mode voice** (finish-checklist STEP 4) — a separate FORM session.

## Installing the units (detail)
`voice-stack install` symlinks `systemd/*.service` into `~/.config/systemd/user/` and runs
`daemon-reload`. The units use `%h` for `$HOME`, `EnvironmentFile=%h/company/voice/ops/voice.env`,
`WorkingDirectory=/home/tim/company`, and per-engine `ExecStart` pointing at that engine's venv python.
`enable-boot` makes them start at user login (like `vllm-stack enable-boot`).
