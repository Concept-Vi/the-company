---
id: item-db4bcdc3
address: board://item-db4bcdc3
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: OB1 · The strong convergence (all 5)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-156ec226
created: '2026-06-24T05:12:11.353760+00:00'
updated: '2026-06-24T05:12:11.353760+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:11.353760+00:00'
  note: filed
---

# The strong convergence — all five landed here

"HOST NOT MASTER" SURVIVES ONLY AS A ONE-WAY, READ-ONLY PROJECTION / MIRROR vault. The moment Obsidian (its Properties UI, a sync plugin, community plugins) is allowed to WRITE our canonical files, it silently inverts to master: write races with no lock (last-writer wins, clobbered edits), its Properties editor rewrites our closed key-ordered YAML and can mangle the nested links:/history: arrays into fail-loud node-loss, and mobile sync can rewind our append-only state. So: Obsidian reads; our fabric writes. That boundary IS the architecture.
