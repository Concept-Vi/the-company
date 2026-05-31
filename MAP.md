# MAP.md — the loadable map

The orientation an agent loads first, and the seed of the **linked code-knowledge** that becomes Tim's click-and-talk surface (the system, navigable as a graph — by agent and by Tim). As the code grows, this map is maintained *by the system about itself* (the reflective fold).

## The one picture
```
  canvas/  ── the surface you operate (tldraw/React/Tauri) ─────────────┐
     │  composes / sees / works-with                                    │
     ▼                                                                  │  (the bridge, C8 / contracts/)
  runtime/ ── reactive scheduler + memo gate + compile + context  ──────┤
     │  calls                                                           │
     ▼                                                                  │
  fabric/  ── the models (LiteLLM + llama-swap + guards) ───────────────┘
  store/   ── where everything lives, by address (C1/C4)   [under runtime + canvas]
  mcp/     ── the agent face: generic verbs over all of it (C7)
  nodes/   ── the node library (process · content · presentation), each one C2
  contracts/ ── the spine: the shapes all of the above compose against (C1–C8)
```

## Module map (each links to its constitution + governing contracts)
| Module | One-line | Constitution | Governs |
|---|---|---|---|
| `contracts/` | the pinned shapes (the seams) | `contracts/AGENTS.md` | C1–C8 |
| `store/` | addressed store + resolver | `store/AGENTS.md` | C1, C4 |
| `runtime/` | reactive scheduler + memo + compile + context | `runtime/AGENTS.md` | S1, C5, C6 |
| `fabric/` | model binding + guards | `fabric/AGENTS.md` | S6 |
| `mcp/` | agent face (generic verbs) | `mcp/AGENTS.md` | C7 |
| `nodes/` | the node library | `nodes/AGENTS.md` | C2 |
| `canvas/` | the frontend (discovered through use) | `canvas/AGENTS.md` | S5, D3 |

## How a run flows (so you can trace any change)
`canvas` (place+wire nodes) → `compile` (runtime: workflow → execution graph) → `scheduler` (runtime: a node fires when its input **addresses** resolve in `store`) → AI nodes call `fabric` → results persist to `store` (content-addressed + provenance) → status/output flow back through the bridge → `canvas` re-renders. The `mcp` face can drive every step; the right-hand-man's context is resolved by `runtime/context_variables`.

## Self-growth (the point)
Once the kernel runs, **the system's first real use is its own codebase** — this map + the code, indexed and linked, so Tim clicks and talks here and directs changes, which are dispatched back into these modules. The interface is grown by being used on this. See the vault: `Self-hosting first use — codebase as first source.md`.
