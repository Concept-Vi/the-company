# Resume point — query / visualise / embeddings / Company UI (Tim 2026-06-30)

*Written before a conversation compression. Next session direction (Tim): "ways for you to query it, ways to visualise it, we'll talk about embeddings and a Company UI for it."*

## Live state at checkpoint
- **Extraction audit RUNNING** at true 32-wide (the gate fix landed). ~220/1065 done, ~449 rows in `ledger.coverage_findings`, resumable (`ops/extraction_audit_run.py --concurrency 32`). Some `err` (~9%) = oversize/transient — re-runnable (resume skips done). Expect completion in ~30–40 min from checkpoint.
- **Near-universal flagging** so far (almost every file flagged, 0 passes) → the extractor has broad gaps; JS/JSX worst (early signal).

## Where the data lives (for querying/visualising)
- **`ledger.coverage_findings`** (Supabase :15432): `entry_id, project, path, file_kind, complete(bool=PASS), findings(jsonb: [{discrepancy_type(enum: in_contract_not_extracted|in_file_not_in_contract|wrong_in_extraction|other), name, symbol_kind, location, detail}]), kind_seen, run_addr, ts`. Joinable to `ledger.entry`.
- The ledger proper: `ledger.entry` (files: what_it_does, symbols counts via `signals`, metadata via `file_meta`, declares/imports), `ledger.symbol`, `ledger.edge` (deterministic + 3339 fact-edges), `ledger.run`/`latest_run`.

## The immediate analysis to run when the pass completes
- **Failure-class map:** `select discrepancy_type, file_kind, count(*) from ledger.coverage_findings cf, jsonb_array_elements(cf.findings) f group by f->>'discrepancy_type'... ` → which extractors are weak, by language. Drives the root extractor fixes (the loop: fix extractor → re-extract → re-audit → confirm).

## Next-session topics (Tim's stated direction)
1. **Query it** — likely via the Company's MCP tools (find_relations, corpus, node, list_by_type, inspect_address) + SQL; design a queryable face over coverage_findings + the ledger. Stay in-system (MCP/CLI), not bespoke.
2. **Visualise it** — a way to SEE the failure-class map + the ledger graph (tree/graph/filter/zoom — the dual interface for Tim AND the Company). Recognition-level.
3. **Embeddings** — the proximity layer (text + code embedders; Tim holds which) — deferred topic, he'll lead it.
4. **A Company UI** — the front that renders the ledger + findings for Tim's eye; projected surface (MCP tools, UI, company) as the constant map.

## Standing principles (carry through compression)
- No confidence — tags+counts (G16). [[no-confidence-tags-and-counts]]
- Through MCP tools + CLI, not bespoke code. [[prefer-mcp-tools-and-cli-over-direct-code]]
- This whole process reflects into Company operations later (reusable, generalised, automated). [[process-reflects-into-company-operations]]
- The ledger is the dual interface + the seed the unified system grows from. [[the-one-system-resume-point]]
- Full build/integration requirements: `COVERAGE-AUDIT-BUILD-SPEC.md`; 4B/throughput learnings: `4B-FINDINGS.md`.
