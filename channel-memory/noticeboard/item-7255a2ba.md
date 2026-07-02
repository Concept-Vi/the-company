---
id: item-7255a2ba
address: board://item-7255a2ba
type: block
source: claude_code
state: current
scope: channel://operator-surface
author: agent://lead
title: S3 · Self-resolution + default scoping (the 'self' system)
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.154795+00:00'
updated: '2026-06-28T12:56:17.619624+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.154795+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.619624+00:00'
  note: v2 MERGE rewrite (in place)
---

S3 · Self-resolution + default scoping (FIX v1's error)
DECISION (Tim): a 'self' system resolves values from the caller; search DEFAULTS to the caller's own channel, params override.
v2 FIX (v1 was WRONG): the self→handle join is NOT 'one lookup'. resolve_own_session (session_scan.py:137-196) returns ONLY {path,session_id,project_dir,cwd,how,ambiguous} — NEITHER handle NOR claude_pid. BUT the join key (claude_pid, session_scan.py:48) AND the matching .data/channels/*.json reg ARE read internally in _self_marker (session_scan.py:115/118) and then DISCARDED before return.
BUILD: `channels_for_self()` = expose that already-running internal join (return {handle,claude_pid,port,profile,session_id} → channel membership). Does NOT exist (zero grep). Then search defaults to the caller's channel; params → specific/range/all.
NOTE (Tim): 'every agent is for me' → locality default (where am I), not an ownership gate.
