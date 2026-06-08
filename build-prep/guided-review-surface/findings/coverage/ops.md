---
type: findings
layer: coverage-ops
context: guided-review-surface
date: 2026-06-08
scope: ops/cli/ source + tests/ suite coverage
---

# ops/ Coverage Sweep — Guided Review Surface Integration Points

## OBSERVED Relations

### USE (Resident-Model Resource Management for Live Dialogue)

**`ops/cli/app.py:app.py` — the ONE console dispatcher (lines 1-217)**
- **`company up` resource gate** (lines 79-107, 113-126): the policy that REFUSES a start exceeding GPU capacity, always shows what's holding the card, support `--force`/`--evict`/`--wait` flags
- **`--wait` telemetry recording** (lines 45-76): after a model loads, records REAL resident VRAM + elapsed time for measured-over-time budget refinement
- **The all-green gate** (lines 133-149): `company suites` shells `suite_health_acceptance.py` as a subprocess to run EVERY acceptance suite standalone, requiring green (green | needs-live-dep | red) — this is the pre-merge/pre-deploy verification surface
- **Resident model availability assumption**: RHM dialogue + voice presentation both assume a resident model is available to serve the walkthrough narration (voices=resident-always per C8.3) and the guided-tour per-step framing
- **Evidence:** Lines 45-76 the _wait_and_record logic; line 82 `gpu.format_state(reg)` shown on every `up` so agents always know VRAM state without a second call; line 149 gate exit code propagation (0 = all green, non-zero = red)

**`ops/cli/capabilities.py` (lines 1-312) — the model-TYPE capability registry, keyed by model-id**
- **The intrinsic half (what the weights can do)**: tools, json_schema, thinking, context_ceiling, concurrency_knee, speed — each field carries {value, source} with explicit provenance (declared|probed|measured|served)
- **Provides TAG set** (line 50): MATCHES suite.py's `capability_providers()` exactly (chat·json·tools·fast·no-think·vision·thinking·reasoning) — this is what roles.requires ⊆ provides queries against
- **`capabilities_for(model_id)` (lines 168-216)**: returns capability fields + the JOIN to gpu.py (served_by key, vram_budget_mb via gpu.budget_vram, resident_capable, is_resident live view, endpoint for live probe). Unknown model-id returns explicit {"known": False, "action": "ASK", ...} never fabricated
- **`require_resident(model_id)` (lines 288-311)**: C8.4 — assert needed model is resident; return loud STRUCTURED result on miss (resident:bool, served_by, action:'OFFER_LOAD', load_command, message). NEVER auto-loads; operator/lead decides
- **Cloud-decoupling policy** (lines 252-274): COGNITION_PLACEMENT_POLICY — swarm=resident-always (never lost by cloud brain choice), main_brain=selectable (resident|cloud), background=cloud-allowed. `swarm_survives_cloud_brain()` is the invariant-as-query
- **Evidence:** Line 70-76 context_ceiling field docs cite services.json as source; line 178 vram_budget_mb reuses gpu.py NEVER re-stores; line 204 resident_capable is DERIVED via gpu; line 288-311 loud structured failure on miss (the NO silent degrade rule)

**`ops/cli/gpu.py` (lines 1-243) — the ONE VRAM resource manager**
- **Shared core imported by voice/lifecycle.py** (lines 10-14): the single VRAM authority for BOTH the `company` CLI and voice subsystem; stdlib-only so it loads in the 3.14 bridge
- **Public API**: read_gpu (measured VRAM), budget_vram (priority order: config.gpu_util × ceiling → learned telemetry → registry estimate), is_gpu_service, check_fit (refuses-or-evicts), plan_eviction (models→brain→voice priority), teardown (orphan-safe cgroup/pgroup)
- **`check_fit(reg, to_start)` (lines 113-126)**: decides fit using measured free VRAM (nvidia-smi truth) vs sum of registry estimates for not-yet-running services; fallback to estimate vs ceiling if GPU unreadable
- **`fit_report(reg, keys)` (lines 129-173)**: "tell me if my selection won't fit" — given selected GPU service keys, returns each budget, sum vs ceiling, measured free, fits_card/fits_now, evict names + projected free (config-derived so tracks resizes)
- **`format_state(reg)` (lines 95-110)**: the 'what's holding the card' block — shown on refuse + every `up`, so agents always know without a second call
- **Evidence:** Lines 32-43 budget_vram docstring priority order; line 52-58 the _is_running check per-unit signal (not port) because model services share ports; line 202-243 teardown docstring explains EngineCore orphan cgroup kill vs pgroup SIGTERM/SIGKILL

**`ops/cli/registry.py`** — reads services.json + utilities
- **`vram_of(svc)` + `ceiling_mb(reg)`**: imported by gpu.py as VRAM truth source (not duplicated)
- **`resolve(reg, target)`**: parses service key, group, @combo, or `all` into the actual keys to control
- **Evidence:** Imported at line 36 of app.py, line 17 of gpu.py; vram_mb + vram_ceiling_mb live in services.json structure

**`ops/cli/render.py` (lines 1-38) — human/AI-readable views**
- **`status(reg)`**: shows every service grouped by category, live state (▶|◐|✖|·), label, port, VRAM budget (config-derived), title — the operator's view of what's on the card right now
- **`health(reg)`**: port-by-port liveness (✓|✗)
- **Evidence:** Line 26-27 status calls budget_vram + is_gpu_service for every service, surfacing committed VRAM + GPU measured state

**`ops/services.json` — the single registry of truth**
- **Structure**: groups (core|brain|voice|models|reach), services with key/group/title/port/manage/{type,unit}/health/autostart/config (for model services: model, port, gpu_util, max_model_len, flags, env, max_model_len_ceiling, _profile)
- **Model config block**: gpu_util × ceiling = the ONE budget source; max_model_len_ceiling records solo reachable capacity; _profile carries fixed_mb + kv_kb_per_token (measured) for auto-sizing
- **Evidence:** chat-4b service entry shows the full config pattern; vram_ceiling_mb at root = 16376 MB (the card ceiling); combos section defines named sets like @small-pair

### TOUCH (New Suites the Build Needs — Guided Tour, Reachability, Verification Gates)

**Tests covering walkthrough/review/guided-surface lifecycle (existing coverage to extend)**

- **`tests/walkthrough_acceptance.py` (lines 1-50+ scanned)**
  - WHAT: exercises the RHM walkthrough/review organ end-to-end (start_session / present_current / next / respond / session_status, suite.py ~998-1124)
  - ASSERTS: lifecycle (cursor advances one per next, gates open, run fires), ui:// resolver (build_ui_info serializes component registry), governance (recorded verdict immutable, only operator-only resolve_surfaced flips resolved field)
  - **RELATION TO GUIDED REVIEW**: the SAME start_session / present_current / next spine is reused for guided sequences; a guided step differs only in present_current framing (corpus address_help instead of coa model)
  - **Gap tagged**: walkthrough exercises INBOX-ITEM walks; showme_guided_acceptance exercises ADDRESSED-ELEMENT walks; UNIFICATION NEEDED for a suite that proves both paths ON the same resident walkthrough stack

- **`tests/showme_guided_acceptance.py` (lines 1-50+ scanned)**
  - WHAT: C1 · system-initiated guided sequences over ADDRESSED ELEMENTS (ui://<region>/<element> addresses instead of inbox review-ids)
  - ASSERTS: start_guide() binds over registry-true addresses (system-initiated, bare call), each step resolves corpus how-to as narration + registry-valid ui_target (G-43), next() advances model-free (no model ever called), _registry_ui_target honours payload-carried guide_address + REFUSES unregistered (safe fallback to inbox)
  - **RELATION**: the bridge can call start_guide() directly; the RHM can call it (system-initiated from swarm); guided sequences carry per-step ui_target so FE spotlight drives the real element
  - **Coverage**: uses REAL Suite, real corpus registry, NO live model (model-free-by-construction) — proves the stepper works without a brain service running

- **`tests/e2_review_fixes.py` (lines 1-80+ scanned)**
  - WHAT: regression tests for three e2 adversarial review findings (B1 memo port-awareness, B2 memo-skip lineage, S1 unwired-input stuck)
  - **RELATION**: proves the graph scheduler's fundamental correctness (memoization, provenance, stuck detection) — foundational for any build-triggered graph run the guided review would generate
  - **Coverage**: TDD-driven, reproduces bugs on buggy code then passes on fix — the pattern to extend for new failures

**Gate + verification structure**

- **`tests/suite_health_acceptance.py` (lines 1-80+ scanned)**
  - THE STANDING ALL-GREEN GATE: runs EVERY acceptance suite STANDALONE, requires green (needs-live-dep skip | red)
  - Discovered THREE silent-red classes (2026-06-08): conv_reach RED on main undetected (gate never ran it), event_address RED undetected, json_schema FALSE-GREEN on external PYTHONPATH but failed standalone
  - **RELATION TO BUILD**: the guide surface build MUST BE pre-merge gated by this — `company suites` (line 133 app.py) shells this gate as subprocess, pre-merge/pre-deploy/periodic standing gate
  - **Gap tagged**: this gate runs acceptance suites but does NOT run the BUILD verification that suite.py provides (verify_build, verify-by-use). A NEW gate needed for:
    - All new suites the guide surface adds (guided-tour, generate-for-mockups, comprehension)
    - Reachability gate: every ui:// address the guide references IS in the live registry
    - Build gate: running a guide-initiated build produces a committed graph + verified by use

### UNIFY (Gates That Should Cover This Surface But Don't)

**Gap U1: NO VERIFICATION THAT A GUIDE-INITIATED BUILD PRODUCES VERIFIABLE OUTPUT**

- **Current**: walkthrough_acceptance proves the stepper works; e2_review_fixes proves graph fundamentals; suite_health_acceptance proves code-green
- **Missing**: a gate that asserts: `guide generates → builds a graph → graph.json persists → suite runs guide-generated build → assert produces expected output (commit-ready)`
- **Why it matters**: Tim's rule "verify before claiming" — a guide-initiated build (operator clicks "generate," RHM autonomously builds) MUST produce code the suite can verify was not fabricated. The gate lives between build completion and git commit
- **Observed**: app.py lines 133-149 show how the all-green gate works (subprocess, TEMP store, isolation); this PATTERN can wrap guide-generated builds (same isolation, different graph source)
- **Inference**: the bridge → RHM autonomous flow (build_result_review generated, user clicked) needs a parallel verify-by-use path that runs the SAME suite verification but ONLY over the generated output, not the whole codebase
- **Marked UNIFICATION**: a single gate interface `verify_guide_output(generated_graph, test_suite_ref)` that both the bridge (after autonomous build) and `company` (pre-merge) can call

**Gap U2: NO QUERY FOR "CAN THIS GUIDE TOPIC BIND TO THE RESIDENT MODEL?" (C8.2 + C8.4)**

- **Current**: `capabilities_for(model_id)` returns capability fields; `require_resident(model_id)` asserts residency with loud failure; `role_can_bind(requires, model_id)` checks `requires ⊆ provides`
- **Missing**: before guide.start() compiles the guide (picks the corpus how-to addresses + decides if coa() framing is needed), a check: "does the current main brain provide the capabilities this guide's framing requires?"
- **Why it matters**: a guide over a tool-calling node REQUIRES a model with tools=True in provides; starting a guide when the brain is cloudbound but can't tool-call should fail loud before wasting a walk, or auto-downgrade to a model-free walk (guidance-only, no coa framing)
- **Observed**: suite.py:capability_providers() hand-derives the resident's provides; the lead's wire flags this as the ONE place capabilities_for() will be called (capabilities.py docstring, line 17)
- **Inferred**: the bridge route `/api/guide/start?topic=X` needs to call something like `guide_requires = registry.guide_topic_requires(topic)` (new; derived from corpus), then `check_binding = capabilities_for(resident_main_brain, live_probe=True)`, returning guidance-only or requires-load or OK
- **Marked UNIFICATION**: a pre-guide lint that asserts the chosen topic's corpus requirements (tool-calling, json_schema, thinking) are satisfied by the resident before binding RHM roles

**Gap U3: NO GATE FOR GUIDE ADDRESS REACHABILITY (G-43 COMPLETENESS)**

- **Current**: `_registry_ui_target()` (suite.py) honours payload-carried guide_address + falls back to inbox (safe); G-43 says per-step ui_target is registered
- **Missing**: before guide starts, scan EVERY address the corpus will emit (address_help → how_to_use/ what_this_is → the displayed ui:// addresses) and assert all are IN UI_REGISTRY
- **Why it matters**: if a guide references `ui://canvas/nonexistent-node`, the FE spotlight fails (loud, safe fallback to inbox); pre-guide lint catches this in build time, not user time
- **Observed**: build_ui_info (suite.py) builds the live UI_REGISTRY from the live component registry; showme_guided_acceptance line 50+ tests that the addresses ARE reachable
- **Inferred**: a suite that generates a guide, then calls build_ui_info(), then scans the corpus-emitted addresses against the registry (the tautology check)
- **Marked UNIFICATION**: a lint gate `guide_address_reachable(guide_id, registry)` that returns reachable/unreachable + list of bad refs

**Gap U4: NO RESIDENT-MODEL ASSUMPTION IN GUIDE-INITIATED BUILDS (C8.4 + OPERATOR FLOW)**

- **Current**: require_resident() returns loud structure; voice subsystem checks residency before speaking; but a guide can be STARTED without a resident (walkthrough works model-free per showme_)
- **Missing**: when the guide steps call coa() framing (the walk is NOT model-free), a check that asserts resident availability OR offers to load it (async, don't block the walk). Currently there's NO path for the guide walk to say "I need the brain loaded, offer to load?"
- **Why it matters**: Tim's rule: operator/lead decides, never auto-load. But a model-free guide walk (addresses + how-to, no framing) is FAST and COMPLETE; coa() framing is OPTIONAL and requires the brain. The guide needs a two-mode flow: model-free walk OR wait-for-resident framing
- **Observed**: C8.3 docs (capabilities.py lines 252-274) state policy clearly; require_resident (lines 288-311) returns actionable structure with load_command
- **Inferred**: the bridge route `/api/guide/next` needs to check: if step.payload requires framing (coa call needed), call require_resident(resident_main_brain), and if action='OFFER_LOAD', surface the load button ALONGSIDE the next button (both clickable, guide proceeds model-free if not loaded, framing skipped)
- **Marked UNIFICATION**: guide walk state carries framing_available (bool, set by resident check); coa() framing IS called only if true; UI offers load alongside next; walk never blocks or auto-starts

## Summary

**Coverage swept**: ops/cli/ source (app.py, capabilities.py, gpu.py, render.py, registry.py, telemetry.py) + services.json registry + ops/AGENTS.md constitution + tests/ walkthrough/guided/e2/gate suites.

**Four unification gaps identified** (not critical to start, but needed for full-quality surface):
1. **Verify guide output** — gate that runs suite verification over guide-generated builds pre-merge
2. **Guide topic binding** — pre-guide lint asserting corpus requirements (tools/json/thinking) match resident capabilities
3. **Address reachability** — lint that scans corpus-emitted ui:// addresses against live UI_REGISTRY
4. **Model-free vs framing** — guide walk flow offering resident load async, never blocking, proceeding model-free if not loaded

**File paths (absolute, for agent navigation)**:
- `/home/tim/company/ops/cli/app.py` — ONE console, resource gate, all-green gate
- `/home/tim/company/ops/cli/capabilities.py` — model-TYPE registry, binding queries, cloud policy, require_resident loud failure
- `/home/tim/company/ops/cli/gpu.py` — VRAM authority (shared with voice), fit_report, format_state
- `/home/tim/company/ops/cli/registry.py` — registry load + resolve
- `/home/tim/company/ops/services.json` — truth registry + model config blocks (gpu_util, max_model_len_ceiling, _profile)
- `/home/tim/company/ops/AGENTS.md` — constitution, type-views (services, models/VRAM, capabilities)
- `/home/tim/company/tests/walkthrough_acceptance.py` — RHM stepper lifecycle
- `/home/tim/company/tests/showme_guided_acceptance.py` — guide-over-addresses, model-free walk
- `/home/tim/company/tests/suite_health_acceptance.py` — all-green gate (every suite, standalone)
- `/home/tim/company/tests/e2_review_fixes.py` — graph scheduler correctness

**Top unification opportunity**: U1 (verify-guide-output gate) — once the guide build → commit flow is live, wrapping the all-green gate over guide-generated graphs (using the same subprocess + TEMP store isolation pattern at app.py lines 133-149) gives pre-merge confidence without duplication.
