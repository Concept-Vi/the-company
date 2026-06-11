---
type: contract-entry
resource: events
summary: The fabric's fact stream — the closed agent_sessions.* event catalog on the shared durable log, single-writer, seq-cursored; every write op's proof rides here.
schemes: []
status: building
relates-to: ["[[session]]", "[[session-message]]", "[[fabric-config]]"]
---

# Resource: events

## Identity
**An event is identified by its log `seq` (the global cursor over the shared events log);
event TYPES are the closed set below — a kind outside it is not a fabric event.** The
single-writer law is the identity guarantee: ONLY the supervisor service emits
`agent_sessions.*`; the MCP face and bridge write mail, never fabric events. Heartbeats are
deliberately excluded from this log (supervisor-local; retention ruling N8).

## Representation
**The catalog: six event kinds, each named with its payload reality and the state transition
it keys — `turn` carries the correlation key (`intent_id`); `thread` does NOT ride events yet
(an honest, recorded gap: reply aggregation joins on the MAILBOX thread instead).**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/events.record",
  "type": "object",
  "required": ["kind", "seq", "ts", "summary"],
  "properties": {
    "kind":    { "enum": ["agent_sessions.registered", "agent_sessions.spawned",
                          "agent_sessions.turn", "agent_sessions.idle",
                          "agent_sessions.closed", "agent_sessions.adopted"] },
    "seq":     { "type": "integer" },
    "ts":      { "type": "string", "format": "date-time" },
    "summary": { "type": "string" },
    "session": { "type": "string", "description": "supervisor handle (as-…) — canonicalized to the claude uuid by the registry fold via claude_session_id/resume" },
    "claude_session_id": { "type": ["string", "null"] },
    "state":   { "enum": ["supervised-live", "unsupervised-live", "closed"], "description": "optional explicit override of the kind's default transition" } } }
```
| kind | payload (beyond the base) | transition | emitter reality (2026-06-12) |
|---|---|---|---|
| spawned | name, cwd, resume, fork, source, pid | → supervised-live | EMITTED (durable claim) — run-proven |
| turn | claude_session_id, name, duration_ms, is_error, source, **intent_id** | none (activity) | EMITTED (durable claim) — run-proven |
| idle | claude_session_id, name | none (activity) | EMITTED (narration class) — run-proven |
| closed | claude_session_id, name, reason (teardown / exited rc=… / watchdog-timeout …) | → closed | EMITTED (durable claim) — run-proven |
| registered | name?, cwd?, title? | → unsupervised-live | DECLARED, **no emitter yet** — a session announcing itself is a built-vocabulary/unbuilt-writer honest split |
| adopted | name?, cwd? | → supervised-live | DECLARED, **no emitter yet** (supervisor takeover of an existing session) |

## State model
**State model: stateless.** (Events ARE the transition keys of [[session#State model]];
the log itself only ever appends.)

## Caller
**Reading the stream requires no identity on any transport — facts are facts; your position
in them is your own cursor (`since` / `Last-Event-ID`).**

## Operations

## op: events.list
**`events.list` is the poll-shaped fabric read: `agent_sessions.*` events after your event-seq
cursor, optionally narrowed to one session — the write-proof read every post/inject/stop
verifies against.**
```contract:op
op: events.list
resource: events
kind: list
status: building
direction: outbound
atlas: [CC-18.5]
tasks:
  - phrase: "what happened in the fabric since my cursor"
  - phrase: "did my message cause a turn"
    params: {since: "<your posted seq context>", session: "<target>"}
  - alias: "poll fabric events"
bindings:
  - { kind: mcp, tool: sessions, op-param: "op=watch", server: company, exposure: "exposure.json#mcp-company" }
  - { kind: http, method: GET, path: /api/events, transport: bridge-http, exposure: "exposure.json#bridge-http", note: "the bridge's last-60 snapshot carries ALL event kinds — filter kind by prefix client-side; the MCP binding pre-filters to agent_sessions.*" }
liveness: snapshot
live-twin: "[[events#op: events.watch]]"
emits: []
verification:
  filtered-poll: {state: probe-verified, run: "agent_sessions_mailbox_acceptance (watch op: only agent_sessions.*, honest cursor)", date: 2026-06-12}
```
MCP request: `sessions(op="watch", since=-1, session="", limit=50, detail=)`. Response:
`{op, session, total, since, next_since, detail, events, note}` — pagination never skips
(cursor = last returned seq when truncated, the log tail when drained). An empty result with
the supervisor down is HONEST SILENCE, not absence of sessions ([[session#op: session.list]]
shows those) — the note field says exactly this.
```contract:example
captured: synthetic
binding: mcp
request: sessions(op="watch", since=18204, session="session://a3f9…")
response: { "op": "watch", "session": "session://a3f9…", "total": 2, "since": 18204,
            "next_since": 18215, "detail": "concise",
            "events": [ { "kind": "agent_sessions.spawned", "session": "as-b1c2d3e4", "state": null,
                          "seq": 18205, "ts": "2026-06-12T…", "summary": "consult-a3f9-1 · fork of a3f9…" },
                        { "kind": "agent_sessions.turn", "session": "as-b1c2d3e4", "state": null,
                          "seq": 18215, "ts": "2026-06-12T…", "summary": "consult-a3f9-1 · turn 1 done" } ],
            "note": "agent_sessions.* events are emitted ONLY by the supervisor service (single-writer law) — an empty result with the supervisor down is honest silence, not absence of sessions (op='list' shows those)." }
```
Adjacent: [[events#op: events.watch]] for push; [[session#op: session.post]] is the act
this read proves.

## op: events.watch
**`events.watch` is the fabric's push stream: the bridge's SSE endpoint with `id:<seq>`
frames, `Last-Event-ID` resume and ~15s keepalive — live-ness is marked HERE and only here;
the snapshot read is its twin, never its substitute.**
```contract:op
op: events.watch
resource: events
kind: watch
status: building
direction: outbound
atlas: [CC-18.5, CC-08.5]
tasks:
  - phrase: "stream fabric events live"
  - alias: "subscribe to the event stream"
bindings:
  - { kind: http, method: GET, path: /api/stream, transport: bridge-http, exposure: "exposure.json#bridge-http", note: "carries ALL store events — filter kind: agent_sessions.* client-side" }
liveness: watch
frames: "SSE: `id:<seq>` + `data:<event json>` per event (the events.record schema)"
resume: "Last-Event-ID header (or reconnect and read the gap via [[events#op: events.list]] with since=)"
keepalive: "~15s comment frames"
termination: "server keeps the stream open; client disconnect ends it — no terminal frame"
emits: []
verification:
  sse-mechanics: {state: probe-verified, run: "the bridge's standing SSE surface (pre-F1, in production use by the harness UI); fabric-event frames over it UNVERIFIED until the supervisor runs beside it end-to-end (lead's slice)", date: 2026-06-12}
```
This op owns the SSE mechanics ONCE — other entries link here and never restate them
(CONTRACT-FORMAT §10 C-C5). Per-session, supervisor-grain frames (text/tool/done) are a
DIFFERENT stream: [[session#op: session.watch]].
Adjacent: [[events#op: events.list]] (snapshot twin), [[session#op: session.watch]]
(one session, finer frames).

## Errors
**The stream's failure mode is absence, not refusal: a down supervisor means no
`agent_sessions.*` frames — declared honest silence in every read's note — and a down bridge
is a connection error, never a silent empty 200.**

## Links
**Every event's `session` field is a `session://`-class id (handle or uuid) dereferencing to
[[session]]; `intent_id` on turn events joins [[session-message]] records by their `id`
field (plain string key — the read is `sessions(op='inbox', …)` filtered by thread, since
intent ids found here name the mailbox record that caused the turn).**
