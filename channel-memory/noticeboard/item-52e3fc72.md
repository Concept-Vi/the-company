---
id: item-52e3fc72
address: board://item-52e3fc72
type: block
source: claude_code
state: current
title: P8 · Option C — Derived parallel vault + inbox replay
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-80c37615
created: '2026-06-24T05:12:10.292710+00:00'
updated: '2026-06-24T05:12:10.292710+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.292710+00:00'
  note: filed
---

### Option C — Derived parallel vault + inbox replay
Like A for the read direction (a separate derived vault, clean plane separation), but the vault has a
designated **inbox area** (e.g. `_inbox/` notes, or a Templater capture) where Obsidian-authored input
lands as *new* notes with a known shape. The watcher replays only the inbox into the runtime as new board
items; the rest of the vault stays a read-only projection that gets regenerated. This gets you iOS
write-back **without** ever risking the projected canonical-mirror files, because input and projection are
physically separated planes.

- **Truth:** intact; cleanest separation of "lens" and "intake."
- **Gain:** iOS write-back for *new* annotations (the dominant case) with near-zero conflict surface.
- **Cost:** duplicate storage (a derived vault alongside the canonical dir); *editing an existing item's
  body* from Obsidian is not supported by the inbox plane (you'd add a comment, not edit the body) — which
  is arguably *correct* under mark-is-truth anyway (you annotate, you don't overwrite). This option is B's
  conflict-free subset made physical.
