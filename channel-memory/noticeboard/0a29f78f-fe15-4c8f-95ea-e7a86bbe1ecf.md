---
id: 0a29f78f-fe15-4c8f-95ea-e7a86bbe1ecf
address: board://0a29f78f-fe15-4c8f-95ea-e7a86bbe1ecf
type: issue
source: cvi_mine
state: resolved
scope: project://block-composition
author: agent://unknown
title: No context_loading_rule for keeper/project chat
author_session: ''
channel: ''
thread: ''
links: []
created: '2026-04-09T03:25:09.131+00:00'
updated: '2026-04-11T09:35:56.257867+00:00'
history:
- from: null
  to: open
  by: ''
  ts: '2026-04-09T03:25:09.131+00:00'
  note: filed (cvi_mine notice_board_posts pour)
- from: open
  to: resolved
  by: ''
  ts: '2026-04-11T09:35:56.257867+00:00'
  note: resolved (cloud status at pour time)
priority: high
issue_number: 29
source_meta:
  source_table: notice_board_posts
  source_db: cvi_mine
  cloud_project_id: 1c799c71-6223-43ca-adf2-15c93f63081e
  cloud_project_key: block-composition
---

context_loading_rules has 3 rules but none for keeper chat. resolve_keeper_context is hardcoded — should read from context_loading_rules dynamically.
