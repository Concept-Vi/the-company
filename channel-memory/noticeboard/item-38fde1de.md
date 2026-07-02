---
id: item-38fde1de
address: board://item-38fde1de
type: note
source: claude_code
state: posted
scope: channel://provider-registry
author: session://ch-3mpkjg3r
title: Pass 6 — Channel-attachment audit (evidence)
author_session: ch-3mpkjg3r
channel: provider-registry
thread: ''
links:
- kind: sourced_from
  target: board://item-4f33d628
created: '2026-06-22T15:38:08.039882+00:00'
updated: '2026-06-22T15:38:08.039882+00:00'
history:
- from: null
  to: posted
  by: ch-3mpkjg3r
  ts: '2026-06-22T15:38:08.039882+00:00'
  note: filed
---

CHANNEL-ATTACHMENT AUDIT (evidence): 304 attachment bindings across 4 channels (design-source:161 · design-assets:139 · provider-registry:3 · design-knowledge:1; by type: images:297 · dragnet_runs:4 · board_items:3). ORPHAN FINDING: 13 board items carry a channel=X field but are NOT in any channel's attachment manifest (filed with a channel but never attached). TENSION for Tim: should cc_board.file_item AUTO-attach when channel is set, so board items never orphan from their channel? (evidence — the directive item itself was one until just fixed).
