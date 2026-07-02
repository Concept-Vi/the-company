---
id: item-17bea2b3
address: board://item-17bea2b3
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: 'P7 · 4. Graph view & backlinks / unlinked-mentions — PARTIAL, and lossy. The '
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-3480c157
created: '2026-06-24T05:12:09.811445+00:00'
updated: '2026-06-24T05:12:09.811445+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:09.811445+00:00'
  note: filed
---

### 4. Graph view & backlinks / unlinked-mentions — PARTIAL, and lossy. The high-stakes honesty call.
This is **the trap**: it's the thing Tim most wants (he re-derived "the unified walkable typed graph" from his own head — design-map A2/A6) and the thing Obsidian *least faithfully* delivers on our data.

- Out of the box, Obsidian's graph shows **nothing** between our items, because our edges are frontmatter address-strings, not `[[wikilinks]]`. Every item is an island.
- To show *anything*, we'd have to **dual-write** `[[item-xxxx]]` wikilinks alongside the real typed edges — a second, redundant link layer to maintain (a write, Axis 2 red).
- Even then the graph is a **lossy fragment**:
  - It **loses the edge `kind`** — `commented_on`, `reply_to`, `references`, `part_of` all collapse into one undifferentiated grey line. The *type* is the whole point of our graph; Obsidian's graph can't carry it.
  - It **cannot represent `image://`, `code://`, `decision://`, `session://` targets at all** — those aren't files in the vault, so half our graph (the cross-address edges that make it powerful) simply **does not exist** in Obsidian's view.

So the Obsidian graph would be a pretty, incomplete shadow of our real graph — and it could *mislead* (Tim sees a sparse graph and thinks that's the relationship structure, when the rich typed web is invisible). **The honest recommendation: do not lean on Obsidian's graph as the lens for our typed graph. Our own walkable-graph (the system's declared-unbuilt next step) is the right home; Obsidian's graph is the wrong tool for this specific job.** Unlinked-mentions (text co-occurrence) is mildly useful as serendipity but unrelated to our edges.
