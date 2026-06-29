---
type: proposal
area: channels
title: The CHANNELS Fusion — one channel concept, built into the Company
posture: both sides are incomplete, AI-generated, unreviewed; no source of truth; no horizon. Goal = best parts of each, fused, BUILT INTO THE COMPANY. No duplicates inward or outward.
register: prescriptive
status: unconfirmed
provenance: Company-side claims VERIFIED LIVE against source (file:line below). OWUI donor-side (threads/reactions/@model/webhook/socket) is MAP-SOURCED from owui-side-map.md — read against installed open_webui 0.9.6, NOT re-verified here.
verified_live: 2026-06-28
sources:
  - runtime/cc_channels.py
  - runtime/session_channels.py
  - runtime/channel_boundary.py
  - runtime/channel_boundary_run.py
  - mcp_face/tools/cc_channel.py
  - mcp_face/tools/channels.py
  - ops/owui_room.py
relates-to:
  - "[[area-D-channels-voice]]"
  - "[[area-A-runtime-core]]"
  - "[[owui-side-map]]"
---

# The CHANNELS Fusion

> One channel concept. An OpenWebUI channel **is** a Company channel: `session_channels` durable structure +
> `cc_channels` live transport, with OWUI's valuable surface (threads, reactions, realtime socket,
> @model-participant, members UX) built INTO the Company. No parallel channel store survives — inward
> (the two Company stores) or outward (OWUI's schema as a second home).

---

## 1. BEST PARTS — honestly, each side

### Company side (VERIFIED LIVE — file:line)

- **A clean transport/structure split that already exists.** This is the keeper architecture, not a problem to erase:
  - `cc_channels.py` — **live-session transport**: `live_sessions()`, `find()`, `push()` dispatching over TWO transports through ONE interface — `"channel"` (HTTP POST to a member's port) and `"supervised"` (supervisor `/inject` for fork-owned sessions) (`runtime/cc_channels.py:96-198` region; transport resolved by `_transport_of(reg)`). Presence is real: `_alive(pid)` = `os.kill(pid,0)`, pruned on dead pid.
  - `session_channels.py` — **durable structure**: `fold_channels()` projects channel rows `{id, kind, name, purpose, mode, coordinator, status, members:{sid→{participation,added}}, …}` from an **append-only log** (`agent_sessions/channels.jsonl`), `append_channel_event()` validates `kind ∈ CHANNEL_OPS` and fsyncs under graph-lock (`runtime/session_channels.py:307-353`). Closed vocabularies: `CHANNEL_OPS`, `KINDS=(channel,gathering)`, `MODES=(direct,conducted)`, `PARTICIPATION=(awake,listening)`, `ROW_STATUS`.
- **Coordination modes** `direct` (fan to every member) vs `conducted` (whole post → ONE intent to a coordinator) — a richer routing primitive than OWUI has (`session_channels.py` MODES; `channel_act(action='post')` doc, `mcp_face/tools/channels.py:178-232`).
- **Gatherings** — momentary grabs, promotable to durable channels (`gather`/`promote`/`disperse`), with provenance stamped both ways. OWUI has no equivalent.
- **Two-store-honest shared edge.** `channel_boundary.py` publishes to Supabase `channel_posts` as a **least-privilege RLS principal** (not service-role), with `route_inject()` skip-by-origin fan-out — the cross-instance (company ↔ Claude Design) timeline (`runtime/channel_boundary.py`).
- **Reactions-as-control, already proven live** in `ops/owui_room.py`: tapping 🛑/❌ on a member's message tears it down, ⏸/✋ interrupts its turn — native, works on the phone (`ops/owui_room.py:438-454`). This is the genuine UX win on the Company side, but it lives in a parallel daemon (see §3).

### OWUI side (MAP-SOURCED — owui-side-map.md §2, read against open_webui 0.9.6, not re-verified here)

- **@model as a first-class streaming participant.** `model_response_handler` parses `@model` mentions, builds thread history into a system prompt, and calls the **full chat-completion pipeline** (tools, RAG, filters) with `chat_id=channel:{id}`, streaming tokens back as `message:update` events (owui-side-map §2 → `routers/channels.py:854-1018`). This is the differentiator.
- **A real Slack-style relational schema** — 7 tables: `channel` (standard/group/dm), `channel_member` (role, status, muted, pinned, `last_read_at` → unread), `message` (`reply_to_id`, `parent_id` thread-root, `is_pinned`), `message_reaction` (emoji, aggregated `{name,users[],count}`), `channel_webhook` (bot identity, `secrets.token_urlsafe(32)`), `channel_file`.
- **Realtime via Socket.IO** — room `channel:{id}`, events `message` / `message:reply` / `message:update` (incl. streaming AI tokens) / `message:reaction:add|remove` / `message:delete`, plus `typing` and `last_read_at` (owui-side-map §2 Socket.IO).
- **Members/roles + unread/mute/pin per member**, three access models (standard-ACL / private-group / DM), inbound webhooks with bot identity.

### OWUI weak parts (do NOT inherit — owui-side-map §2 "Fragile")
Single-level threads only (no nesting); **public webhook endpoint fully unauthenticated** (token-in-URL = the password, no HMAC/rate-limit); **AI response in a BackgroundTask with bare `except: log.exception`** → failures swallowed (violates the Company's no-silent-failure law); hard-delete messages; fixed 0.15s throttle, no backpressure; the UI itself is a compiled SvelteKit bundle (fork-only, license-capped at 50 users).

---

## 2. THE FUSED CHANNEL — what ONE channel concept is

**Identity:** an OWUI channel `channel:{owui_id}` **is** a Company channel `channel://{id}`. One row in
`session_channels` (`channels.jsonl`) is the durable truth; `cc_channels` is its live transport; the OWUI
channel is a **rendered face** of that same row, not a second store.

Concretely, the relationship flow — each OWUI capability built INTO an existing Company primitive:

1. **Structure → `session_channels` row.** OWUI's `channel` + `channel_member` map onto the existing
   `fold_channels` row: `name/purpose/mode/coordinator/members{sid→{participation}}/status`. OWUI roles
   (`manager`) and per-member `muted/pinned/last_read_at` become **new fields on the member sub-record**
   (additive events: `channel.member_status` already exists; extend its payload — registry-is-truth, a
   field not a new code path). No new table; OWUI's 7-table schema collapses into the one append-only leaf.

2. **Transport/realtime → `cc_channels.push` + the Socket.IO emitter as a SINK.** A `channel_act(action='post')`
   already fans `direct`→every member (live→supervisor inject) or `conducted`→coordinator. The fusion adds
   ONE sink: after the durable append, emit the same event to OWUI's `channel:{id}` Socket.IO room
   (`message`, `message:update`, `message:reaction:*`). The OWUI socket becomes a **projection of Company
   channel events**, not an independent message bus. Humans on the OWUI UI and AI members on `cc_channels`
   transport see one timeline.

3. **@model-as-member → a Company member whose transport is the brain, not a session.** OWUI's `@model`
   first-class participant generalizes to the Company's existing member model: a channel member can be a
   **session** (reached via `cc_channels` inject) OR a **brain/role** (reached via `cognition.run_role` /
   `brain_router.ask`). An `@mention` of a brain-member routes the thread history + post as a model turn and
   streams the reply back as `message:update` — reusing the Company's grounded chat pipeline (Suite.chat,
   TIM-RULE model pick) instead of OWUI's. Built into `channel_act` post-routing as a third member-kind,
   not a special case. **Fix on the way in:** the AI turn must NOT be a swallowed BackgroundTask — failure
   surfaces as a Notice + a (Gap) note (the Company's no-silent-failure law), unlike OWUI's bare `except`.

4. **Threads → the existing `thread` provenance, extended one level.** `channel_act` posts already mint/join
   a `thread` (`mcp_face/tools/channels.py` post-routing → `agent_sessions/mail.jsonl` thread index). OWUI's
   `parent_id` single-level thread maps directly onto this thread id. (OWUI's no-nesting limit is acceptable
   for v1; nesting is a later field, flagged not blocked.)

5. **Reactions-as-control → promoted from the owui_room daemon into the channel primitive.** The 🛑/⏸ reaction
   handlers proven live in `ops/owui_room.py:438-454` become first-class channel events
   (`message:reaction:add` → `interrupt`/`teardown` via supervisor) folded into the same post-routing layer —
   so control gestures work for ANY channel face, not only the owui_room daemon's rooms.

**Net:** humans (OWUI UI), AI sessions (`cc_channels` transport), and AI brains (cognition) are all
**members of one channel row**, exchanging on one durable timeline, with realtime delivered through whichever
face a member is attached to (Socket.IO for humans, inject for sessions, model-turn for brains).

---

## 3. COMPANY-INTERNAL RESOLUTION — heal the duplication, keep the legitimate layering

The three-layer split is **legitimate and stays**: transport (`cc_channels`) ≠ durable structure
(`session_channels`) ≠ cross-instance shared edge (`channel_boundary`). The confusion is NOT the layering —
it is a duplicated **named-channel store** and a duplicated **MCP tool surface** sitting on top of it.

### 3a. The real duplication (verified live)
There are **two named-channel stores**:
- `session_channels.create_channel/add_member/remove_member/archive_channel` → `agent_sessions/channels.jsonl`
  (append-only log, the forward-truth structure layer).
- `cc_channels.create_channel/list_channels/add_member/remove_member/archive_channel`
  (`runtime/cc_channels.py:459-543`) → `.data/channels/_channels/<id>.json` (a JSON-per-channel store).

Two stores for the same concept (a named channel + its roster). This is the inward duplicate.

### 3b. The doubled MCP tool surface (verified live)
Both auto-register via pkgutil (`mcp_face/server.py:112-115`):
- `cc_channel` (`mcp_face/tools/cc_channel.py:35`) — live-messaging ops (`list/send/broadcast/mail`) **AND**
  channel-management ops (`create_channel/list_channels/add_member/remove_member/archive_channel`) backed by
  `cc_channels`' own store.
- `channels` + `channel_act` (`mcp_face/tools/channels.py:92,178`) — CQRS pair backed by `session_channels`.

The channel-management ops on `cc_channel` **duplicate** `channel_act`. The live-messaging ops do NOT.

### 3c. The fix (precise — which functions move, which stay)
1. **Fold `cc_channels`' named-channel store INTO `session_channels`.** Delete
   `cc_channels.create_channel/list_channels/add_member/remove_member/archive_channel` and the
   `_channels/<id>.json` store; the one channel-structure truth is `channels.jsonl`. **KEEP** `cc_channels`'
   live-messaging ops (`live_sessions/find/push/send/broadcast/mail` + the two transports) — those are the
   transport layer and are NOT duplicated.
2. **Collapse the MCP surface to ONE shape.** `cc_channel`'s channel-management ops are removed (they backed
   the deleted store); `cc_channel` keeps ONLY `list/send/broadcast/mail` (live messaging). All channel
   structure (create/add/remove/archive/mode/promote/gather/disperse) goes through `channels`/`channel_act`.
   Result: ONE write tool for structure (`channel_act`), ONE read tool (`channels`), ONE live-messaging tool
   (`cc_channel`) — no overlap.
3. **Fold `ops/owui_room.py` into `session_channels`.** owui_room currently holds its OWN roster in
   `.data/owui_room_state.json` (`rooms = {cid: {name, roster}}`, `ops/owui_room.py:57-87`) and imports
   `cc_channels`+`cc_clone` but NOT `session_channels` — a third parallel roster. Re-base it: each OWUI
   channel it manages becomes a `session_channels` row (its roster = the row's `members`); spawn/teardown/
   rename/persona become `channel_act` member events + supervisor calls; its proven reaction-control and
   member↔member breaker stay (promoted into the channel primitive per §2.5). owui_room shrinks to the
   **OWUI-face adapter** (token holder, Socket.IO bridge, webhook minting) over the one structure layer —
   not a separate channel engine.

After this: ONE channel row store, ONE structure tool-pair, ONE live-messaging tool, ONE roster — the OWUI
room daemon and the MCP face both project the same `session_channels` truth.

---

## 4. BROKEN / HALF-BUILT SEAMS this rests on (named as work, not assumed)

1. **`channel_boundary` Realtime — built, but unverified-live AND unwired (three-part seam, verified):**
   - *Mechanism:* **implemented**, not a stub. `ChannelInjectSubscriber.start()` is a full websocket client —
     `postgres_changes` join, `on_message→parse_realtime_message→on_insert` chain, phoenix heartbeat +
     JWT token-refresh, reconnect-with-backoff (`runtime/channel_boundary.py:198-249`). `build_join_msg`/
     `parse_realtime_message` are offline-unit-tested (`:297-310`). **This corrects the area-A map's claim of
     "Realtime transport is STUBBED."**
   - *Live round-trip:* **UNVERIFIED.** The file itself states (`:319`) "LIVE WS round-trip pending." No
     connection to live Supabase tables has been confirmed.
   - *Hook ABSENT:* nothing routes a durable channel post into the boundary. `session_channels.py` has only
     keyword hits on "shared/thread" (`:190,481,514,648`) — **zero** `channel_boundary` import or call. The
     publish path and subscriber both exist; the discriminator that decides "this post is shared → publish it"
     does not. (area-A flagged this as pending the shared-vs-internal product call.)
   - *Entrypoint not running:* `runtime/channel_boundary_run.py` exists as the entrypoint but is **not** in
     `ops/services.json` and has no systemd unit — entrypoint exists; not confirmed running.

2. **`ops/owui_room.py` is a manually-launched daemon, not a service.** Not in `ops/services.json`, no
   systemd unit (verified) — run by hand with `OWUI_PASSWORD=… .venv/bin/python ops/owui_room.py`. Its OWUI
   base (`http://127.0.0.1:8081`) and home-channel id are env/hardcoded defaults. Folding it (§3c.3) is the
   work; until then it is a parallel roster that can drift from `channels.jsonl`.

3. **OWUI's unauthenticated public webhook** (`POST /webhooks/{id}/{token}`, map §2) — if the fusion ingests
   via OWUI webhooks, the token-in-URL with no HMAC/rate-limit is inherited insecurity. Decide: keep webhooks
   as the human/bot ingress but gate them, or replace with `cc_channels` transport. (Work, not assumed safe.)

4. **OWUI AI-turn error-swallowing** (map §2: BackgroundTask bare `except`) — must NOT be inherited. The
   fused @model/@brain turn (§2.3) routes through the Company's no-silent-failure law (Notice + Gap on
   failure). This is a behavior the fusion must ADD, not port.

5. **Member-kind extension is unbuilt.** §2.3 (brain-as-member) and the per-member `muted/pinned/last_read_at`
   fields (§2.1) are additive events on `session_channels` that do not exist yet — named as the build, not
   present.

---

## 5. VERIFICATION DONE (what I checked live + result)

| Check | Method | Result |
|---|---|---|
| Three channel layers exist | Read `cc_channels.py`, `session_channels.py`, `channel_boundary.py` | CONFIRMED — transport / durable-structure / shared-edge, distinct modules |
| Doubled MCP tool surface | Read `mcp_face/tools/cc_channel.py:35`, `channels.py:92,178`; `server.py:112-115` pkgutil auto-register | CONFIRMED — `cc_channel` (msg+channel-mgmt) and `channels`/`channel_act` (CQRS) both register |
| Two named-channel STORES | `grep` in `cc_channels.py:459-543` vs `session_channels.py:307-353` | CONFIRMED — `_channels/<id>.json` (cc) vs `channels.jsonl` (sc) — the real duplicate |
| owui_room reinvents roster, imports cc_channels not session_channels | Read `ops/owui_room.py` (full, 612 lines); imports line 34 | CONFIRMED — `from runtime import cc_channels, cc_clone`; own `rooms` state in `.data/owui_room_state.json:57-87` |
| owui_room reaction-control live | Read `ops/owui_room.py:438-454` | CONFIRMED present — 🛑/⏸ → teardown/interrupt via supervisor |
| `channel_boundary` Realtime "stubbed"? | Read `channel_boundary.py:198-249` (start/heartbeat) + `:297-319` (tests/self-note) | CORRECTED — mechanism IMPLEMENTED (full WS client); live round-trip UNVERIFIED (`:319` self-admits); hook into session_channels ABSENT (grep: zero calls); entrypoint not in services.json/systemd |
| Launch status of boundary + owui_room | `grep services.json`, `ls ~/.config/systemd/user` | CONFIRMED — neither is a registered/systemd service; both manual entrypoints |

**Not verified (declared):** OWUI donor-side internals (threads/reactions/@model/webhook/Socket.IO events) are
taken from `owui-side-map.md` (read against installed `open_webui` 0.9.6), NOT re-read here. The fusion lands
in the Company, so verification was spent on the Company side.
