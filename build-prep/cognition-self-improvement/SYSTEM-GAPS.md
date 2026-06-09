# MCP / System Gaps — the running ⑫ backlog (for next workflows)

> Things the engine/MCP needs that surfaced BY USE. Each is a buildable seam for a future workflow (the engine-improves-engine front-end reads this). Status: 🔴 open · 🟡 partial · ✅ closed. Tim's standing law: first-use friction is the input, not a failure — note it here as found.

## Surfaced 2026-06-09 (the registry-coverage audit test — "use the models")
- 🔴 **G1 · Ephemeral/draft-role run path on the MCP face.** `run_role`/`run_items` take a registered role id (string). A one-off bounded classification (e.g. "classify these 39 candidates once") forces either `create_role` (commits a throwaway role → registry pollution + a `.git/index.lock` race with any concurrent commit) or dropping below the MCP. NEED: `run_role(draft_spec={...})` / `run_items(draft_role={...})` — fire an inline role spec, validated + run, NEVER written/committed. (The internal `_resolve_role` reportedly accepts a dict draft; the MCP wrapper types `role: str` and doesn't expose it.) This is the grunt-offload reflex's (⑪) missing primitive. [testing the draft path now]
- 🔴 **G2 · New role not live in the running MCP server until rediscover.** A role file written to `roles/` is only seen by the running bridge/MCP after `create_role`'s in-process `_rediscover_roles` (or a server restart). So you can't "write a role file + immediately run_items it" through the live server without committing via create_role. Relates to G1 (the draft path sidesteps this entirely).

## Surfaced earlier (the compositions grounding — COMPOSITIONS.md / WORKFLOW-ARCHITECTURE.md seam backlog)
- 🔴 **G3 · Cascade multi-variable prompt substitution.** A saved cascade decl threads ONE `inputs` value + fixed per-step roles; richer per-step `${var}` interpolation into prompt_templates is unbuilt.
- 🔴 **G4 · The `retrieve`/`similarity` cascade ops.** No engine primitive — retrieve runs inline + feeds `inputs`. Blocks the corpus-RAG cascades (①/④/⑨) from being fully save_cascade-able.
- 🔴 **G5 · Role-scoped capability gating.** B5 projects op/thinking/tools against the BRAIN, not a role's bound model. A role bound to a non-brain model gets the wrong capability set.
- 🔴 **G6 · `suite.py:capability_providers()` live-bind resident-only.** CATALOG (C2.5) widened the model DATA; the live-provider set the swarm binds against is still resident-4b-only. The other half of the catalog widening.
- 🟡 **G7 · Embedder-resident handling under contention.** `ensure_resident(op=embed)` proven on a stub; unproven BY USE under real swap on the contended card (the V-A RG10 cluster-reduce is the first real test). No steady state yet → the swap path matters.

## How a future workflow consumes this
⑫ (engine-improves-engine) reads this file → scouts each gap against the code → drafts a buildable lane-cut → I review + dispatch. Closed gaps move to ✅ with the commit sha.

## Surfaced 2026-06-09 (running the unified V-A workflow)
- 🔴 **G8 · The workflow Commit-phase mega-agent times out (API stream-idle).** One agent doing gate + 6 commits + AGENTS.md + records is too big — it died on the stream-idle timeout TWICE (the build pieces stranded, adopted manually). FIX: split the Commit phase (one agent per piece, or a pipeline), OR make the runner (me) commit directly rather than via a sub-agent. Workflow-pattern lesson: keep agent turns bounded; a long serial commit agent is fragile. The build-parallel/commit-serial split should be commit-per-piece, not commit-all-in-one.
