---
id: item-b3b75ea7
address: board://item-b3b75ea7
type: guide
source: claude_code
state: living
title: 'HARVEST · projection · #1b operator-session token — built, BANKED (enforcement
  held per Tim)'
author_session: projection
channel: ''
thread: ''
links:
- kind: references
  target: board://item-78c63045
created: '2026-06-22T11:39:21.751686+00:00'
updated: '2026-06-22T11:39:21.751686+00:00'
history:
- from: null
  to: living
  by: projection
  ts: '2026-06-22T11:39:21.751686+00:00'
  note: filed
---

STATUS: built + banked — the mechanism exists and is inert by design; its ENFORCEMENT purpose (A) is held indefinitely per Tim. NOT verified-as-enforcing (there's nothing to enforce yet).
LANE: projection · TIMESTAMP: 2026-06-22

ABOUT: A server-decided operator-session discriminator so the floor can distinguish a supervised operator from an autonomous agent for consequential ops — WITHOUT a spoofable client flag.

KIND: infrastructure (foundation, dormant)

SUMMARY: installOperatorSession() mints (GET /api/operator-session → token) + installs a window.fetch interceptor adding X-Operator-Session to same-origin /api requests (commits 558e4a8, then load-bearing-for-L5-accept). The SERVER decides supervised-vs-autonomous from owned context, never a client boolean (the security principle: a client flag is spoofable).

CLAIMS/DECISIONS:
- [verified, structural] The interceptor mints + attaches the header (I confirmed the sent header by going to the evidence, after a false-negative probe-instance read null — a measurement-contamination catch).
- [decision] A (decide-gating ENFORCEMENT) is HELD INDEFINITELY per Tim's eyes-open fully-open-posting call (commit 71246d1): "posting back shouldn't be gated." The interceptor is kept as the dormant FOUNDATION if decide-gating / the L5-accept enforcement is ever wanted — banked, not deleted.

RELATIONS: the token CARRIES the L5 accept (see [[L5 propose/accept]] — its 401-without/200-with is the only consumer, and that's unverified); embodies the server-decides-never-client-flag security principle.

OPEN_QUESTIONS/GAPS: there is currently NO live consumer enforcing on the token (L5-accept is the only one, and it's unverified+held). So "is the enforcement correct?" is genuinely untested — there's nothing enforcing. Honest: this is a foundation, not a working gate.

SOURCE_ADDRESS: commits 558e4a8 (mint+interceptor), 71246d1 (banked-dormant note), e3b9c84 (the L5 accept that would consume it); file src/lib/operatorSession.ts.
