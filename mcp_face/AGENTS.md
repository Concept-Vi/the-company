---
type: constitution
module: mcp_face
aliases: ["mcp_face — constitution"]
tags: [company, constitution, mcp_face, agent-face]
governs: [C7]
relates-to: ["[[Company Map]]", "[[runtime — constitution]]", "[[contracts — constitution]]"]
status: living
---

# mcp_face/ — module constitution

> Dir is `mcp_face`, **not** `mcp`, to avoid shadowing the installed `mcp` SDK package.

**Is:** the agent face — a FastMCP server (`server.py`) exposing the **generic verbs** the right-hand-man (and any agent) uses to drive everything (C7). Thin: it calls the shared `runtime.suite.Suite` — the same brain the UI bridge uses.
**Guarantees:** verbs are **generic over node-type** — there is **no tool-per-node-type**; tools consult the registries to act on any type. `ToolAnnotations` (readonly/destructive/idempotent) live in `contracts/tools.py` and feed governance (S7/D4); **at the face layer they are wired through to SDK hints for the session-fabric tools** (`tools/sessions.py` — the first honest instance, F10.1; the older tools carry contracts-layer annotations only, face wiring pending). Consolidated tool modules EXPORT a closed `OPS` constant (CONTRACT-FORMAT §9.2 — the contract corpus's machine inventory; `tools/sessions.py` is the first, drift teeth in `tests/supervisor_routes_acceptance.py`; older modules predate the obligation and the reality extractor will fail loud on them when it lands). One brain, two faces (this + the canvas).
**Where new things go:** adding a node-type/model/source adds **zero tools**. A genuinely **new kind of operation** = one new verb (rare).
**To extend:** only add a verb for an operation the system never had; otherwise nothing here changes when the system grows.
**Seam:** implements C7; reads the registries (C2/S3); calls [[runtime — constitution]]; governed by S7.
**Never:** add a tool per node-type · leave a destructive verb unannotated · duplicate logic that belongs in the internal API.

## What's in here

The agent face — the **generic verbs** (C7) exposed over a FastMCP stdio server. It is how
an **AI operates the system**: drive any node-type, query the registries, run graphs, read
state — all through type-generic tools, never a tool-per-type. It shares the **one
`runtime.suite.Suite`** the canvas UI bridge uses — one brain, two faces. The live verb set
is the single source of truth in [[Company Map]] (do not duplicate it here; that's the rule
in [[Vault Conventions]]).

## Relates to

- **Calls / shares** [[runtime — constitution]] — the *same* `Suite` the UI bridge calls.
  One brain, two faces: this one is the AI's, the canvas is the operator's.
- **Governed by** [[contracts — constitution]] — the C7 verb contract is the shape every
  tool here obeys.
- Note: operator-only actions (apply / approve) are deliberately **NOT reachable** from this
  face — the AI proposes; the operator disposes.

## Read next
[[Company Map]] (the live verb set + the whole picture) · [[runtime — constitution]] (the shared brain behind both faces) · [[Concepts and Principles]] (C7 and the generic-verb idea).
