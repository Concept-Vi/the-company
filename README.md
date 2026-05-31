# company — the Vi composition suite (engine)

The build target: an **interface-driven composition suite** — a canvas where AI chains are composed over sources, configured, run, steered live, and worked with — that runs without depending on Tim.

> **AI agents: read [`AGENTS.md`](AGENTS.md) first, then [`MAP.md`](MAP.md), then the `AGENTS.md` of the module you're in.** There are no human developers — this repo is built and grown entirely by AI, and is structured to be navigable and extensible by you (every module carries a constitution; the contracts are the spine).

> **Source of truth = the build-prep vault**, not this README.
> Specs, contracts (C1–C8), engine design (S1–S7), decisions (D1–D7), and the build plan live at:
> `/mnt/c/Users/Workstation001/Documents/Claude/Projects/counterpart/the Company/build-prep/`
> Start at `Company Build Hub.md`. This repo is where code lands; the vault is where it's specified.

## Layout (boundaries — each maps to a contract/spec)
| Dir | Responsibility | Governed by |
|---|---|---|
| `contracts/` | the pinned data shapes — the seams everything composes against | C1–C8 |
| `store/` | the addressed store + resolver (address → bytes; fs first → Supabase) | C1, C4, S2 |
| `runtime/` | the reactive scheduler + memo gate + compile + context-variable resolution | S1, C5, C6 |
| `fabric/` | model-fabric binding: LiteLLM + llama-swap + adapters + reliability guards | S6 |
| `mcp_face/` | the agent face — FastMCP generic-verb tools (dir is `mcp_face`, not `mcp`, to avoid colliding with the `mcp` SDK) | C7 |
| `nodes/` | the node library (process · content · presentation types) | C2 |
| `canvas/` | the frontend — tldraw + React + Tauri (the interface track) | S5, D3, interface.md |
| `docs/` | pointer to the build-prep vault (the source of truth) | — |

## How it runs (eventually — see the build plan)
- Backend (Python): `runtime/` hosts the scheduler + the bridge (Yjs sync server + action endpoint) and calls `fabric/`.
- Frontend (TS/Tauri): `canvas/` connects as a peer of the runtime's shared document.
- Storage: `store/` on the WSL **ext4** side (not `/mnt/c`) — the runtime needs real fsync.
- First milestone = the **walking skeleton**: one node → runtime → result, real store + real bridge, no AI. See `build-prep/Phase-1 Build Plan.md`.

## Status
🦴 **Skeleton only.** Boundaries drawn; nothing implemented. Build proceeds stage-gated per decision D7.
