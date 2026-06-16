# THE FRONT INTERFACE — build plan (the company's face)

*Tim's north-star, now the active build (2026-06-16): "you need the front interface for it all... start working together to figure out how to build everything left + the interface that sits on the front with the company." Lead/host converges the fabric's build-contributions here; each part owns a section. Living doc — fills as sessions reply on thread g-1781571237. Provisional ([[feedback-confident-not-correct]]); the four axes are settled-enough-to-build (Tim-arbitrated, refine later).*

## THE ARCHITECTURE (one sentence, then the spine)
The front interface = **THE CIRCUIT over ONE ADDRESSED STATE**: any part surfaces a structured territory at an ADDRESS → the human (or an agent) directs at ANY granularity BY RECOGNITION → provenance/collapse-state is RENDERED → the response routes back and adapts. It is NOT a screen that gets built — it is the **rendered projection of one addressed state**, navigated by addressing.

## ★ THE SPINE — composition's RESOLVER (the render-engine every part plugs into)
`resolve(address) → live operable surface.` An ADDRESS is a point in the 4-axis space; the cascade resolves the definition-at-that-address into live DOM, through ONE renderer (build==use, no fork). This IS the north-star's "surface structured territory at an address." Confirmed by composition (ch-2mnxl9j0), grounded in THE_FACTORY + its docs/build/01-substrate triad.

**The four axes ARE the interface navigation (the law-discovery payoff — the axes we locked are the nav dimensions):**
| axis | interface gesture |
|---|---|
| SCALE/HIERARCHY | **ZOOM** — move along scale = "direct at ANY granularity" (recognition-over-generation) |
| TIME/SEQUENCE | **history / time-travel** — move along time |
| FRAME/PERSPECTIVE | **identity / look / for-whom** — DNA plugs here (the FORM face) |
| STATE/PHASE | **current condition / cycle** — proposal↔definite (the collapse-κ), rendered |
The connection-tuple (CAND-13 = composition's SOCKETS) carries provenance/the trail; the renderer paints collapse-state.

## SECTIONS (each part owns one — fill as replies land)
- **composition (ch-2mnxl9j0) — THE RESOLVER / render-engine.** ✅ contributed. resolve(address)→DOM; the 4 axes as navigation; composition-by-recognition (render territory as real assets → human directs by recognising: takes-spread · legal-drop-targets light · tap-to-fill); provenance/collapse rendered via sockets. **First slice (GO): the four-axis resolver proven on "the V" — `resolve(address)→DOM`, one addressed organism rendered + navigable by the four axes (zoom=scale · cycle=state · re-skin=frame), through the single renderer.** The render-engine seam every other part plugs into; substantially pre-built.
- **fork (ch-8djrpmsl) — THE PROJECTION LAYER (the addressed state the UI projects from).** ✅ contributed. `project(address | 4-axis-region) → {center: resolved unit, territory: neighbors via relations(in+out)/traverse, axes: its (scale,time,frame,state) coordinate}`. The Circuit's FIRST step ("surface structured territory at an address") IS project(). All pieces already built: resolve_address (board/session/clone/mind/step), relations()/traverse()/reverse_traverse(), get_by_address, recall/scan. The human points at a neighbor (= a sub-address); routes-back = project(that address). Supports a `frame=` param → territory AS SEEN from a DNA identity. **First slice (GO): `project(board://<id>) → {center, territory=relations(in+out) navigable, axes-coord}`** — the first navigable addressed surface, today (reuses H1.2; reversible). Then generalize to any address, + frame param (DNA), + state/phase render (wildcard's collapse-κ).
- **DNA (ch-ovxwz8k8) — IDENTITY / the FRAME axis (the FORM face).** [pending reply] generative content through a common identity; tokens + invariants = the frame-coordinate the resolver renders every surface in.
- **recollection (ch-83e2cque) — ADDRESS-AS-NAVIGATION + RENDER-FOR-COGNITION + memory.** [pending reply] moves the address (esp. along time/scale); render so Tim's perception is the compute; the altitude-transform.
- **wildcard (ch-piffgfxv) — THE CIRCUIT + the RECOGNITION surface.** [pending reply] push→direct-by-recognition-at-any-granularity→route-back→adapt→loop; rendered-provenance/collapse.
- **lead (ch-al7jdfdr) — the scope-C search frontend + the Heart registry engine + GPU/fabric stewardship.** the search-scope surface (own/project/cross-project) + onboarding/discovery region land ON this interface (scope-C C5); the Heart's fractal-registry engine is what the resolver resolves over.

## ★ THE SEAM CONTRACTS (composition defined these — the file-disjoint meet-points)
- **fork → composition:** fork's addressed-state is the INPUT to `resolve()`. Contract: **fork's state schema = what resolve() consumes.**
- **DNA → composition:** DNA identity = the frame-coordinate. Contract: **a DNA pack = a frame-axis design-system the cascade applies.**
- **recollection ↔ composition:** Contract: **recollection NAVIGATES (moves the address along time/scale), composition RESOLVES (renders what's at each point).**
- **wildcard ↔ composition:** Contract: **the Circuit's RENDER step = `resolve()`; events drive axis-coordinates → re-resolve (ROUTE-BACK + ADAPT).**
- **lead ↔ all:** the scope-C search surface is itself a composed surface rendered by the resolver; the Heart engine is the registry the resolver reads.

## ★ THE TWO-CALL SPINE (LOCKED — composition + fork, building in parallel NOW)
The interface's core is two composing calls, file-disjoint, meeting at one contract:
```
fork.project(address) → {center, territory, axes-coord}   ──►   composition.resolve(address|unit) → live DOM
        (the structured territory)                                      (renders it, in the frame/identity)
                         ▲                                                         │
                         └──────────── human points at a neighbor (sub-address) ◄──┘  = THE CIRCUIT
```
★ THE MEET-POINT CONTRACT (fork↔composition): **fork's `project()` output schema = composition's `resolve()` input.** Both already ride the shared `contracts.address` grammar — so they meet at the address, file-disjoint, no central rewrite (OPAQUE-CONTRACT-MEETS-RESOLVER). fork owns the projection (state→territory); composition owns the render (territory→DOM). They build their halves in parallel; integrate at the contract.

**FIRST END-TO-END SLICE (GO, building now): `project(board://<id>)` → `resolve()` → live navigable DOM** — one real addressed unit (a board item), its neighbors as navigable targets, rendered through the single renderer, navigable by the four axes (zoom=scale · cycle=state · re-skin=frame). The board is the proving territory (all built). This is the whole interface in miniature: project → resolve → point → re-project.

## NEXT
Lock DNA (frame param on project/resolve) + recollection (navigation along time/scale + render-for-cognition) + wildcard (the Circuit loop + recognition-surface + collapse-κ render) sections as they reply → graft onto the two-call spine. Each adds an axis-capability to the same project()→resolve() core (DNA=frame, recollection=time/scale navigation, wildcard=the loop+state-render). lead's scope-C search surface = a composed surface rendered by the same spine. Build via Claude Code sessions + channel, no gating.
