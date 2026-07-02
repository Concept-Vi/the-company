# Glyphic Language — Research Synthesis (ground truth)

> The evidence base the Criteria + Guide rest on. Findings from three exploration agents
> (2026-06-30) + direct reading this session. Rule: this is **what EXISTS**; specs bend to
> this, not the reverse. Status tags: **VERIFIED** (confirmed by running), **READ** (confirmed
> by reading the code), **DESIGNED** (intended, not built).

## The headline
Glyphic ("a glyphgraph is a meaning-representation — concepts + typed relations — that
transglyphs to a sentence") is **~75% already wired** across the design system and the Company.
The job is **completion + a few new pieces**, NOT a new system. Do not build parallels.

## Round 1 — the meaning layer (design system) — READ + VERIFIED this session
- `assets/icons/cv-meaning.js` (`window.CV_MEANING`) — the **one home of meaning**, redesigned this
  session into the language layer: FIELDS `{feeling, senses[], type}`, `MEANING_TYPES`, combinatorial
  `modeOf`, `field()/describe()/describeRelation()`, edge facets (line/edge/direction/outline). Loud-fail.
  **VERIFIED** headless (`_demo/verify_language.js`): the read-out composes from facets; all loud-fail cases throw.
- `assets/icons/cv-glyphics.js` — `CV_GLYPHIC.compose` (one node → SVG), `composeRelation` (node→edge→node
  → `{html, sentence, read}`), `describe` (delegates to CV_MEANING). **VERIFIED**. *This is the atomic unit
  of a glyphgraph — reuse directly, call it N times.*
- `assets/icons/cv-edges.js` (`window.CV_EDGES`) — edge-kind vocab (face/documents/higher-order/navigates),
  `.resolve()` applies defaults. **READ.** Extend with the operator class + more kinds.
- `assets/icons/cv-shapes.js` — `CV_SHAPES.edgeSVG(facets,opts)` renders the connector (line texture +
  arrow); `markSVG` renders a node shape; `shapeTypes` = form→type-class. **READ.** Reuse; extend edgeSVG for
  line colour + the new line-types (right-angled/curved/free).

## Round 2 — the type graph / schema (design system) — READ
- `app/registry/types-core.js` (`window.CV_REGISTRY`) — **already a typed graph schema.** `register/resolve
  (single-inheritance flatten)/lineage/query`. **`accepts(socket, type, ctx)` (lines 249–273) = socket
  domain/range validation** — REUSE for edge domain/range. Type record carries `sockets {accepts, forbid,
  conditions, address}`, `valueSlots`, `parts`, `classification`, `extends`, `conditions`.
- `app/registry/kinds-type.js` — **`kind.graph` ALREADY EXISTS** (lines ~48–56): *"typed nodes placed by
  relationship — a node is a Glyphic; an edge carries a relationship type"*, sockets `nodes: accepts
  ['glyphic','atom','block']`, `edges: accepts ['relationship']`, `runtime: {kind:'engine', key:'DiagramSolver'}`.
  **The 'relationship' socket is an UNFILLED PLACEHOLDER** — no relationship Types are seeded. This is the seam.
- `app/registry/glyphic-type.js` — the Glyphic as a Type with `parts` (ring/symbol/fill — each a mini-Type
  with own valueSlots/sockets) and `sockets` (accepts + address-to-occupant). **The parts ARE the
  independent ring/symbol substrate.** Sockets already bear addresses.
- `app/registry/conditions.js` (`window.CV_COND`) — full condition engine: `test/testAll/failures`,
  forms (structured `{field,op,value}` / DSL "fill != none" / predicate), operators (==,!=,>,>=,<,<=,in,
  exists…), composites (all/any/not). **REUSE for conformance/well-formedness AND conditionals/negation.**

## Round 2b — the generative engine (design system) — READ
- `core/cv-nodes.d.ts` — **`CVGraph` IR ALREADY EXISTS**: `{type, nodes:[{id,label,shape,tone,icon,x?,y?}],
  edges:[{from,to,kind,label?}], center?, axes?, state?}`. **This is the glyphgraph data model** — extend
  the node to carry a full glyphic-spec + an `address`, the edge to carry a relation-type id + line facets.
  Note: `edge.label` is in the IR but NOT rendered (gap).
- `core/DiagramSolver.jsx` — **graph layout + render ALREADY EXISTS** (closed-form per type: hub/network/
  pipeline/timeline/quadrant/tree/stack). `layout(graph)` (30–76) → `{id:{x,y}}`; renders SVG edges
  (straight, center-to-center, arrowhead by kind, lines 288–296) + absolute-positioned nodes (298–325).
  NOT a general layout engine (curated formulas). **Extend: add a `glyphgraph` layout case + render nodes as
  full glyphics (CV_GLYPHIC.render) + DRAW edge labels.**
- `core/RenderType.jsx` — bridge: a registry Type with `content.graph` → `{kind:'diagram', graph}` →
  DiagramSolver (line 124). **A glyphgraph plugs in here, no new bridge.**
- `core/Slide.jsx` — the `diagram` archetype already hosts any CVGraph. `core/archetype-catalog.js` — add a
  `glyphgraph` META/SAMPLES entry → it becomes a catalogued, selectable type.

## Round 3 — addresses + edges (the Company backend) — READ (the convergence)
- `contracts/address.py` + `runtime/cognition.py:resolve_address` (~1014–1163) — **one addressed state**,
  18+ schemes (run:// cas:// ui:// skill:// guide:// session:// board:// decision:// …), extensible
  dispatch. **A glyphgraph node can BE an address.** A `glyphgraph://<frame>/<id>` scheme follows the
  decision://vi-vision:// precedent (a new dispatch branch) — held for the convergence phase.
- `runtime/relation_types.py` + `relation_types/` dir — **a file-discovered registry of typed, directional
  edges** between corpus units: each `relation_types/<id>.py` declares `RELATION_TYPE {id, directed, inverse,
  near, far, label, desc}`. API `.as_records()/.get()/.directed()`. **This IS the general edges registry.**
  `board_edges/` is a specialization (one mechanism, many vocabularies). **glyphgraph edges ≡ relation_types**
  (or a parallel `glyphgraph_edges/` vocabulary on the same mechanism).
- So the deep convergence (already true, not invented): **addresses = the nouns, relation_types = the verbs.**
  Glyphic over the Company = a graph of addresses joined by relation_types. The design-system glyphgraph and
  the Company address/edge world are the SAME language at two altitudes — the design side renders + reads it,
  the Company side stores + resolves it.

## Reuse / extend / add verdict
| Need | Verdict | Where |
|---|---|---|
| atomic node→edge→node render + sentence | **REUSE** | `cv-glyphics.js:composeRelation` |
| meaning fields + read-out | **EXTEND** | `cv-meaning.js` (add readGraph, operators, new facets) |
| edge-kind vocab | **EXTEND** | `cv-edges.js` (+ operator class, line colour, new line-types) |
| connector geometry | **EXTEND** | `cv-shapes.js:edgeSVG` (line colour, right-angled/curved/free) |
| glyphgraph data model | **REUSE/EXTEND** | `core/cv-nodes.d.ts:CVGraph` (node += glyphic-spec+address; edge += relation-type+label) |
| layout + render | **EXTEND** | `core/DiagramSolver.jsx` (+glyphgraph layout, full-glyph nodes, edge labels) |
| type graph / domain-range | **REUSE** | `CV_REGISTRY.accepts` + seed `relationship` Types (fill `kind.graph`'s placeholder) |
| conformance + conditionals | **REUSE** | `CV_COND` |
| independent ring/symbol | **REUSE** | `glyphic-type.js` parts |
| node = address; edges = relations | **REUSE/EXTEND** | `resolve_address` (+glyphgraph:// later); `relation_types/` |

## Do-NOT-duplicate (loud)
Do not fork CV_GLYPHIC, CV_SHAPES, CV_MEANING, CV_EDGES, CV_REGISTRY, DiagramSolver, or relation_types.
Do not build a second edge registry, a second layout engine, or a second meaning store. Every new thing is a
**registration** (a relationship Type, an operator field, a layout case), per extend-by-registration.

## Round 4 — folded into scope (2026-06-30 unfinished-scan; Tim: "anything found → add to scope")
A broad sweep surfaced 18 unfinished/related items. ALL folded into scope (3 clusters). Detail in the
exploration outputs; the actionable scope additions:
**A · Rendering completeness** — (1) `fill:'solid'` is seeded in CV_MEANING but has NO render (cv-meaning.js:322
"aspirational"); need a solid-colour FILL_RAMPS recipe + compose path. (2) `outline` (solid/dashed/none) is
MEANING-seeded but SCHEMA-ORPHANED — not in `CV_GLYPHIC.FACETS`, no markSVG param; this blocks the "potential"
(dashed) mode the whole fill-gradient needs. (3) edge facets (line/lineColor/direction) seeded in CV_MEANING but
not wired into CV_EDGES.resolve→edgeSVG render; (4) DiagramSolver edge LABELS + facet styling not rendered.
→ folds into G2/G5.
**B · Wiring** — (5) `relation_types.py` registry complete but `find_relations` NOT wired into the Suite (the
graph-from-relations bridge is a future seam, relation_types.py:48); (6) glyphic-type parts/slots/sockets only
partially formalized → `candidatesForSocket` doesn't work for glyphics yet; (7) no `edge://`/`relation://` address
scheme (address.py) — needed when an edge is navigable. → folds into G3/G6.
**C · Vocabulary/templates** — (8) symbol taxonomy is a flat list, needs domain/kind/tags facets (ICON-AUDIT
flagged); (9) symbolGloss has ONE entry (house→home) — backfill ~110 + auto-gloss in the foundry; (10) meaning
PROFILES: only the default ships — author template profiles (deck/diagram/ui/…); (11) System-Map draft encoding
channels (border/texture/glow, cv-meaning.js:246–252) unbuilt; (12) `kinds/raw.py` tentative, awaiting ratify.
→ folds into G1/G8 + a new "vocabulary" track.
**Verdict:** none deferred (under-prep costs more than it saves). Priority unchanged: rendering-completeness
(outline+solid first — it unblocks the fill-gradient) rides in G2; wiring in G3/G6; vocabulary continuous via G0
authoring + G8.

## Round 5 — dual-surface / context-attachment (2026-06-30 page/guide explorer) — for G8
- **Attach a PAGE** to any address: `inspect_address(address, op='attach_page', html, title)` → stored cas://,
  served no-script at :8774 (page_face.py:107, mcp_face/server.py:215). Render via `page_render.render_address_page`.
- **Attach a GUIDE/howto** (dual AI+human): drop `guides/<id>.py` `{id,target,content,grounded_from(non-empty!),
  source_hash}` → `guide://<id>`; or `author_guide(target, grounded_from, guide_id)` (model-composed, grounded-only).
- **Design-system self-doc:** `@dsCard` comment in a `preview/*.html` → auto-appears in the Studio (face-index/_ds_manifest).
- **Dual = guide://(AI reads) + page(human reads)**, and skill://(instruction) + guide://(narrative). So each Glyphic
  thing gets: a guide (AI narrative), a page (human face), an @dsCard/system page (design self-doc) → G8.

## Open / decide
- **Layout for arbitrary graphs:** DiagramSolver's closed-form layouts suit small structured graphs; a free
  meaning-graph may need a force-directed / DAG (dagre-style) layout. DECISION (Guide §G5): start by
  authoring positions (`x/y` already supported in the IR via the quadrant path) + a simple layered layout;
  reach for force-directed only if needed. No external lib without checking the CSP/bundle.
- **Where edges live for the convergence:** reuse `relation_types/` vs a new `glyphgraph_edges/`. DECISION:
  reuse `relation_types/` where semantics align; only branch a vocabulary if glyphgraph needs edge kinds that
  aren't corpus relations.
- **glyphgraph:// scheme:** held for the convergence phase (G6), not v1.

## Round 6 — G11 layout RESOLVED: stable-slot, NOT force-directed (2026-06-30 layout build)
- **The "Open / decide" layout item above is now decided by RUNNING the real engine, not reasoning.**
  Measured the existing layered layout (`DiagramSolver.layout()` case `glyphgraph`) on a branch and a
  branch+1-sibling: the even-spread `x = 44 + ci*(VB-88)/(m-1)` **re-centred the whole row on every
  sibling addition** — existing node `pr` jumped 276→160 (a 116px / 36%-of-canvas jump) purely because a
  sibling appeared. That is the one real insufficiency, and it is precisely the staged-reveal goal's enemy.
- **Force-directed/DAG (the CRITERIA G11 "richer" words) is the WRONG axis** — it relaxes the whole graph,
  so it is the LEAST stable under incremental reveal, and it tempts the no-external-lib CSP line. The right
  axis is **deterministic / index-stable**, a SMALL fix, not a rebuild. So G11 ships as a stability fix.
- **The fix (in `core/DiagramSolver.jsx`, the `glyphgraph` case):** STABLE-SLOT placement. Each node sits at
  `x = LAY_MARGIN + slotIndex * LAY_PITCH` where slotIndex = the node's stable AUTHOR order within its rank
  row, and `LAY_PITCH` derives from a **FIXED** reference size (58), not the count-dependent render size — so
  neither adding a sibling NOR crossing the 4/6-node render-shrink thresholds moves any existing node.
  Rows anchor LEFT (the honest tradeoff: a bounded viewbox can't both pin existing nodes AND re-centre).
- **Scope (honest):** stability is for SAME-RANK sibling addition within capacity (~2 slots/row at this pitch).
  Beyond capacity, later slots run OFF the right edge honestly (no silent re-pack). An edge that changes a
  node's longest-path RANK moves it to another row — out of scope by design (mandate = "siblings added").
- **Verified BY RUNNING** `_demo/verify_g11.js` (21/21): the REAL `layout()` source-sliced out of the JSX (not
  reimplemented); strict-equality oracle (every pre-existing node byte-identical across 2→3→4→5 reveal),
  no-overlap within capacity, count-independent pitch, honest overflow, siblings (hub/network/quadrant) preserved.
- **Two HONEST boundaries (verified, not hidden):** (a) the no-overlap claim holds for SHALLOW graphs
  (≤5 ranks); a DEEP pure CHAIN (≥6 ranks) compresses VERTICALLY below the render size and overlaps — this is
  PRE-EXISTING (the y row-pitch `232/(nR-1)` is untouched by this fix, which is X-axis only); the harness asserts
  WHERE the boundary is rather than claiming it away. (b) the slot is POSITIONAL (author order), so the verified
  stability is "same-rank sibling APPENDED to the nodes array" — insert-in-middle/reorder shifts later slots
  (out of scope by design; staged reveal in practice is append or show/hide on a fixed array).
- **FLAGGED for Tim (FORM, NOT green-painted) — a CHOICE, not just a defect:** rows now LEFT-HUG (source +
  small rows sit at the left margin, right gutter empty) — the cost of pinning over centring. There is a STABLE
  centred alternative that keeps all 21 tests green: `x = cx + (ci - (CAP-1)/2)*LAY_PITCH` (CAP fixed from
  VB/pitch) — count-independent, so still no-jump, but rows sit centred instead of hugging left. So the call is
  **left-anchored vs centred-on-fixed-capacity, BOTH stable — which reads better** — a taste call for Tim's eye
  in the live render (`system/language.html`), not a binary defect.
