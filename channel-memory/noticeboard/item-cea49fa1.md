---
id: item-cea49fa1
address: board://item-cea49fa1
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P12 · ❌ Intent tags, priority, status lifecycle, diff previews, versioning,
  au
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-f9f4a6a6
created: '2026-06-24T01:32:22.070229+00:00'
updated: '2026-06-24T01:32:22.070229+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:22.070229+00:00'
  note: filed
---

### ❌ Intent tags, priority, status lifecycle, diff previews, versioning, audit trail (BD-D additions)
The envelope should be structured — it already is (typed observation + content + address + thread). The *additions* (intent enum, priority, received/working/applied status, proposed-change diff preview, stale-target detection) are a workflow-management system bolted onto a comment. Tim writes prose; the lead infers intent from prose perfectly well today. Add structure when the *volume* of envelopes makes prose-routing fail — not before. A diff-preview-before-it-lands is a genuinely nice future feature and a genuinely large build; it is not this week.
