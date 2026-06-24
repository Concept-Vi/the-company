---
id: item-45ed819d
address: board://item-45ed819d
type: block
source: claude_code
state: current
title: 'P6 · 5. Threads must RESOLVE, not just accumulate — the open/closed state
  is '
author_session: ch-3mpkjg3r
channel: dragnet-development
thread: ''
links:
- kind: part_of
  target: board://item-a72b23c2
created: '2026-06-24T01:32:22.515472+00:00'
updated: '2026-06-24T01:32:22.515472+00:00'
history:
- from: null
  to: current
  by: ch-3mpkjg3r
  ts: '2026-06-24T01:32:22.515472+00:00'
  note: filed
---

## 5. Threads must RESOLVE, not just accumulate — the open/closed state is everything

The design has threading (reply_to edges, A2/A5). Threading without **resolution state** is a chat log, not a markup. The defining feature of every real annotation tool (Word, Google Docs, PDF proofs, GitHub review) is that a comment is **open or resolved**, and resolved ones *visually recede*. The whole emotional experience of finishing a review is watching the open-count go to zero.

What the brief is missing:
- A **resolve** action, and crucially **who is allowed to resolve**. Convention: the *author* of a query can't mark their own query resolved — the *recipient* answers, the *author* accepts-and-closes. Here: a member replies/acts, but **Tim closes the loop**. A mark Tim raised stays *open* until *Tim* taps "resolved" (or "applied — looks good"). This is the missing back-half of his loop: he can submit and see replies (BD-F), but there's no described act of **accepting** an answer. Without it, nothing ever ends and the "needs your eyes" lane grows forever.
- **Reopen.** The agent says "done," Tim looks, it's not done — reopen the thread. Trivial in concept, always forgotten, infuriating when absent.
- **Resolved marks recede but don't vanish.** A grayed, collapsible margin dot. The audit trail (BD-D: "envelope doubling as audit trail") *requires* they persist; usability requires they get out of the way. Both, via dimming + filter ("show resolved").

This is the cleanest fit with the system's own grain: design-map says *state is composed from the observation-thread, never stored* (A5 "mark-is-truth"). So **"resolved" is itself just another observation appended to the thread** — an `accepted` or `resolved` mark by Tim. The open/closed badge is a *fold* of the thread, computed, not stored. That's beautiful and it's already the system's pattern — point it at annotation threads and resolution falls out for free.

---
