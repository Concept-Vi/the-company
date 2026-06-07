---
type: design
module: build-prep/concurrent-cognition/broader
aliases: ["Model Capability Registry — design", "Concurrent Cognition B4"]
tags: [company, design, models, capabilities, registry, vram, roles, concurrent-cognition]
status: draft
relates-to: ["[[runtime — constitution]]", "[[fabric — constitution]]", "[[ops — constitution]]", "[[Company Map]]", "[[Role Registry — design]]"]
---

# B4 — The Registry-Driven Model + Per-Model-Capability Config

**What this is.** A read-only map of the model/VRAM machinery that EXISTS in `~/company` today (service `config` blocks, the `ops/cli/gpu.py` resource-manager, `resolve_role`/`ROLE_REGISTRY`/`MODEL_KNOBS`, telemetry), then an on-paper design (**NOT built**) for the missing layer Tim names: a **model-TYPE capability registry** — where a model's *capabilities* (tool-calling, json_schema, thinking-vs-no-think, context ceiling, concurrency-knee, speed/latency, role-suitability) become **declared registry values keyed by the model-id**, so that **a role's model choice, the swarm's slot budget, and the fit gate all read from ONE source**. Framed as **a new sibling registry** (like `MODEL_KNOBS`/`STT_PROVIDERS`/`ROLE_REGISTRY`), additive and one-source (AGENTS.md rules 2+3+8), never a duplicate of the deployment data already in `services.json`.

> [!important] Epistemic status
> Every "EXISTS today" claim carries a `file:line` read directly from the repo. Every "net-new" is design, marked as such. The benchmark constants (the `32` knee, tok/s, p99, json_schema reliability) cite `~/vllm-tests/BENCHMARK_FACTSHEET.md` — the **measured** source (introspective-data-building outputs, not magic numbers). Mapping is **Observed**; the design is an **Inferred** proposal, not verified by execution.

---

## The load-bearing distinction: THREE keyings, kept separate

The whole design lives or dies on not blurring three things that already exist, each keyed differently. The task says "keyed by model TYPE" — that is exactly the *first* one, and it is the net-new piece:

| Keying | Keyed by | What it holds | Where it lives | Status |
|---|---|---|---|---|
| **Model-TYPE capabilities** (intrinsic to the weights) | **model-id** (the HF/cloud string, e.g. `cyankiwi/Qwen3.5-4B-AWQ-4bit`, `deepseek-v4-pro:cloud`) | tool-calling · json_schema · thinking/no-think · context-ceiling · concurrency-knee · speed/latency profile · role-suitability | **net-new — `MODEL_CAPABILITIES` registry** | **does not exist** |
| **Service-INSTANCE deployment** (how this machine serves it) | **service-key** (`chat-4b`, `embed-bge`, …) | `gpu_util` · `max_model_len` · `max_model_len_ceiling` · `_profile` · `vram_mb` · flags/env | `ops/services.json` `config` block | **EXISTS** |
| **Measured / telemetry** (what we observed) | **service-key** | `learned_vram`, load seconds, predicted-vs-measured | `ops/cli/telemetry.jsonl` + the benchmark sheet | **EXISTS** |

**The JOIN is the point** — and the proof case is already in the code: the `judge` role's `recommended_model` (`suite.py:954`) is `cyankiwi/Qwen3.5-4B-AWQ-4bit`, which is *byte-for-byte* the `chat-4b` service's `config.model` (`services.json:56`). **The same model-id is the bridge:** a role binds a model-id → reads its capabilities by model-id; AND *if* that model-id is locally served, looks up the backing service-key → reads residency/VRAM by service-key via `gpu.py`. The capability registry must NOT re-store gpu_util/vram (rule 3 — that's the service layer's job); it stores only what is intrinsic to the weights.

> [!warning] Two model POPULATIONS, only one has VRAM
> `fabric.transport.list_models` (`transport.py:15-25`) returns ollama+cloud ids (the brain's options — `deepseek-v4-pro:cloud`, etc., at `:11434`). `services.json` `config.model` returns the **locally vLLM-served** ids. Capabilities apply to **both** populations; residency/VRAM applies **only to locally-served** model-ids. A capability entry may legitimately have **no local service backing it** (a cloud model has capabilities but no VRAM budget) — the design must not assume every model-type has a service-key.

---

## Part A — what EXISTS today (Observed, file:line)

### A1. Service `config` blocks ARE the one source for model SIZING (`services.json`)
Each config-driven model service carries a `config` block that is authoritative for how vLLM is launched:
- `model` · `port` · `gpu_util` · `max_model_len` · `max_num_seqs` · `flags` · `env` (`services.json:55-80` for `chat-4b`).
- `max_model_len_ceiling` (`services.json:74` = `262144`) — the **context CEILING** the model can serve, distinct from the currently-set `max_model_len` (`65536`). This is the one place a model-intrinsic ceiling is recorded today, but it lives **per-service**, not per-model-type.
- `_profile` (`services.json:75-79`): `{fixed_mb: 5838, kv_kb_per_token: 31.7, measured: "256K solo: KV 8.37GiB/270482 tok"}` — the **measured cost model** that lets ctx auto-size gpu_util. `kv_kb_per_token` is arguably a **model-intrinsic** fact (KV bytes per token is a property of the architecture/quant), stored per-service today (see the migration note in C4).
- `serveconfig.args_for` (`serveconfig.py:31-42`) projects this block into vLLM CLI args — so a model's serve settings are **DATA**, editable via `company config <svc> <key> <value>` (`registry.set_config`, `registry.py:68-80`), never hardcoded in a shell script.

### A2. The resource-manager — `ops/cli/gpu.py` (the ONE VRAM authority)
- `budget_vram(reg, key)` (`gpu.py:32-43`): VRAM to budget, in priority order — (1) `config.gpu_util × ceiling` (authoritative for config-driven models, because that IS the reservation vLLM takes); (2) `learned_vram` telemetry; (3) the `vram_mb` estimate.
- `check_fit` (`gpu.py:113-126`) / `fit_report` (`gpu.py:129-173`): answers "will THIS selection fit the 16 GB card?" — `fits_card` (sum of config-derived budgets vs ceiling) and `fits_now` (not-yet-running vs *measured* free VRAM). `fit_report` is the settings fit-surface (`bridge.py:174`, `/api/fit`).
- `plan_eviction` (`gpu.py:176-191`): evicts `models → brain → voice`, largest first, only as many as needed.
- `teardown` (`gpu.py:202-243`): orphan-safe stop via the systemd cgroup (reaps vLLM EngineCore).
- Shared core: `voice/lifecycle.py` imports `gpu.py` rather than keeping a second budget (per STATE.md / the `budget_of` alias, `gpu.py:47`).

### A3. The co-residence work — `_apply_model_ctx` + the voice-switch shrink (`bridge.py`)
- `_apply_model_ctx(key, ctx)` (`bridge.py:40-72`): sets a model's `max_model_len`, **auto-sizes gpu_util from `_profile`** (`need = fixed_mb + ctx × kv_kb_per_token/1024 + 500`; `auto_util = min(0.92, need/ceiling + 0.005)`, `bridge.py:55-58`), then budget-gated restart (fail loud, never OOM — `bridge.py:63-69`).
- The voice-switch path (`bridge.py:828-853`) treats the judge+brain co-residency as **non-negotiable**: it reads the voice service's `config.coresident_brain_ctx` (a STORED max, `services.json:201` for orpheus = `65536`) and **shrinks+restarts the brain BEFORE loading the voice** (`bridge.py:842-845`). `_local_brain_key` (`bridge.py:75-83`) finds the brain's service-key by matching `config.model == rhm_config.model` (group `brain`) — the model-id↔service-key JOIN, already in code.
- The `small-pair` combo (`services.json:6-12`) records a VERIFIED co-resident pair (2B@0.45 + 0.8B@0.30 ≈ 12.3 GB).

### A4. Role→model binding — `resolve_role` + `ROLE_REGISTRY` (`suite.py`)
- `ROLE_REGISTRY` (`suite.py:943-972`): a role declares `default_model`/`default_base_url` (None → the brain), `recommended_model`/`recommended_base_url`/`recommended_reason`, `thinking`, `output`, `tools`, `context`, `knobs`, `env_*`. `judge` is the only registered role.
- `resolve_role(role_id)` (`suite.py:3186-3210`): precedence **config-binding > env > declared-default**; None default → the RHM brain (`cfg["model"]`). Fail-loud on an unknown role (`suite.py:3193-3194`, rule 8). So **swapping a role's model is a config change, never a code change** (`suite.py:3190-3191`).
- The `roles` config slot (`suite.py:1176-1180`, `1231-1256`): bindings live in ONE dict; `set_rhm_config` validates each role-id against `ROLE_REGISTRY` (fail loud, `suite.py:1236-1237`) and deep-merges three levels.

### A5. `MODEL_KNOBS` — the per-request knob catalog (`suite.py:1011+`, `knobs_for` `suite.py:3212-3235`)
A declarative catalog of per-REQUEST knobs (temperature/max_tokens/top_p/tools/thinking/structured_output), emitted in the node `config_schema` shape so the UI renders them with `NodeConfigForm`. **Crucially it carries a `applies` provenance vocabulary** (`suite.py:1227-1233`): `always` (always applies), `capability`→`probed` live (the `tools` knob is probed via `_model_supports_tools`, endpoint-aware), and `declared` (thinking/structured-output, can't be universally probed). `structured_output` already declares the axis `["none","json","json_schema"]` (`suite.py` MODEL_KNOBS) but is `declared`-only — inert (the `json_schema` transport branch is net-new; see file 01 §C2).

### A6. Live tool-capability detection — `model_supports_tools` (`transport.py:89-170`)
Endpoint-aware, **fail-loud** capability probe: `ollama` (`/api/show` capabilities list), `litellm` (`supports_function_calling`), `vllm` (a forced-tool-choice probe). It RAISES when capability can't be determined — never assume-capable. **This is the precedent for "probe wins over declared":** the live endpoint is the truth; a declared cache is a fallback.

### A7. Telemetry — the measured half (`ops/cli/telemetry.py`)
`record(service, load_seconds, resident_mb, estimate_mb, model)` (`telemetry.py:13-19`) → `learned_vram(service)` (`telemetry.py:36-40`) feeds `budget_vram`. `rollups()` (`telemetry.py:43-61`) flags estimate-vs-measured drift. **Keyed by service-key**, carries the `model` id as a field. The write-half of the introspective-data-building law.

---

## Part B — what is MISSING (the gap Tim names)

There is **no model-TYPE capability layer**. Today:
1. **Capabilities are scattered and mostly implicit.** `thinking` is a per-ROLE field (`suite.py:945`), not a per-model fact. Tool-calling is probed at call time (no cached registry). json_schema support is a `declared`-only knob, not asserted per model. The context ceiling lives per-service (`max_model_len_ceiling`). The **concurrency-knee is a hardcoded `32`** in the swarm design (file 03 §C.3) sourced from the benchmark sheet, not from a registry value. Speed/latency lives only in prose (`recommended_reason`, `suite.py:956-958`) and the benchmark sheet.
2. **Role-suitability is a hand-written PREFERENCE string** (`recommended_model` + `recommended_reason`, `suite.py:954-958`) — a human sentence ("local 4B no-think judged FINISHED in 463ms…"), not a computed match of role-needs against model-capabilities.
3. **Nothing connects "this role wants a no-think, tool-capable, fast model" to "which registered models satisfy that".** The operator/brain picks a model by reading prose, not by querying capabilities.

So the swarm (file 03) reaches for a hardcoded `Semaphore(32)`, the fit gate (`gpu.py`) reads context-ceiling only as a per-service number, and a role's model choice rests on a prose recommendation — **three readers, three sources.** Tim's premise is that these should be ONE source keyed by model TYPE.

---

## Part C — the design: `MODEL_CAPABILITIES`, keyed by model-id (Inferred / proposed, NOT built)

### C0. Stance — a new sibling registry, the JOIN explicit, no duplication
Add `MODEL_CAPABILITIES` as a class-level registry on the Suite (the exact shape-pattern of `MODEL_KNOBS`/`ROLE_REGISTRY`/`STT_PROVIDERS`), keyed by **model-id**. It declares ONLY model-intrinsic facts. It NEVER stores gpu_util/vram (that's the service layer, rule 3). It exposes a `model_capabilities(model_id)` resolver that:
- returns the declared capabilities for the id (fail loud on an unknown id, rule 8 — or a `source:"unknown"` row that forces an ASK, never a silent assume);
- **overlays the live probe** where one exists (`tools` via `model_supports_tools`) — **the probe wins**, the declared value is the fallback/cache (A6 precedent);
- **joins to the service layer**: if the id is locally served (a `services.json` `config.model` match — the `_local_brain_key` JOIN generalised), it attaches `{served_by: <service-key>, context_ceiling: max_model_len_ceiling, vram_via_gpu: budget_vram(reg, key)}`; if cloud/ollama-only, `served_by: None` and no VRAM (Part B trap 1).

### C1. The proposed capability schema (each field: source + reuse anchor / net-new)
```python
# suite.py — class-level, sibling of MODEL_KNOBS. Keyed by MODEL-ID (the weights), not service-key.
MODEL_CAPABILITIES = {
  "cyankiwi/Qwen3.5-4B-AWQ-4bit": {
    # --- INTRINSIC CAPABILITIES (net-new layer; what the weights can do) ---
    "tools":            {"value": True,  "source": "declared"},   # OVERLAID by live probe (A6) — probe wins
    "json_schema":      {"value": True,  "source": "measured"},   # BENCHMARK_FACTSHEET.md:85-96 (schema-conforming JSON reliable)
    "thinking":         {"value": False, "source": "declared"},   # no-think model (the judge's lesson, suite.py:959)
    "context_ceiling":  {"value": 262144,"source": "served",      # JOIN: services.json:74 max_model_len_ceiling
                         "from": "chat-4b"},
    # --- PERFORMANCE PROFILE (net-new; the MEASURED numbers the swarm + fit gate read) ---
    "concurrency_knee": {"value": 32,    "source": "measured"},   # BENCHMARK_FACTSHEET.md:11,30 — the Semaphore size
    "speed_profile":    {"value": {"decode_tok_s": 100, "ttft_ms_c32": 150, "p99_s_c32": 1.89},
                         "source": "measured"},                   # BENCHMARK_FACTSHEET.md:11-14,21-30
    # --- ROLE-SUITABILITY: a CAPABILITY SET, not a list of role names (see C3) ---
    # INTRINSIC tags only. "fast" is a coarse intrinsic tag (relative to the local fleet). Residency
    # ("can this be held warm on the 16GB card") is NOT here — it is DERIVED from the JOIN (see C2 + D2.4),
    # because it depends on footprint × card-capacity × co-resident pressure, which is the deployment layer.
    "provides": ["tools", "no_think", "json_schema", "fast"],
  },
  "deepseek-v4-pro:cloud": {
    "tools":            {"value": True,  "source": "probed"},     # ollama /api/show
    "json_schema":      {"value": None,  "source": "declared"},   # unknown for cloud — ASK / fail loud, never assume
    "thinking":         {"value": True,  "source": "declared"},   # a REASONER (the wrong tool on the hot path, suite.py:957)
    "context_ceiling":  {"value": None,  "source": "served", "from": None},  # cloud — no local ceiling, no VRAM
    "concurrency_knee": {"value": None,  "source": "declared"},   # cloud-throttled, not a local knee
    "speed_profile":    {"value": {"ttft_s": 2.1, "verdict_s": 6.5}, "source": "measured"},  # suite.py:957 prose → datum
    "provides": ["tools", "thinking", "reasoning"],              # NOT "fast", NOT "resident_capable"
  },
}
```
**Provenance vocabulary** reuses `MODEL_KNOBS`' (`always`/`probed`/`declared`, A5) **plus `measured`** for benchmark-sourced facts and `served` for JOIN-derived facts. Do not invent a parallel vocabulary (advisor).

### C2. The resolver — `model_capabilities(model_id)` (net-new, thin)
```
spec = MODEL_CAPABILITIES.get(model_id)              # fail loud / "unknown" row on miss (rule 8 — ASK, never assume)
caps = dict(spec)                                    # declared baseline
if "tools" probeable at the model's endpoint:        # OVERLAY — probe wins (reuse model_supports_tools, A6)
    caps["tools"] = {"value": probe(...), "source": "probed"}
key = service_key_for(model_id)                       # the JOIN (generalise _local_brain_key, bridge.py:75-83)
if key:                                               # locally served → attach the deployment/VRAM facts (DON'T copy them)
    caps["served_by"] = key
    caps["context_ceiling"] = max_model_len_ceiling(key)   # read services.json, not re-stored
    caps["vram_budget"] = gpu.budget_vram(reg, key)        # read gpu.py, not re-stored
    # residency is DERIVED here (not an intrinsic `provides` tag, C1): does its budget fit the card headroom?
    caps["resident_capable"] = gpu.budget_vram(reg, key) <= gpu.ceiling_mb(reg)   # footprint vs capacity, via gpu.py
return caps
```
Surfaced through `capabilities()` (the system's single self-description — AGENTS.md rule 8) so the UI/RHM/brain read it the same way they read node-types/verbs/models. A status read (`model_capabilities()` with no arg → the whole catalog) mirrors `roles()`/`available_stt()`.

### C3. Suitability is a COMPUTED match, not a hardcoded matrix (the Tim-shaped answer)
Do **not** maintain a per-role list of suitable models (a second registry that drifts, rule 3). Instead:
- A **model declares what it `provides`** (a capability set — C1).
- A **role declares what it `requires`** — a *net-new field on `ROLE_REGISTRY`* (additive; file 01 widens these rows anyway). E.g. `judge.requires = ["no_think", "fast", "json_schema"]` — lifted from the prose at `suite.py:956-967`.
- **Suitability is derived:** `suitable(role) = [m for m in MODEL_CAPABILITIES if set(role.requires) ⊆ set(m.provides)]`, ranked by `speed_profile`. The current `recommended_model` prose becomes a *computed* recommendation + a one-line *why* generated from the matched capabilities, not a hand-written sentence. The hand string can remain as an override seed, but the registry is the source.

This makes "which model for this role" a query, not a lookup — and a NEW model that declares the right `provides` is automatically a candidate (path-of-least-resistance; registry-is-truth).

### C4. Migration note (open, not a defect)
`_profile.kv_kb_per_token` (`services.json:77`) is a **model-intrinsic** fact (KV bytes/token is an architecture/quant property) currently stored **per-service**. Today there is one service per model-id, so it is *fine* — not broken. But it is a **migration candidate**: it conceptually belongs in `MODEL_CAPABILITIES` keyed by model-id, with the service block holding only the *instance* knobs (gpu_util/max_model_len). Mark as **needed/open**, do NOT claim the current placement is wrong. (Likewise `max_model_len_ceiling`.)

---

## Part D — how it COMPOSES with the resident-model + co-residence work, and what cognition ADDS

### D1. Compose, don't relocate — gpu.py stays the VRAM authority
`MODEL_CAPABILITIES` **adds** intrinsic facts the existing machinery currently hardcodes or lacks; it **removes** nothing from `gpu.py`:
- **The swarm `Semaphore`** (file 03 §C.3) reads `model_capabilities(resident_id)["concurrency_knee"]` instead of a literal `32`. One source: change the model, the knee changes, the semaphore re-sizes.
- **The fit gate** (`fit_report`, `gpu.py:129`) already reads `_profile` + `max_model_len_ceiling` per service; the capability layer makes `context_ceiling` *also* readable by model-id (the JOIN), so a role-binding UI can show "this model tops out at 256K" without knowing the service-key.
- **`budget_vram`** is untouched — the capability registry has no gpu_util/vram of its own (rule 3); it *points at* the service layer for those.

### D2. What "concurrent cognition" ADDS on top
1. **A concurrency BUDGET per resident model.** The resident model-id's `concurrency_knee` (C1, e.g. 32) is the total ceiling; the swarm reserves `knee − R` (file 03 §C.3) and the foreground stream/judge hold the rest. This budget is now a **registry-derived value** (the knee) split by a **config slot** (R) — not two hardcoded numbers. When a different model is made resident (a bigger model with a smaller knee), the swarm self-resizes from its declared knee.
2. **Role→model suitability as a query** (C3) — the swarm's roles (file 01) each declare `requires`; the resident model declares `provides`; the system computes which roles can run on the resident endpoint *right now*, and **fails loud / surfaces** if a role requires a capability no resident model offers (rule 4 — never silently run a no-think role on a reasoner, the judge's exact trap, `suite.py:963-967`).
3. **Fallbacks = the EXISTING chain + fail-loud, never silent** (advisor, rule 4). The chain already exists: `resolve_role` precedence (binding > env > default > brain). The capability layer adds a *pre-flight check*: before firing a role, assert the resolved model `provides` the role's `requires`; a missing **required** capability → fail loud and surface (the judge's stance, `suite.py:3266-3269`), never a silent degrade. For `json_schema`-unsupported endpoints specifically: fall to the `json_object` path **with a loud marker** (file 01 §C2), not a quiet downgrade — and carry file 01's caveat that strict-schema enforcement removes the judge's deliberate substring leniency for thinking-model fallbacks (file 01 §B3 migration note).
4. **The resident set is a budgeted residency tier** (file 01 §D2): brain-shared roles (no extra VRAM) · co-resident small models (VRAM-budgeted, owned by `gpu.py`) · on-demand (loaded on trigger). The **DERIVED** `resident_capable` field (computed in the resolver from the JOIN — `budget_vram` vs card headroom, C2 — NOT an intrinsic `provides` tag) tells the resource-manager which model-ids can be held warm on the 16 GB card. The capability registry is the *declarative input* (the intrinsic facts) to the residency decision `gpu.py` already enforces; residency itself stays a `gpu.py` computation.

### D3. The co-residence JOIN, generalised
`_local_brain_key` (`bridge.py:75-83`) already does the model-id→service-key match for ONE model (the brain). The capability resolver's `service_key_for(model_id)` (C2) is the **general** version of exactly this — so the same JOIN that lets the voice-switch shrink the resident brain also lets a role's capability lookup find its VRAM cost. One bridge, reused.

---

## Part E — reuse-vs-net-new summary

| Capability registry concern | Reuse anchor (file:line) | Net-new |
|---|---|---|
| registry shape / provenance vocab | `MODEL_KNOBS` `applies` (`suite.py:1011+`); `roles()` status read (`suite.py:3172`) | **`MODEL_CAPABILITIES` dict + `measured`/`served` provenance** |
| tool-calling capability | `model_supports_tools` live probe (`transport.py:89-170`) — **probe wins** | declared cache only |
| json_schema capability | benchmark proof (`BENCHMARK_FACTSHEET.md:85-96`); `structured_output` knob (`suite.py` MODEL_KNOBS) | **per-model assertion + the transport `json_schema` branch (file 01 §C2)** |
| thinking / no-think | per-role `thinking` field (`suite.py:945`) | **per-model fact (the source the role reads)** |
| context ceiling | `max_model_len_ceiling` (`services.json:74`); `_profile` (`:75-79`) | **readable by model-id via the JOIN** |
| concurrency knee | `BENCHMARK_FACTSHEET.md:11,30` (the `32`) | **`concurrency_knee` value the swarm Semaphore reads** (replaces the literal) |
| speed/latency profile | `recommended_reason` prose (`suite.py:956-958`); sheet §1 | **`speed_profile` datum (prose → structured)** |
| role-suitability | `recommended_model` prose (`suite.py:954`) | **computed match: role `requires` ⊆ model `provides`** |
| VRAM / residency | `gpu.budget_vram` (`gpu.py:32`); `_profile` auto-util (`bridge.py:55-58`); co-residence (`bridge.py:828-853`) | **— (untouched; the registry POINTS at it, never copies)** |
| the model-id↔service JOIN | `_local_brain_key` (`bridge.py:75-83`) | **`service_key_for(model_id)` (generalised)** |

**Net-new is concentrated in:** (1) the `MODEL_CAPABILITIES` dict + `model_capabilities()` resolver (additive, the shape already exists in siblings); (2) the role `requires` field + the computed `suitable()` query (additive to `ROLE_REGISTRY`); (3) wiring the swarm `Semaphore`/fit-surface to read the knee/ceiling from the registry instead of literals. The VRAM authority (`gpu.py`) and the deployment data (`services.json`) are **reused unchanged** — the capability registry composes with them via the JOIN.

---

## Open decisions to surface for Tim (not to decide silently)
- **Capability provenance per model** — for cloud models, several capabilities (json_schema, knee) are *unknowable* without a probe or a doc. Do unknown rows **fail loud / force an ASK** (rule 8 stance), or carry a conservative declared default? (Proposed: `source:"declared", value:None` → a surfaced question before a role binds it, never a silent assume.)
- **kv_kb_per_token / context_ceiling migration** (C4) — leave them per-service (fine while one-service-per-model), or migrate the intrinsic half into `MODEL_CAPABILITIES` now to pre-empt the day two services serve one model-id?
- **`provides`/`requires` vocabulary** — who governs the capability TAG set (`no_think`/`fast`/`resident_capable`/`reasoning`/…)? It is a small controlled vocabulary; it should itself be a registered list (registry-is-truth) so a role can't `require` a tag no model can `provide`. Proposed: a `CAPABILITY_TAGS` tuple validated on both sides (fail loud on an unknown tag, like the role-id check at `suite.py:1236`).
- **Knee as ceiling vs. per-mode** — `concurrency_knee` is one number per model-id; but the *effective* budget depends on co-resident pressure (a model sharing the card with a voice has less headroom). Is the knee a pure model fact (proposed) with the residency split (R) handled by the swarm config, or should it be residency-aware? (Proposed: pure model fact; residency is `gpu.py`'s concern — keep the layers clean.)
- **Suitability ranking signal** — rank candidates by `speed_profile` (proposed), by measured telemetry (`run_stats`), or by an operator-pinned preference? The registry can carry all three; which wins by default is a Tim call.
