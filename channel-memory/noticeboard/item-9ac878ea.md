---
id: item-9ac878ea
address: board://item-9ac878ea
type: block
source: claude_code
state: current
title: S10 · Artefacts — re-anchoring, orphan tray, live/interactive
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.284787+00:00'
updated: '2026-06-28T12:56:17.744665+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.284787+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.744665+00:00'
  note: v2 MERGE rewrite (in place)
---

S10 · Artefacts — re-anchoring + orphan tray + live/interactive
DECISION (Tim): artefacts re-anchor.
v2: re-anchoring (CSS-locator + text-match fallback, unified with text-span anchoring as ONE model) + an orphan tray for un-pinnable comments (no-silent-failure).
LIVE ARTEFACTS = the generalization: a run-monitor / recall-browser IS an artefact (a live bridge-served view). SECURITY: the safe postMessage boundary drops allow-same-origin → BREAKS today's same-origin annotation injection (surface_server.py:597-678). So **S8+S9+S10 are ONE coupled build** — the annotation path must move to postMessage too. In MERGE, engine calls from an artefact route through /api + the human-tier gate (verb whitelist).
