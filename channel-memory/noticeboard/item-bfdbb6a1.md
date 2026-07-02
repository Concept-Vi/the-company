---
id: item-bfdbb6a1
address: board://item-bfdbb6a1
type: block
source: claude_code
state: current
scope: channel://operator-surface
author: agent://lead
title: S8 · Comments — threading-back, inline replies, typed flags, states
author_session: lead
channel: operator-surface
thread: ''
links:
- kind: part_of
  target: board://item-ed91000e
created: '2026-06-28T11:35:00.253187+00:00'
updated: '2026-06-28T13:05:39.826199+00:00'
history:
- from: null
  to: current
  by: lead
  ts: '2026-06-28T11:35:00.253187+00:00'
  note: filed
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T12:56:17.713220+00:00'
  note: v2 MERGE rewrite (in place)
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:03:19.387041+00:00'
  note: restore v1 content dropped in v2 rewrite
- from: edit
  to: body
  by: lead
  ts: '2026-06-28T13:05:39.826199+00:00'
  note: fold corroboration corrections (3 unbiased agents)
---

S8 · Comments — RIDE annotate (eventing) + threading + typed flags + states
DECISION (Tim): threading-back + replies-in-place + states; typed into registries.
v2: RIDE /api/annotate (bridge.py:3387 — records the annotation AND EMITS an event) + /api/annotations GET (1893). Surface today writes raw cc_board comments with ZERO eventing (surface_server.py:870-893) → repoint to /api/annotate so the company sees them.
REPLY: cb.reply (reply_to edges) + nested thread already exist (cc_board); net-new = the reply composer. EDIT/DELETE = NET-NEW on the bridge (/api/annotate is create-only; the surface's delete os.remove's the file :895-911, bypassing eventing — must not).
TYPED FLAGS = mark_types/ rows (question/correction exist as comment sub-types; do-this-now a reaction value). COMMENT STATES (open->actioned->resolved->disputed) = composed-mark (suite.mark on board://<comment-id>; latest comment_state mark = state) — NOTE compose_state hardcodes decision_take (decision_registry.py:179) → needs its own tiny fold.
RESTORED(v1) — ★ THE COMMENT-AS-INSTRUCTION LOOP (the native standout): a comment flagged `do-this-now` ROUTES (via the S6 route registry) to dispatch the work, and the RESULT threads back onto the comment (reply_to) with the comment's state advancing open→actioned→resolved. The annotation becomes a tracked instruction with its outcome attached — only possible because the surface is wired into live sessions. Fail-loud: a failed dispatch surfaces a Notice on the comment, never vanishes. COMMENT-STATE option: composed-mark is recommended, but an item_type state-machine (cb.transition, legal-move enforcement) is the alternative if illegal transitions must be rejected.
CORROBORATED + nuances: /api/annotate routes through ingest_comment (bridge.py:3387) which ALSO emits a located-gold TRAINING turn — riding it does MORE than record (a known side-effect). READ side already built (S8 named only the write): /api/annotations (:1893), /api/chats (:1904), /api/address-history (:1911) — ride these for the thread display. comment-state fold: compose_state hardcodes decision_take/retract (decision_registry.py:179/192) → the comment_state fold is genuinely net-new.
