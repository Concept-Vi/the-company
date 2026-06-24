---
id: item-7f8e00cf
address: board://item-7f8e00cf
type: block
source: claude_code
state: current
title: P6 · ❌ The long-press multi-scale gesture (BD-B) — the biggest trap
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-f9f4a6a6
created: '2026-06-24T01:32:21.794562+00:00'
updated: '2026-06-24T01:32:21.794562+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:21.794562+00:00'
  note: filed
---

### ❌ The long-press multi-scale gesture (BD-B) — the biggest trap
The brief lavishes paragraphs on: long-hold to activate, thumb-up = coarser, thumb-down = finer, haptic ticks per level, live outline preview, zone selection, left/right reserved slots. **This is the single most over-engineered idea in the brief and Tim himself walked it back in MSG2:** *"I actually kind of like a lot of the current selection."* He already softened "long-press is the primary mechanism" to "long-press is for when I want to go *more granular than the current selection*." The current tap-a-block selection is good enough. Building a custom thumb-drag-scale gesture engine on mobile Safari — fighting native scroll and text selection, tuning haptics, previewing subtrees — is **weeks of finicky, device-only-verifiable work to replace a tap that already works.** Defer entirely. If granularity friction appears in real use, add a simple "expand selection up / shrink down" pair of buttons — no gesture engine.
