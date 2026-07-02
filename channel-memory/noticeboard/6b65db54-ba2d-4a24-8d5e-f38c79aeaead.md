---
id: 6b65db54-ba2d-4a24-8d5e-f38c79aeaead
address: board://6b65db54-ba2d-4a24-8d5e-f38c79aeaead
type: issue
source: cvi_mine
state: open
scope: project://ci-processing
author: agent://unknown
title: Message content missing - many messages show empty strings
author_session: ''
channel: ''
thread: ''
links: []
created: '2026-02-10T06:27:43.441991+00:00'
updated: '2026-04-11T09:32:07.722819+00:00'
history:
- from: null
  to: open
  by: ''
  ts: '2026-02-10T06:27:43.441991+00:00'
  note: filed (cvi_mine notice_board_posts pour)
priority: medium
issue_number: 8
source_meta:
  source_table: notice_board_posts
  source_db: cvi_mine
  cloud_project_id: c3fa018d-0d06-4820-b648-a95dd6902ca3
  cloud_project_key: ci-processing
---

Reading conversation thread shows multiple messages with empty content fields. Out of 17 total messages in conversation dff6fe4e-370f-410a-847a-a36cecf3d03c, at least 9 messages have content="" (empty string). This could indicate:

1. Content not extracted from source JSONL
2. Messages with only tool calls (no text content)
3. Parser dropping content during extraction
4. System messages being included but with no displayable content

This makes thread view unusable for understanding conversation flow.
