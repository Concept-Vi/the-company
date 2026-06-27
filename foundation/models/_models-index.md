---
type: hub
title: Models — Index
folder: models
date_started: 2026-05-27
tags: [foundation, models, hub, moc]
---

# Models — Index

> Folder: `~/company/foundation/models/`
> All entries here follow [open-future mode]([[../TIM#Layer 3 — Open-future writing mode (2026-05-27)]]) — provisional, dated, examples-not-specs, every closure marked, every gap explicit.

This file is the hub for every model that lives on or is served by the substrate. The **By Need** section is the entry path most agents will use; the **Registry** is the model-name lookup; the **Open** register names what hasn't been characterised. Each model has its own file linked from the Registry.

## How this folder works

- **One file per model.** Filename is the kebab-case form of the HF identifier — `cyankiwi/Qwen3.5-4B-AWQ-4bit` becomes `qwen3_5-4b-awq.md`. Underscores preserve version-dot semantics; hyphens separate identifier segments.
- **Hub-to-model links** use wikilinks: `[[qwen3_5-4b-awq]]`.
- **Status taxonomy** (used in frontmatter and the Registry):
  - `deployed-default` — running on a known port as the default for its role
  - `swap-only` — fits the substrate; used by swapping out a default
  - `tested` — verified to load and produce coherent output; performance characterised
  - `downloaded` — present on disk; never test-loaded
  - `theoretical` — referenced or proposed; not yet on disk
  - `auxiliary` — supporting model (reranker, layout detector, generic embedder) used by tooling rather than as a primary endpoint
- **Each model file holds**: at-a-glance facts (size, quant, architecture, native context); what-it-fits-for (links back to By Need entries); tested performance (or "to characterise" register); known good config; quirks; open at this entry; sources.

## How to add a new model entry

A future agent extending this folder works through this sequence. Empty fields are useful — they make the test-backlog visible to whoever picks up next.

1. **Pull the model** into `~/.cache/huggingface/hub/` (vLLM / jina-v4-env) or register with Ollama (GGUF). Verify completeness (no `*.incomplete` blobs).
2. **Create** `~/company/foundation/models/<kebab-id>.md`. Use the most-similar existing file as template — match the section headers exactly so consistency self-propagates.
3. **Fill** at-a-glance, source, and any known facts. Leave performance fields explicitly empty with a *"To characterise"* register if untested.
4. **Add a row** to the Registry table in this hub, dated.
5. **Link from By Need.** If the model fits an existing need, add a bullet. If it opens a new need, add an H3 entry under By Need with a short narrative.
6. **Date the entry.** Every claim about performance, fit, or status carries a date.
7. **Add an Open register** at the bottom of the model file naming what's not known.

The pattern propagates by example. An agent landing here for the first time learns the convention by reading the files, not by reading instructions.

## By need (Tim-invariant)

These are the jobs an agent on Tim's behalf might be filling. Models below each entry are the means to that job. The list is provisional; new needs surface as Tim's work surfaces them. Existing AI-default need-categories (generic summarisation, generic code-gen) should be added only when an actual Tim-relevant job demands them, not assumed in advance.

### High-throughput chat for batch / mass-parallel work

The substrate's primary deployment target. The job: process many concurrent chat requests, batched at the runtime layer, optimised for aggregate tokens/second rather than per-request latency.

- [[qwen3_5-4b-awq]] — deployed-default on port 8000. Tested ceiling ~2,250 tok/s aggregate at concurrency 32, ~21 req/s sustained; TTFT degrades above concurrency 128. Verified production-stable over 8-min mixed-load sustained run (3,540 reqs, 0 errors, 2026-05-26).
- [[qwen3_5-0_8b]] — extreme-concurrency alternative. KV cache supports 158x at 4K context; suited to short-prompt classification / routing / triage workloads. Per-request quality lower than 4B.
- [[nemotron-3-nano-30b-a3b-awq]] — MoE 3B-active candidate for AWQ-on-vLLM throughput. Untested as of 2026-05-27.
- [[qwen3_6-35b-a3b-gguf-q3-k-m]], [[qwen3_6-35b-a3b-gguf-iq3-s]] — MoE candidates for GGUF-on-Ollama throughput. Q3_K_M registered with Ollama as `qwen3.6-35b-a3b-q3km:latest`. Concurrent-throughput characterisation pending.

Tradeoff: AWQ / GPTQ in vLLM is the fastest-per-request path; GGUF in Ollama has wider model availability and lower-bit options but historically slower at high concurrency. Direct head-to-head untested.

Open: optimal concurrency per model; sustained throughput across multiple models simultaneously; GGUF-MoE-via-Ollama vs AWQ-MoE-via-vLLM under matched workloads.

### Long-context document QA / RAG

The job: feed long contexts (multi-thousand tokens) and get coherent answers grounded in the input.

- [[qwen3_5-4b-awq]] — characterised 4K–30K input. Prefill scales sublinearly: 4K input → 398ms TTFT, 30K input → 1.07s TTFT, 28K tok/s prefill rate. Native context 262K (untested above 30K). Needle-in-haystack 5/5 at 10/25/50/75/90% depth (3K context).
- [[qwen3_6-27b-gguf-q3-k-m]] — larger model, GGUF path; recall and prefill characteristics in Ollama untested.

Open: 32K–262K context band on the 4B; whether higher-bit GGUF quants would noticeably improve long-context recall vs the 4B AWQ baseline.

### Tool calling, structured output, agentic work

The job: emit JSON-schema-conformant outputs and OpenAI-style `tool_calls` reliably.

- [[qwen3_5-4b-awq]] — verified working with `--enable-auto-tool-choice --tool-call-parser qwen3_xml`. Tool selection 3/3 correct including the negative case. Structured output (`response_format: json_schema`) 3/3 valid JSON. The chat-template patch at `~/vllm-tests/chat_template_nothink.jinja` is required (default-disables Qwen3's `<think>` mode which otherwise consumes output tokens and breaks tool calls).
- Other models: tool calling untested.

Open: tool-calling reliability for the larger Qwen3.6 variants via Ollama; whether the Hermes-style parser would work for non-Qwen models.

### Single-stream high-quality reasoning (low concurrency, high capability)

The job: one query at a time, higher quality than the throughput-optimised default. Slow is acceptable; depth is not.

- [[qwen3_6-27b-gguf-q3-k-m]] — dense 27B at Q3_K_M. Single-stream Ollama performance not yet measured.
- [[qwen3_6-35b-a3b-gguf-q3-k-m]] — MoE 35B / 3B-active. Knowledge closer to 35B-class.
- Cloud-routed Ollama models (`gemma4:31b-cloud`, `nemotron-3-super:cloud`, `deepseek-v4-pro:cloud`, `kimi-k2.6:cloud`, etc.) — accessed via the same Ollama API; cost-incurring but capability ceiling above any local model.

Open: which local model has the best single-stream quality at Tim's typical query patterns; whether GGUF Q3 is enough quality or higher-bit variants are needed; cloud-vs-local decision rules for reasoning-heavy work.

### General dense text embedding for semantic search

The job: convert text to dense vectors for nearest-neighbour retrieval over arbitrary corpora.

- [[bge-m3]] — deployed-default on port 8001. 1024-d dense embeddings. 8K context. Tested ~1,370 embeddings/s at concurrency 32. Multi-output capable (dense + sparse + ColBERT from one forward pass) — see the next two needs.
- [[jina-embeddings-v5-text-small]] — 677M params, 1024-d, instruction-aware (4 task adapters). Tested semantic check (cat/feline vs cat/stocks: 0.682 / 0.081 — strong separation). Not currently served.
- [[qwen3-embedding-8b]] — flagship multilingual dense embedder (top MTEB at time of pull). 8B params. Downloaded, never served.

Open: which embedder best fits Tim's actual corpora (Obsidian vault, Xero / bank statements, code); whether deployment of Qwen3-Embedding-8B would beat BGE-M3 for general use enough to justify the VRAM trade.

### Sparse / lexical embedding (exact term matching)

The job: when dense semantic match misses exact tokens — proper names, jargon, link labels, filenames — supplement with sparse retrieval.

- [[bge-m3]] — sparse head accessible via the FlagEmbedding library (`BGEM3FlagModel`), not via vLLM. Sparse and ColBERT outputs come from the same forward pass as dense.

Open: production access path for BGE-M3 sparse (vLLM doesn't expose it; either run a sidecar via FlagEmbedding or route to a different server).

### Multi-vector / ColBERT-style precise retrieval

The job: token-level late interaction for higher recall on hard queries.

- [[bge-m3]] — ColBERT head accessible via the FlagEmbedding library. ~30 vectors per chunk at 128-d each. Storage cost noticeable; recall improvement on hard queries documented in the literature.

Open: storage architecture for multi-vector indices on Tim's likely data scale; whether the recall gain justifies the storage / compute cost for Obsidian-scale corpora.

### Code embedding for codebase / repo retrieval

The job: embed code chunks for semantic search over codebases. Prose embedders perform poorly on code; specialised models exist.

- [[nomic-embed-code]] — 7B Qwen2-based code-specific embedder, 32K context, 27GB on disk (FP16 weights). Downloaded, never served. Would displace the default embed if served.

Open: whether nomic-embed-code is the right code embedder for Tim's code corpora vs alternatives; whether to serve it as swap-only or run alongside BGE-M3 (VRAM constraint).

### Multimodal: text + image

The job: accept image inputs alongside text and reason about both.

- [[qwen3_5-4b-awq]] — vision-language architecture; vision input never benchmarked on this substrate despite the capability being present.
- [[jina-embeddings-v4]] — multimodal embedder (text + image), runs in `jina-v4-env` on port 8002 because of `transformers<5.0` dependency.

Open: vision input on Qwen3.5-4B-AWQ — TTFT, decode rate, accuracy on Tim-relevant tasks (OCR, document understanding, image-grounded Q&A); how vision tokens count against context budget.

### Multimodal: text + image + visual documents (charts, PDFs with layout)

The job: handle documents with layout — charts, scanned PDFs, mixed text/figures — as embeddings or as input to a chat model.

- [[jina-embeddings-v4]] — designed for visual documents; suitable for visual-doc retrieval. Throughput on this substrate not characterised.
- [[unstructuredio/yolo_x_layout]] — auxiliary layout-detection model (207MB) for preprocessing PDF documents before embedding. Used by document-processing tooling, not as a primary endpoint.

Open: full doc-RAG pipeline — layout detection → chunking → multimodal embedding → retrieval — never assembled or tested end-to-end on this substrate.

### Multimodal: text + audio

The job: accept audio inputs (transcription, audio-grounded Q&A).

- Gemma-4-E4B omnimodal variant was tested in an earlier session (2026-05-26) but is not currently on disk. The 26B-A4B-GGUF variant ([[gemma-4-26b-a4b-gguf-q3-k-m]]) is on disk but whether the GGUF retains audio capability is unverified.

Open: confirmed-working audio path on the substrate; which model (if any currently downloaded) reliably handles audio input.

### Vision-language single-shot (OCR, visual QA)

The job: one image + one question → answer. Distinct from image-as-input-to-a-conversation.

- [[qwen3_5-4b-awq]] — VL architecture supports this; untested for OCR / visual QA tasks specifically.

Open: OCR quality, visual QA quality, suitable use-case fit for Tim's likely document / screenshot workloads.

## Registry

Status as of 2026-05-27. Sizes are disk usage. The runtime / port columns reflect current systemd-managed services and Ollama registration.

| Model | File | Disk | Quant | Architecture | Status | Runtime | Port |
|---|---|---|---|---|---|---|---|
| Qwen3.5-4B-AWQ | [[qwen3_5-4b-awq]] | 3.8G | AWQ Int4 | VL / hybrid Mamba-attention | deployed-default | vllm | 8000 |
| Qwen3.5-0.8B | [[qwen3_5-0_8b]] | 1.7G | BF16 | VL / hybrid Mamba-attention | tested | — | — |
| Qwen3.5-2B | [[qwen3_5-2b]] | 4.3G | BF16 | text-only base | downloaded | — | — |
| Nemotron-3-Nano-30B-A3B-AWQ | [[nemotron-3-nano-30b-a3b-awq]] | 17G | AWQ | MoE 3B-active | downloaded | — | — |
| Qwen3.6-35B-A3B GGUF Q3_K_M | [[qwen3_6-35b-a3b-gguf-q3-k-m]] | 16G | GGUF Q3_K_M | MoE 3B-active | downloaded | ollama | 11434 |
| Qwen3.6-35B-A3B GGUF IQ3_S | [[qwen3_6-35b-a3b-gguf-iq3-s]] | 13G | GGUF IQ3_S | MoE 3B-active | downloaded | — | — |
| Qwen3.6-27B GGUF Q3_K_M | [[qwen3_6-27b-gguf-q3-k-m]] | 13G | GGUF Q3_K_M | dense | downloaded | ollama | 11434 |
| Gemma-4-26B-A4B GGUF Q3_K_M | [[gemma-4-26b-a4b-gguf-q3-k-m]] | 12G | GGUF Q3_K_M | MoE 4B-active, omnimodal | downloaded | — | — |
| BGE-M3 | [[bge-m3]] | 4.3G | FP16 | dense + sparse + ColBERT | deployed-default | vllm | 8001 |
| Jina v5 text small | [[jina-embeddings-v5-text-small]] | 1.3G | FP16 | dense | tested | — | — |
| Jina v4 | [[jina-embeddings-v4]] | 7.4G | BF16 | multimodal embed | deployed | jina-v4-env | 8002 |
| Qwen3-Embedding-8B | [[qwen3-embedding-8b]] | 15G | FP16 | dense | downloaded | — | — |
| Nomic-embed-code | [[nomic-embed-code]] | 27G | FP16 | dense, code-specific | downloaded | — | — |
| sentence-transformers MiniLM L6 v2 | [[auxiliary-minilm-l6-v2]] | 888M | FP32 | dense, small | auxiliary | — | — |
| ms-marco MiniLM L6 v2 cross-encoder | [[auxiliary-ms-marco-reranker]] | 88M | FP32 | cross-encoder reranker | auxiliary | — | — |
| YOLO X layout | [[auxiliary-yolo-x-layout]] | 207M | FP32 | layout detector | auxiliary | — | — |
| nomic-embed-text (Ollama) | [[ollama-nomic-embed-text]] | 262M | quantised | dense embed | available | ollama | 11434 |

Cloud routes (Ollama; not local — incur per-token cost; accessible via the same `http://localhost:11434/v1` endpoint):

| Cloud route | Tier hint |
|---|---|
| `gemma4:31b-cloud` | mid |
| `nemotron-3-super:cloud` | high |
| `deepseek-v4-flash:cloud` | mid-fast |
| `deepseek-v4-pro:cloud` | high |
| `kimi-k2.5:cloud`, `kimi-k2.6:cloud` | high (very-long context) |
| `glm-5:cloud`, `glm-5.1:cloud` | mid |
| `gemini-3-flash-preview:cloud` | fast |
| `qwen3.5:397b-cloud` | flagship |

Open: which cloud routes are worth keeping wired up vs trimming; cost characteristics per route; latency vs local.

## Runtimes (short summary; full ops in [[../operations/_operations-index|operations]])

Three local runtimes plus Ollama cloud routing.

- **vLLM 0.21** at `~/vllm-env/`. Serves AWQ / GPTQ / FP8 / FP16 / BF16. Native VL support. Tool calling + structured output via flags. WSL CUDA toolchain pinned to 13.0 (see [[../operations/cuda-toolchain]]). Hosts: chat (port 8000), embed (port 8001). Will not serve GGUF or jinaai-v4's dynamic-LoRA architecture in this version. *See [[../operations/runtimes#vLLM]].*
- **Ollama** at port 11434, systemd `ollama.service` (system, not user). The GGUF runtime. Currently registered: `qwen3.6-35b-a3b-q3km:latest`, `qwen3.6-27b-q3km:latest`, `nomic-embed-text:latest`. Also routes cloud models. *See [[../operations/runtimes#Ollama]].*
- **jina-v4-env** at `~/jina-v4-env/` (Python venv with `transformers<5.0`, Pillow, torchvision). Hosts jina-v4 multimodal embedder on port 8002 via `serve_jina_v4.py`. Exists because jina-v4's bundled `qwen2_5_vl.py` is incompatible with `transformers>=5`. *See [[../operations/runtimes#jina-v4-env]].*

## VRAM allocation patterns

The substrate runs on 16 GiB VRAM (RTX 4080). Observed patterns:

- **Default co-resident (verified 2026-05-27 at ~15.5 GiB / 95% util)**: chat (Qwen3.5-4B-AWQ, ~12.8 GiB with KV) + embed (BGE-M3, ~2.7 GiB) + jina-v4 (~7.4 GiB BF16 weights) — three services concurrently, all responding. The actual fit depends on each service's `--gpu-memory-utilization` budget; current configuration leaves ~3% headroom.
- **Single large model**: any of the 12–17 GiB models (Nemotron-30B-A3B, GGUF MoE Q3_K_M variants, Gemma-26B-A4B GGUF) requires stopping the chat default first (`vllm-stack swap-chat <model_id>`).
- **Theoretical four-way**: not feasible. Adding any additional large model on top of the three-way default OOMs.

Swap procedure: `vllm-stack swap-chat <model_id>` stops current chat, edits serve.sh, restarts. Cold start ~2–3 minutes per swap (torch.compile cache shared per-model; CUDAGraphs re-captured each process restart).

## Open at this folder

(Things known to be unknown; examples; more surface as work proceeds.)

- Vision input never benchmarked on [[qwen3_5-4b-awq]] despite VL architecture being present
- Audio input not exercised on any currently-on-disk model since Gemma-4-E4B-FP8 was removed
- GGUF MoE concurrent throughput via Ollama not measured for any registered variant
- IQ3_S variant of Qwen3.6-35B-A3B downloaded but not registered with Ollama as of 2026-05-27
- Gemma-4-26B-A4B Q3_K_M downloaded but not registered with Ollama
- [[nemotron-3-nano-30b-a3b-awq]] never test-loaded; fit on 16GB at load unverified
- [[qwen3-embedding-8b]] downloaded but never served
- [[nomic-embed-code]] downloaded but never served
- Head-to-head embedding quality comparison ([[bge-m3]] vs [[jina-embeddings-v5-text-small]] vs [[qwen3-embedding-8b]]) on Tim's likely corpora never run
- BGE-M3 sparse and ColBERT outputs not exposed via the vLLM endpoint; alternative serving path open
- Speculative decoding never tested on any model
- LoRA adapter loading never tested on any model
- Concurrent multi-model performance under sustained mixed load over hours/days not measured
- The **needs vocabulary** above is provisional; new needs from Tim's work surface as new H3 entries (existing AI-default categories like "summarisation" or "generic code-gen" should be added only when a concrete Tim-need requires them, not assumed in advance)
- The **auxiliary** models (MiniLM, MS-MARCO reranker, YOLO X layout) have stub entries; their actual use in Tim's pipelines is gestured-at by their presence on disk but undocumented here
- Cloud-route cost characteristics, latency, and rate limits not characterised

## Connects to

- [[../TIM]] — foundation document; Layer 3 defines the writing mode every entry here follows
- [[../operations/_operations-index]] — operational hub for the runtimes that serve these models
- [[../exchanges/_exchanges-index]] — verbatim primary sources for conversations that produced this knowledge
- [[../system/README]] — synthesis layer; principles + architecture
