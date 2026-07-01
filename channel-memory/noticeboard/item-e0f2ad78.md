---
id: item-e0f2ad78
address: board://item-e0f2ad78
type: block
source: claude_code
state: current
title: C2 · MERGE — the decision + why
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-5c0698ed
created: '2026-06-28T12:23:39.925101+00:00'
updated: '2026-06-28T12:23:39.925101+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T12:23:39.925101+00:00'
  note: filed
---

RECOMMENDATION: MERGE. The surface becomes a pure-client PWA the bridge serves (like it serves /studio, bridge.py:1428), consuming /api + /api/stream + the operator token. The standalone surface_server.py BACKEND is retired. surface/app (:5174, already 'deliberately thin over the SAME bridge') is the likely target shape — v2 ≈ 'adopt/finish surface/app', not 'rebuild surface_server.py'. MERGE does NOT mean cramming logic into the 3669-line bridge.py — it means deleting the surface's parallel scaffolding (2nd FsStore, in-mem SSE, bespoke renderer, relay chat, 2nd channel registry) and serving a static front-end over /api.
Five factors: (1) warm-Suite — favors riding the bridge (the brain is expensive, held alive by the one process; the island has no Suite at all). (2) operator-token vantage lives in the bridge → favors MERGE (CONSUME makes the surface a forever-second-class foreign client proving identity across a process boundary). (3) duplication → strongly MERGE (the island re-implements 2nd store, in-mem SSE, 2nd renderer, relay chat, 2nd channel registry — all already solved in the centre). (4) mobile-reachability → WASH (both bind 127.0.0.1; tailnet exposure is identical work either way — verified). (5) Tim's laws = tie-breaker → MERGE: surface_server.py IS the textbook island; the law isn't 'cleaner bridge between island+mainland' (=CONSUME), it's 'island's good parts built INTO the centre + drop parallel scaffolding' (=MERGE).
CARRY INTO THE CENTRE (the island's good parts): the working inbound-push loop (fabric→server→SSE + 'tim' member registration, surface_server.py:63-72/829-841 — the correct two-way pattern), the mobile bottom-sheet/tabbar UI, the per-deploy auto-reload chrome. RETIRE: everything behind those.
