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

## GROUP 2 · INSTRUMENT — THE SQUARE/STRUCTURE HALF (the grid) 🔴
Today: a per-point depth scalar + `rings:4` hardcoded. The seed's m/2 concentric circles + i,j grid.
- **FUNCTION** — the i,j grid and m/2 concentric rings RESOLVE from the ui:// address hierarchy
  (`contracts/ui_info.py:parse_ui_address` segments) per the seed §1; the `rings:4` hardcode and the
  depth-scalar are replaced by the real nested geometry. ☐ by use
- **FORM** — the grid renders as a navigable structural surface (not a number); legible at both
  faces; on tokens. ☐ by the rubric

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

## GROUP 6 · ABILITY — THE CIRCLE / SEMANTIC RADIUS 🔴 (needs a resident embedder)
projection.py:155 is a no-op stub (both branches = age).
- **FUNCTION** — a `radius_from=='semantic'` resolver reads cosine-from-centre off the persisted index
  (`suite.query_corpus`/`store.get_vector` + cosine); a `bindings/semantic.py` row; points ranked by
  meaning-distance from the centre. ☐ by use
- **FORM** — meaning-distance reads spatially (near = close); legible at both faces. ☐ by rubric

## GROUP 7 · ABILITY — STRAIN / FORBIDDEN ZONES 🔴 (needs Groups 2 + 6)
Zero code today. The structure↔meaning gap.
- **FUNCTION** — per-point square-position vs circle-position disagreement is computed and surfaced as
  a strain field OR a 'strain'/'forbidden' mark_type (`mark_types.py` + `append_finding`); render,
  never auto-correct; operator-overridable. ☐ by use
- **FORM** — strain reads as visible tension (the gate inbox / drift / axis-growth signal), not a
  number; on tokens. ☐ by rubric

## GROUP 8 · ABILITY — EMBEDDING SUBSTRATE LIVE 🔴 (gates Groups 6,7,9,11)
Mechanism complete; NO embedder resident now (ports HTTP 000); only stale default vectors on disk.
- **FUNCTION** — an embedder up via `company up`; a capture+embed pass populates the named Group-L
  spaces (topics/principles/worldview/repo); index freshness confirmed
  (`vector_index.index_staleness`). ☐ by use (coordinate with the retrieval/ops session)
- **FORM** — n/a (substrate). ☐

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
5. **Group 2** — ← NEXT — the structural square half (i,j grid + m/2 concentric rings from the ui:// address hierarchy; replaces the rings:4 stub; completes the instrument's structure; no embedder needed).
6. **Group 8** — embedding substrate live (operational; gates all semantic ability).
7. **Group 6** — semantic radius (the first ability ring).
8. **Group 7** — strain / forbidden zones (needs 2 + 6).
9. **Group 10** — the event→row edge + order-from-edges + angle-from-a-registry (the keystone).
10. **Group 9** — the two-gravity separator (gated on Model Call 2; highest value once unblocked).
11. **Group 11** — the multi-scale pyramid.
12. **The small registries + gate surface + 20/80 water-law** — once the axes are chosen.
