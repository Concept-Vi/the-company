# AREA: History-Deep — census of FINDINGS-LOG (Slices ≤38) + AXES/UNIFICATION/INTEGRATION

> Reader teammate report, glyphic census. Territory: `design/claude-ds/analysis/FINDINGS-LOG.md`
> lines 1183–2592 (Slice 38 down to Slice 1 — the foundry/icon/component/generative-core/AI-union
> eras) read in FULL, plus the icon-foundry genesis (Slices "58/59" era, lines ~660–960, read to
> ground §B/§C — outside the literal line-range but the direct ancestor of everything below it and
> load-bearing for the unification findings) + `AXES.md`, `UNIFICATION.md`, `INTEGRATION.md` in FULL.
> Every claim tagged **Observed** (file:line), **Inferred**, or **Verified** (I ran nothing this
> pass — no code execution occurred; "Verified" below means "the ledger/audit already verified this
> and I cross-read it," never my own execution).

---

## §A — Slice-by-slice / doc-by-doc account (dense, file:line)

### A1. The generative-core genesis (Slices 1–5, FINDINGS-LOG.md:2534–2592)
- **Slice 1** (`FINDINGS-LOG.md:2553`): token recalibration. `--accent-gold #E0C010` = the REAL
  sampled logo gold; the deck's softer `#d6bf57` is an *applied ramp stop*, not the logo colour —
  this distinction (identity-colour vs applied-ramp-colour) is the ancestor of the ordinal-ramp
  question Amendment A4 revisits for glyphic (`#d6bf57→#c09d5d→#b98664`).
- **Slice 2** (2585): frames typed as a system (`-ar`/`-w` declare, `-h` derives) — the FIRST
  instance of the "declare the input, derive the rest" pattern that later becomes CV_AXES'
  `resolveCSS` and, in glyphic, the profile-field pattern R2 just finished generalising.
- **Slice 3** (2534): `core/ContainmentTree.jsx` (block solver) + `core/DiagramSolver.jsx` (graph
  solver) + `core/cv-nodes.d.ts` (shared node type) — THE split that AXES.md later names "BLOCK &
  GRAPH are one generative system... differing only in their layout solver." Glyphgraph (G3-G11)
  is explicitly a THIRD member of this family never named as such anywhere in the glyphic docs —
  see §B1.
- **Slice 4a** (2475): `core/Slide.jsx` — archetype = pure function `content → CVNode tree`;
  `renderAtom` promoted from `if/else` chain to a registry (`ATOM_RENDERERS` + `registerAtom`) —
  this is the exact shape G1's lexicon and G3's relationship-Types later copy (a registry of typed
  things resolved by id, extend-by-registration). The atom registry born here is a direct sibling
  of what cv-edges.js later calls "the ONE home for edge kinds."

### A2. The two-halves duplication and its weld (Slices W1–W7, 2355–2474, cross-read with UNIFICATION.md)
- **The finding** (UNIFICATION.md:10-21): the type system (`CV_REGISTRY`) and the rule engine
  (`core/*` solvers) were built as **two disconnected halves, zero grep references between them**,
  each half describing one part of `design = f(content, axis)`. Slice 4a's `Slide`/`Archetypes` made
  it *worse* — a **third** parallel archetype list (UNIFICATION.md:122: "a fourth parallel strand
  instead of welding the existing three" — counting `surface.deck-slide.*` Types + `WS_LAYOUTS` +
  `Slide`/`Archetypes` as three before the weld).
- **The canonical decision** (UNIFICATION.md:42-61): `CV_REGISTRY` = the type system; core solvers =
  the ONE rule engine; `typeToNode(type,data,axis)` = the bridge (one function); catalogue single-
  sourced via `core/archetype-catalog.js`; `Slide` = the deck-slide case of `RenderType`, not a
  parallel registry.
- **W1** (2445, `core/RenderType.jsx`): the bridge exists — `typeToNode` resolves ANY CV_REGISTRY
  Type into the solver IR. **This is the exact missing piece glyphgraph's G6.1 (`address` resolves
  via `resolve_address`) needs** — glyphgraph nodes are never expressed as CV_REGISTRY Types, so they
  never get a `typeToNode` path; they are rendered by a bespoke `glyphgraph` case in DiagramSolver
  instead of through the bridge. See §B2.
- **W2** (2450, `core/archetype-catalog.js`): ONE archetype catalogue, both halves read it.
- **W3** (2368, 2390): render-through-the-engine reaches slide, block, doc, widget-system previews.
- **W4** (2361): the app finally loads `styles.css` (not just `colors_and_type.css`) — before this,
  the app literally could not see `core/containers.css`'s zone-depth machinery.
- **W5** (2377): the generator loop closes — a Vi-`proposeType`'d Type that extends a known
  archetype previews through the engine automatically.
- **W6** (2281-2301, 2094-2098): editable engine atoms — text/note/metric/hero-number/bullet/chip/
  image-caption leaves become contentEditable when given `onEdit`+a data path. Round-trip proven.
  Remaining: the composer's `def.render` swap (never closed as of this log's end — status unknown to
  me past this file; the glyphic G5 render criteria never reference W6's editable-leaf pattern for
  glyphgraph nodes, which is a live gap — see §B3).
- **W7** (2303-2324): the dataviz atom (`chart` role: spark/bar/gauge) + `delta` on metric — closes
  the live-widget/product-UI rendering gap. `WidgetRender` now renders its body through the engine.
- **LOUD-FAIL as a structural law, stated repeatedly** (2379, 2388, 89): "every fallback removed...
  no silent placeholder renders" — this is the SAME law G3.3/G4.6/G2.5 encode for glyphic
  (collect-then-throw, unknown-value throws). The loud-fail law is NOT glyphic-specific; it is the
  generative-core's founding discipline, inherited wholesale.

### A3. The icon-foundry story — Mark → Glyphic (the direct ancestor of the whole glyphic language)
(Read at FINDINGS-LOG.md:660–960 to ground this — technically above line 1183 but the essential
origin; every glyphic engine file's vocabulary is minted here.)
- **The renaming brief** (946-949, undated slice before "58"): "the icon system is really a
  multi-facet compositional MARK" — Tim/Vi's own framing, later renamed Mark→**Glyphic** (877).
  The motivating audit (950-959) found FOUR pre-existing single-source systems already load-bearing
  before "Glyphic" was even named: `INTEGRATION.md`'s four registries, `AXES.md`'s `f(content,axis)`,
  `CV_SHAPES` (Form facet, `markSVG` composing ring+icon+fill+pattern+ink+shadow — **this is the
  literal ancestor of every glyphic-type.js part**), `CV_ICONS` (~110 glyphs, flat taxonomy).
- **The 8-facet compositional model was built ROW BY ROW, live, in front of Tim** (899-943): ring
  colour vs icon colour split (900-909) → depth as 8th facet (914-923) → fill locking-to-'none'
  cascading through later rows (926-930) → the cumulative 7-row "each row changes ONE axis, the
  ending value LOCKS for every row below" walk (933-943). **This cumulative-lock pattern is the
  direct ancestor of what CRITERIA A3 now calls "a change re-resolves inside its boundary and holds
  outside it"** — the SAME shape (a change at one level propagates forward/inward, not backward/
  outward) was proven correct here for FACET composition before glyphic ever tried to apply it to
  SPATIAL placement. R3's redo should look at this row-lock mechanism as prior art for "propagates
  forward, holds elsewhere," not just cv-address's span algebra.
- **Faceted taxonomy + CV_GLYPHIC born together** (877-897): `CV_ICONS.taxonomy` (13 domains × 4
  kinds) + `cv-glyphics.js → window.CV_GLYPHIC` (8-facet schema, `compose`/`render` delegating
  geometry to `CV_SHAPES.markSVG`, symbols to `CV_ICONS` — "redraws nothing, pure composition
  layer"). This IS the "one mechanism" G0 later formalises for MEANING; CV_GLYPHIC itself does
  geometry composition, never meaning — meaning arrives one step later.
- **★ THE KEY FINDING — CV_MEANING was born EXPLICITLY to solve "nothing has one fixed meaning"**
  (850-874): *"every meaning-binding must be LOADABLE/swappable because meaning is contextual,
  EXCEPT symbols (a house is always a house). Ship a default I author, editable later."* This is
  **Tim's own words from the ORIGINAL build, word-for-word the same law re-stated as Amendment
  correction #2 on 2026-07-03**. `CV_MEANING` was built (853-874) as a registry of named PROFILES
  (register/load/export/resolve/use/list), separating INVARIANT (geometry, symbols) from CONTEXTUAL
  (what colour-value/fill/texture/depth/motion MEAN), round-tripping to JSON, swappable via `use(id)`.
  **This means R1/R2's "meaning is a field, not a fixed literal" is not a new law being retrofitted
  — it is CV_MEANING's day-one founding law, which R2 found VIOLATED at cv-meaning.js:663-691 (the
  REFERENT_KIND/OP consts) because later work (the readGraph/referent system) was added WITHOUT
  routing through the profile the way the original 2026-06-xx design already mandated.** The bug
  R2 fixed is not "the system evolved and needs new laws" — it is "a later addition (referent()) did
  not conform to the architecture's own already-stated law." This sharpens AMENDMENT A1's framing:
  it should cite this origin (850-874) as the LAW's source, not present it as a new 2026-07-03
  correction invented after the fact. See §D1.
- **The AI foundry (glyphic.generate/glyphic.save) — built, then partially abandoned** (740-744,
  834-838): `system/glyphic-foundry.html` — conversational propose→feedback→click→save, routed
  through `CV_AI.execute('glyphic.generate')`, with a graceful DEMO fallback when no model is bound.
  Verified END-TO-END AT THE TIME (743-744): "4 candidates render as live glyphics, Save grew
  library 126→127." **This is a COMPLETE, WORKING, VERIFIED conversational icon-generation UI that
  the current glyphic build (G0-G11) never references, never builds on, and never mentions in
  CRITERIA/GUIDE/SYNTHESIS/ROADMAP.** It solves exactly the "AI can read the language in-context AND
  configure it" requirement G0.4/G8.3 restate from scratch. See §C1 — this is the single biggest
  disconnected-and-abandoned asset in my territory.
- **The three-way icon fork** (Slice 34, 1273-1292; confirmed again Slice 33/35/36/37): `assets/
  icons/cv-icons.js` (`window.CV_ICONS.data`) is the LIVE consumed home; `icon-paths.js`/
  `ConceptVIcon.jsx` is **flagged as drift, never retired** across FOUR separate slices (34: "flagged,
  not yet retired (todo)"; the retirement never appears as DONE anywhere in slices 33-38). This is a
  standing, acknowledged, never-closed fork — see §C2.

### A4. Component-layer, AtomiCity, CV_HOST, CV_AI unification (Slices 6–33)
- **Slices 30-33** (1294-1365): the component layer (`tokens/controls.css` — buttons/cards/fields/
  badges/pills/chips/tags/table, then tabs/segmented/switch/avatar/tooltip, then modal/stepper) built
  bottom-up from source-grounded control vocabulary, NOT invented. Slice 33 (1294) is a rare
  "audited, found NOT drift" result — `.dsa-btn`/`.ws-blk-*` app chrome already shared the same
  token vocabulary as the new `cv-*` primitives; renaming was correctly judged low-value/high-risk
  and NOT done. **Pattern for glyphic: not everything that looks like duplication is drift — audit
  before assuming.**
- **Slices 10-22** (1587-2017): CV_HOST (the Bridge — pluggable runtimes review→fsapi→native,
  `commit()` as the one write call, serializers per change-kind) and CV_MODE (interaction modes as
  a registry — operator/inspect, `interaction = f(mode)`) and CV_PICK (universal element-picker →
  live restyle) — three MORE registries built with the identical register/resolve/query/subscribe
  shape as CV_REGISTRY/CV_AI/CV_AXES/CV_MEANING/CV_SCAN. **By this point in the corpus's history
  there are AT LEAST 7 independently-invented registries sharing one shape** (CV_REGISTRY, CV_AI,
  CV_AXES, CV_MEANING, CV_HOST, CV_MODE, CV_SCAN) — a pattern so consistent it should itself be named
  and enforced as a meta-law (a "registry-shape law": register/resolve/query/subscribe/lineage,
  single-inheritance, loud-fail-on-unknown), not re-derived per subsystem. Glyphic's own registries
  (CV_MEANING, the relationship Types in CV_REGISTRY, CV_AI's glyphic capabilities) already comply;
  this is confirmation, not a new finding — but it means any FUTURE glyphic registry (a `glyphgraph_
  edges/` vocabulary per G6.2, if ever needed) has a very well-worn template to copy.
- **Slice 6-9** (2075-2187): CV_AI unification (5 layers: provider/behaviour/skill/capability/
  context) — the exact registry the glyphic AI face (`ai-glyphic-language.js`, G0.4/G8.3) plugs into.
  **43 capabilities across 14 families** by the end of this arc (2086) — glyphic's own capabilities
  (`glyphic.generate`, `glyphic.save`, and whatever G0.4's AI face registers) are members of this
  SAME catalogue, not a separate one. INTEGRATION.md §6 (read in full) states the AI contract
  identically to how glyphic's G0 states the meaning contract — same shape, same law, same "one
  catalogue of moves."

---

## §B — UNIFICATION findings: parts recorded here now separate from the glyphic language that should fold IN

### B1. Glyphgraph is a THIRD solver the AXES/UNIFICATION model never named — and should
AXES.md:117-127 ("BLOCK & GRAPH are one generative system... two layout solvers... **One type
system, one rule engine, two solvers**") was written and believed TRUE before glyphgraph (G3-G11)
existed. Glyphgraph is now, structurally, a **third solver** — it has its own node type (glyphic
specs, not CVNode atoms), its own edge model (relationship Types via CV_REGISTRY, not the block
solver's containment nesting), and its own layout logic (the G11 placement redo, entirely separate
from `ContainmentTree`'s flow/stacking or `DiagramSolver`'s radial/mesh/pipeline). **UNIFICATION.md
and AXES.md have never been updated to say "three solvers"** — this is a real doc-drift: the
canon that PHASE RECONCILE's own opening line cites ("the pieces below stand on these homes") is
stale about the shape of its own foundation. **Concrete fold-in**: AXES.md §"BLOCK & GRAPH are one
generative system" should become "BLOCK, GRAPH, and GLYPHGRAPH are one generative system, three
solvers" — same typed-nodes/typed-edges/rules-compute-layout frame, glyphgraph's difference being
that its NODES carry full glyphic specs (composed visual units) rather than block atoms, and its
EDGES carry MEANING (a relationship Type with directed/inverse) rather than pure geometry. This is
not cosmetic: R3's placement redo should explicitly ask "does cv-address's relative-span algebra
generalise to ALL THREE solvers, or is it graph-solver-specific?" — UNIFICATION.md's own bridge
pattern (`typeToNode`) argues it should, since a glyphgraph node with an `address` (G6.1) is
supposed to resolve exactly the way any other Type resolves through the SAME bridge.

### B2. Glyphgraph nodes bypass `typeToNode`/`RenderType` entirely — a direct union violation
G6.1 (CRITERIA.md:113, still ☐) wants a glyphgraph node's `address` to resolve via `resolve_address`
to a real Company thing. But UNIFICATION.md's whole point (§2, canonical decision #3) is that THE
bridge for "a registry Type resolving into a renderable node" is `typeToNode(type,data,axis)` — ONE
function, no second bridge. Glyphgraph nodes today (Observed via CRITERIA G5.1: "DiagramSolver
renders each node as a full glyphic via CV_GLYPHIC.render") are rendered by a bespoke `glyphgraph`
case inside `DiagramSolver`, not by `typeToNode`. If a glyphgraph node is ever registered as a
CV_REGISTRY Type (which G3.1's "optional address" field implies it eventually should be, to satisfy
G6.1's "resolves to a real Company thing" — Company things being reached through the ONE registry
per INTEGRATION.md §6), it should render through `typeToNode`→`RenderType`, exactly like a block
or slide Type does, not through a parallel DiagramSolver special-case. **Fold-in**: G6.1's build
should route glyphgraph-node resolution through `typeToNode`, extending it with a `glyphgraph-node`
case (mirroring the existing `graph-bearing→graph solver` case UNIFICATION.md:2447 already
documents for the DIAGRAM solver) — not inventing a fifth path.

### B3. The W6 editable-atom pattern is never referenced by glyphic's own authoring/G8 work
W6 (§A2 above) proved a general mechanism: any leaf tagged with a data path + given `onEdit` becomes
live-editable, round-tripping through a dotted-path setter, with the render staying pure/computed.
Glyphic's G0.2 (`CV_MEANING.author` mutates the active profile) and G8.3 (the still-☐ USER authoring
PANEL) are solving the SAME problem — "let a human edit a live value and see the language update" —
but from scratch, with no reference to W6's already-proven contentEditable+commit-on-blur mechanism
or its `onEdit(path,value)` threading convention. **Fold-in**: when G8.3's user panel is built, it
should reuse the W6 pattern (tag glyphic-authorable fields with a data path, thread `onEdit` from
the panel down through the render, commit via the same dotted-path setter used for block/slide
content) rather than inventing a bespoke form UI. This is a concrete unions-not-bridges opportunity
the ROADMAP's PHASE REMAINING ("G8 self-describing... the USER authoring panel") does not mention.

### B4. CV_SCAN's "used by" graph is the missing mechanism for glyphic's G8.4 ("reach its... authoring affordance through the system")
G8.4 (CRITERIA.md:153, ☐) wants: "from a Glyphic thing you can reach its howto, its page, and its
authoring affordance through the system (not by reading source)." Slice 14 (1784-1813) built exactly
this class of mechanism for TOKENS: `CV_SCAN` walks CSSOM + the manifest + the host tree and answers
"what uses this, from where" continuously and automatically — the Foundations inspector's "Used by N
places" (1864-1866) is the SAME deliverable G8.4 wants, already built, for a different registry.
**Fold-in**: G8's "context attached" mechanism should extend `CV_SCAN`'s extractor registry with a
glyphic-aware extractor (recognising `CV_MEANING.field(...)` calls, `relationship.<kind>` Type
resolutions, `glyphgraph` renders) rather than building a separate discovery mechanism — CV_SCAN
already IS the "reach it through the system" answer for every other registry.

### B5. The row-cumulative-lock pattern (§A3) is unread prior art for R3's "propagates inward, holds outside"
Already covered in §A3 in detail — flagging again here because it belongs in the UNIFICATION
finding set, not just the historical note: R3's relative-placement law ("a change re-resolves
INSIDE its boundary and holds OUTSIDE it") was **proven correct as a compositional law once already**
in the glyphic engine's own ancestor (the 7-row cumulative facet walk, FINDINGS-LOG.md:933-943)
before glyphic existed as a name. It is not a new invention; it is the same shape recurring at a
different axis (facet-composition order vs spatial position). Worth citing in the R3 build notes as
confirming evidence, not just cv-address's span algebra.

---

## §C — Disconnected/unused things this history reveals (built then abandoned — evidence)

### C1. The glyphic-foundry conversational UI (`system/glyphic-foundry.html`) — built, verified, orphaned
**Evidence** (FINDINGS-LOG.md:740-744, 834-838): a COMPLETE conversational propose→feedback→click→
save surface, routing through `CV_AI.execute('glyphic.generate')` with a graceful demo fallback,
verified end-to-end at build time ("4 candidates render as live glyphics, Save grew library
126→127... saved strip updates"). `ai-glyphic.js` registers `glyphic.generate` (threaded multi-step,
parses+validates candidates) and `glyphic.save` (validate→`CV_ICONS.add`). **This file and these two
capabilities are never mentioned anywhere in CRITERIA.md, GUIDE.md, SYNTHESIS.md, ROADMAP.md, or
READING-LEDGER.md** — the entire G0-G11 plan-of-record is silent about it, despite G0.4 and G8.3
independently re-deriving "the AI should be able to configure the language" as if from nothing.
**Status**: Observed as built + verified in the log; **never confirmed still-functional** by anyone
in the current census (not in the ledger's read list, not in ADVISOR-AUDIT's file inventory — worth
checking `system/glyphic-foundry.html` still exists and boots before assuming it's dead weight or
treating it as found money).
**Disposition recommendation**: before building ANY new G8.3 user authoring panel, open
`system/glyphic-foundry.html`, verify it still boots against the current CV_MEANING/CV_GLYPHIC/
CV_AI, and if live, FOLD it forward as the seed of G8.3 rather than building a second authoring
surface. This is a "not-in-use, disconnected, should have been designed-in" find of the exact kind
Tim's brief to this census team named directly.

### C2. icon-paths.js / ConceptVIcon.jsx — a standing, four-times-flagged, never-retired fork
**Evidence**: Slice 34 (FINDINGS-LOG.md:1276-1278) names it explicitly as drift and says "flagged,
not yet retired (todo)"; Slice 34's own open-items list (1290-1292) repeats "retire icon-paths.js/
ConceptVIcon.jsx into the one home"; it is not mentioned as closed in slices 35, 36, 37, or 38 (the
remainder of my territory, all narrower icon-fidelity passes that never touch this). **This is a
named, acknowledged parallel system that has survived at least 4 slices of icon work without
retirement** — a direct instance of "islands join mainland" not yet executed. Not directly glyphic-
engine work (it's the icon RENDERING layer, one level below CV_GLYPHIC's composition layer), but it
sits exactly upstream of every glyphic symbol render (CV_GLYPHIC delegates symbol rendering to
CV_ICONS) — if `icon-paths.js` is ever accidentally consumed by a new component instead of
`cv-icons.js`, it silently reintroduces stale geometry into the glyphic language. **Recommend**: a
one-time grep-and-retire pass, flagged for whoever next touches the icon layer, not glyphic-engine
scope itself but adjacent enough to book here.

### C3. `system-map.json` / the old file-graph system-map — explicitly superseded, left in place, "harmless"
**Evidence** (FINDINGS-LOG.md:671-673): "Dropped the meaningless file-graph + Full/Directory/Roles
modes (Info: discard). system-map.json retained (still powers nothing now; harmless)." A genuinely
dead artifact, explicitly acknowledged as dead, left in the tree. Low-risk (Tim/Info directly signed
off on discarding it), but it is exactly the kind of "nothing is in use" find Tim asked this team to
surface — flagging for cleanup, not urgent.

### C4. AtomiCity's stated destiny to replace Studio — never confirmed done, no mention in glyphic docs
**Evidence** (FINDINGS-LOG.md:1958-1961): "AtomiCity is meant to *eventually replace* Studio —
migration of Studio's generative canvases (Colors/Icons/Voice/Workshop) into AtomiCity surfaces is
the next arc." If Icons (i.e., the icon/glyphic authoring canvas) was ever meant to migrate into
AtomiCity's Vi-driven, learning, conversational shell, that's a THIRD candidate authoring surface for
glyphic (alongside the CV_AI glyphic-foundry of §C1 and the still-unbuilt G8.3 user panel) that no
current glyphic doc references. **Worth a direct check**: has Icons/glyphic migrated into AtomiCity
at any point after this log's end? If yes, G8.3 may already be substantially done under a different
name; if no, it's a second orphaned intention to reconcile before building new authoring UI.

### C5. `describeRelation` (the 2-node inspector read) does not realise inverses — a known, booked gap
Not from my slice range directly but confirmed in READING-LEDGER.md's R1 log (already read in
grounding) — flagging here because it's exactly the kind of "found something pointing at a stale
resource, resolve it into scope" item: `describeRelation` is a SEPARATE read-path from `readGraph`
that was NOT updated when R1 added inverse composition to `readGraph`. It is explicitly "noted, in
scope when the inspector read is next touched" — a deliberately deferred (not forgotten) gap. Since
Tim's directive says nothing waits "for later," this should be pulled into R1's own closure rather
than left as a someday-item — it is the SAME edge law, applied inconsistently across two read-paths
of the same data.

---

## §D — Corrections to anything the plan files/ledger/audit get wrong about this territory

### D1. Amendment A1 (and AMENDMENT framing generally) undersells the referent-words bug as "new" when it is a known-law regression
As detailed in §A3: CV_MEANING's founding brief (FINDINGS-LOG.md:850-874, pre-dating the "Glyphic"
name itself) states, in terms nearly identical to Tim's 2026-07-03 correction #2, that "every
meaning-binding must be LOADABLE/swappable because meaning is contextual... ship a default I author,
editable later." Amendment A1 frames the REFERENT_KIND/OP consts bug as a violation of "the engine's
OWN G0.1 law" (READING-LEDGER.md:143, correctly identified as self-inconsistency) but CRITERIA.md's
prose presents the fix as responding to Tim's *new* 2026-07-03 statement. **The correction**: this is
not new guidance being applied retroactively — it is the ORIGINAL architecture's own stated law,
which a LATER addition (`referent()`/`parse()`, built well after CV_MEANING's founding slice)
violated by not routing through the profile. Worth stating plainly in any write-up to Tim: this
wasn't drift introduced by ambiguity in the brief — it was a later contributor not reading (or not
finding) the original design intent, exactly the "narrow subjective determination replacing what was
already written" root-failure-mode Tim named in correction #8. It is a clean, concrete instance of
the exact failure Tim is worried about across the whole seat — found in the OLDEST part of my
territory, not the newest.

### D2. SYNTHESIS.md 7.2's "KEPT AS MACHINERY" list for the W-loop is accurate against my territory — no correction needed
Cross-checked SYNTHESIS.md:188-189 ("cv-organisms.js port · cv-address.js... · cv-arc.js... ·
cv-nodes.d.ts drift fix") against my read of `core/cv-nodes.d.ts`'s origin (Slice 3, FINDINGS-LOG.md:
2542: "the shared node type both solvers consume") — accurate, no correction. Flagging only that
`cv-nodes.d.ts` has grown fields incrementally across MANY slices in my territory (`focus`, `author`,
`loading`, `mode`, `disclose`, `chart`/`points`/`delta`/`deltaKind` — Slices spanning 2198-2314) with
no single canonical listing of its current full shape anywhere I read. If cv-address/R3 work touches
node typing, a quick "what does cv-nodes.d.ts actually contain today" read is warranted before
extending it further — small risk, cheap to close.

### D3. ROADMAP's PHASE CONVERGENCE (counterpart/design fusion) has an unstated but real precedent for HOW to do such a fusion
ROADMAP.md:41-42 says to identify counterpart/design's unique parts and fuse the best into claude-ds,
"drop the parallel (islands-join-mainland)." My territory contains a WORKED EXAMPLE of exactly this
class of fusion done well: Slice 27 (FINDINGS-LOG.md:1471-1506), the capital-raise corpus fold-in —
audit overlap first (11/12 folders already known, 1 genuinely new), extract the NEW grammar into
named docs, hold ambiguous findings for a second-source confirm before minting a token (the sage-
green accent, held for confirmation at 1489-1490, later confirmed and shipped in Slice 28), and only
THEN build into all four registries in one pass with matching builders (never a metadata-only
archetype). This is not a correction to the roadmap so much as a concrete method to point at: PHASE
CONVERGENCE should follow the Slice 27→28 shape (audit-overlap → extract-grammar → hold-for-confirm
→ build-into-all-four-registries-together), not a file-by-file copy pass.

---

## §E — Direct inputs for PHASE RECONCILE R3 (placement) / R4 (meaning-shape) / the axes story

### For R3 (placement redo, relative laws)
1. **The row-cumulative-lock precedent** (§A3, §B5) — cite as confirming prior art: "propagates
   forward/inward, holds outside" is a law the corpus already validated once, at the facet-
   composition axis, before glyphic ever existed. Strengthens confidence R3's chosen shape is right,
   not merely Tim's stated preference.
2. **Glyphgraph is a third solver** (§B1) — R3 should explicitly decide whether cv-address's
   relative-span algebra is being built as a GRAPH-solver-specific placement system or as a
   candidate THIRD entry in the one-rule-engine model AXES.md describes. If the latter, AXES.md and
   UNIFICATION.md need the "two solvers"→"three solvers" text update (concrete edit block in §F).
3. **`typeToNode` bridge bypass** (§B2) — if glyphgraph nodes ever carry a CV_REGISTRY Type
   (implied by G6.1's `address`), R3's placement work should route new/changed nodes through
   `typeToNode` rather than deepening the DiagramSolver-only special case, or it will need a SECOND
   unwind later exactly like W1-W7 unwound the original two-halves split.
4. DiagramSolver's pre-existing non-glyphgraph layout types (network/hub/morph/pipeline/timeline/
   quadrant/tree/stack, all built Slice 3, FINDINGS-LOG.md:2544) are NOT relative-address-based today
   (they're the original force/computed-position solvers) — R3's relative-address law, if applied
   universally per CRITERIA's phrasing ("the SAME laws govern every relational mutation"), has a
   much bigger blast radius than glyphgraph alone: every pre-existing diagram type would need the
   same redo, or R3 needs to scope itself explicitly to glyphgraph-only placement and say so.
   **This scope question is unresolved in CRITERIA/ROADMAP and should be asked of Tim or decided
   explicitly, not silently assumed either way.**

### For R4 (meaning-shape: 12 minted symbols, ordinal ramp)
1. **The ramp's identity-vs-applied distinction** (§A1, Slice 1) — `--accent-gold` (identity) vs
   `--ramp-1..4` (applied gradient stops) was a real, hard-won distinction from the ORIGINAL token
   recalibration. R4's ordinal-axis fix ("resolved relative to the telling's extent") should keep
   this distinction: the ordinal ramp's *tokens* are applied-gradient stops (correctly, per Amendment
   A4, pointing at `--ramp-*` not a flat accent) but the *meaning* of "ordinal position N" is
   contextual (per CV_MEANING's founding law, §D1) — these are two different single-sources
   (token-graph vs meaning-field) that must stay properly separated per G0.3's "meaning via
   CV_MEANING.field, value via the token graph... ONE mechanism, three single-sources."
2. **CV_MEANING's founding exception for symbols** ("a house is always a house... symbols
   deliberately excluded") is DIRECTLY relevant to R4's 12 minted 'language'-family symbols: if these
   are SYMBOLS (a form/icon identity) rather than FACETS (colour/fill/texture/motion meaning), the
   founding law says their base identity is allowed to be fixed/intrinsic (per `CV_ICONS.facets`,
   "symbol meaning is intrinsic (never profile-governed)" — glyphic-type.js, per READING-LEDGER.md);
   what must NOT be fixed is any INTERPRETIVE gloss/sentence layered on top of that symbol. R4's own
   text already gets this right ("meaning FIELDS (feeling + senses, combinatorial)... glosses stay")
   — flagging as a confirmation, not a correction: the glosses staying is consistent with symbols
   being the one deliberately-intrinsic axis in the whole system.

### For the axes story generally
AXES.md's containment hierarchy (Deck→Band→Section→Zone→Cluster→Atom, AXES.md:42-56) and its
"everything is a typed container at some tree level" capstone (AXES.md:102-115) never once mentions
glyphgraph or glyphics — the entire generative-model document, read in full, is BLOCK-solver-centric
with a late graph-solver unification note. A future revision of AXES.md (not urgent, but real) should
add glyphgraph as explicitly the SAME containment logic applied to MEANING-composed nodes + verb-
typed edges, closing the loop §B1 opens.

---

## §F — PROPOSED PLAN-FILE EDITS (concrete tentative text blocks)

### F1. AXES.md — update "two solvers" to name glyphgraph (addresses §B1)
Proposed insertion after AXES.md:127 ("Build them on the same core; pick the solver by content kind
(`block` vs `graph`). This is the whole system in one line."):

> **A third solver joined later: GLYPHGRAPH.** The glyphic language (build-prep/the-one-system/
> glyphic/) adds a third member to this family — nodes carrying full glyphic specs (composed visual
> units via CV_GLYPHIC, not block atoms) and edges carrying MEANING (a `relationship.<kind>` Type
> with `directed`/`inverse`, not pure geometric connection). Same typed-nodes + typed-edges +
> rules-compute-layout shape; its layout solver is the placement law under redo (CRITERIA Amendment
> A3 / ROADMAP R3). **One type system, one rule engine, THREE solvers.**

### F2. UNIFICATION.md — flag the typeToNode bridge gap for glyphgraph (addresses §B2)
Proposed insertion in "Still open (next)" (after UNIFICATION.md:112, before the closing "Move the
registry ENGINE" bullet):

> - **Glyphgraph nodes bypass the bridge.** `typeToNode`/`RenderType` is the ONE path from a
>   CV_REGISTRY Type to a rendered node (W1's canonical decision). Glyphgraph nodes today render via
>   a bespoke `glyphgraph` case in `DiagramSolver` directly. If/when glyphgraph nodes carry a real
>   registered Type (implied by G6.1's `address` resolving to a Company thing), route them through
>   `typeToNode` with a new `glyphgraph-node` case — mirroring the existing graph-bearing case — not
>   a second parallel bridge.

### F3. ROADMAP.md — cite the glyphic-foundry as a candidate seed for G8.3 (addresses §C1)
Proposed insertion in "PHASE REMAINING," under the G8 bullet (ROADMAP.md:74):

> **Before building the G8.3 user authoring panel, check `system/glyphic-foundry.html` (built +
> verified end-to-end pre-Glyphic-rename: conversational propose→feedback→click→save via
> `CV_AI.execute('glyphic.generate')`/`glyphic.save`, FINDINGS-LOG.md era ~Slice 58-adjacent) — if
> still live, fold it forward as the panel's seed rather than building a second authoring surface.**

### F4. READING-LEDGER.md / SYNTHESIS.md — record CV_MEANING's founding law as the source of Amendment A1 (addresses §D1)
Proposed addition to READING-LEDGER.md, appended under the existing cv-meaning.js entry:

> **CV_MEANING's founding brief** (FINDINGS-LOG.md, pre-"Glyphic"-rename era): Tim/Vi, verbatim-in-
> substance: "every meaning-binding must be LOADABLE/swappable because meaning is contextual, EXCEPT
> symbols... ship a default I author, editable later." This is the ORIGINAL source of the law
> Amendment A1 restates as a 2026-07-03 correction — the REFERENT_KIND/OP bug is a later
> contribution's regression against this founding law, not new guidance. Cite this origin when
> explaining A1/R2 to Tim: it closes a self-inconsistency the system's own first design already
> forbade, which is a sharper and more defensible framing than "Tim corrected us on 07-03."

---

**Summary of scope covered**: FINDINGS-LOG.md:1183–2592 (Slices 38→1) read in full; FINDINGS-LOG.md:
660–960 (icon-foundry genesis, "Slice 58/59" era) read to ground ancestry; AXES.md, UNIFICATION.md,
INTEGRATION.md read in full. No code executed, no files modified outside this census file.
