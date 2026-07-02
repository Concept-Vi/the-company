---
id: item-ea9b2a06
address: board://item-ea9b2a06
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P4 · 2. The long-press gesture model fights iOS, and Tim already half-retract
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-eb5d71e7
created: '2026-06-24T01:32:20.597644+00:00'
updated: '2026-06-24T01:32:20.597644+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:20.597644+00:00'
  note: filed
---

### 2. The long-press gesture model fights iOS, and Tim already half-retracted it

Read MSG2 carefully. After actually touching the artefact, Tim says he *likes the current tap selection* and now wants the long-press only for "more granular than current" / a secondary menu. **The elaborate hold-and-slide-thumb-to-change-scale mechanism — the most-designed thing in the whole brief (BD-B) — is the part the client softened on first contact with the real screen.** Build it as specified and you've poured the most effort into the least-wanted interaction.

And it fights the platform concretely:

- **iOS Safari long-press is overloaded.** Long-press on text = the native selection/callout (copy/look-up/share). Long-press on a link/image = the context menu / save-image sheet. You're competing with system gestures that fire on the same timing. You can fight them with `-webkit-touch-callout:none`, `user-select:none`, and `preventDefault`, but then you've **disabled the native text selection Tim explicitly said he likes** ("highlighting is obvious"). You can't have native highlight-to-select-a-word AND a custom long-press on the same elements without them colliding. That's a genuine contradiction in the spec, not a tuning problem.
- **Hold-then-slide-vertically to change level directly conflicts with scroll.** A finger held and moved up/down is *the scroll gesture*. Disambiguating "this drag changes selection level" from "this drag scrolls the page" by timing alone is fragile and will misfire constantly one-handed, especially when the user's thumb is also the thing occluding the live level-indicator the brief wants to show under it.
- **PWA caveat:** in a home-screen PWA (which Tim wants — MSG2 section B), there's no URL bar to fall back on and gesture quirks differ from in-tab Safari. The "verify on device" loop (BD-I) isn't a polish pass; it's where you discover the gesture is unusable and have to redesign. Budget for the redesign, not the verification.

**Verdict:** the gesture is over-engineered *and* fragile *and* partially unwanted. The honest move is to ship the existing tap selection + an explicit small "scale" control (the buttons the brief lists as a mere "fallback" in BD-B should be the *primary*), and treat hold-slide as an experiment, not a requirement.
