# ORGAN REBUILD STUDY — THE GRAPH + THE PATH
*(④ the-one-system · fusion session, 2026-07-02. Six sides read as partial articulations of one mental model. Observed/Inferred tagged.)*

## PART 1 — EACH SIDE: IS / WORKS / REACHING

**A1 — cloud public.graph_edges (54 rows)**
IS [O, 37275]: {id, source_uri, target_uri, relationship, frame, metadata, created_at, created_by} — free-text kind, free-text URI endpoints, both endpoints + kind indexed. WORKS [O]: 19 kinds. Dominant use = **session lineage**: branched_from 7, restarted_from 7, continues 2 — targets are PATH POSITIONS inside URIs (`thread:.../checkpoint:2`). syncs_with 9 (symmetric, strategy in metadata). **Stores both directions explicitly**: depends_on/depended_by 4+4, continues/continued_by — the reverse row carries metadata.reverse_of <forward-id>: derived data stored as if authored. Two URI grammars coexist + test pollution (thread:test-1). `frame` contextualizes the edge ("debugging", "keeper"); one row carries an FSSF frame/scale/scope/focus object. REACHING: relationship-with-context, sessions as journeys with checkpoints, and the equal-and-opposite law implemented by hand because no registry declares inverses.

**A2 — cloud public.type_instance_edges (606 rows)**
IS [O, 40465]: {from_type, from_id, to_type, to_id, edge_type, project_id, metadata, created_by} + UNIQUE on the 5-tuple, project scoping with RLS, and — unique among all sides — **behavior on insert** (trg_edge_dispatch, cache invalidation). "Cartography for project spaces." WORKS [O]: 65 kinds. belongs_to 319 (mostly board-item→project 224, resource→scope 95) — **containment duplicated as rows**. produced 95 (agent→resource) — lineage. Long tail: knowledge cartography (resolves_from, cascades_to, dispatches_to, parallels…) with near-duplicate kinds (parallels vs parallel_to). REACHING: typed endpoints (a poor man's address grammar), project as first-class scope, **edges as live circuitry** — an edge that does something when it lands.

**A3 — cloud graph schema (11 tables)**
IS [O]: nodes (388: kind, stable_key UNIQUE, layer, status, confidence) / edges (326: node-FK endpoints, rel_type, status, confidence) / evidence (388: → source_artefacts (329) with pointer, excerpt, confidence, CHECK node-or-edge) / **sequences + sequence_steps** — the path as a first-class table: {name, sequence_state, start/end_node, confidence} with steps {ordinal UNIQUE-per-seq, node_id OR edge_id, step_state('inferred'), label} / + decisions, observations, build_tasks, future_modules, comments. WORKS [O]: all 326 edges are 'contains'; nodes = a DB-discovery census. **sequences/sequence_steps: 0 rows.** REACHING: the most complete EPISTEMICS of any side (status+confidence on every node/edge, every claim carries evidence → a source artefact) — and **the PATH designed as a first-class record. Designed, never inhabited.**

**B1 — engine ledger.edge (720,461 rows, live)**
IS [O]: {run_id, from_ref, kind, to_raw NOT NULL, to_resolved NULLABLE, line, extra, produced_by_session, pass, extracted_at} — **resolution-as-a-step is schema**. From_refs are canonical addresses. WORKS [O]: 44 kinds — calls 493k, contains 108k, imports 65k, references 39k, then the semantic band (calls-endpoint/serves-endpoint, emits-event/subscribes-event, generated-by 1,403, capability-of, binds-ui, same_law, governed-by, refutes…). 265,805 resolved / 454,656 unresolved, the unresolved **classified** (external 122k · builtin 54k · stdlib 33k · unclassified 245k). Single-direction; in-degree computed at read. Kind drift: part_of AND part-of; depends-on vs cloud depends_on. REACHING [O, NORTH-STAR]: "the common world… a multi-axis coordinate space" — graph, vectors, paths, scale, time, **transcript provenance as ROOT** (generated-by → exchange://), one grammar, one resolver.

**B2 — engine registries + addresses**
IS [O]: board_edges/ — **kinds as file-per-row registry rows**: RELATION_TYPE = {id, directed, inverse?, near?, far?, label?, desc?}, one RelationTypeRegistry mechanism shared with relation_types/ (contradicts, depends_on, fragment_of, precedes, principle_beneath, sibling) and mark_types/ (marks = valued dispositions over addresses — arguably edges from a judgement to an address). Fail-loud on unregistered kinds; add-a-row = add-a-file. WORKS [O]: cc_board traverse() follows links through cognition.resolve_address — one addressed graph, one resolver; reverse_traverse() = the equal-and-opposite read, computed by scan. Step addresses as grammar: session://<sid>/step/<tid> (cc_gate:12), run://<turn>/<member>[/<i>] (cc_gate:79), run://<graph.id>/<node>[@branch][#port] (compile.py:25-28), clone:// point-in-time forks via session_pointintime — **replay of a session at a past point is proven code**. correlation_id threads the cloud circuit. REACHING: the grammar itself — governed kinds WITH declared inverses, cross-registry edges through one resolver, journeys addressable at step grain.

**B3 — the counterpart/design substrate**
IS [O]: address-registry.json — 669 addresses, every one carrying parent + edge_from_parent (prime axis contains), rules declaring "equal_opposite: every typed edge declares a directional inverse"; assemble.py:22-23: "the INVERSE is itself a TYPED edge (NOT a generic referenced_by bucket): import↔imported_by" — inverses composed from an INVERSE map, **ghost nodes** for missing targets (with inverse-edge counts). Types declare valid edges + valid inverses (SUBSTRATE-ARCHITECTURE §13-18). graph.py projects graph.json for the visual instrument: {meta counts-including-zero, types→icon, clusters (containment first-paint), edges (resolved lateral only), spine (top-N by composed in-degree)}. WORKS [O]: the checked-in registry currently carries containment only (graph.json meta: edges 0, ghosts 0, spine 0) — mechanism exists, lateral census unfolded. REACHING: the LAW layer — derive-never-place, registry-is-truth, ghosts as managed surface, inverse-as-typed-edge — and the projection contract for a human instrument.

## PART 2 — COMMON CORE · UNION'S EDGES · IMPLIED-BUT-ABSENT

**Common core** [O in every side]: a directed TYPED edge {from, kind, to} + metadata + created_at + provenance stamp · both endpoints indexed (every side pays for reverse reads structurally) · endpoints are REFERENCES not FKs (the edge outlives its endpoints; B1 keeps to_raw unresolved; B3 makes the missing target a ghost) · containment is the highest-volume relation everywhere it's recorded.

**Union's edges**: A1 — frame (edge context); lineage vocabulary over checkpoint-URIs; explicit reverse rows with reverse_of. A2 — project scoping + RLS; 5-tuple uniqueness; **edges with behavior**. A3 — sequences/sequence_steps (path as table); evidence→source_artefacts; status+confidence everywhere. B1 — volume-proof (720k); **resolution-as-a-step** + far-classification; run-scoped extraction; generated-by transcript provenance. B2 — **kind-as-registry-row with directed + inverse declared**; one-resolver traversal; step/clone grammar; marks; path replay code. B3 — inverse-as-TYPED-edge law; ghosts; counts-including-zero; per-type valid-edge declarations; the visual projection contract.

**Implied-but-absent (in ALL sides)**:
1. **The PATH as a living record.** A3 designed the table (0 rows); B2 minted step addresses and built point-in-time replay — no side has an addressed, ordered, typed walk you can query, embed, or promote. Every side gestures; none inhabits.
2. **One kind vocabulary.** 19+65+1+44+~25 kind strings across five stores, collisions, no shared registry. B2 has the mechanism; the cloud has the volume; they never met. compose_graph (schema.sql:9120-9210) is the confession: five stores unified only at read, per-lens, LIMIT 100.
3. **Declared reverses** — the inverse field exists in B2's schema and B3's map; A1 hand-writes reverse rows: the same need, met three ways, governed nowhere.
4. **Path → flow promotion** — flows/ is a registry of reusable operations; promoted_from exists as a kind; nothing connects a successful walk to a minted flow.
5. **Edge/path embeddings** — NORTH-STAR names vectors as an axis; ledger.embedding holds 76k rows; none are paths.

## PART 3 — THE REBUILT ONE

### 3.1 One edge grammar — the kind registry
edge_kinds/<id>.py → assembled into a DB registry (files as authoring surface, DB derived):
```
EDGE_KIND = {
  id: "imports",            # == filename; ONE spelling (kills part_of/part-of drift)
  directed: True,
  inverse: "imported_by",   # the DECLARED equal-and-opposite NAME (typed, B3's law)
  face: "knowledge",        # containment | knowledge | lineage — the JOB, declared per kind
  endpoints: ["code://","cap://"],   # valid endpoint schemes (A3 §13 pattern)
  behavior: None | "dispatch",       # A2's trigger, a declaration not a hidden trigger
  near/far, label, desc
}
```
Symmetric kinds (syncs_with, parallels, sibling) declare directed: False.
**Reverses: composed-at-read, never stored.** The evidence decides: A1's explicit reverse rows carry metadata.reverse_of — derived data masquerading as authored, doubling rows, orphan risk (what derive-never-place forbids). B1 runs 720k single-direction with both endpoints indexed; B3 composes imported_by at fold time. One stored row per edge; the reverse is the kind row's inverse applied at read. The substrate law is satisfied at the GRAMMAR level — stronger than data-level duplication because it can never drift.
**Edge record** (extends the proven ledger.edge):
```
edge { edge_id, from_addr, kind→registry, to_raw, to_resolved, project, pointer/line,
       confidence, status, evidence_ref (A3: pointer+excerpt→source artefact),
       provenance { produced_by_session, generated_by: exchange://sid/i },
       run_id, extra, extracted_at }
```
All endpoints in the ONE grammar; thread: → session://, A2's (type,id) pairs → addresses.

### 3.2 The three jobs — faces of one grammar, not separate stores
The five-store split is the disease (A2's 319 belongs_to duplicating a column; A3's 326 all-contains). **One store, one grammar; the JOB is the kind's declared face**:
- **containment** — the prime axis; derived-never-placed wherever the address encodes it; stored as edges only where genuinely lateral.
- **knowledge** — the semantic cartography (implements, resolves_from, cascades_to, same_law, refutes, binds-ui…).
- **lineage** — time-directional provenance (generated-by, produced, branched_from, restarted_from, promoted_from); may point at PATH-STEP addresses (A1's checkpoint URIs already do — they just had no path record to land on).
Lenses become registry-resolved face filters, replacing the 5-source union function.

### 3.3 PATH as first-class — path://
Record shape = a direct adoption of A3's designed-but-empty sequences/sequence_steps, landed in the ledger schema:
```
path      { path_id, address: path://<project>/<id>, kind: cascade-run | fusion | navigation |
            session-lineage | authored-flow, name, summary, start_addr, end_addr, state,
            confidence, status, provenance {generated_by, produced_by_session},
            promoted_to: flow-ref|null, created_at }
path_step { path_id, ordinal (unique per path), at_addr,      -- the node stood on
            via_kind → edge-kind registry (nullable at step 0), via_edge_id?,
            payload_addr,   -- run://<turn>/<member>[/<i>], session://<sid>/step/<tid>, cas://…
            stamp, step_state (observed|inferred|planned), label, metadata }
```
Every step addressable — path://<id>/<ordinal> — mirroring the session/run step grammar. **A path is an ordered typed walk: alternating addresses and registry kinds** — the same grammar as the graph, plus ordinals and time.
**Derivations (never hand-placed)**: cascade run → path from the run envelope's legs (via_kind = the graph edge walked; payload = the leg's output) · fusion sequence → same fold, correlation_id as the grouping key · user navigation → steps at ui:// (+ resolved code:// shadows), via_kind=navigated_to · session lineage → A1's branched_from/restarted_from as lineage-face edges targeting path-step addresses; clone://<sid>/<cut> = a branch edge to the source path's step.
**Replay via the resolver**: two proven modes compose — re-materialization (session_pointintime/cc_clone) and re-execution (a cascade path's via sequence re-run). path_replay(path_id, mode) invents nothing.
**Embedding paths**: render to step-transcript → embed into ledger.embedding under space='paths' — path-similarity = cosine ("this debugging walk resembles the walk that fixed X") [I design; mechanisms Observed].
**Promotion — natural selection**: a mark (favour/gold_likelihood over the path:// address) surfaces a successful path; promotion derives a flows/<id>.py row carrying promoted_from → path://… . Walk → mark → flow: the successful journey becomes a capability, lineage intact.

### 3.4 Data landing
| Source | Rows | Landing |
|---|---|---|
| graph_edges | 54 | normalize URIs (thread:→session://); lineage rows → lineage-face edges targeting path-steps; **drop ~8 stored reverse rows** (identified by metadata.reverse_of) — they become composed; syncs_with → directed:false; frame → metadata; quarantine thread:test-*. Net ~40 real edges |
| type_instance_edges | 606 | **drop belongs_to 319 as stored edges** (containment face, derived from fields); produced 95 → lineage; ~190 knowledge edges land with (type,id)→addresses + kind normalization; the 5-tuple uniqueness → (from_addr,kind,to_resolved); dispatch behavior → declared on the kind row |
| graph schema | 326 edges, 388 nodes/evidence | the census re-derives from live introspection; **evidence→source_artefacts adopted wholesale**; **sequences/sequence_steps (0 rows) superseded by path/path_step** — their shape is the ancestor; retire with a pointer |
| vi_sync_edges (1) + documentation_relationships (39) | fold in as kinds; **retire compose_graph** — the lens becomes a face filter |
| ledger.edge 720k | already the shape; gains kind→registry validation (fail-loud), spelling normalization, face tags on its 44 kinds |

### 3.5 The visual Graph instrument — the projection contract
The instrument consumes a DERIVED projection (graph.json pattern), regenerated on change: meta (counts incl. zero) · types→icon · clusters (containment, first paint) · edges (resolved lateral only, with kind) · spine (top-N by composed in-degree) · ghosts (the unresolved surface, counted, managed) · **NEW paths[]: {id, kind, label, steps:[{at, via, ordinal}], state}** — the instrument gains a path lens: light a journey's steps in order over the graph, scrub along ordinals (time axis), compare two paths. The projection stays pure derivation; the Graph organism gains one overlay primitive: an ordered highlighted walk.

### 3.6 Genuinely NEW (everything else is adoption)
(a) the **face** field on kind rows (three jobs unified) · (b) the **path:// scheme** with addressable steps · (c) **path embedding + promotion-to-flow** as the selection loop.

## PART 4 — EACH SIDE'S PARTIALITY
A1 saw lineage + equal-and-opposite but had no registry/grammar — reverses became hand-stored rows, path positions smuggled into URI strings. A2 saw scope + edges-as-circuitry but not derive-never-place — half its volume restates containment; 65 free-text kinds drift. A3 saw the epistemics and DESIGNED the path — but only ever inhabited contains, and its sequences stayed empty: a shape without a producer (the natural producers — runs/sessions — lived in the other family branch). B1 saw scale, resolution-as-a-step, transcript provenance — but single-direction, extractor spellings, no governed vocabulary: volume without grammar. B2 saw the grammar — but edges live in item links arrays, reverses are full scans, marks/edges/steps never met in one store: grammar without volume. B3 saw the laws and the instrument — but its lateral census is unfolded and it is one repo's local instance: the constitution without the population.

**The rebuilt organ: B2's grammar governing B1's volume, under B3's laws, with A3's epistemics and path shape, A2's scoping and behavior, A1's lineage vocabulary — and the PATH as the family's shared unfinished sentence, finally written.**

**Key refs**: cvi_mine graph_edges/type_instance_edges/graph.* · schema.sql:9120-9215 (compose_graph), 37275, 40465 · ledger.edge (720,461 live) · board_edges/AGENTS.md · runtime/cc_board.py:300-345 · runtime/cc_gate.py:12,78-85 · runtime/cc_clone.py · runtime/compile.py:25-28 · flows/ · NORTH-STAR.md · engine/substrate/assemble.py:11-151 · engine/substrate/graph.py · registry/address-registry.json · SUBSTRATE-ARCHITECTURE.md §10, §13-18.
