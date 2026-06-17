# Kimi-cloud for COGNITION — the gap (FILED, non-blocking)

```
trust: fabric-derived. author: ch-8djrpmsl (fork). date: 2026-06-17.
status: FILED — lead-directed non-blocking (path A / local nemotron landed the role-half green NOW; this
extends kimi from BUILD/clone use to the in-engine cognition transport). NOT started; needs lead co-scope
(capability_providers is suite.py — lead's hot file) + the litellm key wiring.
relates: #71 resolve_model (runtime/model_routing.py) · the role re-tier (35fd8e3) · the clone path (working).
```

## The distinction to HOLD (lead, 2026-06-17)
- **kimi as BUILD/generate/clone brain** = WORKING TODAY via the ollama-cloud path (`ollama launch claude
  --model kimi-k2.7-code:cloud`; clones green; the #71 clone branch of `resolve_model` routes to it). This
  gap does NOT touch that — it stays Tim's build brain.
- **kimi as a COGNITION provider** (a role/judge/synth fires ON kimi via the in-engine OpenAI transport) =
  the GAP. Two concrete blockers below. Once closed, re-tiering ANY judge/synth → kimi-cloud is a single
  registry edit (the registry-is-truth payoff).

## Blocker 1 — `capability_providers()` is LOCAL-ONLY (cloud not surfaced)
- **WHERE:** `runtime/suite.py:5848 capability_providers()`. It enumerates `ops/services.json` services and
  keeps only those with a `config.model` that has a catalog `provides` row, building
  `{provider_id: {model, base_url: http://127.0.0.1:{port}/v1, provides, resident}}`.
- **WHY cloud is absent:** cloud models (kimi/deepseek/glm/…) are in `ops/model_capabilities.json` (the
  catalog) but are NOT `ops/services.json` SERVICES — they have no local port/VRAM slot. So they never enter
  the provider set. VERIFIED: `capability_providers()` returns 18 LOCAL providers; no kimi. (`resolve_model
  {kind:role}` therefore can only bind a role to a local provider today — which is exactly why path A / local
  nemotron was the unblock.)
- **FIX (lead's suite.py — file-disjoint diff from fork on request):** surface the cloud catalog as providers.
  A cloud provider row = `{model: <catalog id>, base_url: OLLAMA_DIRECT (:11434/v1), provides: <catalog
  provides>, resident: False, cloud: True}`. Source the cloud set from `MODEL_CAPABILITIES` rows whose id
  ends `:cloud` (registry-is-truth — no hardcode). Keep residents-first ordering so local still wins ties;
  cloud is a legal-but-remote bind target (no VRAM, no swap-approval).

## Blocker 2 — kimi via litellm :4100 → 401 (no api key)
- **EVIDENCE:** `curl` kimi through the litellm OpenAI proxy `:4100/v1` → `401 Authentication Error, No api
  key passed in`. The proxy has no kimi/ollama-cloud key wired.
- **THE BASE_URL CHOICE (already encoded):** reach kimi via **ollama-OpenAI `:11434/v1`** (`fabric.config.
  OLLAMA_DIRECT`), NOT litellm `:4100`. The clone path already uses the ollama-native launcher; the cognition
  transport should point cloud providers at OLLAMA_DIRECT. (Recorded in the kimi catalog `json_schema` note.)
- **ALT FIX (if :4100 is wanted as the single cognition transport):** wire the ollama-cloud api key into
  `litellm.config.yaml` so :4100 proxies kimi. Then cloud-provider `base_url` = LITELLM_PROXY. Lead's call
  which transport is canonical for cognition; `resolve_model` returns whatever `base_url` the provider seam
  gives, so either is a registry/config edit — no resolver change.

## Verify-after (when closed)
1. `capability_providers()` includes a kimi cloud provider with `provides ⊇ [chat,json,reasoning]`.
2. `resolve_model({kind:role, role_id:reduce_synth}, suite=SUITE)` → kimi (satisfied=True) AFTER a registry
   re-tier toward a cloud reasoner — assert it's the kimi provider, NOT the nemotron/4B floor.
3. A real cognition turn fires a role ON kimi via the chosen transport (200, schema-conformant) — verify by
   use, not by config-read (the :4100 401 was caught exactly because config looked fine).

## Why non-blocking
Path A (local nemotron) lands the role-half green now with no auth wall. This gap only EXTENDS reach to
cloud cognition; nothing in #71 Phase 1 depends on it. Phase 2 (the byte-identical `resolve=` kwarg) is the
next #71 step and is independent of this.

---

## Phase-2 SEAM LIST (co-scope with the lead FIRST — R13 byte-identical; do NOT touch unilaterally)
1. **Wire `resolve_model` into the firing path** (`run_swarm`/`run_role` in `runtime/cognition.py`) via a
   byte-identical `resolve=`-style kwarg: the resolver must return the SAME model the scattered logic does
   today (resident 4B for the cast), so the live turn is unchanged until a role is deliberately re-bound.
2. **Enroll `runtime/model_routing.py` in `COG_SOURCES`** (`tests/cognition_governance_acceptance.py` C9.2).
   The moment model_routing joins the `_run_swarm` firing path it becomes floor-relevant; the C9.2 source-scan
   must cover it so a future dispatch call can't slip in unscanned. It PASSES C9.2 today (only
   `resolve_role_binding`/`resolve_binding` calls — not the floor verbs `resolve_surfaced`/`governance.resolve`),
   so enrolling is FREE. (advisor-flagged 2026-06-17.)
3. **Clone branch base_url is INFORMATIONAL.** `resolve_model({kind:clone})` returns `OLLAMA_DIRECT`
   (`:11434/v1`) but clones LAUNCH ollama-native (no `/v1`) via `ollama launch claude` — `clone_at` never
   consumes the field. Phase 2 must NOT start treating it as a live HTTP endpoint for clones.
