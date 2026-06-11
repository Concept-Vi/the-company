---
type: contract-entry
resource: routines
summary: Cloud-resident Claude Code automation — a saved prompt + repos + connectors that runs autonomously on Anthropic-managed infrastructure, started by a schedule / bearer-token API call / GitHub event; plus the session-scoped local cron (/loop, CronCreate) that survives only inside an open CLI session. The company exposes NEITHER today — both are native Claude Code surfaces, contracted with the gap named.
schemes: []
status: planned
relates-to: ["[[workflows]]", "[[ci]]", "[[session]]", "[[events]]"]
---

# Resource: routines

## Identity
**A routine is identified by its cloud routine id (`trig_…` for its API trigger, the routine
record at claude.ai/code/routines); a session-scoped scheduled task is identified by its
8-character CronCreate id — NEITHER is a company address and there is no `routine://` scheme,
because the Company exposes no scheduling face at all.** Routines are a native Claude Code
capability that runs on Anthropic-managed cloud infrastructure
(https://code.claude.com/docs/en/routines.md), entirely outside this machine; session-scoped
tasks are a native CLI feature that lives inside one `claude` conversation
(https://code.claude.com/docs/en/scheduled-tasks.md). This entry contracts the real
trigger/auth model of both so a UI can present and reason about them, and names per op the
gap that the Company has built no proxy.

## Representation
**Two distinct things share the "automation" word and MUST NOT be conflated: a CLOUD routine
(durable, machine-off-safe, autonomous, fresh repo clone, no local files) and a SESSION-SCOPED
task (lives in one open CLI conversation, fires only while Claude is running and idle, dies on
a fresh conversation).** The deciding axes are runs-on (Anthropic cloud vs your machine),
durability (survives-machine-off vs session-lifetime), and local-file access (none, fresh
clone vs full). Sourced verbatim to the three-way comparison table at
https://code.claude.com/docs/en/scheduled-tasks.md#compare-scheduling-options.

```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/routines.record",
  "type": "object",
  "description": "A CLOUD routine as the native surface models it. NOT a company record — no company endpoint returns this shape today; the fields mirror the claude.ai/code/routines creation form (https://code.claude.com/docs/en/routines.md).",
  "properties": {
    "id":            { "type": "string", "description": "cloud routine id; its API trigger is trig_… (e.g. trig_01ABCDEFGHJKLMNOPQRSTUVW)" },
    "name":          { "type": "string" },
    "prompt":        { "type": "string", "description": "the self-contained directive Claude runs each fire; must state what success looks like (autonomous, no interactive follow-up)" },
    "model":         { "type": "string", "description": "model selected in the prompt input; used on every run" },
    "repositories":  { "type": "array", "items": { "type": "string" }, "description": "GitHub repos cloned at the start of each run from the default branch; Claude writes claude/-prefixed branches unless unrestricted-branch-pushes is enabled" },
    "environment":   { "type": "string", "description": "cloud environment id controlling network access, env vars, setup script (Default = Trusted network access — the default-allowed-domains allowlist only)" },
    "connectors":    { "type": "array", "items": { "type": "string" }, "description": "claude.ai MCP connectors included; ALL of a connector's tools (incl. writes) are usable without a per-run prompt — local `claude mcp add` servers do NOT appear, only claude.ai connectors or a committed .mcp.json" },
    "triggers":      { "type": "array", "items": { "enum": ["schedule", "api", "github"] }, "description": "one routine may combine all three" },
    "repeats":       { "type": "boolean", "description": "schedule trigger paused/active toggle" } } }
```
| field | type | volatile? | changed-by | address? → resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| id / triggers / prompt | — | no (config) | edit on claude.ai/code/routines or `/schedule update` | — | NO company representation — lives only in the user's claude.ai account. The company stores, returns, and reconciles NONE of it |
| run status | enum | yes | each fire creates a new cloud session | — | a "green" run status means the session started and exited without infra error — it does NOT mean the prompt succeeded (source: routines.md "View and interact with runs"). Read the run transcript to confirm |
| session-scoped task id | string (8-char) | yes | CronCreate / CronDelete | — | lives in ONE open CLI session's memory; `CronList` enumerates; 50 tasks max per session; cleared on a fresh conversation, restored on `--resume`/`--continue` if unexpired |

## State model
**State model: stateless** (from the Company's vantage — the Company holds no routine state).
The native surfaces have their own lifecycles documented inline: a cloud routine is
active/paused (the **Repeats** toggle) and a one-off auto-disables to **Ran** after firing; a
session-scoped recurring task auto-expires 7 days after creation (fires one final time then
deletes itself), and all session tasks clear on a new conversation. None of these transitions
are observable through any Company endpoint.

## Caller
**Cloud routines run as YOU: they belong to your individual claude.ai account, count against
your account's daily run allowance, and anything they do through your connected GitHub identity
or connectors appears as you (commits/PRs carry your GitHub user; Slack/Linear actions use your
linked accounts).** The API trigger authenticates with a per-routine bearer token (scoped to
firing that one routine). Session-scoped tasks run as the operator who owns the CLI session.
There is no Company caller-identity story because there is no Company face — when (if) the
Company ever proxies routine creation it would be a `bridge-http`/`cli-local` binding under the
explicit-self-label convention in [[ci#Caller]], named here so a UI builds toward the real seam.

## Operations

## op: routines.list
**`routines.list` is the PLANNED enumeration of a consumer's cloud routines (and, separately,
the session-scoped tasks of one open CLI session) — there is no Company endpoint that returns
either; the native surfaces are `/schedule list` in the CLI and the web list at
claude.ai/code/routines for cloud, `CronList` for session tasks.**
```contract:op
op: routines.list
resource: routines
kind: list
status: planned
direction: outbound
atlas: [CC-21.1]
tasks:
  - phrase: "what scheduled routines do I have"
  - phrase: "list my session's scheduled tasks"
  - alias: "show my automations"
  - alias: "list cron jobs"
bindings:
  - { kind: cli, command: "/schedule list   (NATIVE Claude Code CLI slash command — cloud routines; NOT a `company` command)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: the company CLI (ops/cli/) has no cron/schedule/routine noun (verified 2026-06-12). /schedule is a claude.ai-login-only CLI command, hidden under API-key/Bedrock/Vertex auth (routines.md troubleshooting)" }
  - { kind: cli, command: "CronList   (NATIVE session tool — session-scoped tasks of the CURRENT open conversation only)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: session-scoped, in-memory; not company-reachable. Surfaced conversationally ('what scheduled tasks do I have?') per scheduled-tasks.md" }
liveness: snapshot
live-twin: "none — static between edits"
emits: []
verification:
  cloud-list:   {state: unverified, note: "no company face; native /schedule list + claude.ai/code/routines"}
  session-list: {state: unverified, note: "no company face; native CronList, session-scoped"}
```
The two listings are different universes: cloud routines persist in your claude.ai account and
are listable from any session or the web; session-scoped tasks belong to the single open
conversation and vanish when it ends. A UI presenting "my automations" must keep them visually
distinct (the durability axis in [[routines#Representation]]). Mechanics owned here; the trigger
configuration is in [[routines#op: routines.create]].
Adjacent: [[routines#op: routines.create]], [[routines#op: routines.act]] (run-now / pause),
[[workflows]] (the in-session ways to keep work going).

## op: routines.create
**`routines.create` is the PLANNED save of a new cloud routine (prompt + repos + environment +
connectors + one-or-more triggers) or a new session-scoped task — the Company builds neither;
the native paths are the claude.ai/code/routines web form, `/schedule [description]` in the CLI
(scheduled trigger only), and `CronCreate` for an in-session cron task.**
```contract:op
op: routines.create
resource: routines
kind: create
status: planned
direction: outbound
atlas: [CC-21.2, CC-21.3]
tasks:
  - phrase: "schedule a daily PR review at 9am"
    params: {trigger: schedule, cadence: daily}
  - phrase: "run a routine every weeknight against my issue tracker"
    params: {trigger: schedule}
  - phrase: "give a routine an HTTP endpoint my alerting tool can call"
    params: {trigger: api}
  - phrase: "run a routine when a PR is opened"
    params: {trigger: github, event: "pull_request.opened"}
  - phrase: "poll the deployment every 5 minutes inside this session"
    params: {surface: session, tool: CronCreate}
  - alias: "automate work on a schedule"
  - alias: "set a recurring cloud task"
  - alias: "create a cron job"
bindings:
  - { kind: cli, command: "/schedule daily PR review at 9am   (NATIVE — creates a SCHEDULED cloud routine; API + GitHub triggers are web-only)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: no company face. Cloud creation also at claude.ai/code/routines or the Desktop app (New routine → Remote). Min cloud interval = 1 hour (sub-hour cron rejected)" }
  - { kind: cli, command: "CronCreate(expression, prompt, recurs)   (NATIVE session tool — 5-field cron, session-scoped, min 1 minute)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: in-memory, session-lifetime. Also reachable via `/loop <interval> <prompt>` (see [[workflows]]) or natural language ('remind me at 3pm to …')" }
liveness: none
emits: []
consequences:
  - when: "cloud routine fires (schedule/api/github)"
    expect: []
    evidence: "each fire creates a NEW cloud session in your claude.ai session list; the API trigger's response body carries `claude_code_session_id` + `claude_code_session_url` (see Examples). There is no company event — the run is observable ONLY on claude.ai, not on [[events]]"
  - when: "session-scoped task fires"
    expect: []
    evidence: "the scheduled prompt fires BETWEEN turns of the open CLI session (the scheduler checks every second, enqueues at low priority, waits if Claude is mid-turn) — observable only in that local terminal, never company-side"
correlate: []
verification:
  cloud-create:   {state: unverified, note: "no company face — native cloud routine"}
  session-create: {state: unverified, note: "no company face — native CronCreate"}
```
### Description (purpose-free)
Save a reusable automation. CLOUD: a routine packages a self-contained prompt, one or more
GitHub repositories (cloned fresh from the default branch on every run), a cloud environment
(network policy + env vars + cached setup script), and the claude.ai connectors it may use,
plus any combination of three trigger types. It runs autonomously as a full Claude Code cloud
session with NO permission-mode picker and NO approval prompts — what it can reach is bounded
only by the selected repos + their branch-push setting, the environment's network access, and
the included connectors (scope each tightly). SESSION-SCOPED: `CronCreate` registers a 5-field
cron prompt that re-fires inside the current conversation; it is the durable-only-within-this-
session counterpart, and `/loop` (see [[workflows]]) is its interval-shaped sibling. The
trigger model is the load-bearing detail and is contracted in [[routines#op: routines.act]]'s
trigger schema and the GitHub/API trigger notes below.
### Request (the cloud routine's trigger shapes — PLANNED contract, sourced to routines.md)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/routines.create.triggers",
  "type": "object",
  "properties": {
    "schedule": { "type": "object",
      "description": "recurring cadence (hourly/daily/weekdays/weekly preset) or a one-off timestamp; custom cron via `/schedule update`. Times entered local, converted to wall-clock. MIN INTERVAL 1 HOUR — more-frequent expressions are rejected. Runs may start a few minutes late (consistent per-routine stagger)",
      "properties": {
        "cadence": { "enum": ["hourly", "daily", "weekdays", "weekly", "custom", "one-off"] },
        "cron":    { "type": "string", "description": "set via `/schedule update`; ≥ 1h granularity" } } },
    "api": { "type": "object",
      "description": "a dedicated per-routine HTTP endpoint; the token is generated AFTER save (depends on the routine id) and shown ONCE (store it — cannot be retrieved later). CLI cannot create/revoke tokens; web-only",
      "properties": {
        "endpoint": { "type": "string", "description": "https://api.anthropic.com/v1/claude_code/routines/<trig_id>/fire" },
        "token":    { "type": "string", "description": "per-routine bearer (sk-ant-oat01-…), scoped to firing this routine only; rotate/revoke via Regenerate/Revoke" } } },
    "github": { "type": "object",
      "description": "repository-event trigger; REQUIRES the Claude GitHub App installed on the repo (`/web-setup` grants clone access but does NOT install the App or enable webhooks). Web-only config. Each matching event starts its OWN session (no reuse). Subject to per-routine/per-account hourly caps in research preview",
      "properties": {
        "event":   { "enum": ["pull_request", "release"], "description": "categories; pick a specific action (pull_request.opened) or all-in-category" },
        "filters": { "type": "object", "description": "PR filters: author/title/body/base-branch/head-branch/labels/is-draft/is-merged, each with operator equals|contains|starts-with|is-one-of|is-not-one-of|matches-regex (regex tests the WHOLE value — use .*hotfix.* for substring)" } } } } }
```
### Errors
```contract:error
code: routines.not-exposed | http: 501 | retryable: false
when: any attempt to create/manage a routine through a Company endpoint
teach: "The Company exposes no scheduling face. Create CLOUD routines at claude.ai/code/routines, the Desktop app (New routine → Remote), or `/schedule` in the CLI (scheduled trigger only; API/GitHub triggers are web-only). Create SESSION-SCOPED tasks with CronCreate / `/loop` (see [[workflows]]). To run unattended cron-driven Claude in CI instead, see [[ci]]."
```
```contract:error
code: routines.schedule-unavailable | http: 400 | retryable: false
when: "`/schedule` returns 'Unknown command' in the CLI"
teach: "`/schedule` requires a claude.ai subscription login and is hidden when ANTHROPIC_API_KEY/ANTHROPIC_AUTH_TOKEN/apiKeyHelper is set, when telemetry-disable env (DISABLE_TELEMETRY/DO_NOT_TRACK/CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC/DISABLE_GROWTHBOOK) is set, inside a Claude-Code-on-the-web session, or on CLI < v2.1.81. Manage at claude.ai/code/routines regardless (source: routines.md troubleshooting)."
```
```contract:error
code: routines.org-disabled | http: 403 | retryable: false
when: "'Routines are disabled by your organization's policy'"
teach: "A Team/Enterprise admin turned off the Routines toggle at claude.ai/admin-settings/claude-code. This is a server-side org setting and cannot be overridden locally — contact your admin."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud (V11); no company face exists
binding: cli
request: |
  /schedule daily at 9am, summarize yesterday's merged PRs
response: |
  (NATIVE CLI) Claude walks through the same fields the web form collects (name, prompt,
  repos, environment), confirms the absolute schedule, and saves the routine to your claude.ai
  account. There is NO company-side record and NO company endpoint involved.
```
```contract:example
captured: synthetic            # the cloud API trigger fire — the real auth/response model (routines.md)
binding: http
request: |
  POST https://api.anthropic.com/v1/claude_code/routines/trig_01ABCDEFGHJKLMNOPQRSTUVW/fire
  Authorization: Bearer sk-ant-oat01-xxxxx
  anthropic-beta: experimental-cc-routine-2026-04-01
  anthropic-version: 2023-06-01
  Content-Type: application/json
  {"text": "Sentry alert SEN-4521 fired in prod. Stack trace attached."}
response: |
  HTTP/1.1 200 OK
  {"type": "routine_fire",
   "claude_code_session_id": "session_01HJKLMNOPQRSTUVWXYZ",
   "claude_code_session_url": "https://claude.ai/code/session_01HJKLMNOPQRSTUVWXYZ"}
  # NOTE: this is the Anthropic cloud API, NOT a company route. The optional `text` body field
  # is freeform and unparsed — JSON sent here arrives as a literal string. The /fire endpoint is
  # claude.ai-users-only, behind the experimental-cc-routine-2026-04-01 beta header. Full API
  # reference: https://platform.claude.com/docs/en/api/claude-code/routines-fire
```
Adjacent: [[routines#op: routines.act]] (run-now / pause / one-off), [[ci]] (the CI-provider
way to run cron-driven Claude — GitHub Actions `schedule:` / GitLab pipelines),
[[workflows]] (in-session `/loop`, `/goal`, channels), [[session]] (the cloud session each
fire produces — observable only on claude.ai, not [[events]]).

## op: routines.act
**`routines.act` is the PLANNED control surface for an existing routine — run-now, pause/resume
the schedule, fire a one-off, generate/rotate/revoke an API token, cancel a session-scoped task
— each a native claude.ai/code/routines control or a session tool (`CronDelete`), none of them
a Company act.**
```contract:op
op: routines.act
resource: routines
kind: act
status: planned
direction: outbound
atlas: [CC-21.4]
tasks:
  - phrase: "run a routine now without waiting for the schedule"
    params: {act: run-now}
  - phrase: "pause a routine"
    params: {act: pause}
  - phrase: "schedule a one-off cleanup PR in two weeks"
    params: {act: one-off}
  - phrase: "cancel the deploy-check scheduled task"
    params: {act: cancel-session-task}
  - alias: "stop a routine"
  - alias: "rotate a routine's api token"
  - alias: "delete a cron job"
bindings:
  - { kind: cli, command: "/schedule run | /schedule update   (NATIVE — run-now / change a cloud routine)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: no company face. Run-now / pause (the Repeats toggle) / token Regenerate-Revoke are on the routine detail page at claude.ai/code/routines" }
  - { kind: cli, command: "CronDelete(id)   (NATIVE session tool — cancel a session-scoped task by its 8-char id)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: session-scoped. `Esc` clears a pending `/loop` wakeup; CronDelete cancels a task scheduled by asking Claude directly. CLAUDE_CODE_DISABLE_CRON=1 disables the whole scheduler" }
liveness: none
emits: []
consequences:
  - when: "run-now / one-off fire (cloud)"
    expect: []
    evidence: "a new session in your claude.ai session list; a one-off auto-disables to **Ran** after firing. No company event"
  - when: "cancel session task"
    expect: []
    evidence: "the task disappears from `CronList`; no further fires. No company event"
correlate: []
verification:
  cloud-control:  {state: unverified, note: "no company face — native claude.ai/code/routines controls"}
  session-cancel: {state: unverified, note: "no company face — native CronDelete / Esc"}
```
### Description (purpose-free)
The lifecycle controls a consumer reaches for once a routine exists. Cloud: **Run now** starts
a run immediately; the **Repeats** toggle pauses/resumes a schedule (paused routines keep config
but don't fire); a one-off fires once then auto-disables; the API-trigger modal generates,
regenerates, or revokes the per-routine token; the delete icon removes the routine (past
sessions remain in the session list). Session-scoped: `CronDelete` cancels by id; `Esc` clears
a pending `/loop` wakeup. None of these is a Company operation — each binding names the native
control and the absent Company proxy.
### Errors
```contract:error
code: routines.control-not-exposed | http: 501 | retryable: false
when: any control call against a routine through a Company endpoint
teach: "The Company proxies no routine controls. Use claude.ai/code/routines (Run now / Repeats toggle / token Regenerate-Revoke / delete), `/schedule run|update` in the CLI, or CronDelete for a session-scoped task. See [[routines#op: routines.create]] for creation."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud (V11)
binding: cli
request: |
  cancel the deploy check job
response: |
  (NATIVE) Claude calls CronDelete with the task's 8-character id; the task stops firing.
  No company endpoint participates; the task only ever existed in this open CLI session.
```
Adjacent: [[routines#op: routines.create]] (save), [[routines#op: routines.list]] (enumerate),
[[ci]] (cron-in-CI), [[workflows]] (in-session keep-going).

## Errors
**Resource-level vocabulary: `routines.not-exposed` (the honest 501 create/manage returns until a
Company scheduling face is built), `routines.control-not-exposed` (the same 501 on control calls —
run/repeat/revoke/delete), `routines.schedule-unavailable` (the native `/schedule`
hidden-command condition), `routines.org-disabled` (the admin Routines toggle).** Each teaches
the real native recovery path; none claims a Company capability that the code does not have
(verified 2026-06-12: no cron/schedule/routine noun in `ops/cli/`, no routine surface in
`runtime/` or `mcp_face/`).

## Links
**No address-typed fields resolve to a Company entry: a cloud routine's API endpoint is an
`api.anthropic.com` URL (external), its fires produce claude.ai cloud sessions (NOT the local
`session://` fabric of [[session]], and NOT observable on [[events]]), and a session-scoped
task id is a local CLI handle.** The only in-corpus relations are conceptual: [[workflows]]
(the in-session keep-going mechanisms that are the local alternative to a scheduled routine),
[[ci]] (GitHub Actions `schedule:` as the CI-provider durable-cron alternative), and the cloud
GitHub trigger overlaps [[ci]]'s `@claude` mention model — both are contracted, neither is a
Company face.
