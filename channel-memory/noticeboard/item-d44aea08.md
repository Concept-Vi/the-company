---
id: item-d44aea08
address: board://item-d44aea08
type: block
source: claude_code
state: current
title: M5 · What this means for our build
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-8798b611
created: '2026-06-24T11:10:37.693738+00:00'
updated: '2026-06-24T11:10:37.693738+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T11:10:37.693738+00:00'
  note: filed
---

# What this means for us

- The live chat we just wired (app /chat-send → cc_channels push → my session) IS this official mechanism — confirmed working (the test injected, delivered:true).
- Our company_channel.mjs is the working reference the fork builds on: declares `claude/channel`, emits the notification, exposes a `reply` tool. The fork's job: (a) the reply path to the BROWSER (SSE on the app, per the docs' pattern) so my replies appear without reload; (b) register the app as a pushable member so replies route to it; (c) member picker + role-resolution for 'the lead'; (d) project switcher.
- Reliability notes to carry: keep the lead session persistent (events only while open); gate sender; expect batched-to-turn delivery; build our own delivered/seen confirmation. We're on Linux/WSL not Windows, so #46125 doesn't bite.
Sources: code.claude.com/docs/en/channels · /channels-reference · /mcp · github anthropics/claude-code #41733 #3174 #46125.
