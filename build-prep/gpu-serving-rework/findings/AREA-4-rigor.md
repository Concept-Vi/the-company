---
type: research-finding
register: descriptive
aliases: ["AREA-4 — Rigor / Make-or-Break", "GPU rework — where the model is fragile"]
tags: [gpu, vllm, loadout, profiler, rigor, research-wave, build-prep]
status: unconfirmed
coverage: {note: "rigor lane of the measure-then-compute research wave; evidence from ops/cli/gpu.py + services.json (read), vLLM issues + blog (fetched 2026-06-30), and arithmetic on the session's measured numbers"}
---

# AREA 4 — Rigor / Make-or-Break: where measure-then-compute is fragile

**Mandate:** try to BREAK the measure-then-compute model. Default to "this is wrong, find why." The ANCHOR §6 and SCOPE open-questions already concede a list (hybrid 7×, prefix cliff, sleep-mode, per-seq 34-vs-49.5, cuda-graph, WSL2). Re-reporting those adds nothing. **My value is the delta.** Every finding below is tagged one of:

- **[NEW BREAK]** — a failure the anchor does NOT see.
- **[HARDENS]** — a conceded flag turned into a measured number or a refutation.
- **[CONCEDES]** — I attacked it and it holds; say so plainly, don't manufacture a break.

**The through-line — error DIRECTION is everything.** This week's incident was `No available memory for the cache blocks` — an **OVER-prediction of capacity at bring-up → OOM → "won't come back up."** The honest taxonomy of how a computed budget fails splits in two: (a) at **bring-up**, errors that make `need_mb` too small relative to what the engine reserves → the start is refused / OOMs (the incident's class: co-resident swing + startup-profiling instant); (b) at **run-time**, with `--kv-cache-memory-bytes` pinning a fixed slab, the slab **cannot be overrun** — vLLM queues/preempts — so the failures are **throughput collapse, silent concurrency caps, and silent SSM corruption**, NOT OOM. A conservative static fraction errs toward **waste** (never OOM). The design's stated direction — "size each model to its NEED, never over-grab" (gpu.py:54) — is what introduces the dangerous errors below. **The point of this lane: distinguish which failures are OOM-at-bring-up vs throughput/correctness-at-runtime, because the anchor blurs them, and the fixes differ.** That is the spine.

---

## ★ Headline NEW BREAK — block-quantization guts the worker loadout (concurrency cap + prefix-cache death NOW; a 2-8× under-count the MOMENT the design tightens KV sizing)

**First, what the code does today** (I initially misread this — correcting it makes the finding *sharper*, not weaker). `auto_gpu_util` (ops/cli/gpu.py:71) sizes the KV term by `max_model_len`, a **shared pool**, NOT by `max_num_seqs × req_len`:

```python
kv_mb = kv_per_tok * mml / 1024.0       # mml = max_model_len: ONE full-context seq's worth of slots
                                        # max_num_seqs does NOT enter the KV term  [Observed gpu.py:71]
```

So today's formula **over-provisions** KV for the worker (sizes for a 65536-token pool when jobs are 480 tokens) — safe-but-wasteful, the *opposite* of OOM. **Two real defects remain even so:**

**Defect A — silent concurrency cap (present in the live code).** The formula never checks that the pool holds `max_num_seqs` concurrent sequences' *minimum* footprint. On this hybrid every active seq needs **≥1 block = 1056 tokens** the instant it runs. 32 concurrent seqs need ≥ `32 × 1056 = 33,792` token-slots **minimum**. If a loadout sets a small `max_model_len` (the worker wants a *small* window) the KV pool sized by `mml` can be **smaller than 32 minimum-blocks** → declared `max_num_seqs=32` **silently caps** to whatever fits. e.g. a 16K worker window = 15 blocks = **15 concurrent seqs max, not 32** — the loadout quietly delivers under half its declared concurrency, no error. Direction: **silent under-delivery of the worker's whole reason to exist.** [Inferred — from gpu.py:71 + 1056 block + SCOPE.md:36]

**Defect B — the 2-8× under-count the design's own direction walks into.** The mandate is "size each model to its NEED, never over-grab" (gpu.py:54). The *natural* next step — and the only way to make a tight worker budget — is to size KV per-concurrency/per-request rather than by `mml`. **The instant the formula moves that way, block-rounding under-predicts 2-8×**, because vLLM rents whole 1056-token blocks: a 480-token request consumes a full 1056-block. The fix `ceil(req_len/block) × block × N` becomes **mandatory** the moment KV sizing tightens. This is a break in the *proposed direction*, not the current code — stated as such.

I computed the rounding at the measured fp8 rate (17.4 KB/tok, SCOPE.md:32):

| request length | blocks rented | tokens charged | formula KV | actual KV | **under-count** |
|---|---|---|---|---|---|
| 128 tok | 1 | 1056 | 2.17 MB | 17.94 MB | **8.25×** |
| 256 tok | 1 | 1056 | 4.35 MB | 17.94 MB | **4.12×** |
| 480 tok | 1 | 1056 | 8.16 MB | 17.94 MB | **2.20×** |
| 512 tok | 1 | 1056 | 8.70 MB | 17.94 MB | **2.06×** |
| 1056 tok | 1 | 1056 | 17.94 MB | 17.94 MB | 1.00× |
| 2048 tok | 2 | 2112 | 34.80 MB | 35.89 MB | 1.03× |

*(arithmetic, this session; `under-count = actual / formula`)* — **[Inferred — computed, not run on the live engine]**

**Why the worker loadout is the worst place for it.** The whole reason the profiler exists (SCOPE Phase 5) is the `@extract` worker: **small window, high concurrency (max_num_seqs=32), many short jobs** — every request *below* the 1056 block, rounding up hard. The damage is NOT OOM (the pinned slab can't be overrun — vLLM queues/preempts). It is two things the token math hides:

1. **Effective shelf shrinks 2-8×.** 32 concurrent 480-token jobs occupy `32 × 1056 = 33,792` real slots while the token math counts `32 × 480 = 15,360`. The shelf the operator *thinks* holds the batch holds less than half of it → **more preemption, lower throughput, queued jobs** — exactly the worker loadout's failure mode (slow, not crashed).
2. **Prefix-caching dies below the block.** Forcing block size to 1056 means prefix caching only works at that coarse boundary; below it, **~0% cache hit** [Observed — research finding 3 / vllm#40696]. Real measured impact: **QPS halved (200 → <100) just by shortening a prompt from 560 to 480 tokens.** For the many-small worker workload (routing/classification/extract), treat prefix caching as **absent** — the "one shelf, many small jobs" win is far worse than the token math implies.

**Bridge to the conceded 7.3× (ANCHOR §6 / research finding 2), corrected.** The anchor's defence — "we MEASURE load-deltas, so we escape vLLM's *computed* hybrid over-reservation" — holds for the boot capacity number. But measuring the *rate* (17.4 KB/tok) doesn't save you the moment you size by *requested* tokens instead of *block-rounded* tokens (Defect B). The anchor footnotes "internal fragmentation (small requests round up)" (SCOPE.md:36) but **never connects it to (a) the silent concurrency cap or (b) prefix-cache death** — and those, not OOM, are the worker loadout's real breaks. That connection is the finding.

**The fix:** the resolver must reason in **whole blocks**, not tokens — `blocks = ceil(req_len/1056)`, real concurrency `= floor(KV_pool_tokens / 1056)`, and surface "this loadout's declared max_num_seqs=32 actually fits N at this window" so the cap is **loud, not silent**. And it must treat prefix-caching as off for sub-block workloads when sizing throughput expectations.

---

## NEW BREAK — sleep→wake on a HYBRID model is a silent-correctness landmine, not just a memory regression

The card-sharing story (ANCHOR §3, SCOPE Phase 4) leans on `--enable-sleep-mode`. Two independent pieces of fetched evidence say the danger on OUR model is worse than "buggy on some models":

1. **Sleep is broken since 0.14.0 [Observed — issue #32714, fetched 2026-06-30].** In 0.13.0, sleep level 1 freed 20 GB+; in 0.14.0 it frees only ~6 GB, leaving ~16 GB resident (vs the expected 1.14 GB). It is a **memory-freeing regression** — sleep stops reclaiming VRAM, which is the *entire point* for card-sharing. Reverting to 0.13 fixes it. The issue does NOT mention Mamba/FP8 specifically, so on memory alone this is "verify on our 0.21." But —

2. **The Mamba state is a known silent-corruption surface under exactly our conditions [Observed — AI21 blog, fetched 2026-06-30].** Separate from sleep: vLLM misclassifies a *new* request as `decode` when the **token budget is exhausted** (a 1-scheduled-token request is treated as decode regardless of whether it's new), so it **reads stale SSM state from a previous request's slot instead of zero-initialising.** Because "the state accumulates recursively, garbage at the start corrupts everything that follows" — the model emits plausible-looking garbage, **no crash, no error.** Triggering conditions verbatim: **low `gpu_memory_utilization` (tested 0.2), token-budget exhaustion, new request arrival.**

**Headline condition — this is fully gated on the 0.21 build.** The AI21 fix (new requests always take the prefill path) shipped; **whether our vLLM 0.21 contains it is the first thing to verify** — if it does, this finding is a near-non-issue (CONCEDE); if it doesn't, it's a live correctness landmine. So: **VERIFY the prefill-path fix is in 0.21 before anything else in Phase 4/5.**

**Why it plausibly lands on us** *(the budget→trigger link is INFERRED, not measured — stated honestly).* The corruption's documented trigger is **scheduler token-budget exhaustion** (`max_num_batched_tokens`), tested at gpu_util **0.2**. That is *not the same axis* as a tight `--kv-cache-memory-bytes` KV slab — they are different knobs. My claim is only that they **correlate**: a tight-budget, high-concurrency worker loadout running near its scheduling limits is *more likely* to hit token-budget exhaustion than a roomy conversational one. I have **no measurement** that our tight budgets trigger it — I flag it as a regime to test, not a proven path. What IS certain and severe: when it fires, the failure is **wrong tokens that look right** — invisible to "no error = working," the worst class for an agentic brain.

This is a NEW break because the anchor frames hybrid risk purely as *capacity over-prediction* (a memory problem); the recursive-state corruption is a **correctness problem**, on a different axis, and on a small model unusually sensitive (it's the recursive SSM state, not attention KV, that accumulates garbage). → if the fix is absent in 0.21: add a fail-loud floor and pin to a fixed build; if present: CONCEDE and note the sensitivity.

---

## HARDENS — sleep-mode fallback cost, quantified (the card-sharing economics)

If sleep-mode is unusable on our model (likely, per the two findings above), the fallback is teardown + cold reload. I costed it [Inferred — arithmetic]:

- **Sleep working:** ~1–2 s wake (CUDA restore, weights stay paged).
- **Cold reload of the 5.67 GiB FP8 brain:** disk read alone ~1.1 s (NVMe 5 GB/s) to ~11 s (WSL2 9p path is slow), **plus** vLLM engine init + memory-profiling pass + CUDA-graph capture ≈ tens of seconds (20–90 s cold typical).
- **Gap: ~30–60×.**

So the card-sharing win (`sleep one brain, wake another` — SCOPE Phase 4) is **real only if sleep works**; the fallback (order-aware bring-up + reload) is **not a near-equivalent** — it's a 30-60× slower swap. The loadout-switch UX cannot promise sub-second model handoff on the fallback path. The honest design position: **treat sleep-mode as UNAVAILABLE on Qwen3.5-4B-FP8 until proven by use on 0.21**, and budget the loadout-switch latency at "tens of seconds, reload-based." (ANCHOR §3 says "~1s wake" as if granted — that number is the *best* case of an *unverified* feature.)

---

## HARDENS — the per-seq 34 MiB measurement is contaminated UPWARD; linearity is unproven by the method that produced it

ANCHOR §6 / SCOPE.md:33 flag "measured 34 vs computed 49.5 MiB — which governs." I attack the **measurement**, not just the gap.

The 34 MiB/slot came from: shelf 439,756 → 380,868 tokens as `max_num_seqs` 2 → 32 at gpu_util 0.85 solo, i.e. ~1.0 GiB / 30 slots [Observed SCOPE.md:33]. **But `profile_run()` sizes its dummy prefill batch by `max_num_seqs`** [Observed — research HTML §02, vLLM gpu_worker.py profile_run]. Raising max_num_seqs 2→32 therefore **also grows `activation_peak`**, and the activation peak is subtracted from the same pool the shelf is measured in. So the 1.0 GiB shelf drop is **per-seq Mamba state + the growth in activation peak**, conflated. The 34 MiB is an **upper bound contaminated upward**; the pure per-seq state is *below* it — which means the 34-vs-49.5 gap is **partly an artifact of the measurement method, not (only) a real architecture-vs-reality discrepancy.**

Consequence for the profiler: the formula `per_seq_mb × max_num_seqs` (gpu.py:79) assumes the term is (a) pure per-seq state and (b) **linear in max_num_seqs.** Pure SSM state genuinely IS O(1)/seq (research finding §03.1), so linearity is *plausible* — but the activation-peak contamination is itself **super-linear-ish** in batch and is being smuggled into the per-seq coefficient. **The method that produced 34 cannot separate them.** The clean protocol (research HTML §02 steps 3-4) is mandatory: vary concurrency **at fixed SHORT length**, and subtract an **independently measured** activation_peak — otherwise the profiler bakes activation growth into a coefficient it then multiplies by max_num_seqs, double-counting it. Direction of the resulting error: the coefficient is too *high* → the budget reserves too *much* per-seq → it errs toward **under**-prediction (waste) here — the one term that's conservative. Fine for safety, wrong for accuracy, and it means the "34 governs" decision (SCOPE.md:33) is resting on a number that isn't what it claims to be.

---

## NEW BREAK — `--enforce-eager` as a global default is wrong; it's a ~39% decode-latency tax on the conversational loadout

ANCHOR §4 *my-idea* (line 27): "pair [the byte budget] with `enforce-eager` to remove the cuda-graph blind spot." Stated as a general pairing. **It is not free, and the anchor presents it as if it were.**

- Disabling CUDA graphs returns per-step kernel-launch overhead. Measured: **89 tok/s → 54 tok/s, ≈39% slower decode** [External — vLLM parameter benchmark, fetched 2026-06-30].
- A 4B model's decode step is cheap, so it is **launch-overhead-bound** — exactly where CUDA graphs help most and enforce-eager hurts most. The smaller the model, the bigger the relative hit.

So enforce-eager is **per-loadout, not global**:
- **Worker loadout** (throughput-bound, batch audit): enforce-eager is fine — deterministic footprint matters more than per-token latency.
- **Conversational loadout** (latency-bound, Tim talking to the brain): a 39% decode-latency hit is a **felt regression** in the primary interaction.

The anchor's clean "byte-budget + enforce-eager makes load-order stop mattering" is half-right: it buys determinism by spending interactive latency. The design must let the **loadout** choose (it already declares its shape — ANCHOR §3), and the conversational loadout should keep CUDA graphs + instead account for the ~0.43 GiB graph cost explicitly in its budget (the graph cost is measurable and now its own log line since 0.21 — research HTML §04). Direction note: with CUDA graphs ON, the ~0.43 GiB graph capture happens **after** profiling and is invisible to the budget → **OVER-prediction → OOM at high util** (the captured-after-profiling blind spot, SCOPE.md:34). So the real choice is: *enforce-eager (lose 39% latency, gain determinism)* **vs** *graphs-on (keep latency, must add 0.43 GiB to the budget by hand).* Both are viable; **neither is the free default the anchor implies.**

---

## NEW BREAK — `--kv-offloading-size` (the "many caches in RAM" win) collapses on WSL2

SCOPE.md:49 lists `--kv-offloading-size` ("park evicted KV in CPU RAM — the 'many threads' caches in RAM' win") as an adoption target (SCOPE Phase 3). WSL2 reality breaks it:

- CPU↔GPU KV transfer needs **pinned (page-locked) memory** for tolerable PCIe bandwidth; **pinned memory is unreliable/off under WSL2** [External-prior-art — WSL2 known limitation, also flagged ANCHOR §6 "pin_memory off"]. Without pinning, every offload/reload pays the un-pinned PCIe penalty (the research's "~15× offload cliff," SCOPE/prompt).
- The offload only pays off when the *same prefix* is reused (agentic loops with one system prompt — research HTML §05.4). The worker loadout's many *distinct* short jobs are the weak case.

So the "many small caches live in RAM" win is **doubly weak on our box**: WSL2 strips the bandwidth, and the worker workload (distinct requests) is exactly the pattern offload doesn't help. **Concede it for the conversational loadout** (one long-lived prefix, offload could persist idle history — SCOPE.md:43 "idle conversation history is FREE") **only if** pinned memory can be made to work on WSL2 — which must be VERIFIED, not assumed. Flag: do not list KV-offload as a banked win in the build plan; it is WSL2-gated.

---

## CONCEDES — fp8 KV cache does NOT degrade reasoning/tool-calling materially (do not conflate with INT4)

The prompt asks me to attack fp8-KV accuracy because "INT4-KV scored 0.00 on small thinking models." **That is a different format and I will not borrow its scare number.** [External — vLLM fp8-kvcache blog, fetched 2026-06-30]:

- FP8 KV-cache + FP8 attention on **Qwen3-30B-A3B-Thinking-2507** (a reasoning model, same family lineage as ours): **~1–2 points average accuracy change** across decode-heavy tasks; worst case 97% recovery (GPQA-Diamond). e4m3 (4 exp / 3 mantissa) with an fp32 per-tensor scale.
- The 0.00 cliff (research finding §05.3) is **INT4** KV, naive, *per-channel* — a 4-bit format with a tiny dynamic range, needing the SAW-INT4 rotation fix. **fp8 e4m3 is not that.**

**This holds.** The design is right to "build the math on FP8 as baseline" (research §05.1). My only residual caution, NOT a break: nobody has published fp8-KV numbers on *tool-calling structured output* specifically (the benchmarks are QA/reasoning, not strict-JSON tool calls), and our brain is agentic. Recommend a one-shot verify-by-use (run the brain's actual tool-calling suite fp8-KV on vs off, diff the outputs) — but I have **no evidence** of degradation, so the default is CONCEDE.

---

## CONCEDES (with a sharp caveat) — the non-vLLM co-tenant penalty is real but the byte-budget mostly handles it

ANCHOR §6 / SCOPE.md:41: the −3.78 GiB co-resident swing = the embedder (~5.4 GB) counted as "non-torch device memory" inside vLLM's budget. I attacked whether the byte-budget fixes this and it **mostly does**: `--kv-cache-memory-bytes` pins an **absolute** KV target, so it doesn't shrink when a co-tenant appears (unlike the gpu_util fraction, which is a fraction of *total* and silently collides). **BUT** — the startup **profiling pass still needs activation memory physically free at that instant** (SCOPE.md:41), and the absolute budget does NOT change that. So the byte-budget makes the *steady state* load-order-independent but **not the startup instant.** The anchor's open-question §8 ("is the byte budget enough to make load-order irrelevant?") — **answer: NO at startup, YES at steady state.** Sequencing (or sleep, if it worked) is still required for bring-up. Half-concede: the keystone flag is genuinely better than the fraction, but the "load-order stops mattering" claim (ANCHOR §2, SCOPE Phase 2) is **overclaimed by one regime** — it stops mattering *after* everyone is up, not *while* bringing the last one up.

---

## STEELMAN — "just a conservative static budget + sequencing" vs the full computed profiler

The prompt asks me to steelman the simpler design. Honestly:

- **What the static fraction gets right that the profiler gets wrong:** every error mode I found above (block-rounding under-count 2-8×, cuda-graph blind spot, startup-instant pressure, sleep unavailable, Mamba corruption at tight budgets) pushes the *computed* budget toward **OVER-prediction → OOM** — the literal incident. A conservative static fraction *cannot* OOM by over-prediction; it errs toward waste. **On the one axis that hurt us this week, the dumb approach is safer.**
- **Where the steelman fails (why the profiler still earns its place):** (1) Tim has mandated it — "that 50% has gotta go, nothing should hand-guess" (SCOPE.md:14); a static fraction is the thing being explicitly rejected. (2) The static fraction can't answer "5 GB free → does 128K fit?" in Tim's units — the whole point of the units idea (ANCHOR §4). (3) For a **changing model set** and **new-model onboarding**, hand-tuning every model is the toil the profiler removes.
- **The synthesis position I'd defend:** the profiler earns its complexity for **live-headroom computation + new-model onboarding + Tim's-units reasoning.** But for the **fixed, known model set**, the right artifact is a **measured-once per-loadout table** (profile each loadout ONCE by load-delta, record the real numbers incl. block-rounded KV, store them) — not a formula re-derived live on every bring-up. A live formula that's wrong (block-quantization) is worse than a measured-once table that's right. **Measure-then-compute, yes — but "compute" should mean "look up the measured loadout row + scale by live headroom," not "re-run a token-linear formula that mismodels the engine."** This reconciles Tim's mandate with the OOM-asymmetry: the danger isn't computing, it's computing *from a wrong model of how vLLM allocates.*

---

## Summary of the delta (what synthesis should carry from this lane)

| # | finding | tag | failure mode (corrected) |
|---|---|---|---|
| ★ | vLLM rents **1056-token blocks**; today's `mml`-sized formula **over-provisions** (waste) but (A) **silently caps concurrency** when the worker window < 32 blocks, and (B) **under-counts 2-8×** the moment KV sizing tightens per the design's own "size to NEED" direction; **prefix-caching ~0% below the block** (measured QPS 200→<100) | **NEW BREAK** | runtime: **concurrency cap + throughput collapse** (NOT OOM — slab can't be overrun) |
| 2 | Mamba SSM state silently corrupts on **scheduler token-budget exhaustion** (AI21 bug, tested gpu_util 0.2); **fully gated on whether the prefill-path fix is in our 0.21** — verify first. Budget→trigger link is **inferred**, not measured | **NEW BREAK** (cond.) | **silent correctness** (wrong tokens, no error) |
| 3 | sleep-mode broken since 0.14 (#32714, memory not freed); fallback reload **~30-60× slower** than the assumed ~1s wake | NEW BREAK + HARDENS | UX (no fast handoff) |
| 4 | per-seq 34 MiB is **contaminated upward** by activation_peak (profile_run batches by max_num_seqs); linearity unproven by the method that produced it | HARDENS | under-predict (safe / wasteful) |
| 5 | `enforce-eager` global default = **~39% decode-latency tax** (89→54 tok/s) on the latency-bound conversational loadout; must be per-loadout | NEW BREAK | latency; graphs-on → 0.43 GiB blind spot → OOM-at-bring-up if unaccounted |
| 6 | `--kv-offloading-size` collapses on WSL2 (no pinned memory → PCIe cliff) + weak for distinct-request worker load | NEW BREAK | perf (offload unusable) |
| 7 | byte-budget fixes steady-state load-order but **NOT the startup-profiling instant** → sequencing still required for bring-up | half-CONCEDE | **OVER-predict at bring-up → OOM** (the incident's class) |
| 8 | fp8 e4m3 KV ≈ 1-2 pts on a Qwen3 Thinking model — **holds**; do NOT borrow the INT4 0.00 cliff | CONCEDES | — |

**The one sentence:** measure-then-compute is sound in *spirit*, and `--kv-cache-memory-bytes` genuinely removes the runtime OOM (the slab can't be overrun) — but the failures **move, they don't vanish**: at **bring-up** the budget can still under-size vs the startup-profiling instant (the incident's real class, #7), and at **runtime** the engine's **1056-block quantization** turns the worker loadout's tidy token math into a silent concurrency cap + prefix-cache death + (the moment sizing tightens) a 2-8× shelf under-count — none of which is OOM, all of which is the worker loadout failing *slowly and silently*. Build it as a **block-aware, measured-once per-loadout table scaled by live headroom** — reasoning in whole blocks, surfacing the real concurrency a window supports, with enforce-eager per-loadout and sleep-mode treated as unavailable until proven — **not** a token-linear formula re-derived live.

---

### Sources (fetched / read 2026-06-30)
- ops/cli/gpu.py (read) — `auto_gpu_util`:48-83 (KV formula :71, per-seq :77-79), `budget_vram`:86.
- ops/services.json (read) — chat-4b-fp8 (gpu_util 0.9 / seqs 32 / 65536, `_profile: null`), chat-4b AWQ `_profile`, chat-9b-fp8 `_profile`.
- ANCHOR.md, SCOPE.md (read in full).
- .data/unify-exercise/gpu-autoprofiler-research.html (read) — block 528/1056, 7.3×, profile_run, 49.5 MiB, INT4 0.00, fp8 baseline.
- [vLLM #32714 — sleep broken since 0.14.0](https://github.com/vllm-project/vllm/issues/32714)
- [AI21 — One token to corrupt them all: a vLLM Mamba debugging tale](https://www.ai21.com/blog/vllm-debugging-mamba-bug/)
- [vLLM blog — The State of FP8 KV-Cache and Attention Quantization](https://vllm.ai/blog/2026-04-22-fp8-kvcache)
- enforce-eager 89→54 tok/s — vLLM parameter benchmark (web search, 2026-06-30; verify by use before relying on the exact %).
- Block-quantization, reload-cost, enforce-eager arithmetic: this session (Inferred — computed, not run on the live engine).
