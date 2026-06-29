# ANCHOR — the measure-then-compute GPU/serving/loadout model (research wave)

## 0 · How to read this
This is the **shared anchor** for a research wave. Read it IN FULL first, then read the companion `SCOPE.md` (beside it — the dense captured understanding + the measured numbers + every flag + the existing code to extend). **We are NOT confirming this** — stress-test it, contradict it where it's naive, ground every claim in what vLLM 0.21 (and the ecosystem) actually do. **Leave the idea bigger and more real than you found it** (expansion ratio > 1). The "yes, but actually…" is the gold. Mark every claim: **Observed** (file:line / doc URL) / **Inferred** / **External-prior-art** / **My-idea**. Write fully — your area was sized for depth.

## 1 · The problem (concrete, not abstract)
One 16 GB Ada GPU (WSL2, vLLM 0.21) hosts several models at once: an agentic **hybrid Mamba/attention** brain (Qwen3.5-4B-FP8 on :8001), a custom-server embedder (~5.4 GB), and voice (kokoro ~0.9 GB). Real pain we hit THIS WEEK:
- A sibling session raised the brain's `max_num_seqs` and **it wouldn't come back up** — `No available memory for the cache blocks`, even after reverting to a config that had run 40 min earlier. Root cause (proven from the boot log): at `gpu_util 0.5` co-resident, **`Available KV cache memory: −3.78 GiB`** — negative. Solo it was +1.87 GiB. A ~5.6 GiB swing = the co-residents counted against vLLM's budget + the startup profiling pass needing memory free at that instant.
- Every memory knob is **hand-guessed**: a static `gpu_util 0.5`, a fixed `max_num_seqs 2`, "load the brain first" as a workaround. Tim's verdict: *"that 50% has gotta go — nothing should hand-guess."*
- The same model wants **opposite shapes** for different work: deep-context low-concurrency (conversation) vs small-context high-concurrency (a bulk audit needing 32-at-once). Today that's a manual config flip that breaks the loadout-fit check.

## 2 · The insight / the big what-if
**What if no resource parameter is ever hand-typed — every one is COMPUTED from a model's MEASURED profile + the LIVE-available headroom, expressed in Tim's units ("16K context = N GB"), leaning entirely on vLLM/industry built-ins rather than custom bandaids — and the whole thing is attached to declarable LOADOUTS that Tim, MCP agents, and the RHM can select per job?**

Sub-what-ifs: Can we *measure* a model's true costs cleanly (weights, KV-per-token, per-seq state, activation peak) — mostly by parsing vLLM's OWN boot output — and generalise it to any model incl. the non-vLLM embedder? Can an absolute KV byte budget (`--kv-cache-memory-bytes`, verified in our 0.21) + `--enforce-eager` make load-order stop mattering? Can a loadout *declare* its shape (budget/concurrency/priority/cache/sleep) so "the work picks its shape" replaces hand-tuning?

## 3 · The shape, held loosely
- A **profiler** that loads a model once, parses the 4-term memory decomposition vLLM prints at boot + a short knob-sweep, and writes a `_profile` — auto-running when a model is added.
- A **computed-budget resolver** that turns `_profile` + live headroom into the actual serve flags (absolute KV budget, enforce-eager, concurrency) per service — extending the EXISTING `auto_gpu_util` (ops/cli/gpu.py), not a parallel system.
- **Loadouts that carry resource intent** — a loadout/combo declares the shape it wants (deep-context vs worker, priority, sleep-eligible, recall co-resident or not); bring-up computes the budgets so the set fits, in the right order.
- **Adoption of stack built-ins** instead of bandaids: priority scheduling (foreground chat > background swarm), chunked prefill + prefix caching (already on), KV-offload to RAM (conversation persistence), sleep-mode (VRAM time-share between models).
- **Multi-actor selection** — the CLI, the MCP tools, and the RHM all see + select loadouts for jobs.

## 4 · My ideas (marked as ideas, to be challenged)
- *My-idea:* `_profile` schema = `{fixed_mb, kv_kb_per_token, per_seq_mb, activation_mb, cudagraph_mb, block_size, measured}`. (Today it's only `fixed_mb` + `kv_kb_per_token`; I added `per_seq_mb`.)
- *My-idea:* express budgets in "units" where 1 unit = 16,384 tokens, so an agent reasons "5 GB free → 128K fits."
- *My-idea:* the absolute byte budget (`kv-cache-memory-bytes`) is more robust than the gpu_util fraction because it pins the steady state; pair with `enforce-eager` to remove the cuda-graph blind spot.
- *My-idea:* the conversational↔worker shape tension is solved by TWO declared loadouts of the same model, not one tunable instance — but maybe sleep-mode or a second lightweight instance is better; unknown.

## 5 · Why it belongs here (existing machinery to build ON, not reinvent)
- `ops/cli/gpu.py: auto_gpu_util(reg,key)` — already computes a gpu_util fraction from `_profile`; `budget_vram` priority (static > auto > learned > estimate); `check_fit`/`plan_eviction`/`ram_fit` — the resource gate.
- `ops/cli/serveconfig.py: args_for(key)` + `_resolved_gpu_util` — emits the serve command.
- `runtime/capabilities/` — the family/serve-flag resolver (`serve_flags`, `family_sampling`, the serve_values enum pattern for kv_cache_dtype/vision); this is where new flags attach as serve-contract capabilities.
- `ops/services.json` combos + the extends/swap/add/remove **variant** mechanism; `apply_loadout` + `ensure_resident` + `active_brain` (the switch + the live-brain resolution, both built this session).
- The loadout-resolution `requires`-gate (work declares the loadout it needs) — built this session; the selection surfaces extend it.

## 6 · The honest hard parts (where it's fragile — the rigor area lives here)
- **The hybrid pool padding can over-predict capacity** (research saw ~7× on one AWQ workload). A measured profile that's wrong is worse than a fraction.
- **Prefix-cache hit-rate drops toward 0 below the forced 1056-token block** — may gut the win for the many-small worker workload.
- **Sleep-mode is reported broken on some models since vLLM 0.14** — the whole card-sharing idea leans on it; must verify on OUR model or fall back.
- **The per-seq state number is uncertain**: measured ~34 MiB/slot, research computed ~49.5 MiB — which governs, across what max_num_seqs range?
- **The cuda-graph blind spot** (captured AFTER profiling) can OOM at high gpu_util even with a "correct" budget.
- **Non-vLLM co-tenants** (the embedder, voice) honor no vLLM fraction — the budget model has to account for processes it doesn't control.
- **WSL2 quirks** (pin_memory off, nvidia-smi unreliable per-process) — measurement must use torch allocator APIs, not nvidia-smi.

## 7 · What I can already see (real anchors to verify + extend)
- `ops/cli/gpu.py:48 auto_gpu_util` (just extended w/ `per_seq_mb × max_num_seqs`, commit 0045363); `budget_vram` ~79; `_vram_overhead_mb`.
- `ops/cli/serveconfig.py:36 _resolved_gpu_util`, `args_for`.
- `ops/services.json`: chat-4b `_profile = {fixed_mb:5838, kv_kb_per_token:31.7}`; chat-4b-fp8 `_profile: null` (the gap); combos incl. interaction-fp8, quality-9b.
- Measured FP8 (this session): weights 5.67 GiB · KV ~17.4 KB/tok (fp8) · per-seq ~34 MiB · cuda-graph 0.43 GiB · block 1056 · co-resident KV −3.78 vs solo +1.87 at gpu_util 0.5.
- Verified-present 0.21 flags: `kv_cache_memory_bytes`, `enforce_eager`, `enable_sleep_mode`, `num_gpu_blocks_override`, `kv_offloading_size`, `cpu_offload_gb`, `scheduling_policy`, `async_scheduling`, the `_set_default_max_num_seqs_and_batched_tokens` auto-derive.
- Prior research artefact: `.data/unify-exercise/gpu-autoprofiler-research.html`.

## 8 · Open what-ifs (threads to pull)
- Is the absolute byte budget enough to make load-order irrelevant, or is sequencing/sleep-mode always needed for non-vLLM co-tenants?
- Should the profiler measure by a controlled sweep (vary one knob, read the shelf delta) or can it derive everything from ONE boot's 4-term log?
- Can one model serve both shapes live (priority + chunked prefill on one instance) so we DON'T need two loadouts or sleep-mode swaps?
- How do non-vLLM services (the custom embedder, kokoro) get profiled + budgeted in the same model?
- What's the right unit + interface for an MCP agent / the RHM to *select* a loadout — and what does "the work declares its shape" look like end-to-end?
- Is there a cleaner industry substrate (llama-swap pinned groups, LLMSnap, a router) we should adopt wholesale rather than build?

## Closing — spirit note to the agents
Bring what's ACTUALLY there — in our code, in vLLM's real source/docs, in the ecosystem — not what this anchor hopes. Where the anchor is naive, say so with evidence. Where a built-in already does what we'd build, name it. Where a number is uncertain, ground or refute it. Leave each area bigger and more real than you found it. The synthesis depends on your honesty, not your agreement.
