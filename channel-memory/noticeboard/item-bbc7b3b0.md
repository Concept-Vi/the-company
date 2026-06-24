---
id: item-bbc7b3b0
address: board://item-bbc7b3b0
type: block
source: claude_code
state: current
title: P5 · 1.3 Frontmatter-mangle meets fail-loud → cascading unreadability (SEVERE
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-48cd6801
created: '2026-06-24T05:12:10.982321+00:00'
updated: '2026-06-24T05:12:10.982321+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T05:12:10.982321+00:00'
  note: filed
---

### 1.3 Frontmatter-mangle meets fail-loud → cascading unreadability (SEVERE, compounding)
`get_item` raises `BoardError` if `id` is missing/unparseable. That fail-loud is *correct* for our
discipline, but it makes us **brittle against a sloppy co-writer**. One plugin that breaks YAML
parsing on a file (e.g. a smart-quote, a tab, an unescaped colon in a value Obsidian injected) takes
that node **out of the graph entirely** until a human fixes it. With 265 files and a phone-driven
mobile-sync writer in the mix, this is not hypothetical — it's a when, not an if. The blast radius
of a single bad write is "this node vanishes from the master," which is exactly the credibility-eroding
half-working failure mode Tim cannot afford.

---
