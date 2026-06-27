---
type: terrain-entry
name: voicemode
register: descriptive
aliases: ["voicemode"]
path: /home/tim/.voicemode
relation: external
kind: engine
status: unconfirmed
created: 2025-12-01
last_active: 2025-12-23
size: 2.9G
coverage: { files_read: 1, files_total: 1, last_read: 2026-06-26 }
git_remote: none
ports: [whisper server port — set in voicemode.env]
models: [whisper.cpp]
service_units: [voicemode-whisper]
launched_by: voicemode-whisper.service → start-whisper-server.sh
launched-by: ["[[company-systemd]]"]
part-of: ["[[company]]"]
secrets: false
move_intent: none
tags: [voice]
---

# voicemode

## What it is
A 2.9G whisper.cpp speech-recognition service tree (the "voicemode" Whisper STT install). It is the older/standalone Whisper ear, distinct from the GPU NeMo/transformers ears (parakeet/canary/granite) that run from `~/.voice-venvs`.

## How it works
- `voicemode-whisper.service` (unit header: "voicemode-whisper.service v1.2.0", last updated 2025-12-01) → `ExecStart=/home/tim/.voicemode/services/whisper/bin/start-whisper-server.sh`.
- The unit comments note the start script "sources voicemode.env for port/model config" — so the listen port and whisper model are config in `voicemode.env`, not in the unit. `After=network.target`; `PATH` includes `%h/.local/bin` and `/usr/local/cuda/bin`.

This is a direct single-hop wire: ExecStart runs the in-tree start script.

## What it connects to
- `[[company]]` / `[[company-systemd]]` — the unit is `WantedBy=default.target` alongside the Company services; it provides STT for the voice circuit.

## When / where
`/home/tim/.voicemode`, 2.9G. Unit header dated 2025-12-01; unit file mtime 2025-12-23 — the oldest of the voice-related units (predates the June voice-venv ears build), suggesting it is the legacy/baseline Whisper path.

## Notes / evidence
- Read: `voicemode-whisper.service` (verbatim ExecStart + header).
- **Caveat:** the concrete listen port and whisper model live in `voicemode.env` (not read here) — recorded as config-driven rather than asserting a specific port.
