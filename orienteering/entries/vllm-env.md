---
type: terrain-entry
name: vllm-env
register: descriptive
aliases: ["vllm-env"]
path: /home/tim/vllm-env
relation: external
kind: engine
status: unconfirmed
created: 2026-05-26
last_active: 2026-06-06
size: 8.4G
coverage: { files_read: 9, files_total: 9, last_read: 2026-06-26 }
git_remote: none
ports: [8000, 8001, 8003, 8004, 8005, 8006]
models: [Qwen3.5-4B-AWQ, Qwen3.5-2B, Qwen3.5-0.8B, BGE-M3, jina-v5-text-small, Nemotron-30B-A3B-AWQ, Qwen3-Embedding-8B]
service_units: [vllm-chat, vllm-2b, vllm-08b, vllm-embed, vllm-jina-v5, vllm-nemotron, vllm-qwen3emb]
launched_by: serve_model.sh / serve_2b.sh (which `source` this venv) ← vllm-*.service
launched-by: ["[[company-systemd]]"]
part-of: ["[[company]]"]
relates-to: ["[[vllm-tests]]", "[[llama-swap]]"]
secrets: false
move_intent: none
tags: [model]
---

# vllm-env

## What it is
The 8.4G shared vLLM inference runtime venv — the single Python environment in which nearly every config-driven local chat/embedding model is served. It carries the vLLM install plus the bundled CUDA cu13 toolchain (`vllm-env/lib/python3.12/site-packages/nvidia/cu13`) that `serve_model.sh` exports as `CUDA_HOME`.

## How it works — TWO-HOP wire (the ExecStart does NOT name this venv)
The systemd units do not reference `vllm-env` directly. The chain is:

1. The unit's ExecStart runs a launcher script:
   - `vllm-chat.service` → `ExecStart=/home/tim/company/ops/serve_model.sh chat-4b`
   - `vllm-2b.service` → `ExecStart=/home/tim/company/ops/serve_model.sh chat-2b`
   - `vllm-08b.service` → `ExecStart=/home/tim/company/ops/serve_model.sh chat-08b`
   - `vllm-embed.service` → `ExecStart=/home/tim/company/ops/serve_model.sh embed-bge`
   - `vllm-jina-v5.service` → `ExecStart=/home/tim/company/ops/serve_model.sh embed-jina-v5`
   - `vllm-nemotron.service` → `ExecStart=/home/tim/company/ops/serve_model.sh chat-nemotron`
   - `vllm-qwen3emb.service` → `ExecStart=/home/tim/company/ops/serve_model.sh embed-qwen3`
2. **`serve_model.sh` activates this venv** (the proof of the wire): `source "$HOME/vllm-env/bin/activate"` and `export CUDA_HOME="$HOME/vllm-env/lib/python3.12/site-packages/nvidia/cu13"`, then `exec vllm serve …`.

`serve_model.sh` is the ONE registry-driven launcher: it reads per-service flags from `ops/services.json` (via `cli/serveconfig.py`) so model id/port/gpu-util are config, not hardcoded. The 2B/0.8B path via `serve_2b.sh` ALSO sources this venv (`source "$HOME/vllm-env/bin/activate"`).

## What it connects to
- `[[company]]` — the launcher and the model registry live in `~/company/ops`.
- `[[company-systemd]]` — the `vllm-*` units belong to the Company target.
- `[[vllm-tests]]` — `serve_2b.sh` lives there and also activates this venv.
- `[[llama-swap]]` — routes qwen2b/0.8b through `serve_2b.sh`, indirectly using this venv.

## When / where
`/home/tim/vllm-env`, 8.4G, dir mtime 2026-05-26; units last edited 2026-06-06. Venv files not enumerated.

## Notes / evidence
- Read: `serve_model.sh` (full header + activate line), `serve_2b.sh`, and all 7 `vllm-*.service` units (verbatim ExecStart above).
- **Correction to the starting fact:** the units do NOT name `vllm-env` — they run `serve_model.sh`/`serve_2b.sh`, which `source $HOME/vllm-env/bin/activate`. The venv is a two-hop dependency, not a direct ExecStart target.
