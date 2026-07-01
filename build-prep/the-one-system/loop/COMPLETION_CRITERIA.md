# Completion Criteria — embedding/memory unification (overnight loop)

*The truth-table for the unattended overnight build. Mission: **A** (activate the provenance spine) **+ D** (run it as a sequenced program) **building toward B** (the one Supabase store) — connecting the already-built pieces, not rebuilding. Coordinate with the Glyphic fabric session throughout.*

## Verification rules (READ FIRST — the loop follows exactly this)
- **FUNCTION bar:** verified BY USE on REAL data — run the query/join and show real rows/results, never "the code looks right." No stubs, no partial.
- **DATA-FACE bar** (the FORM analogue for this backend/data work — there is no UI surface here): every produced record is **addressed** (a scheme from `contracts/address.py`), **honest** (no silent truncation/skip — a limit is DETECTED + recorded, per the nomic num_ctx lesson), **queryable** (retrievable by a real query), and **navigable not a dump** (grouped/counted/related, not a flat text wall). A result is green only when BOTH faces hold.
- **Standing laws:** everything fails loud (record or raise, never drop) · through the Company's own tools/CLI/stores, not bespoke parallel systems · no confidence floats (tags + counts) · DB is Supabase :15432 · lean on the DB (it wedged before under heavy passes — batch, don't swamp).
- **TIM'S DECISIONS (2026-07-02 — now AUTHORIZED, no longer draft-only):**
  1. **Canonical `code://` = the LEDGER form** `code://<project>/<path>::<symbol>`. APPLY the reconciliation: migrate the corpus `repo` space + `resolve_scope`/S3 surface to it. (My embeddings already use it.) Do it **additive→verify→cutover** (add the new-form records/resolver path, verify, then retire the old form) — never a blind rename; enumerate what each step preserves.
  2. **Supabase = FULL MIGRATE tonight.** APPLY: enable pgvector on :15432, create the shared vector schema, move ALL vector spaces (FsStore + recollection sqlite) onto Supabase. **SAFETY: additive→verify→cutover — copy into Supabase, verify counts + a real query match the source, and KEEP FsStore/sqlite as the source-of-truth fallback until verified; never delete the source in the same pass.**
  3. **Descriptions = CARRY-FORWARD + DELTA.** APPLY (Group D): reuse the 3061 unchanged `what_it_does` (source_hash match from run 3f923cdb) + re-run the model on the ~341 changed/new files; then it unlocks the description-embedding space.
- **STILL unattended-safe discipline:** never restart the live brain; batch DB work (it wedged before); everything fails loud / no silent truncation; commit per criterion; coordinate the Supabase SCHEMA specifics (multi-dim strategy) with Glyphic via the thread but PROCEED with best judgment (full-migrate is authorized) — only mark `NEEDS-TIM` for a NEW decision not covered above, never guess on those.
- **Commit protocol:** commit per criterion as it goes green (on `main`, the repo's commit law + co-author trailer). Track everything.
- **Verify by:** `PGPASSWORD=postgres psql -h 127.0.0.1 -p 15432 ...` for the ledger; `ops/build_embeddings.py --query` for spaces; `.venv/bin/python` (not vllm-env) for repo code; `/home/tim/vllm-env/bin/python` only for numpy/embedding scratch.

## Priority order (dependency-first)
E (finish embedding leaves) → D (restore descriptions) → P (activate provenance spine) → V (verify/query surface) → S (Supabase migrate + code:// reconcile — APPLY, build toward B) → C (coordinate) — with C checked every tick. Rationale: finish/restore the DATA (E,D) so the migrate (S) moves a complete store; activate provenance (P) + verify (V) before cutover; migrate last so it moves a verified whole.

## Group D — restore the interpretive descriptions (APPLY — Tim: carry-forward + delta)
- **D1 · carry-forward unchanged descriptions** — the 3061 files whose source_hash matches the old described run (3f923cdb) get their `what_it_does` (+ concerns/standouts/etc. interpretive fields) copied onto the new latest run's entries.
  FUNCTION — a SQL update-join lands 3061 descriptions on the new run; a count confirms.  ☐ by use
  DATA-FACE — carried fields keep their provenance (interp_model/interp_at from the source run); no fabrication.  ☐ by use
- **D2 · re-interpret the delta** — the ~341 changed/new files (no source_hash match) get freshly described via the interpretive pipeline (`ops/ledger_interpret_producer.py`, scoped to the delta, bounded/fed per the model-envelope lesson — chunk giants, don't dump).
  FUNCTION — the ~341 get real `what_it_does`; combined with D1, the new run's code files are ~100% described.  ☐ by use
  NOTE — if a giant file (>window) can't be described whole, describe from its symbols (the symbol-scale chunking answer), don't truncate. Model choice: the resident local brain or kimi; bounded pointed prompts.
- **D3 · description-embedding space** — build a `desc` space (pplx) embedding each code file's `what_it_does` (Tim's "descriptions of code files, embedded differently from markdown").
  FUNCTION — `desc` space built; `--query "<plain-language capability>"` returns the right code files.  ☐ by use

---

## Group E — finish the embedding leaves (SAFE, additive)
- **E1 · docs space** — the pplx doc-content space is built over the new run's real markdown.
  FUNCTION — `ops/build_embeddings.py --space docs` completes; N doc vectors persisted; re-run skips unchanged (incremental).  ☐ by use
  DATA-FACE — each doc addressed `code://company/<path>`; oversize (>real window) FLAGGED not truncated; `--query "<x>"` returns sensible docs.  ☐ by use
- **E2 · giants covered by symbol-scale** — the 4 file-level giants (suite/bridge/cognition/useAppController) are confirmed covered at symbol scale (their functions embedded whole).
  FUNCTION — query the `symbol` space; confirm symbols from each giant file are present + retrievable.  ☐ by use
  DATA-FACE — a count per giant of its embedded symbols; the file-level flag cross-references the symbol coverage (honest, navigable).  ☐ by use
- **E3 · no silent truncation anywhere** — re-audit both code spaces: every stored vector's source was within the model window at embed time (detection held); every over-window item is in a flagged list, not stored as a lie.
  FUNCTION — a query over the vector records + the flagged list reconciles to the corpus count (embedded + flagged + empty = total). ☐ by use

## Group P — activate the provenance spine (SAFE, additive — the A in A+D)
- **P1 · run the built-but-dormant crossings/provenance join** — recollection's crossings (`~/recollection` crossings.ts) OR the equivalent `tool_call.file_path → exchange://` join is RUN, producing the `file:// →produced_by→ exchange://<sid>/<i> →contains→ session://` links that are currently `links=0`.
  FUNCTION — after the run, the link count is > 0 on real data; a spot query ("what exchange produced file X") returns a real exchange.  ☐ by use
  DATA-FACE — links are addressed edges (the shared grammar); counts reported by kind; NO silent drops (unparsed tool_results recorded, not ignored).  ☐ by use
  NOTE — if the join must land in the ledger (not just recollection's sqlite), add it as an additive edge kind (`generated-by` / `produced-in`) from `code://company/<path>` → `exchange://<sid>/<i>`. Additive only.
- **P2 · connect a ledger code node to its genesis** — demonstrate the end-to-end axis: pick a real code file, resolve it through the provenance join to the exchange/session that generated it.
  FUNCTION — for ≥5 real ledger code files, output the generating `exchange://` + timestamp + session.  ☐ by use
  DATA-FACE — presented as a navigable mapping (file → exchange → session → time), not a raw dump.  ☐ by use
  NOTE — needs a `file://<abs-path>` ↔ `code://<project>/<path>` path-join; implement the join READ-ONLY (don't rewrite addresses). If the path-join is ambiguous, record the ambiguity (NEEDS-TIM), don't guess.

## Group V — the query/verification surface (SAFE)
- **V1 · every space is queryable + honest** — a single verifier reports, per space (code/symbol/docs/extractions/history/repo/…): vector count, dim, emb-layer, and a sample query result.
  FUNCTION — `ops/` verifier prints the per-space table on real data.  ☐ by use
  DATA-FACE — counts + models + a real top-k per space; flagged/oversize/empty surfaced; reads as a navigable status, not a wall.  ☐ by use
- **V2 · cross-scale navigation** — demonstrate file↔symbol scale movement: from a file-level hit, list its symbol-level children (and vice versa) via the shared address (`code://<path>` ↔ `code://<path>::<symbol>`).
  FUNCTION — a query returns a file and its embedded symbols as a scale-linked set.  ☐ by use

## Group S — migrate to the Supabase store + reconcile code:// (APPLY — Tim authorized full migrate)
- **S1 · pgvector enabled** — `vector` extension available + enabled on :15432.
  FUNCTION — `create extension if not exists vector` succeeds; version recorded.  ☐ by use
- **S2 · shared Supabase vector schema APPLIED** — the schema holding multi-dim (nomic 3584 / pplx 2560 / bge 1024), space/scale, emb-layer, content_hash, canonical source-address (ledger form), + pyramid rungs. Also write it up in `build-prep/the-one-system/SUPABASE-VECTOR-SCHEMA.md` for Glyphic.
  FUNCTION — the schema is created in Supabase; a test insert+query round-trips a vector.  ☐ by use
  DATA-FACE — one store, addressed by the shared grammar; multi-dim handled (per-dim column/table); every space representable.  ☐ by use
  COORDINATE — fold Glyphic's models/dims if they reply; else proceed with nomic/pplx/bge (the known set).
- **S3 · migrate all vector spaces → Supabase (additive→verify→cutover)** — copy every FsStore space (code/symbol/docs/desc/extractions/history/repo/topics/code_archaeology + scale rungs) AND recollection's fingerprints into Supabase; verify counts + a real query match the source; then make Supabase the read path. KEEP FsStore/sqlite until verified.
  FUNCTION — per space: source count == Supabase count, and a `query` returns matching top-k from Supabase.  ☐ by use
  DATA-FACE — no silent drops; a reconciliation table (space: source_n / supabase_n / match) proves completeness.  ☐ by use
- **S4 · canonical code:// reconciliation APPLIED (additive→verify→cutover)** — migrate the corpus `repo` space + `resolve_scope`/S3 to the ledger form `code://<project>/<path>::<symbol>`; add the `file://`↔`code://` path-join for provenance. Enumerate what each step PRESERVES.
  FUNCTION — the corpus/repo addresses + resolve_scope resolve on the ledger form; a spot query proves the S3 join still works.  ☐ by use
  NOTE — additive first (accept both forms), verify the surface still resolves, THEN retire the stem form. If any consumer can't migrate cleanly, record it + keep the alias — never break the live surface.

## Group C — coordinate (check EVERY tick)
- **C1 · Glyphic reply folded in** — each loop tick, `cc_channel(op=mail, thread="t-1782921350-ch-518m76r0")`; if they replied, fold their models/dims/store + reactions into the schema draft (S2) and reply with the converged direction.
  FUNCTION — reply detected → schema updated + acknowledged; no reply → a status ping left at most once, then proceed.  ☐ by use

## NEEDS-TIM (surface, never guess)
- Canonical `code://` form (ledger vs stem) — system-wide, touches S3. Draft only.
- Apply Supabase migration + move the live store off FsStore — the one big build; needs the schema agreed with Glyphic.
- Interpretive-layer re-run (carry-forward 3061 + ~341 delta) — feeds a description-embedding space; separate decision (DETERMINISTIC-PASS-GAP-ANALYSIS.md).
