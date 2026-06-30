---
type: research-companion
register: descriptive
area: "AREA-1 — the measurement / profiler substrate"
aliases: ["Profiler Substrate", "Measure-then-compute profiler", "Auto-profiler design"]
tags: [gpu, vllm, profiler, measurement, _profile, loadout, build-prep, research-wave]
status: unconfirmed
coverage: {captured_from: "vLLM 0.21.0 installed source + company ops/ source + live registry, read 2026-06-30", note: "no live boot performed — chat-4b-fp8 is solo-serving the bulk audit (SCOPE §State); live parse marked as a build-phase verification"}
vllm_version: "0.21.0 (verified ../vllm-0.21.0.dist-info/METADATA)"
---

# AREA-1 — The Measurement / Profiler Substrate

> How to MEASURE a model's true resource costs cleanly, turn it into a `_profile`, and generalise that across vLLM models, the non-vLLM custom embedder, and kokoro voice — leaning on vLLM's own measurement routine, not custom bandaids.

**Evidence labels:** **Observed** (file:line / log) · **Inferred** (computed/pattern, not executed) · **External** (ecosystem/docs) · **My-idea** (proposal to challenge).
**Verification posture (per CLAUDE.md):** I read the installed vLLM 0.21.0 source and the company ops source. I did **not** boot a model this session (the FP8 brain is mid-audit). Every "vLLM prints X" is Observed-in-source; "X parses cleanly at boot" is Inferred-until-a-real-boot and flagged as a build-phase verify.

---

## 0 · TL;DR — the three findings that change the anchor

1. **One DEBUG boot gives almost the whole profile — no knob-sweep needed for the 4-term split or per-token-KV.** vLLM's own `memory_profiling` routine decomposes weights / peak-activation / non-torch / KV and prints all four — **but the per-term split and the suggested absolute byte budget are at `logger.debug`, not INFO** (gpu_worker.py:461, 685). The anchor's "vLLM PRINTS the 4-term, just parse it" is **naive without `VLLM_LOGGING_LEVEL=DEBUG`**. Weights, cudagraph-total, "Available KV cache memory", "GPU KV cache size: N tokens", and "Maximum concurrency: Nx" are INFO. *Observed.*

2. **The cuda-graph "blind spot" is NOT a blind spot in 0.21 — it's accounted by default.** `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS` defaults to **True** (envs.py:266) and the estimate is **subtracted** from the KV budget (gpu_worker.py:446). The `0.85→0.877` warning the session saw is the *accounted* path telling you cudagraph correctly shrank KV — not a budget that's blind to it. `--enforce-eager` removes cudagraph entirely, so it's a **determinism / throughput tradeoff**, not a correctness fix. The anchor (§6, §4) overstates this. *Observed.*

3. **The keystone, made precise: `--kv-cache-memory-bytes` does NOT make load-order irrelevant — and the survivor is bigger than "weights".** `request_memory()` returns `ceil(total_memory × gpu_util)` — co-tenant-**independent** — but **raises** if live `free_memory < requested` (utils.py:408-421), and it runs at worker init (gpu_worker.py:302-303) **before** the kv-cache-bytes early-return (gpu_worker.py:366). It reads `gpu_util` **unconditionally** — setting `kv_cache_memory_bytes` suppresses only KV *sizing* (the "does not respect gpu_util" at line 376), **not** this free-check. So the surviving boot guard is `free ≥ total × gpu_util` — the **requested fraction**, not the weights. With the FP8 brain's static `gpu_util: 0.9` that demands ~14.4 GiB free at boot regardless of the 5.67 GiB weights — load-order sensitivity *worse* than the footprint needs. **The lever (hands AREA-2 a concrete fix):** when the resolver emits `--kv-cache-memory-bytes` it must **co-lower `gpu_util` to the measured footprint fraction** `(fixed + kv_bytes + activation + non_torch + cudagraph) / total`; then the free-check only demands the real footprint be free — the irreducible minimum. Refined conclusion: byte-budget **+ matched gpu_util** *minimizes* load-order sensitivity down to the irreducible weights-resident step; sequencing/sleep-mode covers only that residue. The byte budget alone is necessary but not sufficient. This is the traced answer to Open-what-ifs #1 and #8. *Observed (the call sites + bodies, utils.py:408-421).*

Plus a fourth, quieter one: **the `vram_overhead_mb` hand-bump (512 → 1024) is itself a hand-guess Tim wants dead** (visible in the chat-9b-fp8 profile note). A profiler that measures `activation_mb` + `cudagraph_mb` + `non_torch_mb` per model **dissolves that fudge class** — the overhead margin stops being a global literal and becomes a measured per-model term. This is the "design for the class" contribution of this area.

---

## 1 · What vLLM 0.21 actually measures, and where it prints it

vLLM already runs the exact measurement we'd otherwise build. The flow, traced:

**At worker init** (`v1/worker/gpu_worker.py: init_device`, lines 295-307) — unconditional CUDA path (the only `else` raises for non-CUDA, line 308):
```
init_snapshot = MemorySnapshot(device)              # 302 — measure free/total/torch NOW
requested_memory = request_memory(init_snapshot, cache_config)   # 303
```
`request_memory` (`v1/worker/utils.py:403-423`) — **Observed**:
```
requested_memory = ceil(init_snapshot.total_memory × gpu_memory_utilization)   # 408-410
if init_snapshot.free_memory < requested_memory: raise ValueError(...)          # 412-421
return requested_memory
```
→ The requested slice is a fraction of the **total** card (co-tenant-independent), but the **free-fit guard** is co-tenant-dependent and fires at every boot. *This is the load-order survivor.*

**At `determine_available_memory`** (gpu_worker.py:354-506):
- If `kv_cache_memory_bytes` is set → **still runs `profile_run()`** (to compile for max_num_batched_tokens) but **skips the profiling-based KV sizing** and returns the pinned bytes verbatim (366-384). *Observed.* This is the path that pins steady-state KV regardless of co-tenants.
- Else → wraps `profile_run()` in `memory_profiling(...)` (388-392), reads `torch.accelerator.memory_stats(device)["allocated_bytes.all.peak"]` (394-396), optionally profiles cudagraph (402-407), then:
```
non_kv_cache_memory = non_torch_increase + torch_peak_increase + weights_memory   # 413-417
available_kv = requested_memory − non_kv_cache_memory − cudagraph_estimate         # 443-447
```
*Observed.* The 4 terms ARE the spine: `weights + activation_peak + non_torch + KV-residual`.

**`MemorySnapshot.measure()`** (`utils/mem_utils.py:96-126`) is the clean measurement API — and it is EXACTLY what our profiler should reuse, because it works on this WSL box where nvidia-smi can't (see §2):
```
torch_peak   = memory_stats(device)["allocated_bytes.all.peak"]   # 104-106
free, total  = current_platform.mem_get_info(device)              # 108
cuda_memory  = total − free                                       # 118
torch_memory = memory_reserved(device)                            # 123
non_torch    = cuda_memory − torch_memory                         # 125  ← co-tenant footprint lives here
```
*Observed.* `non_torch = cuda − torch` is the one number that sees processes vLLM doesn't control — the embedder + voice. That is the term to watch for the co-resident penalty.

### What prints at which log level (the DEBUG caveat — Observed, file:line)
| Line / GiB term | Source | Level |
|---|---|---|
| `Model loading took N GiB memory and Ts` (weights) | gpu_model_runner.py:4959-4961 | **INFO** |
| `Estimated CUDA graph memory: N GiB total` | gpu_model_runner.py:6142-6145 | **INFO** |
| `CUDA graph pool memory: N (actual), N (estimated)` | gpu_worker.py:621-628 | **INFO** |
| `Available KV cache memory: N GiB` | gpu_worker.py:462-465 | **INFO** |
| `GPU KV cache size: N tokens` | kv_cache_utils.py:1710 | **INFO** |
| `Maximum concurrency for N tokens per request: N.NNx` | kv_cache_utils.py:1711-1712 | **INFO** |
| The 4-term split (`torch_peak_increase / non_torch_increase / weights`) via `MemoryProfilingResult.__repr__` | gpu_worker.py:461 `logger.debug(profile_result)` | **DEBUG** |
| `Initial free / Requested (util)` + `Free after profiling` | gpu_worker.py:450-460 | **DEBUG** |
| **The suggested `--kv-cache-memory=<bytes>`** (both "to requested limit" and "to gpu limit"), with the per-term breakdown inline | gpu_worker.py:663-685 | **DEBUG** |

**Implication for the profiler:** to read the full decomposition AND vLLM's own recommended absolute byte budget from one boot, run the profiling boot with `VLLM_LOGGING_LEVEL=DEBUG`. The INFO-only path still yields weights + cudagraph-total + KV-tokens + concurrency — enough to derive `kv_kb_per_token` (the chat-9b-fp8 profile already did exactly this from INFO lines) but **not** the activation/non-torch split nor the suggested byte budget.

### The keystone vLLM gives us for free (gold — frame loudly)
Lines 663-685 print **vLLM's own recommended `--kv-cache-memory=<bytes>`** in two flavours: fit-into-requested and fully-utilize-gpu. **The computed-budget resolver may not need to *compute* the KV budget at all — it can read vLLM's suggestion from a profiling boot.** (At DEBUG.) The "redundancy_buffer_memory = 150 MiB" safety margin (644) is baked into vLLM's own suggestion — note that when comparing to our `vram_overhead_mb`.

---

## 2 · Clean measurement APIs — torch allocator vs nvidia-smi (the WSL truth, verified)

**Verified empirically this session:** `nvidia-smi --query-compute-apps=pid,used_memory` on this WSL box returns `[N/A]` for `used_memory`. *Observed (ran it).* So **per-process VRAM is unreadable from outside the process** on this machine — `gpu.py`'s `_vram_source` doc and `format_state` are right to never present a per-process figure as measured. nvidia-smi total `used/free` (read_gpu, gpu.py:142-152) is fine for the **whole card**; it's the per-process attribution that's `N/A`.

**Consequence:** the profiler must measure from **inside** the model's own process via the torch allocator, exactly as vLLM does:
- `torch.cuda.reset_peak_memory_stats()` before a forward → `torch.cuda.memory_stats()["allocated_bytes.all.peak"]` after = peak activation (the `torch_peak` vLLM uses, mem_utils.py:104). *External (torch API) + Observed (vLLM uses it).*
- `torch.cuda.mem_get_info()` → `(free, total)`; `total − free = cuda_memory`; `memory_reserved()` = torch's slice; `cuda − reserved = non_torch` = the co-tenant + CUDA-context footprint. *Observed (mem_utils.py:108-125).*
- Why `allocated.peak` not nvidia-smi: nvidia-smi (and `memory_reserved`) report the **caching allocator's reserved high-water** incl. freed-but-cached blocks — over-reports. `allocated_bytes.all.peak` is true peak *used*. *External (prior research artefact §02 "the measurement trap") + consistent with mem_utils comment 99-106.*

This is also why the embedder server already calls `torch.cuda.empty_cache()` after each forward (serve_pplx_embed.py:204-205) — to return the activation spike's reserved blocks so the high-water drops back for chat-4b co-residence. *Observed.*

### Reconciling per-seq state: 34 (measured) vs 49.5 (computed) — present BOTH, don't pick from recall
Two independent derivations of the hybrid Mamba per-seq fixed reservation:
- **Measured shelf-delta (34 MiB/slot):** vary `max_num_seqs` 2→32 solo at gpu_util 0.85, read the "GPU KV cache size: N tokens" shelf shrink (439,756 → 380,868 tok ≈ 1.0 GiB over 30 added slots → ~34 MiB/slot). *Inferred from SCOPE's session numbers — the method is sound; the exact MiB is approximate.*
- **Computed (≈49.5 MiB/seq):** `block_size × per_token_KV_per_layer × n_linear_layers`. The prior research artefact closed this exactly: forced block 528 (bf16) × 4 KiB/tok/layer × 24 linear layers. **Note the block-size depends on KV dtype:** fp8 halves per-token-KV-per-layer, so the forced block *doubles* (528 bf16 → 1056 fp8, as SCOPE measured) to keep the attention page ≥ the mamba page — and the product `block × per_tok_KV_per_layer × 24` lands at ~49.5 MiB **either way** (the dtype change cancels). So the 528 here and the 1056 in SCOPE/the schema are the *same closure*, not a contradiction. *External (prior artefact §00/§01) + Inferred (the dtype cancellation).* **Caveat I verified:** the log string "Setting attention block size to N tokens" the artefact quotes (issue #40696) **was NOT found in our 0.21 source** — so the "read block size off the log" path is unconfirmed in our build. The robust route is to read `block_size` programmatically from `kv_cache_spec.block_size` / `page_size_bytes` (kv_cache_utils — `get_max_concurrency_for_kv_cache_config` uses `page_size_bytes`, line 887). *Observed (the field exists; the log line does not).*

**Why they disagree (Inferred):** the measured 34 is the *marginal* shelf cost per added slot at one operating point; the computed 49.5 is the *architectural* per-seq page. They needn't match — block-table overhead, the shelf rounding to whole blocks, and the specific max_num_seqs range all move the marginal number. **The disagreement IS a deliverable, not a number to resolve away.** → profiler design below captures both and flags divergence.

---

## 3 · The existing `_profile` + `auto_gpu_util` — what's there, what's missing

`ops/cli/gpu.py: auto_gpu_util(reg, key)` (lines 48-83) — **Observed**. Computes:
```
kv_mb   = kv_kb_per_token × max_model_len / 1024
need_mb = fixed_mb + kv_mb + per_seq_mb × max_num_seqs + vram_overhead_mb     # 79
gpu_util = min(1.0, need_mb / ceiling_mb)                                      # 83
```
Reads `_profile = {fixed_mb, kv_kb_per_token, per_seq_mb?}` + config `max_model_len`, `max_num_seqs`. Returns `None` if `fixed_mb`/`kv_kb_per_token`/`max_model_len` missing (69-70) → then `budget_vram` falls to static gpu_util / learned telemetry / estimate (gpu.py:86-101), and `serveconfig._resolved_gpu_util` FAILS LOUD if there's neither a profile nor a static (serveconfig.py:49-53). *Observed.*

**Live registry state (Observed, `services.json` 2026-06-30):**
| service | `_profile` | gpu_util | mml | max_num_seqs |
|---|---|---|---|---|
| chat-4b (AWQ) | `{fixed_mb:5838, kv_kb_per_token:31.7}` — no per_seq_mb | — | 16384 | 4 |
| **chat-4b-fp8** | **`null`** ← the gap | **0.9** (static, hand-set) | 65536 | 32 |
| chat-9b-fp8 | `{fixed_mb:12155, kv_kb_per_token:39.52}` — no per_seq_mb | — | 16384 | 2 |
| embed-bge / embed-jina-v5 / embed-qwen3 | null | 0.3 / 0.3 / 0.92 | — | — |
| **tts-kokoro** | null | null (vram_mb:900 est) | — | — |

The FP8 brain — the model the whole rework is about — is still `_profile: null` + static `gpu_util: 0.9`. That's the "50% has gotta go" gap, live.

**Schema gap — what a COMPLETE `_profile` needs** (My-idea, extending the anchor's §4):
```jsonc
"_profile": {
  "fixed_mb":        5670,    // weights (Observed term: "Model loading took N GiB")  [USED by auto_gpu_util]
  "kv_kb_per_token": 17.4,    // per-token KV at the model's kv_cache_dtype          [USED]
  "per_seq_mb":      34,      // measured marginal Mamba/state per slot               [USED ×max_num_seqs]
  "per_seq_mb_computed": 49.5,// architectural cross-check (block×kv/layer×n_linear)   [NEW — flag if ≫ measured]
  "activation_mb":   null,    // torch_peak_increase (DEBUG term)                      [NEW — dissolves vram_overhead fudge]
  "non_torch_mb":    null,    // non_torch_increase (CUDA ctx + framework)             [NEW]
  "cudagraph_mb":    430,     // "Estimated CUDA graph memory" (INFO)                  [NEW — 0 under enforce-eager]
  "block_size":      1056,    // forced page (programmatic, not log)                   [NEW — explains prefix-cache≈0 below it]
  "kv_cache_dtype":  "fp8",   // so per-token KV is interpreted correctly             [NEW]
  "suggested_kv_bytes": null, // vLLM's own --kv-cache-memory= recommendation (DEBUG)  [NEW — the keystone shortcut]
  "measured":        "<provenance string: when, how, which log lines>"
}
```
`auto_gpu_util` today reads only `fixed_mb`, `kv_kb_per_token`, `per_seq_mb`. The NEW fields let the **computed-budget resolver** (AREA-2's job) replace the global `vram_overhead_mb` literal with this model's measured `activation_mb + non_torch_mb + cudagraph_mb`, and emit `--kv-cache-memory-bytes` directly from `suggested_kv_bytes` or from `(fixed+activation+non_torch+cudagraph) → KV residual`. *My-idea — to be validated against AREA-2.*

---

## 4 · The profiler design — what it loads, parses, sweeps, writes

### Two read strategies — offer both (the log-parse is brittle; the attribute-read generalises)
**(a) Log-parse path (quick):** boot the model under the normal launcher with `VLLM_LOGGING_LEVEL=DEBUG`, scrape:
- INFO: `Model loading took N GiB` → `fixed_mb`; `Estimated CUDA graph memory: N GiB` → `cudagraph_mb`; `GPU KV cache size: N tokens` + the boot's `Available KV cache memory: N GiB` → `kv_kb_per_token = KV_GiB×1024×1024 / N_tokens` (exactly how chat-9b-fp8 was profiled — Observed in its `measured` note); `Maximum concurrency` as a sanity cross-check.
- DEBUG: the 4-term `__repr__` (activation/non-torch split) + the suggested `--kv-cache-memory=<bytes>` (663-685).
- **Risk (My-idea flag):** log strings drift across vLLM versions — Tim hates bandaids over moving targets. The block-size log line already vanished between the artefact's reference build and our 0.21. So log-parse is the *fast* path, not the *durable* one.

**(b) Attribute-read path (robust — My-idea, recommended for the generalised version):** a small harness instantiates `vllm.LLM(...)` (or `EngineArgs` → engine) **in a subprocess**, and after init reads the worker's own attributes instead of regexing logs:
- `model_runner.model_memory_usage` → weights (gpu_model_runner.py:4947) — *Observed it's set there.*
- `worker.peak_activation_memory` (gpu_worker.py:428), `worker.non_torch_memory` (427), `worker.cudagraph_memory_estimate` (429), `worker.available_kv_cache_memory_bytes` (443), `worker.requested_memory` (303).
These are plain attributes set during `determine_available_memory` — reading them needs no DEBUG logging and no string match. The subprocess is required so the model's VRAM is fully released on exit (matters on a 16 GB card). *My-idea — needs a build-phase spike to confirm the attributes survive on the worker object reachable from the `LLM` handle; vLLM's process topology (EngineCore in a child proc) may require reading them via a collective/RPC rather than direct attribute access. FLAG.*

### The sweep — minimal, and only for the term that needs it
- **4-term split + per-token-KV:** ONE boot. No sweep. (Finding #1.)
- **`per_seq_mb` (measured):** a **2-point sweep** — boot at `max_num_seqs=2` and `=32` (solo, same gpu_util), read each boot's "GPU KV cache size: N tokens", take `(tokens_low − tokens_high) × kv_kb_per_token / (32−2)` → marginal MiB/slot. Cross-check against `per_seq_mb_computed`. *Inferred method (sound; matches SCOPE's session measurement).*
- **block_size:** programmatic from the KV-cache spec, no sweep.

### Auto-run on model-add
*My-idea:* hook the profiler into the model-registration path so a model added without a `_profile` is profiled once (gated, because it occupies the whole card briefly). Candidate trigger: `company config` add-model, or a `company profile <key>` command that the add-flow invokes. Must respect SCOPE's "measure manually first, THEN automate" — so v1 is an explicit `company profile <key>` operator command; auto-on-add is v2 once the manual command is trusted. *Aligns with SCOPE §The 7-phase plan #1.* It must also refuse to profile while a conflicting model is resident (the card can't hold both) — i.e. it's a single-tenant operation, fail-loud if the card isn't clear or evictable. *My-idea.*

### Where it writes
Into `services.json`'s `config._profile` for that key (the existing slot `auto_gpu_util` reads) + a provenance line into `ops/cli/telemetry.jsonl`. The profile is the durable artefact; telemetry stays the append-only event log.

---

## 5 · Generalising to non-vLLM services (embedder + kokoro)

Neither emits a vLLM boot log. The **only** route is the in-process torch-allocator probe — the same `MemorySnapshot.measure()` primitives, run inside the service's own process around its load + a representative forward.

**The custom embedder** (`ops/serve_pplx_embed.py`) — *Observed*:
- Custom arch `PPLXQwen3ContextualModel`, transformers `from_pretrained`, NOT vLLM (lines 1-13). No KV cache (it's an encoder) — so its profile has **no `kv_kb_per_token`/`per_seq_mb`**; it's essentially `{fixed_mb (weights), activation_mb (the forward peak)}`.
- It already has the load timing + an env-controlled activation cap: weights bf16 8.04 GB → int8 5.19 GB (lines 41-57); the **activation peak** is the dangerous term — an uncapped long input ballooned to 15.5 GB (lines 140-149), fixed by capping `model_max_length` + `batch_size`. So the embedder's `activation_mb` is **input-dependent** and must be profiled at the *capped* worst case (max_tokens × batch), not idle.
- **Precedent to extend:** `ops/measure_8bit_vs_bf16.py` (referenced serve_pplx_embed.py:50, 119) already loads this model and measures — the profiler's non-vLLM probe should generalise that script: wrap load in `reset_peak_memory_stats()` → read `allocated.peak` after a worst-case forward → `fixed_mb` (post-load, pre-forward) and `activation_mb` (peak − post-load). *My-idea, grounded in the existing script.*

**kokoro** (`tts-kokoro`) — *Observed (services.json)*: `model: ""` (id unconfirmed/uncatalogued), `vram_mb: 900` (estimate only), custom user-unit on port 4123, not vLLM and not even a `from_pretrained` we can see. The generic in-process probe is the **only** route, and it first needs the service to expose a profiling hook (or the profiler to attach around its startup). At ~0.9 GB it's small — but SCOPE's mandate is "applies to ALL services, not just the brain," so it gets a real measured `fixed_mb + activation_mb` too. **FLAG:** kokoro's model id must first be located/catalogued (its `_note` already flags this) before it can be profiled cleanly. The ecosystem prior (External: "speech belongs on CPU, reclaims 2-6 GB") suggests the bigger win for voice is moving it off the GPU entirely — profiling confirms whether 0.9 GB is worth reclaiming.

**Generalisation principle (My-idea):** a `_profile` has a *kind* — `vllm` (4-term + KV terms, boot-log/attribute readable) vs `inproc` (weights + activation only, torch-allocator probe). `auto_gpu_util` already degrades gracefully (a profile without `per_seq_mb` → term 0, byte-identical; gpu.py:77). An `inproc` profile with no KV terms would need `budget_vram` to treat `fixed_mb + activation_mb` as the whole footprint (no gpu_util fraction — these aren't vLLM and honour no fraction). That's an AREA-2 resolver concern; the **measurement** side just produces the right terms per kind.

---

## 6 · Existing telemetry — what it gives, where it's dirty

`ops/cli/telemetry.py` + `telemetry.jsonl` — *Observed*. `record(service, load_seconds, resident_mb, estimate_mb)` is called once from `ops/cli/app.py:80` after a `--wait` start, using `resident = after.read_gpu()` delta. `learned_vram(service)` returns the most-recent non-zero `resident_mb` (telemetry.py:36-40), used as budget priority #3 (gpu.py:101).

**Why telemetry is NOT a substitute for the profiler (the dirty-data finding):**
- `resident_mb` is a **whole-card load-delta** (total GPU jump across the load), not clean weights. It includes the profiling pass, the KV reservation, cudagraph, AND any co-tenant churn during the window. E.g. chat-4b-fp8 recorded `resident_mb: 9942` (telemetry.jsonl:31) while its true weights are ~5.67 GiB — the 9942 is weights + the gpu_util-0.9 KV reservation + everything. *Observed.*
- Many records are `resident_mb: 0` (lines 13, 17, 27, 28...) — the delta was unmeasurable (model loaded while the card was already moving, or the start didn't `--wait`). *Observed.*
- So telemetry answers "how much did the card jump when we started this" (useful for the live fit-gate) but **cannot decompose** into the 4 terms. The profiler's `MemorySnapshot`-style in-process measurement is the only clean decomposition. **The profiler and telemetry are complementary, not redundant:** profiler = clean per-term decomposition (durable `_profile`); telemetry = dirty whole-card load events (live learned fallback + drift detection). The `rollups()` "⚠ estimate off" flag (telemetry.py:58) is the friction-sensor that says "this model needs a real profile."

---

## 7 · Stress-tests / contradictions of the anchor (the "yes, but actually")

1. **"vLLM PRINTS the 4-term, parse it" (anchor §3, SCOPE §RESEARCH)** → *Yes, BUT only at DEBUG for the split + suggested byte budget.* INFO gives weights + cudagraph-total + KV-tokens. Build the profiler to set `VLLM_LOGGING_LEVEL=DEBUG`, or prefer the attribute-read path. **Contradiction grounded.**
2. **"cuda-graph blind spot can OOM even with a correct budget" (anchor §4, §6)** → *Not in 0.21 by default — it's accounted (envs.py:266 True, subtracted gpu_worker.py:446).* The blind spot only opens if someone sets `VLLM_MEMORY_PROFILER_ESTIMATE_CUDAGRAPHS=0`. `enforce-eager` is a determinism choice, not a correctness patch. **Contradiction grounded.**
3. **"the absolute byte budget makes load-order stop mattering" (anchor §2 keystone, Open #1/#8)** → *Half-true, and the survivor is the requested-fraction check, not weights.* `request_memory` raises if `free < total × gpu_util` (utils.py:408-421), reading `gpu_util` unconditionally — `kv_cache_memory_bytes` does NOT suppress it. With static `gpu_util 0.9` that's a ~14.4 GiB free demand at boot, far above the 5.67 GiB weights. Fix: the resolver must co-lower `gpu_util` to the measured footprint fraction alongside the byte budget, shrinking the survivor to the irreducible weights-resident step; sequencing/sleep-mode covers only that. **Refined with a trace + a concrete lever for AREA-2.**
4. **per-seq 34 vs 49.5** → *Neither is "the" number; they measure different things (marginal vs architectural).* The profiler captures both and flags divergence. **Reconciled by keeping both.**
5. **"measure by a knob-sweep" (Open #2)** → *Mostly no.* One boot for the 4-term + per-token-KV; a 2-point sweep ONLY for measured `per_seq_mb`. **Reduced the work.**
6. **My-idea risk on myself:** the attribute-read path (§4b) assumes worker attributes are reachable from the `LLM` handle — vLLM 0.21 runs EngineCore in a child process, so this may need an RPC, not a direct read. **Flag for a build-phase spike — do NOT assume it works.**

---

## 8 · Open threads handed to synthesis / build
- **Build-phase verify (held this session — FP8 brain is mid-audit):** one real DEBUG boot of chat-4b-fp8 (after the audit restores) to (a) confirm every term parses, (b) capture the two solo-vs-co-resident boot logs that close the −3.78 attribution (currently Inferred), (c) populate its `_profile` and retire its static `gpu_util: 0.9`.
- **Attribute-read spike:** confirm `model_runner.model_memory_usage` / `worker.peak_activation_memory` etc. are reachable post-init in 0.21's process topology, or via what RPC.
- **Profiler ↔ AREA-2 boundary:** the profiler writes terms; the resolver turns them into `--kv-cache-memory-bytes`. Confirm AREA-2 wants the raw terms OR vLLM's `suggested_kv_bytes` (the keystone shortcut) — likely both, with `suggested_kv_bytes` as the trust-but-verify default.
- **kokoro id:** locate/catalogue the model before profiling (its `_note` flags it); decide CPU-vs-GPU for voice from the measured number.
- **enforce-eager decision:** measure throughput cost on our FP8 before adopting it as a determinism default — it's a tradeoff, not free.

---

### Provenance
All vLLM citations from the installed `0.21.0` source under `/home/tim/vllm-env/lib/python3.12/site-packages/vllm/`. Company citations from `/home/tim/company/ops/`. The `nvidia-smi [N/A]` and the live `services.json` profile state were read this session. No model was booted (SCOPE §State). The prior research artefact (`.data/unify-exercise/gpu-autoprofiler-research.html`) is cited as External where its numbers were not re-derived here; its block-size log string was checked against our 0.21 source and **not found** — flagged in §2.
