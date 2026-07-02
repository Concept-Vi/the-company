# Plan A design · take 1 — the SUBSTRATE-MINIMALIST lens (2026-07-02)

*One of three independent design perspectives (D1 this · D2 asset-first · D3 agent-experience).
Maximum reuse, smallest new-code bill. Report verbatim below.*

The substrate is read — R1/R2, the north star, the rules AST (`runtime/rules.py` RULE_OPS + MAX_RULE_DEPTH), the `_ActionRegistry` cascades precedent (`suite.py:395-396`, door `coherence_actions.build_action:23`), and the live incident (`18a3a875`: the ui-join rebuild run 390286ec stranded 4,199 descriptions + 1,403 generated-by edges below `*_latest`; the interim fix was a source_hash carry-forward). Here is the design take, verbatim, ready to file.

---

# Plan A design take · SUBSTRATE-MINIMALIST — jobs as the sixth *row type*, not the sixth *mechanism*

*Lens: every new table/module must justify itself against extending something that exists. The bill of new materials is stated at the end and defended line by line.*

## 0 · The one-sentence design

A **job is a data row in a fourth `_ActionRegistry` store** whose body is **always a cascade decl** — the existing `run_cascade` becomes the universal executor by adding **three step kinds** (`flow`, `graph`, `agent`); triggers are a **fifth registry of rows carrying `rules.py` data-ASTs**, walked by a **new fourth driver inside the existing `ActivationCaller` tick**; every fire lands **one `op.run` record**; the floor transfers field-for-field from flows (`proposes_only`) and routines (`permission_mode`). No queue table, no pg_cron, no new daemon, no sixth peer.

Everything below is the elaboration of that sentence.

---

## 1 · The job-definition row

### Where it lives — and why not the alternatives

**A new `jobs.json` via `_ActionRegistry`** (`runtime/suite.py:395-396` pattern — third/fourth instantiations of an existing class, zero new persistence code). The cascades store is the only existing proof in the whole system that "a registered runnable = a data row an agent writes through a face under a validation door" (R1 §8) — jobs copy that proof exactly.

- **Not files (the flows pattern):** repo-committed definitions are R2's trap #3 verbatim — the moment a definition isn't a row, agents can't configure it through MCP and the premise breaks. Flows' own docstring fences this (`flows.py:15-17`).
- **Not a ledger/Supabase table yet:** north-star directive 4 — *"Everything ends up in Supabase — but not all at once… the rest later, deliberately."* The row shape below is deliberately flat `id + jsonb`-liftable so the eventual move is a copy, not a redesign. Building the Postgres spine now would also couple Plan A to Plan B's in-flight migration.
- **Not inside cascades.json:** jobs *reference* cascades but carry trigger/allocation/floor fields cascades must not grow (a cascade stays a pure chain decl; a job is a chain + circumstances).

### Schema (dict shape; the store is JSON rows keyed by id)

```
JOB_FIELDS (closed set, unknown field FAILS LOUD — the routines.py:136-140 discipline):
  id            str   — unique; addressable as job://<id>
  label         str   — required
  description   str   — required
  run           dict  — {"cascade": <name-in-cascades.json>} OR {"cascade_inline": <full decl>}
                        THE ONLY BODY SHAPE (see §4 — role/graph/flow/agent are step kinds, so
                        "what-to-run kind" collapses into the cascade vocabulary; a bare role is
                        a 1-step decl)
  params        dict  — {name: {"desc": str, "default": <value-or-None-if-required>}}
                        EXACTLY flows.py:29-30's shape; validation/merge logic lifted from
                        Flow.run (flows.py:53-64) into a shared helper — the one mechanism that
                        already has declared+validated+defaulted params-as-data (R1 matrix)
  allocations   dict  — {"model": <registry-model-or-None>, "max_tokens": int?, "max_calls": int?,
                         "time_budget_s": int} — definition-side budget (R2 §5.3: allocations on
                        the definition, actuals on the run); model validated ∈ live registry at save
  outputs       dict  — {"address": "run://job/<id>/<fire_id>"} — the job-level landing address;
                        step outputs keep their own run://<turn>/<i>-<role> addressing untouched
  proposes_only bool  — the flows floor field, default True (see §7)
  permission_mode str — routines' field, default "plan"; ONLY meaningful if the body contains an
                        `agent` step (save-door cross-check)
  max_turns     int?  — ditto, agent-step bound
  enabled       bool
  created_by / created_at / version — provenance stamps (every row traces to its authoring
                        exchange:// per the north-star provenance law)
```

### The validation door

**One door, the existing one's sibling:** `build_job(decl, *, models, cascades, triggers)` in `runtime/coherence_actions.py`, next to `build_action:23`. It refuses at save: unknown fields, params not in the flows shape, `run.cascade` naming a non-existent cascade, `cascade_inline` failing `build_action` itself (the inner decl goes through the SAME cascade door — no second cascade validator), model ∉ registry, an `agent` step present without `permission_mode`, and a consequential body without `proposes_only`. The governance scan (`tests/cognition_governance_acceptance.py:103-125` pattern) folds `jobs.json` into `COG_SOURCES` so the floor is asserted structurally, third layer, same as flows.

### How agents author it

One new MCP tool **`jobs`** (mirror of the routines/cascades op-grammar):
`jobs(op='save'|'list'|'get'|'fire'|'enable'|'disable'|'delete'|'runs', ...)` → thin wrapper over `Suite.job_save / job_list / job_fire / …` — and the **same Suite functions** serve `/api/jobs` on the bridge (one-function-two-faces; the FACE-4 pilot routes `bridge.py:1631-1640` show the wiring pattern). `op='save'` of a job whose body contains an `agent` step with non-plan permissions does not save-live: it **surfaces** (`surface_review` ask-event, resolved=None) and only operator `resolve_surfaced` arms it — the exact flows `op='propose'` gate (`mcp_face/tools/flows.py:27-30, 57-61`) reused, not re-invented.

---

## 2 · The trigger registry

### Where it lives

**`triggers.json`, the same `_ActionRegistry` class**, own door `build_trigger` (validates the AST via the existing `rules.validate_ast` — arity table, closed `RULE_OPS`, `MAX_RULE_DEPTH=6` fail-loud all come free, `runtime/rules.py:65-108`).

### Row shape

```
TRIGGER_FIELDS:
  id        str
  job       str   — must exist in jobs.json (door-checked)
  kind      "change" | "schedule" | "event" | "condition" | "manual"
  config    dict  — kind-specific (closed per kind, unknown key fails loud):
     change:    {"sources": ["git:<abs-project-root>", ...],   # v1: git sources only (below)
                 "quiet_window_s": int,                        # debounce, default 120
                 "refire_mode": "replace"}                     # graphile job_key semantics named
     schedule:  {"every_s": int} | {"on_calendar": str}        # routines' cadence grammar
                                                               # (routines.py:41-43) reused verbatim
     event:     {"event_kinds": [<kinds on the ONE event log>], "cursor": "held"}
     condition: {}                                             # pure when-AST sensor (see below)
     manual:    {}
  when      data-AST | null — a rules.py AST evaluated over the TRIGGER SNAPSHOT (below);
                              null = unconditional. This is the mode_detection_rules shape
                              ({id, priority, when, candidate}) with candidate:mode swapped
                              for job:id — R1 reuse #2 executed literally.
  params    dict — per-trigger param bindings/overrides for the job (validated against job.params)
  priority  int  — first-match ordering within a tick, mode_detection discipline
  enabled   bool
  armed_by  str? — resolve:// ref when operator arming was required (§7)
```

### The trigger snapshot (what `when` reads)

Analogous to `activity_signal`: a dict assembled per-trigger per-tick — `{now, change: {sig, files_changed_n, since_change_s, since_quiet_s}, event: {...matched event fields...}, job: {last_fired_at, in_flight, last_outcome}, watermark}`. The AST's `field` op traverses it by dot-path exactly as today. **A condition trigger is therefore NOT a resident job** — it is a cheap predicate evaluated on the tick that enqueues-by-firing when true (R2 trap #2, the Airflow-sensor lesson, honoured by construction: there is nothing *to* occupy).

### Where change-detection comes from (v1 decision + the honest boundary)

**v1: git, computed on the tick.** Per `git:` source, the driver computes `sig = hash(HEAD sha + git status --porcelain output)` — one subprocess, milliseconds, no watcher daemon, no new infra, and it sees *every writer* (agent sessions, manual edits) which is the property Airflow Datasets can't have (R2 §2.4). The heartbeat's own sources are repo files, so row #1 needs nothing more.
- **Not DB triggers on ledger tables (yet):** the ledger tables are mid-migration (Plan B); wiring `AFTER UPDATE` outbox triggers now builds on moving ground. The `config.sources` grammar reserves `"ledger:<table>"` as a source kind whose implementation is the Supabase trigger→outbox→drain miniature (R2 §3.5) **when the store lands there** — the row shape doesn't change, only a driver gains a source resolver.
- **Not the op.run/event log as the change signal:** that detects *system* actions, not file truth — it would recreate Airflow's "only sees changes made through itself" blind spot for manual/agent edits outside recorded ops.
- `event:` triggers DO ride the ONE event log, via a held cursor (the `RollupDriver` cursor pattern, `activation.py:490`) — that's their correct semantics (react to system happenings), distinct from change (react to world state).

---

## 3 · The scheduler tick

**Host: `ActivationCaller`, alone.** A fourth driver, `TriggerDriver`, walked inside `activation_tick` beside `background_tick` + `RollupDriver.tick` + `propose_mode` (R1 reuse #3). Both existing doors transfer untouched: `/api/activation/tick` (`bridge.py:93, 3077-3085`) is the always-live manual heartbeat-of-the-heartbeat; the autonomous cadence stays behind `COMPANY_ACTIVATION_LOOP` (`activation_driver.py:84-104`, default OFF, 60s) — **arming the whole auto-run system remains one operator switch**, which is the floor's outermost ring.

**pg_cron: no — with a named future seam.** pg_cron now would be a second scheduler (hard constraint) driving Python-side bodies through an awkward door. Its legitimate future role (R2 §3.3): the *tick generator* for the DB-side change outbox once the store lives in Supabase — and even then it drains into this same `TriggerDriver` walk, never fires jobs itself. Recorded as a seam, not built.

### Debounce/watermark — R2's shapes expressed in THIS substrate

The insight that keeps the bill small: **because there is exactly one caller ticking, the tick + a per-trigger state row replace the entire queue table.** graphile's `job_key` upsert exists to coordinate many enqueuers against many workers; we have one of each, so its semantics compress into two fields:

Per-trigger persisted state (in the store beside the registries — a small `trigger_state.json`, corrupt-file = raise with path + regeneration breadcrumb, never silent-reset):
```
{trigger_id: {sig, changed_at, last_fired_sig, last_fired_at, watermark, in_flight_fire_id}}
```
Per tick, per change-trigger:
1. Compute `sig`. If `sig != state.sig` → `state.sig = sig; state.changed_at = now`. **This IS job_key replace-mode:** every fresh change re-arms the quiet window by moving `changed_at`.
2. **Due** ⇔ `sig != last_fired_sig` ∧ `now − changed_at ≥ quiet_window_s` ∧ `when`-AST truthy ∧ `in_flight_fire_id is None`.
3. On fire: snapshot `sig_at_start`, run the job with `params + {watermark: state.watermark}`. On completion: `watermark = fire_start_ts; last_fired_sig = sig_at_start`. **The mid-run edge is lossless by arithmetic:** changes landing during the run make live `sig ≠ sig_at_start = last_fired_sig`, so the trigger re-arms and fires again after the next quiet window — graphile's "running keyed job spawns a successor" without a queue row.
4. **Watermark, not payloads** (R2 §4.3): the heartbeat never receives the change events — its first step rediscovers work from `changed_at > watermark`. Coalescing is free; a missed tick self-heals on the next.
5. **Single-flight + loud stall:** `in_flight_fire_id` set at fire-start (also emitted as a `job.run` start event, so it survives a state-file loss); a tick finding `now − last_fired_at > allocations.time_budget_s × 1.5` with in-flight still set emits a **`job.stalled` event + surfaces to the operator + releases** — recorded, never a silent wedge, never a silent double-run.
6. **Backpressure:** `params.budget_files`-style caps on the job (bounded drain); leftover work is caught by the watermark on the next fire — graceful lag, never pile-up (R2 §4.4).

---

## 4 · The executor dispatch — run_cascade IS the dispatcher

The minimalist's central move. Rather than a thin dispatcher *above* five executors, the five collapse *into* the one that already has output→input threading, per-step model/budget, fan-out, deterministic `check` gates, jury/panel, persistence, and per-step op.run indexing (`cognition.py:2644-2990` — R1 reuse #1). **Three new step kinds:**

| new `kind` | fires | notes |
|---|---|---|
| `flow` | `Flow.run(**step_params)` via injected resolver | flows become **staging steps** — their own in-code split ("flows stage, cascades declare", `cognition.py:2704-2705`) finally realized; `proposes_only` checked at decl-build |
| `graph` | `Suite.run(graph)` (rides the existing `guard("run")` policy router) | outputs (`run://<graph>/<node>`) threaded to the next step as addresses; the graph keeps its own event shape (§6) |
| `agent` | `routine_runner.fire(..., prompt_override=<templated>)` | the ONLY consequential kind; `prompt_override` (`routine_runner.py:38`) finally exposed as the params seam R1 gap #2 named; bounded by job `permission_mode` + `max_turns`; returned record landed as op.run (§6) |

Everything else already exists: `role` (1→1), `items` (MAP), `reduce` (JOIN), `retrieve`, `check`, `jury`, `panel`. A job whose "what-to-run" is a bare role is a one-step decl; there is **no what-to-run enum and no dispatcher module at all** — the enum became step kinds, dispatch became the runner's existing kind-switch.

Params flow: `job.params` merged/validated flows-style → substituted into the decl (step-0 `inputs`, `{params.x}` in `shared`/`unit_ctx` — both existing seams) → `run_cascade`. The "job runner" is ~one page of glue in `runtime/jobs.py`.

---

## 5 · The heartbeat AS ROW #1 (actual rows)

**Job row** (`jobs.json`):
```json
{"id": "ledger-heartbeat",
 "label": "Ledger heartbeat — change → extract → re-embed → joins → descriptions",
 "description": "Incremental maintenance of the ledger from the change watermark; upgrade-1 as a registered job.",
 "run": {"cascade": "heartbeat-incremental"},
 "params": {"project":      {"desc": "project root",                    "default": "/home/tim/company"},
            "since":        {"desc": "watermark override (ISO)",        "default": null},
            "budget_files": {"desc": "max changed files per fire",      "default": 200}},
 "allocations": {"model": null, "time_budget_s": 600},
 "outputs": {"address": "run://job/ledger-heartbeat/<fire_id>"},
 "proposes_only": true, "permission_mode": "plan", "enabled": true}
```

**Cascade `heartbeat-incremental`** (saved through the normal cascade door; steps by kind):
1. `flow` **changed-set** — git-diff + dirty files since `{watermark|params.since}`, capped `budget_files` → the changed `code://` unit list. *(Deterministic set-work in code — the dragnet lesson, enforced by shape.)*
2. `flow` **incremental extract + INGEST-WITH-CARRY-FORWARD** — re-extract only changed files; at ingest, every unit whose `source_hash` is unchanged **carries its prior descriptions + generated-by edges onto the new run** (the proven 18a3a875 repair, promoted from emergency script to a *contractual ingest step*).
3. `flow` **re-embed changed** — embedding pipeline over changed units only, bounded batch.
4. `flow` **joins re-derive** — ui→code / reference edges, scoped to touched units.
5. `items` **descriptions re-carry/re-generate** — fan over units with changed `source_hash` only (role step); unchanged units were carried in step 2 and are *recorded as carried* (a derivation-tag, never a silent skip).
6. `check` **supersession guard** (deterministic, from the checks registry, `on_fail: flag`) — post-conditions: `entry_latest` description count ≥ pre-run count for untouched scopes; generated-by edge count not reduced; dangling-edge ratio not worsened. **A failing check FLAGS → routes `surface` → operator inbox.** The stranding class becomes a loud same-hour surface instead of a next-morning zero.

**The run-supersession contract, stated as an invariant:** *no fire may reduce the enrichment coverage of units it did not change.* Step 2 (carry-forward-at-ingest) is this design's enforcement **now**; if Plan B ships layered `unit_latest` views, step 2 degrades to a no-op and **step 6 remains as the permanent guard** — the contract is mechanism-independent, so Plans A and B can land in either order without re-opening the heartbeat.

**Trigger row** (`triggers.json`):
```json
{"id": "heartbeat-on-change", "job": "ledger-heartbeat", "kind": "change",
 "config": {"sources": ["git:/home/tim/company"], "quiet_window_s": 120, "refire_mode": "replace"},
 "when": {"op": "ge", "args": [{"op": "field", "path": "change.files_changed_n"},
                                {"op": "lit", "value": 1}]},
 "params": {}, "priority": 10, "enabled": true}
```
(Quiet-window/single-flight/watermark are driver mechanics — their *parameters* are the config row; the `when`-AST is the declarative guard on top.)

---

## 6 · The run record — unify at the JOB level onto op.run

**Every fire = ONE parent `op.run` row** via the existing `Suite.emit_run_record` (`suite.py:736-747`): `op='run_job'` added to `ENGINE_RUN_OPS`, carrying `{job, trigger, fire_id, params_resolved, watermark_from/to, result_address, duration, outcome}`, with `outcome ∈ done | failed | check_flagged | budget_exhausted | stalled` — budget-exhausted and stalled as **first-class recorded terminals**, distinct from failed (R2 §5.3, and Tim's fail-loud law). Children thread by `fire_id`:
- cascade steps: already per-step op.run — nothing to do;
- `agent` steps: the routine record — today *returned to the caller, never indexed* (R1 §8) — is landed as an op.run child, closing that gap for every agent fire through the system;
- `graph` steps: keep their `kind='run'` event (73 graphs' history is not migrated), but the step emits an op.run child that *references* it — discoverability without a retro-rewrite.
`runs(op='find')` + `run_stats` then answer "this job's history" with zero new query machinery. Five shapes aren't retro-merged; they are **joined under one parent shape**, which is all discovery needs.

## 7 · The floor — transferred field-for-field

Concentric, all existing mechanisms:
1. **Outermost:** the autonomous loop is env-gated (`COMPANY_ACTIVATION_LOOP`) — auto-run as a whole is one operator switch; `/api/activation/tick` manual fires remain available below it.
2. **Definition floor:** `proposes_only` default-true on the job row, enforced flows-style in three layers (door refusal at `build_job` · runner check · governance-scan fold of jobs.json into `COG_SOURCES`).
3. **Computation floor by construction:** role/items/reduce/flow/graph steps only write `run://`; the step vocabulary contains no resolve/approve/dispatch; `FORBIDDEN_DESTINATION_VERBS` (`rules.py:134`) holds unchanged.
4. **The consequential kind is doored:** an `agent` step runs under the job's `permission_mode` (default "plan") + `max_turns`. **Auto-fired** (non-manual trigger) agent work above plan mode requires the trigger row itself to have been operator-armed — `jobs(op='save')`/`build_trigger` refuses to arm it live and instead **surfaces** (`surface_review` ask-event); only `resolve_surfaced` stamps `armed_by: resolve://…`. Operator manual fires pass directly.
5. **Anything beyond run:// writes** routes `surface` — the operator's resolve remains the only apply verb in the entire system, untouched.

## 8 · Retired / absorbed

| thing | fate |
|---|---|
| **flows/** | **Absorbed as the `flow` step kind** (staging steps) — their own docstring's destiny. The `flows/` directory *stays* as the handler registry (R2: "rows for everything; code only in the handler registry"); the standalone `flows(op='run')` MCP face deprecates toward `jobs(op='fire')` after row #1 proves out. |
| **routines/** | **Absorbed:** each of the 5 rows re-registered as a job (`agent`-step body) + a `schedule` trigger from its cadence string. `routine_runner.fire` survives as *the* agent-work primitive. **`routine_schedule.py` (the systemd generator) RETIRES** — the tick replaces generated timers; generates-not-arms is preserved one level up by the env gate. The `routines` MCP tool deprecates after migration. |
| **graph llm/ask parallel model path** | **Frozen, not ripped** (73 stored graphs). The job system does not inherit the second model door — its model work goes through cascade role steps. Absorbing the graph path behind the role system is flagged debt for a later pass. |
| **activation modes/rollup** | Untouched peers of the new driver in the same tick. |
| **Not retired** | cascades (the spine), the ONE event log, `run://` addressing, `_ActionRegistry`. |

## The bill of new materials (the entire new-code inventory)

1. `runtime/jobs.py` — registry glue + the ~1-page job runner + `TriggerDriver` (one module).
2. Three step kinds inside the existing cascade runner.
3. `build_job` / `build_trigger` beside `build_action` in `coherence_actions.py`.
4. `mcp_face/tools/jobs.py` + `/api/jobs` bridge routes over the **same** `Suite.job_*` functions.
5. Two JSON stores (`jobs.json`, `triggers.json`) + `trigger_state.json` — three more files in `.data/store/`, zero new persistence classes, zero tables.
6. Acceptance tests (door refusals, floor scan, debounce arithmetic, stall-loudness, the step-6 supersession check).

## Component diagram

```
        MCP jobs(save|list|fire|runs…) ─┐                      ┌─ /api/jobs (UI face)
                                        └── Suite.job_* (ONE) ─┘
                                                 │
              ┌──────────────────────────────────┴───────────────────────────┐
              │ jobs.json (_ActionRegistry · door: build_job)                 │
              │ triggers.json (_ActionRegistry · door: build_trigger         │
              │               + rules.validate_ast — closed RULE_OPS)        │
              └──────────────────────────────────┬───────────────────────────┘
  /api/activation/tick (manual, always) ─► ActivationCaller.activation_tick
  COMPANY_ACTIVATION_LOOP (operator switch)   ├─ background_tick        (existing)
                                              ├─ RollupDriver.tick      (existing)
                                              ├─ propose_mode           (existing)
                                              └─ TriggerDriver          (NEW)
                                                   │ per-trigger state {sig·changed_at·watermark·in_flight}
                                                   │ due? quiet-window ∧ when-AST ∧ single-flight
                                                   ▼
                                          run_job(job, params, watermark)
                                                   │  = run_cascade(materialized decl)
        ┌─────────┬─────────┬──────────┬───────────┼────────────┬──────────────┐
      role      items     reduce    retrieve/    flow (NEW)   graph (NEW)   agent (NEW)
    (exists)  (exists)  (exists)   check/jury    Flow.run     Suite.run     routine_runner.fire
                                    (exist)                   via guard()   plan-floor + max_turns
                                                   ▼
             run:// step outputs · ONE parent op.run (op='run_job', fire_id) · check-fail → surface
```

## Build sequence (step 1 is step 1)

1. **Walking skeleton, manual-only:** `build_job` + `jobs.json` + `jobs` MCP tool + `run_job` over the *existing* step vocabulary; parent op.run from day one. (Everything downstream composes on this; testable without any trigger.)
2. Step kinds `flow` + `graph` — the heartbeat body becomes expressible.
3. `TriggerDriver` in the tick: `manual`/`schedule`/`condition` kinds + state persistence + single-flight + loud stall.
4. `change` kind (git sig · quiet window · watermark) → **write the two heartbeat rows**; supervised fires through `/api/activation/tick` with the loop still off (①'s supervised-flip style).
5. The supersession contract: carry-forward-at-ingest (step 2) + the `check` guard (step 6); coordinate with Plan B — the check ships regardless of which side wins.
6. `agent` step kind + arming doors; migrate the 5 routines; operator arms the loop.
7. Deprecations (flows run-face, routines tool, systemd generator) + the Supabase lift of the stores when "everything in Supabase" reaches them.

## The 3 biggest risks of THIS design (honest)

1. **No queue table = single-process assumption load-bearing.** Collapsing queue+worker into "one tick walks one state file" is only safe while exactly one `ActivationCaller` exists. A bridge-restart overlap or any future parallel worker makes the in-flight check racy — JSON state has no `FOR UPDATE SKIP LOCKED`. The stall/loud mechanics are advisory, not atomic. The row shapes are lift-ready for R2's three-table spine, but that is a *second build*, and the failure mode is that we patch the state file instead of doing it when parallelism arrives.
2. **run_cascade becomes load-bearing for everything.** Adding `flow`/`graph`/`agent` turns a runner designed for model chains into the universal executor — side-effectful staging steps and 10-minute agent sessions inside a synchronous step loop stress contracts (no memoization there, thread semantics, blocking) it wasn't designed under. It is the cheapest-code choice and it concentrates risk: a runner bug now stalls the heartbeat *and* chat-adjacent cascades. The rejected alternative (a thin dispatcher above five executors) is the named fallback seam if `agent` steps fight the runner.
3. **Change detection and debounce mechanics are partly code, not data — and git-shaped.** The git-sig source misses non-git truth (`.data/store`, the ledger tables themselves) until the reserved `ledger:` source kind is implemented post-Plan-B; and the quiet-window/re-arm/mid-run-refire *mechanism* lives in `TriggerDriver` Python with only its parameters as rows. Read strictly against everything-as-data, this is the design's weakest joint — accepted deliberately for code size, and confined to one module so a stricter later form (outbox rows) replaces it behind the same trigger-row schema.

---

**Constraint check:** everything-as-data ✓ (definitions, triggers, params, guards, budgets = rows; code only in handlers) · fail-loud with breadcrumbs ✓ (door refusals, corrupt-state raise-with-fix, `job.stalled`/`budget_exhausted`/`check_flagged` as recorded outcomes, step-6 surfaces) · one-function-two-faces ✓ (`Suite.job_*` → MCP + `/api/jobs`) · no second scheduler ✓ (one tick, pg_cron reserved as a future *feeder* only) · no silent drops ✓ (watermark self-healing, mid-run refire arithmetic, carried-descriptions recorded as carried).
