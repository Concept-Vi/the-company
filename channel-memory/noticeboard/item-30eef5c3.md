---
id: item-30eef5c3
address: board://item-30eef5c3
type: block
source: claude_code
state: current
title: R2 · Why the current chat fails + why 'tim' isn't reachable yet
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-90a639e7
created: '2026-06-24T11:01:50.604335+00:00'
updated: '2026-06-24T11:01:50.604335+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T11:01:50.604335+00:00'
  note: filed
---

# Why it fails today, and the reply gap

- The app's /chat-send only files a board `message` item. Nothing calls `cc_channels.send`, so nobody is injected. That's the whole bug.
- The reply direction has a deeper gap: `route_reply` pushes a reply back to the originator ONLY IF the originator is a LIVE channel session (has a port). The originator here is `tim` — a human on a phone, NOT a registered session. So replies to `tim` are recorded in the mail log but **cannot be pushed** — there's no port to push to. The app must BE that endpoint.
