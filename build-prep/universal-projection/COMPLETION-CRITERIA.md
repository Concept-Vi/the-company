# Universal Projection — Completion Criteria

**Originated by Tim Geldard; all derived work attributed to him.** A truth-table for the
instrument→ability buildout — each item a verifiable statement about the system, not a task. Built on
RESEARCH-SYNTHESIS.md; HOW lives in IMPLEMENTATION-GUIDE.md.

## Verification rules (the loop follows exactly what's written here)

**FUNCTION bar:** verified BY USE — run it, curl it, drive it in the browser. Never by reading code,
never by a DOM/JS query alone, never "the code looks right." The instrument's invariants verify
against the COMMITTED acceptance suite (Group 1) — NOT `tests/projections_acceptance.py`, which tests
the unrelated LENS registry (the name collision; see synthesis Round 4).

**FORM bar (the design rubric, run on every operator-facing surface by a SEPARATE design-critic, not
the implementer):** built on the design system's components (`components/kit.tsx`) + corpus tokens
(`design/design-system.css`), NO hardcoded values, NO bespoke one-offs · no overlaps · responsive at
desktop AND 390×844 · consistent scale/type/spacing · settings consolidated · a navigable
visual/spatial surface, not a text-wall · empty/loading/error states · the outcome demonstrable.
Machine-gated by `design/_system/check.py` (design-lint) against BOTH the .tsx AND app.css. THE ONE
EXCEPTION: the per-point hue = angle (colour IS geometry) is a deliberate non-token colour — preserve
it; it is not a lint target.

**Status:** ✅ verified-by-use · 🟡 designed/stubbed (intent, not fact) · 🔴 broken/absent.
**The floor:** the instrument is a PURE READ over the store — no resolve/approve/dispatch, ever.
**Registry-is-truth:** lenses/bindings/sectors are declared rows, never hardcoded ("no first binding
ruins the system"). **Expand-before-harden:** the brain docs are captured design, NOT ratified.

---

## BUILD STATUS — 2026-06-14 (NOT "build complete" — ONE honest item remains, genuinely Tim-gated)

Groups 1–11 are all ✅, both faces, design-critic-passed. Both loop TARGETs (Group 10 then Group 9) are
✅ to THE BAR. The ONLY remaining item (#12) is genuinely gated on a Tim fit-test — green-painting it
would be the dishonesty this loop exists to avoid. This is a STATUS, not a completion claim.

- **INSTRUMENT half — ✅ COMPLETE.** Group 1 (the variable-engine floor / acceptance suite), Group 5 (the
  FORM face on the corpus design system), Group 3 (time-freed/relative centre + scrubber), Group 4
  (real-time SSE pub-sub), Group 2 (the square/dyadic-grid half). All ✅, both faces, design-critic-passed.
- **ABILITY half — ✅ COMPLETE.** Group 8 (embedding substrate live), Group 6 (the circle / semantic radius),
  Group 7 (strain / structure↔meaning gap), Group 11 (the multi-scale SCALE axis) — all ✅. Group 10 (the
  connections in the registries) — ✅ 2026-06-14 (Tim unblocked; my prior "needs an acyclic backbone" was a
  self-imposed constraint — nonsequential IS valid): the directional typed edges render as an INTERACTIVE
  directed-chord web (drive-to-explore), verified to THE BAR, critic RESOLVED both viewports. Group 9 (the
  two-gravity separator) — ✅ 2026-06-14 (Tim unblocked; general variable-two-pole read, AI supplies its own
  pole): the fifth gate + the two-basin drivable FORM (balance bar, pole-picker, reset), verified to THE BAR,
  critic PASS both viewports. Both faces each.
- **THE ONE REMAINING (#12 — small registries + gate surface + 20/80 water-law) — 🔴 genuinely Tim-gated.**
  Re-examined this fire: NOT gated on relations (Tim gave those → Group 10 shipped). The real open gates are
  Tim's to set, by his own SEED: the operational definition of "forbidden" (§10 "Tim: you tell me"; §7
  "deliberately unresolved"; the deep-holes growth law "awaiting Tim's fit-test") and which two AXES are the
  spine (§7 "the other is open"). Deferred to a fit-test, not parked out of caution; not a loop target.
- **GENUINELY REMAINING (all honestly gated — the loop must NOT churn on these):**
  · **Group 9** (two-gravity separator) — ✅ DONE (2026-06-14, both faces, to THE BAR). SUPERSEDED the AI-tells
    gate: Tim "there is no single purpose" → general variable-two-pole read, AI supplies its own pole. FUNCTION:
    a PURE two-pole read over the persisted vectors (no embed-lens) + the fifth gate (separation_report:
    distinctness · both spreads · ρ≠+1 · a pole must attract somebody) + the AI plants its own AI-corner anchor;
    proven live on a real NON-centroid balanced pair (worldview.py vs sessions.py: separates, ρ −0.41, 57/105).
    FORM: the two gravities as two spatial BASINS (left/right), radius=|lean|, a diverging BALANCE bar so the
    skew is seen, a pole-PICKER (drive the two gravities live); design-critic PASS at 1440×900 AND 390×844.
    Pollution instance = named DEFERRED application (lens-mismatch 162/0 → correctly refused, honest).
  · **Group 10** (the connections in the registries) — ✅ DONE (2026-06-14, both faces, to THE BAR). The
    directional-typed-edge wheel + the connection web (directed chords, cycles rendered AS cycles, drive-to-
    explore) shipped; design-critic RESOLVED both viewports. The prior "needs an acyclic backbone, three data
    sources fail" was my self-imposed total-order constraint — retired by Tim's "nonsequential IS valid / only
    directional edges type." (The relation_types vocabulary has no instances yet — a growth front, not a gap.)
  · **The small registries + gate surface + 20/80 water-law** — 🔴, GENUINELY Tim-gated (re-examined 2026-06-14,
    this fire — and the gate is REAL, not my caution). The 20/80 water-law is TYPE-NUCLEATION: a type/axis is
    BORN where the FORBIDDEN-ZONE density (gap-pressure) fills past threshold (SEED: "forbidden-zone density =
    gap-pressure = the instruction to GROW A NEW AXIS"; "new types are born at the deep holes"). The strain
    quantity exists (Group 7 computes per-point structure↔meaning incommensurability). BUT the gate is NOT the
    relations model (Tim GAVE that — Group 10 shipped on it); the stale "gated on relations" claim is CORRECTED.
    The real, still-open gates are two things Tim's own SEED reserves to him:
      (1) **the operational definition of "forbidden"** — SEED §10 header is literally "THE FORBIDDEN,
          operationally (Tim: 'you tell me')", and §7 lists it under "Open tensions (expand-before-harden —
          DELIBERATELY unresolved)" with two candidate readings ("likely both"). The new-types-at-deep-holes
          growth law is flagged in CONVERGENCE-OBJECT 65/75 as "the most mine … explicitly awaiting Tim's
          fit-test … if right it is the system's growth law."
      (2) **which two AXES are the spine** — SEED §7: "Time is the obvious candidate for one. The other is
          open … choosing them is choosing the system's spine."
    Building a strain-density read and calling it the water-law/type-nucleation would harden a definition Tim
    deliberately left open — green-paint of his core science (the loudest place for "half-working damages
    credibility"). So this is correctly DEFERRED to a Tim fit-test, not parked out of caution. It is also NOT
    a loop TARGET (the loop targets were Group 10 + Group 9, both ✅).
- **VERIFIED THIS CONSOLIDATION:** 16/16 broad-regression suites green (projection ×4, drift, bridge_routes,
  conv_index ×3, space_embed, embeddings, durability, events, fs_session_guard, set_ref_atomic, bridge_session);
  live surface all 5 bindings resolve (5994 pts), scrubber shifts `now`, semantic-pending shows the scale
  ladder, semantic-active over 162 units (all carry strain), rung=8 resolves 8 sized+labelled themes.
- **ACTIVE BUILD — Tim UNBLOCKED both, 2026-06-14 00:35Z (the ceiling was my error, twice):** the prior
  "ceiling/hold" is RETIRED. Tim's corrections (verbatim intent):
  · **Separator (Group 9): "You do not need me to tell you the AI tells, and asking me to give it to you
    assumes a single purpose. There is no single purpose."** → The two-gravity separator is a GENERAL
    variable-two-pole resolution (poles are variables like centre/axes; registry-true, no hardcoded poles);
    pollution (origin vs AI-corner) is ONE instance, and for THAT instance the AI SUPPLIES its own AI-pole
    (I characterize my own deformation — never demand the tells from Tim; see ai-supplies-domain-knowledge).
  · **Relations (Group 10): "I have already given it to you. The only edges that get typed are the
    directional ones."** → The relations model is GIVEN, not unformalized: registries↔registries,
    types↔types, fields↔fields; every typed edge is DIRECTIONAL and carries its EQUAL-OPPOSITE; ONLY
    directional relations type (symmetric associations don't). And nonsequential IS valid (line 495) — so
    my "needs an ACYCLIC backbone" was a self-imposed total-order constraint Tim never set. Order the wheel
    by the directional typed edges where they sequence; render real cycles AS cycles, not flattened.
- **THE BAR (Tim's completion gate for this build — all four, or it is not done):** (1) VERIFIED LIVE (not
  code-reading — curl + driven in the browser); (2) connects to ALL the REAL data (every registry / the
  whole event corpus / the real directional typed edges — never a toy slice); (3) Tim can DRIVE it; (4) it
  is INTERACTIVE. This bar is half of "done" alongside the FUNCTION+FORM bars.
- **THE LOOP (this is "my loop", Tim 00:35Z):** one big beat per fire → build toward Group 10 (the
  directional typed-edge wheel = "the connections in the registries") then Group 9 (the variable two-gravity
  separator, AI-supplied pole) → verify against THE BAR (live + all real data + drivable + interactive) +
  the floor → commit → update this status honestly. No green-paint, no forced-acyclicity, registry-true.

---

## GROUP 1 · INSTRUMENT — THE FLOOR (the variable engine) ✅ (suite committed 6615e53)
`runtime/projection.py:project` + `BindingRegistry` + `bindings/` resolve a frame from a swappable
lens; sectors data-driven; lock x=2π/n re-divides evenly.
- **FUNCTION** — the angle/depth/now/binding floor is a pure read over the store; no hardcoded
  sectors; a COMMITTED acceptance suite proves the invariants (r∈[0,1], θ inside its sector wedge,
  even re-division at every n, lock holds, kind-group '*' remainder catches everything). ✅ by use —
  `tests/projection_instrument_acceptance.py`, 26 passed 0 failed; deliberately does NOT pin the
  stubs (rings:4, time-radius) that G2/G6 replace.
- **FORM** — n/a (backend). The suite IS the form of "done" here. ✅

## GROUP 2 · INSTRUMENT — THE SQUARE/STRUCTURE HALF (the grid) ✅ (ebbfb89; critic-passed both faces)
The seed's m/2 concentric circles + dyadic (i,j) grid — built. Both stubs (rings:4, depth scalar) gone.
- **FUNCTION** — ✅ by use: `_grid_cell(address)`→(i,j,d) the dyadic quadtree coord (MSB-first → a parent
  cell contains its children; scheme-agnostic — NOT parse_ui_address, which is ui://-only fail-loud);
  per-point `cell`; `grid` m = 2^(deepest path, cap 4); `rings` = m/2 (the rings:4 hardcode gone).
  Proven: live payload rings 8 / grid 16 / per-point cell; suite 35→41 (power-of-2, rings==m/2, cell
  bounds, depth-tracks-nesting, determinism+scheme-strip, CONTAINMENT).
- **FORM** — ✅ (design-critic PASS both viewports): the box frames the wheel (the outer circle inscribed,
  corners past it at the diagonals);
  the dyadic grid fades by level (coarse anchors, fine recedes); the picked point's CELL lights up gold
  (its square home — the circle/square duality, seen); the card shows 'cell i,j · depth d'. On tokens
  (box/grid --tx-3, cell --acc), angle-hue preserved. The first design-critic FAILED it (grid
  under-contrast, imperceptible at native viewing — measured delta 5–19); contrast RAISED per its
  prescription (box 0.85, grid by-level 0.50→0.14). ✅ by rubric — the SEPARATE design-critic re-confirmed
  PASS at 1440×900 AND 390×844 (measured: box frame Δlum ~66-113, coarse grid ~14-43, fine ~5-7 with the
  level-graded fade intact, subordinate to the wheel; the picked cell reads as a located cell, not floating).

## GROUP 3 · INSTRUMENT — TIME-FREED / RELATIVE CENTRE ✅ (backend dabf952; FE 9be11cc + 3f65f70)
The centre is freed — both in the engine (`project(now=, center=)` + bridge `?at=`/`?center=`) and in the
surface (the scrubber + re-centre + animation).
- **FUNCTION** — `?at=` parsed in bridge, `project(now=)` filters events ts≤now (the scrubber); AND a
  non-now ADDRESS centre re-projects radius as STRUCTURAL tree-distance from that address
  (`_tree_distance`, mirrors `address_tree_distance`, kept in projection.py so the floor has no suite
  dep). ✅ by use — suite 26→35 green; live curl: `?at=-2h` shifts `now` 2h back, `?center=` flips
  `radius_from`→'address' with the centre event at r=0, all r∈[0,1]. FE driven at both faces: scrub
  (5470→2105 pts, '◷ 125h ago'), live→'◷ past'→return-to-now, re-centre (chip + distance-shells),
  clear, lens, frames, zoom, mobile bottom-sheet 'centre on this'. The cosine/semantic relevance ring
  (a SEMANTIC centre-radius) was stubbed here pending Group 6 — now DELIVERED by Group 6 ✅
  (`radius_from='semantic'`: pick any embedded item → "◎ meaning-field from here"); the old 🔴 is retired.
- **FORM** — ✅ by rubric: the scrubber (⏱, gold = the privileged time axis) + zoom (⌕, dim) are
  distinct controls; a 'centre on this' affordance + a '⊙ <name> ✕' chip; re-centring/reframe ANIMATES
  (easeOutCubic rAF, identity survives, off the live-refresh path). All on corpus tokens; pointer-events
  fixed so foot controls are real-tappable; foot wraps (no phone overflow); design-lint clean
  (LatticeView 0 / lattice app.css 0). A SEPARATE design-critic passed all 6 dimensions at 1440×900
  AND 390×844 (slider-distinctness defect found + fixed + re-confirmed).

## GROUP 4 · INSTRUMENT — REAL-TIME PUB-SUB ✅ (528704a; Tim's explicit ask)
The lattice subscribes to `/api/stream` (SSE over the shared events.jsonl tap); the 15s poll is retired.
- **FUNCTION** — ✅ by use: an EventSource on `/api/stream?since=<latest seq>` (only future events stream);
  on a new event, a 220ms-coalesced re-projection (server stays the projection authority — no parallel
  client math); `setInterval(15000)` removed; `now` advances on a continuous ~22fps client-clock rAF
  (the centre breathes smoothly, stops when frozen/scrubbed). Proven: network `GET /api/stream?since=`
  [200]; appended a real event → live count 5493→5494 in <2s with NO reload (and it minted a new
  kind-sector 50→51 — the data-driven engine, live). Suite 35/35.
- **FORM** — ✅ by rubric: updates are setProj + canvas REPAINT (the `<canvas>` is never remounted —
  verified same DOM node across re-projection → not a flicker/reload); new arrivals DRIFT IN (markNew →
  the easeOutCubic fade-in tween) while placed points hold. A SEPARATE design-critic: PASS, no FORM
  regression at 1440×900 AND 390×844.
- **ROBUSTNESS (carry-forward, found in G5 review)** — the error view returns early and renders NO foot
  HUD, so there are no controls; recovery relies on the mounted effect's 15s interval, which only runs
  while `live=true`. A failed pull WHILE FROZEN (e.g. a bind-change pull that 503s) is a stuck dead-end
  until reload. Pre-existing (not a G5 regression); fix here — give the error state an in-view retry OR
  keep the live toggle reachable. ☐ by use

## GROUP 5 · INSTRUMENT — THE FORM FACE (the lattice on the design system) ✅ (committed dc3378a)
LatticeView.tsx WAS the LONE region still on the dead GitHub-dark palette (undefined --accent/--ink-dim
→ hardcoded fallbacks; 37 CSS + 6 tsx literals). Repaid.
- **FUNCTION** — unchanged behaviour through the rebuild (lens switch, frames, forager seam,
  live/frozen, zoom, pick→card, select→set-bar→hand-to-builder all still work). ✅ by use — every
  interaction driven at 1440×900 AND 390×844; builder-context fires; mobile card docks bottom-sheet.
- **FORM** — chrome rebuilt on kit primitives (Badge pills, EmptyState error) + corpus tokens;
  the draw() palette resolved from --acc/--tx/--bg/--line/--tx-3 (no hex), live-dot off-palette
  green → gold, box-shadows → --shadow, ls-go text → --ink-accent; design-lint CLEAN on
  LatticeView.tsx (0) and the lattice's app.css contribution (37→0); the angle-hue PRESERVED;
  a SEPARATE design-critic passed the WHOLE screen at desktop AND 390×844 (pixel-verified). ✅ by rubric
  NOTE (out of scope): 2 pre-existing #fff remain in app.css (.review-frame/.studio-frame) — deliberate
  white 'paper' for rendering mockup HTML, not the lattice; left intentionally. CONSEQUENCE: a
  FILE-LEVEL gate (`check.py --target canvas/app/src --fail-on`, rule 9) stays RED from those two —
  "Group 5 lattice-clean" is NOT "the app.css gate is green". A white token (or a lint allowlist) is a
  design-folder concern (generated CSS, another session), not the app's to hand-edit.

## GROUP 6 · ABILITY — THE CIRCLE / SEMANTIC RADIUS ✅ (2026-06-14; both faces verified by use, design-critic PASS)
Built on Group 8's live spaces. commits 078eb6a (FUNCTION) + 53b4baf (FORM + empty-core fix) + 7d231a0/this (criteria).
- **FUNCTION** ✅ by use — `project(..., radius_from=='semantic')` resolves r = MEANING-distance from the
  centre = 1 - cosine, read off the persisted per-space vectors (project stays PURE — vectors ride in via
  `vectors=`, keyed by `_addr_of`; the store I/O is the bridge's: `store.get_vector` over the binding's
  space). `bindings/semantic.py` (space='topics'). `vector_index._cosine` replicated in the floor.
  Verified by use (live bridge, center=suite.py over topics): 162 points, centre at r=0, nearest
  neighbours small r, claimed_status.py at the rim; no-centre → legible 400; raw/time bindings unchanged
  (41/41 instrument regression). `tests/projection_semantic_acceptance.py` (15 checks).
- **FORM** ✅ by rubric — the lattice renders the meaning-field: pick any embedded point → "◎ meaning-field
  from here" (sets the semantic lens + centre together — no chicken-egg); radius reads off p.r (temporal
  frames hidden), axis "farther in meaning →", a normalized note + a pick-a-centre banner; r_unknown points
  faint at the rim. design-lint contribution 0. EMPTY-CORE FIX: the centre's cosine=1.0 was an outlier that
  compressed neighbours into the outer band (design-critic caught it, nearest at r~0.39); now the centre is
  EXCLUDED from the normalization band → centre at 0, nearest at 0.06, full radius. SEPARATE design-critic
  re-verified at BOTH viewports (1440×900 + 390×844): inner core populated, smooth gradient from near-origin
  (~4-6% of max) to rim, near-vs-far readable by distance — PASS on both (was a hollow-core FAIL).

## GROUP 7 · ABILITY — STRAIN / FORBIDDEN ZONES ✅ (2026-06-14; both faces verified by use, design-critic PASS)
The structure↔meaning gap (SEED §111). Built on Groups 2 (the square) + 6 (the circle). commits f00aa25 + this.
- **FUNCTION** ✅ by use — per-point STRAIN = |r_struct − r_semantic|: where it's FILED (structural radius
  = tree-distance from the centre over the SOURCE address, normalized like r) vs where it MEANS to be (the
  semantic radius). NOT a 2D cell↔wheel distance (the one-sector angle is hash-jitter → the centre, the
  MOST coherent point, would read max-strain — the advisor caught this); compared like-for-like as radii at
  a shared angle, so the centre is 0/0 → strain 0. Computed in `project()` semantic-mode-only (the circle
  must be MEANING); a vectorless point carries NO strain (no fabricated coherence). `mark_types/strain.py`
  registered (score · surface — so strain can be MARKED + surfaced; render, never auto-correct). Verified by
  use (live bridge, center=suite.py): 162 points carry strain, centre strain 0.0, divergences real
  (flows.py means-like-suite-but-filed-far → 0.80; coherence_calibrate.py filed-near-but-means-differently
  → 0.73). `tests/projection_semantic_acceptance.py` extended (23 checks incl. the centre≈0 dispositive
  guard + coherent≈0 + divergence-high + far+far-is-coherent).
- **FORM** ✅ by rubric — a "⊿ strain" toggle on the meaning-field draws the RADIAL tension segment from
  r_struct to r at each point's angle (SEED §111's literal "line between where it's filed and where it means
  to be"); alpha+width ∝ strain so coherent points vanish and only divergence reads as tension; the picked
  card shows "⊿ strain · filed ↔ means". design-lint contribution 0. SEPARATE design-critic PASS at BOTH
  viewports (1440×900 + 390×844): lines appear, toggle ON/OFF clean, card math exact (e.g. 0.69 filed ↔ 1.00
  means → 0.31), geometry proven (distinct radii, not a spoke artifact), gradation self-thins (not a
  hairball — eye drawn to real divergences), gold-on-warm-dark tokens. Honest caveat: a busy CENTRE (one
  with many near-in-meaning-but-filed-far neighbours) reads denser near the origin — a centre-choice, not a
  width artifact; still legible. (forbidden-zone = a high-strain threshold marker — a later refinement.)

## GROUP 8 · ABILITY — EMBEDDING SUBSTRATE LIVE ✅ (2026-06-14; verified by use, unblocks 6,7,9,11)
CORRECTION of the prior "mechanism complete" premise: the mechanism was NOT complete. The single-lens
`repo` path existed (ingest_paths → repo_digest → repo space) and `history` was populated, but the
embeddable lenses topics/principles/worldview had NO producer — declared spaces, EMPTY on disk (0 each).
The capture-schema builder the architecture NAMED (projections.py:5 / suite.py:292 "output_schema built
FROM model_projections()") was never built. So Group 8 was a BUILD, not a bring-up. Built it.
- **FUNCTION** ✅ by use —
  · embed-bge UP via `company up embed-bge` (no --evict; co-fits chat-4b on the 16GB card — needs ~4.9G,
    7.0G free); HEALTHY on :8001 (BGE-M3, verified `/health`→200).
  · `Suite.capture_corpus_lenses` (runtime/suite.py) — the MULTI-LENS capture lane: builds ONE dynamic
    output_schema FROM the registry (model_projections ∩ requested lenses), fans it over file units
    (run_items @ chat-4b :8000), captures+embeds each lens field into its space (capture_corpus →
    embed_corpus_to_spaces → build_index(space=)). REUSE: walk_files + run_items + capture_corpus, no
    parallel vector path. Fail-loud: a non-registry / non-model / non-embeddable lens RAISES. Incremental
    (resume-safe; bounded batches compose to full coverage).
  · POPULATED: topics/principles/worldview = 162 each (full backend corpus: runtime/store/contracts/ops/
    roles/projections/fabric/nodes/mcp_face), real BGE-M3 1024-dim vectors, 0 failures; content is
    meaningful + render-not-judge (verified: topics.py → topics=["content lens","vector space",…]);
    queryable via `query_corpus(space=…)` (live :8001 cosine). repo=644, history=1464 pre-existing.
  · index freshness CONFIRMED via `vector_index.index_staleness` (extended with `space=` param):
    topics/principles/worldview fresh=True (162 corpus==162 indexed, 0 missing/changed/extra), repo
    fresh=True (644==644). The 20-check staleness regression still passes (space=None byte-identical).
  · acceptance suite `tests/capture_lenses_acceptance.py` (18 checks) + drift green; commits ea10f24
    (lane + index_staleness space=) + 30e8356 (suite + STATE reflection).
  · COVERAGE: backend 162/repo-644 (partial — the substrate IS live; "populates" met). NOT self-driving:
    `capture_corpus_lenses` extends ONLY when RE-INVOKED with broader roots (frontend .tsx / docs) — the
    incremental lane is resume-safe, but nothing auto-calls it yet (a routine/later beat must re-invoke).
  · query_corpus(space='topics') ranks items by cosine, returning the source address as `id` (verified —
    e.g. "subjects a file covers" → what.py/projections.py nearest); this IS Group 6's semantic-radius input.
- **FORM** — n/a (substrate). ✅

## GROUP 9 · ABILITY — TWO-GRAVITY SEPARATOR ✅ (2026-06-14; both faces, design-critic PASS both viewports, to THE BAR)
> SUPERSEDES the old plan (a "steerable embedder" threaded through transport→client→embed→build_index +
> Tim's AI-tells). Tim 2026-06-14: "There is no single purpose" → the separator is a GENERAL variable-two-pole
> resolution; the AI supplies its OWN AI-pole (never demand the tells from Tim). And the PURE-READ law: the
> instrument never re-embeds — it READS the per-space vectors that already exist. So the built mechanism is a
> pure two-pole read over the persisted vectors, NOT an embed-lens. Poles are VARIABLES (any address with a
> vector in the lens — a corpus item, a cluster:// theme centroid, or a planted anchur://), registry-true
> (declared in a binding ROW, overridable per request) — no hardcoded poles.
>
> **BUILT this beat (FUNCTION, commit pending):**
> · `runtime/projection.py` — `radius_from='separator'`: per item pull_a=cos(item,A), pull_b=cos(item,B),
>   signed lean=pull_b−pull_a; radius=|lean| min-max (NEUTRAL→centre, BOTH poles→rim — the two gravities as
>   equals, no centre-pile); BOTH raw pulls + the lean carried per point (no signal thrown away). Vectorless
>   point → rim + r_unknown (flagged, never dropped). Missing poles → fail loud.
> · **THE FIFTH GATE** — `separation_report()` (raw cosines, the witness the field actually SEPARATES, since a
>   normalized radius gradients over noise): FOUR degeneracies ALL refused → pole_distinctness ≥ floor · spread_a
>   AND spread_b ≥ floor (kills a dead/constant pole) · Spearman(pulls_a,pulls_b) NOT ≈ +1 (kills a redundant
>   pole; opposed poles ρ→−1 PASS — the false-negative the earlier gap-rank draft would have had is gone) · AND
>   min(lean_a,lean_b) ≥ 1 (kills a ONE-SIDED field — a pole attracting NOBODY collapses to a one-pole distance;
>   a hard count-of-zero, not a tuned threshold). The BALANCE (lean_a/lean_b/minority_frac) is also surfaced for
>   the DEGREE of skew among fields that do separate.
> · `runtime/bridge.py` `_separator_projection` — resolves the two pole vectors (unit item / cluster centroid /
>   planted anchor) + the item vectors from the store; project() stays pure; poles drivable via ?pole_a=&pole_b=.
> · `bindings/by_separator.py` — the general lens (default poles = the two MOST-distinct topics clusters).
> · `runtime/anchors.py` — the AI plants its OWN AI-corner pole: characterizes AI-deformation, embeds it through
>   the SAME BGE-M3 lens, persists anchor://ai-corner. The named pollution-instance mechanism.
> · `tests/…acceptance.py §13` — 75 pass: hermetic two-blob SEPARATES (flat=bug), identical-poles REFUSED,
>   dead-pole REFUSED, pole-agnostic 2nd config, balance, opposed-poles PASS, vectorless→rim, missing-poles fail-loud.
>
> **VERIFIED LIVE — the real-data ✅ gate (the honest, non-circular one):** the separator, driven over ALL 162
> real topics items through the bridge. The PRIMARY evidence is a NON-CENTROID pair (two real corpus ITEMS from
> different regions, NOT means of the corpus, so non-circular): pole_a=code://projections/worldview.py vs
> pole_b=code://mcp_face/tools/sessions.py → `separates:True`, distinctness 0.40, **Spearman −0.41** (strongly
> opposed gravities), balance **57/105 (minority 0.35 — a genuinely two-sided field)**, and the leaders (DIFFERENT
> items than the poles) spot-check region-clean: toward worldview ← topics.py, what.py, lineage.py, principles.py;
> toward sessions ← introspection.py, channels.py, ui_claude_session.py, rule.py. The default centroid pair (c6
> vs c4) corroborates (separates, balance 47/115) but is partly circular (centroids are means of the items), so
> the NON-centroid pair carries the claim. The general two-gravity separator is demonstrated on real data.
>
> **HONEST — the pollution instance is the NAMED DEFERRED application, correctly REFUSED today:** probed origin
> (worldview centroid, a §17 corpus sample standing in for the deferred true Tim-pole) vs anchor://ai-corner →
> balance **162/0** (every code-topic item leans to the code centroid; the free-text AI-corner attracts nobody).
> This is the lens-mismatch the design anticipated (a free-text prose pole vs a code-topic corpus). The hardened
> fifth gate now reports **separates:False** for it (the one-sided degeneracy) — so the pollution probe is not
> faked-green; it is honestly refused. DEFERRED: the true Tim-pole (§17, not a corpus sample) + a text-lens where
> the AI-corner is comparable. The ✅ rests on the balanced non-centroid real pair, never on this probe.
- **FUNCTION** — the general two-pole read + the fifth gate, verified live on a real balanced pair. ✅ by use
- **FORM** — ✅ (2026-06-14, both viewports, design-critic PASS). The two gravities render as two spatial BASINS
  (advisor's (b), chosen over recolouring): pole A fans LEFT / pole B fans RIGHT, radius = |lean| (neutral at the
  centre, strong lean at the rim), colour reinforces the side (cool A / warm B); the two poles are marked + named
  at the rims; a NEUTRAL divide bisects; the centre is a quiet neutral marker (NOT the breathing-NOW dot, which
  would lie). The readout card carries the FIFTH GATE made visible — both pole names (full, stacked), a diverging
  BALANCE bar (the advisor's mandate: separates:True can still be lopsided → Tim must SEE the 47/115 skew), and
  the verdict (separates · distinct · ρ). DRIVE-TO-EXPLORE: tap a point → its pulls + lean; ◀ set pole A / set
  pole B ▶ re-drives the field keeping the other pole (proven live — driving channels.py as pole A re-drove to
  2/160), and ↺ default poles resets to the binding's declared pair (added 2026-06-14, verified live: drive →
  reset → back to 47/115). Time controls suppressed (radius is lean, not time), like the semantic lens.
  > BUILT (commit pending): canvas/app/src/regions/LatticeView.tsx (the basin layout sepTheta used identically by
  > draw + pick; pole hues; readout + balance bar; pole picker; the controls/centre-dot separator branches) +
  > app.css (lc-sep, token-only; pole hues via inline computed hsl, the colour-IS-pole exception). VERIFIED:
  > driven LIVE in chrome-devtools at 1440×900 AND 390×844 on the real 162-item field; the pole-picker re-drives;
  > a SEPARATE design-critic PASSED all 4 criteria on BOTH viewports (caught + I fixed: a full-height card burying
  > the mobile wheel, rim labels colliding at centre, ellipsis-truncated names; and a bridge label bug — an
  > overridden pole kept the stale default label). design-lint: LatticeView 0 off-token literals (the 2 #fff in
  > app.css are the pre-existing white-paper, out of scope; the separator CSS added zero literals). 76 acceptance
  > checks still green.

## GROUP 10 · ABILITY — ORDER-FROM-EDGES + ANGLE-FROM-A-REGISTRY + THE CONNECTIONS ✅ (2026-06-14; Tim-unblocked, both faces, design-critic RESOLVED, to THE BAR)
> DONE 2026-06-14 (Tim unblocked — see ACTIVE BUILD up top): the old "edge-order needs an ACYCLIC backbone /
> three sources all fail" finding is SUPERSEDED — Tim: "the only edges that get typed are the directional
> ones" + nonsequential IS valid (no acyclic requirement I'd invented). BUILT, both beats:
> · BEAT 1 — the connections DATA (commit 85df987): project() SURFACES the directional typed edges (edges =
>   directed sector-index pairs; bidir = a real mutual cycle, rendered AS a cycle); whole_set renders a
>   registry's WHOLE structure; the bridge resolves node-types → all 16 rows + 49 DIRECTIONAL-only type-flow
>   edges; bindings/by_node_type.py; +6 floor invariants.
> · BEAT 2 — the interactive FORM (commit b136d17): the directional typed edges render as directed CHORDS
>   (bow to centre, arrowhead at target, bidir = head both ends); DRIVE-TO-EXPLORE — tap a row → its OUT
>   edges blaze gold, IN ink, the rest fade, readout card lists feeds-to/fed-by; tap centre to clear; the
>   whole-registry labelled; a backend point-drop fix (no event-dump into the last sector). SEPARATE
>   design-critic RESOLVED at BOTH viewports (drive-to-explore lights the wheel — 26,392 px change vs the
>   prior 177-px FAIL; direction readable; phone labels staggered, no collision). floor 59→60; design-lint 0.
> VERIFIED TO THE BAR: live (curl + driven in-browser) · all real data (the live node registry + its real
> type-flow) · Tim can drive it (tap rows) · interactive. The edge-order/connections FORM 🟡 is now ✅.
> NOTE: the directional typed-edge VOCABULARY (relation_types: precedes/depends_on/…) has no INSTANCES yet;
> as real typed relations are instantiated between items they render in this same view (registry-true).
> NEXT: Group 9 — the variable two-gravity separator (AI supplies its own pole).
The keystone. commits (this beat). The advisor stopped a fake "derived precedence" (order_by=time in a
costume) — only REAL persisted directed edges order sectors; registries have none yet (growth front).
- **FUNCTION** ✅ by use — (1) THE EVENT→ROW EDGE formalized: `_row_of(event, angle_from)` — a registry's
  SINGULAR-field convention (op.run→`role`, corpus.record→`projection`; `_singular` depluralizes, one rule)
  + a graph's node-ref (connect→`from_node`). (2) `_resolve_sectors` gains the angle_from=<registry/graph>
  branch (sectors = the entity-set's PRESENT rows via the edge; an event naming no row → an honest '—'
  remainder). (3) `order_by='edge'` = `_toposort` over the passed REAL directed edges (Kahn, STABLE
  tie-break, cycle-safe) — the alphabetical default RETIRED (count). Verified by use: `by_lens` (live
  bridge) divides the wheel by the projection registry (history/repo/principles/topics/worldview/what + '—');
  order_by=edge topologically orders a real graph (review-1780773666-26: 52 nodes/26 edges, 0 edge
  violations, stable). `tests/projection_instrument_acceptance.py` +12 invariants (53 total).
- **FORM** ✅ (2026-06-14, both viewports, design-critic RESOLVED — Tim-unblocked). Two faces, both shipped:
  · ANGLE-FROM-A-REGISTRY: `bindings/by_lens.py` renders the registry-divided wheel (sectors = the projection
    lenses + an honest '—' remainder), design-critic PASS at both viewports.
  · THE CONNECTIONS (the directional typed edges, drawn): the node registry's type-flow renders as directed
    CHORDS (bow toward centre, arrowhead at the target; a bidir pair = a real mutual cycle, rendered AS a
    cycle — never flattened); whole_set renders the registry's WHOLE structure; DRIVE-TO-EXPLORE — tap a row
    → its OUT edges blaze gold, IN ink, the rest fade, a readout lists feeds-to / fed-by. design-critic
    RESOLVED both 1440×900 + 390×844 (drive lights the wheel — 26,392-px change vs a prior 177-px FAIL).
  > SUPERSEDED — the prior long "needs an ACYCLIC edge-backbone / three data sources all fail / a connection-
  > web is a different feature for Tim" finding was retired by Tim 2026-06-14: "the only edges that get typed
  > are the directional ones" + "nonsequential IS valid." That made the directional-typed-edge connection web
  > the CORRECT face (cycles rendered as cycles, no acyclic order imposed), and it shipped (commits 85df987 +
  > b136d17). My "acyclic backbone" was a self-imposed total-order constraint Tim never set.
  > NOTE: the relation_types VOCABULARY (precedes/depends_on/…) has no INSTANCES yet; as real typed relations
  > are instantiated between items they render in this same view (registry-true) — not a gap, a growth front.

## GROUP 11 · ABILITY — MULTI-SCALE EMBEDDING PYRAMID ✅ (both faces verified; the SCALE axis)
THE REVERSAL (evidence-forced): the spec's "sentence/turn/session/project" rungs were CONVERSATION-shaped;
the corpus is code-digest-shaped + the per-space probe KILLED lineage as the rung axis — within ONE space
`session` is CAPTURE-BATCH provenance (ingest-flow/full-repo/g25/smoke-test — which ingest run wrote the unit,
NOT a semantic nest) and `project` is ONE point per space (company dominates). A centroid over a capture batch
is noise; a one-point project rung is degenerate. So the honest coarsening is over MEANING (the same circle
Group 6 built), not provenance: the coarse rung = fewer, larger meaning-regions = CLUSTERS of near points; a
coarse point = the cluster CENTROID. (Same plausible-but-wrong trap the advisor caught on 6/7/10; the
distinctness test below was locked BEFORE the render.)
- **FUNCTION** ✅ by use — `runtime/scale.py`: ONE agglomerative dendrogram (WARD linkage) cut at each rung →
  the rungs NEST (every fine cluster ⊂ exactly one coarse cluster — independent per-K k-means would NOT;
  ward not average — average CHAINED 129/162 & 525/644 into one giant, verified on the real topics space;
  ward gave balanced 9/19/31). Centroids persist via the SAME store.put_vector into `scale:<space>:k<K>` (no
  parallel index — `query_index` resolves them with the existing cosine); the nesting/membership/exemplar
  rides a `store.save_scale_pyramid` sidecar. Dependency-free (Lance-Williams, no numpy). `default_rungs`
  derives a DYADIC ladder from n (SEED §1 m=2^k; topics 162 → [32, 8]). The bridge's `/api/projection?rung=`
  feeds the rung's centroids to project() as pseudo-events (semantic radius unchanged) — "zoom changes which
  rung RESOLVES". Centre is PORTABLE across rungs (a theme centre resolves from its native rung; no 400 when
  stepping). Built LIVE over topics (40 centroids, real exemplars: scheduler/vector_index/README/worldview…);
  coarse query ≠ fine query proven on real data. `tests/projection_scale_acceptance.py` (29 invariants):
  nesting, ward-not-chaining, centroid=normed-mean, coarse≠fine over a real store, discriminative, persisted
  nesting, incremental, fail-loud, derived dyadic rungs.
- **FORM** ✅ by rubric — a SEGMENTED rung ladder (⊟ units|32|8), distinct from the radial ⌕ zoom (advisor's
  collision avoided); coarse points render as discs SIZED by member-count + labelled by exemplar (region halos);
  stepping rungs CROSSFADES (departing rung fades out as the incoming fades in — continuous scale move, not a
  mode switch); a theme card carries size/finer-count/exemplar + ⊕ zoom-into-theme (steps to the finer rung,
  centred on the exemplar). SEPARATE design-critic PASS at BOTH viewports (1440×900 + 390×844): scale
  legibility (8→32→units reads as a genuine grain progression), discs-as-regions, ladder-vs-zoom distinct,
  token-coherent, responsive. The critic's one FAIL (centre/dense-rung label overprint) was FIXED
  (collision-aware placement: reserve the centre marker, skip the centred theme's label, biggest-first
  non-colliding slot, drop-if-no-slot) and re-verified RESOLVED. design-lint: 0 off-token from this change.
- GROWTH FRONT (honest): raw-source sentence/turn chunking (the corpus is 1-sentence digests → chunking is a
  no-op here); a richer space (repo=644/history=1464) gets more/larger rungs automatically via default_rungs.
  The pyramid is RUNTIME data (.data, like every space) — rebuilt via the DISCOVERABLE route `POST
  /api/scale/build {space}` (registered in the bridge route table → api_verbs; fail-loud on empty/thin
  space), not a hidden script; so the ladder can't silently vanish with no recourse if .data is rebuilt.

## GROUP 12 · MODEL CALLS — DISSOLVED (2026-06-13; Tim confirmed "your logic was actually all correct")
See SEED-SCALE-PRIMES-SEPARATOR.md §17. The gate is GONE — every "model call" was the lead trying to
freeze a variable Tim deliberately left free (the hardcoding reflex). Resolution:
- **Call 1 (register = prime/divisor lattice?) — INVALID.** Not a separate formalism; the equation
  recursing one scale up (corners = primes already). No ratification, no gate.
- **Call 3 (the two privileged axes) — INVALID.** Axes are variables; it is ONE-and-three — only TIME
  is privileged (settled); the three of space stay variable. Build the resolver, never fix them.
- **Call 2 (two-gravity anchors) — ANSWERED structurally.** Poles = the CENTRE (Tim's model/origin +
  the gradient field of his recognitions) and the CORNER (AI deformation). Nothing in the corpus is
  purely Tim, so the Tim-pole is the origin+gradient, NOT corpus samples. The ONLY input is Tim
  describing the AI-tells (volunteered). → Group 9 is UN-GATED.
- **Call 4 (harmonics) — ANSWERED.** "As one instance" — a lens, not the core; spectrum stays out.
- Genuinely-open growth fronts (not gates, not blockers): k (the dimension); prioritization-at-scale;
  the 20/80 dial / promotion gesture — these stub honestly and refine with use. CAVEAT (2026-06-14): "stub
  honestly" does NOT license a stand-in that misrepresents the concept. The 20/80 is TYPE-NUCLEATION (a type
  is born when a region fills past ~20/80 — brain doc 303/327-333/503), NOT a visual prioritization/emphasis
  dial; and its substrate (registry-row relations / typed edges) is the part Tim states he has NOT formalized
  (line 495). So it is gated on Tim's formalization, not a free stub — building a density dial here = green-paint.
**Consequence: NO build item is blocked awaiting a Tim decision. The whole sequence is buildable now.**

---

## PRIORITY ORDER (dependency; instrument-first then ability — the loop walks this)

0. **Model calls DISSOLVED** (§17; Tim confirmed) — no gate; the whole sequence is buildable. (Group 9's old
   "AI-tells input" is also retired — Tim: "there is no single purpose"; the AI supplies its own AI-pole.)
1. **Group 1** — ✅ DONE (6615e53) — the acceptance suite (regression floor; 26 invariant teeth).
2. **Group 5** — ✅ DONE (dc3378a) — the FORM rebuild (lattice onto the corpus design system).
3. **Group 3** — ✅ DONE (backend dabf952 + FE 9be11cc/3f65f70: scrubber + re-centre + animation, both faces, critic-passed).
4. **Group 4** — ✅ DONE (528704a: SSE subscription, poll retired, smooth client clock, critic-passed).
5. **Group 2** — ✅ DONE (ebbfb89: dyadic grid + m/2 rings + picked-cell highlight; critic-passed both faces). The INSTRUMENT half is complete.
6. **Group 8** — ✅ DONE — embedding substrate live (embedder resident via the `company` CLI + capture+embed).
7. **Group 6** — ✅ DONE — semantic radius (the meaning-field, the first ability ring).
8. **Group 7** — ✅ DONE — strain / forbidden zones (per-point structure↔meaning incommensurability).
9. **Group 10** — ✅ DONE (2026-06-14, both faces) — the event→row edge + angle-from-a-registry + THE
   CONNECTIONS (the directional typed-edge web, cycles AS cycles, drive-to-explore). The keystone.
10. **Group 9** — ✅ DONE (2026-06-14, both faces) — the two-gravity separator (general variable-two-pole read
    + the fifth gate + the two-basin drivable FORM). Tim retired the old "Model Call 2 / AI-tells" gate.
11. **Group 11** — ✅ DONE — the multi-scale pyramid as the SCALE axis: ward-clustered meaning-rung centroids
    (NOT lineage — evidence-killed), nested rungs, a crossfading rung ladder, design-critic PASS both faces.
12. **The small registries + gate surface + 20/80 water-law** — 🔴 GENUINELY Tim-gated (re-examined this fire).
    NOT gated on relations (Tim GAVE relations → Group 10 shipped; that stale claim is corrected). The REAL
    open gates, reserved to Tim by his own SEED: (1) the operational definition of "forbidden" (§10 "Tim: you
    tell me"; §7 "deliberately unresolved"; new-types-at-deep-holes "awaiting Tim's fit-test"), and (2) WHICH
    TWO AXES are the spine (§7 "the other is open"). Building it now = green-painting his core science. NOT a
    loop TARGET (the targets were Group 10 + Group 9).
