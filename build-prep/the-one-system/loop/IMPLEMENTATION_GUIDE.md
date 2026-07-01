# Implementation Guide — embedding/memory unification (overnight loop)

*HOW to make each criterion true. Read RESEARCH_SYNTHESIS.md + EMBEDDING-MEMORY-SUBSTRATE.md first. Principles are load-bearing — they encode this session's hard-won lessons; don't "improve" past them.*

## Principles (why, not just what)
1. **Connect, don't rebuild.** The grammar is one (`contracts/address.py`), the embedder is shared (:8007 pplx), the scale pyramid exists (`runtime/scale.py`), the provenance join is built (recollection crossings). Every new file is a warning sign — search for the existing equivalent first (principle 2 of loop-prep).
2. **Detect, never silently truncate** (the session's core lesson). ollama's default embedding `num_ctx` is ~4096 and silently truncates — ALWAYS pass `options.num_ctx=32768` and check `prompt_eval_count` to detect the real ceiling; flag over-window items, never store a truncated (lying) vector. Same discipline for any model call.
3. **Deterministic work to code, judgment to models.** A join / count / set-diff is code's job (exact). Only no-oracle judgment (what does this mean) goes to a model, asked pointed + bounded + fed (never open-exhaustive-over-large — the dragnet lesson).
4. **Additive over destructive, especially unattended.** Overnight, only APPLY additive/safe work; DRAFT anything that moves the live store or changes system-wide addresses. A wrong overnight mutation with no one watching is the worst outcome — when unsure, draft + NEEDS-TIM.
5. **Lean on the DB.** It wedged twice under heavy parallel passes. Batch (≤32), one connection, transactional; never a fan of parallel heavy queries.

## Group E — finish the embedding leaves
- **E1 docs:** `ops/build_embeddings.py --space docs`. It already routes docs through the fabric/pplx path (batched 16, char pre-filter at the real 32768-token window since pplx's custom server can't report tokens). Confirm pplx is up (`:8007/v1/models`); if down, `systemctl --user restart company-embed-pplx.service` (the override raising it to 32768 is at `~/.config/systemd/user/company-embed-pplx.service.d/override.conf`). Verify with `--space docs --query "..."`.
- **E2/E3:** query `ledger.symbol_latest` for symbols whose `parent_path` ∈ {the 4 giants}; confirm each is in the `symbol` vector space (via `store.get_vector(space_address(code_id,'symbol','nomic-code'))`). Reconcile corpus totals: embedded + flagged + empty == corpus size, per `ops/build_embeddings.py` output.
- FILE ROLES: `ops/build_embeddings.py` (MODIFY only if adding a verifier subcommand; keep the SPACES registry shape — add a space = add a row). REUSE `store/vector_index.py` + `store/fs_store.py` (import, never copy).

## Group P — activate the provenance spine (the highest-value connect)
- **Principle:** the transcripts are the root; the join re-anchors generated code to its genesis. It's BUILT + VERIFIED on live data, just never run (`links=0`).
- **P1 sequence:** (1) locate the crossings runner in `~/recollection` (crossings.ts + its CLI in `cli/`; the survey found the builder + `test/crossings.test.ts`). (2) Run it against the live `.recollection` store (`RECOLLECTION_CONFIG_DIR=/home/tim/company/.recollection`). (3) Confirm `links > 0` in the sqlite DB (`.recollection/conversation-index/db.sqlite`, table `links`). (4) If it needs the tool_call→file_path extraction, that's `JSON_EXTRACT(tool_input,'$.file_path')` on Write/Edit rows (99.99% populated per MERGE-INTENTION). DON'T re-embed; this is a mechanical graph build.
- **P2 sequence (ledger↔genesis):** for a ledger code file `code://company/<path>`, map to `file://<abs-path>` (abs = `/home/tim/company/<path>`), look up the crossings `file://` node → its `produced_by` `exchange://` edges → the exchange's session + ts. Do this READ-ONLY (a query across the two stores). If landing in the ledger: add an additive edge kind (`generated-by`) — `code://company/<path> → exchange://<sid>/<i>` — via a small ops script, batched, transactional. Do NOT rewrite any existing address.
- **DO / DON'T:** DON'T guess a path-join when a file maps ambiguously (moved/renamed) — record it NEEDS-TIM. DON'T parse `tool_result` (unparsed by design; flag, don't invent). DON'T run recollection's distill/embed pipelines that would re-embed at scale unattended without confirming they're additive + bounded.

## Group V — query/verification surface
- Build (or extend `ops/verify_extraction/` style) a small `ops/embed_status.py`: iterate the FsStore `vectors/` records grouped by `(space, emb, dim)`, print counts + one `query_index` top-k per space. REUSE `store.space_matrix`/`query_index`. Keep it a READ.
- V2 cross-scale: `code://company/<path>` (file space) ↔ `code://company/<path>::<symbol>` (symbol space) — the addresses already nest, so "children of a file" = symbol-space keys sharing the path prefix. Demonstrate with one file.

## Group S — Supabase draft (build toward B, do NOT apply)
- **S1:** `select name,default_version,installed_version from pg_available_extensions where name='vector';` (read-only).
- **S2 schema draft** — the hard problem is multi-DIM (pgvector columns are fixed-dim). Options to lay out (recommend, don't unilaterally pick): (a) one table per (space,model) with a typed `vector(N)` column; (b) one `embeddings` table with a `dim`+`model`+`space` tag and the vector in a per-dim partition/child table; (c) separate `vector(3584)`/`vector(2560)`/`vector(1024)` columns nullable. Map recollection's `fingerprints (unit_id, space, model, dim, metric, source)` — it already has the right columns — as the row shape. Every open call → NEEDS-TIM/Glyphic marker. Write the migration to a FILE under `migrations/` or the draft doc; do NOT `apply_migration`.
- **S3 code:// reconciliation** — enumerate the 3 forms (see EMBEDDING-MEMORY-SUBSTRATE.md), propose the ledger form canonical, list EVERY consumer that would change (corpus repo space, `resolve_scope`, the S3 surface) and what each PRESERVES. Plan only.

## Group C — coordinate
- Each tick: `cc_channel(op="mail", thread="t-1782921350-ch-518m76r0")`. If a reply from `ch-518m76r0` exists, incorporate their models/dims/store choices into S2 and `cc_channel(op="send", to="ch-518m76r0", thread=..., message="converged: ...")`. If none, proceed; ping at most once per few ticks.

## What every change PRESERVES (enumerate before committing)
- The live ledger runs + the extraction pipeline (untouched — this loop reads the ledger, adds at most additive edges).
- recall + recollection + corpus continue working (shared :8007 embedder untouched; recollection sqlite read/appended, not restructured).
- The FsStore vector spaces already built (code/symbol/extractions/…) — additive; the Supabase work is DRAFT, so FsStore stays the live store until the agreed migration.
- The live brain / services (never restarted by this loop; pplx already up at 32768).
