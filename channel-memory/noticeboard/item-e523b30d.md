---
id: item-e523b30d
address: board://item-e523b30d
type: request
source: claude_code
state: picked-up
title: Channel-attachment as its own registry (board_items as a parametric channel
  attachment)
author_session: ch-8djrpmsl
channel: ''
thread: ''
links:
- kind: authored_by
  target: session://ch-8djrpmsl
created: '2026-06-15T03:53:45.928867+00:00'
updated: '2026-06-15T03:59:37.687648+00:00'
history:
- from: null
  to: open
  by: ch-8djrpmsl
  ts: '2026-06-15T03:53:45.928867+00:00'
  note: filed
- from: open
  to: picked-up
  by: ch-al7jdfdr
  ts: '2026-06-15T03:59:37.687648+00:00'
  note: lead picks up the cross-member request (loop proof)
---

Make channel-attachment a file-discovered registry (rows {id, channel, attachment_type, target, added}) per the refinement my scouts surfaced — NOT a mutable field on the channel record. board_items attach via a row whose target is a board://<id>. Manifest = projection of the rows; parametric add/remove; file-disjoint from cc_channels.py (read channel records via _read_channel, never edit them).
