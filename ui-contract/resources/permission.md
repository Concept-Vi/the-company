---
type: contract-entry
resource: permission
summary: The tool-approval posture a Claude Code session runs under — the mode (default/acceptEdits/plan/dontAsk/bypassPermissions/auto) plus the allow/deny/ask rule lists that gate every tool call; the company exposes ONE fabric-wide posture today, the per-session rule surface is planned.
schemes: []
status: planned
relates-to: ["[[fabric-config]]", "[[session]]", "[[model]]", "[[headless-control]]"]
---

# Resource: permission

## Identity
**A permission posture is identified by the SESSION it governs (`session://<id>`) — there is no
standalone permission record and no `permission://` scheme; the posture is an attribute of a
session, read from the fabric config and (when the per-session surface lands) set at spawn.**
Claude Code's permission model is the five-step evaluation order (hooks -> deny rules -> ask rules
-> permission mode -> allow rules -> `canUseTool`) documented at
https://code.claude.com/docs/en/agent-sdk/permissions.md — this resource contracts the levers a
consumer turns over that machinery, NOT a new addressable object. Today the only live lever is the
fabric-wide posture read via [[fabric-config#op: fabric-config.get]]; everything finer is `planned`
with the spawn-param gap named per op.

## Representation
**A session's effective permission state is a permission MODE (one closed enum value) plus three
ordered rule lists (allow / deny / ask) plus the resolved tool surface — the company today pins
mode=`COMPANY_FABRIC_PERMISSION` (default `plan`) and a single fixed allow rule (`mcp__company`)
across every spawned session; per-session mode and rules are the planned extension.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/permission.posture",
  "type": "object",
  "required": ["mode"],
  "properties": {
    "mode": { "enum": ["default", "acceptEdits", "plan", "dontAsk", "bypassPermissions", "auto"],
              "description": "the baseline approval behaviour; source of truth https://code.claude.com/docs/en/agent-sdk/permissions.md#available-modes. auto is TypeScript-SDK only" },
    "allow": { "type": "array", "items": { "type": "string" },
               "description": "rule strings pre-APPROVED, e.g. Read, Bash(git diff *), mcp__company__*. Tool-name globs only after a literal mcp__<server>__ prefix; an unanchored */mcp__* is ignored with a startup warning" },
    "deny":  { "type": "array", "items": { "type": "string" },
               "description": "blocked even under bypassPermissions. Bare name (Bash) removes the tool from context entirely; scoped (Bash(rm *)) blocks only matches; * removes every tool; mcp__* every MCP tool" },
    "ask":   { "type": "array", "items": { "type": "string" },
               "description": "rule strings that force the canUseTool prompt even under bypassPermissions; under dontAsk a matching ask rule is DENIED instead of prompting" },
    "resolved_tools": { "type": "array", "items": { "type": "string" },
                        "description": "the actual tool surface after deny-removal — read-only reflection (system/init carries it on the stream-json face, see [[headless-control]])" } } }
```
| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| mode | enum | yes (planned: per-session at spawn / SDK set_permission_mode mid-session) | NO company event today — the env flip is call-time read by `fabric_permission()` (`runtime/session_supervisor.py:134-136`) and applied as `--permission-mode` on EVERY spawn (`:263`) | — | 100% = `COMPANY_FABRIC_PERMISSION`, default `plan`; read via [[fabric-config#op: fabric-config.get]] `.permission`. Per-session override = NOT BUILT (spawn takes no permission param) |
| allow | array | no (fixed) | — | — | exactly `["mcp__company"]` on every spawn (`--allowedTools mcp__company`, `:265`) — the fabric grants ONLY the company MCP tool; native tools fall through to the mode. NOT consumer-tunable today |
| deny / ask | array | n/a | — | — | EMPTY — the fabric passes no `--disallowedTools` and configures no settings.json ask rules for spawned sessions. The whole rule surface is `planned` |
| resolved_tools | array | yes | the session's own init | — | observable on the per-session stream's `system/init` event (NOT yet surfaced through a company face — see [[headless-control#op: headless-control.watch]]) |

## State model
**State model: stateless.** A permission posture has no lifecycle of its own — it is an attribute
read from config or fixed at a session's spawn. The session it governs has the lifecycle
([[session#State model]]); a posture is just one of that session's launch parameters.

## Caller
**Reading the live fabric posture is anonymous-local via [[fabric-config]]; SETTING a posture is
the operator's act today (env on the service + restart — deliberately not an op), and when the
per-session surface lands the setter is whoever spawns the session, carrying it as a spawn
parameter — never an ambient default.** No consumer can today widen another session's permissions;
the fabric's read-only-by-default posture (`plan`) is the safety floor, raised only by a recorded
operator decision (the same B3-class discipline as the bind in [[fabric-config#Caller]]).

## Operations

## op: permission.get
**`permission.get` is the pre-flight posture read: the mode every fabric-spawned session will run
under and the fixed `mcp__company` allow surface — a consumer reads this to know whether a spawned
session can write files (acceptEdits) or only plan (plan), exactly as it reads the cap before
fanning.**
```contract:op
op: permission.get
resource: permission
kind: get
status: building
direction: outbound
atlas: [CC-07.1]
tasks:
  - phrase: "what permission mode will a spawned session run under"
  - phrase: "can fabric sessions edit files or only plan"
  - alias: "check the fabric's approval posture"
  - alias: "is the fabric read-only"
bindings:
  - { kind: http, method: GET, path: /health, transport: supervisor-http, exposure: "exposure.json#supervisor-http", note: "the SAME read as fabric-config.get; .permission is the posture mode. There is no dedicated permission endpoint — the posture is a config field" }
  - { kind: cli, command: "company status   (the session-supervisor row reflects up/down; the posture rides the health read)", transport: cli-local, exposure: "exposure.json#cli-local" }
liveness: snapshot
live-twin: "none — static between operator env changes + restart"
emits: []
verification:
  posture-read: {state: probe-verified, run: "session_supervisor_acceptance section 1 (health asserts .permission)", date: 2026-06-12, note: "the field is the same one [[fabric-config#op: fabric-config.get]] proves; this op is the permission-lens NAME for it"}
```
This op deliberately overlaps [[fabric-config#op: fabric-config.get]] — same wire read, different
retrieval lens (a consumer asking "permissions" finds it here; one asking "fabric posture" finds it
there; both resolve to `GET /health`'s `.permission`). Mode meanings are in the
[[permission#Representation]] enum, sourced to the permissions doc.
```contract:example
captured: synthetic            # status=building — replaced by captured evidence at flip-to-live (V11)
binding: http
request: |
  GET /health HTTP/1.1
response: |
  HTTP/1.1 200 OK
  {"ok": true, "service": "session-supervisor", "bind": "127.0.0.1",
   "sessions": {"total": 1, "by_state": {"idle": 1}},
   "cap": 3, "turn_timeout_s": 900.0, "permission": "plan"}
```
Adjacent: [[fabric-config#op: fabric-config.get]] (the same read, fabric lens),
[[session#op: session.create]] (the spawn this posture governs),
[[permission#op: permission.act]] (the planned per-session setter).

## op: permission.act
**`permission.act` is the PLANNED per-session approval steer: set a spawned session's mode and
allow/deny/ask rules at launch and (SDK-style) change the mode mid-session — the spawn-param + the
control-request the company does not yet wire, named here so a UI builds toward the real seam, not a
fiction.**
```contract:op
op: permission.act
resource: permission
kind: act
status: planned
direction: outbound
atlas: [CC-07.2, CC-07.3, CC-07.4]
tasks:
  - phrase: "spawn a session that can edit files without prompting"
    params: {mode: acceptEdits}
  - phrase: "lock a session to a fixed tool surface"
    params: {mode: dontAsk, allow: ["Read", "Grep"]}
  - phrase: "let a session run a turn then tighten its permissions"
    params: {act: set-mode}
  - alias: "approve edits for this session"
  - alias: "raise a session's permissions"
  - alias: "change permission mode mid-session"
bindings:
  - { kind: http, method: POST, path: "/spawn  (PLANNED extension: a permission block on the body)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: planned, note: "GAP: spawn() (runtime/session_supervisor.py:254) accepts cwd/resume/fork/name/source ONLY — no permission/mode/allow/deny param. Every spawn is pinned to fabric_permission() + --allowedTools mcp__company. Wiring = add a permission block -> map to --permission-mode/--allowedTools/--disallowedTools" }
  - { kind: http, method: POST, path: "/permission  (PLANNED: mid-session set-mode control_request, the SDK setPermissionMode analogue)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: planned, note: "GAP: no control surface writes a control_request to a live session's stdin for permission. The held-open stream-json transport CAN carry it; unbuilt" }
liveness: none
emits: []
consequences:
  - when: "set at spawn (planned)"
    expect: [agent_sessions.spawned]
    bound: "the spawn's own bound ([[session#op: session.create]]); the posture is a launch attribute, observable only via the session's system/init resolved_tools — NOT a distinct fabric event"
    evidence: "[[headless-control#op: headless-control.watch]] system/init tools/permissionMode — the named read for an absence-of-dedicated-event outcome (CONTRACT-FORMAT section 6 V9)"
  - when: "set mid-session (planned)"
    expect: []
    evidence: "the next tool call's approval behaviour on [[session#op: session.watch]] (a write the new mode would have prompted now auto-approves, or vice-versa) — there is no fabric event for a mode change; its proof is behavioural"
correlate: [session]
verification:
  spawn-with-mode: {state: unverified, note: "the spawn param does not exist — planned"}
  set-mode-mid:    {state: unverified, note: "no control surface — planned"}
```
### Description (purpose-free)
Two planned capabilities the native model supports and the company does not yet expose. (1) At
spawn: carry a permission block (mode + allow/deny/ask rule strings) so a session launches under a
chosen posture instead of the fabric-wide default — the native CLI does this with
`--permission-mode`, `--allowedTools`, `--disallowedTools` (https://code.claude.com/docs/en/headless,
https://code.claude.com/docs/en/agent-sdk/permissions.md). (2) Mid-session: change the mode of a
live supervised session, the native `setPermissionMode()` / `set_permission_mode()` SDK call
(https://code.claude.com/docs/en/agent-sdk/permissions.md#set-permission-mode) — start restrictive,
loosen as trust builds. Both ride parameters the supervisor's spawn and held-open stdin could carry;
neither is wired today, so this op is `planned`, its examples synthetic-and-loud, its verification
rows honestly unverified.
### Request (PLANNED shape — the contract the seam should fulfil)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/permission.act.request",
  "type": "object",
  "required": ["session", "act"],
  "properties": {
    "session": { "type": "string", "description": "session://<id> being spawned or steered" },
    "act":     { "enum": ["set-at-spawn", "set-mode"], "description": "set-at-spawn rides the /spawn body; set-mode is the mid-session control_request" },
    "mode":    { "enum": ["default", "acceptEdits", "plan", "dontAsk", "bypassPermissions", "auto"] },
    "allow":   { "type": "array", "items": { "type": "string" } },
    "deny":    { "type": "array", "items": { "type": "string" } },
    "ask":     { "type": "array", "items": { "type": "string" } } },
  "additionalProperties": false }
```
### Interaction semantics
Native rules a consumer MUST respect even when this op lands (sourced to the permissions doc):
- **Deny beats everything.** A `deny` match blocks the tool even under `bypassPermissions`; hooks
  and ask rules are evaluated before the mode check and can still block.
- **`allow` does NOT constrain `bypassPermissions`.** Setting `allow:["Read"]` with
  `mode:bypassPermissions` still approves Bash/Write/Edit — to block specifics under bypass you must
  use `deny`. (The locked-down recipe is `mode:dontAsk` + `allow:[...]`.)
- **Subagent inheritance (the dangerous one):** a parent in `bypassPermissions`/`acceptEdits`/`auto`
  propagates that mode to ALL its subagents and it cannot be overridden per subagent — an `ask` rule
  is the only per-subagent forcing of a prompt. This is WHY the fabric's default is `plan`.
- **`plan` mode** never auto-approves file edits even when an allow rule matches; edits route to
  `canUseTool`.
### Errors
```contract:error
code: permission.unsupported-mode | http: 400 | retryable: false
when: mode not in the closed enum (e.g. a typo or a TypeScript-only "auto" against a non-TS face)
teach: "Modes are default/acceptEdits/plan/dontAsk/bypassPermissions/auto (auto is TS-SDK only). See [[permission#Representation]]; meanings at https://code.claude.com/docs/en/agent-sdk/permissions.md."
```
```contract:error
code: permission.not-exposed | http: 501 | retryable: false
when: any call against this op today
teach: "Per-session permission setting is PLANNED — the fabric pins COMPANY_FABRIC_PERMISSION + mcp__company on every spawn. To run a session under a different posture today, an operator restarts the service with COMPANY_FABRIC_PERMISSION=<mode>; READ the live posture via [[permission#op: permission.get]]. The spawn-param gap is named in this op's bindings."
```
```contract:example
captured: synthetic            # status=planned -> synthetic legal AND loud; no spawn permission param exists (V11)
binding: http
request: |
  POST /spawn HTTP/1.1   (PLANNED body extension)
  {"cwd": "/home/tim/scratch", "name": "editor-1",
   "permission": {"mode": "acceptEdits", "deny": ["Bash(rm *)"]}}
response: |
  HTTP/1.1 501 Not Implemented
  {"error": "Per-session permission is planned; the fabric pins COMPANY_FABRIC_PERMISSION (plan) + --allowedTools mcp__company on every spawn. Read the live posture at GET /health .permission."}
```
Adjacent: [[permission#op: permission.get]] (the live read that DOES work),
[[session#op: session.create]] (the spawn this would extend),
[[headless-control#op: headless-control.watch]] (where `resolved_tools` becomes observable).

## Errors
**Resource-level error vocabulary: `permission.unsupported-mode` (closed-enum guard) and
`permission.not-exposed` (the honest 501 every `planned` setter returns until the spawn-param seam
is built).** Both teach the recovery in-corpus: read the live posture, or have the operator flip
the fabric env. No error claims a capability the code does not have.

## Links
**No address-typed fields: a posture references the `session://` it governs (dereferences to
[[session]] via that entry's accepting ops) and nothing else.** The `allow`/`deny`/`ask` strings are
tool-NAME patterns (Claude Code permission-rule syntax,
https://code.claude.com/docs/en/settings#permission-rule-syntax), not fabric addresses — they never
resolve to a corpus entry, by design.
