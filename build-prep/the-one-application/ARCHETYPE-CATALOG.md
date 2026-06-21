# THE ARCHETYPE CATALOG — the operator interface's component-type vocabulary
*composition-owned (the type/contract lane). Tim's "custom component types — graphs, diagrams, selectors, interactive visual/spatial materials, instruments." Each is an ARCHETYPE (a render-type, archetype.schema.json instance): a typed thing → the renderer fills its slots FROM resolved data → a surface. Adding a kind = a type row + an archetype row, ZERO new screen-code. DNA RENDERS each (renderArchetype + lyRender); composition owns the TYPE/contract; the resolver places it across the device axis; the V/RHM inhabit it. Building the catalog = building the interface into what it becomes — every face is a composition of these.*

> Status: **decision-card** is BUILT (the first archetype, proven). This catalog defines the rest — each a concrete contract DNA renders to. Grounded in REAL usage (a named face/need), never speculative. The shared laws (operator-legibility · DNA-token-built · resolver-placed · navigable-not-text · native dual-device) are in archetype.schema; this adds each archetype's SLOT-SHAPE + TAKE + grounding.

## The catalog (6, incl. the built decision-card)

| archetype | render_kind | renders | the slots (shape) | take | grounded in (real usage) |
|---|---|---|---|---|---|
| **decision-card** ✅ | slide / sequence | a decision (present·explain·choose) | question·shape(device)·explanation·options·state | decision_take | FACE-2 / the operator cycle (built) |
| **graph** | graph | addressed nodes + TYPED EDGES (resolved relations) | nodes·edges·legend·header | select-node→navigate | channel-mesh · transcript-viz · the substrate graph · address-view (FACE-1) |
| **selector** | selector | a choice among options/modes/things | options·current·groups? | select→set-value | mode-selector · tool-picking (FACE-3) · any pick surface |
| **instrument** | instrument | a LIVE reading/steering surface | reading·dials·controls·state | drive→re-resolve | the V (state→colour·verb-fan) · gauges · the mode-cascade (FACE-1/4) |
| **diagram** | diagram | an AUTHORED relational picture (flow/seq/hierarchy) | nodes·links·flow | (read-mostly) | flows · sequences · the decision-flow · org/structure pictures |
| **spatial-material** | spatial-material | interactive visual/spatial SUBSTANCE | surfaces·materials·reveals | reveal/expand | the socket-materials (animation/glow/effect) · radial/connection reveals · the "material weight" register |

## How they COMPOSE the interface (the through-line)
Every face is a composition of archetypes resolved against context: the **channel-mesh** (graph) nodes open a **session-card** (a decision-card sibling); its transcript opens the **transcript-viz** (graph); the **board-view** is zones; the **V** is an instrument; a tool opens via a **selector** + renders its result. ONE engine (renderArchetype), ONE resolver (device/viewer/… placement), ONE DNA language (the finish) — the archetypes are the NOUNS, the resolver the VERB, the faces the compositions. Adding a face = composing existing archetypes + (rarely) a new archetype row.

## The EDGE/RELATION binding (graph · diagram · timeline — the relational family)
The relational archetypes bind EDGES between node-records — the one shape the scalar/list archetypes never needed. The contract supports it via the slot_map: `edges` → a field-path (`'edges'`) OR a `'resolve:relations'` directive (the substrate's typed edges, via find_relations/crossings — read-only, reuses territory_for's relations leg). ★ The exact mechanism (a slot the renderer reads vs renderArchetype resolving relations itself) is DNA's renderArchetype's call — co-shape per archetype.

## Build order (grounded-first, render-independent contracts now; DNA renders as each lands)
1. **graph** — highest usage (channel-mesh · transcript-viz · the substrate graph). Concrete contract: graph.schema.json (this commit). The node-graph LAYOUT family (radial/cluster/tree) resolves via the resolver (RESOLVER-CONTRACT); edges via resolve:relations.
2. **selector** + **instrument** — FACE-3 (tool-face) + the V; concrete contracts next.
3. **diagram** + **spatial-material** — flows + the socket-materials (already a built runtime — the spatial-material archetype formalizes its contract).
Each: a concrete `<archetype>.schema.json` (archetype_of + render_kind const + the required slot-shape + take) + a flag to DNA to render to it. The catalog GROWS the interface; this is composition building it toward what it becomes.
