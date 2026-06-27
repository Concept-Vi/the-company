---
type: operations
title: Runtimes — vLLM, Ollama, jina-v4-env, Open WebUI
date_started: 2026-05-27
tags: [foundation, operations, runtimes]
---

# Runtimes

> [[_operations-index|← Operations hub]]

Three runtimes serve models on this substrate, plus Open WebUI as an interactive chat surface. Each exists because the others can't do what it does, not because of historical accident.

## vLLM

**Location:** `~/vllm-env/` (Python 3.12 venv)
**Version:** vLLM 0.21.0 with torch 2.11.0+cu130
**Serves:** AWQ / GPTQ / FP8 / FP16 / BF16 weights; native VL support; tool calling + structured output via flags
**Hosts:**
- [[../models/qwen3_5-4b-awq]] — port 8000 (`vllm-chat.service`)
- [[../models/bge-m3]] — port 8001 (`vllm-embed.service`)

**Why this runtime exists:** vLLM is the high-throughput batched serving engine. Its continuous batching, prefix caching, and CUDAGraphs are what take a single-stream rate of ~100 tok/s to an aggregate of >2,000 tok/s at concurrency 32. No other runtime on this substrate matches it for batched chat throughput.

**Critical operational facts:**

- Requires the cu13 toolchain inside the venv. See [[cuda-toolchain]] — without the version pinning + linker symlinks documented there, flashinfer JIT compilation fails and the engine doesn't load.
- Environment variable `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0` is set in service launchers. This disables a memory estimation that was over-reserving VRAM, breaking models that fit tightly.
- WSL forces `pin_memory=False` (logged warning on startup). Slight host-to-device transfer slowdown. Native Linux would avoid this; not a fix Tim controls.
- `enforce_eager=True` is **off** in production. It was on during initial tests and produced ~24 tok/s instead of >2,000 — eager mode disables the kernels vLLM depends on for batching.

**What it cannot serve in 0.21:**

- GGUF files → use [[#Ollama]]
- jina-embeddings-v4 (uses `JinaEmbeddingsV4Model` arch with dynamic HF modules + peft LoRAs) → use [[#jina-v4-env]]

**Launch surface:**

- Service units in `~/.config/systemd/user/vllm-*.service`
- Launcher scripts in `~/vllm-tests/serve.sh` and `~/vllm-tests/serve_embed.sh`
- Command-line operation via [[vllm-stack-cli]]

**Open at vLLM:** version upgrade strategy (0.21 → 0.22+ when worth it); whether speculative decoding is worth enabling; LoRA adapter loading never tested.

## Ollama

**Location:** system-level binary (`/usr/local/bin/ollama` v0.17.4); managed by system systemd (`ollama.service`)
**Port:** 11434
**Serves:** GGUF weights + cloud-routed models
**Hosts (local GGUF):**
- [[../models/qwen3_6-35b-a3b-gguf-q3-k-m]] — `qwen3.6-35b-a3b-q3km:latest`
- [[../models/qwen3_6-27b-gguf-q3-k-m]] — `qwen3.6-27b-q3km:latest`
- [[../models/ollama-nomic-embed-text]] — `nomic-embed-text:latest`

**Plus cloud routes** (visible in `ollama list`; accessed via the same endpoint, incur per-token cost): `gemma4:31b-cloud`, `nemotron-3-super:cloud`, `deepseek-v4-flash:cloud`, `deepseek-v4-pro:cloud`, `kimi-k2.5:cloud`, `kimi-k2.6:cloud`, `glm-5:cloud`, `glm-5.1:cloud`, `gemini-3-flash-preview:cloud`, `qwen3.5:397b-cloud`.

**Why this runtime exists:** vLLM doesn't serve GGUF natively in 0.21. The GGUF format ecosystem (llama.cpp lineage) has wider coverage of low-bit quants (IQ3, IQ4, Q3_K_M, Q4_K_S, etc.) than AWQ / GPTQ ranges — important for fitting big MoE models into 16 GB VRAM.

**Operational facts:**

- API endpoints: `/api/*` (Ollama native) and `/v1/*` (OpenAI-compat). Both work; substrate prefers `/v1/*` for cross-tool consistency.
- Serving is single-process — concurrent requests are queued, not batched the way vLLM batches. For high-throughput workloads this is a real limitation; for single-stream / reasoning use, no issue.
- Models registered via `ollama create <name> -f <Modelfile>`. See [[ollama]] for the registration pattern.
- Cloud-routed models incur cost per token; routes appear in `ollama list` with no local size.

**What it cannot serve:**

- AWQ / GPTQ / non-GGUF quants → use [[#vLLM]]
- Anything needing batched concurrent throughput at vLLM's level

**Open at Ollama:** systemd unit ownership and lifecycle (system-managed, not in the `vllm-stack` CLI surface); cloud-route cost characteristics unmeasured; Modelfile patterns for custom prompt templates / tool parsers not documented yet.

## jina-v4-env

**Location:** `~/jina-v4-env/` (Python 3.12 venv, separate from vllm-env)
**Pinned:** `transformers<5.0`, `Pillow`, `torchvision`, peft, accelerate
**Port:** 8002 (`vllm-jina-v4.service`)
**Serves:** [[../models/jina-embeddings-v4]] only

**Why this runtime exists:** [[../models/jina-embeddings-v4]] uses dynamic HF modules and peft LoRAs that vLLM 0.21 doesn't load. The model's bundled `qwen2_5_vl.py` references a ROPE init key (`'default'`) that transformers 5.x removed. Pinning `transformers<5` resolves the conflict; the pin can't share vLLM's venv (vLLM wants 5.x). So: separate venv.

**Server implementation:** `~/vllm-tests/serve_jina_v4.py` — a small FastAPI server exposing OpenAI-compat `/v1/embeddings`. Lock-serialised GPU access (single-process). Simple and inefficient by design; concurrent throughput is a server-shape question, not a model question.

**Operational facts:**

- Activates `~/jina-v4-env/`, not vllm-env
- CUDA library path: shares the `~/vllm-env/lib/python3.12/site-packages/nvidia/cu13/` toolkit via env var (the linker artefacts and CUDA stubs are reused; only the Python dep stack differs)
- Co-resident with vLLM at ~7.4 GB VRAM (BF16 weights)

**Open at jina-v4-env:** rewriting the server with proper request batching; whether to elevate the venv to a stable runtime or replace when vLLM gains support; multi-vector output mode supported by the model but not exposed by the server.

## Open WebUI

**Container:** Docker, `openwebui/open-webui:latest` image, name `open-webui`, host networking
**Port:** 8080
**Connected to:** the vLLM endpoints (chat on 8000, embed on 8001)

**Why this runtime exists:** Interactive chat surface for testing models with multi-turn, system prompts, vision input, structured outputs, document upload. Not a serving runtime in the load-bearing sense — it's a client that talks to the runtimes above via their OpenAI APIs.

**What it can and cannot configure:** see [[open-webui]].

**Operational facts:**

- Auth disabled (`WEBUI_AUTH=false`) for local use
- Persistent chat history in Docker named volume `open-webui-data`
- HF_TOKEN injected into container so it can pull its own auxiliary models without rate limits
- Embedding engine routed to the substrate's BGE-M3 (`RAG_EMBEDDING_ENGINE=openai`, `RAG_OPENAI_API_BASE_URL=http://localhost:8001/v1`) to prevent the container from downloading its own embedder

**Open at Open WebUI:** Ollama models don't auto-appear (the connection points only at vLLM endpoints currently); adding the Ollama endpoint as a third connection would surface the GGUF-hosted models in the dropdown.

## Cross-runtime considerations

| Concern | Resolution |
|---|---|
| Which runtime for a new model? | AWQ / GPTQ / FP8 / native HF → vLLM. GGUF → Ollama. Custom-arch / version-pinned-deps → dedicated venv. |
| Tool calling parser | Per-model + per-runtime decision. vLLM uses `--tool-call-parser <name>` (qwen3_xml, hermes, granite, etc.). Ollama uses its own template handling. |
| Chat template overrides | vLLM: `--chat-template <path>` (this is how the no-think patch loads). Ollama: Modelfile `TEMPLATE` directive. |
| Co-resident operation | vLLM and jina-v4-env both contend for the same 16 GiB VRAM; Ollama loads its model into the same VRAM on demand. The default co-resident set is documented in [[vram-budget]]. |
| Endpoint exposure | All four expose OpenAI-compat APIs. Cross-runtime client code only needs the right base URL per service. |

## Open at this topic

- Whether to consolidate to fewer runtimes (e.g., wait for vLLM GGUF support and drop Ollama) — currently no
- Whether to add TEI (HuggingFace Text Embeddings Inference) as a fourth runtime — currently no, BGE-M3 + jina-v4 cover the embedding slate
- Whether a runtime-routing layer (LiteLLM proxy) should sit in front of all four, unifying the API surface — not necessary for current use; would simplify Open WebUI's connection management

## Connects to

- [[_operations-index]] — hub
- [[cuda-toolchain]] — the load-bearing CUDA pinning vLLM depends on
- [[systemd-services]] — service units for each runtime
- [[vllm-stack-cli]] — the command surface
- [[ollama]] — Ollama-specific operations
- [[chat-template-patch]] — Qwen3.5 no-think template
- [[open-webui]] — UI configuration
- [[../models/_models-index]] — what each runtime serves
