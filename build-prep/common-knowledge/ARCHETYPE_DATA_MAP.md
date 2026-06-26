# ARCHETYPE → DATA-SOURCE → EXISTING-LIVE-REGION map (recollection — the data-layer for the lead's interface catalog + DNA's assembly)

*DNA proved the discriminator: a surface screen is data-driven WITHIN AN ARCHETYPE; the reuse unit is the ARCHETYPE (~5-7 renderers built once, instances cheap), NOT per-screen adapters. This map supplies the part DNA explicitly can't see from her repo + the lead's catalog needs: (b) WHERE each archetype's DATA comes from (the bridge routes / corpus spaces — grounded from surface/app/src/api.ts + the regions this session), and ★ which archetypes ALREADY have a LIVE region implementation in surface/app (so the build is CONVERGE, not greenfield). Tim's direction: archetype = composition's FACTORY (structure: slots/sockets) + DNA's RENDER (visual), one jointly-built codebase. The lead drafts the final catalog (screens→archetypes + assembly + the two-faces structure) — this is its data-layer input.*

## THE ARCHETYPES (renderer-status · data-source · existing live region)

1. **single-unit immersive** (the unit-face) — renderUnit ✅ BUILT + proven.
   DATA: a common_knowledge corpus UNIT — digest via `/api/cognition/corpus?address=` · pins/relations via `/api/cognition/neighbours` (mine) · `/api/annotations`. Live region: the FACE drill-in (hosted).

2. **piece-in-focus** (scr-piece) — renderPiece ✅ BUILT this session (pixel-identical + 2nd instance proven).
   DATA: a corpus piece + takes/versions `/api/ref-versions` · pins `/api/cognition/neighbours` (mine) · dials `/api/mode` (the cascade). Live region: partial (Inspector/Versions).

3. **canvas / board** (app-canvas, scr-canvas) — renderer NOT built.
   DATA: the graph/nodes `/api/graph` + registryStore + node-state. ★ LIVE REGION EXISTS: the canvas IS surface/app's core (NodeShape/registryStore/CognitionView) — converge, don't rebuild.

4. **ledger / list** (scr-ledger, app-scr-ledger) — renderer NOT built.
   DATA: runs `/api/cognition/list_runs` + `/api/run-stats` · corpus list `/api/cognition/corpus` · `/api/address-history`. ★ LIVE REGION: History (`/api/address-history`), Activity, SelfChanges.

5. **dashboard cards+grid** (scr-dashboard, app-comp-cards) — renderer NOT built.
   DATA: `/api/now` · `/api/events` · `/api/surfaced` · `/api/run-stats` · `/api/inbox`. ★ LIVE REGION: GreetingCard, Inbox, Fleet (`/api/models`), Activity.

6. **compare** (scr-compare, app-scr-compare) — renderer NOT built.
   DATA: `/api/ref-versions` · `/api/address-history`. ★ LIVE REGION: Versions (`/api/ref-versions`).

7. **compose / build** (scr-compose) — renderer NOT built. THE GENERATE rung (heaviest; the 6th V-socket).
   DATA: `/api/build-intent` · `/api/cognition/run_role` · `/api/apply` · RegistryProposals. ★ LIVE REGION: Grow, Workshop, ProposeAffordance, BuildIntentCard.

8. **home / landing** (scr-home) — renderer NOT built.
   DATA: `/api/inbox` · `/api/surfaced` · `/api/now` · greeting. ★ LIVE REGION: GreetingCard + the board home.

## CROSS-CUTTING (NOT screen-archetypes — layers over the others)
- **controls** (app-comp-controls): knobs/config `/api/knobs` · `/api/model/config` · `/api/voice/engine-knobs`. LIVE: Settings (rich — already pulls capabilities/roles/voice/fit/model-load). = the controls layer, maps onto any archetype.
- **states** (app-states, app-states-2): node-state-by-colour (idle/ran/cached/stuck/failed/live) — a STYLE/STATUS layer (the node `status` field on `/api/graph`), applied across archetypes, not its own screen.
- **flows** (app-flow / fused / full): the multi-screen walkthrough/deck — a NAVIGATION/SEQUENCE layer that ORDERS the archetypes (the Walkthrough region), not a single renderer.

## THE SHAPE FOR "SCALE-TO-19" (the budget, grounded)
- ~8 screen-archetypes; 2 built (unit, piece), 6 to build — BUT 5 of the 6 already have a LIVE region implementation in surface/app to CONVERGE the renderer with (canvas, ledger, dashboard, compare, compose, home all have live regions). So it's not 6 greenfield renderers — it's 6 archetype-renderers reconciling DNA's render + composition's factory-structure over data sources that ALREADY flow to live regions.
- 3 cross-cutting layers (controls, states, flows) reused across archetypes.
- Per Tim: each archetype = factory(structure) + DNA(render), one codebase — so the 6 are built jointly with composition, not by DNA alone.
- recollection's data under it: the corpus units (unit/piece archetypes) + neighbours (pins, every archetype with relations) + recall to locate any screen's authoring intent (the Phase-A demo→session map).
