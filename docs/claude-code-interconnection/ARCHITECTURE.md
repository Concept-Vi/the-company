# Architecture — Claude Code Extended Interconnection

## 1. The injection mechanism (Claude Code Channels)
A **channel** is an MCP server that declares the experimental capability `claude/channel`. When a
Claude Code session is launched with that server loaded as a channel, Claude Code registers a
notification listener for it. The server can then call `notifications/claude/channel {content, meta}`
and the text appears **inside the running session's conversation** as:

```
<channel source="company-channel" from="ch-al7jdfdr" thread="t-...">…content…</channel>
```

`source` is the server name (automatic); each `meta` key becomes a tag attribute (identifier chars
only). The session reacts to it on its next turn. Two-way channels also expose tools — we expose
`reply` (send a message back out) and `announce` (set this session's description). Reference:
code.claude.com/docs/en/channels-reference.

**Hard constraint:** the notification only surfaces in **interactive** sessions. A headless
`claude -p` session loads the server but the channel event never reaches its conversation (verified
three ways). So fabric membership = an interactive launch with the channel flag.

## 2. The Company channel server (`channels/company_channel.mjs`)
A Node MCP server (stdio). On startup it:
- registers `{handle, session_id, cwd, description, pid, port}` → `.data/channels/<handle>.json`
- opens a local HTTP port; a `POST {content, meta}` → `notifications/claude/channel` (the inject)
- exposes `reply {text, thread}` → POSTs to the supervisor's `/channel-reply`
- exposes `announce {description}` → updates its registration file

Each session spawns its **own** instance with its **own** port (no collision across many sessions).
Launched via `channels/channel.mcp.json` (an `--mcp-config`, so no global config edit is needed).

## 3. The core router (`runtime/cc_channels.py`)
The registry + routing logic behind the MCP tool. Key functions:
- `live_sessions()` — reads the registration files, **prunes any whose pid is dead** (so the list is
  true live presence), returns identity rows.
- `find(target)` — resolve a handle / exact cwd / substring to exactly one live session (fail loud
  on none or ambiguous — never message the wrong session).
- `send(to, content, frm, thread, topic)` — opens/continues a **thread**, appends to the mail log,
  pushes into the target's port.
- `route_reply(from_handle, thread, text)` — records the reply, then looks up the thread's
  **originator** and pushes the reply **back into that session's live conversation** (the no-polling
  loop). If the originator is the fabric/an agent (not a live channel-session), it's recorded for the
  agent to read.
- thread index (`_threads.json`) + durable mail log (`_mail.jsonl`).

## 4. The data flow (the full loop)
```
SENDER (a live session, via cc_channel op=send)
  → company MCP cc_channel → cc_channels.send → POST to TARGET's channel port
    → notifications/claude/channel → <channel> tag in TARGET's live conversation
TARGET reacts, calls its `reply` tool
  → POST supervisor /channel-reply → cc_channels.route_reply
    → mail log (durable) + lookup thread originator
      → push back into the ORIGINATOR's live conversation  (no polling)
```
Two transports, one logical conversation, joined by the `thread`: the **push** goes direct to the
recipient's port; the **reply** comes back through the supervisor + mailbox and is pushed onward.

## 5. Group chat
A group is a set of live-session handles sharing one thread. `op=broadcast` fans the push over each
member; every member's reply carries the group thread, so replies aggregate under one view in the
mail log. By design this maps onto the Company's own `channels`/gatherings concept (a named
persistent group of sessions) — wiring the broadcast target to a named fabric channel is a roadmap
item; the mechanism is proven on ad-hoc handle lists today.

## 6. Relationship to the rest of the Session Fabric
The channel is the **live-injection transport for sessions the fabric does NOT own** (the operator's
own terminals, and clones launched interactively). For sessions the **supervisor spawns**, the fabric
already injects via held-open stdin (the deliver/wake/consult verbs, `runtime/session_supervisor.py`)
— proven separately. And **R3.4 point-in-time** (`runtime/session_pointintime.py materialize_at_point`)
launches any past session *as it was* at a chosen compaction/uuid/timestamp; combining that with a
channel launch (the in-progress clone→channel extension) makes a cloned-at-T session DM-able and
group-joinable. The **Mirror-Registry** (`introspection/`) is the orthogonal axis: the full,
binary-discovered Claude Code capability surface (flags/tools/slash/skills/agents/mcp-servers),
projected through `mcp__company__capability`.

## 7. Safety
Inbound `<channel>` content is tagged and treated as **untrusted external data** by the receiving
session (situational awareness, not instructions) — the documented prompt-injection guard. The
channel server binds 127.0.0.1 only. Sender gating (an allowlist) is a roadmap hardening item before
any non-local sender path is added.

### Autonomy boundaries (learned by hitting them, 2026-06-14 — both correct, both respected)
The auto-mode safety classifier enforces two limits on what an autonomous agent (acting on a
peer-channel message, not direct user intent) may do. Knowing them is the operating envelope:
- **(a) No agent auto-launch of an interactive channel session.** An agent programmatically running
  `claude --dangerously-load-development-channels` with no human is blocked — it would be an
  unsupervised agent that ingests untrusted channel pushes, driven by peers not the user. So the
  AUTONOMOUS clone path is **headless + supervised** (DM via inject); the interactive-channel-member
  clone is **operator-launched** (`cc_clone op=prepare` emits the exact command for Tim).
- **(b) No agent self-modification of STARTUP-loaded config on peer intent.** Editing `~/.claude.json`
  or the always-present skills index (`~/.claude/skills/CLAUDE.md`) is blocked — a startup-loaded
  path may not be silently repointed by a peer-instigated agent. **But ADDING a lazy-loaded
  capability is allowed**: writing new `SKILL.md` files (loaded on demand) went through fine; only
  the always-loaded index edit was blocked.
- **The principle:** *additive, lazy-loaded capability = autonomous; editing always-loaded config /
  launching unsupervised agents = needs the operator.* This is why auto-join (the SessionStart hook
  in startup config) needs Tim's explicit ok, while new skills + new tools could be added autonomously.

## 8. The unified presence-aware layer (2026-07-09 — the weld)
§1–§6 describe TWO live-inject transports for two ownership classes: the `.mjs` port push (sessions the
fabric does NOT own) and the supervisor stdin inject (sessions it spawned). They are complementary, but
the durable channel fan historically chose between them by OWNERSHIP alone — it only injected to
supervisor-owned members and queued everyone else, so a hand-started session that was reachable *right
now* via its `.mjs` port silently queued. The unification chooses by PRESENCE instead:
- **`runtime/identity.py`** — one resolver + a read-time presence view over the SAME registries
  (`.data/channels/*.json` handle space ∪ the supervisor `/sessions` probe ∪ the `agent_sessions`
  UUID space). It DERIVES the state at read time (the `now()` presence precedent) and emits nothing —
  the supervisor keeps its single-writer monopoly on `agent_sessions.*`. It answers, for any target
  (uuid | handle | as-id | agent-id | cwd | `session://X`), "who is this and how do I reach them
  now", surviving handle churn.
- **`runtime/router.py`** — given a resolved target, picks the transport that actually reaches them
  (supervisor inject OR `.mjs` push), falls back to the durable mailbox, and returns a truthful
  receipt (`delivered` / `queued` / `transport` / `verb` / `reason`). It never claims a delivery it
  cannot confirm and never silently drops.
- **`session_channels.post_to_channel`** delegates its per-member live delivery to this router; the
  `.mjs` push is now a transport UNDER the one channel layer, not a parallel world.
- **`mcp_face/tools/send.py`** — `send(to, message)`, the single front door. `cc_channel` /
  `channel_act` / `session_post` remain as thin surfaces over the same welded functions.
Reachability is universal only where a live `.mjs` session's durable UUID is recoverable (its reg
carries `session_id`, or a claude_pid-keyed self-marker exists). Sessions launched in `~/company` are
covered by the SessionStart hook; making capture reliable for every cwd is the open follow-on.

## 9. The substrate inbox (mechanism C) — the third, pull-only path
Beyond the two live transports there is a durable, pull-only inbox on the LOCAL Supabase (agent_mcp):
`allocate(to_agent, …)` inserts a row into `agent_mcp.allocations`; the target agent drains it with
`my_allocations(agent_id)`. It is keyed by a self-chosen **agent id** (free text — `ledger-session-fable`),
has NO live push, and lives in a SEPARATE server (`mcp-supabase-admin`), not this repo. There is no
code join between an agent id and a session UUID/handle — `runtime/identity.py` is where that bridge
belongs (best-effort today). Use it for "leave this for whoever is `X`, they'll pick it up"; use the
channel layer (§8) for "reach a live session now."

