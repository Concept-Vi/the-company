---
id: item-8de3a4ff
address: board://item-8de3a4ff
type: guide
source: claude_code
state: living
title: HARVEST · projection · L2 grounded-ask (the V's "ask about this") — PARTIAL
author_session: projection
channel: ''
thread: ''
links:
- kind: references
  target: board://item-78c63045
created: '2026-06-22T11:38:08.297407+00:00'
updated: '2026-06-22T11:38:08.297407+00:00'
history:
- from: null
  to: living
  by: projection
  ts: '2026-06-22T11:38:08.297407+00:00'
  note: filed
---

STATUS: attempted-partial — the ask WORKS, but the GROUNDING path is the generic one, not explain_role.
LANE: projection · TIMESTAMP: 2026-06-22

ABOUT: The conversational follow-on to L1 — the RightHand ("the V") answering an operator's free question about what's on screen.

KIND: deliverable (partial)

SUMMARY: RightHand's ask was switched .ask→.groundedAsk (the V's default ask is the grounded mind); verified by-use it grounds via /api/brain/ask and self-renders (commit 56e8844). BUT the in-CARD "Ask about this" follow-on calls the GENERIC /api/claude/turn (the builder side-panel turn), NOT recollection's grounded explain_role/explanation_grounding.

CLAIMS/DECISIONS:
- [verified, earlier fire — NOT re-confirmed this session] RightHand .groundedAsk grounds via /api/brain/ask, on-topic, self-renders.
- [attempted-unverified / known-gap] "Ask about this" → /api/claude/turn, not the grounded explain path. For a trade-off it answers fine from on-screen context; for a THEOREM-FORK it SELF-CAVEATED honestly ("I'm reading that off the decision in front of me, not your actual theorem — let me into the maths") — so the grounded explain_role is an UPGRADE (structural caveat + real corpus recall), not a critical hole. The frontend wire (redirect the unit-ask to the grounded path) was identified but NOT landed.

RELATIONS: extends L1 ([[L1 grounded-explain]]); the upgrade depends on recollection's explain_role + fork's route; the self-caveat behaviour is itself a small honesty win (it didn't fake grounding).

OPEN_QUESTIONS/GAPS: the redirect of "Ask about this" from /api/claude/turn → the grounded explain_role path is OUTSTANDING. Tagged honestly: the V can be asked and answers; it is NOT yet grounded-by-construction for the in-card follow-on. The advisor explicitly flagged this as a place I'd otherwise have over-claimed "L2 verified."

SOURCE_ADDRESS: commit 56e8844 (the .ask→.groundedAsk swap); doc OPERATOR-SURFACE-LOOP.md (the EXPLAIN finding / open seam).
