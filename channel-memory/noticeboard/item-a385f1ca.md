---
id: item-a385f1ca
address: board://item-a385f1ca
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P11 · 3.1 Plugin lock-in & Obsidian-specific syntax leaking into canonical
  dat
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-48cd6801
created: '2026-06-24T05:12:11.146595+00:00'
updated: '2026-06-24T05:12:11.146595+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:11.146595+00:00'
  note: filed
---

### 3.1 Plugin lock-in & Obsidian-specific syntax leaking into canonical data (MEDIUM)
The value pitch is "adopt Obsidian's mature features." But the features that matter here
(readable titles, typed-ish views, Bases) **only exist via Obsidian syntax/plugins**:
- Bases `.base` files, Dataview `dataview` code blocks, callouts `> [!note]`, `%%comments%%`,
  block-reference `^block-id` anchors, embeds `![[...]]`. If any of these leak into the **body** of
  our items (because a human edits in Obsidian and uses the affordances Obsidian offers), our body
  is no longer clean portable markdown — it's **Obsidian-dialect markdown** that our phone surface
  and any other reader must now parse or strip. The canonical data quietly becomes Obsidian-shaped.
- This is the slow version of inversion: not "Obsidian becomes master" by decree, but **the data
  accretes Obsidian-only constructs** until you can't render it correctly *without* Obsidian. The
  "second lens" becomes load-bearing.
