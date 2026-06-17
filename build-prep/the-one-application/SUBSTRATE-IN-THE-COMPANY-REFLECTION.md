# Where the Substrate Lands in the Company — the lead's reflection
*Grounded in the corpus (queried the company's own structure 2026-06-17), the 3 design scans, the substrate architecture, the MCP tool surface, and the lead's full scope. The connected picture — where it builds, what unions open, what upgrades fall out. Provisional; Tim is the judge.*

## ★ THE FINDING THAT CHANGES THE PLACEMENT
The company has ALREADY been circling this. The corpus surfaced:
- `contracts/address.py` + `contracts/resolver.py` — the address spine EXISTS (16 schemes; "truth in registries not literals"; CAS immutable-content + mutable-pointers).
- `build-prep/registry-generation/COORDINATION.md` — an IN-FLIGHT company effort building an ADDRESS REGISTRY via two parallel loops (guided-review + cognition). ★ MUST reconcile — substrate ≈ this effort converging.
- `build-prep/coherence/findings/AREA-1-addressable-substrate.md` — a prior analysis of address-registry readiness.
- `address_scope` resolver (UI-address → code-symbol → file-path) + `addr_context` (address-keyed context w/ relevance/recency decay).
So the substrate does NOT bolt onto the company — it COMPLETES a thing the company already has the resolver-half of. DNA's census/typed-edges = the POPULATION of the address registry the company already has the spine for. **It lands as the convergence of: contracts/address.py (the spine) + the registry-generation effort (the population) + DNA's proven cut (the architecture+seed).**

## WHERE IT BUILDS (the seams, grounded)
- **Address registry** → completes `contracts/address.py`/`resolver.py` + the registry-generation effort. The substrate's per-file census fills the addresses the spine already resolves.
- **Type registry** → a NEW registry in the EXISTING file-discovery mechanism (`runtime/registry.py` "runtime is a queryable graph of relationships"; `runtime/roles.py` the discovery pattern). Same registry-is-truth base — reuse, don't re-create.
- **Typed directional edges (equal-and-opposite)** → the SAME law in THREE places already: the substrate's file-edges, the canvas's typed node-PORTS (`compose_acceptance`: Number→Text rejected), and the `relation_types` registry (contradicts/depends_on/precedes — already directional). UNION: one typed-edge law, three surfaces.
- **The census dispatch** → `runtime/cognition.run_items` (the fan) + the supervisor spawn + #71 routing. NOTE: the scheduler is SERIAL (`concurrent-cognition/02-graph-substrate-reuse.md` flags it needs parallelizing for real concurrent coverage).

## THE UNIONS (what connects to what — the relational picture)
```
            THE SUBSTRATE (addressed, typed graph — structural)
            /          |            |            \            \
       CORPUS       INSTRUMENT    THE FACE      TRIGGERS      #71
     (semantic)     (project/    (interface=   (act-layer)  (routing)
                     the wheel)   command bridge)
```
1. **SUBSTRATE ↔ CORPUS** (the biggest): same addresses, two halves — substrate = STRUCTURE (edges/types/conventions), corpus = MEANING (embeddings). A `code://` address already carries a corpus digest; the substrate adds its typed structure to the SAME address. → query one address space STRUCTURALLY or SEMANTICALLY. The census feeds both (Tim's "two halves" law, made literal).
2. **SUBSTRATE ↔ THE INSTRUMENT** (`project` tool): the substrate is a new SPACE/lens the wheel projects over — dial by-edge, by-ghost-density, by-convention-divergence. Tim's "queryable substrate → filters/slices/views" IS the instrument pointed at the substrate.
3. **SUBSTRATE ↔ THE FACE** (my scope): the substrate is the data-model the interface RENDERS + the V drives; the WAYFINDER is its navigation; DNA's archetypes render substrate addresses. The interface and the substrate are the SAME thing from two ends (Tim's "areas of one thing").
4. **SUBSTRATE ↔ TRIGGERS** (my scope, the act-layer): triggers fire on substrate EVENTS — a ghost node appears → fire a repair panel; a convention-divergence count crosses → fire. The addresses + attachments + time-coordinate are exactly what triggers watch.
5. **SUBSTRATE ↔ #71** (my scope): the census allocates read-agents across tiers (sonnet read-and-report / local / cloud / claude-code) — that allocation-by-region IS `resolve_model(intent)`. #71 is the dispatch the census needs.
6. **SUBSTRATE ↔ THE FABRIC** (my scope): the session-fabric-registry-frame says channels/sessions/board/projects are all REGISTRIES — they become ADDRESSES + ATTACHMENTS in the substrate. The fabric is the substrate's coordination layer; the substrate is the fabric's ground.

## ★ GHOST NODES = the introspective self-build seam (the deepest union)
A ghost node = an edge pointing at what isn't there. Tim's own words: "a missing file that could be RECONSTRUCTED from everything that assumes it." That IS the self-build loop: ghost detected (substrate) → trigger fires (act-layer) → the build-brain (#71/kimi) reconstructs from the implicating edges → writes back → re-census. The company finding + filling its own gaps. The ghost-node surface is where the substrate, triggers, #71, and self-build become ONE mechanism.

## UPGRADES / FEATURES THAT FALL OUT (free byproducts)
- **Convention-divergence surface** (typed primitives by count+position) → automatic code-health/consistency view, free from the census.
- **Temporal queries** (the time-coordinate on every address) → diff/history/re-run over the company's OWN structure, first-class.
- **Self-describing folders** — `CLAUDE.md` per folder resolved FROM the substrate → the legibility architecture (meaning-fields) realized at folder level. ★ This is composition's legibility work (meaning-in-registry-fields) and the substrate's per-address attachments = THE SAME feature. Union flag for composition.
- **Project registry** → the company covering MANY projects (Vi, the vaults, the design repo) = the "common memory for ALL projects" vision ([[project-common-memory-temporal]]) realized. One engine, many project-instances.
- **Parallel census** → forces the serial-scheduler upgrade concurrent-cognition already wants — the substrate is the use-case that earns it.

## MY SCOPE, HELD TOGETHER (the convergence)
Everything I lead CONVERGES on the substrate, which is why building it into the company isn't a side-build — it's the FOUNDATION my whole scope has been circling:
- the **FACE/Phase B** = the substrate's face · the **act-layer/triggers** = its hands · the **corpus** = its memory · **#71** = its dispatch · the **fabric** = its coordination · the **union** = the substrate IS the one-application's ground.
So the recommendation crystallizes: the substrate built into the company is THE keystone that unifies my entire scope — not another parallel thread. Build it as the company's foundation; the interface, triggers, routing, and corpus all already point at it.

## ★ DNA's REORGANISATION-PROPOSAL (found 2026-06-17) — convergence, the island as proving-ground for the centre
DNA's repo carries `docs/dev/REORGANISATION-PROPOSAL.md` — a mature, verified, R1–R22-drift + 5-workstream + staged reorg of counterpart/design into SIX FIRST-CLASS TERRITORIES (`registry/` addr+type+language+project · `dna/` · `surface/` · `app/` · `server/` · `pieces/`). It is built on the SAME laws as the company substrate (derive-never-place · registry-is-truth · equal-and-opposite typed edges · the two halves · dispatch-by-territory) and the SAME substrate engine (substrate-assemble/scan/wayfinder/graph).

RECONCILIATION (per island→mainland-into-the-centre):
- This is NOT a competing reorg — it's the substrate architecture PROVEN ON THE ISLAND. Its GOOD PARTS absorb INTO the company centre: (a) the SIX-TERRITORY taxonomy (a clean candidate structure for the centre's project-instance shape); (b) the substrate ENGINE (substrate-assemble/scan/wayfinder/graph — the SEED I generalize into the company, already named in the build plan); (c) the GRAPH INSTRUMENT (substrate projected as a navigable radial graph = a rendering of the substrate through the one instrument — a real feature to absorb); (d) the DRIFT DISCIPLINE (the 22-item verified drift list + proof-suite/lint as derive-never-place enforcement); (e) the staged-sequence + per-stage-verification method.
- THE ONE THING TO WATCH (the only conflict risk): DNA's `registry/` + its substrate engine must NOT become a SECOND AUTHORITATIVE substrate parallel to the company's. Per Tim: ONE substrate engine, home = the company centre; DNA's repo = the FIRST PROJECT INSTANCE under it; DNA's engine is the seed that's generalized IN, then DNA's repo conforms to the centre's engine (rides the upgraded spine). DNA's near-term island-internal workstreams (A green-proofs, B single-source, C role-layer, D assembler) are healthy island build-up — proceed; the SUBSTRATE/REGISTRY layer (its E + registry/) is the convergence seam to the centre.
- SHARED DECISIONS: DNA's open-decisions #1–#19 overlap the UNION's 5 DECISIONS-FOR-TIM at the same seam (esp. #8 typed-edges, #11 surface-axis-taxonomy, #2 runtime-mutation-boundary, #14 substrate-in-canon, #15 content registry ≈ the form taxonomy). Align them so Tim decides ONCE across both, not twice. The island-specific ones (flat-vs-faces/, render location, archive cleanup) stay DNA's call.
- ADDS TO THE PATCHWORK INVENTORY (R-* reconciles): the address/registry/substrate efforts to unify into ONE now number: contracts/address.py (spine) · registry-generation/ (UI-element grain) · DNA substrate (file grain) · DNA REORGANISATION-PROPOSAL (six-territory structure) · address_scope/addr_context resolvers · coherence AREA-1. SIX partial substrate efforts → ONE centre. This IS the patchwork Tim named.

## OPEN / FLAGS
- ★ RECONCILE the in-flight `registry-generation` effort (is it ancestor or live? it's building the SAME address registry — converge or it forks). recollection to pin.
- The serial scheduler (parallel census needs it).
- DNA's seed handoff (engine/substrate-*.py) + which seams are design-repo-specific.
- The substrate↔corpus address-key alignment (both must key the same address grammar).
