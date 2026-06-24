---
id: item-43616aaf
address: board://item-43616aaf
type: block
source: claude_code
state: current
title: P6 · 4 · `order` / `part_of` logical documents — the cleanest native mapping
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-4baaab55
created: '2026-06-24T05:12:09.386541+00:00'
updated: '2026-06-24T05:12:09.386541+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:09.386541+00:00'
  note: filed
---

## 4 · `order` / `part_of` logical documents — the cleanest native mapping

This is the strongest "it just fits" win, so it gets its own section.

**[Observed]** A `document` item (e.g. `item-11da929d`, the client brief) carries `order: [board://item-…, …]` (18 blocks), and each block links `part_of → board://item-11da929d`. `assemble_document` (cc_board.py:497) reads the doc as ordered blocks. Storage is FLAT; the document is *logical*.

**Native Obsidian expression — transclusion:**
- A document note's body becomes the `order` list rendered as embeds:
  ```
  ![[item-a2c9902b]]
  ![[item-2ee208de]]
  ![[item-7abb3974]]
  …
  ```
  Obsidian renders this as the assembled document inline, **in sequence** — exactly what `assemble_document` produces, but in Obsidian's reading view, on the phone, for free. **[Inferred]**
- `part_of` becomes a backlink: every block note shows "linked from [the document]" automatically once block bodies carry `part_of:: [[doc]]`. **[Inferred]**

**The catch:** the document item's body today is a one-line summary, not the embed list. So this is an L2 generator output: read `order`, write the `![[…]]` sequence into **either** the doc's body (survives runtime writes unless the doc body is edited) **or** a sidecar `_assembled/item-DOC.md` (zero mutation). The sidecar is the cleaner "host not master" choice — the assembled view is a *projection*, which is conceptually what `assemble_document` already is.

**Result:** Obsidian's reading surface gives Tim the same ordered-blocks-with-threads view the custom phone surface gives him — a genuine second lens on the identical logical document, no data duplication.

---
