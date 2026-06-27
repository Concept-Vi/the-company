---
type: model
id: stelterlab/NVIDIA-Nemotron-3-Nano-30B-A3B-AWQ
filename: nemotron-3-nano-30b-a3b-awq
status: downloaded
runtime: not-yet-served
date_added: 2026-05-26
tags: [foundation, models, chat, awq, moe]
---

# NVIDIA Nemotron-3-Nano-30B-A3B-AWQ

> [[_models-index|← Models hub]] · linked from: high-throughput chat (AWQ-on-vLLM MoE candidate)

## At a glance

| Field | Value |
|---|---|
| HF id | `stelterlab/NVIDIA-Nemotron-3-Nano-30B-A3B-AWQ` |
| Disk | 17 GB |
| Architecture | NVIDIA Nemotron 3 Nano family; MoE 30B total, ~3B active per token; **Hybrid Mamba-attention** |
| Quant | AWQ |
| Status | downloaded; never test-loaded |

## Source

Pulled 2026-05-26 as the AWQ-on-vLLM MoE candidate. Direct competitor to [[qwen3_6-35b-a3b-gguf-q3-k-m]] for the throughput-MoE role, but on a runtime path (vLLM) that historically handles concurrent batched serving far better than Ollama's GGUF path.

NVIDIA Nemotron family is built on hybrid Mamba-attention (same family as Qwen3.5) but trained on NVIDIA's data mix and post-trained differently — distinct behavioural profile, distinct tool-calling format, distinct knowledge weighting.

## Fits these needs

- [[_models-index#High-throughput chat for batch / mass-parallel work|High-throughput chat]] — the AWQ-on-vLLM MoE candidate. If this fits in 16 GB and serves at vLLM's batched-concurrency rates, it would substantially outperform any Ollama-served alternative.

## Tested performance

Not yet test-loaded. The model is large (17 GB on disk including non-weight artifacts) — fit on 16 GB VRAM with KV cache is **unverified**. Could be the throughput winner; could OOM at load.

*To characterise:*

- Does it load in vLLM 0.21? AWQ + Nemotron-3 architecture support in this version is unverified
- VRAM at load — 17 GB on disk likely means 13–14 GB weights + tokenizer/etc; should fit but with very tight KV margin
- Concurrent throughput — expected closer to a 3B dense AWQ model in tok/s/req, with knowledge near 30B; this is the hypothesis the throughput-MoE bet rests on
- Tool calling — Nemotron has its own tool-call format; vLLM has a Nemotron-specific parser (not the Qwen `qwen3_xml` we use for the default)
- Chat template — Nemotron has its own; the no-think patch built for Qwen is not directly applicable

## Known-good launch config

Not yet defined. Provisional pattern (untested):

```
vllm serve stelterlab/NVIDIA-Nemotron-3-Nano-30B-A3B-AWQ \
  --port 8000 \
  --gpu-memory-utilization 0.92 \
  --max-model-len 4096 \
  --max-num-seqs <tbd — start at 32, raise if KV cache permits> \
  --enable-prefix-caching \
  --enable-auto-tool-choice \
  --tool-call-parser <find Nemotron-specific> \
  --trust-remote-code
```

Cannot co-exist with the current default chat — swap-only deployment (`vllm-stack swap-chat ...`).

## Quirks

- **NVIDIA's chat template will differ from Qwen's.** The no-think patch at `~/vllm-tests/chat_template_nothink.jinja` is Qwen-specific. Nemotron will need its own template handling — possibly straightforward (no thinking mode at all) or possibly different reasoning-mode controls.
- **17 GB on disk is borderline for 16 GB VRAM.** AWQ packs efficiently but bring up may be tight.
- **Behaviourally distinct from Qwen.** Different knowledge cutoff, different post-training, likely different tool-calling reliability. Worth Tim-relevant testing rather than benchmark-proxy testing.

## Open at this entry

- Everything operational. Never loaded.
- The right tool parser for vLLM
- Whether NVIDIA shipped a thinking / non-thinking variant or this is the only one
- Comparison vs the Qwen MoE GGUF variants on matched workloads — the central question this model exists to answer

## Connects to

- [[_models-index]] — hub
- [[qwen3_6-35b-a3b-gguf-q3-k-m]] — direct competitor (GGUF / Ollama route)
- [[qwen3_5-4b-awq]] — would displace from default chat slot if proven
- [[../operations/runtimes]] — vLLM serving details
- [[../operations/vllm-stack-cli]] — `swap-chat` procedure
