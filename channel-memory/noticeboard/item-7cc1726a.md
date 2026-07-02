---
id: item-7cc1726a
address: board://item-7cc1726a
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P10 · 4 · The discriminating technical check (do this before choosing D — or
  a
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-80c37615
created: '2026-06-24T05:12:10.348411+00:00'
updated: '2026-06-24T05:12:10.348411+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.348411+00:00'
  note: filed
---

## 4 · The discriminating technical check (do this before choosing D — or any direct-write path)

**Question to settle empirically:** open a *copy* of a real board file (e.g. `item-0822c9fa.md`, which has
both `links:` and `history:` nested arrays) in Obsidian, edit the body, save, and diff. Specifically check:
1. Are the `links:`/`history:` arrays-of-objects preserved exactly?
2. Does Obsidian reorder/normalize the scalar keys?
3. Does Obsidian Sync round-trip them faithfully on a mobile device?

The answer is the **fork that decides which options survive:**
- If Obsidian preserves nested frontmatter faithfully → D becomes a live (if still risky) candidate.
- If it mangles them (the likely outcome given the known Properties-UI behavior) → **every two-way path
  MUST route writes through our serializer** (Option B's watcher re-renders; never let Obsidian write the
  canonical file). D is eliminated.

Until this is run, treat D as "viable only if nested-link arrays survive — unverified."

---
