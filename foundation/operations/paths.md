---
type: operations
title: Paths — substrate disk layout
date_started: 2026-05-27
tags: [foundation, operations, paths]
---

# Paths

> [[_operations-index|← Operations hub]]

## Substrate layout

| Path | Holds | Owner |
|---|---|---|
| `~/vllm-env/` | Main vLLM venv (Python 3.12, vLLM 0.21.0, torch 2.11.0+cu130, pinned cu13 toolchain) | substrate |
| `~/jina-v4-env/` | Dedicated venv for jina-v4 (transformers<5, Pillow, torchvision) | substrate |
| `~/vllm-tests/` | Source archive: launchers, benchmarks, chat-template patch, CLI | substrate; primary operational record |
| `~/.config/systemd/user/vllm-*.service` | systemd user units for chat / embed / jina-v4 | substrate |
| `~/.local/bin/vllm-stack` | Symlink to `~/vllm-tests/vllm-stack` (CLI on PATH) | substrate |
| `~/.cache/huggingface/hub/` | HF cache: all pulled models live here | shared across vllm-env and jina-v4-env |
| `~/.cache/huggingface/token` | HF auth token (chmod 600) | substrate |
| `~/.cache/vllm/torch_compile_cache/` | torch.compile cache per model | vLLM-managed |
| `~/.cache/flashinfer/` | flashinfer JIT'd kernels | vLLM-managed |
| `~/.ollama/` | Ollama model registry (separate from HF cache) | Ollama |
| `~/company/foundation/` | This knowledge layer — TIM, exchanges, models, operations, system | Company foundation |

## Source archive (`~/vllm-tests/`)

The primary operational record. Configs that actually run; scripts that actually execute. Files here are the source of truth for runtime behaviour; the synthesis at `~/company/foundation/operations/` distills and indexes them.

| File | Role |
|---|---|
| `serve.sh` | Chat launcher (used by `vllm-chat.service`) |
| `serve_embed.sh` | Embed launcher |
| `serve_jina_v4.sh` | jina-v4 launcher (activates jina-v4-env) |
| `serve_jina_v4.py` | FastAPI server for jina-v4 |
| `chat_template_nothink.jinja` | Patched Qwen3.5 template — see [[chat-template-patch]] |
| `env.sh` | Reference env vars (CUDA paths) |
| `vllm-stack` | The CLI — see [[vllm-stack-cli]] |
| `bench.py`, `bench_embed.py`, `bench_suite.py`, `bench_long_ctx.py` | Benchmarks — see [[benchmarks]] |
| `test_chat.py`, `test_embed.py`, `test_gen.py` | Pre-production single-model verification scripts |
| `BENCHMARK_FACTSHEET.md`, `README.md`, `OPERATIONS.md`, `OPEN_WEBUI.md`, `EMBEDDING_STRATEGIES.md` | Original operational documentation (now mostly superseded by `~/company/foundation/operations/` and the models hub) |

The originals are kept in place because:

1. The launchers are referenced by absolute path in systemd units; moving them breaks the substrate
2. They serve as the verbatim source layer (like exchanges) — when the foundation synthesis here diverges from reality, the originals are how to ground-truth what's actually running

## HF cache layout

The HuggingFace hub cache uses content-addressed blobs with snapshot symlinks:

```
~/.cache/huggingface/hub/models--<org>--<repo>/
  blobs/<sha-named blobs>
  snapshots/<sha>/<filename> -> ../../blobs/<sha>
  refs/main -> snapshots/<sha>
```

When a file is referenced (e.g. by `vllm serve <id>` or by an `ollama create` Modelfile), follow the snapshot symlink to find the actual blob. **Editing snapshots directly is refused by tooling** — symlinks to read-only-by-convention content.

## Foundation layer (`~/company/foundation/`)

| Subfolder | Purpose |
|---|---|
| `TIM.md` | The single foundation document at the root |
| `exchanges/` | Verbatim primary-source archive of dense conversations |
| `models/` | Model registry and per-model files |
| `operations/` | This folder — substrate operations |
| `system/` | Synthesis layer (principles, architecture) |

The foundation layer is **the Company's persistent memory across sessions**. Source archives (vllm-tests, exchanges) sit alongside synthesis (models, operations, system) — primary source preserved, synthesis indexed.

## What lives outside `~/`

| Location | Role |
|---|---|
| `/usr/local/bin/ollama` | Ollama binary (system-installed) |
| `/etc/systemd/system/ollama.service` | Ollama system service |
| `/usr/lib/wsl/lib/` | WSL-side CUDA stub libraries — see [[cuda-toolchain]] |
| `/etc/wsl.conf` | WSL boot config (systemd=true) |
| Docker volumes (managed by Docker daemon) | `open-webui-data` for WebUI persistence |

## Open at this topic

- Whether to move `~/vllm-tests/` into `~/company/foundation/operations/source/` for consolidation — pro: single foundation layer; con: breaks the absolute paths in systemd units
- Disk-usage forecasting as more models accumulate (currently 41% of 1TB used; multiple model variants could double in months)
- Backup policy for the HF cache (re-downloadable but slow), the venvs (reproducible from `uv pip install`), `~/.ollama/` (re-registrable), and `~/company/foundation/` (irreplaceable — synthesis would have to be re-derived from chat transcripts)
- Whether to keep historical benchmark logs (`/tmp/bench_*.log`) in a foundation-layer archive vs treat as ephemeral

## Connects to

- [[_operations-index]] — hub
- [[cuda-toolchain]] — venv-internal CUDA paths
- [[runtimes]] — what each venv hosts
- [[../TIM]] — the foundation layer this folder is part of
