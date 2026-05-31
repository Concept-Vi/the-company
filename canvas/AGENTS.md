# canvas/ — module constitution

**Is:** the frontend — the surface Tim operates (tldraw + React + Tauri). Implements S5/D3. **This is the part discovered through use** — expect it to grow as Tim hits limits and directs fixes; build for change.
**Guarantees:** **one generic `ai-node` shape**, data-driven from `/object_info` (C5) — **not** one shape per node-type (so new types need zero frontend code). The canvas **reflects** state, never **owns** it (the runtime is authoritative; the canvas is a peer of the shared document via the bridge, C8). Render-modes (collapsed→workshop) are conditional rendering on the node's props (D3).
**Where new things go:** a new **surface/component** (now-view, inspector, inbox, RHM panel, presence dial…) = a component here. A new **node-type** needs **nothing** here.
**To extend:** add a component for a new surface; keep node rendering generic. Interface decisions (look/feel/layout) are Tim's (I0) — read them from the vault.
**Seam:** consumes `/object_info` (C5) + the bridge (C8); renders C3 records; render-set/inspector per C2.
**Never:** write per-node-type frontend code · hold authoritative state · hardcode layout that should be data-driven · pre-bake an interface Tim hasn't decided (let it grow through use).
