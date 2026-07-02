---
id: item-01fe6ca8
address: board://item-01fe6ca8
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P8 · 5. Properties / frontmatter UI — PARTIAL, and write-risky.
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-3480c157
created: '2026-06-24T05:12:09.838161+00:00'
updated: '2026-06-24T05:12:09.838161+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:09.838161+00:00'
  note: filed
---

### 5. Properties / frontmatter UI — PARTIAL, and write-risky.
Obsidian's Properties panel renders **flat** frontmatter fields editably and nicely (good for eyeballing `type`/`state`/`channel`). But our `links:` and `history:` are **lists-of-objects** (nested) — Obsidian's Properties UI handles those poorly and editing them by hand is error-prone. And *any* edit here is a **WRITE** → straight into the two-writer conflict. Useful as a read-display of the scalar fields; not a place to author. Axis 1 partial, Axis 2 red.
