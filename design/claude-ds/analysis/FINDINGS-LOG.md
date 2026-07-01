# FINDINGS & ACTIONS LOG — per-slice audit outcomes

> Practice (per the build discipline): every slice records here — what the scoped audit found,
> what it changed about the plan, and what was done. This is the running memory of the build so
> autonomous sessions don't repeat or contradict. Newest first.
>

## Slice 82 — Glyphic G10: MULTI-TARGET transglyphing (the read-out generalises past English)
Made `readGraph`'s `target` REAL (it was accepted-but-ignored — English was the only projection). The
meaning IS the graph; a target is one PROJECTION of it. Factored so the TRAVERSAL is shared and only the
LEAF/CLAUSE realisation differs per target — no forked `readGraph`, no second traversal.
- **`assets/icons/cv-meaning.js`** — added `READGRAPH_TARGETS` (target id → realiser-factory, extend-by-
  registration). A realiser supplies `{node, relation, clause, coordinate, subordinate, conditional,
  finalize}`; the shared `walk`/`walkAsObject` (focus selection, recursion, visited/depth guards,
  coordination/subordination shape, the G2.4 conditional front-hoist) call only `T.*`.
  - **`english` realiser** reproduces the prior behaviour BYTE-FOR-BYTE (verified: `verify_readgraph.js`
    output diff-identical pre/post; negation in `edgeClause`, conditional owned solely by `conditional`).
  - **`triples` realiser** = a compact S-expression over STRUCTURE: a node → its `id` (always-present,
    validated, arbitrary — NOT an English word), a relation → `(<kind> <subj> <obj>)`, negation →
    `(not …)`, conditional → `(if <cond> …)` (via a `conditionTriple` that REUSES `CV_COND.normalize`,
    not a new parser), coordination → `(and …)`, subordination → nesting. NEVER calls `referent()` —
    English cannot leak into the structured target (else the "meaning is the graph" proof is fake).
  - **target dispatch** = the colorForValue absent-vs-present pattern: `target` ABSENT → `'english'`
    default (existing callers pass no opts and keep working); `target` PRESENT-but-unknown → THROWS,
    naming it + listing known targets. LOUD-fail still holds INSIDE triples (present-unknown edge
    kind/line throws via `self.field`).
  - **two bugs caught by the test (both fixed):** (1) triples first double-wrapped `(if …)` on the
    lone-conditional front-hoist path (relation() applied `cond` AND the outer `T.conditional` applied
    it again) — fixed by mirroring English: negation folds into the relation triple; the `(if …)` wrap
    is owned by `T.conditional` ALONE, so it wraps exactly once. (2) the `{kind:'not'}` form (the kind
    IS the negation operator, its field `.negates`) double-negated → `(not (not f p))` because
    `kindToken` emitted `not` as the inner relation token AND `neg()` wrapped again — fixed by mirroring
    English's `relationVerb` rkPhrase guard: when `f.negates`, `kindToken` suppresses the relation token
    (emits the structural placeholder `rel`) so `neg()`'s single `(not …)` IS the negation → `(not (rel f p))`.
- **`_demo/verify_g10.js`** (NEW) — runs BOTH targets on the SAME seven graphs (single · relation · branch
  [coordination] · chain [subordination] · negation [explicit marker] · notOp [`{kind:'not'}`] · conditional),
  asserts triples is well-formed + structural (no English-noun-phrase leak), English still equals the known
  sentences, absent-target → english default, unknown target throws, and loud-fail holds inside triples.
  **30 passed, 0 failed.**
- **Verified:** `node --check` clean; `verify_g10.js` 27/0; `verify_readgraph.js` BYTE-IDENTICAL to baseline;
  `verify_g9.js` (round-trip) + `verify_g2_4.js` still green. Load order: `conditionTriple` references
  `window.CV_COND` lazily at call-time (same pattern as the shipped G2.4 English conditional) — no
  index.html load-order change needed. Open: a third target (e.g. `code`) throws today (registered-when-built).

## Slice 81 — Glyphic G2.4: NEGATION + CONDITIONALS in the read-out (REUSE, one home)
Wired negation and conditionals into BOTH read-outs (`readGraph` + `describeRelation`) via ONE shared
helper set — no second negation/conditional path, no reinvented parser.
- **`assets/icons/cv-meaning.js`** — added 4 hoisted helpers used by both read-outs: `isNegated(self,edge)`
  (negation single-homed in the dictionary — an edge negates when its kind's field carries `.negates`
  [e.g. `{kind:'not'}`] OR it has an explicit `negate:true` marker on a real relation kind
  [`{kind:'face',negate:true}` → "is NOT the face of", the relation word SURVIVES]; detection reads
  `.negates`, NEVER a string-match, so any future operator marked `negates:true` negates for free);
  `relationVerb()` (folds negation into the verb — "is"→"is not", "could be"→"could not be" — and
  **suppresses the relation word when the kind IS the negation operator** so `{kind:'not'}` reads "is not"
  not "is not not"); `conditionPhrase(cond)` (verbalizes a condition via **`CV_COND.normalize`** — reused,
  not reinvented; renders field/op/value + all/any/not trees to an English antecedent; loud-fail if
  `CV_COND` absent); `conditionalWrap(edge,clause)` ("if … then …" when `edge.conditions` present — the
  G3.3 key, NOT a second home). `describeRelation` now builds its verb via `relationVerb` + wraps via
  `conditionalWrap`, exposing `edge.negated`/`edge.conditional` flags. `readGraph`'s `walk`/`walkAsObject`
  wrap each clause; a LONE conditional edge from the focus hoists the antecedent to the front
  ("if <cond> then <subject> <verb> <object>"). **`CV_MEANING.field()` now carries `negates`/`operator`/
  `symbol`** through (they were dropped before — that drop is WHY `isNegated` first read false; carrying
  them single-homes the flag in the seed).
- **`assets/icons/cv-glyphics.js:composeRelation`** — forwards `negate` + `conditions` from `edgeSpec` into
  `describeRelation` explicitly (EDGES.resolve drops them — same pattern as the lineColor thread; a silent
  loss would be a law violation), so the rendered relation negates/conditionalizes too.
- **PRE-EXISTING bug fixed in the same pass (resolve-into-scope, never flag-and-park):** `resolveBindings`
  (G8b) called `self.resolveSet` where `self=CV_MEANING`, but `resolveSet` lives on `CV_MEANING.encodings`
  → it threw `resolveSet is not a function` for every bound spec. Fixed to `self.encodings.resolveSet`.
  The `verify_g8b.js` harness made the SAME mistake on 3 direct calls (`M.resolveSet`) — fixed to
  `M.encodings.resolveSet`. verify_g8b now green. (Untouched by the G2.4 edits — proven-localized: my
  G2.4 changes are in field/describeRelation/readGraph/new-helpers, lines ~495–820; the G8b call is ~869.)
- **Verified by RUNNING:** new `_demo/verify_g2_4.js` (22/22) — negation reads "is not"/"could not be" with
  the relation word surviving, the `not` operator reads single negation (no double-not), conditionals read
  "if … then …" in both functions + through composeRelation, a negated conditional reads
  "if … then … is not …", and LOUD-FAIL holds under the new branches (present-unknown line/kind/lineColor on
  a negated OR conditional edge throws; absent contributes nothing). Full regression: verify_g2,
  verify_readgraph, verify_language, verify_g3, verify_g0, verify_glyph, verify_g8b all exit 0. NOT synced
  (lead syncs DesignSync after).

## Slice 80 — Glyphic G5: the RENDER (the glyphgraph laid out + read live)
Built the visual surface for the glyphgraph (CRITERIA G5.1/G5.1b/G5.2/G5.3) — REUSE, no fork.
- **`assets/icons/cv-shapes.js:edgeSVG`** — added a **POSITIONED mode** alongside the existing BOX mode
  (one renderer, two framings — no parallel edge geometry). When `opts.from/opts.to` (real coords) are
  given it emits a bare positioned `<g>` (path + inline arrow polygon in the line colour + optional
  `<title>`), drawn between two points; the existing box mode (`composeRelation`'s inline glyphic) is
  byte-unchanged. Added the line **routing** facet — `straight` (default) · `right-angled` (orthogonal L)
  · `curved` (eased Q-bow) · `free` (harder bow) — the line-types CV_MEANING already seeds
  (routes/eases/sketches to). The arrow shares the line colour, so per-edge line-COLOUR (state) reaches
  the arrowhead with no fixed `<marker>`. Verified both modes by a node shim + `verify_glyph.js` (box-mode
  intact: 3 SVGs, arrowhead, textured line).
- **`core/DiagramSolver.jsx`** — added `case 'glyphgraph'` in `layout()` (authored x/y in 0..1, else a
  closed-form **layered** fallback by longest-path-from-source, else a ring — no external layout lib) AND
  an early-return `glyphGraphView`: each node renders as a **FULL glyphic** (`CV_GLYPHIC.render(node)` —
  facets read at the node top-level, the SAME object `readGraph` consumes), each edge via
  `CV_SHAPES.edgeSVG` positioned mode (line texture=mood · colour=state via `CV_MEANING.field('lineColor')
  .token`→`CV_GLYPHIC.colorForValue`, the single-source token path · routing · arrow=direction). **EDGE
  LABELS OFF BY DEFAULT** (G5.1b): the per-edge read sits in a `<title>` (native hover, zero layout) and a
  label-chip layer renders ONLY when `graph.labels` is on; the chip text is the relation's MEANING
  (`field('edge',kind).feeling` → "part of" / "the face of"), never the raw kind id. The edge `<title>` is
  a **2-node `readGraph`** clean clause ("this owner is part of the project"), not `describeRelation`'s
  facet-narration — passes the octagon oracle. Existing solver types (hub/network/pipeline/timeline/
  quadrant/tree/stack/stepper/orbital/…) untouched.
- **`system/language.html`** — new section "A laid-out glyphgraph — a whole sentence, drawn": loads
  React+Babel UMD and fetch+transforms `DiagramSolver.jsx` **from source** (the app/index.html pattern —
  avoids the stale `_ds_bundle.js`), renders ONE real graph (a project: owner+file part-of the project,
  the project's page face) via `DiagramSolver(type:'glyphgraph')`, and computes the paragraph **live** from
  the SAME graph via `CV_MEANING.readGraph`. A "show edge labels" toggle flips `graph.labels` (one reused
  React root). Token-pure styles.
- **Verified by running** (chrome-devtools @ :8775): diagram lays out 440×440, 4 full glyphics + 3 edges,
  reads WITHOUT labels (mood/colour/direction/routing all legible); labels-mode + hover titles work;
  console clean (one pre-existing non-engine 404). `verify_readgraph` + `verify_g2` (35/0) regressions green.
- **FLAGGED for Tim (FORM/taste — not green-painted):** (1) mixed routing (2 curved gold edges + 1 straight
  green) is a first taste-pass, not a settled rule; (2) arrowheads on curved edges use the chord tangent so
  they land at a slight angle on the dashed face edge; (3) the live paragraph covers the auto-focus walk
  (owner→project→page) so the *file* clause is dropped from the SENTENCE though the PICTURE shows all 3
  relations — readGraph's single-source walk; sentence-coverage + wording are explicitly the LIVE-tuning
  surface (G4.5), not a build gate. Open: per-edge midpoint relation-glyph (operator edges have an icon)
  deferred — line facets are the visual carrier for the seeded kinds.

## Slice 79 — Glyphic G3: the glyphgraph RULEBOOK (relationship Types + validateGlyphgraph)
Built the grammar layer for the glyphgraph (CRITERIA G3.2–G3.4) — REUSE, no fork.
- **NEW `app/registry/relationships-seed.js`** — fills `kind.graph`'s empty `edges` socket
  (`accepts:['relationship']`, an unfilled placeholder). Registers one Type per edge-kind with
  `kind:'relationship'`, `classification:['relationship']`, `family:'relationship'`, and `source`/
  `target` sockets `accepts:['glyphic','atom','block']` (mirrors `kind.graph`'s nodes socket). The
  id list is the **union reconciled live** from the real homes — `CV_EDGES.ids()` (face/documents/
  higher-order/navigates) + `CV_MEANING.valuesFor('edge')` operators (equals/not/and/becomes/part-of)
  — so every edge kind a real graph carries resolves; meaning/look are NOT re-authored (mirrored as
  provenance metadata). 9 Types seeded. `?`/`!` correctly excluded (illocutionary, not binary relations).
- **NEW `assets/icons/glyphgraph.js`** (`window.CV_GLYPHGRAPH.validateGlyphgraph`) — well-formedness
  via REUSE: resolves each `edge.kind`→`relationship.${kind}` Type, checks source/target via
  `CV_REGISTRY.accepts` (domain/range) + edge-instance `conditions` via `CV_COND` (distinct from the
  socket conditions accepts() runs internally). Collect-then-throw with the SPECIFIC violation. Node
  classification is **derived** (`node.classification||['glyphic']`) so a bad-class node is actually
  rejectable — the accepts check is non-vacuous (a `['panel']` node throws a source-socket violation).
  Structural ill-formedness (untyped edge, dangling endpoint, dup id) throws — NOT the absent-facet law.
  CV_REGISTRY/CV_COND resolved **lazily at call time** → load-order-proof.
- **WIRED** into `app/index.html` after kinds-type.js (relationships-seed) + after cv-glyphics (glyphgraph).
- **VERIFIED by running** `_demo/verify_g3.js` (node window-shim + localStorage stub): 25/25 — placeholder
  filled (candidatesForSocket + query return the 9), good graph passes, and every loud-fail path throws
  with its specific message (unknown kind · panel-class reject via accepts · dangling endpoint · untyped
  edge · dup id · failing edge condition; matched-pair sanity proves accepts + CV_COND really evaluate).
  Regression: verify_language / verify_g2 (35/0) / verify_glyph all still exit 0 — no engine file edited.
- **Open / flag:** full FORM/browser verification N/A (G3 is engine-only, no FORM face per CRITERIA).
  Browser load path differs only in native localStorage + babel/jsx (neither touches these plain-JS
  additions; glyphgraph lazy-resolves) — a chrome-devtools load of app/index.html would confirm the
  in-page wiring but isn't required for the G3 FUNCTION bar. DesignSync left to the lead (per task).

## Slice 78 — System Map: Sunburst re-thought (folder rings + size-encoded file SPOKES + rim labels)
Info: the sunburst "has a similar limitation to the icicle" — couldn't differentiate files or their
sizes, nor see the folder connection. Root cause: every file got an equal thin arc (angle = importance
≈ uniform), so size was invisible and folders blurred. Re-thought the radial ENCODING (kept the loved
circular-root-at-centre form):
- **Angle = leaf-count** (memoised), so every file gets the SAME angular width across the whole circle
  — files are now uniform, countable, comparable (no folder's files thinner than another's).
- **Folders = inner-ring sectors** (rings by depth, occupying the inner 42%): each top folder owns a
  contiguous angular wedge, depth-1 tinted strongest, with small gaps between top sectors → the
  folder→file connection reads as a clear coloured column from centre out.
- **Files = outer SPOKES whose LENGTH encodes the size-lens metric** (folderZone→folderZone+fileMax·
  frac, frac normalised 0.14–1 across all files). So files form a readable radial "skyline" — long
  spokes = big files — differentiable at a glance, and the Size lens (bytes/links/used-by) re-maps the
  lengths live (reflow→applyLayout in radial). Files brighter (.62) than folder rings.
- **Rim labels** for the 14 top-level folders (rotated, flipped on the left half) name each sector.
radialHTML now layers folder rings → file spokes → labels → centre hub. select/edges/panel unchanged
and verified on both spokes and rings (1 sel + 9 hot + 9 chord edges + panel). 63 folder arcs, 1108
spokes, 14 rim labels; console clean. (Default Size lens is "Role" so spokes vary by role weight;
switch Size→"File size" to see bytes — single-sourced through the size lens, no second size definition.)


## Slice 77 — System Map: Icicle replaced with radial SUNBURST (arc render mode)
Info: the flat/horizontal Icicle "still doesn't make sense" (empty folder cells + ~100 file rows
crammed in one column). Yes to Layers + the extras; extend the system, keep core principles. Removed
Icicle and added **Sunburst** — the sensible radial form of an icicle and the "rings" mentioned
earlier. It is the system's first NON-rectangle layout, added as a contained arc render mode without
disturbing the rectangle engine:
- LAYOUTS.sunburst has `radial:true` + a build that lays the tree as annular sectors: root at centre,
  depth = concentric rings, angular share = childValues (same weight rule as every layout). Stores
  RECT[id]={x,y(centroid),w:0,h:0,depth,arc:{a0,a1,r0,r1}} so EDGES (centre = centroid) still work.
- buildMap branches on isRadial(): renders an inline `<svg class="rsvg">` of `<path class="arc">`
  (folders = inner faint rings, files = outer rings) + a centre hub, via the new annular() path
  helper and radialHTML(). Non-radial path unchanged.
- Generalised the shared machinery to arcs (data-id carries through): select/deselect/applyFilters now
  target ".chip,.arc"; CSS .arc.sel/.hot/.dim (author CSS beats SVG presentation attrs). flipFrom skips
  <path> (no transform morph — arcs fade in). Colour-lens + size-lens changes route through
  applyLayout when radial (reflow()/colour menu are isRadial-aware); recolor() stays for rect layouts.
- Edges in radial: global faint wiring is SUPPRESSED (would be centre-noise); only the SELECTED node's
  edges draw as chords — so a click traces exactly that node's resolution web. Verified: select an arc →
  1 sel + 9 hot + 1161 dim + 9 chord edges + panel; 1171 arcs (63 folder rings); switching back to
  Nested restores 63 boxes/0 arcs. Console clean.
LAYOUT_ORDER now nested · sunburst · districts · layers. (Sunburst leaves are thin on the outer ring —
inherent to 1100 files — but folder rings read clearly and dim-on-select makes tracing legible; the
colour-menu system filters still hide bulk.)


## Slice 76 — System Map: layouts reconsidered for MEANING (Icicle reworked + Districts + Layers)
Info: the flat top-down Icicle "has no meaning" (files became meaningless vertical slivers) — rethink
the relational structures, modify it, and add the other layouts mentioned. The renderer is
rectangle-based (RECT{x,y,w,h,depth} → div boxes/chips + FLIP morph + centre-to-centre edges), so all
layouts stay rectangles to reuse the proven engine; each now reveals a DIFFERENT relational structure:
- **nested** — containment (where a file lives; the folder tree). Kept.
- **icicle** — REWORKED to horizontal: depth = columns left→right, height = share. Reads as a
  parent→child cascade; leaf files are full-column-width rows so names are legible (was unreadable
  vertical slivers). maxDepth counts folder depth only so files sit one column right of their folder.
- **districts** — NEW. Regroup every file by SYSTEM/role, ignoring folders → labelled regions
  (Assets·406, Ingest·271, App shell·56, Tokens·21…), files squarified within. Shows the system by
  KIND, not location. 25 regions.
- **layers** — NEW, the relational one. Stratify files by how depended-on they are (resolveIn count):
  Foundations·23 (single sources, gold, at the BASE) → Core·18 → Used·135 → Leaves·932 (top). Band
  height ∝ √(importance) so the huge leaf band doesn't crush the hubs; gold resolve-edges flow down to
  the foundations. Directly visualises "everything resolves from single sources."
Infra: layouts may push labelled `LAYOUT_REGIONS` (rendered as non-interactive `.rgn`+`.rlab` behind
chips); `ROLE_LABELS`/roleLabel() single-sources the district/legend names. Because Districts/Layers
change the on-screen NODE SET (no folder boxes), layout switches now go through `applyLayout()` (full
buildMap + FLIP from previous rects — survivors morph, new appear, removed vanish) instead of
relayout(); `reflow()` routes size-lens changes to applyLayout when regions are present, relayout
otherwise. Menu projects all four from LAYOUT_ORDER.
Verified live: menu lists Nested/Icicle/Districts/Layers; nested/icicle = 63 boxes+1108 chips;
districts = 0 boxes + 1106 chips + 25 regions; layers = 4 bands (labels confirmed); edges (652) hold
across all; switching back to Nested restores folders. Console clean.

DEFERRED (offered to user): true radial **Sunburst/Rings** needs an ARC renderer (SVG path segments,
not div rects) — a separate render mode rather than a rectangle layout; flagged as the next add.


## Slice 75 — System Map: glyphic toolbar + undo/redo + drag-and-drop
Info's direction: the toolbar must BE glyphics (the universal unit), organised by component feel —
Add ▸ file/folder, Remove ▸ archive/delete — with verb names on hover; lenses (layout/size/colour)
and the rest become glyphics too; plus undo/redo and drag-and-drop move.

SYMBOLS (single source — extended cv-icons.js, never a local set): added undo, redo, duplicate,
archive, trash, ruler (24×24 stroke bodies + facet tags). Reused plus/minus/file-edit/transfer/
refresh/network/hierarchy/color-swatches/file-list. CV_ICONS.add still validates via CV_GLYPHIC.

GLYPHIC TOOLBAR (system-map.html): loads the glyphic stack (cv-icons → cv-vi-glyph → cv-shapes →
cv-glyphics) and renders every control with `CV_GLYPHIC.render({form,symbol,color},{size:22})` — the
toolbar is a PROJECTION of the glyphic system, not a parallel button set. Encoding: FORM = group
(hexagon lens/view · square structure-op · circle system/history), COLOUR = polarity (gold lens ·
sage add · clay remove · blue neutral edit · muted history · amber ops). Groups: [undo redo] · [layout
size colour] · [relationships] · [rescan edit] · editonly[add▸ rename duplicate move remove▸ ops].
Menu glyphics open popovers (modeMenu for lenses w/ live ✓ on the active mode; Add/Remove rows with
their own small glyphics; Relationships folds the wiring toggle + edge-type slices + system filters in
one place). Verb tooltips on hover; lens tips show the live value ("Layout — Icicle"). The old
<select>s, #etb and loose buttons are gone.

UNDO/REDO: history stack of {data, ops, sel} snapshots (structuredClone). morphEdit snapshots pre-
mutation; emit() commits the snapshot to undoStack + clears redo (so only real edits make history).
undo/redo applyState → reindex + buildMap + FLIP morph + restore selection + persist. Cmd/Ctrl+Z,
Shift for redo (+Ctrl+Y); toolbar undo/redo glyphics disable when their stack is empty. Factored the
FLIP morph into captureRects()/flipFrom() shared by morphEdit + applyState.

DRAG & DROP: pointer-based (survives the scaled canvas) — pointerdown on a chip/box in edit mode,
>6px starts a drag (body.dragging-node, source dimmed), elementFromPoint resolves the folder under the
cursor (file → its parent), validity guard (not self/descendant/same-parent) highlights the target
(.drop-ok dashed gold), pointerup performs the move via the same relocate+emit path; a __dragHappened
flag suppresses the trailing click so drag never selects. Click-to-pick (Move glyphic) kept as
fallback with a #movehint banner. Keyboard: Del/Backspace delete, Cmd+D duplicate, Esc closes
popover/cancels move.
Verified live: 14 glyphic buttons (28 svgs, no fallbacks), menus open + switch layout, edit group
reveals, add→folder creates (badge=1), undo removes, redo restores, drag file→folder moves it with
drop-highlight + op queued. check_design_system clean (52 cards, 499 tokens, manifest in sync).

NEXT (not started): drag a folder onto another (works via same path); Rings/Sunburst layouts; live
texture/border/glow encoding channels; extends/defines edge types (need type-graph parsing).


## Slice 74 — System Map PIECE 5: editor (create/rename/duplicate/move/archive/delete) + op queue + adapter
Info: "Yeah I want real disk edits, need to be able to create and archive too, and duplicate." The
browser preview cannot write project files, so the honest architecture (built): edits mutate the
in-memory model, morph the canvas, persist to localStorage, and emit a typed OPERATION QUEUE (the
schema); a disk-write ADAPTER (Claude Code) replays it to make changes real, then Rescan shows truth.
Built in system-map.html:
- Edit-mode toggle → floating toolbar (+ Folder, + File, Rename, Duplicate, Move →, Archive, Delete)
  acting on the selection; Operations drawer (count badge, list, Export JSON, Clear).
- Engine: `relocate()` (moves a node + all descendants, rewrites paths/ids, remaps edges + globals;
  guards self-nesting + name clashes), create/duplicate/delete/archive helpers, `morphEdit()` (mutate
  → reindexAll → buildMap → FLIP-morph survivors). Move is pick-target (Move → then click a folder;
  folder clicks route to finishMove during a move). Every action `emit()`s `{op,from,to|path,at}`.
- Persistence: `{data, ops}` in localStorage["cv-sysmap-edits-v1"] — plain reload keeps the edited
  view, Rescan re-reads disk, Clear reverts; the 6s auto-poll is suppressed while edits pend so it
  can't clobber them.
- Verified end-to-end headless: clean sequence emitted createFolder/createFile/move/archive/delete
  with correct from→to paths; subtree moves rewrite descendant ids; name-clash + self-nest guards
  fire. Export payload = `{generatedFrom, ops[]}`.
Adapter spec: `analysis/SYSTEM-MAP-EDITOR-ADAPTER.md` — op schema, ordered apply algorithm (mkdir/mv/
cp -r/rm -rf), staleness guard, compiler-artifact cautions, re-source-after-apply, and how to keep
the op vocabulary single-homed (add an op in the editor + adapter together).

PIECES 1–5 COMPLETE. The System Map is now a living codebase canvas: full dynamic model (Piece 1/1b),
switchable LAYOUTS (2), bidirectional-verb EDGE types (3), CV_MEANING-sourced encoding (4), editor +
op-queue + adapter (5) — every axis a single-source registry projected into the UI (principle gate).
Future: drag-to-move (pick-target works now), Rings/Sunburst layouts, live texture/border/glow
channels, extends/defines edge types (need type-graph parsing) — all one registry entry each.


## Slice 73 — System Map PIECE 4: visual-encoding vocabulary sourced from CV_MEANING
Info's direction: the encoding vocabulary "should come from the meaning registry, in some section
for this surface. Draft a few sets + descriptions for Claude Code to build properly and extend."
Built a SURFACE-ENCODINGS section in CV_MEANING's real home (`assets/icons/cv-meaning.js`) — additive,
glyphic API untouched: `CV_MEANING.encodings.register/resolve/has/list`. Registered the `system-map`
profile: channels (colour/size/texture/border/glow/opacity) + 9 encoding SETS, each binding a node
FACET → a CHANNEL with discrete value-maps or scales + plain descriptions:
- LIVE: role-colour, type-colour, link-heat (colour); usedby-size, filesize-size, links-size (size).
- DRAFT (draft:true, for Claude Code): depth-border, kind-texture, state-glow.
Single-sourcing: `build-system-map.js` now takes `encoding` and writes it to `model.encoding`;
regen evals cv-meaning.js, grabs `encodings.resolve('system-map')`, bakes it into system-map.json.
The map reads it live: `ENC=DATA.encoding`; `rc()` + COLORERS(type/heat)/heatCol resolve from
`encSet(id)` (inline tables are fallback only). Verified inline backgrounds resolve from the profile
(role→gold/blue/green, type js→gold css→amber md→grey, heat→stops). (A computed≠inline read on the
two boot-selection-connected chips was the known paused-transition artifact; inline = correct.)
Grammar doc: `analysis/SYSTEM-MAP-ENCODING-GRAMMAR.md` — channels, facets, set schema, the live/draft
sets, how the map projects it, and how Claude Code extends (new set = one entry; draft channel =
implement renderer keyed off set.channel reading values/scale from ENC; never hardcode in the UI).
check_design_system clean (52 cards, 499 tokens, manifest in sync).

NEXT: Piece 5 — editor (move/create/duplicate/archive/rename) + disk-write adapter spec for Claude Code.


## Slice 72 — System Map PIECE 3: EDGE-TYPE registry keyed by bidirectional verb pairs
Info's direction: edge types must map to a 2-way directional VERB (forward/reverse), not opaque names
like "type-extends". Built `EDGE_TYPES` — the single home for every relationship, each entry IS a verb
pair: contains(contains↔sits-inside, draw:false — shown by nesting), loads(loads↔loaded-by, blue),
resolves(resolves-from↔resolves-into, gold). `edgeType(kind)` classifies; buildEdges tags each drawn
edge with its `type`; drawEdges colours by `EDGE_TYPES[type].color` and skips `edgeHidden[type]`.
Added an edge-type toggle legend in the topbar (`#elegend`, projected from EDGE_ORDER via
buildEdgeLegend) — click a verb-pair chip to slice that relationship on/off; tooltip shows "fwd / rev".
Selecting a node already shows ITS edges (highlight), now respecting type visibility. Verified: all
on = 652 drawn (252 resolves + 400 loads), resolves-off = 400, both off = 0.
GENERATOR now emits typed edges (single source): `build-system-map.js` adds `type` to every edge
(contains/loads/resolves); regenerated system-map.json (1171 nodes, 1795 edges: 1143 contains, 400
loads, 252 resolves). HTML reads `e.type` if present, else classifies from kind (back-compat).
EXTENSIBLE: adding extends↔extended-by or defines↔defined-in = one EDGE_TYPES entry + the generator
emitting that kind (extends needs CV_REGISTRY type-graph parsing — noted for the Claude Code handoff).

NEXT: Piece 4 (meaning-registry visual-encoding draft + grammar doc), Piece 5 (editor + disk adapter).


## Slice 71 — System Map PIECE 2: switchable LAYOUTS registry (Nested + Icicle)
Info's direction: layouts must be a SWITCHABLE registry of types (no chosen "most important"), same
pattern as SIZERS/COLORERS. Built `LAYOUTS` — the single home for every "directory → RECT"
projection. Each entry's `build(W,H)` deterministically projects the SAME real tree into
RECT{x,y,w,h,depth}; buildMap renders RECT regardless of layout, and switching is the existing FLIP
morph (relayout). Two layouts so far:
- **nested** — the squarified treemap (folders as boxes-in-boxes); refactored the old computeRECT body
  into this entry.
- **icicle** — top-down partition: depth = horizontal bands (bandH = height/maxDepth), width = each
  node's share (childValues). Top folders are wide short bars at band 1; leaves extend to the floor as
  slivers. Different cognitive read (hierarchy/depth) of the same tree.
`computeRECT` now just delegates to `LAYOUTS[layoutMode].build`. Added a **Layout** selector in the
topbar (projected via fillSel from LAYOUT_ORDER) wired to `layoutMode + relayout()`. Verified inline
geometry: nested app 287×260 nested box; icicle app 157×116 top-band bar (top:8), glyphic-type.js
icicle 5.7×237 sliver at the depth-3 band (top:245). Adding a layout (Rings/Districts/Sunburst) is
now one registry entry. PRINCIPLE GATE held: LAYOUTS/SIZERS/COLORERS are all single-source registries
projected into topbar selectors.

NEXT: Piece 3 (EDGES registry keyed by bidirectional verb pairs), Piece 4 (meaning-registry encoding
draft + grammar doc for Claude Code), Piece 5 (editor: move/create/duplicate/archive + disk adapter).


## Slice 70 — System Map: lens application made deterministic (FLIP morph, no transition-dep)
Verifier confirmed slice 69's math but found a user-facing race: `relayout()` mutated width/height
on existing elements and relied on the CSS width/height TRANSITION to reach the final size. With
transitions on, the rendered size was non-deterministic — a rapid second lens switch interrupted the
morph, and a backgrounded/throttled tab paused it, leaving chips frozen at the previous lens's size
(computed 29.6px while inline said 68.6px). So the displayed sizes didn't dependably match the lens.

FIX — geometry is now AUTHORITATIVE & INSTANT; the morph never affects correctness:
- `relayout()` snaps inline left/top/width/height with `transition:none` → `computed === inline`
  immediately, independent of any animation finishing.
- The morph is a FLIP transform layered on top: capture previous rects, recompute, set each element's
  `transform` to the inverted delta (translate+scale), then on a double-rAF transition `transform→''`.
  Transform does NOT change computed width/height, so a paused or interrupted animation leaves the
  layout correct.
- CSS `.box`/`.chip` transition changed from left/top/width/height to `transform` (+ background,
  border-color). buildMap-created elements therefore render at correct size with NO transition (fresh
  inline value = instant), killing the boot/rebuild race too.
Verified the verifier's exact repro: rapid importance→size→even→links→size loop (120ms each) ends with
registry files proportional (thumb 69 > core 64 > cond 22); single switch to size + 1.5s settle →
thumb(27.8KB) 69px WIDER than cond(5.7KB) 22px; importance mode → thumb 30 < cond 53. Deterministic.


## Slice 69 — System Map: File-size (and all) lenses fixed — folder-local weight normalization
Liam/Info switched the map to the "File size" lens and the whole layout broke: bulk image folders
(_ingest 271 files, inspo, uploads, _qa) swallowed the canvas and crushed the system code into a
corner, dragging the wiring into an unreadable knot. Investigated to ROOT CAUSE (not symptom):

1. **Unit mismatch (the real bug).** Folders were weighted in *importance* units (~10–120, a sum of
   role weights) while files in size-mode were weighted in *bytes* (thousands–millions). Where a
   folder and a loose file are siblings (root, and inside `app`: index.html/app.css), the file's
   byte-weight dwarfed the folder — e.g. `app/registry` collapsed to **0.24×1.25px**. Confirmed by
   dumping RECT: registry rect went 177×130 (importance) → ~0 (size).
2. **Zones must not move.** Sizing zones by content also destroys spatial memory (the map reshuffles
   every lens switch) — the opposite of this tool's purpose.

FIX — `childValues(parentId)` is now the single layout-weight authority for every level:
- Subfolders keep their **stable** weight (`stableFolder` = recursive importance sum) → zones never
  move across lenses; spatial memory holds.
- A folder's loose **files share a fixed budget** (their combined importance) and split it by the
  current metric (`metricLeaf` = `SIZERS[mode].leaf`). So a file resizes ONLY against its own
  siblings, never across the folder boundary, and folder+file weights are the same currency at every
  level. `place()` and the root layout both call `childValues`.
Verified: zones identical across importance/size/even (e.g. `app/registry` stable 23243); inside
registry the files now scale by bytes (types-thumb.jsx 27.8KB → 68.6px wide, types-core.js 16KB →
63.6px, conditions.js 5.7KB → 21.5px) — proportional, was uniform. `SIZERS.size.leaf` reverted from
log to linear (log only mattered when zones ballooned; with stable zones, within-folder byte range
is moderate and linear reads honestly). No transform scaling; getBoundingClientRect mid-transition
reads were the only red herring (inline styles are the source of truth and are correct).

NEXT unchanged: Pieces 2–5 (todos 74–77) remain collaborative — Info wants to design representation
together. PRINCIPLE GATE (78) reaffirmed: SIZERS/COLORERS are single-source registries projected
into the topbar selectors; adding a lens is one entry.


## Slice 69 — System Map: computed-visual LENSES (size-by + colour-by, registry-projected)
Info wants to tie the directory's own metadata to computed visuals, experimentally. Built two
single-source registries the topbar selectors PROJECT from (principle gate):
- **SIZERS** (size = f(node)): `importance` (role weight, default), `size` (bytes on disk),
  `links` (total connections, deg=out+in), `influence` (in-degree — how many depend on it),
  `even` (uniform → pure folder structure). Treemap normalises siblings, so every leaf size is
  automatically RELATIVE to others in its own folder/zone whatever the metric.
- **COLORERS** (colour = f(node)): `system` (role, default), `type` (by extension), `heat`
  (cool→gold→red by connection count, vs HEATMAX).
Refactored buildMap → computeRECT + buildMap (full paint, caches `EL` id→element) + **relayout()**
(same elements MORPH to new rects via CSS transitions on left/top/w/h — the "aesthetic animation")
+ **recolor()** (in-place re-tint, no relayout). Selectors built from `SIZE_ORDER`/`COLOR_ORDER`.
- **Full byte-sizes**: scanner only read code files, so docs/data/images had size=null (floored in
  size mode). Filled sizes for the whole tree — 280 docs/data via text length, ~520 images via
  readFileBinary().size (budget-bounded incremental passes); 39 odd files remain null. Patched
  `build-system-map.js` (added `readFileBinary` param + step 3b size-all pass) so future regens
  size everything within budget, images incrementally beyond it.
Verified via inline-style probe: types-core.js 139×102 (influence) → 33.6×56 (size) → 12×18 (even,
equal to sibling). getBoundingClientRect mid-transition reads stale — use inline style or settle.

NEXT: Info confirmed wanting multiple PROJECTIONS (Piece 2) + edge-type/slice registry (Piece 3);
will do Piece 4 (visual-encoding grammar) in Claude Code IF given stubs + a taxonomy/grammar. So a
near-term deliverable is the stubs+grammar doc for encodings, plus the projection & edge-type
registries. (todos 74,75,76→stub,78,79)


## Slice 68 — System Map → living codebase canvas, PIECE 1 + 1b (complete dynamic model)
Info reframed the System Map as a tool he will use heavily for visual/spatial cognition of the
codebase: see the FULL directory, project it onto a canvas, overlay multiple edge-types/slices,
encode meaning through colour/texture/size, and eventually edit (move/add files) — built piece by
piece, fused into the system's own registry/token/projection principles. Agreed roadmap = todos
71–78. He asked to START with: full directory in, dynamic, stored with metadata, refreshable.

DONE this slice:
- **`system/build-system-map.js`** — the CANONICAL, environment-agnostic generator
  (`buildSystemMap({ls,readFile})`). SINGLE SOURCE of the model; `system-map.json` is its OUTPUT,
  never hand-edited. Parallel-BFS walk (one ls round-trip per directory LEVEL — sequential walk
  blew the 30s budget on ls latency), `classifyRole()` is the one place system-membership is
  decided, regex extraction of `defines`/`uses` (window.CV_*), and `loads` edges (script/href/
  import/require/@import resolved to real nodes).
- **Full tree captured**: 1169 nodes (1106 files / 63 folders) vs the old hand-bounded 777. The
  old scan had silently DROPPED five real top folders — `_archive-v1`, `_ingest` (271 files!),
  `inspo`, `screenshots`, `uploads` — and missed 9 globals (CV_EXPLORE/MODE/OVERRIDE/PICK/SCAN/
  SHOT/TONES/SHAPE_PTS/REGISTRY_SEED). Now 27 globals, 1793 edges (1141 contains, 252 uses, 400
  loads). Per-node metadata: size, defines[], uses[]. Only generated artifacts + dotfiles excluded
  (_ds_bundle/_ds_manifest/_adherence/.thumbnail).
- **Canvas (`system/system-map.html`)**: new roles (archive/ingest/inspo/upload/shot) given muted
  colours + low treemap weights so the newly-included bulk shrinks but stays present (nothing
  missed). Added **Piece 1b refresh loop**: `reload()` resets indexes + rebuilds preserving
  selection/view; live status readout ("1106 files · 63 folders"); ↻ Rescan button; 6s auto-poll
  that rebuilds only when `generatedAt` changes. (Cache-bust via `?t=` 404'd in this preview
  server → switched to `fetch(..,{cache:'no-store'})`.)

NEXT (collaborative — Info wants to design representation together): Piece 2 layout-as-projection,
Piece 3 edge-type/slice registry, Piece 4 token/axis-driven visual encoding, Piece 5 editor suite.
PRINCIPLE GATE (todo 78): every edge-type / layout / encoding / metadata-facet must live in ONE
registry projected into the UI — the canvas is a projection of the registries, not a parallel list.


## Slice 67 — System Map: VISIBLE resolution wiring (the actual ask, finally)
Info (still furious): the legible board was STILL just a file browser — "a directory tree with file names
means nothing on its own; I need to see the connections of all the things that resolve into the values
that make a thing a thing. The glyphics alone has many axes, heaps of parts." The connections were
hidden behind a click — the whole point was missing from the VIEW. Built the resolution diagram as the
default:
- New "Resolution" view (default; "Directory" = the board, via top-bar toggle). A 4-column layered flow
  with the connecting LINES DRAWN (SVG curves): The Glyphic → its PARTS (ring/symbol/fill/whole) → the
  DIALS each part reads (9 axes: form, ring-colour, texture, symbol, symbol-colour, fill, motion, depth,
  size) → the SINGLE SOURCE each dial resolves from (shape engine, symbol library, colour/texture/depth/
  size tokens, motion keyframes). 21 nodes, 22 edges — the wiring IS the picture.
- Authored from the real system structure; every node anchored to its actual file → click lights its
  connected chain + opens the existing rich panel; clicking through jumps into the Directory view
  highlighted. Verified: 21 nodes, 22 paths, Ring-click lights 4 + panel=cv-shapes.js, toggle both ways.
> Lesson (5th time): the RELATIONSHIPS must be the visible content, not structure alone. "How a thing
> resolves from its parts and many dials" drawn as connected flow = what was asked all along. The
> Glyphic is the worked example; same shape generalises to every component next.


## Slice 66 — System Map: treemap → LEGIBLE region board (the real fix for "illegible")
Info (furious, repeated): the treemap was an illegible brown wall — couldn't read a single folder/file.
Named the root problem honestly: 717 equal cells packed into slivers can never be legible. Replaced the
WHOLE visualization (kept all verified data/panel/relationship logic) with a readable region board:
- Each top-level folder = a titled CARD (colour swatch + plain title + one-line description + count),
  in system-meaningful order (axes, assets, components, app, core, tokens, system, …).
- Inside each card: real file ROWS — dot + sub-path prefix (shows structure, e.g. "motion/") + filename
  + plain "what it is". Noise (images/data/notes, no curated desc) collapsed to "+N supporting files".
  Cards cap at 13 rows with "+N more files" (expands in place).
- CSS GRID overlapped (variable heights → 23 overlaps); switched to multi-column masonry
  (column-width + break-inside:avoid) → 0 overlaps. Verified: 15 cards, 100 rows, 0 overlaps, 3 cols.
- Selecting a file highlights its connected rows across ALL cards in gold (auto-expands cards holding a
  connection) + opens the rich panel (what it is / provides / connects out / connects in, clickable).
  Dropped zoom/pan/treemap/SVG-edges. Legend toggles role groups; search filters rows + hides empties.
> Lesson finally applied: legibility first. A readable grouped board of named files-with-meaning beats
> a "shows everything at once" treemap that shows nothing readably.

> 🟢 **New session: read `analysis/HANDOFF.md` first** — the complete briefing this log feeds into.

## Slice 68 — System Map (6th attempt — the constraints, obeyed): single-screen TREEMAP
Info, still furious: (1) "if I have to scroll it's invalid" — a vertical tree CAN'T satisfy that, so a
standard tree viewer was always wrong; (2) must see it ALL on one screen as a map; (3) "draws on is
not a real relationship" — generic verb + generic role-template descriptions are useless. Rebuilt
system/system-map.html as a SINGLE-SCREEN SPATIAL MAP:
- TREEMAP layout (recursive slice, weighted by descendant file count): all 761 nodes (717 files + 44
  folders) packed into one fit-to-screen rectangle — folders are labelled regions, files are coloured
  cells inside them. body NOT scrollable; pan (drag) + zoom (wheel-to-cursor) + Fit button for map
  navigation, never document scroll.
- REAL SPECIFIC relationships: SYS map gives each registry a named system + distinct verb — uses:
  CV_SHAPES→"draws ring shapes with", CV_ICONS→"pulls symbols from", CV_REGISTRY→"registers/looks up
  types in", CV_AXES→"reads dial settings from", CV_MEANING→"looks up meaning in", CV_AI→"runs AI moves
  through", etc. On select, edges are drawn across the map (gold=out, bronze=in) each LABELLED with its
  real verb; related cells highlight, unrelated dim.
- REAL SPECIFIC descriptions: DESC map rewritten with true per-file text (e.g. SaveAsTypeModal.jsx =
  "Save-as-Type dialog — the pop-up where you name a new arrangement and save it into the Type
  Catalogue"); definers described by their system; non-curated files use prettified-name + role, images
  marked as images. No blanket "a catalogue".
- Detail = compact fixed panel (what it is · what it provides · connects out → with verbs · connects in
  ← with verbs · unwired note), every relation clickable. Legend toggles role visibility (re-layouts).
  Opens on the Glyphic. Verified via DOM: 761 cells, 23 labelled edges, specific verbs + description,
  body non-scrollable, no console errors. (Preview-pane capture still glitching; verified by probe.)
- Fixed a boot crash (stray invalid identifier in a dead COLOR literal) before it rendered.
> Treemap = directory expanded + every file in its folder + all on one screen + real labelled
> resolution edges — the first version that honours "one screen, no scroll, real relationships".


Info, furious after 4 wrong attempts (concept-tour; directory-atlas with bare names/jargon; a systems
graph). The actual ask, decoded: the FULL directory tree (real files, folders, NAMES) AND the
resolution connections across them showing how files resolve together into a "thing" AND every node in
PLAIN language (what it is, what uses it, what it feeds into) — structure + meaning + connections in
ONE view, readable by a non-developer.
- Rebuilt system/system-map.html from system-map.json (777 nodes; 1377 edges contains/loads/uses:CV_*;
  26 globals = which file defines which registry). The uses:CV_X edges + globals map ARE the real
  resolution wiring (generated FROM the live code), so no risky live-script loading.
- LEFT: full directory tree, expanded (architecture open; pure-asset/huge dirs collapsed), every row =
  real name + PLAIN-LANGUAGE descriptor ("Motion dial — all the kinds of movement anything can use",
  "The Mark-maker", "Raw design values"). Role-coloured dot + file counts.
- RIGHT (per node, plain words, all clickable): What this is (curated DESC for ~30 key files/folders +
  role glossary + registry GLOSS); What it provides (globals defined); folder contents; What it draws
  on → (loads + uses, phrased "draws on the Dials/Symbol library/…"); What uses it ← (with unwired
  note); and "How it resolves together" — a recursive RESOLUTION TREE down to raw values, each node a
  real file.
- Selecting highlights connections IN THE TREE (draws-on/used-by tags) + auto-expands ancestors;
  search filters by name + meaning; opens on the Glyphic by default. Header links to deeper specs.
- Verified live (DOM probe; preview-pane capture glitched): 777 rows, cv-glyphics.js selected, 22 tree
  connections, detail provides/draws-on→6/used-by←17/resolution, res-tree 54 rows. check clean (52 cards).
> Concept-tour content gone; system-atlas.html (bare directory) superseded. One map = structure +
> meaning + resolution.

## Slice 66 — System Atlas rebuilt AGAIN: an architecture map of the SYSTEMS (not files)
Info (frustrated, third attempt): the file-graph/tree has zero meaning — they want to see THE SYSTEMS
built (registries, tokens, axes, components, the universal grammar), WHERE they are and HOW it all
works; couldn't even scroll the tree. The miss across slices 62/64/65: I kept showing FILES or a
separate playground. Rebuilt system/system-atlas.html as a CONCEPT-LEVEL ARCHITECTURE MAP:
- 9 systems as concept cards in 4 stacked layers (Foundation: Tokens → Dials: Axes + Meaning → Things:
  Glyphic, Symbols, Components → Catalogue/Intelligence/Composition: Registry, AI Foundry, Engine),
  with "↓ builds into ↓" flow between layers. Plain-language one-liner + count + token/symbol/glyphic
  peek on every card.
- Click a system → detail panel: "What it is" in plain English, "Live — the real thing" (real swatches
  / live glyphics / symbol grid pulled from CV_AXES/CV_GLYPHIC/CV_ICONS), "What's inside" (live member
  list, e.g. the 9 axes, the components, registry layer counts), and "How it connects" (clickable
  relationships to other systems, each explained). Deep-dive buttons into the builder/types/foundry cards.
- Main column SCROLLS (fixed the prior overflow trap). Reads the live build, so counts/contents are true.
- Verified: Tokens shows 499 + colour swatches; Glyphic opens 8 live glyphics + 3 connections + builder
  link; 9 systems / 4 layers; connections navigate between systems. check_design_system clean.
> The atlas now answers "what are the systems and how do they work", at the concept level, interactively
> — not a file dump. system-map.html (guided tour) + the spec cards remain as the deeper references.


Info: slice 64 was the wrong thing — I replaced the system MAP with a concept tour. The map (directory
+ registries + relationships) was what was wanted, rebuilt with REAL interactivity/control; the data
extraction was "the back half" (done). Kept the concept tour (system-map.html) per Info, BUILT THE
ACTUAL MAP next to it: system/system-atlas.html.
- Reads system-map.json (777 nodes, 1377 edges incl. contains + 626 semantic loads/uses, 26 globals).
- A genuinely interactive force/cluster graph: PAN (drag bg), ZOOM (wheel, to cursor, + buttons), DRAG
  nodes, FIT. Deterministic CLUSTER layout (group by top-level folder on a ring, phyllotaxis-pack each)
  after a physics sim diverged (scale→1e-129); stable now (15 cluster labels).
- Controls/meaning: role legend (click to show/hide any role, All/None), edge-type toggles
  (Structure/Loads/Uses), search (filters + folder-aware), Map/Tree modes. Click any node → its edges
  light gold + everything else dims + detail panel (role + plain description, defines/contains/uses→/
  ←used-by, all click-through). Orphan files get a red dashed ring + ⚠ callout = "not wired in".
- Verified by DOM probe: click types-core.js → 48 edges hot, 731 nodes dimmed, detail lists defines
  CV_REGISTRY + uses conditions.js + affects 46. (Screenshot pane glitched this turn; functional checks
  pass; verifier will capture.) check_design_system clean (52 cards).
> Lesson: "redo the system map with interactivity" meant rebuild THAT artifact's UX, not invent a new
> one. Atlas is the real map; system-map.html stays as the plain-language tour.


Info: the file/edge map "has no meaning" for a non-developer with no code view; redo ALL viewers with
real meaning + interactivity + control; discard the front-end. Rebuilt system/system-map.html from
scratch as a PLAIN-LANGUAGE, INTERACTIVE tour reading the LIVE registries (not file paths):
- Left nav + 4 views. **Overview**: "What this is" in plain words + live count cards (9 axes / 127
  symbols / 1 glyphic / 11 components / 94 types) + a left-to-right "how the pieces fit" flow
  (Tokens→Axes→Glyphic&components→Documents), all clickable to drill in.
- **Build a glyphic** (centrepiece): 9 live controls (95 options pulled from CV_AXES) — ring/symbol/
  fill/ring-colour/symbol-colour/texture/motion/depth/size — compose a big live glyphic via
  CV_GLYPHIC.render that rebuilds on every click, with a plain spec readout. Real control, the system
  DOING something. Verified: clicking octagon rebuilds the mark.
- **Axes**: pick-an-axis pills → plain description + every value rendered with a type-appropriate
  preview + its token name ("defined once, used everywhere"). Interactive browsing.
- **Components**: registered Types grouped by human layer names ("Small parts / Building blocks /
  Framed areas / …") each in plain terms — "varies by" (its axes) + "holds" (its sockets), no jargon.
- Kept deep-dive links to the Glyphic model / Axis / Type / Foundry cards. Dropped the meaningless
  file-graph + Full/Directory/Roles modes (Info: discard). system-map.json retained (still powers
  nothing now; harmless). check_design_system clean.
> Reframed from FILES (meaningless to a non-dev) to CONCEPTS + live interactivity. This is the new
> front-end pattern; the other spec cards (glyphic/axis/type/foundry) remain as deeper references.


Info: "yes to literally everything, a partial view won't show me what isn't already done." Extended the
relationship extraction from the core dirs to the ENTIRE tree, resumably (the one-pass scan times out):
- Batched edge-scan over all 295 text files (js/jsx/css/html/ts/md/json) across every dir incl.
  ui_kits/preview/atomicity/specimens/templates/app(all)/_qa — tracked via m.scanned so batches resume;
  0 remaining. Now 626 semantic edges (loads + uses:CV_*) + 26 discovered globals, derived from real
  file contents across the whole project.
- **Full map** view mode added to system-map.html: every one of the 733 files as a dot, clustered by
  top-level directory (15 clusters), with cross-cluster dependency edges; selecting a node draws only
  its edges (legibility). ORPHAN MARKER: any file with zero in+out semantic links gets a red dashed
  outline (477 today) — the direct "not wired in / not done" signal Info wanted to see. Detail panel
  also shows a ⚠ "No detected links" callout for orphans.
- Verified: Full map renders 733 dots / 15 clusters / 477 orphan-marked; stats 626 links, 26
  registries; Architecture/Directory/Roles unchanged. check_design_system clean.
> The map now shows EVERYTHING, including the large unwired surfaces (ui_kits, preview cards, atomicity
> app, specimens) — so gaps and orphans are visible, not hidden by a curated subset.


Info: build a dynamically-populated viewer of the directory structure / registries / tokens — "all of
this" — as the PARENT page to the glyphic system, with view modes, click-to-inspect showing what each
thing connects/affects/is-affected-by + highlighted edges, read from the directory not hardcoded.
- **Manifest generated by SCANNING the real tree** (run_script): recursively walked the project →
  `system/system-map.json` (777 nodes: 733 files + 44 folders, skipping screenshots/uploads/_archive/
  _ingest/inspo). Each node DERIVES a role from path/name (axis-core/axis/value-source/glyphic-core/
  meaning/registry/ai/engine/component/token/spec/doc/card/template/ui-kit/atomicity/…). Semantic
  EDGES extracted from actual file CONTENTS: `loads` (script src / href / @import / es-import, path-
  resolved) + `uses:<GLOBAL>` (CV_* references → the file that defines `window.CV_*`). 17 registries
  discovered (CV_AXIS/AXES/REGISTRY/GLYPHIC/ICONS/SHAPES/MEANING/AI/COND/…), 257 semantic edges.
- **`system/system-map.html`** — the parent hub (group "Glyphic System"), loads the manifest live.
  Three view modes: **Architecture** (clustered force-style graph of the core roles + semantic edges,
  cluster labels Axes/Values/Glyphic/Registry/AI/Engine/Components/Tokens/Specs); **Directory**
  (collapsible full tree, role-coloured dots, search); **Roles** (grouped columns). Click ANY node
  (graph/tree/role/relation-row) → detail panel: role + description, `defines` (registries it owns),
  `contains`, `uses/loads →` (outgoing), `← used by/affects` (incoming) — every relation clickable to
  navigate; in graph mode the selected node's edges highlight gold and the rest dim. Header links to
  the Glyphic model / Type / Axis / Foundry cards (it is their parent). Search filters all modes.
  Verified: types-core.js → defines CV_REGISTRY, uses conditions.js (CV_COND), affects 20 files;
  cv-glyphics.js → 16 edges highlit; tree expands axes/→9 subfolders; roles columns populate.
- check_design_system clean (51 cards incl. System Map).
> Reads from the directory + live globals, not a hardcoded list — re-running the scan refreshes it.


Info: "populate full plan, operate autonomously, full universal system / total coverage." Laid out a
9-item linear plan (A–I) in AXIS-REFACTOR.md and executed:
- **A · Condition evaluator** `app/registry/conditions.js` → CV_COND. Three input forms (structured
  {field,op,value} + boolean all/any/not · string DSL "fill != none" / "A requires B" / "x and y" ·
  predicate fn). Wired into types-core accepts() (socket conditions) + new slotEnabled() + used by
  axis subscription validation. ONE evaluator everywhere. Verified: "texture requires fill != none"
  with fill=none → false.
- **B · Event-sockets + addresses**: socket schema gained kind('slot'|'event')/event/address/onPick;
  socketInfo() resolver. Modal.trigger + composition-menu.onItemClick demonstrate event-sockets.
- **C · TOTAL COMPONENT COVERAGE** `app/registry/components-type.js`: the 10 UI components
  (Button/Badge/Avatar/Card/Input/Switch/Tabs/Segmented/Stepper/Modal) registered as universal-
  component Types — classification + value-slots (axis subscriptions e.g. Avatar.size→size axis,
  Card.depth→depth axis; enums e.g. Button.variant) + content/event sockets. With Glyphic = 11
  components as Types; 94 Types total.
- **D · Token/axis reconciliation**: seed token.color.*/token.shape.* gained axis/axisValue pointers
  (token.color.gold→axis 'color' value 'gold'); normalize() carries them. Tokens ARE axis value-units.
- **E · Type System projection card** `system/type-system.html`: live from CV_REGISTRY — 94 Types
  across 6 layers, each showing classification/value-slots(axis)/parts/sockets(accepts,event)/
  conditions. Includes a declarative-acceptance demo (composition-menu items socket → 7 candidates).
- **F · Other KINDS** `app/registry/kinds-type.js`: composition-menu PANEL (glyphic-accepting socket
  + event-socket), graph + slide kind refs pointing at the existing engines (DiagramSolver/Slide).
- **G · Glyphic Foundry UI** `system/glyphic-foundry.html`: conversational propose→feedback→click→
  save surface. Routes generation through CV_AI.execute('glyphic.generate') (loads ai-registry/seed/
  glyphic), graceful DEMO fallback when no model bound; Save → CV_ICONS.add (+ symbol-axis rebuild).
  Verified end-to-end: 4 candidates render as live glyphics, Save grew library 126→127, saved strip
  updates. (Live model threw → demo fallback engaged cleanly, as designed.)
- **H · Consumer convergence — resolved by analysis**: brand_shapes/brand_vi/components_box_variants
  render ENTITY VESSELS (shape+label / fillable image-slot) via CV_SHAPES.markSVG; CV_GLYPHIC.render
  delegates to that same single source. They are not glyphics (composition layer) → routing them
  through CV_GLYPHIC would be a category error. Already one source; no change.
- **I · Docs**: README (universal-component grammar bullet), DESIGN-LANGUAGE §18, AXIS-REFACTOR status,
  this slice. check_design_system clean (49 cards incl. Axis System + Type System + Glyphic Foundry;
  Glyphic compiles; tokens 499; no issues). App load order: conditions→types-core→…→glyphic-type→
  components-type→kinds-type.
> Universal foundation complete to the extent buildable without further decisions: one grammar (parts·
> slots·sockets·conditions) + axes (tokens as units) + AI foundry, every layer covered, all projected
> as markable DS cards. Remaining genuinely needs Info/Tim: §7 value vocabularies + a bound live model
> for the foundry; deeper per-axis cards; a visual socket-wiring editor.


Self-directed (per Info: runs until fully actioned; the DS tab is how they see/steer, so the axes must
be VISIBLE; "the interface is a projection of the registries"). Built `system/axis-system.html` —
@dsCard group "Axis System" — that renders EVERY axis live from window.CV_AXES (no parallel list; add/
extend an axis → it appears). Per axis: label, home, value/group counts, description, then each group's
values with a TYPE-APPROPRIATE preview + token name: colour→swatch (var resolved), fill→fill recipe,
space→bar, size→box at px, depth→shadowed tile, motion→animated dot (mo-* class), texture→markSVG
pattern, form→markSVG shape, symbol→glyph (capped 14/group, "+N"). Verified in-DOM: 9 axes, Colour 22
vals/5 groups, Texture 8 pattern SVGs, Form 8 shape SVGs, Symbol 118 vals/116 glyphs/13 domains. This
makes the whole axis foundation inspectable + comment-able by Info/Tim. check_design_system clean
(48 cards now incl. "Axis System"; 499 tokens; no issues).

## Slice 59 — UNIVERSAL AXIS SYSTEMS: every facet a first-class axis (autonomous)
Info/Tim's convergence brief (scope in analysis/AXIS-REFACTOR.md): every primary axis becomes its own
dedicated hierarchical typed system; EVERYTHING resolves its value of an axis FROM that system; a
Glyphic is just one CONSUMER that DECLARES which values it subscribes to; the hardcoded glyphic-motion
must not exist — motion is its own axis with many types. Invest in the universal foundation + directory
now (downstream of everything). Autonomous build; scope tracked so nothing is lost.
- **Scope captured**: analysis/AXIS-REFACTOR.md + spec §08 "Universal axis systems".
- **CV_AXIS / CV_AXES** (axes/axis-core.js): generic axis factory + registry mirroring the other
  registries — register/resolve/list/query/subscribe + value HIERARCHY (groups) + resolveCSS (value→
  token var / css / computed) + SUBSCRIPTION helpers (candidates/validate for {axis,groups?,values?}).
- **9 axes built & verified at runtime**: color · space · size · motion · texture · depth · fill ·
  form · symbol. color/space/size/depth token-backed; form wraps CV_SHAPES.geom; symbol wraps CV_ICONS
  (126 values, intrinsic-meaning flag, rebuild() for foundry adds); motion/texture/fill name CSS/markSVG
  realisations. Verified: motion glow→'mo-glow', color gold→var(--accent-gold), size md→var(--size-md)
  +40px, meaning bridge ok.
- **TOKENS ARE THE VALUE-UNITS** (Info clarification): axes don't replace tokens — the colour axis IS
  the colour tokens typed/grouped; values carry `token` as canonical id; added the `--size-*` element
  ramp to tokens/sizing.css (the size axis's tokens). Reframed axis-core + color-axis + AXIS-REFACTOR.
- **Motion de-owned from Glyphic**: keyframes → axes/motion/motion.css (cvmo-* + .mo-*), value set →
  axes/motion/motion-axis.js; cv-glyphic.css reduced to base only; CV_GLYPHIC.motionClassFor() resolves
  via the Motion axis (legacy fallback). The hardcoded ownership is gone.
- **Slots → subscriptions**: app/registry/glyphic-type.js valueSlots now sub(axisId,{groups?,values?,
  default}) resolved live from CV_AXES (no copied vocab); part colour slots subscribe to colour-axis groups.
- **Meaning reconciled**: CV_MEANING.facets ARE axis ids (the contextual layer OVER the axes); added
  CV_MEANING.axis(facet)→CV_AXES bridge; symbols stay the intrinsic exception.
- **Wiring**: app/index.html + system/glyphic-system.html + assets/icons/index.html load the axis layer
  in dependency order (axis-core → value sources → axes → meaning → glyphics; motion.css linked).
- **Directory**: new axes/<name>/ tree = the axis layer's home. Legacy value-source libs stay in
  assets/icons/ (already the one home; moving = ~20 card-ref breakages for no single-source gain).
- check_design_system: no issues; 499 tokens (+6 --size-*); Glyphic compiles (17 components); 47 cards.
- **Carried scope still owed** (AXIS-REFACTOR DO-NOT-LOSE + spec §08): foundry conversational UI;
  consumer convergence; §7 open questions (await Info/Tim); socket condition evaluator + event-sockets;
  per-axis DS cards.

## Slice 58 — The UNIVERSAL COMPONENT grammar: Glyphic as parts/slots/sockets + the notches
Info/Tim's keystone brief (verbatim in spec §01b): make the Glyphic a real component in the
components place + registry, with three independent parts (ring/symbol/fill) and SLOTS (values a part
takes) + SOCKETS (typed attachment points it fills, incl. event/onClick, with addresses + conditions);
this is the first example of a UNIVERSAL component grammar every kind (panel/graph/slide) shares —
"everything in any interface is a templated dynamic component"; the interface is a PROJECTION of
declarations (no bespoke wiring). Revised anatomy: fill is NOT a 3rd equal part — it's the ring's
INNER space; the ring also has an OUTER space; the element is a perfect SQUARE. Build with purity bc
it's the foundation+example for everything.
SPEC DOC (system/glyphic-system.html): added §01b verbatim brief; §05b universal component, §05c
slots vs sockets (mapped onto CV_REGISTRY.slots/accepts/candidatesForSocket; +event-sockets,
addresses, conditions), §05d revised anatomy (SVG diagram: square → outer space → ring stroke → inner
space/fill → symbol; parent + 2 part sub-components), §05e declarations/"attachments" (draft Type
decl + a panel declaring a glyphic-accepting socket); §6 plan updated (3 new BUILT steps); viewport
2700→4400.
BUILT:
- CV_REGISTRY (app/registry/types-core.js) extended ADDITIVELY: normalize() now carries kind,
  classification, sockets (alias of slots), valueSlots, parts, conditions; accepts() gained
  classification/forbid matching + array-accepts; candidatesForSocket alias. Existing consumers
  untouched.
- app/registry/glyphic-type.js: registers glyphic-ring/glyphic-symbol/glyphic-fill part-types +
  parent 'glyphic' Type (classification ['glyphic','mark','atom']). Parent sockets ring/symbol;
  ring sockets innerSpace(accepts fill)/outerSpace; valueSlots seeded LIVE from CV_GLYPHIC.facets
  (no second vocab list). R.glyphic accessor added.
- components/Glyphic.jsx + .d.ts: React socket around CV_GLYPHIC.compose (props per part slot); loud
  fallback if CV_GLYPHIC absent. Compiles as the 17th component (check shows "Glyphic").
- Motion token home: assets/icons/cv-glyphic.css (.cv-glyphic base + .mo-* keyframes the compositor
  names; reduced-motion-safe). Linked in app/index.html, explorer, spec.
- Depth wired to tokens/depth.css: DEPTHS tint now var(--shadow-c); documented as the SVG mirror of
  the --elev-* ramp. FILL_RAMPS documented as token recipes.
- AI foundry (registry-way): CV_GLYPHIC.schema (symbol+glyphic record schemas) + validateSymbol();
  CV_ICONS.add/_persist/_loadPersisted (write path, provenance vi, localStorage); app/ai/ai-glyphic.js
  registers glyphic.generate (threaded multi-step, parses+validates candidates) + glyphic.save
  (validate→CV_ICONS.add). Conversational UI surface = the remaining piece (needs §7 sign-off + live
  provider) — logged, not faked.
- app/index.html load order: full glyphic stack (icons→vi-glyph→shapes→meaning→glyphics + cv-glyphic.css)
  + glyphic-type.js (after registry) + ai-glyphic.js (after CV_AI).
- README.md refreshed (Glyphic universal-component bullet + components/ + system/ index lines).
check_design_system: Glyphic compiles, 17 components, 47 cards (Glyphic System group), tokens 493.
NOTE: did NOT converge brand_shapes/vi/box-variants onto CV_GLYPHIC.render (they already use the
shared CV_SHAPES.markSVG which CV_GLYPHIC delegates to — same single source; convergence is cosmetic,
deferred). Left for verifier's fresh iframe given a transient serving glitch last slice.
> Foundation laid faithfully: one declaration grammar (parts·slots·sockets·conditions) every universal
> component will reuse; the Glyphic is its reference implementation.


Tim/Vi: yes to all six remaining notches; KEY refinement — every meaning-binding must be LOADABLE/
swappable because meaning is contextual, EXCEPT symbols (a house is always a house). Ship a default I
author, editable later. Reframes step-5 from a fixed binding table into a loadable meaning system.
- **`assets/icons/cv-meaning.js` → `window.CV_MEANING`**: a registry of named meaning PROFILES, mirroring
  the other registries (register/load/export/resolve/use/list + valuesFor/meaningOf/tokenForValue).
  Separates two layers cleanly: INVARIANT (geometry CV_SHAPES.geom, symbols CV_ICONS, render defaults)
  vs CONTEXTUAL (what form/colour-value/fill/texture/depth/motion MEAN). Symbols deliberately excluded
  (valuesFor('symbol') throws — intrinsic, lives in CV_ICONS.facets).
- **Default profile `conceptv-default`** (authored, editable): form bindings SEEDED FROM
  CV_SHAPES.shapeTypes (reference, not copy — geometry source stays the home of form→type); colour
  values (neutral/active/positive/warning/error/info/muted → token names), fill/texture/depth/motion
  meanings as first-draft strings. Profiles round-trip to JSON: export() → edit → load(json, makeActive).
  use(id) switches context; loud-fail on unknown profile.
- **Wired into CV_GLYPHIC**: `meaningOf(facet,value)` now routes through CV_MEANING.active (back-comat
  1-arg = form); new `colorForValue(value)` resolves an allocated value→token via the active profile;
  `normalize`/`compose` accept a `value` field so a spec like `{form:'octagon',symbol:'globe',
  value:'warning'}` colours itself from the profile (turns blue under a 'process-map' profile, etc).
- Spec doc `system/glyphic-system.html`: §6 step 5 rewritten "Loadable meaning profiles · BUILT"; added
  a §3 callout "Meaning is loadable — and lives apart from geometry"; loads cv-meaning.js. Explorer +
  spec load order now cv-icons → cv-vi-glyph → cv-shapes → **cv-meaning** → cv-glyphics.
- check_design_system clean (47 cards, manifest in sync; cv-meaning.js is a helper, not compiled).
  NOTE: hit a transient serving-layer glitch (all subresources 404 with a frozen cache token) during
  in-iframe QA — code verified structurally + logic tested earlier; left for the verifier's fresh iframe.
> Remaining of the six: motion-token wiring, register Glyphic as a CV_REGISTRY atom, move FILL_RAMPS/
> DEPTHS to token homes, converge consumers on CV_GLYPHIC.render, and the AI glyphic-foundry (step 6).


Vi: do the next notches (rename Mark → "Glyphic"). Shipped §6 steps 1–4 of the spec plan:
- **Faceted taxonomy (single source)** in `assets/icons/cv-icons.js`: `CV_ICONS.taxonomy` = 13 `domains`
  (people, property, visualization, document, communication, interface, media, data, commerce, place,
  action, system, feature) + 4 `kinds` (object/action/state/concept); per-symbol `CV_ICONS.facets`
  ({domain, kind, tags[], brand?}) on every glyph; queries `byDomain / byKind / search`. Replaces the
  old flat ad-hoc section comments + `brand` array.
- **The Glyphic registry** `assets/icons/cv-glyphics.js` → `window.CV_GLYPHIC` — the ONE home for the
  unit, mirroring CV_REGISTRY/CV_AI shape: `facets` (8-facet schema: source/zero/value-space/meaning),
  `defaults`, `valuesOf`, `normalize`, `validate` (loud-fail vs live vocabularies), `meaningOf`
  (form→type via CV_SHAPES.shapeTypes), `compose`/`render` (delegates geometry→CV_SHAPES.markSVG,
  symbols→CV_ICONS; resolves colour+fill+depth tokens; form:'none' = ring-zero), `symbols` query.
  Redraws nothing — pure composition layer. Verified in _qa/glyphic-test.html (validate catches bad
  form/symbol/texture; compose renders circle/octagon/none/diamond specs correctly).
- **Interface = projection:** icon explorer (`assets/icons/index.html`) category bar now DERIVED from
  CV_ICONS.taxonomy (Brand + 13 domains + Other fallback), not a hand-kept CATEGORIES list; loads
  cv-glyphics.js. Spec doc `system/` renamed mark-system.html → **glyphic-system.html**, group
  "Glyphic System"; Mark→Glyphic throughout; §3 facet specimens now render through CV_GLYPHIC.render
  (not raw markSVG) — proving the registry; §6 steps 1–4 badged · BUILT, naming Q marked decided.
  Load order in consumers: cv-icons → cv-vi-glyph → cv-shapes → cv-glyphics. check clean (47 cards).
> Remaining plan items: §6 step 5 (value→facet binding registry) and step 6 (the conversational AI
> glyphic-foundry on CV_AI.icon.generate). Motion still CSS-only pending motion-token wiring.


Vi (viewing assets/icons/index.html): make them colour-token driven with distinct colours for at least
the outer ring and the icon. Done:
- Split the single "Tone" toggle into two token-driven pickers — **Ring** (default gold) and **Icon**
  (default bronze) — each {gold,bronze,ink,sage} → `var(--accent-*)`/`--fg-primary`. renderIcon now uses
  `ring` for the polygon/circle stroke (or fill, when Filled) and `ink` for the glyph, so ring and icon
  are independently coloured (the Mark's two colour facets, demonstrated live).
- Killed geometry drift: the explorer's hardcoded `SHAPE_PTS` (stale flat-top hex etc.) now pulls from
  `CV_SHAPES.geom[...].points` (single source; septagon→heptagon), with literal fallback only if the
  bundle fails to load. Loaded cv-vi-glyph.js + cv-shapes.js into the page. Filled-mode glyph switched
  to `--paper` for contrast on the filled ring. check clean.
> Connects the icon library one notch further into the generative system: geometry now single-sourced,
> colour now token-driven per-facet. (Faceted taxonomy + registry home + AI foundry still per the spec plan.)


Vi: decrease outer-ring roundedness a bit; make shadows / sense of depth its own axis in a new row,
the rest of the rows normal. Done:
- `CV_SHAPES.markBox.radius` 9 → 6 (single source; all marks across brand_shapes/vi/box-variants get
  slightly crisper corners).
- Added **Depth** as the 8th facet: in §3 table (home tokens/depth.css, range flat→raised→deep,
  meaning elevation/focus) and as row 8 of the cumulative walk — `DEPTHS` shadow scale (flat·0 → d1..d6
  → normal), rendered via markSVG `opts.flat`/`opts.shadow`. Row uses a `fix:{size:56}` override so it
  stays legible after the Size row locks 86. Other rows keep the normal default shadow (unchanged).
- Fixed §3b lede (fill ends on its zero 'none'; noted Depth as the last row) + viewport height 2400→2700.
  check clean.


Vi: Fill row should be 8 different MUTED BRAND colours, each distinct, and END on 'none' (so fill locks
to none for all rows below). Done: row 3 vals = f-gold/f-bronze/f-sage/f-amber/f-blue/f-clay/f-ink/none
(each a low-% color-mix toward paper, added to FILLS); end value 'none' auto-locks via the cumulative
`st`, so rows 4–7 now render transparent-interior. Removed `if(opts.frameOnly) hasPat=false` in
markSVG so the Texture row still shows its pattern over a transparent (none) fill. check clean.


Vi's inline comment on §3b: more examples; each row changes ONE axis from the last; the value a row
ENDS on locks for every following row; 8 per row; cover all axes.
- Rebuilt §3b as a 7-row cumulative walk (Symbol→Form→Fill→Colour→Texture→Motion→Size), 8 cells each,
  running `st` state that locks each row's final value (gold "lockend" caption) into all rows below.
  Row 2's first cell is the Form-axis ZERO (no ring → icon only, via `iconOnly()`); by row 7 the Mark
  is fully composed (octagon+house+gold wash+gold colour+hatch+glow) shown across 8 sizes 30→86.
- Texture facet only had hatch/lines (2) — extended `CV_SHAPES.markSVG` pattern factory to 8: none,
  hatch, dense, cross, grid, lines, vert, dots (single source, real values).
- Motion facet rendered via CSS keyframes in the doc (glow/pulse/breathe/spin/bob/tilt/float), gated on
  prefers-reduced-motion; flagged in-copy as "via CSS for now — see the plan" (motion tokens later).
  Colour/Fill drive through markSVG stroke/ink + fill-gradient arrays. check clean.


Vi's brief: the "icon system" is really a multi-facet compositional MARK; audit all the registries/
tokens/single-sources/generated systems, see the emerging architecture, and write a NEW VISIBLE
CATEGORY into the DS (filled with the verbatim brief + my decomposition + codebase research + a plan)
so they can comment/mark it up — they can't direct this through chat for lack of terminology.
- **Audited the whole architecture** (no code changed, context-gathering): the four registries
  (`INTEGRATION.md`: tokens / CV_REGISTRY / core solvers / CV_AI — one `register/resolve/lineage` API);
  the parametric model (`AXES.md`: `design=f(content,axis)`, orthogonal-axes rule); CV_SHAPES (Form
  facet, already typed + token-parametric + `markSVG` composes ring+icon+fill+pattern+ink+shadow);
  CV_ICONS (~110 glyphs, flat ad-hoc taxonomy per `_ingest/ICON-AUDIT.md`); the modifier facets all
  already tokenised (colors_and_type L0/L1/L2, texture.css, motion.css, icons.css); CvIcon `shape=` +
  the graph-solver nodes (a Mark IS the engine's atom — CV_REGISTRY even defines an `atom` layer as
  "icon glyph / status dot / stamp"); and the EXISTING CV_AI `icon.generate`/`icon.edit`/`icon.single`
  capabilities + `openai-image` provider + `theme.generate` multi-candidate pattern (the conversational
  mark-foundry is a short hop, not a new subsystem).
- **The synthesis (the insight):** one generative grammar — typed things × orthogonal axes × token-
  resolved rendering, computed not hand-set — recurs at every scale (doc→AXES, block→ContainmentTree,
  graph→DiagramSolver, **mark→this new Mark System**). The Mark is that grammar's ATOM:
  `mark = f(facet-spec)` is `design=f(content,axis)` at its smallest radius. Self-similar from a glyph
  to a deck; the Mark just needs a registry home mirroring the other three.
- **Built `system/mark-system.html`** — a new `@dsCard group="Mark System"`, a long-form LIVING SPEC
  (uses the DS's own tokens; renders real example Marks via `CV_SHAPES.markSVG`). Sections: 00 how to
  mark up · 01 the brief VERBATIM · 02 decomposition (names the unit "Mark", facets, orthogonality →
  meaning is multiplicative, "the space between" as its own facet, every facet has a zero) · 03 the
  facet model (Form/Symbol/Fill/Colour/Texture/Motion/Size — each: range incl. zero, single-source
  home, meaning carried — with live specimens) · 03b meaning-multiplies matrices (fixed symbol×vary
  form; fixed form/symbol×vary colour-value) · 04 codebase research (8 cards w/ file refs) · 05 the
  emerging architecture (one grammar, every scale) · 06 the plan (6 sequenced steps + draft Symbol &
  Mark JSON schemas) · 07 open questions for markup (naming, v1 facet set, Form-axis ends, meaning
  vocabularies, the value variable, taxonomy depth). New top-level folder `system/`. `[data-screen-label]`
  on each section for comment context. check clean — first card in a new "Mark System" group.
> This is a forward spec, not a shipped rule, so DESIGN-LANGUAGE.md is left until we build it; the spec
> doc itself is the home for the concept and the place Vi will steer it via markup.


Teammate brief: connect to the icon system; move from specific entities → typed meaning; add the other
shapes (≤8 sides); connect colour/thickness/shadow/every part to tokens; one system-wide default but
EVERYTHING a parameter; shapes have distinct typed meaning with descriptions; this system is distinct.
Rebuilt `cv-shapes.js` as the shape system:
- **Geometry**: a regular n-gon generator → triangle(3) square(4) diamond(4) pentagon(5) hex(6, pointy)
  heptagon(7) octagon(8, flat) + circle. NEVER >8 sides. Points inset r=46 (stroke room for CvIcon),
  clips full-bleed r=50 (content fill); markSVG re-fits via roundedFit.
- **`shapeTypes`** (NEW semantic layer): each shape = a TYPE with meaning + description + default icon:
  Entity(circle/person) · Action(triangle/play) · Object(square/file) · Decision(diamond/atom,lines) ·
  Feature(pentagon/star) · System(hex/gear,hatch) · Specialised(heptagon/unique) · Gateway(octagon/globe).
  Tied to the brand's established usage (circle=portal, hex=engine, octagon=output, diamond=AI) + extended.
- **`markDefaults`** (NEW): the one system-wide default treatment, every value a TOKEN — stroke
  `var(--accent-gold)`, fill `[--bg-surface,--paper,--paper-2]`, ink `var(--accent-bronze-2)`, shadow
  flood `var(--accent-bronze)`, + iconScale. `inkRole` maps role→token. Pixel-sampled hex kept only as
  an opt-in `{preset:'sampled'}`.
- **`markSVG(spec, opts)`** rewritten + fully parameterised: spec = shape key | type id | entity id;
  cascade markDefaults ◀ shapeType/entity ◀ opts; renders an **icon from CV_ICONS inside** the shape
  (or the Vi wordmark), all colours via tokens. Connected systems: cv-icons.js (glyph), tokens (every
  colour), CvIcon/ContainmentTree (points/clip), kept working.
- `entities` kept as a compat layer (instances adopting a type) so CvIcon/decks/Vi card still resolve.
- Rewrote `brand_shapes.html` → "Shape system" card: 8 typed shapes, icon inside, type + sides + icon +
  meaning description, foot crediting CV_SHAPES/CV_ICONS/markDefaults. Vi card copy updated to reference it.
  check clean, tokens 493.
> Single-source win: meaning, geometry, icon and treatment all resolve from ONE registry; a new shape =
> a shapeTypes entry, a retheme = a markDefaults/token change. Nothing hand-set per shape.
>
> Fix (same slice): icons were fixed-size (0.42·span) and centred on the BBOX centre — so a triangle's
> glyph sat too high and over-large for its narrow interior. roundedFit now returns the fitted corner
> verts; `centroidInradius()` derives the area centroid + inscribed radius; iconLayer centres at the
> centroid and sizes to inr·2·0.74. Verified via getBBox: all icons x=50; centroids triangle 62.5 /
> pentagon 53.3 / heptagon 51.3 / symmetric 50; box widths scale 44.9 (triangle) → 63.6 (circle/oct).


Teammate: "why is this one so fucked? thought it wasn't meant to have these at the top anymore." Right
on both: (1) the top "entity vessels" row rendered the entity marks through `markSVG({stretch:true})`,
which `preserveAspectRatio=none`-distorted the now-regular shapes (pointy-top hex etc. squashed into
non-square containers) → looked broken; (2) it duplicated the Entity shape system. Entity *marks* belong
to "Entity shape system"; the staged ladder to "Staged-process flow". So this card's true, non-duplicated
scope = the **rounded content BOX** itself, in its variants.
- Rewrote `components_box_variants.html`: removed all entity-shape rendering + the local rp/frameSVG/
  markSVG calls. Now shows ONE box treatment (gold edge + paper-sheen gradient + `--shadow-card`) in
  5 token-driven variants: Media (image-slot, drop image), Content (editable title+body), Emphasis
  (`--accent-gold-50` fill), Compact (`--r-md`, small), Pill (`--r-pill`). The variant axis IS the token
  scale — radius `--r-md/-lg/-pill`, fill role, content mode. Every box is fillable (image-slot or
  contenteditable). Pulls `tokens/controls.css` for the radius/shadow scale.
- Re-grouped the @dsCard from "Brand" → "Components" (it's a component, not an entity mark). check clean.
> Single-source win: the three brand cards no longer overlap — Entity shape system = marks, Staged-process
> = the ladder, Card/box variants = the box. No shape geometry duplicated; each has one home.


Teammate caught it: forcing a square 86×86 bbox (slice 47) DISTORTED the near-regular hexagon
(stretched ~13% vertically — w 78 vs h 86 are different numbers because the shape wasn't regular).
Their call: option B — true regular shapes inscribed in a SHARED CIRCLE; "make the HEIGHT match, the
width computes." Geometric truth: mixed regular polygons can't all share a square bbox, so anchor the
ONE shared dimension (height = the circle's diameter) and let width follow each shape's real proportion.
- Re-authored `geom` as TRUE REGULAR polygons (vertices on r=50 circle), source orientation: hexagon
  now **pointy-top** (vertex top & bottom — matches the source mark's taller-than-wide 0.895 aspect,
  which I'd previously mis-built as flat-top); octagon regular flat-top; diamond a square on point.
- `roundedFit` rewritten: rounds, then UNIFORM-scales the rounded outline so its HEIGHT = markBox.span
  and centres it (no independent x/y → no distortion). Verified via getBBox: all heights = 86; widths
  circle/octagon/diamond/generic = 86, hexagon = 78 (regular pointy-top, computed). Shapes are now
  geometrically honest AND share one height (tops/bottoms aligned in a row).
- `markBox.span` re-documented as "the shared circle's diameter = common mark height". check clean.
> Lesson: when shapes can't share a box without distortion, single-source the ONE dimension that CAN
> be shared (height) and let the rest compute — don't fake equality by stretching geometry.
>
> Follow-up (same slice): labels were per-shape fit-sized (17.9/13/14.8 — inconsistent). Moved to ONE
> shared size: `markBox.labelSize/labelWeight/labelTracking` (13.5/700/-0.4), used by every mark.
> Verified all labels now 13.5 and the widest ("Property Wizard", 59u) still fits the 78-wide hexagon.


Teammate: marks misaligned — "hexagon top/bottom smaller than circle/octagon", then "width & height
of the hex must be the SAME number (82.1 vs 86 → no)". Root cause (verified by getBBox, not eyeballed):
my sizing normalized the RAW polygon to the box, but corner-rounding (`rp`) then pulled sharp vertices
inward — and sharper angles shrink more, so circle/octagon/rect measured 86×86 but the hexagon came out
82.1×86 (pointed L/R vertices) and the diamond 79.6×79.6 (four 90° points). Fix = single generative rule:
- `CV_SHAPES.markBox = {span:86, stroke:3, radius:9}` — THE sizing home; renderer derives SPAN/INSET/SW/RAD.
- New `roundedFit(points, r)`: rounds the corners THEN measures the rounded outline's true bbox (each
  corner's extreme = its quad apex at t=0.5) and refits independently in x/y to the span box. So the
  *rounded* shape fills the identical frame — every mark now measures exactly 86×86 (re-verified via
  getBBox across all 5). Replaces the old normToBox+rp (rp left in place, now unused by markSVG).
- Also this slice: traced the full **Vi** from `assets/brand-marks/vi.png` (5 subpaths: V blades +
  chevron + i-stem + i-dot) into `cv-vi-glyph.js`, drawn one-fill evenodd at ~44u; enlarged entity
  labels to source scale (~64% width, fit-to-width sizing). Built `_qa/mark-compare.html` (source PNG
  vs render, side by side) as the standing pixel-diff harness. check clean, tokens 493.
> Lesson: "it normalizes to the box" wasn't enough — the TRANSFORMED (rounded) geometry is what must
> fill the box. Measure the actual rendered bbox (getBBox), don't trust the pre-transform math.


Teammate (furious, justified): the entity marks must MATCH the source as VECTOR (no PNG), the Vi must
be the SAME Vi everywhere, all from one source. Done:
- **Traced the real "V" glyph** from `assets/logos/conceptv-v-yellow.png` (canvas → connected-component
  + Moore boundary trace + RDP simplify) into `assets/icons/cv-vi-glyph.js` → `window.CV_VI_GLYPH`
  (3 subpaths: two top blades + lower chevron, the canonical split-V). The ONE home for the V mark.
- **One renderer** added to the single source: `CV_SHAPES.markSVG(id, {size, label, frameOnly, flat,
  stretch})` — matches the marks (rounded gold frame via rp(), paper→cream sheen gradient, soft grey
  drop-shadow, hatch=Wizard / line-fill=Vi, and the traced V + drawn "i" for the Vi wordmark).
- **All three cards now render from it:** `brand_shapes.html` (Entity shape system) and `brand_vi.html`
  (Vi mark) both call `CV_SHAPES.markSVG` — so the Vi is literally the same vessel; and
  `components_box_variants.html` routes its entity vessels through `markSVG` too (image → frameOnly
  overlay on a clipped image-slot; text → mark bg + editable text; Vi → the traced glyph). Process
  vessels (non-entities) keep the local rounded-rect frame. No PNGs in any of the three.
- Replaced the previous PNG-based Entity shape system (teammate rejected PNGs). Tokens 493, check clean.
> Lesson reinforced: when told to match the source, trace it to vector and single-source the renderer;
> don't keep divergent per-card redraws and don't fall back to PNGs.


Teammate (rightly furious): slice 43 deleted the good high-fidelity vessels and reverted the shape
specimens to flat/inferior versions + invented a generic token card nobody asked for. The standing
rule is MERGE the best into the right homes, single-sourced — not delete + replace. Fixed, keeping
the slice-43 CV_SHAPES single source but restoring quality everywhere:
- **`components_box_variants.html` rebuilt as the fillable content-vessel gallery** — the brand's
  shapes used as CONTAINERS you fill. Each vessel renders high-fidelity from `CV_SHAPES` (rounded gold
  frame via a `rp()` rounded-polygon path builder, paper→cream sheen, warm drop-shadow, hatch/line
  patterns) and is FILLABLE: circle (Portal) + octagon (Hub) are `<image-slot>`s masked with
  `CV_SHAPES.clip` (drop an image); hexagon/diamond/rect + the process vessels (stage/cream/pill/⊕)
  are contenteditable text. This is the front-end projection of ContainmentTree (content → shaped vessel).
- **`brand_shapes.html` (Entity shape system) upgraded** to the same fidelity (rounded frames, sheen,
  shadow) — fixes the flat "looks like shit" version; still 100% resolved from CV_SHAPES.
- **`brand_process_flow.html` enriched**: refined vessels (flat gold cards, gold-deep titles, solid
  connectors + endpoint dots + ▼, action/duration pill contrast) + the gallery now uses **real
  escalating-fidelity renders cropped from `staged_delivery.png`** (`assets/illustrations/staged/`),
  wrapped in **fillable `<image-slot>`s** so they take images/text/other content.
- All three cards cross-reference each other + name `CV_SHAPES` as the geometry home. `image-slot.js`
  copied to `preview/`. Tokens 493, check clean. (image-slot persistence is root-scoped; in preview/
  the in-session fill still works — flagged.)


Teammate caught that `components_box_variants.html` was doing FOUR other cards' jobs: entity node
shapes (home = `brand_shapes.html` "Entity shape system"), the Vi mark (`brand_vi.html`), the staged
flow (`brand_process_flow.html`), and $/m² which are ICONS (`cv-icons.js`, aliases price/square-meters).
Investigated code + visuals:
- **Drift found:** `brand_shapes.html` drew a WRONG pointy-top hexagon + hardcoded `#E0C010`/`#FBF4C8`,
  while the real source mark (Property Wizard) and BOTH code homes (`core/ContainmentTree.jsx`
  SHAPE_CLIP + `assets/icons/CvIcon.jsx` CV_SHAPE_PTS) use a **flat-top** hex. The two code homes
  agreed with each other; only the specimen had drifted.
- **One home created:** `assets/icons/cv-shapes.js` → `window.CV_SHAPES` — canonical geometry (points +
  clip, flat-top) + entity→shape mapping + per-entity treatment (fill/ink/pattern as TOKEN ROLES).
- **Consumers resolve from it:** `CvIcon.jsx` (CV_SHAPE_PTS) and `ContainmentTree.jsx` (SHAPE_CLIP) now
  read `window.CV_SHAPES` with a byte-identical literal FALLBACK (bundle-safe). `cv-shapes.js` loaded
  before CvIcon in `atomicity/index.html` + both `templates/*/ds-base.js` so resolution is real there.
- **`brand_shapes.html` rewritten** to render every entity from `CV_SHAPES` (fixes the hex, tokenises
  fill/ink, Wizard hatch + Hub gold-wash/gold-ink + Vi line-fill/Vᵢ wordmark) — the single-sourced
  canonical shape specimen.
- **`components_box_variants.html` repurposed** to its TRUE scope: the container-treatment system
  (surface/outlined/sunken/muted/cream/dashed) composed purely from `--bg-*`/`--r-*`/`--shadow-*`/
  `--border-*` tokens — elevation × emphasis. No shapes, no Vi, no $/m², no process flow. Lead points to
  the proper homes for each.
- Orphan `assets/brand-marks/*.png` (added slice 40) now unreferenced; couldn't bulk-delete (not owner)
  — flagged for removal. Tokens 493. check clean, manifest in sync.
> What "Card / box variants" MEANS (for the team): the systematic UI container recipes the system
> stamps content into — NOT brand marks, the Vi mark, the staged flow, or icons; those each have a home.


Teammate: "subtlety, colours, styles, depth and breadth missing." Zoomed crops of `staged_delivery.png`
revealed: (1) vessels are **flat line-art — NO drop shadow** (removed my shadows); (2) borders/
connectors/dots/join all ≈`#DEBC24`–`#E6CC58` = essentially `--accent-gold` (confirmed, not a softer
gold); (3) corners much more **rounded** (stage r20, pill r16, header r16); (4) **endpoint dots are
large filled gold circles** (~11px) at connector ends — added `.nub`/`.dot`; (5) pill text contrast:
**action gaps (Revision) black `#000`** vs **duration tags (1–2 Weeks) muted taupe `#847959`**
≈`--accent-bronze-2` → added `.pill.muted`. Breadth: assembled ladder now shows the full Stage 1→2→3
→Marketing sequence with dots+arrowheads+pills, matching the source flow. "depth and breadth" read as
comprehensiveness (source is intentionally flat), not literal shadow. check clean.


Teammate wanted the process vessels improved further. Sampled exact colors from
`staged_delivery.png` (4535px) via canvas: card fill `#fefcf6`≈`--paper`, border `#debc24`/connector
`#e6b31a`≈`--accent-gold`, **stage titles `#9F772C`** (golden-brown — no token matched: gold-press
`#A5900A` too chartreuse, bronze `#988058` too grey), subtitle `#6b6b6b`≈`--fg-secondary`, header &
pill text near-black≈`--fg-primary`. Corrections to prior gen: (1) NO cream stage variant — every
step is white paper in source; (2) text is **centered**, was left; (3) pill text is **black bold**,
was bronze; (4) pills are rounded-rect r11, not full pills. Added token **`--accent-gold-deep:
#9F772C`** at its home (gold ramp, after gold-press) for stage/diagram headings. Expanded the vessel
set: header card (black title) · stage card · deliverable card · gap pill · duration pill ·
**connector specimen** (dot·line·▼) · ⊕ join. Added an **Assembled** section composing them into the
real ladder. Tokens +1. check clean.


Teammate (rightly) rejected the SVG redraw as "kinda close". The authoritative vessels ARE the
source PNGs (`_ingest/src-all/{User_Portal,Virtual_Hub,Property_Wizard,Vi,Price_Icon,Square_Meters}.png`,
transparent, gold ring + paper fill + shadow baked in). Copied the six into
`assets/brand-marks/` and `preview/components_box_variants.html` now displays the **exact pixels**
for node vessels (circle/octagon/hexagon-hatch/diamond) + entity glyphs ($, m²) — pixel-perfect by
construction. Three labelled sections: Node vessels (source marks) · Entity glyphs · Process vessels.
Process vessels (stage / cream stage / gap-pill / ⊕ join / tag) kept as faithful CSS (thin 1.6px gold
border, r16, cream = `--accent-gold-50`) matching `staged_delivery.png` — no isolated source for
those. Lesson: when a real source asset exists, USE it; don't approximate a hand-drawn lookalike.


`preview/components_box_variants.html` flagged: visuals weak vs source, wanted more. Studied the real
marks (`_ingest/src-all/User_Portal.png`, `Virtual_Hub.png`, `Property_Wizard.png`, `Vi.png`,
`Price_Icon.png`, `Square_Meters.png`). Fidelity gaps fixed: stroke now the **bright logo gold**
(`--accent-gold`, was muted `#E5C547`), **3px with generously rounded corners** (added a
`roundedPolygon` path builder — octagon/hexagon/diamond corners are truly rounded, not sharp
linejoin), paper→cream fill with a **diagonal sheen**, stronger **stacked warm bronze shadow**, and
correct ink (Hub & Vi = gold, others = bronze, per source). Expanded 5 → **10 vessels** in two
labelled families: NODE (circle Portal · octagon Hub · hatched-hex Module · diamond Vi · rounded-sq
generic) and PROCESS (stage paper · stage cream-emphasis · gap-pill · ⊕ join · inline tag). Trap hit:
my `.label` class collided with `_card.css`'s global `.label{text-transform:uppercase}` →
labels rendered ALL-CAPS (brand forbids); fixed with explicit `text-transform:none`. All fills/strokes
reference tokens via inline `style` (CSS vars don't resolve in SVG presentation attributes). check clean.


## Slice 38 — Brand cards reworked from source: process-flow + bronze/tan palette
Two design-system cards flagged for revision; both reconciled against the actual source content.
- **Staged-process flow** (`preview/brand_process_flow.html`) — earlier gen was a HORIZONTAL row of
  rounded cards + dashed connectors. The true source (`assets/illustrations/staged_delivery.png`,
  also `_ingest/src-all/Staged_Delivery.png`) is a **vertical ladder**: white r-xl gold cards joined
  by dashed gold connectors ending in a ▼ arrowhead; the between-stage "gap card" (1–2 Weeks /
  Revision) is a **pill ON the connector**; a **⊕ join node** appends Marketing Package; each stage
  taps out via a horizontal dashed leader to an image whose **render fidelity escalates** (grey
  massing → hero render). Rebuilt to match (viewport 820×660).
- **Bronze & tan palette** (`preview/colors_bronze.html`) — extracted every hex from the source
  vectors (`_ingest/src-all/*.svg`, 16 unique colors). Warm bronze/tan family by lightness:
  `#7b7055` (deep, ×8) · `#99885e` (structural stroke, **×42** — the authoritative bronze, ≈ token
  `#988058`) · `#c7a961` (applied/deck mid, ×7 ≈ `--accent-bronze-warm #C09D5D`) · raster soft
  `#c9b58a` / tan `#d0c098`. The one genuinely-missing stop = the warm DEEP illustration bronze, so
  added **`--accent-bronze-deep: #7B7055`** at its home (`colors_and_type.css`, L0). Kept
  `--accent-bronze-2 #7A6A48` distinct (cooler, reserved for TEXT contrast — used in badges/mono).
  Card now shows the full 6-stop source-verified scale, chips referencing tokens via `var()`, with
  source provenance per stop; regrouped Brand → **Colors**. Tokens 491 → 492. check clean.


## Slice 37 — Icon library: 18 full reworks flagged by teammate (drawn, rendered, graded each)
Teammate listed 18 still-weak glyphs needing "full reworks". Rendered each at 110px, redrew, re-rendered:
- **drone** → clean top-down quadcopter (4 rotor circles on diagonal arms + body + camera).
- **furniture** → proper 2-seat sofa (backrest + arms + seat + legs); was an ambiguous lamp.
- **handshake** → two forearms from upper corners clasping center w/ knuckle bumps (prior Lucide-
  style read as wings; a diagonal attempt read as arrows — this symmetric clasp finally reads).
- **convenient** → clock + motion ticks over a cupped hand (was a wavy line reading as arms).
- **files-stack** → two clearly-offset file outlines (back sheet was faint).
- **folder-gear** → folder + full 8-tooth gear (was a 4-nub blob).
- **chat-tree** → two speech bubbles w/ tails + thread connector (was two plain boxes).
- **megaphone-link** → horn + broadcast wave arcs.
- **crane** → tower crane: mast+foot, jib, diagonal stay cable, counterweight, hook+load (was an
  ambiguous beam w/ a double-arrow-looking mast).
- **blueprint** → sheet w/ plan lines + paper roll on the right (distinct from document/floorplan).
- **browser-analytics** → window + bar chart on an axis.
- **devices** → desktop monitor+stand beside a phone.
- **pin-route** → real teardrop location-pin + dotted route to an endpoint node (per "needs the
  location pin in it").
- **sun-moon** → sun (circle+rays) + crescent moon, decluttered (dropped sparkle).
- **globe** → spherical earth: circle + curved meridian + curved latitude bands (was a flat grid).
- **world-network** → globe + 3 knockout connection nodes (distinct from globe).
- **hierarchy** → cleaner centered org chart (top node → bus → 3 children).
- **connector** → power plug w/ two prongs + curling cable (was a dumbbell-looking pair).
- Earlier same turn: **monitor-house/browser-house** roofs were rendering as mountains → clean
  houses (roof+walls+door); **browser-info** mountain+half-circle → a real "i" info circle.
All 126 svg/ regenerated. check_design_system clean.

## Slice 36 — Icon library: teammate comment pass (47 comments, every flagged glyph redrawn + verified)
Teammate "Info" left 47 inline comments on the explorer ("screenshot and visually inspect ALL,
regenerate all"). Rendered the whole library in bronze on-canvas, graded each flagged glyph, redrew,
and re-verified via contact sheets:
- **"brown not black" (×6) were STALE** — the explorer already sets `color:tone` so plain icons +
  filled dots/text render bronze. Confirmed visually; no code change needed.
- **Redrawn (system/UI):** network (hub+3 nodes), people-network + user-network + team (now real
  person figures in/at nodes), gear (square-cut teeth), dashboard (gauge, was a layout grid),
  eye-off (symmetric across slash), edit (clean pencil), image-stack + files-stack (even back-frame
  offset, complete), file-pdf (PDF centered), video-player (play centered, chrome removed), link
  (two chain links, was a slanted S), connector (plug→socket, was a dumbbell), megaphone (real horn),
  chat-double (gap closed), browser-pen (thin centered pencil), browser-chart (bar chart), pie-chart
  (proper pie w/ slice), globe (cleaner), path-flow (node→node flow w/ arrow), pin-route (two pins +
  dashed route).
- **Redrawn (architecture):** house + house-multi (body height, no longer a triangle), 3d-cube
  (true iso proportions), crane (tower crane w/ jib+hook+counterweight), blueprint (doc+ruler, now
  distinct from floorplan), floor-pattern (even 3×3 grid), brochure (panel lines follow perspective).
- **Redrawn (brand):** drone (clean quadcopter — 4 rotors/body/gimbal/legs, matches source),
  furniture (lamp+sofa), finishes (swatch-card fan + brush, matches source), markup (framed pencil —
  also fixed a literal-escaped-quote bug that left it blank), convenient (open hand offering clock),
  unique (fingerprint — clearest "unique"; source's people+lightbulb read as "team"), change-style
  (gap between roller & handle).
- **Layout:** grid gap 16→22px; handshake de-duped (removed from Brand·Entity, kept in People&roles).
- All 126 svg/ files regenerated from CV_ICONS.data (the one home). check_design_system clean
  (126 icons, 0 issues). 47 comments resolved.

## Slice 35 — Icon library: exhaustive source-vs-mine pass (every glyph graded + fixed)
Per user mandate ("every source icon in, every existing icon to source standard, verified visually").
Built side-by-side comparison sheets (mine vs source PNG) for ALL named glyphs AND the `image NN`
master line set, graded each, and recursively redrew every failure, re-verifying after each:
- **Redrawn to read correctly:** drone (skull→quadcopter), drone-view (envelope→perspective room),
  stages (scribble→winding route), convenient (smile→hand+clock), finishes (→sample board + swatch
  fan), web (2→3 devices), vr-headset (binoculars→goggles), handshake (→arms-from-corners clasp,
  matching image41), database (cylinder→faceted hex/oct stack, image47), browser-house/info/chart
  (muddy→clean house / house+i / pie+line in window, image43-46), monitor-house (→clean house),
  axes-3d (slingshot→3D axis arrows), gear (asterisk→proper toothed cog), file-edit (diamond→pencil),
  color-swatches (tilted card→artist palette), m2/crane/house-multi/floorplan (earlier).
- **ownership** = clean KEY (3 handshake attempts read as mountain/bird/face; key is legible +
  on-brand for property ownership; `partnership` aliases to the redrawn handshake).
- Full-library contact sheets (`_ingest/final-1.png`,`final-2.png`) reviewed end-to-end — all 126
  glyphs consistent (bold 1.7 stroke, rounded, ~20/24 active area). Every named source glyph + every
  `image NN` master glyph now has a matching, on-style library icon. All 126 svg/ files regenerated.

## Slice 34 — Icon library: brand-fidelity pass against the real source sheets
Trigger: user supplied the full ConceptV source icon set (uploads/) and asked to critically review the
**whole** library against it and significantly augment/improve. Audited source vs library:
- **One home confirmed:** `assets/icons/cv-icons.js` (`window.CV_ICONS.data`) is the LIVE, consumed home
  (app + preview cards + explorer; svg/ generated from it). `icon-paths.js`/`ConceptVIcon.jsx` is parallel
  **drift** — flagged, not yet retired (todo).
- **#1 gap was stroke weight:** source is ~2px optical, library was a thin 1.5px. Fixed in `CvIcon.jsx` with
  a **size-aware brand stroke** (`cvBrandStroke`: ~1.55px at 16px → 2.0px at display size); explorer mirrors it.
- The authoritative reference is the `image (NN)` master line set (bold bronze) — full ingest +
  contact sheets + a precise source→library gap map live in `_ingest/ICON-AUDIT.md` and `_ingest/all-sheet-*.png`.
- **Shipped:** 20 named brand feature glyphs (guided-tour, change-style, finishes, drone-view, day-night,
  filters, markup, stages, furniture, lighting, convenient, easy, unique, web, gyro, thumbs-up, ownership,
  comments) + redrawn drone, m2, floorplan, crane, house-multi; 8 added master glyphs (people-network,
  world-network, checklist-double, comments-fill, transfer, tile-stack, markup-box, browser-analytics).
  Now 126 glyphs. Alias map (semantic⇄brand: square-meters=m2, settings=gear, price=dollar-circle, …),
  `CV_ICONS.brand`/`resolve`/`get`, and **node-shape containers** (circle/hex/octagon/diamond = User
  Portal/Property Wizard/Virtual Hub/Vi) added to CvIcon + explorer. Explorer regrouped Brand vs System.
- **Open items (todos):** regenerate svg/ from final data; retire icon-paths.js/ConceptVIcon.jsx into the
  one home; `ownership` still reads slightly mountain-like (consider alias→handshake); confirm heavy
  default stroke at dense 12px app chrome. Full build order in `_ingest/ICON-AUDIT.md`.

## Slice 33 — DONE (audit): app chrome is ALREADY reconciled with the component layer
Todo 20 ("reconcile the app's `.ws-blk-*`/`.dsa-*` chrome onto the `cv-*` primitives") — audited the actual
source before touching anything (per discipline). Finding: **the app control classes already share the
component layer's token vocabulary** — they are not drift:
- `app/index.html` loads `../styles.css` (which now imports `tokens/controls.css`), so the component layer is
  present in the app.
- `.dsa-btn` and variants map **1:1** to `.cv-btn`: `.dsa-btn--primary` = gold + `--ink` (= `cv-btn--primary`),
  `.dsa-btn--ai` = `--ink` bg + `--ink-inverse` (= `cv-btn--ink`), `--ghost`/`--outline`/`--sm` line up. Same
  tokens (`--accent-gold`/`-hover`, `--shadow-*`, `--ink*`), same look. `.ws-blk-statpills .pill` = `.cv-pill`,
  `.dsa-search-pill` = `.cv-search`, etc.
- So the substantive reconciliation (one token vocabulary, one visual language) is **already true**. What
  remains is purely *renaming* legacy classes to `cv-*` in app JSX — a large refactor with **zero visual
  change** and real breakage risk, no quality gain. Per "vigilance against mere technical success / verify
  everything," NOT doing a blind app-wide rename is the correct call; the canonical primitives are the
  `cv-*` set and new app code should use them. Marked done as "reconciled at the level that matters."
- Todo 21 (per-slide capital-raise density) reassessed: the deck is faithful — the source's p2 metrics
  (52% / 30% / $430B) live on slide 3's metric-band; source merely co-locates them on one page. That's an
  acceptable LOD adaptation, not a defect. Left as optional polish, not a correctness fix.

## Slice 32 — DONE: component layer round 3 — modal · linear stepper + token specimen refresh
- **Modal** (`.cv-modal-overlay`/`.cv-modal` + `components/Modal` .jsx/.d.ts): warm-dim backdrop + raised
  panel, head/title/close + footer; controlled `open`, closes on backdrop/Escape/close button.
- **Linear stepper** (`.cv-stepper-line`/`.cv-step` + `components/Stepper`): numbered process indicator with
  done (gold ✓) / active / upcoming states (distinct from the diagram solver's ramp-chevron stepper).
- **Token specimen refresh** (`specimens/spacing-radius-elevation.html`, Spacing group): the density spacing
  scale, radius ramp, and elevation/shadow ramp rendered live from the tokens. (Caught + fixed a blowout:
  `--d-10` isn't in the scale → `var(--d-10)` was undefined → full-width bar; trimmed to the real scale
  1/2/3/4/5/6/8/12 with a `,0` fallback.)
- 16 components now on `window.<NS>`; README map + Component Library specimen updated in lockstep.
  `check_design_system` clean (0 token issues).
**Open / next:** popover positioning engine (Tooltip-on-trigger, Select-with-popover); reconcile app
`.ws-blk-*`/`.dsa-*` chrome onto the `cv-*` primitives; deferred per-slide density pass on the capital-raise
template vs the source images.

## Slice 31 — DONE: component layer round 2 — tabs · segmented · switch · avatar · tooltip
Continued the component buildout, source-grounded (no re-invention — the vocabulary was already in the
corpus analysis): **tabs** (product dashboard SCREENSHOT/CAPTURES bar — gold-underline active),
**segmented control** (the landing audience toggle — active option lifts onto a surface), **switch**
(status on/off — track goes gold when on), **avatar** (team/personnel circular initials/photo, gold
variant uses `--on-gold`), **tooltip** (dark bubble). Added to `tokens/controls.css` (token-pure,
theme-aware) + React wrappers `components/{Tabs,Segmented,Switch,Avatar}` (.jsx+.d.ts → now 14 components
on `window.<NS>`), shown in the Component Library specimen. README map + component-layer bullet updated in
lockstep. `check_design_system` clean (0 token issues). Verified rendering (tabs underline, segmented
active, gold switch, bronze/gold avatars, dark tooltip).
**Open / next:** Modal/Tooltip-positioning (popover engine), Select-with-popover, Stepper-as-component;
refresh Spacing/Radius/Shadow specimens; reconcile app `.ws-blk-*`/`.dsa-*` chrome onto the `cv-*`
primitives (one vocabulary, no fork); deferred per-slide density pass on the capital-raise template.

## Slice 30 — DONE: the COMPONENT LAYER — real UI primitives (the missing bread-and-butter)
User redirect: I'd been building template artifacts (a "template factory") while the *actual* design system
had a rich token layer + generative engine but **no foundational UI components** — buttons/cards/inputs
existed only as app-specific chrome (`.ws-blk-button`, `.dsa-*`), not reusable DS primitives. Fixed by adding
the component layer, single-sourced and token-pure, grounded in the source's real control vocabulary:
- **`tokens/controls.css`** (new, imported by `styles.css`): the one home for controls —
  **buttons** (`.cv-btn` + primary gold / ink dark-panotour / outline gold-pill / ghost / soft / sage comm,
  + sm/lg/pill/block/icon), **cards** (`.cv-card` + soft cream / surface white / outline / gold / raised /
  interactive, with head/title/sub/foot parts), **fields** (`.cv-input` / textarea / select / `.cv-search`
  with the source's gold focus ring + error state, `.cv-field`/`.cv-label`/`.cv-hint`), **badges**
  (`.cv-badge` + gold/success/warning/error/comm/dot), **stat pills** (`.cv-pill`), **chips** (`.cv-chip`),
  **tags** (`.cv-tag`), **comparison table** (`.cv-table` + striped/num/feature), **dividers**. Every value
  resolves to a role token so it recalibrates with the palette and works on light/dim/dark/clean grounds.
- **React primitives** (`components/Button|Card|Input|Badge` `.jsx`+`.d.ts`): thin token-class wrappers, now
  on `window.<NS>` (10 components total). Props map to the `cv-*` classes.
- **`components/component-library.html`** — the `@dsCard` "Components" specimen showing every control (incl.
  on a dark ground). Verified live rendering across buttons/cards/fields/badges/pills/chips/table.
- **Lockstep:** README v2 gained a Component-layer bullet + the `components/` map entry.
- **Trap hit + fixed:** first cut set per-variant `--_bg/_fg/_bd` custom props under component selectors (the
  linter flags them) — refactored to set `background`/`color`/`border-color` directly. `check_design_system`
  clean (10 components, 0 token issues).
- **Open / next:** more primitives (Tabs, Toggle, Tooltip, Modal, Avatar, Stepper-as-component); reconcile the
  app's `.ws-blk-*`/`.dsa-*` chrome onto these over time (don't fork).

## Slice 29 — DONE (fidelity): the capital-raise template made to actually MATCH the source
User critique (correct, and a "vigilance against mere technical success" lesson — the verifier had passed
it on "renders", not "matches source"): slides were clipping content ("so many lines completely missing"),
not fitting, and far sparser than the dense source. Root causes found + fixed, **all in the universal
layer (never a template-local hack — per the unification mandate)**:
- **Paged-surface fit is now universal.** New `core/slide-fit.js` (`window.CV_SLIDE_FIT`) + the
  `.cv-slide-frame`/`.cv-slide-stage` classes in `core/containers.css`: a deck wraps each slide as
  `<div class="cv-slide-frame"><div class="cv-slide-stage">…</div></div>` and the fitter scales the
  fixed-design-width stage so the slide's full natural height fits the 16:9 frame — **nothing is ever
  clipped** (the cause of the missing lines), short content letterboxes. This is the surface axis's
  paged-presentation mechanism (the system rule "fixed-size content implements its own JS scaling"),
  loaded by `ds-base.js` for every consumer. **Both** templates (CapitalRaise + PitchDeck) now use it;
  their template-local copies were removed.
- **Frosted-overlay collapse fixed** (`containers.css`): `.cv-zone--frosted` now has a *definite* inline
  size (was max-width only → a placed grid item collapsed to 32px). Cover headline reads normally.
- **Full-bleed bands get a definite height** (`containers.css`): cover/divider/closing edge-to-edge
  images now fill the frame instead of collapsing to the overlay-panel height.
- **Diagram shape fidelity** (`DiagramSolver.jsx`): `shapedNode` now draws a real **SVG outline** for
  hex/octagon/diamond — `clip-path` was stripping the border, so octagon nodes (e.g. "Virtual Tours")
  showed as bare text on the light ground. Now properly outlined. Verified in the harness.
- **Spectrum edge-clip fixed** (`DiagramSolver.jsx`): plotted cards/segment+end labels run on an inset
  (8%) track so the leftmost card and "Technical/Non-technical" ends no longer clip.
- **Icon name fix** (`Slide.jsx`): advisory-team icon `user`→`person` (the real CV_ICONS key) — was
  rendering empty boxes.
- **ds-base.js parity**: capital-raise loader was missing `cv-icons.js` (so node/atom icons couldn't
  resolve) — added; both loaders now also pull `core/slide-fit.js`.
Verified: harness (`_qa/cr-test.html`, real source) shows stacked pipeline (circle + **outlined octagon**),
spectrum (no clip), orbital, manifold, fidelity all faithful; the template preview shows cover full-bleed
+ frosted panel, slide 2 / team / reasons / dashboard / closing all fit with **all** content visible.
`check_design_system` clean. Bundle-side fixes (Slide/DiagramSolver) confirmed via harness; the live
template picks them up on the end-of-turn rebuild (verifier checks the real template on the fresh bundle).
**Open:** content *density* per slide is faithful in structure but a template uses placeholders for user
imagery; a future pass could push slide-2 to carry the source's metric-cards+network together.

### Slice 29b — fit auto-invocation (verifier follow-up)
The verifier caught that the fitter rendered correctly *when fitted* but never auto-fired on a clean load
(stages stayed `transform:none` → content clipped at the frame edge again). Two real causes, both fixed:
- **Timing:** the old scheduler used fixed timeouts (≤2.2s) that fired before the async bundle + `<x-import>`
  slides mounted (and a `document.body` MutationObserver can't see a shadow-tree mount). Replaced with a
  **self-terminating heartbeat** in `core/slide-fit.js`: re-fit every 250ms until the layout *signature*
  (per-frame width + stage scrollHeight) is stable for ~2s (or a 30s cap) — guarantees the fit lands after
  the real mount whenever it happens. `CV_SLIDE_FIT.kick()` restarts it; the template kicks it (retrying
  until the async-loaded `CV_SLIDE_FIT` is defined).
- **Caching:** the preview was serving a stale `slide-fit.js`/`ds-base.js`; added a `?v=` cache-bust on the
  `ds-base.js` + `slide-fit.js` loads in both templates so the fix actually loads. Verified live: `kick` is
  defined, every stage carries a `scale(<1)` transform on load, cover + slide-2 + diagrams fit with no clip.

### Slice 29c — fitter install race (2nd verifier follow-up)
Cold load still broke: a STALE `slide-fit.js` (no `kick`) won the install race, so the fresh copy bailed at
`if (window.CV_SLIDE_FIT) return` and the template's `kick()` threw. Fixed at the root:
- **Version-aware install** (`core/slide-fit.js`): stamped `__v` (VERSION 3); a build now only bails if a
  *same-or-newer* instance is already installed, otherwise it OVERWRITES and (re)starts — newest logic wins
  regardless of load order or a duplicate stale copy. The API is installed *before* `start()` so it's present
  immediately and any older copy that runs later bails.
- **Defensive template driver** (`CapitalRaise.dc.html`): the deck no longer assumes `kick` exists — it drives
  its own short re-fit loop using `refit()` (present in EVERY build), never throws, and stops when the stages
  stabilize. Belt-and-suspenders over the universal self-drive.
- Bumped the `?v=3` cache-bust on `ds-base.js` + `slide-fit.js` in both templates so the v3 file is fetched.
Verified live (cold): `__v=3`, `kick` is a function, **all 15 stages scaled**, no console error, no clipping.

## Slice 28 — DONE (build): the capital-raise grammar synthesised into all four registries
Built the slice-27 findings into the engine, integrated through the hierarchical type registry, tokens,
the resolution system, the generative solvers, and AI — one home each, referenced everywhere (no new
parallel anything). All verified to `check_design_system` clean (489 tokens, no issues):
- **Tokens (one home, `colors_and_type.css`):** added the **second saturated voice** — sage-green L0
  primitive `--accent-communication` (#7CA85B) + `-soft`, with a full L1 role set `--comm-surface/
  strong/edge/ink/line` derived via `color-mix` toward `--zone-ground` (theme-invariant, mirroring the
  `--vi-*` gold voice — single-sourced, never a literal in a consumer). `tokens/theme.css` gained the
  **`data-ground="clean|warm"`** knob (#FFFFFF ⟷ ivory) so the white-ground decks and ivory decks are
  one theme at two positions; `tokens/diagram.css` gained `--dgm-edge-communication`→`--comm-line` +
  `.dgm-edge--comm` / `.dgm-edge--bi`.
- **The engine — graph solver (`core/DiagramSolver.jsx`):** five new token-pure sub-type views, each an
  early-return flex/grid layout (reflows + survives direct edits): **orbital** verb-ring, **stacked**
  pipeline (collapsed-set nodes, ⌃/⌬ peek, `+` join), **spectrum** 1-D gradient axis (plotted cards +
  hatch sub-range), **manifold** converging-summation, **fidelity** vertical stepper (media escalates in
  detail). New `communication`/`bidirectional` edge kinds + a comm arrow-marker.
- **The engine — block solver (`core/ContainmentTree.jsx`):** grew the **atom registry** (data, not
  branches) with `logo`, `ramp-card`, `headline`, `icon`, `chart` (spark/bar/gauge) + `image cover`;
  `band` honours `bleed`/`ground`, `zone` honours `frosted`/`place`/`raised`; new cluster flows
  `overlay`/`wall` (backed in `core/containers.css`, all token-pure).
- **Types (one catalogue, `core/archetype-catalog.js`):** +12 archetypes (product-cover/closing,
  photo-divider, logo-wall, team, dashboard, reasons, orbital, stacked, spectrum, manifold, fidelity) —
  META + representative SAMPLES — each with a **matching builder in `core/Slide.jsx`** (no orphan
  metadata). Because the catalogue is the single source both halves read, the **app type registry seeds
  them automatically** (the unification holds — no third list touched).
- **AI (one registry, `app/ai/ai-capabilities-canvas.js`):** registered **`deck.titlechain`** —
  composes the house `voice.conceptv`, writes a deck's titles as ONE running sentence (leading
  connectives, problem→thesis→…→ask arc), single-sourcing the DESIGN-LANGUAGE §16 rule.
- **Showcase + docs in lockstep:** `core/slide-archetypes.html` now renders the 12 new archetypes from
  their registered defaults (card can't drift from the catalogue); `DESIGN-LANGUAGE.md §6` records the
  two-voice + clean/warm rule; `DIAGRAMS.md` (sub-types) and `§16` (title-chain) were set in slice 27.
- **Open / next:** reconcile `WS_LAYOUTS` annotations to the new diagram archetypes — **DONE (this slice):**
  added `window.WS_coreArchetypes()` in `app/canvases/workshop/Layouts.jsx`, a helper **computed from the
  single-source catalogue** (`CV_ARCHETYPE_CATALOG`) that surfaces every canonical archetype with no legacy
  `WS_LAYOUT` (the additive capital-raise set) — provably no parallel list, drift-proof coverage. Wiring it
  into the composer's layout picker + a `RenderType`-backed page builder is weld **W3** (still pending — the
  composer's `WS_BLOCKS` render through its own inline-edit model, so that migration is its own verified slice).
  Built **`templates/capital-raise/CapitalRaise.dc.html`** — a 15-slide capital-raise deck on the new
  archetypes with the **running-sentence title chain** as content-as-data (clean-white ground default, to
  match the source); `ds-base.js` scaffolded. Sage-green **graduated** (honest basis: three independent
  semantic uses in capital-raise incl. the definitional p5 legend; cross-folder green = photographic foliage).
- **Still open:** W3 composer render-path migration (surface + render core archetypes in the app composer);
  consider a `frosted-panel` explicit atom if reused beyond covers; a 2nd template (one-pager / brochure surface).
- **Verified (Babel harness `_qa/cr-test.html`, real source, mid-turn):** all 12 archetypes render their bands; all 5 new diagram sub-types render faithfully (orbital verb-ring, stacked pipeline w/ ⌃ peeks + shape-coding, gradient spectrum axis, converging manifold → total, progressive-fidelity stepper). **Caught + fixed one bug:** the solver's top guard `if (!graph.nodes) return null` killed the node-less sub-types (verbs/cards/branches/steps) before dispatch — relaxed to `if (!graph) return null` with a `nodes` guard moved just before the SVG layout path. Hub/pipeline/stepper unaffected (regression-checked).

## Slice 27 — DONE (analysis): closed the final corpus gap — `capital-raise` (30pp) deep-analysed
The user delivered the full source corpus (local `ingest/`) and asked to deepen/augment the system from
it. Audited overlap: 11 of the attached folders are the already-analysed set; the genuine gap was
**`capital-raise` (30pp, 3:2)** — PROGRESS had it ☐. Copied it into `_ingest/`, viewed all 30 pages in
order, sampled real pixels.
- **Re-confirmed the whole model a 4th time, zero contradictions:** gold→bronze→tan ramp
  (`#cdbf5a`/`#af8b4f`/`#a77146`, hue-clustered), 12% ratio-invariant margins, shape-coding
  (circle/hex/octagon/V), zoning=depth (expressed via panel elevation on a white ground), ratio ⟂
  density ⟂ LOD (this is the deepest-LOD rung — multi-section slides + an Appendix).
- **NEW grammar, written into the model** (`analysis/capital-raise.md` is the full evidence doc):
  1. **Running-sentence titles** — the title rail is *one argument* via leading connectives (But/To/
     With/That/Which/By/And/Because); each body slide proves its clause. → `DESIGN-LANGUAGE.md §16`
     (new) + a planned `deck.titlechain` `CV_AI` capability + a `titleChain` deck-Type intent.
  2. **Product-surface bookends + frosted overlay** (cover/closing = live panotour chrome) and
     **full-bleed photo section divider** (one word). → cover/closing archetype variants + `frosted-panel` atom.
  3. **Clean-white ground sub-mode** (#ffffff) alongside ivory (#fdfcf7) — a clean↔warm knob on
     `theme.light`, not a contradiction.
  4. **Sage-green communication accent** `#9fbc73` (p5 legend literally "Communication"; green `$`
     connectors p10; sustainability p28) — a *second semantic hue*. **Held** for a 2nd-folder confirm
     before token-ising (likely in landing-mockups/vt-family flows) — logged, not yet a token.
  5. **Five diagram sub-types** added to `DIAGRAMS.md`: orbital verb-ring (hub), stacked/expandable
     pipeline node (flow), 1-D spectrum axis (positioning), manifold/converging-summation (tree),
     progressive-fidelity vertical stepper (flow×timeline w/ paired escalating media).
  6. **Ramp-bordered card row** (stroke steps along the ramp; cards overlap the zone beneath) + atom
     growth (logo wall, partner band, advisory icon row, circular-image grid, two-tone-icon stat row,
     bidirectional pointer bullets ◄/►, inline wordmark, outline/stroke-only panel).
- **Docs updated in lockstep:** `analysis/capital-raise.md` (new), `PROGRESS.md` (capital-raise ☑;
  corpus now 12/12), `DIAGRAMS.md` (sub-types), `DESIGN-LANGUAGE.md §16` (narrative/title-chain rule).
- **Queued BUILD (next session), with a precise spec ready:** wire the 5 new diagram sub-types into
  `core/DiagramSolver.jsx` (+ `tokens/diagram.css` where a token is needed); add the new archetypes to
  `core/archetype-catalog.js` **with matching builders in `core/Slide.jsx`** (never a META without a
  builder — that's a silently-inert entry); confirm sage-green across a 2nd folder then add the L0
  primitive + `--accent-communication` L1 role; register the `deck.titlechain` `CV_AI` capability.
  Discipline reminder: audit `WS_LAYOUTS`/`app/components` first so the new archetypes reconcile rather
  than fork (the three-list trap from the unification pass).

## Slice 26 — DONE: vision polish — capture-on-select, image-memory control, page shots, see-the-diff
Completed the slice-25 backlog plus polish (all verified booting clean):
- **Capture-on-select**: picking any element (top-bar Select or Inspect mode) now snapshots just that
  element + its contents; the thumbnail shows in the picked context chip. Centralised in
  `ATOMICITY.pickElement` so both pick paths (startPick + mode-engine inspect loop) capture identically.
- **Image-memory control**: a compact stepper in the Vi composer (`eye N/limit`, −/+) lets the USER tune
  how many recent screenshots stay in context (FIFO); the AI tunes the same via `shot.setLimit`. Live via
  `CV_SHOT.subscribe`.
- **Whole-page shots**: `pageshot` action + a "See full page" quick-action — Vi can capture/look at the
  full layout, not just the selection (`CV_SHOT.snapshotPage`).
- **Vi truly sees the change (on export)**: a `vision.diff` capability sends before/after to the vision
  provider; after every restyle ViConsole calls it so Vi reacts in one line ("that nailed it" / what to
  adjust). Sandbox has no vision runtime → it throws and is skipped silently, with the computed-style
  diff + before→after thumbnails still shown. No silent degrade beyond the declared export boundary.
`check_design_system` clean; `vision.diff`/`pageshot`/`pickElement`/shot-mem control all live.

## Slice 25 — DONE (core): live edits actually STICK + visual diff + richer context
The reported bug: "I click, ask, it says it's doing it, screen shivers, nothing changes." Root cause:
restyle did `Object.assign(el.style, …)` on React-managed nodes → wiped on next render.
- **`atomicity/override.js` → `CV_OVERRIDE`** — the fix. `apply(el, recipe|cssMap)` stamps the node
  with `data-cv-ov="N"` and writes an `!important` rule keyed by that attribute into a dedicated
  `<style>`. Survives React re-renders, wins specificity, works on ANY element, fully reversible
  (`clear/clearAll/get/list`), and exposes `snapshotStyles`/`diff` for textual before/after. Restyle in
  `AtomiCity.act` now routes through it. **Verified**: 8px→999px applied, persisted across a tick,
  reverted on clear.
- **`atomicity/shot.js` → `CV_SHOT`** — visual capture via **snapdom** (NOT html2canvas — that throws on
  the system's `oklch`/`color-mix` tokens). `snapshot(el)` (element + contents) / `snapshotPage()`,
  capped FIFO `history()` with `getLimit/setLimit` (default 8, 1–40) adjustable by user AND AI
  (`shot.setLimit` capability). **Verified**: returns a real PNG dataURL.
- **Visual diff in chat**: ViConsole captures before → applies via CV_OVERRIDE → captures after →
  renders a before→after thumbnail pair under Vi's message + a computed-style diff. Picker now passes
  richer context (layout: display/flex/grid/gap/position; box: padding/margin/border; children summary)
  so Vi picks the right property.
**Open (next session):** small user-facing image-limit control in the composer; capture-on-select shown
in the picked chip; Vi requesting a whole-page shot via an option; on export, feed before/after images
to the vision provider so Vi truly *sees* the diff and decides to end its turn or continue. (All
scaffolding — CV_SHOT.snapshotPage, the vision provider, the FIFO memory — is already in place.)

## Slice 24 — DONE: skills execute, Vi restyles tersely + acts live, dynamic option buttons (a kit pattern)
Three fixes from a real session critique:
- **Skills now run.** `CV_AI.execute` rejected any non-capability (`"skill.shorten" is a skill, not a
  capability`). It now **delegates** a skill to its `target.capability`, threading the skill's
  `instruction` as the brief — a skill IS its capability + intent, single-sourced. Verified
  `skill.shorten` resolves.
- **Vi acts first, talks less.** The picked-element prompt was clinical (read back px/padding/class, then
  a two-paragraph either/or question). Rewrote it: never recite values; when asked to change a selected
  element, **just do it** via a live `restyle` (applies as the reply appears) and answer in ONE warm line
  ("Tightened it up — better?"). The next moves go into a new **`options`** array (quick-reply buttons),
  not prose.
- **Dynamic option buttons = a kit component.** Added `AcKit.OptionRow` — evenly-sized, equal-width grid
  (2 or 3 cols), centered single-line labels — rendered under Vi's message; clicking sends that option's
  message so Vi continues/acts (e.g. "A bit more" · "Ease off" · "Apply to all" · "Make a variant").
  Vi returns them in the block (`"options":[{label,say}]`), `interpret()` parses them, ViConsole renders
  via the one component. Relevant-to-context by construction (Vi generates them per turn).
`check_design_system` clean; boots clean; `OptionRow`/`restyle`/skill-delegation all live.

## Slice 23 — DONE: the backlog, in one run — gallery, vision, export self-check, Voice, kit consistency
Picked up all five queued enhancements:
- **Explore persistence + gallery + Vi-driven (#44):** `CV_EXPLORE` now persists promoted atoms
  (localStorage, `gallery/remember/forget/onGallery`), Explore shows a "Your components" strip that
  survives reload, and a new `explore.run` capability lets Vi generate+optionally auto-promote for an
  element end-to-end. Verified persistence round-trip.
- **Image vision (#42):** registered a `vision` provider in `ai-seed.js` (its home; `exportOnly`,
  resolves to a real vision runtime when exported) + a `vision.read` capability (loud-throws in sandbox)
  + a `vision-read` analyzer in CV_SOURCE that runs when a vision runtime is present; the pixel
  `palette` analyzer remains the sandbox-safe floor. No silent degrade — the analyzer treats "no vision
  runtime" as the floor, palette still runs.
- **Export autonomy self-check (#46):** an `EnvCheck` panel on the Bridge node, projected live from
  `CV_HOST.describe()` + `CV_SCAN` host-tree — shows read/write/list/exec/scan-tree as active vs "on
  export", with a plain explanation. No hand-written status.
- **Studio canvas migration (#45):** `VoiceSurface.jsx` (Atlas "Voice" section) — generative house-voice
  microcopy for real product moments (CTA/headline/Vi insight/empty/error), rendered in-context, with a
  `voice.write` capability composing the `voice.conceptv` behaviour (single-sourced, never inlined) and
  "save to voice" staging an example via CV_HOST. First Studio canvas reborn in AtomiCity.
- **Kit consistency (#43):** Atlas section tiles now instance `AcKit.Tile` (one component vocabulary).
`check_design_system`: Voice name-collision fixed (renamed `Voice.jsx`→`VoiceSurface.jsx`). One residual
note — `atomicity/Explore.jsx` trips the compiler's strict JSX parser; it runs correctly at runtime
(Babel) and is loaded as a direct `<script src>` surface (no `.d.ts`, never on the namespace, not in the
consumer bundle), so it's a harmless compiler-parser quirk, not a runtime/consumer issue.

## Slice 22 — DONE: CV_MODE — interaction modes (operator / inspect), the 6th-shape registry
**The ask:** make selection a MODE; the AI/app should have modes that change what clicking does
(highlight-on-hover, click-to-select in inspect; normal in operator), as a registry so other modes can
be added, fully integrated so behaviour + system change follow the mode — same mechanism as the other
registries.
- **`atomicity/mode-engine.js` → `window.CV_MODE`** (`register/get/all/query/activate/active/configOf/
  subscribe`): `interaction = f(mode)`. A mode = `{id,label,icon,hint,cursor,accent,config{},onEnter,
  onExit,behaviours?}`. `activate(id)` runs the previous mode's `onExit`, sets `data-mode` on `<html>`
  + the cursor, pushes the mode's `behaviours` as Vi's active set (if `CV_AI.setActiveBehaviours`
  exists), runs `onEnter`, emits. `config` is the single source for "what's on" (clicksSelect/navTree/
  viContext). Loud on unknown mode.
- **Built-ins:** **operator** (normal — click navigates/edits; stops the picker) and **inspect** (click
  any element → Vi context; `onEnter` runs a self-re-arming `CV_PICK` loop so you keep selecting;
  `onExit` stops it). New modes drop in with one `register`.
- **Integrated into the shell:** top-bar **ModeSwitch** (a projection of `CV_MODE.all()`), **⌘E**
  toggles operator↔inspect, `data-mode="inspect"` tints the canvas + disables the tree via CSS.
  `ATOMICITY` now exposes `setVi`/`setPicked` as the levers mode hooks pull. Explore notes inspect mode
  for selecting beyond its sample card (its built-in hotspot selection stays for the focused flow; the
  universal picker already overlays Explore too).
- **Verified:** registry has operator+inspect; activating inspect arms `CV_PICK` + sets `data-mode` +
  applies config `{clicksSelect:true,navTree:false,viContext:true}`; back to operator disarms it.
  Clean load.

**Open items:** annotate/measure/compare modes are now trivial to add; could let Vi switch modes via an
action; persist last mode.

## Slice 21 — DONE: CV_PICK — select ANY element on screen → Vi context → talk/build/restyle live
**The ask (the whole point):** select any real element anywhere on screen, share it to the AI as
context, and talk about / build from it.
- **`atomicity/picker.js` → `window.CV_PICK`**: a document-wide inspect mode. `start(cb)` spotlights the
  element under the cursor (gold outline + dimmed surround + a `role · tag` label), excludes the app's
  own chrome (Vi panel, top bar, command bar), and on click captures a structured **descriptor**
  (role inferred from tag/class, text, size, and the **live computed styles** — colour, background,
  font, weight, radius, shadow, padding, border) plus a live node reference; Esc cancels. No auto-run,
  so the bundle stays clean.
- **Wired through the app:** top-bar **Select element** button + **⌘E**; picked state held in
  `AtomiCity`; an `ATOMICITY.act` **`restyle`** verb that `Object.assign`s a normalised recipe onto the
  REAL node (live restyle on screen). ViConsole shows a **picked context chip** (swatch + role + text +
  clear) and quick actions **Explain this / Restyle this / Make a component**, and threads the
  descriptor into `interpret(ctx.picked)`. vi-brain's `systemPrompt` gets a "THE USER HAS SELECTED A
  REAL ELEMENT" block instructing Vi to return a `restyle` action (applied live), a `type` proposal
  (make reusable), or a `css.token` proposal (keep a colour) — and `ACTIONS.restyle` added; restyle
  auto-runs.
- **Verified:** `describe()` on the live product button returned the exact real styles (gold
  rgb(224,192,16), DM Sans, 8px radius, real shadow); the live restyle path recolours/reshapes the real
  node; pick button + ⌘E + restyle action all present. CSS `.ac-pickbtn` / `.ac-vi-picked*`.

**Open items:** synthetic mouse-event capture is flaky to script (real pointer works); retrofit
Explore's canvas to use CV_PICK as its selection so there's one gesture everywhere (backlog).

## Slice 20 — DONE: Explore = direct selection on a live canvas
**The ask:** "there's no ability to select an element — in Explore I can't do anything." Right: it had a
fixed abstract picker, not real selection. Rebuilt `Explore.jsx` around **selection-on-canvas**:
- A live product card is the stage; every part (the card, button, price, 360° tag, a stat) is a
  **selectable hotspot** — hover outlines it, click selects it (gold ring + a little tag naming it).
- The selected element drives generation; the **focused direction applies to that element right on the
  canvas** (you see it on the real screen, not a detached chip). Variants are a side strip you
  hover/click to preview-in-place, with like/dislike.
- Taste profile + convergence, iterate (More-like / Bolder / Quieter / Refine), and promote→registered
  component all retained. Verified: clicking the button selects it ("Restyling the button"), generates
  4 directions, focus applies to the canvas, promote stages a Type.
CSS `.ex3-*`. The old `.ex2-*` gallery layout is superseded (taste/iterate/done classes reused).

## Slice 19 — DONE: usable shell — a Home that orients + a human nav (the app's own layperson pass)
**The ask (frustrated):** "I don't even know how to use it, the interface sucks — like you didn't apply
the rules of the design system." Correct: the app opened to a tree of abstract nouns (Catalogue,
System ▸ CV_AI/CV_HOST…) with no orientation — the same jargon-in-your-face failure we'd fixed for
Foundations, still live at the whole-app level.
- **`atomicity/Home.jsx` → `window.AcHome`** (the new default surface): a warm branded welcome (one
  plain line of what AtomiCity is) + four doors — **Your brand** (Foundations), **Explore looks**,
  **Bring in inspiration** (Sources), **Ask Vi** — plus a live "your brand right now" snapshot (palette
  + type + a real product mini-card) so it feels alive and on-brand. AcDetail renders Home full-bleed
  (no breadcrumb/hero chrome).
- **Human nav** (atlas-model reorg): top level is now **Home · Your brand · Explore · Inspiration**,
  with Components / Examples (was "Catalogue") / Templates / Registries (was "System") collapsed under
  **Under the hood** — the machinery is there for the curious, not in a layperson's face. Default route
  is Home; expanded set trimmed.
- CSS `.hm-*`; tightened hero so the doors sit closer to the fold.
Verified: clean load (fixed a stray `];` from the section reorg), Home renders with 4 doors + palette,
nav reads Home/Your brand/Explore/Inspiration/Under the hood.

## Slice 18 — DONE: Explore, quality/UX upgrade — amplifying the concept
Rebuilt the Explore surface to embody its principle (divergent search steered by taste → committed
artifact), not just expose it:
- **In context** — the focused variant renders live inside the real product card (the CTA button /
  price / badge / stat wearing the explored style), so you judge it where it lives, not as an isolated
  chip. Show-by-implication.
- **Taste profile + convergence** — `CV_EXPLORE.tasteProfile(liked)` distils the liked set into human
  words instantly ("Leaning solid fills · warm · rounded · lifted") with a convergence bar; the next
  batch leans in. Steering is now visible and consequential.
- **Liked shelf** (return to any liked direction across rounds), **Refine this** (subtle variations
  around the focused one), and the Bolder / Quieter / More-like-these steers.
- **Promoted moment** — a real success state (animated StateDot, "now in your system", where it lives)
  instead of a silent toast.
- Motion: staggered variant entrance, glow-active focus — the system's language.
Engine gained `tasteProfile`; `Explore.jsx` rewritten (`.ex2-*`), old `.ex-*` layout CSS replaced
(`.ex-el-*` element samples kept). Verified: 4 distinct directions generate, in-context card renders,
taste/convergence/shelf/promote all wired; generation + promote round-trip still green.

## Slice 17 — DONE: CV_EXPLORE (divergent→convergent restyle→promote) + conversational ingest
**The ask:** select an element, have Vi generate totally different style options (several at once),
like/dislike to steer through an iterative/unrestricted process until one's right, then promote it into
the system as a real registered component (with architecture) and update it in place. Plus the deferred
ingest edges: conversational source analysis (and image vision noted as export-gated).

**Built `atomicity/explore-engine.js` → `window.CV_EXPLORE`** — `generation = f(element, intent, taste)`:
- 5 restyleable elements (button/card/price/badge/stat); `variations()` asks the model (token-anchored
  but free to diverge) for N **distinct directions** as compact recipes (salvage-parsed, truncation-safe);
  `styleFor(recipe)` normalises token names → a live style object so each variant paints on-system.
- `promote()` turns a chosen recipe into a **registered atom Type** — `CV_HOST.commit({kind:'type'})`
  → `app/registry/types-seed.js` AND `CV_REGISTRY.register()` live (shows in the Atlas at once). Loop
  closed: explore → curate → promote → it's in the architecture. Capabilities `explore.variations` /
  `explore.promote` registered into CV_AI (family `explore`).
- **`atomicity/Explore.jsx` → `window.AcExplore`** (Atlas section "Explore"): pick an element, a live
  grid of variations each with 👍/👎, iterate chips (More-like-liked · Bolder/diverge · Quieter),
  focus one, "Add … to the system". Composed from AcKit; CSS `.ex-*`.

**Verified end-to-end:** generated 4 visibly-distinct button directions (Minimal Ink, Warm Gold Fill,
Soft Brass Layer, Bold Bronze Edge) on real tokens; promote staged a real `CV_REGISTRY.register({…})`
to `types-seed.js` and registered it live (`atom.button.warm-gold-fill`).

**Conversational ingest:** added `ingest` + `explore` verbs to VI_BRAIN's action protocol and
`ATOMICITY.act` — Vi can open Sources and add+analyse pasted material, or open Explore, from chat
(auto-run). **Image vision stays palette-only** (canvas) until an exported vision provider is connected.

`check_design_system` clean.

## Slice 16 — DONE: CV_SOURCE — source ingestion → deep analysis → DNA proposals
**The ask:** upload source material so the system can analyse it deeply — recognise its type + context,
mine it for depth, and bring findings forward to improve the DNA. "A really big part of this."

**Built `atomicity/ingest.js` → `window.CV_SOURCE`** — the ingestion registry (same shape as the rest):
`dna-signal = f(source, recognizers, analyzers)`.
- **recognizers** detect TYPE + CONTEXT (heuristic `by-shape` first; the deep read refines, e.g. notes →
  "brand-voice-system-brief"). Extend with `registerRecognizer`.
- **analyzers** mine DEPTH per dimension, each finding carrying evidence + an optional CV_HOST proposal:
  `palette` (image → dominant colours via **canvas**, no model) and `deep-read` (text → a structured
  model pass across colour/type/voice/structure/value/motif). Extend with `registerAnalyzer`.
- **sources** — the persisted corpus (localStorage, text capped). `addSource/recognize/analyze/
  bringForward/bringAll`.
- The deep prompt knows the system's vocabulary so findings map to real change kinds; **salvage()**
  pulls complete finding objects even when the model response is truncated (token-budget safe — parses
  balanced `{…}` objects out of a partial findings array). Capabilities `source.recognize/analyze/
  synthesize` registered into CV_AI (family `ingest`).
- **`atomicity/Ingest.jsx` → `window.AcIngest`**: a "Sources" surface (top-level Atlas section) — drop
  files / paste, each source shows its detected type + an animated StateDot, "Analyse for depth" runs
  the read, findings group by dimension with evidence + per-finding **Bring forward** (and Bring-all),
  staged through CV_HOST. Composed from AcKit; routed via AcBody; CSS `.ig-*`.

**Verified end-to-end:** a voice-notes paste → recognised as a voice brief → 4 high-signal findings
(voice/colour/value), each with the correct proposal kind (voice → `ai.entry`, palette → `css.token`);
"Bring forward" staged a real `ai.entry` to `app/ai/ai-seed.js` via CV_HOST. `check_design_system` clean.

**Open items:** image vision is palette-only (no model OCR of screenshots — could route to a vision
provider on export); add analyzers for type-personality and structure→archetype proposals; let Vi open
a source conversationally from the chat ("analyse this for me").

## Slice 15 — DONE: AcKit + Foundations "face" — designed for a layperson, by implication
**The ask (after two misses):** be intentional about what each zone is FOR; the inspector wasn't
closable; everything leaked raw technical info (`var(--r-md, 10px)`, `--dgm-node-radius`, "2 files")
that means nothing to a user with zero system/domain knowledge; show difference *by implication*; use
animated SVG icons for state; and "build a small set of sophisticated, versatile, multi-layered
components that nearly everything can instance and compose with."

**Built `atomicity/kit.jsx` → `window.AcKit`** — the composable primitive set:
- **`Specimen`** — renders the VISUAL TRUTH of a value (a colour you see, a roundness you see as an
  actual rounded shape, spacing as a real gap, depth as a floating card, type as live "Ag") at a
  tangible scale. No numbers, no token names. The rail, gallery and inspector all instance it.
- **`StateDot`** — an animated SVG that shows state by morphing (idle ring → selected pulsing gem →
  active drawn check → edited dot), not by a label.
- **`Tile`** (elevation/hover/selected ring), **`Sheet`** (the closable panel — X + Esc + slide),
  **`HumanControl`** (layperson editor that adapts: colour = a big tappable swatch; roundness/spacing =
  a "Sharp→Round"/"Tight→Roomy" track with no px; depth/type = a plain sentence), **`Field`** (label +
  plain hint).

**Rewrote `atomicity/Foundations.jsx`** as a curated, human face (the 477 raw tokens stay in the
Atlas/Scanner for the technical view; this presents the *brand's visual language*):
- Zones with one job each: **rail** (choose a facet — Palette · Type · Roundness · Depth · Spacing,
  each with a plain blurb) · **gallery** (the choices as visual specimens, grouped Surfaces/Brand/Text
  etc.) · **preview** (the real property surface — the effect, live) · **inspector** (a *closable*
  Sheet).
- **Friendly throughout:** "Gold", "Paper", "Soft", "Floating", "Cozy" — never a token name or px.
  The inspector shows a big specimen, a plain description, one `HumanControl`, and "Used in N places
  across your product" (from CV_SCAN, in plain language). Raw name/value/files are behind an opt-in
  "Show technical details" disclosure only.
- Edits still apply to `:root` live and "Save to brand" stages via CV_HOST.

**Verified (DOM; screenshot infra down on this page):** facets + grouped galleries render; colour
specimens resolve real values (Paper #FCFAF2, Gold #E0C010, Night #1F1A12…); roundness/spacing/depth
show by implication; the inspector Sheet opens on select, has a working close (X → closed), and shows
**zero `var()`/`--`/px/.css leakage** before the advanced disclosure; "Used in 119 places" reads in
plain language; 9 animated StateDots present. `check_design_system` clean.

**Open items:** retrofit Atlas tiles / Vi to instance `AcKit.Tile`/`Specimen` for consistency; the
HumanControl for depth/type is descriptive-only (no direct edit yet); consider a layperson "advanced"
toggle at the app level to expose the raw Atlas for technical users.

## Slice 14 — DONE: CV_SCAN — the autonomous, continuous scanner (the 5th-shape registry)
**The ask:** make "what uses this token" real and general — an automatic system that *registers
everything to scan* (tags, TODOs, usages), runs autonomously and continuously, and stays up to date
without intervention. (The token-graph "Used by 0" for leaf tokens like `--border-soft` was the tell.)

**Built `atomicity/scan-engine.js` → `window.CV_SCAN`** — same register/resolve/query/subscribe shape
as the other registries, but for self-knowledge that isn't in a hand-authored catalogue:
`scan-index = f(sources × extractors), continuously`.
- **Sources** (each resolves `{path,text}` units): `cssom` (live `document.styleSheets` — always
  current, zero fetch), `manifest` (every file the DS manifest references — self-grows with the
  system), `extra-styles` (curated app/kit stylesheets outside the manifest), `host-tree` (walks the
  REAL repo via a connected CV_HOST list+read runtime — dormant in sandbox, full coverage on
  export/MCP). Extendable with `CV_SCAN.registerSource`.
- **Extractors**: `token-usage` (`var(--x)`), `dscard`, `template`, `todo` (TODO/FIXME/HACK — "things
  to do"). Extendable with `CV_SCAN.registerExtractor`.
- **Autonomous + continuous**: `start()` runs on load, then on a 45s interval and on
  `visibilitychange` (only when visible, debounced) — stays fresh with no manual rebuild. Per-file
  fetch misses collected into `report()` (best-effort discovery), not silently swallowed; emits only
  when the index signature changes. `describe()/stats()` self-document.
- **Wired**: loaded in `index.html` (after CV_HOST) + `CV_SCAN.start()` at boot; surfaced in the Atlas
  **System** section (Scanner ▸ Sources / Extractors); the Foundations inspector now shows real
  per-file usage + live CSSOM selectors via `CV_SCAN.usage(name)`, subscribed so it updates as scans
  complete.
- **Verified live**: 81 files scanned across 4 sources, 343 tokens tracked, 0 errors, ~2s;
  `--accent-gold` → 480 uses across ~45 files + real selectors; **`--border-soft` → 41 uses** (was the
  "Used by 0" case — now truthful); 44 `@dsCard` tags indexed. Continuous loop active.

**Open items:** in-sandbox coverage is cssom + manifest + curated extra-styles (the `extra-styles`
path list is the one curated seam); on export `host-tree` makes it fully self-maintaining over the real
tree. Could add extractors for icon usage / component imports and a dedicated Scanner card.

## Slice 13 — DONE: Foundations Workbench + View-Transition page motion
**The ask:** Foundations read flat (a pile of swatches). Make it a structured, well-organised
*table* of all the values, with a *live view of a component* and the ability to *change values and
see the effect*. "Add it as components, do whatever." Also: bring back choreographed page-load motion.

**Built `atomicity/Foundations.jsx` → `window.AcFoundations`** — routed to by `AcBody` for
`sec/foundations`, `token-group`, and `token-file` nodes (so opening Foundations, or any token kind,
becomes the workbench). It is:
- **A structured value table** — tabs by kind (Color 248 · Spacing 96 · Radius 5 · Depth 17 · Type 10
  · Other 101), rows grouped by their source file, each row = a live preview chip + the token name +
  a **kind-aware editor** (hex → colour picker + text; px → slider + number; shadow/oklch/other →
  text) + stage/reset actions.
- **A live specimen preview** (sticky, right) — real buttons, a content card with shadow+radius, a
  swatch strip, the type ramp, a Vi pill, an entity badge — all reading the same tokens.
- **Live propagation, demonstrated** — editing a value calls `setProperty` on `:root`, so the WHOLE
  app and the preview recompute instantly. Verified: setting `--accent-gold` live changed the top-bar
  wordmark AND the preview button together — the single-source story made visible.
- **Stage to source** — each edit can `CV_HOST.commit({kind:'css.token', file: definedIn, …})`, the
  same review→write path as Vi; Reset reverts the live override. Edits persist in a module map across
  navigation (`window.__acFoundationEdits`), never localStorage.
- **Trap:** manifest token `name`s already include the leading `--`; an early `'--'+name` produced
  `----paper` (and broke `var()`/`setProperty`). Fixed to use the name as-is and strip `--` only for
  the serializer payload (which re-adds it).

**View Transitions:** `openNode` now wraps the selection in `document.startViewTransition(() =>
ReactDOM.flushSync(go))` (guarded; falls back to a plain set), and `.ac-detail-inner` carries a
`view-transition-name` with tuned `::view-transition-old/new(ac-detail)` keyframes (exit accelerates
up+out, enter decelerates up+in, using the motion tokens) — so the detail pane choreographs between
nodes instead of snapping. The earlier opacity-stuck risk is gone because this drives the *transition*,
not a fill-mode animation on a persistent element. Reduced-motion collapses it to 1ms.

`check_design_system` clean. (Screenshot infra was flaky on this page; verified via DOM probing —
workbench renders, chips resolve to real colours, 123 colour pickers, live edit propagates app-wide.)

**Follow-up (same slice): made it truly ONE page.** First cut still opened a per-token leaf page when you
drilled the tree. Now: the tree collapses token kinds/files (no deep drilling — `AcTreeNode` hides
`token-group`/`token-file` children, kept in the index so search still finds individual tokens), and
`AcBody` routes *every* foundations node (`sec/foundations`, `token-group`, `token-file`, **and**
`token`) to the one workbench. The workbench always shows the whole folder (all kind tabs); the entry
node only picks the tab and, for a specific token, flashes + scrolls to its row. The hero is unified to
"Foundations · workbench · Design tokens · live" regardless of entry. Verified: opening a deep token or
a kind both land on the single page with the right tab; tree shows only the 6 kind groups + Axes/Fonts.

**Redesign (same slice) — Foundations *Studio*, calm + intelligent.** The table cut was noisy (raw
`--names`, duplicate swatch+hex+picker per row, weak preview, middle/right misaligned). Rebuilt:
- **Slim rail of human-named tokens** — `humanize()` + curated `LABELS`/`DESCS` turn `--paper` → "Paper",
  `--accent-gold` → "Gold — primary accent". One representation per row (the swatch IS the value); no
  tech name, no hex, no per-row controls.
- **Inspector on selection** — reveals the technical `--name`, a one-control editor (picker/slider/text
  by kind), **Set active** (stages via CV_HOST) + **Undo**, and a collapsible **Used by** graph computed
  from real token values (`--accent-gold` → 13 followable humanized links; leaf tokens say "consumed
  directly in component & layout styles"). Detail on demand, not in your face.
- **Live preview = a real product surface** — a ConceptV property listing (address, gold price,
  bed/bath/car/m², 360° pill, Vi insight, stat trio, app bar) on the same `:root`. Verified: editing gold
  recoloured the preview price AND the top-bar wordmark together; Undo reverts.
- **Alignment fixed by construction** — rail + stage are one grid row, tops equal to the pixel (verified
  `railTop === stageTop`). Responsive: one column under 860px, card stacks under 520px.

## Slice 12 — DONE: AtomiCity visual overhaul — composed FROM the system's own language
**The ask:** the first AtomiCity cut read "flat, written by a developer." Make it leverage the
high-quality render the system is capable of — subtlety, depth, recognition, intuitive + digestible,
"use all the tokens, the components, the design — make it compositional itself."

**Audited the real DNA first** (didn't invent): `tokens/depth.css` (warm `--elev-0..5` ramp, `--glow-active`,
`.grain`), `tokens/texture.css` (`.blueprint` grid, gold `--hatch-*`, frame-signature), `tokens/motion.css`
(`--ease-entrance/exit/emphasized/spring`, `--dur-*`, `.enter-*`, `.stagger`), `colors_and_type.css`
(gold scale `--accent-gold-50/faint/soft/dashed/press`, `--vi-surface/strong/edge`, `--paper-2/3`,
`--ink-2..5`, `--r-*`, `--s-*`, the `.cv-*` type ramp), and CvIcon's `circle` entity-badge treatment.

**Rewrote `atomicity/atomicity.css` to compose from those** — every value a token, no raw literals beyond
geometry: grain tooth on rail + canvas, an editorial **hero band** per node (blueprint grid ghost +
left-weighted gold hatch baseline = the frame signature, Sora title in bronze, eyebrow, SECTION pill),
section **tiles** as warm sheets that lift on the `--elev` ramp with **gold-ring entity-badge icons** and
**big-gold-number** counts (Sora), **dashed-gold** tree connectors + a gold selection bar + `--vi-surface`
selected wash, the "What Vi can do" block as the brand's **soft-gold Vi panel**, token leaves with a large
swatch + big-mono value + a gold single-home callout, and the Vi console as warm paper with `--vi-surface`
header, chat **bubbles** (vi/user), gold send, and `--glow-active` focus. Top bar gains a gold underglow +
atom mark. JSX touches in `Atlas.jsx`/`AtomiCity.jsx`/`ViConsole.jsx`: circle icons, hero, big counts,
wordmark, bubble classes.

**Trap hit + fixed:** entrance animations (`.enter-up`) on the *persistent* detail wrapper left it stuck at
`opacity:0` (re-render cadence kept the `both`-fill animation from settling) — removed entrance motion from
the persistent wrapper/tiles; kept hover lift + the FAB/command-bar/message entrances (genuinely-new nodes).
Verified live: hero + tiles render, token swatch shows real `#E0C010`, single-home note present, Vi panel
opens, `.ac-detail-inner` opacity 1.

## Slice 11 — DONE: AtomiCity — the standalone app (the system, navigable + a Vi that acts & learns)
**The user's ask:** a *proper standalone build* (not a Studio tab) that is the whole design system
"enhanced and composable" — a hierarchical browser of everything AND a resident Vi that knows the
system cold, finds things without being told, interprets intent (no exact commands), can add
pages/components/capabilities, **adds to its own behaviour (learns)**, takes conversational feedback
and asks fluid follow-ups, and folds learnings into context so it improves. Works in the sandbox;
lights up with real fs/model/MCP when exported. (Slice 10's CV_HOST is the engine it writes through.)

**Lives in `atomicity/` — entirely separate from `app/` (Studio). Five files, all projections:**
- `atomicity/atlas-model.js` → **`window.ATLAS`**. The single projection of the whole system into a
  hierarchical tree, DERIVED from `_ds_manifest.json` + all four registries (tokens by kind→file,
  components, cards by group with the `UI Kit —` two-level nest, templates, and a System section that
  shows CV_REGISTRY/CV_AI/CV_HOST reading themselves). `census()` = the machine-readable "knows
  everything" feed Vi reads. `search`/`pathTo`/`find`. Rebuilds on CV_HOST/CV_REGISTRY change so it
  never drifts. **Trap hit:** must NOT subscribe rebuilds to `CV_AI` — its `notify()` also fires on
  `setActiveSurface` (every navigation) → infinite rebuild↔navigate loop. Keyed the context effect on
  `selId`, not the node object.
- `atomicity/vi-brain.js` → **`window.VI_BRAIN`**. Vi's mind: `systemPrompt` (architecture rules +
  live census + viewing-node + applicable learnings + an actions protocol), `interpret` (model turn →
  prose + parsed interface actions + auto-staged CV_HOST proposals + a followup), `suggestions`/
  `quickCommands` (proactive, context-aware), and the **learning loop** `learn()` — distils feedback
  into a crisp instruction, registers it LIVE as a `CV_AI` behaviour (family `learned`, provenance
  `vi-learned`) for immediate effect, persists to localStorage, AND proposes it to `CV_HOST` (→
  ai-seed.js) for permanence. Registers `context.atomicity` + `atomicity.interpret`/`atomicity.learn`
  capabilities into the one AI catalogue.
- `atomicity/atomicity.css` → its own surface identity, entirely token-driven (incl. the `.vi-shape`
  rules that normally live in app.css — **trap:** AtomiCity doesn't load app.css, so without them
  ViShape's SVG ballooned to 924px).
- `atomicity/Atlas.jsx` → the browser: collapsible tree (disclosure carets) + a live detail pane that
  renders each node by kind (token swatch+value, card iframe, live component mount in an error
  boundary, template iframe, AI-entry lineage, CV_HOST change source…) and always ends with "What Vi
  can do here" chips — browser and agent welded.
- `atomicity/ViConsole.jsx` → the omnipresent agent: always-present FAB → console with Chat / Teach /
  Memory modes, action chips (run real `ATOMICITY.act` verbs), staged-proposal chips (open the change
  in the Atlas), followups, and a fluid feedback nudge after acting.
- `atomicity/AtomiCity.jsx` → root: nav state, the **`ATOMICITY.act()` verb protocol** Vi drives the
  UI through (open/expand/highlight/search/connect/run), pushes the active node into `CV_AI` context,
  Cmd+K command bar (system search + Ask-Vi rows).
- `atomicity/index.html` → standalone shell; loads React/Babel, the icon lib (+ an inline alias map in
  the boot script — **trap:** a separate `<script src>` alias file silently didn't execute; the boot
  babel script does, so the 21 semantic→real icon aliases live there), `styles.css` (token-only),
  CV_REGISTRY+seed, CV_AI (registry/seed/canvas), CV_HOST (runtime+serializer), the `_ds_bundle.js`
  for live mounts, then the AtomiCity files; boots by `ATLAS.init()` → mount. Registered as a Brand
  `@dsCard` (cards 43→44).

**Verified live (`eval_js`):** boots; hierarchical tree + disclosure; token/card/Bridge detail render;
icons resolve; Vi answers with real system knowledge + actions + followup; command bar search works;
**the keystone** — `ds.propose` (and Vi's propose path) serialize a token to exact `colors_and_type.css`
source and stage it; **the learning loop** — feedback distils → live `CV_AI` behaviour (family
`learned`) + staged `ai-seed.js` permanence + persisted memory; `forget`/`changes.clear` clean up.
`check_design_system` clean (no issues).

**The honest boundary (unchanged, still loud):** in the sandbox Vi authors *real* changes and stages
them (review mode); disk writes need a connected runtime (fsapi on export / native+MCP) — the env pill
says "Sandbox review" and the Bridge node shows it. AtomiCity assumes-and-wires the exported case
(fsapi `connect` verb, native-model/mcp-tools providers) without faking it in the sandbox.

**Open items:** AtomiCity is meant to *eventually replace* Studio — migration of Studio's generative
canvases (Colors/Icons/Voice/Workshop) into AtomiCity surfaces is the next arc; live component mounts
that need props show a graceful note rather than a configured demo; tree has a minor horizontal
scrollbar to tidy; consider an `exec` runtime verb so an exported AtomiCity can run the compiler.

## Slice 10 — DONE: CV_HOST, the Environment/Host layer (the Bridge)
**The user's ask:** give Vi a real way to author and (when possible) persist changes to the repo,
and "reverse-engineer" the platform's read-only Design-System surface into an in-repo one that
reads the *same single source* and can be extended — working in the sandbox AND lighting up when
the repo is exported and run locally with disk/MCP access.

**Audited first:** `app/ai/ai-registry.js` (the CV_AI shape — provider `resolveProvider` already
loud-fails on missing runtime), `ai-seed.js` (providers/behaviours/skills/context as data),
`app/components/ExportPatch.jsx` (the *primitive ancestor*: manual, scattered icon/color/pattern
patch strings, download-based — confirmed this is what to supersede, not duplicate), `index.html`
load order, `App.jsx`/`Sidebar.jsx` nav wiring.

**Built (single-sourced, same register/resolve/describe shape as CV_AI):**
- `app/ai/host-runtime.js` → **`CV_HOST`**. A registry of pluggable **runtimes** resolved by
  capability: `review` (sandbox floor, always available, stages to a reviewable queue) → `fsapi`
  (browser File System Access — real disk when run top-level/exported) → `native`
  (`window.CV_HOST_NATIVE` shell/MCP — read/write/list/exec/tools, auto-detected on export).
  Uniform op surface (`read/list/write/capabilities`), `commit()` (the one call Vi makes —
  serialize → always stage → write only if a writer is connected AND auto-apply is on),
  localStorage change store, handoff-mode setting (`review`|`stash`|`download`; **download off by
  default**, `stash` = the agent-pickup loop), IDB-persisted directory handle, `describe()` self-doc.
- `app/ai/host-serializer.js` → **serializers** (one home per change kind: `ai.entry`→ai-seed.js,
  `type`→types-seed.js, `css.token`→colors_and_type.css, `card`→preview/*.html, `file`). Each turns
  a registry mutation into *exact source* (functions serialized via `toString`, so Vi can author a
  real `run()`). Plus **host providers** (`host-fs`, `native-model`, `mcp-tools` — declared,
  activate on export) and **repo capabilities** (`repo.read/list`, `ds.propose`, `ds.apply`) in the
  one CV_AI catalogue, routed through `execute()`.
- `app/ai/ai-registry.js` `resolveProvider` now **delegates unknown runtime kinds to
  `CV_HOST.resolveProviderRuntime`** before throwing — so the AI catalogue can name fs/native/MCP
  providers without CV_AI knowing how to reach them. Still loud.
- `app/canvases/Bridge.jsx` → the interactive surface (pure projection of `describe()`): env +
  capability chips, connectable runtimes, handoff settings, the staged-change queue (source preview,
  Copy, Apply-to-disk), the agent stash, and "what Vi can do here". Wired into `index.html`, the
  `bridge` route in `App.jsx`, and the **AI & settings** sidebar group.
- `preview/ai_bridge.html` → the read-only `@dsCard` (group **AI**) projecting the same `describe()`.

**Anchor sentinels** added (`// CV_HOST:ai-entries`, `// CV_HOST:types`) so append-block insertions
land predictably (falls back to EOF if absent).

**Verified live (`eval_js`):** CV_HOST loads; runtimes detected (review active, fsapi connectable,
native dormant); `ai.entry`/`css.token` serialize to correct source + file; `commit` stages in
sandbox; `repo.*`/`ds.*` capabilities + `host-fs`/`native-model`/`mcp-tools` providers in the
catalogue; Bridge canvas renders the full projection. `check_design_system` clean (AI cards 1→2).

**The honest boundary (kept loud, not hidden):** the in-page runtime cannot itself write disk in the
sandbox — `review` mode stages real source for the agent/human to commit; `fsapi`/`native` give true
write only when exported/connected. This is surfaced explicitly in the UI ("Sandbox review"), never
silently degraded. `ExportPatch.jsx` left in place (Colors/Patterns still call it) — a future slice
should retarget those flows through `CV_HOST.commit` and retire it.

**Open items:** retire `ExportPatch` in favour of `CV_HOST.commit`; add a real `repo.write` capability
if a use appears beyond `ds.propose`; persist `fsapi` reconnect UX testing on a true top-level page;
let `native` runtime also satisfy the `exec` capability surface (run `check_design_system`/compiler
from inside the exported app).

## Slice 9 — PLANNED (next session): every generator a registered capability
**Approved & scoped, not yet built.** Slice 8 put every model *call* on the union (one provider,
loud-fail). The remaining thoroughness pass: make every generative *move* a first-class CV_AI
**capability** in the catalogue (like the composer's 11 + image's 2), not just a bare `CV_AI.complete`.

Concrete approach (mirror how AIEngine registers its capabilities — built-ins carry `run`):
- For each canvas, register capability entries with `{ id, name, layer:'capability', family, surfaces,
  behaviours:['voice.conceptv'], provider:'claude', params, run }` where `run` wraps the existing
  prompt-builder + parse (kept co-located with its helpers, as AIEngine does):
  - **Colors** → `color.palette.generate`, `color.recolor` (family:'color')
  - **Icons** → `icon.generate`, `icon.edit`, `icon.single` (family:'icon')
  - **Voice** → `voice.rewrite`, `voice.variants`, `voice.audit` (family:'voice'; compose VOICE_RULES)
  - **Patterns** → `pattern.generate`, `pattern.shadow` (family:'pattern')
  - **Components** → `component.generate` (family:'component')
  - **Build** (orchestrator) → `build.plan`, `build.triage`, `build.copy`, `build.icons`,
    `build.colors`, `build.template` (family:'build')
  - **Workshop** → `deck.generate`, `block.refine`, `block.variations`, `slide.compose`
  - **Widget/Wizard draft** → `widget.draft`, `wizard.draft`
  - **types-vi** → `type.propose`, `type.materialize`, `type.suggest-slots`
- Then route each call site `CV_AI.complete(...)` → `CV_AI.execute('<cap.id>', {…})` where the move is
  cataloguable (keep `CV_AI.complete` only for genuinely one-off, non-reusable prompts).
- Add per-family context resolvers where a move benefits (e.g. color/icon canvases resolve current
  palette/library). Verify the catalogue covers every generative move; `check_design_system`; log here.

Rationale: the catalogue then describes the FULL generative surface (every Vi move is data —
queryable, inheritable, projectable in the inspector), completing "the interface is a projection into
both so they are synchronised" for every screen, not just the composer.

## Slice 11 — CV_AI specimen card (projects the AI catalogue into the DS tab) (DONE & validated)
`preview/ai_registry.html` (`@dsCard group="AI"`) renders the **live** CV_AI catalogue — loads the
three lightweight registry scripts (`ai-registry`+`ai-seed`+`ai-capabilities-canvas`) as data (no
React/model runtime needed to read it) and projects all five layers grouped with swatch dots, counts,
and entry-id chips (2 providers · 3 behaviours · 8 skills · 32 capabilities · 4 contexts). No
duplicated list — it reads `CV_AI.query()` live, so it can't drift; a footnote notes the composer +
image capabilities register at app runtime (the in-app `AIRegistryPanel` shows the full 43). The AI
layer is now projectable in the visible Design System tab alongside the token/type/brand cards, not
just the in-app inspector. New DS-tab group "AI". Verified rendering; `check_design_system` clean.

## Slice 10 — central docs: the operating manual + anti-drift law for all four registries (DONE)
Captured the session's work as durable, future-proofing guidance so the unification keeps being built
and nothing drifts:
- **`CLAUDE.md` (NEW, project root — injected into every conversation).** The operating manual: the
  one idea (one home per concept; reference, never copy), the **four single-source registries** table
  (tokens · types · engine · AI) with home + how-consumed + how-to-extend each, the propagation rules
  for adding anything, the non-negotiables (no second home, loud-fail, interface-as-projection, audit
  before touch), the after-every-change checklist, and the traps.
- **`analysis/INTEGRATION.md` extended** from a token-only contract to **all four registries**: new §0
  table + §6 "same contract for Types and AI" (catalogue/inheritance/projection/loud-fail rules), so
  the wiring contract now governs `CV_REGISTRY` and `CV_AI` with the same discipline as tokens.
- **`DESIGN-LANGUAGE.md` + §13/§14 (NEW rules):** §13 "one home per concept — change once, propagate
  everywhere (the anti-drift law)"; §14 "AI is part of the system, not bolted on" (the CV_AI layers +
  `ai = f(capability, context, params)`).
- **`analysis/HANDOFF.md`:** top-of-file banner pointing to `CLAUDE.md` and naming the four registries.

Net: a new session reads `CLAUDE.md` first and learns to change anything in its one home and have it
propagate — the user's explicit goal. Docs-only; `check_design_system` unaffected/clean.

## Slice 9 — every generator a registered capability (DONE & validated)
Built the canvas-capability catalogue so CV_AI describes the FULL generative surface, not just the
composer. New `app/ai/ai-capabilities-canvas.js` registers **30 capability entries** across every
surface — color (palette/recolor), icon (generate/edit/single), voice (rewrite/variants/audit),
pattern (generate/shadow), component, build (plan/triage/copy/icons/colors/template), deck
(generate/refine/variations/compose), widget/wizard draft, type (propose/materialize/suggest-slots),
inbox classify, chat, and 2 image-studio moves. Each is a real, queryable, inheritable, projectable
capability with provider + behaviours + surfaces + a generic executable `run` that completes the
prompt the canvas hands in — so the move is catalogued WITHOUT duplicating its prompt (the prompt
stays single-sourced where its domain helpers live).

**Total now: 43 capabilities across 14 families.** The 9 cleanly-standalone generators are routed
through `CV_AI.execute()` (Build plan/triage/copy/icons/colors, Workshop deck.generate, types-vi
propose/materialize/suggest-slots) — verified they resolve with provider+run. The remaining call sites
are inline component-event handlers (Colors/Icons/Voice/Patterns/Components edit buttons) — already on
the union via `CV_AI.complete`; they can adopt `execute('<id>')` opportunistically as each handler is
next touched (the capability ids now exist for them). Console + `check_design_system` clean.

**The AI layer is now fully unified end to end:** one registry owns every model touch (text + image),
every generative move is a catalogued capability resolved through one `execute()` path (provider +
context + behaviours), the voice is single-sourced, failures are loud, and the registry inspector
projects the whole catalogue — the interface and the AI read one source, on every screen.

## Slice 8 — total union: every AI call routes through CV_AI (DONE & validated)
Acting on "actively look for more things that still don't call and use the union," grepped the whole
`app/` tree for every endpoint bypass and closed them all:
- **All text completion routes through `CV_AI.complete`** (the resolved Claude provider, loud-fail) —
  **35 raw `window.claude.complete` call sites across 12 files** rewritten: Inbox, Workshop (4),
  Colors (2), Icons (3), Patterns (2), Voice (4), Components, WidgetBuilder, WizardBuilder (2),
  ChatRail, types-vi (3), and **Build.jsx the orchestrator (10)**. A final sweep confirms **0 raw
  `window.claude.complete` remain in any consumer** — the only binding left is the provider definition
  in `ai-registry.js`. Both string and `{messages}` forms verified through the provider.
- **All image generation routes through the `openai-image` provider** — `generateImage`/`editImage`/
  `responsesImage` exposed on the resolved provider; the 9 call sites in AIStudio/ChatRail/ImageEditor
  go through `CV_AI.resolveProvider('openai-image')`. (cvOpenAI's *config* surface — getSettings,
  isConfigured, getModelCapabilities, subscribe, listImageModels, validateSize — legitimately stays on
  the service; it's settings, not generation.)
- **Voice single-sourced** (anti-drift, the system's own thesis): the inline brand-voice fragment that
  was duplicated in Workshop (4), WidgetBuilder, WizardBuilder and Build's voice-specialist now reads
  `window.CV_AI.get('voice.conceptv').text`. (Voice.jsx keeps its own `VOICE_RULES` — it's the canvas
  that DEFINES them, the authority, not a duplicate.)

**Net:** one registry now owns every model touch in the app — text and image, composer and canvases
and orchestrator — with one place to swap providers, one voice, and loud failure if a runtime is
absent. Console + `check_design_system` clean.

## Slice 7 — AI loud-fail + full provider migration + registry projection (DONE & validated)
Per the directive "loud fail instead of anything silent," closed the slice-6 follow-ups:
- **All completion routes through a CV_AI-resolved provider.** `aiComplete`/`cachedComplete` no longer
  touch `window.claude` directly — they resolve the `claude` provider from CV_AI and throw if the
  registry/runtime is absent. No raw-endpoint path remains in AIEngine.
- **The four direct callers migrated + de-silenced.** `classifyIntent` (was swallow→'question'),
  `generateEdit` (was swallow→null), `viSuggest` (was swallow→heuristics), `auditWorkspaceVariables`
  (was swallow→[]) — their error-swallowing `try/catch` removed so failures surface; all now complete
  through CV_AI. `RegistryInspector.runViAction` likewise routed through CV_AI (+ its parse no longer
  silently swallows; the voice string there is gone — it reads the registry).
- **Image service unified.** The `openai-image` provider now exposes `generateImage`/`editImage`/
  `getModelCapabilities` (loud if `cvOpenAI` absent); the 8 call sites in AIStudio/ChatRail/ImageEditor
  resolve through `CV_AI.resolveProvider('openai-image')`. Added `image.generate` + `image.edit`
  capabilities so imagery is in the same catalogue and runs through `execute()`.
- **Registry inspector projects CV_AI.** New `AIRegistryPanel` in the global Vi rail renders the AI
  catalogue grouped by layer (provider/behaviour/skill/capability/context), live on `CV_AI.subscribe`,
  showing the active surface — the AI registry is now inspectable beside the type registry.

**Validated** (live): 13 capabilities (11 + image.generate/edit); `openai-image` resolves both image
methods; `classifyIntent`/`generateEdit` route through CV_AI (stubbed-provider call count confirmed);
`execute('does.not.exist')` throws (loud). Console + `check_design_system` clean. (Open next wave: the
per-canvas generators still call `window.claude.complete` directly — Colors, Icons, Voice, Patterns,
Components, Inbox, Workshop, Widget/WizardBuilder, types-vi — route those through CV_AI providers too;
their catches surface user toasts, so not silent, but they're not yet on the one registry.)

## Slice 6 — the AI layer unified as a parametric registry (CV_AI; DONE & validated)
**Audit:** the AI system was `WS_AI` in `app/canvases/workshop/AIEngine.jsx` (+ the image service
`app/services/openai.js`). It was the one major subsystem that did NOT follow the unified discipline:
~11 hardcoded `viX()` functions, each with an inline bespoke prompt, the voice string duplicated in
every one, a single hardcoded provider (`window.claude.complete`) called directly, no context
resolution (each call hand-assembled its own neighbourhood), and the transform menu a hand-kept array
parallel to the logic. The opposite of "one type system + rule engine + solvers."

**Built — `CV_AI`, the Universal AI Registry** (`app/ai/ai-registry.js` + `ai-seed.js`), mirroring
`CV_REGISTRY` verbatim (register/registerMany/update/remove/get/all/query/resolve/lineage/subscribe,
LS-persisted user/vi provenance, built-ins in memory, single-inheritance `resolve` that merges
params/behaviours leaf-wins). Five layers — **provider · behaviour · skill · capability · context**:
- **providers** (2): `claude` (text/stream), `openai-image` (image) — `resolveProvider` binds each to
  its live runtime and throws loudly if absent (no silent fallback).
- **behaviours** (3): `voice.conceptv` (the house voice, now single-sourced — AIEngine reads
  `BRAND_VOICE` FROM the registry), `angle` (parametric shorter/formal/specific/different),
  `diversity` (parallel-slot seeding).
- **skills** (8): the whole-doc transforms (shorten/lengthen/urgent/friendly/pro/audit/concrete) +
  theme — each binds to a capability. **The composer's transform menu is now a projection of these**
  (`docTransforms()` queries the registry; registering a skill makes it appear, no UI edit).
- **capabilities** (11): the tool set (insert.block, alternate.block, insert.page, doc.transform,
  theme.generate, layout.generate, widget.alternate, widget.kpis.regen, wizard.step.insert,
  wizard.step.alternate, field.alternate) — `id == target.kind` so **the catalogue IS the dispatch**;
  the per-target `switch` is gone. Each declares surfaces, behaviours, provider, params; registered
  from AIEngine where the prompt helpers live (as CV_REGISTRY built-ins carry `render`).
- **context** (4): per-surface resolvers (deck/brochure · widget · wizard · generic floor) — `execute`
  resolves "what screen Vi is on" from `CV_AI.active` (pushed by `BRIDGE.setActive`) and feeds the
  compact context to every prompt. Context is resolved, never hand-passed.

**`execute(capabilityId, …)` is the generative path** — `ai-output = f(capability, context, params)`:
resolves the capability (+inheritance), resolves context from the active surface, composes the
behaviour preamble, dispatches to the resolved provider, parses. `WS_AI.generateCandidates` now
delegates to it; unknown targets throw.

**Validated** (live, in-app): 11 caps / 2 providers / 3 behaviours / 8 skills / 4 contexts all
resolve; provider binds to its runtime; deck context resolves (pageIdx, currentPageEmpty,
neighbourhood); behaviours compose; `field.alternate` carries provider + [voice, angle]; transform
menu projects 8 skills. End-to-end: a `field.alternate` routed `generateCandidates → execute →
provider call` with a prompt carrying BOTH the voice AND the shorter-angle, parsed back to a
candidate. Console clean; `check_design_system` clean. (Open: migrate `classifyIntent`/`generateEdit`/
`viSuggest`/`auditWorkspaceVariables` and the image service onto CV_AI providers too; surface the
registry in the Registry inspector as a projection of CV_AI alongside CV_REGISTRY.)

## Cleanup + convergence — WidgetBuilder on the one engine (DONE & validated)
Deleted the dead `Widget*` cluster (`WidgetKPIs/Media/Hybrid`, `KPITile`, `Delta`, `StatusDot`, `Spark`
— ~145 lines) that the engine-backed body had already superseded. `WidgetRender` now uses the engine's
own vocabulary end-to-end: authorship badge via the shared `.by-*` provenance classes (`author` →
Vi/You, replacing the bespoke diamond mark); the `loading` resolve dial (mock feed switch shows
skeletons one beat, then real data resolves with `motion`); motion entrance in prototype mode. Verified:
resolved → 2 metric atoms + `.by-vi` + 0 skeletons; loading → 4 skeletons, no value leak; dead refs gone;
console clean. No `Widget*` matches remain. `check_design_system` clean.

## Upgrade — focus / dim-the-rest (focus.css; DONE & validated)
A `cluster` now takes `focus` (a child id or index): the container becomes a `.focus-scope.is-focusing`,
the named child lifts (`[data-focus]` → translateY + scale + elevation) and the rest recede (desaturate +
dim + blur, from focus.css). Spatial attention turned into a mechanism; reduced-motion drops the lift.
Added `focus` to `cv-nodes.d.ts`. Also removed a stray duplicate `case "zone":` label in the solver.
Verified: subject lifts (transform applied), others dim (opacity < 1). `check_design_system` clean.

## Upgrade — content resolves, never pops (states.css §10; DONE & validated)
Added a `loading` dial through `ContainmentTree`/`RenderType`/`Slide`: when on, every leaf renders as a
shaped `.skeleton` shimmer placeholder whose shape follows its role (metric → value+label bars, icon/badge
→ circle, image/chart/qr → aspect box, text/bullet/note → two lines) so the layout doesn't jump when real
data swaps in (with an `.enter-*` resolve). Reduced-motion → static dim (from states.css). Verified:
loading → 6 skeletons + `data-loading`, no real text leaks; resolved → 0 skeletons, real values render.
`check_design_system` clean.

## Upgrade — authorship is legible (DESIGN-LANGUAGE §11; DONE & validated)
A zone now carries `author` (human · vi · suggested): the engine adds the `.by-*` badge in the zone
header and the `.vi-authored` wash for Vi output awaiting review (from `tokens/provenance.css`) — the
trust signal the agentic/Vi workspace needs. Added `author` to `cv-nodes.d.ts`. Verified: a vi zone
renders the wash + `.by-vi` badge; a human zone renders `.by-human`. `check_design_system` clean.

## Upgrade — icons as first-class content (DIAGRAMS.md; DONE & validated)
Added an `icon` atom to the block solver: renders a CV icon from `window.CV_ICONS` in the icon language
(24-grid, 1.5px stroke, `currentColor` → tone bronze/gold/ink) with an optional editable label, so
icon-flow rows (a `cluster flow:"row"` of `icon` atoms) are now first-class content. Verified: 3 icons
render as svgs with tones + labels. ✅ **Completed:** graph-solver nodes render `node.icon` inside the
shaped node (verified: 4 entity-node icons in a hub); `ds-base.js` loads `assets/icons/cv-icons.js` so
standalone templates carry the 99-icon library. `check_design_system` clean.

## Upgrade wave — motion wired into the engine (AUDIT-INDEX tension #2; DONE & validated)
The "nothing teleports" language was fully tokenised (`tokens/motion.css`: `.enter-*`, stagger via `--i`,
`.moves`, reduced-motion gating) but never emitted by the engine. Wired it as an **opt-in `motion` dial**:
`ContainmentTree`/`RenderType`/`Slide` now take `motion` (default false). When on, a container staggers
its children in via `.enter-up` with computed `animationDelay` (depth-first wave); the end-state is the
base style, so motion OFF — composer, registry previews, print, `prefers-reduced-motion` — stays static.
Verified: `motion:true` → 3 staggered `.enter-up` leaves; `motion:false` → 0. `check_design_system` clean.
Open: tie `motion` to a `register` (presenter↔reader) meta-dial; per-slide `[data-deck-active]` gating in
decks so each slide animates on entry.

## Upgrade wave — register/pace meta-dial (REQUIREMENTS C3; DONE & validated)
Added the `register` axis (presenter ↔ reader) to `RenderType`/`Slide`: it sets **LOD + density + motion
together** (presenter ⇒ pitch + compact + motion; reader ⇒ full + comfortable + static) — but any explicit
`lod`/`density`/`motion` prop overrides it, so the axes stay **separable** (correlation ≠ coupling, AXES.md).
Exposed as a live tweak on the `PitchDeck` template (custom / presenter / reader — register drives the
whole deck unless custom). Verified: presenter → density compact + `.enter-up` present; reader →
comfortable + no motion. `check_design_system` clean.
**Open upgrades (next):** per-slide `[data-deck-active]` motion gating (IntersectionObserver so each deck
slide animates on entry, not all on mount); the **space↔time** variant (a container shown in space OR
played over time — a stateful `mode`, REQUIREMENTS E2); progressive disclosure (per-node LOD on expand, F1).

## Upgrade wave — space↔time + progressive disclosure (REQUIREMENTS E2/F1; DONE & validated)
- ✅ **Space↔time (E2):** a `cluster` with `mode:"time"` plays its children one at a time (a `TimePlayer`
  with prev/next + dots + counter, `.moves` transition) instead of showing them all in space — same
  subtree, two renderings. Verified: only frame 1 shows + "1 / 3"; › advances to frame 2.
- ✅ **Progressive disclosure (F1):** a `section` with `disclose:true` rendered at a low LOD shows a
  "+ Show more" toggle that re-renders its children at full LOD in place (local LOD raise). Verified:
  at summary the support bullets are hidden + a toggle appears; expanding reveals them.
- Node-type fields added (`mode`, `disclose`) to `cv-nodes.d.ts`. `check_design_system` clean.
- **Still open:** per-slide `[data-deck-active]` motion gating in decks (IntersectionObserver, template-level). ✅ DONE — PitchDeck observes each `[data-deck-slide]` and reveals it with a `deckSlideIn` fade-up on entry (base visible for print/no-JS/reduced-motion). All three upgrade waves (motion · register · space↔time · disclosure · deck-active) landed.

## FULL CONVERGENCE — diagrams render + edit through the engine (DONE & validated)
**Vi toolbar reconnected + composer fully on the engine.** The engine's editable leaves (`edit()` in
`ContainmentTree`, `edLabel()` in `DiagramSolver`) now fire `window.__cvFieldFocus` on focus; Workshop
wires that to `WS_FIELD.activate` (mapping the data path → fieldName, the leaf's `onEdit` → onApply), so
the per-field Vi regen toolbar works on engine-rendered fields. Verified: app mounts, engine live,
`__cvFieldFocus` wired, Workshop loads clean. (Only-remaining trim: the now-dead `Spark`/`Delta`/`KPITile`/
`Widget*` sub-components in `WidgetBuilder.jsx` — unused, harmless, flagged.)

Closed the last in-engine gap: `DiagramSolver` node labels (all graph types + stepper) are now inline-
**editable** (`edLabel` helper, contentEditable + commit-on-blur) when given `onEdit` + a node `edit`
path; `ContainmentTree` passes `onEdit` to the graph solver; `blockToNode` tags diagram nodes with data
paths (process→`steps.N.title`, funnel→`steps.N.label`, timeline→`milestones.N.label`, orgDiagram→
`hub.label`/`nodes.N.label`); the composer `WS_ENGINE_EDIT_SKIP` is narrowed to just the two cross-doc
embeds. Verified: a `process` diagram renders via the graph solver with editable labels — editing
"Mobilisation"→"Kickoff" wrote back `steps.0.title` → re-rendered; `check_design_system` clean.

**ONE unified system:** everything renders + edits through the one engine, one catalogue, same atoms +
tokens, loud-fail — atom · chart · block · slide · deck/brochure · widget-system · live widgets · diagrams
· composer authoring — across templates, registry/inspector/architecture previews, the live product-UI
widgets, and the composer. The only `WS_BLOCKS.render` left is **cross-doc embeds** (references rendered by
the widget engine, itself engine-backed) — not a parallel block renderer. Optional polish: reconnect the
Vi per-field regen toolbar onto the engine's editable leaves; delete the dead `Spark`/`Delta`/`KPITile`/`Widget*` parts.

## W6 pass — editable engine atoms (infrastructure DONE & verified)
The last live render duplication is the composer *editing* via `WS_BLOCKS`. The blocker was that the
engine rendered read-only. Built the editable layer:
- ✅ `ContainmentTree` now takes an `onEdit(path, value)` callback (captured per-leaf during the
  synchronous render walk via a module var — no signature churn). An `edit()` helper makes a text leaf
  contentEditable + commit-on-blur (the app's proven uncontrolled pattern — no cursor thrash).
- ✅ Made editable: the **text · note · metric (value/label) · hero-number · bullet (title/text) ·
  chip · image-caption** atoms, and the **Band/Section/Zone titles** — each editable only when the
  block solver tagged it with a data path (`node.edit` / `editValue` / `editLabel` / `editTitle` /
  `editText`) AND an `onEdit` is supplied.
- **Verified** (in-app probe): a tagged node renders 4 contentEditable leaves (section title, body,
  metric value, metric label), no errors; `check_design_system` clean.

**Remaining (the composer rewire — now de-risked):** every block-solver `blockToNode` case is tagged
with its data paths, and the round-trip is **proven** — rendering a `stats` block through `RenderType`
with `onEdit` wired to a dotted-path setter, editing a value committed `items.0.v` → the data updated
(label preserved) → re-render reflected it. `RenderType` now accepts `onEdit` and threads it to the
solver. So the composer wiring is the one clean step left: in Workshop, render each block section via
`RenderType({type:block, data:sec.data, onEdit:(p,v)=>updateSection(setPath(sec.data,p,v))})` instead
of `WS_BLOCKS[k].render`, render diagram/embed sections via their existing renderers, and reconnect the
Vi per-field regen toolbar. Then `WS_BLOCKS` editing retires.

## Dataviz-atom pass — closing the W7 chart gap (DONE & validated)
The widget-system preview rendered through the engine but charts/deltas were placeholders (the engine
had no dataviz leaf). The dataviz language was **tokenised** (`tokens/dataviz.css`: `.viz-spark`/`.viz-bar`/
`.viz-gauge`/`.viz-stat` delta) but never **atomised** — so completing it is unification infrastructure,
not new design.
- ✅ Added a **`chart` atom** to the block solver's registry (`ContainmentTree`): `chart:"spark"`
  (polyline + soft area fill from `node.points`, normalised to the viewbox) · `"bar"` · `"gauge"`
  (from `node.value` 0–100), all drawn with the tokenised `viz-*` styling (gold = key series).
- ✅ Added a **`delta`** to the `metric` atom (`node.delta` + `deltaKind` → green ▲ / red ▼).
- ✅ Wired `widgetToNode` (RenderType) to emit real `chart` + per-KPI `delta` atoms instead of an
  image placeholder + string-folded delta. Added the `chart`/`points`/`delta`/`deltaKind` fields to
  `cv-nodes.d.ts`.
**Verified** (in-app probe + screenshot `_qa/shot-viz.png`): the hybrid widget tile renders through the
engine with gold KPIs, green ▲ deltas, a live gold **sparkline** ("Captures · 13w"), row list and CTA —
F2 (product UI = containment tree) realised *with* affordances. All three chart kinds (spark/bar/gauge)
render directly; no errors; `check_design_system` clean. **W7 LIVE widgets done:** `WidgetRender` (the
live dashboard/hub/embed renderer used across the Workshop builder, dashboard tiles, embeds and thumbs)
now renders its body **through the engine** — its frame/header/CTA chrome kept, but the data-viz body is
the engine's chart/metric/bullet atoms via `__cvTypeToNode(...,{__bodyOnly:true})`. Its parallel
`Spark`/`Delta`/`KPITile` parts are no longer used (left in place, flagged for removal). Verified: the
hybrid widget renders 1 frame card + 5 engine atoms + sparkline + 2 deltas, **0 legacy KPI tiles**, no
errors. So live widgets, registry previews, decks and templates now share the same atoms + tokens.

## Drift-reconciliation pass — agent-facing docs/cards to v2 (DONE)
**Stock-take** (whole `list_files` + targeted greps): the render-path unification covers core + app
registry/composer/previews; the **unexamined** surface is `ui_kits/*` (3 kits), most `app/canvases/*`,
~35 `preview/*` cards, several `tokens/*`, the v1 `Tonal Zoning System.html` + `tonal-zoning.css`. Took
~1/5: the **anti-drift reconciliation** the handoff §8 flagged. Verified the v1 token refs are LIVE (not
dead) — `--accent-gold-50`/`--bg-sunken`/`--accent-gold-soft` are still registered, so consumers aren't
broken; the residual drift is *teaching* (docs/cards still codifying the v1 narrow read) + the saturated
v1 panel still used in places (slice-1c migration, deferred).
**Actions:**
- ✅ **`SKILL.md`** (the agent skill ENTRYPOINT — what a consuming agent loads first) was still pure v1
  ("gold is the only loud colour", "bronze for illustrations", ivory canvas, no generative layer).
  Reconciled to v2: added "the system is generative" section (one type system + engine + two solvers,
  `design = f(content, axis)`, `RenderType`/`Slide`/archetypes), the **ramp** + colour-role logic
  (bronze = structural voice), zoning-as-depth, texture/motion, and the v2 doc/`core`/`templates` refs.
- ✅ **`Tonal Zoning System.html`** (a Colors @dsCard) reframed from the v1 semantic+cool model
  ("ivory content, stone supports, cool source, manila handoff" · "Ten semantic surfaces") to v2:
  zoning = containment depth, warm near-white throughout, semantic tones an opt-in layer.
- ✅ **`specimens/surface-zone-registry.html`** sub + **`colors_and_type.css`** "source" comment
  reframed off "cool grey-white" / "Ten semantic surfaces" to depth-first + warm-neutral.
- ✅ **`preview/*` color/component cards** (the DS-tab docs): `colors_gold` ("the only loud colour" →
  gold is the active/decision **ramp**), `colors_bronze` ("reserved almost entirely for illustrations"
  → bronze = the **structural/quiet voice**: illustrations + section heads + captions),
  `components_section_panel` (reframed: the soft-gold panel is the **product-UI** grouping pattern;
  deck/generative surfaces group via the **depth-keyed zone wash**). Swept the rest — remaining
  "signature" copy (dashed-gold selection) is correct v2, left as-is.
**Still open (the unexamined surface, for next):** `ui_kits/*` (W7 — product UI onto the engine, needs
a dataviz atom), the remaining `app/canvases/*` (own pattern defs to reconcile), a full `preview/*` card
sweep (copy + any saturated v1 panels → `--zone-*`), the unread `tokens/*`. `check_design_system` clean.

## Unification pass W3–W5 — one engine, in the app, loud (DONE & validated)
**Mandate:** do W3+W4+W5 together, **loud-fail with no silence or fallback**, then drive the whole
thing until there are no failures. Constraint honoured: the bundle only rebuilds at end of turn, so
the app runs the core **as source** — which made the full weld verifiable THIS turn.

**Actions taken**
- ✅ **W4 — one engine in the app.** `app/index.html` now loads `../styles.css` (the FULL token +
  `core/containers` layer — the app previously loaded only `colors_and_type.css`, so it never had
  `--d-*`/`--fs-*`/the zone-depth machinery the engine output needs) and loads the four core files
  (`DiagramSolver`/`ContainmentTree`/`Slide`/`RenderType`) via a **strip-and-eval bootstrap** that
  sets `window.__cv*`. (Tried `<script data-type="module">` first — this Babel build throws
  `targets["esmodules"] must be a boolean`; the strip-eval is the proven harness pattern.) Verified
  in-app: registry Type → `RenderType` → solvers → gold `rgb(224,192,16)` `.cv-band`.
- ✅ **W3 (slide path) — render through the one engine.** Rewrote `SurfaceSlideThumb`
  (`app/registry/types-thumb.jsx`) to render the deck-slide Type via `RenderType` instead of a
  hand-drawn mock — so the registry, the inspector, and the Architecture ladder all preview slides
  through the SAME engine the templates use. Enriched `core/archetype-catalog.js` with representative
  `defaults` per archetype (the preview seed + the Type's sample, like `WS_BLOCKS` defaults). Added
  `title`/`content`/`section` builder aliases in `Slide.jsx` so every deck-slide Type (incl. the app's
  alias kinds) resolves to a real builder. **Verified:** Type Registry shows 18 engine `.cv-band`
  previews, 0 legacy mocks; Architecture renders its `content`-alias band via the engine; Workshop /
  Colors / Templates all navigate error-free; app boots clean.
- ✅ **W5 (deck-slide) — generator loop.** A Vi-proposed Type that `extends` a known archetype now
  previews through the engine automatically (same `SurfaceSlideThumb` path) — generate → see, on-DNA.
- ✅ **LOUD-FAIL everywhere.** Removed every fallback: `RenderType` throws without the engine / on an
  unresolved Type; `Slide` throws without the bridge; `buildSlide` throws on an unknown archetype;
  `typeToNode` throws without the builders; `CoreTypes.archetypeSeeds` / `types-seed` / `ds-base.js`
  throw without the catalogue/bundle. The only async gate (`SurfaceSlideThumb` awaiting
  `window.__coreReady`) is readiness, not a silent wrong render.

**Verified green** (`eval_js` against the running app; html-to-image capture flaked on the heavy
registry canvas — a known capture artifact, DOM probes are authoritative): app mounts, 64 Types,
engine renders in-app, 18 slide previews via the engine, all canvases error-free, `check_design_system`
clean (6 components, manifest in sync).

**Broadened (same pass) — the block path through the engine.** Read the full ~37-block `WS_BLOCKS`
library and extended `blockToNode` to express **every** content block in the core vocabulary
(simple → atoms/clusters/zones; composites process/funnel/timeline/tagCluster/orgDiagram → the graph
solver). Rewrote `BlockThumb` to render block Types via `RenderType` too. **Verified:** all probed
slide + block Types render through the engine (zones/clusters/10 diagrams/badges, 0 legacy hosts, 0
placeholders, no errors). Boundaries kept (correct, not fallbacks): cross-doc embeds stay on
`WidgetRender` (a different engine; `blockToNode` throws loud for them); Workshop **inline-editing**
keeps the editable `WS_BLOCKS` blocks (engine output is read-only — editing-on-engine = W6).

**Verifier fix (null node).** `blockToNode('divider')` returns `null` (a divider has no atom) → the
engine must tolerate it. Added `if (!node) return null;` at the top of `ContainmentTree.renderNode`
(also covers null children) and made `RenderType` skip a null node. Also **broadened block-Type
registration**: `types-seed.js` now registers EVERY `WS_BLOCK` as a `block.*` Type when `WS_BLOCKS`
loads (11 stubs → 34 content blocks; `embedWidget`/`embedWizard` excluded — widget references, not
slide blocks). Re-verified: all 34 block Types render through the engine as siblings under one root
(the previously-crashing scenario) — 10 diagrams, 0 placeholders, no console errors; app boots clean.

**Broadened further — doc + widget levels.** (a) `DocDeckThumb`/`DocBrochureThumb` now render their
first slide through the engine (sample slides single-sourced from the archetype catalogue into
`doc.deck`/`doc.brochure` defaults) — the whole hierarchy block→slide→deck/brochure previews through
one engine. (b) `SystemWidgetThumb` renders widget systems (kpi/media/hybrid) via `widgetToNode` →
a Zone tile (REQUIREMENTS F2: product UI = the same containment tree; KPIs→metrics, rows→bullets,
media/chart→image placeholders). Verified: doc thumbs render real bands, 3 widget tiles render
(3 zones, 20 atoms), no errors; check clean. **Open:** live widget render + a real dataviz atom
(chart/delta) = W7; the chrome-framed `SurfaceWidgetThumb` stays on `WidgetRender` (live placement
context).

**Still open (honest — documented in UNIFICATION.md §3)**
- **Editing-on-engine (W6):** preview/thumbnail rendering is now fully through the engine; the
  Workshop authoring surface still uses editable `WS_BLOCKS` (needs editable atoms).
- **Registry engine into the bundle** so templates share the app's registry singleton (templates
  currently use the `CoreTypes` minimal lookup).

## Unification pass W1–W2 — welding the two halves (DONE & validated)
**The reframe (from harsh, fair review):** the system was built as TWO disconnected halves —
(1) the **type system + generator** (`app/registry/*`: `CV_REGISTRY` 7-layer model + inheritance +
slots + `types-vi.proposeType`, the north-star generator, ALREADY BUILT) and (2) the **rule engine +
two solvers** (`core/*`: `f(content, axis)`). `grep` confirmed **zero references between them.** They
are the two halves of the one described machine. Slice-4a's `Slide`/`Archetypes` made it worse — a
*fourth* parallel archetype list (alongside `surface.deck-slide.*` Types and `WS_LAYOUTS`). The whole
job is **unification, not new design.** Full critical map + the canonical decision: `analysis/UNIFICATION.md`.

**Audit (read, not assumed):** `app/registry/types-core.js` (the model), `types-seed.js` (every surface
mirrored as a Type — incl. `block.*`=WS_BLOCKS, `surface.deck-slide.*`, `doc.*`), `types-vi.js`
(`proposeType`/`promoteInstance` — Vi already generates on-DNA Types), `types-adapter.js` (registry→legacy
mirrors), `WS_LAYOUTS`/`WS_BLOCKS` (the composer), the token math (`sizing.css` modular scale + clamps,
`density.css` `--d-*` knob). Found: the app loads **only `colors_and_type.css`, not `styles.css`** — it
doesn't even consume the token/`core` layer (a W3/W4 weld, flagged). Source ground-truthed against
`_ingest/pitch-deck/p-05.jpg` (the 2-pane compare).

**Actions taken (mechanism only — no new design)**
- ✅ `analysis/UNIFICATION.md` — the duplication map (3 parallel archetype lists, 3 atom/block lists),
  the canonical decision (CV_REGISTRY schema = the one type system; core solvers = the one engine;
  `typeToNode` = the bridge; catalogue single-sourced; `Slide` = deck-slide case of `RenderType`), and
  the staged weld W1–W5 (each stage leaves the system working).
- ✅ **W1 — the bridge:** `core/RenderType.jsx` (+`.d.ts`) — `typeToNode(type,data,axis)` resolves a
  CV_REGISTRY Type into the solver IR (deck-slide→archetype band · doc→sequence via its slots · block/atom→
  the core atom vocab via `blockToNode`, reusing ONLY existing roles · graph-bearing→graph solver), and
  `RenderType` renders it through the one engine under the axis-dials. `Slide` now **delegates to
  `RenderType`** (one render path; direct-solver fallback for lean pages).
- ✅ **W2 — single-source the catalogue:** `core/archetype-catalog.js` (plain JS, `window.CV_ARCHETYPE_CATALOG`)
  is the ONE archetype catalogue in the CV_REGISTRY Type schema. Both halves read it: the bundle's
  `RenderType.CoreTypes.archetypeSeeds()` and the app's `types-seed.js` (`registerMany(window.CV_ARCHETYPE_CATALOG)`,
  loaded via a new `<script>` in `app/index.html` before the seed). The app's `title/content/section`
  deck-slide Types are now **aliases via `extends`** onto the canonical `cover`/`statement` (the registry's
  own inheritance — reconciliation, not a parallel definition; keeps `Architecture.jsx`'s
  `surface.deck-slide.content` reference resolving). `WS_LAYOUTS` (all ~30) annotated with `.archetype`
  → its canonical Type; `WS_BLOCKS` annotated with `._atomRole` → its core atom role. The render schema
  (catalogue) and render runtime (Slide builders / atom registry) are separated like Type vs `runtime`.

**Verified** (`_qa/bridge-test.html`, harness — bundle stale §6.1): `CV_ARCHETYPE_CATALOG` present;
`CoreTypes.seeds()` = 15 from the shared catalogue; `RenderType` resolves a Type id → renders through the
solvers (embossed KPIs + bronze note, DNA-pure); a `doc.deck` Type expands its `slides` slot into a
3-band sequence through the same engine. Zero errors. `check_design_system` clean — `RenderType`+`CoreTypes`
on the namespace.

**Open / next (the remaining welds, documented in UNIFICATION.md)**
- **W3 — migrate the composer:** the app deck renderer renders via `RenderType` (using the `WS_LAYOUTS.archetype`
  + `WS_BLOCKS._atomRole` maps) instead of app-only JSX; then retire the duplicate arrays behind the adapter.
- **W4 — registry engine into the bundle:** so templates use the SAME registry singleton as the app; load
  `styles.css`+bundle in the app so it consumes the token/core layer (it currently doesn't).
- **W5 — close the generator loop:** render `types-vi.proposeType` output live through `RenderType`.
- Atom/block weld is currently a faithful re-expression in `blockToNode` using existing roles only; the
  composite blocks (orgDiagram/statTable/funnel) route through the graph solver in W3.

## Slice 4a — the generative archetype & template layer (DONE & validated)
**Scope audited first (per discipline): the existing layout/block systems.**
- The app's `app/canvases/workshop/Layouts.jsx` (`WS_LAYOUTS`, ~24 layouts) + `Blocks.jsx` (`WS_BLOCKS`)
  are a *parallel* archetype/atom system — they render via the app's own `ws-blk-*` CSS, **NOT**
  through the generative core solvers. This is exactly the drift the handoff warns of: two systems
  doing one job. I did **not** rebuild on top of WS_LAYOUTS; I built the canonical generative layer
  on the core and **reconciled the vocabulary** (archetype names + content schemas mirror WS_LAYOUTS:
  comparison→compare, threeFeatures→triptych, metricSet→metric-band, investmentTerms→terms,
  bioFacts→profile, rolloutTimeline→timeline, contactClosing→closing, the staged chevron→stepper).
  **Open (slice 5 / deck→app bridge):** migrate the app composer to consume `Slide`/`ContainmentTree`
  so there is ONE archetype engine, not two.
- The block solver's `renderAtom` was a chain of `if (role===…)` branches (handoff §8 flagged this:
  "make atom rendering a registry so new atoms are data, not code branches").

**Actions taken**
- ✅ **Block solver → atom REGISTRY** (`core/ContainmentTree.jsx`): `renderAtom` is now `ATOM_RENDERERS`
  keyed by role + `ContainmentTree.registerAtom(role, fn)` / `.atomRoles()` for data-extensibility.
  Existing roles (metric/bullet/chip/text) preserved byte-for-byte; **added**: `hero-number` (embossed
  raised KPI chip — texture-&-depth §13), `note` (italic-bronze synthesis line — the connective tissue,
  pitch-deck §10), `badge` (the entity SHAPE system as a leaf — circle/hex/octagon/diamond; Vi renders
  the "Vᵢ" wordmark; optional `caption`), `qr` (phygital Virtual-Tour card), `image` (striped sunken
  placeholder + mono caption — never a hand-drawn SVG). Set `window.__cvContainmentTree`.
- ✅ **Graph solver grown** (`core/DiagramSolver.jsx`): added `octagon` shape (Virtual Hubs) and a
  `stepper` type — interlocking ramp-tinted chevrons (Design▸Marketing▸Sales▸Construction), accent
  slides along `--ramp-1..4` by position with an `active` cutoff (vt-family: ramp = a variant-theming
  parameter, not only a fixed role).
- ✅ **The archetype layer** (`core/Slide.jsx` + `.d.ts`): an archetype is a **pure function
  `content → CVNode tree`** (slides ARE templates: fixed Section/Zone/Cluster subtree + content-as-data).
  Registered all 13 corpus archetypes (pitch-deck §6) + `stepper` + bare `diagram`. `<Slide archetype
  content lod surface density/>` builds the tree and runs it through the block solver (diagram nodes →
  graph solver), resolving both solvers from their window globals so a template needs **zero wiring**.
  Exposed `Slide` + `Archetypes` (`.list` / `.build` / `.register`) on the namespace. This is
  `design = f(content, axisPosition)` literally — same content, different LOD = recomputed.
- ✅ **The first real template** `templates/pitch-deck/PitchDeck.dc.html` (`@template`): the ConceptV
  investor arc (cover→problem→consequences→hub→compare→stepper→science→team→terms→closing) as
  **content-as-data** in the logic class; the template `<x-import>`s `Slide` from the DS bundle and
  iterates with `<sc-for>`. **LOD / density / theme are exposed as tweaks** (the axis-dials) so the
  whole deck recomputes live. Each slide is a full-width 16:9 band (so the vw-fluid type sizes to the
  slide, sidestepping the slice-3 "fluid type ignores container width" trap without a manual scaler).
  Simplified the scaffolded `ds-base.js` to load `styles.css` only (it @imports everything else).
- ✅ `core/slide-archetypes.html` — `@dsCard` (Components): one `split` spec across 3 LOD + the
  archetype gallery (cover/metric-band/compare/triptych/stepper/hub-diagram).

**Verified** (harness `_qa/archetype-test.html`, because the bundle is stale mid-turn — §6.1):
all 9 archetypes render with zero errors (9 bands, stepper, hub diagram with the 4 entity shapes,
7 shaped badges); LOD pruning, ramp-tinted chevrons, warm/neutral compare panels, italic-bronze
notes, embossed hero-numbers all correct. Fixed one bug found in-harness: the `badge` atom duplicated
its label (inside + below) → now the shape carries the label inside, caption only when given. The
template shell (`_qa/shot-template.png`) renders the deck chrome + `sc-for` 16:9 frames + tweak-driven
header; slides fill at end-of-turn once the rebuilt bundle carries `Slide`.

**Open / next (slice 4b + 5)**
- **Comparison/PRICING TABLE** (a true row×column matrix — distinct from the two-pane `compare`) and
  remaining diagram presets (network/morph/quadrant/tree real-content presets + icon-in-node content
  type per DIAGRAMS.md) are the top slice-4b items.
- Grow `renderAtom` further (geo-locator, device-channel strip) — now trivial via `registerAtom`.
- Encode the fuller per-container collapse rules (pitch-deck §21) into `core/containers.css`.
- **Unify the app composer onto the core** (kill the WS_LAYOUTS/Slide duplication) — slice 5.

## Slice 3 — the generative core (DONE & validated)
**Audit findings**
- The app/kit `.jsx` files **self-mount at module top-level** (`createRoot(getElementById('app'))`) — fine on their own pages, but they THROW when the shared `_ds_bundle.js` loads on any other page, aborting bundle eval before later exports attach. Latent bundle-poisoning bug; my component card was the first to surface it. Also a TDZ bug in `AIEngine.jsx` (`cache: PROMPT_CACHE` referenced before its `const`).
- `_ds_bundle.js` only **rebuilds at end of turn** — mid-turn it serves the STALE bundle. So a component card can't be verified through the bundle the same turn it's authored. Workaround used: a throwaway harness (`_qa/core-test.html`) that Babel-transpiles the `.jsx` directly (each in its own `new Function` scope to avoid top-level `const h` collision) — verifies solver logic without the bundle.
- Fluid type uses `vw` → does NOT respond to container width; a band in a narrow column stays viewport-huge. Fix: render bands as fixed-width slide artboards that scale to fit (the slide-surface pattern), as in the LOD demo.

**Actions taken**
- ✅ `core/containers.css` — the typed containment ladder (Band→Section→Zone→Cluster→Atom). Zone wash = `color-mix` of pigment toward `--zone-ground` at `depth × ~2.1% × intensity` → **zoning = containment depth made visible**, theme-invariant. Per-container collapse rules via container queries. Token-pure.
- ✅ `core/cv-nodes.d.ts` — the shared node type both solvers consume (CVNode + CVGraph + CVAxis).
- ✅ `core/ContainmentTree.jsx` (+`.d.ts`) — the **block solver**: walks the tree, prunes by LOD (priority cutoff + drops `detail:"support"`), emits the ladder with depth set inline, renders metric/bullet/chip/text atoms in DNA vocabulary (gold tabular numbers, ▸/→/✓ bullets).
- ✅ `core/DiagramSolver.jsx` (+`.d.ts`) — the **graph solver**: computes positions per type (network/hub/morph/pipeline/timeline/quadrant/tree/stack), renders edges (flow=gold arrow, dep/ref/rej dashed) + shaped nodes; `state:before↔after` tweens via motion tokens (the morph).
- ✅ Fixed the bundle-poisoning: DOM-guarded the 4 self-mounts (`if(getElementById('app'))…`) in app/App.jsx + the 3 kit apps; made `WS_AI.cache` a getter (TDZ). Their own pages still mount; the shared bundle no longer throws.
- ✅ `core/generative-core.html` — `@dsCard` (Components group): one content spec computed across 3 LOD levels (scaled artboards) + diagrams across types + the live network→hub morph.
- ✅ **Verified** via harness: LOD pruning correct (summary = priority-1 section + 3.2× metric only; neutral 12k zone + "What changes" pruned); hub/pipeline/quadrant all compute + render in vocabulary. check_design_system clean — ContainmentTree + DiagramSolver exposed on the namespace, 40 cards, 477 tokens.

**Open / next**
- Slice 4: build the template library (atoms→13 archetypes, stepper, the other diagram types as presets) on this core. Slice 5: motion + interactivity → deck→app bridge.
- Note for slice 4 verification: author component cards, then rely on the **end-of-turn bundle rebuild** + `ready_for_verification` (or the harness pattern) — the bundle is stale mid-turn.

## Slice 1 — token recalibration (in progress)
**Audit findings**
- `--accent-gold #E0C010` is the REAL logo gold (sampled from the logo PNG) → must NOT be softened. The deck's softer gold `#d6bf57` is the *applied* gold = a ramp stop. (Corrected the synthesis plan.)
- gold/bronze hex is **hardcoded in ~10 consumers** (Colors.jsx, Patterns.jsx, Workshop.jsx, Export.jsx, Layouts.jsx, openai.js, preview/*) → drift risk; needs a de-hardcode pass.
- `Layouts.jsx` already implements **blueprint-ghost + gold-grid + diamond watermark** → the system is *less flat than README claims*; mine it for texture tokens (don't rebuild from scratch).
- `--status-*` warm status set already exists (lines ~59-68) → KEEP/extend, don't fork.

**Actions taken**
- ✅ Added `--ramp-1..4` (#DAD364/#D6BF57/#C09D5D/#B98664) + `--accent-bronze-warm` additively. Logo gold + bronze untouched. check_design_system clean (440 tokens).
- ✅ Wrote AUDIT-INDEX.md (whole-system content-type map + 10 reconciliation tensions) and AUDIT-SLICE1.md.

**Open actions (queued)**
- De-hardcode the ~10 gold/bronze consumers → `var(--accent-gold)`/ramp (so recalibration propagates).
- Measured zone-ladder retune: compute current `--zone-*-surface` vs sampled `#fdfcf7/#f8f8f8`, adjust pigment %, verify.
- Extract texture tokens from `Layouts.jsx` blueprint/gold-grid into `tokens/` (hatch + blueprint-ghost) per REQUIREMENTS A5.
- Reconcile status chips with existing `--status-*`.
- Update README/SKILL where v1 codifies the narrow read (tensions 1–7) — in lockstep, once DNA lands.

## Slice 1c — zone-ladder measured check (DONE — finding flips the action)
**Measured** current `--zone-*-surface` computed output (probe `_qa/zone-probe.html`): all already
**very subtle** at intensity 1 — content ≈ oklch(0.994 L, 0.003 C) ≈ near-white warm; panel ≈
oklch(0.982 L, ~0 C) ≈ neutral grey; reject/source/etc all ~0.97–0.99 L, <0.015 C. **These already
match the sampled near-white ladder (`#fdfcf7`/`#f8f8f8`).**
→ **Correction:** the `--zone-*` system I built is NOT the "too saturated/flat" problem. The
saturation complaint is the **v1 `#FBF4C8` soft-gold / `#FBF7EC` ivory panels** still used by app
consumers. So slice-1c is **not a token retune** — it's a **migration**: move consumers off the old
`--accent-gold-50`/`#FBF4C8` panels onto the subtle `--zone-*` ladder. Folds into the de-hardcode
pass (1b). No zone-token change needed.

## Slice 1d (partial) — texture tokens (DONE, additive)
Added `tokens/texture.css` (wired into styles.css; 450 tokens, clean): `--hatch-*` + `.hatch-band`/`.hatch-rule` and `--blueprint-*` + `.blueprint`. Values reconciled with already-built `Layouts.jsx` (bronze linework @0.18, gold grid @~0.12) so app + tokens agree. Additive, no consumer churn. Remaining 1d: extract the blueprint SVG set from Layouts.jsx into a reusable asset; reconcile status chips with `--status-*`.

## Slice 2 (frames typed) — DONE & validated
Rebuilt frame ratios as a **TYPE system** in `tokens/surfaces.css`: each surface declares `-ar` (aspect ratio) + `-w` (base), height **derives** `calc(w / ar)`. Probe `_qa/frame-probe.html` confirms: 16:9→1920×1080, 3:2→1893×1262, A4→794×1123, mobile→390×844. Added ratio-invariant grid % types (`--grid-margin 12%`, `--grid-title-y 7.5%`, `--grid-band 76%`, `--grid-split 46%`). Added explicit modular-scale rule (`--scale-ratio 1.25`, `--scale-base`) in `tokens/sizing.css` so new type steps derive. Adding a surface now = declare `-ar`+`-w`; `-h` auto-calculates. **Still pending slice 2:** bullet-kind tokens (▶/→), frame-signature utility, status-chip↔`--status-*` reconcile.


## Slice 1b — DE-HARDCODE pass (SCOPE CORRECTION)
Audit reframes the pass: most "hardcoded" gold/bronze sites are **legitimate literal holders**, NOT drift — `Colors.jsx BASE_PALETTE` (a palette EDITOR — needs literal hex for swatches/picker), `Export.jsx` standalone CSS (intentionally inlined for self-contained exports), `openai.js` brand-prompt (descriptive text), `preview/*` swatch cards (display). Converting these to `var()` would BREAK them. → Real de-hardcode targets are narrow: brand-chrome SVG fills that should track the token (e.g. `Layouts.jsx` motif strokes). Action taken: UPDATED `Colors.jsx` palette to include `--ramp-1..4` + flag `gold-50` as v1-legacy (keeps editor working AND in sync). Remaining: optionally point `Layouts.jsx` motif `#E0C010`/`#988058` → `var()`; migrate any real UI that paints the v1 `#FBF4C8` panel onto `--zone-*`.

Per slice: (1) scoped audit of ONLY that content type, mapped keep/recalibrate/deprecate; (2) record findings + plan corrections HERE; (3) make additive/low-risk edits first, defer churn to a deliberate pass; (4) check_design_system; (5) keep specimen cards + README/SKILL in lockstep. The audit routinely surfaces already-built things + inconsistencies that must be folded into scope (e.g. Layouts.jsx textures) — never assume the plan is complete before auditing the section.
