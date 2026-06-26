# 07 — OpenWebUI ↔ Company Fabric: The Connection

**Question (lead):** wire OpenWebUI as the human front-end onto the Company FABRIC — Tim seeing
members, messaging them, and participating in channels through it. Research the integration SURFACES,
and settle the crux: can the fabric deliver an INBOUND message to OpenWebUI, or only to MCP-connected
Claude Code sessions?

**Status:** research + design, pre-implementation. Evidence is from reading the named runtime files and
current OpenWebUI docs (links at the foot). Statements are tagged **Observed** (in the code) /
**Inferred** (pattern, not executed) / **Verified** (none here — nothing was run end-to-end). Source
refs are `file:line`.

---

## 0. The one thing to get right first — there are TWO "channel" systems

The fabric has **two distinct channel concepts** with the same word. The design depends on not
conflating them.

| | **A. CC-Channels** (`runtime/cc_channels.py`) | **B. Session-Channels** (`runtime/session_channels.py`) |
|---|---|---|
| What it is | Cross-session **live-injection transport** — push text INTO another running session's conversation | The fabric's **named-channel / agent-session** concept — posts fan to a member roster as mail intents |
| Store | `.data/channels/<handle>.json` regs + `.data/channels/_mail.jsonl` (Observed `cc_channels.py:29-31`) | `agent_sessions` event log + `agent_sessions/mail.jsonl` (Observed `session_supervisor.py:44-56`) |
| Member identity | a launched CC session: `{handle, session_id, cwd, pid, port}` (Observed `cc_channels.py:6-7`) | a `session://<id>` agent session, OR a bare **label** that is reply-addressable but not session-addressable (Observed `session_channels.py:486-488`, `edges_for` `:650`) |
| Delivery | HTTP POST to the session's local port → injected into the live convo; supervised members via supervisor `/inject` (Observed `cc_channels.py:173-198`, `232-267`) | per-member **mail intent** on the shared leaf: `verb='deliver'` if supervised-live (supervisor injects) else `verb='queue'` (picked up next turn) (Observed `session_channels.py:544-550`) |
| MCP tool | `mcp__company__cc_channel` (ops: list/send/broadcast/mail/create_channel/…) (Observed `mcp_face/tools/cc_channel.py:15-26`) | `mcp__company__channels` / `channel_act`; bridge `POST /api/channel/post` + `GET /api/channel-history` |
| Bridge HTTP? | mail log only (no first-class bridge route yet — supervisor has `/channel-send`,`/channel-reply`) | **YES** — `POST /api/channel/post`, `GET /api/channel-history?channel=`, `GET /api/channels` (Observed bridge route registry) |
| Reply model | reply pushed BACK into asker's live session, no polling (Observed `cc_channels.py:393-407`) | replies aggregate on the thread; read via `agent_mail_since(thread=…)` / inbox (Observed `session_channels.py:562`) |

**For an OpenWebUI front-end, System B (Session-Channels) is the right spine.** It already has
**HTTP routes on the bridge** (System A is MCP/port-only), its membership is a registry fact that does
**not** require the member to be a live process (Observed `cc_channels.py:507-510` analog; `session_channels`
members are roster entries), and it already tolerates a **non-session label** as a member with a reply
path (Observed `session_channels.py:486-488`). That label is the seam where OpenWebUI plugs in.

---

## 1. THE CRUX — can the fabric deliver INBOUND to an arbitrary endpoint? (definitive)

**Finding (Observed): the supervisor delivers ONLY to sessions it OWNS. It cannot push to an arbitrary
registered external mailbox/endpoint.**

Evidence, traced:
- `POST /inject {session, message, source?}` requires a `session` that resolves via `SUP.find(...)` to a
  `Supervised` object the supervisor itself spawned/holds; an unknown id is a hard 404 (Observed
  `session_supervisor.py:1653-1664`). There is **no** "register an external mailbox / callback URL"
  route in the supervisor's route table — the full set is `/health /sessions /watch /spawn /inject
  /interrupt /teardown /bridge-session /channel-reply /channel-send` (Observed `SUPERVISOR_ROUTES`
  `session_supervisor.py:127-136`). None of those registers a foreign receiver.
- `cc_channels.push()` dispatches on exactly two transports: `channel` (HTTP POST to a launched CC
  session's **local port**) and `supervised` (supervisor `/inject`) (Observed `cc_channels.py:184-198`).
  Both terminate at a Claude-Code-shaped endpoint. There is no third "webhook/arbitrary-URL" transport
  today.
- The transport is a **property of the registration**, not a hardcoded assumption — this is the
  designed extension point (Observed `cross-session-unified-transport.md:18-39`, and `_transport_of()`
  `cc_channels.py:59-66`). A third transport `"webhook"` is an additive registration shape, not a rewrite.

**So inbound to OpenWebUI is NOT free.** But the fabric is **not** locked to Claude-Code-only delivery —
there are three clean ways OpenWebUI can receive, in order of least→most work:

1. **POLL the durable record (works today, zero fabric change).** Every channel post + reply is written
   fsync'd to the mail leaf / `_mail.jsonl`. `GET /api/channel-history?channel=<id>` returns the
   channel's whole exchange oldest-first with a `next_since` cursor (Observed
   `session_channels.py:617-638`). An OpenWebUI Pipe/background task polls `next_since` and renders new
   posts into the chat. This is the inbound-delivery answer that needs **no** supervisor work.

2. **Register OpenWebUI as a labelled fabric member (small fabric change).** Add OpenWebUI to a channel
   roster as a member handle (a label like `openwebui`). On every `post_to_channel`, a non-live member
   already gets a `verb='queue'` mail intent (Observed `session_channels.py:544-550`); a labelled member
   is accepted as a reply path (Observed `:486-488`). Then a **new outbound transport** delivers that
   queued intent to OpenWebUI's HTTP injection endpoint (see §2 + §5). This is the "OpenWebUI is a real
   participant" path.

3. **Ride the Supabase shared-channel boundary (most decoupled).** `runtime/channel_boundary.py` already
   defines SHARED channels as single-source on Supabase: a company post writes to `channel_posts`, and an
   **outbound Realtime subscription** injects new rows into live members (Observed
   `channel_boundary.py:1-24`). OpenWebUI could be a second subscriber on that same Supabase Realtime
   stream — the SAME mechanism Claude Design uses. (Caveat — Observed `channel_boundary.py` BUILD STATE:
   the Realtime *subscriber transport* is **stubbed**; publish + inject-routing are built/offline-tested.
   So this path inherits an unfinished gate.)

**The definitive statement for the lead:** *inbound delivery to OpenWebUI is feasible WITHOUT making
OpenWebUI a Claude Code session, but the fabric will not push to it for free — the cheapest real path is
OpenWebUI POLLING `/api/channel-history` (today), and the cleanest "first-class participant" path is a
new `"webhook"` transport + a labelled member registration (small, additive, matches the existing
two-transport design).*

---

## 2. The integration surfaces (what's reachable, how)

### 2a. The bridge HTTP API (`:8770`) — already HTTP-reachable
The bridge exposes a large `/api/*` JSON surface (Observed bridge route registry). The ones that matter
here:
- `GET  /api/channels` — the live fabric roster of named channels (Observed bridge `:1528`,
  `fold_channels`).
- `GET  /api/sessions` — the agent-session fleet, filterable `?state=&cwd=&q=&limit=` (Observed `:1534`).
  **This is "Tim sees the members."**
- `GET  /api/channel-history?channel=<id>` — one channel's exchange (Observed `:1633`). **Inbound poll.**
- `POST /api/channel/post {channel, message}` — the OPEN ungated channel post (Observed `:2640`).
  **This is "Tim messages a channel."**
- `GET  /api/inbox`, `GET /api/board` — inbox lanes / noticeboard as data (Observed `:1738`, `:1556`).
- `GET  /api/transcript-search?q=`, `GET /api/session-recall?op=…&session=…` — recall by meaning
  (Observed `:1577`, `:1599`).
- `POST /api/chat` / `POST /api/chat/stream` — the RHM grounded conversation (Observed `:2918`, `:2863`).

**Auth/CORS (Observed):** the bridge has **no CORS headers and no `do_OPTIONS`** in the route handlers,
and only a process-scoped operator-token gate (`X-Operator-Session`, minted at `GET /api/operator-session`)
on a few consequential routes like `/api/decision/update/accept` (Observed bridge `:503-534`, `:2549`).
Implication: OpenWebUI must reach the bridge **same-origin / server-side** (an OpenWebUI Tool or Pipe
calling from the OpenWebUI backend), not via browser fetch from the OpenWebUI page, until CORS is added.
This is fine — the recommended pattern (§3, §5) is server-side anyway.

### 2b. The company MCP servers — `company` + `company-channel`
- `mcp__company__cc_channel` (System A live-injection) and `mcp__company__channels` / `channel_act`
  (System B named channels) are MCP-only today (Observed `mcp_face/tools/cc_channel.py`).
- These are MCP (stdio/SSE). To let OpenWebUI *call* them as tools, they need an HTTP/OpenAPI face —
  which is exactly what **mcpo** provides (§4).

### 2c. The supervisor (`:8771`) — owns session lifecycle
HTTP-reachable but **not** for arbitrary delivery (see §1). Relevant outbound use: it's how a fabric
message reaches a *live* member; OpenWebUI doesn't talk to it directly in the recommended design.

---

## 3. OUTBOUND — OpenWebUI → fabric (Tim messages members/channels)

**Cleanest path (recommended): an OpenWebUI Tool/Function that calls the bridge server-side.**
- "Tim posts to a channel" → OpenWebUI Tool calls `POST /api/channel/post {channel, message}` (Observed
  bridge `:2640`). Ungated, already live.
- "Tim DMs a live CC session" → OpenWebUI Tool calls the supervisor `POST /channel-send {to, message,
  from}` (Observed `session_supervisor.py:1645-1651`) OR `mcp__company__cc_channel op=send` via mcpo.
- "Tim sees members" → OpenWebUI renders `GET /api/sessions` + `GET /api/channels` (Observed `:1534`,
  `:1528`).

OpenWebUI Tools/Functions run server-side with **no execution timeout** and can call any HTTP API
([OpenWebUI Functions docs]). So outbound is the easy direction — a thin tool wrapper over the bridge
routes that already exist. **No fabric change needed for outbound.**

Alternative outbound via **mcpo** (§4): expose `cc_channel`/`channels` MCP tools as OpenAPI so the
OpenWebUI model calls them as native tools (model-driven), rather than hand-wired Tool functions
(deterministic). Both are valid; mcpo gives the LLM agency, the bridge-Tool wrapper gives control.

---

## 4. mcpo — the MCP→OpenAPI bridge (web-researched)

**Observed (docs):** `mcpo` is OpenWebUI's official "MCP-to-OpenAPI proxy." It takes an MCP server
(stdio, SSE, or Streamable-HTTP) and republishes every tool as REST endpoints + an auto-generated OpenAPI
schema + Swagger UI, with **API-key protection**, per-tool routing, reverse-proxy subpath (`--root-path`),
a multi-server config file (Claude-Desktop format) with hot reload, and OAuth 2.1
([mcpo GitHub], [OpenWebUI MCP docs]).

**Feasibility for us (Inferred):** point mcpo at the `company` + `company-channel` MCP servers; OpenWebUI
then consumes `cc_channel`, `channels`, `channel_act`, `sessions`, `inbox`, `session_recall`, etc. as
OpenAPI tools. This is the lowest-custom-code way to give the OpenWebUI model the **whole** fabric tool
surface at once, vs. hand-writing one Tool per route. Risk: the company MCP exposes a *large* tool set;
likely want a curated subset (a thin MCP that re-exports only the channel/session/recall tools) so the
model isn't flooded. I have **not** verified the company MCP servers launch cleanly under mcpo.

---

## 5. INBOUND — fabric → OpenWebUI (the crux, mechanism detail)

OpenWebUI **does** accept externally-injected messages into a chat (web-researched, **Observed in docs**):
- External callers POST to `POST /api/v1/chats/{chatId}/messages/{messageId}/event` with an `embeds`
  payload (incl. `replace: true`) to inject content into an existing chat message, using a dedicated
  **admin/service-account API key** (an admin key works for any user's chat)
  ([OpenWebUI Events docs], [OpenWebUI API endpoints]).
- The realtime layer is Socket.IO (FastAPI↔SvelteKit), with the event-emitter writing to the DB even
  with no browser attached ([OpenWebUI Real-time Communication]).
- Limitation (Observed docs): interactive `__event_call__` (asking the user for input) needs the
  bidirectional WS and is **not** available to external callers; one-way fire-and-forget injection IS.
  Fine for "show me the fabric's reply" — that's one-way.

So the inbound mechanism on the OpenWebUI side exists. The fabric side gets there by one of §1's three:

- **(1) Poll (today):** an OpenWebUI background Pipe polls `GET /api/channel-history?channel=&since=` and
  renders new posts. Simplest; works now; latency = poll interval.
- **(2) Webhook transport (recommended first-class):** add `transport:"webhook"` to the two-transport
  router (Observed extension point `cross-session-unified-transport.md:18-39`). Registration carries
  `{handle:"openwebui", transport:"webhook", url:"http://<openwebui>/api/v1/chats/.../event", api_key}`.
  `cc_channels.push()` gains a `webhook` branch that POSTs the rendered message to that URL with the admin
  key. Register `openwebui` as a member of the channels Tim watches → every fabric post fans to it →
  delivered into his OpenWebUI chat. **Reply path:** Tim's reply in OpenWebUI is an outbound `POST
  /api/channel/post` (§3), tagged with the thread → aggregates exactly like any member reply. This makes
  OpenWebUI a **symmetric participant**: it sends (via §3) and receives (via this webhook) on the one
  thread, mirroring how a CC session sends/receives.
- **(3) Supabase Realtime (most decoupled):** OpenWebUI subscribes to the shared `channel_posts` Realtime
  stream alongside Claude Design (Observed `channel_boundary.py:1-24`) — but the subscriber transport is
  currently stubbed, so this path waits on that gate.

---

## 6. Can OpenWebUI be a registered fabric PARTICIPANT (a handle + mailbox)? — YES

**Inferred (high confidence from the code shape):** yes, via path §1.2 / §5.2. A fabric member is just a
roster entry that can be a non-session **label** with a reply path (Observed `session_channels.py:486-488`,
`edges_for` labels marked `addressable:false` but kept `:650`). Registering `openwebui` as a channel
member gives it a handle; the webhook transport gives it a mailbox (its OpenWebUI chat-event endpoint).
It then appears in `GET /api/channels` rosters and `member_statuses` (Observed `:566-613`) like any other
member. The work is purely additive: a member registration shape + one new `push()` transport branch +
its acceptance test (mirrors the supervised-transport acceptance list in
`cross-session-unified-transport.md:115-122`).

---

## 7. Feasibility paths, shallow → deep

| Path | Inbound | Outbound | Fabric change | "Tim is a participant"? |
|---|---|---|---|---|
| **P0 — Poll + bridge Tools** | OpenWebUI polls `GET /api/channel-history` | OpenWebUI Tool → `POST /api/channel/post` + `GET /api/sessions` | **none** | reads channels, posts, sees members — but inbound is pull, not push |
| **P1 — mcpo tool surface** | (still poll, or P2) | OpenWebUI model calls `cc_channel`/`channels`/`sessions` via mcpo OpenAPI | none (run mcpo) | model-driven fabric access |
| **P2 — Webhook member (recommended)** | fabric `push(transport="webhook")` → OpenWebUI chat-event endpoint | `POST /api/channel/post` tagged with thread | **small, additive**: a 3rd transport branch + a labelled member reg + acceptance test | **YES — symmetric send/receive on one thread** |
| **P3 — Supabase Realtime** | OpenWebUI subscribes to `channel_posts` alongside Claude Design | publish via boundary | depends on the **stubbed** Realtime subscriber gate | YES, fully decoupled, multi-client |

**Recommendation:** ship **P0 immediately** (it's wiring over routes that exist — Tim sees members,
posts to channels, polls replies, with zero fabric edits), layer **P1 (mcpo)** to give the OpenWebUI
model the full tool surface, and build **P2 (webhook transport)** as the real "first-class participant"
increment because it (a) matches the already-designed two-transport router exactly, (b) is small and
additive, and (c) gives true push-inbound without waiting on the stubbed Supabase Realtime gate. P3 is
the long-horizon multi-client convergence once the boundary's Realtime subscriber lands.

---

## Sources
- Code (Observed, this repo): `runtime/cc_channels.py`, `runtime/session_supervisor.py`,
  `runtime/session_channels.py`, `runtime/channel_boundary.py`, `runtime/bridge.py` route registry,
  `mcp_face/tools/cc_channel.py`, `build-prep/cross-session-unified-transport.md`,
  `build-prep/CROSS-SESSION-CHANNELS-PROVEN.md`.
- [mcpo (MCP-to-OpenAPI proxy) — GitHub](https://github.com/open-webui/mcpo)
- [OpenWebUI — MCP Support](https://docs.openwebui.com/features/extensibility/mcp/)
- [OpenWebUI — Functions](https://docs.openwebui.com/features/extensibility/plugin/functions/)
- [OpenWebUI — Events (event emitter / chat-event injection)](https://docs.openwebui.com/features/extensibility/plugin/development/events/)
- [OpenWebUI — API Endpoints](https://docs.openwebui.com/reference/api-endpoints/)
- [OpenWebUI — Backend-Controlled API Flow](https://docs.openwebui.com/reference/api-flow/)
- [OpenWebUI Real-time Communication (DeepWiki)](https://deepwiki.com/open-webui/open-webui/16-external-integrations)
