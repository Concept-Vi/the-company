---
id: item-addd2919
address: board://item-addd2919
type: block
source: claude_code
state: current
title: OB3 · What's lossy or gated (honest)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-156ec226
created: '2026-06-24T05:12:11.408573+00:00'
updated: '2026-06-24T05:12:11.408573+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:11.408573+00:00'
  note: filed
---

# What's lossy or gated

- GRAPH VIEW is partial/lossy: Obsidian's graph is path-based [[wikilinks]]; our edges are TYPED, ADDRESS-based (board://, image://, code://, decision://). It can't carry the edge KIND and can't see cross-scheme targets at all (~50 of our edges would simply not appear). So OUR typed graph must stay canonical; Obsidian's graph is a rough bonus view, not the real one.
- TITLE LEGIBILITY: every item currently reads as `item-xxxx` / "Note" — any Obsidian surface needs a human-title pass first or it's unreadable.
- iOS + SYNC depends on the sync infra (WSL vs Windows) — confirm before relying on it.
