# The World Interface — charter for ③ (2026-07-02)

*Tim's mandate, interpreted and written down before any build. This is the direction document for the projection/world-map interface — the thing Tim sees and directs through. Companion to NORTH-STAR.md (§③) and UI-CODE-JOIN-ACCOUNTING.md (② — the pointing half of the same circuit).*

## The mandate (Tim, verbatim-in-substance)
- The projection/canvas UI **was never fully built — it was waiting for now.** Like everything here: AI-generated through the chat interface, never actually used, not finished — but *substantially built so that at a future point it could be modified and adapted to its full build.* That future point is now, because the world it renders (the unified ledger coordinate space) now exists.
- **The projection survives; its current form does not.** Interaction "sucks and is missing heaps", performance is bad, UI design is bad — "basically nothing is 'right'". It is **bones and a face** we are free to modify and use however serves the design, precisely *because* it has never been in use. That freedom was its purpose.
- **Design authority is delegated**: "the investigation and imagining of it is needed, for *you* and your agents to design and build." Tim directs by recognition, not specification — so the design process must produce things he can SEE at checkpoints (rendered views, mockups, screenshots), never spec-documents-as-checkpoints.
- **It will need the world map.** And its architecture "is more substantial and needs mapping, understanding and design" — investigate before imagining, imagine before building.

## What this interface IS (the interpretation)
The visible half of the common world. The ledger is a multi-axis coordinate space (graph · vectors · scale · time · provenance · paths · addresses); agents already touch it through tools; **this is the same space made visible and touchable for Tim** — his window and his hand. With ② (the pointing mechanism) it closes the circuit: **see → point → direct.** It is not "a frontend for the ledger"; it is the second face of the one set of functions (north-star: capabilities projected to MCP and UI from the same functions).

## Design principles (binding)
1. **Resolve from the schema and content of the data.** The UI derives its structure from what the data IS: the spaces, kinds, axes, scales, and projects present in the ledger define the lenses, sectors, filters, and views. Add a new space/axis/kind to the ledger → it appears in the interface without interface code. (projection.py already states the seed of this: *"meaning lives in the DATA, never in the instrument."* Keep that law; rebuild the instrument.)
2. **Build on things — compositional.** Views compose from lenses; lenses compose from axes; axes come from the schema. Nothing hand-built per-view that can be derived.
3. **One function, two faces.** Every query/projection/resolve the UI calls is the same ledger-backed function agents call via MCP. No UI-only logic that knows things agents can't know.
4. **Zoom = scale.** The scale pyramid (unit ⊂ fine ⊂ coarse; "zoom changes which rung resolves") is the zoom model — at coarse zoom you see cluster-centroids, zooming resolves finer rungs down to files/symbols. This is also the PERFORMANCE answer: never ship 76k points to a canvas; ship the rung the zoom level resolves (server-side aggregation the pyramid already provides).
5. **Multi-project by address.** A project is a top-level address; the world map is per-universe; the interface is reusable across every project universe the generation chain creates.
6. **The pointing loop is the interaction primitive.** Anything visible answers: what are you (identity/description) · what powers you (② resolve_scope) · where did you come from (provenance → the exchange that generated it) · what is near you (vectors) · what depends on you (graph). And from any answer: direct (mint an intent, dispatch work).
7. **Form is half of done.** Built on the design system (claude-ds is the canonical design language per the fusion findings — reconcile, don't fork), design-critic verified, navigable-not-text. The FORM bar from loop-prep applies to every view.
8. **Live, not a photograph.** The interface reads the living store; changes in the world appear without rebuilds (the SSE/stream seam exists — assess it in mapping).

## What exists (the bones — honest state)
- `runtime/projection.py` — the projection ENGINE: data-driven polar bindings (θ = categorical, r = distance), lens registry. Concept: right. Form: events-only, polar-only — needs generalizing to the full coordinate space.
- `canvas/app` — React+tldraw studio: LatticeView (canvas polar render of /api/projection), RhmChat, AddressHelp, SelfChanges, Review, Settings, StudioKit; `useAppController.ts` is a 197KB god-hook (one of the 4 giants — itself a signal the architecture needs rework).
- `surface/app` — the instrument/wheel surface + RightHand/RHM + the DNA gallery runtime; grew outside the address registry (② is registering it).
- `runtime/scale.py` — the pyramid (built, rungs in the store, migrated to Supabase).
- The bridge API + SSE stream; the unified Supabase store (76k vectors, graph, provenance) — the world itself, ready.
- KNOWN-BAD (Tim): interaction, performance, visual design — all to be redesigned, no compatibility owed to any of it (never used).

## The process (how ③ actually runs)
1. **MAPPING WAVE** (fan-out agents): the full architecture of canvas/app + surface/app + projection.py/scale.py + the API/live seams + the design-system state. Each agent reports: architecture, capabilities present, placeholder-vs-substantial, performance characteristics, interaction inventory (exists/missing), reuse verdict (keep / adapt / replace) with evidence. → synthesized architecture map.
2. **IMAGINING/DESIGN WAVE**: multiple independent design perspectives over the map + this charter (the world map, the lenses, the pointing loop, navigation between scales/axes) — judged, synthesized into ONE design. Produces RENDERED artifacts (mockups/screens) for Tim's recognition — Tim corrects by sight.
3. **Checkpoint with Tim** — recognition on the design (not a spec review).
4. **loop-prep triad** (criteria two-faced FUNCTION+FORM · guide · synthesis) → **build loop** with design-critic + acceptance gates.
5. Build order inside ③: the shared functions first (they're also ②'s), then the world map + pointing loop as the first composed surface, then the further views.

## Open questions the mapping wave must answer (so design isn't imagined blind)
- What projection geometry serves the world map at each scale (polar lens vs force/cluster layout vs hybrid) — and what does the scale pyramid make cheap?
- tldraw: keep as the canvas substrate, or is it wrong for a data-projection instrument?
- The 197KB useAppController: what does it actually hold, and what's the decomposition?
- The two apps (canvas vs surface): one interface or two faces of one? (Instinct: ONE world interface; the RHM/instrument elements become components of it. Verify against what each uniquely does.)
- The live-update seam (/api/stream): sufficient for a live world, or rebuilt?
- Where the design language actually lives (claude-ds canonical vs company tokens) and its component coverage for this instrument.
- What of LatticeView's render approach survives contact with 76k units + rung-based zoom.

## Sequencing
② (population + shared functions + cutover) runs first/now — its two functions ARE this interface's first building blocks. The ③ MAPPING WAVE can fan out in parallel once ② building starts (mapping is read-only). Design wave gates on the mapping synthesis. Tim's recognition checkpoint gates the build.

---
## THE MANDATE SHARPENED (Tim, 2026-07-07 — BINDING on the L8 window design; supersedes any viewer-shaped reading)

Tim's words, in substance: **"This is not just a viewer — it is the truest definition of the word
interface."** The window must let Tim ACTION the system, not observe it:

1. **Every kind of QUERY** — the full ledger.query vocabulary actionable from the surface: semantic,
   lexical, graph (direction/depth/expand), paths, scale-drill, counts, address-sets, every filter — each
   composable, none hidden behind an agent.
2. **Every kind of FILTER and VIEW** — the axes as controls; views over any result set.
3. **Every kind of MODEL RUN** — all the flows and models in the company MCP, runnable from the surface:
   run_role/run_items/run_reduce/cascades/graphs/jobs — set up, configured, fired, watched.
4. **EMBEDDINGS as an operable surface** — Tim must be able to SET, CONFIGURE and RUN embeddings from the
   window (spaces, lenses/embedders, rebuild, pyramid rungs).
5. **FULL design-system integration** — the front is built entirely on the design system (claude-ds
   canonical), not adjacent to it.

Implication for the projection contract + loop-prep: every capability the MCP face exposes needs a
UI-face twin (one-function-two-faces held to its strongest reading). The feed side (ledger.query,
/api/query, embed routing, jobs/cascade/role doors) already exists MCP-first; the window binds them.
Sequencing (Tim, same message): the BACK first — the front is deferred until the back is whole.
