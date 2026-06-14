# Cross-Session Channels — PROVEN BY USE (2026-06-14)

Tim's original hallmark goal — message INTO another live Claude Code session's actual conversation
(no inbox-polling), both directions, and group chat — is built and proven live through the company MCP.

## Mechanism
Claude Code **Channels** (code.claude.com/docs/en/channels). A session launched with
`--mcp-config /home/tim/company/channels/channel.mcp.json --dangerously-load-development-channels server:company-channel`
runs `channels/company_channel.mjs`, which declares `claude/channel`, registers
`{handle,session_id,cwd,description,pid,port}` under `.data/channels/<handle>.json`, turns a POST to its
port into a `notifications/claude/channel` event (injected into the live conversation), and exposes
`reply` (routes to supervisor `/channel-reply` → mailbox → pushed back into the asking session) and
`announce` (sets the session description). Works in INTERACTIVE sessions, not headless `-p`.

## Proven live 2026-06-14 (3 channel sessions + the lead, all via mcp__company__cc_channel)
- **Discovery** — `cc_channel op=list` saw 4 live sessions; auto-PRUNED a dead one (4→3) = real presence.
- **Identity** — `announce` set the lead's description (ch-al7jdfdr); shows in discovery.
- **1:1 send** — `op=send` to ch-83e2cque returned ok:true; message landed in its live conversation.
- **Reply back (the loop, no polling)** — ch-83e2cque called `reply`; "CROSSPROOF received" was PUSHED
  into the LEAD's conversation (originator-routing via the thread). Verified in the mail log:
  message 16:50:56 → reply 17:06:00, thread t-1781419856-ch-83e2cque.
- **Group broadcast** — `op=broadcast` to ch-83e2cque + ch-piffgfxv: one message, both ok:true, one
  shared thread g-1781420795.
- **Durable record** — every message + reply in `.data/channels/_mail.jsonl`.

## Tools (all on the company MCP, file-drop auto-registered)
- `cc_channel(op=list|send|broadcast|mail)` — runtime/cc_channels.py + mcp_face/tools/cc_channel.py
- per-session: `announce`, `reply` (channels/company_channel.mjs)
- supervisor: `/channel-reply`, `/channel-send` (runtime/session_supervisor.py)

## Design (Tim, locked 2026-06-14)
identity = cwd + self-announced description · replies go THROUGH the mailbox AND get pushed into the
right session (recipient never chooses to look) · group = the fabric `channels` concept (members = live
sessions).

## Next increments (not yet built)
- Capture each session's claude `session_id` at registration (join the 1,098-session catalog/dossiers).
- Auto-join: a SessionStart hook so sessions opt into the channel without the manual launch flag
  (Tim chose "global" — but the ~/.claude.json edit was auto-denied as a self-mod; needs his explicit ok
  or the per-launch flag stays).
- Wire group membership to the real fabric `channels`/`channel_act` (named persistent groups), so a
  broadcast targets a named channel, not an ad-hoc handle list.
- Reply aggregation surfaced in the UI / RHM; distinct per-session voices (the voice thread).
