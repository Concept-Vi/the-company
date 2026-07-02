---
id: item-b69720ab
address: board://item-b69720ab
type: guide
source: claude_code
state: living
scope: global
author: agent://projection
title: HARVEST · projection · L4 channel-post composer — built, SUCCESS-LAND UNVERIFIED
author_session: projection
channel: ''
thread: ''
links:
- kind: references
  target: board://item-78c63045
created: '2026-06-22T11:38:20.309228+00:00'
updated: '2026-06-22T11:38:20.309228+00:00'
history:
- from: null
  to: living
  by: projection
  ts: '2026-06-22T11:38:20.309228+00:00'
  note: filed
---

STATUS: attempted-unverified — built + FORM-verified + fail-soft-verified, but the SUCCESS LAND (a real post rendering in a real membered channel) was NEVER confirmed.
LANE: projection · TIMESTAMP: 2026-06-22

ABOUT: The operator posting back INTO the fabric from the surface — the V-post composer in the RightHand panel.

KIND: deliverable (unverified at the success path)

SUMMARY: The composer (commit 08209b9): a toggle + a channel-NAME picker (human names, __test__ filtered — operator-law) + message → forkVBrain.postToChannel(name, msg); fork resolves the name server-side + self-renders the transparency. Fully open (no gate/token — per Tim's "posting back shouldn't be gated"). FORM verified both viewports; the wire verified END-TO-END only in the FAIL-SOFT sense (the render path on a non-landing post).

CLAIMS/DECISIONS:
- [verified] FORM both viewports; the composer dispatches and the fail-soft render path works.
- [attempted-unverified] The SUCCESS land — posting to an ACTIVE, MEMBERED bridge-store channel and SEEING the success-transparency render — was never achieved. ★ ROOT (the dead-end): the two-store issue — the test channels I created live in the cc_channel store, NOT the bridge's fold_channels store; they're dead-letter (no members) or archived, so a "successful" post never rendered a real landing. (See the friction record.)

RELATIONS: depends on fork's post backend (which was read-only / propose-gated earlier, then opened per Tim); blocked-verify by the two-store split.

OPEN_QUESTIONS/GAPS: pick a genuinely active+membered channel in the BRIDGE store, post, screenshot the success render both viewports. This is OWED and not done. Do NOT read the fail-soft verification as success-verification.

SOURCE_ADDRESS: commit 08209b9 (the composer); doc OPERATOR-SURFACE-LOOP.md (the post-landtest two-store finding).
