# Research Synthesis — the embedding/memory unification (overnight loop)

*The evidence base. Most of it is already captured in sibling docs; this points to them + adds the loop-specific facts. Ground truth from this session's investigation (2026-07-01/02).*

## Round 1 — the embedding/memory substrate (what EXISTS)
Full map: **`build-prep/the-one-system/EMBEDDING-MEMORY-SUBSTRATE.md`** (read it first). Headlines:
- **Grammar is ONE.** `contracts/address.py` SCHEMES holds `code:// cap:// exchange:// board:// clone:// session:// vec:// file:// project://`, all resolving through `runtime/cognition.py:resolve_address`. Nothing to merge — add citizens.
- **recall** (`runtime/session_recall.py`) = single-session `.jsonl` search, sidecar files, :8007 pplx + :8008 jina. Ephemeral, no store.
- **recollection** (`~/recollection`, sqlite-vec, 8224 exchanges embedded via :8007 pplx 2560/int8) = cross-session memory. Addresses `exchange://<sid>/<i>`. `fingerprints (unit_id, space)` PK = the multi-lens seam. **Distill pipeline + crossings graph are BUILT+TESTED but NEVER RUN** (`links=0`, `units` only `clone-reflection`).
- **corpus/extractions** (`ops/embed_extractions.py`, `runtime/freshness.py`, MCP `corpus`) = FsStore spaces: `extractions`(2994), `history`, `repo`, `topics`, `code_archaeology`, in pplx(2560)+bge(1024).
- **scale pyramid** (`runtime/scale.py`, `/api/scale/build`) = multi-scale UP: agglomerative dendrogram, nested rungs `unit ⊂ fine ⊂ coarse`. Built for `extractions` (`scale:extractions:k512`).
- **projection engine** (`runtime/projection.py`) = axis-projection (θ=kind, r=time).

## Round 2 — my new work (this session, committed)
- `ops/build_embeddings.py`: `code` space (nomic-embed-code 3584, ollama, num_ctx=32768 — killed ollama's hidden ~4096 truncation) = 1038 files; `symbol` space = 6201 symbols (each fn/method/class from its source slice); `docs` (pplx 2560) = **not yet built**. All in FsStore, space-keyed `(space, emb-layer)`, truncation-detected via `prompt_eval_count`, empty-skipped, giants flagged for chunking (not truncated).
- Vector store API: `store/vector_index.py` (`build_index`, `query_index`, `content_hash`, incremental); `store/fs_store.py` (`put_vector`, `get_vector`, `space_address`, `space_matrix`).
- Extraction/ledger (also this session, committed): `ops/ledger_build.py` (real-parser JS/TS, resolver w/ far-classification + endpoint/event seams), `ops/verify_extraction/` (0 symbol misses). Latest ledger run has 0 interpretive descriptions (deterministic-only) — the interpretive layer carry-forward (3061 reusable, ~341 delta) is documented in DETERMINISTIC-PASS-GAP-ANALYSIS.md.

## Round 3 — the master plan (the bigger frame)
`build-prep/episodic-memory-adaptation/MERGE-INTENTION.md`: transcripts (.jsonl) are the ROOT; every generated artefact re-anchors to its genesis. **The provenance join is VERIFIED on live data** (`tool_calls.tool_input→file_path` on 99.99% of Write/Edit; 75k exchanges, 6.7M tool-calls, 7351 sessions) but the cross-system join is not wired. Three memory systems (capture/understanding/consolidation) → one store; the ONE big net-new build = the storage backend (Supabase).

## Round 4 — external/coordination surface
- **Glyphic session** `ch-518m76r0` (fabric): building AI-fusion, touches embeddings, Supabase shared backend. Coordinated via `cc_channel` thread `t-1782921350-ch-518m76r0` — my state + proposed schema/address direction sent; **reply pending**. Check `cc_channel(op=mail, thread=...)` each loop tick; fold any reply into the schema draft.
- **Supabase**: local Docker Postgres 17.6 on **:15432** (NOT 54322), `postgres/postgres`, the `ledger` schema. pgvector availability = a Round-1 check for the loop (see criteria SUP-1).

## Implications (what this means for the loop)
- CONNECT, don't rebuild — everything shares the :8007 pplx lens + the one grammar.
- SAFE to apply overnight (additive): docs space; run the built crossings/provenance join → ledger edges; query-verify; the recollection built-but-unrun pipelines (read-additive).
- DRAFT-only overnight (needs Glyphic + Tim): the Supabase vector schema + migration; the canonical code:// change (touches the S3 surface); the actual FsStore→Supabase data move.
- The code:// format divergence (ledger `code://<project>/<path>::<symbol>` vs contract `code://<file-stem>/<symbol>`) is the join point; provenance uses `file://<abs-path>` → needs a path-join. DRAFT the reconciliation, do not apply.
