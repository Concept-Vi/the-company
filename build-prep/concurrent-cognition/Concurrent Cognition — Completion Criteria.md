# Concurrent Cognition — Completion Criteria

*The truth table for the build. Document 1 of the loop-prep triad (see also the Implementation Guide + Research Synthesis). Every criterion is two-faced — FUNCTION and FORM — and green only when BOTH are verified by USE. This is the common reference the sub-agent-driven build reads; it is registry-driven by Tim's law L1, rule-based-routing by L2 (see `DECISIONS.md`).*

> **⚠ Hardened by Round-1 review — `review/R1-FOLD.md` is the binding correction layer.** Key folds woven below: the **resource ceiling is real** (the resident 4B serves `max_num_seqs=16`, KV shared with the main context → the swarm cap is **state-dependent: ~12–14 with short roles + a higher-util (~0.63) swarm-brain, collapsing to ~2–5 only at a full 64K main + long roles** — not the "32" throughput number); **parallelism lives in the cognition driver, not the shared scheduler**; **addressing is `run://` throughout** (never `swarm://`); **injection, `chat_parts`, the activation substrate, and the jury flow are NET-NEW** (not free reuse); **rule-determinism and the `claude -p` floor are enforced invariants with tests**, not assertions. Locate code **by symbol** (the line refs drifted ~+14).

---

## Verification rules (how a criterion goes green)

- **FUNCTION bar:** the behaviour is demonstrated by USE — run it, observe real values, no stub, no "no error ≠ working." A worker may not self-pass; it provides proof (the request/response, the event, the rendered frame, the measured number).
- **FORM bar:** built on the design system (its components + tokens, no bespoke values), coherent + responsive, a navigable visual surface not a text-wall, settings consolidated. Graded by a SEPARATE design-critic pass, never self-graded by the implementer.
- **Tools:** backend by `tests/*.py` + curl of the live seam + `drift_acceptance.py`; FE in chrome-devtools on the worktree's bridge/canvas; GPU by `company gpu`/`nvidia-smi` before any load (shared card — never stomp).
- **The laws bind every criterion** (AGENTS.md + DECISIONS): registry-driven not hardcoded · rule-based routing (a model runs only inside a *role*, never inside a *rule*) · deterministic gates / no confidence value · fail loud, no silent fallback · schema-additive · author from the registry never invent · **autonomous build-dispatch / `claude -p` stays lead-only** · reflects-never-owns (canvas drives via addresses; backend truth) · prove by USE.
- **`needs-tim`** (never green by the loop): the *feel* of the staged stream, audio quality, the cognition view's aesthetics on-device, whether a 4B aggregator's fused output is good enough — these are flagged for Tim, never self-certified.

---

## G0 · Proving spike (GATE — before any fan-out)

> The whole build is gated on this. Settles the one risk the research could not: does the rule-based, resident-4B mechanism actually produce a coherent staged reply — and does a routed/fused multi-role result hold up.

- **C0.1 · A 2-role staged turn, end-to-end.**
  FUNCTION — a real utterance → `focus` fires → Part 1 emits from base context instantly → one auxiliary role (`recall` or `ground`) runs concurrently, writes structured JSON to an address → its rule injects into Part 2's context → Part 2 emits enriched → both parts stream as one reply. Demonstrated by use (the event log shows the role fire, the injection, the two parts).  ✅ by use (G0 commit fd0f347; lead re-ran in isolated store vs live 4B)
- **C0.2 · Routing is rule-based + deterministic — tested on a NON-TRIVIAL rule (R1-FOLD F5).** A *declared rule* (one that reads multiple resolved fields, not a one-liner) resolves a `run://` address; re-running identical inputs routes identically — even though the wave's roles finished in nondeterministic order. Proven: run twice → identical routing trace, with the rule reading values that completed in different orders.  ✅ by use (12-run race: finish-order flipped 7/5, identical routing every time)
- **C0.3 · The 4B-as-aggregator question, answered.** If the spike includes a fusing role (combine 2 role outputs), measure whether the 4B's fused result is coherent; if routing-only suffices (per L2), record that aggregation is optional. → `needs-tim` on quality; FUNCTION = it runs.  ◑ needs-tim (routing-only sufficed per L2; a fusing role's quality is deferred — not gating)
- **C0.4 · No starve, fail loud.** The main stream keeps its reserved slots; if the resident model is down, the turn fails loud + offers to load (never silent).  ✅ by use (rule raises on any missing declared input; unresolved ref raises; role failure propagates FabricError)
- **C0.5 · MEASURE the real resource ceiling (the gate that matters most — R1-FOLD F1).** On the actual co-resident voice config (4B @ util 0.49 + the 4-bit voice resident), with a staged main reply running, MEASURE: how many concurrent role-runs actually serve before latency thrashes (bounded by `max_num_seqs=16` AND KV/per-role-context), and the real **inter-part wall-clock** (slowest dep role + JSON-retries). The spike must PRODUCE these numbers — not assume 32. The swarm cap is then `min(max_num_seqs−R, KV-budget/per-role-ctx)` from the registry.  ✅ by use MEASURED 2026-06-07 (KV pool 66,036 tok@0.49 vs 135,574@0.63; max-concurrency 1.01x→2.07x at 64K req; bind flips on main-depth; budget=min(16-2,KV/role) in SlotBudget.from_registry)

*Spike passes → fan-out unlocks. Spike fails → redesign before building further. (Per R1-FOLD: as originally worded G0 could pass without testing the thing most likely to break — C0.5 fixes that.)*

## G1 · Node-mechanism substrate rebuild (THE make-or-break · serial spine)

> The dual-use spine (app surface + cognition). Full registry-driven rebuild (Tim: "full substrate now"). The concurrent executor is the one genuinely net-new engine piece.

- **C1.1 · Concurrent dispatch in the COGNITION DRIVER (not the shared scheduler — R1-FOLD F2).** Parallelism is a property of `_run_swarm` / the in-turn part runner, leaving the app's `Suite.run` serial (no behaviour change to the governed app face). It first builds a **materialized ready-set** (the scheduler is a re-scanning loop today, no ready-set), then dispatches it via a thread pool; store writes serialize safely behind the wave barrier. Proven: N independent role-runs run in ~max(role) not ~sum(role); a concurrent app `Suite.run` is unaffected.  ✅ by use (8 roles wall=1.52s vs sum=12.12s≈max; 14-role wave 0.60s wall; scheduler.py grep-verified serial; commit 9a3f… G1)
- **C1.2 · Request-concurrency budget from the REAL registry values (R1-FOLD F1).** The semaphore = `min(max_num_seqs − R, KV-budget / per-role-context)` read from the registry — **NOT a hardcoded/assumed 32** (`max_num_seqs=16`; KV is shared with the main context). Roles are short-context so many fit. Reserve R for the main stream/judge. Proven: the measured-max concurrent role-runs (C0.5) complete; the main stream never blocks AND never just waits in vLLM's admit queue behind the swarm.  ✅ by use (SlotBudget.from_registry reads max_num_seqs=16+R=2 from services.json, no hardcoded 32; knee=14 shallow→1 at deep-64K-main; main acquire 0.0–0.2ms during in-flight 14-role wave)
- **C1.7 · A mode-selected SWARM-BRAIN config (R2-FOLD H1, refined by R2-resource-math).** Swarm width is **state-dependent and the bind flips**: with short roles (~1–2K each) + a bounded main context, `max_num_seqs=16` binds → **~12–14 concurrent roles**; only at a *full 64K main + long roles* does the shared KV pool bind and collapse it to ~2–5. The lever (corrected): a **higher-util swarm-brain (`util ~0.63`)** that claims the ~3.8 GB the voice config (0.49) leaves idle → KV pool grows to ~140–155K tokens → 15 roles @ 4K + a full 64K main fit, seq-cap becomes the sole bind. So **MODE selects the brain CONFIG** (a first-class registry artifact via `company config`/`swap`) + the build encodes a **role context budget ~1–2K** + **R=2 reservation**. Overlap-vs-between is a **per-role choice** (warmed prefix makes re-prefill near-free). Proven: C0.5 measures the empirical knee; a swarm-brain config hits ~12–14.  ◑ budget formula proven by use at 0.49 (knee=14 shallow / 1 deep, KV-grounded); the 0.63 swarm-brain KV pool is C0.5-measured (135,574 tok) but the deep-main knee AT 0.63 is computed-not-use-measured (needs the lead/Tim GPU reconfig to drive a real 64K-main wave) — needs-tim
- **C1.3 · Edge type system + the injection edge (NET-NEW read — R1-FOLD F3).** Edges carry a declared `kind` (data-wire · **injection** · gate/branch · fan-in) — not a bare wire. Adding `kind` to `contracts/node_record.py` is a **CONFIRM-level contract edit** (bump `schema_ver`; default-kind for existing edges; vault-spec update). The injection edge is a **net-new ref-read branch** in part-context assembly (the existing `_resolve_context_at`/`_r2_gather` reads operator-notebook strata, NOT fresh role refs — it does NOT do this). Role outputs live at **`run://<turn>/<role>`** (never `swarm://` — not a registered scheme). Proven: a later part reads the resolved value at a role's `run://` address.  ✅ by use (Edge.kind added schema-additive SCHEMA_VER 1→2 default 'data', old bare-edge graphs load unchanged; EDGE_KINDS registry + drift home + edge_kinds_acceptance 13✓; resolve_run_ref = store head→get_content [canonical, NOT context_variables — per R1-FOLD F3]; run:// read-back ✓, swarm:// rejected, missing-ref fails loud)
- **C1.4 · Output schema enforced via client-side validate/retry (R1-FOLD F9).** The transport sets `json_object` (valid JSON, not schema-conformant); enforcement is `complete()`'s validate/retry (`client.py`), which catches a malformed role output + retries (counts toward inter-part latency — C0.5). True server-side schema-constrained decoding is a separate, optional transport change.  ✅ by use (register_module reads declared OUTPUT_SCHEMA; a malformed first response caught + retried then validated, attempts=2)
- **C1.5 · Per-draw cache-key (NOT blanket VOLATILE — R1-FOLD F9).** A jury's N draws each get a distinct draw-id so they don't collapse at the memo gate — WITHOUT disabling `llm` memoization app-wide (memoization is a real app feature). Proven: a 3-run quorum returns 3 distinct generations; ordinary `llm` nodes still memoize. *(Scope, R2-FOLD H7: C0.2's replay-identical applies to ROUTING; a jury's DRAWS are intentionally varied — the verdict OVER them is then deterministic. No contradiction.)*  ✅ by use (a 'draw' config field = pure memo-key differentiator, not sent to model; 3 draws→3 distinct sigs→3 distinct generations @temp1.0; no-draw node still memo-hits on re-run; no scheduler edit)
- **C1.6 · Swarm telemetry batched + store writes atomic (R1-FOLD F8).** The swarm's per-role run-records do NOT fsync-flood `append_event` (one batched rollup per turn, not one fsync per role-fire); `memo_set`/`write_provenance` are atomic-ized like `set_ref`. Proven: a concurrent in-process store test; no event-log thrash under a full swarm.  ✅ by use (8-role wave → exactly 1 cognition.wave rollup containing all 8 records; memo_set + write_provenance routed through _fsync_atomic_write like set_ref)
  FORM (whole group) — the substrate stays one shared lower layer + two thin drivers (app `Suite.run` serial-governed, cognition `_run_swarm` concurrent-ephemeral); no parallel system; drift_acceptance passes.  ✅ by use (one substrate + two drivers held: parallelism only in cognition.py, scheduler.py untouched-serial, store/registry/contract not forked; drift 5/5✓; 18 suites green) — FORM-as-rendered (the cognition VIEW) is L-fe/G7, not this backend group

## G2 · Role registry (file-discovered, declarative, mode-scoped)

- **C2.1 · Roles are file-discovered registry data**, not a hardcoded dict. A role declares {id · prompt template · input addresses · output schema · trigger · model binding · mode-scope · rule(s) · render hint}. Adding a role = adding a file; it self-registers + is queryable.  ✅ by use (RoleRegistry mirrors NodeRegistry discover/rediscover; drop a file→discovered+queryable, remove→un-registers, malformed→raises, _-file→skipped; roles_acceptance 30✓)
- **C2.2 · The judge is a role in the registry** (role #0), bound to its resident-4B recommendation, unchanged in behaviour.  ✅ by use (roles/judge.py role#0; config byte-identical; fired through the registry: FINISHED 336ms / MORE 62ms / empty→no-call; e5_suite green)
- **C2.3 · The `listening` cast exists + fires:** focus · recall · ground · connect · check · voice (mode-scoped). Proven: in `listening`, these fire; in another mode, a different/empty cast.  ✅ by use (6-role cast fired concurrently via run_swarm: wall 0.613s vs sum 3.488s ≈5.7× concurrency; unknown mode→empty cast, no crash/no default-fire)
- **C2.4 · Jury/ensemble is first-class.** Any role may declare `draws: N` + a verdict rule (quorum/vote). Proven by use (C1.5). *(Caveat, E4 epistemic-monoculture: N draws on ONE model measure variance, not independent error — a correctness-jury that truly matters needs model diversity; the verdict-rule is designed so a 2nd small model / cloud tiebreak can slot in. v1 may accept single-model with the limit documented — Tim-fork F-a.)*  ✅ by use (roles/verify_jury.py draws:3 → 3 distinct sigs at run://turn/role#i + pure order-independent majority verdict; E4 single-model-variance caveat documented in-file, verdict-rule shape accepts a future 2nd-model tiebreak)
- **C2.5 · Roles bind models from the capability registry** (G8) — suitability is a query (`role.requires ⊆ model.provides`), not hand-written prose.  ◑ by use (the QUERY seam is built + proven: focus.requires=['chat','json']→resolves to resident provider; ['vision']→fails loud. Provider set today = resident chat-4b only; G8/L-model widens the catalog — query shape unchanged) — needs G8

## G3 · The rule engine (rich predicates over resolved values · the L2 core)

> **Rule-vs-role classifier (E3 — the unifier):** every combine/aggregate/route pattern decomposes by one test — deterministic over resolved values → a **rule** (the predicate grammar); needs model judgment → a **role** the rules wire. So vote/threshold/weighted-quorum/veto are rules; rank-then-fuse = rule-rank + a fuse *role*; generative MoA-aggregation = a role, quarantined off the spine. This keeps every aggregation option L2-legal by construction.

- **C3.1 · Full declared logic, with determinism ENFORCED not asserted (R1-FOLD F5).** A rule is declared logic over a role's output + may chain. The evaluator runs **post-barrier, as a pure function of fully-resolved address values only**, against a **referenceable-input whitelist** (resolved role outputs). BANNED in a rule: `now()`/random/wave-completion-order/partial-results/any model call. Proven adversarially: a rule that tries to read order/time/partials is rejected by the evaluator.  ✅ by use+adversarial (declared data-AST, restricted evaluator never eval/exec; RULE_OPS closed grammar — now/random/call/getattr/import are NOT ops; unknown-op→RuleError; live-4B e2e: role finish-order FLIPPED across turns, routing identical; spike injection_rule generalized to declared AST byte-identical)
- **C3.2 · A rule routes to any destination:** inject-into-reply · chain/trigger another role · land-at-address · surface-to-inbox/decisions · typed-lane/channel. All five demonstrated.  ✅ by use (inject/address land at run://; chain FIRED the real check role at the 4B; surface routed through real Suite.surface_review emitting ask resolved=None; lane = typed event. DESTINATION_KINDS={inject,chain,address,surface,lane} — resolve/approve/dispatch CANNOT be declared, claude-p floor by construction)
- **C3.3 · Routing is renderable** — every rule + its firing is addressable data the live view (G7) can draw.  ✅ by use (rule+firing are addressable as_record()/when_text; nesting past depth-6 fails loud) — edge-badge rendering itself is G7/L-fe
- **C3.4 · New/changed rules ride the normal change path** (no special gate; review/commit like any change).  ✅ by use (static AST whitelist-walk validate_role_rules runs at role discovery = the commit gate; malformed rule fails loud across all roles; drift_acceptance rides it; rules_acceptance 64✓)

## G4 · Staged-response queue (the reply as parts)

> **`THOUGHT_SHAPES` = ~5 archetypes, built once (E1 / E0-EXPLORE-SYNTHESIS):** `linear-stream` (voice) · `reduce-tree` (fan-out→`join`→one answer) · `jury-select` (N candidates→score→winner) · `scatter-route` (N classifications→own lanes, no reduce) · `scatter-write` (N consolidations→sinks, no reply). The four post-voice applications each instantiate one + force one of R1–R4 (jury · typed-lane · activation-budget · join/fanout) — so building them realizes the reshapes. Net-new shape fields: `archetype` · `fanout` · `join:<role>/*` barrier-dep · `render_from`. **Overlap-vs-between-parts is a per-role choice** (E3), warmed shared prefix makes re-prefill near-free.

- **C4.1 · Part grain follows the mode** (a config table: e.g. focus=line · listening=beat · explaining=paragraph). Proven: switching mode changes the grain.  ☐ by use
- **C4.2 · Part 1 fires from base context instantly**; later parts read the resolved values at the concurrent roles' **`run://<turn>/<role>`** addresses via the **net-new ref-read branch** (NOT `swarm://`; NOT the existing `_chat_context`/`_resolve_context_at`, which reads operator-notebook strata, not fresh role refs — R1-FOLD F3 / R2-FOLD H4).  ☐ by use
- **C4.3 · Conditional staging is mandatory** — a cheap brevity judge bypasses the whole machine for one-liners (mode-biased). Proven: a trivial turn does NOT spin the swarm.  ☐ by use
- **C4.4 · Coherence across parts** — each part carries the prior parts; the reply reads as one voice (not disjoint).  ☐ by use / needs-tim (feel)
- **C4.5 · Tools on the final part only** (intermediate parts pure generation) unless a shape declares otherwise.  ☐ by use

## G5 · Activation contexts (mode = the dial, generalised)

> **NET-NEW substrate, not "generalise mode" (R1-FOLD F7).** Repo sweep found NO activation substrate — zero `.timer` units, `background` is just a directive string. Background/sense/rollup are **three net-new subsystems** (a timer/scheduler for rollups · an event-hook for sense · an idle-loop for background), each net-new build, sequenced AFTER per-turn (C5.1) works, each under a mode's slot budget.

- **C5.1 · Per-turn** cognition (the live reply) works (the spine of G0–G4).  ☐ by use
- **C5.2 · Background** cognition fires between turns (consolidating/preparing) under a mode's budget.  ☐ by use
- **C5.3 · Sense-triggered** cognition fires on screen/app/state changes (an activation trigger, not a user turn).  ☐ by use
- **C5.4 · Rollups** fire on schedule (the introspective-data-building loop — the swarm's own run-records consolidated).  ☐ by use
- **C5.5 · Mode allocates** the slot budget + the active cast + whether/when to stage across all contexts.  ☐ by use

## G6 · Voice coupling (streams as it thinks)

- **C6.1 · Each completed part is the TTS streaming unit** — synth part N while the brain generates part N+1 (overlap brain↔TTS). Proven: audio of Part 1 plays before Part 2 is generated.  ☐ by use
- **C6.2 · The `/api/voice/stream` circuit consumes a sequence of parts** (not one full reply); in-order playback + iOS unlock + trial recording preserved.  ☐ by use / needs-tim (on-device)

## G7 · The live cognition view (in the first build)

- **C7.1 · The per-turn thought-graph renders on the canvas** — roles as nodes (status: latent/firing/ran/injected/failed), chains as edges, injections as edges into the brain/reply node. Driven by `cognition.*` SSE events, reflects-never-owns.  ☐ by use
- **C7.2 · Live + addressable** — the RHM can read its own cognition via the same addressed data (`ui://cognition/<turn>`).  ☐ by use
  FORM — design-system components + tokens, navigable not a wall, responsive, design-critic graded.  ☐ design-rubric / needs-tim

## G8 · Model + capability registry (config by type)

- **C8.1 · `MODEL_CAPABILITIES` keyed by model-id** (tool-calling · json_schema · thinking · context-ceiling · concurrency-knee · speed), provenance declared/probed/measured/served (live probe wins).  ☐ by use
- **C8.2 · The JOIN** — a role binds a model-id → reads capabilities → if locally served, looks up the backing service for VRAM via `gpu.py` (reuse the resource-manager, never duplicate).  ☐ by use
- **C8.3 · Cloud decoupled** — the swarm always runs resident; the main brain is separately selectable (resident or cloud); a mode can auto-pick cloud; cloud can run background roles. The swarm is never lost by a cloud choice.  ☐ by use
- **C8.4 · Residency fail-loud** — model not resident when needed → surface + offer to load (no silent degrade).  ☐ by use

## G9 · Governance & safety (binds everything)

- **C9.1 · Roles act only within the existing governance posture** — in permitted modes a role may trigger reversible/AUTO-class actions (like `decide-for-me`); never bypasses the deterministic gates.  ☐ by use (incl. adversarial: a role cannot escalate past its posture)
- **C9.2 · The `claude -p` floor as an unforgeable-event INVARIANT + a regression test (R1-FOLD F6).** Restated precisely: **no role path may emit a `resolve`/`approve` event** (the sole dispatch trigger; today only the operator-only `resolve_surfaced` emits it). A regression test asserts no role/`_run_swarm` path can emit it — so the floor holds even if a future role-reachable AUTO verb is added. Adversarially verified.  ☐ by use
- **C9.3 · Fail loud everywhere** — a down model, a starved turn, a malformed output, a bad rule, a missing reference (a rule's `run://` dep pruned/failed → fail-loud or declared `on_missing`, never implicit truthy) → loud legible surface, never a silent swallow.  ☐ by use
- **C9.4 · Self-description + drift homes for every net-new registry (R2-FOLD H5 — gates fan-out).** Each net-new registry — roles · the capability registry · edge-kinds · rules · thought-shapes · activation-contexts · the `cognition.*` event kinds (runtime event-strings, NOT a `contracts/` contract) — declares its self-description home and a `drift_acceptance` assertion, so drift has something to check. No net-new registry ships without its drift home.  ☐ by use

## PRODUCT-FACE group (FORM across all surfaces)
- **CF.1** — the cognition view + any settings for roles/rules/modes are on the design system (components + tokens), consolidated, non-overlapping, legible on mobile (390px), navigable-not-text. Design-critic graded across every surface this build adds.  ☐ design-rubric / needs-tim

---

## Priority order (dependency — foundations first)
1. **G0 spike** (gate — nothing fans out until it passes)
2. **G1 substrate** (the make-or-break; the parallel executor + slot budget + edge-types + schema + volatile gate everything)
3. **G2 role registry** + **G3 rule engine** (the declarative core; depend on G1)
4. **G4 staged queue** (depends on G1–G3) → **G6 voice coupling** (depends on G4)
5. **G8 model/capability registry** (parallel to G2/G3; the binding substrate)
6. **G5 activation contexts** (depends on G4 working per-turn; then broadens)
7. **G7 live view** (in first build; depends on the `cognition.*` event contract from G1–G4)
8. **G9 governance** + **Product-Face** (cross-cutting; verified throughout, not last)

*Parallelism note (per B5): this is mostly a SERIAL SPINE on `runtime/suite.py` (+`bridge.py`) — G0→G4 — flanked by 3 genuinely-disjoint parallel lanes (the transport `json_schema`, the `llm`-volatile node fix, the canvas render FE for G7). 32-way parallel cognition ≠ 32-way parallel build.*
