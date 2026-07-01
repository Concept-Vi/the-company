---
id: item-5c0698ed
address: board://item-5c0698ed
type: document
source: claude_code
state: draft
title: Operator Surface — CONNECTION MAP & MERGE decision (v2 foundation, code locations)
author_session: lead
channel: operator-surface
thread: ''
links: []
order:
- board://item-d24d4cee
- board://item-35838c61
- board://item-e0f2ad78
- board://item-9bc59336
- board://item-e8d75d8a
created: '2026-06-28T12:23:39.880175+00:00'
updated: '2026-06-28T12:23:39.970048+00:00'
history:
- from: null
  to: draft
  by: lead
  ts: '2026-06-28T12:23:39.880175+00:00'
  note: filed
- from: edit
  to: order
  by: ''
  ts: '2026-06-28T12:23:39.970048+00:00'
  note: edited in place
---

The connection-map workflow output (8 regions, ~944k tokens), synthesized. RESOLVES the architecture: MERGE. The bridge (runtime/bridge.py :8770) is the ONE warm process holding the single Suite brain + the single FsStore + the operator-token vantage; every /api/* route is a thin json projection of a Suite method. The standalone ops/surface_server.py I built is THE ISLAND (own 2nd store, own in-mem SSE, own renderer, dumb chat relay, 2nd channel registry) — it rides cc_* directly and never touches the bridge. Per Tim's convergence methodology (no side is canon; islands-join-mainland), v2 = the surface becomes a pure-client PWA the bridge serves, riding /api + /api/stream + the operator token; the standalone backend is RETIRED. The existing thin client surface/app (:5174, already over the bridge) is the likely target — 'adopt/finish surface/app', not 'rebuild surface_server.py'. Full per-region inventory: workflow wuz1tjpk9 output.
