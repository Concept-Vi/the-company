---
id: item-b6af8629
address: board://item-b6af8629
type: guide
source: claude_code
state: living
title: HARVEST · projection · the architectural spine (the durable design laws of
  the surface lane)
author_session: projection
channel: ''
thread: ''
links:
- kind: references
  target: board://item-78c63045
created: '2026-06-22T11:40:55.745063+00:00'
updated: '2026-06-22T11:40:55.745063+00:00'
history:
- from: null
  to: living
  by: projection
  ts: '2026-06-22T11:40:55.745063+00:00'
  note: filed
---

STATUS: verified-as-pattern (these laws produced 4 working breadth surfaces + L1 + the nav; the pattern holds).
LANE: projection · TIMESTAMP: 2026-06-22

ABOUT: The reusable design decisions the whole operator surface rests on — the part most worth carrying forward, independent of any single surface.

KIND: architecture / design-laws

CLAIMS/DECISIONS:
- [verified] FROM-DNA LAW: the surface NEVER renders a bespoke component for anything DNA owns. The host fetches data + frames + mounts DNA's organism (faceRecord adapter → renderArchetype). Every breadth surface is this. When DNA hasn't shipped a shape, the surface is BLOCKED, not faked (see timeline). This is the operator-surface instance of "don't build a parallel system."
- [verified] SIBLING-OVERLAY SEAM (host seam 1): each face is an App-root overlay over the instrument, opened by a window event (channels:open / board:open / sessions:open / transcript:open / decision:open), Esc-closes. The instrument (the wheel) is the base/home. Uniform, composable.
- [verified] THE VERB-BUS: surfaces emit on ONE bus (gallery:verb → App.onVerb) with specific handlers + an honest Notice fallback for unhandled verbs. New surfaces get honest handling for free.
- [verified] VERIFY-MODE (?verify=1): suppresses consequential writes (decision_take) so by-use verification never mutates real state — how I dogfought without ghost-takes.
- [verified] REGISTRY-IS-TRUTH: stores hold exactly what the route declares and branch on nothing it doesn't (e.g. isTimFacing = owner==='tim', the transition-fallback deleted once owner went live). Honest degrade + fail-loud, never a silent empty or a fabricated value.
- [decision/principle] SERVER-DECIDES-NEVER-CLIENT-FLAG: a supervised-vs-autonomous discriminator must be server-side (the #1b token), because a client boolean is spoofable.
- [decision/principle] THE LOOK BEATS THE INFERENCE: by-SIGHT whole-screen verification overrides the a11y-tree / DOM / self-authored record (the gallery-frame width:0 and the channel-view island both rendered "fine" to the tree). See [[the honest-state discipline]].

RELATIONS: every projection record is an instance of these laws; the from-DNA law is WHY timeline is blocked not faked; verify-mode is how all the by-use verification was done safely.

OPEN_QUESTIONS/GAPS: these laws are MINE (projection's); whether they're the right company-wide surface laws is a composition/Tim call. They're verified to WORK, not ratified as canonical.

SOURCE_ADDRESS: files src/App.tsx (onVerb/verb-bus, overlay mounts), src/decisions/decisionsStore.ts (registry-is-truth), src/lib/operatorSession.ts (server-decides); doc OPERATOR-SURFACE-LOOP.md.
