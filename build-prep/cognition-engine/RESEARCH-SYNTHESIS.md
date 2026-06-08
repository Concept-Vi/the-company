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

---
# ROUND 1 ENRICHMENT — the parallel research wave (2026-06-09, 4 read-only agents)
*Resolves the ?open + corrects the ~recall. Reports: .build/prep-{registry,surface,design,corpus}.report.json.*

## REGISTRY audit (prep-registry) — CORRECTION + the real gaps
- **CORRECTION to ROUND 1:** `field_types` is NOT "the one un-projected/hardcoded select" — it IS projected (MCP + /api/cognition/field_types). The real issue: its **SET is wrongly-CLOSED (flat scalars)**. Distinguish "closed grammar, correct" (RULE_OPS/SCHEMES/op) from "closed set, too narrow" (FIELD_TYPES). So B2 isn't "make it a registry" — it's **widen the type grammar** (rows in `authoring.py:48` + a recursive renderer, lines 115-151).
- **`output_schema` is ALREADY real Pydantic** — nested/enum/optional/list[dict]/defaults ALL work today. Richer types = new FIELD_TYPES rows + a richer field-spec grammar + a recursive renderer (nested→sub-BaseModel · enum→Literal · optional→T|None · list[dict]→list[SubModel]), import-gated. **NOT a Pydantic change.** (Big de-risk for B2.)
- **The real registry gaps (mostly DISCOVERABILITY, two duplication):** (1) `available_inputs`/cognition_inputs OMITS skill://·context://·SCHEMES (B3). (2) `op` enum gated at roles.py:173, no projecting select, not capability-checked (B5). (3) `thinking`/`tools` on create_role NOT validated vs MODEL_CAPABILITIES.provides (B5 unbuilt at create). (4) `run_reduce` mode re-typed in the MCP docstring (two sources — dedup). (5) `_REDUCE_RULES` (count|concat|first) lives only in server.py:371, invisible to /api/FE (project it). `models_for_role` is fail-SOFT (not pure).
- **Exemplars to mirror:** MODE_REGISTRY (gold standard one-source) · the cognition_info projection · MODEL_KNOBS→/api/knobs (live-probes the tools knob — add to ROUND 1).

## SURFACE matrix (prep-surface) — the bridge is the G2 bottleneck + a name-collision
- **`fe_reads_backend` = reflects-never-owns, VERIFIED by code** (registryStore inits {} + populates only from backend; no client-side hardcoded list). ✓ upgraded from ~recall.
- **THE LANE-CUT GAP:** because the FE only renders what /api serves, and **/api does NOT serve run_role/run_items/run_reduce/embed/DIRECT-create/list_runs**, a **`runtime/bridge.py` /api-route expansion is a MY-SIDE prerequisite for G2** — it needs its OWN lane (the guide's LANE-SURFACE owned only mcp_face). → **add LANE-BRIDGE.**
- **NAME COLLISION:** `/api/corpus` + the FE "corpus" vocabulary = the **mockup/design gallery**, NOT the Group-D cognition corpus. D1 MUST use `/api/cognition/corpus` (or it clobbers the gallery). (Don't-duplicate ledger += this.)
- create is an ASYMMETRY: MCP=direct+propose · /api=role-propose-ONLY (no skill/context author route) · FE=nothing. The loadout (C) is the BEST-covered (all 4 faces) — confirms the one-resource-manager principle.

## DESIGN system (prep-design) — ROUND 3 ?open RESOLVED: usable-now, no bespoke FE permitted
- **Tokens (source of truth):** `design/_system/tokens.json` → `emit.py` → `design/design-system.css` (GENERATED, never hand-edit); app imports it in main.tsx; `app.css` legacy vars are ALIASES. Theme **FINAL (Tim 2026-06-07)** — gold-primary; rule: TWO-VIVID + ONE-MUTED status colour (lifecycle reads apart by sight).
- **Components:** `canvas/app/src/components/kit.tsx` (Surface·SectionHead·LaneHead·Badge·EmptyState) + `StudioKit.tsx` (Card/Rail/Stage/Composer/RhmPanel, mounted as regions/Review.tsx) — the composition-workspace precedent.
- **The G2 pattern (a new surface MUST follow):** import kit → SectionHead/LaneHead → every row a `Surface` card with tone + data-ui-ref (never a bare line) → state-by-Badge-colour → loud EmptyState → data from a registry via /api (reflects-never-owns) → tokens only (zero raw hex/px). **Closest exemplar: `Fleet.tsx` (the live model layer as kit-cards) — G2 EXTENDS it (add GPU/runs), don't parallel.** `Settings.tsx` = the configure/switch precedent; `CognitionView.tsx` = legit bespoke-SVG for a flow-not-a-list.
- **The FORM gate:** `python3 design/_system/check.py --target canvas/app/src --fail-on` (off-token/bespoke → build fails) + a separate design-critic + the operator. The implementer cannot self-grade FORM.

## CORPUS pieces (prep-corpus) — GROUP D is almost entirely WIRING; the saved-chain validator EXISTS
- **BUILT (wire, don't rebuild):** the store sink (put_content/get_content·set_ref/head/ref_history·put_vector/get_vector/index_corpus·append_event) · `vector_index.py` (build_index incremental + query_index k-NN, dim=1024/BGE-M3, fail-loud) · op=embed (full, MCP-exposed, ensure-gated) · **run_reduce(cluster) FULLY built** (the built-twice primitive) · run_items · **the saved-chain type: `runtime/coherence_actions.py` `build_action(decl,*,models)` IS the one-door validator** (decl={name,steps:[{op,model}],output_schema}) + `ActionRegistry` (saved type + persistence + save_calibration) + `build_coherence_info` projection.
- **Net-new vs wiring (D1-D6):** ONLY **D1** is meaningfully net-new (thin `runtime/corpus.py` tying put_content+append_event+put_vector + a corpus.write event-kind). D2/D3 = pure wiring (mirror `suite._retrieve_for_consult_semantic` for D3). D4 = built (needs live embedder). D5 = wiring + a small invalidation policy (content_hash + index_staleness give it). D6 = wire the runner to fire a saved Action (validator/registry built) — cognition↔coherence co-design.
- **CORPUS-CHAIN.md is STALE** (its "reduce doesn't exist / the seam is net-new / build_chain needed" claims are contradicted by current code — the engine generalization already happened). The cognition-engine synthesis (this doc) is correct; don't over-correct it. fs_store.py MUST NOT be edited (coherence-contended + Supabase-portability seam).
- **Flags:** op.run seq not cross-process-unique (matters if a corpus index keys on seq) · list_runs O(events) reparse (E2 — any corpus projection inherits) · dim consistency across embed paths = the one silent-correctness hazard (fails loud at cosine — correct).

## REVIEW HISTORY
- Round 0: the scaffold (current knowledge). Round 1: this enrichment (4 parallel research waves) — design-system RESOLVED · field_types reframed (projected-but-narrow, Pydantic-ready) · LANE-BRIDGE added · corpus = wiring + saved-chain-exists · the /api/cognition/corpus name-collision. **Next: the reference-session file (Tim's path) + any contradiction-resolution round.**

---
# ROUND 2 ENRICHMENT — run-1 (the by-hand prototype) + the MCP-tool inspection (the actual connection map)
## run-1 (~/wizard-run-1/) — the prototype of the corpus/discovery pillar (read WHOLE: field-report+methodology+fleet.py+capture2.py+db.py+registries)
- **The connections (the spine):** run_role/run_items = the per-file MAP · run_reduce(cluster) = corroboration · op=embed/put_vector/query_index = multi-space embedding · **the coherence finding/disposition store = THE MARKS layer (same shape: target/mark_type/value/confidence/source_pass/evidence/status)** · **coherence_actions.ActionRegistry/build_action = the saved-cascade validator (EXISTS)** · MODEL_CAPABILITIES = the model-tier registry (+cloud rows) · the run-index (#54) = the runs table.
- **run-1's actual code:** `capture2.py:build_schema()` builds ONE json_schema from `projections.json` → run_role renders all lenses in one call → splits to the projections table. `fleet.py:local4b(json_schema=,rep_penalty=)` (finish=length→retry-bigger), `kimi` (reasoning-field+headroom+multi-turn), `embed`, `map_local/map_kimi`. `lift.py`+`markdown_lifters.json` = registry-driven code projections. `db.py` = files/projections/links/blocks/marks/call_log/runs. Resume-safe single-writer per-file commit.
- **The generation-pathology (the engine WILL hit it):** greedy temp0 + grammar-constrained long arrays → degenerate repetition loop (~20%; input-size does NOT predict; cure = repetition_penalty ladder, frequency_penalty WRONG; found by READING raw output — "content too big" is the LAST hypothesis). My whole-repo test dodged it with 700-char heads.
- **The method (the dynamic law):** patterned-visibility (run→look→mark→next, operator+system, NOT scripted) · match-question-to-LEVEL (map/reduce/system) · render-not-judge · corroboration positive-only/semantic/cross-session · fingerprint-subtraction (AI-tics catalogued+extensible) · no-projection-privileged · EVERYTHING a registry (projections/prompts/mark-types/AI-tics/relation-types/lifters/forms/generation-policies). The corpus reframe: scattered AI-echoes, gold=MEANING-not-surface, reconstruct-intent→confirm→design-fresh.
## the MCP-tool inspection (.build/mcp-tool-inspection.report.json) — the actual map
- **41 tools, two engines on ONE shared spine** (store/address/event-log/governance + sibling serializers object_info↔cognition_info) — connected, NOT duplicated. Nothing stale, nothing disconnected (static trace).
- **The authoring split (grounded):** node-TYPE = `guard('code_build')` CONFIRM (writes a code module); role/skill/context = guard-free correctness-gate+git-revert (#58). → the principled line: declarative-direct / executable-code-gated.
- **B violations (registry-is-truth):** _REDUCE_RULES (server.py:372 literal) · api_verbs (suite.py:827 hand-typed) · ENGINE_RUN_OPS/PROTECTED_ROLES. capabilities IS the umbrella (embeds cognition_capabilities). Redundant: get_results⊂get_state, find_runs⊂list_runs, list_surfaced⊂inbox. Inconsistent: delete_node-direct vs delete_role-surfaces; guard-wrapping uneven.
