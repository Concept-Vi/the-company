---
id: item-f17968de
address: board://item-f17968de
type: block
source: claude_code
state: current
title: P4 · 2 · Separate the decision into THREE independent axes
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-80c37615
created: '2026-06-24T05:12:10.182403+00:00'
updated: '2026-06-24T05:12:10.182403+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.182403+00:00'
  note: filed
---

## 2 · Separate the decision into THREE independent axes

Most "one-way vs two-way sync" framing is too coarse and hides the real fork. There are three orthogonal
choices; the candidate architectures are points in their product:

| Axis | The question | Options |
|------|--------------|---------|
| **A · Write direction** | Does Obsidian (its editor / a sync plugin) ever write files our runtime reads? | read-only lens · two-way |
| **B · Reconciliation authority** | When two writers touch one item, who mints canonical truth? | runtime-reconciles · file-is-truth (last-writer-wins) |
| **C · Storage topology** | Where does the vault sit relative to `channel-memory/noticeboard/`? | vault *over* the canonical dir · *derived parallel* vault |

The honest evaluation criterion for every option is the same three questions — I score each option on
exactly these in §5:
1. **Identity law intact?** (flat-opaque `board://`, edges = our address array, no path-as-identity)
2. **Two-writer conflict behavior?** (what happens when runtime AND Obsidian/sync both write)
3. **iOS write-back possible?** (the brief explicitly wants the iOS app + sync as *a way IN*, not just a
   read lens — this is the implied constraint that kills pure read-only as *the* answer)

---
