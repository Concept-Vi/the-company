-- 0011_ledger.sql — THE LEDGER (the-one-system): the non-flat, run-scoped structural ledger.
-- Canonical, tracked home for the ledger schema (supersedes the loose build-prep/the-one-system/ledger_schema.sql,
-- which is retired to a pointer). Idempotent: safe to re-apply. Reversible: DROP SCHEMA ledger CASCADE.
-- Non-flat: every extraction is a RUN scoped by (project, channel, purpose, layer); runs ACCUMULATE and are
-- comparable over time (drift). Reuses the code:// coordinate. Provenance + per-extractor version on every row.

create extension if not exists vector;
create extension if not exists pg_trgm;
create extension if not exists ltree;

create schema if not exists ledger;

create table if not exists ledger.run (
  run_id          uuid primary key default gen_random_uuid(),
  project         text not null,
  channel         text,
  purpose         text not null,
  layer           text not null,
  session_id      text,
  scope           jsonb,
  model           text,
  prompt_version  text,
  schema_version  int default 1,
  tool_git_sha    text,
  tool_version    text,
  status          text not null default 'running',
  stats           jsonb,
  started_at      timestamptz not null default now(),
  ended_at        timestamptz,
  notes           text
);

create table if not exists ledger.entry (
  entry_id        uuid primary key default gen_random_uuid(),
  run_id          uuid not null references ledger.run(run_id) on delete cascade,
  project         text not null,
  path            text not null,
  node_type       text not null,
  parent          text,
  depth           int,
  ext             text,
  language        text,
  size_bytes      bigint,
  line_count      int,
  source_hash     text,
  address         text,
  coverage_state  text not null default 'none',
  exclude_reason  text,
  imports         jsonb,
  declares        jsonb,
  address_schemes_used jsonb,
  stores_touched  jsonb,
  env_vars        jsonb,
  markers         jsonb,
  signals         jsonb,
  kind            text,
  purpose_doc     text,
  what_it_does    text,
  inputs          jsonb,
  outputs         jsonb,
  observations    jsonb,
  standouts       jsonb,
  conventions     jsonb,
  concerns        jsonb,
  notes           text,
  questions       jsonb,
  purpose_vs_actual text,
  apparent_themes jsonb,
  intention_signals text,
  novelty         text,
  extra           jsonb,
  suggested_fields jsonb,
  proposed_edge_kinds jsonb,
  extractor       text,
  extractor_version text,
  produced_by_session text,
  pass            text,
  model           text,
  prompt_version  text,
  extracted_at    timestamptz not null default now(),
  unique (run_id, path)
);

create table if not exists ledger.symbol (
  symbol_pk       uuid primary key default gen_random_uuid(),
  run_id          uuid not null references ledger.run(run_id) on delete cascade,
  code_id         text not null,
  parent_path     text not null,
  name            text not null,
  symbol_kind     text,
  signature       text,
  params          jsonb,
  returns         text,
  decorators      jsonb,
  bases           jsonb,
  line_start      int,
  line_end        int,
  is_exported     boolean,
  is_async        boolean,
  does            text,
  description     text,
  observations    jsonb,
  notes           text,
  extra           jsonb,
  extractor       text,
  extractor_version text,
  produced_by_session text,
  pass            text,
  model           text,
  extracted_at    timestamptz not null default now(),
  unique (run_id, code_id)
);

create table if not exists ledger.edge (
  edge_id         uuid primary key default gen_random_uuid(),
  run_id          uuid not null references ledger.run(run_id) on delete cascade,
  from_ref        text not null,
  kind            text not null,
  to_raw          text not null,
  to_resolved     text,
  line            int,
  extra           jsonb,
  produced_by_session text,
  pass            text,
  extracted_at    timestamptz not null default now()
);

-- additive columns for an already-existing schema (idempotent ALTERs)
alter table ledger.run    add column if not exists tool_git_sha text;
alter table ledger.run    add column if not exists tool_version text;
alter table ledger.entry  add column if not exists extractor text;
alter table ledger.entry  add column if not exists extractor_version text;
alter table ledger.symbol add column if not exists extractor text;
alter table ledger.symbol add column if not exists extractor_version text;

create index if not exists entry_run_idx    on ledger.entry (run_id);
create index if not exists entry_path_idx   on ledger.entry (path);
create index if not exists entry_parent_idx on ledger.entry (parent);
create index if not exists entry_cov_idx    on ledger.entry (run_id, coverage_state);
create index if not exists entry_path_trgm  on ledger.entry using gin (path gin_trgm_ops);
create index if not exists entry_hash_idx   on ledger.entry (run_id, source_hash);
create index if not exists symbol_run_idx   on ledger.symbol (run_id);
create index if not exists symbol_code_idx  on ledger.symbol (code_id);
create index if not exists edge_run_idx     on ledger.edge (run_id);
create index if not exists edge_from_idx    on ledger.edge (from_ref);
create index if not exists edge_toraw_idx   on ledger.edge (to_raw);
create index if not exists edge_tores_idx   on ledger.edge (to_resolved);

-- ── views (the accumulation feature made usable) ──────────────────────────────────────────────
create or replace view ledger.latest_run as
  select distinct on (project, purpose) *
  from ledger.run where status = 'complete'
  order by project, purpose, started_at desc;

create or replace view ledger.entry_latest as
  select e.* from ledger.entry e join ledger.latest_run r using (run_id);

create or replace view ledger.symbol_latest as
  select s.* from ledger.symbol s join ledger.latest_run r using (run_id);

create or replace view ledger.edge_latest as
  select g.* from ledger.edge g join ledger.latest_run r using (run_id);

create or replace view ledger.coverage as
  select r.project, r.purpose, e.coverage_state, count(*) n
  from ledger.entry e join ledger.latest_run r using (run_id)
  where e.node_type = 'file'
  group by r.project, r.purpose, e.coverage_state;
