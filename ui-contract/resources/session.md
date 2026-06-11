---
type: contract-entry
resource: session
summary: A Claude Code session under fabric management — every session this machine has run (1,065 backfilled + live ones), addressable, spawnable, messageable, watchable, stoppable.
schemes: ["session://"]
status: building
relates-to: ["[[session-message]]", "[[events]]", "[[transcript]]", "[[fabric-config]]"]
---

# Resource: session

## Identity
**A session is identified by `session://<id>` where `<id>` is canonically the Claude session
uuid; ids come from the registry (`session.list`), never guessed.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/session.address",
  "type": "string",
  "pattern": "^(session://)?([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}|as-[0-9a-f]{8})$",
  "description": "uuid = the canonical registry key. as-<8hex> = a supervisor-local handle minted before init names the uuid (accepted by supervisor-http ops; registry rows migrate onto the uuid at first contact)." }
```
Ops accepting `session://` as input: `session.get`, `session.post`, `session.inject`,
`session.interrupt`, `session.stop`, `session.watch`, `session-message.list`. Bare ids and
`session://`-prefixed forms are both accepted everywhere (normalized server-side).

## Representation
**A registry row carries identity + liveness for one session; `session.get` joins it with the
durable record's envelope — and a SECOND, finer state vocabulary (the supervisor's
process-grain `starting|idle|busy|closed`) rides supervisor-http responses, distinct from the
registry fsm by design.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/session.record",
  "type": "object",
  "required": ["id"],
  "properties": {
    "id":            { "type": "string" },
    "name":          { "type": ["string", "null"] },
    "cwd":           { "type": ["string", "null"] },
    "state":         { "enum": ["supervised-live", "unsupervised-live", "closed", null] },
    "last_activity": { "type": ["string", "null"], "format": "date-time" },
    "title":         { "type": ["string", "null"] },
    "title_source":  { "enum": ["ai-title", "custom-title", "last-prompt", "first-user-turn", "untitled-envelope", null] },
    "started":       { "type": ["string", "null"], "format": "date-time" },
    "summarizer":    { "type": "boolean" },
    "seq":           { "type": ["integer", "null"], "description": "last folded event seq — a since-cursor" },
    "git_branch":    { "type": ["string", "null"] },
    "cc_version":    { "type": ["string", "null"] },
    "project":       { "type": ["string", "null"] },
    "jsonl_path":    { "type": ["string", "null"] },
    "jsonl_bytes":   { "type": ["integer", "null"] },
    "turns":         { "type": ["integer", "null"] } } }
```
| field | type | volatile? | changed-by (event) | address? → resource | reality (measured 2026-06-12, 1,065 records) |
|---|---|---|---|---|---|
| id | string | no | — | session:// → session | 100% (uuid; the registry refuses no-id records) |
| state | enum | YES | agent_sessions.spawned/adopted → supervised-live · registered → unsupervised-live · closed → closed (stream: events.jsonl → watch op: [[events#op: events.watch]]) | — | 100%; whole backfilled catalog = closed |
| last_activity | iso | YES | every agent_sessions.* event's ts (same stream/watch) | — | 100% |
| title | string | rarely | record refresh (importer re-read on jsonl change — a NON-event path, stated honestly) or an event carrying `title` | — | 100% via the fallback chain: ai-title 35 (3.3%) · last-prompt 212 (19.9%) · first-user-turn 1 (0.1%) · untitled+envelope 817 (76.7%) — measured by `ops/agent_sessions_importer.py` backfill; NEVER assume ai-title presence |
| summarizer | bool | no | — | — | true on 772/1,065 (72.5%) — CC-internal one-shot summary sessions; filter them for any fleet-of-real-conversations view |
| name | string | sometimes | spawned/adopted events carrying `name` | — | null on backfilled rows; set on supervisor-spawned ones |

Supervisor-grain record (supervisor-http responses only): `{id (as-handle),
claude_session_id, name, cwd, state: starting|idle|busy|closed, resume, fork, created,
last_activity, turns, pid, close_reason}` — process truth, finer than and never to be
confused with the registry fsm below.

## State model
**Three registry states routed on by every verb: supervised-live (push reaches it),
unsupervised-live (pull-only), closed (wake-able) — transitions are keyed by `agent_sessions.*`
events and nothing else.**
```contract:fsm
states: [supervised-live, unsupervised-live, closed]
transitions:
  - { on: agent_sessions.spawned,    to: supervised-live }
  - { on: agent_sessions.adopted,    to: supervised-live }
  - { on: agent_sessions.registered, to: unsupervised-live }
  - { on: agent_sessions.closed,     to: closed }
  - { on: agent_sessions.turn,  to: null, note: "activity only — moves last_activity, never state" }
  - { on: agent_sessions.idle,  to: null, note: "activity only" }
legality:
  session.list:      [supervised-live, unsupervised-live, closed]
  session.get:       [supervised-live, unsupervised-live, closed]
  session.post:      { supervised-live: "deliver/auto/consult", unsupervised-live: "queue/auto/consult", closed: "wake/auto/consult", unknown: "queue/auto/consult — NOT deliverable" }
  session.inject:    [supervised-live]
  session.interrupt: [supervised-live]
  session.stop:      [supervised-live]
  session.watch:     [supervised-live]
  session.create:    "n/a — creates; refused only by the concurrency cap"
```

## Caller
**Identity on this resource is always EXPLICIT: the MCP face requires `from_session` on every
post (your reply path), supervisor-http callers are anonymous-local with a free-text `source`
self-label, and the CLI is the operator.** Per-transport identity models: [[TRANSPORTS]].
Replies route to whatever `from_session` you give — pass your own `session://<id>` or your
answers land in an inbox you must remember to read under that label.

## Operations

## op: session.list
**`session.list` is the fleet read: every registered session — the 1,065-session backfilled
catalog plus live ones — filtered by state/cwd/substring, newest-activity first, with the
fold's honesty counter (`fold_errors`) in every result.**
```contract:op
op: session.list
resource: session
kind: list
status: building
direction: outbound
atlas: [CC-08.1]
tasks:
  - phrase: "list every Claude Code session on this machine"
  - phrase: "find a session by title or directory"
    params: {q: "<substring>", cwd: "<exact path>"}
  - phrase: "which sessions are alive right now"
    params: {state: "supervised-live"}
  - alias: "show the fleet"
  - alias: "session catalog"
bindings:
  - { kind: mcp, tool: sessions, op-param: "op=list", server: company, exposure: "exposure.json#mcp-company" }
  - { kind: http, method: GET, path: /api/agent_sessions, transport: bridge-http, exposure: "exposure.json#bridge-http", status: planned }
liveness: snapshot
live-twin: "[[events#op: events.list]] with since= — rows move only when agent_sessions.* events fire"
emits: []
```
Request: `sessions(op="list", state="", cwd="", q="", since=-1, limit=50, detail="concise")` —
`state` must be a registry state (unknown values REFUSED with the teaching error, never a
fabricated filter); `q` substring-matches title+name+id; `since` is an event-seq cursor
(record-only rows carry seq=null and are excluded by it — honest: no event moved them).
Response: `{op, total, fold_errors, detail, sessions: [record…]}` (concise rows carry
id/name/state/title/cwd/last_activity; `detail="detailed"` returns full records).
`fold_errors > 0` = malformed fabric events were counted-not-hidden.
```contract:error
code: session.unknown-state | http: n/a (mcp tool error) | retryable: false
when: state filter not in the closed vocabulary
teach: "The registry's states are supervised-live (supervisor-owned, deliverable), unsupervised-live (alive, pull-only), closed (wake-able). Fix the filter and re-read via [[session#op: session.list]]; nothing is silently widened."
```
```contract:example
captured: synthetic            # status=building — replaced by captured evidence at flip-to-live (V11)
binding: mcp
request: sessions(op="list", q="vault", limit=2)
response: { "op": "list", "total": 7, "fold_errors": 0, "detail": "concise",
            "sessions": [ { "id": "0004d571-4623-4aed-8c44-06038405f6a2", "name": null,
                            "state": "closed", "title": "Untitled — -home-tim-company-interactive · 2026-06-06 · 2 turns",
                            "cwd": "/home/tim/company-interactive", "last_activity": "2026-06-06T02:16:15.470Z" } ] }
```
Adjacent: [[session#op: session.get]] for one row in full; [[session#op: session.post]] to act on one.

## op: session.get
**`session.get` is the single-session describe: the registry row joined with the durable
record's envelope (project, jsonl path/bytes, turns, git branch) plus a mail-traffic summary —
log-derived state always wins over the record's stored copy.**
```contract:op
op: session.get
resource: session
kind: get
status: building
direction: outbound
atlas: [CC-08.2]
tasks:
  - phrase: "inspect one session in full"
  - phrase: "is this session alive, and what has it been mailed"
  - alias: "describe a session"
bindings:
  - { kind: mcp, tool: sessions, op-param: "op=describe", server: company, exposure: "exposure.json#mcp-company" }
liveness: snapshot
live-twin: "[[session#op: session.watch]] (supervised sessions) / [[events#op: events.watch]] (any)"
emits: []
```
Request: `sessions(op="describe", session="session://<id>", detail=)`. Response:
`{op, session, record, mail: {inbound, outbound, latest: [{id, from, verb, thread, ts}…]}, detail, next}`.
Unknown id REFUSES loud with the registry's teaching error (never a fabricated session).
```contract:error
code: session.unknown | http: 404 | retryable: false
when: id resolves to no registry record (no agent_sessions/ record, no agent_sessions.* event)
teach: "Ids come from [[session#op: session.list]]; the importer (ops/agent_sessions_importer.py) backfills history. Titles are ~100% populated only via the fallback chain — match on id, never title alone."
```
```contract:example
captured: synthetic
binding: mcp
request: sessions(op="describe", session="0004d571-4623-4aed-8c44-06038405f6a2")
response: { "op": "describe", "session": "session://0004d571-4623-4aed-8c44-06038405f6a2",
            "record": { "id": "0004d571-…", "name": null, "state": "closed", "title": "Untitled — …",
                        "title_source": "untitled-envelope", "cwd": "/home/tim/company-interactive",
                        "started": "2026-06-06T02:16:12.708Z", "last_activity": "2026-06-06T02:16:15.470Z" },
            "mail": { "inbound": 0, "outbound": 0, "latest": [] }, "detail": "concise",
            "next": "sessions(op='inbox', session=…) reads the mail bodies; session_post sends to it." }
```
Adjacent: [[session-message#op: session-message.list]] for the mail bodies; [[transcript]] for its past content.

## op: session.create
**`session.create` spawns one SUPERVISED session — new, resumed (`--resume`, context intact)
or forked (`--fork-session`, original untouched) — under the held-open stream-json transport,
capped by the registry-refused concurrency law.**
```contract:op
op: session.create
resource: session
kind: create
status: building
direction: outbound
atlas: [CC-18.1, CC-08.3, CC-08.4, CC-05.1]
tasks:
  - phrase: "spawn a supervised Claude Code session"
  - phrase: "resume an old session under supervision"
    params: {resume: "<session id>"}
  - phrase: "fork a session into a sandbox copy"
    params: {resume: "<session id>", fork: true}
  - alias: "launch a session"
bindings:
  - { kind: http, method: POST, path: /spawn, transport: supervisor-http, exposure: "exposure.json#supervisor-http" }
  - { kind: cli, command: "company session new [--cwd D] [--resume ID] [--fork] [--name L] [--prompt …]", transport: cli-local, exposure: "exposure.json#cli-local" }
liveness: none
emits: []
consequences:
  - when: "spawn accepted"
    expect: [agent_sessions.spawned]
    bound: "response returns after init or COMPANY_FABRIC_INIT_WAIT_S (default 15s); the spawned event precedes the response (emitted at fork, durable)"
  - when: "prompt= was included"
    expect: [agent_sessions.turn, agent_sessions.idle]
    bound: "turn ≤ COMPANY_FABRIC_TURN_TIMEOUT_S (default 900s) — above it the watchdog reaps to closed"
correlate: [session]
verification:
  spawn-new:    {state: probe-verified, run: session_supervisor_acceptance (stub binary, real service), date: 2026-06-12}
  spawn-resume: {state: probe-verified, run: T2 (~/xsession-tests/RESULTS.md), date: 2026-06-11, note: "real-claude resume physics; end-to-end via this service is the lead's"}
  spawn-fork:   {state: probe-verified, run: T4 (~/xsession-tests/RESULTS.md), date: 2026-06-11, note: "original byte-identical; via this op real-claude UNVERIFIED"}
```
Request `{cwd?, resume?, fork?, name?, prompt?, source?}` (fork REQUIRES resume — a fork is a
fork OF something). Response `{ok: true, session: <supervisor-grain record>}` — `state` here
is the PROCESS vocabulary (`starting|idle`); the registry row becomes `supervised-live` via
the spawned event. The session runs `--permission-mode` per [[fabric-config]] (default
`plan`, read-only) with the strict company-MCP config.
```contract:error
code: fabric.concurrency-cap | http: 429 | retryable: true
when: live sessions + this spawn would exceed the cap
teach: "The refusal names the cap, what is live, and the ways forward: free a slot (session.stop) or raise COMPANY_FABRIC_CONCURRENCY deliberately on the service. Read the cap via [[fabric-config#op: fabric-config.get]]."
details: { "cap": 3, "live": "t0(idle), t1(idle), t2(busy)" }
```
```contract:error
code: session.fork-needs-resume | http: 409 | retryable: false
when: fork=true without resume=
teach: "A CONSULT/fork is a copy OF an existing session. Pass resume=<id>, or use [[session#op: session.create]] without fork for a fresh session."
```
```contract:example
captured: synthetic
binding: http
request: |
  POST /spawn HTTP/1.1
  Content-Type: application/json
  {"cwd": "/home/tim/company", "name": "scout-1", "resume": "0004d571-4623-4aed-8c44-06038405f6a2"}
response: |
  HTTP/1.1 200 OK
  {"ok": true, "session": {"id": "as-91cf4502", "claude_session_id": "0004d571-…", "name": "scout-1",
   "cwd": "/home/tim/company", "state": "idle", "resume": "0004d571-…", "fork": false,
   "created": "2026-06-12T…", "last_activity": "2026-06-12T…", "turns": 0, "pid": 12345, "close_reason": null}}
```
Adjacent: [[session#op: session.post]] (verb=wake does spawn+inject in one routed act);
[[session#op: session.stop]] frees the slot.

## op: session.post
**`session.post` is the routed durable message act — the ONE fabric write on the agent face:
it appends an intent to the mailbox (deliver / wake / consult / auto / queue), the supervisor
acts on it, and proof arrives as correlated `agent_sessions.*` events plus a thread-joined
mailbox reply — never in this response.**
```contract:op
op: session.post
resource: session
kind: act
status: building
direction: outbound
atlas: [CC-09.1, CC-09.2, CC-08.3, CC-08.4, CC-05.1]
tasks:
  - phrase: "send a message to another session"
  - phrase: "resume a closed session and ask it something"
    params: {verb: wake}
  - phrase: "ask N forked copies of a session in parallel"
    params: {verb: consult, copies: N}
  - phrase: "leave a message a running unsupervised session picks up next turn"
    params: {verb: auto}
  - alias: "notify a session"
  - alias: "fan out a question"
  - alias: "consult a session without disturbing it"
bindings:
  - { kind: mcp, tool: session_post, server: company, exposure: "exposure.json#mcp-company" }
  - { kind: http, method: POST, path: "/api/agent_sessions/{id}/messages", transport: bridge-http, exposure: "exposure.json#bridge-http", status: planned }
liveness: none
emits: []                      # single-writer law — this op appends intent; only the supervisor emits
consequences:
  - when: "verb resolved deliver (target supervised-live)"
    expect: [agent_sessions.turn, agent_sessions.idle]
    bound: "inject-to-idle ≤5s is the F1.1 bar; the supervisor polls mail every 0.5s; a busy target holds the intent (head-of-line, durable) until idle"
  - when: "verb resolved wake (target closed)"
    expect: [agent_sessions.spawned, agent_sessions.turn, agent_sessions.idle]
    bound: "spawned ≤ init wait (15s default); turn ≤ turn timeout (900s default)"
  - when: "verb resolved consult (any state, copies=N)"
    expect: ["agent_sessions.spawned ×N", "agent_sessions.turn ×N"]
    bound: "all N ≤ cap; N replies join the ONE returned thread"
    invariant: "original session file byte-identical (fork law — probe-verified T4 2026-06-11, ~/xsession-tests/RESULTS.md)"
  - when: "verb resolved queue (unsupervised-live / unknown — NOT deliverable)"
    expect: []
    evidence: "[[session-message#op: session-message.list]] with verb=queue shows the waiting intent — the named snapshot read for this absence-shaped outcome"
correlate: [intent_id]         # turn events carry intent_id; REPLIES join on the mailbox thread —
                               # thread does NOT ride events yet (honest gap, see [[events#Representation]])
verification:
  deliver: {state: probe-verified, run: session_supervisor_acceptance §6 (stub binary), date: 2026-06-12}
  wake:    {state: unverified, note: "router built + refusals proven (agent_sessions_mailbox_acceptance); real-claude wake end-to-end is the lead's"}
  consult: {state: probe-verified, run: T4 fork physics only, date: 2026-06-11, note: "via this op real-claude UNVERIFIED"}
  queue:   {state: probe-verified, run: agent_sessions_mailbox_acceptance (post→inbox round-trip), date: 2026-06-12}
```
### Request
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/session.post.request",
  "type": "object",
  "required": ["to", "message", "from_session"],
  "properties": {
    "to":           { "type": "string", "description": "target — bare id or session://<id>" },
    "message":      { "type": "string", "minLength": 1, "description": "body — rides cas://, size unconstrained" },
    "verb":         { "enum": ["auto", "deliver", "wake", "consult"], "default": "auto" },
    "copies":       { "type": "integer", "minimum": 1, "default": 1, "description": ">1 only with verb=consult; ≤ the cap — read it via fabric-config.get, never assume" },
    "from_session": { "type": "string", "minLength": 1, "description": "REQUIRED on every binding — your reply path (session://<your id>); a stable label is accepted but not reply-addressable" },
    "thread":       { "type": "string", "description": "join an existing conversation; omitted → a fresh thread is minted (= this post's mail id)" } },
  "additionalProperties": false }
```
### Response
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/session.post.response",
  "type": "object",
  "required": ["posted", "seq", "to", "verb", "thread", "routed"],
  "properties": {
    "posted":         { "type": "string", "description": "the mail record id (mail-<seq>)" },
    "seq":            { "type": "integer", "description": "your watch cursor into the mailbox: replies have seq > this" },
    "to":             { "type": "string" },
    "verb":           { "enum": ["deliver", "wake", "consult", "queue"], "description": "the RESOLVED routing" },
    "requested_verb": { "enum": ["auto", "deliver", "wake", "consult"] },
    "state_at_post":  { "type": ["string", "null"] },
    "copies":         { "type": "integer" },
    "thread":         { "type": "string", "description": "the aggregation key every reply joins" },
    "routed":         { "enum": ["supervisor-inject", "supervisor-wake", "supervisor-fork", "next-turn-pickup"] },
    "what_happens":   { "type": "string" },
    "replies":        { "type": "string", "description": "the literal read that returns the answers" } } }
```
### Errors
```contract:error
code: session.verb-state-conflict | http: 409 | retryable: false
when: explicit verb illegal for target state — deliver→closed (nothing to inject into) · wake→supervised-live (double-spawn) · wake→unsupervised/unknown (a second writer silently BRANCHES a live session — T1)
teach: "Use verb=auto (routes by state), or [[session#op: session.get]] first. A refusal after a passed pre-check is expected concurrency — verdict pass-via-refusal."
```
```contract:error
code: fabric.copies-cap | http: 429 | retryable: true
when: copies > the concurrency cap, or copies > 1 without verb=consult
teach: "Fan ≤ cap (COMPANY_FABRIC_CONCURRENCY; read it via [[fabric-config#op: fabric-config.get]]) — refused loud, never silently truncated. copies only means anything for consult fans."
```
```contract:error
code: session.reply-path-missing | http: 400 | retryable: false
when: from_session empty (or message empty — same refusal class)
teach: "from_session is the REPLY PATH — pass your own session://<id> so answers route back to your inbox, read via [[session-message#op: session-message.list]]."
```
Plus `session.unknown` (the registry's 404-class teach, as on [[session#op: session.get]]).
### Interaction semantics
Durability: intent fsync'd on append, cross-process-unique seq under the mail lock — an
acknowledged post survives a crash; the supervisor consumes strictly in order (head-of-line
hold for busy targets: nothing skipped). Idempotency: NONE — re-posting duplicates the intent
(stated, not hidden). Ordering: FIFO per leaf; a consult fan's replies aggregate under the one
returned `thread`. Concurrency: any number of posters; the supervisor is the sole writer to
any session itself.
### Consequences & proof shape
Completion = the declared events appearing via [[events#op: events.list]] after your post,
joined on `intent_id` (= the mail id you got back as `posted`), THEN the reply content via
`sessions(op="inbox", session=<your from_session>, thread=<thread>)` — body text resolved,
`verb: "reply"` (or `"error"` carrying the supervisor's teaching refusal — also a result,
also thread-joined). Never trust `what_happens` prose as completion.
### Live-ness
`liveness: none` — the receipt is immediate; aftermath rides [[events#op: events.list]]
(poll) / [[events#op: events.watch]] (SSE stream) and the mailbox.
```contract:example
captured: synthetic
binding: mcp
request: session_post(to="session://a3f9…", message="What did you decide about facet chips?",
                      verb="consult", copies=3, from_session="session://caller-uuid")
response: { "posted": "mail-18", "seq": 18, "to": "session://a3f9…", "verb": "consult",
            "requested_verb": "consult", "state_at_post": "closed", "copies": 3,
            "thread": "mail-18", "routed": "supervisor-fork",
            "what_happens": "the supervisor forks 3 copies (--fork-session, original untouched); replies aggregate under this thread",
            "replies": "sessions(op='inbox', session='session://caller-uuid', thread='mail-18')" }
```
Adjacent: before — [[session#op: session.list]], [[session#op: session.get]]; observe —
[[events#op: events.list]]; read results — [[session-message#op: session-message.list]];
flow — [[message-and-read-reply]].

## op: session.inject
**`session.inject` is the direct operator push — one turn written straight into a SUPERVISED
session's held-open stdin, no mailbox, no durable reply record: the synchronous twin
`session.post(verb=deliver)` should usually win.**
```contract:op
op: session.inject
resource: session
kind: act
status: building
direction: outbound
atlas: [CC-18.2]
tasks:
  - phrase: "push a turn directly into a supervised session"
  - alias: "type into a running session"
bindings:
  - { kind: http, method: POST, path: /inject, transport: supervisor-http, exposure: "exposure.json#supervisor-http" }
  - { kind: cli, command: "company session send <id> <message…>", transport: cli-local, exposure: "exposure.json#cli-local" }
liveness: none
emits: []
consequences:
  - when: "accepted (target idle)"
    expect: [agent_sessions.turn, agent_sessions.idle]
    bound: "turn ≤ COMPANY_FABRIC_TURN_TIMEOUT_S; the watchdog reaps silent hangs to closed"
correlate: [session]
verification:
  inject-idle: {state: probe-verified, run: session_supervisor_acceptance §4, date: 2026-06-12}
```
Request `{session, message, source?}`. Refusals teach: busy → 409 ("wait for idle, interrupt,
or queue via the mailbox — the supervisor retries deliver intents until idle"); closed → 409
("WAKE it instead: spawn with resume=<id>"); unknown → 404. Unlike `post`, the assistant's
reply is NOT mailed anywhere — watch it live via [[session#op: session.watch]] or read the
turn event. Differences from post are the contract: choose post for durability + replies.
Adjacent: [[session#op: session.post]] (the routed, durable act), [[session#op: session.watch]].

## op: session.interrupt
**`session.interrupt` writes a control_request onto a busy session's stdin to stop the
in-flight turn — contracted honestly as UNPROVEN against a real claude turn (the watchdog
remains the enforcement backstop either way).**
```contract:op
op: session.interrupt
resource: session
kind: act
status: building
direction: outbound
atlas: [CC-18.3]
tasks:
  - phrase: "stop a session's in-flight turn without killing it"
  - alias: "cancel a running turn"
bindings:
  - { kind: http, method: POST, path: /interrupt, transport: supervisor-http, exposure: "exposure.json#supervisor-http" }
liveness: none
emits: []
consequences:
  - when: "interrupt honoured by the subprocess"
    expect: [agent_sessions.turn]
    bound: "unbounded-with-evidence: the session's watch stream shows interrupt_sent immediately; the turn event closes the turn when claude yields"
correlate: [session]
verification:
  real-claude-interrupt: {state: unverified, note: "stub subprocesses ignore control_request by design; built-untested against a real turn — stated in the service's own docstring"}
```
Refusal: not-busy → 409 teach ("nothing to interrupt"). Watch `interrupt_sent` on
[[session#op: session.watch]] for the attempt; the watchdog reap (closed, reason names it)
is the guaranteed ceiling regardless.
Adjacent: [[session#op: session.stop]] (the hard stop), [[fabric-config]] (the timeout).

## op: session.stop
**`session.stop` tears down supervision of one session — subprocess terminated (kill after
5s grace), state closed with reason "teardown", record retained, slot freed; calling it on an
already-closed session is an idempotent OK.**
```contract:op
op: session.stop
resource: session
kind: act
status: building
direction: outbound
atlas: [CC-18.4]
tasks:
  - phrase: "tear down a supervised session"
  - phrase: "free a fabric slot"
  - alias: "kill a session"
bindings:
  - { kind: http, method: POST, path: /teardown, transport: supervisor-http, exposure: "exposure.json#supervisor-http" }
  - { kind: cli, command: "company session stop <id>", transport: cli-local, exposure: "exposure.json#cli-local" }
liveness: none
emits: []
consequences:
  - when: "stop of a live session"
    expect: [agent_sessions.closed]
    bound: "≤ ~5s (terminate grace, then kill); the subprocess is verifiably dead — the no-orphans law"
correlate: [session]
verification:
  teardown: {state: probe-verified, run: session_supervisor_acceptance §7 (pid-checked), date: 2026-06-12}
```
A closed session is not gone: it stays in the registry and is wake-able
([[session#op: session.post]] verb=wake). Unknown id → 404 teach.
Adjacent: [[session#op: session.create]] (re-spawn), [[events#op: events.list]] (the closed claim).

## op: session.watch
**`session.watch` is the per-session live stream: ndjson frames of ONE supervised session's
activity — replay of its recent frames, then live, keepalive-padded — in the supervisor's
frame vocabulary, which is NOT the `agent_sessions.*` event vocabulary.**
```contract:op
op: session.watch
resource: session
kind: watch
status: building
direction: outbound
atlas: [CC-08.5, CC-18.5]
tasks:
  - phrase: "watch what a session is doing right now"
  - alias: "tail a session"
bindings:
  - { kind: http, method: GET, path: "/watch?session=<id>", transport: supervisor-http, exposure: "exposure.json#supervisor-http" }
liveness: watch
frames: "ndjson, one JSON object per line: {seq (per-session counter), ts, session (handle), type: init|text|tool|injected|interrupt_sent|done|closed, …type-specific fields}"
resume: "none — connection replays the session's buffered frames (≤500) then streams; there is no cross-connection cursor (stated, not hidden)"
keepalive: "{\"type\":\"keepalive\"} every ~15s of silence"
termination: "stream ends after the closed frame, or on client disconnect (subscriber detached server-side)"
emits: []
verification:
  watch-stream: {state: probe-verified, run: session_supervisor_acceptance (subscriber fan), date: 2026-06-12}
```
Frame meanings: `init` (claude_session_id named) · `text` (assistant text as it streams) ·
`tool` (one-line tool trace: name + key arg) · `injected` (a turn entered) · `done` (turn
result: result text head, num_turns, is_error) · `closed` (reason). For fleet-wide,
durable, seq-cursored observation use [[events#op: events.watch]] — that is the proof
stream; this is the human-grade live view of one mind.
Unknown session → 404 teach ("GET /sessions for the live set").
Adjacent: [[events#op: events.watch]], [[session#op: session.inject]].

## Errors
**Resource-level error vocabulary: every refusal on this resource TEACHES — names the limit
or conflict, the live state, and the way forward — and rides the per-face carriers in
[[CONVENTIONS]] until the §9.5 envelope obligation lands.** Codes declared on the ops above:
`session.unknown` · `session.unknown-state` · `session.verb-state-conflict` ·
`session.fork-needs-resume` · `session.reply-path-missing` · `fabric.concurrency-cap` ·
`fabric.copies-cap`. State names in error details are members of this entry's fsm (registry
grain) or the supervisor grain where the op is supervisor-bound (stated per op).

## Links
**Address-typed fields on this resource's shapes: `session://` throughout — `to`, `from`,
`forks`-class fields, and the `session` field on every consequence event — all dereference
to THIS entry via the accepting ops listed under Identity.** `thread`/mail ids in responses
are plain strings today (PLANNED schemes per [[CONVENTIONS]] — no dead-end address is
claimed for them); resolve them via [[session-message#op: session-message.list]] params.
