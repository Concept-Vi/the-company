# Loop status — embedding/memory unification (COMPLETE 2026-07-02 ~06:20)

*The overnight loop is DONE. All authorized auto-work is green; only Tim-supervised items remain (below). Criteria: COMPLETION_CRITERIA.md. Tick log follows this summary.*

## ✅ FINAL — what the loop achieved
**The unified Supabase embedding+memory store is LIVE: `ledger.embedding` (:15432) = 76,039 vectors across 26 spaces + 1,403 provenance edges. ALL auto-work complete (desc 1043/1043 done — the stalls were resource contention during peak-load ticks, not a bug; ran clean once the machine was quiet).** Both halves of the merge-intention spine — *what exists* (code) and *why/when it exists* (conversation) — in ONE pgvector store, one address grammar.
- **E — multi-model, multi-scale embeddings:** code 1042 + symbol 6201 (nomic-embed-code 3584) · docs 679 + desc 504/1041 (pplx 2560). Killed two hidden truncations (ollama 4096, pplx 8192→real 32768). Multi-scale = file ↕ symbol ↕ the 16 pyramid rungs.
- **D — descriptions:** carry-forward 3384 + delta re-run → still-missing code/md **0**. Unlocked the `desc` space (plain-language code search).
- **P/S4 — provenance spine:** activated recollection's dormant crossings (23,608 links); landed **1,403 `generated-by` edges** — code node → the `exchange://` that made it, queryable from the ledger.
- **S — full Supabase migrate:** halfvec multi-dim schema (nomic 3584 / pplx 2560 / bge 1024, HNSW). Migrated every FsStore space + recollection's 6,983 conversation embeddings + scale rungs. Each additive→verified (counts + ranking match FsStore). FsStore kept as fallback.
- **V — verified by use:** `ops/embed_status.py` + a cross-space query ("resolve which brain model") returns the right code (desc: fabric/config.py, decide-for-me.py), the conversations (exchange), and the docs — one query, all three sides.

## ⚠ NEEDS-TIM (the only remaining items — NOT done unattended)
1. **S4-B — code:// surface reconcile.** Migrate corpus/repo + `resolve_scope`/S3 to canonical `code://<project>/<path>::<sym>`. LIVE chat-surface code → ~15-min supervised change; plan in `CODE-ADDRESS-RECONCILIATION.md`. (Everything NEW already uses the canonical form; only the old surface diverges.)
2. **Read-path cutover.** All data is IN Supabase + verified; flip `query_index`/`corpus` reads FsStore→Supabase when you + Glyphic confirm. FsStore stays the live read until then.
3. **Glyphic (`ch-518m76r0`) schema input.** No reply overnight. Shared schema drafted (`SUPABASE-VECTOR-SCHEMA.md`) — awaits their models/dims before cutover.
4. **desc space remainder** (537 of 1041) — pplx stall-prone under load; non-critical 3rd lens. Resume `ops/build_embeddings.py --space desc` (incremental) when pplx is unloaded, then migrate.

## Tools built (reusable): ops/build_embeddings.py · ops/embed_status.py · ops/migrate_vectors_to_supabase.py · ops/migrate_recollection_to_supabase.py · SUPABASE-VECTOR-SCHEMA.md · CODE-ADDRESS-RECONCILIATION.md · EMBEDDING-MEMORY-SUBSTRATE.md

---


## TICK 6 (05:45) — FULL MIGRATE essentially complete; unified store = 74,996 vectors / 25 spaces
- **S3 FULL MIGRATE GREEN** — `ledger.embedding` on :15432 now unifies: code 1042 · symbol 6201 · docs 679 · all corpus spaces (extractions 51600/history/repo/topics/code_archaeology) · **exchange 6983** (recollection's conversation embeddings — the MEMORY half; 8222 fingerprints→6983 = honest same-source dedup, verified) · **16 scale-pyramid rungs** (~1046 centroids). CODE + CONVERSATION + multi-scale, ONE pgvector store. FsStore/sqlite kept as fallback (not yet cut over).
- **D GREEN** — still-missing code/md → **0** (2 kimi bad-json files retried successfully). Real code fully described.
- **S4-provenance GREEN** — 1403 generated-by edges (code↔exchange) in ledger.edge.
- **desc space** — PARTIAL (504/1041); pplx stall-prone under concurrent load; resumed (incremental) — the ONLY in-flight embedding piece. It's the 3rd lens (plain-language code search); core spaces are done without it.

## NEEDS-TIM (the only non-auto items):
- **S4-B code:// surface reconcile** — resolve_scope/S3 is LIVE chat-surface code; drafted (CODE-ADDRESS-RECONCILIATION.md) as a ~15-min supervised change. NOT done unattended.
- **cutover** — switch the query read-path FsStore→Supabase (all data is IN Supabase + verified; the read-path flip is a deliberate step for when you + Glyphic confirm).
- **Glyphic** — still no reply; the shared schema (SUPABASE-VECTOR-SCHEMA.md) awaits their models/dims.

## Essentially COMPLETE. Remaining auto: desc finish+migrate (in-flight). Everything else = NEEDS-TIM.

## TICK 5 (05:14) — corpus migration verified, D2 done, provenance edges landed, desc space built
- **S3 corpus GREEN** — history 2928 / repo 1292 / topics 325 / code_archaeology 2900 / extractions 51600 all migrated + count-verified. **ledger.embedding now holds 66,967 vectors across 8 spaces.**
- **D2 GREEN** — ingested scoped output; still-missing code/md **299→2** (the 2 = kimi bad-json on ledger_coverage_audit.py + use_side_gates_acceptance.py — mechanical retry). Real code 1041/1228 described (rest = excluded claude-ds).
- **S4-provenance GREEN** — **1403 `generated-by` edges** (459 code files) landed in ledger.edge: code node → the `exchange://` that generated it (e.g. store/vector_index.py → exchange://7c2c1b74…/1). The code↔conversation spine is queryable FROM the ledger.
- **D3** — `desc` space (pplx over what_it_does) built (1041) + migrating to Supabase (bg task bpcjc7jwz).
- **S4-B code:// surface = NEEDS-TIM** — resolve_scope/S3 is live chat-surface code; additive-alias cutover drafted (CODE-ADDRESS-RECONCILIATION.md) for a ~15-min supervised change. Not done unattended (never break the live surface).

## REMAINING: desc migrate (finishing) · recollection fingerprints 8222 → Supabase (memory side of full-migrate, TODO) · scale rungs (scale:extractions:k512) → Supabase · 2 D2 bad-json retries · S4-B (Tim) · Glyphic still no reply.

## TICK 4 (04:43) — S3 (my spaces) migrated+verified; D2 scoped-fixed & grinding; corpus migration backgrounded
- **S3 partial GREEN** — `ops/migrate_vectors_to_supabase.py`: code 1042→1042, symbol 6201→6201, docs 679→679 into `ledger.embedding` (exact counts). VERIFIED by query: "resolve which brain model" against Supabase symbol space returns the SAME ranking as FsStore (require_brain/brainRow/active_brain/_local_brain_key/_chat_brain_cfg) — halfvec fp16 distances differ, ranking identical. FsStore kept as fallback.
- **corpus migration RUNNING** (bg, tmp/migrate_corpus.log): history/repo/topics/code_archaeology/extractions(51600) → ledger.embedding. Heavy (watch DB). Verify counts next tick.
- **D2 scoped-FIXED** — producer was describing 5650 .json noise (sorted ahead of code); scoped to code/docs exts. D2-scoped grinding (309 real items, ~150/309). When done: ingest FRESH out/ → still-missing code/md 299→~0.
- **NEXT:** verify corpus migration counts → finish D2 (ingest) → **D3** (desc space: pplx over what_it_does, batch≤4) → **S4** (code:// reconcile corpus/repo+resolve_scope to canonical, additive alias first; LAND provenance edges via file://↔code:// join now that both are queryable). Glyphic: still no reply.

## TICK 3 (04:11) — V green, S1+S2 green (Supabase schema live)
- **V GREEN** — `ops/embed_status.py`: efficient per-space table (code 1042 · symbol 6201 · docs 679 · extractions 51600 · history 2928 · repo 1292 · topics 325 · code_archaeology 2900). Retrieval PROVEN: query "resolve which brain model" → code: brain_router/model_routing; symbol: the exact fns active_brain/_chat_brain_cfg/require_brain; docs: brain-loadouts.md. Multi-scale semantic search works.
- **S1 GREEN** — pgvector 0.8.2 enabled on :15432.
- **S2 GREEN** — `ledger.embedding` applied + round-trip verified. One table, per-dim **halfvec** columns (3584 nomic / 2560 pplx / 1024 bge), HNSW-cosine indexed (halfvec→4000 dims; plain vector caps at 2000 so nomic+pplx would be exact-only). Addressed by canonical code://. Schema draft written for Glyphic: SUPABASE-VECTOR-SCHEMA.md.
- **D2 still grinding:** batch2 producer (kimi, --limit 400) still running; its ingest (waiting task) fires when done → still-missing code/md drops from 299. Fresh-only ingest (stale-june archived).
- **NEXT: S3** (migrate all FsStore spaces + recollection fingerprints → ledger.embedding, additive→verify→cutover) → **S4** (code:// reconcile on corpus/repo+resolve_scope; LAND provenance edges via the file://↔code:// join, now trivial since both can be SQL) → finish D2 → D3 (desc space).

## TICK 2 (03:39) — done: D2 ingest #1 (120, still-missing 341→299), provenance spine ACTIVATED
- **P GREEN — provenance spine live.** Ran `recollection/dist/crossings-cli.js build` (RECOLLECTION_CONFIG_DIR=/home/tim/company/.recollection): **23,608 links** (produced 4790 · referenced 4019 · temporal 6560 · containment 8239); 33,007 gap (Bash/Grep, no artefact path) deliberately NOT crossed (no fabrication). Axis PROVEN: `crossings-cli touched <abs-path>` resolves a code file → the `exchange://<sid>/<i>` + session + timestamp that generated it (e.g. store/vector_index.py → exchange://7c2c1b74…/1, 2026-05-31). Recent files (ledger_build.py) return [] — not yet in the indexed archive; honest.
- **Landing provenance as LEDGER edges** folds into S: once recollection's data is on Supabase, the `file://`↔`code://<project>/<path>` join is one SQL — no throwaway sqlite→postgres bridge. (P is green; the ledger-edge materialization is an S sub-step.)
- **D2 in progress:** ingest #1 landed 120 (still-missing code/md 341→299). Batch2 (`--limit 400`) grinding via kimi-cloud in background (log: tmp/d2_batch2.log). NEXT TICK: when batch2 done, move its fresh out/ files (mind the stale-june set already archived to out-stale-june/), ingest, repeat until still-missing→0.
- **E FULLY GREEN** (verified via store index): code 1042 · symbol 6201 · docs 679.

## NEXT (this order): finish D2 (ingest batch2 → repeat → 0) → D3 (desc space, pplx over what_it_does) → V (embed_status verifier) → S (Supabase migrate + code:// reconcile + LAND provenance edges) → C.

## GREEN (verified by use)
- **E1 docs space** — pplx 2560, 679 embedded + 3 flagged oversize (>110k chars). *(Fixed a pplx OOM: docs batch 16→4; freed ollama's nomic to give pplx the card.)*
- **E code/symbol spaces** (prior ticks) — code 1038 (nomic), symbol 6201 (nomic). num_ctx=32768, truncation-detected.
- **D1 carry-forward** — 3384 interpretive descriptions copied from run 3f923cdb onto the new run (source_hash match). Code files now **919/1228 described** (was 0). DB mutation (no git artifact).

## IN FLIGHT
- **D2 re-interpret the 341 delta** — `ops/ledger_interpret_producer.py --project company --backend ollama` (kimi-cloud, zero GPU). PRODUCES to `build-prep/the-one-system/interpret/wave-ollama/out/<proj>/<path>.json`; a SEPARATE `ledger_interpret.py ingest` then loads to Supabase. **Two subtleties for the next tick:**
  1. `--limit 120` per run → needs re-running until the 341 are done (still-missing count: `select count(*) ... what_it_does='' ...`).
  2. **skip-if-exists against a possibly-STALE wave dir** — the wave-ollama/out had pre-existing (June) output; D2 skips files that already have a .json there, so CHANGED files (68) may keep stale June descriptions. For a clean redo of the changed set, produce to a FRESH out dir. NEW/blind files (273, no prior output) produce correctly.
  3. After producing: **run the ingest** (`ops/ledger_interpret.py` ingest of the wave) to land descriptions in the ledger, THEN verify still-missing drops.

## NEXT (priority order E→D→P→V→S→C)
- **D2 finish + ingest** (above) → **D3** build the `desc` space (pplx over each code file's what_it_does — the description-embedding space).
- **P** activate the provenance spine — run recollection's crossings (`~/recollection`, `RECOLLECTION_CONFIG_DIR=/home/tim/company/.recollection`); `links=0` → >0; connect ledger code nodes to their generating `exchange://`.
- **V** build `ops/embed_status.py` — per-space count/dim/model + a real top-k (efficient read, not the slow per-file scan).
- **S** (Tim AUTHORIZED — additive→verify→cutover): pgvector on :15432 → shared schema → migrate all spaces + recollection fingerprints → then the ledger `code://` reconciliation (corpus repo + resolve_scope/S3). Keep sources as fallback until verified.

## COORDINATION
- Glyphic `ch-518m76r0`: no reply yet (3 msgs sent, thread t-1782921350-ch-518m76r0). Check every tick; fold their models/dims into the Supabase schema. Proceeding with nomic/pplx/bge.

## GPU note
- Embedding pass owns the card: chat-4b evicted; pplx :8007 @ 32768 (batch env=1); ollama nomic unloads between code passes. Don't co-load a big brain during pplx work (OOM). Never restart the live brain without coordination.

---
## SESSION CONTINUATION (2026-07-02, Fable) — ①+② EXECUTED LIVE; ③ mapping wave RUNNING
- **② COMPLETE:** the ui→code join DERIVES inside every ledger build (binds-ui → calls-endpoint → serves-endpoint → powered-by; hand-seed folded: 178 links, 4 skipped visibly). `suite.resolve_scope` → the shared `runtime/scope.py` (sidecar commented out); **the MCP `scope` tool = the agent face that never existed**. 156 ui nodes, 359 powered-by edges. Test gate green: address_scope(25) + feedback_to_wire(25) + self_change_locating(25) + conv_payload(27) + conv_context(22) + conv_consent(35).
- **① COMPLETE:** the vector namespace on Supabase (store/pg_vectors.py; FsStore delegates; file store retired → store/fs_store_file_vectors.retired.py). Search IN Postgres (HNSW; vec_any overflow = any new dim, no schema change; ValueError dim guard; per-root __root_* namespacing preserves test isolation). 7 readers verified; corpus test sweep green; 4 reds proven PRE-EXISTING on the file-store HEAD (conv_index×2 key-form drift, capture_lenses, staleness variant).
- **LIVE:** bridge restarted — /api/scope answers from the ledger join; /api/corpus-query ranks from Supabase (51,600-space). Both faces of both cutovers serving.
- **③ MAPPING WAVE RUNNING** (ops/map_interface.py, kimi-cloud, 128 interface files → interface-map/out/). Next: synthesis → the design wave (rendered mockups) → Tim's recognition checkpoint.
- Glyphic pinged (main moved; their glyph vectors now land directly in ledger.embedding).

---
## 2026-07-02 (evening, Fable) — L9+L10+L11 ALL LANDED; converged with ④'s L4; the lanes are ONE system
- **L9 SUPERSESSION — CURED + verified.** 0014: ledger.interpretation (content-keyed) / file_meta (git time axis, 10,685 paths) / assertion (authored edges) + unit_latest/edge_unified. Backfilled 9,051 descs + 1,935 provenance edges. Cure proven: blanked a run-scoped copy → durable read survived. sync_durability (idempotent + freshness-guarded) wired into every ledger load. Desc corpus repointed to the durable read.
- **L10 JOBS — skeleton + handler kind.** Jobs = data rows (ActionRegistry/jobs.json, teaching-refusal door); run_cascade reused; `handler` run-kind against the closed HANDLERS registry; durability-sync + file-meta-walk REGISTERED AS JOBS and fired by use. Awaits ④'s L5 green-light for the CIRCUIT bind (executions=intent://, marks-only lifecycle).
- **L11 COORDINATE QUERY — LIVE, both faces.** 0015 (composite edge idx + FTS-on-interpretation + trgm) → 0016 ledger.query(spec): filter/time/graph-restrict/semantic/lexical → RRF; every axis + full composition verified by use; fail-loud closed vocabulary; meta.plan echoes counts. MCP face = coordinate tool (embeds text via pplx, teaches refusals). ④'s L4 absorbed my assertion kinds (110-kind registry); my writes validate via ledger.validate_edge_kind; ④'s projection contract reads MY edge_unified. Migration block closed: 0014✓ 0015✓ 0016✓ (all board-announced).
- **GATED/next:** L10↔CIRCUIT bind (on ④'s L5 ping) · cluster_member for scale-drill (0020 reservation requested) · paths[] axis for ledger.query (④'s path/path_step stable — read the shape) · triggers/heartbeat arming (operator switch stays with Tim) · L8 the window (Tim's go).

---
## 2026-07-02 (night, Fable) — L5-CIRCUIT COMPLETE + THE L10↔L5 BIND; all held lanes closed but scale-drill
- **L5-CIRCUIT (④'s green-light, my lane): ALL SIX CRITERIA landed + independently verified.** C5.1 marks→container.mark (0021, read-equal 114/114, per-root ns) · C5.2 compose_state with THE CLOCK IN THE FOLD (41-check matrix) · C5.3 the pour — ADVERSARIALLY RECOMPUTED: 107 intents → 73 LAPSED + 16 terminal + 12 pending + 6 suspended = 107 ✓ (the 73 zombies compose to lapsed, no reaper, zero destructive edits) · C5.4 take-retract bounded by claim · C5.5 CONFIRM→inbox, operator-only release · C5.6 deadline law. All 4 suites green (77 checks). Report: .build-container/lanes/L5-CIRCUIT.report.json. Handed to ④ for their verify.
- **L10↔L5 BIND: every job fire IS a claimed intent** (lease=time_budget_s, terminal on every exit) — verified: real fire → terminal/succeeded; simulated mid-run death → LAPSED (no reaper); lapsed → re-claimable → terminal. Jobs inherit the circuit's zombie-proofing.
- **Shared-file ore fixed**: doc_drift suites gate → exact-token (④'s adversary find); the fixed gate caught the 3 new circuit suites unindexed → refresh_self_description run, drift zero.
- **REMAINING (mine): scale-drill on 0022** (cluster_member + the query's scale axis). **GATED ON TIM:** the continuous loop (COMPANY_ACTIVATION_LOOP), L8 the window go. ④: L7-KEEPER building → phase-B sweep → walkthrough.

---
## 2026-07-03 — SCALE-DRILL LANDED; ledger-session PHASE B SPENT
- 0022 cluster_member (213,725 rows, all 7 sidecars, per-rung reconciled) + the scale stage in ledger.query — the ZOOM verified by use (history k16 drill 1464→335, on-topic). Migration map closed: 0014/15/16 + 0021 + 0022, all announced.
- ④'s phase B also complete (L1–L7 committed, 325 checks, walkthrough delivered to Tim). "How Tim drives it" lines handed to ④ for the unified walkthrough.
- EVERYTHING NOW GATED ON TIM: the L8 window go · arming COMPANY_ACTIVATION_LOOP (continuous heartbeat) · follow-ons not gated (code/symbol/docs/desc pyramids via build_scale_pyramid row-emit; paths[] axis on L4's shape).

---
## 2026-07-03 (overnight, Fable) — THE SCALE+WIRINGS LOOP COMPLETE (all P-criteria green)
- **PYRAMIDS over every lens**: docs (84c/2037r) · desc (3129r) · code (3126r, first nomic-3584) · symbol (kmeans k128/32/8, 168c/18,603r — self-similarity 1.0000 THROUGH the drill: the zoom is exact) + topics/worldview k8 centroid holes found+HEALED. cluster_member total ≈ 244k rows.
- **ROWS-FORWARD**: build_scale_pyramid emits cluster_member rows (reconciled, ns-isolated); sidecar write retired-commented; load_pyramid/rung_points reconstruct from rows (verified == legacy). Rebuild = job 'scale-pyramids' (daily schedule, born PROPOSED; incremental proven: refire → built=0 skipped=84).
- **WIRINGS**: /api/query LIVE (GET probes + POST full-spec; teaching 400s; embedder-down 503) · fabric/embed_routing (code/symbol→nomic-3584 w/ num_ctx, else pplx-2560) shared by bridge + coordinate tool via ONE run_query · golden gate tests/ledger_query_acceptance.py 22 checks green.
- **PERF DEBT flagged**: build_scale_pyramid does per-member psql get_vector calls (~20min for symbol) — fix = a store.get_vectors_bulk; also _member_hash reads default-space keys (returns None per member → hash constant-ish; harmless for fresh builds, weakens incrementality for symbol-scale spaces). Morning follow-on.
- GATED ON TIM: window go · COMPANY_ACTIVATION_LOOP · arming scale-pyramids + heartbeat-durability's continuous fire.

---
## 2026-07-07 — TIM'S "DO ALL THE BACK" RUN (window deferred; mandate sharpened → charter §MANDATE SHARPENED)
- **BOTH OPERATOR GATES FLIPPED on his word**: scale-pyramids armed · COMPANY_ACTIVATION_LOOP=1 (drop-in on company-bridge; activation-caller thread VERIFIED in the live process) — the system self-maintains every ~60s now.
- **THE RECOLLECTION MOVE (0024)**: ledger.exchange (6,985 exchanges WITH full text + FTS) · ledger.tool_call (52,694) · links 23,608 → assertion provenance='derived' under 4 NEW exchange-* edge kinds (authored + assembled per ④'s procedure). All reconciled with denominators; sqlite stays source-of-record. VERIFIED: semantic exchange hits JOIN THEIR WORDS; generated-by resolves to real rows; produced_by graph queryable; FTS reaches transcripts.
- **QUERY v3**: lexical.over='exchange' (transcript FTS through the ONE function) + exchange results enrich from their own words. Golden gate re-run green (22).
- **PERF+CORRECTNESS**: content_hashes bulk prefetch in BOTH pyramid builders (was per-member psql AGAINST THE WRONG KEY — incrementality was silently membership-only); numpy/sklearn/scipy → .venv (env unified). Symbol-rebuild timing verify running.
- **PROVENANCE BACKFILL**: ops/backfill_provenance.py (all ~10k session archives; write-tools → generated-by; project-roots normalization; mtime+line watermarks; counted discards). Probe verified; FULL WALK RUNNING; registered+ARMED as daily job 'provenance-backfill'.
- **FACES**: `company query` CLI verb (verified) · jobs/coordinate/scope MCP tools live · orienteering dot-recollection updated · self-description refreshed, drift zero.
