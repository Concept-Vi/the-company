---
id: item-d24d4cee
address: board://item-d24d4cee
type: block
source: claude_code
state: current
title: C0 · The spine (who holds what)
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-5c0698ed
created: '2026-06-28T12:23:39.895534+00:00'
updated: '2026-06-28T12:23:39.895534+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T12:23:39.895534+00:00'
  note: filed
---

ONE warm process holds the brain; everything else is a projection.
- BRIDGE (runtime/bridge.py :8770, stdlib HTTP+SSE) holds the ONE warm Suite (suite.py) + ONE FsStore + mints/validates the operator-token vantage (_mint_operator_token :564, _is_genuine_operator :572). do_GET :1416 / do_POST :2499 = giant if/elif over path literals; each route a thin json projection of a Suite.<method>.
- MCP FACE (mcp_face/server.py) is built LAZILY against THIS SAME Suite (bridge.py:598-604) — agent face + HTTP face = two doors, one brain.
- CANVAS APP (canvas/app, Vite→proxy :8770): api.ts = ~75 fetch wrappers; useAppController.ts = the SSE dispatch-by-kind hub (:632-720).
- STANDALONE OPERATOR SURFACE (ops/surface_server.py :8782) = THE ISLAND: own FsStore, own process-local in-mem SSE (lost on restart, no replay, surface_server.py:42-53), rides cc_board/cc_channels DIRECTLY, writes comments with NO event emission → the rest of the company never sees them.
- EVENT BUS = the live spine: events.jsonl; events_since (fs_store.py:629) reads shared file (captures BOTH faces); /api/stream (bridge.py:2091) SSE tail with ?since=/Last-Event-ID replay. CAVEAT: append_event seq is process-local-unique only (fs_store.py:589-596); the mailbox (:1394) took the cross-process lock and is the model.
