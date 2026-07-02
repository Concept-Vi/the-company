# Plan A design take · ASSET-FIRST / DECLARATIVE (perspective 1 of 3) — 2026-07-02

*Independent design lens over R1 (existing machinery) + R2 (external patterns), leaning maximally into
R2's Dagster finding: DECLARE the data assets + derivation edges + freshness, and DERIVE all recurring
work from staleness. Jobs remain for one-offs; the heartbeat stops being a job at all.
Working doc — one perspective, to be judged + synthesized. Assumptions flagged inline.*

---

## 0. The stance (one paragraph)

The Company's recurring work is not "jobs that happen to touch data" — it is data that must stay fresh.
Every heartbeat step already has the shape *X is derived from Y; when Y moves, X is stale*. So the primary
declaration is the **asset row**: what exists, what it's derived from, who materializes it, how fresh it
must be. The scheduler owns no schedules; it owns **one comparison** (input watermarks vs last
materialization) and derives everything else. This is the everything-as-data law applied to time itself:
the heartbeat becomes rows an agent can read, edit, and render — and the just-lived supersession incident
(run `390286ec` stranding 4199 descriptions + 1403 generated-by edges below `*_latest`, hand-repaired in
`18a3a875`) becomes a *class the system detects and repairs by construction*, because enrichment layers
are assets whose staleness against the latest extraction run is first-class.

Reuse spine (R1's top-5, adopted whole): `run_cascade` as chain executor · `rules.validate_ast/evaluate`
as the condition language · `ActivationCaller` as the ONE tick host · `routine_runner.fire` as the
agent-work primitive · the cascades-in-store precedent as proof agents author rows through a door.

---

## 1. The asset row

### 1.1 Where rows live: STORE ROWS, not files (decided, with the tradeoff stated)

Postgres rows in a new `jobs` schema, same database as the ledger. Three reasons:
- R2 trap #3: definition-in-code/files is Airflow's most-regretted property — the moment a declaration
  isn't a row, agents can't configure it through MCP and the premise breaks.
- The cascades precedent (`.data/store/cascades.json` + `build_action` one-door validation) already
  proves the repo's own pattern for "agents author runnable declarations as data."
- The tick's derivation query is SQL over watermarks that live in the same DB — declarations beside
  state means one query, no sync seam.

What we keep from the file-registry pattern: **one validation door** (`asset_declare/asset_edit` — a
single Python function + SQL constraint set; malformed rows refuse at write, never at tick), id
discipline, and fail-loud discovery. What we lose: git review of declarations. Mitigation (borrowed from
`routine_schedule`'s generates-not-arms): a `jobs(op='export_seed')` renders the current asset rows to
`jobs/seed/assets.json` in-repo on demand — a versioned snapshot, never the source of truth. Every
declare/edit also emits a `self_change` event with the acting session (`exchange://` provenance per the
north star: every row traces to its generating transcript).

### 1.2 `jobs.asset` — the declaration (long-lived, versioned)

| field | type | meaning |
|---|---|---|
| `asset_id` | text PK | An ADDRESS in the one grammar: `asset://<family>/<name>` with `{partition}` slots, e.g. `asset://ledger/{project}/extraction`, `asset://emb/{project}/{space}/{embedder}`. Resolvable by the one resolver (`contracts/address.py` gains the `asset://` scheme). |
| `label`, `description` | text | self-description discipline; rendered on both faces. |
| `partitioning` | jsonb | `{axes: ["project"] \| ["project","space","embedder"], discover: "<named SQL>"}` — partitions are DISCOVERED from data (distinct projects in `entry_latest`, spaces from the corpus registry), never hand-enumerated. See §6. |
| `derived_from` | jsonb | `[{asset: "asset://source-tree/{project}", map: "identity"}, {asset: "asset://ledger/{project}/descriptions", map: "self-prior"}]` — upstream refs with a partition mapping: `identity` (same partition), `all` (fan-in), `self-prior` (own last materialization — the carry-forward edge, §2.3). Also plain **source keys** for non-asset inputs: `{source: "ledger.run/{project}"}`. |
| `materializer` | jsonb | `{kind, ref, params}` — §4. |
| `automation` | jsonb | condition AST — §1.3. |
| `freshness` | jsonb | `{warn_lag_s, fail_lag_s}` → PASS/WARN/FAIL computed INDEPENDENTLY of the automation path (two separate eyes on the same watermark data — the alarm still fires when automation is broken, wrong, or paused). |
| `quiet_window_s` | int | debounce re-arm window (§3); `max_delay_s` caps starvation. |
| `allocations` | jsonb | model/budget: `{model?, max_calls?, max_total_tokens?, max_tokens_per_call?}` — enforced by the executor; `budget_exhausted` is a distinct recorded terminal state (R2 §5.3). |
| `floor` | jsonb | for `agent_prompt` kind only: `{permission_mode: "plan", max_turns: N}`; see §4 floor rules. |
| `enabled` | bool | agents may declare disabled assets freely; ENABLING an `agent_prompt` asset or one whose allocations exceed a threshold SURFACES for operator resolve (the flows-propose floor transplanted). |
| `owner`, `created_by`, `created_at`, `version` | | provenance + append-only `jobs.asset_revision` history on every edit. |

Deliberately absent: `last_materialized_at`, watermarks, status — **declaration and state never share a
row** (the Prefect/Dagster split; overwriting state on the definition is how history gets silently lost).

### 1.3 Automation-condition vocabulary (a data-AST, reusing `rules.RULE_OPS` discipline)

Atoms: `stale` (any upstream watermark > last materialization's snapshot) · `missing` (never
materialized) · `cron_due("0 3 * * *")` (cursor-tracked, fires once per window) · `in_progress` ·
`upstreams_settled` (no upstream materialization currently running — Dagster's built-in anti-thrash) ·
`quiet_for(s)` (no input event for this key in s seconds) · `within_window("02:00-06:00")` · `manual`
(never auto-fires). Composition: `all_of / any_of / not`.

The three named policies are just canned ASTs:
- **eager** ≡ `all_of(any_of(stale, missing), upstreams_settled, not(in_progress))`
- **on_cron(x)** ≡ `all_of(cron_due(x), any_of(stale, missing))` — cadence-gated, but only when something actually moved
- **on_missing** ≡ `all_of(missing, not(in_progress))`

Validated at declare-time by one `validate_automation_ast` (same fail-loud shape as
`mode_detection_rules`); evaluated pure over a snapshot at tick-time. Unknown atom = refusal at the door,
never a silent no-op at the tick.

### 1.4 State tables

- **`jobs.materialization`** (append-only): `id, asset_id, partition jsonb, run_id → jobs.run,
  started_at, finished_at, status, input_watermarks jsonb` ← *the snapshot of every upstream watermark
  at materialization time — staleness is exactly `current_watermark > snapshot`, never time-based
  guessing* — `output_ref` (a `run://` or ledger `run_id`), `error`. View `materialization_latest`
  per (asset, partition).
- **`jobs.watermark`**: `(source_key, partition) → mark jsonb, bumped_at` — mark is whatever identifies
  "position": a timestamp, a ledger `run_id`, a tree content-hash. Bumped by §2.
- **`jobs.input_event`** (outbox): `id, source_key, partition, payload jsonb (e.g. changed paths),
  created_at, consumed_by_tick` — the coalescible burst detail; the watermark is the loss-proof cursor,
  events are the optional specifics (R2 §4.3: a missed event is caught by the next watermark run).

---

## 2. Watermarks + change detection (what bumps what, in THIS system)

### 2.1 The bumpers

| source | mechanism | notes |
|---|---|---|
| ledger tables (`entry`, `symbol`, `edge`, `embedding`, descriptions) | `AFTER INSERT/UPDATE` triggers → same-transaction `input_event` row + watermark upsert (transactional outbox, R2 shape 5) | Because the ledger IS in Postgres, this sees **every writer** — MCP tools, ops scripts, hand-repairs — the change-visibility Airflow's Datasets can't have. |
| `ledger.run` completing (`status='complete'`) | trigger on `ledger.run` → watermark `ledger.run/{project}` = the new `run_id` | **This is the supersession tripwire** (§2.3). |
| working tree (source files) | the ONE poll: sensor asset `asset://source-tree/{project}` — a cheap deterministic tree-hash/mtime walk run each tick (bounded), bumps its own watermark on change | Never a resident waiter (R2 trap 2 — sensors are tick-time predicates, not jobs). |
| git hooks (post-commit) | optional POST to the tick's manual door as a *latency hint only* | The row/poll is the source of truth; a lost hook loses nothing (the LISTEN/NOTIFY lesson generalized). |
| transcripts / session exports | the existing exporter becomes the materializer of `asset://transcripts`, `on_cron`; its completion bumps a watermark like any other | folds one of the two live systemd timers into the system. |

### 2.2 The 18-runs reality

`ledger.run` already accumulates runs and `entry_latest`/`symbol_latest`/`edge_latest` resolve through
`latest_run` per (project, purpose) (`ops/ledger_build.py:898, 1377`). The asset system does not fight
this — it makes the run pointer the watermark: the extraction asset's mark IS the latest `run_id`.
Materializations record which `run_id` they were built against; staleness is run-id inequality, exact and
cheap. Old runs remain history (they are the materialization trail the asset system would otherwise have
had to invent).

### 2.3 Supersession as a first-class derivation edge (the incident, designed away)

The incident: a rebuild run (`390286ec`) made `*_latest` resolve to fresh rows, stranding the
descriptions + `generated-by` edges attached to the PRIOR run's rows — invisible until hand-verified,
hand-repaired by `source_hash` carry-forward (`18a3a875`).

The design move: **enrichment layers are assets whose `derived_from` names BOTH the base extraction AND
their own prior materialization**:

```
asset://ledger/{project}/descriptions
  derived_from: [ {source: "ledger.run/{project}", map: identity},     ← the tripwire
                  {asset: self, map: self-prior} ]                     ← the carry-forward input
  materializer: python ledger_enrich_carry
                params: {project: "{partition.project}",
                         new_run: "{watermark:ledger.run/{project}}",
                         prior: "{self_prior.output_ref}"}
  automation: eager · freshness: warn 1h / FAIL 24h
```

Consequence chain, automatic: new extraction run completes → trigger bumps `ledger.run/{project}` →
descriptions asset is stale *by watermark inequality* (DETECTED) → tick enqueues → materializer runs the
proven carry-forward (`source_hash` match from the prior run's rows — exactly the `18a3a875` repair, now
a registered runnable) + delta-describes only genuinely new/changed rows (REPAIRED) → materialization
records the new `run_id` in its snapshot. If anything in that chain breaks, the **independent freshness
check** goes WARN→FAIL and surfaces — stranded enrichment can no longer be silent. Same declaration
shape for `asset://ledger/{project}/provenance-edges` (the generated-by layer).

*Honest interplay with Plan B:* Plan B's proper fix (layered `unit_latest` / carry-forward-at-ingest)
removes the stranding by construction; when it lands, this asset's materializer shrinks to
delta-describe only — the declaration, freshness alarm, and derivation edge stay unchanged. The asset
row is the durable part; the materializer body is the swappable part. That is the right coupling.

---

## 3. The evaluation tick

**Where it lives: inside `activation_tick`, as the fourth driver on the module-level `ActivationCaller`**
(beside background_tick, RollupDriver, propose_mode) — R1 reuse #3, the no-second-scheduler constraint
honored literally. The manual door (`POST /api/activation/tick`) exercises it today; the autonomous
cadence stays behind `COMPANY_ACTIVATION_LOOP` (operator-armed, default 60s). pg_cron is noted as the
eventual tick generator when "everything ends up in Supabase," not adopted now — one scheduler at a time.

**Single-flight:** `pg_try_advisory_lock(hashtext('jobs_tick'))` on a dedicated connection at tick
start; held → skip (logged, not silent). Session-scoped, so a crashed holder self-releases.

**The tick, in pseudo-steps:**

1. **Sense** — run due sensor assets (source-tree poll; bounded per tick); bump watermarks on change.
2. **Derive** — ONE SQL comparison: for each enabled asset × discovered partition, join
   `materialization_latest` against current `jobs.watermark` rows for its `derived_from` set →
   `{stale, missing, in_progress, quiet_for, cron_cursor}` snapshot; evaluate each asset's automation
   AST pure over the snapshot.
3. **Enqueue** — for each TRUE: upsert into `jobs.queue` with
   `job_key = 'asset:<asset_id>:<partition-hash>'`, **replace mode**, `run_at = now() + quiet_window_s`
   (graphile-worker's debounce: every new change re-arms; the job runs only after quiet). Payload
   array-merges changed paths from unconsumed `input_event` rows. Anti-thrash guards: `in_progress` on
   the same key → do NOT replace, mark the running materialization `superseded_pending` so a successor
   row spawns at completion (the mid-run-event edge case — never lost); after `max_delay_s` of
   continuous re-arming, switch to preserve_run_at (throttle) so a permanently-busy tree still gets
   periodic materialization.
4. **Claim** — `UPDATE jobs.queue SET state='running', locked_by=$tick ... WHERE id IN (SELECT ... WHERE
   state='available' AND run_at <= now() ORDER BY priority, run_at LIMIT $cap FOR UPDATE SKIP LOCKED)
   RETURNING *` — bounded batch = backpressure; leftover work is graceful lag, never pile-up.
5. **Dispatch** — each claimed row through the ONE executor (§4). Success → `jobs.run` +
   `jobs.materialization` append + queue row completed. Failure → `run_at = now() + backoff(attempts)`,
   `attempts++`; at `max_attempts` → `state='discarded'` with `last_error` preserved AND a
   `surface_review` event with breadcrumbs (dead-letter is a first-class surfaced outcome, never a drop
   — the fail-loud law).
6. **Record** — append `jobs.tick_log`: watermarks read, events consumed (cursor semantics — each tick
   only considers events since the last it consumed, Dagster's duplicate-trigger prevention), what was
   enqueued/claimed/skipped and WHY. "Why didn't X run" is a query, not an investigation.
7. **Alarm** — recompute freshness PASS/WARN/FAIL per (asset, partition) from watermarks alone
   (independent of steps 2–5); transitions to FAIL surface.

Quiet windows are per-asset data (`quiet_window_s`); global maintenance windows are just
`within_window(...)` atoms in the AST — no scheduler-side special cases.

---

## 4. The materializer contract

`materializer: {kind, ref, params}` — six kinds, ALL dispatched by one executor that already exists in
pieces (this is the single "what to run" dispatcher R1 gap #3 demands):

| kind | dispatches to | floor |
|---|---|---|
| `flow` | `flows` registry `run(**params)` | proposes_only, unchanged (3 layers) |
| `cascade` | `run_cascade(name, inputs=params)` | run:// computation only |
| `graph` | `run_graph` | `guard()` policy router |
| `role` | `run_role` | run:// only |
| `agent_prompt` | `routine_runner.fire` with **`prompt_override` finally exposed as the params seam** (R1 reuse #4) | asset `floor` block: permission_mode (default plan) + max_turns; ENABLING surfaces for operator resolve |
| `python` | a small in-code **handler registry** dict (`ops/` functions: `ledger_build` incremental, `build_embeddings`, the carry-forward, the tree-hash sensor) | rows for everything, code only in the handler registry (R2's closing law) |

**Params get the asset context by template rendering.** Param values may contain slots the executor
renders from the materialization context:

- `{partition.project}`, `{partition.space}`, `{partition.embedder}` — which slice is stale
- `{changed}` — coalesced changed addresses/paths from the consumed input events (may be empty — then
  the materializer discovers its own work from the watermark, the self-healing default)
- `{since_watermark}` / `{watermark:<source_key>}` — the position bounds
- `{upstream.<asset>.output_ref}` — the input materialization's address
- `{self_prior.output_ref}` — own last materialization (the carry-forward slot)

Missing slot at render time = loud dispatch failure with the breadcrumb naming the slot, the asset, and
the fix. The `jobs.run` row records the RENDERED params (exact provenance: this run, these inputs, this
prompt version if the ref is a role — the Langfuse discipline).

`jobs.run` (the ONE run record R1 gap #5 demands): `run_id, trigger_kind (asset|manual|event|agent),
actor, asset_id?, job_id?, materializer snapshot, rendered_params, started/finished, status
(complete|failed|budget_exhausted|schema_failed|discarded), output_ref, error, usage {tokens_in/out,
calls}`. Every fire — asset-derived, manual, agent one-off — converges into this same row (Windmill's
uniformity), and each also emits the existing `op.run` event so `runs`/`run_stats` discovery works
unchanged.

---

## 5. The heartbeat as declarations — the FULL asset graph

No job named "heartbeat" exists anywhere below. Partition axis is `project` unless noted.

```
asset://source-tree/{project}          SENSOR   python tree-hash walk        automation: every tick (bounded)
        │ bumps watermark source-tree/{project}
        ▼
asset://ledger/{project}/extraction             python ledger_build --incremental {changed}
        │ (writes entry+symbol+edge atomically in ONE ledger run — one asset, one materializer)
        │ automation: eager · quiet 120s · freshness warn 30m
        │ completion bumps ledger.run/{project} (DB trigger)
        ├────────────────────────────────────────────────┐
        ▼                                                ▼
asset://ledger/{project}/ui-join                asset://ledger/{project}/descriptions
  python ui-join extractor                        python ledger_enrich_carry  ◄─┐ self-prior
  (the 390286ec rebuild, now derived)              (carry-forward + delta-describe) ─┘
  automation: eager · quiet 300s                  automation: eager · freshness warn 1h / FAIL 24h
        │                                                │
        │                               asset://ledger/{project}/provenance-edges
        │                                 (generated-by; same carry class, derives from
        │                                  extraction + transcripts + self-prior)
        │                                 automation: eager · freshness FAIL 24h
        ▼                                                ▼
asset://emb/{project}/{space}/{embedder}        asset://emb/{project}/desc/{embedder}
  partition: project × space × embedder           (desc-space embeddings)
  python build_embeddings --space {partition.space} {changed}
  automation: eager · quiet 300s · freshness warn 1h
        │
        ▼
asset://scale/{space}/k{N}                       partition: space × k
  python rung clustering
  automation: on_cron("0 3 * * *")  — expensive; nightly, AND only if the space's embeddings moved
                                      (on_cron ≡ cron_due ∧ stale — the Dagster semantic)

asset://transcripts                              the sessions-exporter, absorbed
  automation: on_cron (its current cadence)      (one of the 2 live systemd timers becomes a row)
asset://recall/claude-sessions-index
  automation: eager on transcripts               (the other live timer becomes a row)
```

Upgrade 1's chain — *change → incremental extract → re-embed changed → joins re-derive → descriptions
re-carry* — is now literally the arrows above. Adding a new embedder or space = declaring one row (a new
partition value materializes via `on_missing` semantics inside eager). Adding a project = a new address
prefix; every `{project}`-partitioned asset discovers it (§6). Upgrades 5 (suite.py decomposition) and 6
(symbol descriptions, B-pass tail, bad-json retry) are one-off jobs (§7) or additional enrichment-class
asset rows — no new mechanism.

---

## 6. Partitioning

- **Partition = address prefix**, per Tim: a partition value is just a segment of the asset's own
  address (`asset://emb/company/repo/nomic-code` IS the partitioned identity). Freshness, watermarks,
  materializations, and queue keys all carry the partition; the world-map can render per-partition
  freshness because partitions are addresses, hence coordinates.
- **Axes are coarse and discovered**: `project`, `project×space×embedder`, `space×k`. The `discover`
  SQL names where the values come from (distinct projects in `entry_latest`, the corpus-space registry)
  so a new project/space appears as a `missing` partition, not a config edit.
- **Path-subtrees are NOT partitions.** Fine granularity rides the `{changed}` payload (coalesced event
  paths) inside a per-project materialization — the watermark pattern makes the run discover its own
  work. Per-subtree partition rows would explode the bookkeeping for zero scheduling benefit at this
  scale. (Assumption flagged: if one project's tree grows huge, promote hot subtrees to partitions
  then — the schema already permits it.)

---

## 7. One-offs / manual / agent-triggered jobs — beside, not beneath

A **job is a materializer without an asset**: `jobs.job` row = `{job_id, label, description,
materializer (same {kind,ref,params} shape), trigger: manual | once_at(ts) | event(source_key),
job_key?, reuse_policy (default allow_duplicate; assets always keyed), created_by, floor, allocations}`.

- Fired via MCP `jobs(op='fire', job=..., params=...)` or declared with `once_at`/`event` triggers the
  tick honors in step 2 (an event-triggered job is just an automation AST of one atom).
- Same queue table, same claim, same executor, same `jobs.run` record, same floor per kind. `trigger_kind`
  + `actor` distinguish it in history — nothing else does. One vocabulary; the five mechanisms stay what
  they are (the things materializers dispatch TO), and no sixth silo grows.
- Idempotency where agents double-fire: caller-supplied `job_key` + River-style partial unique index over
  active states + `reuse_policy` (`allow_duplicate_failed_only` = "retry failures, never re-run a
  success") — dedupe in the substrate, not in agent discipline.

Upgrade-5-style efforts (suite.py decomposition via mapped hints) are exactly this: an `agent_prompt`
job with params-as-data, fired stepwise, every run recorded.

---

## 8. Faces

**One function → both faces** (the north-star directive): `asset_status(asset?, partition?)`,
`asset_graph()`, `asset_declare/edit`, `materialize(asset, partition)`, `job_fire`, `runs_for(...)` are
shared functions; MCP tools and `/api/assets` + `/api/jobs` bridge routes are thin projections of them.

- **MCP**: `assets(op = declare | edit | list | status | graph | history | materialize | pause)` +
  `jobs(op = fire | list | runs)`. `status` returns per-(asset, partition): freshness PASS/WARN/FAIL,
  lag, last materialization, queue state, dead-letters. `capabilities(section='assets')` joins the
  discovery surface.
- **UI — the world-map renders freshness.** Assets are addresses, so they are coordinates in the same
  space the projection engine already renders. One data-driven binding row (θ = asset family, r =
  staleness lag, color = PASS/WARN/FAIL, size = partition count) and `LatticeView` shows the system's
  metabolic state live — meaning in the data, never in the instrument. The asset GRAPH (derivation
  edges) is the first genuinely graph-shaped thing the ③ window can draw.
- **CLI**: `company assets` (status table) — read-only, small.
- **Floor summary**: declare/edit = open through the one door, every change evented; enable of
  `agent_prompt` or over-budget assets = surface → operator resolve; materializers inherit each kind's
  existing floor; dead-letters and FAIL freshness = surfaced events. No resolve/approve/dispatch anywhere
  in the tick path.

---

## 9. Build sequence

1. **Schema + door**: `jobs.asset / asset_revision / watermark / input_event / materialization / queue /
   run / tick_log`; `validate_automation_ast`; the declare/edit door; `asset://` in the address grammar.
2. **Bumpers**: outbox triggers on ledger tables + `ledger.run`; the source-tree sensor handler.
3. **Executor**: the one dispatcher over six kinds (flow/cascade/graph/role wired first; python handler
   registry; `agent_prompt` LAST), `jobs.run` + op.run emission, budget enforcement.
4. **Tick**: fourth driver on `ActivationCaller` — derive → job_key upsert → claim → dispatch →
   tick_log → freshness alarm; advisory-lock single-flight. Manual door first; loop armed by Tim later.
5. **Declare the heartbeat graph** (§5 rows), automation OFF; materialize each once by hand through
   `materialize()`; verify outputs against the current ops scripts' outputs; then enable eager one asset
   at a time, extraction-first. (This is also where the 2 red test classes — conv_index key-form,
   capture_lenses — get their staleness contract defined, per the plan.)
6. **Faces**: MCP `assets`/`jobs` tools + shared status functions + dead-letter surfacing.
7. **UI binding**: the freshness world-map render; fold the 2 systemd timers into on_cron assets.
8. **One-off jobs op + agent_prompt kind** with the enable-surfaces floor.

---

## 10. The 3 biggest risks of THIS design (honestly)

1. **The staleness comparison is the system's single point of quiet failure.** Everything hangs on
   watermark-snapshot semantics being exactly right (partition mappings, the self-prior edge, cron
   cursors). A subtle bug reads as "not stale" — i.e. work silently not happening, the precise
   silent-failure class that already cost a day. Mitigations are designed in (freshness alarms computed
   independently of automation; tick_log makes every skip queryable; step-5 build order verifies each
   asset against the known-good scripts before enabling) — but the residual risk is real: this design
   trades visible hand-wired schedules for an inference layer, and inference layers fail quietly by
   nature. This is the design's core bet and it must be tested adversarially (deliberately strand an
   enrichment run in staging and prove the FAIL fires).
2. **Latency and starvation tuning is a live, per-asset surface.** The working tree is watched by poll +
   quiet-window debounce; an agent editing continuously re-arms eager assets indefinitely (bounded by
   `max_delay_s` throttle, but that's a knob, not a law), and the end-to-end heartbeat latency = sensor
   poll + quiet window + tick cadence + chain depth (5 hops source→desc-space). If Tim expects
   near-live freshness on the map, the defaults here give minutes-to-tens-of-minutes. Getting these
   windows right will take live iteration, and mis-tuning shows up as either thrash (re-embedding on
   every keystroke burst) or staleness complaints — both plausible in week one.
3. **The asset layer can quietly become the sixth mechanism.** The queue + tick + executor + four new
   tables are genuinely new machinery beside the five (however much they reuse). The design holds the
   line by making jobs "materializers without assets" and by dispatching INTO the existing five rather
   than replacing them — but if, in building, cascades grow trigger fields or routines grow their own
   queue "for convenience," Plan A's unification inverts into one more silo plus five untouched ones.
   The guard is procedural, not structural: the build must RETIRE surfaces as it goes (the 2 systemd
   timers become rows in step 7; routine cadence strings deprecate toward asset/job declarations), and
   the synthesis judge should hold this take to that retirement list.
