---
type: model
id: jinaai/jina-embeddings-v5-text-small
filename: jina-embeddings-v5-text-small
status: tested
runtime: vllm
date_added: 2026-05-26
date_last_characterised: 2026-05-26
tags: [foundation, models, embedding]
---

# Jina Embeddings v5 — Text Small

> [[_models-index|← Models hub]] · linked from: general dense text embedding

## At a glance

| Field | Value |
|---|---|
| HF id | `jinaai/jina-embeddings-v5-text-small` |
| Disk | 1.3 GB |
| Quant | FP16 |
| Architecture | `JinaEmbeddingsV5Model` — supported by vLLM 0.21 |
| Embedding dim | 1024 |
| Parameters | ~677M |
| Native context | 8,192 tokens |
| Status | tested loading + semantic check; not currently deployed |

## Source

Pulled 2026-05-26 as the small-fast instruction-aware alternative to [[bge-m3]]. v5 is supported natively by vLLM (v4 is not — see [[jina-embeddings-v4]] for why a separate venv exists).

## Fits these needs

- [[_models-index#General dense text embedding for semantic search|General dense text embedding]] — alternative to BGE-M3, smaller and faster per-request, instruction-aware via task adapters

## Tested performance (2026-05-26)

Loaded cleanly via vLLM `--runner pooling`. Semantic check on the same probe used for [[bge-m3]]:

| Pair | Cosine sim |
|---|---|
| "cat" vs "feline" | 0.682 |
| "cat" vs "stocks" | 0.081 |

The 0.081 for unrelated text is a sharper separation than BGE-M3's 0.404 — the v5 small does cleaner semantic discrimination on this probe than the much larger M3.

Concurrent throughput not measured.

## Known-good launch config

Same pattern as [[bge-m3]] — `vllm serve jinaai/jina-embeddings-v5-text-small --runner pooling --port <port> --trust-remote-code`.

Currently not deployed because the embed slot is held by BGE-M3 (multi-output capability tips the default toward M3 for the substrate's general role). Swap via `vllm-stack swap-embed jinaai/jina-embeddings-v5-text-small`.

## Quirks

- v5 architecture is the **vLLM-supported** Jina embedder. v4 is not. This drives an architectural split: text-only / vLLM-served = v5; multimodal / standalone-served = v4. The substrate accommodates both.
- Instruction-aware: prepend task instructions on the query side, not document side. Standard Jina pattern.
- 677M params is small enough that running it alongside other services on this substrate is comfortable VRAM-wise.

## Open at this entry

- Concurrent throughput characterisation
- Direct head-to-head retrieval quality vs BGE-M3 on Tim's actual corpora
- Whether the cleaner separation on the synthetic probe translates to better retrieval on Tim's data

## Connects to

- [[_models-index]] — hub
- [[bge-m3]] — current default; semantic-check comparison documented
- [[jina-embeddings-v4]] — multimodal sibling; runtime-incompatible with vLLM
