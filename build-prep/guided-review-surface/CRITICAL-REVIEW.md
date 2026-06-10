# CRITICAL REVIEW — the guided-review surface, both faces, by USE on the rendered surface

> **Updated in place (2026-06-09, second pass).** The prior pass could NOT drive the surface
> (tldraw click-interception defeated it) and concluded the populated experience was "UNVERIFIED /
> not seen." This pass **succeeded in driving the populated surface** — the gallery, the guided tour,
> click+talk, comment, and generate — and so CORRECTS several of the prior pass's pessimistic calls
> with real observation, CONFIRMS others, and adds the make-or-break finding the prior pass never reached.
>
> Driven on the REAL surface: temp store, isolated bridge `:8799`, vite `:5188`, model `:8000` up for
> the RHM. No green-paint, in either direction — a thing not seen working is not "met," and a thing the
> harness blocked is "couldn't-observe," NOT "not-met" (the false-negative trap cuts the same as
> green-paint). Screenshots in `.build/interface/shots/review-*.png`.
>
> **Provenance labels:** *by-use* = I drove/curled it and watched the result · *code-confirmed* = read
> in source (structure, NOT run — never stated as verified function) · *couldn't-observe* = harness/
> empty-store blocked observation.

---

## ★ HEADLINE VERDICT — dev-stuff, or a navigable at-altitude surface that takes a non-dev through?

**It mostly does NOT feel like dev-stuff. The at-altitude, "takes-you-through" face is genuinely
built and genuinely works — with two specific, nameable dev-stuff LEAKS, and one make-or-break
FUNCTION break sitting behind a good-looking front.** This is materially better than the prior pass
claimed (it never saw the tour or the populated surface) AND it is not done (F2's loop is broken).

**The surface IS on the design system / corpus tokens — settled objectively, not eyeballed
(this resolves the "deliberately unstyled" tension):**
- `evaluate_script` read **280 live CSS custom-property declarations**; `--bg:#0c0a08`,
  `--ink:#f3ece1`, `--font-display:'Fraunces'`, body font `IBM Plex Mono` (the corpus serif-display +
  mono voice). `design-system.css` is imported via `main.tsx`. (by-use)
- The chrome reads as a designed product: gold-on-near-black, a calm `◧ canvas / ▦ review` view-switch
  with plain-language tooltips, a grouped corpus gallery, at-altitude lede prose. (review-01, -05)
- Every chrome element carries a real `data-ui-ref` (`ui://view-switch`, `ui://studio/rail`,
  `ui://chat/input`, `ui://studio/generate`…) — the addressed-surface FORM substrate is fully present.

**The guided tour genuinely LEADS (the prior pass said this was "not seen / unbuilt" — WRONG):**
- Clicking `? guide` started a 3-step sequence; the **view drove to the element and ringed it**
  (`.ui-spotlight` on `▶ run`); progress read "**1 of 3**". Clicking `next →` advanced to
  `ui://toolbar/presence`, "**2 of 3**", spotlight + narration moved. (by-use; review-09, review-10)
- Narration is the corpus 3-leg, in plain language: *"WHAT: the Run control. WHAT YOU CAN DO: click it
  to recompute the current graph… HOW TO CHANGE IT: …"* — reads like a person, not a JSON/registry dump.

**Click + talk works at altitude (the prior pass said "unseen / chat box" — partly WRONG):**
- With a mockup focused (`focus.selected=["mockup://C1-inbox-desktop.html"]`, a LIST — the FE sends a
  list), the RHM said: *"you're looking at a design mockup called C1 · Inbox… three zones: Top bar…
  Left rail…"* — at-altitude prose grounded in the mockup HTML. (by-use, C1 verified through the stream)
- `/api/chat/stream` returns NDJSON parts incrementally (`{idx:0}` then `{idx:1}`) — B1 streaming
  FUNCTION verified-by-use.

**The genuine dev-stuff leaks (narrow + specific — NOT a general condemnation):**
1. **tldraw editor chrome bleeds through the review surface.** The drawing toolbar (Select/Hand/Draw/
   Rectangle/Ellipse/Star/Cloud/Heart…), the page-menu, the zoom control, and a **"MADE WITH TLDRAW"**
   badge are visible *in the review workspace* (review-02, review-05). The studio overlay
   (`.studio-shell`, `position:fixed; z-index:40`) does not occlude the editor beneath it. To a
   non-developer this reads as "a diagram/editor tool," not "a product reviewing my designs." *Top
   FORM gap, and the prior pass was right about this one.*
2. **A CSS-text leak bug:** the responsive-overflow stylesheet renders its own source as visible
   toolbar text — `#_rh__main > *:nth-child(n + 10) { display:none } …` shows as a literal string.

**Net:** remove the two leaks and the "looks like a product" claim holds for what's built. The feel
face is closer to PASS than the lead's blanket "needs-tim" deferral implied.

---

## ★ THE MAKE-OR-BREAK IS BROKEN AT THE SEAM (F2) — looks fine, doesn't connect

The founding promise — comment on a mockup → generate → it edits the mockup — **cannot complete from
the live surface.** Not because the engine is broken (it works), but because **the comment and the
generate read two different stores.** This is the exact end-to-end gap curl-verification missed: curl
exercised the engine; the engine works; the *operator's path* does not.

**The contradiction — two recent decisions disagree on the source of truth:**
- `regions/Review.tsx:14` (code-confirmed): the mockup-feedback JSONL is *"RETIRED for this in-app
  surface"* — the studio `💬 comment` posts to `/api/annotate` → the **address-keyed annotation store**
  (`api.ts:220` says so explicitly).
- `runtime/generate_mockup.py:91` + Tim's own re-scope at `Completion Criteria.md:988` (2026-06-09):
  generate reads feedback from **`design/mockups/.feedback/<file>.html.jsonl`** — the retired store.
- **No FE path writes the JSONL generate reads.** (`POST /api/mockup-feedback` exists at
  `bridge.py:1641` but the studio Composer never calls it.)

**By-use proof of the break:**
- I commented in the studio on C1 ("add a divider and a count badge per lane"). It recorded + showed
  as `operator` at `ui://inbox` (review-11) and persisted in the annotation store (`GET
  /api/annotations?address=ui://inbox` returned it).
- I then called generate → `{"error":"GenerateError: mockup 'C1-inbox-desktop.html' has no actionable
  feedback (0 total note(s)) — nothing to generate from"}`. The comment is invisible to generate.
- **The engine itself works** (by-use): with a note seeded in `A1-…html.jsonl`, `POST
  /api/mockup-generate {mode:"plan"}` returned a well-formed plan — `route:"mockup_edit"`,
  `scope:["design/mockups/A1-canvas-empty-desktop.html"]`, `actionable_feedback_count:1`, a clean
  at-altitude `instruction_core`. Plan mode = read-only (`changed_files==[]`).
- **The FE render is built** (code-confirmed `StudioKit.tsx:222-230`): shows "proposed edit for
  <file> · mode plan · N file(s) would change" + the `proposed_summary` prose — NOT a diff/JSON.

**Verdict on F2:** engine ✅ by-use · render-card 🟢 code-confirmed (couldn't-observe live, blocked by
the seam) · **operator's comment→generate loop ✗ broken by-use.** The make-or-break does not deliver
its founding promise from the surface until the comment store and the generate-feedback store are
unified (the cleanest fix: the studio Composer writes BOTH, or generate reads the annotation store).

---

## SCORECARD — each criterion × FUNCTION × FORM (no green-paint)

Legend: ✅ verified-by-use · 🟢 code-confirmed (present, not run) · 🟡 partial · ✗ not-met (saw fail/
absent) · ◌ couldn't-observe (harness/store blocked — NOT a fail).

| Criterion | FUNCTION | FORM |
|---|---|---|
| **A1** enter sequence → drive view to stop 0 | ✅ `? guide` started a 3-step seq; view drove to stop 0, element ringed (review-09) | ✅ guided overlay on corpus tokens; spotlight+card read as one place |
| **A2** narrate AT-ALTITUDE what-this-is / what-you-can-do | ✅ stop narration = corpus 3-leg, plain language (by-use) | ✅ reads like a person, not a dump (review-09/10) |
| **A3** you set the pace — next/back/dwell | ✅ `next →` advanced 1of3→2of3, spotlight moved (by-use) | 🟡 next + "N of M" + voice/text visible; **no BACK control confirmed at stop 1** |
| **A4** guided walk across mockup FILES | ✗ live tour walks `ui://` chrome only; mockup stops blocked by F1/L1 | 🟢 Stage renders a mockup in an iframe beside the panel (review-05) |
| **B1** streamed text talk-back, part-by-part | ✅ `/api/chat/stream` NDJSON `{idx:0}`,`{idx:1}` incremental (by-use) | 🟡 parts land as whole-paragraph blocks; in-browser **cadence couldn't-observe** → stays 🔴 needs-tim |
| **B2** talk-back follows what you point at | ✅ focus(LIST)→locus; mockup:// grounds reply in the mockup (by-use) | 🟡 locus shown as "this surface: ui://inbox" + composer chip; **no "talking about: X" chip on the reply turn** |
| **B3** interruptible (barge-in on text) | ◌ not driven | ◌ |
| **B4** the RHM asks BACK / clear voicing | 🟢 rides the model; replies offered follow-ups | ✅ `you ◆` vs `vi ◇` voicing distinct (DOM-confirmed) |
| **C1** a mockup explains itself at altitude | ✅ RHM named the mockup + walked its zones via the stream (by-use) | 🟡 prose not raw HTML; lands in the RHM panel (not a dedicated card) |
| **C2** registered live elements explain (3-leg) | ✅ the guide stops ARE the 3-leg bundle (by-use) | ✅ WHAT / WHAT-YOU-CAN-DO / HOW-TO-CHANGE read as zones |
| **C3** routed through altitude-shaping | ◌ not traced; synthesis flagged it possibly declared-not-wired | 🟡 register reads at-altitude in practice; wire unconfirmed |
| **C4** 14KB-cap pre-digest | 🟢 cap present `suite.py:2202`; not exercised on a big mockup | n/a |
| **D1** mark accrues at an address (visible) | ✅ comment recorded + persisted at `ui://inbox`, source=operator (by-use) | ✅ shows as a visible authored mark in the composer thread (review-11) |
| **D2** context auto-resolves at locus (R2) | 🟢 running per synthesis; not re-driven | 🟡 no visible "what's been said here" read-face in the studio |
| **D3** group roll-up (descendant-gather) | ◌ not built/driven | ◌ |
| **E1** the singular wire end-to-end | 🟢 verified by the PRIOR wire build (not re-run) | 🟢 |
| **E2** accumulate → compose → one-approve BATCH | ◌ no batch-review board observed; generate is per-mockup | ◌ |
| **F1** mockup-aware guided stop | ✗ tour walks `ui://` only; `mockup://` not in SCHEMES (see L1) | n/a |
| **F2** GENERATE-FOR-MOCKUPS (MAKE-OR-BREAK) | **✗ operator loop broken at the comment→generate seam**; engine ✅ by-use | 🟢 card is prose not diff (`StudioKit.tsx:222-230`); couldn't-observe live (seam blocked) |
| **G1** "this/here" current locus | ✅ focus resolves to pointed element (by-use) | ✅ "this surface: ui://…" visible |
| **G2** standing locus-trail (breadcrumbs) | ◌ not driven (lowest urgency) | ◌ no breadcrumb strip observed |
| **H1** voice-in feeds dialogue, locus-aware | ◌ device-only (mic) | 🟢 `🎙` push-to-talk + voice/text toggle present |
| **H2** the FE show-me lane (SEES himself walked) | ✅ tour drives + spotlights + narrates + paces (by-use, review-09/10) | ✅ reads as ONE guided surface, not a row of buttons |
| **I1** the surface IS the walkthrough mode | 🟢 guide/teach/presence-dial present; mode-drive not independently traced | ✅ dial + guided register shift visible |
| **I3** advancing re-grounds the chat | ◌ tour advanced but I didn't ask a question per stop to confirm | ◌ |
| **I4** RHM-annotate verb | ◌ not driven | ◌ |
| **I5** anti-parallel guard | 🟢 one chat organ reused (RhmChat in both canvas HUD + studio panel — same component) | n/a |
| **J3** "Next" human go-gate | ✅ tour held at each stop until I advanced (by-use) | 🟡 reads as a go-control; back unconfirmed (A3) |
| **J1/J2/J4–J9** queue/origin/lifecycle/branch/verdict/derived-from/modes/S1-S7 | ◌ empty store / scenario / device legs | ◌ |
| **K1–K4** walkthrough cast / posture / injection | ◌ CognitionView not driven | ◌ |
| **L1** register `mockup://` in SCHEMES | ✗ code-confirmed ABSENT: `contracts/address.py:32` `SCHEMES=("run","cas","blob","vec","ui","code")` — no `mockup` (this is why F1 can't tour mockups) | n/a |
| **M1/M2/M3** coherence oracle / verify-gate / FORM hook | ◌ cross-lane / coherence-owned | ◌ |
| **O1/O2/O3** general organ + 7 consumers | 🟢 structural; build-review is consumer-1 under test | n/a |

**Tally (honest count):**
- **Met BOTH faces by-use:** **A1, A2, C2, D1, G1, H2** (+ B2 with a FORM caveat) ≈ **6–7 criteria.**
- **FUNCTION-met, FORM-partial:** A3, B1, C1, B4, J3.
- **Genuinely NOT met (saw fail / confirmed absent):** **F2 operator loop, F1, A4-mockup-stop, L1.**
  F2 is the make-or-break.
- **Couldn't-observe (empty store / device / cross-lane — surfaced, NOT failed):** B3, D3, E2, G2, H1,
  I3, I4, J1/J2/J4–J9, K1–K4, M1–M3.

---

## GAP LIST — built-and-good vs built-but-dev-stuff vs not-built

**Built-and-good (FORM passes — don't touch):**
- The corpus-token styling (280 vars, Fraunces/mono, gold-on-dark) — objectively on the design system.
- The guided tour's lead-feel: spotlight-drive + "N of M" + 3-leg at-altitude narration.
- The at-altitude lede + plain-language tooltips.
- The addressed substrate (every element `data-ui-ref`'d).
- The comment-as-visible-authored-mark, threaded at its address.

**Built-but-dev-stuff (FORM fails — fix, not rebuild):**
- **tldraw editor chrome leaking into the review surface** (toolbar, shapes, "MADE WITH TLDRAW"). The
  review overlay must hide/occlude the editor in review mode. *Top FORM gap.*
- **CSS source rendered as visible toolbar text** (`#_rh__main > *:nth-child…`).
- **No persistent "talking about: X" locus chip on the chat turn** (B2 FORM) — locus is shown at the
  composer, not bound visibly to the scrolling reply.
- **No BACK pace control confirmed** at the tour's first stop (A3 FORM).
- **No visible "what's been said here" read-face** in the studio (D2 FORM).

**Not-built / confirmed-absent (FUNCTION):**
- **F2 operator loop** — comment→generate seam (annotation store ≠ generate's JSONL). *Make-or-break.*
- **F1 mockup-aware tour stop** — blocked by **L1**: `mockup://` not in `SCHEMES`, so the tour can't
  walk the proposals it exists to review.
- **E2 batch-review board** — not observed; generate is per-mockup only.

**Couldn't-observe (empty temp store + headless harness — surface to Tim, neither done NOR failed):**
the J-group outer circuit (queue / origin / lifecycle / branching / verdict / derived-from) needs
seeded inbox items; voice/auto-listen needs a device; B1 *cadence*, the *led feel*, and the
*his-altitude landing* are 🔴 needs-tim by design.

---

## The "deliberately unstyled" tension — NAMED

**Settled: the surface is genuinely on the design-system / corpus tokens, NOT unstyled dev-stuff.**
Objective evidence (not opinion): 280 live CSS-var declarations, the corpus type pair, `design-system.css`
imported, `--bg/--ink` on `body`. The dev-stuff *feel* that remains is NOT from being unstyled — it is
from **two foreign-chrome leaks** (the tldraw editor surface + the CSS-text bug) on top of an
otherwise-designed product. The prior pass's "deliberately unstyled was cover for not doing FORM" call
is **overturned by measurement** — the FORM work was largely done; the leaks and the missing locus-chip
are the residue.

---

## Harness / stability notes (artifacts, NOT product verdicts — so they aren't mis-scored)

- **The bridge process died twice** mid-session (silent, no traceback; model `:8000` unaffected),
  producing a transient "⚠ chat stream failed (500)" (review-08). Attributed to process management
  under the dev harness (long background curls / setsid session), **not** a product defect. B1 FUNCTION
  stands from the earlier successful streams. Worth a glance: the single-process bridge has no
  auto-restart.
- **Mobile (390) = couldn't-observe, NOT not-met.** `resize_page` to 390 did not take
  (`window.innerWidth` stayed 945), so review-13 is not a real phone render. The CSS carries the
  responsive intent: **16 `@media` queries** incl. `max-width:699px`, and `app.css:1569
  .studio-shell{grid-template-columns:1fr}` reflows the studio to single-column on phone. Real device/
  emulation verification is owed; do NOT hand Tim a bleak mobile verdict off this.
- **`POST /api/mockup-feedback` did not persist** in two attempts (empty response, no file written);
  possibly related to the bridge deaths. Secondary; flagged.
- **Conversation-history bleed:** a fresh turn sometimes answered about the prior turn's subject before
  correcting. Continuity behavior, not a C1 comprehension fail.

---

## Screenshots (FORM evidence)

- `review-01-landing-1440.png` — canvas surface (designed, gold-on-dark, palette + panels).
- `review-02-review-surface-1440.png` — review view; **tldraw toolbar + "MADE WITH TLDRAW" leak visible**.
- `review-03-gallery-loaded-1440.png` / `review-05-c1-inbox-loaded-1440.png` — grouped corpus gallery +
  C1 staged in the iframe ("showroom with a guide").
- `review-08-talkback-studio-panel-1440.png` — studio RHM panel; the "⚠ chat stream failed (500)"
  bridge-death artifact (NOT a product defect).
- `review-09-guide-stop1-1440.png` / `review-10-guide-stop2-1440.png` — **the guided tour leading**:
  spotlight on the element, 3-leg at-altitude narration, "1 of 3" → "2 of 3".
- `review-11-comment-recorded-1440.png` — comment as a visible authored mark at `ui://inbox`.
- `review-12-generate-result-1440.png` — post-generate (view reset to canvas; result card not shown live).
- `review-13-mobile-canvas-390.png` — **resize did not take (innerWidth=945); NOT a valid 390 render**.
