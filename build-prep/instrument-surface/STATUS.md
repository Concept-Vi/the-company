# INSTRUMENT SURFACE — STATUS (handoff)

**Assume more work.** This is the FIRST vertical slice of the fresh front end — real and verified, but the
mandate (MANDATE.md) is large and mostly ahead (PHASE-2). Nothing here is "the product done."

## What exists now (committed to main: `d077478`, `7a0b901`)

A fresh **React 18 + Vite 6 + Framer Motion** app at **`surface/app`**, built ALONGSIDE `canvas/app` (the live
PWA on :5173 is untouched). It renders the **instrument WHEEL** lens over the Company's real data, in the fresh
**paper aesthetic**, fully animated, native at three form factors, on the inherited **address+context spine**.

### How to run it
```
cd ~/company/surface/app && npm install && npm run dev      # serves :5174 (or next free port; was :5175 in test)
```
Needs the bridge on :8770 (already managed). Proxy `/api`→:8770. Tailscale allowedHosts set (phone reachable).
NOTE: `surface/app` is UNMANAGED like `canvas/app` — a future ops/services.json row could manage it.

### What's built & verified by use (see COMPLETION-CRITERIA.md → SLICE-1 VERIFICATION LOG)
- Paper token system (`src/tokens/paper.css`) — warm grounds, soft elevation, muted pigment, 1.25 type, dyadic spacing.
- Single motion system (`src/tokens/motion.ts`) — springs + eased; **rAF-proven tween (2.4→5.56), no teleport**.
- The wheel (`src/wheel/Wheel.tsx`) — seed geometry (m/2 rings, x=2π/n sectors), 600 real pts, angle-hue,
  decorative animated layer + invisible r=15 **touch hit layer**.
- **G10 connections re-homed** — `proj.edges` rendered as **directed chords** (source dot + arrowhead; bidir =
  arrowheads both ends = a real cycle). Verified on the `by_node_type` lens: 49 real directional edges + 16
  registry sectors render at 1440×900 AND 390×844. Registry-true, token-only. (`34fd496`)
- **G9 two-gravity separator re-homed** — `src/wheel/Separator.tsx`, chosen by `radius_from==='separator'`. Two
  basins (pole A left / pole B right, distance = |lean|), the fifth-gate verdict + diverging balance bar
  (47/115) + real pole labels; point-select shows the point's lean. Verified at both viewports, console clean.
  (`e128f9b`)
- Address spine (`src/lib/address.ts`) — **615 `data-ui-ref` nodes**, capture listener, single `resolveUiTarget`
  sink, `/api/context` R2 resolution (ancestor walk works).
- Three authored layouts (`src/layouts/`) — desktop / portrait (bottom-sheet) / landscape (rail); design-critic PASS.
- Disclosure (`src/wheel/Disclosure.tsx`) — peek→open, real summary+context, word-boundary excerpts.
- Taste toggles (`src/toggles/Settings.tsx` gear → `Taste.tsx`) — typeface/pigment/motion, flip live.
- Lens chip (`src/toggles/LensChip.tsx`) — registry-true (reads `bindings[]`), collapsed→menu on demand.

## OPEN — needs Tim (S5.4)
The §8 taste calls are decided by **his reaction to renders**, not by spec. Surfaced: typeface (Source/Crimson/
Lora), pigment saturation (Muted/Soft/Present), motion feel (Spring/Eased) — all flippable via the gear. Also
open: paper-light only vs a later "dusk paper"; shell topology; the second seed axis.

## NEXT (PHASE-2 — sequenced, not parked; see CRITERIA §PHASE-2)
Re-home all 12 lenses · live SSE spine (`/api/stream`) · multipurpose strata (greeting/inbox/builder/forager/
panels/settings/self-change-log) · the **project system** on `lineage.project` (company = starter) · embed
registry definitions via the company MCP (nucleable symbolic registries) · the **registry-promotion gesture**
(candidate→proposal via `/api/registry/proposals` + MCP `propose_role`; instrument stays pure-read).
Plus the critic's non-blocking polish (compose the HOWTO block, selection tether, gutters).

## RETURNING TO THE EQUATION (Tim, 2026-06-14 11:05) — the dual, and types-as-gravity
Tim: the surface had only the CIRCLE (meaning); "the grid hasn't been built — that's half of the equation,"
and "the types/divisions of the circle [should be built in] so the data points close around the types."
- **THE GRID (square/structure half) — BUILT** (`b9ec38d`). A ○/◻ ViewToggle switches the seed's two coordinate
  systems over one space (§2): ○ circle = meaning (wheel/lenses), ◻ square = structure (the dyadic nested grid +
  axes + concentric circles + coincidence spine + forbidden corner-circle; points at their real address cells).
  `src/wheel/Grid.tsx`. The dual the equation demands is now both-visible.
- **TYPE-GRAVITY (Ask 1) — BUILT** (`9909d55`). `src/wheel/Nucleation.tsx`, chosen by radius_from==='nucleation'.
  Each registry TYPE is an angular division (sector); items cluster INSIDE their best-fit type (the membership
  boundary circle) — "close around their types"; misfits pile OUTSIDE in the forbidden ring; a distinct pile
  blooms as a candidate new type (✦), BORN past the 20/80 dial (live, client-side). Defaults to a populating
  same-space drive (topics:topics → 149/162 inside); items/types/rung pickers drive the engine (registry-true);
  cross-instance proof one pick away. Verified both viewports, console clean. Design-critic PASS ("most
  conceptually expressive lens in the set"); its #1 fix done — the BIRTH (born ✦ green bloom) is now visible
  on the plate, placed at the pile's true angle (`89a190e`).
  · NOTE for Tim: this reuses the nucleation engine (G12) — it IS "types as divisions, points close around them."
    If you pictured something other than the inside-cluster/outside-pile reading, this is the place to redirect.
- **RELATIVE CENTRE (seed §8) — BUILT** (`8b74e86`). "Centre here" (⊙) in the disclosure re-centres the space on
  the attended item; every lens refetches with center=<ref> and re-projects (no teleport); a CentreChip shows
  the centre + returns to root. Makes the semantic lens meaningful (was all-rim) and — key — the engine now
  returns r_struct + strain per point, unlocking strain. Fixed the n=1 degenerate wedge. Verified both viewports.
- **STRAIN (G7) — BUILT** (`de468f8`). In the semantic+centred state each point draws a radial segment from its
  FILED radius (r_struct, an open tick) to its MEANS radius (r, the dot); length+opacity = structure↔meaning
  divergence (the forbidden tension); coherent points have ~no segment. The central tension, visible. Both viewports.
  Design-critic PASS ("most conceptually loaded view in the set… an elegant tension field, the density earns its
  meaning"); its #1 (longest segments reading as axes near the hub) softened (`cap`). Remaining polish: make strain
  SIGNED (which way it pulls), de-knot the densest zone, selection tether.
- **LEGEND + THREE-WAY VIEW — BUILT** (`3c0dac7`, answering Tim 2026-06-14 12:44 + 12:51). (a) A per-lens LEGEND
  (`Legend.tsx`) now orients every lens — name + "N sectors · angle = …" + "radius · …" + centre, derived from
  the binding (the fix for "I don't know what it is or what it chose"). (b) The view is a THREE-WAY toggle —
  **Both | Circle | Square** — default **Both = the circle INSCRIBED in the square** (the heart of the equation:
  outer square + dyadic grid framing the inscribed wheel + rings + forbidden corner-circle), so the grid is
  present from the start; Circle isolates meaning, Square isolates structure. Geometry corrected: square is the
  OUTER frame (half-side R), circle touches its edge midpoints. Both viewports, console clean.
- **"WHAT IT CHOSE" — BUILT** (`65a3b58`). Closes the second half of Tim's 12:44 note. The legend says what the
  lens IS; now selecting a point narrates WHY it's there — a per-lens placement readout in the disclosure
  (`in · <division>` + radius-meaning: semantic→meaning+tension, separator→leans pole/strength, nucleation→fits
  inside (val) / misfit→piled→new type, time→age), derived from the binding. Verified: raw → "in corpus.record ·
  age long ago (1.00)"; nucleation → "in worldview.py · fits inside (0.90)".
- **THE LIVE SPINE — BUILT** (`bae90c3`). The surface is no longer static snapshots: it tails `/api/stream`
  (SSE) from the newest seq; new events throttle-pulse a re-fetch so the present moves (new points bloom in, no
  teleport). A pulsing LiveDot (top-right) shows live; tap to freeze/resume; gapless reconnect (Last-Event-ID).
  Verified BY USE: emitting one real event (an annotation) triggered live re-fetches with no UI interaction (4
  projection requests, 1 open stream). (A static design-critic can't see live motion — verification is by use.)
- **GROUP 10 DRIVE-TO-EXPLORE — BUILT** (`a8fe9b8`). The connection web is now INTERACTIVE (the cron's #1, was
  static): tap a sector → its OUT edges (it feeds) glow gold w/ arrowheads, IN edges ink, the rest fade; a
  readout names the sector + degree (N out · M in). Tap again / lens-switch clears. Registry-true, pure read,
  no forced order. Verified both viewports (codebase → 6 out · 0 in), console clean. Design-critic PASS ("the
  single best interactive move in the set"); fixes applied — soft tint selection (no hard box), stronger
  arrowheads (direction seen), and 0-in/0-out told as a finding ("pure source" / "pure sink") (`ae675dc`).
- **FORBIDDEN (§10) — SKIPPED this fire (data-thin, honest):** of the 3 kinds, only the CORNER (max strain, 23
  pts) has data; DRIFT (square-without-circle = r_unknown) = 0 in the embedded spaces; GATE-INBOX (circle-
  without-square = un-addressed orphans) isn't in the projection (needs the residue source). Building it now
  would be 1-of-3 + a re-display of strain = half-done. Revisit when an unembedded/orphan data source is wired.
- **GROUP 9 POLE-PICKER — BUILT** (`e3770d8`). The two gravities are now VARIABLES: in the separator lens a
  selected item offers "set as pole A / pole B" (parallel to "centre here"); both set → re-project between the
  two chosen items; "↺ default poles" resets. Verified both viewports: picked AGENTS.md vs repo.py → separates,
  134/28; design-critic PASS ('a drivable instrument where the operator names both gravities'), its #1 fixed (pole labels on paper chips, clear of points). Pure read, registry-true. → BOTH cron targets (G10 drive-to-explore + G9 drivable poles) now
  interactively complete in the surface.
- **Project-scoping checked (L13):** /api/projection does NOT scope by project, and only "company" has
  substantive data (3037 records; "cognition-engine" has 1). The project system is thus data-thin + needs an
  engine scoping pass — deferred until a real second project's data exists (Tim's MCP make-data, or it accrues).
- **GROUP 3 TIME SCRUBBER — BUILT** (`79f56ac`). A slim bottom bar slides the temporal centre into the past
  (?at=); the instrument re-projects only ts≤then (count/sectors shrink); far-right = the live present; past
  pauses the live forward-pull; "now" returns to live. Verified both viewports (Jun 3 → 48 pts/4 sectors;
  Jun 5 → 339; now → 600). The complement to the live spine. Pure read. Design-critic PASS ('the media-scrubber idiom makes drive-time intuitive; time joins centre and poles as a driven variable'); #1 fixed — past-state now reads pre-attentively (accent border+wash+glyph).
- **FIX (`bdefb7a`):** points were keyed by address, but addresses recur (many events at one ui:// address,
  e.g. chat turns at ui://chrome/chat) → 784 duplicate-key React warnings once such events entered the
  projection. Now every point layer keys + layoutId by p.seq (unique/stable); data-ui-ref stays the address.
- **GROUP 11 MULTI-SCALE PYRAMID — BUILT** (`b19ef8f`, `343ffa3`, `4043cb0`, `9f5f6c3`, `797825e`). The semantic
  lens now has a **rung ladder** (units · 32 · 8): step the meaning-field between every unit (162) and coarser
  WARD theme-centroids (?rung=, pure read). Blob size = cluster membership; radius = meaning-distance. KEY FIX
  (the heart of Tim's "I don't know what it CHOSE"): at the coarse rung each theme **names itself** at a glance —
  its exemplar's leaf (scheduler.py, README.md, recall.py, registry.py, …) sits under the blob, capped to a
  legible count (denser rungs stay name-on-click via the disclosure, which also narrates 'cluster of N · e.g.
  <exemplar>'). So the most-summary view in the instrument says WHAT it chose, not only that there are 8.
  Design-critic: cold pass FAILed 3 mechanical points (portrait top-bar clip, centre occluded, rung unnamed) —
  all fixed (`343ffa3`); then a 2nd cold pass FAILed 2 Product-Face points and the re-judge PASSed after fixes:
  (1) the time-scrubber filled its track with the lone COOL hue (plum --pig-accent) → now ink (--ink-dim, joins
  the control family; PAST state warms to ochre) — verified warm RGB(92,83,74) both viewports; (2) portrait
  dead-band (pill orphaned above a low circle) → wheel region is a centred square + the {legend+wheel} plate
  centres evenly in the visible region (measured 104/113px ≈ 0.92:1, was 2.27:1). Circle is at its geometric max
  (width-bound: the forbidden corner-circle r·√2 must fit the width). Verified both viewports, console clean.
- **LENS RE-HOMING COMPLETE:** all 12 seed groups are now in the surface (G2 grid · G3 scrubber · G4 live SSE ·
  G5 form · G6 semantic circle · G7 strain · G8 substrate implicit · G9 two-gravity poles · G10 directional edges ·
  G11 scale pyramid · G12 type-nucleation). The seed's FORMS are all expressed; what remains is DEPTH of the
  equation's descriptions (audit below) + the keystone + data-thin lenses.
## RETURNING TO THE EQUATION — the descriptions audit (Tim 2026-06-14: "for ALL of its descriptions")
The 12 lens FORMS are all present; the frontier is the equation's DESCRIPTIONS. Full audit (seed §-by-§ vs the
live surface) lives in **EQUATION-AUDIT.md** — the gap-list that drives the next fires. First gap built:
- **COINCIDENCE SPINE — BUILT** (`ce04fcf`). The seed's central tension (§3): rings pass through the axial grid
  points, and those coincidence points = the ratified/addressable spine; off-axis the systems never agree (the
  forbidden translation-loss). Geometry was already right (engine emits rings=grid/2, verified) but UNMARKED —
  so the most central claim was invisible. Now ink diamonds (rotated square on the circle = structure∧meaning)
  mark each ring∧axis crossing in Both view; legend names it. Both viewports, console clean.

## TIM'S DIRECTION (2026-06-15) — "all three": keystone + engine beats + surface polish
Asked where the loop should go now the grounded surface-only frontier is narrowing, Tim chose THREE of four
(NOT "call it done"): **(1) DO THE KEYSTONE — the model-load is GREENLIT** (his explicit consent satisfies
`consult-before-model-loads`; embedder default = pplx-embed-context-4b per the embedding-model decision; load via
the `company` CLI, fail loud); **(2) GREENLIGHT THE ENGINE BEATS** — extend the engine (still pure-read instrument)
for composable axes (#3) + wire find_relations→typed edges (#4, the relation_types "next pass"); **(3) KEEP
POLISHING THE SURFACE** (tether, densification, wheel framing). So nothing is parked — all three lanes are live.
Suggested order by dependency: L14 (embed registry defs — the model-load data-build) unblocks the L15 keystone;
the engine beats + surface polish are independent. Each is one big beat per fire.

- **NEXT BEATS (re-sequenced by GROUNDEDNESS — the gate work below proved several audit gaps are blocked):**
  1. ✅ done — audit + gap #1 coincidence spine (`ce04fcf`).
  2. ✅ done — gap #2 CORNER reading: residue → grow the box (`ec1ba61`); design-critic FAIL→fixed→**PASS**.
  3. ✅ done — strain is now SIGNED (warm = meaning farther · cool = nearer; seed §3) (`615b66a`, `440fc7d`);
     critic resolved the cool-tips-cold worry (NO); residual = pre-existing portrait core density (carry-over).
  4. **NEXT (grounded, buildable): selection tether** — a line from the selected point to its detail card, on
     ALL lenses (grounded in selection state; the broadest legibility gain, critic-noted).
  5. **BLOCKED → surface to Tim (engine work, not counterfeit):**
     · audit #3 *axes as variables* — the cosmetic relabel is green-paint (the legend already names the axes;
       the lens menu already switches them). The SUBSTANTIVE form = COMPOSABLE axes (fill angle vs radius vs
       centre vs n independently) needs engine support the bindings lack (they're fixed pairings). An engine beat.
     · audit #4 *edges as canonical moves* — the projection's edges are bare from→to, ALL one kind ("feeds");
       the typed relations (`relation_types`: depends_on/precedes/contradicts/…) are declared but NOT instantiated
       (`runtime/relation_types.py`: "the SUITE lane wires find_relations to label edges … that is the next pass").
       No move-type data to render → building it now = inventing the mapping. Needs the find_relations↔relation_types
       wiring first (an engine beat; also the cron's own "cascade precedes / relation_types" edge sources).
  6. **Registry-promotion keystone (L15)** — BLOCKED on L14 (embed registry defs) = a model-load → explicit Tim ASK.
  7. Resonance law (#5, subtle/green-paint-risk), forbidden all-3-kinds (§10), project system (L13) — data-thin.
  8. Other carry-over polish: strain portrait-density densification; desktop wheel floats in empty canvas; de-knot.
- Note: a test annotation ("live-spine verification ping") was written to `ui://instrument/wheel` during live
  verification — benign, append-only; harmless real comment.

## DESIGN-CRITIC — both new lenses PASS (2026-06-14)
"Connections" (G10) = beautiful string-art-on-paper; "Two gravities" (G9) = the most instantly-legible data
claim in the set. Neither reads as prototype. Fix #1 (G9 card↔pole-label overlap) DONE (`d24181f`).
Remaining non-blocking polish, sequenced (not parked): G10 de-muddy the central chord knot (inner-radius gap /
lower opacity at hub); G9 tighten the central basin gutter; selection tethers (point→card) on all lenses; G9
portrait balance the pole-label wrapping; G10 unify the ~9 o'clock sector marker; G10 a subtle "0 by design" cue.
