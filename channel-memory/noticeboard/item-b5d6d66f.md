---
id: item-b5d6d66f
address: board://item-b5d6d66f
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P8 · 7. Where I'd push back on the converged architecture
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-60542ab3
created: '2026-06-24T01:32:21.446546+00:00'
updated: '2026-06-24T01:32:21.446546+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:21.446546+00:00'
  note: filed
---

## 7. Where I'd push back on the converged architecture

- The brief treats voice as living *inside* the envelope (an attachment, a text source). I'd argue voice deserves to be a **modality field on the envelope itself** — `input_modality: voice|touch|mixed`, `transcript_raw`, `transcript_confidence`, `audio: blob://…` — so downstream members and the audit trail know *how* it was authored and read it accordingly. Authoring modality is provenance, and this system cares about provenance.
- The "intelligent block selection" tree (BD-C) is justified in the touch brief as *what the thumb-walk needs*. I'd reframe its primary justification as **what makes spoken scale-words resolvable** ("everything under this heading" only means something if headings own subtrees). The tree earns its cost faster for voice than for touch.
- **Accessibility is not the iOS-polish lane (BD-I).** It's the spine. This operator is, functionally, a *situationally and by-preference* hands-light, type-averse user — the exact population voice-first/accessible design exists for. Designing for him *is* designing accessibly; they're the same requirement, not two.

**One-line throughline:** *Speak to produce, touch to repair, and keep both channels live at all times — because for this operator the voice is the pen and the thumb is the eraser.*
