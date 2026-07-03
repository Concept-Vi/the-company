# AREA CENSUS — canvas engines (`design/claude-ds/core/`) — the UNIFICATION lens

> R3 territory read, 2026-07-03. Every file in `core/` read line-by-line; both assigned verifiers
> RUN. Lens: Tim's hypothesis — "DiagramSolver was before this generative language was made, so the
> best parts of it would be built into the generative language." Evidence marks: **Observed**
> (file:line, read directly) · **Inferred** (labelled, unverified) · **Verified** (executed/run).
> Sources read-only; this file is the only write.

**Verifier ground truth (Verified, run 2026-07-03 from `/home/tim/company/design/claude-ds`):**
`node _demo/verify_g11.js` → **19 passed, 2 failed** — the two failures are exactly the ledger's
claim: (1) `chain(6)` deep-chain vertical compression asserted at verify_g11.js:100 no longer
happens (the W2 fixed 116px row-pitch removed the documented `232/(nR-1)` compression), and
(2) honest-overflow asserted at verify_g11.js:121-122 no longer happens (W2 brick-wrap keeps
over-capacity slots in-frame; `wide[id].x > VB` is never true).
`node _demo/verify_address.js` → **13/13 pass** (span partition · encode/decode round-trip ·
seam · LCA/lcaAll · zones · slot-freeze · doubling · loud-fail).

---

## §A · FILE-BY-FILE ACCOUNT

### DiagramSolver.jsx (524 lines, 38.8K) — THE GRAPH SOLVER
**What it is (Observed):** position computed from RELATIONSHIPS, one `{type, nodes, edges}` spec →
a laid-out diagram in a 320×320 viewbox (`VB=320`, DiagramSolver.jsx:14). One `layout(graph)`
dispatcher (lines 30-141) with per-type solvers; then three render strata (below). Exposed as
`window.__cvDiagramSolver` (line 522).

**The three strata, in build order (the heart of the unification question):**
1. **PRE-LANGUAGE stratum** (Observed — header cites `analysis/AXES.md + DIAGRAMS.md`, the
   design-DNA/unification era, lines 2-8; no CV_MEANING/CV_GLYPHIC anywhere in it):
   - layouts: `hub`(42) · `morph`(48, before=ring/after=hub, the animatable transform) ·
     `network`(53) · `pipeline`(54) · `timeline`(57) · `quadrant`(60, authored x/y 0..1) ·
     `tree`(128) · `stack`(135) · default ring(138). All are **f(live count)** — ring angles
     `i·2π/n`, pipeline spread `i·(VB-80)/(n-1)`.
   - **a parallel edge vocabulary**: `EDGE_CLASS` (line 143) — flow/dependency/reference/rejected/
     communication/bidirectional as CSS classes; kind→marker mapping at line 464; a **hardcoded hex
     fallback `var(--comm-line, #7CA85B)`** at line 516 (token violation, pre-language).
   - **a parallel shape vocabulary**: `SHAPE` clip-paths (144-150) + `POLY` outline points inside
     `shapedNode` (183) — geometry duplicated from what `CV_SHAPES` now owns.
   - **a parallel state-colour table**: `TONE_FILL` (153-158) + `RAMP` (152).
   - the SVG node path (470-497): label-first boxes, icon via raw `window.CV_ICONS.data` (489).
2. **SUB-TYPE VIEW stratum** (capital-raise grammar, slice 28; Observed lines 160-294 + 408-453):
   `stepper`(412) · `orbital`(196) · `stacked`(214) · `spectrum`(236) · `manifold`(258) ·
   `fidelity`(277) — early-return HTML/flex layouts, token-referencing, each with its own inline
   style vocabulary (`SOFT_CARD`, `CAP`, `shapedNode`). Also `edLabel` (16-26), the
   contentEditable commit-on-blur inline-edit mechanism used by every view.
3. **LANGUAGE stratum** (G5, slice 80 + W2; Observed lines 63-127 + 297-401): the `glyphgraph`
   layout case + `glyphGraphView`. This stratum resolves EVERYTHING through the language's single
   sources: nodes render as full glyphics via `CV_GLYPHIC.render` (367), edges via
   `CV_SHAPES.edgeSVG` positioned mode (347), edge kind/line/direction via `CV_EDGES.resolve`
   (322), per-edge colour via `CV_MEANING.field('lineColor', v).token` (328), hover title = a
   2-node `readGraph` clause (338-340), node title = `ME.referent(nd)` (380), label chips (off by
   default) from `ME.field('edge', kind).feeling` (359).

**The W2 frozen-address placement (the code A3/R3 replaces), traced (Observed 63-127):**
- rank = longest path from any source, computed only to seed NEW nodes (77-91).
- constants: `LAY_SIZE=58` (92) · `LAY_PITCH=58·1.55=89.9` (93) · `LAY_MARGIN=44` (94) ·
  `LAY_ROW_PITCH=116` (95, "CONSTANT ((VB−2·44)/2; rows run off honestly)") · `PER_LINE=3` (117) ·
  `SUB_PITCH=40` (118).
- `nd._slot = {row, slot}` assigned ONCE, **never recomputed** (100-104) — "FROZEN — the graph
  carries its addresses (one IR)".
- pixel projection: `x = 44 + col·89.9 + (line%2)·44.95`, `y = rowY + line·40` with brick-wrap
  `col = slot % 3` (117-122).
- authored `nd.x/nd.y` (0..1) is priority 1: `x = 30 + nd.x·(VB−60)` (108-109) — note **margin 30
  for authored vs 44 for slots**, two framings in one canvas.
- `nd._pos` written back (124) — the one-home the generator reads.
- **Line 74's comment claims "(The address IS the CV_ADDRESS shape — row/slot as a frozen path)" but
  the code NEVER calls CV_ADDRESS** (Verified by grep: the only CV_ADDRESS match in this file is
  that comment). The W2 edit reimplemented the idea inline with pixel constants — the absolute rule.
- node render size is separately `f(count)`: `n>6?44:n>4?50:58` (313) — layout is count-independent
  but RENDER size is not (deliberate, asserted by g11's "no 4/6-node reflow" tests).

**Loud-fail state (Observed):** glyphGraphView throws if CV_GLYPHIC/CV_SHAPES absent (309).
Three catch-paths: edge-title catch WARNS then blanks (342-345, deliberate + logged); node-referent
catch at 380 returns `""` **silently** (a pre-existing loud-fail violation, also flagged by the
advisor audit); label-chip catch at 359 falls back to the RAW KIND ID **silently** — directly
contradicting the same function's comment "never the raw kind id" (354-355). Both belong on R3's
sweep list.

**Consumed by (Verified by grep):** `system/glyphgraph-generator.html` (the live canvas),
`system/language.html` (the G5 page), `system/the-whole-thing.html` (5 live glyphgraphs),
`core/ContainmentTree.jsx` (kind:"diagram" → line 419-422), `core/RenderType.jsx`,
`app/canvases/workshop/WidgetBuilder.jsx:193-196`, `core/generative-core.html`, `_demo/verify_g11.js`
(source-slices `layout()` out of the file text — so **any refactor that renames
`function layout(graph) {` or moves `return pos;` breaks the harness loader** (verify_g11.js:22-27)).

### ContainmentTree.jsx (447 lines, 28K) — THE BLOCK SOLVER
**What it is (Observed):** the containment ladder — Band→Section→Zone→Cluster→Atom
(renderNode, 362-428). Position from NESTING + flow (CSS), never x/y. Zone wash computed from
nesting depth (`--zone-depth` passed down, 400). LOD prunes by priority/support before layout
(20-31). Atom rendering is a REGISTRY (`ATOM_RENDERERS`, 111-318; extend via
`ContainmentTree.registerAtom`, 443) — 16 roles: metric · chart · hero-number · bullet · chip ·
badge · note · qr · logo · ramp-card · image · icon · text · headline (+role inference, 320-325).
Mechanisms: motion/entrance wave (59-65), TimePlayer space↔time (70-84), Disclose progressive
disclosure (88-94), focus/dim-the-rest (335-344), loading skeletons (348-359), inline-edit `edit()`
(95-107). Delegates `kind:"diagram"` to DiagramSolver (419-422). Exposed as
`window.__cvContainmentTree` (446).
**Duplication note (Observed 38-47):** `SHAPE_CLIP` is a **byte-identical fallback copy** of
`CV_SHAPES.clip()` for the compiled bundle, marked "keep in sync" — an acknowledged second home
(drift risk of the exact class the system exists to prevent; disposition belongs to the fold-in §B).
**Consumed by:** RenderType, WidgetBuilder, generative-core.html, templates (via the bundle).

### RenderType.jsx (212 lines) — THE BRIDGE (UNIFICATION W1)
**Observed:** resolves a CV_REGISTRY Type + data → solver IR (`typeToNode`, 104-133): deck-slide
surface → archetype builder (110-114, throws if `window.__cvArchetypes` missing); doc → slide
sequence (116-122); graph-bearing → diagram node (124); widget → zone tile (128-130,
`widgetToNode` 136-155); block/atom → `blockToNode` (32-100, the whole WS_BLOCKS taxonomy
re-expressed in core vocabulary — including `process/funnel/timeline/tagCluster/orgDiagram` cases
that mint pre-language graphs with `kind:"flow"` edges, 88-92). `REGISTER` meta-dial
(presenter/reader → lod+density+motion, 23-26). LOUD on missing engine (170) and unknown type
(174). `CoreTypes` (199-208) reads the single-source catalogue, throws if absent (193-195).
Exposed as `window.__cvRenderType` / `window.__cvTypeToNode` (210).

### Slide.jsx (320 lines) — THE ARCHETYPE LAYER
**Observed:** archetype = pure function content → CVNode tree (ARCHETYPES, 44-287): the 13 corpus
archetypes + stepper/diagram/section + the 12 capital-raise archetypes; aliases title/content
(290-291). `buildSlide` throws on unknown archetype (295-299). `Archetypes.register` = the
extend-by-registration door (305). `Slide` renders through RenderType, throws if the bridge is
absent (313-314). Exposed as `window.__cvSlide` / `window.__cvArchetypes` (318).

### archetype-catalog.js (100 lines) — THE SINGLE-SOURCE CATALOGUE (W2 weld)
**Observed:** META (27 archetypes, 16-45) + SAMPLES (defaults, 49-77) → registry-shaped seeds
`surface.deck-slide.<key>` (79-93); `window.CV_ARCHETYPE_CATALOG`/`CV_ARCHETYPE_META` (95-98) +
CommonJS export. **Consumed by (Verified by grep):** `app/registry/types-seed.js:216,259,343-347`
(seeds CV_REGISTRY from it), `core/RenderType.jsx` (CoreTypes), `core/slide-archetypes.html:110`,
`system/system-map.html:242`. The weld holds — one catalogue, no parallel list found.

### cv-address.js (92 lines) — THE ADDRESS ALGEBRA (the W1 port)
**Observed:** `window.CV_ADDRESS` = `span(k,n,parent)` (children PARTITION a parent's [0,1);
25-30) · `encode(path)`/`decode(start,radices)` mixed-radix (33-52) · `lca`/`lcaAll` (56-69 — "the
boundary that must HOLD through a change is the lowest common ancestor of the changers' addresses —
derived, never chosen") · `zones(parts,axisPx)` (74-78) · `slotFor(index,capacity)` (83-88 —
k-th INSERTION gets a FROZEN span; capacity doubles, existing slots never move). Loud-fail
throughout. Ported-by-COPY from `counterpart/design@212ba23 engine/prove/resolve.mjs` (proven
11/11 against measured pixels) + `dna/address.json`, generalized + given the LCA (header 9-17).
**Verified 13/13** (`_demo/verify_address.js`, run this pass).
**THE STRUCTURAL FACT (Verified by grep):** consumed by **nothing but its own verifier**. No
production file calls CV_ADDRESS — DiagramSolver's only reference is the line-74 comment.
**The law split inside this one file (Observed, decisive for R3):** the file's own header states
the relative law — *"addresses are DERIVED from counts, never assigned (insert a sibling and every
address re-derives — an address is a view, never a stored fact that can stale)"* (5-7) — which IS
Tim's A3 correction. Then lines 15-17 + `slotFor` bolt the OPPOSITE onto it: *"a node's slot = its
span in its frame, FROZEN at insertion (stable-slot)"*. **span/encode/decode/lca/zones = the
relative algebra A3 needs; slotFor = the freeze primitive of the era A3 overturns.**

### cv-arc.js (54 lines) — THE ARC RESOLVER (the W1 port)
**Observed:** `CV_ARC.plan(arcName, n, {roles, arcs})` — expand an arc's elastic runs to n beats,
archetype affinity + dial envelope per beat, deterministic, loud-fail. Data-injected (seed:
`assets/icons/glyph-arc-seed.json`, exists — Verified). Ported from counterpart's
resolve-sequence.mjs (7/7). Purpose per header 15-18: give a conversation-grown graph its telling
SHAPE (open→argue→show→prove). **Verified 7/7 previously (ledger); consumed by nothing but
`_demo/verify_arc.js`** (Verified by grep). Disposition per A4: keep as machinery; it is the
natural supplier of the ORDINAL/telling-order dimension the `_field` halo already paints.

### cv-nodes.d.ts (118 lines) — THE SHARED IR TYPES
**Observed:** CVAxis (lod/surface/density), CVNode (kinds band/section/zone/cluster/atom/diagram +
all atom fields), CVGraphType incl. `"glyphgraph"` (73, "W0 drift-fix — the solver already handles
it"), CVGraphNode (authored x/y documented as "quadrant placement" only, 83-85 — stale: glyphgraph
authored-override also uses them), CVGraphEdge with the glyphgraph facets (line/direction/routing/
lineColor, 95-103 — lineColor "resolved to a token — never hex"). **Drift (Observed):**
`"compare"` is declared in CVGraphType (72) but `layout()` has NO compare case — it falls to the
default ring silently. `line` union (97) conflates MOOD values (solid/dashed/dotted/lines) with
ROUTING values (right-angled/curved/free) that the engine treats as a separate `routing` facet.

### containers.css (198 lines) — THE CONTAINMENT LADDER, CSS LAYER
**Observed:** band/section/zone/cluster/atom classes; zone wash = `calc(var(--zone-depth) · 2.1%)`
pigment mix (77-92) — structure read by undertone; cluster flows col/row/grid/split/overlay/wall
(124-146); collapse rules per container query (157-166); the paged-surface stage
`.cv-slide-frame`/`.cv-slide-stage` (179-198). Token-pure. Consumed by both solvers' emitted
markup + the deck templates (Verified: `templates/capital-raise/CapitalRaise.dc.html`,
`templates/pitch-deck/PitchDeck.dc.html`, `system/system-map.html`).

### slide-fit.js (107 lines) — THE PAGED-SURFACE FITTER
**Observed:** `CV_SLIDE_FIT` v3 — scales `.cv-slide-stage` (design width 1280) into
`.cv-slide-frame` so nothing clips; version-aware install (27); ResizeObserver + MutationObserver +
a settle heartbeat for async `<x-import>` mounts (83-93). Consumed by the deck templates +
system-map (Verified by grep). Connected, working machinery; not R3-relevant beyond "don't break".

### generative-core.html · slide-archetypes.html — THE SPEC/DEMO CARDS
**Observed:** `@dsCard` gallery pages proving the engine: one spec across 3 LODs; hub/pipeline/
quadrant; the network→hub morph (generative-core.html:116-131); the 25-archetype gallery pulling
defaults from the single-source catalogue (slide-archetypes.html:106-118). Both load React from
unpkg CDN (dev-pinned, integrity-hashed). These are the FORM face of the pre-language engine —
they contain no glyphgraph specimen (Observed): **the language render has no card in core/'s own
demo pages** (it lives in system/language.html) — a gallery-visibility gap worth noting against
"gallery is the visible surface".

### The four .d.ts stubs (DiagramSolver/ContainmentTree/RenderType/Slide .d.ts)
**Observed:** accurate for the pre-language surface. Drift: `DiagramSolver.d.ts` type list omits
glyphgraph + the sub-type views and documents an `axis` prop the component never reads
(DiagramSolver.jsx:404 destructures only `{graph, onEdit}`); `Slide.d.ts` ArchetypeName lists 15
of the 27 catalogue keys.

---

## §B · UNIFICATION FINDINGS — Tim's hypothesis, verdict + the fold-in design

### Verdict on the hypothesis: CORRECT, with a precision
**DiagramSolver predates the language** — Observed on internal evidence (git history is squashed at
the 2026-07-02 "baseline" commit in the nested repo and 2026-07-01 in ~/company, so dating is
internal): the base strata cite AXES/DIAGRAMS (the design-DNA era), carry their own edge vocabulary
(EDGE_CLASS), shape geometry (SHAPE/POLY), state colours (TONE_FILL), and a hardcoded hex — all
things the language now owns as CV_EDGES/CV_SHAPES/CV_MEANING fields. The precision: the language
was **already built INTO it once** — the G5 glyphgraph stratum (slice 80) resolves every visual
fact through the language's single sources. So the fold-in is not "start"; it is **finish**: one
stratum of the file already lives under the language's law, two don't, and the placement law is
wrong in all three.

### The GOOD parts (what the language should absorb — each with its door)
1. **Relations-drive-position** (the file's founding idea, line 3-5: "position is COMPUTED FROM
   RELATIONSHIPS… not from nesting"). The hub/pipeline/tree/stack/timeline layouts are really
   RELATIONSHIP READINGS — hub = one-to-many from a centre; pipeline = a chain of `flows-to`;
   tree = `contains`. Under R3 these become *named projections of relational structure into span
   partitions* (see §E) rather than separate pixel formulas. Door: the layout case becomes data
   (a projection registry), not a switch branch — the same move ATOM_RENDERERS already made.
2. **The morph** (48-51 + generative-core.html:116-131): the same node-set under two relation
   structures, positions tweened by motion tokens — "nothing teleports". This is the ANCESTOR of
   A3's movement law (bounded, angled, animated). Door: R3's address-diff motion generalises it —
   morph becomes "re-resolve under the new relation structure inside the changed boundary".
3. **The growth animator** (379-382 + tokens/diagram.css): stable React keys + CSS transitions on
   left/top = a style change GLIDES, a new key ENTERS. Already the LCA-anchor law "satisfied
   structurally at this scale" (comment 376-378). KEEP as-is; R3's bounded movement rides it.
4. **`_pos` write-back, one home** (124-125): surfaces read the computed place, never re-derive.
   KEEP; under R3 write back the resolved address AND the projected position.
5. **`edLabel`/`edit()` inline editing** (16-26; ContainmentTree 95-107): the same
   commit-on-blur pattern in both solvers — already unified in shape, duplicated in code. Candidate
   one-home later; not R3.
6. **The sub-type views as archetypes**: orbital/stacked/spectrum/manifold/fidelity are corpus-
   evidenced compositions. They stay; their inline shape/colour vocabularies should resolve through
   CV_SHAPES/tokens over time (the `shapedNode` POLY table duplicates CV_SHAPES geometry —
   Observed 183 vs the CV_SHAPES canonical).
7. **ContainmentTree's whole mechanism inventory** — LOD-prune, zone-depth wash, focus,
   space↔time, disclosure, skeletons, atom registry — is the mature statement of "property derived
   from position-in-structure". The language's render already composes WITH it (a glyphgraph is a
   `kind:"diagram"` node inside the ladder). No fold needed; the law unifies (see §B-d below).

### The PARALLEL parts (unions-not-bridges — retire into the language's homes)
- **EDGE_CLASS + the legacy `kind:"flow"|"dependency"...` vocabulary** (143, 460-468): a second
  edge home predating CV_EDGES/CV_MEANING. It is live — RenderType's blockToNode mints
  `kind:"flow"` edges (RenderType.jsx:39,88-92) and every archetype deck uses them. Disposition
  (Inferred design, not yet built): these six kinds become meaning fields + relationship Types with
  inverses through the R1 doors (flow → flows-to/flows-from; dependency → depends-on/depended-by —
  note the Company's relation_types already carry this shape), and the legacy render path resolves
  its class/marker FROM the field (kind → CV_MEANING edge field → line/colour/marker), with the
  CSS classes kept as the projection. The A2 law then covers the WHOLE solver, not just glyphgraphs.
- **SHAPE/POLY/TONE_FILL** (144-158, 183): resolve through CV_SHAPES (geometry) + the token/value
  system (fills). ContainmentTree's SHAPE_CLIP fallback copy (38-47) rides the same disposition —
  the bundle-fallback rationale is real, but the copy should be generated, not hand-synced.
- **`var(--comm-line, #7CA85B)`** (516): the one raw hex in the territory. Flag: hardcoding;
  replace with the token (the sage `--comm-*` voice exists in tokens per slide-archetypes.html:42).

### (d) Two solvers, one law? — YES, and A3 IS the law
ContainmentTree: position from NESTING (a child renders inside its parent's box; CSS flow resolves
the span). DiagramSolver: position from RELATION (computed x/y in a viewbox). **cv-address states
the single law both are instances of: children PARTITION a parent's span; an address is derived,
never stored** (cv-address.js:3-7). The block solver already obeys it (a zone's box IS its span in
its parent; the depth wash is a property derived from the address). The graph solver's W2 state
violates it (frozen slots + pixel constants = addresses stored, not derived). R3 (§E) makes the
graph solver obey the same law by making rank-rows and row-slots FRAMES and SPANS — after which
"one type system, one rule engine, two solvers" (cv-nodes.d.ts:3-7) becomes "…two PROJECTIONS of
one placement law": nesting resolves spans via CSS; relations resolve spans via the address algebra.
The LCA anchor law (cv-address.js:54-69) is the shared motion face for both.

---

## §C · DISCONNECTED / UNUSED (evidence per item)

1. **cv-address.js — zero production consumers** (Verified: grep for `CV_ADDRESS|slotFor` across
   the repo hits only cv-address.js, _demo/verify_address.js, and the DiagramSolver line-74
   COMMENT). The W2 edit name-checked the algebra and reimplemented a frozen version inline. R3
   connects it (§E) — the disposition A4 anticipated ("the address algebra's span math serves A3
   directly").
2. **cv-arc.js — zero production consumers** (Verified: grep for `CV_ARC` hits only cv-arc.js +
   _demo/verify_arc.js). Its seed (`assets/icons/glyph-arc-seed.json`) and its natural consumer
   surface (the ordinal `_field` halo by telling-order, glyphgraph-generator.html:659-665) both
   exist; the wire between them is unbuilt.
3. **`"compare"` CVGraphType** (cv-nodes.d.ts:72) — declared, no layout case; falls to the default
   ring silently (DiagramSolver.jsx:138). Either implement or remove from the union; the silent
   fall-through is a soft-fail.
4. **`axis` prop on DiagramSolver** — declared (DiagramSolver.d.ts) and passed by ContainmentTree
   (421), never read (DiagramSolver.jsx:404). Inert.
5. **Slide.d.ts ArchetypeName** — 15 of 27 keys; the capital-raise set and `section` are missing
   from the type though live in ARCHETYPES. Stale stub.
6. **kinds-type.js layout enum** `[force,tree,radial,flow,grid]` vs the solver's real set —
   declaration/implementation drift (already ledgered; confirmed against the real switch).
7. NOT unused (checked): archetype-catalog (4 consumers), slide-fit + containers stage classes
   (2 templates + system-map), all of ContainmentTree's mechanisms (reached via RenderType/
   WidgetBuilder/templates).

---

## §D · CORRECTIONS to plan/ledger/audit claims about core/

1. **A3/R3's "cv-address slotFor pixel projection" phrasing overstates cv-address's role in the
   breakage.** The absolute-freeze is implemented ENTIRELY inside DiagramSolver.jsx:92-122;
   `slotFor` is called by nothing (Verified). What A3 should say: the freeze PRIMITIVE (`slotFor`,
   cv-address.js:80-88) encodes the overturned stable-slot law and is redesigned/removed; the REST
   of cv-address (span/encode/decode/lca/zones) is the algebra the redo builds ON. (SYNTHESIS 7.2's
   "span algebra — serves A3 directly" is exactly right; extend it with the slotFor caveat.)
2. **The stable-slot era record is NOT in FINDINGS-LOG slices ≤78.** ADVISOR-AUDIT §6.1 sends the
   reader to "slices ≤78" for the stable-slot 21/21 era, the force-directed rejection, and the
   left-vs-centred call. Verified by grep: FINDINGS-LOG.md contains NO occurrence of stable-slot/
   force-directed/G11/left-anchor (its numbered slices jump 59→66, the System-Map era). The
   placement history actually lives in **SYNTHESIS.md Round 6 (lines 133-166)** — complete there:
   the measured 276→160 jump, the force-directed rejection by measurement, the stable-slot design,
   both honest boundaries, AND the stable CENTRED alternative formula
   (`x = cx + (ci − (CAP−1)/2)·LAY_PITCH`). The G11 build itself violated the folder's own
   append-a-slice law (as R1/R2 later did — audit §4). Correction for the audit/plan: R3's
   required pre-read for placement history = SYNTHESIS Round 6 + verify_g11.js's own header, not
   the FINDINGS-LOG.
3. **verify_g11's 2 failures — confirmed by run and now explained at code level** (see header of
   this file). The ledger's "behaviour arguably changed for the better in isolation" is fair on
   (b) brick-wrap-vs-off-edge, but note the W2 row-pitch change also silently REMOVED a
   count-relative behaviour (y = 232/(nR−1) — rows fitting the extent) and replaced it with a
   constant. Under A3 the count-relative y was actually the MORE law-conformant half (a rank-row
   IS a span of the vertical extent) — the W2 edit "fixed" the wrong direction. Neither old nor
   new y-law survives R3 unchanged; both are inputs to §E.
4. **ADVISOR-AUDIT §4's citation "DiagramSolver.jsx:318 (every glyphgraph edge)"** — now line 322
   (post-R2 line drift); the claim itself (EDGES.resolve on every edge; no kind-less callers)
   re-verified true against the current file, and the-whole-thing/language/face-index kinds all
   resolve post-R1 (face/projection-of/part-of/mirrors are meaning-kinds in the union).
5. **The silent-fallback inventory for this file is one bigger than audited:** the audit flagged
   the referent-title catch (380); the label-chip catch (359, raw-kind fallback contradicting its
   own comment) is a second, unrecorded soft-fail. Both belong on the R3 sweep.
6. **G3.1's "existing DiagramSolver consumers still work unchanged"** — the preserve set asserted
   by verify_g11 (hub centre, network ring, quadrant authored x/y) passes today (Verified in the
   19/21 run: all three preserve tests green). The two reds are W2-vs-contract only.

---

## §E · THE R3 DESIGN INPUT — relative placement on the cv-address algebra

### The shape (each element traced to Tim's law + the existing code)
**Position = a relative address, derived; the viewbox is only a projection.** (GUIDE "THE CORRECTED
LAWS": "the address IS the position".)

1. **Frames.** The graph's placement structure is a TREE of frames: the canvas root [0,1)² → one
   frame per rank-row (the vertical dimension partitioned by the rank structure) → within each row,
   one span per member (the horizontal dimension partitioned by membership). Both partitions are
   `CV_ADDRESS.span(k, n, parent)` — derived from the CURRENT structure every resolve, exactly the
   algebra's stated law ("an address is a view, never a stored fact that can stale",
   cv-address.js:6-7). `nd._slot` (the stored fact) is deleted; what may be cached is the node's
   PATH `[[rowK, nRows], [memberK, nInRow]]`, and even that re-derives on mutation.
2. **Mutation = re-partition ONE parent span; the boundary is the LCA.** Add/remove/reorder/
   retarget/containment-change all reduce to: some node's path changes → `lcaAll` of the changed
   paths names the ONE frame whose children re-partition (cv-address.js:65-69 — the anchor law is
   already implemented). Inside that frame, siblings re-resolve (shift proportionally: child k of
   n → k of n+1); outside it, paths are untouched so positions are IDENTICAL by construction —
   Tim's "a change re-resolves INSIDE its boundary and holds OUTSIDE it" falls out of the algebra
   rather than being enforced by freezing.
3. **Order-changes are the SAME operation** (A3's explicit demand): before→after on a relation =
   memberK changes within the same row-frame = the same re-partition. No special case.
4. **Movement is bounded, angled, animated.** The change budget is structural: a re-partition of
   one frame moves a sibling by at most its parent-span/n-ish delta (proportional shift), never
   across the boundary. The motion face is the EXISTING growth animator (stable keys + token
   transitions, DiagramSolver.jsx:376-382) — the address diff GLIDES. "Some things must move;
   that's the point — it's generative."
5. **Authored x/y (drag) stays the per-node override** (A3 verbatim) — priority 1, exactly as
   today (108-109); the generator's drag path (glyphgraph-generator.html:277-285) is untouched.
   ONE improvement: single-source the frame constants (the generator hand-copies VB/MARG/SPAN with
   a "must match" comment at line 245 and duplicates the render-size formula at 246 — export the
   projection from the solver/CV_ADDRESS instead of copying).
6. **Left-vs-centred dissolves structurally, but still goes to Tim's eye.** Under span partition,
   member k of n centres at `(k−0.5)/n` of the row — rows are self-centring and the left-hug
   disappears. This is mathematically the Round 6 "stable centred alternative" with n live instead
   of CAP frozen — i.e. the taste call's second option, now law-derived. Per A3 the call STILL
   goes in front of Tim in the live render (present both; recommend centred-by-derivation).
7. **What replaces the freeze's virtue (no-jump) honestly:** stability was the frozen law's
   selling point; the relative law replaces "nothing ever moves" with "movement is scoped +
   proportional + animated". The old verify_g11 strict-equality oracle is therefore REWRITTEN, not
   patched (the byte-identity assertions are assertions OF the overturned law).
8. **Sizing joins the same law (Inferred, propose):** node render size currently = f(global count)
   (313). Under spans, size can derive from the node's span width (min(span·VB·factor, 58)) — the
   4/6 thresholds dissolve into the same relative law. Optional within R3; flag, don't smuggle.

### What R3 KEEPS (enumerate-what-each-change-preserves, standing rule)
The sibling layouts (hub/morph/network/pipeline/timeline/quadrant/tree/stack) unchanged this pass ·
authored x/y priority + drag · `_pos` write-back · the growth animator + gg-node handles · the
`_field` ordinal halo (368-374) · glyphGraphView's render path (edges/titles/chips) untouched ·
the generator's selection/rubber-band/dblclick paths.

### What R3 REPLACES / REMOVES
DiagramSolver.jsx:76-126 (the frozen-slot block: rank-only-for-new, `nd._slot`, the six pixel
constants, brick-wrap) → the frame/span resolver · cv-address.js `slotFor` (the freeze primitive)
→ removed or redesigned as `pathFor(structure, node)` (derive, don't freeze) · verify_g11.js →
rewritten (below). Sweep en route: the two silent catches (359, 380) go loud-with-notice; the
line-74 comment finally becomes true.

### What the rewritten verify_g11 asserts (THE LAWS, falsify-first against the current code)
1. **Scoped movement:** add a sibling in row r → ONLY row-r members' x change, each by the
   proportional re-partition delta (assert the exact new spans).
2. **Outside-boundary stillness:** all nodes whose path does not pass through the mutated frame
   are byte-identical (the LCA law) — across addition, removal, reorder, retarget.
3. **Order-change = same law:** swap two members' order → same-frame proportional shift, nothing
   outside moves (this is the assertion the old harness could not express).
4. **Bounded budget:** max displacement under any single mutation ≤ the mutated parent's span
   (no global reflow ever).
5. **Derived-never-stored:** two layouts of the same structure from scratch are identical
   (no hidden per-node state); a mutated-then-restored structure returns to the original
   positions (addresses are views).
6. **Authored x/y wins and is mutation-stable** (kept from today's harness).
7. **Siblings preserved** (hub/network/quadrant — kept).
8. **In-frame honesty:** all resolved positions lie inside the root frame by construction (spans
   partition [0,1)) — replacing both the off-edge-overflow AND brick-wrap eras; assert no overlap
   within a row down to the declared min-span boundary, and name the boundary where n is large
   enough that spans < node size (the honest limit, asserted not hidden).
9. **Loud-fail:** malformed graph/path input throws (inherit cv-address's fail()).
Note for the rewriter: the harness loads `layout()` by source-slicing on the literal strings
`'function layout(graph) {'` and `'return pos;'` (verify_g11.js:22-27) — keep the loader in step
with any signature change, or the harness lies by failing to load.

---

## §F · PROPOSED PLAN-FILE EDITS (tentative text blocks — for the seat/lead to fold in)

**F1 · CRITERIA.md, AMENDMENT A3 — replace the parenthetical naming cv-address:**
> current: "(DiagramSolver W2 edit + cv-address slotFor pixel projection) is redesigned to this"
> proposed: "(the DiagramSolver W2 edit — the freeze is implemented wholly inline at
> DiagramSolver.jsx:76-126; cv-address is consumed by NOTHING today, its line-74 mention is a
> comment) is redesigned to this. cv-address's span/encode/lca/zones ARE the A3 algebra (its own
> header states the derive-never-store law); its `slotFor` freeze primitive encodes the overturned
> stable-slot law and is removed/re-derived with the redo."

**F2 · ROADMAP.md, R3 bullet — append:**
> "Placement history pre-read = SYNTHESIS Round 6 (NOT FINDINGS-LOG ≤78 — verified: the G11 era
> was never sliced into the log; Round 6 holds the measured jump, the force-directed rejection by
> measurement, both honest boundaries, and the stable centred formula). Under span partition the
> centred option becomes the law-derived default ((k−0.5)/n of the row) — present left vs centred
> to Tim's eye in the live render with that noted. R3 sweep: the two silent catches
> (DiagramSolver.jsx:359 raw-kind label fallback, :380 blank referent title) go loud-with-notice;
> single-source the generator's copied frame constants (glyphgraph-generator.html:245-246)."

**F3 · ROADMAP.md, PHASE REMAINING — add one line (the solver-wide edge-law tail):**
> "The legacy diagram edge vocabulary (EDGE_CLASS flow/dependency/reference/rejected/communication/
> bidirectional + RenderType's minted kind:'flow') is the pre-language second edge home still live
> in every archetype deck — disposition through the R1 doors (verb-pairs w/ inverses; render
> class/marker resolved FROM the meaning field), so the edge law covers the whole solver, not only
> glyphgraphs. Also: the one raw hex `--comm-line,#7CA85B` fallback (DiagramSolver.jsx:516) → token."

**F4 · READING-LEDGER.md — new entry (this census):**
> "core/ READ IN FULL (all 17 files) + verify_g11 (19/21, failures explained at code level) +
> verify_address (13/13) re-run. Structural facts: CV_ADDRESS + CV_ARC consumed by nothing but
> their verifiers; the W2 freeze never calls the algebra it name-checks; the stable-slot era record
> lives in SYNTHESIS Round 6, not FINDINGS-LOG; 'compare' graph-type declared-not-implemented;
> DiagramSolver axis prop inert; Slide.d.ts/DiagramSolver.d.ts stale vs the live sets; a second
> unrecorded silent catch at DiagramSolver.jsx:359. Census: census/AREA-canvas-engines.md."

**F5 · SYNTHESIS.md — Round 7 convergence-facts, append:**
> "Tim's DiagramSolver hypothesis verified with a precision: the solver predates the language
> (EDGE_CLASS/SHAPE/TONE_FILL parallel homes, AXES-era header) AND the language was already welded
> into it once (the G5 stratum resolves everything through CV_GLYPHIC/CV_SHAPES/CV_MEANING/
> CV_EDGES). The fold-in is a finish, not a start: R3 puts the placement law under the language
> (spans), the edge-law tail puts the legacy vocabulary through the R1 doors, and the two solvers
> become two projections of ONE placement law (nesting=CSS-resolved spans; relations=address-
> resolved spans; LCA = the shared motion anchor)."
