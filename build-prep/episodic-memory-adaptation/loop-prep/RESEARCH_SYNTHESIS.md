# recollection — RESEARCH SYNTHESIS

> The evidence base the Completion Criteria + Implementation Guide are built on. What EXISTS that informs the build. Structured by round; each finding → its implication. Ground truth from the actual code/corpus — when a spec contradicts a finding here, the spec changes, not this.
>
> **Companion docs (the exhaustive detail lives here — this synthesis integrates + points):**
> Design: `../EPISODIC-UPGRADE-PLAN.md` (the decided design §0–P10 + COMPLETE DESIGN) · `../../brain/CONVERGENCE-OBJECT.md` (the laws) · `../MERGE-INTENTION.md` (pillars/merge frame) · `../../../foundation/exchanges/20-the-convergence-object.md` (primary source).
> Deep reads: `../reads/1-provenance-spine.md` · `2-company-store.md` · `3-substrate-mcp.md` · `4-conversation-intelligence.md` · `5-fabric-model-layer.md`.
> Wave-1: `wave1-constraints-ledger.md` (38 constraints) · `wave1-design-truth.md` (design + sibling rays + gaps) · `wave1-build-map.md` (clone-base + integration + harvest).
> Decisions: `OPEN-DECISIONS.md` (the 8 open for Tim + resolved-by-me).

---

## ROUND 1 — What exists in the codebases (the build territory)

### 1.1 The clone base — `~/episodic-memory` (v1.4.2, MIT) → becomes recollection
**Found (build-map + reads/1):** a working Claude-Code memory plugin. Plugin chassis (`.claude-plugin/plugin.json`, `hooks/hooks.json` SessionStart, `cli/` + `mcp-server-wrapper.js`); capture-incrementality (`indexer.ts` high-water-mark resume on `MAX(line_end)`, `sync.ts` mtime-gated atomic copy, `summary-sentinel.ts`, `file-lock.ts`); the `exchanges` + `tool_calls` atom tables with additive-ALTER migration (`db.ts`); `read`/`show.ts` render; version-stamped re-embed engine (`embedding-migration.ts`); two MCP tools `search`+`read`.
**Live footprint (reads/1):** 75,397 exchanges / 6.72M tool_calls / 7,351 sessions / 96 projects; `tool_calls.tool_input.$.file_path` present on 99.99% of Write/Edit; `tool_result` 100% NULL; DB in the versioned plugin cache (update-clobber risk).
**Means:** KEEP the chassis/capture/atom-tables/migration/render/re-embed/tool-names. MODIFY paths→`~/.recollection`, include agent sidechains (episodic excludes `agent-*.jsonl`), demote hardcoded `vec_exchanges FLOAT[384]` to one lens. REPLACE in-process ONNX embeddings → fabric multi-lens; cloud-SDK summarizer → local resident-4B (also kills SessionStart recursion); flat KNN search → the gather+judge machine.

### 1.2 The integration target — `~/company` (patterns recollection MUST match)
**Found (build-map + reads/2,5):** store = content-addressed **ext4 filesystem** (`.data/store/`, `FsStore`/`FilesystemResolver`, C4 Resolver Protocol); vectors = filesystem JSON per (item, space), `vec://<source>#space=<lens>`, bge-m3/1024 currently, 2,186 vectors live. The Postgres+pgvector resolver is **designed but unbuilt**. `corpus.py:write_record` enforces 3-axis lineage (session/round/project) fail-loud. Fabric: embeddings via vLLM pooling @ `:8001`, model registry (`services.json`+`model_capabilities.json`); mining via resident 4B; `run_items` (map) / `run_reduce(mode=cluster|role)` / `SlotBudget.from_registry`. MCP face = parametric verbs (`return_format summary|content|stats|addresses`), never tool-per-op. `find_relations` (edge layer) is **unbuilt**.
**Means:** three patterns to match (so absorption is a re-point not a rewrite): (1) registry-is-truth/no-hardcoding; (2) addressed-record + space-keyed-vector store with fail-loud lineage; (3) parametric MCP verbs + map/reduce cognition. recollection writes its SQLite **portable-by-field** (explicit space/source/dim/model/lineage columns).

### 1.3 Harvest sources
**substrate-mcp (`~/repos/obsidian-overlord`, reads/3 + build-map):** harvest the **temporal/state layer** (`state_history` append-only change-log + `find_state_asymmetries` directional time-gap sensor), `cluster_by_embedding` (NumPy spherical k-means, centroid-labels = the unbuilt pattern_cluster), the structure-aware chunker. Porting is shallow (SQLite is ground truth, Chroma disposable). ⚠ Correction: `embeddings.py` is NOT in the repo — the harvestable `OpenAIEmbedder` survives only in CC file-history (`~/.claude/file-history/bda8ce28-.../ae22f5e848708178@v2`). `consolidate` is aspirational (wikilink-resolve only) — true dedup/merge/prune is net-new.
**conversation-intelligence (`~/repos/Supabase`, reads/4 + build-map):** harvest the **turn-context embedding** unit (turn-pair + tool-call summary), the **artifact-provenance graph** (tables `indexed_artifacts` / `artifact_provenance` — 9,833 rows proven), the **parametric-tool/return-envelope** design (5 tools in 20260210 migration + `ci_issues` 6th in 20260211). The ingestion+turn-context-search lane worked (1,205 convs / 24,847 turn embeddings); the knowledge/agent tier is dormant (harvest ideas, not schema).

## ROUND 2 — The comparable landscape (what others do; what to borrow)
**Found (`../LANDSCAPE.md`, 18 systems):** memoirs = the closest reference (same sqlite-vec substrate, ingests CC transcripts, RRF hybrid + HippoRAG graph + sleep-consolidation + PII + bi-temporal, fully local) — read it for the net-new pieces (true consolidation, RRF, PII). claude-mem = 3-layer progressive disclosure (~10× token saving), live-hook capture, dual SQLite+Chroma. memsearch = markdown-canonical + disposable vector cache, ONNX local embeddings, hooks-no-MCP, haiku turn-summaries with anchors. **Design lessons:** keep single SQLite+sqlite-vec; run raw AND distilled both; progressive disclosure; proactive + on-demand; bounded growth/consolidation is the biggest gap.

## ROUND 3 — The laws & the design (what governs the build)
**Found (`../../brain/CONVERGENCE-OBJECT.md` + `wave1-constraints-ledger.md` = 38 constraints):** the Convergence Law (info healthy at structural∩semantic; resistance=deviation; deep-hole √2/2), the Classification Law (1 axis/2 extremes/3–5 even bins/progressive chains), classification-is-addressing, registry-is-truth, grounded-chain, extraction-vs-judgment, no-versioning, no-hardcoding, the ten derivations. North star: identity-continuity (Pillar 1) + cross-project omniscience (Pillar 2), one single-origin transcript spine.

## ROUND 4 — Sibling-session rays (triangulation; `wave1-design-truth.md`)
**Found:** (1) the **address-coordinate model** (quadtree/Morton path; radius=relevance, angle=relation-type, scale=n) — fills P1's abstract "addresses"; OPEN-DECISION D-1. (2) the **questionless-sweep lane** — Pillar 2's broad ops need sweeps that emit findings unasked (query-time gather can't); proven by the other session's 940→483 overnight RG10 run; ADDED as a component. (3) **memory = record + return-condition**; reuse the concurrent-cognition rules engine, don't invent a DSL; write-once-project-many incl. procedural/predictive(twin)/meta memory-kinds. (4) the **asymmetry / no-fiction-about-Tim law** — the memory must never misremember Tim; the reason P5's gate exists. (5) embedding ops-traps + **jina = CC-BY-NC** (non-commercial → OPEN-DECISION D-4).

## Contradictions & resolutions (see OPEN-DECISIONS.md for the full ledger)
- C3 pre-compaction snapshot: DROPPED (plan wins). C1/C2 stale text (embed→link; bge-m3-unify superseded): cite corrected. G2 questionless-sweep: added. G4 no-fiction: recorded hard. G5 multi-vector own-index: recorded. The core spine is internally coherent and law-consistent; all findings are additive or housekeeping.

---
## ⚠ SUPERSEDED FACTS (2026-06-17) — see loop-prep/BUILD-ORDER-REFRESH.md for current state
Three Round-1 facts went stale after 2026-06-15→17 (verified by explorer waves):
- **embed:** NOT bge-m3/1024 — the corpus core is now **pplx-2560 @ :8007** (bge-m3 dormant). recollection's lens = pplx-ctx-4b-docs, dim 2560.
- **find_relations:** NOT "unbuilt in the Company" — it is **BUILT** (runtime/suite.py:10854, mcp_face/server.py:918) + a `relation_types/` registry + `lifters/links.py`. → recollection's LINK stage WIRES IN, not parallels.
- **forms/lifters + common_knowledge:** the Company now has typed-extraction (forms/lifters, built-but-unwired R9) + a live publish space (common_knowledge) + /api/cognition/neighbours. → DISTILL wires through forms/lifters; absorption (D-8) has STARTED.
The DESIGN (criteria, decisions, 8-stage pipeline) is unchanged + canonical; only these "what-exists-today" facts moved. Build-through = BUILD-ORDER-REFRESH §C.
