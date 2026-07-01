# Loop status — embedding/memory unification (live)

*Updated each tick so the next tick (and Tim) resume cleanly. Criteria: COMPLETION_CRITERIA.md.*

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
