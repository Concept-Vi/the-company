---
type: terrain-entry
name: CosyVoice
register: descriptive
aliases: ["CosyVoice"]
path: /home/tim/CosyVoice
relation: external
kind: engine
status: unconfirmed
created: 2026-05-26
last_active: 2026-06-04
size: 5.3G
coverage: { files_read: 2, files_total: 2, last_read: 2026-06-26 }
git_remote: https://github.com/FunAudioLLM/CosyVoice.git
ports: [4126]
models: [CosyVoice2-0.5B]
service_units: [company-voice-cosyvoice]
launched_by: company-voice-cosyvoice.service (via the cosyvoice venv python, which adds this repo to sys.path)
launched-by: ["[[company-systemd]]"]
part-of: ["[[company]]"]
depends-on: ["[[voice-venvs]]"]
secrets: false
move_intent: none
tags: [voice]
---

# CosyVoice

## What it is
A git clone of Alibaba FunAudioLLM's CosyVoice repository (Apache-2.0) plus the downloaded CosyVoice2-0.5B TTS model weights — 5.3G. It provides the upstream library code + `pretrained_models/CosyVoice2-0.5B` snapshot that the Company's in-repo `cosyvoice.py` engine imports.

## How it works
The wire is indirect — no ExecStart names this folder directly; it is pulled in by `sys.path` at runtime:
- `company-voice-cosyvoice.service` → `ExecStart=%h/.voice-venvs/cosyvoice/bin/python /home/tim/company/voice/engines/cosyvoice.py 4126`.
- `voice/engines/cosyvoice.py` header documents the contract: `git clone --recursive https://github.com/FunAudioLLM/CosyVoice.git` then `export COMPANY_COSYVOICE_REPO=/path/to/CosyVoice  # added to sys.path here`, with model dir `pretrained_models/CosyVoice2-0.5B`.

So: the unit launches the cosyvoice venv python on the in-repo engine; the engine adds this `/home/tim/CosyVoice` checkout to `sys.path` and loads its `CosyVoice2-0.5B` weights. Serves on port 4126.

## What it connects to
- `[[voice-venvs]]` — runs under the `cosyvoice` venv's Python (3.10, per the unit note).
- `[[company]]` — imported by `voice/engines/cosyvoice.py`.
- `[[company-systemd]]` — fired by `company-voice-cosyvoice.service`.

## When / where
`/home/tim/CosyVoice`, 5.3G. Git remote `https://github.com/FunAudioLLM/CosyVoice.git`; last commit 2026-05-26. cosyvoice venv mtime 2026-06-04.

## Notes / evidence
- Read: `company-voice-cosyvoice.service` (verbatim ExecStart), `voice/engines/cosyvoice.py` header (clone/sys.path/model-dir contract); `git remote -v` and `git log -1` for remote + date.
