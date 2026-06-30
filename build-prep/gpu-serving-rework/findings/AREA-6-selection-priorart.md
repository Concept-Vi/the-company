---
type: research-finding
register: descriptive
area: "AREA-6 — the selection interface (multi-actor) + the prior-art frame"
aliases: ["Loadout Selection Surface", "Adopt-vs-Build Router Verdict", "Multi-Actor Loadout Selection"]
tags: [gpu, vllm, loadout, selection, mcp, rhm, cli, llama-swap, llmsnap, litellm, sleep-mode, prior-art, research-wave]
status: unconfirmed
coverage: {captured_from: "research-wave 2026-06-30", grounded_in: "ops/cli/app.py · mcp_face/server.py · runtime/bridge.py · runtime/suite.py · ops/cli/gpu.py · ops/services.json · web (llama-swap/LLMSnap/LiteLLM/vLLM sleep-mode)", note: "design + grounded verdict; NOT a build"}
---

# AREA-6 — The selection interface (multi-actor) + the prior-art frame

## 0 · Bottom line up front (the synthesis agent can stop here)

**The verdict is unambiguous: BUILD the thin selection layer on the spine that already exists; ADOPT vLLM's in-engine built-ins (sleep-mode, priority, kv-cache-memory-bytes); ADOPT NO external proxy wholesale.**

Per tool, one line each:
- **llama-swap** — *do NOT adopt as the runtime.* Its per-model VRAM control IS `gpu_memory_utilization` (External, its own docs) — **the exact hand-set fraction Tim said "has gotta go"** (SCOPE:15). Mine its `groups`/`swap:true` coexistence DSL as a *design reference* for the loadout shape Company already has (combos + extends/swap/add/remove variants). Reference, not dependency.
- **LLMSnap** (napmany/llmsnap, a llama-swap fork) — *do NOT adopt the proxy.* It is the reference *implementation* of sleep/wake orchestration over vLLM sleep-mode. Adopt the underlying **vLLM `--enable-sleep-mode` built-in directly** (reach-for-the-stack), wired into Company's own `apply_loadout` switch — not the Go wrapper. 48 stars, 5 releases, latest Apr 2026 (External) — too thin to depend on anyway.
- **LiteLLM** — *redundant.* A front-door router. `run_role` already resolves `base_url` from the model id (the ollama-vs-vLLM split, mcp_face/server.py:747-759, Observed). No gap it fills that the existing model→endpoint resolution doesn't.

**The reason no proxy adopts cleanly:** they are *front-door proxies that OWN start/stop/swap* keyed off the request's `model` field. Company's lifecycle is **systemd units + the resource manager** (`check_fit`/`plan_eviction`/`ram_fit`, app.py:120-165, Observed) + telemetry + the WS-R RAM-leg. Put a proxy in front and either (a) it owns lifecycle and you lose the RAM-gate / eviction / telemetry / systemd accounting, or (b) you keep systemd and the proxy degrades to a dumb router = LiteLLM, redundant. **There is no clean wholesale-adopt seam.** (My-idea, grounded in the code below.)

**What to actually build:** three faces of ONE resolution spine that already half-exists, plus closing two real visibility/parity gaps I verified in the code (§4).

---

## 1 · The spine that already exists (the thing all three actors funnel into)

This is the most important grounding the anchor under-states. There is **already a one-resolver spine** for "work declares the loadout it needs → resolve → confirm/switch." The selection surfaces are three FACES of it, not three systems.

The spine (all Observed):
```
DECLARE/SELECT  →  _resolve_loadout(class)        suite.py:2643  (combos table → services, missing)
                →  residency check                 suite.py:2675-2681
   resident?  ──yes──→  proceed silently
              ──no───→  inbox.surface("loadout_swap", …)   suite.py:2688  (RAISE the confirm)
                   →  operator APPROVES (read from inbox, never a caller flag)   suite.py:2736
                   →  apply_loadout(sid)            suite.py:2726
                        → ensure_resident(s, evict=True)  per service  suite.py:2753  (the ONE gated actuator; WS-R RAM+VRAM invariant)
                        → _repoint_rhm_for_loadout(...)   suite.py:2772  (verify-by-probe + revert — dissolves the broken-brain class)
```

The **floor** is the load-bearing invariant: `apply_loadout` reads approval FROM the inbox (`inbox.is_approved(sid)`, suite.py:2736) — *the autonomous loop / RHM can RAISE the confirm but can NEVER self-approve it* (suite.py:2728, GovernanceError on unapproved). Every selection face must preserve this: an actor *selects/declares/raises*; the operator *approves*; `apply_loadout` *actuates*. (Observed.)

The combos table (`ops/services.json` → `combos`, Observed) IS the loadout registry today: `interaction`, `interaction-fp8`, `interaction-parakeet`, `quality-9b`, `xsession`, `instrument`, `wake`, `small-pair`, `xsession-brain`, `wake`. The `extends/swap/add/remove` variant mechanism (services.json:7) is exactly llama-swap's groups-DSL aspiration, already shipped — a "loadout class" = a base combo + its variants, resolved centrally by `registry.combos()` (fail-loud on missing base / bad swap target / extends-cycle).

**So: the loadout registry, the resolver, the confirm/approve gate, the gated actuator, and the RHM repoint all exist.** AREA-6's build is the *selection FACE* for each actor + closing the visibility gaps — not a new mechanism.

---

## 2 · The three actors — what each SEES and SELECTS (the design)

### 2.1 Tim (visible + selectable) — extends `company combos` / `company up @loadout`

**What he has today (Observed):**
- `company combos` (app.py:256) lists every runnable combination with its note + an `⚠ EXCEEDS HARDWARE` flag from `validate_combo_capacity` (app.py:263). This IS the loadout menu for Tim.
- `company up @loadout` (app.py:333,347) brings the set up through the resource manager, then `_repoint_loadout_brain` (app.py:88) repoints the RHM via the bridge. The atomic switch + revert is built.
- He approves a surfaced `loadout_swap` (the inbox card the FE renders).

**What's naive about the anchor here:** it says "Tim sees + selects loadouts" as if new. He already does. The gap is **ergonomics, not existence** — `company combos` prints service keys + free-text notes, not *the shape in his units*. (See §5 — units.)

**The thin build (My-idea):** enrich `company combos` (and a new `company combos <name>` drill-down) to show, per loadout, the COMPUTED resource shape in Tim's terms, derived from `_profile` + live headroom — e.g.

```
@interaction-fp8   brain=chat-4b-fp8 · embedder · voice    [deep chat: 2 seqs × ~128K ctx]
                   fits: ~14.2 GB of 16 GB · headroom ~1.8 GB
@extract           brain=chat-4b-fp8 (solo)               [32-worker: 32 seqs × ~4K ctx]
                   fits: ~12.9 GB solo · embedder+voice EVICTED
```

This is a *render* over the existing `validate_combo_capacity` + `auto_gpu_util` (no new mechanism), translating bytes → "deep chat / 32-worker" + Tim's "N units fit" framing. It satisfies SCOPE:18 ("Tim … able to SEE and SELECT loadouts for jobs") at the altitude Tim works at.

### 2.2 The MCP agent (a tool param / a `requires` declaration) — TWO real gaps

**What an agent has today (Observed):**
- It declares `requires: <loadout>` on a **cascade/action** → `_gate_work_requires` (suite.py:2665, called at suite.py:1327) resolves the loadout, and if a service is missing, surfaces a `loadout_swap` confirm and **fails loud** (no silent degrade). Built this session (SCOPE:24). This is "the work declares its shape" for cascades — already real.
- `run_role` has `ensure` / `ensure_evict` (mcp_face/server.py:669) — but that ensures ONE model resident, not a loadout shape.

**GAP A (verified, concrete) — an agent CANNOT SEE the loadout menu over MCP.**
I grepped `mcp_face/` for `combos`/`loadout`: **zero hits.** `capabilities()` (suite.py:1496) exposes `node_types`, `models`, `modes`, `mode_directives`, `mode_registry` — **but NOT the combos/loadouts table.** (Observed — suite.py:1499-1535, grep empty.) So an agent that wants to declare `requires: @extract` has no MCP way to *discover that @extract exists* or what shape it is; it would have to invent the name (violating the "author from the registry, never invent" law that `capabilities()` itself states, server.py:294).
→ **Build:** a read tool / a `capabilities(section='loadouts')` section mirroring `company combos` — `{id, services, brain, note, shape: {seqs, ctx_units, fits_solo, evicts}}`. Registry-is-truth, generated from the same `registry.combos()` + `validate_combo_capacity` the CLI uses. This is the agent's "see" face; it's the missing precondition for "declare `requires`."

**GAP B (verified, a real seam to name) — requires-gating is asymmetric: cascades have it, `run_role` does not.**
`_gate_work_requires` is called for a **cascade** (suite.py:1327). A single `run_role` (server.py:669) only has `ensure`/`ensure_evict` for *one model* — it does NOT take a `requires: <loadout>` and route through the gate. So "the work declares its shape" is true for cascades but NOT for a one-off role fire. (Observed.)
→ **Design position (not over-engineered):** add an optional `requires: <loadout>` param to `run_role` that routes through the SAME `_gate_work_requires` before firing (reuse, never a parallel gate). A role's *model* need (`ensure`) and its *loadout-shape* need (`requires`) are different axes — `ensure` says "this one model must be up," `requires` says "this whole shape must be the resident loadout." Both can coexist; the loadout gate is the outer one. Flag this as the seam; the build is one delegation call, not a new system.

**The agent's SELECT verb, end-to-end:**
```
agent: capabilities(section='loadouts')         → sees @extract exists + its shape   [GAP A → build]
agent: run_cascade(requires='@extract', ...)     → _gate_work_requires resolves         [Observed]
        ├─ resident?  → runs
        └─ missing?   → surfaces loadout_swap + FAILS LOUD ("operator approves, re-run") [Observed: suite.py:2695]
operator: approves the inbox card
system: apply_loadout(sid) → ensure_resident + repoint                                  [Observed]
agent: re-runs → now resident → proceeds
```
The agent NEVER self-switches the loadout (it can't approve — the floor). It declares + retries. This is correct and already-enforced; AREA-6 only adds the *see* (GAP A) and the *run_role parity* (GAP B).

### 2.3 The RHM (a verb that RAISES, never self-approves)

**What's there (Observed):** the mode→loadout binding. A mode carries `brain_config` (the mode→loadout map, suite.py:2185,2386) and `set_mode` calls `_maybe_surface_loadout_swap(mode)` (suite.py:2640,2699) — switching a presence mode *surfaces* a loadout_swap confirm when the mode binds a `loadout_class` whose services aren't resident. The mode switch ALWAYS succeeds (a config write is free); the *resident-model change* waits for operator approval (suite.py:2636-2640). So the RHM already has a path: change mode → raise the swap.

**The RHM's design verb (My-idea, preserving the floor):** a first-class `select_loadout(loadout_class, for_work=…)` RHM/MCP verb that:
1. resolves the loadout (`_resolve_loadout`),
2. if resident → reports "ready, the shape is X" (a `say`-able line),
3. if missing → **surfaces a loadout_swap confirm and tells Tim out loud** (`say`, server.py:255) — "to run the 32-worker audit I need to evict the embedder + voice and go solo on the brain; approve the swap?" — then BLOCKS the work.

Critically the verb **raises, never actuates**: it routes to `inbox.surface` + `say`, never to `apply_loadout` directly (that needs the read-from-inbox approval). This is the RHM analogue of the agent's `requires` and Tim's `company up @loadout` — the same spine, spoken. It also closes the *altitude* gap (Tim's "translate everything → human meaning"): the RHM says the shape in Tim's terms, not service keys.

---

## 3 · "The work declares its shape" — one table across the three faces

| Actor | SEE the menu | SELECT/DECLARE | gate | actuate |
|---|---|---|---|---|
| **Tim** | `company combos` (+ enriched shape render — build) | `company up @loadout` | resource-manager refuse/`--evict` (app.py:120) | `_act` + `_repoint_loadout_brain` (Observed) |
| **Agent** | `capabilities(section='loadouts')` **(GAP A — build)** | `requires:<loadout>` on cascade (Observed); on `run_role` **(GAP B — build, 1 delegation)** | `_gate_work_requires` → surface + fail-loud (Observed) | operator approves → `apply_loadout` (Observed) |
| **RHM** | `select_loadout(...)` resolve + `say` the shape (build) | `set_mode` → `brain_config` binding (Observed); or `select_loadout` verb (build) | `_maybe_surface_loadout_swap` (Observed) | operator approves → `apply_loadout` (Observed) |

Everything in the "actuate" column is ONE path: `apply_loadout` → `ensure_resident` (the gated actuator, WS-R RAM+VRAM invariant) → repoint (verify+revert). No actor gets a second actuator. The floor (RAISE-but-never-self-approve) is preserved on all three faces. (Observed across suite.py:2726-2795, app.py:88-117.)

---

## 4 · The verified gaps (what's actually missing — the build list for this area)

1. **GAP A — loadouts invisible over MCP.** `capabilities()` omits combos; `mcp_face/` has zero `combos`/`loadout` references. Build a `loadouts` capability section / read tool. *(Verified: grep empty + suite.py:1499-1535.)* — the agent's "see" face.
2. **GAP B — `run_role` has no `requires` loadout-gate** (cascades do, suite.py:1327; run_role doesn't, server.py:669). Add `requires:` param routing through `_gate_work_requires`. *(Verified.)* — work-declares-shape parity for single roles.
3. **Ergonomic render gap.** `company combos` + the menu show service keys + prose, not the COMPUTED shape in Tim's units. Build the shape-render over `auto_gpu_util`/`validate_combo_capacity`. — Tim's "see" altitude (§5).
4. **RHM `select_loadout` verb** — a raise-not-actuate verb that `say`s the shape. — the RHM's "select" face.

None of these is a new mechanism; each is a thin face/delegation over the existing spine. That is the whole AREA-6 build.

---

## 5 · Units / ergonomics — making selection MEANINGFUL (grounded in the real numbers)

The anchor's "1 unit = 16,384 tokens" (ANCHOR:26) is the right primitive, and it grounds cleanly against what `auto_gpu_util` ALREADY computes: `KV = kv_kb_per_token × max_model_len / 1024` (gpu.py:55-56, Observed). The MEASURED FP8 profile (SCOPE:32) gives the conversion: **1 unit (16,384 tok) ≈ 0.28 GiB per concurrent full-context seq.**

So a loadout's shape renders in Tim's terms directly from `_profile`:
- **`@interaction-fp8` = "deep chat"** → `max_num_seqs 2`, deep ctx (e.g. 128K = 8 units) → KV ≈ 2 × 8 × 0.28 ≈ **4.5 GB KV** on top of weights 5.67 GiB + embedder + voice. "2 concurrent deep conversations."
- **`@extract` = "32-worker"** → `max_num_seqs 32`, small ctx (4K ≈ 0.25 unit) → KV ≈ 32 × 0.25 × 0.28 ≈ **2.2 GB KV** + the per-seq Mamba toll (~34 MiB × 32 ≈ 1.1 GB, SCOPE:33) → fits SOLO ~487K-token shelf, embedder+voice EVICTED. "32 small extractions at once."

The selection surface should say exactly that — **"deep chat / 32-worker," "N concurrent," "evicts the embedder"** — not gpu_util fractions or byte counts. This is the layer that translates `_profile` (the measured truth) into a *meaningful choice*. (My-idea, grounded in SCOPE:32-33 + gpu.py:48-79.) It is the same translation Tim demands everywhere ("translate everything → human meaning," memory).

A subtlety worth flagging for synthesis: the *render is the easy part once `_profile` is populated* — but `chat-4b-fp8._profile` is currently `null` (ANCHOR:49). So the units-render for the FP8 loadouts is BLOCKED on the profiler (Phase 1) landing the FP8 profile. The selection surface degrades honestly until then: show the loadout + a "shape not yet profiled" note, never a fabricated number (no-silent-fiction).

---

## 6 · Prior-art frame in depth (the External grounding)

### 6.1 llama-swap (mostlygeek/llama-swap)
- **What it does (External):** Go proxy in front of OpenAI/Anthropic-compatible backends (llama.cpp, **vLLM**, TabbyAPI, …). Reads the request's `model` field, starts/swaps the right upstream, routes. Out of the box: one model at a time (swap on model change). `groups` + `swap:true` let several models coexist; `gpu_memory_utilization` tunes per-model VRAM. `ttl` auto-unloads idle models. **Groups V2 ("swap matrix," issue #643)** adds a DSL for sets-that-run-together + a solver that decides what to unload for a new model.
- **Maturity (External):** 3,000+ stars, active (v201, Apr 2026). Production-grade.
- **The "yes-but-actually" (My-idea, grounded):** its per-model VRAM control is `gpu_memory_utilization` — **literally the static fraction Tim is killing** (SCOPE:15, "that 50% has gotta go"). Adopting it wholesale would *re-import the anti-pattern this whole rework exists to dissolve.* Its Groups-V2 swap-matrix is conceptually exactly Company's combos + `extends/swap/add/remove` variants (services.json:7) — **Company already shipped the DSL llama-swap is still designing.**
- **Verdict:** reference, not runtime. Mine the groups-coexistence concept (validates Company's combo shape); don't depend on it.

### 6.2 LLMSnap (napmany/llmsnap)
- **What it does (External):** a **llama-swap fork** that adds **vLLM sleep/wake** — "offload memory instead of full restart" — plus Docker/Podman orchestration. Same `models`/`groups`/`ttl`/`aliases`/`hooks`/`macros` YAML config family. Backends: any OpenAI-compatible server (llama.cpp, vLLM, tabbyAPI, …) + Anthropic.
- **Maturity (External):** 48 stars, 5 releases, latest Apr 2026 — *thin / early.* Too immature to be a load-bearing dependency.
- **Why it matters anyway:** it is the **reference implementation** of the sleep/wake-orchestration pattern the anchor wants (ANCHOR:21,40, SCOPE:80). It proves the pattern — keep the process alive, sleep one model's VRAM, wake another — works as a swap primitive over vLLM.
- **Verdict:** don't adopt the proxy. Adopt the **vLLM built-in it wraps** (`--enable-sleep-mode`) directly into Company's own `apply_loadout` switch (reach-for-the-stack, SCOPE:16). LLMSnap is the worked example to read, not the code to run.

### 6.3 vLLM sleep-mode (the actual built-in — the thing to adopt)
- **What it is (External, vLLM docs/blog):** releases most GPU memory (weights → CPU RAM, KV discarded) **without stopping the server**; wake resumes without a full reload. **Benchmarks: 18–200× faster switches, 61–88% faster first inference vs cold starts.** Works with TP/PP.
- **The conditional verdict (dependency on the rigor area — DO NOT re-litigate here):** *IF* sleep-mode verifies on OUR Qwen3.5-4B-FP8 hybrid (flagged broken on some models since 0.14, ANCHOR:40, SCOPE:80 — that's another area's job), THEN wire the LLMSnap pattern (sleep the outgoing brain, wake the incoming) into `apply_loadout` as the swap primitive, *replacing evict-reload* for brain↔brain switches. ELSE order-aware bring-up stays the fallback (ANCHOR:55). **Handoff:** the selection surface design is sleep-mode-agnostic — it selects loadouts; whether the *switch underneath* uses sleep-mode or evict-reload is the actuator's concern, transparent to all three faces. So AREA-6 does not block on the sleep-mode verification.

### 6.4 LiteLLM
- **What it does (External):** a front-door router/gateway — load-balancing, latency/usage-based routing across many deployments (cloud + local vLLM/Ollama), pin-model-version advice. Sits in front of inference engines.
- **The "yes-but-actually":** Company's `run_role` **already resolves `base_url` from the model id** — the ollama-vs-vLLM split (mcp_face/server.py:747-759, Observed): an HF-path id → its resident vLLM service; an ollama `:cloud`/`:tag` id → the fabric ollama endpoint (:11434, auto-starts, proxies ollama-cloud). That IS the routing LiteLLM would provide, already built and *registry-native*.
- **Verdict:** redundant. No gap it fills. Adding it would be a parallel router over the one Company has.

### 6.5 What's deliberately NOT in scope (External, from SCOPE:65, confirmed not re-opened)
TGI (archived/dead), MIG (unavailable on Ada), MPS (helps only the small tenants), LMCache (vLLM-native CPU KV-offload beats standing it up at our scale). These were already triaged in the prior research; I confirm none changes the adopt-vs-build verdict.

---

## 7 · The conversational ↔ worker tension (AREA-6's edge — taking a position)

The anchor leaves this open (ANCHOR:28): one tunable instance vs two declared loadouts vs sleep-mode. **Position (My-idea, grounded):** the robust primitive is **TWO declared loadouts of the same model, selected per job** — `interaction-fp8` (deep chat, 2 seqs) and `@extract` (32-worker, solo) — *which is precisely WHY the multi-actor selection surface must exist.* The two-loadout answer and the selection surface are the same design: if work picks its shape, the shapes must be declarable + selectable + visible to all three actors.

- One tunable instance can't serve both live cleanly: `max_num_seqs` is fixed at load (changing it = a reload, SCOPE:42) and the per-seq Mamba toll is reserved at load — so "deep chat 2-seqs" and "32-worker" are genuinely different resident shapes, not a runtime dial.
- Priority scheduling + chunked prefill (SCOPE:50) *soften* the tension within one shape (foreground chat jumps ahead of background swarm on the SAME instance) — adopt them — but they don't dissolve the seq-count/ctx tradeoff. They're the in-shape optimization, not the cross-shape primitive.
- Sleep-mode (if it verifies) is the *fast-switch optimization* between the two declared loadouts — not a replacement for declaring them.

So: declare two loadouts → select per job (the AREA-6 surface) → switch via sleep-mode-if-available-else-evict-reload (the actuator, transparent). The tension resolves INTO the selection surface, confirming why it's worth building.

---

## 8 · Contradictions of the anchor (the honest list)

- **ANCHOR §2 / §0bis frames multi-actor selection as something to design from scratch.** It's ~70% built: the resolver, the combos registry+variant-DSL, the requires-gate (cascades), the confirm/approve floor, the gated actuator, and the RHM repoint all exist (Observed). The real work is two visibility gaps (A, B) + ergonomic render + an RHM verb. Saying "build the selection interface" overstates it; "build the selection FACES + close two gaps" is accurate.
- **ANCHOR §8 "cleaner industry substrate to adopt wholesale?"** — No. Every proxy either fights Company's systemd+resource-manager lifecycle or duplicates the model→endpoint routing already in `run_role`. The adopt is *vLLM built-ins*, not a wrapper.
- **The anchor leans on llama-swap pinned-groups as a possible substrate (ANCHOR:60).** Its VRAM knob is the static fraction Tim is removing — adopting it would undo the rework's premise. Reference only.
- **`brain_config` already binds modes→loadouts (suite.py:2185).** The anchor doesn't mention that the RHM's selection path partially exists via `set_mode`. The RHM verb is an enrichment of an existing path, not a new one.

---

## 9 · Handoffs / dependencies for synthesis
- **Sleep-mode verification (other area):** AREA-6's design is sleep-mode-agnostic; the switch-actuator consumes the verdict, the faces don't. No block.
- **Profiler / FP8 `_profile` (Phase 1):** the units-render is blocked on `chat-4b-fp8._profile` (currently null). Selection surface degrades honestly ("not yet profiled") until then — never fabricates a shape.
- **The `@extract` worker loadout (Phase 5):** must be a DECLARED combo in services.json for the agent/RHM to select it by name (today it's hand-built live, SCOPE:74,88). The selection surface needs it as a real registry row — that declaration is a precondition, and it's also where GAP A's "see" tool gets something to show.
