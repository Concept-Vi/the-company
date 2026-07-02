# PLAN A — THE design: the parametric job system (judged synthesis of D1/D2/D3 · 2026-07-02)

*This is the ONE design, produced by judging the three independent takes (D1 substrate-minimalist ·
D2 asset-first · D3 agent-experience) against each other, the research (R1/R2), the north star, and the
laws. Sections: Tim-altitude opening → the judgment (per-dimension verdicts) → the decided architecture →
the heartbeat's actual rows → worked agent examples → build sequence → rejected alternatives → risk
register → the few questions only Tim can answer. Register: prescriptive, unbuilt — this is the design
Tim recognizes (or corrects) before the loop-prep triad.*

---

## (a) What this system is — Tim's page

**One circuit, one new row type, no new silo:**

```
world changes → trigger row notices → job row fires → cascade body runs → run record lands → surface shows it
```

Today the Company has five half-systems that each hold one piece of "work that runs": flows have
parameters, routines have schedules, cascades have chains, graphs have canvases, activation has the
always-on tick. None of them can do what the others do, and nothing lets an agent say **"when X happens,
run Y with these settings"** as a piece of data. That sentence — when / run / with — becomes two row
types an agent writes through the MCP face and you see rendered on the surface:

- **A JOB row** — *what runs*: a chain (the existing cascade language, extended with three new step
  kinds so a chain can include staging work, a graph, or a real agent session) + declared parameters +
  a budget + where outputs land. A job is data. Editing the job is editing a row, not code.
- **A TRIGGER row** — *when it runs*: on change (files moved), on schedule, on condition (a declared
  rule over system state), on event, or by hand. Also data. **An agent can propose a standing trigger;
  only you arm it** — arming autonomy stays with you, always.

**The heartbeat is not a special machine — it is row #1.** "Something changed → re-extract just that →
re-embed just that → re-derive the joins → re-carry the descriptions → check nothing was stranded" is one
job row + one change-trigger row, written in the same language every future job uses. One-offs, targeted
re-processing, conditional processing, generative work, traversal — all the same two row shapes with
different fields.

**Freshness is the visible pulse.** You never read a cron expression. The surface shows, per region of
the world: **current / lagging / stale** (PASS / WARN / FAIL), computed by comparing when the sources
last moved against when the maintenance last succeeded — *independently* of the trigger machinery, so
the alarm still fires when the machinery itself is broken. When the pulse is green, the world the agents
work through is the world as it is. The supersession incident (a rebuild silently stranding 4,199
descriptions overnight) becomes impossible to miss three ways: the ingest **carries enrichment forward**
by contract, a **check step inside the heartbeat** verifies nothing was stranded on every fire, and the
**freshness alarm** goes red if both of those somehow fail.

Everything rides what already exists: the one activation tick (no second scheduler), the one event log,
the one `run://` address space, the one validation-door pattern, the one floor (compute freely; anything
consequential surfaces to you). The five mechanisms don't get a sixth sibling — they become the **organs
one job language composes**, and every fire of anything, forever, is a discoverable record.

---

## (b·0) THE JUDGMENT — per-dimension verdicts

Scored against: Tim's laws (everything-as-data · fail-loud · one-function-two-faces · no second
scheduler) · structural prevention of the supersession class · single-machine TODAY vs growing-model-
layer future · build cost · risk concentration.

| # | dimension | verdict | why (the load-bearing reason) |
|---|---|---|---|
| 1 | Where rows live | **D1 — JSON `_ActionRegistry` stores** (`jobs.json`, `triggers.json`), rows kept flat + jsonb-liftable | North-star directive 4 is explicit: Supabase *deliberately later*. The cascades store is the only **proven** agents-author-rows-through-a-door pattern in the repo; zero new persistence code. D2's Postgres schema builds on Plan B's moving ground and buys concurrency properties nothing consumes yet. Condition of the verdict: row shapes are designed lift-ready so the eventual move is a copy, not a redesign. |
| 2 | Executor | **D1/D3 — the job body IS a cascade decl**; `run_cascade` gains three step kinds (`flow`, `graph`, `agent`); no dispatcher module | Two independent takes converged on it. `run_cascade` already owns output→input threading, fan-out, deterministic `check` gates, jury/panel, persistence, per-step op.run (R1 reuse #1). D2's materializer is a new dispatcher over the same executors and runs only ONE thing per asset — chains would need cascades anyway. D2's `python` kind collapses into `flow` (flows/ stays as the handler registry — its own docstring's destiny). D1's fallback seam (a thin dispatcher above executors, if `agent` steps fight the runner) is retained as the named escape hatch. |
| 3 | Change triggers | **D1 — git-sig + quiet-window + per-trigger state**, with **D2's watermark semantics adopted** (the extraction watermark IS the latest `ledger.run` id; staleness = id inequality) and `ledger:<table>` reserved as the post-Plan-B outbox source kind | The heartbeat's ROOT source is the working tree; a git sig on the tick sees **every writer** (the property Airflow can't have) for zero infra. D2's DB-trigger outbox is the right shape for ledger-internal sources — *later*, when the store stops moving; the trigger-row schema already carries it. Debounce/re-arm/mid-run-refire compress into two state fields because there is exactly ONE ticking caller (graphile `job_key` semantics without the table). |
| 4 | Asset/freshness layer | **SPLIT — the synthesis's central call.** REJECT D2's staleness-derived *scheduling* (the full asset graph). ADOPT D2/D3's staleness-derived *visibility*: freshness PASS/WARN/FAIL as an independent, read-only projection on both faces | D2's own risk 1 is disqualifying under Tim's laws: "a subtle staleness bug reads as *not stale* — work silently not happening" is precisely the silent-failure class that cost a day. Explicit chain steps in ONE cascade are loud; a derivation-inference layer is quiet. But D2's **two-eyes principle** (freshness computed independently of the automation path) is the best idea in all three takes for the supersession class — kept as an alarm, not a scheduler. The full asset graph is the named future IF the derivation web outgrows one cascade (many projects × spaces × embedders); D2 §1–2 is filed as that future's shape. |
| 5 | Selector grammar | **D3 — `over:` on steps**, v1 subset `list` · `path` · `changed_since` (+ `$prev`/`$step[i]`); `near`/`traverse` **teach-refused naming Plan B** | The consumer-honest unification: targeted, traversal, and the heartbeat's changed-set are all ways of saying *these*. Shipping only the kinds with existing machinery behind them keeps the seam without creating the second dialect D3 itself warned about — Plan B *extends* the selector vocabulary through the same door. `over` resolves to the unit list the existing items/fan machinery consumes (composition to be verified in the skeleton — D3's own tagged assumption). |
| 6 | Approval/floor | **D1's enforcement × D3's lifecycle.** Field-for-field floor transfer (proposes_only ×3 layers · permission_mode · FORBIDDEN_DESTINATION_VERBS · env-gated loop) + D3's `proposed → ask → armed` states, teach-refusal returns, and you_can guidance. **Pre-approved classes DEFERRED** with the constraint pre-decided (class predicate must be a data-AST, auditable; `agent`-step jobs never class-eligible) | D1 supplies the three-layer structural enforcement the governance scan can assert; D3 supplies the experience that makes the floor legible instead of obstructive. Classes are deferred because D3 admits the class predicate's limits are undesigned and a too-broad class is a floor bypass — at v1 volume (heartbeat + a handful) individual arming is cheap. |
| 7 | Run records | **D1's substrate + D3's vocabulary.** ONE parent `op.run` per fire (`op='run_job'`, children threaded by `fire_id`; routine records finally indexed; graph events referenced, not migrated) + D3's state machine and read shapes (distinct terminals, `watch` with `poll_after_s`, per-step actuals, breadcrumbed failures) + D2's rendered-params provenance on the run | No new table; `runs`/`run_stats` discovery works day one. The five record shapes are joined under one parent, not retro-merged. Terminals: `succeeded · failed · schema_failed · check_flagged · budget_exhausted · cancelled · stalled` (+ `deduped` pointing at the live run) — budget and schema outcomes are first-class recorded states, never flavors of `failed`. |
| 8 | Queue | **D1 — no queue table.** One tick walks trigger state; per-trigger single-flight + loud stall; R2's three-table spine (`SKIP LOCKED` claim) is the **named lift** when a second worker becomes real | Single machine, one `ActivationCaller`, zero concurrent claimants exist — a queue table today is ceremony guarding against a race that can't occur. The in-flight marker is double-recorded (state file + start event) so it survives state loss. The lift trigger is explicit: the moment the growing model layer wants parallel workers, dimension 1's lift-ready rows move to Postgres and the claim query replaces the walk — schema unchanged. |

---

## (b) THE DECIDED ARCHITECTURE

### The job row (`jobs.json`, `_ActionRegistry`, door `build_job`)

```
JOB_FIELDS (closed set — unknown field FAILS LOUD, the routines.py discipline):
  id              str    — addressable job://<id>
  label           str    — required
  description     str    — required
  run             dict   — {"cascade": <name>} | {"cascade_inline": <decl>}   ← THE ONLY BODY SHAPE
                           (inline decl passes through build_action itself — no second validator;
                            a bare role is a 1-step decl; what-to-run enum = step kinds)
  params          dict   — {name: {"desc": str, "default": <value-or-None-if-required>}}
                           flows.py's shape verbatim; validation/merge lifted from Flow.run into a
                           shared helper (the one proven params-as-data mechanism)
  budget          dict   — {"model": <registry-model?>, "max_total_tokens"?, "max_calls"?,
                            "max_tokens_per_call"?, "time_budget_s", "per_day"?: {...}}
                           allocations on the DEFINITION, actuals on the RUN (R2 §5.3);
                           generative steps without a budget get the default injected AND stated
  outputs         dict   — {"address": "run://job/<id>/<fire_id>", "notify"?: [{on, to}]}
                           notify ∈ rules destination vocabulary minus forbidden verbs
                           (surface | board | channel); terminal failures of standing jobs
                           auto-surface by default
  proposes_only   bool   — default True (flows floor field, 3-layer enforcement)
  permission_mode str    — default "plan"; meaningful ONLY with an `agent` step (door cross-check)
  max_turns       int?   — ditto
  enabled         bool
  created_by / created_at / version — provenance; every row traces to its authoring exchange://
```

### The trigger row (`triggers.json`, `_ActionRegistry`, door `build_trigger`)

```
TRIGGER_FIELDS:
  id        str
  job       str   — must exist in jobs.json (door-checked)
  kind      "change" | "schedule" | "event" | "condition" | "manual"
  config    dict  — closed per kind, unknown key fails loud:
     change:    {"sources": ["git:<abs-root>", ...],          # v1: git only; "ledger:<table>"
                 "quiet_window_s": 120,                        #   RESERVED (post-Plan-B outbox)
                 "refire_mode": "replace", "max_delay_s"?: int}# D2's starvation cap adopted:
                                                               # continuous re-arming degrades to
                                                               # throttle after max_delay_s
     schedule:  {"every_s": int} | {"on_calendar": str}        # routines' cadence grammar verbatim
     event:     {"event_kinds": [...], "cursor": "held"}       # the ONE event log, RollupDriver-
                                                               #   style held cursor
     condition: {}                                             # pure when-AST sensor: a cheap
                                                               #   tick-time predicate, NEVER a
                                                               #   resident poller (R2 trap #2)
     manual:    {}
  when      data-AST | null — rules.py AST (closed RULE_OPS, MAX_RULE_DEPTH, validate_ast — all
                              free) over the TRIGGER SNAPSHOT: {now, change:{sig, files_changed_n,
                              since_change_s, since_quiet_s}, event:{...}, job:{last_fired_at,
                              in_flight, last_outcome}, watermark}
  params    dict  — per-trigger bindings validated against job.params
  priority  int   — first-match ordering within a tick (mode_detection discipline)
  state     "proposed" | "armed" | "paused" | "retired"        # D3's lifecycle, explicit
  armed_by  str?  — resolve:// ref when operator arming was required
  enabled   bool
```

### The tick (no second scheduler)

**Host: `ActivationCaller`, a fourth driver `TriggerDriver`** beside background_tick, RollupDriver,
propose_mode. `/api/activation/tick` stays the always-live manual door; the autonomous cadence stays
behind `COMPANY_ACTIVATION_LOOP` (default OFF, 60s) — **arming the whole auto-run system remains one
operator switch**, the floor's outermost ring. A module-level tick mutex loud-skips overlapping ticks.
pg_cron: not now; recorded as the future *feeder* of the DB-side outbox — even then it drains into this
walk, never fires jobs itself.

Per tick, per armed change-trigger (state in `trigger_state.json` —
`{trigger_id: {sig, changed_at, last_fired_sig, last_fired_at, watermark, in_flight_fire_id}}`;
corrupt file = raise with path + regeneration breadcrumb, never silent-reset):

1. `sig = hash(HEAD sha + git status --porcelain)` per source. `sig != state.sig` → update sig,
   `changed_at = now`. **This IS `job_key` replace-mode** — every fresh change re-arms the quiet window.
2. **Due** ⇔ `sig != last_fired_sig` ∧ `now − changed_at ≥ quiet_window_s` ∧ when-AST truthy ∧ not
   in-flight. (`max_delay_s` exceeded → fire anyway: throttle beats starvation.)
3. Fire: snapshot `sig_at_start`; run with `params + {watermark}`. Complete: `watermark = fire_start_ts`,
   `last_fired_sig = sig_at_start`. **Mid-run changes are lossless by arithmetic**: live `sig ≠
   last_fired_sig` → re-arms → fires after the next quiet window (graphile's successor-job, no queue).
4. **Watermark, not payloads**: the job's first step rediscovers work from `changed_at > watermark`
   (minus a safety overlap) — coalescing free, missed ticks self-heal.
5. **Single-flight + loud stall**: `in_flight_fire_id` set at fire-start AND emitted as a run-start
   event (survives state loss). `now − last_fired_at > time_budget_s × 1.5` with in-flight set →
   `job.stalled` event + surface + release. Never a silent wedge, never a silent double-run.
6. Schedule/condition/event kinds ride the same walk (cadence check · when-AST over snapshot · held
   event cursor with Dagster-style consume-once semantics).

### The executor — `run_cascade` IS the dispatcher

Three new step kinds inside the existing runner (everything else — role/items/reduce/retrieve/check/
jury/panel — already exists):

| kind | fires | floor |
|---|---|---|
| `flow` | `Flow.run(**step_params)` via injected resolver — flows become **staging steps** ("flows stage, cascades declare" realized); flows/ stays as the deterministic handler registry | proposes_only checked at decl-build |
| `graph` | `Suite.run(graph)` | rides `guard()`; outputs threaded as addresses |
| `agent` | `routine_runner.fire(..., prompt_override=<templated>)` — the params seam finally exposed | the ONLY consequential kind: job `permission_mode` (default plan) + `max_turns`; auto-fired agent work above plan requires the trigger row operator-armed |

Plus one new step **field**: `over: <selector>` — resolves to the unit list the existing items/fan
machinery consumes. v1 kinds: `{list:[...]}` · `{path:'glob'}` · `{changed_since:'watermark'}` ·
`'$prev'` / `'$step[i]'`. `{near:...}` and `{traverse:...}` are **teach-refused at the door**: *"this
selector kind lands with Plan B's coordinate query — the grammar is reserved for it."* One `over`
grammar covers targeted AND traversal AND the heartbeat's changed-set; Plan B extends the vocabulary
through the same door instead of fighting a dialect.

Params flow: `job.params` merged/validated flows-style → substituted into the decl (step-0 inputs,
`{params.x}` in shared/unit_ctx — existing seams) → `run_cascade`. The job runner is ~one page of glue
in `runtime/jobs.py`. Generative steps inherit the R2 §5 retry ladder in the runner, not authored:
transport → backoff · invalid-output → error-fed-back repair, max 2 · semantic garbage → recorded
`schema_failed`. Missing template slot at render = loud dispatch failure naming slot, job, and fix.

### The run record

**Every fire = ONE parent `op.run`** (`Suite.emit_run_record`, `op='run_job'` added to ENGINE_RUN_OPS):
`{job, trigger, fire_id, params_resolved, prompt_refs, watermark_from/to, result_address, duration,
outcome}` — rendered params + prompt versions recorded (provenance: exactly what produced this output).
Children thread by `fire_id`: cascade steps already per-step op.run; `agent` steps land the routine
record as an op.run child (closing R1's never-indexed gap for every agent fire); `graph` steps emit a
child *referencing* their `kind='run'` event (73 graphs' history not migrated). Terminals:
`succeeded | failed | schema_failed | check_flagged | budget_exhausted | cancelled | stalled`;
duplicate fire of an active run-key returns the existing run with `deduped:true` — a success shape.
Run keys are derived (`<job>:<firing-identity>:<params-hash>`); dedupe lives in the substrate, not
agent discipline. `runs`/`run_stats` answer job history with zero new query machinery.

### Freshness — the independent second eye (read-side only, both faces)

`job_freshness()` — a shared function, NOT part of the trigger path: per watched surface (extraction ·
embeddings · joins · descriptions · transcripts/recall), compare the source change signal (git sig
timestamp · latest `ledger.run` id — D2's run-id-inequality semantics) against the last **succeeded**
fire covering it → **PASS / WARN / FAIL** with declared lag thresholds per surface (rows in the job's
`outputs.freshness` block). FAIL transitions surface to the operator. Because it reads watermarks and
run records only, **it still fires when the trigger machinery is broken, mis-tuned, or paused** —
D2's two-eyes principle as an alarm instead of a scheduler. On the UI it is region 3 of the jobs face
and the first world-map binding (θ = surface family, r = lag, color = PASS/WARN/FAIL).

### The floor (concentric, all existing mechanisms)

1. **Outermost**: the autonomous loop is env-gated — one operator switch for auto-run as a whole.
2. **Definition floor**: `proposes_only` default-true, enforced three layers (door · runner ·
   governance-scan fold of jobs.json into COG_SOURCES).
3. **Computation floor by construction**: steps write `run://` only; no resolve/approve/dispatch in the
   vocabulary; FORBIDDEN_DESTINATION_VERBS holds.
4. **Standing triggers arm through Tim**: any agent-authored non-manual trigger saves as `proposed` +
   surfaced ask (`you_can` guidance in the return); only `resolve_surfaced` stamps `armed_by`. Manual
   fires of pure-compute bodies run immediately. Inline fires (`fire(job={...})`) can't be standing by
   construction and **refuse `agent` steps**; a repeated inline shape gets a register-me nudge.
5. **The `agent` kind is doored**: permission_mode + max_turns; never class-approved (when classes
   arrive at all — deferred, constraint pre-decided).
6. **Every refusal teaches** (D3's door): field path + closest-match + `fix` fragment + resubmit line;
   `define(check=true)` iterates to clean before anything saves.

### Faces (one function, two faces)

`Suite.job_*` + `job_freshness` serve BOTH the MCP tool and `/api/jobs`. MCP:
`jobs(op = describe | define | fire | runs | watch | probe | pause | resume | cancel | retire)` —
`describe(about='vocabulary'|'targets'|'<id>')` joins the registries into the runnable-ref catalog with
params schemas (the schema IS the documentation). UI (when ③ reaches it): JOBS (definitions + asks
float to top) · RUNS (state-colored timeline, step trail, breadcrumbed errors verbatim) · FRESHNESS
(the pulse). Tim's verbs = the same ops, different floor.

### Component diagram

```
      MCP jobs(describe|define|fire|runs|watch|probe|…) ─┐            ┌─ /api/jobs · UI: JOBS/RUNS/FRESHNESS
                                                         └ Suite.job_* ┘        ▲
                                                              │            job_freshness()  ← reads watermarks
             ┌────────────────────────────────────────────────┴─────────┐      + run records ONLY (2nd eye)
             │ jobs.json      (_ActionRegistry · door build_job)        │
             │ triggers.json  (_ActionRegistry · door build_trigger     │
             │                 + rules.validate_ast · states:           │
             │                 proposed→armed→paused→retired)           │
             └────────────────────────────────────────────────┬─────────┘
  /api/activation/tick (manual, always) ─► ActivationCaller.activation_tick
  COMPANY_ACTIVATION_LOOP (operator switch)  ├─ background_tick / RollupDriver / propose_mode (existing)
                                             └─ TriggerDriver (NEW)
                                                  │ trigger_state.json {sig·changed_at·watermark·in_flight}
                                                  │ due? quiet-window ∧ when-AST ∧ single-flight · loud stall
                                                  ▼
                                         run_job(job, params, watermark) = run_cascade(materialized decl)
        ┌─────────┬─────────┬───────────────┬─────┴──────┬──────────────┬───────────────────┐
      role      items     reduce         retrieve/     flow (NEW)    graph (NEW)         agent (NEW)
    (exists)  (exists)  (exists)        check/jury     Flow.run      Suite.run+guard()   routine_runner.fire
                          over:<selector> (NEW field — list·path·changed_since; near/traverse → Plan B)
                                                  ▼
        run:// step outputs · ONE parent op.run (op='run_job', fire_id, terminals incl. budget/schema/stalled)
                          · check-fail → surface · freshness FAIL → surface
```

---

## (c) THE HEARTBEAT — row #1, actual rows

**Job row** (`jobs.json`):
```json
{"id": "ledger-heartbeat",
 "label": "Ledger heartbeat — change → extract → re-embed → joins → descriptions",
 "description": "Incremental maintenance of the ledger from the change watermark; upgrade-1 as a registered job.",
 "run": {"cascade": "heartbeat-incremental"},
 "params": {"project":      {"desc": "project root",               "default": "/home/tim/company"},
            "since":        {"desc": "watermark override (ISO)",   "default": null},
            "budget_files": {"desc": "max changed files per fire", "default": 200}},
 "budget": {"model": null, "time_budget_s": 600,
            "max_total_tokens": 300000, "per_day": {"max_total_tokens": 2000000}},
 "outputs": {"address": "run://job/ledger-heartbeat/<fire_id>",
             "notify": [{"on": "failed|budget_exhausted|check_flagged|stalled", "to": "surface"}],
             "freshness": {"surface": "ledger", "warn_lag_s": 1800, "fail_lag_s": 86400}},
 "proposes_only": true, "permission_mode": "plan", "enabled": true}
```

**Cascade `heartbeat-incremental`** (saved through the normal cascade door):
1. `flow` **changed-set** — git diff + dirty files since `{watermark|params.since}`, capped
   `budget_files` → the changed `code://` unit list. *(Deterministic set-work in code — the dragnet
   lesson, enforced by shape.)*
2. `flow` **incremental extract + INGEST-WITH-CARRY-FORWARD** — re-extract changed files only; at
   ingest every unit with unchanged `source_hash` **carries its prior descriptions + generated-by edges
   onto the new run** (the proven 18a3a875 repair, promoted from emergency script to contractual step;
   carried units recorded as carried — a derivation-tag, never a silent skip).
3. `flow` **re-embed changed** — bounded batch over changed units, `over:'$prev'`.
4. `flow` **joins re-derive** — ui→code / reference edges, scoped to touched units.
5. `items` **descriptions re-generate** — fan over units with changed `source_hash` only (role step,
   output_schema'd, budgeted).
6. `check` **supersession guard** (deterministic, checks registry, `on_fail: flag`) — post-conditions:
   `entry_latest` description coverage for UNTOUCHED scopes not reduced · generated-by edge count not
   reduced · dangling-edge ratio not worsened. Flag → `surface` → operator inbox same hour.

**The supersession contract, stated as the invariant:** *no fire may reduce the enrichment coverage of
units it did not change.* Step 2 enforces it now; the step-6 check detects it in-run; the freshness FAIL
alarm detects it out-of-band. If Plan B ships layered `unit_latest`/carry-at-ingest, step 2 degrades to
a no-op and the other two layers remain — the contract is mechanism-independent, so A and B land in
either order without re-opening the heartbeat.

**Trigger row** (`triggers.json`):
```json
{"id": "heartbeat-on-change", "job": "ledger-heartbeat", "kind": "change",
 "config": {"sources": ["git:/home/tim/company"], "quiet_window_s": 120,
            "refire_mode": "replace", "max_delay_s": 3600},
 "when": {"op": "ge", "args": [{"op": "field", "path": "change.files_changed_n"},
                                {"op": "lit", "value": 1}]},
 "params": {}, "priority": 10, "state": "proposed", "enabled": true}
```
*(Written as `proposed`; Tim's resolve arms row #1 — the floor applies to the system's own heartbeat,
deliberately: the first arming is the recognition checkpoint made operational.)*

---

## (d) WORKED AGENT EXAMPLES (D3's three, adapted to the decided grammar)

**(i) The heartbeat, as the fire-and-arm experience** — an agent (or the build itself) saves the job +
trigger rows above; the return is `{"state":"proposed", "surfaced":"ask://surface_review/.../heartbeat-
on-change", "why":"standing triggers arm through the operator", "you_can":["fire once now — op='fire'
needs no approval", "watch for state='armed' via op='describe'"]}`. Tim resolves on the surface. Later:
`jobs(op='describe', about='ledger-heartbeat')` → `{"state":"armed", "trigger":{"kind":"change",
"last_watermark":"2026-07-02T09:12Z"}, "next":"fires 120s after next quiet window", "freshness":"PASS"}`.

**(ii) One-off: re-describe 12 changed files, then re-embed desc** — inline fire, no registration,
still recorded:
```
jobs(op='fire', job={
  "run": {"cascade_inline": {"name": "_inline", "steps": [
    {"kind":"items", "op":"generate", "role":"describe_code", "model":"kimi-k2",
     "output_schema":"schema://code-description@2",
     "over": {"list": ["code://company/canvas/app/src/A.tsx::render", "...12 addresses"]}},
    {"kind":"flow", "flow":"re_embed", "over":"$prev", "params":{"emb":"desc"}}]}},
  "budget": {"max_total_tokens": 60000}})
→ {"run":"run://job/_inline/2026-07-02T10:03:b31c", "state":"queued",
   "outputs_will_land":["run://job/_inline/.../0-describe_code","run://job/_inline/.../1-re_embed"],
   "poll_after_s": 15}
```
`watch` returns the step trail with per-step `units`, `out` addresses, and token actuals; addresses are
known before results exist — the next agent never searches for an output. (Inline bodies refuse `agent`
steps; the fourth identical inline fire this week returns a nudge with a prefilled `define` call.)

**(iii) Conditional: when a test file gains a powered-by edge, refresh the ui-join rung** —
```
jobs(op='define', job={"id":"ui-join-on-powered-by",
  "run": {"cascade_inline": {"name":"refresh-ui-join",
          "steps":[{"kind":"flow","flow":"refresh_rung","params":{"rung":"ui-join"}}]}},
  "outputs": {"notify":[{"on":"succeeded","to":"board"}]}})
jobs — trigger row: {"kind":"condition", "config":{},
  "when": {"op":"eq","args":[{"op":"field","path":"event.edge_kind"},{"op":"lit","value":"powered-by"}]},
  ...}  → proposed → Tim arms.
jobs(op='probe', id='ui-join-on-powered-by')
→ {"would_fire": false, "evaluated_at":"2026-07-02T10:07Z", "cursor":"edge-seq:88412", "matched": []}
```
The condition is a tick-time predicate over the trigger snapshot with a held cursor — never a resident
poller; `probe` answers "would this fire, and on what?" without firing.

---

## (e) BUILD SEQUENCE (step 1 is a walking skeleton)

1. **Walking skeleton, manual-only:** `build_job` door + `jobs.json` + MCP `jobs` tool (`describe ·
   define(check=) · fire · runs` subset) + `run_job` over the EXISTING step vocabulary + parent op.run
   from day one. **Verifies D3's tagged assumption immediately** (cascade decl as job body, params
   substitution) before anything else stacks on it.
2. **Step kinds `flow` + `graph` + the `over` field** (list/path/changed_since) — the heartbeat body
   becomes expressible; teach-refusals for near/traverse.
3. **`TriggerDriver` in the tick:** manual/schedule/condition kinds + `trigger_state.json` +
   single-flight + loud stall + `probe`/`pause`/`resume` ops + proposed→armed lifecycle.
4. **`change` kind** (git sig · quiet window · watermark · max_delay throttle) → **write the two
   heartbeat rows**; supervised fires through `/api/activation/tick`, loop OFF (①'s supervised-flip
   style).
5. **The supersession contract + freshness:** carry-forward-at-ingest flow (step 2) + the `check` guard
   (step 6) + `job_freshness()` with FAIL surfacing. **Adversarial test required here:** deliberately
   strand an enrichment run in staging and prove all three layers fire (the check flags, freshness goes
   FAIL, the surface shows it).
6. **`agent` step kind + arming doors;** migrate the 5 routines (each = job row + schedule trigger);
   Tim arms `COMPANY_ACTIVATION_LOOP`.
7. **Faces + retirements:** `/api/jobs` routes over the same Suite functions; the UI freshness region /
   world-map binding; deprecate the flows run-face and routines tool toward `jobs`; **retire
   `routine_schedule.py`** (the tick replaces generated timers); fold the 2 live systemd timers into
   schedule-trigger rows; verify the lift-ready property (rows flat, no store-class coupling) for the
   eventual Supabase move.

---

## (f) REJECTED ALTERNATIVES (what each take lost, and why)

| rejected | from | why |
|---|---|---|
| **Postgres `jobs` schema now** (asset/queue/run/watermark/outbox tables) | D2 | Builds on Plan B's moving ground; buys concurrency nothing consumes on one machine; north-star says Supabase deliberately later. Survives as the NAMED lift (dimension 8) — the rows are shaped for it. |
| **Staleness-derived scheduling / the full asset graph** (derived_from, partitioning, automation ASTs, "the heartbeat falls out of declarations") | D2 | The conceptually strongest idea and the biggest quiet-failure surface: "a subtle watermark bug reads as *not stale*" is the silent-failure class Tim's law exists to kill. Also the largest new-machinery bill and D2's own "sixth mechanism" risk. Its two best organs are kept: freshness-as-independent-alarm and watermark-as-run-id. The full graph is the future IF the derivation web outgrows one cascade — D2 §§1–2, 5 is that future's filed shape. |
| **Materializer contract** ({kind,ref,params} single-step dispatch) | D2 | A new dispatcher module over the same executors, and single-step-only — chains need cascades anyway. The cascade body subsumes it; `python` kind collapses into `flow`. |
| **`near`/`traverse` selectors in v1** | D3 | Front-runs Plan B into a second dialect. Grammar reserved, door teaches, Plan B extends. |
| **Pre-approved trigger classes in v1** | D3 | The class predicate is an undesigned floor bypass; deferred with its constraint pre-decided (data-AST, auditable, never for `agent` steps). |
| **`do:`/`over:` re-skin of the whole step grammar** | D3 | Don't re-skin a working language (8 cascades, the runner, 73 graphs' conventions); take `over` as a new FIELD, keep the existing kind/op vocabulary. |
| **`job:` step kind (job-calls-job composition)** | D3 | Deferred: cheap cycle-check but adds recursion semantics to the runner before the skeleton has proven the three simpler kinds. Revisit after step 6. |
| **jobs as repo files** (the flows pattern) | (all rejected it) | R2 trap #3 verbatim: the moment a definition isn't a row, agents can't configure it through MCP and the premise breaks. |
| **pg_cron / systemd timers as the scheduler** | (all) | Second scheduler, hard constraint. `routine_schedule.py` retires; pg_cron is at most the future outbox feeder. |
| **LISTEN/NOTIFY or git hooks as delivery** | (all, R2 trap #1) | Fire-and-forget delivery is a silent-drop machine; rows/sig are the source of truth, hooks at most a latency hint. |

## (g) HONEST RISK REGISTER (the nine, merged and deduped, + what the merge adds)

1. **Single-process assumption is load-bearing (D1-1).** No queue table means the in-flight/stall
   mechanics are advisory, not atomic; safe only while exactly one `ActivationCaller` exists. Mitigation:
   in-flight double-recorded (state + event); the lift is named and the rows are shaped for it. Residual:
   the temptation to patch the state file instead of lifting when parallelism actually arrives.
2. **`run_cascade` becomes load-bearing for everything (D1-2).** Agent sessions and side-effectful
   staging inside a synchronous step loop stress contracts it wasn't designed under; a runner bug now
   stalls the heartbeat AND chat-adjacent cascades. Named fallback seam: the thin dispatcher above
   executors. The skeleton (build step 1) exists to surface this early.
3. **Change detection is partly code, not data — and git-shaped (D1-3).** Non-git truth (`.data/store`,
   ledger tables) is invisible until the reserved `ledger:` source lands post-Plan-B; quiet-window
   mechanics live in `TriggerDriver` Python with only parameters as rows. Accepted deliberately, confined
   to one module behind a stable trigger-row schema.
4. **The freshness projection can lie green (D2-1, transformed).** Rejecting staleness-*scheduling*
   shrank but did not remove the quiet-failure surface: a wrong watermark comparison in `job_freshness`
   reads as PASS. Mitigations: it reads only two simple inputs (change sig vs last succeeded fire); the
   build-step-5 adversarial stranding test is REQUIRED, not optional; the in-run check step is an
   independent layer. Residual is real and must stay tested.
5. **Latency/starvation tuning is a live surface (D2-2).** Quiet window + tick cadence + `max_delay_s`
   give minutes-scale freshness; a continuously-editing agent re-arms until throttle. Mis-tuning reads
   as thrash or staleness complaints in week one. (→ open question 2 for Tim.)
6. **Jobs could become the sixth mechanism (D2-3).** The guard is the retirement list in build step 7
   (routines tool, flows run-face, systemd generator, the 2 timers) — if the build adds jobs without
   retiring surfaces, unification inverts into six silos. Procedural, so it must be held in the
   loop-prep acceptance gates.
7. **The selector seam still front-runs Plan B (D3-1, mitigated).** Even the v1 subset fixes grammar
   Plan B must honor (`over`, selector-kind names). Accepted: the grammar is data and extension goes
   through the same door; the coordinate query was always going to need a caller-side shape.
8. **Tim in the arming loop (D3-2).** Every standing trigger waits on Tim's resolve until classes are
   designed; the system's own currency can stall on his attention. At v1 volume this is deliberate
   (arming IS the floor); it becomes friction as job count grows. (→ open question 1.)
9. **Inline fire is a second citizenship (D3-3, tightened).** Adopted with the tightenings (no `agent`
   steps inline; repeat-nudge toward `define`). Residual: `_inline` runs are harder to attribute at
   volume; the nudge is advisory.
10. **NEW — merge-created: two deferred lifts stack on the same rows.** The Supabase lift (dim 1) and
    the queue lift (dim 8) are both "the rows are ready" claims that nothing currently exercises. If
    both arrive together (growing model layer + everything-in-Supabase), "lift-ready" gets its first
    test under pressure. Mitigation: build step 7's explicit lift-ready verification; keep row shapes
    flat and store-class-free as a checked property, not an intention.
11. **NEW — merge-created: the op surface outruns the substrate.** D3's ten ops ride D1's minimal
    skeleton; `watch`/`probe`/teach-refusals are UX promises the walking skeleton doesn't need and
    could drag step 1 into surface-building. Mitigation: the op subset per build step is pinned in (e)
    — skeleton ships four ops.

## (h) OPEN QUESTIONS — only Tim can answer these

1. **Arming friction threshold.** v1: every agent-proposed standing trigger waits for your resolve —
   arming autonomy stays with you absolutely. Pre-approved classes (approve a job *shape* once, matching
   instances auto-arm) are designed-later with constraints pre-decided. **Is individual arming
   acceptable until then, or should classes move earlier in the sequence?** (This is your attention
   budget; nothing technical decides it.)
2. **What should the pulse feel like?** The decided defaults (120s quiet window + 60s tick + bounded
   batches) make the world current **minutes** after an edit burst settles — self-healing, thrash-proof,
   cheap. Near-live freshness (seconds) is possible but changes the tuning and the compute spend.
   **Is minutes the right heartbeat, or do you want the map to move as you watch?**
3. **The real budget ceilings.** The design injects defaults into any unbudgeted generative step (the
   numbers in the rows above — 300k tokens/fire, 2M/day for the heartbeat — are placeholders). **What
   are the actual per-fire and per-day ceilings you want the system to hold itself to?** (Money/compute
   allocation is yours; enforcement is the system's.)
