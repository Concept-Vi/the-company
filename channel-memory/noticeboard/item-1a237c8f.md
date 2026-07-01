---
id: item-1a237c8f
address: board://item-1a237c8f
type: block
source: claude_code
state: current
title: S13 · Home + production floor
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.329569+00:00'
updated: '2026-06-28T13:05:39.878519+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.329569+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.790400+00:00'
  note: v2 MERGE rewrite (in place)
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:03:19.435623+00:00'
  note: restore v1 content dropped in v2 rewrite
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:05:39.878519+00:00'
  note: fold corroboration corrections (3 unbiased agents)
---

S13 · Home + production floor (mostly DISSOLVES under MERGE)
DECISION (Tim): home gets a bigger augmentation — needs-me first + a channel/project view + more.
v2 HOME: RIDE /api/greeting (bridge.py:1737 → Suite.greeting suite.py:2076 — the caught-up digest ALREADY at Tim's altitude) as the opening screen + the needs-me inbox (S5) + a channel/project browser (S2) + an artefact gallery. Empty = 'nothing needs you · N running'.
PRODUCTION FLOOR mostly DISSOLVES under MERGE: the bridge is ALREADY a durable long-running service → RETIRE the v1 'separate company-surface systemd service' item; full-board rescan → RIDE /api/board (1597, one shared projection); the bespoke md_to_html → use the canvas app's real renderer.
NET-NEW that remains: outbound device PUSH (Web-Push/VAPID — NOTHING in the repo does it; SSE only reaches a foregrounded app) tiered 1:1 with a needs-me card; an offline service-worker.
RESTORED(v1): OFFLINE QUEUED COMMENTS — a comment written with no signal QUEUES and sends on reconnect (Tim is mobile, on the move); not just a read-cache service-worker. Also: loading/empty/ERROR states in HUMAN REGISTER (a failure is a sentence Tim understands + a Gap note, never a stack trace or silent no-op — no-silent-failure on the surface's own paths).
CORROBORATED + prerequisite: outbound Web-Push REQUIRES a service worker — NONE exists; today's auto-reload is SSE + location.reload() (surface_server.py:445) and the SW must not collide with it. Name the SW as the push prerequisite. Concurrency [NOT VERIFIED]: ThreadingHTTPServer + one shared Suite, no visible request-lock → run tests/concurrency_acceptance before trusting concurrent operators.
