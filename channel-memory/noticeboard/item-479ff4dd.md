---
id: item-479ff4dd
address: board://item-479ff4dd
type: block
source: claude_code
state: current
title: P4 · The lean week-one build (the whole of it)
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-f9f4a6a6
created: '2026-06-24T01:32:21.691700+00:00'
updated: '2026-06-24T01:32:21.691700+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:21.691700+00:00'
  note: filed
---

## The lean week-one build (the whole of it)

In priority order. This is the entire scope I'd defend:

1. **Fix the chrome Tim already complained about.** His MSG2 feedback is gold — it's the only *verified* friction in the entire brief, because he actually used the thing. One-line top bar (hamburger + fitted title), icon buttons not text buttons, one-line input that grows, no on-screen echo of the highlighted selection, PWA meta so it saves to home screen with a matching theme colour, kill the always-there bottom bar, no emojis (use the DNA brown-circle icons). **This is real, tested, cheap, and he asked for it directly.** Do it first.

2. **Add a "send now" button** beside post/cancel. He said it explicitly: sometimes one comment, fire it immediately. Trivial, removes friction, done.

3. **Draft queue + submit-all + a count badge.** The keystone above. Hold comments locally, one submit action for 1 or 12, a badge showing how many are pending.

4. **A replies view.** A single list: "here's what came back." Badge when unread. Tap → jump to the comment it answers. Does not need to be a chat. Does not need a radial menu. A list and a badge.

5. **Document switcher that works.** He flagged bugs in it. Fix the existing switcher; don't redesign it. A hamburger list of documents.

That's it. Five things, all anchored in either verified friction or the one capability that closes the cycle. A week, not a quarter.

---
