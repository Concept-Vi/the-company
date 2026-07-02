---
id: item-ec9ebc51
address: board://item-ec9ebc51
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: M3 · The reply path (two-way)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-8798b611
created: '2026-06-24T11:10:37.631732+00:00'
updated: '2026-06-24T11:10:37.631732+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T11:10:37.631732+00:00'
  note: filed
---

# Reply path — external app ← Claude

- Add `tools: {}` capability + register a standard MCP tool (e.g. `reply(chat_id, text)`).
- Put an `instructions` string in the server constructor telling Claude when to reply + which `meta` attr to route back on (injected into the system prompt).
- Claude calls the reply tool → the handler sends the reply OUT (POST to the platform, or SSE broadcast). The docs' local example uses SSE on `GET /events` purely so `curl -N` can watch replies live — that's the model for pushing replies to OUR browser app.
- Permission relay also exists (v2.1.81+): `claude/channel/permission` to approve tool-use remotely — only with sender gating.
