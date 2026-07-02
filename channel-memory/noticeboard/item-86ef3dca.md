---
id: item-86ef3dca
address: board://item-86ef3dca
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: S2 · Your forks — yours to decide (preserved, not flattened)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-897e8fa3
created: '2026-06-24T15:26:59.817101+00:00'
updated: '2026-06-24T15:26:59.817101+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T15:26:59.817101+00:00'
  note: filed
---

# Your forks — these are yours

**A. What runs the reasoning rooms** — a persistent forked-context per critic (richer, carries across rounds, but capped at 3 at a time) vs a cheaper parallel swarm. This decides whether rooms run in parallel at all.

**B. (linked to A) Where the "implied" layer is captured + on which model** — a cheap small model does fact-extraction within budget but *loses the implied* (inverts your brief); full Claude-class fact+implied on all 121 comments is the real value but costs more. A & B are one decision at two tiers.

**C. How the auditor handles disagreement** — "no contradictions" fights "preserve tensions." Proposed fix: a two-verdict auditor — a logic ERROR goes back to the room; a genuine DISAGREEMENT is promoted to a named fork for you.

**D. How to size the run** — by comment-count (~50–60 agents) vs by the number of genuine decisions (~4–8). The latter may be far leaner.

**E. How the map is built** — pure similarity-clustering (cheap, but blind to your anchored relational links) vs clustering + one small new relational join.
