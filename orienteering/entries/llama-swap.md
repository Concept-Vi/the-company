---
type: terrain-entry
name: llama-swap
register: descriptive
aliases: ["llama-swap"]
path: /home/tim/llama-swap
relation: external
kind: engine
status: unconfirmed
created: 2026-05-30
last_active: 2026-05-30
size: 8K
coverage: { files_read: 1, files_total: 1, last_read: 2026-06-26 }
git_remote: none
ports: [9090]
models: [Qwen3.5-2B, Qwen3.5-0.8B]
service_units: [llama-swap]
launched_by: llama-swap.service → /usr/local/bin/llama-swap
launched-by: ["[[company-systemd]]"]
launches: ["[[vllm-tests]]"]
part-of: ["[[company]]"]
depends-on: ["[[vllm-env]]"]
secrets: false
move_intent: none
tags: [model]
---

# llama-swap

## What it is
An 8K folder holding a single `config.yaml` — the model-router config for the `llama-swap` binary, which swaps small models in/out on demand behind one OpenAI-compatible endpoint on `127.0.0.1:9090`. (The binary itself lives at `/usr/local/bin/llama-swap`; only the config is here.)

## How it works
- `llama-swap.service` → `ExecStart=/usr/local/bin/llama-swap -config /home/tim/llama-swap/config.yaml -listen 127.0.0.1:9090 -watch-config` (the `-config` flag is the proof of the wire — the unit reads THIS file).
- `config.yaml` defines two models, each routed to a vllm-tests launch script with a TTL so they unload when idle:
  - `qwen2b` → `cmd: /home/tim/vllm-tests/serve_2b.sh Qwen/Qwen3.5-2B ${PORT}`, `ttl: 600`
  - `qwen0.8b` → `cmd: /home/tim/vllm-tests/serve_2b.sh Qwen/Qwen3.5-0.8B ${PORT}`, `ttl: 600`

## What it connects to
- `[[vllm-tests]]` — both model cmds invoke `serve_2b.sh` there.
- `[[vllm-env]]` — `serve_2b.sh` activates it.
- `[[company]]` / `[[company-systemd]]` — `llama-swap.service` is on the Company target (`WantedBy=default.target`).

## When / where
`/home/tim/llama-swap`, 8K, config.yaml mtime 2026-05-30. Unit description tags it "(test)" but it is wired and enabled.

## Notes / evidence
- Read: `/home/tim/llama-swap/config.yaml` (full, verbatim cmds above), `llama-swap.service` (verbatim ExecStart with `-config` pointing here).
