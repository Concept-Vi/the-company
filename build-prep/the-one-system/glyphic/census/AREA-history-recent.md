# AREA — Recent History (FINDINGS-LOG Slices 78→39, PROGRESS.md, UNDERSTANDING/)

> Census reader lens: UNIFICATION. Territory: the build's own memory for the recent+language-era work
> — the System Map placement saga, the universal-component grammar origin, the meaning-is-loadable
> decision. Every claim marked **Observed** (file:line, seen without executing) / **Inferred** (labelled,
> pattern-match, unverified) / **Verified** (run/tested by me this pass). READ-ONLY on all sources.
> Files read first-hand this pass: `analysis/FINDINGS-LOG.md` slices 78→38 (lines 207–1183), `analysis/PROGRESS.md`,
> `analysis/glyphic-language/UNDERSTANDING/{00-the-thinking,03-the-intent-and-trajectory}.md`,
> `system/build-system-map.js` (edge section), `system/system-map.html:789–818` (EDGE_TYPES).

---

## §A · SLICE-BY-SLICE ACCOUNT (dense; built / decided / flagged)

### The System Map placement saga (Slices 66→78 — the R3 rationale lives here)
The System Map (`system/system-map.html` + `system/build-system-map.js` + `system-map.json`) is a
living-codebase canvas Tim uses for **visual/spatial cognition of the code** (Slice 68 framing,
FINDINGS-LOG.md:498). It went through **at least 8 placement/layout attempts**, each rejected by Tim
("Info") for a named reason. This is the same class of work R3 is about to redo on the glyphgraph, so
the rejection reasons are load-bearing.

- **Slice 66 (three near-simultaneous "attempt" entries, FINDINGS-LOG.md:549, 618, 638+).** Tim
  *furious, repeated*: the treemap was "an illegible brown wall — couldn't read a single folder/file"
  (**Observed** :550). Root cause named honestly: **"717 equal cells packed into slivers can never be
  legible"** (:551). Also across these attempts: "a directory tree with file names means nothing on its
  own; I need to see the CONNECTIONS of all the things that RESOLVE into the values that make a thing a
  thing" (Slice 67, :531–532). And: **"if I have to scroll it's invalid"** + "must see it ALL on one
  screen as a map" + **"'draws on' is not a real relationship" — generic verbs are useless** (Slice 68
  6th-attempt, :569–571, **Observed**).
- **Slice 67 (:530).** Built the **Resolution view** as default — a 4-column layered flow with the
  connecting LINES DRAWN (SVG curves): Glyphic → its PARTS → the DIALS each part reads (9 axes) → the
  SINGLE SOURCE each dial resolves from. "the wiring IS the picture" (:540). Recorded lesson (5th time):
  **"the RELATIONSHIPS must be the visible content, not structure alone"** (:544, **Observed**).
- **Slice 68 (:497) — PIECE 1/1b, the canonical generator.** `system/build-system-map.js`
  (`buildSystemMap({ls,readFile})`) is the SINGLE SOURCE of the model; `system-map.json` is its output,
  never hand-edited (:505–506, **Observed**). Parallel-BFS walk (sequential ls blew the 30s budget).
  Full tree = 1169 nodes vs old 777; the old scan had **silently dropped 5 real folders** incl. `_ingest`
  (271 files) and missed 9 globals (:511–514). **PRINCIPLE GATE (todo 78, :526):** every edge-type /
  layout / encoding / metadata-facet lives in ONE registry projected into the UI — the canvas is a
  projection of the registries, not a parallel list.
- **Slice 69 (two entries, :439 and :471) — computed LENSES + the folder-local weight fix.** SIZERS
  (size=f(node): importance/size/links/influence/even) + COLORERS (system/type/heat), each a
  single-source registry the topbar PROJECTS from (:471–482). Then the **File-size lens broke the whole
  layout** (bulk image folders swallowed the canvas). ROOT CAUSE (:444): **unit mismatch** — folders
  weighted in *importance* units (~10–120) while files in size-mode weighted in *bytes*
  (thousands–millions); `app/registry` collapsed to 0.24×1.25px. **Second root cause, stated as a law:
  "Zones must not move. Sizing zones by content also destroys spatial memory (the map reshuffles every
  lens switch) — the opposite of this tool's purpose"** (:449, **Observed** — directly relevant to R3).
  FIX: `childValues(parentId)` = one layout-weight authority for every level; **subfolders keep a STABLE
  weight so zones never move across lenses; a folder's loose files share a fixed budget and split it by
  the current metric — a file resizes ONLY against its own siblings, never across the folder boundary**
  (:452–458). This is a relative-within-boundary partition — the same shape A3/R3 wants.
- **Slice 70 (:417) — geometry made AUTHORITATIVE & INSTANT.** Verifier found a race: `relayout()`
  relied on the CSS width/height TRANSITION to reach final size, so a rapid switch or a backgrounded tab
  left chips frozen at the previous size (computed 29.6px while inline said 68.6px, :422). FIX:
  **geometry snaps inline with `transition:none` → computed===inline immediately; the morph is a FLIP
  transform layered on top (transform doesn't change computed w/h), so a paused/interrupted animation
  leaves the layout CORRECT** (:424–432, **Observed**). Load-bearing for R3: *animation must never be
  load-bearing for correctness — position is authoritative, movement is decoration on top.*
- **Slice 71 (:395) — PIECE 2, switchable LAYOUTS registry.** `LAYOUTS` = the single home for every
  "directory → RECT{x,y,w,h,depth}" projection; each entry's `build(W,H)` deterministically projects the
  SAME real tree; switching is the FLIP morph. Two layouts: **nested** (squarified treemap) + **icicle**
  (top-down partition). `computeRECT` delegates to `LAYOUTS[layoutMode].build` (:406). Adding a layout =
  one registry entry.
- **Slice 72 (:376) — PIECE 3, the EDGE-TYPE registry (★ the biggest unification finding, see §B).**
  Tim's direction (verbatim-in-substance, :377): **"edge types must map to a 2-way directional VERB
  (forward/reverse), not opaque names like 'type-extends'."** Built `EDGE_TYPES` — "the single home for
  every relationship, each entry IS a verb pair" (:379): `contains(contains↔sits-inside, draw:false)`,
  `loads(loads↔loaded-by, blue)`, `resolves(resolves-from↔resolves-into, gold)`. This is **Tim's edge
  law (A2), stated and built for the System Map in June — separately from the glyphic language's edges.**
- **Slices 73–75 (:353, :324, :283) — PIECES 4/5 + glyphic toolbar.** Slice 73: the visual-encoding
  vocabulary is **sourced from CV_MEANING** — a SURFACE-ENCODINGS section added to `cv-meaning.js`
  (`CV_MEANING.encodings.register/resolve/has/list`), a `system-map` profile binding node FACET→CHANNEL
  (:356–361). Slice 74: real disk edits via an in-memory model + typed OPERATION QUEUE + a disk-write
  adapter (Claude Code replays it), `relocate()` moves a node + descendants (:324–344). Slice 75: the
  toolbar is BUILT FROM glyphics — every control rendered via `CV_GLYPHIC.render` (a projection of the
  glyphic system, not a parallel button set, :293–294); + undo/redo history stack + pointer-based
  drag-and-drop move (survives the scaled canvas).
- **Slices 76–78 (:253, :228, :207) — layouts reconsidered for MEANING; the radial turn.** Slice 76:
  Tim — the flat Icicle "has no meaning". Added **districts** (regroup by SYSTEM/role, ignore folders)
  + **layers** (stratify by how depended-on: Foundations→Core→Used→Leaves, gold resolve-edges flow down
  to the foundations — "directly visualises everything resolves from single sources", :265–268). Slice
  77: Icicle REPLACED with radial **Sunburst** — the system's first non-rectangle layout, an arc render
  mode; edges in radial suppress the global faint wiring, only the SELECTED node's edges draw as chords
  (:244). Slice 78: sunburst re-thought — **angle = leaf-count (uniform per file), folders = inner-ring
  sectors, files = outer SPOKES whose LENGTH encodes the size-lens metric** (:212–220).

### The universal-component grammar + meaning-is-loadable origin (Slices ~40→58)
- **Slice 58 (:804) — the UNIVERSAL COMPONENT grammar keystone (Tim's brief, verbatim in spec §01b).**
  Make the Glyphic a real component with three independent parts (ring/symbol/fill) + **SLOTS** (values
  a part takes) + **SOCKETS** (typed attachment points, incl. event/onClick, with addresses + conditions)
  — "the first example of a UNIVERSAL component grammar every kind (panel/graph/slide) shares —
  'everything in any interface is a templated dynamic component'; the interface is a PROJECTION of
  declarations (no bespoke wiring)" (:806–810, **Observed**). Refinement: **fill is NOT a 3rd equal part
  — it's the ring's INNER space; the ring also has an OUTER space; the element is a perfect SQUARE**
  (:810–812). Built `glyphic-type.js` (ring/symbol/fill part-types + parent 'glyphic' Type;
  `valueSlots` seeded LIVE from `CV_GLYPHIC.facets` — no second vocab list, :826).
- **The meaning-is-loadable decision (unlabelled slice, :850) — Tim's, near-verbatim.** "yes to all six
  remaining notches; KEY refinement — **every meaning-binding must be LOADABLE/swappable because meaning
  is contextual, EXCEPT symbols (a house is always a house)**. Ship a default I author, editable later."
  Built `cv-meaning.js` → `window.CV_MEANING`: a registry of named meaning PROFILES, separating
  **INVARIANT** (geometry, symbols, render defaults) from **CONTEXTUAL** (what form/colour/fill/texture/
  depth/motion MEAN) (:852–857). **Symbols deliberately excluded** — `valuesFor('symbol')` throws,
  intrinsic, lives in `CV_ICONS.facets` (:857). This is the *documented origin of "nothing has one fixed
  meaning"* — and it already carved the one legitimate exception (symbols).
- **Slices ~40–57 (:900–1182) — the shape-system + brand-fidelity era.** `cv-shapes.js` built as the
  shape system (n-gon generator ≤8 sides; `shapeTypes` = each shape a TYPE with meaning + description +
  default icon; `markDefaults` = one system-wide default, every value a token, :983–998). NOTE for §D:
  **`shapeTypes` is where the "octagon=Gateway / hex=System / diamond=Decision" table originated**
  (:987–990, **Observed**) — "Tied to the brand's established usage (circle=portal, hex=engine,
  octagon=output, diamond=AI) + extended." The rest of this era (geometry honesty, rounded-fit bbox,
  Vi-glyph tracing, PNG-vs-vector) is icon FORM-fidelity, not language semantics.

### PROGRESS.md (the corpus tracker)
12/12 source folders analysed (Tim's real decks): the zoning ladder, gold ramp (`#d6bf57→#c09d5d→#b98664`),
LOD axis (ratio ⟂ density ⟂ LOD), register (terse/verbose cut). Build sessions logged: token
recalibration → generative core → archetype/template layer → **UNIFICATION W1–W2** (found via grep that
the type system + the rule engine had ZERO references + THREE parallel archetype lists; built
`RenderType.jsx` bridge + `archetype-catalog.js` single source, PROGRESS.md:37, **Observed**).

---

## §B · UNIFICATION FINDINGS (parts here now SEPARATE from the generative language; unions-not-bridges)

**★ U1 — The System Map's `EDGE_TYPES` is a SECOND, PARALLEL edge-type registry with hardcoded verb-pairs
and hardcoded hex.** (**Verified** by reading source.)
- `system/system-map.html:789–793` defines `EDGE_TYPES = { contains:{fwd:"contains",rev:"sits inside",
  color:"#6b6354",draw:false}, loads:{fwd:"loads",rev:"loaded by",color:"#7CA0D0",draw:true},
  resolves:{fwd:"resolves from",rev:"resolves into",color:"#E0C010",draw:true} }` — **Observed**.
- This is EXACTLY Tim's edge law (A2): "each entry IS a verb pair" with forward/reverse (Slice 72,
  FINDINGS-LOG.md:379). It was built for the System Map in June, and R1 (Slice 83) built the *same law*
  independently into the glyphic language's `CV_EDGES`/relationship Types with `{directed,inverse}`.
  **Two homes now encode the equal-and-opposite edge law with no reference between them** — the exact
  drift class Tim's CLAUDE.md ("The one idea: everything defined once, referenced everywhere") and the
  islands-join / unions-not-bridges rules forbid.
- Worse for the corpus laws: `EDGE_TYPES` **hardcodes a hex per edge** (`#6b6354`, `#7CA0D0`, `#E0C010`)
  — a raw-hex-in-consumer violation of the four-registry non-negotiable — AND it **bakes fixed verb
  wordings** ("sits inside", "loaded by") as consts the author API cannot reach — the *same* violation
  class R2 (Slice 84) just fixed inside `cv-meaning.js` (REFERENT_KIND consts → profile field data).
  The System Map has the pre-R2 disease that R2 cured elsewhere.
- **The union (concrete):** the System Map's three edge families are relations over a real graph (files
  and folders). Under G6 ("a glyphgraph node = a real address; an edge = a relation_type") and the
  glyphic=address law, **the System Map IS a glyphgraph** — its edges should be relationship Types in
  the ONE home (`CV_EDGES` ∪ `CV_MEANING` edge fields → `relationships-seed.js`), carrying
  `{directed, inverse}` and reading their verbs from meaning fields, its edge colours resolving from the
  meaning profile (Slice 73 already routes the System Map's *node* encoding through
  `CV_MEANING.encodings`; the *edge* verbs/colours were left hardcoded). Fold `EDGE_TYPES` INTO the
  language's edge home; the System Map renders edges by projecting relationship Types, not a private table.

**★ U2 — The System Map's `LAYOUTS` registry is the placement machinery R3 is about to reinvent, and it
already implements the relative-partition primitive.** (**Observed**, FINDINGS-LOG.md:395–412, 452–458.)
- `LAYOUTS[mode].build(W,H)` projects the SAME real tree into `RECT{x,y,w,h,depth}`; `computeRECT`
  delegates; switching is a FLIP morph (Slice 71). The **`childValues(parentId)`** authority (Slice 69,
  :452) is *precisely* A3's "a change re-partitions ONE parent span; siblings inside shift proportionally,
  nothing outside the boundary moves": subfolders keep a stable weight (outside-boundary stillness); a
  folder's loose files share a fixed budget split by the metric (inside-boundary re-resolution). **The
  relative-within-boundary partition A3 mandates already exists, working, in `system-map.html`.**
- **The union:** R3 should not hand-build a new placer from cv-address spans in isolation. It should
  fold the System Map's `LAYOUTS`/`childValues` partition and the glyphgraph's `DiagramSolver` placement
  into ONE relative-address placement system (the cv-address span algebra as the home), so BOTH surfaces
  (codebase canvas + glyphgraph) resolve position the same way. The System Map is the older, more-tested
  consumer; it is an island whose good part (the stable relative partition + the FLIP-is-decoration
  discipline) joins the mainland.

**U3 — The System Map's node encoding is ALREADY single-sourced to `CV_MEANING`; the edge encoding was
not.** (**Observed**, FINDINGS-LOG.md:353–367.) Slice 73 put node colour/size/texture channels into
`CV_MEANING.encodings('system-map')`. The asymmetry (nodes single-sourced, edges hardcoded in U1) is the
concrete unfinished seam — closing it is the same move as U1.

**U4 — The glyphic toolbar is the pattern to REUSE, not rebuild, for the glyphgraph generator's controls.**
(**Observed**, FINDINGS-LOG.md:283–301.) Every System Map control renders via `CV_GLYPHIC.render` — "a
projection of the glyphic system, not a parallel button set" (:294), with FORM=group / COLOUR=polarity
encoding. The glyphgraph-generator's toolbar should be the same projection, not a bespoke button set.

**U5 — `glyphic-type.js`'s SLOTS/SOCKETS grammar (Slice 58) is the universal-component home the glyphgraph
node and the System Map node should both declare through.** (**Observed**, :804–827.) "Everything in any
interface is a templated dynamic component; the interface is a projection of declarations." A System Map
file-node and a glyphgraph node are two consumers of the one parts/slots/sockets grammar — today the
System Map builds its own chip/box DOM. Union: both render through the universal-component Type + `RenderType`.

---

## §C · DISCONNECTED / UNUSED THINGS THIS HISTORY REVEALS (built then abandoned — evidence)

- **C1 — Multiple superseded System Map layouts / whole rebuilds, each replaced.** The history records the
  treemap (Slice 66/68) *replaced* by a region board (:549), then a resolution flow (:552), then rebuilt
  again as an atlas (:618), a concept tour (:657+), a single-screen treemap (:568). `system-atlas.html`
  and the "concept tour" are named as **superseded** (:615, :635, :654). **Inferred:** several of these
  HTML surfaces may still be on disk unreferenced — a census sweep of `system/*.html` should confirm
  which are live vs abandoned (I did not enumerate the folder this pass; flagged for the connection-map).
- **C2 — Icicle layout removed.** Slice 77 (:231) "Removed Icicle and added Sunburst". The `LAYOUTS`
  registry entry for icicle was retired — **Observed** in the narrative; whether the entry is fully gone
  from `system-map.html` is unverified.
- **C3 — `system-map.json` was, at one point, retained but powering nothing.** Slice (around :673)
  "system-map.json retained (still powers nothing now; harmless)" during the concept-tour era — later
  re-adopted by Piece 1 (Slice 68). This is a whole generated model that went dead then live again — a
  liveness the ledger must not assume either way (matches the repo's `status: unconfirmed` default).
- **C4 — Orphaned brand-mark PNGs.** Slices ~40–43 (:1128, :1160) copied source PNGs into
  `assets/brand-marks/`, then the vector-trace era (Slice 43) made them "unreferenced; couldn't
  bulk-delete (not owner) — flagged for removal" (:1128, **Observed**). Likely still orphaned on disk.
- **C5 — The `verbs` table in cv-edges.js** (already dispositioned by R1 as removed drift, per
  READING-LEDGER) is the *same species* of abandoned-parallel as `EDGE_TYPES` — one was caught and
  removed, the twin in system-map.html was not. **Inferred** they are the same class; **Observed** that
  R1 removed the cv-edges one and left EDGE_TYPES untouched.

---

## §D · CORRECTIONS to what the plan files / ledger / audit get wrong about this history

- **D1 — The ADVISOR-AUDIT's CRITICAL R3 gate is satisfiable from FINDINGS-LOG, and I can now name the
  exact rationale it flagged as missing.** ADVISOR-AUDIT §6 item 1 says "the stable-slot 21/21 era, the
  measured force-directed rejection, and the never-surfaced left-vs-centred call live in that history"
  and must be read before R3. **Correction/completion:** the *glyphgraph* stable-slot 21/21 rationale
  lives in **SYNTHESIS.md:140–164** (which I read — it is the DiagramSolver `glyphgraph` case), NOT in
  the Slices ≤78 I was assigned. What Slices 66–78 hold is the **SIBLING placement saga for the System
  Map** — the *same laws discovered on a different surface*, which is arguably MORE valuable for R3
  because it states the laws as principles ("zones must not move / destroys spatial memory", :449; unit
  mismatch across a boundary breaks partition, :444; animation must not be load-bearing, :424). The
  audit treats the placement rationale as one thing in one place; it is actually **two parallel
  discoveries** (glyphgraph in SYNTHESIS, System Map in FINDINGS-LOG 66–78) — which is itself the U2
  unification finding.
- **D2 — The "measured force-directed rejection" the audit cites: I found the System Map's version,
  not necessarily the glyphgraph's.** FINDINGS-LOG (:644, concept-tour era) records a **physics sim that
  diverged (scale→1e-129)** on the System Map, replaced by a deterministic CLUSTER layout. **Observed.**
  This is a *measured* force-directed rejection — but on the System Map surface. If the plan files
  attribute a single force-directed rejection to the glyphgraph alone, that is incomplete: there are two,
  and the System Map's is the one with the concrete failure number (1e-129 blow-up).
- **D3 — The octagon=Gateway table's true origin.** The course-correction memory and A4 treat the fixed
  shape-tables as "AI inventions". **Correction (nuance, not contradiction):** `cv-shapes.js` `shapeTypes`
  (FINDINGS-LOG.md:987–990) records they were **"Tied to the brand's established usage (circle=portal,
  hex=engine, octagon=output, diamond=AI) + extended."** So the *seed* had a real-brand basis (Tim's
  decks use those shapes that way); the *drift* was baking it as a fixed one-sentence interpretation
  unreachable by the author API. The fix is still A1/R2 (fields, authorable) — but the ledger should
  record that these are brand-grounded seeds to be *fielded*, not pure fabrications to be *erased*.
- **D4 — No contradiction found in READING-LEDGER or the audit about this era.** Everything the ledger
  and audit say about Slices ≤78 being unread was true; nothing they assert about this history is wrong.
  My additions are *fills*, not corrections, except D1/D2's "one place → two parallel places" reframing.

---

## §E · DIRECT INPUTS FOR R3 (placement) — rationale, numbers, open taste calls

**The laws R3 must honour, stated as PRINCIPLES in the System Map history (all Observed):**
1. **Zones must not move under a re-lens / re-metric.** "Sizing zones by content destroys spatial memory
   (the map reshuffles every lens switch) — the opposite of this tool's purpose" (FINDINGS-LOG.md:449).
   → R3: a facet/metric change must NOT re-place established nodes; only re-resolve within a boundary.
2. **One weight currency across every level, or the partition breaks.** The File-size bug was a **unit
   mismatch** — folders in importance units (~10–120), files in bytes (thousands–millions) — collapsing
   `app/registry` to 0.24×1.25px (:444–447). FIX = `childValues` makes folder+file weights the same
   currency at every level (:456). → R3: the span/angle partition must use ONE relative currency; never
   mix an absolute measure (pixels, live count) with a relative one — that is *exactly* the "absolute
   rule on a relative system" Tim named.
3. **A child resizes only against its own siblings, never across the folder boundary** (:456–457). →
   R3's "re-partition ONE parent span; nothing outside the boundary moves" — this is the SAME rule,
   already built and verified for the System Map.
4. **Geometry/position is authoritative and INSTANT; movement is a FLIP transform layered on top and
   must never affect correctness** (:424–432). The bug it fixed: relying on a CSS transition to reach the
   final size left nodes frozen at the wrong size on a backgrounded/throttled tab (:422). → R3: resolve
   the relative address to a position instantly; animate the diff with a transform that does not change
   the resolved geometry. A paused animation must leave the layout correct. (This directly informs A3's
   "bounded, angled, animated" movement — the animation is decoration, the address is truth.)
5. **The measured force-directed failure (a real number for the "reject force-directed" call):** the
   System Map's physics sim **diverged, scale→1e-129** (:644), replaced by a deterministic phyllotaxis
   cluster layout. → R3: deterministic/index-stable placement over physics is evidenced, not preference.

**The open taste call R3 must FINALLY surface to Tim (never surfaced — Observed across sources):**
- **Left-anchored vs centred-on-fixed-capacity, both stable.** SYNTHESIS.md:159–164 (glyphgraph
  stable-slot): rows now LEFT-HUG (source + small rows at the left margin, right gutter empty) — "the cost
  of pinning over centring." There is a STABLE centred alternative keeping all tests green:
  `x = cx + (ci - (CAP-1)/2)*LAY_PITCH`. "left-anchored vs centred-on-fixed-capacity, BOTH stable —
  which reads better — a taste call for Tim's eye in the live render." **This was flagged for Tim and
  never surfaced** (confirmed by CRITERIA.md:168 and SYNTHESIS.md:210). The System Map's rows *also*
  anchored LEFT (Slice 76 nested/icicle, and the sunburst rim-labels flip on the left half) — so the
  left-vs-centred question is a *cross-surface* taste call, not glyphgraph-only. R3's live render is the
  vehicle; do not let A3 leave it as prose again.
- **The corollary honest boundary R3 inherits:** stable-slot stability held only for SAME-RANK sibling
  append within capacity (~2 slots/row); beyond capacity later slots ran OFF the right edge honestly
  (SYNTHESIS.md:147–149). The System Map's answer to "too many siblings" was the radial Sunburst (angle
  = leaf-count, uniform per file, FINDINGS-LOG.md:212) — a candidate relative-placement mode for the
  glyphgraph when a rank overflows a linear row. **Inferred** this is a reusable mode, not proven for the
  glyphgraph.

**The `childValues` / span-partition code to reuse (pointers, not copies):**
- `system/system-map.html` — `childValues(parentId)`, `computeRECT` → `LAYOUTS[mode].build`, `relayout()`
  / `applyLayout()` / the FLIP `captureRects()`+`flipFrom()` pair. (**Observed** in the slice narratives;
  exact line numbers not enumerated this pass — a follow-up read of `system-map.html` should pin them
  before R3 reuses them.)
- `core/DiagramSolver.jsx` `glyphgraph` case + `core/cv-address.js` span algebra (the A3-designated home)
  — the audit's CRITICAL "read DiagramSolver in full before R3" still stands; my history read does not
  replace it, it *contextualises* it (the System Map is the working sibling implementation).

---

## §F · PROPOSED PLAN-FILE EDITS (tentative text blocks — assumptions + refs inline, correctable)

> These are drafts for the lead to fold. Each carries its source. Marked with the target file.

**F1 — ROADMAP.md, PHASE RECONCILE R3, add a unification note (the placement redo is a JOIN, not a
fresh build):**
```
- **R3 · Placement redo (A3) — the relative laws.** [existing text stands] …
  UNIFICATION (from AREA-history-recent §B/§E): the relative-within-boundary partition A3 mandates
  ALREADY EXISTS, working+verified, in system/system-map.html — `childValues(parentId)` keeps zones
  stable across a re-lens (subfolders hold a stable weight; a folder's loose files share a fixed budget
  split by the metric → a child resizes only against its own siblings, never across the boundary;
  FINDINGS-LOG.md:452–458). R3 FOLDS that partition + the glyphgraph DiagramSolver placement into ONE
  relative-address system (cv-address spans the home), so the codebase canvas AND the glyphgraph resolve
  position the same way (islands-join). The System Map also proves: (a) geometry must be authoritative &
  instant, the FLIP morph is decoration that must never affect correctness (:424–432); (b) never mix an
  absolute measure with a relative one — the File-size unit-mismatch bug (:444) is the "absolute rule on
  a relative system" failure in the wild; (c) the measured force-directed rejection has a number
  (physics diverged scale→1e-129, :644). SURFACE the left-vs-centred taste call in the live render — it
  is a CROSS-SURFACE call (System Map rows also left-hug), never surfaced (SYNTHESIS.md:159–164, 210).
```

**F2 — ROADMAP.md, PHASE RECONCILE R1 (the edge law), add the second-home finding:**
```
- **R1 · The edge law …** [existing text] …
  UNIFICATION: there is a SECOND, undispositioned home for the equal-and-opposite edge law —
  system/system-map.html:789–793 `EDGE_TYPES` (contains↔sits-inside, loads↔loaded-by,
  resolves↔resolves-into), built for the System Map in June (FINDINGS-LOG Slice 72:377–379). It hardcodes
  a hex per edge (raw-hex-in-consumer violation) AND bakes fixed verb wordings the author API can't reach
  (the SAME pre-R2 disease R2 cured in cv-meaning.js). Under G6 (a glyphgraph node = an address, an edge
  = a relation_type) the System Map IS a glyphgraph → its edges must be relationship Types in the ONE
  home, verbs read from meaning fields, colours from the meaning profile (its NODE encoding is already
  CV_MEANING-sourced, Slice 73; only the EDGE table was left hardcoded). Fold EDGE_TYPES INTO the edge
  home; render edges as a projection of relationship Types.
```

**F3 — CRITERIA.md, G6 (Convergence) or a new note under G11-history, record the parallel-placement fact:**
```
NOTE (AREA-history-recent, Observed): the System Map (system/system-map.html + build-system-map.js +
system-map.json) is a living-codebase glyphgraph that went through 8+ placement attempts, each rejected
by Tim for a NAMED reason (illegible treemap slivers; "if I have to scroll it's invalid"; "'draws on'
is not a real relationship"; zones-must-not-move). Its LAYOUTS/childValues placement + EDGE_TYPES
verb-pairs + CV_MEANING-sourced encoding are a MORE-TESTED SIBLING of the glyphgraph engine. R1/R3
converge these two surfaces onto the one edge home and the one relative-placement system (unions-not-
bridges), not two parallel implementations.
```

**F4 — READING-LEDGER.md, append a BUILD LOG / census entry:**
```
## FINDINGS-LOG Slices 78→38 + PROGRESS.md + UNDERSTANDING/ — READ IN FULL (census, AREA-history-recent)
- The System Map placement saga (Slices 66–78) = the sibling of the glyphgraph placement redo; states
  the relative-placement LAWS as principles (zones-must-not-move :449; one-currency-or-partition-breaks
  :444; geometry-authoritative-FLIP-is-decoration :424; measured force-directed blow-up scale→1e-129 :644).
- ★ system/system-map.html:789 EDGE_TYPES = a SECOND home for the equal-and-opposite edge law (hardcoded
  hex + baked verbs) — R1's twin, undispositioned. system/system-map.html childValues = A3's relative
  partition, already built+verified. Both are unions-not-bridges targets (§B U1/U2 of the census).
- Slice 58 (:804): the universal-component parts/slots/sockets grammar origin (Tim's keystone brief).
  The meaning-is-loadable decision (:850, Tim): meaning-bindings are LOADABLE/CONTEXTUAL, EXCEPT symbols
  (a house is always a house) — the documented origin of "nothing has one fixed meaning" + its one
  carved exception. shapeTypes octagon=Gateway etc. (:987) were BRAND-GROUNDED seeds ("circle=portal,
  hex=engine, octagon=output, diamond=AI + extended"), not pure fabrications — field them, don't erase.
- Disconnected/abandoned found: superseded System Map surfaces (system-atlas.html, concept tour :615/635/654),
  removed Icicle layout (:231), system-map.json dead-then-live (:673), orphaned brand-mark PNGs (:1128).
```

**F5 — SYNTHESIS.md, add to ROUND 7 §7.4 (Convergence facts) the cross-surface placement/edge finding:**
```
- The System Map (system-map.html) is a working, more-tested SIBLING of the glyphgraph engine: it holds
  a parallel edge-type registry (EDGE_TYPES, verb-pairs + hardcoded hex, Slice 72) and a parallel
  relative-placement partition (LAYOUTS/childValues, Slice 69/71) — both are unions-not-bridges targets
  for R1/R3, not to be left beside the glyphgraph engine. Its node encoding is ALREADY single-sourced to
  CV_MEANING.encodings (Slice 73); only its edge verbs/colours were left hardcoded (the open seam).
```
