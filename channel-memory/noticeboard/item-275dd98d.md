---
id: item-275dd98d
address: board://item-275dd98d
type: block
source: claude_code
state: current
title: P2 · 1. The mark has a VERB before it has content — and you're missing the
  ta
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-a72b23c2
created: '2026-06-24T01:32:22.374831+00:00'
updated: '2026-06-24T01:32:22.374831+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:22.374831+00:00'
  note: filed
---

## 1. The mark has a VERB before it has content — and you're missing the taxonomy

When an editor touches a manuscript, the *first* decision isn't "what do I type," it's **what kind of mark is this**. We have a fixed, tiny, learned vocabulary:

- **Change** ("set this in roman," "delete," "stet") — an instruction, expects action, no reply wanted.
- **Query** (the editor's "Au:" or the proofreader's marginal "?") — a *question to the author*, expects an answer, blocks resolution until answered.
- **Comment / note** — context, not an instruction, no action expected.
- **Approve / stet** ("leave as is," a tick) — explicit *positive* mark. Toy tools have no way to say "this is good, don't touch it."
- **Strike / reject** — kill this.

The brief gestures at this once — "sometimes I want a specific thing updated, other times it's on something else" (BD-D, INTENT). That instinct **is** the verb taxonomy. But it's buried as one optional `intent` tag. It should be the **first thing the long-press resolves to**, not a dropdown after. In redlining, the mark-type *is* the gesture: a caret means insert, a loop means delete, a wavy underline means "wrong font." Tim never says "delete" in words — he draws the symbol.

**Steal this:** the long-press, once it commits a block, should open the radial onto **verbs first** (Change / Ask / Note / Approve / Strike), each a distinct icon (he hates emojis — DNA's brown-circle iconography is perfect here). The *typed text* is secondary and often unnecessary. Half my marks are a single symbol with no words. A "strike" or an "approve" should be **one tap with zero typing** — that's what makes a tool feel professional instead of chatty.

This also fixes a real routing problem hiding in BD-E: the supervisor can't triage envelopes well if every envelope is just "a comment." A **Query** routes to whoever can answer; a **Change** routes to whoever can edit; an **Approve** routes nowhere — it just resolves a thread and closes the loop. The verb *is* the routing key.

---
