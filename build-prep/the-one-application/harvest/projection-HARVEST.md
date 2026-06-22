# HARVEST — projection / the FACE-1 operator surface + the Right-Hand-Man (the V)

**author_session:** projection — filing session transcript `f609942f-fc17-47f5-a739-966343e5a54c` (the lane spans multiple session-ids across the 4 days; recollection's transcript-extraction is the cross-session BACKBONE this harvest is the curated COMPLEMENT to).
**territory:** the half of the Company an operator (Tim) sees and acts through, so he can leave the CLI — `surface/app/` (the Instrument :5174, thin over the bridge :8770) + `build-prep/universal-projection/`.
**role:** build the operator surface (instrument/map + sibling-overlay faces + the decision card) and wire the Right-Hand-Man (L1 grounded-explain, L2 ask, L4 post-back, L5 propose/accept).
**bar:** every claim tagged `verified` (re-seen by-use THIS harvest/session, not from the loop-doc) | `attempted-unverified` | `broken` | `abandoned` + WHY. No self-certify — I proved IN-SESSION that my own record lied (channel-view was logged "verified both viewports" and was a 162px bug), so the loop doc's ~1800 lines of "verified" are NOT inherited.

**Board complement:** 13 structured, typed-edge-linked board records, root `board://item-ef7eb599` (each `authored_by` projection, indexed there).

---

## WHAT I AM (about / kind / summary)
- **about:** a thin, from-DNA operator surface over the bridge — an instrument (the wheel/map) with sibling-overlay faces (decisions · the fabric · the board · sessions · history), a nav rail to reach them, and a decision card that explains itself grounded (L1), can be asked about (L2), accepts a post-back to the fabric (L4), and has an assistant-proposes-an-update wire (L5). **kind:** built-artifacts + architectural-laws + one structural honesty-gap (the operator loop never closed on a real Tim decide).
- **summary:** drove the FACE-1 breadth + the RHM layers to their real close-gates. The throughline: **the LOOK beats the inference — a green measurement is as suspect as a green claim, and a self-authored "verified" is not evidence.** That discipline caught 5 false measurements and one lying record before they shipped.

## ★ THE DEEPEST HONEST STATE (corroborating composition)
**The operator loop NEVER closed on a real Tim decide.** `verified` (by-the-absence). The whole point — Tim makes a real decision/act ON the surface and it flows through to execution — was never demonstrated end-to-end with the real Tim. WHY, three compounding reasons: (1) every by-use verification I did was in `?verify=1` mode, which by DESIGN suppresses the `decision_take` write — so I never even let a real decide-write happen; (2) Tim was on the OLD canvas surface (:8770), not my Instrument (:5174), which was localhost-only until a late Tim-authorized bind — the **access-path was never confirmed to be the surface I built**; (3) L5 (assistant-proposes → Tim-accepts) is built but end-to-end-unverified. So the surface is verified to RENDER and to move its own state by ME; it is NOT verified that TIM can close a real operator loop on it. This is the single most important carry-forward — composition recorded the same from its side.

## CLAIMS (each tagged — re-checked this session)

1. **FACE-1 breadth surfaces (channels · board · sessions · transcript) on ONE from-DNA clone-host pattern.** `verified` (by-use BOTH viewports this session, post-bounce; `board://item-09464b5e`). transcript-viz is the headline (commit 5211961): the 35,904-chunk corpus searched by meaning → DNA's constellation. ★ Route-backend gotcha caught BEFORE building (advisor): /api/transcript-search reads a sqlite/chroma index, NOT the numpy VEC_PATH my memory named — curl'd it serving first.

2. **The phone-frame FORM sweep — 3 surfaces.** `verified` (by-sight this session). DNA's `.screen` is a fixed 390px phone-frame; at 1440 it pinned graph/zones bodies to a 162px island. Fixed in transcript (162→412), board (2ef987b — was hiding the WHOLE Guide group behind Signal), channel (d8f1320 — the record had FALSELY logged it verified). One-line fix each.

3. **sessions-roster FILTER.** `verified` (by-use both viewports; e729c98). The 60-cap roster had no search; added an instant client-side filter (title/name/cwd/state, never the id). 60→3 on 'supervised-live', honest no-match.

4. **L1 grounded-explain streams on the card.** `verified` (by-sight this session, warm-isolation; 6016ecc; `board://item-96a3e3da`). cube-3d (theorem-fork): warm route 2.2s → the .dc-explain region swapped placeholder→content (Tim's multi-axis theorem + the why-line + the AI-inference-flagged ground-note). ONLY theorem-fork re-verified; other subtypes `attempted-unverified`. Grounding QUALITY is fork/recollection's correctness call.

5. **SurfaceNav — the orphan-screens fix.** `verified` (by-use this session; 0f44693; `board://item-58f23618`). Tim's gap: "where are the other screens? how do I access them?" — surfaces were built but orphan. The rail (DNA's navRail) opens each. I clicked the real History tile → it opened.

6. **L2 grounded-ask.** `attempted-partial` (`board://item-8de3a4ff`). The V's ask works (.groundedAsk via /api/brain/ask, verified an earlier fire). BUT the in-card "Ask about this" hits the GENERIC /api/claude/turn, not recollection's explain_role — so it's not grounded-by-construction. It self-caveated honestly on a theorem-fork (didn't fake grounding). The redirect was identified, NOT landed.

7. **L4 channel-post composer.** `attempted-unverified` at the success path (08209b9; `board://item-b69720ab`). FORM verified + fail-soft verified, but a real post landing in a real membered channel was NEVER seen — the two-store dead-end (cc_channel store ≠ the bridge's fold_channels store; my test channels were dead-letter).

8. **L5 propose/accept wire.** `attempted-unverified` + HELD (e3b9c84; `board://item-b000495e`). Route-level built (accept→POST /api/decision/update/accept, token→200/none→401). End-to-end visual NEVER verified (waits on a bounce + DNA's Accept-button). NOW also gated on Tim's design walk-through (the new user-facing-walks-through-Tim rule). NOTHING about L5 is verified-by-use.

9. **#1b operator-session token.** `built + banked` (558e4a8; `board://item-b3b75ea7`). Server-decided supervised-vs-autonomous discriminator (never a client flag — spoofable). The interceptor mints+attaches the header (structural-verified). Enforcement (A) held indefinitely per Tim's fully-open-posting call. No live consumer → "is enforcement correct?" is genuinely untested.

10. **The architectural spine (design laws).** `verified-as-pattern` (`board://item-b6af8629`): from-DNA law (never bespoke; blocked-not-faked when DNA hasn't shipped) · sibling-overlay seam · the one verb-bus · verify-mode (no ghost-takes) · registry-is-truth (honest degrade, never silent-empty) · server-decides-never-client-flag · the-look-beats-the-inference. These produced 4 working surfaces; whether they're canonical company-wide is a composition/Tim call.

## NOT-DONE (honest)
- **timeline surface** — `blocked-on-DNA` (`board://item-2649cb09`). DATA verified (/api/events serves: {seq,ts,kind,summary,op,duration_ms,...}); RENDER blocked — DNA ships no timelineRecord adapter / 'timeline' archetype. I handed continuing-DNA the live shape + the precise ask (thread g-1782120769); will clone-host the instant it ships.
- **address surface** — `not-started`; no clean route found; asked DNA to name one.
- **L4 success-land / L5 end-to-end** — owed, gated on a coordinated bounce (+ L5 on Tim's walk-through).
- **The earlier universal-projection / invariant theorem body** (criteria · union-seam · widen · dimension-bridge · glossary · theorem-sources · multi-layer-consult) — `accounted, NOT re-certified` (coverage ledger `board://item-a7f13103`). A large body of theorem-mapping I did not do this session; SCAFFOLDING, correctness is Tim's framework call; backbone holds it. I do NOT vouch for it as done/true.
- **The company-landscape dragnet** (10 AREA docs) — `produced`; accuracy/use is the recall-substrate mission's (recollection's) now.

## RELATIONS (typed edges)
- **derives_from:** all breadth surfaces ← DNA's adapters+archetypes (the gate); L1 ← fork's /api/decision/explain + recollection's grounding + DNA's region.
- **composes_with:** L5-accept → the #1b interceptor (its only consumer); the surface → fork's bridge READ-API; the decision card → DNA's renderArchetype.
- **blocked_by:** timeline/address → DNA's unshipped shapes; L4-success → the two-store split (fork); L5 → a bounce + DNA's Accept-button + Tim's walk-through.
- **refutes:** the channel-view false-"verified" → any inherited loop-doc green; the operator-loop-never-closed → any "the surface works for Tim" claim.
- **same_law:** the 5 measurement false-negatives ↔ the lying channel-view record ↔ the committed-not-live trap ↔ the access-path miss — ALL one law: **the look beats the inference; verify the actual thing in a trusted context, never the claim, the measurement, or the record.**

## OPEN QUESTIONS (for whoever resumes)
- Does the operator loop CLOSE for the real Tim, on the real access-path, with a real (non-verify-mode) decide that executes? Never demonstrated. THE question.
- Is the loop-doc's historical "verified" still true post-reboot? Re-verify by-use; don't trust the green.
- timeline/address: DNA ships the shapes → clone-host (mechanically ready).
- L2's "Ask about this" → redirect to explain_role (identified, unbuilt).

## DEAD-ENDS / REASONING worth keeping
- **Measurement contamination (5×):** L1 read "stuck on placeholder" TWICE (competing probe-fetches; then a bounce severing the in-flight GPU run) — a clean warm-first isolation proved it streams. Plus the concurrent-explain sweep, a 0-char timing race, an operatorSession ?v2 probe reading null. **Lesson: distrust the measurement as hard as the claim — go to the primary evidence.**
- **The lying record (channel-view):** I told the lead "channel-view already fine" on the stale "verified" record + an inference (svg force-sized) — the advisor pushed me to LOOK; it was a 162px island, and even my WHY was wrong. **Lesson: don't trust a "verified" record you've already seen lie about the surface next door.**
- **committed-not-live:** routes returned {}/404 on the running bridge despite being committed — the bridge caches runtime in sys.modules until a BOUNCE. **Lesson: verify the route SERVES (curl), not just exists in code, before building on it.**
- **The two-store split:** cc_channel store ≠ the bridge's fold_channels store → my L4 test posts dead-lettered. **Lesson: confirm WHICH store the live path reads.**

## PROVENANCE
Session `f609942f-...` (lane: projection). Built artifacts (author_session = projection), under `surface/app/src/`: transcript/ · board/ · channels/ · sessions/ · nav/ · gallery/GalleryMount · lib/groundedExplain · lib/operatorSession · rhm/RightHand · decisions/ · App.tsx (verb-bus/overlays) · scripts/sync-gallery.mjs. Docs: `build-prep/universal-projection/OPERATOR-SURFACE-LOOP.md` (the 4-day log — read its "verified" as attempted-unverified unless re-seen) + TIMELINE-ROW-SHAPE / GROUNDED-EXPLAIN-MECHANISM / TOOL-FRICTION-LOG. 391 [projection] commits. Board harvest root: `board://item-ef7eb599`. Recall backbone for my arc: `session_recall(op=…, session="f609942f-fc17-47f5-a739-966343e5a54c")`.
