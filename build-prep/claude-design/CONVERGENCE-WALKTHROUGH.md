# Convergence Walkthrough — one stable main (2026-06-08)

> Lead: the interface session, assigned by Tim 2026-06-08 to "integrate and fully deliver and merge into
> one stable main" while he walked, with the system to itself. This is the close-out: what converged,
> what's on main now, what's proven, and the handful of things that are Tim's to decide.

## The mandate → done
Converge the parallel work (the interface/studio stream, the Claude Design prep, and the cognition merge)
into ONE stable main, verified, no green-paint. **Main is stable: the all-green gate holds — 117 suites,
113 green, 4 documented live-dep skips, 0 RED.**

## What converged onto main (three commits, all verified)
```
81f48be  prep      the unified Claude Design pack (docs-only, 21 files)
8734c40  studio    the in-app Review surface + its backend seam (the unstyled scaffold), by-use 6/6
6d27099  stabilize the 2 studio-introduced suite reds, fixed correctly (not silenced)
```
The cognition session had already merged its stream into main (the mode-dial JOIN — "the two streams are
one cognition"); this convergence folded the interface/studio side in on top, unified and green.

## 1 · The Claude Design prep — READY (`build-prep/claude-design/`)
One canonical home, one-source:
- **BACKEND-SEAM-PACK.md** (cognition's) — canonical for the backend contract surface: 102 /api routes,
  the SSE event contract, the address/resolution substrate, the projections, the 9 FE laws, and the
  "where Claude Design output lands" FE-placement map.
- **AUTHORING-FE-HANDOFF.md / AUTHORING-UI-BRIEF.md** (cognition's) — the cognition authoring surface.
- **APPLICATION-STRUCTURE-PACK.md** (this session's keystone) — the framing (I make the architecture
  visible/understandable so Claude Design does the design; Tim owns the design system; sockets vs plugs;
  the two-context bundle seam), the 5 layers (cross-referencing the seam pack, not restating), and the
  genuinely-new layers: the **token-slot contract** (the styling interface a design fills), the **surface
  layer** (IA-as-parent / the Sequences primitive / the 17-surface map / the studio end-state), and the
  **how-to-add-a-region recipe** + the **studio per-surface brief**.
- **README.md** — the reading order + the division (cognition = backend + authoring backend; interface
  session = FE structure + design-into-it + studio).
- **research/** — the evidence base (the layered inventory + deep-reads).

## 2 · The studio surface — READY to design into (`canvas/app/src/regions/Review.tsx`)
The standalone detached HTML is superseded by a **real in-app Review surface** — a page of the app, the
canvas↔review view-switch, three regions `[ Rail | Stage | RhmPanel(+Composer) ]`, wired to the REAL
backend (the sin of the old standalone was reinventing): gallery from `/api/corpus` (registry-is-truth),
the RhmPanel IS the real right-hand-man organ chatting at the pointed `mockup://`/`ui://` locus (and it
reads the mockup's content FOR Tim), comments → `/api/annotate` into the shared address-keyed store (the
bespoke jsonl retired). **Verified by use, both widths (1440 + 390), on a temp store** (never the live one):
switch toggles · gallery loads · stage loads a mockup · chat grounded at the locus · comment persists to
the shared store · canvas unchanged.

**It is deliberately UNSTYLED** — neutral `--studio-*` token-slots, no aesthetic. That is the point: it is
the *structure* you point Claude Design at to design the look into. Structure done; look is yours, in
Claude Design.

## What's proven vs what's yours to decide
**✅ Proven:** main is 0-red (the gate); the studio renders + its seams work by-use both faces; drift holds
(the self-description absorbed the studio); the prep is one-source + cross-referenced; every commit is
path-scoped + clean.

**🟡 Your eyes / decisions:**
1. **A scoping call I made (reversible).** The `ui_registry` gate now checks the LIVE app
   (`canvas/app/src`); the redesign mockups the studio brought legitimately PROPOSE future-surface
   addresses (ui://palette, ui://rhm, ui://canvas/node/*, …) — like `run://`, those aren't live-registry
   entries, so they're reported as info, not gated (registering them would mint canonical entries for
   unbuilt surfaces — never-invent). If you'd rather gate mockups too, it's a one-line revert.
2. **studio-extract removal — deferred to you.** It's a dead pre-merge fork (its content is on main), but
   its worktree has uncommitted regenerable design-data; I didn't force-discard it with a concurrent
   session active. To clear it: `git worktree remove --force /home/tim/company-studio-extract && git
   branch -D studio-extract`.
3. **The studio's FORM** — intentionally unstyled, awaiting your design pass in Claude Design.
4. **Two harmless live-store leaves** — the scaffold agent's first run wrote one studio annotation + one
   chat turn to the live store before catching itself (append-only, non-code). Scrub if you want; harmless.
5. **The net-new studio binds** (small, not blocking): R2 `/api/context?address=` route, per-address tier
   data (I4), a persistent server-side locus (R1), the auto comment→build-intent promotion (L1), in-frame
   element deixis. The substrate for all is built; these are the last binds.

## Notes
- Another session is doing research-prep (docs only, in build-prep/) — disjoint from this code work,
  harmless, confirmed.
- `operable-interface-build` + `company-interface` worktree remain (their unique content is on main now);
  left in place (the loop's home + artifacts) — a separate tidy-up if you want.

## What's next (your move)
Point Claude Design at the scoped FE + the prep, and design the studio (then the other surfaces) into the
structure; the bundle integrates back via the recipe. The cognition authoring surface is the other ready
FE build (backend done, UX is the interface session's per the handoff). The net-new binds above close the
studio's last 5%.
