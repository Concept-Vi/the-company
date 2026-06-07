# Concurrent Cognition — Completion Criteria

*The truth table for the build. Document 1 of the loop-prep triad (see also the Implementation Guide + Research Synthesis). Every criterion is two-faced — FUNCTION and FORM — and green only when BOTH are verified by USE. This is the common reference the sub-agent-driven build reads; it is registry-driven by Tim's law L1, rule-based-routing by L2 (see `DECISIONS.md`).*

> **⚠ Hardened by Round-1 review — `review/R1-FOLD.md` is the binding correction layer.** Key folds woven below: the **resource ceiling is real** (the resident 4B serves `max_num_seqs=16`, KV shared with the main 64K context → the true co-resident swarm cap is **well below 32 at usable context**; "32" was a 4K-context throughput number, not the voice config); **parallelism lives in the cognition driver, not the shared scheduler**; **addressing is `run://` throughout** (never `swarm://`); **injection, `chat_parts`, the activation substrate, and the jury flow are NET-NEW** (not free reuse); **rule-determinism and the `claude -p` floor are enforced invariants with tests**, not assertions. Locate code **by symbol** (the line refs drifted ~+14).

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
  FUNCTION — a real utterance → `focus` fires → Part 1 emits from base context instantly → one auxiliary role (`recall` or `ground`) runs concurrently, writes structured JSON to an address → its rule injects into Part 2's context → Part 2 emits enriched → both parts stream as one reply. Demonstrated by use (the event log shows the role fire, the injection, the two parts).  ☐ by use
- **C0.2 · Routing is rule-based + deterministic — tested on a NON-TRIVIAL rule (R1-FOLD F5).** A *declared rule* (one that reads multiple resolved fields, not a one-liner) resolves a `run://` address; re-running identical inputs routes identically — even though the wave's roles finished in nondeterministic order. Proven: run twice → identical routing trace, with the rule reading values that completed in different orders.  ☐ by use
- **C0.3 · The 4B-as-aggregator question, answered.** If the spike includes a fusing role (combine 2 role outputs), measure whether the 4B's fused result is coherent; if routing-only suffices (per L2), record that aggregation is optional. → `needs-tim` on quality; FUNCTION = it runs.  ☐ by use / needs-tim
- **C0.4 · No starve, fail loud.** The main stream keeps its reserved slots; if the resident model is down, the turn fails loud + offers to load (never silent).  ☐ by use
- **C0.5 · MEASURE the real resource ceiling (the gate that matters most — R1-FOLD F1).** On the actual co-resident voice config (4B @ util 0.49 + the 4-bit voice resident), with a staged main reply running, MEASURE: how many concurrent role-runs actually serve before latency thrashes (bounded by `max_num_seqs=16` AND KV/per-role-context), and the real **inter-part wall-clock** (slowest dep role + JSON-retries). The spike must PRODUCE these numbers — not assume 32. The swarm cap is then `min(max_num_seqs−R, KV-budget/per-role-ctx)` from the registry.  ☐ by use (measured)

*Spike passes → fan-out unlocks. Spike fails → redesign before building further. (Per R1-FOLD: as originally worded G0 could pass without testing the thing most likely to break — C0.5 fixes that.)*

## G1 · Node-mechanism substrate rebuild (THE make-or-break · serial spine)

> The dual-use spine (app surface + cognition). Full registry-driven rebuild (Tim: "full substrate now"). The concurrent executor is the one genuinely net-new engine piece.

- **C1.1 · Concurrent dispatch in the COGNITION DRIVER (not the shared scheduler — R1-FOLD F2).** Parallelism is a property of `_run_swarm` / the in-turn part runner, leaving the app's `Suite.run` serial (no behaviour change to the governed app face). It first builds a **materialized ready-set** (the scheduler is a re-scanning loop today, no ready-set), then dispatches it via a thread pool; store writes serialize safely behind the wave barrier. Proven: N independent role-runs run in ~max(role) not ~sum(role); a concurrent app `Suite.run` is unaffected.  ☐ by use
- **C1.2 · Request-concurrency budget from the REAL registry values (R1-FOLD F1).** The semaphore = `min(max_num_seqs − R, KV-budget / per-role-context)` read from the registry — **NOT a hardcoded/assumed 32** (`max_num_seqs=16`; KV is shared with the main context). Roles are short-context so many fit. Reserve R for the main stream/judge. Proven: the measured-max concurrent role-runs (C0.5) complete; the main stream never blocks AND never just waits in vLLM's admit queue behind the swarm.  ☐ by use
- **C1.3 · Edge type system + the injection edge (NET-NEW read — R1-FOLD F3).** Edges carry a declared `kind` (data-wire · **injection** · gate/branch · fan-in) — not a bare wire. Adding `kind` to `contracts/node_record.py` is a **CONFIRM-level contract edit** (bump `schema_ver`; default-kind for existing edges; vault-spec update). The injection edge is a **net-new ref-read branch** in part-context assembly (the existing `_resolve_context_at`/`_r2_gather` reads operator-notebook strata, NOT fresh role refs — it does NOT do this). Role outputs live at **`run://<turn>/<role>`** (never `swarm://` — not a registered scheme). Proven: a later part reads the resolved value at a role's `run://` address.  ☐ by use
- **C1.4 · Output schema enforced via client-side validate/retry (R1-FOLD F9).** The transport sets `json_object` (valid JSON, not schema-conformant); enforcement is `complete()`'s validate/retry (`client.py`), which catches a malformed role output + retries (counts toward inter-part latency — C0.5). True server-side schema-constrained decoding is a separate, optional transport change.  ☐ by use
- **C1.5 · Per-draw cache-key (NOT blanket VOLATILE — R1-FOLD F9).** A jury's N draws each get a distinct draw-id so they don't collapse at the memo gate — WITHOUT disabling `llm` memoization app-wide (memoization is a real app feature). Proven: a 3-run quorum returns 3 distinct generations; ordinary `llm` nodes still memoize.  ☐ by use
- **C1.6 · Swarm telemetry batched + store writes atomic (R1-FOLD F8).** The swarm's per-role run-records do NOT fsync-flood `append_event` (one batched rollup per turn, not one fsync per role-fire); `memo_set`/`write_provenance` are atomic-ized like `set_ref`. Proven: a concurrent in-process store test; no event-log thrash under a full swarm.  ☐ by use
  FORM (whole group) — the substrate stays one shared lower layer + two thin drivers (app `Suite.run` serial-governed, cognition `_run_swarm` concurrent-ephemeral); no parallel system; drift_acceptance passes.  ☐ design-rubric

## G2 · Role registry (file-discovered, declarative, mode-scoped)

- **C2.1 · Roles are file-discovered registry data**, not a hardcoded dict. A role declares {id · prompt template · input addresses · output schema · trigger · model binding · mode-scope · rule(s) · render hint}. Adding a role = adding a file; it self-registers + is queryable.  ☐ by use
- **C2.2 · The judge is a role in the registry** (role #0), bound to its resident-4B recommendation, unchanged in behaviour.  ☐ by use
- **C2.3 · The `listening` cast exists + fires:** focus · recall · ground · connect · check · voice (mode-scoped). Proven: in `listening`, these fire; in another mode, a different/empty cast.  ☐ by use
- **C2.4 · Jury/ensemble is first-class.** Any role may declare `draws: N` + a verdict rule (quorum/vote). Proven by use (C1.5).  ☐ by use
- **C2.5 · Roles bind models from the capability registry** (G8) — suitability is a query (`role.requires ⊆ model.provides`), not hand-written prose.  ☐ by use

## G3 · The rule engine (full declared logic · the L2 core)

- **C3.1 · Full declared logic, with determinism ENFORCED not asserted (R1-FOLD F5).** A rule is declared logic over a role's output + may chain. The evaluator runs **post-barrier, as a pure function of fully-resolved address values only**, against a **referenceable-input whitelist** (resolved role outputs). BANNED in a rule: `now()`/random/wave-completion-order/partial-results/any model call. Proven adversarially: a rule that tries to read order/time/partials is rejected by the evaluator.  ☐ by use
- **C3.2 · A rule routes to any destination:** inject-into-reply · chain/trigger another role · land-at-address · surface-to-inbox/decisions · typed-lane/channel. All five demonstrated.  ☐ by use
- **C3.3 · Routing is renderable** — every rule + its firing is addressable data the live view (G7) can draw.  ☐ by use
- **C3.4 · New/changed rules ride the normal change path** (no special gate; review/commit like any change).  ☐ by use

## G4 · Staged-response queue (the reply as parts)

- **C4.1 · Part grain follows the mode** (a config table: e.g. focus=line · listening=beat · explaining=paragraph). Proven: switching mode changes the grain.  ☐ by use
- **C4.2 · Part 1 fires from base context instantly**; later parts resolve `swarm://` addresses written by concurrent roles (injection = address-resolution via the existing `_chat_context` path).  ☐ by use
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
- **C9.3 · Fail loud everywhere** — a down model, a starved turn, a malformed output, a bad rule → loud legible surface, never a silent swallow.  ☐ by use

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
