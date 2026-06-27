---
type: model
id: BAAI/bge-m3
filename: bge-m3
status: deployed-default
runtime: vllm
port: 8001
date_added: 2026-05-26
date_last_characterised: 2026-05-26
tags: [foundation, models, embedding, deployed]
---

# BGE-M3

> [[_models-index|← Models hub]] · linked from: general dense embedding · sparse / lexical embedding · multi-vector / ColBERT retrieval

## At a glance

| Field | Value |
|---|---|
| HF id | `BAAI/bge-m3` |
| Disk | 4.3 GB |
| Quant | FP16 weights |
| Architecture | Transformer encoder; **three output heads**: dense + sparse + ColBERT |
| Dense dim | 1024 |
| Sparse | learned token-importance weights (variable nonzeros per chunk) |
| ColBERT | ~30 vectors per chunk at 128-d each (multi-vector late interaction) |
| Native context | 8,192 tokens |
| VRAM | ~2.7 GiB at deployed config |
| Service unit | `vllm-embed.service` |
| Endpoint | `http://localhost:8001/v1` |

## Source

Pulled 2026-05-26 from BAAI as the multi-output default for the substrate. Multilingual (100+ languages). Multi-head output from a single forward pass is the key property — saves compute when sparse and ColBERT are also needed.

## Fits these needs

- [[_models-index#General dense text embedding for semantic search|General dense text embedding]] — the default for this role
- [[_models-index#Sparse / lexical embedding (exact term matching)|Sparse / lexical embedding]] — via `FlagEmbedding` library (the vLLM endpoint exposes only the dense head)
- [[_models-index#Multi-vector / ColBERT-style precise retrieval|ColBERT multi-vector retrieval]] — same as sparse: needs FlagEmbedding

## Tested performance (2026-05-26)

Concurrent embedding throughput (batch=8 per request):

| Concurrency | Embeddings/s | Req/s | Tokens/s | Latency p50 | Latency p95 |
|---|---|---|---|---|---|
| 8 | 678 | 169.5 | 12,418 | 37ms | 111ms |
| 32 | 1,375 | 171.8 | 25,173 | 177ms | 228ms |
| 64 | 1,367 | 170.8 | 25,027 | 338ms | 509ms |

Saturates around concurrency 32 at ~1,370 embed/s; beyond that, latency rises but req/s plateaus (server-side batching ceiling reached).

Co-resident test with [[qwen3_5-4b-awq]] under simultaneous load (both at concurrency 32): embed sustained 1,006–1,290 emb/s while chat sustained 1,860–1,991 tok/s. 100% success on both. GPU 86–97% util.

Semantic check: `sim(cat, feline) = 0.624` vs `sim(cat, stocks) = 0.404` — clear separation, weaker than [[jina-embeddings-v5-text-small]]'s separation (0.682 / 0.081) on the same probe.

## Known-good launch config

Defined in `~/vllm-tests/serve_embed.sh`; managed by `~/.config/systemd/user/vllm-embed.service`.

```
vllm serve BAAI/bge-m3 \
  --port 8001 \
  --host 0.0.0.0 \
  --runner pooling \
  --gpu-memory-utilization 0.30 \
  --trust-remote-code
```

`--runner pooling` (vLLM 0.21) replaces the older `task="embed"` from earlier versions. `--gpu-memory-utilization 0.30` leaves room for the co-resident chat server; this is allocation budget, not actual usage.

## Quirks

- **vLLM endpoint serves only the dense head.** Sparse and ColBERT outputs require the `FlagEmbedding` library (`BGEM3FlagModel`) running as a sidecar process. Two paths forward when sparse/ColBERT are needed:
  - Sidecar process via FlagEmbedding (separate port, separate process; can co-locate on this machine)
  - Recompute sparse/ColBERT in the same forward pass at index time and store all three vector kinds in the vector DB (Qdrant supports named vectors)
- **Different similarity profile than [[jina-embeddings-v5-text-small]].** BGE-M3 dense alone returned 0.404 for "cat" vs "stocks" — semantically distinct text, but the dense embedding still placed them noticeably close. Hybrid retrieval (dense + sparse) is the production pattern; pure dense is weaker for hard cases.
- **8K context is the model's training cap.** Documents longer than 8K need chunking before embedding; the model will not error on longer inputs but quality degrades.

## Open at this entry

- Sparse / ColBERT serving path: vLLM doesn't expose; production design (FlagEmbedding sidecar vs index-time multi-vector storage) open
- Head-to-head comparison vs [[qwen3-embedding-8b]] (downloaded but never served) and [[jina-embeddings-v5-text-small]] on Tim's actual corpora — not done
- Optimal chunk size for Obsidian markdown / Xero text / code — open; depends on retrieval mode
- Whether hybrid retrieval (BGE-M3 dense + BGE-M3 sparse) outperforms BGE-M3 dense + a domain-specific embedder for Tim's use cases

## Connects to

- [[_models-index]] — hub
- [[../operations/runtimes]] — vLLM embedding serving via `--runner pooling`
- [[qwen3_5-4b-awq]] — co-resident service
- [[jina-embeddings-v4]] — multimodal alternative
- [[qwen3-embedding-8b]] — flagship alternative (untested)
- Source archive: `~/vllm-tests/EMBEDDING_STRATEGIES.md`
