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
