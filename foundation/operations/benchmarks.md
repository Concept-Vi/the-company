---
type: operations
title: Benchmarks — scripts, measurements, interpretation
date_started: 2026-05-27
tags: [foundation, operations, benchmarks]
---

# Benchmarks

> [[_operations-index|← Operations hub]]

## What exists

Four benchmark scripts in `~/vllm-tests/`, callable via [[vllm-stack-cli|`vllm-stack`]]:

| Script | Wrapper | Measures |
|---|---|---|
| `bench.py` | `vllm-stack bench-chat` | Concurrent chat throughput at configurable concurrency |
| `bench_embed.py` | `vllm-stack bench-embed` | Concurrent embedding throughput at configurable concurrency |
| `bench_suite.py` | `vllm-stack bench-suite` | Deep characterisation: concurrency sweep + long input + long output + multi-turn + structured output + tool calling + needle-in-haystack + sustained load |
| `bench_long_ctx.py` | `vllm-stack bench-long-ctx` | Long-input prefill performance from 4K to 30K tokens; requires server restarted with `--max-model-len 32768` |

All scripts use `httpx` (installed in vllm-env) and target OpenAI-compat endpoints. Easy to point at any service — the scripts default to the chat endpoint on 8000.

## Why these specific benchmarks

Each one answers a different operational question:

- **bench.py**: "What concurrency level should production run at?" Sweep 8 / 32 / 64 / 128 / 256 / 512 — find the knee where throughput plateaus and TTFT collapses. For [[../models/qwen3_5-4b-awq]] the knee is at concurrency 64.
- **bench_embed.py**: Same for embedding services. BGE-M3 saturates at concurrency ~32.
- **bench_suite.py**: "Does this model do everything we need it to?" The eight-test sweep covers throughput, prefill, decode, multi-turn, structured output, tool calling, recall, and sustained operation in one run.
- **bench_long_ctx.py**: Specific to long-context prefill characterisation. Useful when context length is the gating factor (RAG over big documents).

## Interpretation notes

**Concurrency sweep**: look for the concurrency at which aggregate tok/s plateaus and TTFT begins to climb sharply. Below this, the GPU is underutilised; above it, requests queue. For the 4B AWQ:

- Concurrency 32 = peak throughput (~2,240 tok/s), low TTFT (~150ms)
- Concurrency 128 = same throughput, TTFT collapses to ~3.7s (queue dominates)

**Long input**: prefill tok/s often increases with input length (Flash Attention sublinear scaling). Don't expect linear slowdown; expect efficiency gains up to a model-specific ceiling. For the 4B AWQ on 32K-context config, prefill hits 28K tok/s at 30K input.

**Long output**: per-request decode is usually constant regardless of output length, but aggregate throughput drops as KV cache fills with output. For the 4B AWQ, per-request stays ~100 tok/s from 256 to 1800 output tokens.

**Multi-turn**: with prefix caching enabled, TTFT should stay flat even as cumulative context grows. If TTFT climbs linearly with turn count, prefix caching isn't working (most likely cause: `--enable-prefix-caching` missing from launcher).

**Structured output / tool calling**: pass/fail counts. The fix isn't speed; it's making them work at all. Failure modes: missing `--enable-auto-tool-choice` / `--tool-call-parser` flags; missing chat template (`enable_thinking` defaulting on).

**Needle-in-haystack**: depth × found rate. Modern long-context models should be ≥80% at all depths up to their context limit. Failure suggests context-collapse problem at depth.

**Sustained load**: run length × error count × throughput drift. Goal: zero errors over hours; throughput drift < 5%.

## Storage of benchmark outputs

Benchmark results currently go to `/tmp/*.log` files — ephemeral. Some are summarised in `~/vllm-tests/BENCHMARK_FACTSHEET.md` for the production model.

Per-model performance tables in `~/company/foundation/models/<model>.md` are the canonical synthesis of bench results. The source `/tmp/` logs and `~/vllm-tests/BENCHMARK_FACTSHEET.md` are the primary record.

## Running a fresh bench (procedure)

```bash
# Quick concurrent chat bench
vllm-stack bench-chat --concurrency 32 --requests 200

# Deep suite (~10-30 min depending on --sustained-sec flag)
vllm-stack bench-suite --sustained-sec 180

# Long context (requires restarting chat with --max-model-len 32768 first)
# Edit serve.sh, restart, then:
vllm-stack bench-long-ctx --concurrency 4 --samples 4
```

## Reading a result table

A typical row from a concurrency sweep:

```
| Concurrency | Reqs | Wall(s) | Tok/s agg | Req/s | TTFT p50 | TTFT p95 | TTFT p99 | Latency p50 | p95 | p99 | Errors |
| 32 | 128 | 7.3 | 2241 | 17.51 | 153ms | 181ms | 182ms | 1.80s | 1.89s | 1.89s | 0 |
```

- **Tok/s agg**: total tokens generated divided by wall time. The headline throughput.
- **Req/s**: requests completed per second.
- **TTFT p50/p95/p99**: time to first token, percentiles. The latency users actually perceive in an interactive setting.
- **Latency p50/p95/p99**: total request time (TTFT + decode). What batch-style callers see.
- **Errors**: anything that returned non-200 or didn't produce tokens.

## Open at this topic

- Benchmark history archive — `/tmp/` logs are ephemeral; a `~/company/foundation/operations/benchmark-results/` would preserve historical runs for comparison across model upgrades
- A dashboard-style summary that pulls from the latest benchmark log and renders the headline numbers for the substrate's deployed models
- Cross-runtime benchmarks — `vllm-stack bench-chat` only targets the vLLM-served chat endpoint by default; pointing it at Ollama's port via `--url http://localhost:11434/v1` would give comparable numbers across runtimes (untested)
- Vision benchmark — none exists; the VL capability of [[../models/qwen3_5-4b-awq]] is untested
- Audio benchmark — same gap
- Cost-of-cloud-route benchmark — when cloud routes are used (Ollama's `:cloud` tags), no measurement of per-token cost or comparable throughput

## Connects to

- [[_operations-index]] — hub
- [[vllm-stack-cli]] — command wrappers
- [[../models/qwen3_5-4b-awq]] — the deeply benchmarked model
- Source: `~/vllm-tests/bench*.py`, `~/vllm-tests/BENCHMARK_FACTSHEET.md`
