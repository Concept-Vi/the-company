# Plan A research · R2 — external job/trigger-system patterns (web wave, 2026-07-02)

*The best-known shapes to steal (not dependencies to adopt) for the parametric job system. Produced by a
research agent; synthesized below verbatim. Companion: R1-existing-machinery.md (the five in-repo mechanisms).*

All research complete. Here is the full report.

---

# Parametric, Data-Driven Job/Trigger System — Research Report

Scope: single machine, Postgres/Supabase, Python runtime, agents fire jobs via MCP tools, jobs may call local LLMs or spawn agent sessions. Goal: steal shapes, not dependencies.

---

## 1. Job definition as data — what the field converged on

Across seven systems, the same core record shapes recur. The differences are in *where the definition lives* (code vs rows) and *what the run history is* (status column vs event log).

**The spectrum of "job as data":**

- **Airflow** — definition is Python code (DAG files), only *runs* are data. This is its most-criticized property: no versioning of pipelines, hard to test, scheduler must re-parse code, unusable by non-developers, and the DAG is an *execution* graph (do Y after X), not a data graph. The lesson from a decade of Airflow pain: putting the definition in code couples "what should run" to a deploy; putting it in data makes it inspectable, versionable, and editable by agents/UI — which is exactly your requirement.
- **Prefect** — split the difference with **Deployments**: a *server-side row* representing a flow, carrying `parameter_openapi_schema` (a JSON Schema derived from the function signature, stored in the DB and used for validation + UI), default parameter values, schedules, and infra config. Flow-run and task-run *states* are first-class rows (`flow_run_state`, `task_run_state` tables) — every state transition is a record, not an overwrite.
- **Windmill** — the cleanest "job = JSON in, rows throughout" model: every script's main-function signature is auto-converted to a **JSON Schema stored with the script**; a job is a row = (script path/hash · JSON args · trigger kind · timestamps · result JSON), and *every* execution regardless of trigger kind (webhook, cron, flow step, manual UI) becomes the same uniform job row. Optional strict `schema_validation` makes the job fail loudly if the payload doesn't match the schema.
- **n8n** — whole workflow graph is one JSON document (nodes + connections + per-node params); executions are rows with the full data snapshot. Good for portability, but the graph-in-one-blob shape gets unwieldy — parameters aren't independently addressable.
- **Temporal** — the extreme: the run record is an **append-only event history**, and replay reconstructs state. Too heavy to copy wholesale, but two ideas are cheap to steal: (a) **the workflow ID is the idempotency key** — starting a workflow with an ID that's already open returns "already exists" instead of a duplicate, with a configurable reuse policy for *closed* runs (`allow_duplicate`, `allow_duplicate_failed_only` = "retry failures but never re-run a success"); (b) retry policy is a small declarative object (initial interval, backoff coefficient, max attempts, non-retryable error types) attached per activity.
- **Postgres-native queues (graphile-worker, River, pgqueuer, Procrastinate, pq)** — the minimal job row, battle-tested: `id · task_identifier · payload(jsonb) · queue · priority · run_at · attempts · max_attempts · last_error · locked_at/locked_by · key(jobkey) · created_at`. River adds a `state` enum (`available, scheduled, running, retryable, completed, cancelled, discarded`) with a **partial unique index** enforcing uniqueness per (args, period, queue, state-set).

**Minimal viable vocabulary (the intersection):**

| Concept | Field(s) | Notes |
|---|---|---|
| What to run | `task_identifier` (name → handler registry) | handlers registered in code; *everything else* in data |
| Params | `payload jsonb` + `params_schema jsonb` (JSON Schema) on the *definition* | validate at enqueue, fail loud |
| Trigger | on the definition: kind + config (see §2) | |
| Retry | `max_attempts`, backoff params, `attempts`, `last_error` | declarative, per-definition with per-run override |
| Idempotency | `job_key` / unique-by-(args, period, state) | dedupe at insert, not in the worker |
| Schedule | `run_at` | one column covers delay, retry-backoff, debounce |
| Run record | separate `runs` table: job ref, state transitions, started/finished, result jsonb, error, resource usage | append states, don't overwrite |
| Output address | `output_ref` — where the result was written | your "outputs addressed/recorded" requirement; Prefect/Windmill both persist results per run |

The crucial split all mature systems share: **definition table** (template: what/schema/trigger/allocations — long-lived, versioned) vs **queue table** (materialized pending work) vs **run table** (immutable history). Airflow's `dag` / `dag_run` / `task_instance` is the same triad; Prefect's `deployment` / `flow_run` / `flow_run_state` likewise.

---

## 2. Trigger models

Five trigger kinds cover the whole field; each is a small config object naming its kind:

1. **Schedule (cron)** — everywhere; pg_cron gives it natively (§3). Windmill's twist worth noting: a **scheduled poll with persisted state** ("trigger scripts" store a cursor/state JSON between runs, return only new items since last run) — this converts *any* pollable source into an event trigger with three columns.
2. **Event / pub-sub** — a row insert into a queue table (transactional outbox) + NOTIFY as a wake-up. In Postgres-land the event *is* a row; pub-sub is "trigger function writes queue rows for every subscribed job definition."
3. **Condition / sensor** — Airflow sensors are the cautionary tale: a sensor is a polling task that *occupies a worker slot while idle* (100 slots + 100 idle sensors = a fully idle cluster that can run nothing); Airflow had to bolt on deferrable operators to fix it. The stealable fix: a sensor is **not a job — it's a periodic cheap SQL predicate** evaluated by the scheduler tick; only when it flips true does a job get enqueued. Dagster sensors work this way (a cursor-carrying evaluation function run by the daemon every ~30s).
4. **Data-change** — DB trigger → queue row (§3, §4). Airflow's Datasets show the failure mode to avoid: Airflow only knows about updates *made through Airflow*; changes outside it are invisible, so the "data-aware" scheduling is really task-completion-aware. Because your ledger *lives in Postgres*, real triggers see every change regardless of who made it — you get the property Airflow can't have.
5. **Manual** — same enqueue path with `trigger_kind='manual'` and actor recorded. Windmill's uniformity is the model: every trigger kind converges into one identical job row.

### Dagster's asset-oriented model — in stealable detail

This is the standout for your ledger-heartbeat. The inversion: **don't schedule jobs — declare assets and let the scheduler derive the work.**

- **Assets, not tasks.** You declare data assets (a table, an index, a derived artifact) and their *data* dependencies (asset Y is derived from asset X) — distinct from execution DAGs ("run task Y after task X"). The graph is about what data exists and what it's derived from.
- **Materialization events.** Every time an asset is (re)computed, a materialization event is recorded. "Staleness" = comparison between an asset's last materialization and its parents' — an asset is stale when a parent has newer data than what it was last built from.
- **Freshness policies.** Instead of writing schedules, you declare per-asset how up-to-date it must be (e.g. "at most 30 min behind its sources"); the asset carries a freshness state (**PASS / WARN / FAIL**), and the scheduler works *backwards* from the declared freshness to decide what to run and when — running only what's needed, skipping unnecessary recomputation.
- **Automation conditions** (the current form, "Declarative Automation," successor to auto-materialize policies): each asset carries a condition composed from a small algebra of predicates —
  - `AutomationCondition.eager()` — rebuild whenever any dependency updates (waits for in-progress upstream runs to finish; requires upstreams materialized — built-in anti-thrash),
  - `AutomationCondition.on_cron("...")` — rebuild on a cadence, *but only after* upstreams have updated within that tick,
  - `AutomationCondition.on_missing()` — build when it's never been built and all upstreams are available,
  - composable with boolean operators (`&`, `|`, `~`) from atomic predicates like `missing`, `in_progress`, `any_deps_updated`.
- **The evaluation loop:** a daemon ticks at a fixed interval; for each asset it evaluates the condition against current state (materialization events + cursors), emits materialization requests for whatever evaluates true, and **records the evaluation result to prevent duplicate triggering** (cursor semantics — each evaluation only considers events since the last one it consumed).

**Mapping onto your ledger:** each ledger table/section = an asset row (`asset · derived_from[] · staleness_policy · automation_condition · last_materialized_at · last_input_watermark`). Source-file changes bump input watermarks (via the data-change trigger); the scheduler tick compares watermarks to `last_materialized_at`, and the heartbeat *falls out* of the declarations — no hand-wired "when X changes run Y" jobs. The whole daemon is: one tick job + one SQL comparison + enqueue.

---

## 3. Postgres as the substrate — the standard patterns

The consensus stack for a zero-extra-infra DB-centric job system:

1. **Queue table + `FOR UPDATE SKIP LOCKED`** — the backbone. Worker claims with `UPDATE ... SET state='running', locked_by=$w WHERE id IN (SELECT id FROM jobs WHERE state='available' AND run_at <= now() ORDER BY priority, run_at LIMIT $n FOR UPDATE SKIP LOCKED) RETURNING *`. Atomic, race-free, parallel-safe — two simultaneous workers get *different* rows. This is what graphile-worker, River, pgqueuer, Que, Oban all run on. Jobs survive crashes because they're ordinary rows; retries/priorities/dead-letter are just columns and queries; enqueue is transactional with your business writes (job + data change commit or roll back together).
2. **LISTEN/NOTIFY as wake-up only, never as delivery.** The known pitfalls: notifications are lost if no listener is connected (fire-and-forget), every NOTIFY-carrying commit takes a global serializing lock, and it breaks behind transaction-mode PgBouncer. The pattern all the pg-queue libraries use (pgqueuer explicitly): the row is the source of truth; NOTIFY just tells the worker "poll now instead of in 5s." A worker that missed the NOTIFY still finds the job on its next poll. Latency optimization, not a bus.
3. **pg_cron** — in the standard Supabase Postgres image (self-hosted included); dashboard module on the platform. Schedules SQL directly; supports sub-minute (seconds) syntax; caveat: max ~32 concurrent jobs, one connection each — so use it as the **tick generator** (call a `scheduler_tick()` SQL function every N seconds), not as the runner of N user jobs.
4. **Advisory locks for single-flight** — `pg_try_advisory_lock(hashtext('heartbeat'))`: exactly one runner for a named activity across all processes; session-scoped locks self-release when a crashed holder's connection dies (a real advantage over `locked_at` columns, which need a stale-lock sweeper — graphile-worker sweeps locks older than 4h). Caveat: session-scoped locks and connection poolers don't mix; take them on a dedicated connection.
5. **Trigger → queue (transactional outbox)** — for data-change triggers: `AFTER INSERT/UPDATE OF <columns>` trigger writes a queue row in the same transaction as the change. Supabase's automatic-embeddings reference architecture is exactly this end-to-end: column-scoped triggers enqueue into pgmq → pg_cron drains every 10s in batches (window-function batch numbering, capped at `max_requests × batch_size` per tick — built-in backpressure) → failed messages reappear after a visibility timeout (default 5 min) for retry → successes explicitly deleted. It is a working miniature of your heartbeat: change-driven, batched, retried, all in-database.
6. **Retry with backoff = one column.** `run_at = now() + backoff(attempts)`; a failed job is just re-scheduled into the future. Dead-letter = `state='discarded'` when `attempts >= max_attempts`, with `last_error` preserved. No new machinery.

---

## 4. Debounce / coalesce / backpressure for the change-driven heartbeat

The problem: an agent mid-edit-burst produces dozens of changes per minute; the re-index must neither thrash nor fall behind. Four complementary mechanisms:

1. **Job-key debounce (graphile-worker's `job_key` — the single best steal).** Enqueue with a stable key (`reindex:<scope>`) and a mode:
   - `replace` (default): a pending job with the same key is *overwritten* — payload updated, `run_at` pushed out. Enqueue with `run_at = now() + 30s` on every change → each new change re-arms the timer → **the job runs only after 30s of quiet**. Debounce in one upsert.
   - `preserve_run_at`: updates payload but *keeps* the original `run_at` → **throttle / fixed batching window** — runs at most once per window no matter the burst, at the originally scheduled time.
   - Array-payload merging: if payloads are arrays (e.g. changed file lists), they're merged — coalescing the burst's specifics into one batch.
   - Critical edge-case they solved: if the keyed job is *currently running* when a new event arrives, a **new** job is created (the running one's key is cleared) — so an event landing mid-run is never lost. This is the exact "agent edits while heartbeat is mid-flight" case.
2. **River-style uniqueness** for the coarser guard: partial unique index enforcing one job per (kind, scope) among *active* states (`available, scheduled, running, retryable`) — insert is a no-op if one's already pending. Simpler than job_key when you don't need payload merging (and the heartbeat often doesn't — see watermark below).
3. **Watermarks (high-water mark) instead of per-event payloads.** The incremental-processing standard: the heartbeat doesn't need the events at all — it reads its own `last_processed_at` cursor, processes everything `changed_at > watermark` (minus a small safety overlap), advances the watermark. Then coalescing is *free*: any number of change events collapse into "a run will happen," and the run discovers its own work from the ledger. Events become pure triggers; state lives in the cursor. This also makes the heartbeat self-healing — a missed trigger is caught by the next run.
4. **Backpressure by bounded drain + single-flight.** Cap items per tick (the Supabase pipeline's `max_requests × batch_size`); advisory lock or unique-index single-flight so runs never overlap; if the queue is still non-empty after a tick, the next tick continues — degradation is graceful lag, never pile-up. Dagster's eager-condition detail belongs here too: it *waits for in-progress upstream runs to complete* before triggering — "don't start while the input is still being written" as a first-class predicate.

The composed heartbeat shape: **trigger bumps watermark + upserts keyed quiet-window job → job single-flights under a lock → processes watermark→now in bounded batches → advances watermark → if changes arrived mid-run, the re-armed keyed job fires again after the next quiet window.** Thrash-proof, loss-proof, and each piece is one column or one upsert.

---

## 5. LLM-job specifics

The patterns are younger but converging:

1. **Prompt templates as versioned data (the registry pattern — Langfuse et al.).** Prompts live in a store, not in code: `(name, version, template, config{model, temperature, max_tokens}, labels{production, staging})`. Runtime fetches by name+label; a job row references `prompt_name@version`. Decouples prompt iteration from deploys, and every run can record *exactly which prompt version produced this output* — provenance your no-confidence/derivation-tag discipline needs anyway. Minimal form: a `prompts` table + a `prompt_ref` column on the job definition.
2. **Structured-output contract = the params schema in reverse.** A job definition carries `output_schema` (JSON Schema); the validation pipeline is layered: schema communicated in the prompt (or enforced by guided decoding — you already have this locally) → parse → jsonschema/Pydantic validate → on failure, **retry with the validation error fed back** to the model (the instructor pattern), not a blind re-roll. Consensus cap: **2 retries**; after 3 total attempts, the input is likely outside the schema's scope — record the failure and move on rather than burn tokens looping. (Your fail-loud law: the exhausted-retry row is a first-class recorded outcome, never a drop.)
3. **Budget as job-row fields, enforced pre- and post-.** Established observability practice (Langfuse): tokens + cost computed per generation, aggregated per trace/run/tag. The control side (budget routers, capped tools): allocation fields on the *definition* (`model/role, max_tokens_per_call, max_calls, max_total_tokens`), actuals accumulated on the *run* (`tokens_in, tokens_out, calls_made`); worker checks before each call and stops with state `budget_exhausted` — a recorded, queryable outcome, distinct from `failed`. Notably, pre-run cost *estimation* is still an open request even in Langfuse — enforce limits, don't predict.
4. **LLM-aware retry semantics.** Classify errors: transport/timeout → normal backoff retry; invalid-output → error-feedback repair (bounded, above); *semantic* refusal/garbage → don't retry at all, record for judgment. Retrying bad JSON with the identical prompt is documented as mostly wasted spend.
5. **Determinism boundary (Temporal's deepest lesson, applied to LLMs).** Temporal splits deterministic workflow logic from non-deterministic activities, and makes each activity idempotent and individually retryable. Translation: **each LLM call is its own recorded step** — inputs (prompt version, params, input hash), outputs, usage — so a multi-call job resumes from its last completed step instead of re-running (and re-paying for) everything. Also your law of "deterministic work to code, judgment to models," expressed as a storage schema.

---

# Recommendation memo

## Seven shapes to steal

**1. The three-table spine: `job_definitions` / `job_queue` / `job_runs`** *(Prefect deployments + pg-queue row shape)*
Definitions are the parametric templates (task_identifier → registered Python handler; `params_schema` + `output_schema` as JSON Schema; trigger config; allocations/model/budget; output address template). Queue rows are materialized pending work. Runs are append-only history with state transitions, result ref, error, and token/cost actuals. Fits because agents create/edit *rows* through MCP tools — configurable-everything falls out of definitions being data, and JSON-Schema validation at enqueue is your loud-fail gate. Minimal form: three tables, one handler registry dict.

**2. `FOR UPDATE SKIP LOCKED` claim + `run_at` as the universal time column** *(all pg-native queues)*
One claim query gives atomic, parallel-safe, crash-surviving dispatch; `run_at` alone expresses delay, retry backoff, debounce timers, and schedules. Fits because you get transactional integrity between ledger writes and job enqueues for free — no broker, no extra infra on the single machine. Minimal form: one UPDATE…RETURNING statement and an index on `(state, run_at, priority)`.

**3. `job_key` upsert with `replace` / `preserve_run_at` modes** *(graphile-worker — the highest value-per-line steal here)*
Debounce = keyed enqueue with `run_at = now()+quiet_window` and replace-mode; throttle = preserve_run_at; running-job edge = spawn a successor so no event is lost. This *is* the heartbeat's anti-thrash mechanism. Minimal form: unique index on `job_key WHERE state IN ('available','scheduled')` + one upsert function with the mode switch.

**4. Asset rows + staleness-derived scheduling** *(Dagster declarative automation)*
Declare ledger tables/sections as asset rows (`derived_from[]`, freshness policy, small automation-condition vocabulary: `eager | on_cron | on_missing`, composable), record materializations, and let a pg_cron tick derive what to enqueue by comparing input watermarks to last-materialized. Fits perfectly because your ledger tables literally are the assets and live in the same Postgres — you get the change-visibility Airflow's Datasets can't have. The heartbeat stops being a wired job and becomes a *derived consequence of declarations*. Minimal form: one `assets` table, one `materializations` table, one tick function with a watermark comparison.

**5. Trigger → outbox queue → bounded cron drain** *(Supabase automatic-embeddings architecture)*
Column-scoped `AFTER UPDATE OF ...` triggers enqueue in the same transaction as the change; a frequent tick drains in capped batches; visibility-timeout-style re-delivery on failure. Fits as the data-change trigger kind and as backpressure: bursts degrade to lag, never to thrash or loss. Minimal form: one generic trigger function taking (queue, metadata) + one drain function with a per-tick cap.

**6. Job-ID-as-idempotency-key with reuse policy** *(Temporal + River)*
Deterministic run keys (`heartbeat:ledger:2026-07-02T10`); insert of a duplicate active key is a refusal, not a dup; policy distinguishes "re-run after failure: yes" from "re-run after success: no" (`allow_duplicate_failed_only`). Fits because agents *will* double-fire MCP calls; dedupe must live in the substrate, not in agent discipline. Minimal form: River's partial unique index scoped to active states + a `reuse_policy` check on insert.

**7. LLM job = prompt-ref + output-schema + budget fields + error-classified bounded repair** *(instructor / Langfuse patterns)*
`prompt_ref@version` and `output_schema` on the definition; budget allocations on the definition, actuals on the run; validation failure → feed the error back, max 2 repair retries, then a *recorded* `schema_failed` outcome; `budget_exhausted` as a distinct terminal state; every model call a recorded step with usage. Fits your provenance discipline (which prompt version produced this output) and fail-loud law (exhausted retries and blown budgets are first-class recorded outcomes). Minimal form: four columns on definitions, four on runs, one repair loop in the worker.

## Three traps to avoid

**1. LISTEN/NOTIFY as the delivery mechanism.** Notifications are fire-and-forget (lost when no listener is connected — worker restarts guarantee gaps), NOTIFY-bearing commits serialize on a global lock, and it breaks behind poolers. Every serious pg-queue treats it as a latency hint over a polled table. If the row isn't the source of truth, you've built a silent-drop machine — the precise failure class that already cost you a day.

**2. Airflow-style sensors: polling as resident jobs, and change-awareness that only sees itself.** A waiting condition must never occupy a worker slot (Airflow's idle-sensor deadlock needed a whole async subsystem to fix) — make conditions cheap SQL predicates evaluated on the scheduler tick that *enqueue* work when true. And don't detect "data changed" by watching your own jobs complete (Airflow Datasets' blind spot): your ledger changes when *anything* writes it — DB triggers + watermarks see every writer; job-completion events don't.

**3. Workflow-engine envy: event-sourced replay and definition-in-code.** Temporal's durable-execution machinery (deterministic replay, event-history reconstruction) is enormous and unnecessary at single-machine scale — steal its *idempotency semantics* (shape 6) and step-level recording (shape 7), take resumability from watermarks + idempotent handlers. And don't drift back to jobs-defined-in-Python-files "because it's easier for one job": Airflow's DAG-as-code is its most regretted property (unversionable, untestable, editable only by developers) — the moment a definition isn't a row, agents can't configure it through MCP, and the system's core premise breaks. Rows for everything; code only in the handler registry.

**Sources:** [Dagster Declarative Automation docs](https://docs.dagster.io/guides/automate/declarative-automation) · [Dagster declarative scheduling for data assets](https://medium.com/@dagster-io/declarative-scheduling-for-data-assets-a-breakthrough-in-data-orchestration-85bd5fa6d707) · [Dagster asset-based scheduling](https://dagster.io/blog/asset-based-scheduling) · [Declarative Automation RFC #22811](https://github.com/dagster-io/dagster/discussions/22811) · [graphile-worker job_key docs](https://worker.graphile.org/docs/job-key) · [graphile-worker](https://github.com/graphile/worker) · [River unique jobs](https://riverqueue.com/docs/unique-jobs) · [pgqueuer](https://github.com/janbjorge/pgqueuer) · [Procrastinate](https://github.com/procrastinate-org/procrastinate) · [SKIP LOCKED queue pattern](https://www.dbpro.app/blog/postgresql-skip-locked) · [LISTEN/NOTIFY for job queues — pitfalls](https://nerdleveltech.com/postgres-listen-notify-job-queue) · [Advisory locks for leader election](https://kerkour.com/postgresql-leader-election-advisory-lock) · [Supabase pg_cron](https://supabase.com/docs/guides/database/extensions/pg_cron) · [Supabase automatic embeddings pipeline](https://supabase.com/docs/guides/ai/automatic-embeddings) · [pgmq background jobs on self-hosted Supabase](https://www.supascale.app/blog/background-jobs-and-queues-for-selfhosted-supabase-with-pgmq) · [Temporal Workflow ID / reuse policy](https://docs.temporal.io/workflow-execution/workflowid-runid) · [Temporal on idempotency](https://temporal.io/blog/idempotency-and-durable-execution) · [Temporal vs Airflow (ZenML)](https://www.zenml.io/blog/temporal-vs-airflow) · [Prefect flows/deployments](https://docs.prefect.io/v3/concepts/flows) · [Prefect deployment concepts](https://deepwiki.com/PrefectHQ/prefect/4.1-deployment-concepts) · [Windmill JSON schema & parsing](https://www.windmill.dev/docs/core_concepts/json_schema_and_parsing) · [Windmill jobs](https://www.windmill.dev/docs/core_concepts/jobs) · [Windmill triggers](https://www.windmill.dev/docs/getting_started/triggers) · [Airflow deferrable operators](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/deferring.html) · [Airflow datasets guide + limits](https://www.astronomer.io/docs/learn/airflow-datasets) · [Airflow review — good/bad](https://www.startdataengineering.com/post/apache-airflow-review-the-good-the-bad/) · [6 issues with Airflow (IBM)](https://ibm.com/blog/6-issues-with-airflow) · [Structured output schema validation for pipelines](https://collinwilkins.com/articles/structured-output) · [Langfuse token & cost tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking) · [LangChain budget routers & capped tools](https://medium.com/@Praxen/7-langchain-cost-controls-budget-routers-capped-tools-ffed8faedba8) · [webhook debounce/coalesce design](https://github.com/NousResearch/hermes-agent/issues/20201) · [coalesce pattern overview](https://dataopsschool.com/blog/coalesce/)
