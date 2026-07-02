---
id: item-c7984eee
address: board://item-c7984eee
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P8 · 2.2 Flat id-keyed files vs Obsidian's folder/title UX (HIGH for usabilit
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-48cd6801
created: '2026-06-24T05:12:11.064931+00:00'
updated: '2026-06-24T05:12:11.064931+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:11.064931+00:00'
  note: filed
---

### 2.2 Flat id-keyed files vs Obsidian's folder/title UX (HIGH for usability, the whole point)
Tim's entire ask is a **human-readable phone experience**. Obsidian's UX is built on **filenames =
titles** and **folders = structure**. Our reality:
- Every file is `item-7f3a9c21.md`. In Obsidian's file explorer, the sidebar is **265 identical-looking
  `item-<hex>` rows** with no human meaning. The human `title` lives *inside* frontmatter, which the
  file list does **not** show by default. So the marquee Obsidian benefit — "browse your notes by
  name" — is **dead on arrival** without configuration.
- You can paper over it: Front Matter Title plugin (shows `title` instead of filename), or Dataview/Bases
  views. But now the readable experience **depends on plugins** (see §3) and on **Bases/Dataview
  queries that re-implement what our own board API already does** — you've added a parallel query
  layer that can drift from the master's truth.
- **Document structure is logical, not folders:** a "document" is an `order: [block-addr,...]` list
  resolved by our code. Obsidian has **no concept of this**. It will show the blocks as 30 scattered
  `item-xxxx` files with no inherent order and no assembled-document view. Reconstructing the document
  reading experience requires *our* `assemble_document`, not Obsidian — so for the actual deliverable
  (the ordered, commentable document on the phone) **Obsidian adds nothing and our own surface still
  does all the work.**
