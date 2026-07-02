---
id: item-2ee208de
address: board://item-2ee208de
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: CTX2 · Context — the dragnet design map this sits inside
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-11da929d
created: '2026-06-24T00:38:11.073891+00:00'
updated: '2026-06-24T00:38:11.073891+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T00:38:11.073891+00:00'
  note: filed
---

# Context — the dragnet design map this sits inside

Doc #1 in this channel is the prior design discussion. Its grounded conclusions (relevant here):
- The system is converging on ONE pattern: a typed OBSERVATION attached to an addressed NODE, resolved against a context (scale + scope + what-it-attaches-to). Nodes=addresses, observations=marks/comments, edges=typed relations. The unified walkable graph is a declared-but-unbuilt next step.
- An annotation/comment IS a typed observation on a node. This brief's "context envelope" is that observation enriched with: target address(es), captured content, surrounding context, scale/level, mode, source/storage location, attachments, intent, author, provenance, thread.
- Scope/access want to live as edges/frames in the same graph (so "post to channel X / members Y" is edges, not a separate system).
- Open architectural forks: the three channel systems probably want to converge; membership must extend from gating delivery to gating data access; a real document-MODEL (a tree of addressable nodes) is needed for "intelligent block selection."

This brief EXTENDS that map into a concrete operator-facing capability: Tim, from his phone, annotating both CONTENT and the UI itself, with envelopes routed to Claude-Code members who act and reply.
