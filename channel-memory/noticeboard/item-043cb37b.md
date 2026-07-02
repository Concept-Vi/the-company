---
id: item-043cb37b
address: board://item-043cb37b
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: 'P7 · 6. The document tree: don''t hand-roll the AST — and watch the "what''s
  un'
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-64466290
created: '2026-06-24T01:32:19.291729+00:00'
updated: '2026-06-24T01:32:19.291729+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:19.291729+00:00'
  note: filed
---

## 6. The document tree: don't hand-roll the AST — and watch the "what's under this heading" trap

BD-C's "addressable typed tree" is correct and required (flat blocks can't answer "everything under this heading"). Named guidance:

- **Heading-scoping is a known sharp edge.** "Everything under this heading" = all nodes until the **next same-or-higher-level heading.** Markdown/HTML don't nest headings as containers — they're *flat siblings* with implied hierarchy. Notion solved this by making everything an explicit block with a parent pointer (real tree). Markdown does **not** give you that for free. So the parser must **synthesize** the containment (an `H2` owns everything until the next `H1`/`H2`). This is exactly where naive implementations break: a stray `H3` or a horizontal rule silently changes the subtree. Build it from a real parser (e.g. a CommonMark AST → remark/mdast, or for HTML a DOM walk) and **store the computed subtree boundaries**, don't recompute heuristically per tap.
- **Stable node addresses across re-parse.** If the address is a positional path (`/section[2]/para[3]`), inserting a paragraph above shifts every address below it — and every stored envelope rots. Notion gives each block a **stable UUID** that survives reordering; this is why Notion comments don't orphan when you move blocks. **Mint a stable id per node and key the envelope to it**, with the text-quote anchor as the recovery path when ids can't be matched (e.g. the file was edited outside the system). Positional path = brittle; stable-id + quote-fallback = the Notion+Hypothesis combination that actually survives.
- **"Zones" (gaps between blocks) as addressable nodes** is a genuinely novel idea I haven't seen shipped — it's good for "add something *here*." Closest precedent: Google Docs' insertion-point comments and code-review **whole-file / between-lines** comments. Model a zone as an *anchor between two sibling node-ids* (an edge, not a node) so it survives re-parse the same way a block does.

---
