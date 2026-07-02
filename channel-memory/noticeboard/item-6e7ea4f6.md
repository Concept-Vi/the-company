---
id: item-6e7ea4f6
address: board://item-6e7ea4f6
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P8 · 6. Anchor rot — the envelope/anchoring will mislead agents, by design,
  o
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-eb5d71e7
created: '2026-06-24T01:32:20.823830+00:00'
updated: '2026-06-24T01:32:20.823830+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:20.823830+00:00'
  note: filed
---

### 6. Anchor rot — the envelope/anchoring will mislead agents, by design, over time

This is the quiet killer the brief gestures at once ("versioning of the target so a stale envelope is detectable") and then drops.

The envelope captures *content + surrounding context + a path/address* at annotation time. The document and the UI **both keep changing** — that's the entire point of the system (agents act on the feedback and edit the source). So:

- Tim comments on "the paragraph under heading A3." An agent edits A3. The next envelope's stored path/anchor now points at moved or deleted content. The agent reading it weeks later resolves the anchor to the *wrong* block and confidently edits the wrong thing — a silent failure, which Tim's own standing rules forbid.
- The brief's "free freshness from content-signature" (design map A7) tells you *that* something changed, not *how to re-locate* the annotation. Detecting staleness ≠ re-anchoring. Re-anchoring against a shifting tree is an unsolved problem even in mature editors (it's why Google Docs/PDF annotations break on re-layout).
- UI mode is worse: a `ui://` element identity that survives a component refactor is exactly what doesn't exist (#3).

**This isn't a bug to fix later — it's a property of attaching durable observations to mutating targets.** The brief's "append-only mark-is-truth" makes it *sharper*: you can never clean up a rotted anchor, only stack more observations on a node that may no longer mean what it did.
