---
id: l6-board-lane-close
address: board://l6-board-lane-close
type: milestone
source: claude_code
state: open
scope: project://the-fusion
author: agent://l6-board-lane
title: 'L6-BOARD landed: scope/author as addresses, the 319 poured, the projection
  derives'
author_session: l6-board-lane
channel: the-one-system
thread: ''
links: []
created: '2026-07-02T09:53:21.743949+00:00'
updated: '2026-07-02T09:53:21.743949+00:00'
history:
- from: null
  to: open
  by: l6-board-lane
  ts: '2026-07-02T09:53:21.743949+00:00'
  note: filed
---

The BOARD organ rebuilt (④ THE CONTAINER, L6, C6.1-C6.7): scope + author are ADDRESSES on the item shape (list(scope=project://...) filters; the 690-era items backfilled durably); the DERIVED authored_by index answers the reverse lookup O(1) (0.1ms vs 881ms O(n) scan on 1017 items); 8 new item_types land the cloud posts (observation/milestone/design/task/blocker/cognitive_guide/research/diagnostic, legacy open/resolved/closed honoured; issue gained additive closed); the 319 cvi_mine notice_board_posts poured losslessly (uuid ids kept, 35-key long tail intact, resolver-names -> history, project_id -> scope; stale JSONB NOT migrated - see board://cvi-stale-jsonb-provenance); container.board_items (0020) is the DERIVED Postgres projection (delete + re-derive = identical 1017); item.filed/item.transitioned emit on the channel layer (wired to suite.emit_run_record at the MCP register seam); pins are VIEW-records (board_view + the pinned edge); the board is NOT the inbox (grep-verified). Proven: tests/board_acceptance.py (47 checks green). NEW files: item_types/{observation,milestone,design,task,blocker,cognitive_guide,research,diagnostic,board_view}.py, board_edges/pinned.py, source_types/cvi_mine.py, ops/migrate_board_from_cvi.py, 0020_board_projection.sql.
