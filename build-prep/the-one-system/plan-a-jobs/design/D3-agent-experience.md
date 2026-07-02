# Plan A design · take 3 — the AGENT-EXPERIENCE lens (2026-07-02)

*One of three independent design perspectives (D1 substrate-minimalist · D2 asset-first · D3 this).
Designed from the consumer inward: agents via MCP, Tim via the surface, the system via activation.
Report verbatim below; judged + synthesized after all three land.*

# PLAN A — Parametric Job System · Design Take: AGENT-EXPERIENCE (from the consumer inward)

*Grounded in: JOBS-AND-COORDINATES-PLAN.md §Plan A, R1-existing-machinery.md, R2-external-patterns.md, NORTH-STAR.md. Register: prescriptive proposal, unbuilt. Everything below is design, tagged where it leans on an assumption.*

**The lens's one sentence:** an agent should be able to say "do Z over THESE, when THIS, within THAT budget" in one tool call, get taught instead of rejected when it says it wrong, and find the result at an address it was told up front. Tim should be able to see the same rows as a surface and recognize/direct without reading any of this.

---

## 1. THE TOOL SURFACE — one noun, one tool: `jobs(op=…)`

The repo's face grammar is one-tool-per-noun with `op` (flows/routines/cc_board all work this way — R1 §7, §"Three faces"). Jobs follow it. Triggers are NOT a second tool: per Plan A, the trigger is a **field on the job row**, so there is nothing to address separately — a "standing trigger" is just a job whose trigger isn't `manual`.

### Ops (the complete set)

| op | what it does | consequential? |
|---|---|---|
| `describe` | self-description: `about='vocabulary'` → the job-row schema + step/trigger/selector kinds with one worked example each; `about='targets'` → the runnable-ref catalog (every flow/role/cascade/graph/prompt with its params schema); `about='<job-id>'` → one row, fully resolved | no |
| `define` | author/update a job row; `check=true` validates without saving | writes a row |
| `fire` | enqueue a run — of a registered job (`id=` + `params=`) or an **inline body** (`job=` — the run_draft precedent: ephemeral, recorded, never registered) | yes |
| `runs` | run history: for a job, a run key, or filtered (state/since); one run → full step trail | no |
| `watch` | snapshot of a run: state, current step, budget actuals so far, `poll_after_s` hint (MCP is request/response — watch is a polite poll, push goes through `notify`, §4) | no |
| `probe` | evaluate a job's trigger condition NOW against current state; returns true/false + the bindings that made it so ("would this fire, and on what?") | no |
| `pause` / `resume` | disarm/re-arm a standing trigger (row stays) | resume of agent-work jobs re-surfaces |
| `cancel` | cancel a queued/running run | yes |
| `retire` | soft-close a job row (runs history preserved) | no |

### Authoring conversationally-safely: validation that TEACHES

`define` and `fire` run the row through **one validation door** (the `build_action` precedent — R1 §3: cascades already prove agents can author rows through a validated face). A refusal is never a bare error; it is a teaching object in the fail-loud-breadcrumb style (north-star directive 5 — *expected / previously / fix*):

```json
{ "refused": true,
  "at": "steps[1].do",
  "got": "role:describe-code",
  "expected": "a registered ref — role:<id> from roles/ (38 rows)",
  "closest": ["role:describe_code", "role:describe_symbol"],
  "why": "refs are resolved at define-time so a job never fires into a dangling name",
  "fix": { "steps[1].do": "role:describe_code" },
  "resubmit": "jobs(op='define', check=true, job=<your row with fix applied>)" }
```

Rules of the teaching shape: (a) always name the exact field path; (b) always include a closest-match when the space is enumerable (registry ids, model names, trigger kinds); (c) always include a `fix` fragment the agent can merge and resubmit; (d) `check=true` exists so an agent can iterate to a clean row before anything is saved — define-then-fire never discovers a validation error at fire time.

### Discovery as self-description

`describe(about='targets')` is the "what is runnable" enum made live: it JOINS the existing registries (flows' declared+defaulted params — the only true params-as-data today, R1 §1; roles' 29 fields projected down to what a caller sets; saved cascades; prompt registry `name@version`) into one catalog, each entry carrying its params schema. An agent never guesses a param name — the schema IS the documentation, Windmill-style (R2 §1). `describe(about='vocabulary')` returns the job-row JSON Schema itself plus a worked example per named use (one-off / targeted / conditional / generative / traversal), so the tool teaches its own idioms.

---

## 2. THE JOB VOCABULARY — what one row must say

```
job = {
  id, label, description,                      // identity (id optional on inline fire)
  trigger: { kind: manual | schedule | change | condition | event, ...kind-config },
  params:  { name: {desc, default?} },         // the flow pattern, verbatim (R1 §1)
  steps:   [ step, ... ],                      // the chain — extended cascade vocabulary
  budget:  { max_total_tokens?, max_calls?, max_wall_s?, per_day? },
  output:  { address_template?, notify?: [...] },
  floor:   derived, not authored               // §6
}
```

**Step** — the body IS a cascade decl (R1 reuse-opportunity #1: run_cascade already has threading, fan-out, gates, jury/panel, persistence), with the step vocabulary extended by exactly three kinds and one field:

```
step = { do: <ref>,                            // role:x | flow:x | cascade:x | graph:x | prompt://x@v | agent:<routine-ish spec> | job:x
         over?: <selector | '$prev' | [addresses]>,   // per-unit fan — see below
         params?: {...},                        // bound to job params via $param.name
         model?, max_tokens?, output_schema?,   // per-step, as cascades have today
         on_fail?: flag | drop | halt }         // check-step vocabulary generalized
```

New step kinds: `flow` (staging — absorbing R1's closing flag: "flows stage, cascades declare"), `agent` (the routine_runner claude -p circuit with `prompt_override` finally exposed as the params seam — R1 reuse #4), `job` (composition, cycle-checked at define).

**The five named uses, each in one row:**

- **One-off** — `trigger: {kind:'manual'}` + `fire`, or skip `define` entirely: `fire(job={steps:[…]})` inline. No ceremony for ephemeral work (worked example ii).
- **Targeted** — the job's `over` names a scope. This is the key vocabulary decision: **`over` takes a SELECTOR**, and a selector is any way of naming a set of units in the coordinate space: `{list:[…]}` · `{path:'canvas/**/*.tsx'}` · `{changed_since:'watermark'}` · `{near:{address, emb, k}}` · `{traverse:{…}}`.
- **Conditional** — `trigger: {kind:'condition', when:<data-AST>, cursor:true}`. The `when` AST reuses `rules.RULE_OPS` verbatim (R1 reuse #2 — the mode_detection_rules registry is already "condition rows walked deterministically"); evaluated as a **cheap predicate on the scheduler tick, never a resident poller** (R2 trap #2, the Airflow-sensor lesson), with Dagster-style cursor semantics so each evaluation only sees events since the last it consumed.
- **Generative** — a step with `do:'prompt://x@v'` or `do:'role:x'` + `output_schema` + step budget. Retry semantics are the R2 §5 ladder baked into the runner, not authored: transport → backoff; invalid-output → error-fed-back repair, max 2; semantic garbage → recorded `schema_failed`, never a blind re-roll. The agent writes none of that — it only sees the classified terminal state.
- **Traversal** — **a selector kind, not a job kind and not a new step kind.** `over: {traverse: {anchor:'code://…', edges:['calls','imports'], direction:'out', depth:2, filter?:<AST>}}` resolves to a unit list; the step's `do` runs per unit (the existing items/fan_field machinery consumes it unchanged). Reasoning from the consumer side: an agent thinks "do Z over the things reachable from X" — traversal is a way of saying *these*, and *these* also gets said by path, by change-set, by vector neighborhood. One `over` grammar covers targeted AND traversal AND the heartbeat's changed-set, and it is exactly the seam where Plan B's coordinate query plugs in later (the selector engine and the coordinate query are the same function, two consumers). *Tagged inference: this presumes fan-source and step vocabulary compose cleanly in run_cascade — R1 shows fan_field exists (cognition.py:~2950) but I have not traced whether a selector-produced unit list can feed it without runner changes.*

---

## 3. COMPOSITION UX — refs, addresses, keys

**Refs, never copies.** Every `do` is a registry ref resolved at define-time (dangling ref = teach-refusal with closest-match). Prompts are `prompt://name@version` (R2 §5.1) so a run records exactly which prompt version produced its output — the provenance the derivation-tag discipline needs. Editing a role/flow/prompt changes every job that refs it, visibly: `describe(about='<job>')` returns the row *resolved*, showing current ref targets and versions.

**Outputs are addressed before they exist.** Every fire returns, immediately, where things will land:

```
run://job/<job-id>/<run-key>/<i>-<step>     // per step, the cascade convention extended
```

plus the job's `output.address_template` for the final artifact if declared. The next agent/job never searches for a result — the address is in the fire's return and in the run row. `$prev` / `$step[i]` in a later step's `over`/`params` are these same addresses, resolved by the runner.

**Idempotency the agent doesn't think about.** `run_key` is derived: `<job-id>:<trigger-firing-identity>:<params-hash>` (schedule fires key by window; change fires by watermark span; manual by params-hash + a short nonce unless the agent supplies `key=`). Duplicate fire of an active key returns the EXISTING run with `deduped:true` — a success shape, not an error (agents double-fire MCP calls; dedupe lives in the substrate, R2 shape #6, reuse policy `allow_duplicate_failed_only` as default: failures re-runnable, successes not silently repeated).

---

## 4. OBSERVABILITY — what a run looks like from outside

**One run row, one state machine**, closing R1 gap #5 (five record shapes today):

```
queued → running → succeeded
                 ↘ failed | schema_failed | budget_exhausted | cancelled
   (fire of duplicate active key → deduped, pointing at the live run)
```

`budget_exhausted` and `schema_failed` are distinct recorded terminals, not flavors of `failed` (R2 §5.2–5.3) — an agent branches on them differently (raise budget vs. fix schema vs. investigate).

**The run row an agent/Tim reads** (`runs` or `watch`):

```json
{ "run": "run://job/redesc-changed/2026-07-02T09:41:aa8f",
  "job": "redesc-changed", "state": "running",
  "trigger": {"kind":"manual","by":"agent:session-7f2"},
  "steps": [
    {"i":0,"do":"role:describe_code","state":"succeeded","units":12,"out":"run://job/.../0-describe_code",
     "actuals":{"tokens_in":18220,"tokens_out":6410,"calls":12}},
    {"i":1,"do":"flow:re_embed","state":"running","units":9}
  ],
  "budget": {"allocated":{"max_total_tokens":120000},"actuals":{"tokens":24630,"calls":12}},
  "poll_after_s": 20 }
```

Every model call is its own recorded step-unit (op.run reused — R1 reuse #5), so a failed run resumes from its last completed step, never re-pays the whole chain (R2 §5.5).

**A failed run carries the breadcrumb, not a stack trace:**

```json
{ "state": "failed", "at": "steps[1]",
  "error": { "expected": "space 'desc' rows in ledger.embedding for 3 addresses",
             "previously": "FsStore .data/store/vectors/",
             "fix": "jobs(op='fire', id='redesc-changed', params={addresses:[<the 3>]}) — retries only the failed units" } }
```

**Notify.** The job row's `output.notify` reuses the rules destination vocabulary minus the forbidden verbs (R1 §5): `surface` (Tim's ask queue), `board`, `channel` (the fabric — a watching agent gets pushed instead of polling). Default: terminal failure states of standing jobs auto-surface; successes are silent rows.

---

## 5. TIM'S FACE — the same rows, rendered

One function, two faces (north-star directive 2): `jobs_list / job_runs / probe / freshness` are functions; the MCP ops and `/api/jobs` are both thin projections of them. The UI is **resolved from schema/content**, not hand-built: the job row's params schema renders the param form (the Windmill/Prefect move — R2 §1); the run state machine renders the timeline; nothing on the surface exists that isn't in the rows.

Three regions:

1. **JOBS** — the definitions: name · trigger kind · armed/paused/proposed · last run state · budget-per-day gauge. Standing triggers awaiting approval float to the top as asks.
2. **RUNS** — the living timeline: state-colored run rows, drill into the step trail (same JSON as §4, rendered), the breadcrumbed error verbatim on failures.
3. **FRESHNESS** — the reason jobs belong on Tim's surface at all: the world's staleness as PASS/WARN/FAIL per region (Dagster freshness, R2 §2), derived from watermarks vs. last-materialized. Tim doesn't read cron expressions; he sees "descriptions: 41 files behind, heartbeat armed, next quiet-window fire ~2m." **Freshness is the recognizable projection of the whole job system** — when it's green, the world is current.

What Tim can DO: fire (with the schema-rendered param form) · pause/resume · **approve/deny proposed standing triggers** (§6) · cancel a run · raise/lower a job's budget. All of these are the same ops agents have — the floor differs, not the function.

---

## 6. SAFETY UX — the floor from the consumer's side

**What a job can never contain** (structural, define-time): operator verbs (`resolve/approve/dispatch` — the FORBIDDEN_DESTINATION_VERBS assertion transfers), raw process launches, writes outside `run://` + declared ledger-derived tables + declared output addresses. The one consequential step kind is `agent` (claude -p via the supervisor), bounded by `permission_mode` (default plan) + `max_turns`, exactly as routines are today.

**Standing-trigger approval — the arming rule:**
- **Manual fire of pure-compute steps** → runs immediately. No approval; it's what run_cascade already permits.
- **Any NEW standing trigger** (schedule/change/condition/event) authored by an agent → row saved in state `proposed`, surfaced as an ask; it arms only on Tim's resolve. Arming autonomy stays with the operator — that IS the floor's meaning.
- **Pre-approved classes:** once Tim approves a job, he can approve it *as a class* (this job shape ± params, under this budget); subsequent instances matching the class auto-arm and appear on the surface already-armed with a pause control. This keeps Tim out of the loop for the tenth re-embed variant without making "agent arms autonomous work" ever true. The system's own firings (activation rules) act under classes Tim has approved.
- **`agent`-step standing jobs are never class-approved** — each arms individually.

**How a refusal reads** (same teaching shape as validation):

```json
{ "refused": false, "state": "proposed",
  "surfaced": "ask://surface_review/2026-07-02/jobs/world-heartbeat",
  "why": "standing triggers arm autonomous work; arming resolves through the operator",
  "you_can": ["fire once now — op='fire' needs no approval",
              "watch for state='armed' via op='describe'",
              "match a pre-approved class: [re-embed-changed, redescribe-scoped]"] }
```

**Budget guards:** generative steps without a budget get the default injected AND stated in the define return ("budget defaulted: 50k tokens/run, 200k/day — override in job.budget"); the worker checks before each call; exhaustion is a recorded terminal, surfaced. No unbudgeted model spend can be authored, and no budget stop is silent.

---

## 7. THREE WORKED EXAMPLES — verbatim

### (i) The heartbeat as a standing trigger an agent registers

```
jobs(op='define', job={
  id: 'world-heartbeat',
  label: 'Ledger heartbeat — keep the world current',
  description: 'change → incremental extract → re-embed changed → joins re-derive → descriptions re-carry',
  trigger: { kind: 'change',
             watch: { selector: {path:'**/*', projects:['company']},
                      debounce_s: 120,          // job_key replace-mode: fires after 120s of quiet
                      watermark: true },         // run discovers its own work; events are only wake-ups
  params: { batch_cap: {desc:'max units per fire', default: 200} },
  steps: [
    { do:'flow:incremental_extract', over:{changed_since:'watermark'}, params:{cap:'$param.batch_cap'} },
    { do:'flow:re_embed',            over:'$prev' },
    { do:'flow:joins_rederive',      over:'$prev' },
    { do:'role:describe_code',       over:'$prev', model:'kimi-k2',
      output_schema:'schema://code-description@2', max_tokens:1200 } ],
  budget: { max_total_tokens: 300000, per_day: {max_total_tokens: 2000000} },
  output: { notify:[{on:'failed|budget_exhausted', to:'surface'}] }
})
→ { "state":"proposed", "surfaced":"ask://surface_review/.../world-heartbeat",
    "why":"standing triggers arm through the operator", "you_can":[...] }

# Tim approves on the surface. Later:
jobs(op='describe', about='world-heartbeat')
→ { "state":"armed", "trigger":{"kind":"change","last_watermark":"2026-07-02T09:12Z"},
    "next":"fires 120s after next quiet window", "freshness":"PASS" }
```

### (ii) One-off: re-describe 12 changed files with kimi, then re-embed desc

```
jobs(op='fire', job={                              // inline body — no registration, still recorded
  steps: [
    { do:'role:describe_code',
      over:{list:['code://company/canvas/app/src/A.tsx::render', ...12 addresses]},
      model:'kimi-k2', output_schema:'schema://code-description@2' },
    { do:'flow:re_embed', over:'$prev', params:{emb:'desc'} } ],
  budget:{ max_total_tokens: 60000 }
})
→ { "run":"run://job/_inline/2026-07-02T10:03:b31c", "state":"queued",
    "outputs_will_land":["run://job/_inline/.../0-describe_code","run://job/_inline/.../1-re_embed"],
    "poll_after_s": 15 }

jobs(op='watch', run='run://job/_inline/2026-07-02T10:03:b31c')
→ { "state":"succeeded",
    "steps":[ {"i":0,"units":12,"out":"run://.../0-describe_code",
               "actuals":{"tokens_in":18220,"tokens_out":6410,"calls":12}},
              {"i":1,"units":12,"out":"run://.../1-re_embed"} ],
    "budget":{"actuals":{"tokens":24630}} }
```

### (iii) Conditional: when any test file gains a powered-by edge, refresh the ui-join rung

```
jobs(op='define', job={
  id: 'ui-join-on-powered-by',
  trigger: { kind: 'condition', cursor: true,      // cheap predicate on the tick, never a resident poller
             when: { new_edge: { kind:'powered-by',
                                 src:{path:'tests/**'} } } },
  steps: [ { do:'flow:refresh_rung', params:{rung:'ui-join'} } ],
  output: { notify:[{on:'succeeded', to:'board'}] }
})
→ { "state":"proposed", "surfaced":"ask://...", ... }      // approved → armed

jobs(op='probe', id='ui-join-on-powered-by')                // "would it fire right now?"
→ { "would_fire": false, "evaluated_at":"2026-07-02T10:07Z",
    "cursor":"edge-seq:88412", "matched": [] }
```

---

## THE 3 BIGGEST RISKS OF THIS DESIGN (honest)

1. **The selector grammar front-runs Plan B.** I unified targeted/traversal/change-set under `over: <selector>` and claimed it's "the seam where the coordinate query plugs in." If Plan A ships first, the job system needs a working selector engine *before* Plan B exists — and an interim implementation becomes a second dialect that Plan B must later absorb or fight. Mitigation is discipline, not structure: ship only the selector kinds with existing machinery behind them (`list`, `path`, `changed_since`; `traverse` only if the ledger edge-walk is genuinely one query) and refuse the rest with a teach-refusal naming Plan B.
2. **Approval routing puts Tim in the freshness loop.** Every new standing trigger proposing-then-waiting means the system's own currency (the heartbeat, its future siblings) stalls on Tim's attention; the pre-approved-class escape hatch fixes the friction but *classes are themselves a policy surface* — a too-broad class ("any re-embed job") is a floor bypass an agent could drift into deliberately or not. The class-match predicate must be as strictly data-AST'd and auditable as the triggers it exempts, and I have not designed that predicate's limits.
3. **Inline fire creates a second citizenship.** `fire(job={…})` is the best one-off UX and mirrors run_draft — but it means two ways to run things. Inline jobs dodge the trigger-approval question by construction (they can't be standing), yet they still spend budget, still spawn `agent` steps if allowed, and their `_inline` run rows are harder to attribute and audit at volume. If agents habitually inline everything, the registry stops being the map of what the system does — the exact everything-as-data premise Plan A exists to establish. Possible tightening (undecided): `agent` steps refused in inline bodies, and a nudge in the fire return when the same inline shape fires repeatedly ("this ran 4× this week — register it: <prefilled define call>").

*One structural assumption to verify before build (tagged, unverified): the whole chain design leans on run_cascade accepting three new step kinds and selector-fed fan-out without deep runner surgery — R1 evidences the extension points (fan_field, injected resolvers, step-index-keyed outputs) but no one has traced the actual diff.*
