# recollection — IMPLEMENTATION GUIDE

> HOW to build each thing the Completion Criteria require. Per component: **Principle** (why) · **Schema/Spec** (the concrete shape) · **Files** (KEEP/MODIFY/REPLACE/NEW/HARVEST with paths) · **Model-slot bindings** (registry, never literals) · **Do's & Don'ts** (with *because*) · **Preserves** (what keeps working).
> Tense: "IS" = exists in the clone today; "WILL BE" = to build. Evidence base: `RESEARCH_SYNTHESIS.md`. Truth-table: `COMPLETION_CRITERIA.md`. Open calls: `OPEN-DECISIONS.md` (do not hard-build past an unanswered one — leave the seam).

---

## 0. Governing principles (apply to every component)

- **Registry-is-truth / no-hardcoding.** Every unit-type, lens, judge-type, query-tool, distill-layer, capture-source, return-condition is a **registry entry** (a dropped file/row), never a literal in code. Values are authored *from* the registry, never invented. This is what makes "full lens-set, no winner, dim-per-space" enforceable. *Because:* the whole system must keep growing after the first build without code changes (Tim's "so they can be grown").
- **Extraction vs judgment.** The fan-out swarm (resident 4B, ~120 concurrent) **extracts** observations; a central judge layer **decides** relationally. Workers never decide. *Because:* Tim corrected this exact error before; it's the spine of P3–P5.
- **The bootstrap (build-uses-itself).** The build's first capability — capture + retrieval over Tim's history — is *used by the build process* to recover decisions (the standing "subagents-through-memory-first" directive becomes a recollection query the moment recollection can answer one). Each phase that comes online is turned ON for the next phase's work. *Because:* it's the cheapest verification (the thing works iff the build can use it) and it's Tim's stated intent ("the first connection gets used in the process").
- **Conversation is source of truth; code is a lossy AI projection.** No project is complete/consistent; duplicates/gaps/divergence are GUARANTEED and are SIGNAL (the merge/unify value), never noise. The code→conversation provenance link is the key hop. *Because:* nothing was ever hand-reviewed.
- **No-fiction-about-Tim (the asymmetry law).** The memory must NEVER misremember Tim — the worst available corruption. Principle records are no-fiction: extract only what's in the source; uncertain → abstain/flag, never fabricate. *Because:* every agent reads Tim through this; a wrong principle propagates everywhere.
- **Verify by USE.** A criterion is green only when demonstrated by an actual recall/build run, not by code-reading. *Because:* code that looks right fails on timing/state/dim mismatch.
- **Scout-before/while-building (fabric norm, Tim 2026-06-15).** At the moment the contract is clear but the code isn't written yet (the cheapest point to change course), fan out cheap read-only sub-agents (sonnet, or haiku for pure file-reporting) to survey what ALREADY EXISTS — surfaces things to REUSE, to UPGRADE, and confirms no parallel system. *Because:* no single session holds all the context; scouting is the operational form of reuse-don't-parallel. **Beat-3 (provenance graph) leads with a scout** of: ~/recollection's existing relation/link code, the Company's `find_relations`/relation_types, CI's `indexed_artifacts`/`artifact_provenance` schema, substrate-mcp's link/state code — build ON them, never hand-roll. (This is how Phase-A/seam already ran; now a standing norm.)
- **No-versioning / commit-to-main (in recollection's own repo) / fail-loud (no silent fallbacks).**

## 1. Base & the data model

**Principle.** recollection is the v1.4.2 clone refit into a standalone sibling plugin with its own data dir, written **portable-by-field** so absorption into the Company is a backend re-point, not a rewrite. The atom tables already match the Company's schema-additive law.

**Schema (SQLite + sqlite-vec; portable-by-field).** Build ON the existing `exchanges` + `tool_calls` tables; ADD:
- `atoms` (the lowest unit = event): `id · type(message|tool_call|result) · session_id · project · ts · exchange_ref · raw_ref(line range) · cwd`. Raw bedrock; nothing lost.
- `units` (typed registry instances): `id · unit_type(FK→unit_type registry) · scale · source_address(exchange://<sid>/<i>) · ts_source · lineage(session/round/project, fail-loud) · content(distilled) · raw_ref`.
- `unit_type` registry: `name · scale · extraction_prompt_ref · embed_lenses[] · gated(bool)` — NEW types are rows, not code.
- `links` (the provenance/relation graph): `from · to · edge_type(FK) · direction · inverse · grade(mechanical|semantic) · confidence · ts`. Edge types are directional-with-inverse (precedes/succeeds, contains/is-contained-by, produced-by/produces, describes/described-by).
- `fingerprints` (multi-coordinate): `unit_id · space(lens name) · model · dim · vector` — **one row per (unit, lens)**; `vec://<source>#space=<lens>` addressing. Demote the hardcoded `vec_exchanges FLOAT[384]` to ONE such space, not the schema.
- `verdicts` (typed, multiple per result): `target · verdict_type · value · basis · confidence · ts`.
- `candidates` (P5 principle staging): principle records awaiting ratification.

**Address grammar.** Canonical = `exchange://<sid>/<i>` + `cwd→project` containment (mechanical, free). Geometric lattice (radius/angle/scale) = a render/health projection IF D-1 lands that way. **Leave the seam: address as an interface, one resolver now, pluggable.**

**Files.** MODIFY `src/db.ts` (ADD the above via additive ALTER — KEEP the migration pattern), `src/paths.ts`→`~/.recollection` + `RECOLLECTION_*` env, `.claude-plugin/plugin.json`+`package.json` (rename). KEEP `file-lock.ts`, the reentrancy guard.
**Preserves:** `exchanges`/`tool_calls` capture + `read`/`show.ts` render keep working unchanged; the additive migration means old rows are untouched.

## 2. Capture

**Principle.** Total coverage is the precondition for both pillars and the triangulation method — blind spots are fatal. One unified, pluggable, registry-driven source path.

**Spec.** Sources = a registry (`capture_source` rows: claude-code · voice(STT) · exports · …). Claude Code source: sweep `~/.claude/projects/**/*.jsonl` INCLUDING `agent-*.jsonl` sidechains (the work). Two timings: **backfill** (one pass over the ~13,270-conv existing archive — the head-start) + **live** (Stop/tool hooks → current within a session, enables P8). Incremental via the existing high-water-mark.
**Files.** MODIFY `src/sync.ts` + `src/indexer.ts` (pluggable source registry; STOP excluding sidechains; backfill driver). KEEP `summary-sentinel.ts`, mtime-gating, atomic copy.
**Do/Don't.** DO capture sidechains *because* that's where Tim's work happens (the existing lanes skip them → catastrophic for him). DON'T build a second parallel ingest lane *because* there are already three (episodic hook, Supabase sync, lobe-importer) — unify into this one.
**Preserves:** existing incremental capture + resume.

## 3. Distill

**Principle.** Manufacture memories from raw: read each piece, write what it WAS. Three layers, all registry-grown. Workers extract, central judge decides (extraction-vs-judgment). Principles never auto-commit (no-fiction-about-Tim).

**Spec.** L1 summary (per-conv, swarm-backfill all 13,270). L2 structured extraction (per piece → typed records: decision/rationale/correction/error/bug-fix/needs-tim/frustration/pattern + principle/concept-definition/what-built; types are `unit_type` registry rows). L3 rollups (conv→session→project-arc→settled-view; what survives rollup = a principle). Triggers (registry, extensible): backfill · live · deep-pass(8B + dream-phase) · **interactive (directed/co modes)**. **Principle ratification gate (D-2 model):** L3 principle candidates → `candidates` staging → a *powerful* judge (session model via MCP, or local big model) proposes → Tim refines → commit. Non-principle records self-assemble (no gate).
**Files.** REPLACE `src/summarizer.ts` (cloud Agent SDK → local resident-4B distill via fabric — *because* it removes the cloud dep AND the SessionStart recursion source). NEW `src/distill/` (map = run_items-shaped; reduce = cluster/role). HARVEST CI's turn-context builder (`~/repos/Supabase`).
**Model-slots.** extractor = resident 4B (≥120 concurrent, json+chat); rollup-reduce = cluster (embedder window) + role-synthesis; central judge/ratifier = D-2 slot.
**Do/Don't.** DON'T let workers judge/decide *because* extraction-vs-judgment. DON'T fabricate a principle to fill a slot *because* no-fiction-about-Tim — empty is `""`, uncertain abstains.

## 4. Embed / Place (the lenses)

**Principle.** Multi-coordinate: each unit gets many fingerprints, one per lens; the query picks the space. Every lens is a registry slot — **no model is privileged (bge-m3 zero priority)**; dim is per-space, not a constant.
**Spec / loadout (D-5 default).** Lenses (registry): steerable-dense (qwen3-embed, instruction-directed — the multi-space-by-question trick; steering vocab MINED from corpus) · sparse (exact terms) · code (nomic-code, in-store, `--pooling last`+query-prefix or it fails SILENTLY) · code-grep (LateOn/ColGrep — OWN multi-vector index, NOT the single-column store) · visual (VL pair) · context-aware (project/long units) · compression (archive economy) · CPU-bulk · 8B deep-pass (solo). Everyday co-resident ≈ ~10G; VL swapped in for images; 8B solo. **Re-embed migration:** old 384-dim vectors are NOT reusable; same model/settings for corpus AND queries (else garbage).
**Files.** REPLACE `src/embeddings.ts` (in-process ONNX → fabric registry-driven multi-lens, no hardcoded model/dim). **Interim served stack (CONFIRMED by lead, wire-3 — build against this exactly; env-configurable `EMBED_URL`/`RERANK_URL` so absorption is a re-point):** embed = `POST http://127.0.0.1:8007/v1/embeddings`, documents-mode `{"documents":[[chunk,...]]}` for contextual chunks (per-chunk late-chunking, dim **2560**, INT8, compare by **COSINE**); flat `{"input":[str]}` for single-chunk. rerank/proofreader = `POST http://127.0.0.1:8008/rerank {query, candidates, top_n}` → `{ranking:[{item,text,rerank_score,orig_rank,rank}]}` (jina-v3, CPU). GOLDEN RULE: index + query in the SAME space (pplx-4b interim, D-5). The eventual full lens-set is recollection's OUTER embedder design.
**Do/Don't.** DON'T hardcode a model or dim anywhere *because* registry-is-truth + bge-zero-priority. DON'T mix embed-model between corpus and query *because* spaces must match.

## 5. Link / Provenance

**Principle.** One continuous linking process (recover-from-history + link-new-as-made = same mechanism). Identity = the connected graph. Mechanical skeleton (certain) + semantic enrichment (typed, confidence-graded, high-stakes judged); never an inferred link masquerading as certain. **Anchor = live link, NOT embedded copy.**
**Spec.** Mechanical: containment (atom∈session∈project from cwd) + crossings (every Write/Edit tool_call = artefact↔exchange↔ts, the live join from reads/1). Semantic: cause-edges + cross-project concept-sameness (model-made → `grade=semantic`+confidence; high-stakes → P4 judge). tool_result = LAZY: keyed to the crossing, fetched on demand, NOT distilled. Build the `find_relations` edge layer (unbuilt in the Company — recollection builds its own, portable).
**Files.** NEW `src/links/` (crossings extractor over `tool_calls`; concept-link inferer). HARVEST CI's `indexed_artifacts`/`artifact_provenance` schema.
**Do/Don't.** DON'T embed quote-copies *because* redundant + drifts (Tim's correction). DON'T distill tool_results eagerly *because* low value; key them for on-demand.

## 6. Gather

**Principle.** The querier is an AGENT (me/other CC agents), working from Tim's dense multi-dimensional input — decompose, don't expand. Classification-is-addressing (the chain computes coordinates). Two modes.
**Spec.** Pass0 structural(free) → Pass1 message-type classify → Pass2 sentence-grain decompose → Pass3 per-block typed classify at ~120 concurrency under the **Classification Law** (1 axis/2 extremes/3–5 even bins/progressive chains) → Pass4 typed lookups by block-type (space selected by type) → Pass5 aggregate+inject. Modes: **top-k** (precise) + **gather-all-and-aggregate** (pooling across time). **NEW component — the questionless-sweep lane** (Pillar 2): scheduled sweeps that emit findings unasked (inventory, merge-as-join MATCHED/build-list/debt-list, orphans/residue); map(all units)→reduce(cluster/join), NOT query-time gather. (De-risked: the sibling session's 940→483 overnight run.)
**Files.** REPLACE flat `src/search.ts` → `src/gather/` (decompose+classify+route+fuse, RRF; agreement-across-lenses = signal). NEW `src/sweep/`.
**Model-slots.** classifier/router = 0.8B (~120 concurrent); decompose = small model.
**Do/Don't.** DON'T embed Tim's whole message as one fingerprint *because* it muddies; decompose to threads. DON'T assume top-k answers pooling questions *because* they need gather-all.

## 7. Judge (the judgment layer)

**Principle.** A general "several small readers → structured verdicts" machine, pointable at ANY judgment (relevance, supersession, "what should the agent ask", direction…). An OPEN registry of judgment types. Rule-driven routing on question AND result. Verdicts typed + self-explaining (grounded-chain). = the P8 sub-agent's machinery.
**Spec.** Cleaners: proofreader (CPU cross-encoder, always) → set-reader (shortlist, folds dups/flags conflicts) → jury (4B, wakes on ambiguity OR high-stakes question-type, rule-driven). Judgment registry (rows): junk-kill/answers-vs-mentions · supersession (time-axis directional) · set-curation (arc) · visual-matched · +more. Verdict = `{type,value,basis,confidence}`, multiple per result.
**Files.** NEW `src/judge/`. HARVEST substrate-mcp `find_state_asymmetries` (the time-direction sensor) for supersession. **Proofreader = jina-v3 reranker @ the fork's served `:8008`** (D-4 RESOLVED tim-direct: non-commercial is fine, it's experiments — so jina-v3 IS the proofreader, NOT eval-only; the earlier "ms-marco-default, jina eval-only" line was stale). ms-marco (CPU) stays available as a permissive fallback via the env-configurable `RERANK_URL`, not the default.
**Do/Don't.** DON'T run the jury on everything *because* slow memory stops being used; route on ambiguity. DON'T return bare scores *because* the agent can't reason or audit — verdicts carry their why.

## 8. Recall surfaces

**Principle.** Three arms — shallow (tools), ambient (proactive injection), deep (sub-agent) — usable by Tim's agents via MCP+skill, all grounded-default (easy path = judged+provenance; raw = a deliberate extra hop).
**Spec.** (a) MCP: **parametric core + axis-addressed registry-driven tools** (`whats_my_position_on`, `the_arc_of`, `what_projects_include`, `when_was_worked_on`, `what_touched`…), `return_format` override, **handles-first** (id+gist+verdicts). KEEP the `search`+`read` names (drop-in). (b) recollection skills (wrap the common flow). (c) **sub-agent** = the looping judgment layer (gather→judge→follow-up→assemble) for deep pool/arc. (d) **proactive injection = LAYER 2** (separate build; CC hooks: SessionStart→FLOOR injection [the keystone: Tim's active principles + this project's standing state], UserPromptSubmit→in-session; same gather→judge machine, mode-gated, learns from `tim_correction`). NO pre-compaction snapshot.
**Files.** MODIFY `src/mcp-server.ts` (KEEP names, ADD parametric axis tools + return envelope — match CI's design). NEW `skills/`, `agents/` (recollection's own), `hooks/` (the layer-2 injection — its own design step).
**Do/Don't.** DON'T flood context with full content *because* that's why the current one is unpleasant — handles-first. DON'T make the agent orchestrate raw tools for the common case *because* the skill should wrap it.

## 9. Health (cross-cutting)

**Principle.** Measure the corpus's own drift and re-settle it (lower resistance).
**Spec.** Temperature scan = per-unit resistance (distance between structural position [embed the address-description with the steered lens] and semantic position [embed the unit]); a heat-map of misfiled/drifted units. Annealing dream-phase (deep-pass): re-place drifted, split/merge categories, fold duplicates. HARVEST substrate-mcp `consolidate`/`cluster_by_embedding`; true dedup/merge/prune is NET-NEW (memoirs reference).
**Files.** NEW `src/health/`.

## 10. Dependency-ordered buildable units (informs Tim's build-order; he sets it)
File-disjoint where possible (for parallel build). Phasing (dependency-valid, NOT a mandate):
- **A · Foundation:** clone→recollection rename + `~/.recollection` paths + schema (units/links/fingerprints/verdicts) + unified capture incl. sidechains + backfill from the existing archive + ONE embedding lens (fabric). → first capability online → **bootstrap: use it to recover decisions for B.**
- **B · Understanding:** distill L1/L2/L3 + the provenance link graph + steering-vocab mining + the principle-ratification gate.
- **C · Retrieval:** gather (decompose→classify→lookup, two modes) + judge layer + the axis-addressed MCP tools (first usable recall) + the questionless-sweep lane.
- **D · Delivery:** the sub-agent + proactive-injection layer-2 (hooks) + recollection skills.
- **Cross:** the health/dream-phase once there's volume; the multi-lens loadout filled out.

Each unit's "done" = its FUNCTION + FORM criteria in `COMPLETION_CRITERIA.md`, verified by USE.

## 11. WAVE-3 BUILD-READINESS CORRECTIONS (must honor — each is a SILENT-failure landmine)
Source: `wave3-build-readiness-audit.md`. Each would let the build "pass" while broken.
- **B-1 · Sidechain filter is in SEARCH, not capture.** Capture already sweeps `agent-*.jsonl` (`paths.ts:findJsonlFiles`). The real exclusion is `AND e.is_sidechain = 0` at `search.ts:165` + `:188`. → §2/§6: remove/parameterize that filter; sidechains are captured+embedded already but hard-filtered from results. Tie to D-9 (their graph placement).
- **B-2 / A6 · `tool_result` is 100% NULL on the Claude path** (`parser.ts:202-210` is a discarded TODO; only the Codex path ever populated it — see D-6). → §5: "lazy fetch" = re-read the source `.jsonl` via `show.ts`, NOT query `tool_calls.tool_result`. A query wires a silent empty.
- **B-3 · `dist/` is committed; the MCP server runs from `dist/`.** → ADD `npm run build` (src→dist) to the build/verify protocol; "verify by USE" runs bundled code, so without a rebuild every verification runs STALE code. (Clone's own CLAUDE.md: edit src → build → commit both.)
- **B-5 · `.mcp.json` has an env-var ALLOWLIST.** → §1: renaming env to `RECOLLECTION_*` MUST update `.mcp.json` or the MCP-launched server never gets the var → silent fallback to `~/.config/superpowers` = reads/writes the LIVE 11.4 GB episodic corpus (comingling). Verify G0.1 against the actual data dir used by the MCP-launched server.
- **B-6 · SessionStart recursion (#87) + G8.1 floor injection share the SessionStart trigger.** → §8d: the new floor-injection hook must carry the same fan-out guard; if its judge is the session model (D-2a) it can re-enter by a new path. (Ties to D-10: a precomputed-cached floor avoids the SessionStart model-call entirely.)
- **B-7 · vec0 dim is a REBUILD, not an ALTER.** `vec_exchanges FLOAT[384]` (`db.ts:173`) — sqlite-vec virtual tables don't support dim change. → §1/§4: "demote 384" = per-lens `CREATE VIRTUAL TABLE vec_<lens>`, rebuild not ALTER. (ND-1: retire 384 for a clean fabric re-embed.)
- **B-4 · The "13k head-start" is capture+embeddings, NOT summaries.** Only ~1,286 L1 summaries exist on disk. → §3/G2.1: the L1 backfill is real net-new local-4B compute; prove on a sample + schedule the sweep (ND-2).
- **Secondaries (S-*):** the mcp-server is a near-total REWRITE despite keeping the `search`/`read` names (don't under-budget it) · the `summarizer.ts` REPLACE must PRESERVE the hierarchical-summary / resume / sentinel paths (don't drop them with the cloud SDK) · add an index on `tool_input.file_path` (JSON-extract) for the crossing join · `~120 concurrent` must be `SlotBudget.from_registry`, never a hardcode · the 38 existing tests need a refit policy (keep/adapt/replace) · the 4-file version lockstep + generated `version.ts` must stay in sync.

## 12. FABRIC-ALIGNED build notes (cross-session, 2026-06-14)
- **EMBEDDING-AXIS REGISTRY (lead-committed `channel-memory/mega-prep/EMBEDDING-AXIS-REGISTRY.md` b2c5d7c — faithful operationalization of D-1; ADOPT for recollection's fingerprints/addressing):** a unit's address = co-equal spaces — provenance `exchange://<sid>/<i>` is **CANONICAL** (re-embed-stable spine + cross-axis JOIN key) · temporal · file-position · structural sub-axes (project·session·segment) · **+ ONE co-equal SEMANTIC axis per (embedding-model × embedding-way)** in an extensible file-discovered registry. First populated axis = `pplx-ctx-4b-docs` (model pplx-embed-context-v1-4b, way=documents-mode, :8007, dim 2560, cosine) — index against it now. **Golden rule is PER-AXIS** (a vector matches only its own model×way); provenance/temporal/file-position filter ANY axis (model-independent). Recall carries an axis selector (default = primary served; multi-axis → RRF). This = recollection's `fingerprints` table (one row per (unit, axis)) with provenance as the join; congruent with the running Phase-A schema/lens lanes.
  - **★ DIM IS REGISTRY-SOURCED, NEVER HARDCODED (fork cross-review, B-7 root-class fix):** when sizing `vec_<lens>`, the dim MUST be read from the axis-registry entry's `dim` field — NOT a literal `2560` in code. The B-7 bug WAS a hardcoded legacy dim (384); replacing it with a hardcoded 2560 just moves the bug. Adding a future embedding model×way must be a registry ROW, not a code change. `ensureLensIndex` sizes the table from the registry. (Verify the B-7 fix on this, not just on end-to-end function.)
- **json_schema for extract/judge roles — engine ALREADY enforces it (fork finding, corrects the earlier caveat):** the cognition engine has an enforced structured-output path — `generation_policies.py` carries a `json_schema` flag (true enforced structured-outputs, not just the `json_object` hint) AND `client.complete(schema=)` retries + raises on mismatch. Roles are additive, file-discovered `roles/*.py` = `{id, prompt_template, output_schema}`; `run_items`/`run_swarm` for concurrency. So recollection's gather/judge roles (and the panel) are NOT blocked on any engine fix — author a new additive role with the json_schema policy + an `output_schema`. (Still: use the enforced json_schema path, never bare json_object — [[reference-vllm-structured-output]].)
