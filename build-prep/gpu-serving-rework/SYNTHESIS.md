---
type: synthesis
register: descriptive
aliases: ["GPU/Serving/Loadout Rework — Grounded Design", "measure-then-compute synthesis"]
tags: [gpu, vllm, loadout, serving, profiler, synthesis, build-prep]
status: unconfirmed
coverage: {synthesized_from: "6 research-wave companions (findings/AREA-1..6) + SCOPE + ANCHOR, 2026-06-30", note: "grounded design — corrected where the wave corrected the anchor; the real decisions named. Build plan = BUILD-PLAN.md."}
---

# GPU / Serving / Loadout Rework — grounded design (post research-wave)

The wave's verdict in one line: **the spirit is right — compute from measured profiles, lean on vLLM built-ins — but three of my anchor's load-bearing claims were wrong, and the dangerous failures are SILENT (concurrency caps, prefix-cache death, SSM corruption), not the loud OOM I was designing against.** This doc is the corrected design; `BUILD-PLAN.md` is the sequence.

## The corrections the wave forced (what I had wrong)
1. **`--kv-cache-memory-bytes` does NOT make load-order irrelevant.** It pins steady-state KV (the −KV subtraction never runs — verified, gpu_worker.py:366-384), but the startup gate `request_memory` (`free ≥ total×gpu_util`, utils.py:408-421) still fires, reading gpu_util **unconditionally**. → The resolver must emit **both** the byte budget **and a co-lowered gpu_util** = the measured-footprint fraction. Steady-state becomes order-free; the bring-up instant doesn't. (Areas 1+2, converged.)
2. **The crash-loop root cause was NOT "co-tenants counted against the budget."** Recovered logs: `gpu_util 0.35 → requested 5.60 GiB < weights 5.67 GiB → KV −8.42 GiB before any co-tenant`. A hand-guessed fraction *below the model's own weights*. Co-tenant memory is a diff that mostly cancels; the only co-tenant route is **churn during the profile window**. (Area 2, from journalctl — Observed.) → An absolute byte budget computed from measured weights *structurally cannot* underflow the weights. Purest vindication of the thesis.
3. **The cuda-graph "blind spot" is closed by default in 0.21** (`VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=True`, accounted + subtracted) — **but our `services.json` explicitly sets it to `0`, re-opening it.** → Drop that env (a self-inflicted bandaid).
4. **`enforce-eager` is NOT a free global default — it's a ~39% decode-latency tax** (89→54 tok/s; worse on a small launch-bound 4B). → Per-loadout: worker uses eager (determinism), conversational keeps CUDA graphs (+ accounts the ~0.43 GiB explicitly). (Area 4.)
5. **Do NOT auto-derive `max_num_seqs`** — vLLM picks 256 on our card → ~8.5 GiB Mamba toll → guaranteed OOM. Set it explicitly per loadout. (Area 5.)

## The headline NEW BREAK — the worker loadout fails SILENTLY (Area 4, the make-or-break)
vLLM rents **1056-token blocks** (forced, to align the hybrid Mamba page with the attention page). For the `@extract` worker (small window, 32 concurrent, sub-block jobs) this means, with **no error**:
- **silent concurrency cap** — a 16K window = 15 blocks → only 15 concurrent, not the declared 32;
- **prefix-cache ~0% below the block** → measured QPS halves (200→<100);
- **a 2-8× KV under-count** the moment sizing tightens per the "size to NEED" mandate (a 480-tok job rents a full 1056 block).
None of this is OOM (a pinned slab can't be overrun — it queues/preempts). It's the worker failing *slowly and silently* — the worst kind to detect. **→ The resolver must reason in WHOLE BLOCKS, not tokens, and surface the real concurrency a window supports LOUDLY.**

## The single most important strategic reframe (Area 4's steelman, adopted)
**"Compute" must mean "look up the measured-once per-loadout row + scale by live headroom" — NOT "re-run a token-linear formula live."** A live formula that mismodels the engine (block-quantization, activation contamination) is *worse* than a measured-once table that's right — and every error mode found pushes a live formula toward over-prediction → the exact OOM that bit us. This reconciles Tim's "nothing hand-guesses" mandate with the safety asymmetry: **measure each loadout once (real numbers, block-rounded), store the row, and at bring-up look it up + check it against live headroom.** The danger was never "computing" — it was computing from a wrong model of how vLLM allocates.

## The decisions (named)
- **Profiler:** one `VLLM_LOGGING_LEVEL=DEBUG` boot yields the 4-term split + vLLM's OWN suggested `--kv-cache-memory=<bytes>` (gpu_worker.py:663-685) — *read its suggestion, trust-but-verify*; a 2-point `max_num_seqs` sweep **at fixed SHORT length** isolates per-seq state (the 34 MiB was contaminated upward by activation — measure clean). Use torch-allocator APIs (nvidia-smi per-proc = `[N/A]` on WSL). v1 = explicit `company profile <key>`; auto-on-add is v2.
- **Budget seam:** new `gpu.auto_kv_bytes(reg,key)` sibling to `auto_gpu_util`, emitted in `serveconfig.args_for` — **not** the resolver's serve_values (a computed integer isn't a static enum→fragment). Emits `--kv-cache-memory-bytes` + the co-lowered `--gpu-memory-utilization` gate together.
- **Shape tension resolved:** ONE good model config (`max_num_seqs=32` + chunked-prefill + priority — Area 5 shows it serves both shapes, ~1 GiB Mamba cost), and **the loadout axis is CO-RESIDENCY** (worker = embedder evicted / big shelf; conversational = embedder resident / smaller shelf) — Areas 3+5 reconciled. A loadout/combo must gain per-service **shape fields** (today it's only a service-key list).
- **Priority scheduling** is real but a **dead wire** — `fabric/transport.py:44` allowlist drops `priority`. One-point fix (allowlist + a `run_role` param; everything funnels through it) → foreground chat preempts background swarm.
- **Adopt no proxy wholesale** (Area 6): llama-swap's VRAM knob *is* the static fraction we're killing; LLMSnap is a reference impl of sleep; LiteLLM redundant. Build the thin layer; adopt vLLM built-ins.
- **Selection = 3 faces** on the ~70%-built spine: Tim (enriched `company combos` in units), MCP agent (a `loadouts` capability section + a `requires` param on `run_role`), RHM (a raise-not-actuate `select_loadout` verb). Close 2 gaps: loadouts invisible over MCP; `run_role` not requires-gated like cascades.

## VERIFY-FIRST gates (do NOT build on these until proven on our 0.21 + box)
1. **Mamba SSM silent-corruption fix** — is the AI21 prefill-path fix in our 0.21? If absent, tight-budget high-concurrency loadouts can emit *plausible wrong tokens, no error*. **Verify before Phase 4/5.**
2. **sleep-mode** — broken since 0.14 (#32714, frees ~6 not ~20 GB); fallback reload is 30-60× slower than the assumed ~1s. Treat as **unavailable** until proven; design card-sharing on reload-based switching meanwhile.
3. **KV-offload-to-RAM** — needs pinned memory; unreliable on WSL2 → the ~15× PCIe cliff. Do **not** bank conversation-persistence on it; verify pinned memory works first.
4. **fp8-KV on tool-calling** — concedes (~1-2 pts on reasoning); no published numbers on strict-JSON tool calls. One-shot diff our tool suite fp8-KV on/off.
5. **enforce-eager latency** on our 4B — measure ITL before committing the worker to eager.

## What this is NOT (scope guard)
Not a live token-formula. Not sleep-mode-dependent. Not KV-offload-dependent. Not a new proxy. It's: measure-once → store block-rounded per-loadout rows → bring-up looks up + checks live headroom + co-lowers gpu_util → vLLM built-ins (priority, chunked-prefill, prefix-cache) adopted where verified-safe → loadouts carry shape → 3 selection faces.
