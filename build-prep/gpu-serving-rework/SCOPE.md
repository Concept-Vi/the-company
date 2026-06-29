---
type: scope
register: descriptive
aliases: ["GPU/Serving/Loadout Rework — Scope", "compute-don't-guess scope"]
tags: [gpu, vllm, loadout, serving, profiler, scope, build-prep]
status: unconfirmed
coverage: {captured_from: "live session 2026-06-30", note: "braindump of everything discussed — the don't-lose-it doc; grounds the research-wave + build plan"}
---

# GPU / Serving / Loadout Rework — full scope (captured 2026-06-30)

The "write down everything we talked about" doc, so nothing is lost to compaction. This is the INPUT to a `/research-wave` and the build plan that follows. **Nothing below is the final design** — it's the captured understanding + intent. Verify against the research wave before building.

## The mandate (Tim, verbatim intent)
- **"That 50% has gotta go."** Stop hand-guessing resource params. Everything computed from a model's MEASURED costs + LIVE-available headroom, expressed in Tim's UNITS (e.g. "16K context = N GB", so an agent reasons "5 GB free → 128K fits"). Applies to ALL services — brain, embedders, voice — not just the brain. → [[feedback-compute-dont-guess-reach-for-stack]]
- **Reach for the stack first.** vLLM + the industry already solve most of what we hit; bandaids/abstract-caps/custom-work over already-solved problems are the anti-pattern. Find the built-in capability, use it; custom only where the stack genuinely lacks.
- **Everything built into the system.** All flags/features become first-class `company` capabilities: in the CLI, in the docs, **attached to loadouts** (a loadout declares its KV budget / concurrency / priority / sleep behaviour), fed by the computed gpu-calculation, driven by loadout swap + detection. Nothing stays a raw hand-set vLLM flag.
- **Loadout selection is multi-actor:** Tim, the MCP agents, and the RHM all able to SEE and SELECT loadouts for jobs.
- **Measure manually first, understand, THEN build the generalised/automated version.** Don't generalise before knowing how it works.
- Process: capture (this doc) → `/research-wave` → build plan against it → build (don't build on shallow understanding).

## DONE already this session (committed — the loadout BRAIN layer)
- Atomic loadout switch repoints the RHM, BOTH doors (apply_loadout + `company up @loadout`), verify-probe + revert (b902c1c).
- Work declares `requires: <loadout>` + an action/cascade resolve-gate that surfaces a confirm + fails loud (44a8e61).
- `run_role` applies per-role `knobs` (afa7266); per-FAMILY sampling defaults under per-role/per-call override (a84861c); think knob verified both directions on the FP8.
- `active_brain()` — the resident-brain SENTINEL resolves to the RUNNING brain; the whole cognition layer follows the live loadout (816b8ef). Context-overflow→cloud gate follows the active brain (ab51b2e).
- `auto_gpu_util` extended with the per-seq Mamba term `per_seq_mb × max_num_seqs` (0045363) — dormant for the FP8 until its profile is populated + static gpu_util removed.
- Restored ops/services.json (human-error deletion, resolved) → [[reference-services-json-deletion-incident]].

## The MEASURED FP8-4B profile (real, from this session's sweep — RedHatAI/Qwen3.5-4B-FP8-dynamic, :8001)
- **weights** = 5.67 GiB (boot log "Model loading took 5.67 GiB")
- **KV per token** ≈ 17.4 KB at fp8-KV (110,176 tok = 1.87 GiB; 439,756 tok = 7.47 GiB — consistent). So **1 unit (16,384 tok) ≈ 0.28 GiB per concurrent full-context seq.**
- **per-seq Mamba state** ≈ 34 MiB/slot MEASURED (shelf 439,756→380,868 tok as max_num_seqs 2→32 at gpu_util 0.85 solo = ~1.0 GiB / 30 slots). NOTE: research COMPUTED ~49.5 MiB from architecture — measurement governs; the gap is exactly why we measure not compute.
- **CUDA-graph** ≈ 0.43 GiB, captured AFTER the memory-profiling pass → a blind spot the budget doesn't see (the warning: "increasing gpu_util from 0.85 to 0.877").
- **co-resident penalty**: same gpu_util 0.5 gave KV +1.87 GiB solo vs −3.78 GiB with the embedder up (~5.6 GiB swing = the embedder's footprint counted against vLLM's budget).
- forced **block/page size 1056 tokens** (attention page padded to equal the Mamba page) → prefix-cache hit-rate drops toward 0 below the block size (hurts many-small jobs); internal fragmentation (small requests round up to a 1056 multiple).
- Architecture: hybrid, **8 full-attention + 24 Gated-DeltaNet (linear) layers**; 262,144 native context ceiling.

## The mental model (the rules, as taught)
- **KV cache = a shelf of token-slots.** concurrency × per-request-length must fit the shelf at a given instant.
- **gpu_util = a fraction of TOTAL card, per-instance** (since vLLM v0.6.4 — NOT free VRAM; correction to an earlier wrong claim). The co-resident OOM happens because (a) non-vLLM co-tenants (embedder/voice) are counted as "non-torch" device memory inside vLLM's budget, AND (b) vLLM's STARTUP PROFILING pass needs activation memory physically free at that instant → load-order matters at startup even with budgets. The complete fix = absolute byte budget (`--kv-cache-memory-bytes`) + `--enforce-eager` (kills the cuda-graph blind spot) + controlled load sequence (or sleep-mode handoff).
- **max_model_len = per-request CEILING, not a reservation** (paged attention rents slots as a request actually grows). **max_num_seqs = concurrency cap**, each slot a fixed ~34 MiB Mamba toll reserved at load (changing it = a reload).
- **Idle conversation history is FREE** (evictable prefix cache); only ACTIVE forward-passes compete for the shelf at an instant. A 100K idle chat + 32×2K concurrent jobs only collide if the 100K turn FIRES while the jobs are still generating (then it queues, never crashes).
- **The shelf can be divided any number of ways**; queue + RECOMPUTE-preemption handle overflow gracefully.

## The flags (what each does — to be made first-class company capabilities)
SIZING: `--gpu-memory-utilization` (old fraction, to retire) · **`--kv-cache-memory-bytes`** (absolute KV budget — the keystone; VERIFIED in our 0.21) · `--num-gpu-blocks-override` (blunter absolute, fallback) · **`--enforce-eager`** (kill cuda-graph blind spot → deterministic footprint) · `--kv-cache-dtype fp8` (halve KV — ON).
MIXING SHAPES: `--enable-chunked-prefill` (slice big prompts, interleave with small — ON in V1) · `--max-num-batched-tokens` (per-step work; ITL vs TTFT dial) · `--max-num-seqs` (concurrency cap; auto-derived if unset) · `--scheduler-reserve-full-isl` (admit only if full input fits).
CACHE: `--enable-prefix-caching` (reuse shared prefixes — ON) · `--kv-offloading-size` (park evicted KV in CPU RAM — NOT on, the "many threads' caches in RAM" win) · (`--cpu-offload-gb` = WEIGHT offload, different, not for us).
FOREGROUND/BACKGROUND: **`--scheduling-policy priority`** (chat jumps ahead of swarm/batch) · `--async-scheduling` (overlap CPU scheduling w/ GPU compute; opt-in).
CARD-SHARING: **`--enable-sleep-mode`** (free a model's VRAM, ~1s wake — BUT flagged buggy on some models, VERIFY ours) .
SPEED: speculative decoding n-gram (zero extra VRAM; helps when output echoes input).
All VERIFIED present in our vLLM 0.21 source: kv_cache_memory_bytes, enforce_eager, enable_sleep_mode, num_gpu_blocks_override, kv_offloading_size/cpu_offload_gb, scheduling_policy, async_scheduling, the _set_default_max_num_seqs_and_batched_tokens auto-derive.

## The existing mechanism to EXTEND (not parallel)
- `ops/cli/gpu.py: auto_gpu_util(reg,key)` — computes the gpu_util fraction from `_profile` (`fixed_mb`, `kv_kb_per_token`) + max_model_len + overhead. Now also `per_seq_mb × max_num_seqs` (0045363).
- `_profile` schema today: `{fixed_mb, kv_kb_per_token, [per_seq_mb], measured}`. AWQ chat-4b HAS one; chat-4b-fp8 was `null`.
- `ops/cli/gpu.py: budget_vram(reg,key)` priority: static gpu_util > auto_gpu_util > learned telemetry > registry estimate.
- `ops/cli/serveconfig.py: _resolved_gpu_util(key,c)` + `args_for(key)` — emit the serve command; fail-loud if neither static nor profile.
- `runtime/capabilities/` — the family/serve resolver (serve_flags, family_sampling). The flags above attach here as serve-contract capabilities.
- The loadout/combo system (services.json combos + extends/swap/add/remove variants); `apply_loadout` + `ensure_resident` + `active_brain`.

## RESEARCH already gathered (3+ reports landed; durable copies)
- vLLM capability map (the gpu_util-is-total correction; kv-cache-memory-bytes; auto-derived max_num_seqs; sleep mode; boot log prints capacity; auto_tune.sh). 
- Industry patterns: llama-swap pinned-groups (dissolves load-ordering — pin embedder+voice, swap the brain); vLLM-native CPU KV-offload beats standing up LMCache at our scale; MIG unavailable on Ada; MPS only helps the small tenants; TGI archived/dead; TEI/Infinity for embedders; speech belongs on CPU (reclaims 2-6 GB); quantization (Ada native FP8) is the thing that decides what fits.
- Profiling/auto-sizing: vLLM PRINTS the 4-term memory decomposition at boot (parse it, don't compute); per-seq state readable off the forced-block-size line; measure via torch allocator APIs + reset_peak_memory_stats (nvidia-smi over-reports by the CUDA context); slope/intercept regression splits KV-residual into per-token vs fixed. Artefact: `.data/unify-exercise/gpu-autoprofiler-research.html`.
- (A further research-wave is being run to deepen + surface unknowns before the build plan.)

## The 7-phase plan (intent — refine against the research wave)
1. **Auto-profiler** — load a model, parse its boot-log breakdown + a short knob-sweep, write its `_profile` (weights, per-token KV, per-seq state, activation peak). Auto-runs on model-add. (Manual measurement first — mostly done for the FP8.)
2. **Computed budgets** — from `_profile` + live headroom → emit `--kv-cache-memory-bytes` (+ `--enforce-eager`) per service (brain, embedder, voice). Replaces hand-pinned gpu_util everywhere. In Tim's units. Makes load-order stop mattering.
3. **Adopt in-engine features** — priority scheduling, async scheduling, KV-offload to RAM, confirm chunked-prefill + prefix-cache. Verify-by-use each.
4. **Multi-model card-sharing** — verify sleep-mode on our model; if good, wire into the loadout switch (sleep one brain, wake another — replaces evict-reload). Else order-aware bring-up stays the fallback.
5. **The `@extract` worker loadout** — small window + high concurrency + embedder evicted, as a DECLARED loadout (currently hand-built live for the other session's bulk audit; gpu_util 0.9 / max_num_seqs 32 / fp8-KV, solo, ~487k-token shelf, 32 concurrent).
6. **Loadout selection surfaces** — Tim / MCP agents / RHM see + select loadouts for jobs. Builds on the requires-gate.
7. **Repo gate-reds** — the ~42 pre-existing red acceptance suites (mostly live-dep skip-marking + a few real fixes) → a true green `company suites`.
Each phase: build → verify by use → commit → no regression. 1–2 are the spine; 3 mostly switches; 4–7 build on the spine. Everything lands in CLI + docs + loadout attachments + gpu-calc + swapping.

## Open questions / verify-not-trust (for the research wave + build)
- sleep-mode actually works on OUR Qwen3.5-4B-FP8 (flagged broken on some models since 0.14).
- the hybrid unified-pool padding can over-predict capacity (~7× on one AWQ workload) — measure, don't trust the estimate.
- prefix-cache ≈0% below the 1056 block — does it hurt the many-small @extract workload materially?
- per-seq state measured 34 vs computed 49.5 MiB — which governs at which max_num_seqs; re-measure across the range for the profiler.
- activation_peak as a % for a 3-7B on 16 GB Ada (the 10% vs 25% rules disagree) — measure.
- the conversational loadout must be RESTORED (FP8 → gpu_util 0.5 / max_num_seqs 2, co-resident with embedder+voice) after the other session's bulk audit; the worker shape is temporary.
- resting server-side sampling defaults (`--override-generation-config` / `--default-chat-template-kwargs`) — the resting-default half of per-family sampling, for raw-bypass requests.

## State right now (temporary)
- chat-4b-fp8 is SOLO @ :8001, gpu_util 0.9 / max_num_seqs 32 / fp8-KV — the hand-built @extract preview for the other session's coverage-audit. embed-pplx + tts-kokoro EVICTED. RHM still works (active_brain → :8001) but recall/voice are off until restore.
- resource_capacity T6a is RED because of this temporary config (interaction loadout can't fit at FP8=0.9) — expected, reverts on restore.
