---
type: terrain-entry
name: openwebui-venv
register: descriptive
aliases: ["openwebui-venv"]
path: /home/tim/openwebui-venv
relation: connected
kind: engine
status: unconfirmed
created: 2026-05-26
last_active: 2026-06-23
size: 6.8G
coverage: { files_read: 3, files_total: 3, last_read: 2026-06-26 }
git_remote: none
ports: [8080]
models: []
service_units: []
launched_by: NOT systemd / NOT docker — manual via venv binary (open-webui)
depends-on: ["[[vllm-env]]"]
relates-to: ["[[company]]"]
secrets: false
move_intent: none
tags: [model]
---

# openwebui-venv

## What it is
A 6.8G venv whose `bin/open-webui` launches Open WebUI — the interactive chat UI Tim uses to manually exercise the local vLLM models. Open WebUI auto-discovers OpenAI-compatible model servers and gives a chat/tools/vision/RAG playground on `http://localhost:8080`.

## How it works — NOT systemd-wired (verified)
Unlike the other engines in this ledger, **no systemd unit and no Docker container launch this** — verified:
- `grep -rl -i webui /home/tim/.config/systemd/user` → no unit.
- `docker ps -a | grep -i webui` → no container (rc=1).
- The launch binary is `/home/tim/openwebui-venv/bin/open-webui` (mtime 2026-06-23), so it is started manually/on-demand from the venv.

The connection to the Company is at the model layer, documented in `OPEN_WEBUI.md` (in `[[vllm-tests]]`, mirrored at `~/company/foundation/operations/open-webui.md`): it points at the chat server (port 8000) and embed server (port 8001) and "auto-discovers from both."

## What it connects to
- `[[vllm-env]]` — consumes the vLLM chat (:8000) + embed (:8001) servers as its model backends.
- `[[company]]` — `foundation/operations/open-webui.md` + `open-webui-extras.md` document its use as the Company's model-testing surface.

## When / where
`/home/tim/openwebui-venv`, 6.8G; launch binary mtime 2026-06-23 (recently used). Serves on :8080.

## Notes / evidence
- Read: `bin/` listing (`open-webui`, `uvicorn`), `OPEN_WEBUI.md`, systemd grep + docker ps checks.
- **Correction to the task's frame:** the task assumed an "external engine wired in by systemd." There is NO systemd/Docker wire for this one — it is launched outside systemd (manual venv binary) and connects to the Company purely as a client of the vLLM servers. Recorded as `relation: connected` (a separate tool wired to the Company), not `external`, to be honest about the missing systemd wire.
