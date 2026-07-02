---
id: item-03e6c64e
address: board://item-03e6c64e
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: 'P10 · 8 · Display: opaque ids in the graph'
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-4baaab55
created: '2026-06-24T05:12:09.495011+00:00'
updated: '2026-06-24T05:12:09.495011+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:09.495011+00:00'
  note: filed
---

## 8 · Display: opaque ids in the graph

**[Observed]** Filenames are opaque (`item-1492565a`) → every graph node and link reads as a hash. Real friction for Tim (who reads meaning, never ids).

- **`aliases:` frontmatter** or a title-display plugin (Front Matter Title) makes notes *display* their `title` while the file stays `item-XXX.md` — fixes legibility **without breaking the 1:1 wikilink map.** Recommended. **[Inferred]**
- **Mirror-with-title-filenames** (A2 only): name mirror files by title — prettiest graph, but **breaks the `board://item-XXX → [[item-XXX]]` 1:1 map** (now needs an id→title lookup table, and titles collide/change). The thin shim stops being thin. A real tension: legibility vs the zero-lookup property that makes everything else cheap.

---
