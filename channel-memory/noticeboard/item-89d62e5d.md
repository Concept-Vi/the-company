---
id: item-89d62e5d
address: board://item-89d62e5d
type: block
source: claude_code
state: current
title: 'P6 · 5. Granularity & the long-press: the gesture has two specific phone-kill'
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-64466290
created: '2026-06-24T01:32:19.251359+00:00'
updated: '2026-06-24T01:32:19.251359+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:19.251359+00:00'
  note: filed
---

## 5. Granularity & the long-press: the gesture has two specific phone-killers

The thumb-drag-to-change-level idea is genuinely good and rare (most tools *only* do drag-to-extend). Two named pitfalls from the mobile-annotation world:

- **The selection-vs-scroll war.** On mobile Safari, long-press natively triggers the OS text-selection callout *and* the page wants to scroll under the thumb. Hypothesis, Medium, and every in-browser annotator fight this. The proven move: the long-press handler must call `preventDefault` on `touchstart`/`selectstart` **only inside the annotatable surface**, and you must set `-webkit-user-select` deliberately (off during gesture, restored after) and `-webkit-touch-callout: none` to suppress the iOS magnifier/share sheet. Get this wrong and *either* the native callout hijacks the gesture *or* the page won't scroll. This is a real-device-only verification loop — never green from a desktop browser. (Consistent with BD-I's "verify on his actual device.")
- **Vertical drag = scale-change collides with vertical scroll.** Tim's "move thumb up = coarser, down = finer" reuses the **vertical axis that the page also uses to scroll.** Once the long-press *latches* selection mode this is fine, but the latch must be unambiguous and **haptic-confirmed** (iOS supports haptics via the Vibration API on PWAs in recent Safari — verify on device). Without a crisp latch + a per-level haptic tick + a live outline preview of *exactly what will commit on release*, Tim will mis-commit constantly. Borrow Apple's own pattern: a long-press that "lifts" the element (haptic + slight scale/shadow) so the mode change is *felt*, then the directional drag. The breakdown's "preview outline + haptic ticks" is the right instinct; I'm flagging it as **non-negotiable**, because a level-selector with no preview is a guess-and-undo machine.
- **MSG2 changes the gesture's job.** Tim said he *likes* the existing tap-to-select and now wants long-press reserved for *more-granular / secondary actions* (a right-click-style command bar incl. multi-select). That's the better design and it matches desktop convention: **normal tap = select at the document's natural block level; long-press = the power menu (drill finer, multi-select, change level, attach).** This also sidesteps the scroll war for the common case (a plain tap doesn't fight scroll). Lead with tap; long-press is the expert affordance.

---
