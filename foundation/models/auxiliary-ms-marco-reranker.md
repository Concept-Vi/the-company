---
type: model
id: cross-encoder/ms-marco-MiniLM-L-6-v2
filename: auxiliary-ms-marco-reranker
status: auxiliary
runtime: not-yet-served
date_added: present-before-substrate-setup
tags: [foundation, models, reranker, auxiliary]
---

# ms-marco MiniLM L6 v2 (reranker)

> [[_models-index|← Models hub]] · auxiliary; cross-encoder reranker

## At a glance

| Field | Value |
|---|---|
| HF id | `cross-encoder/ms-marco-MiniLM-L-6-v2` |
| Disk | 88 MB |
| Architecture | 6-layer MiniLM cross-encoder, MS-MARCO-trained for passage ranking |
| Status | present on disk; reranker, not embedder |

## Source

Present in the HF cache prior to deliberate substrate setup. A canonical small reranker — cross-encoders re-score candidate pairs of (query, document) for higher-precision retrieval after a fast initial dense-embedding-based candidate generation.

## Fits these needs

- **Reranking** isn't yet a top-level need-category in the hub but it's a real production pattern. The two-stage retrieval pipeline (dense retrieve top-N → cross-encoder rerank top-K) is what most quality-sensitive RAG systems do.
- Surfacing as a candidate for an explicit `Reranking` need-category in the hub when the need actually arises in Tim's work.

## Open at this entry

- Whether to elevate "reranking" to a named need-category in the hub
- Performance characteristics of this specific reranker
- Whether a bigger reranker (e.g. a Qwen-based one) would be a better default

## Connects to

- [[_models-index]] — hub
