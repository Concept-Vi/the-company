---
type: model
id: Qwen/Qwen3-Embedding-8B
filename: qwen3-embedding-8b
status: downloaded
runtime: not-yet-served
date_added: 2026-05-26
tags: [foundation, models, embedding, large]
---

# Qwen3-Embedding-8B

> [[_models-index|← Models hub]] · linked from: general dense embedding (flagship)

## At a glance

| Field | Value |
|---|---|
| HF id | `Qwen/Qwen3-Embedding-8B` |
| Disk | 15 GB |
| Quant | FP16 |
| Architecture | Qwen3 dense, embedding-tuned |
| Parameters | 8B |
| Status | downloaded; never test-loaded |

## Source

Pulled 2026-05-26 because it was the **top MTEB multilingual embedder at the time of pull** (Multilingual MTEB ~70.58). The flagship-quality option in the embedding slot.

Note that Qwen3-Embedding is named for **Qwen 3**, not Qwen 3.5 or 3.6 — separate, embedding-specialised model line.

## Fits these needs

- [[_models-index#General dense text embedding for semantic search|General dense text embedding]] — would be a quality upgrade over [[bge-m3]] for general semantic search if served

## Tested performance

Not yet served. *To characterise:*

- Does it load via vLLM `--runner pooling`?
- Embedding dimension (Qwen3-Embedding family has multiple sizes; 8B is the largest)
- Concurrent throughput — expected lower than BGE-M3 (much larger model, no multi-output free)
- Quality vs BGE-M3 on representative Tim-relevant text
- Instruction-aware behaviour (Qwen3-Embedding supports task instructions on the query side)
- Context length

## Known-good launch config

Not yet defined. Provisional pattern:

```
vllm serve Qwen/Qwen3-Embedding-8B \
  --port 8001 \
  --runner pooling \
  --gpu-memory-utilization <large; weights alone are ~15 GB at FP16> \
  --trust-remote-code
```

VRAM cost is significant — 8B at FP16 is ~16 GB just for weights. Either:

- Swap out [[bge-m3]] and serve this in its place (loses multi-output sparse/ColBERT capability)
- Find a quantised variant (Qwen has FP8 / AWQ embedders in some sub-families)
- Run with [[qwen3_5-4b-awq]] stopped (frees ~12 GB)

## Quirks

- **Big embedder.** 8B parameter scale is unusual for an embedder; most production embedders are 100M–1B. The quality justifies the size but the throughput tax is real.
- **Instruction-aware on query side only.** Standard Qwen pattern: prepend task instructions to queries, not to documents.
- **Quality leadership claim is point-in-time.** MTEB leaderboard moves; whether this model is still leading at the time of any future evaluation is an open question.

## Open at this entry

- Everything operational. Never loaded.
- Whether the quality gain over BGE-M3 justifies the VRAM trade for Tim's specific corpora
- Whether a smaller Qwen3-Embedding sibling (e.g. 600M / 1.5B / 4B variants if they exist in the family) would be a better fit at less VRAM cost
- Whether dropping the multi-output capability of BGE-M3 in favour of pure dense quality is the right trade

## Connects to

- [[_models-index]] — hub
- [[bge-m3]] — current default; the comparison this model would justify or fail
- [[jina-embeddings-v5-text-small]] — alternative smaller candidate
- [[../operations/runtimes]] — vLLM `--runner pooling`
