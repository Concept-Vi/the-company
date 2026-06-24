---
id: item-c8d428f5
address: board://item-c8d428f5
type: block
source: claude_code
state: current
title: P3 · 2. Margin vs. inline — there are two physical registers and they mean
  di
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-a72b23c2
created: '2026-06-24T01:32:22.421203+00:00'
updated: '2026-06-24T01:32:22.421203+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:22.421203+00:00'
  note: filed
---

## 2. Margin vs. inline — there are two physical registers and they mean different things

Every markup surface I've used has two distinct zones, and the distinction is **semantic**, not cosmetic:

- **Inline marks** sit *in the text flow* — they propose a change *to the words themselves* (insert, delete, replace). They are surgical, located at a character/word boundary.
- **Margin marks** sit *beside* the text — they're commentary *about* a span. Queries, notes, "this whole section feels off."

Tim's word "highlight = word" is an inline mark. His "comment on the whole section under this heading" is a margin mark on a subtree. **These are not the same gesture and shouldn't produce the same envelope shape.** An inline mark needs an *anchor point* (between word 3 and 4) plus the proposed replacement text; a margin mark needs a *span* (the subtree) plus prose.

The block-hierarchy gesture (BD-B) is built entirely for the *margin* case — select a span at some scale, comment on it. There's no inline-edit primitive at all. But Tim *will* want to say "change this word to that word" — that's the most common edit a reviewer makes. On a phone, an inline edit is: highlight the word (he already likes the native selection — see MSG2), then "replace with → [type]". The envelope carries the *old text + new text* as a proposed diff (BD-D ADDITIONS mentions "diff preview" — this is where it's born). The member doesn't interpret prose, it applies a substitution. **Maximum effort-reduction**, which is his stated goal.

**The convention worth stealing:** render margin marks **in the margin** (a thin gutter, marks as small typed icons aligned to their anchor line), and inline marks **in the text** (struck-through old text, the proposed new text in a distinct color). On a phone the margin is a narrow left-edge rail of icon dots; tapping one opens the thread. This is the single most legible way to show "where are all my marks" on a small screen without a separate list — the document *is* the index of marks.

---
