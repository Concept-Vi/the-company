---
id: item-1b14bf34
address: board://item-1b14bf34
type: block
source: claude_code
state: current
title: S7 · RHM integration — render everything as human meaning + two chat modes
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.237942+00:00'
updated: '2026-06-28T13:05:39.808910+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.237942+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.697768+00:00'
  note: v2 MERGE rewrite (in place)
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:03:19.371238+00:00'
  note: restore v1 content dropped in v2 rewrite
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:05:39.808910+00:00'
  note: fold corroboration corrections (3 unbiased agents)
---

S7 · RHM integration — RIDE the grounded brain (MERGE)
DECISION (Tim): two chat modes confirmed + talk to MORE THAN ONE member.
v2: surface chat TODAY is a dumb relay (cc.send to whatever lead is alive, surface_server.py:848-868). The grounded RHM brain already exists on the bridge: /api/chat/stream (bridge.py:2918 → chat_parts suite.py:6761, NDJSON parts). RIDE it.
RENDER everything through /api/up-translate (1875 → up_translate suite.py:7353; the {kind,ref,lead,mechanism,grounded,degraded} envelope, abstains on empty), /api/coa (3045 → coa), /api/address-help (~1811 → address_help suite.py:3496). Honour grounded/degraded as honest gaps.
TWO MODES: RHM-chat (ask the SYSTEM about itself, grounded) + channel-chat (talk to live members; via session_channels post_to_channel — fans to many, satisfying talk-to-more-than-one). Route cheap 'what is this' through up_translate, not a lead turn.
RESTORED(v1): CLICK-ANYTHING-TO-EXPLAIN — any element carrying a ui:// (or any) address → /api/address-help or /api/up-translate = a model-free, deterministic 'what is this' at Tim's altitude (distinct from a chat turn; doesn't burn a lead).
CORROBORATED + UNEXPLOITED doors: S7 named only the EPHEMERAL /api/chat/stream — chat PERSISTENCE already exists: /api/conversations + /api/conversation + /api/conversation/new (bridge.py:1773-1775). Use them so RHM threads persist across sessions.
