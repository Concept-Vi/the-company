# Supabase vector schema — the unified embedding store (2026-07-02)

*The shared pgvector schema both sessions' embeddings land in. Tim authorized the full migrate. Glyphic (ch-518m76r0): react/correct — this is the convergence artifact. Applied to local Supabase :15432, schema `ledger`.*

## The constraints that drive the design
- **Dims in play:** nomic-embed-code **3584** (code/symbol) · pplx-embed-context **2560** (docs/desc/extractions/history) · bge-m3 **1024** (repo/topics legacy). More models coming (Tim: growing model layer).
- **pgvector 0.8.2 ANN-index cap:** `vector(N)` is hnsw/ivfflat-indexable only to **2000 dims**. nomic (3584) AND pplx (2560) BOTH exceed it → plain `vector` would be exact-search-only.
- **Fix: `halfvec(N)`** (fp16) is hnsw-indexable to **4000 dims** — covers all our dims. Precision loss is negligible for cosine ranking (recollection's int8 vectors already verified cosine 0.996 / top-k ~0.97 vs bf16). So halfvec is the right storage type.
- **One grammar:** every row is addressed by `contracts/address.py` schemes (canonical `code://<project>/<path>[::<symbol>]`, `exchange://`, `board://`, …).

## The schema (applied)
```sql
create schema if not exists ledger;
create extension if not exists vector;   -- 0.8.2, enabled

create table if not exists ledger.embedding (
  id             bigint generated always as identity primary key,
  source_address text  not null,          -- shared-grammar address of the embedded item
  space          text  not null,          -- code | symbol | docs | desc | extractions | history | repo | topics | ... | scale:<space>:k<N>
  emb_layer      text  not null,          -- nomic-code | pplx | bge  (the model lens)
  model          text  not null,          -- full model id
  dim            int   not null,          -- 3584 | 2560 | 1024
  content_hash   text  not null,          -- incremental: skip re-embed when unchanged
  -- one per-dim halfvec column is populated per row (the others NULL). Fixed-dim columns are what pgvector
  -- indexes; a per-dim column keeps every model ANN-indexable in ONE table (vs a table-per-model sprawl).
  vec_3584       halfvec(3584),
  vec_2560       halfvec(2560),
  vec_1024       halfvec(1024),
  ts             timestamptz default now(),
  unique (source_address, space, emb_layer)
);

-- partial HNSW cosine indexes, one per dim (only the populated rows)
create index if not exists embedding_h3584 on ledger.embedding using hnsw (vec_3584 halfvec_cosine_ops) where vec_3584 is not null;
create index if not exists embedding_h2560 on ledger.embedding using hnsw (vec_2560 halfvec_cosine_ops) where vec_2560 is not null;
create index if not exists embedding_h1024 on ledger.embedding using hnsw (vec_1024 halfvec_cosine_ops) where vec_1024 is not null;
create index if not exists embedding_space on ledger.embedding (space, emb_layer);
```

## Why this shape (rationale for Glyphic)
- **One table, per-dim columns** (not table-per-model): a new model = a new `emb_layer` value (+ a vec_<dim> column if a new dim) — "add a row/value, not a table." Query filters by `space`+`emb_layer`; ANN via the matching per-dim index. Mirrors recollection's `fingerprints (unit_id, space, model, dim, metric, source)` — same columns, promoted to pgvector.
- **halfvec** so EVERY model (incl. 3584/2560) is ANN-indexable — the whole point of moving off FsStore brute-force.
- **content_hash** carries the FsStore/build_index incremental contract forward.
- **scale rungs** (`scale:<space>:k<N>`) are just more `space` values — the pyramid lands here too.

## Migration (S3, additive→verify→cutover)
1. Copy each FsStore space (code/symbol/docs/desc/extractions/history/repo/topics/code_archaeology + scale) → `ledger.embedding` rows.
2. Copy recollection's `fingerprints` (sqlite) → rows (emb_layer=pplx, space per unit_type).
3. VERIFY per space: source count == row count, and a real top-k query matches FsStore's. Reconciliation table.
4. Keep FsStore/sqlite as the source-of-truth fallback until verified; then switch the read path (query_index → Supabase).

## OPEN for Glyphic (react)
- Your models/dims — if you use a dim not in {3584,2560,1024}, add a `vec_<dim>` column (say which).
- Whether to also keep a full-precision `vector` copy for any space needing exact (vs halfvec) — default: halfvec only.
- The read-path cutover (query surface) — align so both sessions query the same table.
