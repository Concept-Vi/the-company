---
type: model
id: nomic-ai/nomic-embed-code
filename: nomic-embed-code
status: downloaded
runtime: not-yet-served
date_added: 2026-05-26
tags: [foundation, models, embedding, code]
---

# Nomic Embed Code

> [[_models-index|← Models hub]] · linked from: code embedding for codebase / repo retrieval

## At a glance

| Field | Value |
|---|---|
| HF id | `nomic-ai/nomic-embed-code` |
| Disk | 27 GB |
| Quant | FP16 |
| Architecture | Qwen2-based, code-specialised embedding |
| Parameters | ~7B |
| Native context | 32,768 tokens |
| Status | downloaded; never test-loaded |

## Source

Pulled 2026-05-26 as the **code-specialised** embedding option. Prose embedders perform poorly on code (different vocabulary distribution, structural patterns, identifier conventions); a code-trained embedder substantially improves retrieval over codebases.

Built on Qwen2 base, fine-tuned on code corpora. The 27 GB disk size reflects FP16 weights for a ~7B model plus the multiple shards and indexing artifacts.

## Fits these needs

- [[_models-index#Code embedding for codebase / repo retrieval|Code embedding for codebase / repo retrieval]] — the substrate's option for this role

## Tested performance

Not yet served. *To characterise:*

- Loads cleanly via vLLM `--runner pooling`?
- Embedding dimension
- Concurrent throughput
- Quality on Tim-relevant code (Vi codebase, Obsidian plugin code, etc.) vs the prose embedders attempting the same task
- Whether the model handles non-English identifiers / comments well
- Practical chunk size for typical source files (functions, classes, files, repos)

## Known-good launch config

Not yet defined. Cannot co-exist with the chat default at this size — swap-only.

```
vllm serve nomic-ai/nomic-embed-code \
  --port 8001 \
  --runner pooling \
  --gpu-memory-utilization <large; ~14 GB weights at FP16> \
  --max-model-len 32768 \
  --trust-remote-code
```

If served as the embed default, [[bge-m3]] would swap out — losing multi-output and prose-quality. Likely deployment pattern is **on-demand**: bring up only when indexing or querying code, swap back to BGE-M3 for general embedding work.

## Quirks

- **Large for an embedder.** 7B params is large; concurrent throughput will be much lower than BGE-M3 (sub-billion params).
- **Code-only specialisation.** Quality on prose may be substantially worse than a general embedder. Routing decisions (which embedder for which content) become important.
- **Disk-to-VRAM relationship.** 27 GB on disk does not mean 27 GB VRAM — FP16 weight expansion plus optimiser-state-shards typical of training checkpoints can inflate disk size. At inference, expect ~14 GB VRAM.

## Open at this entry

- Everything operational. Never loaded.
- Whether to deploy on-demand vs swap-only vs run-alongside (the VRAM math is tight)
- Quality on Tim's code corpora — the question this model exists to answer
- Routing strategy for mixed-content embedding (e.g. Vi codebase with markdown docs + code) — code chunks to this, prose chunks to BGE-M3, but the routing logic is open

## Connects to

- [[_models-index]] — hub
- [[bge-m3]] — would swap out if deployed
- [[../operations/runtimes]] — vLLM `--runner pooling`
- [[../operations/vllm-stack-cli]] — `swap-embed` procedure
