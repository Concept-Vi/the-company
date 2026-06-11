---
type: contract-entry
resource: headless-control
summary: The stream-json/SDK control protocol that drives a programmatic Claude Code session — the event stream a consumer reads (system/init, assistant deltas, tool_use, result, system/api_retry) and the control requests it writes (a user turn, an interrupt); the company's supervisor SPEAKS this protocol internally and exposes a slice of it through its own faces.
schemes: []
status: building
relates-to: ["[[session]]", "[[events]]", "[[permission]]", "[[model]]", "[[agent-team]]"]
---

# Resource: headless-control

## Identity
**Headless control is the protocol layer of a programmatic (`claude -p`) session: the
machine-readable EVENT stream Claude Code emits and the CONTROL frames a parent process writes —
keyed by the session it drives (`session://<id>`), with no scheme of its own.** The native form is
`claude -p --input-format stream-json --output-format stream-json` (a bidirectional supervisor;
https://code.claude.com/docs/en/headless.md). The company's session supervisor IS exactly such a
supervisor (`runtime/session_supervisor.py` spawns `claude -p --input-format stream-json
--output-format stream-json --verbose` at `:261-262` and parses the stream at `:312-354`), so this
resource is NOT a fiction — it is the contract for the protocol the fabric already runs, with each op
marked for whether the company RE-EXPOSES that slice to consumers (building) or keeps it internal
(the gap named).

## Representation
**The stream is a sequence of typed JSON events (one per line); the company's supervisor folds the
native shapes into its OWN coarser per-session frame vocabulary AND into the durable
`agent_sessions.*` event log — three distinct vocabularies a consumer must not conflate.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/headless-control.stream-event",
  "type": "object",
  "required": ["type"],
  "description": "the NATIVE claude -p --output-format stream-json line shapes (source https://code.claude.com/docs/en/headless.md). The company supervisor consumes these; consumers see the FOLDED forms unless they read a raw stream.",
  "properties": {
    "type": { "enum": ["system", "assistant", "user", "result", "stream_event"],
              "description": "system carries subtypes (init, api_retry, plugin_install); stream_event carries partial-message deltas under --include-partial-messages" },
    "subtype": { "type": "string", "description": "init | api_retry | plugin_install (on type=system)" },
    "session_id": { "type": "string", "description": "the claude session uuid — the supervisor maps it to its as-<hex> handle ([[session#Identity]])" },
    "model": { "type": "string", "description": "on system/init: the resolved model — the observation [[model]] points at" },
    "tools": { "type": "array", "items": { "type": "string" }, "description": "on system/init: the resolved tool surface — the observation [[permission]] points at" },
    "result": { "type": "string", "description": "on type=result: the final turn text" },
    "is_error": { "type": "boolean", "description": "on type=result: a refusal/error turn (e.g. a content-flagged Fable5 turn in non-interactive mode)" },
    "total_cost_usd": { "type": "number", "description": "on the JSON result of --output-format json: per-invocation cost (CC-20 telemetry seam)" } } }
```
| native event | carries | company fold (what a consumer actually sees) |
|---|---|---|
| system/init | session_id, model, tools, mcp_servers, plugins | supervisor mints the `init` per-session frame (`:331`, only claude_session_id) AND emits durable `agent_sessions.registered` (`:338`). The FULL init (model/tools) is parsed but NOT re-surfaced — the [[permission]]/[[model]] observation gap |
| assistant (text block) | streaming assistant text | folded to the `text` per-session frame ([[session#op: session.watch]] `:346`) |
| assistant (tool_use block) | tool name + input | folded to the one-line `tool` frame (name + key arg, `:351`) |
| result | result text, num_turns, is_error, duration | folded to the `done` per-session frame AND the durable `agent_sessions.turn` event (`:353`->_turn_done) |
| system/api_retry | attempt, max_retries, retry_delay_ms, error category | NOT folded — the supervisor's reader ignores non-result chatter (`:323`); a consumer cannot see retry progress through a company face today |
| stream_event (partial) | text_delta tokens (needs --include-partial-messages) | NOT requested by the supervisor spawn (no --include-partial-messages, `:261`) — token-level streaming is internal-unavailable; the `text` frame is per-block, not per-token |

## State model
**State model: stateless (a protocol view).** The control protocol has no lifecycle of its own; it
drives a [[session]], whose lifecycle (starting/idle/busy/closed at supervisor grain;
supervised-live/unsupervised-live/closed at registry grain) is owned there ([[session#State model]]).
The stream simply ends at EOF when the process exits (the supervisor reads it to EOF then marks the
session closed, `:357-359`).

## Caller
**Driving the native protocol is the PARENT PROCESS holding the session's stdin/stdout (the
supervisor IS that parent — consumers never get the raw pipe); observing the folded streams is
anonymous-local over supervisor-http / bridge-http.** A consumer does NOT speak stream-json directly
to a fabric session — it goes through the supervisor's faces (inject/post to write a turn, watch to
read the folded stream). The raw protocol is documented here so a UI understands what the supervisor
is doing and what a future direct-control face would carry.

## Operations

## op: headless-control.watch
**`headless-control.watch` is the live per-session frame read: the supervisor's fold of one
session's native stream into ndjson frames (init/text/tool/injected/done/closed) — this op IS the
company's exposed slice of the control protocol's OUTPUT half, owned in mechanics by
[[session#op: session.watch]] and linked here so a CC-18 consumer finds it under the headless lens.**
```contract:op
op: headless-control.watch
resource: headless-control
kind: watch
status: building
direction: outbound
atlas: [CC-18.6]
tasks:
  - phrase: "read the machine-readable output stream of a programmatic session"
  - phrase: "observe a headless session's tool calls and text as JSON"
  - phrase: "what model and tools did a session resolve at init"
  - alias: "tail a headless session"
  - alias: "stream-json output"
bindings:
  - { kind: http, method: GET, path: "/watch?session=<id>", transport: supervisor-http, exposure: "exposure.json#supervisor-http", note: "the SAME endpoint as [[session#op: session.watch]] — this is its CC-18/headless retrieval lens, not a second endpoint. Frames are the FOLDED vocabulary, not the raw native stream-json" }
liveness: watch
frames: "ndjson, one JSON object per line: {seq, ts, session, type: init|text|tool|injected|interrupt_sent|done|closed, ...}; the native system/init's model+tools fields are PARSED by the supervisor but NOT carried in the folded `init` frame today (the observation gap [[permission]]/[[model]] cite)"
resume: "none — the connection replays buffered frames (<=500) then streams; no cross-connection cursor (same as [[session#op: session.watch]])"
keepalive: "{\"type\":\"keepalive\"} every ~15s of silence"
termination: "ends after the closed frame or on client disconnect"
emits: []
verification:
  folded-stream: {state: probe-verified, run: "session_supervisor_acceptance (subscriber fan) — the same proof as [[session#op: session.watch]]", date: 2026-06-12, note: "the FOLDED frames are proven; raw-native-passthrough is NOT exposed"}
```
This op is [[session#op: session.watch]] under the headless lens — same wire, same frame vocabulary,
owned-once there. For the FABRIC-WIDE durable event stream (the proof stream for writes) use
[[events#op: events.watch]] (SSE). HONEST GAP: the native `system/api_retry` and partial-message
token deltas are NOT in the folded frames (the supervisor neither requests `--include-partial-messages`
nor folds retries) — a consumer wanting token-level streaming or retry progress is reaching for an
unexposed slice; record it as a drop ([[README]] step 7).
Adjacent: [[session#op: session.watch]] (the owning op), [[events#op: events.watch]] (fabric-wide),
[[headless-control#op: headless-control.act]] (writing a turn / interrupt).

## op: headless-control.act
**`headless-control.act` is the control-INPUT half: write a user turn into a held-open session and
interrupt an in-flight turn — the native stream-json input frames + control_request the supervisor
already implements and RE-EXPOSES as [[session#op: session.inject]] / [[session#op: session.interrupt]];
the richer native control surface (output-format selection, structured-output schema, partial
streaming) is planned, with the spawn-flag gaps named.**
```contract:op
op: headless-control.act
resource: headless-control
kind: act
status: building
direction: outbound
atlas: [CC-18.2, CC-18.3, CC-18.7]
tasks:
  - phrase: "push a turn into a programmatic session via stdin"
    params: {act: turn}
  - phrase: "interrupt a headless session's current turn"
    params: {act: interrupt}
  - phrase: "ask a headless session for structured JSON output"
    params: {act: set-output, output_format: json}
  - alias: "send stream-json input"
  - alias: "control a headless session"
bindings:
  - { kind: http, method: POST, path: /inject, transport: supervisor-http, exposure: "exposure.json#supervisor-http", note: "the EXPOSED control-input: a user turn written to the held-open stdin. Owned by [[session#op: session.inject]] — this is its CC-18 lens" }
  - { kind: http, method: POST, path: /interrupt, transport: supervisor-http, exposure: "exposure.json#supervisor-http", note: "the EXPOSED interrupt: a control_request to stdin. Owned by [[session#op: session.interrupt]] — honestly UNPROVEN against a real turn (stub subprocesses ignore it)" }
  - { kind: http, method: POST, path: "/spawn  (PLANNED: output_format/json_schema/include_partial on the body)", transport: supervisor-http, exposure: "exposure.json#supervisor-http", status: planned, note: "GAP: the supervisor hardcodes --output-format stream-json --verbose (runtime/session_supervisor.py:262) and requests NO --include-partial-messages, NO --json-schema. A consumer cannot choose json-result, structured-output, or token streaming. Native flags exist; the spawn does not carry them" }
liveness: none
emits: []
consequences:
  - when: "turn written (act=turn, target idle) — EXPOSED via inject"
    expect: [agent_sessions.turn, agent_sessions.idle]
    bound: "turn <= COMPANY_FABRIC_TURN_TIMEOUT_S; the watchdog reaps silent hangs ([[fabric-config]])"
    evidence: "[[session#op: session.watch]] text/done frames; [[events#op: events.list]] the durable turn event"
  - when: "interrupt written (act=interrupt) — EXPOSED via interrupt"
    expect: [agent_sessions.turn]
    bound: "unbounded-with-evidence: an interrupt_sent frame appears immediately on the per-session watch; the turn event closes when claude yields. UNPROVEN against a real turn (stub ignores control_request)"
    evidence: "[[session#op: session.watch]] interrupt_sent frame; the watchdog reap (closed, reason names it) is the guaranteed ceiling"
  - when: "output-format/structured-output selection (act=set-output) — PLANNED"
    expect: []
    bound: "n/a — not built"
    evidence: "no company-visible outcome; the spawn-flag gap is the contract (named in bindings)"
correlate: [session]
verification:
  turn-write:    {state: probe-verified, run: "session_supervisor_acceptance section 4 (inject -> turn -> idle)", date: 2026-06-12, note: "the EXPOSED control-input slice; full identity is [[session#op: session.inject]]"}
  interrupt:     {state: unverified, note: "real-claude interrupt unproven — stubs ignore control_request; see [[session#op: session.interrupt]]"}
  output-select: {state: unverified, note: "no spawn output-format param — planned"}
```
### Description (purpose-free)
The control-INPUT half of the headless protocol, split by what the company exposes. EXPOSED
(building): write a user turn to a held-open session (native stream-json input -> the supervisor's
[[session#op: session.inject]]) and write an interrupt control_request
([[session#op: session.interrupt]], unproven against a real turn). PLANNED: the native output
controls a consumer cannot reach because the supervisor hardcodes them — `--output-format`
(text/json/stream-json), `--json-schema` for structured output (the result's `structured_output`
field), `--include-partial-messages` for token deltas, `--bare` for deterministic context. A
consumer choosing the shape of a programmatic run is reaching for these planned spawn flags. Native
reference: https://code.claude.com/docs/en/headless.md.
### Request (the EXPOSED turn/interrupt + the PLANNED output controls)
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/headless-control.act.request",
  "type": "object",
  "required": ["session", "act"],
  "properties": {
    "session":       { "type": "string", "description": "session://<id> (supervised-live for turn/interrupt)" },
    "act":           { "enum": ["turn", "interrupt", "set-output"], "description": "turn+interrupt are EXPOSED via inject/interrupt; set-output is PLANNED" },
    "message":       { "type": "string", "description": "act=turn: the user turn text" },
    "output_format": { "enum": ["text", "json", "stream-json"], "description": "PLANNED: only stream-json is used today (hardcoded)" },
    "json_schema":   { "type": "object", "description": "PLANNED: a JSON Schema for structured output (--json-schema); result carries structured_output" },
    "include_partial": { "type": "boolean", "description": "PLANNED: token-level deltas (--include-partial-messages); not requested today" } },
  "additionalProperties": false }
```
### Interaction semantics
- **stdin write semantics** (EXPOSED): a turn is written to the held-open child stdin; a busy target
  refuses (409, "wait for idle / interrupt / queue via mailbox") — unlike [[session#op: session.post]],
  inject mails NOTHING, so the reply is observable only on the stream, not durable. Choose
  [[session#op: session.post]] verb=deliver for a durable, reply-bearing turn.
- **interrupt** (EXPOSED, unproven): writes a control_request; honoured only by a real claude turn
  (stubs ignore it). The watchdog timeout is the guaranteed backstop.
- **output-format** (PLANNED): the native default for `-p` is `text`; `json` adds session_id +
  `total_cost_usd` + a per-model cost breakdown (the CC-20 cost seam); `stream-json` is the per-line
  event stream the supervisor uses. A flagged content turn in non-interactive mode ENDS with a
  refusal `result` (`is_error`), not a prompt — see [[model#op: model.act]].
- **--bare** (PLANNED): skips auto-discovery of hooks/skills/plugins/MCP/CLAUDE.md for deterministic
  scripted runs; the fabric does NOT use it (it loads the strict company MCP config explicitly).
### Errors
```contract:error
code: headless-control.session-busy | http: 409 | retryable: true
when: act=turn against a busy supervised session
teach: "Wait for idle, interrupt the current turn ([[session#op: session.interrupt]]), or use the durable mailbox ([[session#op: session.post]] verb=deliver, which the supervisor retries until idle). A refusal after a passed idle pre-check is expected concurrency — pass-via-refusal."
```
```contract:error
code: headless-control.output-not-selectable | http: 501 | retryable: false
when: act=set-output (any output-format/structured-output/partial-streaming selection)
teach: "Output-format selection is PLANNED — the supervisor hardcodes --output-format stream-json --verbose and folds it to ndjson frames ([[headless-control#op: headless-control.watch]]). For one-shot structured output today, an operator runs claude -p --output-format json --json-schema directly, outside the fabric."
```
Plus `session.unknown` (the registry's 404 teach, as on [[session#op: session.get]]).
```contract:example
captured: synthetic            # status=building for turn/interrupt; set-output is planned (V11)
binding: http
request: |
  POST /inject HTTP/1.1
  Content-Type: application/json
  {"session": "as-91cf4502", "message": "run the test suite and summarize failures"}
response: |
  HTTP/1.1 200 OK
  {"ok": true, "session": "as-91cf4502", "state": "busy"}
```
Adjacent: [[session#op: session.inject]] (the owning turn op), [[session#op: session.interrupt]]
(the owning interrupt op), [[headless-control#op: headless-control.watch]] (the output half),
[[model#op: model.act]] (output-format interacts with content-flagged refusals).

## Errors
**Resource-level error vocabulary: `headless-control.session-busy` (the EXPOSED turn's concurrency
refusal) and `headless-control.output-not-selectable` (the honest 501 for the planned output
controls); the unknown-session 404 is inherited from [[session]].** Every refusal names the live
recovery — wait/interrupt/mailbox for busy, the direct `claude -p` path for output selection. No
error claims a control slice the supervisor does not run.

## Links
**Address-typed fields: `session` everywhere is a `session://` id dereferencing to [[session]] via
its accepting ops; the stream's `session_id` is the claude uuid the supervisor maps to its handle.**
The folded frames and native events are NOT addressable records (they are stream items, read by
watching, never dereferenced) — consistent with [[events#Links]]. The CC-20 `total_cost_usd` seam on
the planned json output is a telemetry hook, not an address.
