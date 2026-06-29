# Resume after WSL restart — state snapshot + verification checklist

*Written 2026-06-29 ~00:40, just before Tim's WSL restart (which restarts WSL, Docker, and this session — Tim resumes the same session). This is the durable safety net: verify the DB survived, then continue the staged plan.*

## ① POST-RESTART VERIFICATION (do FIRST, once Docker + DB are back) — lean queries only
The DB was WEDGED (Docker networking) at restart time — NOT corrupted; writes committed before the wedge. Verify:
1. Docker up, DB answers: `psql -h 127.0.0.1 -p 15432 -U postgres -d postgres -c "select 1"`.
2. **Volume on ext4** (couldn't check while wedged — the STORE1b law): `docker inspect supabase_db_supabase --format '{{range .Mounts}}{{.Source}}{{end}}'` — must NOT be under `/mnt/c`.
3. Ledger intact (one guarded query): interpreted files ≈ 4,400+ ; **data-artifact stubs present** (~3,552, `interp_model='excluded:data-artifact'`) ; **remaining-null = 4** (2× `_ds_bundle.js`, `Build.jsx`, `guides/using-skills.py`).
4. Truncation fix held: `runtime/suite.py` (875KB) has a full `what_it_does` (not a 48k-truncated one).
If any of these are wrong → the volume may not have persisted; STOP and tell Tim before re-running anything.

## ② STATE — done & committed (all durable in git)
- **Truncation REMOVED** (3 producers + shared prompt) — whole-file reads, fail-loud on oversize. Verified on bridge.py (273KB). Commit done.
- **Data-artifact exclusion applied** (3,552 stubbed; conversation-archive kept out of interp; design-system substrate KEPT). Classifier predicate recorded in LEDGER-ENRICHMENT-PLAN.md.
- **Kimi redo COMPLETE** — every previously-truncated REAL file re-interpreted at full length (suite.py, bridge.py, the 408KB docs). 4 remain null (the 2 minified bundles = correct fail-loud; Build.jsx = transient retry; using-skills.py = rename drift).
- **Coverage-audit harness** built (`ops/ledger_coverage_audit.py`) — 4B auditor-vs-ground-truth, two passes (with/without contract), tags+counts. DB/prompt tested; live run needs the 4B.
- **Change-detection form** built (`ops/ledger_changes.py`) — added/changed/deleted vs ingestion. Logic fixed (query by project, not purpose). NOT yet run successfully (needs DB + a leanness fix — see ④).

## ③ BLOCKERS needing Tim
- **The local 4B is DOWN** (vllm-chat crashed ~10:09). Running it at the 32-concurrent optimum needs VRAM that `embed-pplx` holds → a loadout decision. Bring up the 4B loadout, then the coverage audit fires.
- (Docker wedge — resolved by the restart.)

## ④ NEXT ACTIONS (the staged plan — sequence)
1. Verify (§①).
2. Retry `Build.jsx` (counterpart-design) via kimi — transient fail.
3. **Make `ledger_changes.py` LEAN** before running: skip hashing data-artifacts/.recollection (the full 15,806-file hash, incl. the 45MB dump, helped wedge Docker TWICE). Then run it — should report the using-skills.py rename as deleted+added (its validation).
4. **Coverage audit** (needs 4B up): `ledger_coverage_audit.py --sample-per-language 8 --pass with`, then `--pass without`; diff → new contract items; blind-spot map by language (expect JS/TS red — F2).
5. **Metadata pass** (#2, schema proposed to Tim 2026-06-29): git temporal facts (created/last-modified/change-count/authors) + per-type measures (word/heading for docs, symbol/import for code, dims for images, record_count for data) → a `file_meta` jsonb. All facts/counts/timestamps (no confidence).
6. **Fact + grounded edge harvesters** (deterministic, no 4B).
7. **Proximity layer** — DEFERRED until Tim hands over the text+code embedders.

## ⑤ STANDING REMINDERS
- **Lean DB/IO ops** — Docker wedged TWICE this session from heavy passes (parallel scans, the 15k-file hash). One heavy pass at a time; guard psql with `statement_timeout`; never stack a tree-walk on a running sweep.
- **No confidence — tags + counts** (G16). **This whole process reflects into Company operations** (write reusable). See memories: [[no-confidence-tags-and-counts]], [[process-reflects-into-company-operations]], [[the-one-system-resume-point]].
