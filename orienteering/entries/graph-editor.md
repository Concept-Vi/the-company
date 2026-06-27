---
type: terrain-entry
name: graph-editor
register: descriptive
aliases: ["graph-editor", "RelaTesseract", "rltsrct MCP"]
status: unconfirmed
coverage: { files_read: 6, files_total: 19890, last_read: 2026-06-26 }
relation: resource
kind: work
path: /home/tim/repos/graph-editor
created: 2026-02-10
last_active: 2026-05-26
size: 423M
git_remote: https://github.com/Concept-Vi/ReleTesseract
git_branch: main
git_last_commit: 2026-03-29
secrets: false
move_intent: none
prospected-for: ["[[company]]"]
relates-to: ["[[universal-mechanics]]", "[[cognitive-framework]]", "[[creations]]", "[[docs]]"]
depended-on-by: ["[[company]]"]   # ALSO runs as the live rltsrct MCP referenced by the Claude Code session config (was also_relation: dependency); the alias `rltsrct MCP` names that operational role
era: project-vi-tooling
themes: [memory-graph, relations-first-class, registry-driven, address-based, universal-composition, tesseract]
concepts: [graph-as-substrate, relational-primitive, surface-API, JIT-tooling, token-cascade, reference-protocol]
tags: [mcp, memory]
---

# graph-editor (RelaTesseract / rltsrct MCP)

## What it is
Two things in one repo. **The editor:** a browser-based interactive graph visualization/editing tool (vis.js Network, served at `localhost:8899`) for **Project Vi memory graphs** — full CRUD on entities, relations, observations, metadata; comments-as-graph-entities; Focus & Query filtering; JSON export/import. It is mid-migration from a 16,000-line hardcoded `index.html` monolith toward a **registry-driven, token-cascading, component-composed** architecture (18 registries in 6 layers; primitives→semantic→components token cascade). **The MCP (`rltsrct`):** a Model Context Protocol server (`mcp-server/server.js`, ports 8898/8899) that exposes the editor's EditorAPI to agents via an EditorAPI bridge (jsdom), letting Claude read and mutate the same graphs the browser edits.

> README carries an unresolved merge-conflict naming both identities: HEAD "RelaTesseract - graph as execution substrate" vs incoming "ReleTesseract — a universal and relational data store viewer… the natural counterpart to the Architesseract." — `/home/tim/repos/graph-editor/README.md:450-453`

## Key ideas worth mining
- **The Relational Primitive** (`docs/DESIGN_PRINCIPLES.md` principle 10, Tim's stated root): *"things only exist in meaning from the difference between things."* Registry types are defined by relationships to other types; token values resolve through relational chains; "no fallbacks" = "if a chain breaks, the relationship is broken." Relations are first-class.
- **Address-based, not message-based** (principle 8): everything has an address; agents coordinate through a *shared medium of addresses, relations and structures* rather than messages. Scheme: `graph://`, `supabase://`, `src://`, `data://`, `docs://`, `ci://`, `mcp-server://`. Tim: *"the common/shared medium you and your subagents share would be largely address and relations and structures."*
- **Graph as execution / coordination substrate** — entity types are execution-flavored (`PathPosition`, `ContextReveal`, `EntryPoint`, `EvaluationPosition`, `BatchAssignment`); relation types encode flow (`reveals_next`, `progresses_to`, `evaluates_via`, `leads_to_execution`, `loops_to_next`, `on_error`, `annotates`). The graph IS the workflow medium, not just visualization.
- **The memory-graph data model**: `{ graph_name, entities{ name → {type, cluster, observations[], metadata} }, relations[ {from, to, relationType, properties, metadata} ] }`. Observations are first-class node-attached facts; comments become real Comment entities.
- **Tesseract / dimensional duality** — "RelaTesseract" = relational hypercube, framed as *"the natural counterpart to the Architesseract"* — a paired Archi(structure) ↔ Rela(relation) framing within Tim's universal-laws metaphysic.
- **EditorAPI as named "surfaces"** (graph, navigation, registry, system, storage, compute, integration, ui, lifecycle, plugins, history, presentation, collaboration, editor) — one compositional shape exposed identically to UI, plugins, and MCP. Universal Composition / fractal reuse in practice.
- **JIT tiered tooling** — the live server fronts **234 tools** behind a 6-tool discovery facade (`rltsrct`, `execute_tool`, `query_tools`, `get_tool_schema`, `list_surfaces`, `help`): query→schema→execute, keeping a huge tool surface usable without context bloat. Directly relevant to the Company's own MCP surface design.

## What it connects to
Near sibling-DNA to the Company. **Composition:** surface-API exposed identically to UI and MCP mirrors the Company's typed compositional dataflow and one-control-surface ethos. **Relations first-class:** the "difference between things" framing matches the Company's relational-systems spine (`find_relations`). **Memory substrate:** this is the visual + agent-API layer over Project Vi memory graphs — overlaps with "graph IS the coordination plan" (the Company's graph-driven-coordination / fleet graphs). **Addressing:** the `scheme://` medium maps onto the Company's address/registry-accumulation model.

**Relation nuance:** `relation:resource` is right for the *editor/architecture as an idea-source*, but this repo ALSO hosts a **live, registered MCP** (`rltsrct`) referenced by Claude Code config (`/home/tim/.claude.json`; PID file `mcp-server/.rltsrct.pid`; `mcp-server/rltsrct.log` shows "Loaded 234 tools from catalog"). So it is simultaneously a prospecting resource AND an active operational dependency — recorded in `also_relation: dependency`.

## When / where
Created 2026-02-10 (`context/CONTEXT.md @created`); git last commit 2026-03-29; newest non-git mtime 2026-05-26 (a `universal-language-machine` worktree). Path `/home/tim/repos/graph-editor`, 423M, git remote `https://github.com/Concept-Vi/ReleTesseract` branch `main`. Read 6 of 19890.

## Notes / evidence
- Files read: `README.md`, `CLAUDE.md`, `package.json`, `mcp-server/README.md`, `context/CONTEXT.md` (head), `docs/DESIGN_PRINCIPLES.md` (excerpts), plus directory listings + targeted greps across `mcp-server/`, `graphs/`, `context/`, `docs/`.
- File count is misleading: 19890 total but the bulk is `.git/objects` (deep history + worktree) and `.discovery/runs/` JSON dumps. Hand-authored surface is far smaller.
- Secrets: none committed — only `.env.example` files (`./.env.example`, `./vi-sync-mcp-server/.env.example`); no `.env`/`.key`/`*secret*` outside node_modules.
- NOT read: the 266K `server.js` body, the 234-tool catalog, the 16K `index.html`, `src/` component tree, the 18 registries, `agent_workbench/`, `.discovery/` corpus.
- Flag: repo holds MULTIPLE MCP servers — at least `mcp-server/` (rltsrct), `vi-sync-mcp-server/`, and `tools/agent-dev-tracers/`. Only `mcp-server/` was characterized here.
