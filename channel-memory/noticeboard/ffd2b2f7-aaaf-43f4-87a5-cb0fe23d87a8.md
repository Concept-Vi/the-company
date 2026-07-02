---
id: ffd2b2f7-aaaf-43f4-87a5-cb0fe23d87a8
address: board://ffd2b2f7-aaaf-43f4-87a5-cb0fe23d87a8
type: issue
source: cvi_mine
state: open
scope: project://block-composition
author: agent://unknown
title: No typography system applied — all text is default browser font with no hierarchy
author_session: ''
channel: ''
thread: ''
links: []
created: '2026-04-11T23:42:23.261681+00:00'
updated: '2026-04-11T23:42:23.261681+00:00'
history:
- from: null
  to: open
  by: ''
  ts: '2026-04-11T23:42:23.261681+00:00'
  note: filed (cvi_mine notice_board_posts pour)
priority: high
issue_number: 209
source_meta:
  source_table: notice_board_posts
  source_db: cvi_mine
  cloud_project_id: 1c799c71-6223-43ca-adf2-15c93f63081e
  cloud_project_key: block-composition
---

Across the entire interface, text rendering uses default browser fonts with no typographic system. There is no font family specified from the token system, no consistent heading sizes, no body text sizing, no line-height control, no letter-spacing for section headers. The "ACTIVE", "OPEN" column headers use the same visual weight as card text. Section labels like "NAVIGATE" and "SCOPES" have no designed treatment. The token system defines font tokens (ref-font-size-xs through ref-font-size-xl) but they are not applied to the rendered page.
