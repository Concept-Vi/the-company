# Plan B research · R2 — multi-axis query patterns over Postgres+pgvector (web + live-DB wave, 2026-07-02)

*The best-known composition patterns for the ONE coordinate-query function, verified against the live
ledger. Produced by a research agent; report verbatim below. Companion: R1-axes-inventory.md.*

# Research report: multi-axis coordinate query over Postgres+pgvector

## Local ground truth (verified against the live DB, 127.0.0.1:15432, schema `ledger`)

Everything below is **Observed** by direct psql inspection, not inferred:

- pgvector **0.8.2** confirmed. `ledger.embedding` = 76,196 rows, three halfvec columns (`vec_1024`, `vec_2560`, `vec_3584`), each with its **own partial HNSW cosine index** (`WHERE vec_N IS NOT NULL`) — so "26 spaces at 3 dims" means 3 dim-columns/3 indexes shared across ALL spaces; there is **no per-space partial index**. Space distribution is wildly skewed: `extractions` = 51,600 (68%), then `exchange` 6,983, `symbol` 6,201, down to `topics` 329 and scale rungs of 4–470 rows.
- The scale rungs **already exist as embedding spaces**: `scale:extractions:k512/k128/k32/k8`, `scale:history:k64/k16`, `scale:topics:k32`, etc. — centroid vectors are materialized data, not a query trick to invent.
- `ledger.entry` = 164,937 rows **total across 18 runs**; the "~17k nodes" figure is per-run (largest runs ≈ 18k, unique on `(run_id, path)`). `ledger.edge` = **720,461 total**, ~70k per run — so an un-run-scoped query touches 10x the intended graph. Edge kinds per the full table: `calls` 493k, `contains` 108k, `imports` 65k, `references` 39k, then a long typed tail (`calls-endpoint`, `generated-by`, `capability-of`, …).
- Edges are **text-address refs** (`from_ref`, `to_raw`, `to_resolved`), no FK to entry — all graph↔entry joins are string joins on address + run scope. Current edge indexes are single-column btrees (`from_ref`, `to_resolved`, `run_id`); **there is no composite `(run_id, kind, from_ref)` index** — that's a gap for typed traversal.
- Path axis: `entry.path` btree + `gin_trgm_ops`, plus `parent` and `depth` columns. Time axis: `extracted_at`, `interp_at`. Provenance: `run_id`, `produced_by_session`, `model`, `pass`, plus `generated-by`/`authored_by` edges.
- Available-but-unused extensions locally: `pgroonga`, `rum`, `pgrouting`, `pg_graphql`, `pgmq`. **Apache AGE and ParadeDB `pg_search` are NOT in the image.**

---

## 1. Filtered vector search in pgvector (the filtering problem)

The core mechanic: with an HNSW scan, WHERE clauses are applied **after** the index returns candidates. With default `hnsw.ef_search = 40`, a filter matching 10% of rows returns ~4 rows on average, not your k — this is the canonical over-filtering/recall-loss problem stated in pgvector's own README.

pgvector 0.8 added **iterative index scans**: `SET hnsw.iterative_scan = strict_order | relaxed_order` makes the scan keep pulling candidates until the filter is satisfied or a safety valve trips. The valves: `hnsw.max_scan_tuples` (default **20,000**) and `hnsw.scan_mem_multiplier` (default 1 × work_mem). `relaxed_order` is faster but can emit slightly out-of-order results (~95–99% of strict quality) — re-sort the final page with an outer `ORDER BY`. AWS measured **up to 100x improvement in result completeness** with iterative scans on 0.8.0. `hnsw.ef_search` caps at 1000; iterative scan is the mechanism beyond that, not ef_search inflation.

**Pre-filter vs post-filter decision rule (the consensus pattern):**
- **Selective filter (small candidate set)** → pre-filter with a CTE/subquery and let Postgres do an **exact** scan (`ORDER BY vec <=> q` over the filtered rows, no ANN index). Exact scan over a few thousand halfvecs is single-digit ms and has perfect recall. For this ledger: any query scoped to a small space (`topics` = 329) or a tight path prefix should go exact.
- **Broad filter** → HNSW with iterative scan, filter applied during/after the scan.
- **Recurring categorical filter** → partial index (pgvector README's explicit advice: `CREATE INDEX ... USING hnsw ... WHERE (category_id = 123)`). For this ledger the obvious candidate is a partial HNSW per **big** space (`extractions` deserves its own; the tail spaces don't — they're exact-scan-sized).

Crucially, the planner picks exact vs index by cost, and a materialized CTE or join can silently force one or the other — the one query function should make this choice **explicitly** (count the candidate set first, branch), not leave it to planner luck. That's also the fail-loud version of the decision.

## 2. Hybrid search (vector + lexical + structured)

The standard pg-native pattern (Supabase's own docs implement exactly this): two CTEs — one FTS (`tsvector` + GIN, `ts_rank`), one vector (HNSW) — each `LIMIT ~2·k`, then **FULL OUTER JOIN and Reciprocal Rank Fusion**: `score = Σ wᵢ / (rrf_k + rankᵢ)`, with `rrf_k = 60` the near-universal constant. Weights let you tune lexical-vs-semantic emphasis (e.g. 0.7/0.3); RRF needs no score normalization, which is why it composes cleanly with more signals — recency, popularity, graph-degree can each be added as another ranked list in the same sum.

**Why hybrid matters specifically for code:** embeddings are weak at exact identifiers — a query for `run_cascade` or an error code can lose to conceptually-adjacent noise; lexical wins on exact symbols, vectors win on "what does the thing that ingests noticeboard items do". One practitioner measurement: pure vector ~62% precision, +trigram+tsvector RRF → 84%+. For identifier-heavy corpora, **pg_trgm is often better than tsvector** because ts parsers tokenize `snake_case`/`camelCase` badly — and the ledger already has `entry_path_trgm` (GIN trigram on path). ParadeDB's argument for BM25 over `ts_rank` (ts_rank has no corpus-level IDF, so it can't distinguish rare discriminating terms from common ones) is correct, but `pg_search` isn't in this Supabase image; **`pgroonga` and `rum` ARE available locally** if `ts_rank` proves too weak — pgroonga in particular handles code-ish tokens better than the default parser. Pragmatic call: start with trigram-on-(path, symbol-names) + tsvector-on-(what_it_does, purpose_doc) as two lexical lists inside the RRF, before reaching for another index type.

## 3. Graph traversal in Postgres

At ~70k edges per run (720k total), the consensus is clear: **recursive CTEs are fine at this scale, live, with three guards**:

1. **Cycle guard** — Postgres 14+ has the SQL-standard `CYCLE col SET is_cycle USING path` clause; the equivalent manual pattern is a visited-`ARRAY` column with `to_ref <> ALL(path)`. `calls` graphs absolutely have cycles; `UNION ALL` without a guard never terminates.
2. **Depth cap** — a `depth < N` term in the recursive arm; N=2–3 covers nearly all "what calls Y / what does X reach" questions.
3. **Frontier discipline** — hub symbols in a `calls` graph (493k rows corpus-wide) explode fan-out; dedupe the frontier per level and cap it (`DISTINCT ON` / array-membership), and always scope `run_id = $run AND kind = ANY($kinds)` in the recursive arm.

The recursive arm must hit an index or each level is a seq scan: **add `(run_id, kind, from_ref)` and `(run_id, kind, to_resolved) INCLUDE (from_ref)` composite btrees** — the current single-column indexes make the planner bitmap-AND, which works but is 3–5x worse for exactly this access pattern.

**Closure tables**: literature says recursive CTEs degrade for transitive-closure workloads beyond tens of thousands of rows *when depth is unbounded*; with depth ≤ 3 and typed-kind restriction, live traversal is the right default here. Materialize a closure (or a per-kind reachability table refreshed per run) only if unbounded-reachability queries become a real workload — it's a per-run static graph, so a closure is cheap to rebuild at ingest, but it's ~O(paths) storage on a 493k-edge `calls` graph and mostly answers questions nobody is asking yet.

**Apache AGE / pgrouting**: AGE is not a trusted-language extension (C), is not in Supabase's extension set, and would require a custom image — not worth it for typed-adjacency at this scale. `pgrouting` IS available locally but is built for weighted shortest-path/routing semantics, not typed property-graph filtering; recursive CTEs over `ledger.edge` express the actual questions more directly. Verdict: plain SQL.

## 4. Composing all of it — the query-object pattern

The shape worth stealing is **Qdrant's Universal Query API**: a JSON query with (a) `prefetch` sub-queries (each its own search + its own filter), (b) a top-level `query` that **fuses** prefetch results (`fusion: rrf` or score-based), (c) a **global filter** that applies to every prefetch, with filters composed as `must / should / must_not` condition lists. That's precisely the multi-axis composition problem: each axis is a prefetch or a filter; fusion is the combiner. Weaviate's contribution is smaller but useful: a single **`alpha`** scalar (0 = pure lexical, 1 = pure vector) as the user-facing hybrid dial, plus an orthogonal `where` filter tree — a good UI-level simplification over raw per-list weights.

In SQL, the established compilation of such a spec is a **fixed CTE skeleton with optional stages**:

```
candidates (structured pre-filter: run/path/time/provenance/scale-membership)
  → graph (recursive CTE, restrict or expand candidates)
  → semantic (exact over candidates | HNSW iterative + semi-join)
  → lexical (trgm/tsvector over candidates)
  → fused (RRF full-outer-join)
  → page (order, keyset cursor, limit)
```

Only the stages present in the spec are emitted; absent axes collapse to pass-through. Both the "one SQL function with dynamic SQL" and "app-side compiler" camps converge on this same skeleton — the difference is only where the compiler lives (see memo).

## 5. Serving both faces (MCP + web UI) from one definition

The Supabase-native pattern: define **one Postgres function**, exposed automatically by PostgREST as `POST /rest/v1/rpc/<fn>`; `supabase-js` calls it as `.rpc('ledger_query', { spec })`, `supabase-py` identically, and an MCP tool is a thin wrapper around either the Python client or direct psycopg — **all callers execute the same SQL body**, which is the literal one-definition property. Function args arrive as a JSON object whose keys map to parameter names, so a single `spec jsonb` parameter is idiomatic.

Two serving details that matter:
- **Pagination**: if the function `RETURNS TABLE/SETOF`, PostgREST lets clients apply range headers and filters *on the function result* — but that's offset-flavored. For a UI over fused scores, the robust pattern is **keyset pagination on a composite `(score DESC, entry_id)` cursor carried inside the spec** (`page: {limit, cursor}`), because RRF scores are stable within a query and ties are broken deterministically by id. Offset pagination over a re-executed ANN query is subtly non-deterministic (iterative relaxed_order can reorder across executions) — a correctness trap, not just a perf one.
- **Per-query GUC tuning**: `hnsw.iterative_scan` / `ef_search` / `max_scan_tuples` want to be set per call via `SET LOCAL` **inside the same transaction as the scan** — which only a function body (or a managed transaction) can guarantee. This is a real argument for the logic living in the DB.

## 6. Scale/rung-aware querying (coarse-to-fine)

Coarse-to-fine is a thoroughly established family: IVF itself is "centroids first, then members"; RAPTOR does it over summary trees (broad queries hit cluster/root summaries, then drill into relevant subtrees); recent multi-vector work (token-aware clustering, cluster-guided beam search) all use the same two-tier move — route via centroids, restrict fine search to the selected clusters' members.

The ledger is unusually well-positioned because **the rungs are already materialized as spaces** (`scale:extractions:k512` … `k8`). The pattern compiles directly:
1. Query the rung space (`scale:<space>:kN`) — these are tiny (8–512 vectors), so **always exact scan, never HNSW** — take top-P centroids.
2. Resolve centroid → members (membership edges/addresses), which becomes a structured pre-filter on the fine space.
3. Fine search within members — usually exact again, since top-P clusters at k128 over 51k vectors ≈ 400·P candidates.

This also gives the "zoom" semantics for the UI free: `scale: {rung: "k128"}` with no drill = the map view; `drill: {top: 5}` = the zoom-in. One caveat from the literature: centroid routing costs recall when the true neighbor sits near a cluster boundary — mitigate by taking P generously (5–10, not 1–2) since the fine stage is cheap.

---

# Recommendation memo

## The query-spec vocabulary

One `spec jsonb`, Qdrant-shaped (filters + prefetch-like axes + fusion), pg-native names:

```jsonc
{
  "run": "latest",                          // or explicit run_id — ALWAYS resolved, never optional
  "filter": {                               // structured axes = the pre-filter, all btree/trgm work
    "path":   { "under": "canvas/app/", "glob": "*.ts", "not_under": ["node_modules/"] },
    "time":   { "extracted_after": "2026-06-01T00:00:00Z", "interp_after": null },
    "prov":   { "session": null, "model": null, "pass": null },
    "entry":  { "node_type": ["file","symbol"], "language": ["typescript"], "coverage_state": null }
  },
  "graph": {                                // typed-adjacency axis
    "anchor": { "address": "app:supabase.rpc" },   // or {"from_results": true} for post-expansion
    "kinds": ["calls"], "direction": "in", "depth": 2,
    "mode": "restrict"                      // restrict candidates | expand results | rank (degree as RRF signal)
  },
  "scale": { "space": "extractions", "rung": "k128", "top_clusters": 5, "drill": true },
  "semantic": { "space": "extractions", "layer": "summary",
                "text": "how noticeboard items are ingested",   // server embeds, or pass "vector": [...]
                "k": 50, "min_sim": null },
  "lexical":  { "text": "run_cascade", "mode": ["trgm","fts"], "fields": ["path","what_it_does"] },
  "fuse":  { "method": "rrf", "rrf_k": 60, "weights": { "semantic": 1.0, "lexical": 0.7, "graph": 0.0 } },
  "page":  { "limit": 20, "cursor": null },
  "return": { "fields": ["path","what_it_does","kind"], "edges": false, "score_breakdown": true }
}
```

Unknown keys **raise** (fail-loud), every response echoes the resolved run_id + the plan taken (exact vs hnsw, candidate count) so results are never silently under-recalled.

## Where each axis executes

| Axis | Executes as | Index |
|---|---|---|
| run / time / prov / entry-fields | `candidates` CTE WHERE | `entry_run_idx`, `entry_cov_idx`, btrees |
| path | same CTE: prefix → btree `text_pattern_ops`-style range; glob/fuzzy → trgm | `entry_path_idx`, `entry_path_trgm` |
| graph (restrict) | recursive CTE, depth-capped, visited-array, semi-join into candidates | **new** `(run_id, kind, from_ref)` + `(run_id, kind, to_resolved)` |
| scale | exact scan on rung space → member addresses → candidates filter | tiny spaces, no index needed |
| semantic | **branch**: candidates < ~8k → exact `ORDER BY vec <=> q` over join; else HNSW + `SET LOCAL hnsw.iterative_scan = relaxed_order` + semi-join | partial HNSW per dim column (existing); consider partial per-space for `extractions` |
| lexical | trgm similarity + tsvector CTEs | existing trgm GIN; add GIN on generated tsvector of `what_it_does`/`purpose_doc` |
| fuse | RRF full-outer-join of ranked CTEs, k=60 | — |
| page | keyset on `(score DESC, entry_id)` | — |

## The 3 biggest perf traps at this scale

1. **Post-filter starvation on the shared HNSW index.** 68% of vectors are one space; every other space filtered through the same index suffers exactly the README's 10%→4-rows problem, and `scale:*` spaces (4–470 rows) would return near-nothing. Mitigation: the explicit selectivity branch above — exact scan for small candidate sets (perfect recall, ms-cheap), iterative relaxed_order + `max_scan_tuples` raised for broad ones, and report which branch ran.
2. **Recursive traversal over `calls` without composite indexes and frontier caps.** 493k `calls` edges corpus-wide, string-address joins, hub fan-out: depth-3 unguarded traversal is the query that takes 30s. Mitigation: run-scope in the recursive arm, the two composite indexes, `CYCLE`/visited-array, depth ≤ 3 default, per-level `DISTINCT` + frontier cap with a raised notice when the cap trips.
3. **Cross-run leakage and CTE materialization.** The tables hold 18 runs; any stage that forgets `run_id` scans 10x the data and, worse, returns stale-run ghosts as if current (a correctness trap wearing a perf costume). And a `MATERIALIZED` CTE (or one the planner chooses to materialize) between filter and vector stage silently forces exact scans on huge sets or blocks pushdown. Mitigation: resolve `run` once at the top and thread it into every stage; keep CTEs `NOT MATERIALIZED` where inlining is wanted; `EXPLAIN`-test the two or three canonical spec shapes as regression fixtures.

## One SQL function vs thin Python compiler — verdict

**One PL/pgSQL function, `ledger.query(spec jsonb)`, that compiles the spec to dynamic SQL (`format()` + `EXECUTE`) inside the DB.** Reasons, in order of force:

1. **The one-definition property is only literal this way.** PostgREST exposes it to the web UI (`.rpc`), supabase-py/psycopg exposes it to MCP — same body, same version, migrated with the schema (`0011_ledger.sql` precedent). A Python compiler makes the Python service the definition and the UI a client of a second surface — two homes, which is the sprawl the-one-system exists to kill.
2. **GUC tuning is transactional.** `SET LOCAL hnsw.iterative_scan/ef_search/max_scan_tuples` must run in the scan's own transaction; a function body owns that naturally. A Python compiler must ship the SETs alongside generated SQL in a managed transaction on every client — a per-client obligation, i.e. a repeated definition.
3. **The variability is bounded.** Six axes, one fixed CTE skeleton, optional stages, one selectivity branch — a few hundred lines of `format()`. This is well inside dynamic-plpgsql's comfort zone; a general query compiler would argue for Python, but this isn't one.

Mitigate the known costs of dynamic SQL in the function: whitelist every enum (kinds, spaces, layers, fields) against catalog/lookup queries and **raise on anything unrecognized**; use `%I`/`%L` exclusively; keep a golden-spec test file (spec → expected plan shape + expected rows on fixture data) run in CI/migration verify. If a second consumer ever needs the compiler outside Postgres (e.g. compiling to a different store), that is the moment to extract it — not before.

**Local prerequisites surfaced by this research** (small, all verified missing): composite edge indexes `(run_id, kind, from_ref)` / `(run_id, kind, to_resolved)`; a tsvector GIN over the interpreted-text fields if FTS joins the lexical list; optionally one partial HNSW for `space = 'extractions'`. Postgres major version should be checked for the `CYCLE` clause (14+) before choosing it over the visited-array pattern — I verified pgvector 0.8.2 but did not capture `server_version`.

Sources: [pgvector README (filtering, iterative scans, GUCs)](https://github.com/pgvector/pgvector) · [AWS: pgvector 0.8.0 on Aurora — iterative scan gains](https://aws.amazon.com/blogs/database/supercharging-vector-search-performance-and-relevance-with-pgvector-0-8-0-on-amazon-aurora-postgresql/) · [pgvector 0.8.0 release note](https://www.postgresql.org/about/news/pgvector-080-released-2952/) · [Supabase hybrid search guide (RRF in SQL)](https://supabase.com/docs/guides/ai/hybrid-search) · [ParadeDB: Hybrid Search in PostgreSQL — The Missing Manual](https://www.paradedb.com/blog/hybrid-search-in-postgresql-the-missing-manual) · [pg_trgm + pgvector hybrid retrieval precision numbers](https://callsphere.ai/blog/vw7h-pg-trgm-pgvector-hybrid-retrieval-2026) · [Postgres as a search engine](https://anyblockers.com/posts/postgres-as-a-search-engine) · [PostgreSQL docs: WITH queries / CYCLE](https://www.postgresql.org/docs/current/queries-with.html) · [Recursive CTE cycle detection patterns](https://sqlfordevs.com/cycle-detection-recursive-query) · [CTE vs closure-table discussion](https://news.ycombinator.com/item?id=13128295) · [Apache AGE + managed Postgres landscape](https://gdotv.com/blog/running-apache-age-docker-cloud/) · [Supabase discussion: AGE not supported](https://github.com/orgs/supabase/discussions/13263) · [Qdrant hybrid queries / Universal Query API](https://qdrant.tech/documentation/search/hybrid-queries/) · [Weaviate hybrid search (alpha + where)](https://docs.weaviate.io/weaviate/search/hybrid) · [PostgREST functions-as-RPC](https://docs.postgrest.org/en/v12/references/api/functions.html) · [supabase-py rpc](https://supabase.com/docs/reference/python/rpc) · [RAPTOR hierarchical retrieval](https://medium.com/microsoftazure/fixing-sparse-retrieval-with-raptor-on-azure-ai-search-4d540dd3bd43)
