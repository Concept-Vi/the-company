---
type: research-finding
register: descriptive
area: "AREA-3 · Loadout declaration + attachment"
wave: gpu-serving-rework
status: unconfirmed
coverage: {files_read: ["ops/cli/registry.py", "ops/cli/gpu.py", "ops/cli/serveconfig.py", "ops/cli/capabilities.py (ensure_resident)", "runtime/suite.py (_resolve_loadout/_gate_work_requires/apply_loadout/_repoint_rhm_for_loadout)", "runtime/capabilities/resolver.py", "runtime/capabilities/family_capabilities.json", "runtime/capabilities/capability_types.json", "runtime/capabilities/stack_capabilities.json", "ops/services.json (combos + brain/embedder configs)"], last_read: "2026-06-30"}
tags: [gpu, loadout, combo, capability-resolution, serve-flags, vllm, research, build-prep]
---

# AREA-3 — How a loadout DECLARES + CARRIES its resource intent, and how the per-loadout shape tension resolves

> Mandate: design where budget / concurrency / priority / cache / sleep DECLARE, how that intent flows
> through the live switch+gate, and resolve the conversational↔worker shape tension WITH EVIDENCE.
> I read every link in the chain. The headline below contradicts the anchor's tentative My-idea #4 framing
> — it keeps the conclusion (two loadouts) but corrects WHY, and exposes a wiring gap the anchor doesn't name.

---

## 0 · The one-paragraph answer (so the synthesis can anchor on it)

A loadout (combo) today is **only a list of service keys** — it carries NO per-service shape. All serve
shape lives on the **service's single `config` block** (`ops/services.json`). So "two loadouts of the same
model with different budgets" **has literally nowhere to put the difference** in the current architecture —
that is the real gap, and it is the backbone of this finding. The resolution is **(a) two declared loadouts of
the same model, but reframed**: not two hand-tuned configs (that re-commits the sin "the 50% has gotta go"),
but **two declared SHAPE-INTENTS whose budgets are COMPUTED** by the gpu.py spine. Option (b) "one instance
serves both via priority+chunked-prefill" is **impossible** — not (mainly) because of the Mamba reload toll,
but because the two shapes demand **opposite co-residency** (worker = card SOLO with the embedder evicted;
conversational = embedder RESIDENT for recall) and **vLLM cannot resize `max_num_seqs`/the KV pool without a
reload** (Observed: it is an init-time cap; External below). Option (c) sleep-mode reshapes nothing — it is a
VRAM time-share between already-loaded instances; its real home is the **model-swap axis** (4B↔9B), not the
conversational↔worker axis, and it is flagged broken since 0.14 so we don't lean on it. The missing layer is a
**per-service shape on the combo** that flows `combo → apply_loadout → ensure_resident(service, shape) →
serveconfig.args_for(key, shape) → computed KV-byte budget`. None of those links carry a shape param today.

---

## 1 · GROUND: what a loadout/combo actually IS right now (the spine fact)

**Observed (`ops/cli/registry.py:52-103` `combos()`):** a combo resolves to exactly
`{services: [keys...], note, [variant_of]}`. The variant grammar (`extends` / `swap` / `add` / `remove`)
operates **on the service LIST** — it adds/removes/swaps which keys are in the set. There is **no per-service
config layer** anywhere in a combo. Confirmed by dumping `reg["combos"]`: e.g.

- **Observed (`services.json` combos):** `interaction` = `[embed-pplx, chat-4b-fp8, rerank-jina, stt-moonshine, tts-kokoro]`;
  `interaction-fp8` = `extends interaction` `remove [rerank-jina]`; `interaction-parakeet` = `extends interaction`
  `swap {stt-moonshine: stt-parakeet-onnx}`; `quality-9b` = `[chat-9b-fp8]`.
- **Observed:** there is **no `@extract` combo in the registry at all.** SCOPE:74/89 says the worker shape is
  "currently hand-built live" — the other session edited `chat-4b-fp8.config` in place (`gpu_util 0.9 /
  max_num_seqs 32 / fp8-KV, solo`). That hand-edit is the very thing this rework exists to dissolve.

**Observed (`ops/cli/registry.py:30-43` + `gpu.py:86-101`):** all serve shape — `gpu_util`, `max_model_len`,
`max_num_seqs`, `family`, `capability_overrides`, `_profile` — lives on the **single `config` block of the
service**. There is exactly ONE config per service key.

**The consequence, traced concretely (Observed):**
```
suite.apply_loadout(sid)            # runtime/suite.py:2726 — reads payload.services (a key LIST)
  → for s in services:
        capabilities.ensure_resident(s, evict=True)   # ops/cli/capabilities.py:430 — takes a KEY, no shape
            → systemd.control(svc, "start")           # starts serve_model.sh <key>
                → serveconfig.args_for(key)           # ops/cli/serveconfig.py:79 — reads the ONE config block
```
Every link is keyed by the **service key only**. `chat-4b-fp8` started under `@interaction` and `chat-4b-fp8`
started under (a would-be) `@extract` would read the **identical** config block and serve **identically**.
The shape difference the loadout WANTS has no carrier. **This is the gap the anchor's My-idea #4 glosses over**:
it asks "(a) two loadouts of the same model with different computed budgets" as if the budgets could differ —
but with one config block per service, they cannot, until we add a per-service shape layer to the combo.

**Inferred:** the combo grammar already cleanly expresses the SET difference between two loadouts (which
services are co-resident). What it CANNOT express is the **per-service SHAPE** within the set. That is exactly
the missing primitive — and it is orthogonal to the set grammar, so it slots in without disturbing it.

---

## 2 · The shape tension, resolved against the REAL constraints

The anchor (§3, §8) and SCOPE (line 10, 74, 89) pose the same model wanting opposite shapes:

| | **Conversational** (`@interaction`) | **Worker** (`@extract`) |
|---|---|---|
| brain | chat-4b-fp8 | chat-4b-fp8 (SAME model) |
| co-residents | embed-pplx + rerank + voice **RESIDENT** | **SOLO** (embedder/voice **evicted**) |
| concurrency | `max_num_seqs ~2` | `max_num_seqs 32` |
| context | deep (65K+) | small per-seq |
| budget | small KV slice (~0.44 of card co-resident) | large KV slice (~0.9 solo) |
| Source | SCOPE:85 (the value to RESTORE) | SCOPE:74/89 (the live hand-built preview) |

### (b) "ONE instance serves both via priority + chunked-prefill" — REFUTED, twice over

This is the seductive answer ("don't reload, just schedule"). It is wrong on TWO independent grounds, and the
**sharper** of the two is not the one the anchor leads with:

1. **Opposite co-residency (the decisive one).** The worker shape needs the card **solo** — SCOPE:89 has the
   embedder + voice **EVICTED** to free the ~487k-token shelf. The conversational shape needs the embedder
   **resident** (recall is part of `@interaction`). A single running brain instance cannot be simultaneously
   "solo on the card" and "co-resident with the embedder." Priority + chunked-prefill schedule *latency between
   requests on one fixed memory shape* — they **do not change what else is on the card**, and they do not free
   VRAM for the embedder or take it back. So even if concurrency were reconfigurable, (b) cannot satisfy both
   co-residency requirements at once. **My-idea contradiction of the anchor:** §8's open what-if "Can one model
   serve both shapes live (priority + chunked prefill)?" conflates *scheduling on a shape* with *changing the
   shape*. They are different axes. Priority is a real, valuable built-in — but it lives WITHIN a loadout
   (foreground chat > background swarm on the SAME resident set), not across the two loadouts.

2. **`max_num_seqs`/KV-pool are init-time, not runtime-tunable (External + Observed).** vLLM allocates the KV
   cache pool and the per-sequence state slots at **engine init**; `max_num_seqs` is an upper cap fixed at
   start (External: vLLM docs/issues describe it as a launch arg; no runtime-reconfigure API was found — see
   Sources). For our **hybrid Mamba** brain this is doubly hard: the per-seq Mamba state (~34 MiB/slot MEASURED,
   SCOPE:33) is **reserved at LOAD for `max_num_seqs` slots** — Observed in our own budget math at
   `ops/cli/gpu.py:72-79` (`per_seq_mb × max_num_seqs`, with the comment "reserved at LOAD"). Changing
   concurrency = changing that reservation = a **reload**. So you cannot grow a 2-slot conversational instance
   into a 32-slot worker instance live.

### The reload objection to (a) is MOOT

The naive case against (a) — "two loadouts = a reload, reloads are expensive" — does not apply: switching
`@interaction ↔ @extract` is **already** a teardown/bring-up. `@extract` **evicts the embedder + voice**;
`apply_loadout` already runs `ensure_resident(..., evict=True)` per service (Observed `suite.py:2752-2755`),
which tears down and re-starts. The brain reload is **inherent to the co-residency swap**, not an extra cost
that declaring two shapes introduces. So (a)'s only "cost" is one we already pay. **This dissolves the anchor's
own hesitation in My-idea #4** ("a config change = a vLLM reload" framed as a cost of (a)).

### (c) sleep-mode — RIGHT TOOL, WRONG AXIS

**External (anchor §6, SCOPE:51):** `--enable-sleep-mode` frees a model's VRAM (~1s wake) — a **time-share
between two ALREADY-LOADED instances at their own fixed shapes.** It changes nothing about a load-time
`max_num_seqs`. So it does not resolve conversational↔worker (which needs a *different* shape, not a
*paused/woken same* shape). Its legitimate home is the **model-swap axis**: e.g. `@interaction` (4B-FP8) ↔
`@quality-9b` (9B-FP8) — sleep the 4B, wake the 9B, instead of evict+reload. **Mark: flagged broken on some
models since 0.14 (anchor §6); a sibling agent owns verification on OUR model. Do NOT design the loadout layer
to depend on it** — order-aware evict+bring-up (what `apply_loadout` does today) is the working fallback.

### Verdict (my recommendation, evidence-grounded)

**(a), reframed: two DECLARED loadouts of the same model, with COMPUTED (not hand-typed) budgets.** This is
the only option that satisfies the opposite-co-residency constraint, respects the init-time concurrency reality,
and stays faithful to "the 50% has gotta go." (b) is a within-loadout latency tool (keep it — see §3 priority).
(c) is a model-swap-axis tool (park it on that axis, verify-not-trust).

---

## 3 · The DESIGN — where each intent param declares, and the resolution-home map

The high-value deliverable: each resource-intent param resolves through a **different existing spine**. They do
NOT all belong in one place — and pretending they do is a trap. Here is the honest mapping, grounded in code:

| Intent param | Declares as | Resolution home | Emitted how | Status today |
|---|---|---|---|---|
| **KV budget (bytes)** | NOT declared — **computed** | `gpu.auto_gpu_util` / a new `kv_budget_bytes(reg,key,shape)` | `--kv-cache-memory-bytes` (replaces `--gpu-memory-utilization`) | budget computed as a *fraction* today (`gpu.py:48`); the absolute-bytes flag is NOT yet a capability row — **gap** |
| **concurrency** (`max_num_seqs`) | **shape-intent on the loadout** | feeds BOTH the budget math (`per_seq_mb × max_num_seqs`, `gpu.py:78`) AND its own flag | `--max-num-seqs` (`serveconfig.py:86`) | a raw `config` field, emitted directly — NOT loadout-carried — **gap** |
| **context** (`max_model_len`) | **shape-intent on the loadout** | feeds the KV budget (`kv_kb_per_token × max_model_len`, `gpu.py:71`) AND its own flag | `--max-model-len` (`serveconfig.py:84`) | raw `config` field — **gap** |
| **cache dtype** (fp8 KV) | per-model `capability_override` | resolver enum `serve_values` | `--kv-cache-dtype fp8` | **DONE** — `capability_types.json:119` + `chat-4b-fp8.config.capability_overrides.kv_cache_dtype` |
| **priority scheduling** | serve-flag toggle (loadout-level) | NEW capability row, mirror `kv_cache_dtype` | `--scheduling-policy priority` | NOT a capability row yet — **gap** (named SCOPE:50) |
| **kv-offload to RAM** | serve-flag toggle | NEW capability row | `--kv-offloading-size N` | NOT a capability row yet — **gap** (SCOPE:49) |
| **enforce-eager** | family attribute / toggle | EXISTING capability row | `--enforce-eager` | **DONE** as a row (`capability_types.json:23`) — used by nemotron; reusable by any loadout |
| **sleep-eligible** | loadout flag (model-swap axis) | `--enable-sleep-mode` capability row + the switch logic | `--enable-sleep-mode` | NOT wired — **gap**, verify-first |

### 3.1 · The serve-flag toggles → capability rows (mirror the pattern that already works)

**Observed:** `kv_cache_dtype` and `vision` already prove the exact pattern the new flags should follow — an
**enum/bool capability-type row** with `serve_values`, resolved into a serve fragment:
- `capability_types.json:119` `kv_cache_dtype` (enum, `serve_values: {fp8: kv_cache_dtype_fp8, auto: null}`)
- `stack_capabilities.json:48` `kv_cache_dtype_fp8 → ["--kv-cache-dtype","fp8"]`
- `chat-4b-fp8.config.capability_overrides: {kv_cache_dtype: "fp8"}` (Observed in the live config)

So **`priority`, `kv_offload`, `sleep_mode`, `enforce_eager(reuse)` should each become a capability-type row +
a `vllm`-stack serve fragment** — exactly like `kv_cache_dtype`. Adding one is registry-is-truth: one row in
`capability_types.json` + one fragment in `stack_capabilities.json`, no code edit (Observed: the resolver loads
them at import + `reload_registries`, `resolver.py:92`). Example for priority:
```jsonc
// capability_types.json
"scheduling_policy": { "value_shape": "enum", "layer": "field", "order": 8,
  "serve_ref": "scheduling_policy",
  "serve_values": {"priority": "scheduling_policy_priority", "fcfs": null} }
// stack_capabilities.json under "vllm"
"scheduling_policy_priority": { "serve": ["--scheduling-policy", "priority"], "use": "send body.priority per request" }
```
**This is the answer to the anchor's question "is `runtime/capabilities/` where per-loadout serve params should
declare?" — YES for the serve-FLAG toggles (priority/offload/sleep/dtype/eager), via the proven enum/bool row +
`serve_values` mechanism. NO for budget/concurrency/context** (see §3.2 — they feed *budget math* in gpu.py, not
just a flag).

### 3.2 · The honest "yes, but…" — shape-intent is NOT purely a capability

The resolver (`serve_flags`) emits launch **flags**. But concurrency + context + budget also feed the **budget
MATH** in `gpu.py` (`auto_gpu_util` reads `max_model_len`, `max_num_seqs`, `per_seq_mb`). So the loadout-shape
layer **cannot live purely in `runtime/capabilities/`** — a `max_num_seqs` value is both (i) a `--max-num-seqs`
flag and (ii) an input to `per_seq_mb × max_num_seqs` in the VRAM budget. **Mark: I am explicitly saying the
capability resolver is the wrong sole home for shape-intent.** The clean split:
- **serve-flag toggles** (priority, offload, sleep, dtype, eager) → capability rows (resolver-emitted). ✅
- **sizing shape-intent** (max_num_seqs, max_model_len, kv_budget) → a **per-service shape block** that BOTH
  `gpu.py` (budget compute) AND `serveconfig.py` (flag emit) read. This is the genuinely new layer.

---

## 4 · Where the SHAPE attaches — the new primitive (carry it on the combo)

The combo is the natural home because the SHAPE is **per-loadout**, not per-model. Proposed (My-idea, marked
tentative): a combo may declare a **`shape` map keyed by service**, overlaid on the service's base `config`:

```jsonc
// services.json combos (My-idea — the missing per-service shape layer)
"extract": {
  "services": ["chat-4b-fp8"],          // SOLO — embedder/voice not in the set (the co-residency difference)
  "shape": {
    "chat-4b-fp8": { "max_num_seqs": 32, "max_model_len": 16384 }   // worker shape-INTENT: small window, high concurrency
  },
  "note": "the @extract worker loadout — high-concurrency bulk audit, solo on the card. SMALL max_model_len is load-bearing: auto_gpu_util's KV term is kv_kb_per_token × max_model_len (independent of concurrency), so a deep-context worker (65K) would NOT shrink the KV pool — 32-concurrency × a small 16K window is the whole point of the worker shape (SCOPE:74 'small window + high concurrency')."
},
"interaction": {
  "services": ["embed-pplx", "chat-4b-fp8", "rerank-jina", "stt-moonshine", "tts-kokoro"],
  "shape": {
    "chat-4b-fp8": { "max_num_seqs": 2, "max_model_len": 65536 }    // conversational shape-INTENT
  }
}
```
Critically: **only the shape-INTENT is declared; the budget is COMPUTED.** `gpu.auto_gpu_util` already turns
`max_num_seqs` + `max_model_len` + `_profile` into a fraction (and, in this rework, into
`--kv-cache-memory-bytes`). So `@extract`'s ~0.9 and `@interaction`'s ~0.44 would be **derived, never typed** — the
direct answer to "two loadouts with different *computed* budgets." This honours "the 50% has gotta go" at the
LOADOUT layer, exactly as the brain layer already does it per-service.

**Honesty caveat (Observed):** chat-4b-fp8 has **`_profile: null` TODAY** — its live config carries a static
`gpu_util: 0.9` and no `_profile` (verified in the dumped config). So `auto_gpu_util(reg,"chat-4b-fp8")` returns
`None` right now (`gpu.py:69`), and these budgets are NOT yet computable for THIS brain — they become derived
only once the profiler sibling-area populates chat-4b-fp8's `_profile` (the gap SCOPE:49/85 names). The shape
LAYER (this area) is buildable independently; the *computed-budget* half waits on that profile. I present the
mechanism, not a live claim for this brain.

**Why on the combo, not a second service key?** A second service key (`chat-4b-fp8-worker` pointing at the same
model/port) would duplicate the family/overrides/profile (drift risk) AND collide on port :8001 (Observed:
`registry.shared_ports`, `registry.py:142`). The shape OVERLAY keeps ONE service (one `_profile`, one family,
one port) and varies only the load-time sizing — registry-is-truth, no duplication. **Contrast with the
SET grammar:** `add/remove/swap` change WHICH services; `shape` changes HOW a service in the set is sized. Two
orthogonal axes, both on the combo.

### 4.1 · The wiring chain that must carry `shape` (every link is a gap today)

```
combo.shape[key]                              # NEW — declared on the combo
  → suite.apply_loadout: pass shape into…     # suite.py:2752 — passes only the key today
      ensure_resident(key, shape=…)           # capabilities.py:430 — no shape param today
        → start path must export the shape     # serve_model.sh reads serveconfig
          → serveconfig.args_for(key, shape=…) # serveconfig.py:79 — reads only config today
            → max_num_seqs/max_model_len ← shape override config
            → _resolved budget ← gpu.kv_budget_bytes(reg,key,shape)  # gpu.py — uses config max_num_seqs today
```
**Observed: NONE of `apply_loadout` / `ensure_resident` / `args_for` / `auto_gpu_util` take a shape param.**
They are all keyed by the service key alone (verified by reading each signature). So the build work is precisely:
thread an optional `shape` dict from the combo down this chain, with the base `config` as the default when a
combo declares no shape (so every existing combo behaves byte-identically — no regression).

**BLOCKING SUB-GAP — `ensure_resident`'s no-op short-circuit ignores shape, so threading `shape` is necessary
but NOT sufficient.** Observed (`capabilities.py:467-471`): step 1 is "ALREADY RESIDENT → no-op," and it returns
*before* any fit/evict/reload logic, **regardless of `evict=True`.** Trace the failure: when `apply_loadout(@extract)`
calls `ensure_resident("chat-4b-fp8", evict=True)` and the brain is already up in the *conversational* 2-seq shape,
`ensure_resident` sees the key in `running_gpu_services`, returns `already-resident`, and **never reloads** — the
declared worker shape is silently dropped. `_repoint_rhm_for_loadout` then sees the same model/port, the verify
probe passes, no reload happens. So a shared-service-key overlay (§4) cannot actually reshape unless
`ensure_resident` gains a NEW branch: **"resident BUT declared-shape ≠ live-shape → teardown + reload at the new
shape"** (a reshape IS a reload, §2). This is the no-silent-degrade law applied to the actuator itself, and
`ensure_resident` is a named target of this rework — it must change, not just be passed a param. (It needs the
live shape readable — see §9 open thread on reading the resident `max_num_seqs`.)

### 4.2 · Resolution-first alternative (stronger, My-idea — flag for the synthesis)

Rather than a free-form `shape` overlay, the shape could be a **typed `loadout_shape` registry** (mirrors the
capability registries): named shapes `conversational` / `worker` with declared `max_num_seqs` / `max_model_len`
/ priority, and a combo `requires_shape: worker`. This makes the two shapes **first-class typed rows** (Tim's
resolution-first / registry-is-truth law — see memory `feedback-resolution-first-compositional`), reusable
across loadouts, and validated centrally. Trade-off: a free-form overlay is simpler to wire and matches the
combo's current `note`/`swap` style; the typed registry is more aligned with the capability-resolution spine
this whole rework extends. **I lean typed** (it's the same move as `family`/`capability_types`), but flag it for
the synthesis to weigh against build cost.

---

## 5 · How resource-intent flows through the switch + gate (Observed, end-to-end)

**Observed (`suite.py:2643-2663` `_resolve_loadout`):** resolves a loadout_class → `(services, missing)` by
checking `_gpu._is_running` per service. **Resource shape never enters here today** — it only checks presence.

**Observed (`_gate_work_requires`, `suite.py:2665-2697`):** work declares `requires: <loadout>`; if any service
is missing, it surfaces a `loadout_swap` confirm and FAILS LOUD (no silent degrade). The gate is **presence-only**
— it does not check that the resident brain has the right SHAPE for the work. **Gap / risk:** if `@extract`
shares the service key `chat-4b-fp8` with `@interaction`, and the brain is resident in the *conversational*
2-seq shape, `_resolve_loadout("extract")` sees the key running and reports "resident" — **it would pass the gate
while the brain is in the WRONG shape** (2-seq, not 32-seq). With the shape layer, `_resolve_loadout` must also
verify the **resident shape matches the loadout's declared shape**, else surface the swap (a reshape = a reload,
§2). This is the no-silent-degrade law applied to SHAPE, not just presence. **I recommend `_resolve_loadout`
gain a shape-match check** as part of this rework. **The SAME blindness sits one layer deeper in the actuator**
(`ensure_resident`'s already-resident no-op, §4.1 BLOCKING sub-gap) — so shape-match must be enforced at BOTH
the gate (don't claim resident when shape differs) AND the actuator (reload when shape differs), or the reshape
silently no-ops.

**Observed (`apply_loadout`, `suite.py:2726-2763`):** the ONE actuator — reads `payload.services`, captures the
prior brain pointer, `ensure_resident(s, evict=True)` per service, then `_repoint_rhm_for_loadout` repoints +
verify-probes + reverts. **This is where shape must be passed in** (`ensure_resident(s, shape=combo.shape.get(s))`).
The eviction it already does (SCOPE: embedder/voice evicted for `@extract`) is exactly the co-residency swap (b)
cannot do — confirming (a) is the architecture's grain.

**Observed (`_repoint_rhm_for_loadout`, `suite.py:2772+`):** points the RHM at the loadout's OWN brain
(`_brain_in_loadout` — registry-is-truth, the brain NAMED in the set, not `brain_keys[0]`), verified by a live
inference probe, reverting on regression. Shape does not change the repoint logic (same model id, same port) —
so the shape layer is **orthogonal to the repoint** and does not disturb the atomic-switch guarantee.

**Observed (`ensure_resident`, `capabilities.py:430-549`):** the gated actuator — `check_fit` (VRAM) +
`ram_fit` (live MemAvailable) + `plan_eviction`, fail-loud, never OOM. The **computed budget** (`budget_vram`,
`gpu.py:86`) flows in HERE via `check_fit`. Today `budget_vram` reads the service's `config` (static gpu_util OR
auto from `_profile` using `config.max_num_seqs`). With the shape layer, the budget must be computed from the
**loadout's shape** (its `max_num_seqs`), so `@extract`'s 32-seq reservation is gated correctly and `@interaction`'s
2-seq fits co-resident. **This is the single place the per-loadout computed budget becomes a fit decision** —
the `_profile` + computed budget feeding bring-up that the anchor §7/SCOPE asks about.

---

## 6 · `_profile` + computed budget feeding a loadout's bring-up so the SET fits

**Observed:** `auto_gpu_util` (`gpu.py:48-83`) already computes
`need = fixed + (kv_kb_per_token × max_model_len/1024) + per_seq_mb × max_num_seqs + overhead`, `frac = need /
ceiling`. **It reads `max_num_seqs` from `config` (`gpu.py:78`).** For per-loadout budgets this must read the
**loadout's shape** instead. Then:
- `@interaction`: 2 seqs × 34 MiB ≈ 68 MiB per-seq + KV(65K) → small fraction → fits co-resident with embedder.
- `@extract`: 32 seqs × 34 MiB ≈ 1.09 GiB per-seq + KV → large fraction → needs solo (the eviction the swap does).

**The keystone improvement (from the anchor, SCOPE:41/47):** emit `--kv-cache-memory-bytes` (absolute) instead
of `--gpu-memory-utilization` (fraction), paired with `--enforce-eager`. **Why this matters for the LOADOUT
layer specifically:** the co-resident OOM (anchor §1: KV −3.78 GiB at gpu_util 0.5 with the embedder up) is the
fraction-of-TOTAL-card semantics counting the embedder against vLLM's budget. An absolute byte budget computed
from the loadout's shape pins the steady state regardless of what else is on the card — **making the load ORDER
within a loadout stop mattering** (the anchor's central bet). The loadout shape feeds the byte budget; the byte
budget makes the co-residency robust. **NOTE: the budget MATH + the `--kv-cache-memory-bytes` profiler work are
SIBLING-AGENT areas (anchor §6 honest hard parts: per-seq 34 vs 49.5, hybrid pool over-prediction, cuda-graph
blind spot). I reference, do not own them.** My area owns: the shape-intent declaration + how it threads to that
math.

---

## 7 · Multi-actor selection (anchor §2, SCOPE:18) — builds on what exists

**Observed:** the selection spine already exists — `_maybe_surface_loadout_swap(mode)` (`suite.py:2699`) binds a
MODE to a `loadout_class` and surfaces the swap; `_gate_work_requires` lets WORK declare `requires: <loadout>`;
`apply_loadout(sid)` actuates on operator approve (never self-approve). So the three actors map cleanly:
- **Tim / operator** → approves the surfaced `loadout_swap` (the inbox confirm). Already built.
- **MCP agents** → `requires: <loadout>` on a cascade/action (the work declares its shape — exactly the anchor's
  "the work picks its shape"). Already built; with the shape layer, "the loadout" now carries the brain shape too.
- **RHM** → the mode→loadout binding (`mode_registry(mode).loadout_class`). Already built.

**My-idea (extension):** with the shape layer, the *worker* selection becomes natural — a bulk-audit cascade
declares `requires: extract`, the gate sees the brain is in the wrong shape (2-seq, §5 risk), surfaces a swap,
operator approves, `apply_loadout` reshapes (evict embedder + reload brain at 32-seq), runs the audit, then a
follow-up `requires: interaction` restores the conversational shape. The whole worker/conversational dance
becomes **two declared loadouts selected by the work**, no hand-edit — which is the SCOPE:74 phase-5 goal
(`@extract` as a DECLARED loadout) finally closeable.

---

## 8 · Contradictions / corrections to the anchor (the gold)

1. **My-idea #4 ("two loadouts … but maybe sleep-mode or a second instance is better; unknown") — RESOLVED:**
   it's two loadouts, and the reasons sleep-mode/second-instance LOSE are concrete (opposite co-residency;
   init-time concurrency; port collision; profile duplication). Not "unknown" — decided, with evidence.
2. **§8 "Can one model serve both shapes live (priority + chunked prefill)?" — NO, and the framing conflates two
   axes.** Priority/chunked-prefill = latency-scheduling WITHIN a fixed shape (keep them as in-loadout tools);
   they do not reshape concurrency or change co-residency. The decisive blocker is co-residency, not the Mamba toll.
3. **The anchor never names the actual gap:** a combo carries NO per-service shape. "Two computed budgets" is
   impossible until a shape layer is added — this is the real build target, and it's purely in this area's lane.
4. **`runtime/capabilities/` is the right home for serve-FLAG toggles (priority/offload/sleep/dtype/eager) but the
   WRONG sole home for sizing shape** (it feeds budget math in gpu.py, not just flags). The shape layer straddles
   both — say so plainly.
5. **Presence-vs-shape blindness lives at TWO layers, both in this lane:** the `requires`-gate /
   `_resolve_loadout` (presence-only — passes work against a wrong-shaped brain) AND `ensure_resident`'s
   already-resident no-op (`capabilities.py:467-471`, returns before any reload even with `evict=True` — silently
   drops the declared shape). Threading a `shape` param is necessary but NOT sufficient; both must gain a
   shape-match → reload branch (no-silent-degrade applied to shape). This is the load-bearing build correction.

---

## 9 · Open threads for the synthesis (honest unknowns in this lane)

- **Free-form `shape` overlay vs typed `loadout_shape` registry** (§4.2) — I lean typed (resolution-first), but
  it's a build-cost call for the synthesis.
- **Shape-match in `_resolve_loadout`** (§5) — needs the resident brain to report its live `max_num_seqs`. Is
  that readable from the running vLLM (`/v1/models` / a metrics endpoint), or must we record "what shape we
  started it in" as session state? (External — unverified; a profiler-area question too.)
- **Does the absolute byte budget truly make load-order irrelevant for the NON-vLLM co-tenants** (embed-pplx,
  kokoro)? They honor no vLLM budget (anchor §6) — so even with the shape layer, `@interaction` bring-up ORDER
  may still matter. (Sibling-area: the budget/profiler agents.) My lane just needs the shape to flow; whether
  order can be ignored is theirs.
- **Sleep-mode on OUR chat-4b-fp8** (model-swap axis, §2c) — sibling-area verification; if it works, the
  4B↔9B swap (`@interaction ↔ @quality-9b`) gains a `sleep_eligible` loadout flag instead of evict+reload.

---

## Sources (External)
- vLLM `max_num_seqs` semantics (init-time cap, KV-pool allocated at engine init; no runtime-reconfigure API found):
  [vLLM issue #5634](https://github.com/vllm-project/vllm/issues/5634),
  [issue #6641](https://github.com/vllm-project/vllm/issues/6641),
  [vLLM forum: understanding max-num-seqs](https://discuss.vllm.ai/t/to-understand-max-num-seqs-better/2609).
- vLLM 0.21 flags (`--kv-cache-memory-bytes`, `--scheduling-policy`, `--enable-sleep-mode`, `--kv-offloading-size`,
  `--enforce-eager`): VERIFIED-present per the prior research artefact `.data/unify-exercise/gpu-autoprofiler-research.html`
  and SCOPE:53 (not re-fetched this pass; sibling capability-map area owns deep flag verification).
