---
type: model
id: cyankiwi/Qwen3.5-4B-AWQ-4bit
filename: qwen3_5-4b-awq
status: deployed-default
runtime: vllm
port: 8000
date_added: 2026-05-26
date_last_characterised: 2026-05-27
tags: [foundation, models, chat, deployed]
---

# Qwen3.5-4B-AWQ-4bit

> [[_models-index|← Models hub]] · linked from: high-throughput chat · long-context RAG · tool calling · structured output · multimodal text-image (untested)

## At a glance

| Field | Value |
|---|---|
| HF id | `cyankiwi/Qwen3.5-4B-AWQ-4bit` |
| Disk | 3.8 GB |
| Quant | AWQ Int4 |
| Architecture | Vision-language; hybrid Mamba-attention; chat-tuned |
| Native context | 262,144 tokens |
| Tested context | 4K (production), up to 30K (long-context bench) |
| Chat template | Patched; `<think>` off by default — file at `~/vllm-tests/chat_template_nothink.jinja` |
| Tool parser | `qwen3_xml` |
| VRAM at load (KV-included, util 0.9, max_num_seqs 64) | ~12.8 GiB |
| Service unit | `vllm-chat.service` |
| Endpoint | `http://localhost:8000/v1` |

## Source

Pulled 2026-05-26 from the cyankiwi packager because their AWQ Int4 quants of Qwen3.5 had wide community use at pull time and the same packager produced [[qwen3_6-35b-a3b-gguf-q3-k-m|other variants]] consumed elsewhere on this substrate. Original upstream is `Qwen/Qwen3.5-4B`.

The 4B was chosen over [[qwen3_5-0_8b|0.8B]] (too small for production quality) and [[qwen3_5-9b-awq|9B-AWQ]] (vision tower bloated the 9B AWQ build to 12 GB, leaving only ~2.4x concurrency capacity at 2K context — verified 2026-05-26).

## Fits these needs

- [[_models-index#High-throughput chat for batch / mass-parallel work|High-throughput chat for batch work]] — the default for this role
- [[_models-index#Long-context document QA / RAG|Long-context document QA / RAG]] — most characterised model for this band
- [[_models-index#Tool calling, structured output, agentic work|Tool calling, structured output, agentic work]]
- [[_models-index#Multimodal: text + image|Multimodal: text + image]] (capability present, untested)
- [[_models-index#Vision-language single-shot (OCR, visual QA)|Vision-language single-shot]] (capability present, untested)

## Tested performance (2026-05-26 / 2026-05-27)

Concurrency sweep (128-token outputs):

| Concurrency | Aggregate tok/s | Req/s | TTFT p50 | Latency p50 |
|---|---|---|---|---|
| 8 | 809 | 6.3 | 65ms | 1.20s |
| 32 | 2,241 | 17.5 | 153ms | 1.80s |
| 64 | 2,124 | 16.6 | 288ms | 3.76s |
| 128 | 2,251 | 17.6 | 3,736ms | 7.13s |
| 256 | 2,242 | 17.5 | 10,886ms | 14.32s |
| 512 | 1,674 | 13.1 | 26,138ms | 29.79s |

Sweet spot: concurrency 32 — peak aggregate throughput, sub-200ms TTFT. Past concurrency 64, TTFT degrades sharply; past 128 the queue dominates and aggregate throughput plateaus while latency runs away.

Long-input prefill (32K max-model-len; concurrency 4):

| Input tokens | TTFT | Prefill tok/s | Decode tok/s |
|---|---|---|---|
| ~4K | 398ms | 10,207 | 130.3 |
| ~10K | 566ms | 17,610 | 124.3 |
| ~16K | 703ms | 22,721 | 118.8 |
| ~22K | 755ms | 29,095 | 112.3 |
| ~30K | 1,067ms | 28,098 | 104.7 |

Prefill efficiency improves with longer inputs (Flash Attention's sublinear scaling). Decode is steady ~100–130 tok/s/req regardless of input length.

Long-output decode (concurrency 8):

| Max tokens | Per-request tok/s | Aggregate tok/s |
|---|---|---|
| 256 | 101.9 | 783 |
| 512 | 104.0 | 815 |
| 1024 | 101.6 | 806 |
| 1800 | 97.1 | 773 |

No length-induced degradation; aggregate dips slightly as KV cache fills with output.

Multi-turn with prefix caching (8 turns, ~1K cumulative context): TTFT 40–110ms across all turns. Prefix caching reuses prior conversation rather than re-prefilling.

Structured output (`response_format: json_schema`): 3/3 valid JSON conforming to schema.

Tool calling (`qwen3_xml` parser): 3/3 correct including the negative case (no tool when none needed).

Needle-in-haystack (3K context, depths 10/25/50/75/90%): 5/5 found.

Sustained mixed load (concurrency 32, mix 30% short / 40% medium / 30% long): 3,540 requests over 496s wall, 0 errors, 1,382 aggregate tok/s, p50 latency 4.57s, p99 8.20s.

Full report: `~/vllm-tests/BENCHMARK_FACTSHEET.md` (primary record kept in `vllm-tests/` operationally; canonical synthesis lives here).

## Known-good launch config

Defined in `~/vllm-tests/serve.sh`; managed by `~/.config/systemd/user/vllm-chat.service`.

```
vllm serve cyankiwi/Qwen3.5-4B-AWQ-4bit \
  --port 8000 \
  --host 0.0.0.0 \
  --gpu-memory-utilization 0.90 \
  --max-model-len 4096 \
  --max-num-seqs 64 \
  --enable-prefix-caching \
  --enable-auto-tool-choice \
  --tool-call-parser qwen3_xml \
  --chat-template ~/vllm-tests/chat_template_nothink.jinja \
  --trust-remote-code
```

Environment expected: `CUDA_HOME` pointed at the cu13 toolkit inside the venv; `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0`. See [[../operations/cuda-toolchain]].

For long-context work, swap `--max-model-len 32768 --max-num-seqs 8` and accept lower concurrency. KV cache 256K tokens at 32K context.

## Quirks

- **Thinking mode.** Out-of-box chat template emits `<think>…</think>` before answering. Consumes output tokens; breaks tool calling because the visible text becomes commentary about a tool call rather than the call itself. The patched template at `~/vllm-tests/chat_template_nothink.jinja` inverts the default (off unless `chat_template_kwargs: {enable_thinking: true}` is passed). All operational behaviour below assumes the patched template is loaded via `--chat-template`.
- **Vision tower lives in VRAM regardless of input modality.** The model is VL even when only text is sent. Disabling the vision tower without retraining is not supported in vLLM 0.21; the cost is borne whether vision is used or not.
- **Mamba cache mode.** Prefix caching with the hybrid Mamba-attention architecture is marked "experimental" in vLLM 0.21 log output (mode set to `align` automatically). No issues observed in benchmarks; flag for future regressions.
- **`enforce_eager=True` defeats the production case.** Disables torch.compile + CUDAGraphs — the kernels that batch throughput depends on. Earlier this substrate's tests with eager mode reported 24 tok/s; production with eager off reports >2,000.
- **Concurrent multi-service co-residency.** Verified to run alongside [[bge-m3]] on port 8001 and [[jina-embeddings-v4]] on port 8002 at ~15.5 GiB VRAM total (~95% util). Adding a fourth large model will OOM.

## Open at this entry

- Vision input never sent to this server. TTFT, decode rate, accuracy on Tim-relevant visual tasks (OCR, document understanding, image-grounded Q&A) — open.
- 32K → 262K context band unmeasured. Native max is 262K; tested ceiling 30K.
- Speculative decoding never enabled. Could materially change concurrency / throughput characteristics.
- LoRA adapter loading never tested.
- Multi-day sustained operation not measured (longest run: 8 minutes).
- Cloud-vs-local quality comparison on Tim's typical query patterns never run.

## Connects to

- [[_models-index]] — hub
- [[../operations/cuda-toolchain]] — toolchain pins that enable serving
- [[../operations/runtimes]] — vLLM serving details
- [[../operations/chat-template-patch]] — the no-think template
- [[../operations/vllm-stack-cli]] — `vllm-stack` commands for swap/restart
- [[bge-m3]], [[jina-embeddings-v4]] — co-resident services
- Source archive: `~/vllm-tests/BENCHMARK_FACTSHEET.md`
