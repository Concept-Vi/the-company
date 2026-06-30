---
type: research-finding
register: descriptive
area: 5
title: "Scheduler / Concurrency / Cache — the runtime that lets ONE loaded model serve mixed workloads"
status: unconfirmed
coverage: {vllm_version: "0.21.0 (verified /home/tim/vllm-env/.../vllm/version.py:0.21.0)", files_read: "vllm scheduler/config/offloading + company runtime/ops paths", note: "source-grounded; no live launch (brain solo on :8001 serving another session's @extract audit — must not reconfigure)"}
tags: [gpu, vllm, scheduler, priority, chunked-prefill, kv-offload, prefix-cache, loadout, research]
---

# AREA 5 — Scheduler / Concurrency / Cache

**The one-line answer to my area's headline question:** with vLLM 0.21's V1 scheduler, **one instance configured at the worker's `max_num_seqs` can serve BOTH shapes** — the deep-context conversation AND the many-small swarm — *and the two-loadout split for the SHAPE tension largely dissolves*, because chunked-prefill + priority + prefix-cache + (optionally) KV-offload are exactly the built-ins that let a deep prompt and many small jobs share one shelf without a reload. The remaining reason to keep two loadouts is **co-residency** (whether the embedder/voice sit on the card), not the conversational-vs-worker shape. The arithmetic is in §6. But there is one hard blocker the anchor under-weights: **priority is not plumbed through our transport today** (§1), and a second the anchor gets wrong-way-round: **you cannot "just unset" `max_num_seqs`** (§3).

Evidence tags throughout: **Observed**(file:line / URL) · **Inferred** · **External** · **My-idea**.

---

## 1 · Priority scheduling — REAL in vLLM, but a DEAD WIRE in our stack today

### What vLLM actually does (Observed)
- **Policy is engine-level, set at launch.** `SchedulerConfig.policy: SchedulerPolicy = "fcfs"`, where `SchedulerPolicy = Literal["fcfs", "priority"]` — **Observed** `vllm/config/scheduler.py:22,109`. So `--scheduling-policy priority` flips the whole instance into priority mode; it is **not** per-request-selectable which *policy* runs, only the per-request *priority value*.
- **Priority is a top-level REQUEST field, NOT a SamplingParams field.** Both the chat and completion request bodies carry it:
  - `priority: int = Field(default=0, ge=_INT64_MIN, le=_INT64_MAX, ...)` — **Observed** `vllm/entrypoints/openai/chat_completion/protocol.py:324` and `.../completion/protocol.py:107`.
  - The field doc: *"The priority of the request (lower means earlier handling; default: 0). Any priority other than 0 will raise an error if the served model does not use priority scheduling."* — **Observed** chat_completion/protocol.py:329-331. (This confirms the anchor's "on generate()/add_request, NOT SamplingParams" — it rides the request body, then the handler forwards it.)
  - Handler forwards it verbatim: `priority=request.priority` into `engine_client.generate(...)` — **Observed** `chat_completion/serving.py:353`, `completion/serving.py:207`.
  - Down through the engine: `AsyncLLM.add_request(..., priority: int = 0, ...)` → `input_processor.process_inputs(..., priority=priority)` → `Request(priority=...)` — **Observed** `v1/engine/async_llm.py:292/358`, `v1/engine/input_processor.py:244/373`, `v1/request.py:73,83`.
- **The ordering is a strict heap, lower-first, ties by arrival.** `PriorityRequestQueue` is a `heapq` over `Request`; `Request.__lt__` compares **`(priority, arrival_time, request_id)`** — **Observed** `v1/core/sched/request_queue.py:131-152`, `v1/request.py:302+`. `create_request_queue(PRIORITY)` returns the heap; FCFS returns a plain `deque` — **Observed** request_queue.py:201-208.
- **Preemption IS priority-aware.** When the KV cache can't allocate slots for a request, under PRIORITY policy the scheduler preempts the **lowest-priority running request** (`max(self.running, key=lambda r: (r.priority, r.arrival_time))`); under FCFS it pops the last (latest-arrived). — **Observed** `v1/core/sched/scheduler.py:436-462`.

### The "yes, but actually" — our transport silently drops priority (Observed)
This is the blocking gap. Our generate path is `client.complete(openai_transport(...), ...)`. The transport builds the request body from an **allowlist**:
```python
# fabric/transport.py:44-45  (Observed)
"temperature", "max_tokens", "top_p",   # the original three, byte-identical order
"repetition_penalty",                   # the O2 generation-policy ladder rung
```
`_apply_sampling` copies **only** those keys from `opts` into the body (`fabric/transport.py:60`, `body[k] = opts[k]`). **`priority` is not in the allowlist**, so even if we launch the brain with `--scheduling-policy priority`, every request goes out with the default `priority=0` and the priority queue degenerates to arrival-order. **The scheduling policy is inert until we plumb the value.**

`client.complete(transport, ..., **opts)` forwards arbitrary `**opts` to the transport — **Observed** `fabric/client.py:65-67,117` — so the value *can* reach the transport; the only edit needed is the allowlist + a `priority` kwarg on `run_role`.

### Anti-starvation — there is NONE in our version (Observed + External)
- **Observed:** `Request.__lt__` is purely `(priority, arrival_time, request_id)` with **no aging term** (request.py:302+); the heap never re-weights a long-waiting low-priority request. A continuous stream of high-priority (low-number) chat turns can starve the swarm indefinitely.
- **External:** vLLM's own docs note FCFS "ensures fairness and preventing starvation" but describe dynamic priority adjustment to prevent starvation as a *separate/aspirational* mechanism — there is an open RFC ([Issue #6077](https://github.com/vllm-project/vllm/issues/6077)); it is **not** in the 0.21 `PriorityRequestQueue` I read. So: **what saves us from starvation is our workload shape, not a built-in guard** — chat is intermittent (a turn every few seconds, each finishing in seconds), so the swarm gets the card back between turns. **My-idea / design note:** keep the *priority gap small* (chat=0, swarm=10, audit=100) and rely on the intermittency; do NOT run a perpetual high-priority generator. If we ever do, we'd need to add an aging term ourselves (out-of-stack custom — avoid).

### How the foreground chat jumps ahead — the concrete wiring (My-idea, grounded)
Both paths converge on the transport:
- **Foreground chat:** `Suite.chat_parts` → main stream via `client.complete(...)` and the finished-thought judge `is_finished_thought` via `client.complete(...)` — **Observed** `runtime/suite.py:7121,7212,6575`. These should pass **low priority (0)**.
- **Background swarm:** `chat_parts` fires the cast via `_cog.run_swarm(...)` — **Observed** suite.py:7212 — and `run_swarm`'s `_one` calls `run_role(...)` — **Observed** `runtime/cognition.py:1461`. These should pass **high priority number (e.g. 10)**.
- **Audit/@extract bulk worker:** the bulk path also rides `run_role`/`run_items`; pass an even higher number (e.g. 100) so a returning chat preempts it.
- **MCP-initiated jobs (incl. the @extract audit from the other session):** confirmed to funnel through the SAME seam — `mcp_face/server.py:378` imports `runtime.cognition as _cog` ("the ONE engine"), and the MCP `run_role` tool delegates via `out = _cog.run_role(r, ctx, meta=meta, **kw)` (**Observed** mcp_face/server.py:770), explicitly documented as *"REUSES runtime.cognition.run_role (the SAME fire path run_swarm/dry_run_role use — never a parallel)"* (server.py:674). `run_items`/`run_draft`/`run_cascade` all route through `_fire_role_and_persist` → `_cog.run_role` too (server.py:719-722,814-815). **There is no MCP-side bypass `client.complete` for generation** — so the single allowlist+`run_role` edit genuinely covers chat, swarm, AND every MCP-initiated background job. The wiring is single-point.

**Proposed wiring (minimal, additive, byte-identical when absent):**
1. Add `priority: int = 0` param to `run_role(...)` (cognition.py:303) → put it into `opts` → through `complete()` → transport.
2. Add `"priority"` to the transport allowlist (`fabric/transport.py:44`). It's a valid request-body key (it lives on the *request*, not SamplingParams — so it does NOT belong in `_apply_sampling`'s sampling family; cleanest is a tiny `_apply_request_meta(body, opts)` that copies `priority` to the top-level body, OR just add it to the same copy-loop since the body is one flat dict). **Flag:** keep it OUT of the sampling allowlist's *semantic* grouping even if physically the same loop, so a future reader doesn't think priority is a sampling knob.
3. `run_swarm` defaults its `run_role` calls to a high number; `Suite.chat`/`is_finished_thought` default to 0.
4. **Loadout carries the policy:** the brain loadout declares `scheduling: priority` → resolves to `--scheduling-policy priority` at launch (§7). When the policy is `fcfs`, sending a non-zero priority is the documented error case — so the value passthrough must be **gated on the active loadout declaring priority** (fail-loud or send 0 otherwise). **My-idea:** safest default = send priority only when the resolved loadout declares priority scheduling; else omit (→0). The resolver already knows the loadout, so this is a clean gate.

---

## 2 · Chunked prefill + the unified V1 scheduler — the "do we even need two loadouts?" engine

### Observed facts
- **On by default for our model.** `SchedulerConfig.enable_chunked_prefill: bool = True` — **Observed** scheduler.py:84. The auto-setter enables it when `model_config.is_chunked_prefill_supported` and warns that disabling it on a model that supports it "may cause the engine to crash or produce incorrect outputs" — **Observed** `engine/arg_utils.py:2305-2322`. → **Do NOT disable chunked prefill on the hybrid Qwen3.5.**
- **Decode-priority batching.** **External** (vLLM docs, Optimization & Tuning): with chunked prefill, the scheduler **batches all pending decode requests before scheduling any prefill**, then fills the rest of the `max_num_batched_tokens` budget with prefill chunks. This is *exactly* the property the anchor wants: a 100K-token conversation turn that fires gets sliced into chunks and interleaved, so the 32 small jobs' **decodes keep streaming** (low ITL) while the big prefill drips in. The deep turn does not block the swarm, and the swarm does not block the deep turn's progress.
- **The dial.** `max_num_batched_tokens` is the per-step token budget — the **ITL↔TTFT** trade. Smaller = smoother decode for concurrent small jobs (lower ITL), slower big-prompt TTFT; larger = faster big-prompt prefill, choppier concurrent decode. — **Observed** scheduler.py:49-54 + **External** docs.
- **`scheduler_reserve_full_isl: bool = True`** (default ON) — **Observed** scheduler.py:140-144: *"the scheduler checks whether the full input sequence length fits in the KV cache before admitting a new request... Prevents over-admission and KV cache thrashing with chunked prefill."* This is a built-in admission control that already protects against the "32 huge prompts admitted, then thrash" failure. **Correction to SCOPE §flags:** SCOPE lists `--scheduler-reserve-full-isl` as an optional MIXING flag; it is **already the default `True`**, not something to turn on. Leave it on.

### Value for a 4B on 16GB (My-idea, grounded by §6 math)
- `max_num_batched_tokens`: vLLM's auto value for our card+server context is **2048** (§3). For a mixed deep+swarm workload, **My-idea:** set it explicitly to ~**2048–4096**. 2048 keeps ITL tight for the 32-way swarm; 4096 halves big-prompt TTFT at a modest ITL cost. Given the deep conversation is intermittent and the swarm is the throughput-sensitive load, **start at 2048 (the auto default) and only raise if deep-turn TTFT is painful** — this is a verify-by-use dial, not a guess.
- Note the forced **block/page size 1056** (the Mamba-aligned page, SCOPE §measured) interacts with chunked prefill: chunk boundaries on hybrid models are block-aligned (`_mamba_block_aligned_split` — **Observed** scheduler.py:400), so the effective chunk granularity is a multiple of 1056. This is fine for throughput; it's the prefix-cache where 1056 bites (§5).

**Conclusion for the headline:** chunked-prefill (on) + decode-priority batching means **one instance genuinely time-shares a deep prefill and many small decodes**. Combined with §1 priority (chat preempts swarm) and §6 (the budget fits at `max_num_seqs=32`), the SHAPE-tension justification for two loadouts collapses. See §6 for the explicit fit.

---

## 3 · `max_num_seqs` auto-derive — READ the method; we MUST keep setting it

I read the real method: `_set_default_max_num_seqs_and_batched_tokens_args` (**Observed** `engine/arg_utils.py:2377-2449`) and its table `get_batch_defaults` (**Observed** arg_utils.py:2217-2298).

### What it computes for OUR card/context (Observed)
The table branches on `device_memory >= 70 GiB`. Our card is **16 GB Ada → the `else` branch**:
```python
# arg_utils.py:2256-2265  (Observed) — the <70GiB branch
default_max_num_batched_tokens = {LLM_CLASS: 8192, OPENAI_API_SERVER: 2048}
default_max_num_seqs          = {LLM_CLASS: 256,  OPENAI_API_SERVER: 256}
```
We launch via `vllm serve` → **OPENAI_API_SERVER** usage context → if `max_num_seqs` is unset, vLLM derives **`max_num_seqs = 256`** and **`max_num_batched_tokens = 2048`** (then clamped: `max_num_seqs = min(256, 2048) = 256`, and `max_num_batched_tokens = min(256*max_model_len, 2048) = 2048`) — **Observed** arg_utils.py:2403-2407,2430-2443.

### Why we must NOT stop setting it (the refutation, with numbers)
**`max_num_seqs=256` is a guaranteed OOM on our hybrid model.** Each concurrent slot reserves a fixed **~34 MiB Mamba/SSM state at load** (SCOPE §measured; our `auto_gpu_util` already encodes `per_seq_mb × max_num_seqs` — **Observed** `ops/cli/gpu.py:~120`). At 256 slots:
```
256 × 34 MiB ≈ 8,704 MiB ≈ 8.5 GiB   reserved purely for per-seq Mamba state
+ weights 5.67 GiB
= 14.2 GiB before a single token of KV shelf or activation/cudagraph
```
On a 16,376 MiB ceiling that leaves ~2 GiB for KV+activation+cudagraph — it will not boot, and is the exact `No available memory for the cache blocks` class from the SCOPE incident. **The auto-derive is tuned for attention-only models where a seq slot is nearly free; it has no notion of the per-seq Mamba toll.** → **Verdict: keep `max_num_seqs` explicit, computed from the loadout's declared concurrency, NOT auto-derived.** This is a concrete place the "lean on vLLM built-ins" instinct is wrong — the built-in default is unsafe for our architecture.

**My-idea:** the *computed* value should come from the loadout's declared shape (deep-context → 2–4; worker → 32) bounded by what the budget fits (§6), and `auto_gpu_util` already sizes VRAM to that explicit `max_num_seqs`. So the flow is: **loadout declares concurrency → serveconfig emits `--max-num-seqs N` → `auto_gpu_util` reserves `N × per_seq_mb`.** (Today serveconfig only emits `--max-num-seqs` if `c.get("max_num_seqs")` is set — **Observed** `ops/cli/serveconfig.py:86-87` — so the wiring point exists; it just needs the loadout-shape source.)

---

## 4 · KV-offload to CPU RAM — native, and it HANDLES THE HYBRID STATE (the gold)

This is the finding I'm most confident materially upgrades the anchor.

### Config surface (Observed)
- `CacheConfig.kv_offloading_size: float | None = None` — GiB buffer; None = off. — **Observed** `vllm/config/cache.py:167-171`.
- `kv_offloading_backend: KVOffloadingBackend = "native"` — default native; alt "lmcache". *"KV offloading is only activated when kv_offloading_size is set."* — **Observed** cache.py:173-176. **This confirms SCOPE/research: native is the default, no LMCache to stand up.**
- The connector is `OffloadingConnector` (`distributed/kv_transfer/kv_connector/v1/offloading_connector.py`), driven by an `OffloadingSpec` built from the live `kv_cache_config` — **Observed** offloading_connector.py:46-66.

### THE "yes-but-actually": does it move the MAMBA state, or only attention KV? — IT MOVES BOTH (Observed)
The advisor flagged the real risk: for an 8-attention / 24-GatedDeltaNet model, if native offload only spills attention-KV, persisting "the deep conversation in RAM" is only partial. **I read the worker. It is not partial.** The offload worker iterates **every** `kv_cache_group` and branches on the per-layer spec:
```python
# distributed/kv_transfer/kv_connector/v1/offloading/worker.py:86-189  (Observed)
for kv_cache_group in self.spec.kv_cache_config.kv_cache_groups:
    ...
    if isinstance(layer_kv_cache_spec, AttentionSpec):
        ...                       # offload attention KV pages (lines 97-161)
    elif isinstance(layer_kv_cache_spec, MambaSpec):
        state_tensors = kv_caches[layer_name]   # the SSM/conv state
        ...                       # reconstruct (num_blocks, page_size) and offload it (lines 163-186)
    else:
        raise NotImplementedError
```
And our model's linear layers ARE `MambaSpec`: `class GatedDeltaNetAttention(PluggableLayer, MambaBase)` — **Observed** `vllm/model_executor/layers/mamba/gdn_linear_attn.py:239`. Our served model file `qwen3_5.py` imports it **directly**: `from vllm.model_executor.layers.mamba.gdn_linear_attn import GatedDeltaNetAttention` — **Observed** `vllm/model_executor/models/qwen3_5.py:43` (the layer is wired in at `qwen3_next.py:340`, `self.linear_attn = GatedDeltaNetAttention(...)`). So the qwen3_5→GDN→MambaSpec chain is fully traced, not inferred. So **all 32 layers' state (8 attention pages + 24 Mamba state blocks) are offloadable** — the *whole* conversation state can spill to RAM and come back. The `else: raise NotImplementedError` (worker.py:189) is the fail-loud guard for any unrecognized spec — exactly the "no silent drop" property.

### Reload-not-recompute (Observed)
- On preemption the connector stores the blocks (`handle_preemptions` submits `transfer_async` store jobs — **Observed** worker.py:286-290).
- On a returning request, `get_num_new_matched_tokens` returns how many of the request's tokens are already present in the offload store (so they're **loaded back, not recomputed**) and the scheduler allocates around them — **Observed** offloading_connector.py:120-126 + `update_state_after_alloc` 128-134. This is the literal "reloads-not-recomputes" mechanism the anchor wants.

### Fit for our "one deep main thread + bursts" pattern (Inferred + My-idea)
- **RAM cost:** `kv_offloading_size` GiB of pinned-ish CPU buffer. SCOPE: `ram_headroom_mb: 2048` is reserved. **Caveat (Observed/External):** SCOPE/anchor note **WSL2 has `pin_memory` off**, so CPU↔GPU transfers are pageable (slower) — the offload *latency* will be worse than on bare metal. → **Inferred:** native KV-offload is a good fit for the **idle-conversation-persistence** case (a deep chat parked while the swarm runs, reloaded when the user returns — latency hidden behind think-time) but a **poor fit for hot per-token spill** (don't size the GPU shelf so tight that active decode constantly offloads). 
- **My-idea / value:** set `kv_offloading_size` to a modest **2–4 GiB** so a 100K-ish deep conversation's state survives eviction when the worker loadout briefly needs the shelf — this is what lets one instance "hold" a deep thread *across* a swarm burst without keeping its KV resident on the GPU. It directly supports the §6 collapse: the deep conversation doesn't need a *reserved* GPU shelf; its state lives in RAM and is paged in on the next turn.
- **native vs LMCache:** research said native wins at our scale; the code confirms native is the zero-dependency default and **handles our hybrid spec natively** — no reason to stand up LMCache. (LMCache would add an external process + its own memory; pure overhead here.)

**Flag (needs live verify, do NOT verify on the live brain now):** the *throughput* of pageable WSL2 transfers and whether MambaSpec offload is bug-free on 0.21 for this model is unverified. Mark **needs-verification** in the build, not green.

---

## 5 · Prefix caching — ON, but the 1056 block guts it for the worker (Observed + Inferred)

- **On by default** for supported models: `enable_prefix_caching` auto-set from `model_config.is_prefix_caching_supported` — **Observed** arg_utils.py:2334-2342.
- **The 1056-block problem is real.** SCOPE §measured: the attention page is padded to equal the Mamba page → **block/page size 1056 tokens**. Prefix-cache reuse is **block-granular**: a shared prefix only produces a cache hit for *complete* 1056-token blocks. (Area 4 attacks this directly; I assess the upside.)
- **Inferred upside split:**
  - **Conversation (deep main thread):** prefix caching is a CLEAR win. A long system prompt + growing conversation history spans many full 1056-blocks; each new turn reuses all the completed blocks of the prefix → big TTFT savings. The 1056 granularity barely hurts because the prefix is long.
  - **Many-small @extract worker:** prefix caching is **mostly worthless**. If each extract job is a short prompt (< 1056 tokens) with a shared system preamble that *also* doesn't fill a block, there are **zero complete shared blocks** → ~0% hit rate (SCOPE's "hit-rate drops toward 0 below the block size"). Worse, each small request rounds **up** to a 1056 multiple → internal fragmentation (a 200-token job occupies a 1056 slot). 
- **My-idea:** for the worker loadout this means (a) don't *rely* on prefix caching for throughput — the win comes from concurrency (`max_num_seqs=32`) + chunked prefill, not prefix reuse; and (b) the fragmentation is a real shelf-capacity tax the §6 budget should acknowledge (a 32-way worker at short prompts uses more blocks than the raw token count implies). It does NOT argue for disabling prefix caching (it costs ~nothing when it misses) — just don't count it as a worker win. **It is a strong argument that the conversation and the bulk-audit are genuinely different *cache* regimes even if one instance serves both** — which is the strongest surviving reason to consider a loadout distinction (see §6 caveat).

---

## 6 · THE HEADLINE COMPUTATION — does one instance obviate the two-loadout split?

All numbers from SCOPE §measured (RedHatAI/Qwen3.5-4B-FP8-dynamic, fp8-KV) + services.json (`vram_ceiling_mb: 16376`, `vram_overhead_mb: 1024`). In Tim's units: **1 unit = 16,384 tok ≈ 0.28 GiB of full-context KV per concurrent seq** (SCOPE: 17.4 KB/tok × 16384 / 1024² ≈ 0.272 GiB).

### Fixed costs (independent of concurrency)
```
weights (FP8)                          = 5.67 GiB   (boot log "Model loading took 5.67 GiB")
cuda-graph (captured after profiling)  ≈ 0.43 GiB   (the blind-spot term; OR set --enforce-eager → ~0)
overhead margin (services.json)        ≈ 1.00 GiB   (activation/fragmentation)
--------------------------------------------------
fixed                                  ≈ 7.10 GiB   (6.10 GiB with --enforce-eager removing cudagraph
                                                      AND if overhead is trimmed; conservatively ~7.1)
```
Card ceiling = 16,376 MiB ≈ **16.0 GiB**. So the **KV+per-seq budget left ≈ 8.9 GiB** (solo, no embedder/voice co-resident).

### The two shapes, as ONE instance at `max_num_seqs = 32`
**Per-seq Mamba toll** (reserved at load, all 32 slots): `32 × 34 MiB ≈ 1.06 GiB`.
Remaining for the KV shelf: `8.9 − 1.06 ≈ 7.84 GiB` → at 0.272 GiB per 16K-unit per seq, that's **~28.8 units = ~472K tokens of shelf** (matches SCOPE's measured ~487K-token shelf at gpu_util 0.9 solo, max_num_seqs 32 — consistent within margin).

Now serve **both shapes on this one instance:**
- **Worker shape (32 × small):** 32 jobs × ~2K tokens = 64K tokens of active shelf — trivially inside 472K. ✓
- **Deep conversation (1 × deep) sharing the SAME instance:** a 100K-token conversation turn needs 100K tokens of shelf *while it is actively generating*. 100K + the 64K worker = 164K — still inside 472K. ✓ And per SCOPE's mental model, **idle conversation history is FREE** (evictable prefix cache / or offloaded to RAM per §4); only the *active forward pass* competes. So the deep turn only collides with the swarm during the seconds it's actually firing — and chunked-prefill (§2) interleaves them, priority (§1) lets the chat preempt swarm KV blocks (scheduler.py:436), and RECOMPUTE preemption (§next) requeues the bumped swarm jobs without a crash.

### The cost of running the conversation at `max_num_seqs=32` instead of 2
The *only* extra fixed cost of giving the conversational loadout the worker's concurrency cap is the per-seq Mamba reservation: `(32−2) × 34 MiB ≈ 1.02 GiB` of VRAM that sits reserved even when chat is 1-deep. On an 8.9 GiB KV budget that's ~11% of the shelf — it shrinks the max single-turn context from ~487K to ~472K tokens. **That is the entire price.** Everything else (chunked prefill, prefix cache, priority) is free behaviour.

### Verdict
**For the SHAPE tension alone, ONE instance at `max_num_seqs=32` + priority + chunked-prefill + KV-offload obviates the two-loadout split, at a cost of ~1 GiB / ~15K tokens of shelf headroom.** The conversational↔worker "two declared loadouts of the same model" (anchor §4 My-idea) is **not needed** to resolve the shape tension — that My-idea is over-built for this axis. The work *picks its priority and its prompt size*, on one running instance.

### The surviving reasons to keep loadout DISTINCTIONS (honest caveats)
1. **Co-residency, not shape.** The real reason `interaction-fp8` and the `@extract` worker differ is whether the **embedder (~5.4 GiB) + voice (~0.9 GiB)** are on the card. With them resident, the fixed budget jumps by ~6.3 GiB and the shelf collapses (this is the SCOPE −3.78 GiB co-resident incident). So the genuine loadout axis is **"recall/voice co-resident (interaction) vs solo (bulk worker)"** — exactly what SCOPE's `interaction` vs the solo `@extract` already encode. The shape (concurrency) can then be ONE high value across both; what changes between loadouts is **who else is on the card**, which is where §7's computed budgets + sleep-mode/order matter.
2. **Cache regime (§5).** Conversation benefits from prefix caching; the worker doesn't and pays 1056-fragmentation. This is a *soft* reason — same instance still serves both correctly — but if we ever wanted to tune `max_num_batched_tokens` differently (tight ITL for the swarm vs fast TTFT for deep chat), that's a per-instance launch flag, i.e. a loadout difference. **My-idea:** keep it one instance with the swarm-friendly `max_num_batched_tokens=2048`; deep-chat TTFT is acceptable because chat is intermittent.
3. **`max_model_len` ceiling.** A single instance has one `--max-model-len`. If the deep conversation needs 128K but the worker only 8K, you set the instance to 128K (the worker just doesn't use it — max_model_len is a *ceiling*, not a reservation, SCOPE §rules). So this does NOT force two loadouts either.

**Net:** collapse the conversational/worker shape split into one instance; keep loadouts for **co-residency** (recall/voice on or off the card). This is a real simplification of the anchor's 7-phase plan §5 (the `@extract` worker loadout becomes "the solo loadout," differing by co-tenants, not by a re-tuned instance shape).

---

## 7 · Queue + RECOMPUTE preemption — graceful overflow (Observed + External)

- **Default preemption is RECOMPUTE.** `_preempt_request` frees the request's KV (`kv_cache_manager.free`), sets `status = PREEMPTED`, **`num_computed_tokens = 0`**, and **prepends it back to the waiting queue** — **Observed** `v1/core/sched/scheduler.py:910-931`. So an overflowed request is **requeued and re-prefilled from scratch**, never dropped, never a crash. **External** (vLLM docs) confirms V1 defaults to RECOMPUTE over SWAP because recompute has lower overhead in V1. This grounds SCOPE's "queue + RECOMPUTE-preemption handle overflow gracefully."
- The cost: a preempted swarm job loses its computed tokens and re-prefills — wasted compute, not a failure. With priority scheduling, the scheduler preempts the **lowest-priority** running request first (the audit before the swarm before the chat) — **Observed** scheduler.py:436-441 — so the foreground chat's work is the *last* to be thrown away. This is the correct behaviour.
- **Admission control** (`scheduler_reserve_full_isl=True`, §2) reduces how often this happens by not over-admitting in the first place.

---

## 8 · Async scheduling (the dark-horse, opt-in) — Observed

- `SchedulerConfig.async_scheduling: bool | None = None` — *"If set to False, disable async scheduling. Async scheduling helps to avoid gaps in GPU utilization, leading to better latency and throughput."* — **Observed** scheduler.py:146-149.
- `get_scheduler_cls()` returns `AsyncScheduler` when `async_scheduling` is truthy, else the default `Scheduler` — **Observed** scheduler.py:168-176. So `None`/`False` → the standard scheduler; you must explicitly set it on.
- **My-idea / value:** overlaps CPU-side scheduling with GPU compute → helps the many-small swarm (lots of short steps = lots of scheduling overhead to hide). **Worth adopting for the worker/solo loadout**, but it's a verify-by-use knob (it can interact with spec-decode and has had edge cases). Mark **adopt-and-verify**, not assumed-good. The SCOPE/anchor flag of "async-scheduling opt-in" is correct.

---

## 9 · Where these attach in OUR machinery (the build wiring — grounded)

The serve-flags resolver is the right home, exactly as the anchor §5 says:
- **Flags are generated per-capability.** `serve_flags(config)` resolves a family's **ordered capability list** → each capability's stack serve-fragment → concatenated flags — **Observed** `runtime/capabilities/resolver.py:261-328`. New scheduler/cache flags become **new capability rows + stack serve-fragments**, not raw flags. Today the qwen3.5 family's `serve_params` carries `tool_parser`/`reasoning_parser` (**Observed** `family_capabilities.json`), and nemotron carries `cpu_offload_gb:6` (the WEIGHT-offload precedent — proves the pattern accepts numeric serve params).
- **Concretely, add these as serve-contract capabilities:**
  - `scheduling-policy` → `--scheduling-policy {policy}` (loadout/family declares `priority`); gates the §1 priority passthrough.
  - `chunked-prefill` (assert on; emit nothing or `--enable-chunked-prefill`) + `max-num-batched-tokens` → `--max-num-batched-tokens {n}`.
  - `kv-offload` → `--kv-offloading-size {gib}` (backend native = default, no flag).
  - `async-scheduling` → `--async-scheduling` (worker/solo loadout only, verify-by-use).
  - `kv-cache-memory-bytes` + `enforce-eager` are Area-2/3's keystone but ride the same resolver.
- **`max-num-seqs` and the gpu-util fraction stay in `serveconfig.args_for`** (the runtime-param head, before `_resolved_flags`) — **Observed** `serveconfig.py:79-89`. `--max-num-seqs` is already emitted from `c["max_num_seqs"]`; the only change is sourcing that integer from the **loadout's declared concurrency shape** rather than a hand-typed services.json value, and `auto_gpu_util` already consumes it for the per-seq reservation (`ops/cli/gpu.py`).
- **Loadout-carries-intent (anchor §3):** a combo/loadout in services.json declares `{scheduling, concurrency, kv_offload_gib, async}` (My-idea schema); bring-up resolves them into the serve command. The `requires:`-gate + `apply_loadout`/`active_brain` machinery (SCOPE §done) is the actuator.

---

## 10 · Summary of contradictions / upgrades to the anchor (the honest delta)

| Anchor/SCOPE claim | My finding | Tag |
|---|---|---|
| Priority "on generate()/add_request, NOT SamplingParams" | Correct — it's a top-level *request-body* field (protocol.py:324) forwarded to `generate(priority=)`. **But our transport allowlist drops it (transport.py:44) — inert today.** | Observed |
| `--scheduler-reserve-full-isl` is a MIXING flag to set | It's **already default `True`** (scheduler.py:140). Leave on; don't "turn it on." | Observed |
| "max_num_seqs auto-derived if unset" → should we stop setting it? | **NO.** Auto-derive gives **256** on our card (arg_utils.py:2262), ≈8.5 GiB of per-seq Mamba toll → guaranteed OOM. The built-in default is unsafe for our hybrid arch. Keep it explicit + loadout-sourced. | Observed+computed |
| KV-offload persists conversation across eviction | **Yes, and it offloads the Mamba/SSM state too** (worker.py:163 handles MambaSpec; our GDN layers ARE MambaSpec, gdn_linear_attn.py:239) — the *whole* hybrid conversation can spill to RAM and reload-not-recompute. Caveat: WSL2 pageable transfers = slower; size for idle-persistence not hot-spill. | Observed |
| Two loadouts (conversational vs worker) needed for the shape tension | **No** — one instance at `max_num_seqs=32` + chunked-prefill + priority + KV-offload serves both, costing ~1 GiB / ~15K-token shelf. The real loadout axis is **co-residency** (recall/voice on/off the card), not shape. Simplifies plan §5. | computed+Inferred |
| Prefix-cache ≈0% below 1056 hurts the worker | Confirmed it's ~worthless for many-small jobs (and fragments), but a clear win for the deep conversation. Don't disable; just don't count it as a worker throughput source. | Observed+Inferred |
| RECOMPUTE preemption = graceful overflow | Confirmed: `_preempt_request` requeues with `num_computed_tokens=0`, never crashes; priority preempts lowest-priority first (chat last). | Observed+External |
| Starvation handled by the stack | **No anti-starvation/aging in 0.21's PriorityRequestQueue.** Our intermittent-chat workload is what prevents starvation, not a built-in. Keep priority gaps small; don't run a perpetual high-priority stream. | Observed+External |

**Sources (external):** vLLM Optimization & Tuning docs (https://docs.vllm.ai/en/stable/configuration/optimization/); Priority Scheduling RFC (https://github.com/vllm-project/vllm/issues/6077).

**Not verified live (deliberately — brain is solo serving another session's @extract; must not reconfigure):** the priority-preemption *behaviour* end-to-end; KV-offload throughput on WSL2 pageable transfers; async-scheduling stability on this model. All marked **needs-verification** for the build, never green from source-reading alone.
