---
type: terrain-entry
name: voice-venvs
register: descriptive
aliases: ["voice-venvs"]
path: /home/tim/.voice-venvs
relation: external
kind: engine
status: unconfirmed
created: 2026-06-04
last_active: 2026-06-05
size: 48G
coverage: { files_read: 9, files_total: 10, last_read: 2026-06-26 }
git_remote: none
ports: [4124, 4125, 4126, 4127, 4128, 2031, 2032, 2033]
models: [chatterbox-tts, orpheus-tts, cosyvoice2-0.5b, xtts-v2, qwen3-tts, parakeet-tdt-0.6b, canary-qwen-2.5b, granite-speech-4.0-1b]
service_units: [company-voice-chatterbox, company-voice-orpheus, company-voice-cosyvoice, company-voice-xtts, company-voice-qwen3tts, company-stt-parakeet, company-stt-canary, company-stt-granite]
launched_by: company-voice-* / company-stt-* (systemd --user)
launched-by: ["[[company-systemd]]"]
part-of: ["[[company]]"]
relates-to: ["[[CosyVoice]]"]
secrets: false
move_intent: none
tags: [voice, model]
---

# voice-venvs

## What it is
48G of Python virtualenvs, one per voice engine, living outside `~/company`. Each holds the (often conflicting) dependency stack for one STT or TTS engine — they are kept separate because the engines pin incompatible Python/lib versions (cosyvoice's own unit comments: "runs from its own 3.10 venv … its deps pin python 3.10"). Observed contents: `canary chatterbox cosyvoice ears granite orpheus parakeet qwen3tts xtts` (9 dirs).

## How it works
Each engine venv supplies the interpreter that a Company systemd unit's `ExecStart` invokes directly. The engine **code** lives inside the repo (`/home/tim/company/voice/engines/*.py` for TTS, `/home/tim/company/voice/ears/*.py` for STT); the **venv** supplies its Python. The wire is single-hop and explicit — the unit names the venv python.

TTS engines (from `voice/ops/systemd/`, symlinked into `~/.config/systemd/user/`):
- `company-voice-chatterbox.service` → `ExecStart=%h/.voice-venvs/chatterbox/bin/python /home/tim/company/voice/engines/chatterbox.py 4124`
- `company-voice-orpheus.service` → `ExecStart=%h/.voice-venvs/orpheus/bin/python /home/tim/company/voice/engines/orpheus.py 4125`
- `company-voice-cosyvoice.service` → `ExecStart=%h/.voice-venvs/cosyvoice/bin/python /home/tim/company/voice/engines/cosyvoice.py 4126`
- `company-voice-xtts.service` → `ExecStart=%h/.voice-venvs/xtts/bin/python /home/tim/company/voice/engines/xtts.py 4127`
- `company-voice-qwen3tts.service` → `ExecStart=%h/.voice-venvs/qwen3tts/bin/python /home/tim/company/voice/engines/qwen3tts.py 4128`

STT ears (from `voice/ops/systemd/`):
- `company-stt-parakeet.service` → `ExecStart=%h/.voice-venvs/parakeet/bin/python /home/tim/company/voice/ears/parakeet.py 2031`
- `company-stt-canary.service` → `ExecStart=%h/.voice-venvs/canary/bin/python /home/tim/company/voice/ears/canary.py 2032`
- `company-stt-granite.service` → `ExecStart=%h/.voice-venvs/granite/bin/python /home/tim/company/voice/ears/granite.py 2033`

(`%h` = `/home/tim`, so e.g. `%h/.voice-venvs/parakeet/bin/python`.) Each unit also reads `EnvironmentFile=%h/company/voice/ops/voice.env`.

## What it connects to
- `[[company]]` — every venv runs in-repo engine code; the venv is just the interpreter+deps.
- `[[company-systemd]]` — the units that fire them are part of the Company systemd target.
- `[[CosyVoice]]` — cosyvoice's venv pairs with the separate `/home/tim/CosyVoice` weights+code checkout (added to `sys.path` by `cosyvoice.py`).

## When / where
Created/last-active dates from `stat`: chatterbox/xtts/qwen3tts/orpheus 2026-06-04, ears 2026-06-04, cosyvoice 2026-06-04, canary 2026-06-05, granite/parakeet 2026-06-05. Path `/home/tim/.voice-venvs`, 48G total. Per-venv file counts not enumerated (multi-GB venvs; not meaningful to count).

## Notes / evidence
- Read: all 8 voice/stt service units (verbatim `ExecStart` above), `voice/engines/cosyvoice.py` header.
- **GAP (flagged, not papered over):** the venv directory contains a **10th name `ears`** that NO unit's `ExecStart` references — the three STT ears each launch from their OWN per-engine venv (`canary`, `granite`, `parakeet`), not from `ears`. So `ears` is present-but-unwired by any unit found here; it is likely a shared base venv for the ears code, but I have NOT verified what (if anything) loads it. Worth a follow-up.
- The STT units (canary ~10GB, granite ~4.6GB, parakeet ~3GB resident) carry VRAM warnings: they cannot all co-reside on the 16GB card; intended to be enabled one-at-a-time per the VRAM-arbitration decision.
