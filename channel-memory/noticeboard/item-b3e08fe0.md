---
id: item-b3e08fe0
address: board://item-b3e08fe0
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P13 · 7 · Where the boundary sits (the one-line version)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-80c37615
created: '2026-06-24T05:12:10.432242+00:00'
updated: '2026-06-24T05:12:10.432242+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.432242+00:00'
  note: filed
---

## 7 · Where the boundary sits (the one-line version)

**Obsidian owns presentation and intake; our fabric owns identity, edges, resolution, and the minting of
truth.** Concretely: Obsidian may *render* and may *propose* (an edit/annotation event), but only
`cc_board` + `resolve_address` may *mint* a canonical record or an edge. The vault is downstream of the
board on the read path, and upstream-only-as-a-proposal on the write path. The moment a file move, a
rename, or a wikilink is read back as canonical, the boundary has been crossed and Obsidian has become
master.

---
