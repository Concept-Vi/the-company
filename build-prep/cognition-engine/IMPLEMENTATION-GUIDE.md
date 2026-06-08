# Cognition Engine — Implementation Guide (HOW, connecting to what exists)

> **What this is.** How to make each Completion-Criteria group TRUE, built ON the existing systems (Research Synthesis), with file territories + the parallel-lane cut. **Written FIRST from current knowledge; research + the reference-session file ADD TO it.** The standing bar (Tim): intuitive · versatile · operationally-valuable · CONNECTED · zero hardcoding · zero duplication · all required surfaces covered.

## THE GOVERNING PRINCIPLES (apply to every group)
1. **Project, don't hardcode** — every select/option/spec the tools expose comes from a Round-1 registry (Synthesis). The fix for a hardcoded list is "project it from its registry," not "add to the list."
2. **Wire, don't rebuild** — the primitives exist (store · vector_index · op=embed · run_reduce · ensure_resident · resolve_address · the registries). Most makes are WIRING, plus two net-new (the type registry, chunk-and-compose).
3. **One surface, three faces** — the composition surface is projected from the registries and rendered on MCP + /api+FE + CLI. Declare once; cover all faces. Reflects-never-owns.
4. **Each change preserves the rest** — name what still works (the swarm/voice/listening path, the floor, the existing tools) through every edit. Behaviour-preserving.
5. **Verify by use, honest status, form is half** — the criteria bar; a design-critic for any surface; nothing green-painted.

---

## GROUP A — Direct authoring  · STATUS: ✅ built (#58), verify-only
Built: `create_role`/`create_skill`/`create_context` apply live (no approval), full schema, correctness-gate kept, build-dispatch floor kept. CONNECT: RoleRegistry/SkillRegistry/ContextRegistry. No build — re-verify by use only.

## GROUP B — Composition surface from registries (the keystone) · LANES: NEWMOD + SUITE + SURFACE
**Principle:** the tools are a generic renderer over the registries (mirror `build_cognition_info`). A new skill/model/type appears everywhere with no tool edit. **The only hardcoded select is `field_types`.**
- **B2 (NET-NEW, lands first — the contract):** a **type registry** (NEW module `runtime/types_registry.py` OR `contracts/field_types.py`, mirroring the registry pattern) declaring the output-field types — and RICHER: nested objects, list[dict], enum, optional, defaults. `field_types` projects from it. This is the one genuinely-new piece + where richer schemas live.
- **B1/B3/B5 (wire selects → registries):** in `suite.py`, change `field_types`→project the type registry; `available_inputs`(cognition_inputs)→project roles+skills+contexts+the run-index+context-vars+SCHEMES (today omits skill://+context://); the op/thinking/tools selects→project MODEL_CAPABILITIES.
- **B4 (create-spec discoverable+validating):** a `create_spec_schema()` projecting `ROLE_FIELDS` (field set + per-field types/required) + fail-loud validation feedback on create.
- **Files:** NEW `types_registry` · MODIFY `suite.py` (the selects) · MODIFY `mcp_face/server.py` (expose the richer selects + create-spec). CONNECT: all Round-1 registries + the cognition_info projection pattern.
- **Do:** project; mirror cognition_info. **Don't:** add a parallel select system; hardcode any list.
- **Cross-lane order:** B2 (the type registry) lands first → suite.py + mcp_face consume it.

## GROUP C — Loadout / real ceiling · LANES: CONFIG + SUITE
**Principle:** swarm concurrency is mode-driven, provisioned by the resource-manager — not a static config. FOUND: `max_num_seqs:16−R:2=14`; KV supports 44; other services already run 32.
- **C1:** set chat-4b swarm `max_num_seqs`→34 in `ops/services.json` (KV supports it; proven-safe — other services use 32).
- **C2:** swarm-mode's `brain_config` (MODE_REGISTRY) → `ensure_resident` provisions the loadout; the SlotBudget already reads the live config (registry-is-truth — the VALUE was wrong-regime). Wire B(brain_config) + #50(ensure_resident).
- **C3:** re-run the whole-repo map at the swarm loadout; MEASURE the realized knee ≈ 32 + the throughput gain (proven-by-measurement).
- **Files:** MODIFY `ops/services.json` · MODIFY `suite.py` (mode→loadout) · REUSE `ensure_resident`. CONNECT: the resource-manager.
- **Do:** mode-driven, measured, gated-evict. **Don't:** hardcode the number; blind-stomp another session's GPU.

## GROUP D — Corpus / output sink · LANES: NEWMOD + ENGINE + SUITE + SURFACE
**Principle:** map output must BECOME a durable, addressed, embeddable, queryable artifact — a PROJECTION over the store, not a new DB. Every primitive exists; D is wiring + purpose.
- **D1 corpus-record:** NEW `runtime/corpus.py` — a record `{source_address, output, kind, model, ts}` persisted via the store (cas://) + indexed (the run-index pattern). 
- **D2 embed-on-write:** on corpus-write → `op=embed` → `put_vector` (REUSE). 
- **D3 retrieve-as-input:** a `retrieve` over `query_index` → `context://` a role reads (RAG over the corpus; REUSE query_index). 
- **D4 cluster:** `run_reduce(cluster)` over the corpus = built-twice discovery (REUSE). 
- **D6 purposeful chains:** a saved chain (map→reduce→artifact toward a goal), re-runnable — the corpus-chain (see build-prep/coherence/CORPUS-CHAIN.md).
- **Files:** NEW `runtime/corpus.py` · MODIFY `cognition.py` (minimal emit/write hook) · MODIFY `suite.py` (corpus methods/projection) · MODIFY `mcp_face` (corpus tools). CONNECT: store + vector_index + op=embed + run_reduce. **Don't edit `fs_store.py` (coherence's)** — read-project / use existing store methods.
- **Do:** projection over the store; reuse the engine quartet. **Don't:** a parallel DB/pipeline.

## GROUP E — Run discovery + chaining · LANES: SUITE + ENGINE + SURFACE
- **E2 efficient index:** the run-index must not reparse O(events) — an incremental/cached index (still over the op.run event log, registry-is-truth). MODIFY `suite.py`.
- **E3 chain handle:** a "feed-last-output" convenience (the response already carries run://address; add a handle so chaining isn't manual copy). 
- **E4 chain persistence + output-destination:** save a chain config (re-runnable); a run-output `destination` param (route to a named address/lane — REUSE DESTINATION_KINDS). MODIFY `cognition.py` (the destination param) + `suite.py` (save/re-run).
- CONNECT: the run-index + the store + DESTINATION_KINDS.

## GROUP F — Robustness at scale · LANE: ENGINE
- **F1 :// classification:** in `run_items._resolve_unit` (+ resolve_address) — a unit is an address only if it **starts with a registered scheme** (`scheme(leading-token) ∈ SCHEMES`), not merely contains "://". CONNECT: SCHEMES.
- **F2 batch per-unit resilience:** `run_items` — a unit that errors → `failed`/`skipped`; the good units' outputs STILL return (don't re-raise the whole batch). Mirror run_swarm's per-unit capture but for a MAP don't discard the batch.
- **F3 chunk-and-compose (NET-NEW):** files > model context → split→map→compose (the corpus-chain tier). 
- **F4 error clarity:** context-overflow → "context length exceeded"; reduce role-mismatch → a contract error not bare KeyError.
- **Files:** MODIFY `cognition.py` (run_items + resolve_address). **Do first** (cheapest, unblocks real corpus use). **Don't:** break the existing run_items callers (behaviour-preserving for utterance-only/literal units).

## GROUP G — Two faces, one surface · LANE: FE (the FE session's territory — co-design)
- **G1** ✅ MCP. **G2** the FE human face (#55) — Fleet/Settings/CognitionView see+do resident models/GPU/runs + create/run/configure/re-run, reading the SAME registries (Round-1) the MCP reads. **G3** one surface (depends on B). 
- **My side:** serve the registries/projections via /api (reflects-never-owns); the FE session builds the controls. CONNECT: the design system (?open — the mandatory outward research wave before any FE).

---

## THE PARALLEL-LANE CUT (file-disjoint → fan in parallel; each hot file ONE owner)
```
LANE-ENGINE   (runtime/cognition.py, sole owner)   → F1·F2·F3·F4 · D-emit-hook · E4-destination
LANE-SUITE    (runtime/suite.py, sole owner)       → B-selects · B4 · C2-loadout · D-corpus-methods · E2-index · E4-save
LANE-SURFACE  (mcp_face/server.py, sole owner)     → B/D/E MCP tools (the richer selects + corpus + chain tools)
LANE-NEWMOD   (NEW files, fully disjoint)          → B2 type-registry · D1 runtime/corpus.py + retrieve
LANE-CONFIG   (ops/services.json + ops/cli)        → C1 max_num_seqs 16→34
LANE-FE       (canvas/app — co-design w/ FE session)→ G2 (after B + the outward design research)
```
**Parallel-safe** because each hot file has ONE owner-lane. **Cross-lane ordering:** LANE-NEWMOD's contracts (type-registry API, corpus API) land FIRST → SUITE/SURFACE consume them. Within a lane, bundle all that file's criteria into one pass (not N windows). Coordinate the shared files (suite.py/cognition.py/mcp_face) with the other two sessions via the CLAIMS board — but right now they're blocked-on-me, so contention is mostly internal.

## VERIFICATION (per lane)
Batch: one suite-run per lane-completion (governance/floor + the lane's suites + drift). By-use the lane's criteria. Calibrate depth: FULL by-use for safety/floor/ceiling (A4·C·F); lighter for additive. Design-critic for any FE surface (G). Commit my files only, by path, gate green first.

## OPEN (research + the reference-session file enrich these)
- ?the design system (location/components/tokens) for G2 — the outward wave.
- ?the hardcoding sweep beyond field_types.
- ?the surface-coverage matrix (per criterion × MCP/FE/CLI).
- ?the corpus-chain saved-chain shape (declared type) — cross-ref CORPUS-CHAIN.md.
- ?what the reference-session learned directly-using concurrent runs (Tim's file).

---
## LANE-CUT UPDATE (from the surface research) — add LANE-BRIDGE
The FE is reflects-never-owns (verified) → it can only render what `/api` serves, and `/api` does NOT serve run/create/embed/list_runs. So the lane-cut needs a SIXTH lane:
```
LANE-BRIDGE (runtime/bridge.py, sole owner) → the /api routes the human face needs:
   /api/cognition/{run_role,run_items,run_reduce,embed} · the DIRECT create routes · list_runs/find_runs
   · /api/cognition/corpus (NOT /api/corpus — that's the mockup gallery, NAME-COLLISION)
```
LANE-BRIDGE is a MY-SIDE prerequisite for G2 (the FE/#55). It's file-disjoint (bridge.py, sole owner) → parallel with ENGINE/SUITE/SURFACE/NEWMOD/CONFIG.

## CORRECTIONS folded (from the research)
- **B2 de-risked:** `field_types` IS projected; `output_schema` is already real Pydantic (nested/enum/optional work). Richer types = new rows in `authoring.py:48` + a recursive renderer (nested→sub-BaseModel·enum→Literal·optional→T|None·list[dict]→list[SubModel]), import-gated. NOT a Pydantic change, NOT a new registry — widen the grammar + renderer.
- **GROUP D de-risked:** almost all WIRING. Only D1 (thin `runtime/corpus.py`) is net-new. The saved-chain validator/registry ALREADY EXISTS (`runtime/coherence_actions.py:build_action`/`ActionRegistry`) — D6 wires the runner to it, doesn't build it. CORPUS-CHAIN.md is stale (ignore its "net-new reduce/seam" claims). NEVER edit fs_store.py (coherence's).
- **B-discoverability fixes (registry research):** cognition_inputs += skill://·context://·SCHEMES · op-select + capability-check at create (B5) · dedup run_reduce-mode (docstring vs gate) · project _REDUCE_RULES to /api.
