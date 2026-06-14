# COMPLETION CRITERIA — The Instrument Surface

**Third loop-prep doc.** Companion to `MANDATE.md` (gospel) + `RESEARCH-SYNTHESIS.md` (evidence).
**This is a truth table, not a task list.** A line is green ONLY when verified BY USE (driving the browser),
never by code-reading, never by "it renders," never by a DOM query.

> **Scope discipline (advisor-reframed):** this document is **LEAN and scoped to the FIRST VERTICAL SLICE** —
> the smallest complete thing that proves the whole aesthetic+architecture and that Tim can react to. The slice
> is built as a **fresh app ALONGSIDE the working PWA** (`canvas/app` on :5173 is NOT touched). Everything past
> the slice (all 12 lenses re-homed, the multipurpose strata, the project system, registry-promotion) is named
> in §PHASE-2 but NOT detailed here — it gets its own criteria AFTER the slice calibrates Tim's taste. We do not
> over-spec ahead of his reaction. (No-deferral note: PHASE-2 is *sequenced*, not *parked* — it is the next loop,
> not "later/minor.")

---

## THE TWO BARS (every criterion is judged against BOTH — this is non-negotiable, MANDATE §5)

**FUNCTION bar** — the behaviour is real: real data moves, the control changes real state, no stub, no fake
value, fail-loud on error. Verified by *driving it*.

**FORM bar (half of done, MANDATE L4)** — judged on the WHOLE-SCREEN GESTALT (MANDATE L1), by a **separate
design-critic** on captures, at **all three form factors**:
- Paper aesthetic (warm grounds, soft diffuse elevation, restrained pigment, hairline-edged polygons) — nothing
  of the old dark harness (L7).
- **Text-minimal** — resting state near-textless; detail on demand (L2/L6). Word budgets: desktop 5–8 /
  portrait 2–4 / landscape 8–12 resting words. Audited, not eyeballed.
- **No teleport** — every appear/disappear/move/resize is animated, eased, proportioned by the seed grid (L3).
- **Proportionate** — laid out on the seed constants (`m=2^k`, `m/2` rings, `x=2π/n`, `[0.06,1.0]` band), never
  ad-hoc pixels.
- Native + **equally refined** at desktop 1440×900, mobile-portrait 390×844, mobile-landscape 844×390 (L5).

A line with only a FUNCTION face is **not allowed**. A feature that works but reads as a prototype is **half-done**.

**Verification protocol (exact):**
1. Bridge live: `curl -s localhost:8770/api/projection?binding=raw | head` returns real points (FUNCTION source).
2. Surface up: `cd surface/app && npm run dev` (port 5174; does NOT touch :5173). Proxy `/api`→:8770.
3. Drive in `chrome-devtools`: `navigate_page` → `emulate` viewport `1440x900x1`, then `390x844x2,mobile,touch`,
   then `844x390x2,mobile,touch`. `take_screenshot` (full page) at each, resting + one disclosure state.
4. A **separate design-critic agent** judges the captures against the FORM bar (whole-screen gestalt).
5. Green only when BOTH bars pass at ALL THREE form factors. Fix → re-drive → re-judge. No ceiling on iterations.

---

## PRIORITY ORDER (foundations first — dependency, not feature-importance)

1. **S0 Foundation** — the app stands up alongside; tokens; motion system; address spine. (Everything builds on it.)
2. **S1 The instrument wheel** — the heart: real data on the seed geometry. (The thing Tim reacts to.)
3. **S2 Three form factors** — authored layouts for the wheel. (L5; can't skip any orientation.)
4. **S3 Address + context spine** — the ONE inheritance, wired through the wheel. (L10.)
5. **S4 Taste toggles** — typeface / pigment / motion, flippable in-surface. (Resolves §8 open calls by render.)
6. **S5 Whole verification** — driven, critiqued, committed. (The gate.)

---

## SLICE-1 VERIFICATION LOG — 2026-06-14 (honest: states HOW each was verified)

The first interactive slice is **built, driven, design-critic-PASSED, and committed** (`d077478` + `7a0b901`).
Verified BY USE in headless Chrome at all three form factors. Honesty note (advisor): interaction proof used
JS-dispatched events + DOM/rAF sampling (not a human finger); motion was sampled, not eye-watched.

- **S0.1 app alongside** ✅ — surface/app boots (fell back to **:5175**; :5174 held by another session's canvas; the
  live PWA on **:5173 still boots**, confirmed 200). Proxy `/api`→:8770 serves real data.
- **S0.2 paper tokens** ✅ — token-only components; design-critic confirmed coherent warm-paper system.
- **S0.3 motion system** ✅ — Framer installed; **rAF-sampled a selected dot's r animating 2.4→5.56 over 30
  frames (28 distinct values, spring overshoot) — proven tween, NOT teleport.** Console clean (no warnings).
- **S1.1 wheel on real data** ✅ — 600 pts / 7 sectors / rings=8 / grid=16 from `/api/projection?binding=raw`.
- **S1.2 lens switch registry-true + animated** ✅ — 8 bindings from `bindings[]`; switch raw→semantic re-projected
  to 162 pts. NOTE: raw↔semantic are largely DISJOINT sets → the transition is a **crossfade** (exit/enter), not a
  position-morph; shared elements within a lens tween. Crossfade is a valid no-teleport transition (honest scope).
- **S1.3 point discloses** ✅ — peek→open card with real `summary`/`kind`/address; word-boundary excerpt + "…".
- **S2.1/2.2/2.3 three form factors** ✅ — design-critic PASS at 1440×900 / 390×844 / 844×390; each native.
- **S3.1 addressed + layoutId** ✅ — **615 `data-ui-ref` nodes** (600 points minting `ui://canvas/seq-*` + chrome);
  every animated dot carries `layoutId`.
- **S3.2 indicate→resolve→context** ✅ — capture listener + single `resolveUiTarget` sink; disclosure calls
  `/api/context` and renders the **real R2 bundle** (ancestor walk `ui://canvas/seq-X`→`ui://canvas` HOWTO resolved).
- **S4.1/4.2/4.3 taste toggles** ✅ — typeface/pigment/motion behind a gear; flip live. (Awaiting Tim's pick — S5.4.)
- **mobile hit targets** ✅ — invisible r=15 hit layer per point (the 2.4px dot was untappable; advisor fix); a
  dispatched tap on the hit layer opens the disclosure.
- **all 3 disclosure hosts** ✅ — desktop panel, portrait bottom-sheet (slide-up + handle), landscape rail
  (hint→card swap) each exercised with a real selection.

**Design-critic verdict: PASS** (round 2). Non-blocking polish logged for a later pass: disclosure HOWTO is a
run-on block (compose into label:value lines); no leader/tether from selected dot to card; landscape left gutter
tight; desktop resting-hint floats a touch orphaned; portrait top air. **S5.4 (surface to Tim) is the open item.**

---

## S0 — FOUNDATION (the fresh app, alongside; the substrate everything else needs)

**S0.1 · Fresh app stands up alongside the working PWA**
- FUNCTION — `surface/app` is a fresh React 18 + Vite 6 + TS app on **port 5174**, proxying `/api`→`:8770`,
  Tailscale `allowedHosts`. `npm run dev` boots clean. **`canvas/app` (:5173) is untouched and still runs.**
  ☐ verified by use (both servers boot; surface fetches the bridge)
- FORM — the served page is the paper ground (warm off-white, no dark harness) from first paint; no FOUC, no
  borrowed canvas chrome.  ☐ verified by design rubric

**S0.2 · The fresh paper token system (replaces the harness palette wholesale, L7)**
- FUNCTION — a CSS-variable token file defines grounds / ink / 5 pigments / 4 elevation levels / 1.25 modular
  type scale / dyadic spacing / radii, per RESEARCH-SYNTHESIS §E. Every surface reads tokens, **zero hardcoded
  hex/px** in components.  ☐ verified by use (grep components: no literal colors)
- FORM — a swatch/spec page renders the full token set and reads as one coherent warm-paper system; contrast is
  AAA on ink, ≥7:1 on pigment text; elevation is diffuse soft-shadow (paper lift), not borders/glows.
  ☐ verified by design rubric

**S0.3 · The single motion system (no per-component improvisation, L3)**
- FUNCTION — one motion-token module: shared springs (`gentle`, `snappy`), eased curve
  `cubic-bezier(0.4,0,0.2,1)`, durations (enter 300–400 / move 300–500 / exit 250–350 / colour 150ms),
  `prefers-reduced-motion` honoured. Framer Motion installed. Every animated element uses these tokens.
  ☐ verified by use
- FORM — a teleport-audit: nothing in the slice appears/moves/resizes without a tween; motion reads as authored,
  consistent, 60fps-smooth, no jank.  ☐ verified by design rubric

---

## S1 — THE INSTRUMENT WHEEL (the heart of the slice; real data on the seed geometry)

**S1.1 · The wheel renders real data on the seed geometry**
- FUNCTION — fetch `GET /api/projection?binding=<id>`; render the **verified contract**: `rings` (m/2 concentric
  circles), `sectors[{id,from,to}]` (even `x=2π/n` wedges), `points[{theta,r,sector,address,summary,kind,…}]`
  placed at polar `(theta,r)` over the `[0.06,1.0]` band. Real counts (≈3,038 units / 6,120 events available);
  **no toy slice, no placeholder resting state.**  ☐ verified by use (points match curl)
- FORM — the wheel is the §E geometry: soft-filled polygons, hairline edges, angle-hue per sector (colour-IS-
  geometry preserved); reads as a calm paper instrument, near-textless at rest.  ☐ verified by design rubric

**S1.2 · Lens switch is registry-true and animated**
- FUNCTION — the lens palette is read from the response's `bindings[]` (file-discovered, **not hardcoded**);
  switching binding refetches and re-projects; at least `raw` + one semantic lens work.  ☐ verified by use
- FORM — switching lenses **morphs** (shared-element, no teleport): points tween to new positions, sectors
  re-divide smoothly. Never a blank-then-repaint.  ☐ verified by design rubric

**S1.3 · A point discloses on intent (peek→open), text-minimal**
- FUNCTION — hover/tap a point → peek (its glyph lifts); open → a disclosure card shows the point's real
  `summary` + `kind` + `address`; dismiss cleanly. Driven from real point data.  ☐ verified by use
- FORM — resting state shows NO per-point text; the card is visual-first (shape/colour/one line), animated in/out
  (L6 grammar peek→open→pin→dismiss); within the form-factor word budget.  ☐ verified by design rubric

---

## S2 — THREE FORM FACTORS (authored, not responsive-degraded, L5)

**S2.1 · Desktop (1440×900)** — FUNCTION: wheel centered, ambient side strata stub present, fully drivable.
FORM: refined, proportionate, 5–8 resting words.  ☐ both verified by use at 1440×900

**S2.2 · Mobile-portrait (390×844)** — FUNCTION: full-width wheel + bottom-sheet disclosure (peek handle,
draggable), thumb-arc reachable; every wheel action reachable. FORM: native portrait layout (NOT a shrunk
desktop), 2–4 resting words, 44pt targets, safe-area insets honoured.  ☐ both verified by use at 390×844

**S2.3 · Mobile-landscape (844×390)** — FUNCTION: wheel + persistent right rail (selection/actions), every action
reachable. FORM: native landscape layout (NOT a rotated portrait), 8–12 resting words, 44pt targets.
☐ both verified by use at 844×390

> Each is a **discrete layout module** switched by media query — not arithmetic scaling of one layout.

---

## S3 — ADDRESS + CONTEXT SPINE (the ONE inheritance, L10)

**S3.1 · Every element is addressed + carries a layoutId (the coupled rule, §H#5)**
- FUNCTION — every addressable DOM node is stamped `data-ui-ref="ui://…"` as the **literal full string** before
  first render (mirror the corpus convention); each also carries a unique Motion `layoutId`. Dynamic points mint
  `ui://canvas/<node-id>`.  ☐ verified by use (inspect DOM: refs present + valid)
- FORM — addressing is invisible chrome-wise (additive to clicking, no visual cost); the spotlight/indicate paint
  is a soft paper highlight, animated.  ☐ verified by design rubric

**S3.2 · Indicate → resolve → context, through one sink**
- FUNCTION — a capture-phase click reads the nearest `[data-ui-ref]`; `indicate(addr)` sets the locus;
  `resolveUiTarget()` is the single sink (validates grammar, **fails loud** on unknown → a Notice, never silent);
  the disclosure card calls `GET /api/context?address=…` and shows the real R2 bundle (capped at 4000 chars,
  "n more beyond cap" if over).  ☐ verified by use (context for a real address renders)
- FORM — the context surface is text-minimal, on-demand, animated; an address error shows as a calm Notice, not a
  crash or a blank.  ☐ verified by design rubric

---

## S4 — TASTE TOGGLES (resolve the §8 open calls by render, not by asking Tim to spec)

**S4.1 · Typeface toggle** — FUNCTION: flips among the 3 candidate pairings (Charter+Inter / Crimson+Outfit /
Lora+Inter) live, no reload. FORM: each renders cleanly at the modular scale; the toggle is itself paper-elegant.
☐ both verified by use

**S4.2 · Pigment toggle** — FUNCTION: flips pigment saturation (e.g. 20% / 25% / muted) live across the data
sample. FORM: colour still MEANS (bound to data state / angle-hue), never decorative.  ☐ both verified by use

**S4.3 · Motion toggle** — FUNCTION: flips gentle-spring ⇄ eased-out-cubic live on the same transitions. FORM:
both feel smooth; neither teleports; the difference is visible on a panel open / lens morph.  ☐ both verified by use

> These toggles exist so Tim resolves taste by **flipping and watching**, then the winner is baked. They are a
> slice-only scaffold (Scaffolding-not-spec), removed/settled once he picks.

---

## S5 — WHOLE VERIFICATION (the gate)

**S5.1 · Driven across all three form factors** — whole-screen captures (resting + disclosure) at 1440×900 /
390×844 / 844×390; both bars pass.  ☐ verified by use
**S5.2 · Separate design-critic verdict** — a separate agent judges the gestalt against the FORM bar and returns
PASS (defects fixed and re-judged).  ☐ verified
**S5.3 · Live + committed** — bridge curl confirms the data path; the surface is committed to `main` (no branches,
no co-author trailer); the working PWA on :5173 still boots.  ☐ verified by use
**S5.4 · Surfaced to Tim** — the render + the three taste toggles are put in front of Tim to react to (the calls
in MANDATE §8 / SYNTHESIS §I are decided by his reaction, not assumed).  ☐ done

---

## PHASE-2 — DEEPEN AFTER THE SLICE CALIBRATES (sequenced next loop, NOT parked)

Named so it isn't lost; **detailed only after Tim reacts to the slice** (each gets its own criteria then):
- **Re-home all 12 lenses** (G2 grid · G3 scrubber · G4 live-SSE · G5 form · G6 circle · G7 strain · G8 substrate
  · G9 separator+fifth-gate · G10 typed edges · G11 scale pyramid · G12 nucleation) in the paper aesthetic.
- **Live spine** — `/api/stream` SSE, gapless reconnect (`Last-Event-ID`), the moving present.
- **Multipurpose strata** — greeting / inbox / builder / forager / panels / settings / self-change-log /
  capabilities, re-homed as strata of one shell, sharing language + motion + the address spine.
- **The project system (L13)** — build on the existing `lineage.project` dimension (company = starter project);
  a project = registries + spaces + bindings + addressing over a data source; the surface is pointable at anything.
- **Embed registry definitions (L14)** — via the company MCP, so the symbolic registries become nucleable (the
  previously-deferred gap, now in-scope).
- **Registry-promotion gesture (L15)** — candidate bloom → proposal (reuse `/api/registry/proposals` +
  MCP `propose_role`/`edit_role`/`delete_role`) → on-accept the wheel re-divides live. Instrument stays pure-read;
  the OPERATOR acts through the proposal→approval→execution lifecycle.

*This truth table drives the build loop. Green = verified by use, both faces, all three form factors. No ceiling.*
