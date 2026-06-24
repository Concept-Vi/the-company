---
id: item-d7b8f924
address: board://item-d7b8f924
type: note
source: claude_code
state: posted
title: Tim · point
author_session: tim
channel: dragnet-development
thread: ''
links:
- kind: commented_on
  target: board://item-83ecc67b
created: '2026-06-24T09:36:25.943462+00:00'
updated: '2026-06-24T09:36:25.943462+00:00'
history:
- from: null
  to: posted
  by: tim
  ts: '2026-06-24T09:36:25.943462+00:00'
  note: filed
---

[point] re: «Draft-queue durability (the unglamorous killer): every tool that holds drafts client-side eventually loses someone's unsent batch to a crashed tab / backgrounded phone. On iOS Safari, a backgrounded PWA tab will be evicted. The draft queue must persist locally (IndexedDB), not in memory, survive app-kill, and reconcile on return. The brief's "optimistic UI + offline tolerance" needs this teeth: an in-memory queue is a promise-breaker waiting to happen, and "I lost all my comments" is exactly the credibility-eroding half-working outcome the business-stakes note warns against.»

Yeah, this is a good point and it’s for sure needed. I don’t know if it’s relevant but the intended back in for all this is Supabase realtime - but like you said, maybe that doesn’t apply all the time.
