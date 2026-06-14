# Claude Code Extended Interconnection

The system that lets Tim's Claude Code sessions **find each other, talk to each other's live
conversations, group-chat, clone-and-relaunch each other at any point in time, and (next) hold
spoken conversations** — all driven through one chat and through the Company MCP.

Built and proven by use 2026-06-14. This directory is the clean, structured reference for everything
in it. (Operational how-tos also live as **skills**; this is the architecture + reference.)

## Why it exists
Tim runs many Claude Code sessions across many directories. The asset is *the specific
conversation's context* in each. He wanted: reach the ACTUAL live session (never a fresh stand-in),
message across them, make groups, and drive the whole fleet from one place — extending into voice
and into launching any past session as-it-was at a chosen moment.

## The pieces
| Piece | What it does | Where |
|---|---|---|
| **Channels** | Inject a message into a live session's conversation; it can reply back | `channels/company_channel.mjs` |
| **cc_channels core** | Registry of live sessions, push/send, reply-routing, threads, mail log | `runtime/cc_channels.py` |
| **Supervisor routes** | `/channel-reply`, `/channel-send` (route replies to the mailbox + push-back) | `runtime/session_supervisor.py` |
| **MCP tool** | `cc_channel` (list/send/broadcast/mail) — the agent surface | `mcp_face/tools/cc_channel.py` |
| **Session Fabric** | spawn/inject/wake/consult + **R3.4 point-in-time** materialize | `runtime/session_supervisor.py`, `runtime/session_pointintime.py` |
| **Mirror-Registry** | the full Claude Code capability surface, binary-discovered | `introspection/`, `platforms/`, `mcp_face/tools/introspection.py` |
| **@xsession loadout** | embed (session search) + voice + STT on the GPU | `ops/services.json` combos |

## Documents here
- **[ARCHITECTURE.md](ARCHITECTURE.md)** — the mechanism, components, data flow, and the hard constraints.
- **[REFERENCE.md](REFERENCE.md)** — every tool, endpoint, launch command, and the loadout, with examples.
- **[ROADMAP.md](ROADMAP.md)** — what's built ✅, in progress, and next.

## Proven (2026-06-14, with Tim watching)
Discovery (auto-prunes dead sessions) · self-identity (`announce`) · 1:1 inject into a live session ·
reply pushed back into the asker's conversation (no polling) · group broadcast to N sessions under
one thread · group reply-aggregation. All through `mcp__company__cc_channel`, not shell. Two
sessions (a lead + a time-travelled fork of it) collaborated live over the channel. Evidence:
`build-prep/CROSS-SESSION-CHANNELS-PROVEN.md`, mail log `.data/channels/_mail.jsonl`.

## The one hard constraint
Channels deliver into **interactive** sessions only — not headless `claude -p` (confirmed three
ways: a headless session loads the channel server and even says it's "watching for channel
messages", but the notification never surfaces in its conversation). So a session joins the fabric
by being launched interactively with the channel flag (see REFERENCE). The supervisor's `-p` path is
for fabric-owned sessions (deliver/wake/consult); the channel is for the operator's own live
terminals and for clones launched interactively.
