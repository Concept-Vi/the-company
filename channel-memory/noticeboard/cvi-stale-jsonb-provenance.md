---
id: cvi-stale-jsonb-provenance
address: board://cvi-stale-jsonb-provenance
type: note
source: cvi_mine
state: posted
scope: project://the-fusion
author: agent://unknown
title: 'Provenance: the stale projects.notice_board JSONB was NOT migrated'
author_session: ''
channel: ''
thread: ''
links: []
created: '2026-07-02T09:41:06.066248+00:00'
updated: '2026-07-02T09:41:06.066248+00:00'
history:
- from: null
  to: posted
  by: ''
  ts: '2026-07-02T09:41:06.066248+00:00'
  note: filed
---

④ L6-BOARD pour provenance (organ-studies/BOARD.md §1 A1): the cloud carried the board TWICE — the normalized notice_board_posts table (319 rows, POURED losslessly onto this board with their uuids) and an embedded projects.notice_board JSONB array (the SUPERSEDED copy of the same rows: block-composition's froze at 128 while the table grew to 279; the three small projects' JSONB equals their table rows). Migration 20260412070000's own header is the smoking gun: the dashboard read the corpse. The JSONB is therefore NOT migrated — it is the family's negative evidence that a board projected into a container must be DERIVED, never stored there (the law container.board_items now obeys). Source: cvi_mine (read-only).
