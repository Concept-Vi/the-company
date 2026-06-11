---
type: contract-entry
resource: agent-team
summary: Claude Code's NATIVE multi-agent surfaces — single-session subagents (Task/Agent tool, .claude/agents definitions) and experimental agent TEAMS (lead + teammates with a shared task list and a mailbox); the company's own working team primitive is the F1 session fabric, so this entry contracts the native surface as planned and routes the live capability to the fabric.
schemes: []
status: planned
relates-to: ["[[session]]", "[[session-message]]", "[[model]]", "[[permission]]", "[[headless-control]]"]
---

# Resource: agent-team

## Identity
**Claude Code has TWO native worker surfaces, and the company has a THIRD that overlaps neither
cleanly — this entry names all three so a consumer is never confused about which "team" it is
driving:** (1) NATIVE SUBAGENTS — workers inside ONE session that only report back to the caller,
defined in `.claude/agents/*.md` or `--agents` JSON, invoked by the `Agent`/Task tool
(https://code.claude.com/docs/en/sub-agents.md); (2) NATIVE AGENT TEAMS — separate Claude Code
instances that share a task list and message EACH OTHER directly, experimental and disabled by
default (https://code.claude.com/docs/en/agent-teams.md); (3) the COMPANY SESSION FABRIC — the live
capability, where [[session#op: session.post]] verb=consult fans N forked sessions and replies
aggregate on a [[session-message]] thread. The native surfaces (1)+(2) are `planned` at the company
layer; the fabric (3) is the `building` thing a consumer uses TODAY for parallel agents, contracted
on [[session]]/[[session-message]]. There is no `team://` scheme — a native team is keyed by its
NAME (config at `~/.claude/teams/<name>/config.json`), a fabric fan by its thread.

## Representation
**A native agent team is (lead + teammates + a shared task list + a mailbox), each teammate a full
independent Claude Code session with its OWN context window; a native subagent is a single-shot
worker with a system prompt, a tool allowlist and a model, returning only its summary — the company
exposes neither's control surface, so these shapes are the native contract, not a live company
record.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/agent-team.subagent-definition",
  "type": "object",
  "required": ["name", "description"],
  "description": "the .claude/agents/*.md frontmatter / --agents JSON value; source https://code.claude.com/docs/en/sub-agents.md#supported-frontmatter-fields",
  "properties": {
    "name":            { "type": "string", "description": "lowercase-hyphen id; hooks receive it as agent_type" },
    "description":     { "type": "string", "description": "when Claude should delegate to this subagent" },
    "prompt":          { "type": "string", "description": "the system prompt (the .md body, or `prompt` in --agents JSON)" },
    "tools":           { "type": "array", "items": { "type": "string" }, "description": "allowlist; inherits all if omitted. Agent/AskUserQuestion/EnterPlanMode/ExitPlanMode/ScheduleWakeup/WaitForMcpServers are NEVER available to subagents" },
    "disallowedTools": { "type": "array", "items": { "type": "string" } },
    "model":           { "type": "string", "description": "sonnet|opus|haiku|fable|full-id|inherit (default inherit)" },
    "permissionMode":  { "enum": ["default", "acceptEdits", "auto", "dontAsk", "bypassPermissions", "plan"] },
    "maxTurns":        { "type": "integer" },
    "skills":          { "type": "array", "items": { "type": "string" }, "description": "preloaded full skill content; NOT applied when the definition runs as a TEAMMATE" },
    "mcpServers":      { "type": "array", "description": "names or inline configs; NOT applied to teammates (they load project/user MCP)" },
    "memory":          { "enum": ["user", "project", "local"], "description": "persistent cross-session memory scope" },
    "background":      { "type": "boolean", "description": "always run as a background task" },
    "effort":          { "enum": ["low", "medium", "high", "xhigh", "max"], "description": "overrides session effort while active" },
    "isolation":       { "const": "worktree", "description": "run in a temporary git worktree (branched from the default branch), auto-cleaned if no changes" },
    "color":           { "enum": ["red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"] } } }
```
| concept | native reality | company reality (2026-06-12) |
|---|---|---|
| subagent invoke (Task/Agent tool) | the main session's tool; isolates context, returns a summary; CANNOT nest (subagents don't spawn subagents) | a fabric session runs `--allowedTools mcp__company` ([[permission]]) so the native Agent tool is OUT of its allow surface — fabric sessions don't fan native subagents; the fabric's fan is [[session#op: session.post]] consult |
| agent teams gate | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`, requires v2.1.32+; experimental | NOT enabled on fabric spawns; the company manages no native team |
| team storage | `~/.claude/teams/<name>/config.json` + `~/.claude/tasks/<name>/`, runtime state, removed at cleanup/session-end | n/a — the fabric's equivalent is the durable mail leaf + registry ([[session-message]], [[session]]) |
| inter-agent messaging | teammates message by NAME (`SendMessage`); auto-delivered; lead synthesises | the fabric's equivalent is durable mail with explicit `from_session`/`thread` ([[session#op: session.post]]) — addressed, durable, NOT auto-pushed |
| teammate model | `CLAUDE_CODE_SUBAGENT_MODEL` overrides all teammate/subagent models | the fabric sets no such env; consult forks run the account default ([[model]]) |
| teammate permissions | inherit the LEAD's mode (set at spawn, not per-teammate); a parent in bypass propagates to all | the fabric's forks inherit the fabric posture (`plan`); see [[permission#Interaction semantics]] |

## State model
**State model: stateless (this entry is a native-surface catalog; the lifecycle lives elsewhere).**
A native team's lifecycle (lead created -> teammates spawned -> tasks claimed/blocked/completed ->
cleanup) is owned by Claude Code's own runtime, not a company face; a fabric fan's lifecycle is the
spawned sessions' ([[session#State model]]). A task in the shared list has three native states
(pending -> in-progress -> completed, with dependency-blocking) — observable only inside the lead's
own session today, not through any company op.

## Caller
**Driving a native team is the LEAD session's own act (the lead is fixed for the team's lifetime —
no promotion, no nesting); driving the fabric's fan is whoever calls [[session#op: session.post]]
with verb=consult, naming itself via `from_session`.** The company has no face that creates or
controls a native team, so there is no caller-identity model to define for (1)+(2) here — when one
lands it inherits supervisor-http's anonymous-local model ([[TRANSPORTS]]).

## Operations

## op: agent-team.list
**`agent-team.list` is the worker-roster read — PLANNED for native teams/subagents (no company face
enumerates `~/.claude/teams` or `.claude/agents`); the LIVE roster of parallel company workers is a
[[session#op: session.list]] filtered to a consult fan's forks, so this op routes there until the
native surface is exposed.**
```contract:op
op: agent-team.list
resource: agent-team
kind: list
status: planned
direction: outbound
atlas: [CC-09.5, CC-09.6]
tasks:
  - phrase: "list the agent teams"
  - phrase: "what subagent definitions exist"
  - phrase: "show my running teammates"
  - alias: "team roster"
  - alias: "available agent types"
bindings:
  - { kind: http, method: GET, path: "/teams  (PLANNED: a supervisor roster endpoint over ~/.claude/teams + .claude/agents)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: planned, note: "GAP: no endpoint reads native team config or agent definitions. Native discovery is the interactive /agents Library tab + the team config members array — neither exposed" }
liveness: snapshot
live-twin: "[[session#op: session.list]] — the LIVE company workers (filter to a fan's forks by their shared cwd/name); the fabric's roster IS the session catalog"
emits: []
verification:
  roster-read: {state: unverified, note: "no native-team endpoint — planned"}
```
For the LIVE parallel-worker roster today, use [[session#op: session.list]] with
`state=supervised-live`: a consult fan's forks are supervised sessions; match them by the name the
supervisor minted (`consult-<target>-N`) or their shared cwd. Native subagent SCOPES (where
definitions live, highest-priority first): managed-settings > `--agents` CLI > `.claude/agents/`
(project) > `~/.claude/agents/` (user) > a plugin's `agents/` dir
(https://code.claude.com/docs/en/sub-agents.md#choose-the-subagent-scope). Built-in agent types:
`Explore` (Haiku, read-only), `Plan` (inherits model, read-only), `general-purpose` (all tools).
Adjacent: [[session#op: session.list]] (the live roster), [[agent-team#op: agent-team.act]] (spawn).

## op: agent-team.act
**`agent-team.act` is the PLANNED team/subagent control: create a native team, spawn a teammate
(optionally from a subagent definition), assign tasks, message a teammate, require plan-approval,
shut a teammate down, clean the team up — the native operations the company does not expose; the
LIVE analogue for parallel work is the consult fan on [[session#op: session.post]], so this op
documents the native contract and routes the working capability to the fabric.**
```contract:op
op: agent-team.act
resource: agent-team
kind: act
status: planned
direction: outbound
atlas: [CC-09.5, CC-09.6, CC-09.7, CC-09.8]
tasks:
  - phrase: "create an agent team to work in parallel"
    params: {act: create-team}
  - phrase: "spawn a teammate from a subagent definition"
    params: {act: spawn-teammate, agent_type: "security-reviewer"}
  - phrase: "run a parallel code review with three reviewers"
    params: {act: create-team}
  - phrase: "require a teammate to plan before changing code"
    params: {act: spawn-teammate, plan_approval: true}
  - phrase: "shut down a teammate"
    params: {act: shutdown-teammate}
  - alias: "delegate to a subagent"
  - alias: "fan out parallel workers"
  - alias: "message a teammate"
bindings:
  - { kind: http, method: POST, path: "/team  (PLANNED: native team control over ~/.claude/teams)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: planned, note: "GAP: no native-team control surface. Native teams need CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 and are driven from inside a lead session by natural language + SendMessage/task tools — not an API" }
  - { kind: mcp, tool: session_post, server: company, exposure: "exposure.json#mcp-company", note: "the LIVE analogue: verb=consult, copies=N is the company's parallel-worker fan (see [[session#op: session.post]]). NOT native teams — fabric forks, durable mail, no inter-worker auto-messaging" }
liveness: none
emits: []
consequences:
  - when: "native team created/teammate spawned (planned)"
    expect: []
    bound: "no company event — native team state lives in ~/.claude/teams, invisible to the fabric event log"
    evidence: "PLANNED [[agent-team#op: agent-team.list]]; today there is NO company-visible evidence for a native team — the honest gap, not an absence-read"
  - when: "the LIVE consult fan (verb=consult on session.post)"
    expect: ["agent_sessions.spawned x N"]
    bound: "all N <= the cap ([[fabric-config]]); replies join the one returned thread"
    invariant: "each fork's origin session is byte-identical (fork law, T4-verified) — see [[session#op: session.post]] consult branch"
    evidence: "[[events#op: events.list]] for the N spawned events; [[session-message#op: session-message.list]] thread= for the replies"
correlate: [intent_id]
verification:
  native-team:  {state: unverified, note: "no native-team control surface — planned"}
  consult-fan:  {state: probe-verified, run: "T4 fork physics (~/xsession-tests/RESULTS.md) — the LIVE analogue; end-to-end via session.post is the lead's", date: 2026-06-11, note: "this is the fabric capability, contracted in full on [[session#op: session.post]]"}
```
### Description (purpose-free)
The native subagent + agent-team operations, `planned` at the company layer, with the live parallel
capability routed to the fabric. Native subagents (single-shot, report-back-only, cannot nest) and
native agent teams (independent instances, shared task list, direct inter-agent messaging, gated by
`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) are both driven from INSIDE a Claude Code session by natural
language and the `Agent`/`SendMessage`/task tools — there is no external API, so no company face
wraps them. What a consumer uses TODAY for parallel agents is the consult fan: one question to N
forked copies of a session, replies aggregated on a thread — contracted in full on
[[session#op: session.post]]. The two surfaces are NOT equivalent: native teammates auto-message
each other and self-claim shared tasks; fabric forks are isolated, communicate only via durable
addressed mail, and never message each other.
### Request (PLANNED shape for native teams)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/agent-team.act.request",
  "type": "object",
  "required": ["act"],
  "properties": {
    "act":          { "enum": ["create-team", "spawn-teammate", "assign-task", "message-teammate", "shutdown-teammate", "cleanup-team"] },
    "team":         { "type": "string", "description": "team name (-> ~/.claude/teams/<name>)" },
    "agent_type":   { "type": "string", "description": "a subagent definition name to base a teammate on (project/user/plugin/CLI scope)" },
    "name":         { "type": "string", "description": "teammate name (for later message/shutdown by name)" },
    "prompt":       { "type": "string", "description": "the spawn prompt (teammates do NOT inherit the lead's conversation history)" },
    "plan_approval":{ "type": "boolean", "description": "teammate works read-only in plan mode until the lead approves" },
    "model":        { "type": "string", "description": "teammate model; CLAUDE_CODE_SUBAGENT_MODEL overrides it ([[model]])" } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a consumer respects (sourced to agent-teams.md / sub-agents.md):
- **One team per lead, no nesting, lead is fixed.** A teammate cannot spawn its own team; leadership
  never transfers.
- **Teammates inherit the lead's permission mode at spawn** and it can't be set per-teammate at spawn
  time (changeable after). A lead in `--dangerously-skip-permissions` makes all teammates so —
  the [[permission]] inheritance hazard.
- **Subagent definitions reused as teammates** honor the definition's `tools` allowlist and `model`,
  and the body is APPENDED to the teammate's system prompt; `skills` and `mcpServers` frontmatter are
  IGNORED for teammates (they load project/user config instead). `SendMessage` + task tools are
  always available regardless of the `tools` allowlist.
- **Subagents cannot use** Agent/AskUserQuestion/EnterPlanMode/ScheduleWakeup/WaitForMcpServers even
  if listed (UI/session-state tools).
- **Display mode** is `auto`/`tmux`/`in-process` (`teammateMode` / `--teammate-mode`); split panes
  need tmux or iTerm2.
### Errors
```contract:error
code: agent-team.not-exposed | http: 501 | retryable: false
when: any native-team or native-subagent control act against the company today
teach: "Native teams/subagents have no company control surface. For parallel agents NOW use [[session#op: session.post]] verb=consult, copies=N (the fabric fan); list live workers via [[session#op: session.list]]. Native teams are driven inside a lead session, gated by CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1."
```
```contract:error
code: agent-team.experimental-disabled | http: 409 | retryable: false
when: a native-team act when CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS is unset (the gate the company has not flipped)
teach: "Native agent teams are experimental and off by default. Enabling is an operator decision (env/settings.json), and even then they are driven inside a lead session, not via an API. The supported parallel path is the consult fan on [[session#op: session.post]]."
```
```contract:example
captured: synthetic            # status=planned -> synthetic legal AND loud; no native-team company face exists (V11)
binding: mcp
request: agent-team.act(act="create-team", prompt="review PR 142: one security, one performance, one tests")
response: { "error": { "code": "agent-team.not-exposed",
            "message": "no native-team control surface",
            "teach": "Use session_post verb=consult copies=3 for a parallel fan; native teams run inside a lead session.",
            "retryable": false } }
```
Adjacent: [[session#op: session.post]] (the LIVE consult fan), [[session-message#op: session-message.list]]
(collecting a fan's replies on the thread), [[model]] (teammate models),
[[permission#Interaction semantics]] (the inheritance hazard), journey [[message-and-read-reply]].

## Errors
**Resource-level error vocabulary: `agent-team.not-exposed` (the honest 501 — no native control
surface) and `agent-team.experimental-disabled` (the native gate the company has not flipped).** Both
teach the live recovery: the consult fan on [[session#op: session.post]]. No error claims a native
team capability the company lacks; the working capability is always routed to the fabric.

## Links
**No address-typed fields: a native team is name-keyed (a local file path, not a fabric address); a
subagent definition is name-keyed.** The LIVE relationships ARE addressed — a consult fan's forks
are `session://` (dereference to [[session]]) and its replies are mail records on a thread
([[session-message]]); those addresses live on [[session#op: session.post]]'s response, not here.
This entry's `relates-to` carries the cross-resource map.
