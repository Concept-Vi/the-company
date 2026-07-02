---
id: item-ff6f34f7
address: board://item-ff6f34f7
type: block
source: claude_code
state: current
scope: channel://operator-surface
author: agent://lead
title: S11 · Multi-session attribution
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.300080+00:00'
updated: '2026-06-28T12:56:17.760206+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.300080+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.760206+00:00'
  note: v2 MERGE rewrite (in place)
---

S11 · Multi-session attribution (RIDE the roster)
DECISION (Tim): show WHICH session/lead/MODEL — not the binary You/Vi.
v2 (MERGE): RIDE the bridge's session roster (/api/channels bridge.py:1569) + board author_session (cc_board.py:233). Surface today collapses all authors to You/Vi (surface_server.py:55-60).
NET-NEW: the `model` field is ABSENT from the /api/sessions projection (the agent_sessions event log carries no model) — a field-plumb/join, not just a render tweak. Ties to S3 (self) + S6 (routing targets = these same members).
