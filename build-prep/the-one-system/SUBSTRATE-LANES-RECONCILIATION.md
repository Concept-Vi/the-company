# Substrate lanes ↔ ④ THE CONTAINER — reconciliation (ch-5wog4hmx, 2026-07-02)

*How the ledger-substrate session's three builds slot into ④'s L1–L7 lanes so this stays ONE system.
Pending ④'s answers (migration numbers, gap-ownership, circuit-as-job-home — board://item-d47933e2).
This is the substrate session's read; ④ is the authority on its own lanes and may correct it.*

## The three builds vs ④'s lanes

### 1. SUPERSESSION FIX — a GAP ④ also needs → propose as a new lane **L0.5 · DURABILITY** (mine to own)
- **What:** side tables `ledger.interpretation` (keyed `(address, source_hash)`) · `ledger.file_meta` (`(project,path)`) · `ledger.assertion` (run-independent edges, e.g. generated-by) + read views `unit_latest` / `edge_unified`, so descriptions/provenance survive run-rebuilds instead of being stranded below `*_latest`.
- **Why it's a gap:** ④'s L1 SPINE adds `ledger.entry.project_id` (C1.4) but nothing in L1–L7 makes ENRICHMENT survive a new run. SPINE (reads project labels), CIRCUIT/BOARD (read addressed content), KEEPER (composes territory from ledger data) ALL read enrichment — if a rebuild strands it (proven live: 4,199 descriptions + 1,403 provenance edges silently dropped, interim carry-forward applied), ④'s own data rots under it.
- **Collision:** schema-additive (NEW tables + views); does NOT alter ledger.entry (that's ④'s SPINE). Only shared risk = migration NUMBER. **BLOCKS on ④'s answer.**
- **Foundational-for:** the heartbeat's contract (a rebuild must not reduce enrichment coverage) + the coordinate query (time/provenance axes read these tables).

### 2. PARAMETRIC JOBS + HEARTBEAT — COMPOSES WITH L5 CIRCUIT (a layering, not a collision)
- **The seam:** CIRCUIT (L5) is the consequential-action floor — Principal→Delegation→Intent→Proposal→take-mark→claim→terminal→operator-resolve. JOBS are the trigger/registry layer that sits ABOVE it: a job is a data row (what-to-run · params · trigger · allocations); it fires → runs a cascade → **any consequential step routes through CIRCUIT's propose→resolve** (the job floor IS circuit). Non-consequential jobs (the heartbeat: re-extract/re-embed) just run.
- **File-disjoint:** new files `runtime/jobs.py` · `mcp_face/tools/jobs.py` · `.data/store/jobs.json` — ④'s L5 touches marks/circuit files. No merge collision.
- **Reconcile with ④:** is CIRCUIT's mark-lifecycle the intended home for job EXECUTION state (claim/lease/heartbeat marks)? If yes, `run_job` records execution as circuit marks rather than a parallel run record. Asked on the board.
- **The skeleton (buildable NOW, zero schema):** job registry + `build_job` door + `run_job` over the EXISTING cascade step vocabulary + `jobs` MCP tool, manual-fire only. Reuses `run_cascade` (doesn't fork it). No triggers, no consequential routing yet → independent of CIRCUIT → safe to build before L5.

### 3. COORDINATE QUERY `ledger.query(spec)` — IS the engine behind ④'s projection contract
- ④'s L4 C4.7 ("the projection contract emits paths[]/clusters/edges/spine/ghosts") + L8 C8.1 (the window renders containment/edges/spine/ghosts/paths/zoom/time/provenance) NEED a multi-axis read. My `ledger.query(spec jsonb)` (one PL/pgSQL fn, both faces) should BE that engine, not a parallel query path.
- **Depends on:** L0.5 (time/provenance axes) + L4 (edge_kinds registry, path/path_step) + the scale rungs. So it builds AFTER supersession + alongside/after L4.
- **Reconcile:** align the spec's return shape to ④'s projection-contract shape so the window consumes one function.

## Migration-number reality (why I must ask, not assume)
- Files in `build-prep/claude-design/supabase/supabase/migrations/`: `0011_ledger.sql`, `0012_ledger_interpretive.sql` exist. ④'s plan names `0012_container.sql` — **0012 is already taken** by ledger_interpretive, so either ④'s is a different path or a real conflict.
- `ledger.embedding` (my ① work) has **no tracked migration file** — the live DB (:15432) and the migration files have already diverged. Any new schema must reconcile: pick the next free number AND land against the live DB. **This is exactly what I'm holding for.**

## Build order (this session)
1. **NOW (no schema):** the jobs walking-skeleton (registry + door + run_job + tool, manual-fire).
2. **On ④'s migration answer:** L0.5 supersession (retire the interim carry-forward once the durable tables land).
3. **After L0.5 + L4:** `ledger.query(spec)` as the projection-contract engine.
4. Triggers + heartbeat once the skeleton + L0.5 are proven; consequential routing once CIRCUIT (L5) lands.
