---
type: build-plan
register: prescriptive
aliases: ["GPU/Serving/Loadout Rework — Build Plan", "measure-then-compute build plan"]
tags: [gpu, vllm, loadout, profiler, build-plan, build-prep]
status: unconfirmed
coverage: {built_against: "SYNTHESIS.md (post research-wave) + the 6 companions, 2026-06-30"}
---

# Build Plan — GPU/Serving/Loadout rework

Built against `SYNTHESIS.md`. Reshaped by the wave: **a VERIFY-FIRST phase gates everything; the budget is a block-aware measured-once table (not a live token-formula); sleep-mode + KV-offload are de-risked, not banked; enforce-eager is per-loadout.** Each criterion is verified BY USE (a real boot / a real turn / measured numbers), committed, no-regression. Everything lands in the CLI + docs + loadout attachments + gpu-calc + swapping (Tim's standing requirement).

**Note:** most phases need the FP8 brain free (it's mid-audit for the sibling session in the solo-32 worker shape). Phase 0/1/2 require a clear card → run them when the audit is done OR coordinate a window. Code-only sub-steps can land anytime.

## Phase 0 — VERIFY-FIRST spikes (cheap; gate the phases that depend on them)
Each writes a measured answer into SYNTHESIS "verify-gates" + (where relevant) the `_profile`. None is built-upon until answered.
- **0.1 Mamba SSM corruption fix** — is the AI21 prefill-path fix in our 0.21 source? (read vllm scheduler; if unclear, drive token-budget exhaustion at high concurrency + check for garbage). BLOCKS Phase 4/5 worker reliance. If absent → fail-loud floor + pin the build.
- **0.2 sleep-mode** — boot FP8, `/sleep level 1`, measure freed VRAM (expect ~weights-freed; #32714 says it may free far less). If broken → card-sharing is reload-based; design Phase 4 on that.
- **0.3 KV-offload on WSL2** — does pinned memory work? If not → do NOT bank conversation-persistence on offload.
- **0.4 fp8-KV tool-calling** — run the brain's tool-call suite fp8-KV on vs off, diff. Expect ~no degradation; confirm.
- **0.5 enforce-eager ITL** — measure decode latency eager vs graphs on our 4B (expect ~39% hit → confirms per-loadout, not global).
- **0.6 attribute-read reachability** — can the profiler read `worker.peak_activation_memory` etc. post-init, or is an RPC needed (EngineCore child-proc)? Decides profiler strategy (a) log-parse vs (b) attribute-read.

## Phase 1 — The profiler (`company profile <key>`)
FUNCTION: a `VLLM_LOGGING_LEVEL=DEBUG` boot parses the 4-term split + vLLM's own suggested `--kv-cache-memory=<bytes>` (gpu_worker.py:663-685); a 2-point `max_num_seqs` sweep **at fixed SHORT length** isolates per-seq state clean (un-contaminate the 34 MiB); torch-allocator APIs (not nvidia-smi); writes the rich `_profile` `{fixed_mb, kv_kb_per_token, per_seq_mb, per_seq_mb_computed, activation_mb, non_torch_mb, cudagraph_mb, block_size, kv_cache_dtype, suggested_kv_bytes, kind: vllm|inproc, measured}`. Generalises to the non-vLLM embedder + kokoro via the in-proc probe (weights+activation only). v1 = explicit operator command; auto-on-add = v2.
- ☐ verified: `company profile chat-4b-fp8` writes a complete profile; a re-run is stable (±small); the embedder profiles via the inproc path; the 34-vs-49.5 per-seq gap is resolved or both stored with divergence flagged.

## Phase 2 — Block-aware computed budget (kills the hand-guess, all services)
FUNCTION: `gpu.auto_kv_bytes(reg,key)` (sibling to `auto_gpu_util`) computes the absolute KV shelf from the `_profile` + the loadout target + **live headroom**, reasoning in WHOLE 1056-blocks; `serveconfig.args_for` emits `--kv-cache-memory-bytes <n>` + a **co-lowered `--gpu-memory-utilization`** = measured-footprint fraction (so the startup gate passes at the real footprint, not a hand fraction). Drop the `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0` env (self-inflicted blind spot). Populate the FP8 `_profile` + REMOVE its static `gpu_util: 0.9`. Surface a loadout's declared `max_num_seqs` vs its REAL block-concurrency LOUDLY (the silent-cap fix). Apply to brain + embedders + voice.
- ☐ verified: every service launches from a computed budget (zero hand-set gpu_util remain); a worker window that can't hold its declared concurrency says so loudly (not silently caps); bring-up succeeds in any order when the set fits (sequencing only for the irreducible weights-resident instant); resource_capacity suite green again.

## Phase 3 — Loadouts carry shape + adopt the scheduler built-ins
FUNCTION: a loadout/combo gains per-service **shape fields** (max_model_len, max_num_seqs, enforce_eager, priority, co-residency) — today a combo is only a service-key list. Fix the presence-vs-shape blindness at BOTH layers (the requires-gate/_resolve_loadout AND `ensure_resident`'s already-resident no-op → a shape-match→reload branch). Wire **priority** (add to `fabric/transport.py:44` allowlist + a `run_role` param → foreground chat preempts background swarm). Confirm chunked-prefill + prefix-cache on; enforce-eager per-loadout (worker=eager, conversational=graphs+trimmed capture). Declare `@interaction` (embedder resident) + `@extract` (embedder evicted, big shelf) as the two co-residency loadouts of the SAME model config.
- ☐ verified: the two loadouts differ by co-residency, both computed-budgeted; a foreground chat turn preempts a running background swarm (by use); switching a loadout reloads only on a shape-change (not a no-op); the @extract loadout is a one-command declared thing (retires the hand-built solo-32).

## Phase 4 — Card-sharing (GATED on 0.2)
FUNCTION: if sleep-mode works on our model → wire `/sleep`+`/wake` into the loadout switch (sleep one brain, wake another). Else → reload-based switching, latency budgeted honestly at "tens of seconds," never promised sub-second.
- ☐ verified: a model-axis switch (4B↔9B) works by the chosen mechanism, RHM repointed (the active-brain path already does this), verified by a real turn on the new brain.

## Phase 5 — Selection surfaces (3 faces + 2 gaps)
FUNCTION: Tim = enriched `company combos` showing each loadout in units ("deep chat / 32-worker / N concurrent / evicts embedder"); MCP agent = a `loadouts` section in `capabilities()` (close gap: loadouts invisible over MCP) + a `requires`/loadout param on `run_role` (close gap: run_role not requires-gated like cascades); RHM = a raise-not-actuate `select_loadout` verb. All on the ~70%-built requires-gate spine.
- ☐ verified: each actor can see + select a loadout for a job, by use (Tim via CLI, an agent via the MCP tool, the RHM via the verb); the gate surfaces a confirm + fails loud on a missing loadout.

## Phase 6 — Everything into CLI + docs (the standing requirement)
FUNCTION: `company profile`, the computed-budget readout, the per-loadout flags, the selection faces — all first-class `company` commands, documented in `docs/brain-loadouts.md` + a new profiler how-to. No raw vLLM flags hand-set anywhere.
- ☐ verified: a fresh agent can profile a new model, see its computed budget in units, declare a loadout's shape, and select it — entirely through `company` + the docs, no raw `vllm`.

## Phase 7 — The repo gate-reds (separate, queued)
The ~42 pre-existing red acceptance suites (mostly live-dep skip-marking + a few real fixes) → a true green `company suites`. Tim queued walking through these together.

---
## Sequence + dependencies
0 (verify) gates 4/5-reliance and informs 1/2 · 1 (profiler) → 2 (budget) is the spine · 3 builds on 2 · 4 gated on 0.2 · 5 on the requires-gate (built) + 2/3 · 6 documents 1-5 · 7 is independent. Phases 1-4 need a clear card (post-audit window). Code-only sub-steps (the priority allowlist wire, the loadout shape-fields schema, the gate reload-branch) can land anytime.
