# Session Supervisor + CLI + Fabric — Research for an OpenWebUI Fabric Integration

**Scope:** how the session supervisor works, the EXACT message-injection mechanism (the load-bearing
fact for whether a non-Claude-Code web UI can receive fabric messages), the `company` CLI, how a
Claude Code session integrates, and the full operation set the supervisor exposes.

**Method:** read-only. Files read in full: `runtime/session_supervisor.py` (1712 lines),
`channels/company_channel.mjs`, `runtime/cc_channels.py`, `channels/claude-fabric.sh`,
`runtime/cc_clone.py`, `ops/cli/app.py`, `ops/cli/sessions.py`, `mcp_face/tools/cc_channel.py`,
`mcp_face/tools/sessions.py`, `store/fs_store.py:1369-1428` (`append_agent_mail`),
`channels/channel.mcp.json`, `ops/services.json` (supervisor row), the systemd unit. Live check:
`curl http://127.0.0.1:8771/health` → supervisor is UP (cap 3, turn_timeout 900s, permission `plan`).

Evidence is classified **Observed** (read directly in code), **Verified** (confirmed by execution —
only the live `/health` ping), or **Inferred** (pattern-matched, labelled as such). Most of this is
Observed.

---

## 0. THE CRUX FIRST — two injection mechanisms, and which one a web UI can use

This is the load-bearing finding. There are **TWO entirely separate ways** a message lands in a
running session, and they have **opposite implications** for a non-Claude-Code client.

### Mechanism A — the `<channel>` tags (Claude-Code-only; a web UI CANNOT receive these)

**Observed.** The `<channel source="company-channel" from="..." thread="...">` tags that appear
inside a live Claude Code conversation are produced by a Claude-Code-specific experimental MCP
capability. The chain (`channels/company_channel.mjs`):

1. Each interactive Claude Code session launches `company_channel.mjs` as an **MCP server** (stdio),
   declaring `capabilities.experimental['claude/channel']` (`company_channel.mjs:80`). This requires
   the launch flag `--dangerously-load-development-channels server:company-channel`
   (`channels/claude-fabric.sh:20`).
2. That same `.mjs` process **also opens its own HTTP listener on a random localhost port**
   (`server.listen(PORT, '127.0.0.1', …)`, `company_channel.mjs:157`) and writes a registration file
   `.data/channels/<handle>.json` carrying `{handle, session_id, cwd, description, model, profile,
   pid, claude_pid, port, started}` (`regEntry`, `:55`).
3. An external `POST http://127.0.0.1:<that-port>` with `{content, meta}` is turned into an MCP
   **notification** `notifications/claude/channel` (`company_channel.mjs:151`).

**Inferred (NOT directly observed in this repo):** that the Claude Code *client* renders that
notification as the `<channel>` tag in the live conversation. What I observed is the `.mjs`
*emitting* the notification; the rendering happens inside the closed Claude Code runtime, which I
cannot trace from here. The inference rests on three real signals: (a) the experimental capability is
named `claude/channel` (`company_channel.mjs:80`), (b) the launch requires the Claude-Code-specific
flag `--dangerously-load-development-channels server:company-channel`, and (c) the company-channel
MCP server's own `instructions` string tells the session "Messages from the Company fabric arrive as
`<channel source=…>` tags … injected live" (`company_channel.mjs:81-82`). I have not verified the
client-side render by execution; if needed it is confirmable against the Claude Code Atlas
`claude/channel` docs.

**Why this matters for the web UI:** the `<channel>` tag delivery depends on a feature *inside the
Claude Code client* (`claude/channel` + `--dangerously-load-development-channels`). A browser /
OpenWebUI front-end is not a Claude Code client, so it **cannot receive `<channel>` tags by this
path.** This mechanism is for hand-launched interactive Claude Code sessions only. (`cc_clone.py:8-14`
states this explicitly: "Channels fire only in INTERACTIVE sessions.")

### Mechanism B — the supervisor's held-open stdin (HTTP-driven; THIS is the web-UI path)

**Observed.** For sessions the **supervisor owns**, injection is pure HTTP + a held-open stdin pipe,
with NO dependency on the Claude Code client's channel feature:

1. The supervisor spawns `claude -p --input-format stream-json --output-format stream-json --verbose`
   and **holds stdin open** (`subprocess.Popen(..., stdin=PIPE, ...)`, `session_supervisor.py:860`).
2. To inject a turn, `inject()` writes one JSON line to that stdin:
   `{"type":"user","message":{"role":"user","content":[{"type":"text","text": <message>}]}}` then
   flushes (`session_supervisor.py:1131-1142`). The T2 finding the module cites: a `claude` process
   held open under `--input-format stream-json` **accepts injected turns while idle, same session_id,
   full memory.**
3. Output (the assistant's reply, tool calls, the final `result`) streams back on stdout as
   stream-json; the supervisor's `_reader` thread parses it (`session_supervisor.py:1028-1071`) and
   **fans every event to HTTP subscribers** on `GET /watch?session=<id>` as ndjson
   (`:1533-1571`).

**This is the integration seam for a web UI.** A browser/OpenWebUI backend talks ONLY to the
supervisor's HTTP API on `127.0.0.1:8771`: `POST /inject {session, message}` to send a turn,
`GET /watch?session=<id>` (ndjson stream) to receive the reply token-stream and the final `done`
event. No Claude Code client feature is involved. The `done` event carries
`{type:"done", result, claude_session_id, num_turns, is_error}` (`:1095`).

### The bridge that already unifies both — the **"supervised" channel transport**

**Observed — this is the most important pre-existing fact for the build.** `runtime/cc_channels.py`
already abstracts over BOTH mechanisms via a per-member `transport` field (`_transport_of`, `:59`):

- `transport:"channel"` → push by HTTP POST to the member's own random port (Mechanism A).
- `transport:"supervised"` → push by `POST <supervisor>/inject {session, message}` (Mechanism B),
  and because a supervised session has **no channel `reply` tool of its own**, cc_channels lazily
  starts a per-member daemon that tails `GET /watch?session=<id>` and **folds the supervisor's `done`
  event back into `route_reply`** — synthesising the reply the member would otherwise have sent
  (`_push_supervised` + `_supervised_watch_loop`, `cc_channels.py:232-346`).

So the fabric **already** has a transport that lives entirely on supervisor HTTP and needs no
in-client channel feature. An OpenWebUI/web client slots in as a member registered under
`.data/channels/<handle>.json` dispatched by `_transport_of` (`cc_channels.py:59`). **But which
template fits depends on the web UI's ROLE** — driving a claude session reuses the `"supervised"`
fold as-is; being a fabric *peer* needs a genuinely new transport. See §8 for the two roles and why
they need different plumbing (this distinction is the build's load-bearing decision).

---

## 1. The supervisor service — what it is, transport, lifecycle

**Observed.**

- **Process / bind:** one long-running Python service, `runtime/session_supervisor.py`, binding
  **`127.0.0.1` ONLY** (the EXPOSURE law, audit B3 — *there is deliberately no env var to widen the
  bind*; any wider exposure is a code change + recorded decision, `:11-13`). Default port **8771**
  (`DEFAULT_PORT`, the single number `services.json` + the systemd unit + contracts all cite).
- **Transport:** plain **HTTP/1.1** via stdlib `ThreadingHTTPServer` (`:1707`). `GET /watch` is a
  long-lived **ndjson** stream (`Content-Type: application/x-ndjson`, replay-then-live, 15s keepalive
  lines, `:1533-1571`). No WebSocket. JSON request/response otherwise.
- **What it owns:** N concurrent `claude` subprocesses. It is the **only** process that launches/
  resumes claude (ONE-OWNER-PER-SESSION + the single-writer law: only the supervisor emits
  `agent_sessions.*` events, `:14-19`). Idle = it owns nothing; subprocesses spawn on demand.
- **Session state machine:** `starting → idle ⇄ busy → closed` (terminal). `Supervised` class holds
  the proc, an in-memory `events` deque (maxlen 500), and `subscribers` (one Queue per `/watch`
  client) (`:471-512`).
- **Two background threads:** `watchdog_loop` (per-turn wall-clock reaper, `COMPANY_FABRIC_TURN_
  TIMEOUT_S` default 900s; also reaps a session stuck in `starting`, `:1197-1215`) and `mailbox_loop`
  (consumes the intent leaf, below).
- **No orphans:** every owned subprocess is terminated on teardown / SIGTERM / SIGINT / atexit; under
  systemd the cgroup is the second net (`:1696-1703`, unit `KillMode` via cgroup).
- **Managed by:** systemd **user unit** `company-session-supervisor.service`
  (`ExecStart=.venv/bin/python runtime/session_supervisor.py 8771`, `Restart=on-failure`,
  `PartOf=company.target`). On-demand only — nothing auto-starts at boot (`services.json` note).
- **Postures (call-time env reads — flip without code change):** `COMPANY_FABRIC_CONCURRENCY`
  (default 3, caps live sessions AND consult fan copies; over it → a *teaching* refusal naming the cap
  and how to free a slot), `COMPANY_FABRIC_PERMISSION` (default `plan` = read-only; acceptEdits is
  opt-in), `COMPANY_FABRIC_TURN_TIMEOUT_S` (default 900).

---

## 2. The supervisor HTTP API — the full operation set

**Observed.** `SUPERVISOR_ROUTES` (`:127-136`) is the machine-readable registry; the dispatch
literals must match it (drift-tested by `tests/supervisor_routes_acceptance.py`). Endpoints:

| Method | Path | Body / query | What it does |
|---|---|---|---|
| GET | `/health` | — | `{ok, service, bind, sessions:{total,by_state}, cap, turn_timeout_s, permission}` |
| GET | `/sessions` | — | every owned session's `record()` (id, claude_session_id, name, cwd, state, turns, pid, close_reason, profile) |
| GET | `/watch` | `?session=<id>` | **ndjson event stream** for one session — replay of buffered events then live (`init`/`text`/`tool`/`done`/`injected`/`declared`/`closed`/`keepalive`) |
| POST | `/spawn` | `{cwd?, resume?, fork?, name?, prompt?, source?, model?, effort?, fallback?, permission_mode?, settings?, add_dir?, output_format?, include_partial?, debug?, safe_mode?, bare?, flags?, provider?}` | launch a supervised session (new / `--resume` wake / `--resume --fork-session` consult); optional `prompt` injects the first turn |
| POST | `/inject` | `{session, message, source?}` | inject a user turn into an idle supervised session (refuses if busy/closed, teaching) |
| POST | `/interrupt` | `{session}` | write a `control_request{subtype:interrupt}` to stdin (HONEST: built-untested vs a real turn; watchdog is the backstop) |
| POST | `/teardown` | `{session}` | terminate + close one session |
| POST | `/bridge-session` | `{operator_consent, capabilities?, extra_tools?, cwd?, resume?, fork?, name?, prompt?, permission_mode?, model?, …}` | **RAIL R1-prime**: consent-gated spawn with a WIDER allowlist (Bash/git/LSP-family/web + mcp__company) + in-session write posture |
| POST | `/channel-reply` | `{from, thread, text}` | a Claude Code channel session's `reply` tool calls here → records in channel mail + pushes back into the asking session (`cc_channels.route_reply`) |
| POST | `/channel-send` | `{to, message, from?, thread?, topic?}` | HTTP twin of `cc_channels.send` — message INTO a live channel member (record + push) |

Note: `/channel-reply` and `/channel-send` are **not** in `SUPERVISOR_ROUTES` but ARE handled in
`do_POST` (`:1636-1652`) — they are the channel-fabric's HTTP hooks living on the supervisor port.

**Error semantics (teaching, never bare):** consent-gate refusal → **403**; concurrency cap →
**429**; state/boundary conflict (busy/closed/rail-boundary) → **409**; bad body → 400; internal →
500 (`:1672-1684`).

---

## 3. Spawn — what can be configured / loaded / extended

**Observed.** Two builders, both PURE (unit-testable without spawning):

- `_build_spawn_cmd` (`:612-695`) — the floor. Fixed transport head: `-p --input-format stream-json
  --output-format stream-json --verbose --permission-mode <p> --mcp-config <strict company MCP>
  --strict-mcp-config --allowedTools mcp__company`. Optional params thread through:
  `model/effort/fallback/permission_mode/settings/add_dir/output_format/include_partial/debug/
  safe_mode/bare`. When none passed, the cmd is byte-identical to the original.
- **`provider='ollama'`** (`:651-655`) runs `ollama launch claude --model <tag> -- <claude args>`
  (NOT an ANTHROPIC_* env overlay — Tim 2026-06-16 direct; a logged-in Claude Code ignores env and
  rejects the ollama model name, so the launcher redirects despite the stored login). PATH fix
  prepends the resolved claude dir so the bare `claude` name resolves under systemd's PATH.
- **`flags` (the registry-declared start-flag surface)** — `SPAWN_FLAG_ASSEMBLY` (`:258-373`) is the
  consumer-emission table for ~40 Claude Code CLI flags (session_id, name, continue, system-prompt
  family, max_turns, max_budget_usd, json_schema, agent/agents, setting_sources, plugins, add_dir,
  betas, teammate_mode, etc.). Each flag's **posture (locked | consent | safe)** is DERIVED from the
  Mirror-Registry rules (`_registry_posture`, `:400-409`) — the registry is the sole truth.
  - `safe` → applied on a plain `/spawn`.
  - `consent` (surface-widening: `allowed_tools`, `mcp_config`, `tools`, `add_dir`, plugins, …) →
    refused on plain `/spawn`, teaching the `/bridge-session` path; applied when `operator_consent`
    rides the call.
  - `locked` (transport invariants like `--input-format`, `-p`, `--verbose`; or dedicated body keys)
    → always refused, teaching the right body key.

**`/bridge-session` (RAIL R1-prime, `:895-989`)** — the consent-gated wider profile. `capabilities`
map to tools: `git→Bash`, `lsp→Read,Edit`, `web→WebFetch,WebSearch`, `edit→Edit,Read`. `computer`
and `browser` are **host/rail boundaries** refused LOUD (computer-use is macOS+interactive only,
never on a `-p`/Linux/WSL2 rail; Chrome browser is beta + not-WSL). Default permission `acceptEdits`.
Results ride back as **PROSE on the turn stream** (`liveness:stream`, no typed return shape).

**What you can "load into"/configure/extend, summarised:** the model & backend (Anthropic/ollama/
litellm-proxy via `provider`+`model`+`fallback`), effort, permission posture, settings, extra dirs,
the system prompt (append or replace), agent/persona definitions, output format, partial-message
streaming (the voice delta seam), the tool surface (floor `mcp__company` → wider via `/bridge-session`
+ consent), and any registry-declared CLI flag. Adding a *new* configurable flag = a new
`SPAWN_FLAG_ASSEMBLY` row + a Mirror-Registry signal (Atlas-grounded, never invented).

---

## 4. The mailbox tier — `session_post` → intent leaf → supervisor (wake/consult dormant sessions)

**Observed.** This is how an agent reaches a NOT-live session (the brief's "wake/consult dormant
sessions"). It is **coordinate-by-contract**: the MCP face only *appends an intent*; the supervisor
*acts*.

- Agent calls MCP tool **`session_post(to, message, verb, copies, from_session, thread, at)`**
  (`mcp_face/tools/sessions.py:299-479`). It NEVER spawns — it appends one record to
  `agent_sessions/mail.jsonl` via `store.append_agent_mail` (`fs_store.py:1369`, which mints
  cross-process-unique `seq`/`id`/`ts` and defaults `thread`, fsync'd).
- **Verbs are routing decisions** (`:58-63` of the supervisor): `deliver` → inject into a live owned
  session; `wake` → `spawn(--resume)` a closed session then inject; `consult` → `spawn(--resume
  --fork-session)` N forked copies (original byte-identical, T4), fan ≤ cap. `auto` routes by live
  state (supervised-live→deliver · closed→wake · else→queue). `at=compact:N|uuid:..|ts:..` →
  **point-in-time launch** (materialise the transcript prefix at that moment, launch the copy;
  original never touched).
- The supervisor's `mailbox_loop`/`_mail_pass`/`_handle_intent` (`:1263-1424`) consume the leaf via a
  durable byte-offset **cursor ref** `agent_sessions/cursor:supervisor`. Strictly in order; an intent
  whose target is mid-turn **holds the cursor** (head-of-line, retried next poll) so a crash never
  skips it. Replies/errors are appended to the SAME leaf (`verb: reply|error`, `re`=intent id,
  `thread`=intent thread) and the turn is claimed as a durable `agent_sessions.turn` event.
- The agent reads replies via **`sessions(op='inbox', session=<from_session>, thread=<thread>)`** —
  client-held cursor, no destructive consume. Other read ops: `list` (the fleet), `describe`,
  `watch` (live `agent_sessions.*` events), `search` (content search over transcripts → live
  handles), `timeline` (compaction points, launchable via `at=`).

**Relevance to a web UI:** a web client could drive the fabric *either* directly over supervisor HTTP
(synchronous, owns the session) *or* through this mailbox (asynchronous intents, supervisor acts) —
but the mailbox path requires the target to be in the agent-session registry, whereas direct
`/inject` + `/watch` is the simplest seam for a live chat surface.

---

## 5. The `company` CLI — how it starts/manages everything

**Observed.**

- Entrypoint: `ops/company` (thin shim) → `ops/cli/app.py:main()`. Symlinked as `~/.local/bin/company`.
- **Service control:** `company up|down|restart [TARGET] [--wait --evict --force]` drives systemd
  units from `services.json`, with a GPU resource-manager that *refuses* an over-budget model load
  (`_act`, `app.py:88-127`). `company status|health|gpu|logs|suites|models|telemetry|config|swap|
  ensure|combos|bench` round it out. **`company up session-supervisor`** starts the supervisor.
- **The fleet face:** **`company session [list|new|send|stop|cap|fleet]`** (`app.py:174-179` →
  `ops/cli/sessions.py`) is the operator face of the supervisor. It is **stdlib-only urllib against
  `127.0.0.1:8771`** — `new`→`POST /spawn`, `send`→`POST /inject`, `stop`→`POST /teardown`,
  `list/fleet`→`GET /sessions`, `cap`→`GET /health`. The console NEVER launches claude itself (the
  supervisor is the single launcher). A down supervisor is a loud teaching failure ("`company up
  session-supervisor`").
- Related read surfaces: `company board` (the inward Noticeboard), `company clone` (the point-in-time
  clone fleet), `company coherence`.

---

## 6. How a Claude Code session integrates / registers as a participant

**Observed — two distinct ways, matching the two transports:**

1. **Interactive channel member (Mechanism A):** launched (by a human, or via Tim's `.bashrc` alias
   `claude-fabric.sh`) with `--mcp-config /home/tim/company/channels/channel.mcp.json
   --dangerously-load-development-channels server:company-channel`. `channel.mcp.json` registers ONE
   MCP server, `company-channel` → `node channels/company_channel.mjs` with env `COMPANY_ROOT`. On
   load, `company_channel.mjs` opens its random port and writes `.data/channels/<handle>.json`. The
   session self-describes via the `profile` / `announce` MCP tools (model/role/focus/expertise). It
   can `reply` to inbound `<channel>` tags (→ `/channel-reply` → pushed back to the asker).
   **AUTONOMOUS agents are correctly BLOCKED** from launching this (`--dangerously-load-development-
   channels` is flagged by the safety classifier), so this path is operator-launched
   (`cc_clone.py:8-14`, `operator_launch_cmd`).
2. **Supervised member (Mechanism B):** the supervisor spawns it (`/spawn`, floor `mcp__company`-only
   allowlist). For it to be reachable by the channel layer, `cc_clone.register_supervised_member`
   writes `.data/channels/<handle>.json` with `{handle, session_id, transport:"supervised",
   supervisor_session, supervisor_base, cwd, description}` (`cc_clone.py:41-56`). Dispatch then
   routes via `/inject` + the `/watch` reply-fold. This is the agent-safe, programmatic path.

**Self-identity:** on a `--resume` (non-fork) spawn the supervisor injects `COMPANY_SESSION_ID` into
the child env so the child's `resolve_own_session("self")` resolves unambiguously
(`session_supervisor.py:842-844`). The channel `.mjs`, the company MCP server, and the SessionStart
hook are all children of the SAME claude process → they walk to the same ancestor PID = the shared
self-id key (`company_channel.mjs:34-53`).

---

## 7. Agent-facing tools (the MCP surface over all this)

**Observed.** Two tool modules expose the fabric to agents (these are what another Claude session, or
a future web-backed agent, calls):

- `mcp_face/tools/sessions.py` → **`sessions`** (read: list/inbox/watch/describe/search/timeline) +
  **`session_post`** (the one write). CQRS-split. `sessions` is posture-tagged `safe` (exposable to a
  non-operator client tier on the remote gateway); `session_post` is operator-only (untagged).
- `mcp_face/tools/cc_channel.py` → **`cc_channel`** (ops: list/send/broadcast/mail +
  create_channel/list_channels/add_member/remove_member/archive_channel) — the live-injection
  transport + named-group registry over `cc_channels.py`.

---

## 8. Bottom line for the OpenWebUI build (the one decision the rest hangs on)

- The `<channel>`-tag delivery (Mechanism A) is **not reusable** by a web UI — it is a Claude Code
  client feature. Do not design the web integration around it.
- The supervisor's **HTTP `/inject` + ndjson `/watch`** (Mechanism B) IS the seam. It is transport-
  agnostic, already running on `127.0.0.1:8771`, and already has a bridge abstraction
  (`transport:"supervised"` in `cc_channels.py`) that folds supervisor `done` events back into the
  fabric's reply routing.
- **TWO web-UI roles — they need different plumbing; decide which (or both) the build wants:**

  - **Role 1 — the web UI DRIVES a claude session** (a chat box: human types → claude answers). This
    reuses the supervised path directly: `POST /inject {session, message}` to send, tail
    `GET /watch?session=<id>` (ndjson) for the token-stream + the `done` reply. The reusable pieces
    are `cc_channels.push`/`_push_supervised`/`route_reply` and the nonce-gated `/watch` fold loop.
    There IS a real claude process behind the session, so the existing `done`-event reply-fold
    applies as-is.
    - *Caveat:* the supervised reply-fold assumes the supervisor SERIALISES turns per session
      (idle⇄busy; `/inject` refused while busy) so each `done` maps 1:1 to the last dispatch
      (`cc_channels.py:201-219`). A web chat wanting concurrent turns per session breaks that
      single-slot assumption — confirm the concurrency model early.

  - **Role 2 — the web UI IS a fabric peer** that other sessions `send`/`broadcast` to (the human at
    the browser is a participant other Claude sessions talk to). This is a **genuinely new transport,
    NOT the supervised path** — there is no claude process and therefore no `done` event on `/watch`
    to fold (the supervised fold keys exactly on that, `cc_channels.py:316-332`). For Role 2 you
    must: (a) deliver an inbound `push` to the browser over the web backend's OWN live stream (SSE/
    WS) instead of POSTing to a claude port; (b) treat the human's typed text as the "reply" and route
    it via `cc_channels.route_reply(handle, thread, text)` — i.e. it behaves like the `'channel'`
    transport's `reply` *tool*, not like the supervised fold. Add a new `transport` value (e.g.
    `"web"`) to `_transport_of`/`push` (`cc_channels.py:59-198`) with these two halves.

**Live state at time of research:** supervisor UP on :8771, cap 3, turn_timeout 900s, permission
`plan`, 2 sessions both `closed` (idle fleet).
