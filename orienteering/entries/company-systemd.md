---
type: terrain-entry
name: company-systemd
register: descriptive
aliases: ["company-systemd"]
path: /home/tim/.config/systemd/user
relation: external
kind: config
status: unconfirmed
created: 2026-06-04
last_active: 2026-06-26
size: small (unit files)
coverage: { files_read: 12, files_total: 22, last_read: 2026-06-26 }
git_remote: none
purpose: the Company's control layer — the user services that boot and run it
ports: [8770, 5173, 8007]
launches: ["[[company]]"]
produced: ["[[corpora]]"]
depends-on: ["[[config-company]]"]
relates-to: ["[[cache-company]]"]
secrets: false
move_intent: none
tags: [control, voice, embedding]
---

# company-systemd

## What it is
The Company's control layer: ~20 systemd user service/timer units plus a `company.target` that groups them. They boot and run the Company's processes — bridge, canvas, session supervisor, voice/STT engines, the embed server, and the export+reindex timers.

Evidence (Observed): 21 `company-*` units + `company.target`. Key units: `company-bridge.service` ("Company bridge — UI face of the Suite (HTTP API on :8770)", `ExecStart=… runtime/bridge.py 8770`); `company-canvas.service` ("operable surface … vite … :5173"); `company-embed-pplx.service` ("pplx-embed-context-v1-4b server … on port 8007"); `company-session-supervisor.service`; STT engines `company-stt-{canary,granite,parakeet}`; TTS/voice `company-tts-kokoro`, `company-voice-{chatterbox,cosyvoice,orpheus,qwen3tts,xtts}`; timers `company-agent-sessions-exporter.{service,timer}` (every 20 min, jsonl→corpora) + `company-claude-sessions-reindex.{service,timer}` (delta reindex ~5 min after each export); `company-remote.service`; a bridge drop-in `company-bridge.service.d/wire.conf`.

## How it works
`company.target` ("The Company — all local services") is the single start point (`systemctl --user start company.target`), members wired via `WantedBy=company.target`. The export→reindex circuit: exporter (`*:00/20`) writes Claude jsonl → `~/corpora/claude-sessions`; reindex beat (`*:05/20`) delta-embeds that into `[[cache-company]]` via :8007. The Company has SOURCE COPIES of these units at `/home/tim/company/ops/systemd/` (Observed) — the installed `~/.config/systemd/user` copies are the active ones.

## What it connects to
- `[[company]]` — boots/runs it; source units mirrored in `company/ops/systemd/`.
- `[[corpora]]` (exporter target) + `[[cache-company]]` (reindex target, :8007 embedder).
- `[[config-company]]` — the remote/serving units use its TLS cert.

## When / where
Path `/home/tim/.config/systemd/user` (`company-*` + `company.target`). 21 units. created 2026-06-04 area; queried live 2026-06-26.

## Notes / evidence
Read: `company.target`, bridge/canvas/embed/exporter/reindex units; confirmed `ops/systemd/` source copies; queried live state.

State note (Verified, 2026-06-26): the units DEFINE a full local stack, but it is only PARTIALLY running. `systemctl --user list-timers 'company-*'` → **0 active timers**; `company-agent-sessions-exporter.timer` and `company-claude-sessions-reindex.timer` are **inactive**; `company-canvas.service` **inactive**; `company.target` **disabled**. Currently ACTIVE: `company-embed-pplx.service` (:8007) and `company-bridge.service` (:8770). This is the root cause of `[[corpora]]` (06-12) and `[[cache-company]]` (06-22) being stale — the export/reindex loop is not currently firing. "Units define a 20-min loop" is Observed; "the loop is flowing" is NOT — the timers are down.
