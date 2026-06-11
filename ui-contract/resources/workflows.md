---
type: contract-entry
resource: workflows
summary: Dynamic multi-step / keep-going coordination — the native Claude Code ways to keep ONE session working across turns (/goal until a condition holds, /loop on an interval, a Stop hook) and to push external events INTO a running session (channels), versus the Company's ONE real coordination primitive that IS built — the supervisor consult-fan (session.post verb=consult). Native surfaces are planned; the fan routes to F1's building session.post.
schemes: []
status: planned
relates-to: ["[[routines]]", "[[session]]", "[[session-message]]", "[[events]]"]
---

# Resource: workflows

## Identity
**A "workflow" here is not a saved addressable object — it is a coordination MODE over sessions:
keep-one-session-going (`/goal`, `/loop`, Stop hook), push-events-into-a-session (channels), or
fan-one-question-to-N-parallel-sessions (the Company consult-fan).** There is no `workflow://`
scheme and no workflow-definition file format in Claude Code today (the older "workflows" notion
in the feature atlas is `[needs-depth-round]`/inferred and is NOT a shipped doc-backed surface —
honest: the real, documented coordination primitives are `/goal`
(https://code.claude.com/docs/en/goal.md), `/loop`
(https://code.claude.com/docs/en/scheduled-tasks.md), channels
(https://code.claude.com/docs/en/channels.md), and agent teams / consult). This entry contracts
those, and points the LIVE multi-session capability at the one the Company actually built:
[[session#op: session.post]] `verb=consult`.

## Representation
**The coordination modes, by what starts the next unit of work and what stops it — the load-
bearing distinction a UI must preserve.** Sourced to the comparison tables in goal.md
("Compare ways to keep a session running") and channels.md ("How channels compare").

```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/workflows.modes",
  "type": "object",
  "description": "NOT a company record — a catalog of native coordination modes + the one company primitive. No company endpoint returns this; it documents the choice space.",
  "properties": {
    "goal":     { "description": "/goal <condition>: after each turn a small fast model (default Haiku) judges whether the condition holds against what Claude SURFACED in the conversation (it runs no tools, reads no files); a 'no' starts another turn with the reason as guidance, a 'yes' clears the goal. One goal per session; condition ≤4000 chars; a wrapper over a session-scoped prompt-based Stop hook" },
    "loop":     { "description": "/loop [interval] [prompt]: re-run a prompt on a fixed cron interval, at a Claude-chosen interval, or the built-in maintenance prompt; session-scoped, 7-day expiry — the cron mechanics live in [[routines]]" },
    "stop_hook":{ "description": "a Stop hook in settings: fires after every turn in its scope, runs a script (deterministic) or prompt (model-evaluated) to decide whether to continue — the durable, cross-session form of /goal" },
    "channel":  { "description": "an MCP server (a plugin) that PUSHES external events into a running session so Claude reacts while you are away; can be two-way (Claude replies through the same channel); events arrive ONLY while the session is open. Research preview, v2.1.80+; Anthropic auth only (not Bedrock/Vertex/Foundry)" },
    "consult_fan": { "description": "THE COMPANY PRIMITIVE: session.post verb=consult forks N copies of a session and asks them one question in parallel, replies aggregating under one thread. This is the only one of these modes the Company itself exposes — see [[session#op: session.post]] (building)" } } }
```
| mode | next turn starts when | stops when | reality (2026-06-12) |
|---|---|---|---|
| `/goal` | the previous turn finishes | the evaluator model confirms the condition | NATIVE CLI (v2.1.139+), interactive + headless (`claude -p "/goal …"`) + Remote Control; NO company face |
| `/loop` | a time interval elapses | you `Esc`, 7 days elapse, or (self-paced) Claude stops | NATIVE; session-scoped — cron details in [[routines]]; NO company face |
| Stop hook | the previous turn finishes | your script/prompt decides | NATIVE settings hook; NO company face |
| channel | an external event is pushed in | session closes / channel removed | NATIVE research preview; plugin + `--channels`; NO company face |
| consult-fan | the fan is fired (one shot) | all N forks reply | COMPANY-BUILT — [[session#op: session.post]] verb=consult (`building`, fork physics probe-verified T4) |

## State model
**State model: stateless** (the Company holds no workflow state). The native modes have
session-local lifecycles: a `/goal` is active until met or `/goal clear` (a `◎ /goal active`
indicator shows runtime; it restores on `--resume` with timer/turn/token baselines reset); a
`/loop` runs until `Esc`/expiry; a channel delivers only while the session is open. The one
stateful primitive the Company DOES drive is the consult-fan's forks, whose lifecycle is the
session FSM in [[session#State model]] — observed via [[events]], not here.

## Caller
**`/goal`, `/loop`, and Stop hooks are operator acts inside one CLI session (and require the
workspace trust dialog — the evaluator is part of the hooks system; `/goal` is unavailable when
`disableAllHooks` is set at any level or `allowManagedHooksOnly` is set in managed settings, and
says why rather than silently no-op'ing).** A channel's senders are gated by a per-plugin
allowlist (pairing for Telegram/Discord; self-chat bypass for iMessage), and a channel only runs
when named in `--channels` AND enabled by the org (`channelsEnabled`) — being in `.mcp.json` is
not enough. The consult-fan's caller is the F1 MCP/HTTP/CLI caller of [[session#op:
session.post]] (explicit `from`/`from_session` — no ambient identity, per [[session#Caller]]).

## Operations

## op: workflows.act
**`workflows.act` is the PLANNED single steer over the native keep-going modes — set/check/clear
a goal, start/stop a loop, install a Stop hook — none wired through the Company; the live
multi-session capability is NOT here but at [[session#op: session.post]] verb=consult.**
```contract:op
op: workflows.act
resource: workflows
kind: act
status: planned
direction: outbound
atlas: [CC-22.1, CC-22.2]
tasks:
  - phrase: "keep Claude working until all tests pass"
    params: {act: set-goal}
  - phrase: "keep working toward a verifiable end state without me prompting each step"
    params: {act: set-goal}
  - phrase: "re-run a prompt every five minutes"
    params: {act: loop, interval: 5m}
  - phrase: "check the goal status"
    params: {act: goal-status}
  - phrase: "stop the goal"
    params: {act: clear-goal}
  - alias: "autopilot until done"
  - alias: "babysit the PR until CI is green"
bindings:
  - { kind: cli, command: "/goal <condition>   (NATIVE — set; `/goal` alone = status; `/goal clear|stop|off|reset|none|cancel` = clear)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: no company face. /goal v2.1.139+. Also `claude -p \"/goal …\"` runs the loop to completion in one headless invocation (Ctrl+C to stop). Evaluator = the configured small-fast model (default Haiku)" }
  - { kind: cli, command: "/loop <interval> <prompt>   (NATIVE — interval keep-going; cron-backed)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: session-scoped; mechanics in [[routines]]. `/loop 20m /review-pr 1234` re-runs a saved skill each iteration" }
  - { kind: cli, command: "Stop hook in settings.json   (NATIVE — durable cross-session keep-going)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: a settings hook, not a company op; script (deterministic) or prompt (model-evaluated)" }
liveness: none
emits: []
consequences:
  - when: "/goal set"
    expect: []
    evidence: "a turn starts immediately with the condition as the directive; after each turn the evaluator's short reason appears in the status view and transcript. Observable only in the local CLI — NOT on company [[events]] (these are native in-session loops, not supervisor-spawned sessions)"
  - when: "/loop set"
    expect: []
    evidence: "the prompt re-fires between turns; the chosen delay + reason print each iteration. Local-only; see [[routines]] for the cron task list"
correlate: []
verification:
  goal: {state: unverified, note: "no company face — native /goal"}
  loop: {state: unverified, note: "no company face — native /loop, mechanics in [[routines]]"}
```
### Description (purpose-free)
Three native ways to keep one session working without per-step prompting, chosen by what starts
the next turn (the table in [[workflows#Representation]]): `/goal` starts the next turn when the
previous finishes and stops when a fresh evaluator model confirms a condition — write the
condition so Claude's OWN output can demonstrate it (the evaluator runs no tools, reads no files;
e.g. "`npm test` exits 0", state a check and the constraints that must not change); `/loop`
starts the next turn on a time interval (mechanics in [[routines]]); a Stop hook is the durable,
settings-scoped, scriptable form. `/goal` and auto mode are complementary — auto mode removes
per-tool prompts, `/goal` removes per-turn prompts. None of these is a Company operation; for
the Company's OWN multi-session coordination, the built path is the consult-fan
([[session#op: session.post]] verb=consult), not anything in this op.
### Errors
```contract:error
code: workflows.not-exposed | http: 501 | retryable: false
when: any keep-going steer attempted through a Company endpoint
teach: "The Company exposes no /goal or /loop face. Use them in a native `claude` session (or `claude -p \"/goal …\"` headless). For the Company's parallel-session coordination, use [[session#op: session.post]] verb=consult (the consult-fan — it IS built). For scheduled/unattended runs see [[routines]] and [[ci]]."
```
```contract:error
code: workflows.goal-unavailable | http: 403 | retryable: false
when: "/goal is blocked"
teach: "`/goal` needs the workspace trust dialog accepted and is unavailable when disableAllHooks is set at any settings level or allowManagedHooksOnly is set in managed settings (the evaluator is part of the hooks system). The command tells you why rather than silently no-op'ing (source: https://code.claude.com/docs/en/goal.md Requirements)."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud (V11)
binding: cli
request: |
  /goal all tests in test/auth pass and the lint step is clean
response: |
  (NATIVE) A turn starts immediately with the condition as the directive; a `◎ /goal active`
  indicator shows. After each turn the Haiku evaluator returns yes/no + a reason; 'no' starts
  another turn, 'yes' clears the goal and records an achieved entry. No company endpoint is
  involved — this is an in-session loop, invisible to company [[events]].
```
Adjacent: [[workflows#op: workflows.watch]] (the channels push-in mode),
[[session#op: session.post]] (verb=consult — the COMPANY parallel primitive, building),
[[routines]] (interval/cron + unattended cloud), [[ci]] (CI-triggered runs).

## op: workflows.watch
**`workflows.watch` is the PLANNED channels mode — an MCP-server plugin pushes external events
(CI results, chat messages, webhooks) INTO a running session so Claude reacts while you are away,
optionally replying back through the same channel; a native research-preview feature, not a
Company face, and distinct from the Company's own SSE event stream [[events#op: events.watch]].**
```contract:op
op: workflows.watch
resource: workflows
kind: watch
status: planned
direction: inbound
atlas: [CC-22.3]
tasks:
  - phrase: "push CI failures into my running session"
  - phrase: "let me message my session from my phone"
    params: {channel: telegram}
  - phrase: "have a webhook reach Claude where my files are already open"
  - alias: "chat bridge to a running session"
  - alias: "react to events while away"
bindings:
  - { kind: cli, command: "claude --channels plugin:<name>@<marketplace>   (NATIVE — opt a channel plugin into a session)", transport: tui-interactive, exposure: "n/a — interactive", status: planned, note: "GAP: no company face. Research preview, v2.1.80+. Plugins: telegram/discord/imessage/fakechat (Bun-based). Requires Anthropic auth (NOT Bedrock/Vertex/Foundry); Team/Enterprise must set channelsEnabled. A channel is an MCP server declaring the experimental channel capability" }
liveness: duplex
frames: "INBOUND: a `<channel source=\"<name>\">` event injected into the session as the next input. OUTBOUND (optional two-way): Claude calls the channel's `reply` tool — the terminal shows the tool call + a 'sent' confirmation, the actual reply text appears on the other platform"
resume: "events arrive only while the session is OPEN — for always-on, run Claude in a background process/persistent terminal; there is no replay of events missed while closed"
keepalive: "n/a — push-driven by the external platform; the channel MCP server polls/subscribes to its platform"
termination: "the channel stops when the session closes or the plugin is removed from --channels"
direction-note: "direction:inbound — the CONSUMER (the channel server) implements the contract: it pushes the event and implements the reply tool; the system reacts. Permission prompts hit while away pause the session unless the channel declares the permission-relay capability (then allowlist senders can approve remotely), or --dangerously-skip-permissions is used in a trusted env"
emits: []
verification:
  channels: {state: unverified, note: "no company face — native channels research preview"}
```
### Description (purpose-free)
A channel is an MCP-server plugin that pushes events from non-Claude sources into the session you
already have open — the gap that fresh-cloud-session (Claude Code on the web) and poll-based MCP
do not fill. Two shapes: a chat bridge (ask from Telegram/Discord/iMessage, the answer returns in
the same chat while work runs against your real local files) and a webhook receiver (a CI / error-
tracker / deploy-pipeline webhook arrives where Claude already has your files open and remembers
the debugging context). Senders are allowlist-gated (pairing-code for Telegram/Discord, self-chat
bypass for iMessage); a channel runs only when named in `--channels` and enabled by the org. This
is NOT the Company's own event stream — the Company's fabric SSE is [[events#op: events.watch]],
which pushes `agent_sessions.*` facts OUT to consumers, the inverse direction.
### Errors
```contract:error
code: workflows.channels-not-exposed | http: 501 | retryable: false
when: any attempt to configure a channel through a Company endpoint
teach: "Channels are a native Claude Code research-preview feature, not a Company face. Install a channel plugin (e.g. /plugin install telegram@claude-plugins-official) and launch with `claude --channels plugin:telegram@claude-plugins-official`. Requires Anthropic auth (not Bedrock/Vertex/Foundry) and, for orgs, channelsEnabled. The Company's OWN out-bound fact stream is [[events#op: events.watch]] (a different direction)."
```
```contract:example
captured: synthetic            # status=planned → synthetic legal AND loud (V11)
binding: cli
request: |
  claude --channels plugin:fakechat@claude-plugins-official
  # then, in the localhost fakechat UI (http://localhost:8787):
  hey, what's in my working directory?
response: |
  (NATIVE) The message arrives in the session as a <channel source="fakechat"> event; Claude
  reads it, does the work, and calls fakechat's `reply` tool — the answer shows up in the chat
  UI. No company endpoint participates. (channels.md quickstart.)
```
Adjacent: [[workflows#op: workflows.act]] (the in-session keep-going modes),
[[events#op: events.watch]] (the Company's OUT-bound fact stream — opposite direction),
[[session#op: session.post]] (the Company's IN-bound message act, the consult-fan).

## Errors
**Resource-level vocabulary: `workflows.not-exposed` / `workflows.goal-unavailable` (the
keep-going modes) and `workflows.channels-not-exposed` (the push-in mode) — every code teaches
the native recovery and, crucially, redirects the LIVE Company coordination need to
[[session#op: session.post]] verb=consult, which is the one primitive in this neighbourhood that
is actually built.** No error claims a Company workflow engine that does not exist (verified
2026-06-12).

## Links
**No address-typed fields resolve to a Company entry: `/goal`/`/loop`/Stop-hook acts produce
turns inside one local CLI session (not [[session]] fabric records, not [[events]]); a channel
event is an external platform message injected locally.** The one in-corpus dereferenceable
relation is the redirect: the LIVE parallel-coordination capability lives at
[[session#op: session.post]] (verb=consult), whose forks ARE `session://` records observable on
[[events]] and joinable by thread on [[session-message]]. [[routines]] holds the scheduled/cron
forms; [[ci]] holds the CI-triggered forms.
