---
type: contract-entry
resource: session-message
summary: One durable mailbox record — an intent, queue-drop, reply or error — on the fabric's append-only mail leaf; seq-cursored, thread-aggregated, bodies content-addressed.
schemes: []
status: building
relates-to: ["[[session]]", "[[events]]"]
---

# Resource: session-message

## Identity
**A session-message is identified by its cross-process-unique `seq` (the cursor key) and its
id `mail-<seq>`; there is deliberately NO `msg://` scheme yet (planned, CONTRACT-FORMAT §9.7)
— ids are plain strings, retrieved by reading, never dereferenced as addresses.**
Messages are born only two ways: a [[session#op: session.post]] (intent/queue records) or the
supervisor's reply/error writes. `thread` (a plain string, defaulting to the founding mail's
id) is the conversation key: a consult fan's N replies all carry the one intent's thread.

## Representation
**A mail record carries explicit routing fields (to / from / verb / thread — each a clean
filter) with the body always behind a `cas` ref, resolved to text for you by the inbox read.**
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/session-message.record",
  "type": "object",
  "required": ["seq", "id", "ts", "to", "from", "verb", "cas"],
  "properties": {
    "seq":            { "type": "integer", "description": "cross-process-unique, monotonic (appended under the mail lock) — the cursor key" },
    "id":             { "type": "string", "description": "mail-<seq>" },
    "ts":             { "type": "string", "format": "date-time" },
    "to":             { "type": "string", "description": "session://<id> — the inbox key" },
    "from":           { "type": "string", "description": "the reply path (session://<id>, or session://supervisor on service errors, or a caller's label)" },
    "verb":           { "enum": ["deliver", "wake", "consult", "queue", "reply", "error"] },
    "thread":         { "type": "string" },
    "cas":            { "type": "string", "description": "cas://-class body ref; inbox reads resolve it" },
    "re":             { "type": "string", "description": "replies/errors only: the intent id answered" },
    "requested_verb": { "type": "string", "description": "intents only: what the poster asked before routing" },
    "state_at_post":  { "type": ["string", "null"], "description": "intents only: target's registry state at post time" },
    "copies":         { "type": "integer", "description": "intents only: consult fan width" },
    "source":         { "type": "string" } },
  "additionalProperties": true }
```
| field | type | volatile? | changed-by (event) | address? → resource | reality |
|---|---|---|---|---|---|
| seq/id/ts | int/string | no — records are immutable once appended (append-only leaf, keep-forever retention) | — | — | store-owned, never caller-settable |
| to / from | string | no | — | session:// → [[session]] (when session-shaped) | enforced non-empty at append (unroutable records refused) |
| verb | enum | no | — | — | replies are `reply`/`error` with `re` = the intent id; supervisor refusals arrive as `error` records — also answers, also thread-joined |
| thread | string | no | — | — | 100% populated (store defaults it to the record's own id; supervisor replies join the intent's thread) |

## State model
**State model: stateless.** Consumption position lives in CURSORS, never on records: no
status field exists or will (read-modify-write on a shared log is the refused design).

## Caller
**Your inbox is whatever `to` you ask for — reads are parameterized by explicit session
address, and your durable position is yours to hold (client-held `next_since`) or to persist
via the per-consumer cursor refs in [[CONVENTIONS]].** The supervisor consumes intents
addressed through it with its own internal cursor; `queue`-verb records are the TARGET
session's to pick up by reading this op at its next turn.

## Operations

## op: session-message.list
**`session-message.list` is the inbox read: messages addressed to one session, OLDEST-first
from your seq cursor, bodies resolved to text, filterable to one thread (a fan's replies) or
one verb — pure and non-destructive, re-reading is always safe.**
```contract:op
op: session-message.list
resource: session-message
kind: list
status: building
direction: outbound
atlas: [CC-09.3, CC-09.4]
tasks:
  - phrase: "read a session's inbox"
  - phrase: "collect the replies to a question I fanned out"
    params: {thread: "<thread from session.post>"}
  - phrase: "check for queued messages at my turn start"
    params: {verb: queue}
  - alias: "check my mail"
  - alias: "did anyone answer"
bindings:
  - { kind: mcp, tool: sessions, op-param: "op=inbox", server: company, exposure: "exposure.json#mcp-company" }
  - { kind: http, method: GET, path: "/api/agent_sessions/{id}/messages", transport: bridge-http, exposure: "exposure.json#bridge-http", status: planned }
liveness: snapshot
live-twin: "poll this with since=next_since; the PUSH-shaped twin is the consequence events on [[events#op: events.watch]] (replies land as mail ≈together with the turn event)"
emits: []
verification:
  inbox-read: {state: probe-verified, run: agent_sessions_mailbox_acceptance (54 checks incl. FIFO/filters/pagination), date: 2026-06-12}
  reply-visibility: {state: probe-verified, run: session_supervisor_acceptance §6 (reply seq-stamped + thread-joined + round-tripped via this read), date: 2026-06-12}
```
Request: `sessions(op="inbox", session=, since=-1, thread="", verb="", limit=50, detail=)`.
`since` is YOUR cursor (mail seq, NOT event seq; -1 = everything). Response:
`{op, session, total, since, next_since, detail, messages: [{id, seq, from, verb, thread,
ts, message (the resolved body text)}…], consumption}` — pass `since=next_since` next call;
`limit` paginates oldest-first without ever skipping.
```contract:error
code: session-message.bad-cursor | http: n/a (mcp tool error) | retryable: false
when: a DURABLE per-consumer cursor (the refs in [[CONVENTIONS]]) is corrupt or moved backward
teach: "Cursors only advance; replay is an explicit since=<older> read, never a rollback. A corrupt stored cursor fails loud — inspect its ref history and re-set deliberately per the cursor law in [[CONVENTIONS#Cursor / pagination law]]."
```
```contract:example
captured: synthetic
binding: mcp
request: sessions(op="inbox", session="session://caller-uuid", thread="mail-18", since=18)
response: { "op": "inbox", "session": "session://caller-uuid", "total": 3, "since": 18,
            "next_since": 21, "detail": "concise",
            "messages": [
              { "id": "mail-19", "seq": 19, "from": "session://fork-1-uuid", "verb": "reply",
                "thread": "mail-18", "ts": "2026-06-12T…", "message": "Facet chips were decided as …" },
              { "id": "mail-20", "seq": 20, "from": "session://fork-2-uuid", "verb": "reply",
                "thread": "mail-18", "ts": "2026-06-12T…", "message": "The decision was …" },
              { "id": "mail-21", "seq": 21, "from": "session://fork-3-uuid", "verb": "reply",
                "thread": "mail-18", "ts": "2026-06-12T…", "message": "…" } ],
            "consumption": "client-held cursor — pass since=next_since on your next read; re-reading is safe (this never consumes destructively)." }
```
Adjacent: the write is [[session#op: session.post]]; sender context — [[session#op:
session.get]] shows a session's mail-traffic summary; flow — [[message-and-read-reply]].

## Errors
**This resource's refusals are append-side structural laws surfacing through the ops that
write it: a record missing to/from/verb/cas is refused as an unroutable black hole — readers
never see half-records.** Read-side: `session-message.bad-cursor` (above); an empty inbox is
an HONEST empty list, never an error.

## Links
**`to`/`from` fields are `session://` addresses dereferencing to [[session]]; `thread`/`id`/
`re` are plain-string keys (no scheme claimed — the planned `msg://`/`thread://` schemes land
with §9.7), resolved only through this entry's list params (`thread=`) and
[[session#op: session.post]]'s `thread` request field.**
