---
type: model
id: unsloth/gemma-4-26B-A4B-it-GGUF (Q3_K_M variant)
filename: gemma-4-26b-a4b-gguf-q3-k-m
status: downloaded
runtime: not-yet-served
date_added: 2026-05-27
tags: [foundation, models, chat, gguf, moe, multimodal]
---

# Gemma-4-26B-A4B-it — GGUF Q3_K_M

> [[_models-index|← Models hub]] · linked from: single-stream high-quality reasoning · multimodal (potentially)

## At a glance

| Field | Value |
|---|---|
| HF id | `unsloth/gemma-4-26B-A4B-it-GGUF` |
| File | `gemma-4-26B-A4B-it-UD-Q3_K_M.gguf` (12 GB) |
| Disk (snapshot symlink) | 12 GB |
| Architecture | Gemma 4 — MoE with 4B active per token; upstream Gemma 4 family supports omnimodal (text + vision + audio) but GGUF retention of non-text modalities is unverified |
| Quant | GGUF Q3_K_M (unsloth dynamic) |
| Ollama tag | not yet registered |
| Status | downloaded; not yet registered with Ollama |

## Source

Pulled 2026-05-27 as a **non-Qwen** alternative for the chat slot — different model lineage, different training data, different behavioural characteristics. Useful as a comparison point and as a backup option if any Qwen-family-specific issue surfaces.

The full-precision [[gemma-4-e4b-fp8|Gemma-4-E4B-FP8]] was tested 2026-05-26 and confirmed multimodal but removed from disk after that session. This 26B-A4B GGUF is a larger sibling at a smaller bit depth.

## Fits these needs

- [[_models-index#Single-stream high-quality reasoning (low concurrency, high capability)|Single-stream high-quality reasoning]] — non-Qwen alternative at the 26B / Q3_K_M scale
- [[_models-index#Multimodal: text + audio|Multimodal: text + audio]] — gestured-at; the underlying architecture supports it but whether the GGUF retains it is unverified

## Tested performance

Not yet served. *To characterise:*

- Loads cleanly via Ollama at 12 GB on the 4080?
- Behavioural difference vs Qwen models on Tim's typical queries (Gemma 4's tonal / structural defaults are distinctly different from Qwen)
- Does the GGUF retain omnimodal capability or is it text-only after the conversion?
- Tool calling reliability via Ollama
- Concurrent throughput at this MoE scale (4B active vs 3B active in the Qwen MoE — minor difference)

## Known-good launch config

To register:

```
ollama create gemma-4-26b-a4b-q3km -f Modelfile
# Modelfile FROM the GGUF path
```

## Quirks

- **A4B (4B-active)** is between [[qwen3_6-35b-a3b-gguf-q3-k-m|Qwen 3B-active]] and dense models in compute-per-token. Slightly slower than Qwen MoE; potentially higher per-token quality.
- **Modality retention through GGUF conversion is the open question.** llama.cpp / GGUF historically focused on text; multimodal extensions exist (e.g. `mmproj` files for vision tower). The unsloth GGUF repo for this model **does** ship `mmproj-F16.gguf` files (visible in the GGUF file listing for related Qwen models); whether they're shipped for this Gemma variant is worth verifying before assuming text-only.
- Gemma 4 has a distinct chat template; Ollama's default template handling may or may not align with the model's training pattern. Worth checking with `ollama show <name>`.

## Open at this entry

- Modality retention through GGUF conversion — open question stated above
- Whether to register and characterise, or remove from disk
- Direct quality comparison vs the Qwen 27B at the same bit depth
- Tool calling support through Ollama for the Gemma family

## Connects to

- [[_models-index]] — hub
- [[qwen3_6-27b-gguf-q3-k-m]] — competing dense 27B
- [[qwen3_6-35b-a3b-gguf-q3-k-m]] — competing MoE
- [[../operations/ollama]] — registration procedure
