---
type: model
id: Qwen/Qwen3.5-0.8B
filename: qwen3_5-0_8b
status: tested
runtime: vllm
date_added: 2026-05-26
date_last_characterised: 2026-05-26
tags: [foundation, models, chat, small]
---

# Qwen3.5-0.8B

> [[_models-index|← Models hub]] · linked from: high-throughput chat (extreme-concurrency variant)

## At a glance

| Field | Value |
|---|---|
| HF id | `Qwen/Qwen3.5-0.8B` |
| Disk | 1.7 GB |
| Quant | BF16 weights |
| Architecture | Vision-language; hybrid Mamba-attention; chat-tuned |
| Native context | 262,144 tokens |
| Tested context | 4K |
| Per Qwen README | "Intended for prototyping, fine-tuning, research" |
| Status | tested; not currently deployed |

## Source

Pulled 2026-05-26 from upstream Qwen. Acts as the high-concurrency / low-quality counterpart to [[qwen3_5-4b-awq]] for jobs where throughput at scale matters more than per-request quality.

## Fits these needs

- [[_models-index#High-throughput chat for batch / mass-parallel work|High-throughput chat]] — when extreme concurrency on short prompts matters more than per-request quality. Useful for classification / routing / triage workloads.

## Tested performance (2026-05-26)

Three-prompt batch with corrected chat API, no `enforce_eager`:

| Metric | Value |
|---|---|
| Load time | 150.8 s (cold; torch.compile + Mamba kernel JIT) |
| Generation time (3 prompts, 91 tokens) | 8.61 s |
| Aggregate tok/s (3-batch) | 10.6 |
| Single-batch peak output rate | 89 tok/s |
| KV cache @ 4K context | 649,774 tokens — **158x max concurrency at 4K per-request** |

The 158x concurrency capacity is the standout. For jobs that can use a small-model output (binary classification, routing, intent detection), this model serves many more concurrent requests per second of GPU time than the 4B does.

Output coherent across all three test prompts (verified semantically — Paris answer, vector DB explanation, Pythagorean theorem statement).

Detailed concurrency sweep at production scale not run because the 4B AWQ took the deployment slot.

## Known-good launch config

Not currently deployed. To swap in:

```
vllm-stack swap-chat Qwen/Qwen3.5-0.8B
```

The existing `serve.sh` config (port 8000, `--enable-prefix-caching`, `--enable-auto-tool-choice --tool-call-parser qwen3_xml`, `--chat-template ~/vllm-tests/chat_template_nothink.jinja`) should work unchanged — same family as the 4B.

Per-model VRAM budget (1.7 GB weights) leaves enormous KV cache room. Could raise `--max-num-seqs` to 256+ to actually exploit the 158x concurrency capacity (currently default 64).

## Quirks

- Same chat-template / thinking-mode pattern as [[qwen3_5-4b-awq]] — the patched template applies cleanly.
- Same VL architecture — vision tower bears VRAM cost regardless of input modality.
- Small enough that output quality is noticeably below the 4B on open-ended prompts. Per the Qwen team's own README, the model is positioned as a research / prototyping artifact, not a production chat default.

## Open at this entry

- Production-scale concurrency sweep at the model's actual ceiling (could be far above 32–64)
- Tool calling reliability at this parameter scale — known to degrade on small models; untested specifically
- Structured output reliability at this parameter scale — same caveat
- Use case profile: which Tim-workloads actually want this model over the 4B, and which would simply lose too much quality

## Connects to

- [[_models-index]] — hub
- [[qwen3_5-4b-awq]] — sibling; the deployed default
- [[../operations/vllm-stack-cli]] — `swap-chat` to deploy
