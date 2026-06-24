---
id: item-b214f58b
address: board://item-b214f58b
type: block
source: claude_code
state: current
title: BD-C · Breakdown · Intelligent block structure (the document tree / types)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-11da929d
created: '2026-06-24T00:38:11.254188+00:00'
updated: '2026-06-24T00:38:11.254188+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T00:38:11.254188+00:00'
  note: filed
---

# Breakdown · Intelligent block structure (the document tree / types)

SPECIFIED: Selection should be INTELLIGENT — individual bullet vs the whole list vs the intro paragraph vs the heading itself vs everything under that heading. He assumes a hierarchy and types.

IMPLIED: This requires a real DOCUMENT MODEL — parse the rendered content into a semantic TREE of typed nodes (heading, paragraph, sentence, word, list, list-item, quote, code-block, table, row, cell, image, zone), where headings OWN the content beneath them until the next same-or-higher heading, lists own items, paragraphs own sentences own words. EVERY node is addressable (a stable path/address). "Everything under a heading" = a subtree. This is beyond the current flat block list — it's an addressable AST. It must be robust across markdown/HTML formats. The same tree-thinking applies to UI (element < component < section < page).

ADDITIONS: Collapse/expand subtrees; breadcrumbs of where the current selection sits; "comment on this node AND its children"; rollup of all comments under a heading; the tree powers navigation (jump to a node), not just selection; node types could carry per-type default comment behaviors.
