# L8 · THE WINDOW — the feed↔render contract (captured 2026-07-03, overnight)

*Perishable coordination knowledge from the night both builders finished Phase B. This is the AS-IS the window (③-A) builds on — the confirmed seams between the three sessions — so loop-prep starts from fact, not memory. Draft: contracts are confirmed by the sessions that own them; the render/FORM choices are Tim's and NOT decided here.*

Authoritative criteria remain `COMPLETION-CRITERIA.md` §L8 (C8.1–C8.5). This doc records HOW the pieces connect, discovered in coordination.

## The three-way division (confirmed on-fabric, threads t-1783002939 / t-1783003005 / g-1783006050)

| Owner | Owns | Session |
|---|---|---|
| **Feed** | `ledger.query` (multi-axis), scale/zoom, `edge_unified` (edges[]), paths axis, the `/api/query` text-in bridge route, embed-by-space routing | ledger — `ch-lp5ecuvo` |
| **Render** | the window surface: projection-contract assembly, the multi-axis view, **selection-as-address-set**, layout | ④ (this session) — `ch-kszn4a1c` |
| **Language** | the glyph/meaning/**read-out** stack (`CV_GLYPHIC.render` · `CV_MEANING.readGraph`), the operator/edge **visual grammar**, the writer compose pipeline, the **fields-on-canvas law sheet** (Glyphic to author before prep closes) | Glyphic — `ch-518m76r0` |

## THE FEED — `ledger.query(spec)` v2 (committed contract; additive-only, unknown keys RAISE)

Spec keys: `{ project, addresses, filter, graph, paths, scale, semantic, lexical, count, limit }`
- `filter`: `path_under` (any-of) + `not_under` (negation) + ext/type/`changed_after`.
- `graph`: `direction` out|in|both · `hops` attributed per result · `expand:true` attaches each result's own edges (from `edge_unified`, both provenances) — hydrate a neighborhood in one call.
- `paths`: `{kind|id|through}` — the journey lens (path_step shape: at_addr/via_kind/ordinal). The fusion campaign path answers its own query (10 ordinals live).
- `scale`: `{space, rung, top_clusters}` — coarse-first, drill-where-warm. **This IS the window's zoom, already answering.** (Overnight: rungs extend over ALL spaces incl. code/symbol, not just docs.)
- `count`: `{by: node_type|ext|language|kind|space|path_prefix}` — aggregates ARE answers.
- `addresses:[…]`: explicit candidate seed. **This is law-9 selection-as-address-set entering the feed** — the window passes a node-selection straight in as `addresses` and asks anything about it. ⇒ **the selection→ask seam needs far LESS custom machinery than specced.**

Results: `[{ address, score, legs, what_it_does, path, node_type }]`
Meta: `{ run_id, candidates_n, plan }` — `plan` echoes every leg's counts (under-recall never silent).

### Text-in UI face — LIVE (ledger P2, committed 2026-07-03; thread g-1783008015)
`/api/query` bridge route is LIVE (additive; bridge restarted):
- **GET** `?text=<phrase>&space=<space>` — quick probe.
- **POST** — full v2 spec body (all axes above).
- Teaching refusals (unknown key / depth-cap) pass through as **HTTP 400** with the verbatim message — the window surfaces them, never swallows.
- Embed routing is single-sourced in `fabric/embed_routing.py` (code/symbol→nomic-3584 w/ num_ctx, else→pplx-2560), shared by the route AND the `coordinate` tool via one `run_query` entry.
- **Golden gate:** `tests/ledger_query_acceptance.py` — 22 checks green (every axis, self-similarity ≈1.0 through the code-pyramid drill, 4 teaching refusals verbatim). The window can rely on this contract as tested ground.

**⇒ The window's search box posts Tim's phrase to `/api/query` and renders the ranked result — NO embed step on the render side. Zoom answers across docs/desc/code/symbol (symbol landing last).**

**Tim-arms dependency:** pyramid freshness is a registered job `scale-pyramids` (daily schedule, born PROPOSED). The window's zoom stays current only once Tim ARMS it — a needs-tim item to surface alongside the window (like the operator flip was).

## THE RENDER — proven building blocks (my side; verified tonight on the phone page)

- **Glyphs are engine-rendered, never hand-drawn.** `CV_GLYPHIC.render(spec)` → HTML string, no React (needs only cv-icons+cv-shapes). `DiagramSolver` (React) draws a full `{type:'glyphgraph', nodes, edges}` with typed edges + layout. Node spec: `{id,form,symbol,fill,color,texture,motion,size,depth,value,x,y}`. Forms: circle/square/triangle/diamond/pentagon/hex/heptagon/octagon/none. `value:'active'` = the ONE gold focal per view (ration it).
- **The read-out is the narration layer.** `CV_MEANING.readGraph(graph)` — per-edge subgraphs joined for full coverage; author page-local glosses (`M.author.setGloss(symbol, noun)`), use VARIED true edge kinds (frames/face/seeds/projection-of/resolves/mirrors/part-of) so it reads as prose not a litany. `hex` form auto-appends "system"; language-family symbols carry default glosses — author WITH the engine.
- **Layout = the claude-ds block ladder.** `<link rel=styles.css>` + `<body data-ground="warm">`; `.cv-band → .cv-section → .cv-zone` (depth-computed wash) → `.cv-cluster` → `.cv-card`/`.cv-btn`. Glass = `.cv-zone--frosted`. Inherit tokens, never redefine `:root`.
- **The projection contract** the render assembles: `paths[]` alongside `clusters/edges/spine/ghosts` — counts-including-zero (honest denominators, C8.4). `edges[]` reads `ledger.edge_unified` {from,to,kind,face,provenance}.
- **The window is an AUGMENTATION — VERIFIED foundation (2026-07-03):** `surface/viewers/graph/graph-view.js` (in `counterpart/design`) IS the instrument — `DNA.mountGraph(opts)` fetches a projection (default `/registry/graph.json`), builds a containment tree, renders an interactive clustered radial graph via `DNA.org.graph` (organisms.js), tokens-only, type-icons from the DNA pack. `registry/graph.json` is the projection shape: `{meta, root, types, clusters, edges, spine}` (669 addresses, 17 clusters; this repo's own graph has edges:0/spine:0 — the CONTAINER projection will carry the ledger's typed edges + paths + ghosts). **The window = `mountGraph` pointed at the container projection (project://the-fusion), fed by `/api/query`, with selection→ask + the read-out layered on.** Do NOT build a parallel instrument — extend this one + the projection contract.
  - Cross-repo seam: RENDER lives in `counterpart/design/surface` (graph-view.js, organisms.js, the DNA pack); FEED lives in `company` (the bridge `/api/query`, `ledger.query`, `edge_unified`, the projection emitter). The window bridges the two.

## THE GAP (gap-extends-union — what's unbuilt vs C8.1–C8.5)
1. The multi-axis window surface itself: containment clusters + typed edges + spine + ghosts + **paths overlay** + zoom (scale:* rungs) + time + provenance-to-conversation, on the chosen surface (C8.1).
2. the-fusion + counterpart-design rendered as living projects — board/decisions/resources/keeper visible through the window (C8.2).
3. Selection = an address-set shared with the Keeper: select nodes → ask → answer scoped to the selection (C8.3). **Now mostly = pass the selection as `addresses` to `/api/query` + scope a keeper_answer to it.**
4. FORM: design-system-built, design-critic pass, design-lint green, native desktop AND native mobile, honest denominators (C8.4).
5. Tim's sight-verify (C8.5) — **his alone.**

## Open (Tim's to decide — NOT presumed here)
- The window's SURFACE (in-gallery instrument augmented? a new app view? the phone form scaled up?) and its FORM/taste — C8.4/C8.5 are Tim's.
- Glyphic's fields-on-canvas law sheet (warmth/ordinal gradients as orientation) — pending, folds in when authored.

## Pointers
- Criteria: `../COMPLETION-CRITERIA.md` §L8 · Design: `../THE-CONTAINER.md` + upgrade laws (law 9 = selection-scoped keeper)
- Proven surface tonight: `/home/tim/company/.build-container/phase-b-served/index.html` (served `https://workstation001.tail777bc2.ts.net:8792/`) — the read-out + real-glyph composition, the window's small sibling.
