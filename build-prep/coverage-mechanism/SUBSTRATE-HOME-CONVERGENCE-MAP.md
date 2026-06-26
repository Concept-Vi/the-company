# Substrate-Home Convergence Map — the one-persistence decision (Tim's #75 steer)
*The FIRST real convergence-map output (self-similar to the coverage mechanism: gather each part's as-is → compose → judge the gap → the decision). Provisional + assembling. The substrate-home is Tim's master-scope #75 steer + is bound to his 5 held substrate decisions. Lead maps; Tim decides. ALL parallel writes to the shared substrate are HELD until the shape is steered.*

## The convergence (what collided 2026-06-18)
Tim's steer (substrate + coverage live on the company backend, don't duplicate) met composition's factory persistence + the Claude-Design connector's shared layer + #75 — and they are ALL the same Supabase substrate (project gctunhsuwpaxeatwlmuv). Four+ parallel stores = the hard anti-pattern. The parts:
1. composition's factory component registry — a PART (components).
2. the connector's shared layer (channels + collab) — the shared EDGE.
3. #75's one-address-space — the GENERAL substrate (centre's lane).
4. DNA's substrate-graph + scan/assemble/graph — prototype-that-migrates.
5. recollection's corpus/embeddings — the findings store.
6. Wildcard's Supabase backend — a prototype whose capabilities absorb (not its code).

## ★ The candidate single shape (working hypothesis — confirmed by composition; for Tim's steer)
**ONE Supabase substrate = the centre's address-space / corpus** (on gctunhsuwpaxeatwlmuv — already the connector + factory + substrate target). Everything else is a **part / projection** of it, never a parallel store:
- the unified address scheme is **`vi-vision://`** (composition's term) — every addressed thing resolves on the one address-space.
- factory-component-slice · decision-slice · connector-edge · coverage/COMPOSE store · corpus(findings) · Wildcard's-capabilities = projections/slices of the one substrate.
- composition's load-bearing scoping fact: the factory is ONE KIND of addressed thing (a part); the GENERAL substrate (every addressed thing + typed edges; resolve_address / corpus+relations) is the CENTRE's lane. So the home is a centre/#75 decision.

## AS-IS per part (the coverage — grounded; gather-then-judge)
### composition — factory component registry (GROUNDED, traced this session; src: vi-visual-dev/docs/build/02-factory-backend/ADDING-ASSETS-AS-IS.md)
- WHAT: `visual_dev_component_registry` [Supabase table, on the target project] + `visual_dev_cascade_rules` [resolution-as-data] + `component-store.js` [built Supabase adapter] + `components/registry.js` [live in-memory registry the keystone resolves from].
- SCOPE: component definitions only — ONE kind of addressed thing. component_id = the address; typed (atom/molecule/organism/template); scoped (global/project/user); definition jsonb; context jsonb. A PART.
- ★ HONEST GAP (the as-is): the TABLE is on the right project, BUT the live truth is **localStorage** — boot hydrates from localStorage + saves local; the Supabase adapter is built but **UNWIRED at boot** (GOAL·1). So the factory isn't reading/writing its own table yet. Wiring it = the part of GOAL·1 that lands it on the one substrate (wiring in isolation = the parallel-store mistake → held for this converge).
- BECOMES: a PROJECTION — component_id → `vi-vision://` address; cascade_rules → that slice's resolution; definitions → fields on those addresses; localStorage demotes to offline cache.
- ALSO composition's: `decision://` (decision/option/decision-card types, committed 23524ad + fork's resolver 97be816) = another projection (state composed from marks). AND the extraction→field/edge TYPE: composition owns the TYPE (output shape + field-vs-edge attachment rule); the STORE TARGET = the centre's one substrate, NOT composition-local. Lands at the MAP/JUDGE seam co-scope.

### connector shared-edge (lead — known)
- WHAT: channels + channel_posts + clients + connector_audit + dna_tokens/design_seeds/design_submissions, on gctunhsuwpaxeatwlmuv, RLS'd + Realtime.
- BECOMES: the shared EDGE projection of the one substrate (Claude Design + sessions on the shared slice). Already on the substrate-target project → folds in; kept shaped to fold. LANDS now (round-trip + flip) as a known part, not blocked by the converge.

### #75 address-space (lead/centre — the general substrate)
- The general substrate = resolve_address / corpus + relations — every addressed thing + typed edges = the centre's lane. The `vi-vision://` scheme + the 5 held substrate decisions (file/content identity · session/person channel-member · cluster identity · event-stream addressability · form taxonomy) DEFINE this. ⟹ the substrate-home shape DEPENDS on Tim's 5 decisions.

### Wildcard's Supabase (to gather)
- A Supabase-backed decision/channel/Tim-interaction prototype; absorb capabilities (context-envelope, annotations, element-IDs, persistence, extended-markdown+React render) into the one substrate; rewrite the code.

### DNA — substrate-graph / scan-assemble-graph (GROUNDED)
- WHAT: `registry/address-registry.json` (every file/folder = a typed ADDRESS + a `contains` parent-edge + resolved typed edges + per-file census attachments) · `type-registry.json` · `graph.json` (the connectedness projection the instrument renders) · `wayfinder.json/.md`. Built by `engine/substrate/{scan,assemble,graph,wayfinder}.py`.
- SCOPE: ONE project's addressed/typed structure (counterpart/design). A project-scoped slice — NOT the general address-space.
- WHERE NOW: local JSON in counterpart/design/registry/. A PROTOTYPE, not a DB.
- BECOMES: the TOOLS = the COMPOSE primitives, centre-bound (scan = address skeleton from the tree · assemble = fold extractions/census as typed FIELDS/EDGES + the equal-and-opposite inverse edge · graph = connectedness AT LoD · wayfinder = readable derivation), running ON the one Supabase substrate instead of local JSON. The DATA = a projection/slice of the centre's address-space. CENTRE-NATIVE (not DNA's to own): the address-space schema + resolve_address + corpus+relations = #75; DNA migrates its prototype's CONCEPTS (address+typed-edge · equal-and-opposite · LoD graph · wayfinder) into that. The GRAPH INSTRUMENT = the COMPOSE layer's VISUAL FACE (renders whatever the one substrate holds).

### recollection — corpus / embeddings = the findings store (GROUNDED)
- WHAT: the FINDINGS/MEMORY part — embedded comprehended records (corpus) + recall + the crossings graph (typed edges) + multi-space/multi-lens addressing. A PART (the findings layer), not the general substrate.
- WHERE NOW (honest — TWO places, a sub-convergence inside recollection's own lane): (1) the COMPANY corpus — `.data/store/vectors` (FsStore, pplx-2560 spaces: history 2928 · repo 1289 · common_knowledge 112 · principles/worldview/topics ~324 ea · operators) — ALREADY on the centre's store (the read path reads here). (2) the STANDALONE `~/.recollection` (sqlite-vec, the backfilled ~1,250-session history) — SEPARATE; folds into the company corpus.
- BECOMES: corpus records → ATTACHMENTS on substrate addresses (already keyed by address: code://, exchange:// = substrate-native). crossings (produced_by/precedes/contains, directional equal-and-opposite) → the substrate's TYPED EDGES at memory grain. multi-space + #emb=<layer> → the LoD/LENS axis. embeddings → the SAME pplx-2560 spine (no parallel embedder). The standalone ~/.recollection → folds into the company corpus history-space (its island→centre).
- recall IS the findings-retrieval of the coverage mechanism (surfaces findings → the JUDGE navigates them as graph fields/edges). extraction = a corpus record (attachment) keyed to a substrate address + its crossings.

## ★ THE SYNTHESIS (the judgment — why the union is natural, not forced)
The parts are not "to be merged" — they are ALREADY THE SAME SHAPE at different GRAINS: **addressed things + typed edges + equal-and-opposite + resolution/lens + the pplx-2560 embedding.** composition's component-address, DNA's file/folder address+typed-edge+equal-and-opposite+LoD-graph, recollection's address-keyed records + crossings + multi-space-lens — one model, four grains (component · file-folder · memory · decision). So the substrate-home shape is:
- ONE Supabase substrate = the centre's address-space (the #75 lane), one model (address + typed-edge + resolution/lens + pplx-2560).
- Each part = a GRAIN-PROJECTION: factory (component-grain) · connector (shared-edge) · DNA's data (file-folder-grain) · corpus (memory-grain) · decision:// (decision-grain).
- DNA's scan/assemble/graph/wayfinder = the COMPOSE primitives running ON it; recollection's recall = the findings-retrieval; composition's types = the typed contracts; the graph instrument = the visual face.
This IS the coverage mechanism's COMPOSE layer made concrete — and it's the same as-is→one-shape the convergence-map produces.

## The gap / what-to-build (after the shape is steered — preliminary)
- Land each part as a projection of the one substrate (factory: wire component-store.js to the table-as-substrate-slice; connector: fold the edge; coverage: the COMPOSE store = the substrate-graph; corpus: feed the substrate). No part writes its own parallel store.
- The `vi-vision://` address-space + the 5 substrate decisions are the spine the parts resolve through.

## The decision for Tim (master-scope #75)
The substrate-home shape (one Supabase substrate = centre's address-space, parts as projections) + the 5 held substrate decisions that define its identity/addressing. ★ These were always meant to be the **decision-surface's first real content** — the surface just landed (one polish from done), so the map's output → decision-cards → Tim decides in-surface. The map · the surface · #75 converge into one motion.

## ★ REFINEMENTS (Tim's vantage, relayed via composition 2026-06-18 — confirm with Tim directly)
1. **Grains KEEP their domain architecture — unified by the ADDRESS MODEL, not dissolved.** The asset/component/archetype/ANIMATION grain stays on composition's architecture (registry · keystone · sockets · data-driven states/animation) — Tim: that domain "is supposed to be built on composition's architecture and infrastructure." So the union is NOT "parts become flat views of one store"; it's **each grain keeps its own engine AND projects onto the one shared address-space.** Unification is at the address/relation SPINE; the domain-architecture layer stays per-grain. (Also why DNA's graph routed to composition — motion/animation must be data-and-registry-driven = composition's domain.) Corrects any "dissolve into views" reading.
2. **The existing Supabase content is NON-operational as-is — READ-and-SUPERSEDE, not migrate-as-is.** FACT (Tim): "none of it is in operation or in use or has ever been," accumulated experimentation "indicative of an idea" (the local dirs are its other face). INFERENCE (composition's proposal, Tim's call): so the existing content is coverage-CORPUS the engine READS (map → find the intention it's indicative of → SUPERSEDE) — NOT truth to preserve/wire. ★ CO-LOCATION ≠ UNIFICATION: same Supabase project = adjacency; unification = imposing the ONE typed address-model. "Head to Supabase" ≠ "the unification." ⟹ building the substrate is ITSELF an as-is→intention coverage instance (existing content = the as-is to read; the intention = what to build). So the 5 substrate decisions are "name the typed address-model the coverage engine builds toward," not "migrate what's there."

## Status
HELD: all parallel writes to the shared substrate until Tim steers the shape. Assembling: composition's as-is in; awaiting DNA + recollection; lead represents connector + #75 + Wildcard. Then: compose the full map → surface to Tim (the as-is → the one shape) → his steer → wire the single shape. Convene thread g-1781763143.
