# THE PIN-OUT — capabilities · goals · requirements · dependencies · strategy
*2026-07-09, after the full tool survey. Posture: THE SPIRAL LAW governs every row here — everything
listed is an ATTEMPT toward the centre, not intent; nothing alone is right; the real thing is between
the arms. This document is itself an arm: attack it, fold over it, never obey it.*

## 0 · The goal (Tim's objective, one statement)
Cross the involution threshold: enough functioning parts, folded inward and connected, that the
universe knows itself — every thing addressed, every layer traversable, laws circulating through the
hands that act, processes living inside and firing on data, nothing buildable lost, coverage 100%
breadth × 100% depth, no plan required for the answer to emerge. No developer, no specs — the method
is composition of what exists + folding strengths over edges.

## 1 · The capability map (what actually exists, by family — all verified live this session)

**COORDINATE / TRAVERSAL (the instrument — already fused):**
- `coordinate` — filter (path/ext/type/time) + semantic (per-space lens auto-routing) + lexical +
  graph (depth≤3) + scale + count, ONE call, meta.plan makes under-recall loud.
- `project` — the radial instrument: binding lenses (semantic · by_separator · **by_nucleation** —
  the keystone) · emb layer · **dim (MRL meaning-zoom)** · **rung (scale-pyramid zoom)** · center
  (attention-is-origin) · at (time scrubber) · pole_a/pole_b.
- `layers` — which emb-layers each space carries (multi-layer model, registry-true).
- `find_relations` — the inversion query (near in space A, far in space B).
- `scope` — ui:// ↔ code symbols (ledger-derived). `inspect_address` — the one read door + page faces.

**COGNITION / EXECUTION:**
- `run_role/run_items/run_reduce(role|rule|cluster)/run_draft(_items)/run_swarm/run_jury` — the fire
  family. `run_reduce(mode='cluster')` IS the pyramid's cluster boundary.
- cascades (8 saved; `spec-compiler` = loop-prep as a chain) · flows (9 registered production lines:
  transcript_mine · repo_ingest · drift_radar · floor_walk · **pattern_cluster** · ts_backfill ·
  dragnet_extract · registry_generation · cc_registry_refresh).
- `panel` (diverse-lens quorum) · minds/ (composition-as-data: pair = extractor→judge with the edge
  as a row; recompose = edit data) · `preview_turn` · casts/modes.
- Models: local 0.8B (ultra-conc) · 2B · 4B AWQ/FP8 · 9B (solo) · cloud kimis (2.6/2.7, NO budgets,
  native structured output) · embedders pplx-2560 / nomic-3584 · reranker jina (GPU, full-pool).

**SELF-AUTHORING / REGISTRIES:**
- `create` (role · skill · context · projection · mark_type · generation_policy · relation_type ·
  ai_tic · guide · mind · type) — direct, gated, auto-reflected. ~30 file-discovered registries
  (constitution + rows + loader + acceptance). `rule` (declarative routing). `field_types`.

**MEMORY / SUBSTRATE:**
- corpus spaces (design_intent 6610 lossless · history 2928 · extractions 51600 · repo · mesh ·
  code/symbol · operators…) — content in fs_store, embeddings in the supabase ledger (:15432).
- `embeddings` (spaces/route/build/**pyramid** — scale rungs exist: runtime/scale.py) · `capture` ·
  `ingest` · `session_recall` · recall stack (@recall) · dragnet grain-assets.
- ledger.* (entry/edge/latest_run/embedding — the address tree; 487 capability rows feed Suite init).

**PROCESS / RESIDENCY (the five arms + the missing tick):**
- flows (callable) · cascades (callable) · routines (5 registered, spawn REAL CC sessions, cadences
  declared, **no ticker**) · jobs (the UNIFIER — run_kinds={cascade,cascade_inline,handler,role,flow},
  trigger_kinds={manual,schedule,change,event,condition}, "skeleton: fires manual only") ·
  activation_driver ("THE ALWAYS-ON CALLER (DORMANT)").

**FABRIC / SESSIONS (the Claude-Code integration):**
- cc_channel (live injection INTO sessions + self-registering membership) · cc_clone · cc_gate
  (per-step gate/abort/rewind) · cc_board · cc_attachments · cc_images · cc_voice/say · cc_retire ·
  `sessions`/`context` (supervised-live ops) · session-supervisor (spawn+inject+capture) ·
  Claude Code HOOKS (proven live in my own config: PreToolUse can inspect/block; SessionStart injects;
  SessionEnd syncs).

**GOVERNANCE / OPERATOR:**
- `operator` (rules propose→confirm) · `decisions`/`list_surfaced`/`inbox` (the gates) · `access`
  (principal/verb/address, fail-closed) · `keeper` (per-project grounded answerer) · `dials`
  (anticipation·stability — **"nothing reads this yet"**) · `marks`/`mark` (18 mark_types incl.
  ai_fingerprint · built_twice · contradiction · intent_*) · ai_tics registry (framework_imposition·
  silent_fallback·…) · governance floors (agents propose, Tim arms/approves).
- supabase stack: db + realtime (UNUSED — the data-driven push) + functions-at-write (UNUSED).

## 2 · The requirements (the banked laws — the fold's material)
Truncation law (no [:N] on model-bound material — chunk completely) · Open-vocabulary law (schema
constrains shape never meaning; closed sets only where code branches; canonicals emerge at the cluster
layer) · Spiral law (attack+fold, nothing is spec) · No-cloud-budgets · Native structured output ·
Declared bindings honoured · Fail-loud everywhere (hangs are the worst silent failure; empty≠dry) ·
Capture-before-reduce · Idempotent resume (skip-list IS the corpus) · Version-gated re-mine ·
Deterministic-work-to-code · Faces never flattened · G16 counts-not-confidence · Extract-the-law-
before-retiring · Measured gates before scale · No priority/no upfront-correctness (convergence
replaces verification) · Reduce trees for over-context wholes · Lenient-in strict-out on SHAPE only.

## 3 · The dependency spine (what stands on what)
```
                       ┌─ D. REFLEX ARC (hooks→coordinate→inject/refuse)
 A. TICK ──────────────┤  (needs: laws-as-rows ✓ · hooks ✓ · coordinate ✓ · channels ✓)
 (jobs.tick armed +    └─ E. LIVE PROPAGATION (realtime→channel inject)
  activation_driver         (needs: supabase realtime ✓ unused)
  woken — everything
  else downstream)     ┌─ F. BOOT BRIEF (SessionStart→compose-from-addresses)
                       │  (needs: registry_freshness seam ✓ · corpus ✓)
 B. LAYER POPULATION ──┤
 (L0 deterministic     └─ G. NUCLEATION LOOP (open words ✓ ALREADY FLOWING →
  tree-attach · L1        run_reduce(cluster) ✓ → kimi naming seat → operators
  0.8B open-tag fan ·     space ✓ → candidate types → Tim's gate ✓)
  routed 4B) — attach
  to ledger addresses  ┌─ H. DRIVERS→RESIDENTS (archaeology_mine/mesh_triangulate/
                       │  census fold INTO flows-registry rows; lens-as-param
 C. UNIFIED QUERY ─────┤  folds mine_design_intent INTO transcript_mine)
 (coordinate+project   └─ I. DORMANCY VIEW + COMPLETION PROPOSALS
  over populated          (needs B+C; feeds Tim's gate → build organs)
  layers = the mesh
  traversable)
```
A is the heart; B is the blood; C is the nervous system; D/E/F are law-circulation at three
latencies (act-time · live · birth); G is how the taxonomy grows itself; H is A1 residency;
I is the payoff loop (nothing buildable lost).

## 4 · The strategy (folds, not builds — each lands alone-useful)
1. **Wake the heart (A):** arm jobs.tick + wake activation_driver — Tim arms (op='arm' is the
   operator door). Routines start beating (completion_poke every 30min; the freshness owners daily).
   Fold: the five process arms wire through jobs' already-declared vocabulary. NOTHING new built.
2. **Fold the drivers in (H):** my three build-prep drivers become flow rows (the mining flow gains
   lens= param — mine_design_intent + mine_exchange one organ; census/mesh-round become a flow with
   territories= derived). Registered, jobs-runnable, resident.
3. **Populate the floor (B-L0):** deterministic tree-attach — every file+exchange as ledger rows
   (ext=type, name=id, path=nesting, mtime+git=time) via a flow, no model. The dormancy WHERE-clause
   becomes real.
4. **First nucleation round-trip (G):** run_reduce(mode='cluster') over the 258+ coined kind-words +
   the 30k intents' subjects → kimi naming seat → candidates land in operators space → surface to
   Tim's gate. THE LOOP CLOSES HERE — the taxonomy's first self-grown types.
5. **Boot brief (F):** compose-from-addresses on the registry_freshness seam (laws + anchors +
   latest round + open gates). Verify: a fresh session wakes knowing.
6. **Reflex arc (D):** PreToolUse hook embeds pending create/edit specs → coordinate against
   principles/laws/ai_tics → inject resonance (warn-first; block only on Tim-confirmed laws).
   The enum mistake becomes structurally difficult.
7. **L1 open-tag fan (B-L1):** 0.8B (fits beside embedder) open-tags EVERYTHING; embed as a layer;
   density routes the 4B finer pass (allocations computed, not chosen).
8. **Live propagation (E):** realtime → cc_channel inject — a law confirmed at 9:00 reaches live
   sessions at 9:01.
9. **Dormancy + completion (I):** standing coordinate views; forgotten+reaching_for+code:// ⇒
   addressed build-candidates → Tim's gate → the cron build organs.

## 5 · The open attacks (named, not resolved — for the next arms)
- jobs.tick vs activation_driver vs routine cadences: THREE tick attempts — which is the fold-point?
  (jobs names the others as run_kinds → likely jobs; verify by reading both tick bodies.)
- The ledger's 88%-noise + 66% dangling edges (prior read) — L0 repopulation may supersede rather
  than repair; decide at the tree-attach flow.
- substrate-mcp: a WHOLE second vault/semantic/graph arm — survey before C hardens; likely holds
  folds (its cluster_by_embedding, get_neighborhood, state-asymmetry tools).
- Reranker in the coordinate path: semantic legs return cosine-ranked; the jina precision stage
  exists (@recall) but coordinate doesn't use it — a fold.
- Dials read by nothing; keeper/access built for a multi-principal future — the reflex arc + boot
  brief should read dials (anticipation governs pre-retrieval — it was BUILT for F).
- connects_to verify-floor (candidate-mentions → real addresses) before the cross-link writes edges.
- The `?` corpus space (11 records) + `what` space (1) — unlabeled attempts; identify before C.
```
STATE: survey ~complete (58 MCP tools + CLI + flows/jobs/routines/cascades/minds + hooks + channels
+ supabase stack) · re-mine DRY at 6610 lossless · open vocabulary FLOWING (258 kind-words) ·
awaiting Tim on: strategy order + what he arms first (the tick is his door).
```
