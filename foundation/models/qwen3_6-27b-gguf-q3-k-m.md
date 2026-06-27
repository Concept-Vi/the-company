---
type: model
id: unsloth/Qwen3.6-27B-GGUF (Q3_K_M variant)
filename: qwen3_6-27b-gguf-q3-k-m
status: downloaded
runtime: ollama
ollama_name: qwen3.6-27b-q3km:latest
date_added: 2026-05-27
tags: [foundation, models, chat, gguf]
---

# Qwen3.6-27B — GGUF Q3_K_M

> [[_models-index|← Models hub]] · linked from: single-stream high-quality reasoning · long-context document QA

## At a glance

| Field | Value |
|---|---|
| HF id | `unsloth/Qwen3.6-27B-GGUF` |
| File | `Qwen3.6-27B-Q3_K_M.gguf` (12.7 GB) |
| Disk (snapshot symlink) | 13 GB |
| Architecture | Dense 27B |
| Quant | GGUF Q3_K_M |
| Ollama tag | `qwen3.6-27b-q3km:latest` |
| Endpoint | `http://localhost:11434/v1` |
| Status | downloaded + registered with Ollama; never load-tested or benchmarked |

## Source

Pulled 2026-05-27 as the **dense, text-only** large-model option for single-stream high-quality work. Distinct from the [[qwen3_6-35b-a3b-gguf-q3-k-m|35B MoE]] which optimises for throughput; this is the per-request-quality option at moderate scale.

## Fits these needs

- [[_models-index#Single-stream high-quality reasoning (low concurrency, high capability)|Single-stream high-quality reasoning]] — dense 27B has higher per-request capability than the MoE-active-3B variants
- [[_models-index#Long-context document QA / RAG|Long-context document QA]] — Qwen3.6 family supports long context; specific limit via Ollama unverified

## Tested performance

Registered with Ollama 2026-05-27. **Never load-tested. No throughput numbers. No coherence verification.**

*To characterise:*

- Loads cleanly at 12.7 GB into 16 GB VRAM with KV headroom for what context length?
- Single-stream tok/s — expected slow (dense 27B is heavy compute per token)
- Quality versus [[qwen3_5-4b-awq]] on Tim's typical queries (the expected upside — capability gap)
- Long-context recall — needle-in-haystack at multi-thousand-token depths
- Tool calling reliability via Ollama / GGUF path

## Known-good launch config

```
curl http://localhost:11434/v1/chat/completions \
  -d '{"model":"qwen3.6-27b-q3km","messages":[{"role":"user","content":"..."}]}'
```

## Quirks

- **Dense, not MoE.** Every parameter computes for every token. No throughput trick — runtime is dense 27B speed at Q3_K_M precision.
- Q3_K_M quantisation loses some quality vs higher-bit variants but is the choice that fits 16 GB with usable KV cache margin.

## Open at this entry

- Everything operational. Model is registered but unmeasured.
- Single-stream latency profile — likely the slowest model on the substrate per request
- Whether the quality gain over the 4B AWQ justifies the latency cost for any specific Tim-workload
- Cloud-route comparison — at this scale + quality, cloud routes via Ollama may be competitive or better depending on cost tolerance

## Connects to

- [[_models-index]] — hub
- [[qwen3_6-35b-a3b-gguf-q3-k-m]] — MoE alternative (throughput-optimised)
- [[../operations/ollama]] — registration procedure
- [[../operations/runtimes]] — Ollama runtime
