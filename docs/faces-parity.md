---
type: reference
register: descriptive
aliases: ["faces parity", "capability × face table"]
tags: [company, faces, mcp, cli, http, parity]
status: living
---

# Capability × Face parity — where each capability is reachable (2026-07-08)

*The one-function-two-faces law, audited. Every substrate capability and which faces serve it:
MCP (agents) · CLI (`company <verb>`, the terminal) · HTTP (the bridge, the future window's feed).
Gaps are named honestly — a blank is a known gap, not an oversight.*

| capability | MCP | CLI | HTTP |
|---|---|---|---|
| coordinate query (all axes) | `coordinate` op=query | `company query` (semantic-only quick form) | GET/POST `/api/query` |
| saved queries (save/list/run) | `coordinate` op=save/saved/run | — gap: a `company query --saved` form | — gap (window will need rpc or a route) |
| query watches (diff + notify) | via `jobs` (handler watch_query) | `company jobs` (visibility) | — |
| pointing (ui→code, symbol) | `scope` op=resolve/symbol | — | `/api/scope`, `/api/address-help` |
| jobs (define/fire/arm/status) | `jobs` all ops | `company jobs` (status only — gap: fire/arm verbs) | — gap (window needs job control) |
| embeddings (spaces/route/build/pyramid) | `embeddings` all ops | `company embed` all subs | — gap |
| authorship timeline | via `coordinate` origin:true | `company timeline PATH` | — |
| model runs (role/items/reduce/cascade/graph) | `run_role`/`run_items`/`run_reduce`/`run_cascade`/`run_graph` | — (by design: model runs are agent/window work) | `/api/*` bridge doors exist for graph/cascade |
| flows / routines | `flows` / `routines` | — | `/api/flows`, `/api/routines` (unconsumed) |
| circuit (marks/decisions/inbox) | `marks`/`decisions`/`inbox` | — | inbox rides the surface routes |
| services/GPU/models | — (deliberate: ops is operator-side) | `company up/down/gpu/models/swap/ensure` | — |
| semantic corpus (legacy face) | `corpus` | — | `/api/corpus-query` |

## The known gaps, ranked
1. **HTTP job control + saved-query routes** — the window's mandate ("action every kind of model run")
   needs these; they belong to the L8 build (the feed side is one thin route each over the existing fns).
2. **CLI fire/arm forms** (`company jobs fire <id>` / `arm <id>`) — cheap adds when wanted; the MCP ops
   exist and `company jobs` shows everything.
3. **`company query --saved`** — same.

## The law this table audits
Every capability is ONE implementation with thin faces (e.g. `run_query` serves the coordinate tool AND
/api/query AND `company query`; `jobs_status` serves the jobs tool AND `company jobs`). A new capability
lands as: the shared function → the MCP face → the CLI/HTTP faces as thin invokers. Never a second dialect.

## The agent substrate (local Supabase MCPs) — where live guidance lives
Agent-authored guides for this terrain live IN the local Supabase substrate (searchable by every agent via
the supabase_admin MCP): `guide_read('ledger-coordinate-query')` · `guide_read('ledger-schema-map')` ·
`guide_read('jobs-heartbeat-system')` (+ `guide_search(q)` over all of them). A response-rule
('ledger-guides-pointer') points any agent running ledger SQL at them automatically. When you change the
query vocabulary, the schema, or the jobs system: UPDATE THE GUIDE (guide_write upserts by name) — the
substrate is the live doc surface; this file is the parity audit.
