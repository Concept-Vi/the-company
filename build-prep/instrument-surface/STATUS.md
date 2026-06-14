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
- **NEXT BEAT — types-as-gravity (Ask 1, mechanism proposed, awaiting Tim's nod since he flagged uncertainty):**
  generalize the two-pole separator to the WHOLE type registry as the divisions of the circle. Each registry
  type = an angular division (a sector) AND a gravity; every item is typed (cosine to each type centroid) → placed
  in its best-fit type's sector and PULLED toward that type (radius = membership strength: strong members cluster
  tight around their type's band, weak/ambiguous looser); items that fit NO type pile to the forbidden rim (the
  G12 water-law pile). So points "close around their types," misfits are the forbidden zone, and as types are
  added/born the divisions re-divide (the lock x=2π/n). Reuses the nucleation typing already in the engine; a new
  binding `by_type` (angle_from=type-membership, radius_from=type-closeness) keeps the instrument a pure read.

## DESIGN-CRITIC — both new lenses PASS (2026-06-14)
"Connections" (G10) = beautiful string-art-on-paper; "Two gravities" (G9) = the most instantly-legible data
claim in the set. Neither reads as prototype. Fix #1 (G9 card↔pole-label overlap) DONE (`d24181f`).
Remaining non-blocking polish, sequenced (not parked): G10 de-muddy the central chord knot (inner-radius gap /
lower opacity at hub); G9 tighten the central basin gutter; selection tethers (point→card) on all lenses; G9
portrait balance the pole-label wrapping; G10 unify the ~9 o'clock sector marker; G10 a subtle "0 by design" cue.
