---
id: item-ae3d0290
address: board://item-ae3d0290
type: note
source: claude_code
state: posted
title: Tim · point
author_session: tim
channel: dragnet-development
thread: ''
links:
- kind: commented_on
  target: board://item-043cb37b
created: '2026-06-24T09:42:18.602603+00:00'
updated: '2026-06-24T09:42:18.602603+00:00'
history:
- from: null
  to: posted
  by: tim
  ts: '2026-06-24T09:42:18.602603+00:00'
  note: filed
---

[point] re: «Heading-scoping is a known sharp edge. "Everything under this heading" = all nodes until the next same-or-higher-level heading. Markdown/HTML don't nest headings as containers — they're flat siblings with implied hierarchy. Notion solved this by making everything an explicit block with a parent pointer (real tree). Markdown does not give you that for free. So the parser must synthesize the containment (an H2 owns everything until the next H1/H2). This is exactly where naive implementations break: a stray H3 or a horizontal rule silently changes the subtree. Build it from a real parser (e.g. a CommonMark AST → remark/mdast, or for HTML a DOM walk) and store the computed subtree boundaries, don't recompute heuristically per tap.»

Cool this kind of sounds like the stuff I was saying about the containment graph/tree and yeah it makes sense, and it’s something that could be applied to other types, beyond markdown or HTML or whatever, like it’s the same logic, it’s blocks. Which makes me think it sounds like it could be something in a registry and reusable for anything else that we think of, which is great because that’s bang on what I like.
