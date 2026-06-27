---
type: terrain-entry
name: vllm-tests
register: descriptive
aliases: ["vllm-tests"]
path: /home/tim/vllm-tests
relation: external
kind: engine
status: unconfirmed
created: 2026-05-26
last_active: 2026-06-06
size: 1.3M
coverage: { files_read: 8, files_total: 40, last_read: 2026-06-26 }
git_remote: none
ports: [8002, 8003, 8004]
models: [jina-embeddings-v4, Qwen3.5-2B, Qwen3.5-0.8B]
service_units: [vllm-jina-v4, llama-swap]
launched_by: vllm-jina-v4.service (serve_jina_v4.sh) + llama-swap (serve_2b.sh)
launched-by: ["[[company-systemd]]", "[[llama-swap]]"]
launches: ["[[jina-v4-env]]", "[[vllm-env]]"]
part-of: ["[[company]]"]
secrets: false
move_intent: none
tags: [model]
---

# vllm-tests

## What it is
A 1.3M / 40-file folder of model-serve scripts, benchmarks, ollama modelfiles, and Company-UI screenshots. **Despite the name, this is NOT scratch** — two live, production services reach INTO it for their launch scripts (see below). It also holds reference docs (`OPERATIONS.md`, `EMBEDDING_STRATEGIES.md`, `BENCHMARK_FACTSHEET.md`, `OPEN_WEBUI.md`), bench scripts (`bench*.py`), the `ollama-modelfiles/` dir, a `vllm-stack` subdir, the shared `chat_template_nothink.jinja`, and Company UI screenshots (`canvas-v1/v2.png`, `company-ai-console.png`, `company-first-purpose.png`, `company-self-grow-ui.png`, `company-walking-skeleton.png`).

## How it works — two live services depend on scripts HERE
1. `vllm-jina-v4.service` → `ExecStart=/home/tim/vllm-tests/serve_jina_v4.sh` (which sources `[[jina-v4-env]]` and runs `serve_jina_v4.py`, also here). Port 8002.
2. `[[llama-swap]]` config.yaml routes both small models through scripts here:
   - `qwen2b` → `cmd: /home/tim/vllm-tests/serve_2b.sh Qwen/Qwen3.5-2B ${PORT}`
   - `qwen0.8b` → `cmd: /home/tim/vllm-tests/serve_2b.sh Qwen/Qwen3.5-0.8B ${PORT}`
   `serve_2b.sh` in turn sources `[[vllm-env]]` and pulls `chat_template_nothink.jinja` from this same folder.

## What it connects to
- `[[llama-swap]]` — points its model cmds at `serve_2b.sh` here.
- `[[jina-v4-env]]` — `serve_jina_v4.sh`/`serve_jina_v4.py` here activate it.
- `[[vllm-env]]` — `serve_2b.sh` here activates it.
- `[[company]]` — `foundation/operations` references this folder (open-webui docs, ports); the screenshots document Company UI history.

## When / where
`/home/tim/vllm-tests`, 1.3M, 40 files. Created ~2026-05-26 (alongside vllm-env); scripts last touched 2026-06-06.

## Notes / evidence
- Read: `serve_jina_v4.sh`, `serve_2b.sh`, `/home/tim/llama-swap/config.yaml`, `OPEN_WEBUI.md`, dir listing; confirmed `foundation/operations/*` references via grep.
- **Correction to framing:** the starting "tests + benchmarks" label undersells it — it is a **load-bearing #model dependency for production**: kill this folder and `vllm-jina-v4` (embeddings, :8002) and the llama-swap small-model router both break. Treat as live infra, not scratch.
