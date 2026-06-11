---
type: contract-format
build: capability-fabric
captured: 2026-06-11
status: frozen — P0.3
provenance: 3-lens dialectic (resource-oriented · event-sourced · capability-verbs, blind proposals + adversarial critiques + synthesis)
---

# CONTRACT-FORMAT — UI Contract Corpus (FROZEN at P0.3)

The format for the corpus that F9 calls "the build's second product": the purpose-free, machine-checked,
embedding-ready contract a UI-building AI consumes instead of ever reading this repo's code or its
disposable harness UI. Anchored to `Session Fabric — Completion Criteria.md` (F9.1–F9.3, audits
B2/B3/C8/C9/N1/N2/N5/N9) and `Session Fabric — Implementation Guide.md` (both in this build-prep
directory, beside this file).

**Frozen** means: entry CONTENT updates freely in place forever (no-versioning law); the FORMAT
(this file + the validator) changes only via a recorded decision, edited INTO the body in place with
a changelog line at the bottom — the body is always current, never appendix-drifted (§11).

---

## 0 · Adjudication — which lens won and why

**Spine: RESOURCE-ORIENTED (Proposal A).** Three grounds, all verified against the live repo on
2026-06-11:

1. **It matches the system's own standing law.** `mcp_face/server.py:30-36` (Observed): "a new need
   is a new `op`, never a new flat tool" — the MCP face is already consolidated resource tools with
   op multiplexing. A noun-keyed corpus with a uniform op set documents that shape 1:1. The
   event-sourced lens fights it (one entry per op AND per route — its critique S4 showed the rule
   self-contradicts); the verbs lens shatters it (one endpoint → 3+ near-duplicate entries, critique
   C-C2's measured retrieval loss).
2. **Lowest cross-lane coupling.** The build method is file-disjoint parallel lanes. Event-sourced
   concentrates ALL coupling on ~30 shared stream/event/machine files every lane must edit (B-d1,
   structural, unfixable without abandoning the lens). Capability-verbs multiplies files 150–300 with
   mandatory restatement (C-C2/D4). Resource entries: one file per noun, lanes own disjoint nouns.
3. **Its critique holes are bolt-ons; the others' are load-bearing.** Every Critique-A finding
   resolves with an added rule or generated artifact (§10 resolves all 27). Critique B found the
   event-sourced spec defeats itself four ways before a consumer touches it (S1–S4) and its signature
   coverage check is unexecutable (B-b3). Critique C found the verbs lens's headline claim
   ("battery shape = corpus shape") is structurally falsified by F9.2's own blindness rule (C-A4) and
   its taxonomy freeze creates permanent debt (C-D5).

**Grafts taken** (each made a binding rule below): from EVENT-SOURCED — the watch-cursor proof shape
(every write's response names where its consequences appear; a task passes when declared events appear,
never when "a response looked ok"), the emits/consequences split under the single-writer law, the
correlation-key law, event-keyed state machines, flat-file-sufficient navigation, the generated
reality-snapshot discipline. From CAPABILITY-VERBS — the generated task/intent index (task-shaped
navigation WITHOUT taxonomy freeze), teach-text errors naming recovery ops, the transports file,
adjacent-ops lateral navigation, field-reality honesty, the profile partition rule (made non-circular
via negative probes), exclusion files (extended to affordance and endpoint grain).

**Factual ground this spec stands on (Observed 2026-06-11):** `contracts/address.py:45` SCHEMES =
`("run","cas","blob","vec","ui","code","skill","context")` — `session://`, `msg://`, `thread://` are
PLANNED, not present. No `session_post`/`agent_sessions`/`AGENT_SESSION_OPS` code exists anywhere in
`~/company`. `BRIDGE_ROUTES` (`runtime/bridge.py:45`) is a flat tuple of ~115 path strings including
the disposable harness's routes; methods are comments. MCP ops live in docstrings/if-elif, not
enumerable registries. T4 fork physics VERIFIED (`~/xsession-tests/RESULTS.md`, 2026-06-11). This
corpus therefore contracts a fabric **under build** — the status machinery (§4.2) is designed for
exactly that, and §9 lists the code-side obligations the format imposes on the build so the
machine-checks have real registries to check against. The corpus never extends "a proven pattern"
where none exists; it extends the bridge's one genuinely proven pattern (registry + bidirectional
drift test) to every face.

---

## 1 · Corpus file layout

```
~/company/ui-contract/                ← corpus root. NOT contract/ or contracts/ — contracts/ is the
                                        Python contracts layer (collision confirmed in repo; same
                                        discipline as audit N2's agent_sessions ruling)
  README.md                           ← AUTHORED, ≤60 lines: ontology + the navigation protocol (§8)
                                        + what the agent has been granted (full read access to this
                                        directory tree, incl. coverage/*.json)
  CONTRACT-FORMAT.md                  ← copy of this spec (canonical lives in build-prep; the corpus
                                        carries the current body, updated in place)
  CONVENTIONS.md                      ← uniform op verbs · uniform error envelope + per-face envelope
                                        mapping (HTTP status table, MCP tool-result shape, CLI
                                        exit-code map) · cursor/pagination law · address grammar ·
                                        purpose-free vocabulary rules + the aliases channel ·
                                        named-act registry (append-only, one line per act — lanes
                                        add lines, never rewrite: merge-clean by construction)
  TRANSPORTS.md                       ← transport ids → protocol, base URL/port or stdio, auth model,
                                        CALLER IDENTITY model per transport (who you are when you
                                        call, and how a non-session HTTP consumer names itself),
                                        inventory source per transport (machine-readable registry —
                                        a transport without one FAILS validation)
  EXPOSURE.md + exposure.json         ← GENERATED exposure registry (§5). Bindings reference keys
                                        here; values are extracted from service config (bind
                                        addresses, tailscale-serve config, stdio nature), never
                                        hand-restated per entry
  resources/
    session.md                        ← one file per resource noun, kebab-case; basenames unique
    session-message.md                  corpus-wide (one link grammar, one resolver — §6.4)
    events.md                         ← the event-type catalog IS a resource (closed set, payload
    transcript.md                       schemas, stream + watch-op per event)
    fabric-config.md
    …                                 ← every lane F1–F8 adds its nouns
  journeys/
    message-and-read-reply.md         ← AUTHORED, one file per canonical cross-resource flow: ordered
    render-a-conversation-live.md       op refs + the disambiguation prose that lives between
    …                                   resources ("transcript for history, watch for live,
                                        messages are not turns")
  atlas/
    FEATURE-ATLAS.md                  ← the 35 classes, frozen ids CC-01…CC-35, AND their affordances
                                        (CC-05.1, CC-05.2 …) — coverage grain is the AFFORDANCE
    OUT-OF-SCOPE.md                   ← affordance-grain exclusions: id → reason → decided-by → date.
                                        Partial classes are expressible (3 affordances in, 2 out,
                                        each out WITH reason). Never silent (N5/C8)
    INVENTORY-EXCLUSIONS.md           ← ENDPOINT-grain exclusions: live endpoints deliberately
                                        uncontracted (the disposable harness's routes, citing
                                        [[feedback-company-ui-disposable]]), each with reason —
                                        counted and reported, never silently skipped
  TASKS.md                            ← GENERATED task index: intent phrase / alias → (op, params)
                                        rows, including "not exposed locally → see exclusion" rows.
                                        Regenerated from per-op `tasks:` declarations — intent
                                        groupings re-cluster freely, NO frozen taxonomy
  INDEX.md                            ← GENERATED: resource table (noun → one-line summary from
                                        frontmatter `summary:` → file) + SCHEMES table (scheme →
                                        owning resource → ACCEPTING OPS) + journey list
  coverage/
    coverage.json                     ← GENERATED two-layer map (§7): contracted vs demonstrated
    reality.json                      ← GENERATED snapshot of the live system (registries + bind
                                        config + tool inputSchemas), timestamped
    load.jsonl                        ← appended by the driving harness: file reads AND substrate
                                        hits (harness logs both — §7.4)
    drops.jsonl                       ← reached-for-but-missing ledger → gap adoption (F10.1)
  evidence/
    runs/<run-id>/<op>.txt            ← captured transcripts per harness run. Run ids identify
                                        distinct events (append-only ledger), they are NOT versions
                                        of one document — the no-versioning law governs canonical
                                        documents, not evidence ledgers (ruling, §10 A-d3)
  tools/
    validate.py                       ← rules V1–V26 (§6) + the reality join. Repo test, fails loud
    extract_reality.py                ← builds reality.json from the code-side registries (§9)
    coverage.py                       ← builds coverage.json (§7)
    rename.py                         ← validator-grade rename: rewrites frontmatter, wikilinks, AND
                                        string refs inside fences (teach/hint), using the same ref
                                        extractor validation uses
```

GENERATED files are never hand-edited (generator overwrites in place; hand-edits fail the diff
check). Markdown is the embedding surface; `coverage/*.json`, `exposure.json`, `reality.json` are
machine artifacts outside the markdown scan by construction — the agent reaches them by filesystem
read, which README explicitly grants.

---

## 2 · Entry template (one file per resource)

````markdown
---
type: contract-entry
resource: session
summary: A Claude Code session under fabric management — addressable, messageable, forkable, watchable.
schemes: ["session://"]
status: planned            # planned | building | live | broken | retired  (§4.2)
relates-to: ["[[session-message]]", "[[events]]", "[[transcript]]"]
---

# Resource: session

## Identity
**The session resource is identified by `session://<id>`; ids come from the registry, never guessed.**
Address grammar as a ```contract:schema``` fence. Scheme rows here feed INDEX.md's SCHEMES table —
each row names the owning entry AND the ops that ACCEPT the scheme as input (dereferenceability is
machine-checked, not just ownership — §6 V7).

## Representation
**A session record carries identity, state, title, timestamps; this section is the canonical shape.**
One ```contract:schema``` fence + a field table:

| field | type | volatile? | changed-by (event) | address? → resource | reality |
|---|---|---|---|---|---|

`volatile` fields MUST name the event type(s) that change them (`changed-by`); every event names its
stream; every stream names its watch op — the field→event→watch chain is machine-checked (§6 V16).
`reality` is the field-population honesty column (audit B2): e.g. title — ai-title ~3–7%, ~100% via
fallback chain — with the measuring tool + date, refreshed by the harness, never hand-typed-and-rotted.

## State model
**States, event-keyed transitions, and per-state op legality for this resource.**
A ```contract:fsm``` fence (states, transitions keyed by event types, legality matrix) + prose.
Stateless resources write exactly: `State model: stateless.` — no junk machines (§10 B-d3).

## Caller
**Who you are when you operate on this resource, per transport.**
Identity-dependent semantics (inboxes, `from` defaults, per-consumer cursors) are defined HERE
against the per-transport identity models in TRANSPORTS.md. Any op whose meaning depends on caller
identity links this section. No implicit "your session" — HTTP consumers name themselves explicitly.

## Operations
One H2 per operation: `## op: session.list`, `## op: session.get`, `## op: session.post`,
`## op: session.watch` … (template §3). Uniform verb vocabulary ONLY:
**list · get · create · update · delete · act (named acts) · watch · search.**
Anything else is remodeled as a resource or a named act — never an ad-hoc verb. Routing modes
(DELIVER/WAKE/CONSULT) are parameters of one act, and they are SURFACED in the task index so
parameter-level affordances are never buried below verb-level navigation (§10 A-a1).

## Errors
**Resource-level error codes beyond the uniform envelope.** ```contract:error``` fences. Codes are
corpus-unique (global registry check, §6 V4); state names used in error details are members of this
entry's fsm fence (closed set — no `supervized-live` typo survives, §10 C-B6).

## Links
**The hypermedia map: every address-typed field in this resource's shapes → scheme → target entry →
accepting ops.** Machine-checked against INDEX.md's SCHEMES table, both existence AND
dereferenceability.
````

**Chunk discipline (binding, applies to EVERY H2 section, not just ops):**
- The FIRST line of every H2 section is a **bold one-sentence restatement** naming the resource, the
  section/op, and its distinguishing mechanics — distinct corpus-wide (duplicate restatement lines
  are linted; boilerplate anchors are a retrieval failure, §10 B-c1). The restatement comes BEFORE
  any fence (prose leads, YAML follows — §10 A-c1).
- Section budget ≤180 lines; file budget ≤600. Overflow relief: an op's Examples may continue in a
  sibling section `## op: session.post — examples (cont.)` that opens with its own restatement line.
  Fences are never split across sections.
- Frontmatter `summary:` is the specced source of INDEX.md's one-line descriptions (§10 A-d2).

---

## 3 · Operation template + COMPLETE worked example: `session.post`

Order within every op section: **restatement line → opspec fence → description (purpose-free) →
request schema → response schema → errors → interaction semantics → consequences & proof shape →
live-ness → examples → adjacent ops.** The opspec fence is the SINGLE machine truth — frontmatter
summaries and prose are checked against it, never trusted over it (§6 V20; §10 C-B9/C-D8).

The following is the complete section as it will appear in `resources/session.md`. Status is
`planned` — honest: no `session_post` exists in code today; only the consult-fork physics are
verified (T4). Synthetic examples are therefore legal AND marked; they MUST be replaced by captured
evidence at the flip to `live` (§6 V11).

~~~~markdown
## op: session.post

**`session.post` is the session resource's one message-sending act: it appends a durable routed
intent (deliver / wake / consult / auto) addressed to a session, returns a receipt plus a watch
cursor, and its consequences arrive as correlated `agent_sessions.*` events — never in the response
body.**

```contract:op
op: session.post
resource: session
kind: act
status: planned                  # flips building → live only via harness-written verification (§4.2)
direction: outbound              # outbound = consumer calls system; inbound exists for hook-shaped ops
atlas: [CC-05.2, CC-08.1, CC-08.3, CC-09.1]
tasks:                           # feeds GENERATED TASKS.md; lint-EXEMPT retrieval aliases included
  - phrase: "send a message to another session"
  - phrase: "resume a closed session and ask it something"   # params surface in the index:
    params: {verb: wake}                                     # wake is findable at index level
  - phrase: "ask N forked copies of a session in parallel"
    params: {verb: consult, copies: N}
  - alias: "notify a session"     # consumer-language bait; aliases never appear in descriptions
  - alias: "fan out a question"
caller: required                 # semantics depend on identity — see [[session#Caller]]
bindings:
  - kind: mcp
    tool: session_post           # split-write tool (consequential-write law); reads consolidate
    server: company
    exposure: exposure.json#mcp.company        # a REGISTRY KEY, never an inline value (§5)
  - kind: http
    method: POST
    path: /api/agent_sessions/{session_id}/messages
    transport: bridge-http
    exposure: exposure.json#bridge-http
  - kind: cli
    command: company session post
    exposure: exposure.json#cli-local
liveness: none                   # the act itself is not a stream; proof rides the watch cursor
emits: []                        # single-writer law: this op appends intent only
consequences:                    # observed on the stream, never returned (event-sourced graft)
  - when: "routed=injected (target supervised-live, idle)"
    expect: [agent_sessions.turn]
    bound: "turn begins ≤5s after receipt (inject-to-idle bar)"
  - when: "routed=wake-spawned (verb=wake or auto on closed)"
    expect: [agent_sessions.spawned, agent_sessions.turn, agent_sessions.idle]
    bound: "spawned ≤30s (model spin-up ceiling); turn/idle unbounded-with-evidence: progress
            observable via agent_sessions.turn heartbeat sequence"
  - when: "routed=fork-spawned (verb=consult, copies=N)"
    expect: ["agent_sessions.spawned ×N", "agent_sessions.turn ×N sharing thread"]
    bound: "all N spawned ≤60s"
    invariant: "original session file byte-identical (fork law — VERIFIED by probe, T4 2026-06-11,
               ~/xsession-tests/RESULTS.md; end-to-end via this op UNVERIFIED until F1.3)"
  - when: "routed=queued (target unsupervised-live)"
    expect: []
    evidence: "[[session-message#op: session-message.list]] with status=queued shows the intent —
               absence-shaped outcomes name a snapshot read or they are uncontractable (§6 V14)"
correlate: [intent_id, thread]   # EVERY consequence event carries both; matchers JOIN on them (§6 V15)
verification:                    # written ONLY by the harness — per BRANCH, never per file (§4.2)
  injected:      {state: unverified}
  wake-spawned:  {state: unverified}
  fork-spawned:  {state: probe-verified, run: T4, date: 2026-06-11, commit: pending-F1.3}
  queued:        {state: unverified}
links:
  - field: $.message.id
    scheme: "msg://"
    resource: session-message
    accepted-by: ["session-message.get"]
  - field: $.thread
    scheme: "thread://"
    resource: session-message
    accepted-by: ["session-message.list"]      # list(thread=) — the fan's aggregation read
  - field: $.forks[*]
    scheme: "session://"
    resource: session
    accepted-by: ["session.get", "session.watch", "session.post"]
```

### Description (purpose-free)
Appends one durable intent record addressed to the target session. A supervisor service — the only
writer of `agent_sessions.*` events — consumes the intent and routes it by the target's state in the
registry: a supervised-live session receives it as an injected turn; a closed session is resumed
under supervision first (wake) or forked N times without touching the original (consult — fork
physics probe-verified T4); an unsupervised-live session has it queued for pull at its next turn.
The call returns a receipt naming the created message, the resolved routing, the thread under which
every consequence aggregates, and a watch cursor into the fact stream. Replies are durable events
carrying the thread id — they are observed, never returned.

### Request
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/session.post.request",
  "type": "object",
  "required": ["to", "message"],
  "properties": {
    "to":      { "type": "string", "format": "address", "x-scheme": "session://" },
    "message": { "type": "string", "minLength": 1 },
    "verb":    { "enum": ["auto", "deliver", "wake", "consult"], "default": "auto" },
    "copies":  { "type": "integer", "minimum": 1, "default": 1,
                 "description": "fork fan width; >1 requires verb=consult; cap is registry-served —
                                 read it via fabric-config.get, never assume" },
    "from":    { "type": "string", "format": "address", "x-scheme": "session://",
                 "description": "originator for the reply thread. MCP binding: defaults to the
                                 calling session. HTTP/CLI bindings: REQUIRED — non-session
                                 consumers use their TRANSPORTS.md-issued consumer id; there is no
                                 implicit identity over HTTP" },
    "intent_id": { "type": "string",
                 "description": "caller-supplied dedupe key; re-posting the same intent_id is a
                                 no-op returning the original receipt (verified by negative probe
                                 at flip-to-live)" }
  },
  "additionalProperties": false }
```

### Response
```contract:schema
{ "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "ui-contract/session.post.response",
  "type": "object",
  "required": ["message", "routed", "thread", "watch"],
  "properties": {
    "message": { "type": "object", "required": ["id", "to", "verb"],
      "properties": {
        "id":   { "type": "string", "format": "address", "x-scheme": "msg://" },
        "to":   { "type": "string", "format": "address", "x-scheme": "session://" },
        "verb": { "enum": ["deliver", "wake", "consult", "queued"] } } },
    "routed": { "enum": ["injected", "wake-spawned", "fork-spawned", "queued"] },
    "thread": { "type": "string", "format": "address", "x-scheme": "thread://" },
    "watch":  { "type": "object", "required": ["stream", "since"],
      "description": "the proof cursor: every consequence of this intent appears on this stream
                      after this seq, carrying intent_id + thread (correlation law)",
      "properties": {
        "stream": { "const": "events" },
        "since":  { "type": "integer" } } },
    "forks":  { "type": "array", "items": { "type": "string", "format": "address",
                "x-scheme": "session://" },
                "description": "present iff routed=fork-spawned; length == copies" } } }
```

### Errors
All four faces emit the uniform envelope `{error:{code,message,teach,details?,retryable}}` — the
per-face carrier (HTTP status, MCP tool-result JSON, CLI stderr+exit code) is defined once in
CONVENTIONS.md; every binding's error reality is evidence-captured at flip-to-live (§6 V11).

```contract:error
code: session.unknown            | http: 404 | retryable: false
when: `to` resolves to no registry record (calling blind is safe — unknown never creates)
teach: "List sessions via [[session#op: session.list]]; addresses come from the registry. Titles are
        ~100% populated only via the fallback chain — match on id, not title alone."
```
```contract:error
code: session.verb-state-conflict | http: 409 | retryable: false
when: explicit verb illegal for target state (e.g. deliver → closed)
teach: "Use verb=auto to let the router resolve by state, or [[session#op: session.get]] first.
        NOTE for drivers: receiving this after a passed pre-check is expected concurrency —
        verdict pass-via-refusal, not contract failure (§8 step 6)."
details: { "target_state": "closed", "legal_verbs": ["wake", "consult", "auto"] }
```
```contract:error
code: fabric.concurrency-cap     | http: 429 | retryable: true
when: copies would exceed the registry-served concurrency cap (teaching error, audit C9)
teach: "Read the cap via [[fabric-config#op: fabric-config.get]]; reduce copies or retry after a
        fork completes. Raising the cap is a recorded decision, not a retry."
details: { "cap": 3, "requested": 5 }
```
```contract:error
code: session.address-malformed  | http: 400 | retryable: false
when: `to` fails the session:// grammar
teach: "Address grammar is in [[session#Identity]]. Prefix with session://."
```

### Interaction semantics
- **Preconditions:** target exists in the registry (any state). Explicit verbs constrain:
  deliver → supervised-live · wake → closed · consult → any (operates on forks) · auto → always legal.
- **Effects/transitions:** per the fsm fence in [[session#State model]] — wake: closed →
  supervised-live (marked by agent_sessions.spawned). Consult: N new sessions; THE ORIGINAL IS NEVER
  WRITTEN (single-writer law; byte-identity probe-verified T4).
- **Durability:** intent durable on receipt (O_APPEND single-write jsonl); crash after receipt loses
  nothing; replies ride durable events.
- **Idempotency:** at-least-once with `intent_id` dedupe (see Request). Without intent_id, a retry
  after timeout MAY duplicate — stated, not hidden.
- **Ordering:** intents to one target consume FIFO; a consult fan's replies aggregate under the one
  returned `thread`.
- **Concurrency:** any number of senders; callers never race the supervisor (it is the sole writer
  to the session itself).

### Consequences & proof shape
Completion is **declared events appearing after `watch.since`, joined on `intent_id`/`thread`** —
never "the response looked ok" (event-sourced graft, the corpus's universal write-proof shape).
The consequences table in the opspec fence is the executable expectation: the driving harness reads
the stream from the cursor, joins on the correlation keys, and matches expect/bound/invariant rows.
Queued (absence-shaped) is evidenced by its named snapshot read.

### Live-ness
This op is `liveness: none` — the receipt is immediate; the aftermath is the stream. Observe via
[[session#op: session.watch]] (per-session) or [[events#op: events.watch]] (fabric-wide SSE,
`id:<seq>` frames, resume via Last-Event-ID, ~15s keepalive — mechanics owned by events.watch ONCE;
this section links, never restates, §10 C-C5). Poll alternative: [[session-message#op:
session-message.list]] with `since=`. Reply CONTENT dereference: agent_sessions.turn events carry
the reply as a `msg://` address — read it via [[session-message#op: session-message.get]] (no
dead-end addresses: every scheme in any response has accepting ops, §6 V7).

### Examples
```contract:example
captured: synthetic              # status=planned → synthetic legal AND loud; replaced by captured
                                 # evidence/runs/<id>/session.post.txt at flip-to-live (V11)
binding: mcp
request:  session_post(to="session://a3f9", message="What did you decide about facet chips?",
                       verb="consult", copies=3, from="session://caller1")
response: { "message": { "id": "msg://01J8", "to": "session://a3f9", "verb": "consult" },
            "routed": "fork-spawned", "thread": "thread://01J9",
            "watch": { "stream": "events", "since": 18204 },
            "forks": ["session://b1", "session://b2", "session://b3"] }
observed_events:                 # validated against [[events]] payload schemas, NOT just type names
  - { seq: 18205, type: agent_sessions.spawned, session: "session://b1",
      forked_from: "session://a3f9", intent_id: "int_77", thread: "thread://01J9" }
  - { seq: 18206, type: agent_sessions.spawned, session: "session://b2",
      forked_from: "session://a3f9", intent_id: "int_77", thread: "thread://01J9" }
  - { seq: 18207, type: agent_sessions.spawned, session: "session://b3",
      forked_from: "session://a3f9", intent_id: "int_77", thread: "thread://01J9" }
  - { seq: 18215, type: agent_sessions.turn, session: "session://b1", intent_id: "int_77",
      thread: "thread://01J9", reply: "msg://01JA" }
invariant_checked: "sha256(a3f9.jsonl) identical before/after"
```
```contract:example
captured: synthetic
binding: http
request: |
  POST /api/agent_sessions/a3f9/messages HTTP/1.1
  Content-Type: application/json
  {"to":"session://a3f9","message":"ping","verb":"deliver","from":"consumer://face-1"}
response: |
  HTTP/1.1 409 Conflict
  Content-Type: application/json
  {"error":{"code":"session.verb-state-conflict","message":"target state is closed",
   "teach":"Use verb=auto to let the router resolve by state, or session.get first.",
   "retryable":false,"details":{"target_state":"closed","legal_verbs":["wake","consult","auto"]}}}
```
(HTTP examples carry status lines and headers — the HTTP semantics layer is owned, §10 C-A2.)

### Adjacent ops
Before: [[session#op: session.list]], [[session#op: session.get]]. Observe: [[session#op:
session.watch]], [[events#op: events.watch]]. Read results: [[session-message#op:
session-message.list]], [[session-message#op: session-message.get]]. Cross-resource flow:
[[message-and-read-reply]] (journey).
~~~~

---

## 4 · Field semantics: status, verification, liveness, direction

### 4.1 `liveness` (per op)
`none | snapshot | watch | duplex | binary-stream`
- **none** — act with immediate receipt; aftermath rides streams (the watch cursor).
- **snapshot** — point-in-time read. MUST name its live twin (`live-twin:` key) or state
  `live-twin: none — static` explicitly. Silence fails (V13).
- **watch** — resumable stream. MUST document frame schema, resume mechanism (Last-Event-ID /
  `since=`), keepalive interval, termination semantics (V13). The `/api/stream` vs `/api/events`
  split is the canon: two ops, live-ness only on the stream.
- **duplex** — bidirectional interactive (computer-use, voice conversations). Documents both
  directions' frame schemas + session teardown.
- **binary-stream** — non-JSON frames (audio). Documents codec/container + chunk grammar.

`duplex`/`binary-stream` exist NOW so F7/F8 lanes don't hit a frozen vocabulary (§10 C-D1 —
pre-resolved, not bet against). The field→event→watch chain (§2 Representation) is the second half
of liveness: every volatile field is machine-traceable to the stream that fires when it changes.

### 4.2 `status` + `verification` (the one honesty axis — no free-text twin)
`planned | building | live | broken | retired`
- **planned** — contracted, no code. Bindings exempt from the reality join's existence check; if a
  planned binding APPEARS in reality, the checker flags "built-but-not-flipped" (loud both ways).
- **building** — code exists behind the binding; synthetic examples still legal, marked.
- **live** — requires ALL of: binding present in reality.json · every example
  `captured: <evidence ref>` (no synthetics) · ≥1 captured error example per binding ·
  harness-written `verification` rows. Flip is performed by the harness, never by hand.
- **broken** — WRITTEN BY THE CHECKER, not humans: a live op whose binding vanished from reality,
  whose evidence replay failed schema validation, or whose negative probe stopped refusing. Broken
  is loud in coverage.json and blocks F9 sign-off. This is the demotion lifecycle (§10 A-d6, B-b1).
- **retired** — removed deliberately, with a recorded decision ref.

**Verification grain is the consequence BRANCH (and per-binding for errors), never the file** — one
exercised branch can never green-paint its siblings (§10 B-d5). Verification rows carry
`{state, run, date, commit}`; evidence replay each harness run re-validates touched live ops against
current reality, so "verified once, asserted forever" cannot happen (§10 B-b1, A-b4, A-b5):
**evidence rot IS the regression check, and it is scheduled** — a fresh reality snapshot + replay of
all live ops' captured evidence is a precondition of every driving run.

### 4.3 `direction`
`outbound` (consumer calls system — the default) | `inbound` (system calls the consumer: hooks,
callbacks — atlas class 13). Inbound ops document the contract the CONSUMER implements: the request
the system will send, the response it expects, retry/timeout behavior. Same fences, inverted roles
(§10 C-D1).

---

## 5 · Exposure semantics (registry, not prose)

Values: `process-local | localhost-only | tailnet | authed`
- **process-local** — stdio/in-process (the company MCP server). No socket exists; network exposure
  vocabulary does not apply to it and is never forced onto it (§10 C-D7).
- **localhost-only** — bound to 127.0.0.1. The fabric's shipping default.
- **tailnet** — reachable over Tailscale serve. Requires `exposure-decision:` ref (audit B3).
- **authed** — authenticated network exposure. Requires decision ref + the auth model in
  TRANSPORTS.md. When auth lands with roles, role granularity is added IN THE REGISTRY — zero entry
  edits (§10 A-d5).

Bindings carry **registry keys** (`exposure.json#bridge-http`), never inline values. `exposure.json`
is GENERATED by `extract_reality.py` from ground truth: service bind config, tailscale-serve config,
unit files. The checker diffs registry vs actual binds — exposure lies are machine-caught at the
config layer, where the ground truth actually lives (§10 C-D3). Widening = one registry-source
change + one recorded decision; the corpus updates by regeneration, atomically, all entries at once.

**Vantage rule:** the harness tells the driving agent its vantage (localhost / tailnet); battery
tasks carry a vantage tag; coverage treats "affordance required from vantage X but only reachable
process-local/localhost" as a COVERAGE FAILURE, not a silent pass (§10 A-a5).

---

## 6 · Validation rules (`tools/validate.py` — repo test, fails loud)

**Static (run always):**
- **V1** frontmatter complete; enums valid; basenames unique corpus-wide; `summary:` present.
- **V2** every `contract:op` parses; verbs ∈ uniform set; named acts ∈ CONVENTIONS registry;
  `tasks:` non-empty (every op is reachable from the task index).
- **V3** every `contract:schema` is valid JSON Schema 2020-12; every example validates against its
  op's schemas; observed_events in examples validate against the EVENT entries' payload schemas
  (traces cannot be fiction-in-every-field, §10 B-b1).
- **V4** uniform envelope on every error; codes corpus-unique; every code carries `teach` naming an
  in-corpus recovery ref; state names in details ∈ the resource's fsm fence.
- **V5** purpose-free lint over Description/Semantics prose (seed list in CONVENTIONS; extendable,
  never shrinkable). `tasks:`/`alias:` fields are EXEMPT — they are the deliberate retrieval bridge
  to consumer vocabulary (§10 A-c2). Escapes need inline `lint-ok:` justification. The lint is a
  reflex-catcher; the driving test is the bar (§10 C-D6).
- **V6** ref closure over wikilinks AND string refs inside fences (teach/hint/evidence) — the ref
  extractor parses fence string fields too; renames go through tools/rename.py which uses the same
  extractor (§10 B-a6, B-d4).
- **V7** scheme closure + DEREFERENCEABILITY: every scheme has an owning entry AND ≥1 accepting op;
  every address-typed response field's scheme is dereferenceable (§10 A-a3, B-a5).
- **V8** chunk discipline: restatement-first on every H2; budgets; fences unsplit; restatement
  lines distinct corpus-wide (§10 B-c1, A-c1, A-c3).
- **V9** consequences law: every write op has `emits` or `consequences` (or both), each consequence
  row has when/expect/`bound` (or `unbounded-with-evidence:` naming the observable progress signal)
  (§10 B-a3); absence-shaped rows (`expect: []`) name an evidencing snapshot read (§10 B-a2).
- **V10** correlation law: every consequence row's event types carry the declared `correlate` keys
  in their payload schemas (§10 B-a1).
- **V11** evidence: `live` requires captured examples (success + error, PER BINDING) with refs under
  evidence/; planned/building synthetics are marked `captured: synthetic`; a live op with a
  synthetic FAILS (no green-paint).
- **V12** canon: no versioned filenames among canonical docs; generated files carry `generated:`
  headers and hand-edits fail; evidence/runs/ is the one sanctioned append-only ledger (§10 A-d3).
- **V13** liveness completeness per §4.1 (snapshot→live-twin; watch→frame/resume/keepalive/
  termination; duplex/binary documented).
- **V14** absence evidence + queued-class outcomes resolvable (subset of V9, checked at journey
  level too).
- **V15** fsm closure: transitions keyed by event types that exist in [[events]]; per-state legality
  matrix covers every op of the resource.
- **V16** field→event→watch chain: volatile fields name changed-by events; events name streams;
  streams name watch ops (§10 A-a4).
- **V17** task-index integrity: every op's `tasks:` rows render into TASKS.md; every out-of-scope
  affordance has a "not exposed" row (§10 C-A5, B-c4 — exclusions out-retrieve lookalikes because
  they are full entries with aliases AND indexed rows).
- **V18** atlas closure: every affordance id ∈ FEATURE-ATLAS.md; every affordance maps to ≥1 op or
  an OUT-OF-SCOPE row; zero silent gaps (affordance grain — partial classes expressible, §10 C-B4).
- **V19** journey closure: every journey's ordered op refs resolve; every multi-resource
  disambiguation named in a critique-class ("history vs live vs messages") has a journey (authored
  list in CONVENTIONS).
- **V20** single-source: frontmatter status/summary ↔ opspec fence equality; prose event names in
  Effects/Consequences sections ⊆ fence-declared (event-name lexicon cross-check, §10 C-A6, C-B9).
- **V21** transport closure: every binding's transport ∈ TRANSPORTS.md; every transport declares an
  inventory source and a caller-identity model; CLI is first-class from day one (§10 C-D2, C-A1).

**Reality rules (require the live system; if unreachable they FAIL LOUD `reality: unavailable` —
never stale-silent, §10 B-b5; a fresh reality.json is a driving-run precondition):**
- **V22** reality join, both directions, at (route,method) / (tool,op) / (cli,command) granularity:
  every in-scope reality pair ↔ exactly one op binding. Multiplexed ops on one endpoint use
  discriminator profiles with the partition rule: disjoint AND exhaustive against the CODE-SIDE enum
  (§9 obligations) — where the enum is corpus-only, exhaustiveness is verified by NEGATIVE PROBE
  (an out-of-contract discriminator value must be observed refusing) so the check is never circular
  (§10 C-B2, A-b3). Out-of-scope endpoints must appear in INVENTORY-EXCLUSIONS.md (§10 C-B1).
- **V23** MCP coherence: live tool inputSchemas ≡ the corpus union schema across that tool's ops
  (generated-from-contract or diffed-equal). The corpus and the tool's self-description can never
  disagree (§10 C-A3).
- **V24** exposure registry ≡ actual bind config (§5).
- **V25** evidence replay: every live op's captured requests re-sent (or schema-diffed for
  mutating ops via recorded replay transcripts), responses re-validated; failures demote to
  `broken` (§10 A-b4, A-b5, C-B5).
- **V26** event reality: observed event payloads (accumulated in evidence) validate against event
  entries; `producers: system` events must name a code ref the extractor confirms AND have ≥1
  observed instance — unobserved system events are flagged (§10 A-b7, B-b2).

---

## 7 · Coverage-map mechanism (F9.3) — two layers, three joins

`tools/coverage.py` builds `coverage.json`; a generated COVERAGE section in INDEX.md renders the
human/agent view.

**Layer 1 — CONTRACTED (claims):**
1. *Affordance → ops:* every CC-nn.m maps to ≥1 op (any status) or an OUT-OF-SCOPE row. Zero
   unmapped (F9.3's bar, at affordance grain).
2. *Ops → reality:* V22's join (statuses interpreted per §4.2 — planned exempt from existence,
   flagged when present).
3. *Ops → completeness:* all required fences/sections present (V-rules green).

**Layer 2 — DEMONSTRATED (proof — corpus tags are claims; task verdicts are proof, §10 A-b1):**
4. *Affordance → passed tasks:* battery tasks are tagged by atlas class+affordance BY THE BLIND
   AUTHOR (they have the Atlas — N1 grants it; they never have the contract). An affordance is
   demonstrated only when a task tagged to it reached verdict `pass`/`pass-via-refusal`. Load
   credit flows from task verdicts, not from corpus self-tags — op-level load can never smear
   credit across co-tagged affordances (§10 A-b1).
5. *Starvation:* `load.jsonl` records file reads AND substrate hits (the harness wraps both and maps
   chunk hits to entry files — retrieval acceleration never blinds the instrument, §10 B-b4).
   Zero-load entries and zero-demonstration affordances are flagged per run. Battery scaling rule:
   accumulated batteries must reach ≥1 task per in-scope affordance before F9 sign-off — the battery
   scales with the ATLAS, not the corpus, and "contracted-but-undemonstrated" is a visible reported
   state, never decoration (§10 C-B8).

**Verdict vocabulary** (harness-written): `pass | pass-via-refusal | fail | blocked-by-build | drop`.
`blocked-by-build` (task hit planned/building ops) keeps the retest cadence running on a
mixed-status corpus — no all-live gate, no ratchet deadlock (§10 C-B7). Drops land in
`coverage/drops.jsonl` → gap adoption (F10.1).

---

## 8 · How the corpus-only driving agent navigates

The agent receives ONE path: `~/company/ui-contract/`. It has plain filesystem read over the whole
tree (README states this — coverage JSONs are reachable; no unstated affordances, §10 C-C3).
Substrate semantic search over the vault is an ACCELERATOR; flat-file navigation MUST suffice
(§10 A-a7). The protocol, corpus-carried in README.md:

1. **Orient:** README → ontology + this protocol + your granted affordances + your vantage.
2. **Find the task:** TASKS.md first — intent phrases and aliases map straight to (op, params),
   including parameter-level affordances (wake/consult are index rows, never buried) and
   "not exposed locally" rows. Cross-resource tasks: check journeys/ (the index lists them).
   Fallback: INDEX.md resource table by noun; last resort: semantic search.
3. **Orient on the resource:** Identity → Representation → State model → Caller. The fsm tells you
   what is legal before you pick; Caller tells you who you are on your transport.
4. **Pick the op and binding:** uniform verb logic (show-many → list; observe-live → watch; cause →
   the named act). Binding by vantage: filter on the exposure registry — a tailnet face wires only
   tailnet/authed keys.
5. **Execute and PROVE:** for writes, take `watch` from the response, read the stream from the
   cursor, JOIN on the correlation keys, match the op's consequences rows within their bounds.
   Done = declared events appeared (or the named snapshot read evidences the absence-shaped
   outcome). For reads, done = response validates + any declared consistency cross-check holds
   (e.g. a just-created resource appears in its list — journeys carry these cross-checks; §10 B-S3:
   reads have a pass-shape).
6. **On refusal:** match `error.code`, follow `teach` (machine-checked to resolve in-corpus). A
   state-gated refusal after a passed pre-check is expected concurrency: verdict
   `pass-via-refusal`, not failure (§10 B-a4). Where multiple ops complete one task (auto-routing
   overlap), the harness scores the OUTCOME evidence, never the op choice (§10 C-A7).
7. **Hypermedia hops:** every address in any response → SCHEMES table → owning entry + accepting
   ops. Runtime values navigate the corpus the way links do, and every hop is dereferenceable by
   construction (V7).
8. **Reached-for-but-missing:** append to `coverage/drops.jsonl` `{task, looked_for,
   where_searched, ts}`. A missing affordance is a recorded gap-pressure event, never a dead end.

---

## 9 · Code-side obligations (the format imposes these on the fabric build — F1+ criteria)

The machine checks are only as real as the registries they read. These are BUILD requirements,
adopted into lane scope (scaffolding-not-spec law), without which V22–V26 cannot run:

1. **BRIDGE_ROUTES carries methods** for fabric routes (structured entries `(path, method)`;
   today's flat tuple is Observed at runtime/bridge.py:45 — methods are comments). The existing
   bidirectional dispatcher-drift test extends to the structured form.
2. **Every consolidated MCP tool module exports a closed `OPS` constant**; `extract_reality.py`
   FAILS LOUD on any tool module without one — the convention is machine-forced, not soft
   (§10 A-b2). Today ops live in if/elif (Observed) — this obligation lands with F1's first tool.
3. **The supervisor ships a `SUPERVISOR_ROUTES` registry** (same law as the bridge) before any
   supervisor binding is contracted. A transport with no inventory source fails V21 (§10 C-B3).
4. **MCP tool descriptions/inputSchemas are generated from the contract** (or CI-diffed equal —
   V23). One truth, two renderings.
5. **Uniform error envelope implemented on all faces** (bridge JSON, MCP tool-result JSON, CLI
   stderr JSON + exit map) — per-binding error evidence is a flip-to-live requirement (§10 A-a6).
6. **One emit helper + a code-side `EVENT_TYPES` registry**; the helper stamps `intent_id`/`thread`
   correlation keys on every fabric event (correlation law is enforced at the only writer).
7. **New address schemes (`session://`, `msg://`, `thread://`, `consumer://`) added to
   `contracts/address.py` SCHEMES** when F1 lands — they do NOT exist today (Observed; §0).
8. **Vault registration check:** at `add_vault ui-contract`, verify the substrate chunker's actual
   unit splits on headings and never mid-fence; if it doesn't, configure heading-chunking before
   indexing (§10 C-C1 — checked at registration, not assumed).

---

## 10 · Dialectic resolutions ledger — every critique finding, resolved

Format: **finding → resolution** (section refs are into this spec). "Eliminated by spine" = the
failure was load-bearing in a losing lens and the synthesized format does not contain the mechanism
that produced it.

### Critique A (vs the resource-oriented proposal — all adopted as repairs)
- **A-a1 verb burial / no synonym layer** → `tasks:` per op + GENERATED TASKS.md with
  parameter-level rows and lint-exempt aliases (§3 opspec, §1, V2/V17). "Resume a closed session" is
  an index row pointing at session.post(verb=wake).
- **A-a2 overlapping message-nouns** → journeys/ kind carries the cross-resource disambiguation
  ("transcript for history + watch for live"); V19 requires journeys for the named ambiguity
  classes (§1, §6).
- **A-a3 closure proves owners not dereferenceability** → SCHEMES rows carry accepting ops; V7
  checks every response scheme is dereferenceable. thread:// has an accepting op
  (session-message.list(thread=)) in the worked example.
- **A-a4 two disconnected liveness vocabularies** → field→event→watch machine chain: `changed-by`
  column + V16 (§2, §6).
- **A-a5 exposure vantage blindness** → vantage told to agent + vantage-tagged battery tasks +
  coverage failure when an affordance is unreachable from its required vantage (§5, §7).
- **A-a6 error envelope only real on HTTP** → envelope is a cross-face code obligation (§9.5);
  per-binding captured error evidence required at flip-to-live (V11).
- **A-a7 substrate fallback may not exist** → search demoted to accelerator; flat-file navigation
  must suffice (§8, graft from B). The embedding-model decision (Tim's, open) no longer blocks the
  driving test.
- **A-b1 atlas self-tag gaming + load-granularity smear** → two-layer coverage: demonstrated credit
  flows from blind-author-tagged task VERDICTS, never corpus self-tags; affordance grain (§7).
- **A-b2 MCP op-set convention unenforced** → extractor fails loud on missing OPS constant —
  machine-forced (§9.2).
- **A-b3 "exactly one binding" vs consolidated tools** → join at (tool,op)/(route,method) pair
  granularity + discriminator partition rule (§6 V22). Multiplexing is first-class, not forbidden.
- **A-b4 schemas never diffed against reality / evidence never replayed** → V25 evidence replay
  every harness run; failures demote to broken.
- **A-b5 changed-not-removed endpoints invisible / no scheduled regression** → fresh reality
  snapshot + evidence replay are PRECONDITIONS of every driving run (§4.2, V25) — rot detection is
  scheduled, not hoped for.
- **A-b6 status/verified two axes, one policed** → single status axis + harness-only per-branch
  verification rows; no free-text twin (§4.2).
- **A-b7 V13 event tautology (no Side B for events)** → code-side EVENT_TYPES registry in
  reality.json (§9.6) + observed-payload validation V26. Events are reality-checked by registry AND
  observation.
- **A-c1 flagship example violates own chunk budget + fence/restatement order contradiction** →
  budget raised to realistic 180/600 with a specified overflow rule; order fixed: restatement line
  FIRST, fence second, stated once in §2/§3 (no contradiction).
- **A-c2 V5 severs the embedding bridge to real queries** → the aliases channel: consumer-language
  retrieval bait in `tasks:`/`alias:`, lint-exempt by rule (V5). Purpose-free governs meaning-prose;
  retrieval gets its own sanctioned slot.
- **A-c3 no restatement rule for non-op chunks** → restatement-first applies to EVERY H2 (§2, V8).
- **A-c4 generated renders pollute embedding space** → generated machine artifacts are .json
  (outside the markdown scan); the one COVERAGE render lives inside INDEX.md as tables, and INDEX
  is short by construction (§1).
- **A-c5 search_by_address over arrays unverified** → no design dependency on it: TASKS.md/INDEX.md
  carry the mappings as plain markdown rows; structural search is a bonus, never an axis the
  protocol needs (§8).
- **A-d1 CONVENTIONS.md choke file** → named-act registry is append-only one-line-per-act
  (merge-clean); acts beyond cross-resource ones are declared per-resource; INDEX/TASKS are
  generated, so lanes never hand-edit shared tables (§1).
- **A-d2 INDEX declared generated but carrying authored prose** → split: README.md authored
  (protocol), INDEX.md generated (tables), descriptions sourced from frontmatter `summary:` (§1, §2).
- **A-d3 evidence dated filenames vs no-versioning** → explicit ruling: evidence/runs/ is an
  append-only EVENT ledger, not document versions; the no-versioning law governs canonical
  documents (§1, V12).
- **A-d4 frozen-with-appended-rulings drifts** → rulings are edited INTO the body in place;
  changelog records the change; the body is always current (§0, §11).
- **A-d5 exposure hand-stated per binding × ops** → exposure registry with binding-side KEYS;
  generated from service config; role granularity lands in the registry, zero entry edits (§5).
- **A-d6 no demotion lifecycle** → `broken` status, checker-written (§4.2).
- **A-factual-1 session:// claimed existing** → corrected in §0: planned schemes, code obligation
  §9.7; the format's status machinery is built for contracting an unbuilt system.
- **A-factual-2 prep docs unaddressable** → they exist at this directory
  (`…/build-prep/Session Fabric — *.md`, verified 2026-06-11); this file lives beside them and
  cites them by relative location (§ header).

### Critique B (vs the event-sourced proposal)
- **B-S1 flagship fails its own reality gate / no planned status** → status vocabulary includes
  planned/building with per-status reality-join semantics; unbuilt vs renamed are DISTINGUISHED
  (planned+absent = fine; live+absent = broken; planned+present = built-but-not-flipped flag)
  (§4.2). The worked example is honestly `planned`.
- **B-S2 consequence_events undefined yet load-bearing** → `consequences:` is a first-class opspec
  key with required structure (when/expect/bound/correlate/invariant/evidence) and V9/V10 enforce
  it (§3, §6).
- **B-S3 reads have no pass-shape** → reads declare consistency cross-checks; journeys carry
  read-after-write checks; verdict rules in §8 step 5. (The full snapshot≡fold check died with the
  projection kind — see B-b3.)
- **B-S4 one-entry-per-op vs per-route contradiction** → resource spine: one op section per logical
  operation; bindings list; reality join at pair granularity (§6 V22). Unambiguous.
- **B-a1 watch-window false-PASS under concurrency** → correlation law: `correlate:` keys mandatory
  on every consequence event, matcher joins on them, enforced at the single writer (V10, §9.6).
- **B-a2 queued/absence unverifiable** → absence-shaped consequence rows MUST name an evidencing
  snapshot read; the intent queue is contracted readable (session-message.list(status=queued))
  (V9/V14, worked example).
- **B-a3 unbounded waits** → every consequence row carries `bound` or
  `unbounded-with-evidence: <progress signal>` — explicit, never silent (V9).
- **B-a4 TOCTOU verdict ambiguity** → `pass-via-refusal` verdict + the rule stated in the error's
  own teach text and the protocol (§8 step 6).
- **B-a5 cas:// dead end in the proof example** → dereferenceability law V7; the worked example's
  reply rides `msg://` with session-message.get accepting it; any cas:// surfaced to consumers
  requires an accepting op or it cannot appear in a response schema.
- **B-a6 prose/teach refs unchecked** → ref extractor covers fence string fields; V6; rename.py
  uses the same extractor (so B-d4's rename pain is tooled too).
- **B-a7 no flow/journey kind** → journeys/ is a first-class authored kind with V19 closure (§1).
- **B-b1 reality join verifies existence not truth** → negative probes (closed enums/
  additionalProperties verified by observed refusal), observed-event payload validation (V3/V26),
  evidence replay each run (V25), verification rows pinned to run+date+commit (§4.2). Truth is
  checked by probing and replaying, not by name-matching.
- **B-b2 producers:system escape hatch** → system events need a code ref the extractor confirms +
  ≥1 observed instance (V26).
- **B-b3 fold-derivability unexecutable** → eliminated by spine: no projection kind, no fold
  interpreter. Representation honesty is field-reality columns + evidence replay — executable
  checks only.
- **B-b4 load-log blind under substrate search** → harness logs substrate hits and maps chunks to
  entry files; both feed load.jsonl (§7.5).
- **B-b5 reality regen with system down** → reality rules fail loud `reality: unavailable`; fresh
  snapshot is a driving precondition; stale-silent is impossible by rule (§6).
- **B-b6 class-grain coverage hides affordance holes** → affordance grain throughout, partial
  exclusion expressible (§1 atlas/, §7, V18).
- **B-c1 formulaic anchor prose** → restatement lines must be distinctive; corpus-wide duplicate
  lint (V8).
- **B-c2 templated H2 near-duplicates cluster by section type** → structurally reduced by the
  resource spine (one session.post section, not three sibling verb files); distinctive restatements
  + aliases carry the capability signal (§2).
- **B-c3 no joins over the corpus itself** → the resource file IS the per-capability join (command
  + state + events + errors in one file); TASKS.md and journeys are the generated/authored
  cross-joins (§1).
- **B-c4 weak out-of-scope entries lose to lookalikes** → exclusions are full entries (what it
  would be, why excluded, what to do instead, aliases) + indexed "not exposed" rows in TASKS.md
  (V17).
- **B-d1 coupling concentrated on shared stream/event files** → eliminated by spine: events.md is
  ONE catalog resource (append-per-lane, line-disjoint additions); state machines live inside their
  resource's file; lanes own disjoint nouns.
- **B-d2 validator frozen before the country exists** → §11: validator evolves WITH the format via
  recorded decisions (the company-CLI UPDATING law applied here); liveness vocabulary pre-extended
  (duplex/binary-stream) and direction:inbound pre-added so known F2–F8 pressure is absorbed now.
- **B-d3 junk machines for stateless commands** → `State model: stateless.` is legal and explicit
  (§2).
- **B-d4 no rename mechanism** → tools/rename.py on the shared ref extractor (§1, V6).
- **B-d5 file-grain verification green-paints branches** → verification grain = consequence branch
  + per-binding error evidence (§4.2). The worked example shows exactly one branch probe-verified,
  three honestly unverified.
- **B-d6 250–350 files + unbudgeted fold engine** → eliminated by spine: ~1 file per noun + a few
  journeys; no fold interpreter exists or is needed.

### Critique C (vs the capability-verbs proposal)
- **C-A1 caller identity absent** → Caller section per resource + per-transport identity models in
  TRANSPORTS.md + `from` explicit-required on non-session transports (worked example Request) +
  V21. Inbox reads are parameterized by explicit consumer id, never implicit.
- **C-A2 HTTP bindings missing the HTTP** → error fences carry `http:` status; CONVENTIONS owns the
  envelope↔status/headers mapping once; HTTP examples carry status lines (worked example).
- **C-A3 corpus vs live tool-description divergence** → V23 + §9.4: tool inputSchemas generated
  from or diffed-equal to the contract union. One truth.
- **C-A4 task-shape claim contradicted by N1 blindness** → resolved structurally: nouns are the
  stable unit; TASK-shaped access is a GENERATED, freely re-clustered index — no frozen taxonomy
  for the blind battery to miss, and the resource table catches noun-phrased tasks regardless of
  intent grouping (§1, §8 step 2).
- **C-A5 exclusions unreachable from navigation routes** → exclusion rows in TASKS.md + full-entry
  exclusions with aliases + filesystem access to coverage explicitly granted (V17, §8).
- **C-A6 fence/prose drift in the flagship example, mechanism asserted not designed** → the drift
  check is designed: V20's event-name lexicon cross-check (prose event mentions ⊆ fence-declared) +
  fence-vs-frontmatter equality. Concrete rules, not "CI flags it."
- **C-A7 sibling-verb confusability / verb-ambiguous task completion** → one op, parameters
  documented in one place (resource spine kills the sibling files); auto-routing overlap is scored
  on OUTCOME evidence per §8 step 6.
- **C-B1 validator dead-on-arrival against harness routes** → INVENTORY-EXCLUSIONS.md: endpoint-
  grain, reasoned, counted, loud — the disposable harness is excludable without hand-editing the
  generated inventory and without silence (§1, V22).
- **C-B2 partition rule circular (no code-side enum)** → §9.2 OPS constants (machine-forced) give
  the code-side set where it can exist; where the discriminator is corpus-only, exhaustiveness is
  verified by NEGATIVE PROBE — refusal of an out-of-enum value is observed evidence, not
  self-reference (V22).
- **C-B3 supervisor has no inventory source** → V21: a transport without a declared machine-
  readable inventory source fails validation; §9.3 obliges SUPERVISOR_ROUTES before any supervisor
  binding is contracted. Neither phantom-fail nor silent-skip can occur.
- **C-B4 class-grain coverage gameable / partial exclusion inexpressible** → affordance grain for
  both coverage and exclusions (§1, §7, V18) + demonstrated-layer credit only from task verdicts.
- **C-B5 examples validate against schemas, never reality** → evidence capture at flip-to-live
  (V11) + replay each run (V25) + field-reality columns harness-refreshed (§2). The example layer
  cannot remain authored fiction past `building`.
- **C-B6 no global error/state registries** → corpus-unique error codes (V4) + state names closed
  against the fsm fence (V4/V15).
- **C-B7 all-live gate deadlocks the retest cadence** → no such gate; `blocked-by-build` verdict;
  driving runs on mixed-status corpora (§7).
- **C-B8 starvation is statistical noise at 25 tasks** → battery scales with the atlas
  (≥1 task per in-scope affordance accumulated before F9 sign-off); per-branch verification keeps
  unverified branches honestly visible rather than decorated (§7.5, §4.2).
- **C-B9 frontmatter unvalidated against fences** → V20 equality check; fence is the single machine
  truth; frontmatter is derived/checked (§3).
- **C-C1 fence-dominated entries embed as JSON noise / mid-fence chunking** → prose-first
  restatements on every H2, prose-led descriptions, fences never split (V8), chunker behavior
  verified at vault registration (§9.8).
- **C-C2 near-duplicate verb files** → eliminated by spine: one op section per logical operation.
- **C-C3 route-3 navigation outside the retrieval surface** → filesystem read of coverage JSONs
  explicitly granted in README; navigation never depends on embedding the JSONs (§8).
- **C-C4 two link grammars, two resolvers** → one grammar: basename wikilinks + corpus-unique
  basenames (V1); V6 resolves them the same way traverse_links does (basename-first); no
  relative-path links.
- **C-C5 duplicated SSE mechanics prose drifts** → mechanics owned by ONE entry (events.watch);
  other entries link, never restate — stated as a rule in the worked example's Live-ness section.
- **C-D1 inbound/duplex/binary classes inexpressible + "no post-freeze pressure" falsified** →
  direction:inbound + duplex/binary-stream liveness exist NOW (§4.1, §4.3); plus §11's evolution
  path for the genuinely unforeseen. The format bets WITH the pressure, not against it.
- **C-D2 CLI transport missing** → CLI bindings first-class from day one (§3 worked example, V21).
- **C-D3 exposure widening = corpus-wide manual sweep, no ground truth** → registry keys + values
  extracted from service config; checker diffs registry vs actual binds — ground truth is the
  config layer, and it IS machine-readable (§5).
- **C-D4 V3+V7+V18 mutually unsatisfiable for fat ops** → realistic budgets (180/600) + specified
  examples-overflow section (§2). No rule collision.
- **C-D5 taxonomy debt frozen at lane-closure order** → the task index is generated and
  re-clusterable at any time; resources are the stable unit; nothing structural is owned by
  whichever lane closed first.
- **C-D6 lint is a token blacklist doing a semantic job** → acknowledged AS a proxy (V5): reflex-
  catcher only, aliases channel legitimizes consumer vocabulary where it belongs, the driving test
  is the real bar. Parameter-design purpose-leakage is caught by the dialectic/review layer, not
  lexically — stated honestly rather than overclaimed.
- **C-D7 localhost-only for stdio is a category error** → `process-local` exposure value (§5).
- **C-D8 three copies of every header fact** → single machine truth in the fence; frontmatter
  checked-equal (V20); prose summaries sourced from frontmatter; exposure values not in entries at
  all (registry keys).

---

## 11 · Freeze & evolution discipline

- Entry CONTENT: updates freely, in place, forever. No versions, no dated copies.
- FORMAT (this file + validate.py, which ship and evolve TOGETHER, same commit): changes only via a
  recorded decision; the change is edited into the body where it belongs; one changelog line lands
  at the bottom of this file (`<date> · <decision ref> · <what changed>`). A fresh lane reading the
  body always reads current law — there is no appendix that quietly supersedes it.
- This format's own driving test: V1–V26 implemented and green on the F1 lane's first entries,
  including one deliberate violation per rule class proving each check fails loud, BEFORE F1
  contract entries are declared done. The format is verified the same way everything else is — by
  use.

## Changelog
- 2026-06-11 · P0.3 synthesis · Frozen from the 3-lens dialectic (resource spine; event-sourced
  proof-shape and capability-verbs task-index grafts; all 83 critique findings resolved in §10).
