# Cognition Engine — Research Synthesis (what EXISTS — connect-to / don't-duplicate map)

> **What this is.** The evidence base under the Completion Criteria + Implementation Guide: what already exists in the system that this build must CONNECT to (never duplicate), which surfaces must be covered, and what primitives are wire-not-rebuild. **Written FIRST from current knowledge** (from building + dogfooding the engine), marked by confidence; **the parallel research wave + the reference-session file ADD TO and CORRECT it** — this is a living scaffold, not a finished map. Confidence tags: ✓known (verified by use/code this session) · ~recall (believe from building, verify) · ?open (research must answer).

---

## ROUND 1 — THE REGISTRIES (the composition material; registry-is-truth — the surface PROJECTS from these, never hardcodes)
*This is the heart of "no hardcoding / no duplication": every select/param/option the tools expose should come from one of these.*
- **RoleRegistry** ✓ — `runtime/roles.py`; file-discovered roles; `ROLE_FIELDS` (id·label·description·prompt_template·output_schema·input_addresses·op·trigger·model_binding·mode_scope·rules·render_hint·draws·verdict_rule·knobs·thinking·output·tools·context); accessors `.get`/`.roles`/`.cast_for_mode`. The create path writes here.
- **SkillRegistry / ContextRegistry** ✓ — `runtime/skills.py`; `skill://`/`context://`; `.read()` (named, NOT `.resolve`, for the floor scan); `.discover`. CREATE is direct now (#58).
- **The run-index** ✓ — `suite.py:list_runs/find_runs` projecting `op.run` events (#54). The discovery layer. (Caveat: reparses O(events) — efficiency is a criterion.)
- **MODEL_CAPABILITIES** ✓ — `ops/cli/capabilities.py`; models + `provides`/`requires` + gpu.py JOIN; `models_for_role` projects it. The op/thinking/tools selects SHOULD project from here (B5).
- **MODE_REGISTRY** ✓ — `suite.py:~1220`; the 13-axis dial (one source; MODE_SPECS/PART_GRAIN/ACTIVATION_ALLOCATION/MODES/MODE_DIRECTIVES derive). Carries `brain_config` (the loadout the swarm wants — C2).
- **NodeRegistry** ✓ — `runtime/registry.py`; node-types (the canvas/graph engine).
- **The closed grammars** ✓ — `runtime/rules.py`: `RULE_OPS` (the rule AST ops) + `DESTINATION_KINDS` (inject·chain·address·surface·lane). The rule-builder projects these.
- **SCHEMES** ✓ — `contracts/address.py`: run·cas·blob·vec·ui·code·skill·context. The input-select SHOULD project these (B3).
- **field_types** ✓ — `suite.py` (the /api/cognition/field_types path) — **HARDCODED flat scalars (str·int·float·bool·list[str]·list[int]). THE ONE select not backed by a registry → B2 makes it a TYPE REGISTRY (+ richer: nested/enum/optional).** The hardcoding to fix.
- **The projection pattern** ✓ — `contracts/cognition_info.py:build_cognition_info` — registry → JSON → FE/agent renders. THE pattern to mirror for every projection (object_info · cognition_info · the coming type/corpus projections). Don't invent a second projection style.
- ?open — the research must SWEEP for other hardcoded selects/lists beyond field_types (the registry-is-truth audit).

## ROUND 2 — THE SURFACES (cover ALL required — each capability reaches the faces that need it)
*"Cover all required surfaces" = for each engine capability, which of these must expose it.*
- **MCP agent face** ✓ — `mcp_face/server.py` (`@mcp.tool` → SUITE/engine). The AGENT composition surface. (15+ cognition tools live.)
- **/api (HTTP)** ✓ — `runtime/bridge.py` — what the FE calls; `/api/cognition/*` + the selects. The bridge between backend truth + the FE.
- **The FE (human face)** ~recall — `canvas/app/src/` regions: `Fleet.tsx` (sees models, reads /api/models), `Settings.tsx` (brain load-on-pick, voice-switch), `CognitionView.tsx` (the Pulse→River→Nodes view + cognition.* SSE). The human composition surface (#55/G2). Reflects-never-owns.
- **The CLI** ✓ — `ops/cli/app.py` (`company ...`: up/down/swap/ensure/gpu/suites). The operator/ops surface; the resource-manager face.
- **The contract:** ONE composition surface, projected from the registries, rendered on all three (MCP·FE·CLI) — reflects-never-owns. Declare once (Round 1 registries) → every face gets it. ?open — the research must enumerate, per criterion, which surfaces it must reach (the surface-coverage matrix).

## ROUND 3 — THE SYSTEMS TO CONNECT TO (no duplication — wire into these)
- **The resource-manager** ✓ — `ops/cli` + `gpu.py` (`ensure_resident`/`check_fit`/`plan_eviction`/`teardown`, the ONE manager). C (loadout/concurrency) wires HERE — `max_num_seqs` is in `ops/services.json`; swarm-mode's `brain_config` → ensure_resident provisions the loadout. DON'T build a second resource path.
- **The store + vector index** ✓ — `store/fs_store.py` (`put_content`/`set_ref`/`head`/`get_content`/`put_vector`/`get_vector`) + `store/vector_index.py` (`query_index` k-NN). D (corpus/embed) wires HERE — the corpus is a projection over the store + the vector index, NOT a new DB. (Note: fs_store is coherence's contended file — coordinate; prefer read-projection in suite.py/new-module over fs_store edits.)
- **The address resolver** ✓ — `runtime/cognition.py:resolve_address` (run·cas·skill·context; `<turn>` materialize; fail-loud on unknown). Every input wires through this. (Round F: the `://` classification bug is here.)
- **The fabric** ✓ — `fabric/client.py` (`complete`/`complete_embeddings`) + `fabric/transport.py` (openai + embeddings transports) + `fabric/config.py` (DEFAULT_BASE_URL=Ollama:11434, RESIDENT=:8000, embed=:8001). The model-call layer. Don't reinvent.
- **Governance / the floor** ✓ — the operator-only build-dispatch floor (`dispatch_decision`/`claude -p`) STAYS (Tim's standing call). Authoring is freed (#58); the floor scan is in `cognition_governance_acceptance` (COG_SOURCES + the AST scan). The boundary every cognition-reachable surface is held to.
- **The design system** ?open — for the FE human face (G2): where it lives, its components + tokens (the mandatory outward wave — don't build a bespoke FE). Research must map it.

## ROUND 4 — PRIMITIVES THAT EXIST (wire, do NOT rebuild)
- `run_swarm` (map) · `run_role` (the seam: input-axis + op-axis) · `run_items` (1×N map) · `run_reduce` (cross-unit join: role|rule|cluster) · `run_jury` (draws-reduce) ✓ — the engine quartet. The corpus map/reduce IS these.
- `put_vector`/`query_index` + `op=embed` ✓ — the vector store + embedding. D (embed-on-write, retrieve-as-input, cluster) WIRES these — every primitive D needs already exists; D is the wiring, not new plumbing.
- `op.run` run-index ✓ — discovery (#54).
- `ensure_resident` ✓ — the gated loadout actuator (#50). C wires this.
- `resolve_address` ✓ — input resolution. `create_role`/`create_skill`/`create_context` ✓ — direct authoring (#58).

## THE DON'T-DUPLICATE / DON'T-HARDCODE LEDGER (the bar Tim set)
- field_types is the ONE hardcoded select → a type registry (B2). Sweep for others (?open).
- The corpus is a PROJECTION over the store + vector-index → NOT a new DB (D).
- The loadout wires the ONE resource-manager → NOT a second GPU path (C).
- Every select PROJECTS from a Round-1 registry → NOT a hardcoded list (B).
- The composition surface is ONE thing rendered on three faces → NOT three parallel surfaces (G).
- The corpus map/reduce IS the engine quartet → NOT a parallel pipeline (D).

## REVIEW HISTORY
- Round 0 (this doc, from current knowledge): the scaffold above. **Next: the parallel research wave + the reference-session file enrich/correct each ?open + verify each ~recall.**
