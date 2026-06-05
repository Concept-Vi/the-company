---
type: constitution
module: canvas
aliases: ["canvas — constitution"]
tags: [company, constitution, canvas, frontend]
governs: [S5, D3]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[nodes — constitution]]", "[[extensions — constitution]]", "[[panels — constitution]]"]
status: living
---

# canvas/ — module constitution

**Is:** the frontend — the surface Tim operates (tldraw + React + Tauri). Implements S5/D3. **This is the part discovered through use** — expect it to grow as Tim hits limits and directs fixes; build for change.
**Guarantees:** **one generic `ai-node` shape**, data-driven from `/object_info` (C5) — **not** one shape per node-type (so new types need zero frontend code). The canvas **reflects** state, never **owns** it (the runtime is authoritative; the canvas is a peer of the shared document via the bridge, C8). Render-modes (collapsed→workshop) are conditional rendering on the node's props (D3).
**Where new things go:** a new **surface/component** (now-view, inspector, inbox, RHM panel, presence dial, fleet…) = a component here. A new **node-type** needs **nothing** here.
**To extend:** add a component for a new surface; keep node rendering generic. Interface decisions (look/feel/layout) are Tim's (I0) — read them from the vault.
**Seam:** consumes `/object_info` (C5) + the bridge (C8) into [[runtime — constitution]]; renders C3 records and [[nodes — constitution]] generically; render-set/inspector per C2; hosts [[panels — constitution]] and [[extensions — constitution]].
**Never:** write per-node-type frontend code · hold authoritative state · hardcode layout that should be data-driven · pre-bake an interface Tim hasn't decided (let it grow through use).

## What's in here

The frontend Tim operates — **tldraw + React + Tauri**, the desktop surface where the system
becomes something you point at and talk to. The structure nests:

- **`canvas/app/`** is the **Vite/React app** itself — the shell, the tldraw board, the
  surfaces (now-view, inspector, inbox, RHM panel, presence dial, fleet). Its own `README`
  documents how to run and build the app.
- **`canvas/app/src/extensions/`** is the **brain-authored extensions live-tree** — arbitrary
  UI the system writes for itself at runtime, gated. It is its own module with its own
  constitution: [[extensions — constitution]].

For the whole picture of how this surface sits over the runtime and the shared document, see
[[Company Map]].

## Relates to

- **Calls** [[runtime — constitution]] via the bridge (C8) — the canvas is a peer of the
  shared document; it **reflects** state, never **owns** it (the runtime is authoritative).
- **Renders** [[nodes — constitution]] generically from `/object_info` (C5) — one `ai-node`
  shape for every node-type, so new types need zero frontend code.
- **Hosts** [[panels — constitution]] (declarative surfaces) and [[extensions — constitution]]
  (arbitrary brain-authored UI, gated).
- **Governed by** [[contracts — constitution]] — the C8 shared document is the contract the
  canvas and runtime both obey.

## Read next
[[Company Map]] (the whole picture) · [[extensions — constitution]] (the brain-authored live-tree this surface hosts) · [[Concepts and Principles]] (why the surface reflects rather than owns).
