---
id: item-96a3e3da
address: board://item-96a3e3da
type: guide
source: claude_code
state: living
title: HARVEST · projection · L1 grounded-explain wire (the decision-card "what this
  is")
author_session: projection
channel: ''
thread: ''
links:
- kind: references
  target: board://item-78c63045
created: '2026-06-22T11:37:37.647337+00:00'
updated: '2026-06-22T11:37:37.647337+00:00'
history:
- from: null
  to: living
  by: projection
  ts: '2026-06-22T11:37:37.647337+00:00'
  note: filed
---

STATUS: verified (re-seen streaming by-use this session, 2026-06-22, warm-isolation test)
LANE: projection · TIMESTAMP: 2026-06-22

ABOUT: The L1 wire that makes a decision card explain itself in GROUNDED terms (traced to Tim's real framework), not a fluent stub.

KIND: deliverable

SUMMARY: POST /api/decision/explain {id} → {what_this_is, why_it_matters, grounding_note}; the host (groundedExplain.ts makeGroundedResolve) injects it through DNA's renderGallery resolve-override seam into the card's .dc-explain region (archetype.js:238-266, which awaits the Promise and swaps the placeholder). This session: flipped GROUNDED_EXPLAIN_ENABLED on + the structured-payload refactor, found stranded uncommitted, durable-ized (6016ecc).

ENTITIES: src/lib/groundedExplain.ts (fetchGroundedExplain, ExplainPayload, makeGroundedResolve); src/gallery/GalleryMount.tsx (resolve override); public/gallery/archetype.js mkExplainRegion + wire(); /api/decision/explain; cube-3d (theorem-fork).

CLAIMS/DECISIONS:
- [verified] cube-3d (theorem-fork) streams the grounded explanation: warm route 2.2s → the region swapped placeholder→content by-SIGHT: the "What this is" paragraph (Tim's multi-axis projection theorem), the "Why this matters —" line, the grounding note honestly flagging AI-inference. The n-panel branch's wire(nview) (archetype.js:377) drives the swap.
- [verified, dead-end recovered] The swap was twice mis-read as "stuck on placeholder" — both measurement contamination (competing fetches; a mid-test bounce). See [[the honest-state discipline]].
- [decision, from an earlier fire] The earlier ROOT cause that the grounded explain never SHOWED: decision-render.js (DNA.decisionSlide) was missing from the gallery sync manifest → renderExplained (carrying the region) never ran (commit 8b5a169 fixed it). Earlier still, "on-topic ≠ grounded" — fluent text was mistaken for grounding; fork's asset-scan (cube=0) was the discriminator (a theorem rebake fixed it at source). [attempted-unverified — relayed from the record, not re-confirmed this session.]

RELATIONS: depends on fork's /api/decision/explain + recollection's grounding + DNA's region; L2 (the "Ask about this" follow-on) is the conversational extension and has its OWN gap (see the L2 record).

OPEN_QUESTIONS/GAPS: only cube-3d (theorem-fork) was re-verified streaming this session. The OTHER subtypes (binary authorize, n-panel trade-off) were NOT re-confirmed grounded this session — attempted-unverified. Grounding QUALITY (is the explanation actually faithful to Tim's maths, not plausible-sounding?) is fork/recollection's correctness call, not mine.

SOURCE_ADDRESS: commits 6016ecc (flip+verified), 8b5a169 (sync-manifest root fix), ae593d6 (the earlier held-off-until-render note); doc build-prep/universal-projection/GROUNDED-EXPLAIN-MECHANISM.md.
