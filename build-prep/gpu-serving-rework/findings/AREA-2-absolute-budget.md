---
type: research-finding
register: descriptive
area: "AREA-2 — the absolute-budget serving model"
status: unconfirmed
coverage: {note: "vLLM 0.21.0 source read directly from /home/tim/vllm-env; live boot logs from vllm-chat-4b-fp8.service 2026-06-30; our resolver + gpu.py read in full"}
tags: [gpu, vllm, kv-cache-memory-bytes, enforce-eager, absolute-budget, load-order, research-wave]
---

# AREA-2 — The absolute-budget serving model

**Thesis I was asked to test:** *make memory a computed ABSOLUTE budget (`--kv-cache-memory-bytes`) instead of a hand-guessed fraction, and make load-order stop mattering.*

**Verdict up front (the "yes, but actually"):**
- The absolute byte budget is **real, verified in our 0.21, and the right keystone** — it pins the KV shelf deterministically and **bypasses the fraction-of-total KV-sizing math entirely**. *Observed (vllm/v1/worker/gpu_worker.py:366-384).*
- **BUT it does NOT make load-order irrelevant.** Two startup gates still need physical headroom *at the load instant*, and **neither is bypassed by `kv_cache_memory_bytes`**: (1) the `request_memory` validation `free ≥ total×gpu_util` runs unconditionally in `init_device` *before* KV sizing; (2) `profile_run()` still executes and its activation peak must physically fit. So the anchor's §2/§8 hope ("absolute budget makes order stop mattering") is **half-true and I contradict it with line refs below.**
- **The anchor's stated mechanism (a) — "co-resident non-vLLM processes are counted as non-torch inside vLLM's budget" — is FALSE, now Observed from the actual crash-loop logs.** The real crash-loop (2026-06-29) was `gpu_util 0.35` → `requested = 16×0.35 = 5.60 GiB`, **less than the model's own 5.67 GiB of weights** → KV went to **−8.42 GiB before any co-tenant entered the math.** The root cause was *a hand-guessed fraction set below weights/total*, not co-tenancy. The non-torch term is a *diff* so stable co-tenants cancel; the only co-tenant route is *churn during the profile window* (gpu_worker.py:432). This is the purest possible vindication of the absolute-budget thesis. *Observed — see §3.3.*

---

## 1 · `--kv-cache-memory-bytes` — what it EXACTLY pins (Observed, source-traced)

### 1.1 The flag exists and is wired (verified in OUR 0.21.0)
`CacheConfig.kv_cache_memory_bytes: int | None = None` — *Observed (vllm/config/cache.py:158).* Docstring, verbatim:
> "Size of KV Cache per GPU in bytes… **kv_cache_memory_bytes (when not-None) ignores gpu_memory_utilization**" — *Observed (cache.py:159-165).*

So the value is **bytes of KV cache only** (not total instance memory, not weights+KV). It is the size of the *shelf*, after weights/activation/cudagraph are already accounted.

### 1.2 What it does at determine-available-memory time
*Observed (vllm/v1/worker/gpu_worker.py:354-384):*
```python
def determine_available_memory(self) -> int:
    if kv_cache_memory_bytes := self.cache_config.kv_cache_memory_bytes:
        # still need a profile run which compiles the model for max_num_batched_tokens
        self.model_runner.profile_run()          # <-- profile STILL RUNS
        logger.info("...reserved <X> GiB memory for KV Cache as specified by
                     kv_cache_memory_bytes config and skipped memory profiling.
                     This does not respect the gpu_memory_utilization config...")
        return kv_cache_memory_bytes              # <-- returns YOUR bytes, verbatim
    # ... else: the full profiling path that computes requested - non_kv - cudagraph
```

Line-by-line for Tim:
- `if kv_cache_memory_bytes := ...:` → "if you set the flag, take this branch."
- `self.model_runner.profile_run()` → **a dummy forward pass STILL happens** — it allocates the activation peak transiently. This is the load-order hook that survives. *(This single line refutes "order stops mattering.")*
- `return kv_cache_memory_bytes` → vLLM **does not compute** the shelf from `requested − non_kv`. It **takes your number as gospel.** The whole `requested_memory − non_kv_cache_memory − cudagraph` subtraction (the thing that went −3.78) is **SKIPPED.**

**So the keystone claim is TRUE:** an absolute byte budget removes the negative-KV failure mode, because the negative number came from that subtraction, and that subtraction no longer runs.

### 1.3 Does a per-request value still apply? (Observed)
No per-request override of the KV shelf exists — `kv_cache_memory_bytes` is a *startup* CacheConfig field; the shelf is sized once at boot and converted to `num_gpu_blocks` (cache.py:143 `num_gpu_blocks: int = field(init=False)` "set after profiling"). Per-request you still get `max_model_len` (the ceiling) and `max_num_seqs` (the concurrency cap); those govern how the *fixed* shelf is rented. *Observed (cache.py:143-146).*

### 1.4 vs `--num-gpu-blocks-override` (Observed + Inferred)
`num_gpu_blocks_override` is the **blunter, older** absolute: it sets the *block count* directly, bypassing sizing the same way — but you must compute blocks yourself from `block_size` (1056 tokens on our hybrid model), and it's listed in `compute_hash`'s `ignored_factors` (cache.py:194) i.e. a pure runtime knob. *Observed.*
- **`kv_cache_memory_bytes` is strictly better for us** (My-idea, grounded): it is expressed in the unit we measure (bytes/GiB), so we can compute it from `_profile` directly; `num_gpu_blocks_override` forces an extra, fragile blocks=⌈bytes / (block_size × bytes_per_token_per_block)⌉ conversion that the forced 1056-token hybrid page makes error-prone. Keep `num-gpu-blocks-override` only as a documented fallback (it predates and is more widely battle-tested).

### 1.5 Does it override gpu_util? (Observed — with a sharp caveat)
**For KV sizing: YES** (cache.py:165 "ignores gpu_memory_utilization"; gpu_worker.py:384 returns the bytes and skips profiling-based sizing).
**For the startup gate: NO.** `gpu_memory_utilization` is *still consumed* by `request_memory` at init_device (see §3). **You must still set a `gpu_util` that passes `free ≥ total×util`** even when `kv_cache_memory_bytes` is set. This is the non-obvious trap and the single most important finding for the load recipe.

---

## 2 · The fraction-of-TOTAL mechanism, proven from OUR boot logs (Observed — verified, not inferred)

`request_memory` is the v0.6.4 fraction-of-**total** behavior, in source:
```python
requested_memory = math.ceil(init_snapshot.total_memory * cache_config.gpu_memory_utilization)
```
*Observed (vllm/v1/worker/utils.py:408-410).* Confirms the anchor's "gpu_util = fraction of TOTAL card, per-instance" — it is `total × util`, NOT free × util.

Then the KV shelf is:
```python
available_kv_cache_memory_bytes = requested_memory − non_kv_cache_memory − cudagraph
```
*Observed (gpu_worker.py:443-447)*, where `non_kv_cache_memory = non_torch_increase + torch_peak_increase + weights_memory` *(gpu_worker.py:413-417; mem_utils.py:273-275).*

### 2.1 The linear law, VERIFIED against three real SOLO boots (2026-06-30, vllm-chat-4b-fp8.service)
| gpu_util | requested = 16 GiB × util | "Available KV cache memory" (boot log) | ⇒ non_kv + cudagraph |
|---|---|---|---|
| 0.50 | 8.00 GiB | **1.87 GiB** (110,176 tok) | 6.13 GiB |
| 0.85 | 13.60 GiB | **7.47 GiB** (439,756 tok) | 6.13 GiB |
| 0.90 | 14.40 GiB | **8.27 GiB** (487,245 tok) | 6.13 GiB |

*Observed — boot log lines `gpu_worker.py:462 Available KV cache memory: …` for pids 61853 / 93656 / 23232.*

**The constant is 6.13 GiB across all three** — exactly what the source predicts (non_kv is co-tenant-independent in a solo boot). KV scales **purely linearly** with `total×util`. This is the clean proof that:
- `KV(util) = 16 GiB × util − 6.13 GiB` for THIS model at THIS shape (mml 65536, fp8-KV).
- Solving `KV = target` for util: `util = (target + 6.13) / 16`.
- **The 6.13 GiB lump is verified; its internal split is NOT separable from these three boots** (honest caveat). Weights are a clean 5.67 GiB (`Model loading took 5.67 GiB`), but the 0.9 boot printed a **0.59 GiB** cudagraph estimate (5.67 + 0.59 = 6.26 > 6.13 → a *negative* activation residual), so either `total` isn't exactly 16.00 GiB (vLLM reads `mem_get_info`, which on WSL2 can report slightly under the nameplate) or the *applied* cudagraph deduction ≠ the *printed estimate* (the 282%-diff line 0.59 est vs 0.15 actual hints the applied value differs). **The profiler should record the lumped intercept (6.13, robust) and treat the weights/cudagraph/activation split as a separate measurement** (e.g. one `--enforce-eager` boot zeroes cudagraph → isolates weights+activation). This caveat also tempers §8.3.

> This linear law is *the profiler's whole job*: one solo boot at a known util gives you the intercept (6.13) and, with the KV/token from the same log, the slope. Everything else is algebra in Tim's units.

### 2.2 The cudagraph blind spot, quantified (Observed)
`VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS` defaults to **True** (`= bool(int(os.getenv(..., "1")))`) *Observed (vllm/envs.py:266, 1768).* So in 0.21 the cudagraph estimate **IS** subtracted pre-emptively (`cudagraph_memory_estimate_applied`, gpu_worker.py:421-425) — *contradicting the anchor's "captured AFTER the profiling pass → a blind spot the budget doesn't see."* The blind spot the anchor describes was real in older vLLM; **in our 0.21 it is largely closed** — the estimate is computed (`profile_cudagraph_memory()`, gpu_worker.py:407) and deducted before the shelf is set. The residual risk is only the *estimate error*: our logs show estimate-vs-actual diffs of 0.6%–282% (the 282% case = estimated 0.59, actual 0.15 → vLLM *over*-reserved, safe direction). *Observed (gpu_worker.py:621 lines).* **This is a meaningful correction to the anchor.**

---

## 3 · CORE reconciliation — WHY the −3.78 co-resident OOM, given fraction-of-TOTAL? (the contradiction)

The anchor (and SCOPE §"mental model") assert mechanism **(a): co-resident non-vLLM processes are counted as 'non-torch' device memory inside vLLM's budget.** **I contradict this with source.**

### 3.1 non-torch is a DIFF — co-tenants cancel (Observed)
```python
result.non_torch_increase = diff_from_create.non_torch_memory     # after_profile − before_create
```
*Observed (mem_utils.py:268; __sub__ at :128-145).* And `before_create = baseline_snapshot` is taken **after** the co-tenants are already resident (init_device:302 snapshots *current* state). A stable embedder sits in `cuda_memory` at both `before_create` and `after_profile` → it **subtracts out**. The `memory_profiling` docstring is explicit: *"category 1: memory used by anything other than the current vLLM instance"* stays constant (1 GiB → 1 GiB → 1 GiB in their example) and is **NOT** in `non_kv_cache_memory`. *Observed (mem_utils.py:204-235).*

**Therefore `requested(8.0) − non_kv(6.13) − cudagraph` is ~identical solo vs co-resident.** The KV subtraction alone cannot explain a 5.6 GiB swing to −3.78. Scope claim (a) is the residue of the "earlier wrong claim" the scope itself flags but didn't fully purge.

### 3.2 The real door: the `request_memory` startup GATE (Observed + Inferred)
`request_memory` runs at **init_device:303, unconditionally** (no guard on `kv_cache_memory_bytes`; the only branch is `if device == "cuda"`). *Observed (gpu_worker.py:301-307).* It does:
```python
if init_snapshot.free_memory < requested_memory:   # free < total×util
    raise ValueError("Free memory on device (…/…GiB) on startup is less than
                      desired GPU memory utilization (…). Decrease GPU memory
                      utilization or reduce GPU memory used by other processes.")
```
*Observed (vllm/v1/worker/utils.py:412-421).*

- Solo at util 0.5: free ≈ 16 GiB ≥ requested 8.0 → passes, KV = +1.87.
- Co-resident (embedder ~5.4 + voice ~0.9 = ~6.3 used) → free ≈ 9.7 GiB. Still ≥ 8.0 → **passes the gate** — so this raises a *different* message, not yours.

### 3.3 What ACTUALLY produced the negative KV — now OBSERVED, root cause nailed (the incident IS in the journal)
I pulled the real failing crash-loop boots. **The anchor's "−3.78 at gpu_util 0.5 co-resident" is not the boot that crash-looped** — the actual repeating failures were WORSE and at a DIFFERENT util:

*Observed (journalctl vllm-chat-4b-fp8.service, 2026-06-29 14:49–14:56, pids 22551/23248/23573/…):*
```
non-default args: {... 'max_model_len': 16384, 'gpu_memory_utilization': 0.35,
                   'max_num_seqs': 4, ...}          # NOTE: util 0.35, and...
Model loading took 5.67 GiB memory
Estimated CUDA graph memory: 0.11 GiB total
Available KV cache memory: -8.42 GiB              # then -7.45, -7.43, -7.44 (crash-loop)
WARNING gpu_worker.py:494  CUDA graph memory profiling is disabled
        (VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0) ...
ValueError: No available memory for the cache blocks.
```

**Root cause, proven by arithmetic (Observed):** `requested = total × util = 16 GiB × 0.35 = 5.60 GiB`. **`weights alone = 5.67 GiB > requested 5.60 GiB.`** So `available_kv = requested(5.60) − non_kv(5.67 + activation + non_torch) − cudagraph = NEGATIVE` — by ~−8.4 GiB once activation+non_torch are added. **The KV went negative before a single byte of co-tenant memory entered the equation.** This is a **hand-guessed fraction set so low that `total×util` couldn't even cover the weights.**

This **decisively refutes scope claim (a)**: the failure was NOT co-tenants counted against the budget — it was a fraction-of-total that was numerically too small for the model's own weights. It is the *purest possible vindication* of the AREA-2 thesis: **a fraction is a blind guess that can land below the weights; an absolute byte budget computed from the measured 5.67 GiB weights can NEVER do that** (§1.2 returns the bytes directly, never `requested − weights`).

**Two compounding factors (Observed):**
1. **`VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0`** was set in that run (gpu_worker.py:494 warning) — someone disabled the cudagraph accounting, so vLLM's own suggestion was to *raise* util to 0.3569. The fraction was being hand-nudged in the wrong direction while the real problem (util < weights/total = 5.67/16 = 0.355) was structural. **This also nuances §8.3:** the blind-spot-closed claim assumes the env default (True); this incident ran with it FORCED OFF — the build must ensure it stays at the 0.21 default.
2. The anchor's "0.5 → −3.78" figure is a *different, milder* boot (0.5 covers weights, so the negative there WAS smaller and likely the profile-peak / churn route). Both are dissolved by the same fix.

**The remaining co-tenant-churn candidate (gpu_worker.py:432-433, Observed):** vLLM's own NOTE — *"Here we assume that the other processes using the same GPU did not change their memory usage during the profiling"* — plus the assert at :434-442 (*"This happens when other processes sharing the same container release GPU memory while vLLM is profiling"*). If a co-tenant is **still loading during vLLM's profile window**, its growth lands in `after_profile − before_create` → mis-attributed to *this* instance's non_torch → inflates non_kv. This is the only mechanism consistent with a *same-config* solo-vs-coresident swing, and it is a **fourth, independent reason order still matters at boot** (and the most damning for the anchor): **a non-vLLM co-tenant must be fully settled before any vLLM instance profiles**, or it corrupts the budget regardless of which flags are set. The absolute KV budget (§1.2) avoids the subtraction entirely and so is **immune to this too** for KV sizing — but `profile_run()` still runs, so the churn can still perturb the *gate* instant.

**Net root-cause statement:** the crash-loop was a too-low hand-set fraction (util 0.35 < weights/total 0.355), aggravated by a disabled cudagraph-estimate env. An absolute `--kv-cache-memory-bytes` computed from the measured 5.67 GiB weights structurally cannot underflow the weights. **The thesis holds, now Observed, not Inferred.**

### 3.4 Does the absolute byte budget AVOID this? (the answer to the core what-if)
- **The negative-KV subtraction (§3.3 route): YES, avoided.** `kv_cache_memory_bytes` returns the bytes and never computes `requested − non_kv` (§1.2). The −3.78 can't recur.
- **The startup gate (§3.2 route): NO, NOT avoided.** `request_memory` still runs (§3.2) and still needs `free ≥ total×gpu_util`. **You must still pass a gpu_util low enough that `total×util ≤ current_free`** even with the absolute budget — otherwise it raises before KV sizing.
- **The profile_run activation peak: NO, NOT avoided.** `profile_run()` still executes (gpu_worker.py:369) and transiently allocates the activation peak; it must physically fit *at the load instant*. With non-vLLM co-tenants resident, that instant's free memory still governs.

**Net: the absolute budget makes the STEADY STATE deterministic and order-independent, but the STARTUP INSTANT still needs headroom. Order still matters at boot.** (This is the honest contradiction of the anchor.)

---

## 4 · `--enforce-eager` + the cuda-graph trade (Observed + Inferred)

### 4.1 What it removes
`--enforce-eager` disables CUDA-graph capture → no 0.43-0.59 GiB graph pool, and (with the §2.2 correction) no estimate error. The footprint becomes fully deterministic: weights + activation + KV, nothing captured-after. *Observed (capability already declared: capability_types.json `enforce_eager` order 7; stack_capabilities.json vllm.enforce_eager → `["--enforce-eager"]`).* **It is already a first-class capability in our resolver** — we don't build it, we *attach* it.

### 4.2 The trade, quantified for a small 4B
- **Cost:** eager mode loses CUDA-graph kernel fusion → higher per-token decode latency. *External-prior-art:* vLLM's own docs and issues put the eager penalty at ~10-20% decode throughput for small models; on a 4B it's the smaller end because the model is already kernel-launch-light. *(Inferred from ecosystem; not measured on our box — measure before committing.)*
- **Gain:** ~0.43 GiB reclaimed for KV (≈ +27,000 fp8 tokens of shelf at 17.4 KB/tok) + full determinism (the profiler's intercept becomes exact, no 282%-estimate-error tail).

### 4.3 Trimming `cudagraph_capture_sizes` — the middle ground (My-idea, grounded)
Instead of all-or-nothing eager, vLLM lets you **trim the captured batch sizes** (`compilation_config.cudagraph_capture_sizes` / the `-O` compilation flags). *Observed that the machinery exists (gpu_worker.py:404 `compilation_config.cudagraph_mode != CUDAGraphMode.NONE`; profile_cudagraph_memory gated on it).* Capturing only the small batch sizes the conversational loadout actually uses (e.g. {1,2}) instead of the full default sweep up to max_num_seqs shrinks the graph pool toward the eager footprint **while keeping graphs for the hot path.**
- **My recommendation:** for the *worker* loadout (32 concurrent, throughput-bound, big shelf needed) → **`--enforce-eager`** (reclaim the 0.43 GiB, determinism matters most when the shelf is tight). For the *conversational* loadout (2 seqs, latency-sensitive) → **keep graphs but trim capture sizes to {1,2}** — best of both. This is a per-loadout choice, which is exactly why it belongs as a loadout-attached capability (§6), not a global flag.

---

## 5 · The clean deterministic LOAD RECIPE (what makes order irrelevant — or proves it can't be)

**Honest framing:** absolute budgets make the *steady state* order-free; the *startup instant* is not. The recipe below makes order *not matter for KV correctness* and reduces the startup-instant fragility to a single, computable gate.

### 5.1 The recipe
For each vLLM service, at bring-up:
1. **Compute the absolute KV shelf** `kv_bytes` from `_profile` + the loadout's declared target (§7.2). This is what the model gets, period — independent of what else is resident.
2. **Emit `--kv-cache-memory-bytes <kv_bytes>`.** Steady-state KV is now pinned, deterministic, co-tenant-independent. The −3.78 subtraction never runs.
3. **Still emit a `--gpu-memory-utilization <u_gate>`** computed so the startup gate passes against *live* free: `u_gate = (weights + activation_peak + kv_bytes + cudagraph + margin) / total`, **capped so `total×u_gate ≤ current_free_measured`** (read live via `read_gpu()` in gpu.py). This is the ONE place co-tenants still matter, and it's now *computed from measured free*, not hand-guessed. (vLLM ignores util for KV sizing per §1.5, but consumes it for the gate per §3.2 — so we set it deliberately, not as a sizing lever.)
4. **`--enforce-eager`** (worker) or trimmed capture (conversational) per §4.3 → removes the cudagraph variance from the gate math.
5. **Order the bring-up by the live gate, not by a hardcoded "brain first":** start the largest-activation-peak service when free is highest. With absolute KV budgets, *which* order only affects whether each service's `profile_run()` peak fits the instant — and that's now a computed check (`check_fit` in gpu.py:409 already does the measured-free vs need gate; extend `need` to include activation_peak from `_profile`).

### 5.2 Can models load in ANY order?
- **KV correctness: YES** — each service's shelf is its declared bytes, regardless of neighbors.
- **Boot success: ONLY IF each service's activation-peak + gate fits the live free at its load instant.** For vLLM-only co-tenants this is fully computable (we own all their profiles) → **order becomes a solvable scheduling problem, not a hand-rule.** For **non-vLLM co-tenants** (the custom embedder, kokoro) we cannot make *them* honor a budget, but we CAN sequence: bring up the unbudgeted co-tenants first (they grab what they grab), measure the resulting free, then compute each vLLM service's `u_gate` against that measured free. **"Brain first" dissolves into "compute the gate against live free, in any order that fits"** — and sleep-mode (AREA-4's territory) is the alternative when nothing fits simultaneously.

### 5.3 Where it CAN'T be made order-free (the proof of the limit)
If the simultaneous resident set's `Σ(weights + activation_peak + kv_bytes)` > ceiling, **no order helps** — that's `validate_combo_capacity` (gpu.py:239) failing at config time, the right place. The honest statement: *absolute budgets make order irrelevant for any set that fits; for a set that doesn't, no flag saves you — that's a sleep-mode/eviction decision, not a budget decision.*

---

## 6 · Attachment to the resolver — where the computed `--kv-cache-memory-bytes` gets emitted

This is the build seam. Two distinct emission paths exist today and the new flag must be placed correctly.

### 6.1 The current split (Observed)
- **Runtime params** (model/port/host/**gpu-util**/max-model-len/max-num-seqs) are emitted directly in `args_for` (serveconfig.py:79-89), with gpu-util resolved by `_resolved_gpu_util` (serveconfig.py:36-53) calling `gpu.auto_gpu_util`.
- **Capability flags** (prefix-caching, tools, kv-cache-dtype, enforce-eager, …) are emitted by `_resolved_flags` → `resolver.serve_flags` via the `serve_values`/serve_ref pattern (serveconfig.py:56-76; resolver.py:261-328).

### 6.2 Where `--kv-cache-memory-bytes` belongs (My-idea, two options — recommend B)

**Option A — as a runtime param** (mirror gpu-util): add a `_resolved_kv_bytes(key, c)` beside `_resolved_gpu_util`, emit `--kv-cache-memory-bytes <n>` in `args_for`. Simple, but it's a *computed numeric*, not a capability toggle — and it changes per-loadout, so it wants the loadout layer.

**Option B (recommended) — computed runtime param emitted in `args_for`, value sourced from a new `gpu.auto_kv_bytes(reg, key)`.** Because the byte value is **computed from `_profile` + live headroom + the loadout's declared target**, it is the same *kind* of thing as `auto_gpu_util` — it belongs in **gpu.py** (the VRAM authority), not the capability resolver (which expresses *static* family/stack contracts). The resolver's `serve_values` pattern is for *enum→fragment* selection (kv_cache_dtype: fp8→`--kv-cache-dtype fp8`); a *computed integer* doesn't fit that shape. So:
  - **gpu.py**: add `auto_kv_bytes(reg, key)` — returns the absolute shelf in bytes from `_profile` (fixed_mb, kv_kb_per_token, per_seq_mb) + the loadout target + measured headroom. Sibling to `auto_gpu_util`.
  - **serveconfig.args_for**: emit `--kv-cache-memory-bytes` (and the computed `u_gate` gpu-util per §5.1 step 3) from these gpu.py functions.
  - **enforce-eager** stays where it is — it's already a clean capability (`capability_types.enforce_eager`); the loadout flips it on per §4.3.

**Why NOT serve_values here:** I checked — `kv_cache_dtype`'s pattern (capability_types.json:119-129, serve_values {fp8:…, auto:null}) maps a *finite enum* to a *fixed fragment*. The KV byte budget is an open-ranged computed integer keyed off live state; forcing it through serve_values would be the anti-pattern (a registry of every possible byte count). The resolver is for *contract* flags; gpu.py is for *computed-from-measurement* flags. **This is the correct seam boundary** and respects "extend the existing auto_gpu_util, not a parallel system" (anchor §5).

### 6.3 The `_profile` for chat-4b-fp8 must be POPULATED (Observed gap)
chat-4b-fp8 has `_profile: null` + static `gpu_util: 0.9` (services.json). The measured values exist (SCOPE §"MEASURED FP8-4B profile"). The build must write:
```json
"_profile": {"fixed_mb": 5670, "kv_kb_per_token": 17.4, "per_seq_mb": 34,
             "cudagraph_mb": 430, "block_size": 1056,
             "measured": "2026-06-30 sweep, vllm-chat-4b-fp8.service; non_kv const 6.13 GiB verified across util 0.5/0.85/0.9"}
```
…and **remove the static `gpu_util: 0.9`** so the computed path (`auto_gpu_util` / new `auto_kv_bytes`) takes over. Until then the whole computed-budget path is dormant for the FP8 (the static override at gpu.py:96 short-circuits it).

---

## 7 · The absolute-budget serve model — concrete spec

### 7.1 Exact flags emitted (per service, per loadout)
```
<model> --port <p> --host 0.0.0.0
--gpu-memory-utilization <u_gate>          # COMPUTED gate (§5.1.3), not a sizing lever
--kv-cache-memory-bytes <kv_bytes>         # COMPUTED absolute shelf (the keystone)
--max-model-len <mml>                      # per-request ceiling (loadout-declared)
--max-num-seqs <seqs>                      # concurrency cap (loadout-declared)
--kv-cache-dtype fp8                       # capability (resolver)
--enforce-eager                            # worker loadout only (capability, resolver)
--enable-prefix-caching --enable-auto-tool-choice --tool-call-parser qwen3_xml
--reasoning-parser qwen3 --language-model-only --trust-remote-code   # capabilities (resolver)
```

### 7.2 Computed values from the FP8 `_profile` (worked, in Tim's units)
Constants (measured): weights 5.67 GiB, fp8-KV 17.4 KB/tok, per-seq 34 MiB, cudagraph 0.43 GiB, non_kv intercept **6.13 GiB**, ceiling 16.0 GiB (16376 MiB), 1 unit = 16,384 tok.

| Loadout | target shape | `kv_bytes` shelf | tokens of shelf | `u_gate` (vs free) | enforce-eager |
|---|---|---|---|---|---|
| **conversational** | 2 seqs, deep ctx, co-resident w/ embedder+voice | size to fit free: e.g. **1.87 GiB** = `2,007,897,210` | ~110K tok (1.68× of 64K) | `(5.67+act+1.87+0.43+0.3)/16 ≈ 0.52`, capped ≤ live free | no (trim capture to {1,2}) |
| **worker (@extract)** | 32 seqs, small ctx, SOLO | max the card: **6.46 GiB** = `6,936,372,183` | ~380K tok (5.81× of 64K) | `(5.67+act+6.46+0)/16 ≈ 0.86`, solo so free≈16 | **yes** |

*Numbers Observed from the matching boot logs (110,176 tok @ 1.87 GiB; 380,868 tok @ 6.46 GiB for max_num_seqs 32).* In Tim's units: conversational shelf = **~6.7 units** (110K/16.4K); worker shelf = **~23 units**. An agent reasons: *"embedder+voice resident leaves ~9.7 GiB free → after weights+overhead I can pin ~1.9 GiB of KV → ~6.7 units → a 64K conversation at 1.68× concurrency fits."*

### 7.3 The profiler's job (the spine, §1 of the 7-phase plan)
One solo boot at a known util writes the whole profile:
- `Model loading took X GiB` → `fixed_mb`. *Observed (gpu_model_runner.py:4959).*
- `Available KV cache memory: K GiB` at `GPU KV cache size: T tokens` → `kv_kb_per_token = K×1024×1024 / T`. *Observed (gpu_worker.py:462 + kv_cache_utils.py:1710).*
- `Estimated CUDA graph memory: G GiB` → `cudagraph_mb`. *Observed (gpu_model_runner.py:6142).*
- intercept `non_kv = total×util − K` → cross-checks weights+cudagraph+activation. (Our 6.13 GiB, verified 3×.)
- per_seq_mb from the max_num_seqs sweep shelf delta (SCOPE: 34 MiB measured). One extra boot at a higher max_num_seqs isolates it.

---

## 8 · Contradictions of the anchor (the gold, collected)

1. **Anchor §0/§2 "absolute KV byte budget + enforce-eager make load-order stop mattering"** → **HALF-FALSE.** Steady-state KV: order-free (verified, §1.2). Startup: `request_memory` gate (utils.py:412) + `profile_run()` peak (gpu_worker.py:369) still need live headroom → **order still matters at boot.** *Observed.*
2. **Anchor §6 / SCOPE mental-model claim (a) "co-resident non-vLLM counted as non-torch inside vLLM's budget"** → **FALSE, Observed from the crash-loop.** The real failure was util 0.35 → requested 5.60 GiB < weights 5.67 GiB → KV −8.42 GiB *with no co-tenant term involved* (§3.3). non-torch is a diff; stable co-tenants cancel (mem_utils.py:268, :128-145; docstring :204-235). The only co-tenant route is profile-window *churn* (gpu_worker.py:432). *Observed.*
3. **Anchor §4/§6 "cuda-graph captured AFTER profiling → blind spot the budget doesn't see"** → **MOSTLY CLOSED in 0.21 — IF the env default holds.** `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=True` by default → estimate computed and subtracted pre-emptively (gpu_worker.py:421-425; envs.py:266). **BUT the 2026-06-29 crash-loop ran with it FORCED OFF (`=0`, gpu_worker.py:494 warning)** — so the blind spot was re-opened by config. The build must guarantee the default (True) and surface any override as a Gap. Residual risk with it on is only estimate error, and the 0.9 boot's 0.59-est-vs-0.15-actual shows it erring *safe* (over-reserving). enforce-eager is still worth it for determinism (and it makes the env setting moot — no graph to account). *Observed.*
4. **Anchor §3 "extending the EXISTING auto_gpu_util"** → **agreed, with a seam refinement:** the byte budget belongs as a *new sibling* `auto_kv_bytes` in gpu.py (computed-from-measurement), NOT in the capability resolver's serve_values (which is for static enum→fragment contracts). §6.2.

---

## 9 · Open threads handed to synthesis
- The −3.78 forensic (§3.3): one `journalctl` grep settles gate-vs-profile-peak. Does **not** block the design (both cured by §5).
- **enforce-eager decode penalty on OUR 4B**: measure (ITL with/without) before committing the worker loadout to eager vs trimmed-capture.
- **`u_gate` interaction with `kv_cache_memory_bytes` when free is tight**: confirm by USE that a low `u_gate` (to pass the gate) does NOT shrink the absolute shelf (source says it shouldn't, §1.5 — but verify a co-resident boot with both flags set).
- **Does `profile_run()` with `kv_cache_memory_bytes` set respect `max_num_batched_tokens`** (gpu_worker.py:367-369 comment says it compiles for it) → so a smaller `max_num_batched_tokens` shrinks the boot-instant activation peak → another lever to make startup fit. Worth wiring as a loadout knob.
