# Participants · Members · Channels — the Company fabric

Research report for the OpenWebUI integration question. Evidence-grounded against the live code in
`/home/tim/company` as of 2026-06-23. The driving question (from the brief): **how could an EXTERNAL
(non-Claude-Code) client become a participant?** That answer lives in §5 (the shared-channel/Supabase
seam) and §8 (the reusable recipe). The rest builds the ground you need to read it correctly.

> **Read this first — there are TWO different "channel" systems.** They share a word and nothing else.
> Keeping them apart is the single most important thing in this report. The members/`shared`/external
> questions are almost entirely **System 1**.
>
> | | **System 1 — the Claude Code CHANNEL fabric** | **System 2 — the Session Fabric structure** |
> |---|---|---|
> | Module | `runtime/cc_channels.py` | `runtime/session_channels.py` |
> | MCP tool | `cc_channel` (`mcp_face/tools/cc_channel.py`) | `channels` + `channel_act` (`mcp_face/tools/channels.py`) |
> | What a "member" is | a **handle** = a live Claude Code session (`ch-xxxx`) | a **session id** (`session://…`) from the agent-session registry |
> | Storage | flat files under `.data/channels/` | append-only log `<store>/agent_sessions/channels.jsonl` |
> | Delivery | live HTTP injection into a running session | fans intents onto the mail leaf (deliver/queue) |
> | The `shared`→Supabase seam | **YES — this is the external edge** | no (it has a mirror schema, but the wired code uses System 1) |
>
> Both define `create_channel`, `add_member`, `archive_channel` — **different functions, different stores.**
> When the brief says "create_channel / add_member / op=list", it means **System 1** (`cc_channels`).
> System 2 is a parallel coordination-structure layer (gatherings, edges, conducted mode); covered in §6.

---

## 1. What a CHANNEL is (System 1 — `cc_channels.py`)

There are actually **two registries** inside System 1, joined on the handle:

1. **The MEMBER registry** — one file per live session: `.data/channels/<handle>.json`. Carries
   *liveness + transport* (pid, port, cwd, profile). Written by the channel MCP server at launch (§3).
2. **The named-CHANNEL registry** — one file per channel: `.data/channels/_channels/<channel-id>.json`.
   Carries *membership* (a list of handles) + purpose + coordinator + the `shared` flag.

The two namespaces are deliberately disjoint (`cc_channels.py:424-430`): a channel record holds membership
facts; liveness for any member is resolved at push-time via `find()`/`live_sessions()`. A member can belong
to several channels at once.

### The channel record shape (`create_channel`, `cc_channels.py:459-477`)

```python
{
  "id": "design",              # slug of name (re.sub → fs-safe; dup-name = file-exists check)
  "name": "design",
  "purpose": "Claude Design ⨯ company — shared design channel",
  "coordinator": "",           # optional member handle that owns the channel
  "members": [],               # list of handles (membership facts, NOT liveness)
  "status": "active",          # active | archived
  "shared": false,             # ← THE EXTERNAL GATE (default False = fail-closed)
  "created": "2026-06-18T15:05:34"
}
```

`create_channel(name, purpose, coordinator, *, shared=False)` fails loud on a duplicate name (no silent
overwrite). Every channel op is fail-loud + teaching (never a silent no-op) — the no-silent-failures law.

### INTERNAL vs SHARED — the publish gate (`cc_channels.py:459-485`)

- **INTERNAL** (`shared=False`, the default): stays LOCAL on the box, never leaves. All existing channels
  with no `shared` key are INTERNAL (additive — `is_shared()` is fail-closed).
- **SHARED** (`shared=True`): "single-source on Supabase" — its posts are *meant to* publish OUT to the
  Supabase `channel_posts` table so an external client (Claude Design today, OpenWebUI tomorrow) can
  participate in the SAME channel. `is_shared(channel)` (`cc_channels.py:480-485`) is the publish-hook's gate:
  a post routes to the Supabase boundary **only when this returns True**.

> **Live state (verified):** there are 11 named channels under `.data/channels/_channels/`. The only one
> flagged `shared:true` is `design.json` (the seeded Claude-Design home). All others are INTERNAL.

### The SHARED→Supabase boundary — **the external-integration seam** (§5 has the full trace)

This is the heart of the brief. A SHARED channel's posts are written DIRECTLY to a Supabase table
(`channel_posts`), and an outbound Realtime subscription brings external-client posts back into the live
company sessions. The design (`runtime/channel_boundary.py:1-29`, Tim 2026-06-18): the internal fabric stays
the one source of truth for INTERNAL work; SHARED channels are single-source on Supabase so the company
sessions and the external client sit in the *same* live room, with **zero box exposure** — the box only
reaches OUT (a publish POST + an outbound WebSocket); nothing connects IN.

---

## 2. What a MEMBER / PARTICIPANT is (System 1)

A member is a **live Claude Code session** that registered itself on the fabric. Its identity =
`cwd` + a self-announced description/profile (`cc_channels.py:13-15`). The member registration file
(`.data/channels/<handle>.json`) — verified live shape:

```json
{
  "handle": "ch-z4ht5ipb",
  "session_id": "",
  "cwd": "/home/tim/repos/counterpart/design",
  "description": "DNA — the decision/operator surface render lane…",
  "model": "claude-opus-4-8",
  "profile": { "model": "...", "role": "...", "focus": "...", "expertise": "..." },
  "pid": 5856, "claude_pid": 5774, "port": 36009,
  "started": "2026-06-20T09:19:57.664Z"
}
```

### How a session BECOMES a member (the launch loop)

`channels/claude-fabric.sh` is aliased as `claude` in `~/.bashrc` (interactive shells only). Every
interactive launch becomes:

```
claude --mcp-config channels/channel.mcp.json --dangerously-load-development-channels server:company-channel
```

That attaches `channels/company_channel.mjs` (the MCP server). On load it (a) opens an HTTP listener on a
random local port and (b) writes its registration file (`company_channel.mjs:55-65, 157-161`). Cleanup on
exit unlinks the file (`:162-165`). So **presence = the registration file + a live pid + a port.** Non-
interactive `claude -p` worker calls get the plain binary (no channel), preserving the autonomous-spawn
boundary.

### The mailbox / live-injection — `<channel>` tags

The member's local HTTP port is its mailbox. An external POST `{content, meta}` to that port becomes an
MCP notification (`notifications/claude/channel`) that lands as a live `<channel source="company-channel"
from="…" thread="…">` tag IN the running conversation (`company_channel.mjs:145-156`). The agent reads it
and acts on it. `meta` keys become `<channel>` attributes.

### `op="list"` — discovering live members (`cc_channels.live_sessions()`, `cc_channel.py:82-88`)

Returns every live member, newest first: `handle · cwd · description · session_id · started`. Transport-aware
(`cc_channels.py:94-149`):
- **channel** transport (default, portful regs): alive = pid alive AND has a port; a dead pid is **pruned**.
- **supervised** transport (clone/fork-owned regs): alive = the supervisor's `/sessions` shows it non-closed;
  pruned ONLY when the supervisor is reachable AND reports it closed — **never** over a transient outage
  (never destroy a fork-owned reg on a blip).

### add_member / remove_member (`cc_channels.py:507-540`)

Membership is a **registry fact**, decoupled from liveness — `add_member` does NOT require the member to be
live (liveness is resolved later at push time). Both fail loud: adding to a missing/archived channel, adding
a duplicate, or removing a non-member all raise teaching errors.

---

## 3. The company-channel MCP server (`channels/company_channel.mjs`)

The Node server each session runs. It declares `claude/channel`, registers the session, and exposes **three
tools** to its own session (these are the session's *self-description + reply* tools, not the cross-session
send tool — that's `cc_channel`, §4):

- **`reply`** — routes the session's reply to the supervisor's `/channel-reply` (which records it in the
  mailbox AND pushes it back into the asking session). `:119-122`.
- **`announce`** — sets a one-line description on this session's reg. `:123-127`.
- **`profile`** — writes WHO-I-AM (`model/role/focus/expertise`) into this session's reg, merged
  (transport fields pid/port preserved). `:128-139`. The `profile`/`announce` data is what `op=list` surfaces.

`claudeAncestorPid()` (`:34-53`) walks `/proc` to find the shared Claude session PID — the self-id key the
channel server, the company MCP server, and the SessionStart hook all resolve to (failure-isolated: any
`/proc` error → null, never throws — a thrown announce would fail a session's fabric registration).

---

## 4. Message flow (System 1 — `cc_channel` tool + `cc_channels` router)

The MCP tool `cc_channel` (`mcp_face/tools/cc_channel.py`) is the agent-facing surface. Ops:

| op | what it does | mechanism |
|---|---|---|
| `list` | discover live members | `live_sessions()` |
| `send` | push a message INTO a live session; opens a thread so the reply pushes back | `send()` → `push()` |
| `broadcast` | group chat: send to many (`to`=comma-sep) under ONE shared thread | loops `send()` |
| `mail` | read the durable message/reply log | `mail()` |
| `create_channel` / `list_channels` / `add_member` / `remove_member` / `archive_channel` | the named-channel REGISTRY | §1 |

### send / push / reply-routing (`cc_channels.py:380-407`)

1. `send(to, content, frm, thread)` resolves the target via `find()` (handle / exact cwd / unique substring),
   mints a thread if none, records the message in the durable mail log (`_mail.jsonl`), opens the thread
   (origin = sender), and `push()`es into the live session.
2. `push()` dispatches on the member's **transport** (`cc_channels.py:173-198`): `channel` → HTTP POST to the
   session's local port; `supervised` → POST to the supervisor `/inject` + a lazy `/watch` tail that folds the
   member's done-event back into `route_reply` (a supervised session has no `reply` tool of its own, so the
   watcher *is* its reply tool — nonce-gated so a replay/foreign turn never mis-routes; `:201-346`).
3. When a member replies (`company_channel.mjs` `reply` → supervisor `/channel-reply` → `route_reply`,
   `cc_channels.py:393-407`), the reply is recorded and **pushed back into the thread's originator's live
   session** (no polling). If the originator is "fabric"/an agent (not a live session), it's recorded for the
   agent to read via `mail`.

`threads` (`_threads.json`) maps `thread → {originator, topic, members}` — the routing index that makes a
reply find its way home.

> The cross-session-fabric skill (`cross-session-fabric`) and the `company-channel` MCP server instructions
> are the agent-facing docs for exactly this flow.

---

## 5. The EXTERNAL seam in full — Supabase `channel_posts` + RLS (THE answer to the brief)

This is how a non-Claude-Code client participates. There are two distinct external paths; **the data path
(this section) is the participation path.** The tool path (§7) is read-only for clients.

### 5a. The data model (live in Supabase — migrations 0002/0003, **applied**, verified)

`migrations/0003_channels.sql` mirrors the channel + post shapes into Supabase:

- **`public.channels`** — `id, kind, name, purpose, mode, coordinator, status, members(jsonb), origin,
  posts, shared(bool, default false), created_at, last_activity`. `shared` is the opt-in publish gate
  (fail-closed). Realtime publication enabled on the table.
- **`public.channel_posts`** — `id(uuid), channel_id(FK→channels), from_session, sender_kind
  ('session'|'client'), to_session(nullable), thread, kind, text, created_at`. **Realtime-published**, so
  every INSERT streams to subscribers. An insert trigger bumps `channels.posts`/`last_activity`.
- **`public.clients`** (`0002_clients.sql`) — the **client registry**, one row per external client. Columns:
  `id, label, allowed_tools(jsonb), scopes, approval_mode, channels(text[]), posture, status,
  oauth_client_id`. Claude Design is the seeded first row (`id='claude-design'`). **This is the row a new
  external client (OpenWebUI) needs** (§8).

**Participation model** (`0003` header): the external client writes a `channel_post` → Supabase Realtime
delivers it to subscribed company sessions → a company session replies (writes a `channel_post`) → Realtime
delivers it back to the client. RLS gates each side to the rows its role may touch.

### 5b. The two RLS gates (live — 0005/0006/0010, **applied**, verified)

There are two distinct authenticated principals, cleanly split (`0010` header):

1. **The company boundary principal** (`0005_boundary_rls_seed.sql`) — a dedicated least-privilege Supabase
   *user* (email+password, `app_metadata.role='company_boundary'`), **NOT** the service-role master key (the
   lead's security rule). RLS (`is_company_boundary()`) scopes it to INSERT+SELECT on `channel_posts` + the
   collab tables, SELECT+UPDATE on `channels`. It may NOT create channels (the company decides that). This is
   the principal `runtime/supabase_principal.py` authenticates as (env-prefix `COMPANY_CHANNEL`).
2. **The external client** (`0006_design_client_rls.sql` + `0010_native_client_id_rls.sql`) — authenticates
   via **OAuth**. Its native server-set `client_id` claim is matched against `clients.oauth_client_id` to
   resolve the client ROW id (`public.client_id()`, SECURITY DEFINER). RLS then ties every write to that id:
   - INSERT a `channel_post` only where `from_session = client_id()` AND `channel_granted(channel_id)` (the
     channel is `shared=true` AND listed in the client's `clients.channels`). Can't forge another client's
     posts or post into an ungranted channel.
   - SELECT posts/channels only in its granted shared channels.

`channel_granted()` (`0006:29-46`) is SECURITY DEFINER (reads `clients`+`channels` as a system fact to avoid
RLS recursion). **Two levels of scoping** (`0003` comment): `channels.shared=true` (global opt-in) AND the
channel listed in `clients.channels` (per-client grant). Registry-is-truth.

> **0010 — "go native" (2026-06-22):** the earlier Custom Access Token Hook (0007) was dropped from the
> claims path (shared-project safety: zero blast radius on the 16 live OAuth connectors). RLS now reads the
> OAuth token's native `client_id` (server-set, not user-forgeable), not a hook stamp. The boundary principal
> is unaffected (it's a password-login user with `app_metadata.role` at creation, no OAuth).

### 5c. The company-side boundary code (BUILT — see §9 for what's NOT yet wired)

- `runtime/supabase_principal.py` — the reusable least-privilege principal (auth → JWT, cached/refreshed,
  fail-loud). Offline self-test passes. One home (vi_vision migrates onto it).
- `runtime/channel_boundary.py` — the PUBLISH + INJECT-ROUTING + Realtime SUBSCRIBER:
  - `build_post_row()` / `publish_shared_post()` — write a post to `channel_posts` as the principal
    (Bearer JWT, NOT service-role); fail-loud-with-reason (a failed publish = the message did NOT send —
    the caller MUST surface a Notice + record a Gap, no silent drop).
  - `route_inject(post_row, members)` — the **single-source correctness rule**: inject to all members
    EXCEPT the origin (skip-by-ORIGIN, BOTH `session` and `client` kinds inject) — so company sessions see
    each other AND see the external client. (The earlier `client`-only filter was a mirror-design artifact
    and is documented as WRONG for single-source.)
  - `build_join_msg()` — ★ load-bearing: the principal JWT rides in the phx_join `payload.access_token`, so
    Realtime applies RLS to `postgres_changes` and streams only rows the JWT can SELECT. No token → silent-
    empty subscription.
  - `ChannelInjectSubscriber` — outbound WS → live-session injector; reconnect + heartbeat + token refresh.
- `runtime/channel_boundary_run.py` — the entrypoint: `post_to_channel()` is the **shared-aware publish
  hook** (SHARED → `publish_shared_post`; INTERNAL → the existing local broadcast — unchanged); `make_inject`
  = `cc_channels.push` (push-only, no local mail record: single-source); `make_members_of` =
  `cc_channels.channel_members`; `ensure_design_channel()` seeds the shared `design` channel;
  `run_boundary()` is the long-running service; `verify_my_half()` is the live by-use round-trip.

> **Note the cross-system join (a seam tension):** `0003_channels.sql` says it "mirrors
> agent_sessions/channels.jsonl" (that's **System 2**'s leaf). But the *wired* publish hook
> (`channel_boundary_run.post_to_channel` / `make_members_of`) reads `cc_channels.is_shared` /
> `channel_members` — **System 1**. The live `design` channel is a System 1 `_channels/design.json` record
> (`shared:true`, verified). So the Supabase schema's comments cite System 2, but the code path that feeds it
> uses System 1. For OpenWebUI, the System 1 path is the live one.

---

## 6. System 2 — the Session Fabric structure (`session_channels.py` / `channels` + `channel_act`)

A separate, parallel layer (Session Fabric R2.2–R2.5) — the *structure around sessions*, not a transport.
Worth knowing so you don't conflate its `create_channel`/`add_member` with System 1's, and because its `edges`
are a useful relationship view. CQRS pair in `mcp_face/tools/channels.py`:

- **`channels`** (read; tagged `posture="safe"` → exposed to external clients, §7): `op=list|describe|history|
  edges`. `describe` composes member statuses (declared awake/listening ∪ derived busy/closed from the
  agent-session registry + a live supervisor probe; `status_source` is always honest). `edges` is a read-time
  projection over the durable mail leaf — who-talked-to-whom, direction-aware, channel-attributed, with a
  ready-to-run follow-up handle.
- **`channel_act`** (write; **untagged → operator-only**): `action=create|gather|add|remove|status|post|mode|
  promote|disperse|archive`. CHANNELS (persistent) vs GATHERINGS (momentary, promotable). MODES: `direct`
  (router fans to all members) vs `conducted` (one coordinator session receives + works the members; recurses
  via sub-channels). A post fans intents onto the mail leaf (deliver to supervised-live, queue for the rest)
  — it **NEVER wakes/spawns** a session (the routing law). Members are `session://` ids validated against the
  agent-session registry (fail-loud on fabricated ids).

Storage: `<store>/agent_sessions/channels.jsonl` (append-only, seq-locked, fold-is-the-index). Vocabularies
are closed module constants (`CHANNEL_OPS/KINDS/MODES/PARTICIPATION/ROW_STATUS`).

---

## 7. The remote-MCP tool path (`mcp_face/remote.py`) — read-only for external clients

The OTHER way an external identity touches the fabric: calling MCP tools over the remote gateway. Architecture
(unified 2026-06-22): **ONE brain** = the box's `remote.py` (live tool registry + identity→posture filter),
reached over a Tailscale Funnel. The Supabase Edge Function (`functions/claude-design-gateway/index.ts`) is now
a **thin OAuth forwarder** — serves OAuth discovery, 401s without a Bearer token, forwards a token-bearing
request verbatim to `BACKEND_URL/mcp`. It holds NO tool list and makes NO access decision (the old
`clients.allowed_tools` 15-subset and the EF's own dispatch are DELETED).

Access is a pure identity→posture filter (`remote.py:57-96`):
- no token → nothing (401);
- `sub == OPERATOR` (Tim's remote self) → ALL tools;
- any other valid user (a client like OpenWebUI) → only tools whose **`posture == "safe"`**; unclassified
  tools are operator-only (fail-closed).

**Consequence for channels (verified against the tool defs):**
- `channels` (read) is registered with `posture="safe"` (`channels.py:89-91`) → an external client **can read**
  `list/describe/history/edges`.
- `channel_act` (write) and `cc_channel` (the cross-session send) are **untagged** → unclassified →
  **operator-only → NOT exposed to an external client.**

**So an external client cannot POST into a channel via MCP.** Its write-participation is the direct
`channel_posts` INSERT over PostgREST/Realtime (§5), RLS-scoped. The seeded `clients.allowed_tools` granting
`cc_channel:{send}` (`0002`) is the OLD model the EF comment marks superseded — it is NOT the live write path.

> **Honest status:** `remote.py`'s own header says it is a **skeleton** — "the tool-dispatch proxy to the
> stdio face's registered tools lands next." So even the safe-posture reads are not confirmed dispatchable
> end-to-end yet. Treat §7 as the designed/partially-built path.

---

## 8. The reusable recipe — how OpenWebUI (or any client) becomes a participant

Claude Design is the **worked instance** of a general pattern. For a new external client, the
participation path is the §5 data path (the §7 tool path gives read-only tool access, optional). What it takes:

1. **A `clients` row** (`public.clients`): `id` (e.g. `'openwebui'`), `label`, `status='active'`,
   `channels=array['<shared-channel>']`, and `oauth_client_id` = the OAuth client id the client authenticates
   with. (`allowed_tools`/`posture` only matter for the §7 tool path; for pure channel participation the
   `channels` grant + `oauth_client_id` are the load-bearing fields.)
2. **A shared channel** the client is granted: a `channels` row (or the System 1 `_channels/<id>.json`) with
   `shared=true`, AND that channel id listed in the client's `clients.channels`. Both levels required
   (`channel_granted()`).
3. **OAuth identity**: the client authenticates against the Supabase auth server; its native `client_id`
   claim must match `clients.oauth_client_id`. Then RLS (`is_design_client()`/`client_id()`/`channel_granted()`)
   lets it INSERT its own posts (`from_session = client_id()`) into the granted channel and SELECT that
   channel's posts. (These RLS functions are named for "design_client" but key purely off the client registry
   — they already generalize to any active client row. A rename to `is_client()` would be cosmetic.)
4. **The company boundary must be running** (`run_boundary`) so the client's posts get injected into the live
   company sessions, and company posts get published out for the client to read. **This is the missing piece**
   (§9) — it is built but not started, and the principal is not provisioned.

**Participation loop, end to end:**
`OpenWebUI INSERTs a channel_post (its OAuth JWT, RLS-scoped)` → `Realtime streams the INSERT` →
`the company boundary subscriber injects it into the live company member-sessions (skip-by-origin)` →
`a company session replies → publish_shared_post writes a channel_post` → `Realtime streams it back` →
`OpenWebUI SELECTs / subscribes and sees it`. Reads of fabric structure (channels list/describe/history) are
additionally available read-only via the gateway→remote.py safe-posture `channels` tool.

---

## 9. LIVE vs BUILT-BUT-UNWIRED — the honest status bar

| Piece | Status | Evidence |
|---|---|---|
| System 1 channel fabric (members, send, reply, named channels, `shared` flag) | **LIVE** | 11 channels + live member regs in `.data/channels/`; `_mail.jsonl` is 6.3 MB of real traffic |
| Channel attachments (§10) | **LIVE** (built, file-discovered) | `runtime/cc_attachments.py`; 7 attachment types |
| Supabase schema (`channels`, `channel_posts`, `clients`, all RLS) | **LIVE / APPLIED** | `list_migrations` shows 0001–0010 applied (`20260618074746`–`20260618095614`) |
| Seeded `design` shared channel + `claude-design` client row | **LIVE** | 0005 seed; `_channels/design.json` has `shared:true` |
| `supabase_principal` / `channel_boundary` publish+route+subscriber code | **BUILT, offline-tested** | self-tests pass; `channel_boundary.py:22-29` says Realtime transport STUBBED, live round-trip pending |
| **The publish hook wired into the live send path** | **NOT WIRED** | grep: `channel_boundary_run.post_to_channel` has **no production caller**; `cc_channel.send` does NOT call `is_shared`/publish. A post to a `shared` channel today still goes the local path only. |
| **The boundary subscriber launched as a service** | **NOT STARTED** | grep: `run_boundary`/`channel_boundary_run` is referenced **nowhere** in `ops/services.json`, the `company` CLI, or any launcher |
| **The boundary principal provisioned** | **NOT PROVISIONED** | `.boundary.env` has the keys but they are **empty** (`COMPANY_CHANNEL_SA_EMAIL=` with no value) |
| `remote.py` tool-dispatch | **SKELETON** | its own header: "the tool-dispatch proxy … lands next" |

**Bottom line for OpenWebUI:** the Supabase data model, the RLS, and the company-side publish/inject *code*
all exist and the schema is live. The external participation loop is **not yet closed** because (a) no
production code calls the publish hook when a shared channel is posted to, (b) the boundary subscriber is
never started, and (c) the least-privilege principal cred is not filled in. Closing those three + adding the
`clients` row/grant/OAuth identity (§8) is the work to make a non-Claude-Code client a live participant.

---

## 10. Channel attachments (`cc_attachments.py` + `attachment_types/`)

Tim's frame: "channels can have things attached… so the channel set-up can be parametrically generated."
A channel-attachment is its OWN registry of BINDING ROWS — `{id, channel, attachment_type, target, added}` —
not a mutable field on the channel record (so `cc_channels.py` is never edited; add/remove = add/remove a row).

- **Bindings** are id-keyed flat files: `channel-memory/channel_attachments/<id>.md` (frontmatter row).
- **`attachment_type`** is a registry ref, validated fail-loud against `runtime/attachment_types/` (file-
  discovered: drop an `attachment_types/<id>.py` declaring `ATTACHMENT_TYPE={…}`, no code change). Live types:
  `board_items, cloning, docs, recall, sessions, images, dragnet_runs`.
- **`target`** is an OPAQUE ref (e.g. `board://<id>`, `session://<id>`, a path, a scope) — stored verbatim,
  resolved by the address scheme, never parsed here.
- **Channel existence is validated** by importing `cc_channels._read_channel` READ-ONLY (file-disjoint — this
  module never writes a channel record). `attach()` fails loud on a dangling channel unless
  `require_channel=False`. Non-`multi` types may bind only once.
- **`manifest(channel)`** is a PROJECTION of the rows grouped by type (a VIEW computed on read, not stored) —
  `{sessions:[…], docs:[…], recall:[…], board_items:[…]}`. The Heart's "manifest = projection of the registry."
- MCP surface: `cc_attachments` tool (`op=attach|detach|list|manifest|types`).

**Board edges:** the `board_items` attachment type binds noticeboard items (`board://<id>`) to a channel —
the channel's requests/issues/tips/guides/ideas — resolved via `cc_board.get_item`. (The noticeboard `cc_board`
is a sibling registry; attachments are the join.)

---

## Key file references

| File | Role |
|---|---|
| `runtime/cc_channels.py` | System 1 core: member registry, named-channel registry, send/push/reply, `shared` gate |
| `mcp_face/tools/cc_channel.py` | System 1 MCP tool (`op=list/send/broadcast/mail/create_channel/…`) |
| `channels/company_channel.mjs` | the per-session MCP server (registration, `reply`/`announce`/`profile`, live `<channel>` injection) |
| `channels/claude-fabric.sh` · `channels/channel.mcp.json` | the auto-join launch wrapper + MCP config |
| `runtime/channel_boundary.py` | SHARED publish + skip-by-origin inject-routing + Realtime subscriber (built; Realtime transport stubbed) |
| `runtime/channel_boundary_run.py` | boundary entrypoint: the shared-aware publish hook, `run_boundary`, `verify_my_half` |
| `runtime/supabase_principal.py` | the reusable least-privilege Supabase principal (auth→JWT) |
| `runtime/session_channels.py` · `mcp_face/tools/channels.py` | System 2: Session Fabric structure (channels/gatherings/edges/conducted) + `channels`/`channel_act` |
| `runtime/cc_attachments.py` · `runtime/attachment_types.py` · `attachment_types/*.py` | channel-attachment bindings + the type registry |
| `mcp_face/remote.py` | the remote-MCP gateway: identity→posture filter (safe-posture reads only for clients) |
| `build-prep/claude-design/supabase/supabase/migrations/0002–0010` | the live Supabase schema + two-gate RLS (applied) |
| `build-prep/claude-design/supabase/functions/claude-design-gateway/index.ts` | the thin OAuth forwarder edge function |
| `.data/channels/_channels/design.json` | the live seeded shared channel (`shared:true`) |
