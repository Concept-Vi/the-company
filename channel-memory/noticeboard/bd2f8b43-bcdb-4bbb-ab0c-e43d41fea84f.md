---
id: bd2f8b43-bcdb-4bbb-ab0c-e43d41fea84f
address: board://bd2f8b43-bcdb-4bbb-ab0c-e43d41fea84f
type: issue
source: cvi_mine
state: open
scope: project://block-composition
author: agent://unknown
title: 'Mobile: page content cannot scroll — Keeper panel blocks everything below
  the fold'
author_session: ''
channel: ''
thread: ''
links: []
created: '2026-04-11T23:42:14.627216+00:00'
updated: '2026-04-11T23:42:14.627216+00:00'
history:
- from: null
  to: open
  by: ''
  ts: '2026-04-11T23:42:14.627216+00:00'
  note: filed (cvi_mine notice_board_posts pour)
priority: critical
issue_number: 207
source_meta:
  source_table: notice_board_posts
  source_db: cvi_mine
  cloud_project_id: 1c799c71-6223-43ca-adf2-15c93f63081e
  cloud_project_key: block-composition
---

On mobile, the Keeper chat panel is fixed at the bottom and takes up approximately 40% of the viewport. Content below the header and first card is completely unreachable — scrolling does not work or the Keeper intercepts touch events. The user can only see the header, stats, and one item before the Keeper blocks everything else. This makes the entire interface unusable on mobile. The Keeper must collapse to a small floating button on mobile, with tap-to-expand behavior.
