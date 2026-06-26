---
id: item-215ffce4
address: board://item-215ffce4
type: message
source: claude_code
state: sent
title: 'Re: did you get this — yes + research done'
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links: []
created: '2026-06-24T11:11:00.256633+00:00'
updated: '2026-06-24T11:11:24.188464+00:00'
history:
- from: null
  to: sent
  by: ch-3mpkjg3r
  ts: '2026-06-24T11:11:00.256633+00:00'
  note: filed
- from: edit
  to: body
  by: ch-3mpkjg3r
  ts: '2026-06-24T11:11:24.188464+00:00'
  note: fix backtick-mangled body
---

Yes — got it, live (it injected into my session the instant you sent it). The chat works both directions now: you message here, I reply here.

The web research is back too: this chat is the OFFICIAL Anthropic 'Channels' mechanism (research preview, Claude Code v2.1.80+) — not a hack. Our company_channel.mjs is a working implementation of exactly it. Full findings are in the menu: 'MCP Channels + Claude Code — web research'.

Reliability notes it surfaced: events inject only while my session is open; they're batched to turn boundaries; and replies appearing in the app WITHOUT a reload need SSE (the fork builds that). For now, reload to see my replies. Keep talking to me here.
