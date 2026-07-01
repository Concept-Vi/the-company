# Completion Criteria — embedding/memory unification (overnight loop)

*The truth-table for the unattended overnight build. Mission: **A** (activate the provenance spine) **+ D** (run it as a sequenced program) **building toward B** (the one Supabase store) — connecting the already-built pieces, not rebuilding. Coordinate with the Glyphic fabric session throughout.*

## Verification rules (READ FIRST — the loop follows exactly this)
- **FUNCTION bar:** verified BY USE on REAL data — run the query/join and show real rows/results, never "the code looks right." No stubs, no partial.
- **DATA-FACE bar** (the FORM analogue for this backend/data work — there is no UI surface here): every produced record is **addressed** (a scheme from `contracts/address.py`), **honest** (no silent truncation/skip — a limit is DETECTED + recorded, per the nomic num_ctx lesson), **queryable** (retrievable by a real query), and **navigable not a dump** (grouped/counted/related, not a flat text wall). A result is green only when BOTH faces hold.
- **Standing laws:** everything fails loud (record or raise, never drop) · through the Company's own tools/CLI/stores, not bespoke parallel systems · no confidence floats (tags + counts) · DB is Supabase :15432 · lean on the DB (it wedged before under heavy passes — batch, don't swamp).
- **SAFETY — unattended scope.** APPLY only additive/safe work. **DRAFT (do NOT apply)** anything that: moves the live store, changes the canonical `code://` system-wide, or touches the S3 surface — those await Glyphic + Tim. Never restart the live brain. If a criterion needs a decision you can't safely make, mark it `NEEDS-TIM` with the specific question — never guess.
- **Commit protocol:** commit per criterion as it goes green (on `main`, the repo's commit law + co-author trailer). Track everything.
- **Verify by:** `PGPASSWORD=postgres psql -h 127.0.0.1 -p 15432 ...` for the ledger; `ops/build_embeddings.py --query` for spaces; `.venv/bin/python` (not vllm-env) for repo code; `/home/tim/vllm-env/bin/python` only for numpy/embedding scratch.

## Priority order (dependency-first)
E (finish embedding leaves) → P (activate provenance spine) → V (verify/query surface) → S (draft Supabase — build toward B) → C (coordinate) — with C checked every tick.

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

## Group S — build toward the Supabase store (DRAFT — the B; do NOT apply)
- **S1 · pgvector availability checked** — is `vector` extension available in the local Supabase (:15432)? Record yes/no + version.
  FUNCTION — `select * from pg_available_extensions where name='vector'` result recorded.  ☐ by use  (read-only — safe to run)
- **S2 · shared Supabase vector schema DRAFTED** — `build-prep/the-one-system/SUPABASE-VECTOR-SCHEMA.md` + a migration FILE (not applied) that holds multi-dim (nomic 3584 / pplx 2560 / bge 1024), space/scale, emb-layer, content_hash, canonical source-address, + the pyramid rungs; maps recollection's `fingerprints` schema + the FsStore records onto it.
  FUNCTION — the draft + migration file exist, internally consistent, cover every current space.  ☐ by inspection
  DATA-FACE — the schema is the unification artifact for BOTH sessions; addresses use the shared grammar; NEEDS-TIM/Glyphic markers on every open decision (dim strategy, canonical code://).  ☐
  DO-NOT — do not `apply_migration` / do not move the live store. Draft only.
- **S3 · canonical code:// reconciliation DRAFTED** — `build-prep/the-one-system/CODE-ADDRESS-RECONCILIATION.md`: the 3 forms, the proposal (ledger form canonical), the file://↔code:// provenance join, and the exact S3-surface migration steps — as a PLAN for approval.
  FUNCTION — the doc exists with the precise change-set enumerated + what-it-preserves.  ☐ by inspection
  DO-NOT — do not change the live address scheme or touch `resolve_scope`/the S3 surface.

## Group C — coordinate (check EVERY tick)
- **C1 · Glyphic reply folded in** — each loop tick, `cc_channel(op=mail, thread="t-1782921350-ch-518m76r0")`; if they replied, fold their models/dims/store + reactions into the schema draft (S2) and reply with the converged direction.
  FUNCTION — reply detected → schema updated + acknowledged; no reply → a status ping left at most once, then proceed.  ☐ by use

## NEEDS-TIM (surface, never guess)
- Canonical `code://` form (ledger vs stem) — system-wide, touches S3. Draft only.
- Apply Supabase migration + move the live store off FsStore — the one big build; needs the schema agreed with Glyphic.
- Interpretive-layer re-run (carry-forward 3061 + ~341 delta) — feeds a description-embedding space; separate decision (DETERMINISTIC-PASS-GAP-ANALYSIS.md).
