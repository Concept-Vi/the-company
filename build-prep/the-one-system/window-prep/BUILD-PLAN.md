# L8 · THE WINDOW — build plan (grounded, 2026-07-03)

*Foundation proven end-to-end tonight. This is the loop-ready plan: what exists, the one real gap, the augmentation approach, the steps. Built on the tested feed contract (`FEED-CONTRACT.md`). FORM/sight-verify (C8.4/C8.5) are Tim's.*

## Foundation — VERIFIED to exist (both halves)
- **Data (company):** `ops/graph_projection.py` → `.build-container/container-graph.json` emits the projection contract for `project://the-fusion`: `{meta, types, clusters, edges, spine, ghosts, paths}`. Live totals: **30,326 resolved edges** (76,490 total, 46,164 ghosts), **40 clusters**, **8 paths**, **18 spine**, 83/111 kinds. Edges `{from,to,kind,face,provenance}`; paths `{id,kind,label,steps:[{ordinal,at,via}],state}`.
- **Render (counterpart/design):** `surface/viewers/graph/graph-view.js` — `DNA.mountGraph(opts)` fetch→render→bind; `DNA.org.graph` (organisms.js) draws the clustered radial graph; tokens-only; DNA type-icons.
- **Live feed:** the bridge `/api/query` (text-in, embed-by-space) + `ledger.query` v2 + `edge_unified` — see FEED-CONTRACT.md.

## The ONE real gap (the build)
`graph-view.js` today builds a **file-containment tree** from `clusters[].nodes[]` (root-relative paths) + a `types` icon-map + a `root` node — the shape of `counterpart/design`'s OWN `registry/graph.json`. The **container** projection is a different, richer shape: clusters are `{id,label,node_count}` (no nodes[]), `types` are edge-faces (knowledge/containment/lineage), plus typed `edges`, `spine`, `ghosts`, `paths`. ⇒ the window is NOT the file-tree view; it is the **substrate view**: organs/clusters as nodes, the ledger's typed edges between them, the spine highlighted, paths as an overlay, ghosts counted.

## Approach — AUGMENT, don't parallel (tonight's lesson)
Extend `DNA.org.graph` / a thin window-view that consumes the container projection directly (clusters+edges+spine+paths), rendered with the SAME DNA tokens + real glyphics (`CV_GLYPHIC` / the icon pack) + the read-out layer (`CV_MEANING.readGraph`) proven on the phone page. Reuse `graph-view.js`'s bind/pan/zoom scaffolding where it fits; add: typed-edge rendering (face→line-grammar, Glyphic owns the visual grammar), the **paths overlay**, **ghosts** count, **scale/zoom** (post `{scale}` to `/api/query`), and **selection→ask** (selected node ids → `addresses:[…]` → `/api/query` + a keeper_answer scoped to the selection = law 9, most machinery already in the feed).

## Steps (each verified by use, in a browser, before the next)
1. **First paint:** serve `container-graph.json`; render its clusters+edges+spine as the substrate graph (real glyphs, DNA tokens). Verify it draws project://the-fusion + the organs, honest denominators (edges/ghosts/paths counts visible).
2. **The read-out:** layer `CV_MEANING.readGraph` so a selected node/edge speaks itself (the phone-page pattern, at window scale).
3. **Live query:** wire the search box → POST to `/api/query` → render ranked results as a focused subgraph (`expand:true` hydrates the neighborhood). Teaching-refusals (400) surface, never swallow.
4. **Zoom:** `{scale:{space,rung,top_clusters}}` → coarse-first, drill-where-warm (the ledger's scale-drill).
5. **Selection→ask:** select nodes → pass ids as `addresses` → scoped keeper answer (law 9).
6. **FORM (C8.4):** design-critic pass, design-lint, native desktop AND mobile, honest denominators on every view. Glyphic's fields-on-canvas law sheet folds in here.
7. **C8.5 — Tim's sight-verify.** His alone.

## Cross-repo seam
RENDER in `counterpart/design/surface`; FEED in `company` (bridge `/api/query`). The window page lives on the surface side, fetches the projection + posts queries to the bridge. Serve on the tailnet (like the phone page) for Tim's sight-verify.

## Coordination
- ledger (`ch-lp5ecuvo`): owns the feed — ping if a projection/query shape needs to change (it's their `ledger.query`/emitter).
- Glyphic (`ch-518m76r0`): owns the edge/operator VISUAL grammar + the fields-on-canvas law sheet (pending) + the read-out stack. The window's edge rendering + canvas orientation consume these.

## Needs-tim (surface with the window, none block the build)
- Arm the `scale-pyramids` job (keeps zoom fresh).
- C8.5 sight-verify; FORM taste.
