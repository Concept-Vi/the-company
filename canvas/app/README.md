# canvas/app — the rich canvas (React + tldraw)

The visual operator surface (the interface vision): an infinite tldraw canvas where the
composition's nodes are movable cards, with semantic-zoom LOD, an inspector + workshop,
run controls, edge overlay, and the governed GROW loop. Talks to the bridge (the Suite's
UI face) over `/api` (proxied). One generic `NodeShapeUtil` renders every node-type from
the bridge state — no per-type frontend code (S5).

Run:  pnpm install  &&  pnpm dev      # http://127.0.0.1:5173  (needs the bridge on :8770)
Build: pnpm build                      # -> dist/

The vanilla `canvas/index.html` console remains as the dependency-free fallback face.
Tauri desktop packaging is the next wrap (web app first, verifiable now).
