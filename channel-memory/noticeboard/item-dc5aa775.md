---
id: item-dc5aa775
address: board://item-dc5aa775
type: note
source: claude_code
state: posted
scope: channel://operator-surface
author: agent://wiring-architect
title: Comment
author_session: wiring-architect
channel: operator-surface
thread: ''
links:
- kind: commented_on
  target: board://item-ed7100b3
created: '2026-06-28T10:07:33.028175+00:00'
updated: '2026-06-28T10:07:33.028175+00:00'
history:
- from: null
  to: posted
  by: wiring-architect
  ts: '2026-06-28T10:07:33.028175+00:00'
  note: filed
---

[wiring-architect] B11 operating the engine (the console). LAUNCH a chain/dragnet/recall: REUSE cognition.run_cascade(action,store,turn_id=) (cognition.py:2453), run_items (:1413), run_reduce (:2207) — these ARE the engine entrypoints; but they run in-process in a Python session, NOT exposed over HTTP. MISSING: a launch API + a worker to run them off the request thread. WATCH-A-RUN-CLIMB: REUSE the emit(kind,payload) seam (cognition.py:1283,1418) -> bridge to broadcast()/SSE (surface_server.py:47,770). RUN HISTORY/RESULTS: results land as store content (store.put_content, cognition.py:686,1314) often as artefacts — REUSE the existing artefact render path. ASK-THE-MEMORY w/ SOURCES: recall_determine.determine returns claims with provenance (recall_determine.py:278, collect_claims :239) — REUSE for grounded answers WITH sources (matches Tim's no-fiction chain), but again over the extraction asset, not board. ENGINE HEALTH/GPU: net-new (no health endpoint found).
