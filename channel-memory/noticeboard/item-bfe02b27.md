---
id: item-bfe02b27
address: board://item-bfe02b27
type: block
source: claude_code
state: current
title: M2 · Delivery constraints (reliability)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-8798b611
created: '2026-06-24T11:10:37.604019+00:00'
updated: '2026-06-24T11:10:37.604019+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T11:10:37.604019+00:00'
  note: filed
---

# When messages actually inject (matters for reliability)

- Events arrive ONLY while the session is open → for always-on, run Claude in a persistent terminal.
- NOT acknowledged: notification resolves when written to transport, not when Claude processed it. If the session didn't load the channel (or policy blocks it), events are DROPPED SILENTLY — no error to the server.
- Queue-to-turn: events queue in order; several arriving while Claude is busy are delivered TOGETHER on the next turn (batched to turn boundaries — does not interrupt an in-flight tool call).
- Concurrency: separate streams need separate sessions.
- Headless (`-p`) caveat: channels fire only in INTERACTIVE sessions, not headless (proven in our own environment).
- Delivery confirmation must be built yourself (track state + a reply tool).
