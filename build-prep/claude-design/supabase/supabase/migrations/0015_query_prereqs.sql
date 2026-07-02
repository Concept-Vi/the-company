-- 0015_query_prereqs.sql — L11 COORDINATE-QUERY prerequisites (ledger session's block: 0014/0015/0016).
-- Idempotent, additive-only (indexes + one generated column; touches no rows, changes no behavior).
-- The B·R2 research (plan-b-coordinates/research/R2-query-patterns.md) named these as the perf floor:
--
-- 1) COMPOSITE EDGE INDEXES — typed graph traversal ("what does X call, in THIS run") currently
--    bitmap-ANDs three single-column btrees; the recursive-CTE arm of ledger.query (and ④'s L4 path
--    walks) needs (run_id, kind, from_ref/to_resolved) to hit ONE index per level. 720k rows: measured
--    3–5x on depth-2/3 walks.
create index if not exists edge_run_kind_from_idx on ledger.edge (run_id, kind, from_ref);
create index if not exists edge_run_kind_tores_idx on ledger.edge (run_id, kind, to_resolved) include (from_ref);

-- 2) LEXICAL AXIS — FTS on the DURABLE interpretation table (the side-table move means descriptions live
--    here, not on entry). A stored generated tsvector + GIN: the query function's lexical leg (RRF hybrid)
--    reads this. english config: the descriptions are model-written English prose.
alter table ledger.interpretation
    add column if not exists fts tsvector
    generated always as (to_tsvector('english',
        coalesce(what_it_does,'') || ' ' || coalesce(purpose_doc,'') || ' ' ||
        coalesce(contribution,''))) stored;
create index if not exists interpretation_fts_idx on ledger.interpretation using gin (fts);

-- 3) IDENTIFIER AXIS — trigram on symbol names (code identifiers tokenize badly under tsvector; trgm is
--    the right lexical lens for `run_cascade`-ish exact/fuzzy identifier search — B·R2's code-search finding).
create extension if not exists pg_trgm;
create index if not exists symbol_name_trgm_idx on ledger.symbol using gin (name gin_trgm_ops);

-- 4) assertion.to_resolved lookups by kind (edge_unified's authored leg filtered by kind+target).
create index if not exists assertion_kind_tores_idx on ledger.assertion (kind, to_resolved);
