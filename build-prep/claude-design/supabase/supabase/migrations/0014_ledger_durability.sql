-- 0014_ledger_durability.sql — L9 SUPERSESSION FIX (the-one-system substrate lane; owner: ledger session).
-- Idempotent (create-if-not-exists / create-or-replace — safe to re-apply). Schema-ADDITIVE only: adds three
-- run-INDEPENDENT side tables + two unified read-views. Touches NO existing table (④'s SPINE owns ledger.entry).
--
-- THE DISEASE (proven live 2026-07-02): ledger.*_latest views pick ONE run per (project,purpose), so every
-- fresh deterministic run STRANDS the prior run's enrichment beneath the latest views — descriptions dropped
-- to 0, all 1,403 generated-by provenance edges went invisible, until a hand carry-forward. Root cause: the
-- enrichment's identity is its CONTENT (address + source_hash) or is RUN-INDEPENDENT (provenance/time), but it
-- was stored in RUN-SCOPED rows that a new run supersedes.
--
-- THE FIX (aligned with ④ THE CONTAINER, board://item-d47933e2 / item-a58c6277):
--   · interpretation — keyed by canonical TEXT address (+ source_hash): a description survives any number of
--     derived rebuilds as long as the file's content is unchanged (same source_hash) — never re-stranded.
--   · file_meta — run-INDEPENDENT git time axis (project,path): "created / last-modified / change_count".
--   · assertion — a run-INDEPENDENT edge with provenance='authored' (generated-by et al.). ONE edge grammar,
--     two provenances (scanned=ledger.edge, authored=here) — NEVER a 2nd edge system. `kind` is
--     forward-compatible with ④'s L4 edge_kinds registry (retro-validated when L4 lands).
--   · unit_latest / edge_unified — THE durable read faces every consumer should move to; edge_unified is
--     shaped to feed ④'s L4 projection contract (a paths[] leg is L4's to add — declared seam, below).

create schema if not exists ledger;

-- ── interpretation — the model's read of a unit, keyed by CONTENT (survives derived rebuilds) ──────────
create table if not exists ledger.interpretation (
    address                 text not null,          -- canonical: code://<project>/<path>[::<symbol>]
    source_hash             text not null default '',-- the content this interp describes; '' = hash-agnostic
    kind                    text,
    purpose_doc             text,
    what_it_does            text,
    purpose_vs_actual       text,
    novelty                 text,
    intention_signals       text,
    contribution            text,
    summary_for_embedding   text,
    intention_for_embedding text,
    inputs                  jsonb,
    outputs                 jsonb,
    observations            jsonb,
    standouts               jsonb,
    conventions             jsonb,
    concerns                jsonb,
    questions               jsonb,
    apparent_themes         jsonb,
    interp_model            text,
    interp_prompt_version   text,
    produced_by_session     text,
    interp_at               timestamptz default now(),
    primary key (address, source_hash)
);
create index if not exists interpretation_address_idx on ledger.interpretation (address);

-- ── file_meta — the run-INDEPENDENT time axis (from git; the axis that kept dying in run-scoped rows) ──
create table if not exists ledger.file_meta (
    project          text not null,
    path             text not null,
    address          text,                          -- code://<project>/<path>
    created_at       timestamptz,
    last_modified_at timestamptz,
    change_count     integer,
    first_commit     text,
    last_commit      text,
    temporal_source  text default 'git',
    updated_at       timestamptz default now(),
    primary key (project, path)
);
create index if not exists file_meta_address_idx on ledger.file_meta (address);
create index if not exists file_meta_modified_idx on ledger.file_meta (last_modified_at);

-- ── assertion — an EDGE with provenance='authored', run-INDEPENDENT (generated-by, authored_by, …) ────
-- Same grammar as ledger.edge (one edge system); `kind` validates against ④'s L4 edge_kinds when it lands.
create table if not exists ledger.assertion (
    from_ref            text not null,
    kind                text not null,
    to_ref              text not null,              -- the raw/target address
    to_resolved         text,                       -- resolved address when known
    provenance          text not null default 'authored',
    evidence            jsonb,
    produced_by_session text,
    ts                  timestamptz default now(),
    primary key (from_ref, kind, to_ref)
);
create index if not exists assertion_from_idx on ledger.assertion (from_ref);
create index if not exists assertion_to_idx   on ledger.assertion (to_resolved);
create index if not exists assertion_kind_idx on ledger.assertion (kind);

-- ── unit_latest — THE durable unit read: entry_latest + its content-keyed interpretation + file_meta ──
-- Coalesces interpretation OVER the (transitional, soon-vestigial) entry.* interp columns, so enrichment is
-- read from the run-independent table first and the run-scoped copy only as fallback. A rebuild can no longer
-- blank a description: the interpretation row is keyed by (address, source_hash), not by run.
create or replace view ledger.unit_latest as
select
    e.run_id, e.project, e.path, e.node_type, e.parent, e.depth, e.ext, e.language,
    e.size_bytes, e.line_count, e.source_hash, e.address, e.coverage_state, e.exclude_reason,
    e.imports, e.declares, e.address_schemes_used, e.env_vars, e.markers, e.signals, e.extra,
    e.extractor, e.extractor_version, e.extracted_at,
    coalesce(i.kind,                    e.kind)                    as kind,
    coalesce(i.purpose_doc,             e.purpose_doc)             as purpose_doc,
    coalesce(i.what_it_does,            e.what_it_does)            as what_it_does,
    coalesce(i.purpose_vs_actual,       e.purpose_vs_actual)       as purpose_vs_actual,
    coalesce(i.novelty,                 e.novelty)                 as novelty,
    coalesce(i.intention_signals,       e.intention_signals)       as intention_signals,
    -- these 5 exist on base ledger.entry but NOT on the (pre-0012, stale) entry_latest view — itself a
    -- supersession-class staleness. Read from the durable interpretation table only (backfilled from the
    -- full base table); no entry_latest fallback is possible. Refreshing entry_latest is ④'s SPINE call.
    i.contribution                                                 as contribution,
    i.summary_for_embedding                                        as summary_for_embedding,
    i.intention_for_embedding                                      as intention_for_embedding,
    coalesce(i.inputs,                  e.inputs)                  as inputs,
    coalesce(i.outputs,                 e.outputs)                 as outputs,
    coalesce(i.observations,            e.observations)            as observations,
    coalesce(i.standouts,               e.standouts)               as standouts,
    coalesce(i.conventions,             e.conventions)             as conventions,
    coalesce(i.concerns,                e.concerns)                as concerns,
    coalesce(i.questions,               e.questions)               as questions,
    coalesce(i.apparent_themes,         e.apparent_themes)         as apparent_themes,
    i.interp_model                                                 as interp_model,   -- not on stale entry_latest
    i.interp_at                                                    as interp_at,      -- not on stale entry_latest
    (i.address is not null)                                        as interp_durable,  -- true = from the durable table
    fm.created_at       as file_created_at,
    fm.last_modified_at as file_modified_at,
    fm.change_count     as file_change_count
from ledger.entry_latest e
left join ledger.interpretation i
       on i.address = e.address and i.source_hash = coalesce(e.source_hash, '')
left join ledger.file_meta fm
       on fm.project = e.project and fm.path = e.path;

-- ── edge_unified — THE durable edge read: scanned (latest run) ∪ authored (run-independent) ───────────
-- ④'s L4 projection contract consumes this. The paths[] leg is L4's to add (declared seam — a future
-- `union all select … from ledger.path_step` when L4 lands); edge_unified's shape is stable for it.
create or replace view ledger.edge_unified as
select from_ref, kind, to_raw, to_resolved, 'scanned'::text as provenance,
       run_id, extracted_at, extra
  from ledger.edge_latest
  where kind not in (select distinct kind from ledger.assertion)  -- authored kinds come from assertion, not the scanned run (no double-count; self-deriving, no hardcoded list)
union all
select from_ref, kind, to_ref as to_raw, to_resolved, provenance,
       null::uuid as run_id, ts as extracted_at, evidence as extra
  from ledger.assertion;

comment on view ledger.unit_latest  is 'L9: durable unit read — entry_latest + content-keyed interpretation + run-independent file_meta. Consumers should read here, not entry_latest, so enrichment survives run rebuilds.';
comment on view ledger.edge_unified is 'L9: durable edge read — scanned (edge_latest) UNION authored (assertion). ONE edge grammar, two provenances. Feeds ④''s L4 projection contract (paths[] leg pending L4).';
