# RECOVERED DECISION — the embedding model (pplx-4b, switched from 8B)

```
trust: tim-direct(session=bda8ce28)   # Tim's decision, made IN bda8ce28 via the AskUserQuestion onboarding (2026-06-12),
                                       #   confirmed again directly 2026-06-14 (L11292). Recovered by structural recall, not inference.
author: ch-8djrpmsl / 11e7d395 (fork)
date: 2026-06-14
verified: by-execution (recovered verbatim from the lead transcript bda8ce28 L4257/L4335/L5098)
recovers: the decision an agent FAILED to recall on 2026-06-14 (L10772–L11292), causing Tim's frustration.
          This file exists so it is never lost again.
```
> Per [[COMMIT-GRAMMAR]] §2. This is the first entry in `recall/` — the output of the session-recall capability (the [[session-store-grammar]] scan + future embedding search). Links: [[2026-06-14-session-splicing-and-channel-memory]].

## The decision (one line)
**The embedding model for past-session / transcript search = `pplx-embed-context-v1-4b` + a jina reranker on CPU — chosen over `Qwen3-Embedding-8B` specifically so the VOICE models fit on the 16 GB GPU alongside it.** `bge-m3` remains the already-running bootstrap (Atlas + vaults). The pplx-4b choice was framed as the *interim/throwaway* transcript embedder; the 8B is the quality ceiling held in reserve.

## The candidates (verbatim from the on-disk model cards, bda8ce28 L4257)
| model | specs | role |
|-------|-------|------|
| **pplx-embed-context-v1-4b** | Qwen3-4B base, Perplexity "diffusion-pretrained" + bidirectional; the **`-context`** variant is purpose-built for **RAG document chunks where surrounding context matters** (a genuinely good fit for conversation transcripts); **2560-dim**, **32K context**, **instruction-free by design**, native **int8** vectors, ~10 GB | **CHOSEN** for transcript/past-session search |
| **Qwen3-Embedding-8B** | **#1 MTEB multilingual (June 2025, 70.58)** — proven quality champion; **4096-dim**, 32K context, instruction-aware; ~15 GB → **owns the 16 GB GPU** | quality ceiling, held in reserve |
| **bge-m3** | 1024-dim; the only embedder **actually run** (Atlas + 10 vaults) | bootstrap / fallback |

## The reasoning (the relational key — why 4B over the better 8B)
**GPU budget.** The machine has a 16 GB GPU. Qwen3-8B owns ~15 GB when serving → **no room for voice**. The 4B (~10 GB) leaves headroom so the **voice models fit on the GPU alongside the embedder**. Tim initially chose the 8B (max quality), then **switched to pplx-4b for this coexistence reason** (bda8ce28 L4335, L5098). Quality was knowingly traded for the voice-on-GPU constraint.

> Verbatim (L4335, 2026-06-12T02:39): *"Past-session search → interim/throwaway: **pplx-embed-context-4b + jina reranker (CPU)**, embedder chosen specifically so **voice fits on the GPU alongside it**, timer bound to the Company so it's visible and never an orphan."*

## The serving complication (already hit, in-session)
- pplx-4b's custom architecture is **NOT in vLLM's 356 supported archs** (`vllm serve` fails at load — bda8ce28 L4368) and its custom code targets an **older transformers** (`create_causal_mask` signature changed/removed in 5.9.0 — L4870). Serving it took real work; `bge-m3` stayed the working fallback.
- Built in-session: `embed-pplx` service (port 8007, on-demand), `jina` reranker on CPU, `claude-sessions-reindex` + `agent-sessions-exporter` timers, all bound to the Company lifecycle (L4893).

## The bigger vision (the loadout, not one winner — bda8ce28 L7889, 2026-06-13)
Not a single embedder but a **purpose-loadout**: *ColGrep for code · a Qwen3-VL pair for visual · pplx-context for long-arc · pplx-0.6b + Granite + Qwen3-8B for scale/deep-pass.* **"bge-m3 is one config, not the winner — and only bge-m3 has actually been run."** Connects to [[mode-loadout-registry]], [[native-model-layer]], [[voice-stack]].

## Lane note
**Embedding-SERVING + GPU loadout + voice is the LEAD's locked lane.** This record is the fork's recall output; acting on it (serving pplx-4b, the GPU/voice coexistence) is the lead's. Relayed to the lead 2026-06-14.
