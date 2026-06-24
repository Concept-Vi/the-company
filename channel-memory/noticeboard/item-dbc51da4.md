---
id: item-dbc51da4
address: board://item-dbc51da4
type: block
source: claude_code
state: current
title: P6 · 3. Dataview — CLEAN on frontmatter, but plugin + desktop-leaning. Demote
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-3480c157
created: '2026-06-24T05:12:09.784283+00:00'
updated: '2026-06-24T05:12:09.784283+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:09.784283+00:00'
  note: filed
---

### 3. Dataview — CLEAN on frontmatter, but plugin + desktop-leaning. Demote vs Bases.
Dataview queries the same flat frontmatter and is more mature (DQL/JS). But it's a **community plugin** (install/maintain), renders best on desktop, and needs a query language. For Tim specifically, **Bases does the same job natively, on mobile, without code** — so Dataview is the *desktop power-user* option, not the recommendation. Same edge-blindness as Bases (it can parse a frontmatter string but won't treat `board://…` as a navigable link).
