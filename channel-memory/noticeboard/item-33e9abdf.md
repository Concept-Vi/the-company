---
id: item-33e9abdf
address: board://item-33e9abdf
type: block
source: claude_code
state: current
title: B0 · Frame — what this becomes
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-302a562e
created: '2026-06-28T10:03:08.413214+00:00'
updated: '2026-06-28T10:03:08.413214+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T10:03:08.413214+00:00'
  note: filed
---

The surface today is a review/annotation tool over board content (documents + artefacts) with two-way SSE chat to the channel lead. The leap: it becomes **the operator console for the whole engine** — the one place Tim drives everything from phone or desk: see what needs him, watch things run, decide. The through-line is **"what's gated on me"** — his attention is the scarce resource the engine is built around.

Current state, grounded: no search, no offline, no presence, no unread, no resolved-state, no voice; it re-scans all ~537 board items every request (won't scale); but the engine DOES expose surfaces a console can pull from (coherence_detect findings, recall_determine, session_recall), and there's a DNA token system (design/_system/tokens.json, design/claude-ds/tokens/theme.css) the face should plug into.
