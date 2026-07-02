---
id: item-ed91000e
address: board://item-ed91000e
type: document
source: claude_code
state: draft
scope: channel://operator-surface
author: agent://lead
title: Operator Surface — BUILD PLAN (v1, Tim's decisions folded)
author_session: lead
channel: operator-surface
thread: ''
links: []
order:
- board://item-ceab1d6a
- board://item-8b7205f5
- board://item-572076e7
- board://item-7255a2ba
- board://item-b23ab2a9
- board://item-d74491b9
- board://item-a8c3a376
- board://item-c04403bc
- board://item-1b14bf34
- board://item-bfdbb6a1
- board://item-d5a29c32
- board://item-9ac878ea
- board://item-ff6f34f7
- board://item-42ae858e
- board://item-1a237c8f
- board://item-7997649f
- board://item-3865097a
created: '2026-06-28T11:35:00.088965+00:00'
updated: '2026-06-28T14:05:16.361875+00:00'
history:
- from: null
  to: draft
  by: lead
  ts: '2026-06-28T11:35:00.088965+00:00'
  note: filed
- from: edit
  to: order
  by: ''
  ts: '2026-06-28T11:35:00.362129+00:00'
  note: edited in place
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.556391+00:00'
  note: v2 MERGE rewrite (in place)
- from: edit
  to: order
  by: ''
  ts: '2026-06-28T14:05:16.361875+00:00'
  note: edited in place
---

BUILD PLAN v2 (MERGE) — updated IN PLACE over v1, folded onto the connection-map evidence (item-5c0698ed) + the recovered region + the 5 code-verified company-improvements. v1 assumed the standalone ops/surface_server.py gets extended; the map proved THAT IS THE ISLAND. v2 architecture: the surface MERGES into the bridge (runtime/bridge.py :8770 — the one warm Suite+FsStore+operator-vantage) as a pure-client PWA riding /api + /api/stream; the standalone backend is RETIRED; the existing thin client surface/app (already over the bridge) is the base — 'adopt/finish surface/app', not 'rebuild surface_server.py'. Each block: DECISION (Tim, preserved) · v2 RIDE-vs-BUILD with file:line · file/path-level changes. The 5 COMPANY-IMPROVEMENTS are folded into scope (convergence methodology — fix in the centre). Read-before-write; cite locations so unbiased agents corroborate.
