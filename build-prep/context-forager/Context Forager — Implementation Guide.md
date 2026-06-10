# Context Forager — Implementation Guide

**Principles:** assembly, not invention (every seam exists — see the Synthesis); reuse-don't-parallel
(the corpus tools, the canvas patterns, the S1 panel seam); registry-is-truth (chips derive from real
index fields; views become declared rows later); fail-loud (honest empties); the spatial frame is the
UI's identity (forager circles live on the SAME canvas, distinct vocabulary, never rearrange the
graph nodes).

## Sequence (per criteria priority)

**A1/A2 · the shape + loader.** NEW `canvas/app/src/ForagerShape.tsx`: TLBaseShape<'forager', {w,h,
address, label, kind, session, score, content_head}> mirroring NodeShape.tsx (T.* validators,
Circle2d geometry, HTMLContainer, zoom>0.5 semantic zoom). Register beside NodeShapeUtil
(App.tsx:364). IDs: createShapeId('f-'+hash(address)). MODIFY loadGraph's prune (NodeShape.tsx:194-222
neighborhood): filter `shape.type === 'node'` before pruning (and the forager's own clear filters
type==='forager') — THE COEXISTENCE RULE, test it explicitly. BUMP persistenceKey → company-canvas-v4
(new shape type; the stale-snapshot lesson).

**Search lane.** NEW region `ForagerBar.tsx` (top-center, kit Surface): input + space select
(spaces from /api/cognition_info projection list — registry-read, embeddable only) + chips row.
On search: GET /api/corpus-query? — CHECK first whether a bridge route for query_corpus exists
(research: the MCP has it; bridge may need a thin GET route added to BRIDGE_ROUTES + dispatch —
mirror /api/now). Hits → fetch record heads (find_corpus by source_address, content head via
detail='detailed' pattern) → create/update forager shapes near viewport center (grid scatter);
re-hit = pulse class, no dupe (dedupe by address prop).

**B3 expand.** Circle click → indicate(address) — the EXISTING locus machinery (the forager rides
I1); River card = reuse the AddressHelp/History panel pattern OR a light in-canvas card; full-screen
= the Workshop modal pattern (reuse).

**B4 edges.** Reuse the Edges screen-space overlay pattern (App.tsx) with a forager-edge list
computed client-side: same lineage.session ⇒ edge; cap ~3 edges/node by recency, fade by weight.

**C1 chips.** Derive chip values from the loaded hits' real fields (kind/session/space) + the
pattern-tag clusters (GET .build/g13/clusters.json needs a route OR fold cluster-tags into the
record-head fetch — prefer a tiny /api/corpus-facets later; v1: client-derive from loaded set).
Chips FILTER the visible set (hide, not delete).

**C2 time flow.** NEW `flows/ts_backfill.py` (proposes_only pattern violated? NO — it WRITES corpus
records; follow the registry-filling write-half: deterministic re-walk via g23's extract_exchanges,
re-capture same addresses with ts_source added — latest-seq-wins supersedes; fail-loud per file).
Run it once; then the time chip buckets ts_source (month granularity v1).

**D1 handoff.** ClaudeChat: read tldraw selection of forager shapes (editor.getSelectedShapes via
registryStore hook or a window-level getter set in App) → "give to builder" button (visible when
N>0) → build the SET BLOCK: `[Operator's selected context — N items]\n- {address} ({kind},
{session}): {content_head ≤400ch}` ... total cap ~6KB; send as context_block on the next
/api/claude/turn (REPLACE wording: "current selection", because --resume compounds blocks).
Backend: none needed (context_block is already opaque — Synthesis/handoff).

**Don'ts:** DON'T touch NodeShape's props (persistenceKey blast radius) — new shape only. DON'T
auto-run searches on keystroke (embedder load) — explicit submit. DON'T let forager state into the
graph store — circles are VIEW-side (run:// graph stays backend-truth; forager set is session-local
v1, a declared view-row later). DON'T fake facets (C3).

**Preserves:** the graph editor (prune filtered, props untouched) · the S1 panel contract (turn
shape unchanged — context_block only) · the indicate/locus machinery (the forager FEEDS it) ·
all existing routes.
