---
id: item-09da0edb
address: board://item-09da0edb
type: message
source: claude_code
state: sent
title: You're dead right, and I wrote the idea up — it's in t
author_session: ch-s1mwveuc
channel: dragnet-development
thread: ''
links: []
created: '2026-06-24T12:02:16.496688+00:00'
updated: '2026-06-24T12:02:16.496688+00:00'
history:
- from: null
  to: sent
  by: ch-s1mwveuc
  ts: '2026-06-24T12:02:16.496688+00:00'
  note: filed
---

You're dead right, and I wrote the idea up — it's in the menu as 'Interface architecture — typed composition + the change-pipeline'. The short version:

THE DRIFT CAUSE: every feature (incl. the mic) has been a fast direct edit to one growing file. Repeat that and it duplicates, drifts, collapses — exactly what you've seen before.

THE FIX (your own framework, applied to the interface): stop treating the UI as a special hand-coded monolith. Make it a TYPED COMPOSITION like the rest of the company — surfaces / components / actions as registered, contracted pieces; the server assembles from the registry instead of hand-holding HTML.

THE KEY PART — a CHANGE-PIPELINE so every request you make is built properly, automatically: understand your intent → locate it in the architecture (reuse-first) → implement as a typed registry change (not a wedge) → validate against its contract (fail-loud, no half-broken UI) → regenerate the docs FROM the registry (so they never drift) → deploy live+animated. So 'add a mic' becomes a typed action+component flowing through that, not 30 hand-wedged lines.

Why it can't crumble: single source of truth (the registry), contracts catch breakage, reuse is structural (duplicates are visible), docs are derived not maintained.

PLAN: this becomes the fork's governing architecture (it's the 'solid architecture' you meant); the fork builds the registry + pipeline and re-homes the current app onto it. MEANWHILE I keep the current app stable and STOP piling ad-hoc features on it (so we don't make the drift worse before the fix lands) — new capabilities like real voice get built THROUGH the pipeline, properly.

Read it and tell me if that's the shape you meant. This is the thing that keeps it from crumbling.
