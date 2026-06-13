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
- **FORM** — 🟡: the box frames the wheel (the outer circle inscribed, corners past it at the diagonals);
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
  is 🔴 embedder-gated (Group 6) — stubbed, not faked.
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

## GROUP 7 · ABILITY — STRAIN / FORBIDDEN ZONES 🟡 (FUNCTION ✅ by use; FORM built, design-critic verifying)
The structure↔meaning gap (SEED §111). Built on Groups 2 (the square) + 6 (the circle).
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
- **FORM** 🟡 — a "⊿ strain" toggle on the meaning-field draws the RADIAL tension segment from r_struct to r
  at each point's angle (SEED §111's literal "line between where it's filed and where it means to be");
  alpha+width ∝ strain so coherent points vanish and only divergence reads as tension; the picked card shows
  "⊿ strain · filed ↔ means". design-lint contribution 0. SEPARATE design-critic verifying both viewports —
  flip to ✅ on its PASS.

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

## GROUP 9 · ABILITY — TWO-GRAVITY SEPARATOR 🔴 (UN-GATED 2026-06-13; needs Group 8 + the AI-tells)
Mechanism named; no instruction-lens embedding; transport carries no framing parameter.
POLES (resolved, §17): Tim-pole = the CENTRE (origin + the gradient field of Tim's recognitions/
corrections — NOT corpus samples, since "none of it has all my intention"); AI-pole = the CORNER (the
AI deformation), seeded by Tim's description of the AI-tells (his volunteered input).
- **FUNCTION** — a steerable embedder served; an instruction/task parameter threaded through
  `fabric/transport.py` → `client.complete_embeddings` → `nodes/embed.py` → build_index; the AI-tells
  lens built; a per-unit signed gap (cosine pull toward centre vs corner) = pollution signal (a thin
  sibling of `find_relations`). ☐ by use
- **FORM** — every point carries its signed pull (toward origin vs AI-corner), readable on the
  surface; on tokens. ☐ by rubric
- **INPUT (not a gate)** — Tim's AI-tells description; the Tim-pole needs no enumeration (it's the
  origin + the existing gradient field).

## GROUP 10 · ABILITY — ORDER-FROM-EDGES + ANGLE-FROM-A-REGISTRY 🔴 (needs the event→row edge)
relation_types vocabulary exists but is unwired; order_by is only count|declared.
- **FUNCTION** — the event→registry-row edge formalized; `_resolve_sectors` gains an
  angle_from=<registry-name> branch and an order_by=typed-edge mode (precedes/depends_on); the
  alphabetical sort retired. ☐ by use
- **FORM** — sectors arranged by their real edges read as a meaningful sequence around the wheel. ☐ by rubric

## GROUP 11 · ABILITY — MULTI-SCALE EMBEDDING PYRAMID 🔴
No sentence/turn chunker; corpus is unit-level only.
- **FUNCTION** — a chunker feeds `build_index(space='scale:<rung>')` per rung (sentence/turn/session/
  project); a zoom-by-rung query layer; zoom changes which rung resolves. ☐ by use
- **FORM** — zoom across rungs reads as a continuous scale move, not a mode switch. ☐ by rubric

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
  the 20/80 dial / promotion gesture — these stub honestly and refine with use.
**Consequence: NO build item is blocked awaiting a Tim decision. The whole sequence is buildable now.**

---

## PRIORITY ORDER (dependency; instrument-first then ability — the loop walks this)

0. **Model calls DISSOLVED** (§17; Tim confirmed) — no gate; the whole sequence is buildable. Group 9's only input is Tim's AI-tells description.
1. **Group 1** — ✅ DONE (6615e53) — the acceptance suite (regression floor; 26 invariant teeth).
2. **Group 5** — ✅ DONE (dc3378a) — the FORM rebuild (lattice onto the corpus design system).
3. **Group 3** — ✅ DONE (backend dabf952 + FE 9be11cc/3f65f70: scrubber + re-centre + animation, both faces, critic-passed).
4. **Group 4** — ✅ DONE (528704a: SSE subscription, poll retired, smooth client clock, critic-passed).
5. **Group 2** — ✅ DONE (ebbfb89: dyadic grid + m/2 rings + picked-cell highlight; critic-passed both faces). The INSTRUMENT half is complete.
6. **Group 8** — ← NEXT (the ability half begins) — embedding substrate live: bring an embedder resident via the `company` CLI + a capture+embed pass; gates all semantic ability.
7. **Group 6** — semantic radius (the first ability ring).
8. **Group 7** — strain / forbidden zones (needs 2 + 6).
9. **Group 10** — the event→row edge + order-from-edges + angle-from-a-registry (the keystone).
10. **Group 9** — the two-gravity separator (gated on Model Call 2; highest value once unblocked).
11. **Group 11** — the multi-scale pyramid.
12. **The small registries + gate surface + 20/80 water-law** — once the axes are chosen.
