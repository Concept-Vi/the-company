---
type: terrain-entry
name: creations
register: descriptive
aliases: ["creations", "VECO"]
status: unconfirmed   # scaffold fact (declarative specs only — no handlers/runtime/package.json) recorded in body Notes; lifecycle status is Tim's to confirm
coverage: { files_read: 13, files_total: 13, last_read: 2026-06-26 }
relation: resource
kind: work
path: /home/tim/creations
created: 2026-03-01
last_active: 2026-03-01
size: 112K
git_remote: none
secrets: false
move_intent: none
prospected-for: ["[[company]]"]
relates-to: ["[[docs]]", "[[world-keeper-profile]]", "[[cognitive-framework]]", "[[universal-mechanics]]"]
era: 2026-03-genesis-event
domain_ref: conceptv.com.au
themes: [composition, circuits, dataflow, model-provider-abstraction, mcp, self-build, role-resolved-cognition]
concepts: [universal-circuit, VECO, genesis-event, principal-domain-intent-proposal-approval-execution, dual-provider-router, per-stage-model-selection, approval-gate]
tags: [mcp, model]
---

# creations (VECO — Universal Circuit Engine / Genesis Event)

## What it is
A small, **declarative TypeScript engine that models any process as a "circuit"** — a typed, staged flow that always runs **Principal → Domain → Intent → Proposal → Approval → Execution** (verbatim Tim's relational-systems circuit from his global CLAUDE.md). "VECO" is the circuit type (the name is never expanded in any file). It ships three circuit shapes: **simple** (linear 6-stage), **conditional** (branches on complexity at a decision node), and **MCP** (adds tool-discovery/binding/execution stages so a circuit can call external MCP tools). It is wrapped in a game/narrative fiction ("Chapter 3: The Living World", "Quest #7: The Genesis Event", authored by NPCs including a "World Keeper v3.0").

> `'Complete 6-stage circuit: Principal→Domain→Intent→Proposal→Approval→Execution'` — `/home/tim/creations/universal_circuit_engine/src/circuits/simpleVECO.ts:5` (stages: Principal="the who", Domain="the what", Intent="the why", Proposal="the how", Approval="the gate", Execution="the result").

Crucially it is a **specification/scaffold, not a working program**: types + circuit data + instance data + named-string handlers (e.g. `"principalHandler"`), with no handler bodies and no runtime. No `package.json`, no build tooling.

## Key ideas worth mining
- **The universal circuit as a reusable primitive** — one invariant flow (the 6 stages) reused across every variant; new capability (branching, MCP tools) added by *extending the same stage sequence*, not rebuilding. Tim's Universal Composition ("identify the relational primitive once, reuse everywhere") rendered literally in code.
- **The Genesis Event as bootstrap-by-self-execution** — `genesis-001` (`instances/genesis.ts`) runs the engine on its own initialization; the first circuit's intent is "establish the Living World." Mirrors the Company's self-hosting / self-build spine (first real use = the system on itself).
- **Dual-provider abstraction (Anthropic + Ollama Cloud)** — a `veco-router-001` router selects provider by **task complexity** and **token requirements** (high→opus, 128k+→ollama_cloud) with automatic failover (timeout/rate_limit/error → Ollama). Provider is *resolved*, not pinned — echoes Tim's cognition-is-role-resolved rule. The nested config even does **per-stage model selection** (principal→opus, domain→sonnet, execution→kimi): different cognition per stage of one circuit.
- **MCP as a first-class circuit capability** — tool discovery → binding → approval → execution modeled as explicit stages with `MCPBinding` (server/tool/input-output mapping).
- **Approval as a structural gate** — "Approval" is mandatory ("the gate"); `requiresApproval: true` is the default. The consent point is built into the primitive.
- **Composition contracts via typed stage I/O** — each stage declares `inputs`/`outputs` and `transitions` — typed dataflow wiring, the same shape as the Company's typed compositional dataflow.

## How it relates conceptually to the Company
A **conceptual cousin / earlier independent expression** of the Company's spine, not a dependency. Composition/circuits-as-primitive → the Company's typed compositional dataflow (stages=nodes, transitions=wires, typed I/O=contracts). The literal 6-stage flow is copied straight from Tim's relational-systems doctrine — strong evidence `creations` is *Tim's framework instantiated by an agent*, a prime pattern-discovery artifact for "what is a circuit to Tim." The router (complexity/token-driven, Anthropic-primary, Ollama-fallback, per-stage models) is a concrete prototype of the Company's Native Model Layer + role-resolved cognition + clone-model-by-context rules. MCP-as-first-class ties to MCP-top-priority. It is an **island** whose good parts (router policy, per-stage model resolution, typed circuit primitive) could be mined INTO the centre. `relation: resource`.

## When / where
Created and last active 2026-03-01 (all `createdAt` stamps 2026-03-01T22:00:00Z). Path `/home/tim/creations`, 112K, 13 files, no git (not a repository). Read 13 of 13 (complete).

## Notes / evidence
- All 13 files read: `src/types/veco.ts`, `src/index.ts`, `src/circuits/{genesis,simpleVECO,conditional,withMCP,mcpVECO,index}.ts`, `src/instances/genesis.ts`, `src/tests/setup.ts`, two `config/dual-provider-circuits.json` copies (root + nested — divergent drafts: root snake_case/flat, nested camelCase/per-stage providerConfig), `config/npcs/ollama_keeper.yaml`.
- `domain_ref`: configs declare `"$schema": "https://veco.conceptv.com.au/schema/dual-provider-circuits.json"`.
- Secrets: **false**. No hardcoded keys; providers referenced only by env-var name (`ANTHROPIC_API_KEY`, `OLLAMA_API_KEY` in the config + `api_key_env: OLLAMA_API_KEY` in the yaml). Config note line 237: *"Both providers require API key provisioning by Tim."*
- Status: scaffold — declarative specs only, named-string handlers, no runtime. Treat as scaffolding-not-spec.
