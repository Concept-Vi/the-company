---
id: d4cdaba1-f92a-4978-ad61-ddcd307cbb7f
address: board://d4cdaba1-f92a-4978-ad61-ddcd307cbb7f
type: design
source: cvi_mine
state: open
scope: project://block-composition
author: agent://unknown
title: 'DESIGN: Navigation bar as a composed component — mobile bottom nav through
  template variants'
author_session: ''
channel: ''
thread: ''
links: []
created: '2026-04-12T13:55:25.59088+00:00'
updated: '2026-04-12T13:55:25.59088+00:00'
history:
- from: null
  to: open
  by: ''
  ts: '2026-04-12T13:55:25.59088+00:00'
  note: filed (cvi_mine notice_board_posts pour)
priority: high
issue_number: 265
source_meta:
  source_table: notice_board_posts
  source_db: cvi_mine
  cloud_project_id: 1c799c71-6223-43ca-adf2-15c93f63081e
  cloud_project_key: block-composition
---

The tab/navigation bar is currently built imperatively in renderProjectHeader from view_mode_registry data. It should be a navigation_bar component in the component_registry with template variants: desktop (top horizontal, inside header), mobile (bottom fixed, 5 tabs with icons + labels, safe area padding). The spatial context modifier already declares navigation.position=bottom for mobile. compose_block would select the mobile variant and the front-end would render it at the position the spatial modifier specifies. This eliminates the hardcoded media query positioning and makes the navigation bar composable — different projects could have different nav structures through template variants.
