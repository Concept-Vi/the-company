---
type: model
id: unsloth/Qwen3.6-35B-A3B-GGUF (IQ3_S variant)
filename: qwen3_6-35b-a3b-gguf-iq3-s
status: downloaded
runtime: not-yet-served
date_added: 2026-05-27
tags: [foundation, models, chat, gguf, moe]
---

# Qwen3.6-35B-A3B — GGUF IQ3_S

> [[_models-index|← Models hub]] · linked from: high-throughput chat (lower-bit fallback)

## At a glance

| Field | Value |
|---|---|
| HF id | `unsloth/Qwen3.6-35B-A3B-GGUF` |
| File | `Qwen3.6-35B-A3B-UD-IQ3_S.gguf` (12.7 GB) |
| Disk (snapshot symlink) | 13 GB |
| Architecture | MoE: 35B total, ~3B active per token |
| Quant | GGUF IQ3_S (importance-weighted 3-bit, unsloth dynamic) |
| Ollama tag | not yet registered |
| Status | downloaded; not yet registered with Ollama |

## Source

Pulled 2026-05-27 alongside [[qwen3_6-35b-a3b-gguf-q3-k-m]] as the lower-bit fallback. If Q3_K_M's 15.5 GB doesn't actually fit at runtime once Ollama adds its own KV cache, IQ3_S provides ~3 GB more headroom at the cost of slightly more quantisation error.

IQ-quants ("importance-weighted") allocate bits more carefully than the K-quants — IQ3_S often produces better quality than Q3_K_S at the same bit depth, though slightly worse than Q3_K_M.

## Fits these needs

- [[_models-index#High-throughput chat for batch / mass-parallel work|High-throughput chat]] — same architectural role as Q3_K_M variant, lower quality / more headroom

## Tested performance

Not yet served. *To characterise:*

- Quality difference vs Q3_K_M on Tim's typical queries
- VRAM headroom (likely 3 GB more than Q3_K_M, opening room for either larger KV cache or additional services co-resident)
- Whether the quality loss is noticeable for the intended use cases

## Known-good launch config

To register with Ollama:

```
ollama create qwen3.6-35b-a3b-iq3s -f Modelfile
# where Modelfile points FROM /home/tim/.cache/huggingface/hub/.../Qwen3.6-35B-A3B-UD-IQ3_S.gguf
```

Pattern repeats the registration done for [[qwen3_6-35b-a3b-gguf-q3-k-m]]; see [[../operations/ollama]] for the exact procedure.

## Quirks

- Same MoE memory pattern as Q3_K_M sibling — all 35B weights resident on GPU.
- IQ-quants compute slightly differently than K-quants; per-token latency could be marginally different (untested).

## Open at this entry

- Direct head-to-head quality vs Q3_K_M on representative tasks
- VRAM headroom value: does the extra ~3 GB enable a meaningfully different deployment (larger context, co-resident with another service, etc.)?
- Whether keeping both Q3_K_M and IQ3_S on disk long-term is worth it, or whether one variant settles as the keep

## Connects to

- [[_models-index]] — hub
- [[qwen3_6-35b-a3b-gguf-q3-k-m]] — sibling (higher-bit, registered)
- [[../operations/ollama]] — registration procedure
