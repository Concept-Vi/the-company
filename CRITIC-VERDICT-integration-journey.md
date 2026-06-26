# Fresh-Eyes Critic — Whole Operator Journey (Integration Test)

URL: http://127.0.0.1:5174/  | Phone 390x844x3 (fresh) + Desktop 1440x900x1 (fresh)

## VERDICT: PASS (with flags)

A cold, non-technical stranger CAN land, understand what they're looking at, find what
needs them, decide, and use the guide. The pieces cohere as one product. The guide (V)
genuinely rescues a lost stranger. Flags below are real but none break the core journey.

## What works (verified)
1. FIRST CONTACT — strong. Title "What's happening", plain explainer ("A live map of
   everything the Company is doing... each dot is one thing that happened..."),
   "N decisions waiting" pill, the map, the V guide, a "right-hand-man" greeting offering
   "Show me around" / "I'll explore". Stranger immediately knows what this is.
2. THE MAP — legible. Circular live map; slice = kind, distance from centre = how long ago,
   centre = now. The explainer spells this out. Not overwhelming.
3. WHAT NEEDS ME — clear. Pill -> "Decisions waiting for you / The Company needs your call
   on these." Each card: plain title + "Suggested:" recommendation.
4. DECIDE — works end-to-end and VERIFIED. Open decision -> framing question + "What this is"
   box + options A/B/C with tradeoffs + RECOMMENDED badge + per-option "Choose ..." button.
   Selecting commits: POST /api/territory/write returned {"ok":true,"written":1,
   "source":"operator"}; count decremented 7->6->5; decided item left the list; closing
   returns to the list. Loop closes correctly.
5. THE GUIDE (V) — the centerpiece, and it delivers. 3-step tour ("What am I looking at?",
   "What can I do here?", "Where can I go from here?") each answered live in warm plain
   language, no jargon, ending with an offer. Free-text Q&A also works (asked "what are the
   decisions waiting for me?" -> real, helpful, recommending the quickest win). Works on
   BOTH viewports.
   SPOTLIGHT (bonus, calibrated): VERIFIED the whole surface dims behind the guide card
   (global dim). NOT observed: a discrete per-control highlight as the guide names individual
   controls. Polled the named-control moment in step 2 ("lens, layer, circle/square, time
   scrubber") for ~6s — no control acquired a highlight/glow/ring while the rest stayed dim.
   So the "light up as it names things" bonus is NOT present (or not catchable); the base
   dim-to-focus is present and works.
6. COMING AWAY — a stranger would understand the surface and could use it.

Coherence: one product, not bolted-on. Desktop = full circle map centerpiece, side rail,
centered modals, V-anchored guide panel. Phone = stacked, full-width sheets. Both clean.
No console errors (desktop). No broken layout (dialog has no real horizontal overflow —
scrollWidth==clientWidth).

## FLAGS (real, none fatal)

A. JARGON LEAK — "RHM" + architectural phrasing in decision option copy. SYSTEMATIC, both
   viewports. Recommended-option text repeatedly leaks the internal acronym and dev framing:
   - "What a cluster is" option C: "(The RHM's read — your call, easily changed.)"
   - "How a saved file's identity works" option C: "(The RHM leans here, in the
     with-derivation frame — your call.)"
   An operator should never see "RHM" or "with-derivation frame". Fix the copy.

B. JARGON LEAK — raw item codes in the guide's own answer. When asked about decisions, the
   guide listed items with raw IDs visible on screen: "(s117)", "(s115)", "(s100)",
   "(s60-review)", "(s118)". Operators shouldn't see these codes.

C. COHERENCE / TRUST GAP — two "what needs me" surfaces disagree (most important flag).
   Stated at the experience level (no source-code claim about cause): a stranger taps
   "5 decisions waiting" and sees five SPECIFIC decisions ("How the live streams are held",
   "How a saved file's identity works", "The real kinds of things in the content", "The
   sharpness of the context behind a decision", "Adopt one shared spine..."). Then they ask
   the guide "what are the decisions waiting for me?" and get five COMPLETELY DIFFERENT items
   with ZERO overlap ("Inbox spring-clean", "Floor walk", "33 elements your screens describe
   differently", "Review the build", "The night's brief") — even the word "decision" means
   something different in each. That's a real coherence/trust break regardless of cause, and
   it is NOT excusable as LLM latency — it's content divergence, not timing.
   Why still non-fatal: all five functional steps (land / understand / find / decide /
   use-guide) complete successfully. This gap lives in ONE guide reply's content, not in a
   broken step — so the journey holds, but the inconsistency would confuse/erode trust.

D. MINOR — header "600" is a raw unlabelled number (= count of things on the map,
   /api/projection?limit=600). No plain-language label/unit; reads as mystery to a stranger.

E. MINOR — decision SUBSTANCE is architectural. The surface PRESENTS decisions as well as
   possible (plain framing + recommendation), but the underlying questions ("is a cluster a
   NAME or a LIVE grouping", "is a saved file the same thing as its content") are abstract.
   A non-technical founder leans on the recommendation rather than truly grasping the stakes.
   This is content depth, not a surface defect.

## NON-ISSUE (investigated, cleared) — evidence-classified
- VERIFIED: the save works. POST /api/territory/write -> {"ok":true,"written":1,
  "source":"operator"}; the decisions count decremented; the decided item left the list.
- A "! Couldn't save — try again" string sits in an aria-live container. NOT OBSERVED on
  screen in any screenshot taken right after the click (an inference from sampled captures —
  a toast could in principle flash and fade between click and capture). Given the write is
  verified ok:true, this appears to be stale/queued live-region text, i.e. a possible
  false-alarm toast — NOT a save failure. Worth tidying so it can't flash, but does not
  affect the journey.

## UNTESTED (noted, low value to chase)
- "Ask about this" button inside each decision: not exercised. It is another door into the
  same right-hand-man guide that was tested thoroughly via the tour + free-text Q&A.
