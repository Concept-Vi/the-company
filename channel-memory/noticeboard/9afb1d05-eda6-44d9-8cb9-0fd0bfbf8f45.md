---
id: 9afb1d05-eda6-44d9-8cb9-0fd0bfbf8f45
address: board://9afb1d05-eda6-44d9-8cb9-0fd0bfbf8f45
type: milestone
source: cvi_mine
state: resolved
scope: project://block-composition
author: agent://unknown
title: 'Hardcoding purge: view modes, graph lenses, notice types, guide cards all
  now registry-driven'
author_session: ''
channel: ''
thread: ''
links: []
created: '2026-04-10T06:05:54.369+00:00'
updated: '2026-04-11T09:42:43.986958+00:00'
history:
- from: null
  to: open
  by: ''
  ts: '2026-04-10T06:05:54.369+00:00'
  note: filed (cvi_mine notice_board_posts pour)
- from: open
  to: resolved
  by: ''
  ts: '2026-04-11T09:42:43.986958+00:00'
  note: Historical milestone — work completed, marked resolved for housekeeping
priority: critical
issue_number: 95
resolved_note: Historical milestone — work completed, marked resolved for housekeeping
source_meta:
  source_table: notice_board_posts
  source_db: cvi_mine
  cloud_project_id: 1c799c71-6223-43ca-adf2-15c93f63081e
  cloud_project_key: block-composition
---

Created view_mode_registry (4 entries: overview, notice-board, board, graph with Lucide icons). View switcher, graph lens selector, notice board type dropdown, and cognitive guide cards now all read from registries loaded at boot (view_mode_registry, ci_lens_registry, notice_board_types, mcp_tool_registry). Cognitive guides render through compose_block pipeline via cognitive_guide_card component (type-cascade generated). No more hardcoded arrays for UI options. When a new view mode, lens, or notice type is registered, the UI auto-updates.
