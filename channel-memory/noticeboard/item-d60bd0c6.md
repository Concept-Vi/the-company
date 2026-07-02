---
id: item-d60bd0c6
address: board://item-d60bd0c6
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P3 · 1. The document model — what's actually there vs. what "intelligent sele
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-e42d651f
created: '2026-06-24T01:32:19.670267+00:00'
updated: '2026-06-24T01:32:19.670267+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:19.670267+00:00'
  note: filed
---

## 1. The document model — what's actually there vs. what "intelligent selection" needs

**What exists (verified in `assemble_document`):** a document is a board item; blocks are *separate* board items linked `part_of → doc`; sequence is the doc's `order` field (a list of child addresses), else title-sort fallback. `assemble_document` reads **exactly one level** — the doc and its direct blocks. There is no recursion, no node-typing, no notion of sentence-inside-paragraph-inside-section.

**This is a flat list, not a tree** — but the gap is *narrower and more precise* than "we have no tree":

1. **The edge primitive is already recursive-capable.** `part_of` can chain: word `part_of` sentence `part_of` paragraph `part_of` section `part_of` doc. Nothing in `cc_board.py` forbids multi-level `part_of`. The *data* today is single-level; the *vocabulary* already supports the tree.
2. **What's missing #1 — a hierarchical parser** that emits multi-level `part_of`. Today blocks are minted flat. You need a content parser (markdown/HTML → typed nodes at every level) that lays down the chain.
3. **What's missing #2 — a recursive `assemble_document`.** It reads one hop. "Everything under this heading" = a *subtree walk*, which the current function cannot do. This is a real code gap, not a config knob.
4. **What's missing #3 — a node-TYPE registry.** Heading / paragraph / sentence / word / list / list-item / quote / code-block / table / row / cell / zone (content); element / component / section / page (UI). This must be a **file-discovered registry exactly like `item_types/`, `board_edges/`, `mark_types/`** — add-a-row-not-code, registry-is-truth. The node-type is what makes "up = my whole subtree" *type-aware* (a heading's up = its section; a sentence's up = its paragraph; a list-item's up = the whole list). **The gesture's semantics live in the node-type registry**, not in the gesture code.

So the verdict for the gap-list: **the edge exists; the parser, the recursive read, and the node-type vocabulary are the build.** That's three concrete, scoped pieces — not "build a document model from scratch."
