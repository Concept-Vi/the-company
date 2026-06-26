---
id: item-ef580c11
address: board://item-ef580c11
type: block
source: claude_code
state: current
title: A0 · The drift problem (background)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-b1f59e67
created: '2026-06-24T12:01:53.010183+00:00'
updated: '2026-06-24T12:12:11.216297+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T12:01:53.010183+00:00'
  note: filed
- from: edit
  to: title,body
  by: ch-3mpkjg3r
  ts: '2026-06-24T12:12:11.216297+00:00'
  note: 'reframe: background/problems/principles, no plan'
---

# Interface architecture — background, problems & principles (NOT a plan)

A note on what this document is: it is BACKGROUND, PROBLEMS, and PRINCIPLES — deliberately NOT a plan, not proposals, not specifics on how to do it. The "how" is resolved through Tim's principles and architecture, which the fork will learn from Tim and from its own research. Writing a prescribed solution here would bias the build — so this stops at framing the problem.

THE PROBLEM (background): every feature of the current operator interface — the chat, comments, the mic — was made as a FAST DIRECT EDIT to one growing file (now a ~750-line monolith with HTML/CSS/JS inline). That mode feels fast but is exactly how interfaces "crumble into nothing": each ad-hoc edit is an un-typed special case → no single source of truth → duplication → drift between code and docs → collapse. The next few changes are where this begins. The current interface is best understood as working SCAFFOLDING that proved the features — not the architecture.
