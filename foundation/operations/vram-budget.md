---
type: operations
title: VRAM budget — 16 GiB allocation patterns
date_started: 2026-05-27
tags: [foundation, operations, vram]
---

# VRAM budget

> [[_operations-index|← Operations hub]]

## Capacity

| Metric | Value |
|---|---|
| GPU | NVIDIA RTX 4080 |
| Total VRAM | 16,376 MiB (~16 GiB) |
| Typical idle usage | ~900 MiB (Chrome / X server / WSL overhead) |
| Effective for substrate | ~15,400 MiB |

## Verified co-resident patterns

**Default (2026-05-27)**: chat + embed + jina-v4 simultaneously

| Service | Model | VRAM at load (KV included) |
|---|---|---|
| `vllm-chat` | [[../models/qwen3_5-4b-awq]] (`--gpu-memory-utilization 0.90`, `--max-num-seqs 64`, `--max-model-len 4096`) | ~12.8 GiB |
| `vllm-embed` | [[../models/bge-m3]] (`--gpu-memory-utilization 0.30`) | ~2.7 GiB |
| `vllm-jina-v4` | [[../models/jina-embeddings-v4]] (BF16 weights, FastAPI server) | ~7.4 GiB BF16 weights — see note below |
| **Combined observed** | | **~15.5 GiB (95% util)** |

Note on jina-v4: the BF16 weights are 7.4 GiB by size on disk; observed combined VRAM with chat + embed sits at ~15.5 GiB total, which means the three services share GPU memory more efficiently than naive addition would suggest. The `--gpu-memory-utilization` values for vLLM-served services are **share-of-free-VRAM** budgets, not absolute reservations — vLLM negotiates against what's free at startup time.

This three-service default has been verified to:
- Boot in sequence successfully
- Sustain concurrent load on chat and embed (both at concurrency 32) without OOM
- Survive 8+ minute mixed-load runs with zero errors

## Verified single-service patterns

When a swap candidate runs alone (chat default stopped):

| Candidate | Approx VRAM | Headroom for KV |
|---|---|---|
| [[../models/qwen3_5-9b-awq]] (the 9B VL, when it was on disk) | ~11.2 GiB weights | very tight; 0.27 GiB KV at 2K context, max concurrency 2.4x |
| [[../models/gemma-4-e4b-fp8]] (when it was on disk) | ~11.6 GiB weights | very tight |
| Larger models (any 12+ GB) | borderline | swap-only at max |

## Co-resident frontiers (untested)

Patterns that should fit by size but haven't been verified:

| Pattern | Expected total | Risk |
|---|---|---|
| chat (4B) + embed (BGE-M3) only — no jina-v4 | ~15.5 GiB | verified |
| chat (4B) + embed (BGE-M3) + [[../models/jina-embeddings-v5-text-small]] (1.3 GB) | ~16.8 GiB | OOM likely |
| chat (4B) + embed (BGE-M3) + jina-v4 + small auxiliary | over budget | OOM expected |
| Two chat services on different ports | typically over budget | swap-only |

## What eats VRAM unexpectedly

- **Vision towers on VL models.** A 4B "text" model that's actually VL carries the vision tower weights even when only text is sent. Discovered via [[../models/qwen3_5-9b-awq]] — 12 GB on disk for a "9B" model.
- **CUDAGraphs memory profiling.** vLLM 0.21 default reserves an estimate for CUDAGraphs ahead of profiling; the estimate is conservative and over-reserves. Disabled via `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0`. See [[cuda-toolchain]].
- **KV cache scaling with concurrency.** `--max-num-seqs N` × `--max-model-len M` is the implicit KV ceiling; raising either consumes proportional VRAM. The 4B at 64 seqs × 4K = the budget that fits 12.8 GB total.
- **Mamba caches.** Hybrid Mamba-attention models (Qwen 3.5 / 3.6 family, Nemotron 3) carry Mamba state per sequence; this is the constraint behind "max_num_seqs (256) exceeds available Mamba cache blocks (17)" errors when raising concurrency on small-context configurations.
- **Co-resident Docker (Open WebUI) and X server** — small but real, ~1 GiB baseline before any model loads.

## The throughput / capacity tradeoff

The 4B AWQ's KV cache supports many concurrent sequences at 4K context:

| Config | KV slot count | Max concurrent |
|---|---|---|
| 4K context, default 64 seqs | 649,774 tokens (for 0.8B, similar pattern at scale) | Bounded by `--max-num-seqs` |
| 32K context, 8 seqs | 255,970 tokens (verified during long-context bench) | 7.81x at full context |

Raising context cuts concurrency proportionally. This is the "long context vs high throughput" lever; current default sits at 4K / 64 for the throughput regime.

## Operational rules of thumb

1. **Co-resident set is the three current services.** Don't add a fourth.
2. **Swap candidates are anything ≥12 GB on disk.** Use `vllm-stack swap-chat` / `swap-embed`. See [[model-swap]].
3. **When tight, lower max-num-seqs before raising gpu-memory-utilization above 0.90.** GPU-mem-util reaching 0.95+ leaves no room for spikes; max-num-seqs reduction is graceful.
4. **Check `nvidia-smi` before bringing up a new service.** If something idle (Chrome with many tabs) is holding >1.5 GB, services that fit by spec may not fit in practice.

## Open at this topic

- Whether memory ballooning between WSL and Windows can affect VRAM-side budgets (probably not — VRAM is GPU-side, separate from system RAM — but worth confirming under low-host-RAM conditions)
- Quantitative VRAM accounting tool — currently dependent on `nvidia-smi` snapshots; no continuous tracker
- VRAM measurement under sustained load for all three services concurrently (only peak verified; long-tail behaviour not characterised)
- Whether to drop `--max-num-seqs` lower in the chat service to free VRAM for an additional small service (4B at 32 seqs would free ~3–4 GiB)

## Connects to

- [[_operations-index]] — hub
- [[model-swap]] — what swap is for (this budget)
- [[runtimes]] — services that consume the budget
- [[../models/_models-index#VRAM allocation patterns]] — same content cross-linked from the models hub
