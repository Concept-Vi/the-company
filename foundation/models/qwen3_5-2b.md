---
type: model
id: Qwen/Qwen3.5-2B
filename: qwen3_5-2b
status: downloaded
runtime: not-yet-served
date_added: 2026-05-26
tags: [foundation, models, chat]
---

# Qwen3.5-2B

> [[_models-index|← Models hub]] · linked from: high-throughput chat (text-only intermediate)

## At a glance

| Field | Value |
|---|---|
| HF id | `Qwen/Qwen3.5-2B` |
| Disk | 4.3 GB |
| Quant | BF16 |
| Architecture | Text-only base (no vision tower) |
| Status | downloaded; never test-loaded |

## Source

Pulled 2026-05-26 specifically because it is **text-only** — the [[qwen3_5-4b-awq|4B]], [[qwen3_5-0_8b|0.8B]], and 9B Qwen3.5 variants all carry a vision tower that bears VRAM cost even when only text is used. The 2B drops that cost.

This is a `-Base` model (not instruct-tuned); to chat-tune it would require either picking up the `-Base` and fine-tuning, or finding a community chat variant.

## Fits these needs

- [[_models-index#High-throughput chat for batch / mass-parallel work|High-throughput chat]] — potential candidate, contingent on instruct-tuning. Larger than 0.8B, smaller than 4B, no vision tax.

## Tested performance

Not yet test-loaded. *To characterise:*

- Does base model load cleanly in vLLM?
- Does the patched chat template apply?
- Without instruct-tuning, can it produce useful chat output at all? (Likely needs significant prompt engineering or a wrapped fine-tune.)
- Throughput characteristics if loaded with same `serve.sh` flags as the 4B.
- KV cache size at 4K context (expected: substantially larger than the 4B due to smaller weights — could push max concurrency well above 32–64).

## Open at this entry

- Whether the base variant is useful without fine-tuning, or whether to find a community instruct-tuned 2B
- Whether 2B-class capacity is enough quality for Tim's workloads
- Whether the text-only-no-VL property actually translates into measurable throughput gain over the 4B AWQ (in practice the AWQ-quantised 4B may still match this in tok/s while delivering better quality)

## Connects to

- [[_models-index]] — hub
- [[qwen3_5-4b-awq]], [[qwen3_5-0_8b]] — siblings
