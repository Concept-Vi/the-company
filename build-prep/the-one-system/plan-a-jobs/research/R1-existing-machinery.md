# Plan A research · R1 — the five job-shaped mechanisms, inventoried (2026-07-02)

*Direct-read inventory (file:line evidenced) of flows/routines/cascades/graphs/activation + the cognition
primitives, CLI, and the cross-cutting registry/run-record/floor/faces patterns — the substrate Plan A
unifies. Produced by a research agent; report verbatim below. Companion: R2-external-patterns.md.*

All eight areas inventoried by direct read. Everything below is **Observed** (file:line) unless marked otherwise.

# INVENTORY: the five job-shaped mechanisms (input to Plan-A unification)

Frame read: `build-prep/the-one-system/JOBS-AND-COORDINATES-PLAN.md` §Plan-A (a JOB = data row: what-to-run × params × trigger × allocations × outputs; trigger registry = the auto-run system; heartbeat = row #1).

---

## 1. FLOWS — repo-committed production lines (9 rows)

**Row shape** — `runtime/flows.py:38` `FLOW_FIELDS = ("id", "label", "description", "params", "proposes_only")`, all REQUIRED; `id == file stem` enforced at `flows.py:97-99`.

**Param declaration** — `params = {name: {"desc": str, "default": <value-or-None-if-required>}}` (`flows.py:29-30`). `Flow.run(**params)` fails loud on unknown names (`flows.py:53-57`) and on missing no-default params (`58-62`), merges defaults (`63-64`). This is the only mechanism with true declared, validated, defaulted params-as-data.

**The proposes_only floor, 3 enforcement layers:**
- Discovery refuses `proposes_only is not True` (`flows.py:100-102`).
- Source-invariant scan: `tests/cognition_governance_acceptance.py:103` folds every `flows/*.py` into `COG_SOURCES`; check C9.2 at `:123-125` asserts the floor covers "loader + every flows/<id>.py row".
- MCP `flows(op='propose')` gates a proposed `body` — "a body touching operator verbs or process launches refuses immediately", clean ones SURFACE for operator approval (`mcp_face/tools/flows.py:27-30, 57-61` → `suite.propose_flow`).

**All 9 rows** (from each file's `FLOW` dict; params → defaults):
| id | does | params |
|---|---|---|
| `cc_registry_refresh` | CC binary version-stamp diff → re-introspect capability surface | discover_fn, executable (both required) |
| `dragnet_extract` | proposes a dragnet bake (surfaces ONE inbox item; does NOT run it) | out_name='full', projects, since, until, design=False |
| `drift_radar` | semantic built-twice/doc-drift sweep over embedded repo corpus | — |
| `floor_walk` | stranded-work/unmounted-component/stale-decision sweep | stranded_after_s=7200, stale_decision_days=7, surface=1 |
| `pattern_cluster` | failure-pattern REDUCE over mined history | — |
| `registry_generation` | grounded mockup→dossier chain, bounded batches | time_budget_s=420 |
| `repo_ingest` | repo → embedded 'repo' corpus keyed `code://<path>` | max_files=60, root='.' |
| `transcript_mine` | transcripts → history memory space | time_budget_s=420, max_mb=20 |
| `ts_backfill` | deterministic ts_source re-stamp on history records | budget=600 |

**Invocation** — `flows(op='run', flow=, params=)` (`mcp_face/tools/flows.py:62-65`); registry fresh-discovered per call (`:41`), repo-root-anchored (`flows.py:74-75` — a cwd-relative default once silently returned []).

**What a flow CAN'T do:** be authored through the MCP (repo-committed only — `flows.py:15-17`), resolve/approve/dispatch, launch `claude -p`, be triggered (no schedule/change/event arm), or chain to another flow/cascade/routine (chaining is only whatever its Python body composes).

## 2. ROUTINES — prompt-driven Claude-Code tasks (5 rows)

**Row shape** — `runtime/routines.py:33-51` `ROUTINE_FIELDS` closed set of 12: `id, prompt` (required) + `label, description, cwd, model, permission_mode` (default "plan"), `cadence, repeats, goal, done_when, max_turns, trigger` (free-text descriptive). Unknown field FAILS LOUD (`:136-140`). **No params** — the prompt is a fixed string (a `prompt_override` exists in `routine_runner.build_spawn_body` `:38` but is NOT exposed on the MCP op=fire).

**How they run** — always by driving a REAL session, never in-process: `runtime/routine_runner.py:1-18` — `fire()` POSTs `/spawn {cwd, prompt, model, permission_mode, name:"routine:<id>", source:"routine"}` to the session-supervisor (`127.0.0.1:8771`, `COMPANY_SUPERVISOR_BASE`), watches `/watch` for the turn's done event, `/teardown`, returns run record `{routine_id, claude_session_id, result, is_error, ts, ...}`.

**Firing arms:**
- MCP `routines(op='fire')` (`mcp_face/tools/routines.py:61-72`) — flagged "the consequential verb of this tool" (`:41` — spawns a real `claude -p`).
- systemd: `runtime/routine_schedule.py` renders per-routine `.service` (oneshot, `python -m runtime.routine_runner <id>`) + `.timer` (`WantedBy=company.target`), **GENERATES-NOT-ARMS** (`tests/routine_schedule_acceptance.py` check 11: emits `arm_command`, never enables). Reality: only 2 generated units exist (`ops/systemd/generated/company-routine-{completion_poke,self_status}.*`) and **neither is active** — `systemctl --user list-timers` shows only `company-agent-sessions-exporter.timer` + `company-claude-sessions-reindex.timer`. No routine appears in `ops/services.json` (`"group": "jobs"` count = 2, neither a routine).

**Cadence grammar** — `OnCalendar=...` or `every:<seconds>` (`routines.py:41-43`); `every:N` → `OnUnitActiveSec`/`OnBootSec` (acceptance check 5). Note `launch-surfaces` declares `cadence: "manual (op=fire)"` — valid as a string, unschedulable by the generator (fail-loud `_timer_directive`).

**All 5 rows:** `completion_poke` (every:1800, repeats, max_turns 12, permission "default"), `dragnet_freshness` (every:86400, repeats), `guide_freshness` (every:86400, repeats), `launch-surfaces` (manual, cwd `~/repos/counterpart/design`), `self_status` (OnCalendar daily 09:00, plan-mode, 1 turn). Goal-loop: `repeats` + `done_when` (substring or `/regex/`) — `routines.py:44-48`, `tests/routine_goal_loop_acceptance.py`.

## 3. CASCADES — declarative chains AS DATA (8 saved rows)

**Storage** — `.data/store/cascades.json` via `_ActionRegistry` (`runtime/suite.py:389-396`); survives reload; validation is the ONE door `coherence_actions.build_action` (`suite.py:1229-1253` — no-name/no-steps/unknown-op/non-registry-model all refuse at save).

**Decl vocabulary** (`mcp_face/server.py:970-997` + runner `runtime/cognition.py:2644-2990`): `{name, steps:[...], output_schema?, shared?}`. Per step:
- `op`: generate|embed|reduce (+ similarity/retrieve/detect "declared but not yet runnable" — `server.py:977-978`)
- `kind` (primitive selector): **role** (1→1) | **items** (MAP 1→N) | **reduce** (JOIN N→1, modes role|rule|cluster) | **retrieve** (role-less corpus RAG, `space`/`k` — `cognition.py:2755`) | **check** (role-less deterministic gate from the checks registry, `on_fail: flag|drop`, drops recorded, empty-thread fails loud — `:2794-2853`) | **jury** / **panel** (judgment steps — `:2856-2900`)
- `model` (per-step, validated ∈ live registry), `max_tokens` (per-step budget), `fan_field` (mid-chain fan-out: explode one upstream output's list field — `:~2950`), `items` (explicit unit list), `unit_ctx` (per-unit templated inputs)
- `shared` resolve-once block: exactly one of `{address | text | corpus_query}` per entry, resolved ONCE, fed to every step (`:2698-2725`)

**The seam** — step 0 reads `run_cascade(inputs)`; step N reads N−1's `run://` address(es); cardinality explicit per kind; outputs step-index-keyed `run://<turn>/<i>-<role>` so shared roles never overwrite (`:2671-2683`). Every step persisted + op.run-indexed.

**The 8 saved rows:** `verify-jury` (items verify_lens → verdict-tally), `option-panel` (items develop_option → role-reduce score_options), `spec-compiler` (decompose_seed → items expand_criterion → items ground_criterion → triad_synth, 4 steps), `ask-the-codebase` (retrieve → reduce_synth), `eval_digest_reduce`, `eval-cascade-probe` (tally-by:intent), `eval-classify-flow` (tally-by:label), `eval_registration_gauntlet` (tally-by:grounded).

**Can't:** triggers, loops, general branching (check flag/drop is the only conditional), agent work, calling a flow/graph/routine.

## 4. GRAPHS — node-graph canvases (73 stored)

**What execution is** — `run_graph` MCP (`server.py:168`) → `Suite.run` (`suite.py:1904`, wrapped in `guard("run")` — the POLICY router) → `runtime/scheduler.py:37`: fixpoint loop; a node fires when every declared input port is wired AND resolved; **memoized** (identical config+inputs → cached; `llm`'s `draw` config is a deliberate per-draw cache-key breaker); per-node error isolation → `failed` dict; unresolvable → `stuck`; `portal` nodes are reference-resolved, never fired. Outputs land `run://<graph>/<node>[@branch]`.

**Node-type vocabulary — 16 types** in `nodes/`: ask, codebase, constant, embed, gate, join, llm, model_of_tim, pair, portal, retrieve, rhm_mode, similarity, titlecase, uppercase, wordcount. Registry `runtime/registry.py:75-90`: each declares `PORTS_IN/PORTS_OUT` (typed, e.g. `"Text"`), `CONFIG` (the inspector-rendered param schema — e.g. `nodes/llm.py` CONFIG: model/base_url/system/temperature/max_tokens/top_p/retries/timeout/draw), optional `OUTPUT_SCHEMA`, `KIND`, `VERSION`. Type-graph queries `produces()/consumes()` (`registry.py:93-97`).

**Params/ports** — params are per-node `config` via `set_config(graph, node, config)` (`server.py:160-164`); no graph-level parameter surface.

**Graphs CANNOT call roles/flows/cascades** — grep of `nodes/*.py` for `run_role|resolve_role|cognition`: **0 matches**. Model access in `llm`/`ask` goes straight to `fabric.client` (their own config slot), a parallel model path beside the role system.

## 5. ACTIVATION — the always-on caller (built, dormant)

**Context registry** — `runtime/activation.py:64-106` `ACTIVATION_CONTEXTS`, **4 rows** with declared trigger kinds: `per-turn` (trigger "turn", owned by chat/chat_parts), `background` ("idle-loop"), `sense` ("event-hook"), `rollup` ("timer", read-half, fires no swarm). Modes allocate which are live + slot budget; `fire_activation` fails loud on unallocated context (`:172-175`) or `reserve_r < FLOOR_RESERVE_R=2` (`:52, 176-180`).

**Entry points** — `fire_activation` (`:141`) fires the mode's cast via `run_swarm` and routes outputs through declared rules over `DESTINATION_KINDS`; `consolidate_rollup` (`:247`) aggregates `cognition.wave` telemetry → `run://rollup/<id>`.

**Drivers** — `background_tick` (`:426`, idle gate `DEFAULT_IDLE_SECONDS=90`; `OPERATOR_ACTIVITY_KINDS` = 11 event kinds `:361-364`); `sense_tick` (`:458`, fails loud on fabricated events); `RollupDriver` held cursor (`:490`); `detect_mode_candidate`/`propose_mode` (`:559, 586`).

**What a 'rule' is here — two distinct kinds:**
1. **Mode-detection rules** — file-discovered `mode_detection_rules/` registry, **3 rows** (background prio 10, focus prio 20, listening), each `{id, candidate, why, priority, when}` where `when` is a declared data-AST over `rules.RULE_OPS` (`op: and/ne/lt/eq/field/lit` — see `mode_detection_rules/focus.py`), evaluated pure over the `activity_signal` snapshot. First-match-wins by priority.
2. **Role routing rules** — roles declare `rules` (ROLE_FIELDS) routed over the **five** `DESTINATION_KINDS` (`runtime/rules.py:119-132`): `inject, chain, address, surface, lane`; `FORBIDDEN_DESTINATION_VERBS = ("resolve","approve","dispatch")` asserted structurally (`:136`). Note `chain` = "trigger a dependent role" — the ONLY cross-unit trigger vocabulary in the whole system, and it fires roles only.

**Doors** — `POST /api/activation/tick` (`runtime/bridge.py:93, 3077-3085`): drives ONE orchestrated tick on the module-level `ActivationCaller` (always background_tick + RollupDriver.tick + propose_mode; sense only with a real supplied `sense_event` in the POST body). Always live. The **autonomous loop** is dormant behind `COMPANY_ACTIVATION_LOOP` (`runtime/activation_driver.py:84-95`, default OFF, call-time read), cadence `COMPANY_ACTIVATION_TICK_S` default 60s (`:98-104`), spawned only by `maybe_start_activation_loop` (`:278`). **Activation has NO MCP tool** (only a mention inside `cognition_info`'s section list, `server.py:428`).

## 6. Cognition-engine primitives (the vocabulary a job composes)

`runtime/cognition.py` (3063 lines): `run_role` (:313, 1→1), `resolve_address` (:1138), `run_swarm` (:1451 — fires a cast concurrently under SlotBudget, emits `cognition.wave`), `run_items` (:1599, MAP), `run_jury` (:2125, N varied draws → deterministic `verdict_rule`), `REDUCE_RULES` (:2360, single-source both faces) + `resolve_reduce_rule` (:2386, incl. parameterised `tally-by:<field>`), `run_reduce` (:2398, role|rule|cluster), `run_cascade` (:2644), plus `run_panel` (fired by cascade panel steps).

MCP wrappers add the config axes: `run_role` (`server.py:690`) — `op=generate|embed`, `model` override with automatic endpoint routing (:770-780), address-valued `inputs` resolution, `policy` (generation-policy repetition-penalty ladder), `think` (per-run reasoning switch), `coordinate`, `ensure/ensure_evict` (gated resource actuator); `run_draft`/`run_draft_items` (:819, :875) — ephemeral inline role specs, tempdir-loaded, never committed; all funnel through `_fire_role_and_persist` (:736) → persist `run://<turn>/<role>` + ONE `op.run` record.

**Role row shape** — `runtime/roles.py:85` `ROLE_FIELDS` (29 fields): `id, label, description, prompt_template, prompt_slot, output_schema, schema_slot, input_addresses, op, trigger, model_binding, mode_scope, rules, render_hint, draws, verdict_rule, knobs, thinking, output, tools, context` + 8 legacy flat binding fields (`default_model` etc.). **38 roles** in `roles/`. Note roles already carry a descriptive `trigger` field and `knobs` (per-request max_tokens/temperature).

## 7. The CLI (`ops/cli/app.py`)

Verbs: `status/up/down/restart/logs · gpu/health/suites · models/swap/ensure/config · combos/bench/telemetry · session (list/new/send/stop over the supervisor) · help`. **Zero flow/routine/cascade/graph verbs** (grep "routine" in `ops/cli/*.py`: 0 hits). Job-adjacent surface: services.json's `jobs` group (2 rows, the only live timers — sessions-exporter + sessions-reindex); `company up <key>` arms a timer; the routine schedule generator emits a services.json entry for arming (acceptance check 10) but none is wired today.

## 8. Cross-cutting

**Registry discovery — ONE pattern, one exception.** File-discovered, id==filename, fail-loud-on-malformed, fresh-rediscover: flows/, routines/, roles/, nodes/, mode_detection_rules/, plus checks/verdict_panels/generation_policies referenced from the cascade runner. The exception is **cascades: JSON rows in the store, data-authored through the MCP** — the only existing proof that "a registered runnable = a data row an agent writes through the face" (exactly Plan-A's job-row shape).

**Run records.** One append-only event log; `Suite.emit_run_record` → `kind='op.run'` with duration + conditions (`suite.py:736-747`); `ENGINE_RUN_OPS` closed set = run_role/run_items/run_reduce (`suite.py:~788`); `runs(op='list'|'find')` MCP projection; `run_stats` rollups (:749). But coverage is uneven: cascade steps YES (per-step op.run); graph runs a different `kind='run'` event + `run://<graph>/<node>`; flows only whatever their internals emit (no job-level record); **routine runs are returned to the caller, never landed in the op.run index**; activation emits `kind='activation'` + `run://rollup/<id>`.

**Floor model.** Flows: `proposes_only` (3-layer). Cascades/graphs/roles: `run://` computation, no resolve/approve/dispatch, no `claude -p`; `surface` destination → `surface_review` `ask` event (resolved=None), only operator `resolve_surfaced` emits `resolve`; graph run rides `guard()`'s policy router. Routines: the one consequential mechanism (spawns real `claude -p`), bounded by `permission_mode` (default plan) + max_turns. Activation: floor by construction (destinations exclude forbidden verbs) + env dormancy.

**Three faces.** MCP: flows·routines·save/list/run_cascade·list/run_graph+node/connect/set_config/get_state/get_results·run_role/items/reduce/draft·runs·capabilities(section='chains' — `server.py:322-330,346` joins flows+cascades in one answer; activation absent). UI/bridge: `/api/flows`, `/api/routines`, `/api/cascades` exist (`bridge.py:1631-1640`, "FACE-4 pilot") but **no frontend consumer found** (grep js/ts/html outside build-prep: 0); graphs are the only mechanism with a full UI (canvas); `/api/activation/tick` is POST-only. CLI: services/timers only.

---

# (a) Capability matrix

| | **flows** (9) | **routines** (5) | **cascades** (8) | **graphs** (73) | **activation** (4 ctx + 3 rules) |
|---|---|---|---|---|---|
| params-as-data | ✅ declared+validated+defaults | ❌ fixed prompt | ◐ `inputs` for step 0 only; decl baked | ◐ per-node config, no job-level params | ◐ mode allocation only |
| triggers | ❌ manual MCP only | ◐ cadence string; timers generated-NOT-armed; op=fire | ❌ manual | ❌ manual | ✅ 4 declared kinds (idle/event/timer/turn); loop dormant |
| chaining | ◐ inside Python body only | ❌ | ✅ declarative steps + fan_field | ✅ typed-port DAG | ◐ rule `chain` → one role |
| conditions | ❌ | ◐ done_when goal-predicate | ◐ check steps (flag/drop) | ◐ gate node + port readiness | ✅ data-AST rules over activity_signal |
| model-work | ✅ composes primitives | indirect (session's model) | ✅ roles | ✅ but via a PARALLEL fabric path, not roles | ✅ fires the cast |
| agent-work (claude -p) | ❌ forbidden | ✅ (the whole point) | ❌ forbidden | ❌ | ❌ forbidden |
| MCP face | ✅ `flows` | ✅ `routines` | ✅ save/list/run | ✅ 8 tools | ❌ none |
| UI face | ◐ /api/flows (unconsumed) | ◐ /api/routines (unconsumed) | ◐ /api/cascades (unconsumed) | ✅ full canvas | ◐ POST tick only |
| CLI face | ❌ | ◐ (generated units → routine_runner CLI) | ❌ | ❌ | ❌ |
| run-records | ◐ own summary dict | ◐ returned record, NOT indexed | ✅ per-step op.run + run:// | ◐ `kind='run'` event, separate shape | ◐ activation events + rollup address |
| floor | proposes_only ×3 layers | permission_mode + max_turns | run:// only | guard() policy | destinations-by-construction + env gate |

# (b) Gaps the unified job system must fill

1. **No trigger registry.** Triggers exist as: 2 unarmed generated timers, 4 hardwired activation context kinds, a dormant env-gated loop, and free-text `trigger` fields on routines/roles. **Change-triggers (the heartbeat's own kind) exist nowhere.** Nothing lets an agent register "when X, run Y" as data.
2. **Params-as-data only in flows.** Routines have zero parameterisation (the runner's `prompt_override` isn't even surfaced); cascades bake everything but step-0 inputs; graphs have node config, not job params.
3. **No cross-mechanism composition.** A cascade can't call a flow/graph/routine; a graph node can't fire a role; rule `chain` fires only roles; the "what to run" enum of Plan-A (flow|cascade|graph|role|agent-prompt) has no single dispatcher.
4. **Agent-work is fenced into routines.** No chain can include a `claude -p` step under the floor; jobs needing model-work + agent-work must span two mechanisms with no seam.
5. **No unified run row.** Five different record shapes (op.run / kind='run' / returned dict / activation event / flow summary); a "job" has no discoverable run history spanning them.
6. **The scheduler doesn't exist as a live thing.** Everything is generates-not-arms or dormant-by-default; there is no armed cadence anywhere for the job mechanisms (only the two ops timers). The unified system needs ONE armed tick (the ActivationCaller is the obvious host).
7. **Face asymmetry.** Cascades are data-authorable via MCP; flows are repo-only; graphs UI-only-ish; activation faceless. A job row must be registered + discovered + fired through the SAME MCP/UI faces regardless of its executor.
8. **Duplicated model path.** Graph llm/ask nodes bypass the role system entirely (own model/config slots) — unification must not inherit two model doors.

# (c) Top-5 reuse-don't-fork opportunities

1. **`cognition.run_cascade` as the chain executor** (`cognition.py:2644`). It already has output→input threading, per-step model/budget, fan-out, deterministic gates, jury/panel, persistence + op.run indexing, injected resolvers (engine-pure). A job's "chain" body should BE a cascade decl; extend its step vocabulary (add `flow`, `agent-prompt` step kinds) rather than building a job runner.
2. **The mode_detection_rules/ registry as the trigger-registry template.** `{id, priority, when: data-AST, candidate}` + `rules.validate_ast`/`rules.evaluate` over `activity_signal` is already "configurable condition rows walked deterministically" — swap `candidate: mode` for `job: id` and the trigger registry exists. The AST + fail-loud discipline come free.
3. **`ActivationCaller` + `/api/activation/tick` + `COMPANY_ACTIVATION_LOOP` as the auto-run heartbeat.** One stateful tick, held cursors, manual door always live, autonomous cadence operator-armed. Add "walk the trigger registry, fire due jobs" as a fourth driver inside `activation_tick` — no second scheduler.
4. **`routine_runner.fire` + the session-supervisor as the agent-work primitive**, and `routine_schedule.render_units` for real OS timers (keeping generates-not-arms). This is the only proven `claude -p` circuit; jobs of kind agent-prompt should call it, with `prompt_override` finally exposed as the params seam.
5. **The cascades.json `_ActionRegistry` + `build_action` one-door validation + the op.run index + `run://` addressing** as the job-row substrate: jobs persisted as validated data rows (the cascade precedent proves agents can author rows through the face under a validation door), every fire an `op.run` record with conditions, `runs`/`run_stats` discovery free. The floor transfers as-is: propose/surface for anything consequential; operator resolve stays the only apply.

One flag for the design wave: `flows` and `cascades` already state their intended split in-code — "flows stage, cascades declare" (`cognition.py:2704-2705`) — so the unified system arguably needs to absorb flows as *setup/staging steps* of jobs, not as a sixth peer.
