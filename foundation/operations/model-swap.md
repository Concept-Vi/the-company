---
type: operations
title: Model swap — chat / embed default-model switching
date_started: 2026-05-27
tags: [foundation, operations, swap, vram]
---

# Model swap

> [[_operations-index|← Operations hub]]

## When swap is the right move

The 16 GiB VRAM on the substrate makes co-resident operation tight. The default — chat + embed + jina-v4 all running at ~15.5 GiB total — uses 95% of available VRAM. Adding a fourth model OOMs.

So when a model that doesn't fit alongside the defaults needs to run, swap is the move: stop one default, start the new model in its slot, optionally swap back later.

Typical swap candidates:

| Model | Reason swap-only |
|---|---|
| [[../models/nemotron-3-nano-30b-a3b-awq]] | 17 GB on disk; doesn't co-exist with chat default |
| [[../models/qwen3_6-35b-a3b-gguf-q3-k-m]] via Ollama | 16 GB; Ollama loads on demand; conflicts with chat default's VRAM |
| [[../models/qwen3_6-27b-gguf-q3-k-m]] via Ollama | 13 GB; same |
| [[../models/qwen3-embedding-8b]] | 15 GB; can't co-exist with chat |
| [[../models/nomic-embed-code]] | 14 GB at load; swap-only |

vs models that **don't** need swap (co-resident with defaults at current settings):

| Model | Why co-resident |
|---|---|
| [[../models/jina-embeddings-v4]] | 7.4 GB; jina-v4-env runtime; fits alongside chat+embed |
| [[../models/qwen3_5-2b]] | 4.3 GB; would fit, but not deployed |
| [[../models/qwen3_5-0_8b]] | 1.7 GB; would fit easily |

## Swap procedure (chat slot)

```
vllm-stack swap-chat <hf-id>
```

What this does:

1. `systemctl --user stop vllm-chat.service`
2. `sed -i 's|MODEL=\"\${1:-[^\"]*}\"|MODEL=\"\${1:-<hf-id>}\"|' ~/vllm-tests/serve.sh` — rewrites the default-model line
3. `systemctl --user start vllm-chat.service`
4. Cold start begins (~2–3 minutes for a new model, less if torch.compile cache hits)

`serve.sh` flags (gpu-memory-util, max-model-len, max-num-seqs, prefix caching, tool parser, chat template) stay as configured. For models whose architecture warrants different flags ([[../models/nemotron-3-nano-30b-a3b-awq]] needs a different `--tool-call-parser`), the swap also requires manually editing `serve.sh`.

## Swap procedure (embed slot)

```
vllm-stack swap-embed <hf-id>
```

Same shape. Different launcher (`serve_embed.sh`). Cold start faster than chat (~30–60s) because embedders are smaller and don't need the chat-template / tool-parser machinery.

## Why a manual swap, not a router

A request-time model router (e.g. LiteLLM proxy in front, spawning backends on demand) would let agents request "give me model X" and have it materialise. The substrate doesn't have this yet. Reasons:

1. **VRAM allocation is the binding constraint**, not request routing. A router doesn't make the model fit; it just makes the model-selection prettier from the caller's side.
2. **Cold-start is 2–3 minutes**. Calling a router and waiting 3 minutes for a response is worse UX than knowing upfront "this slot has X loaded, swap if you need Y."
3. **The substrate is built around a small set of always-on defaults and a clearly-named swap procedure**. A router would obscure that contract.

When the substrate grows beyond one machine, or when on-demand model swapping becomes routine (rather than rare), a routing layer becomes worth adding. Not yet.

## What survives a swap

| Survives | Notes |
|---|---|
| torch.compile compile-cache per model | `~/.cache/vllm/torch_compile_cache/` — re-loads fast on next start of the same model |
| flashinfer JIT'd kernels | `~/.cache/flashinfer/` — shared across processes |
| OS page cache of weight files | Until RAM pressure evicts |
| Open WebUI chat history | Docker volume |
| Vector DB contents | Outside the substrate |

| Doesn't survive |
|---|
| GPU VRAM state of the swapped-out model |
| CUDAGraphs (recaptured each process restart, adds ~5–15s) |
| KV cache contents from prior conversations |
| Any in-flight requests on the swapped-out service |

## Restore-after-swap

After running a non-default model for a session, restore the default with another swap:

```
vllm-stack swap-chat cyankiwi/Qwen3.5-4B-AWQ-4bit
```

Cold start is faster than the original because the model's compile cache is warm.

## Open at this topic

- A `vllm-stack swap-back` command that remembers the previous default and restores it
- A `vllm-stack swap-list` to enumerate the registered candidates for the chat slot
- Per-model flag profiles — when [[../models/nemotron-3-nano-30b-a3b-awq]] is the deployed chat, it wants `--tool-call-parser <nemotron-specific>` not `qwen3_xml`. Currently this would need manual `serve.sh` edits beyond what swap-chat does. A model-aware swap that picks the right flags would close this gap.
- Ollama-swap parity — currently `vllm-stack` does not include an Ollama-side swap; switching the chat endpoint from vLLM:8000 to Ollama:11434 is a different kind of swap, not yet wrapped
- Whether to elevate any swap-only candidate to a permanent secondary endpoint on a different port (e.g. always-running on 8003) — fits some models, breaks the VRAM math for others

## Connects to

- [[_operations-index]] — hub
- [[vram-budget]] — the constraint that makes swap necessary
- [[vllm-stack-cli]] — command surface
- [[systemd-services]] — what swap manipulates
- [[../models/_models-index]] — registry of candidates
