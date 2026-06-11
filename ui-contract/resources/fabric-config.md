---
type: contract-entry
resource: fabric-config
summary: The fabric's live operating posture — concurrency cap, per-turn wall-clock, permission mode, bind — read from the supervisor's health surface; changed by env + restart, raising the cap is a recorded decision.
schemes: []
status: building
relates-to: ["[[session]]", "[[events]]"]
---

# Resource: fabric-config

## Identity
**There is exactly ONE fabric-config: the supervisor service's call-time posture; no id, no
collection — `get` is the whole resource.**

## Representation
**The config read returns the four laws a consumer must respect before acting: the cap
(spawns + consult fans), the enforced turn timeout (the watchdog's ceiling), the permission
posture of spawned sessions, and the literal bind.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/fabric-config.record",
  "type": "object",
  "required": ["ok", "service", "bind", "sessions", "cap", "turn_timeout_s", "permission"],
  "properties": {
    "ok":             { "const": true },
    "service":        { "const": "session-supervisor" },
    "bind":           { "const": "127.0.0.1", "description": "the exposure law: no env var widens this; wider = recorded decision + code change" },
    "sessions":       { "type": "object", "properties": { "total": {"type": "integer"}, "by_state": {"type": "object"} } },
    "cap":            { "type": "integer", "description": "COMPANY_FABRIC_CONCURRENCY (call-time env read; default 3)" },
    "turn_timeout_s": { "type": "number", "description": "COMPANY_FABRIC_TURN_TIMEOUT_S (call-time; default 900) — the watchdog REAPS past it" },
    "permission":     { "type": "string", "description": "COMPANY_FABRIC_PERMISSION (default plan = read-only; acceptEdits is opt-in only)" } } }
```
| field | volatile? | changed-by | reality |
|---|---|---|---|
| cap / turn_timeout_s / permission | yes (env, call-time read) | NO event — env flip is honoured without restart; the REGISTRY-SERVED default is a flagged, recorded seam (registry-is-truth) still riding env defaults | defaults 3 / 900 / plan — read them, never assume |
| sessions.by_state | yes | the supervisor's process states (starting/idle/busy/closed) — supervisor grain, not the registry fsm | live counter |

## State model
**State model: stateless.**

## Caller
**Anonymous-local read; changing the posture is the OPERATOR's act (env on the service /
`company up`), deliberately not an op on any face — there is no fabric-config.update and
that absence is the contract.**

## Operations

## op: fabric-config.get
**`fabric-config.get` is the pre-flight read: the cap your consult fan must fit, the timeout
your long turn must beat, the permission mode your spawned session will run under — read it
via the health door rather than hardcoding any number.**
```contract:op
op: fabric-config.get
resource: fabric-config
kind: get
status: building
direction: outbound
atlas: [CC-25.1]
tasks:
  - phrase: "what is the fabric's concurrency cap"
  - phrase: "is the session supervisor up, and under what posture"
  - alias: "fabric health"
  - alias: "check the cap before fanning out"
bindings:
  - { kind: http, method: GET, path: /health, transport: supervisor-http, exposure: "exposure.json#supervisor-http" }
  - { kind: cli, command: "company status   (the session-supervisor row: up/down)", transport: cli-local, exposure: "exposure.json#cli-local" }
liveness: snapshot
live-twin: "none — static between env changes; liveness of SESSIONS is [[events#op: events.watch]]"
emits: []
verification:
  health-read: {state: probe-verified, run: session_supervisor_acceptance §1 (200 + bind + cap asserted), date: 2026-06-12}
```
```contract:example
captured: synthetic
binding: http
request: |
  GET /health HTTP/1.1
response: |
  HTTP/1.1 200 OK
  {"ok": true, "service": "session-supervisor", "bind": "127.0.0.1",
   "sessions": {"total": 3, "by_state": {"idle": 2, "busy": 1}},
   "cap": 3, "turn_timeout_s": 900.0, "permission": "plan"}
```
A connection refusal IS the down-signal (teach: `company up session-supervisor`) — there is
no degraded 200.
Adjacent: [[session#op: session.create]] / [[session#op: session.post]] (the ops the cap
governs), [[session#op: session.stop]] (how a slot frees).

## Errors
**No error vocabulary beyond transport failure: the read either answers whole or the service
is down — and down is loud (refused connection), never a stale or partial answer.**

## Links
**`sessions.by_state` keys are the SUPERVISOR-grain states (see [[session#Representation]]);
nothing here is address-typed.**
