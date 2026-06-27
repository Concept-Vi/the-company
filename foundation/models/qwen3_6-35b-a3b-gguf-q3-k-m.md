---
type: model
id: unsloth/Qwen3.6-35B-A3B-GGUF (Q3_K_M variant)
filename: qwen3_6-35b-a3b-gguf-q3-k-m
status: downloaded
runtime: ollama
ollama_name: qwen3.6-35b-a3b-q3km:latest
date_added: 2026-05-27
tags: [foundation, models, chat, gguf, moe]
---

# Qwen3.6-35B-A3B — GGUF Q3_K_M

> [[_models-index|← Models hub]] · linked from: high-throughput chat · single-stream high-quality reasoning

## At a glance

| Field | Value |
|---|---|
| HF id | `unsloth/Qwen3.6-35B-A3B-GGUF` |
| File | `Qwen3.6-35B-A3B-UD-Q3_K_M.gguf` (15.5 GB) |
| Disk (snapshot symlink) | 16 GB |
| Architecture | MoE: 35B total, ~3B active per token |
| Quant | GGUF Q3_K_M (3-bit k-quant medium, unsloth dynamic) |
| Ollama tag | `qwen3.6-35b-a3b-q3km:latest` |
| Native context | (Qwen3.6 family — typically 256K+; verify on Ollama side) |
| Endpoint | `http://localhost:11434/v1` (Ollama OpenAI-compat) |
| Status | downloaded + registered with Ollama; never load-tested or benchmarked |

## Source

Pulled 2026-05-27 from unsloth's GGUF distribution. unsloth provides dynamic-quant variants ("UD") with calibration tweaks that often hold quality better than vanilla GGUF at equivalent bit depth.

This variant chosen because:
- 15.5 GB fits within 16 GB VRAM with thin KV margin (Q3_K_M is the highest-bit variant that fits the 4080)
- MoE 3B-active means runtime tok/s closer to a 3B dense model, with knowledge near 35B
- Q3_K_M is the conservative "still good quality" middle of the GGUF range; [[qwen3_6-35b-a3b-gguf-iq3-s|IQ3_S]] is the lower-bit fallback if Q3_K_M doesn't fit at runtime

The Ollama-on-port-11434 path is the runtime, not vLLM — vLLM does not natively serve GGUF in 0.21.

## Fits these needs

- [[_models-index#High-throughput chat for batch / mass-parallel work|High-throughput chat]] — the MoE-throughput candidate via Ollama
- [[_models-index#Single-stream high-quality reasoning (low concurrency, high capability)|Single-stream high-quality reasoning]] — by capability tier, this is the largest local model on the substrate after the dense 27B

## Tested performance

Registered with Ollama 2026-05-27 (visible in `ollama list`). **Never load-tested. No throughput numbers. No coherence verification.**

*To characterise:*

- Does Ollama load it cleanly at 15.5 GB into 16 GB VRAM, or does it spill to CPU?
- Single-stream tok/s — expected closer to a 3B dense model
- Concurrent throughput via Ollama (Ollama's batching is far less efficient than vLLM's; the practical ceiling may be much lower than the architecture would suggest)
- Tool calling — Ollama exposes OpenAI-compat tool calls; the Qwen3.6 family supports them but compatibility through the GGUF + Ollama path is unverified
- Quality versus [[qwen3_5-4b-awq]] on Tim's typical queries
- Native context length as Ollama exposes it (may differ from upstream)

## Known-good launch config

Registered as `qwen3.6-35b-a3b-q3km:latest`. Accessible via:

```
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen3.6-35b-a3b-q3km","messages":[{"role":"user","content":"..."}]}'
```

Open WebUI on port 8080 auto-discovers Ollama models if its Ollama connection is enabled (see [[../operations/open-webui]]).

To swap into the chat-default slot via vLLM is **not possible** — this is a GGUF file, vLLM doesn't serve it. The model lives in Ollama; if it becomes the default chat path, the chat endpoint moves to port 11434 instead of 8000.

## Quirks

- **MoE routing means VRAM stays high even when computation is small.** All 35B weights must be resident on GPU; the "3B active" means computation per token is 3B-scale but memory is 35B-scale.
- **GGUF on Ollama is single-process.** Concurrent requests are queued, not batched the way vLLM batches. For high-throughput workloads this is a real limitation; for the single-stream / reasoning use case it's a non-issue.
- **Dynamic-quant ("UD") variants** are unsloth's calibrated quants. They retain quality better than vanilla GGUF Q3_K_M but the calibration may not match every workload's distribution.

## Open at this entry

- Everything operational. The model is registered but unmeasured.
- The choice between Q3_K_M and [[qwen3_6-35b-a3b-gguf-iq3-s|IQ3_S]] is currently theoretical; head-to-head needed.
- Whether Ollama's serving path makes this faster or slower than the [[nemotron-3-nano-30b-a3b-awq]] candidate (which would run via vLLM)
- Tool-calling compatibility through the Ollama path
- Long-context behaviour
- Cloud-route alternatives (`qwen3.5:397b-cloud` is much larger and Ollama-routed; cost / quality / latency tradeoff vs this local variant unmeasured)

## Connects to

- [[_models-index]] — hub
- [[../operations/runtimes]] — Ollama runtime
- [[qwen3_6-35b-a3b-gguf-iq3-s]] — lower-bit sibling
- [[qwen3_6-27b-gguf-q3-k-m]] — dense alternative
- [[nemotron-3-nano-30b-a3b-awq]] — competing 3B-active MoE; would serve via vLLM
