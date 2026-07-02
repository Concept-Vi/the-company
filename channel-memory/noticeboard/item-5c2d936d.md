---
id: item-5c2d936d
address: board://item-5c2d936d
type: block
source: claude_code
state: current
scope: channel://dragnet-development
author: session://ch-3mpkjg3r
title: P7 · 6. Specific feel-level things that will make-or-break it (his "I can't
  k
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-a5b7cf79
created: '2026-06-24T01:32:18.770875+00:00'
updated: '2026-06-24T01:32:18.770875+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:18.770875+00:00'
  note: filed
---

## 6. Specific feel-level things that will make-or-break it (his "I can't know to ask for these")

These are the small interaction details that separate "feels like a native app" from "feels like a web page," and they're exactly the things a non-designer can't specify:

- **Arming feedback must be instant and physical.** The moment the long-press threshold is crossed, *something must change* — the armed block lifts/outlines, a tick fires, the rest of the page dims slightly. Without an unmistakable "you are now armed" signal, he won't know whether he's selecting or about to scroll. The iOS spacebar-trackpad does this by blanking the keys; you need the equivalent "everything else recedes" moment.
- **The release must be forgiving.** If he lifts his thumb having drifted a few pixels, it should still commit the last-shown level — *never* require a precise lift-in-place. Commit = "whatever the chip currently says."
- **An escape/cancel.** Every armed gesture needs an abort: slide the thumb *off* the content area (or onto a "cancel" zone) → release cancels with no commit. Without it, the only way out of a mis-arm is to commit something wrong and delete it. (His left/right "empty slots" are a natural home: **left = cancel, right = open command bar / multi-select**, rather than leaving both empty.)
- **"Space/zone" selection (his between-bullets, after-paragraph idea) is subtle and I'd partly push back.** Selecting *empty space* as a node is conceptually clean (it maps to the document tree) but *ergonomically risky* — the gaps are tiny tap targets and easy to miss-hit. I'd implement it but make zones **only reachable by drilling DOWN from an adjacent block** (his own "lowest granularity at that spot" instinct), not as a primary tap target. Don't make him aim for a 4px gap with a thumb.
- **Optimistic, local-first everything.** Phone networks drop. Every draft must be held locally and *look* committed instantly (his batch-submit model already implies this); submit-all then syncs and reconciles. A spinner on every comment-tap would destroy the feel. (BD-F/BD-I already imply this — I'm underlining it as a *feel* requirement, not just a data one.)
- **PWA full-screen is non-negotiable for the gesture to even work.** In a normal Safari tab, the bottom toolbar and the pull-to-refresh / swipe-back edge gestures will *eat* his thumb gestures near the edges. Installed-to-home-screen standalone PWA (his MSG2 ask) removes the bottom bar AND disables Safari's edge-swipe-back — which is *required*, not cosmetic, because his V and gesture live exactly where Safari's edge gestures are. The `theme-color` + `display: standalone` + `apple-mobile-web-app-*` meta tags he half-described are the mechanism. **Edge-swipe-back conflict is a real, device-only verification item.**

---
