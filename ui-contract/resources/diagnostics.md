---
type: contract-entry
resource: diagnostics
summary: How Claude Code health, debug output, and failures are inspected — /doctor (install/settings/MCP/context health), /status, --debug categories, --safe-mode/--bare, the OTel telemetry export, and the error-event surface; the company's fabric exposes the supervisor /health read live (building) and folds per-session failures onto the event stream, while the native /doctor + --debug levers are planned (the spawn threads no --debug) with the gap named.
schemes: []
status: building
relates-to: ["[[fabric-config]]", "[[session]]", "[[events]]", "[[headless-control]]", "[[settings]]", "[[platform]]", "[[surfaces]]"]
---

# Resource: diagnostics

## Identity
**A diagnostic is identified by WHAT it inspects (install/settings/MCP/context health, debug
categories, telemetry signals, or a failure event), not a fabric address — there is no
`diagnostics://` scheme; the company surfaces fabric health through the supervisor's `GET /health`
read and surfaces per-session failures as `agent_sessions` events on the fact stream, while the
native single-session diagnostic levers (`/doctor`, `--debug`) are inspectors of an interactive or
headless `claude` process the company does not expose those controls of.** The native diagnostic set
(source of truth https://code.claude.com/docs/en/troubleshooting.md, cli-reference.md): `/doctor`
(one-pass health: install, settings validity, MCP config, context usage, keybinding warnings),
`/status` (active model/auth/setting-sources), `/bug` and `/feedback` (report), `--debug [filter]`
(category-filtered debug log, e.g. `api,hooks` or `!1p,!file`), `--debug-file <path>`, `--safe-mode`
(disable all customizations), `--bare` (minimal mode), and OTel telemetry export
(https://code.claude.com/docs/en/monitoring-usage.md). This resource maps those to the company's two
real diagnostic surfaces (fabric health + the event stream) and names the per-session-debug gap.

## Representation
**A diagnostic state is the pair (fabric health, per-session failure signal): fabric health is the
supervisor's live `{ok, service, bind, sessions, cap, turn_timeout_s, permission}`; a per-session
failure is an `is_error` result / abnormal exit that arrives as an `agent_sessions` event — the
company has NO per-session /doctor or threaded --debug today.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/diagnostics.state",
  "type": "object",
  "properties": {
    "fabric_health": { "type": "object",
      "description": "the supervisor self-report — the company's one LIVE diagnostic read (GET /health). Same field set as [[fabric-config]]",
      "properties": {
        "ok":            { "type": "boolean" },
        "service":       { "const": "session-supervisor" },
        "bind":          { "type": "string", "const": "127.0.0.1" },
        "sessions":      { "type": "object", "description": "{total, by_state}" },
        "cap":           { "type": "integer" },
        "turn_timeout_s":{ "type": "number" },
        "permission":    { "type": "string" } } },
    "session_failure": { "type": "object",
      "description": "a per-session failure as it appears on the event stream (NOT a /doctor object)",
      "properties": {
        "kind":   { "enum": ["spawn-failed", "turn-error", "turn-timeout", "supervisor-down"] },
        "session":{ "type": "string", "x-scheme": "session://" },
        "detail": { "type": "string", "description": "teaching text from the supervisor or the underlying claude is_error result" } } } },
  "additionalProperties": false }
```
| field | type | volatile? | changed-by | address? -> resource | reality (2026-06-12) |
|---|---|---|---|---|---|
| fabric_health | object | yes | the supervisor's live state (session count flips per spawn/teardown) | -> [[fabric-config]] | LIVE-READABLE via `GET /health` (`runtime/session_supervisor.py:702-705`) — the company's one proven diagnostic read |
| session_failure (turn-error / turn-timeout) | event | yes | the supervisor's turn loop: a turn exceeding `turn_timeout_s` is killed (`:478`), an underlying claude `is_error` result is recorded | -> [[events]], [[session]] | OBSERVABLE on the event stream / per-session watch. The supervisor consumes the `claude -p` result event; failures surface as session state + mail/error records; the cost/usage fields of that result are now CAPTURED onto the agent_sessions.turn event (CC-20, [[cost-usage]]) rather than discarded |
| /doctor health object (install/settings/MCP/context) | object | yes | the native /doctor pass | — | NOT EXPOSED. /doctor is an interactive-host command; the spawn threads no equivalent. There is no company "session health" object beyond fabric_health + the failure events |
| --debug log | text stream | yes | the native --debug flag | — | NOT THREADED. The spawn passes `--verbose` (`:260`) but NO `--debug`/`--debug-file`; per-session debug categories are not selectable through the company |

## State model
**State model: stateless.** A diagnostic is a read or an event, not a stateful object. The SUPERVISOR
has an up/down liveness (reflected by `ok` and by `company status`) and SESSIONS have lifecycles
([[session#State model]]); a diagnostic observes those, it does not own a machine of its own.

## Caller
**Reading fabric health is anonymous-local via the supervisor `GET /health`; observing per-session
failures is whoever watches the stream ([[events]] / [[session#op: session.watch]]); the native
per-session diagnostics (`/doctor`, `--debug`) have the HOST operator as their only caller because
they inspect a `claude` process the company drives headlessly without those controls.** No company
consumer can run `/doctor` against a fabric session or stream its `--debug` output; the company's
diagnostic vantage is the supervisor's self-report plus the fact stream.

## Operations

## op: diagnostics.get
**`diagnostics.get` is the fabric-health read: the supervisor's live self-report (up?, session
counts, the operating slice) — the company's one PROVEN diagnostic, the same `GET /health` wire read
[[fabric-config]] and [[settings]] use, surfaced here as the health/troubleshooting lens.**
```contract:op
op: diagnostics.get
resource: diagnostics
kind: get
status: building
direction: outbound
atlas: [CC-33.1]
tasks:
  - phrase: "is the session supervisor up and healthy"
  - phrase: "how many sessions are live and what is the cap"
  - phrase: "check fabric health"
  - alias: "health check"
  - alias: "is the fabric ok"
  - alias: "doctor"
bindings:
  - { kind: http, method: GET, path: /health, transport: supervisor-http, exposure: "exposure.json#supervisor-http", note: "the supervisor self-report — the SAME read as [[fabric-config#op: fabric-config.get]] / [[settings#op: settings.get]]; the health/troubleshooting lens. ok=true + the session/cap/timeout slice. Connection refused = supervisor down (the failure this read detects)" }
  - { kind: cli, command: "company status   (renders the session-supervisor row up/down + the operating slice)", transport: cli-local, exposure: "exposure.json#cli-local" }
liveness: snapshot
live-twin: "[[events#op: events.watch]] / [[session#op: session.watch]] for the live failure events this read's session counts summarize"
emits: []
verification:
  fabric-health-read: {state: probe-verified, run: "session_supervisor_acceptance (health asserts ok + cap/turn_timeout_s/permission/bind)", date: 2026-06-12, note: "proven by the same acceptance section [[fabric-config]] cites; the health/doctor lens on GET /health. Per-session /doctor is NOT this read and its gap is named in diagnostics.act"}
```
This op is the company's working "is it healthy" read. The richer native `/doctor` (install
integrity, settings-file validation, MCP server reachability, context-window usage, keybinding
warnings) is NOT exposed — it inspects an interactive `claude` install, not the fabric. `company
status` is the CLI rendering: a refused connection to `127.0.0.1:8771` IS the down signal (the CLI
teaches `company up session-supervisor`). For per-session failures (a turn erroring or timing out),
watch the stream rather than polling this read.
```contract:example
captured: synthetic            # status=building — replaced by captured evidence at flip-to-live (V11)
binding: http
request: |
  GET /health HTTP/1.1
response: |
  HTTP/1.1 200 OK
  {"ok": true, "service": "session-supervisor", "bind": "127.0.0.1",
   "sessions": {"total": 2, "by_state": {"idle": 1, "busy": 1}},
   "cap": 3, "turn_timeout_s": 900.0, "permission": "plan"}
```
Adjacent: [[fabric-config#op: fabric-config.get]] / [[settings#op: settings.get]] (same read, other
lenses), [[events#op: events.watch]] (the live failure stream), [[session#op: session.watch]]
(per-session failure), [[diagnostics#op: diagnostics.watch]] (folded session diagnostics),
[[diagnostics#op: diagnostics.act]] (the planned /doctor + --debug levers).

## op: diagnostics.watch
**`diagnostics.watch` is the per-session failure-observation read: it is NOT a distinct stream but the
diagnostic LENS on the fabric event surface — spawn failures, turn errors, and turn timeouts arrive as
`agent_sessions` events, and a session's `system/init` carries the resolved tool surface a consumer
checks when a tool is unexpectedly unavailable.**
```contract:op
op: diagnostics.watch
resource: diagnostics
kind: watch
status: building
direction: outbound
atlas: [CC-33.2]
tasks:
  - phrase: "watch for session failures and turn errors"
  - phrase: "why did a session's turn fail"
  - phrase: "what tools did a session actually load"
    params: {look_for: "system/init resolved tool surface"}
  - alias: "debug a failing session"
  - alias: "tail session errors"
  - alias: "session init diagnostics"
bindings:
  - { kind: http, method: GET, path: "/watch  (the supervisor ndjson per-session stream)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", note: "the diagnostic lens reuses the SAME stream as [[session#op: session.watch]] / [[headless-control#op: headless-control.watch]] — there is no separate diagnostics stream. Failure-shaped events (is_error results, abnormal exit, the supervisor's timeout kill) and system/init resolved_tools are read off it. SSE mechanics owned by [[events#op: events.watch]] — this section links, never restates" }
liveness: watch
frames: "ndjson — one JSON event object per line on the supervisor's per-session `/watch` GET (the `agent_sessions.*` shape, `seq`/`type`/`session` + failure fields like `is_error`/`detail`); the SAME frame stream [[session#op: session.watch]] reads. This op restates no frame schema — the canonical event frame is owned by [[events#op: events.watch]] (section 10 C-C5)."
resume: "`since=<seq>` query param on the supervisor `/watch` (the example uses `since=-1` for from-now); reconnect and re-read the gap via the snapshot lens of [[diagnostics#op: diagnostics.get]] / [[events#op: events.list]]. Resume mechanics are owned once by [[events#op: events.watch]] (Last-Event-ID on the bridge SSE twin); this lens links, never restates."
keepalive: "owned by [[events#op: events.watch]] (~15s comment frames on the SSE surface); the supervisor ndjson `/watch` holds the connection open between events with no terminal frame — there is no separate diagnostics keepalive."
termination: "no terminal frame — the server holds the stream open; client disconnect ends it (same as [[events#op: events.watch]]). A session reaching `idle`/exit emits its terminal `agent_sessions.*` event in-band but does NOT close the diagnostic stream."
emits: []
verification:
  failure-observable: {state: probe-verified, run: "session_supervisor_acceptance (turn-timeout kill + is_error surface on the watch stream)", date: 2026-06-12, note: "the failure lens on a proven F1 stream; this op adds NO new transport — it names the diagnostic READ of an existing building watch"}
```
This op does not own a stream; it is the diagnostic READING of [[session#op: session.watch]] /
[[headless-control#op: headless-control.watch]]. The frame schema, resume mechanism (Last-Event-ID /
`since=`), keepalive, and termination are owned ONCE by [[events#op: events.watch]] — read them there.
A turn that exceeds `turn_timeout_s` is killed by the supervisor (`runtime/session_supervisor.py:478`)
and surfaces as a turn-timeout failure; an underlying `claude -p` `is_error` result surfaces as a
turn-error. The cost/usage fields of the result event are now CAPTURED onto the agent_sessions.turn event
(CC-20, [[cost-usage]]) — diagnostics sees the failure AND the spend.
```contract:example
captured: synthetic            # status=building — replaced by captured evidence at flip-to-live (V11)
binding: http
request: |
  GET /watch?session=session://a3f9&since=-1 HTTP/1.1
response: |
  {"seq": 42, "type": "agent_sessions.turn", "session": "session://a3f9", "is_error": true,
   "detail": "tool refused under plan mode: Edit routed to canUseTool"}
  {"seq": 43, "type": "agent_sessions.idle", "session": "session://a3f9"}
```
Adjacent: [[session#op: session.watch]] (the same stream, session lens), [[events#op: events.watch]]
(the SSE mechanics owner), [[headless-control#op: headless-control.watch]] (the stream-json fold),
[[diagnostics#op: diagnostics.get]] (the health summary the failures roll up into).

## op: diagnostics.act
**`diagnostics.act` is the PLANNED single-session diagnostic steer: run `/doctor` against a session,
thread `--debug` categories, or spawn under `--safe-mode`/`--bare` for troubleshooting — native levers
that inspect a `claude` process the company spawns headlessly without them, named here so a UI builds
toward the real seam rather than a fiction.**
```contract:op
op: diagnostics.act
resource: diagnostics
kind: act
status: building
direction: outbound
atlas: [CC-33.3, CC-33.4]
tasks:
  - phrase: "run a health check on a specific session"
    params: {act: doctor}
  - phrase: "spawn a session with debug logging for the api and hooks"
    params: {act: set-debug, filter: "api,hooks"}
  - phrase: "spawn a clean session with no customizations to isolate a problem"
    params: {act: safe-mode}
  - alias: "enable debug mode"
  - alias: "troubleshoot a session"
  - alias: "safe mode"
bindings:
  - { kind: http, method: POST, path: "/spawn  (debug → --debug [categories], safe_mode → --safe-mode, bare → --bare on the body)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: building, note: "BUILT (CC-33.4; runtime/session_supervisor.py _build_spawn_cmd + /spawn body, 2026-06-12): `debug` (string filter or true) threads --debug [categories], `safe_mode` threads --safe-mode, `bare` threads --bare (all Atlas-verified flags). WARNING preserved in the cmd-builder semantics: --bare skips the MCP/keychain/CLAUDE.md the fabric depends on (it would break mcp__company access) — bare is for isolation only, the caller owns that choice. live-verify pending (lead): a real spawn must confirm the debug stream/safe-mode took — built+unit-tested on the cmd-builder, NOT flipped live" }
  - { kind: cli, command: "/doctor   (HOST interactive command; inspects the host install, not a fabric session)", transport: cli-local, exposure: "n/a — Claude Code built-in", status: planned, note: "GAP + scope: /doctor is interactive-host only; it has no headless form the supervisor can invoke per-session. A per-session health object would be net-new company work" }
liveness: none
emits: []
consequences:
  - when: "debug/safe-mode/bare set at spawn (BUILT; /doctor still planned)"
    expect: [agent_sessions.spawned]
    bound: "the spawn's own bound ([[session#op: session.create]]); debug output rides the session's stderr/stream — NOT a distinct fabric event. live-verify pending (lead)"
    evidence: "[[diagnostics#op: diagnostics.watch]] — the debug stream and resolved tool surface are observed on the existing watch; a real spawn confirms the debug categories/safe-mode took (an absence-of-dedicated-event outcome, CONTRACT-FORMAT section 6 V9)"
correlate: [session]
verification:
  doctor-per-session: {state: unverified, note: "STILL planned (CC-33.3): /doctor has no headless form; a per-session health object is net-new company work"}
  set-debug:          {state: probe-verified, run: "session_supervisor_params_acceptance (cmd-builder: debug string→--debug <categories>, debug=true→bare --debug)", date: 2026-06-12, note: "BUILT (CC-33.4): a `debug` filter threads --debug [categories]; unit-proven on the built cmd. live-verify pending (lead): a REAL spawn must confirm the debug stream emits — NOT flipped live"}
  safe-mode:          {state: probe-verified, run: "session_supervisor_params_acceptance (cmd-builder: safe_mode→--safe-mode, bare→--bare)", date: 2026-06-12, note: "BUILT (CC-33.4): safe_mode→--safe-mode, bare→--bare; unit-proven. --bare still BREAKS mcp__company by design (isolation-only). live-verify pending (lead): a real spawn must confirm the isolation took"}
```
### Description (purpose-free)
Three planned diagnostic levers the native CLI supports and the company does not thread. (1) `/doctor`
runs a one-pass health check (install integrity, settings-file validity, MCP reachability, context
usage, keybinding warnings) — interactive-host only, no headless form, so a per-session version is
net-new company work. (2) `--debug [filter]` enables category-filtered debug logging (e.g. `api,hooks`,
or exclusions `!1p,!file`) with `--debug-file <path>` to redirect it. (3) `--safe-mode` disables ALL
customizations (CLAUDE.md, skills, plugins, hooks, MCP, agents, output styles, keybindings) and
`--bare` is a minimal mode skipping hooks/LSP/plugins/CLAUDE.md/keychain — both for isolating a
problem, but `--bare` would strip the `mcp__company` tool the fabric relies on, so it is
isolation-only. Source: https://code.claude.com/docs/en/cli-reference.md, troubleshooting.md.
### Request (PLANNED shape)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/diagnostics.act.request",
  "type": "object",
  "required": ["session", "act"],
  "properties": {
    "session": { "type": "string", "description": "session://<id> being spawned or inspected" },
    "act":     { "enum": ["doctor", "set-debug", "safe-mode", "bare"] },
    "filter":  { "type": "string", "description": "debug category filter for set-debug, e.g. 'api,hooks' or '!1p,!file'" },
    "debug_file": { "type": "string", "description": "optional path to redirect debug output" } },
  "additionalProperties": false }
```
### Interaction semantics
- **`--bare` breaks the fabric** — it skips MCP/keychain/CLAUDE.md, removing `mcp__company`; never use
  it for a working fabric session, only to isolate whether a customization causes a fault.
- **`--debug` is verbose** — category filters keep the stream usable; the fabric already passes
  `--verbose`, so debug adds category-level detail, not the only output.
- **`/doctor` is host-scoped** — even if surfaced, it would report the host install's health, not a
  headless subprocess's; a true per-session health object is a design question, not a flag.
### Errors
```contract:error
code: diagnostics.not-exposed | http: 501 | retryable: false
when: a per-session /doctor health check is requested (CC-33.3 — the residual not-built lever)
teach: "Per-session --debug/--safe-mode/--bare are now BUILT (the /spawn body threads them). A per-session /doctor is still PLANNED — it has no headless form, so a per-session health object is net-new company work. For fabric health use [[diagnostics#op: diagnostics.get]] (GET /health); for session failures watch [[diagnostics#op: diagnostics.watch]]; on the host, the operator runs the interactive /doctor."
```
```contract:error
code: diagnostics.supervisor-down | http: 503 | retryable: true
when: GET /health connection refused (the supervisor process is not running)
teach: "The session-supervisor is down. Start it with `company up session-supervisor`. This is the failure [[diagnostics#op: diagnostics.get]] is designed to detect — a refused connection to 127.0.0.1:8771, not a 5xx body."
```
```contract:example
captured: synthetic            # status=building, live-verify pending (lead): the spawn ACCEPTS debug/safe_mode/bare (cmd-builder unit-proven → --debug/--safe-mode/--bare); a REAL spawn confirming the debug stream emits is the lead's live-verify, so synthetic-and-loud, NOT captured-live (V11)
binding: http
request: |
  POST /spawn HTTP/1.1
  {"cwd": "/home/tim/scratch", "name": "debug-1", "debug": "api,hooks"}
response: |
  HTTP/1.1 200 OK
  {"ok": true, "session": {"id": "as-3c4d5e6f", "name": "debug-1", "state": "starting"}}
  # built (CC-33.4): the body threads --debug api,hooks onto the spawn cmd (safe_mode→--safe-mode, bare→--bare likewise).
  # a per-session /doctor (CC-33.3) is the unbuilt residual; run /doctor on the host for install health.
  # live-verify pending (lead): confirm the debug categories actually stream on a real session.
```
Adjacent: [[diagnostics#op: diagnostics.get]] (fabric health), [[diagnostics#op: diagnostics.watch]]
(session failures), [[session#op: session.create]] (the spawn this would extend), [[settings#op:
settings.get]] (settings validity, which /doctor checks), [[surfaces#op: surfaces.get-keybindings]]
(keybinding warnings /doctor reports).

## Errors
**Resource-level error vocabulary: `diagnostics.not-exposed` (the honest 501 for the residual
per-session /doctor — --debug/--safe-mode/--bare are now built), `diagnostics.supervisor-down` (the 503/refused-connection the health read
is built to detect, teaching `company up`).** Both teach the in-corpus recovery: the live health read,
the failure stream, and the host /doctor for install-level health. No error implies a per-session
/doctor the company does not have.

## Links
**No address-typed fields of its own: a diagnostic references the `session://` it inspects
(dereferences to [[session]]) and the event surface its failures ride ([[events]]); it points at
[[fabric-config]] (the health field set), [[settings]] (settings validity), [[surfaces]] (keybinding
warnings), [[platform]] (install integrity + telemetry), and [[cost-usage]] (the per-turn usage
fields, now captured onto agent_sessions.turn).** Debug category names, /doctor check names, and telemetry signal names are Claude Code
identifiers (https://code.claude.com/docs/en/troubleshooting.md, monitoring-usage.md), not fabric
addresses — they never resolve to a corpus entry, by design.
