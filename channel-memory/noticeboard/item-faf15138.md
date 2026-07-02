---
id: item-faf15138
address: board://item-faf15138
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P16 · 4. Two modes, one schema — the data-model truth
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-e42d651f
created: '2026-06-24T01:32:20.244640+00:00'
updated: '2026-06-24T01:32:20.244640+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:20.244640+00:00'
  note: filed
---

## 4. Two modes, one schema — the data-model truth

Tim's two modes are **one envelope schema with `mode` as a discriminator on two fields only**: `target` (`board://node` vs `ui://element`) and `edit_target` (board/file vs `ui://→code://`). Everything else — node-type, scale, quote-anchor, intent, attachments, frame, lifecycle, threading — is *identical*. 

This is the strongest argument for getting the schema right *once*: a future "annotate an image" (`image://`), "annotate a generated output", "annotate a decision" (`decision://`) is **the same envelope with a different target scheme.** The address grammar already has ~19 schemes through one resolver — the annotation layer becomes *target-scheme-agnostic* the moment the envelope's `target` is just "an address." That's the universal-composition payoff, expressed in the data model: **one envelope type, N target schemes, one resolver.**

The node-type tree is *also* shared: content tree (document → section → … → word/zone) and UI tree (page → section → component → element) are **two instances of one typed-tree pattern**, one node-type registry with two families. The gesture walks both identically.

---
