# R2 · Resource Math — Can the resident 4B run a worthwhile swarm at the voice config?

*Round-2 deep review, quantitative. Validates R1-FOLD F1 (the central risk) against the **real** config + **measured** KV numbers. Read-only. All figures traced to `ops/services.json` (`chat-4b.config` + `_profile`), `~/vllm-tests/BENCHMARK_FACTSHEET.md`, the 2026-06-07 co-residence measurements in memory, and `ops/cli/gpu.py`.*

---

## TL;DR — the verdict

**"Concurrency beats size" SURVIVES at this hardware — but NOT at the literal 64K voice-brain config. It needs a dedicated swarm-mode config (higher `gpu_util` + a short main context + short roles).** The binding constraint is **not** `max_num_seqs=16` — it is the **shared KV pool**, which at `util 0.49` is only **~2.13 GB (~70.6K tokens total)**. The 64K `max_model_len` is the killer: one full 64K main context consumes ~93% of that pool by itself. The fix is a config lever Tim already owns (`company config chat-4b gpu_util/max_model_len/max_num_seqs`), not a hardware wall.

---

## 1. The measured inputs (no speculation)

**Observed** in `ops/services.json`:
- `vram_ceiling_mb = 16376` (the 16 GB card)
- `chat-4b.config`: `gpu_util = 0.49`, `max_model_len = 65536`, `max_num_seqs = 16`
- `chat-4b.config._profile` (measured 2026-06-07): `fixed_mb = 5838` (weights+activations+cudagraphs), `kv_kb_per_token = 31.7`, from a **256K solo run: KV 8.37 GiB / 270,482 tokens**.

**Verified** the KV-per-token figure: `8.37 GiB × 1024² / 270,482 = 32.45 KB/tok` raw → registry's `31.7` is the corroborated effective figure (the small gap is block/overhead rounding). **I treat 31.7 KB/tok as ground truth.**

**Observed** in `ops/cli/gpu.py`: `budget_vram()` reserves `gpu_util × ceiling` for a config-driven model — i.e. `gpu_util` IS the literal VRAM slice vLLM carves, and the KV pool is *that slice minus the fixed weights*. This is the authority the resource manager already uses.

---

## 2. The KV pool at the voice config (util 0.49)

```
4B reservation   = 0.49 × 16376      = 8024 MB  (7.84 GB)
  − fixed (weights+graphs)            = 5838 MB
  = KV pool                           = 2186 MB  (2.13 GB)
  ÷ 31.7 KB/tok                       = ~70,600 tokens  (TOTAL the pool can ever hold)
```

**This is the whole story in one line:** the pool backs **~70K tokens total**. So it is *either* **16 sequences × ~4.4K tokens each** *or* **1 sequence × 64K** — never both. `max_num_seqs=16`, `max_model_len=65536`, and `util 0.49` are **mutually inconsistent for a wide swarm**. R1-FOLD F1 was right that 32 is impossible; the real number depends entirely on how much of the pool the main stream pins.

**Co-residence fits** (this part is fine): `4B(8024) + qwen3tts(4500) = 12,524 MB` → ~3.85 GB headroom; Kokoro leaves ~7.45 GB; even orpheus (util 0.32 → 5240 MB) co-resides at 0.49+0.32=0.81 with ~3.1 GB spare. **The card is not the bottleneck — the KV partition inside the 4B's own slice is.**

---

## 3. Real usable swarm width — the decisive fork

The width is `N = (KV_pool − main_ctx·kv) / (role_ctx·kv)`, then **capped at `max_num_seqs − R`** (R = slots reserved for main/judge). What `main_ctx` is depends on **whether a main request is in flight while the swarm runs** — and the design says **it can be** (C0.5: "with a staged main reply running"; C6.1: "synth part N while the brain generates part N+1"). So both rows are real:

| Main context resident during swarm | role 1K | role 2K | role 4K |
|---|---|---|---|
| **8K** (short main) | 16 (cap) | 16 (cap) | 16 (cap) |
| **16K** | 16 (cap) | 16 (cap) | **14** |
| **32K** | 16 (cap) | 16 (cap) | **10** |
| **64K** (full voice brain) | **5** | **3** | **1** |

*(KV-fit before the seq-cap, util 0.49. The 64K row is the literal voice config's worst case.)*

**The reading:** with the 64K main context resident, the swarm collapses to **1–5** — the main stream alone eats 1.98 GB of the 2.13 GB pool. Cap the main context to **≤16K** and the swarm returns to the **seq-bound 16** at realistic short-role sizes (1–2K). **Width is governed by the main-context budget, not by `max_num_seqs`.**

**Temporal nuance (don't over-claim the collapse):** parts are sequential. In the *between-parts* window, the prior part's request has completed and vLLM can reclaim its KV blocks — so a swarm that runs strictly between parts can use ~the full pool (→ 16-cap even with a 64K brain). The cost then moves to **Part-2 re-prefill** of the main context, which IS the inter-part wall-clock C0.5 must measure (see §5). The 1–5 collapse is the *overlap* case (swarm fired while Part-1 is still generating with a large base context) — which the design explicitly wants for latency-hiding. So the honest statement is a **trade: swarm width ⟷ main-context-resident-during-overlap**, not a flat hardware floor.

---

## 4. The lever: a swarm-mode brain config (util is unpriced headroom)

At util 0.49 + a light TTS, **~3.8–7.5 GB sits idle on the card.** Raising `gpu_util` for swarm-heavy modes roughly multiplies the KV pool (still co-resident with qwen3tts @ 4.5 GB):

| `gpu_util` | KV pool | total KV tokens | +qwen3tts headroom |
|---|---|---|---|
| 0.49 (voice default) | 2186 MB | ~70.6K | 3852 MB |
| 0.55 | 3169 MB | ~102K | 2869 MB |
| 0.60 | 3988 MB | ~129K | 2050 MB |
| 0.66 | 4970 MB | ~161K | 1068 MB |
| 0.72 | 5953 MB | ~192K | 85 MB (tight) |

**Recommended swarm-mode config:** `gpu_util 0.60–0.66`, `max_model_len ~16384`, `max_num_seqs 16`. At util 0.66 the pool holds ~161K tokens, so even with a 16K main context resident, **16 roles × 1.5–2K each fit comfortably** (16K main = 0.49 GB; 16 × 2K = 0.97 GB; total 1.46 GB ≪ 4.97 GB pool). The seq-cap (16), not KV, becomes the binding limit — exactly where you want it.

---

## 5. Inter-part wall-clock (the other half of C0.5)

From the factsheet: per-request decode is **~100 tok/s** steady; prefill is sublinear (4K=0.40s, 16K=0.70s, 30K=1.07s). Two costs feed the inter-part stall:
- **Slowest dependency role** in a wave: a 1–2K-context role producing a small JSON ≈ 0.4–0.7s TTFT + short decode → **sub-second** per wave.
- **Part-N re-prefill** when the main context grows: re-prefilling 16K ≈ 0.7s. **Prefix caching defuses most of it** — the multi-turn table shows 40–110ms TTFT when the prior context is cached, so only the *newly injected* role-output tokens re-prefill, not the whole context. Keeping the main base context stable (append-only injection) is therefore a hard design requirement for the latency story to hold.
- **JSON validate/retry** (C1.4): client-side enforcement (`client.py`) means a malformed draw costs one extra full role round-trip — budget +0.5–0.7s per retry into the inter-part number.

---

## 6. Design implications

1. **The swarm width number for C1.2's semaphore is `min(16 − R, KV_pool/kv − main_ctx/kv ÷ role_ctx)`** — exactly R1-FOLD's formula, now with concrete inputs: at util 0.49 it is **~12–16 for short roles, but only 1–5 if the 64K main is resident during overlap.** The semaphore MUST read live `gpu_util`, `max_model_len`, `max_num_seqs` and the `_profile` KV figure from the registry (all present) — never a constant.
2. **A leaner brain config IS needed for swarm-heavy modes.** The 64K voice brain and a wide concurrent swarm cannot share one 2.13 GB pool. Resolution options, in preference order: (a) a **mode-bound swarm config** (`util 0.60–0.66`, `max_model_len 16K`) that `company config`/`company swap` selects when a staging mode activates; (b) keep 64K but **cap the main-context-resident-during-overlap** to ≤16K (run the swarm between parts, accept Part-2 re-prefill); (c) accept a narrow (2–5) overlap swarm at the literal voice config for short modes. Mode = the attention budget already chooses this (per `project-concurrent-cognition`).
3. **Roles MUST be short-context** (≤2K prompt+output). A single 4K role costs ~124 MB — three of them at 64K-main leave nothing. This is a registry-enforced contract, not a guideline.
4. **C0.5 is correctly the gate.** This math is the *predicted* answer; the spike must MEASURE it on the live config with qwen3tts resident, because effective KV block allocation, preemption thresholds, and prefix-cache hit-rate are vLLM-internal and only the running system produces the true knee. **Predicted realistic usable width: ~12–16 with a swarm-mode config and short roles; ~2–5 at the literal 64K-voice-brain under overlap.**

**Bottom line:** "concurrency beats size" is true at this hardware *only* with a swarm-mode config (higher util, short main, short roles). At the literal 64K voice brain with a full main context in flight, the swarm narrows to 2–5. The fix is a config lever Tim already controls — so the architecture holds, but the build must treat the swarm-mode brain config as a first-class, mode-selected artifact, not an afterthought.
