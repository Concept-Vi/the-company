-- 0019_type_registry.sql — ④ THE CONTAINER (the-one-system, L3-REGISTRY): the generated-artifact
-- projection for the generative type registry (organ-studies/REGISTRY.md §3; C3.2/C3.3).
--
-- (Numbering: 0013=④ container · 0014-0016=ledger session · 0017=L2 · 0018=L4 · 0019=L3 — the
--  next-free-at-write-time rule, board-announced.)
--
-- WHAT THIS IS: the DERIVED read-side of the type registry. Vocabulary = FILES (types/<id>.py +
-- cascades/<id>.py, git-lifecycled); the generated ARTIFACTS are DERIVED, one-way (file → generate_all →
-- this table). A row here with no source types/<id>.py is a GHOST — the completeness ledger fails loud.
--
-- LAWS CARRIED:
--   · text address = IDENTITY (law 1): artifact PK = address text ('type://<type>/face/<cascade>').
--   · reverses composed at read (law 4): ONE direction is stored — type_id = the `generated_from` edge
--     (artifact → type). The equal-and-opposite `generates` (type → artifact) is COMPOSED AT READ
--     (select where type_id=…), NEVER a second stored row. The generated_from_edge VIEW makes both
--     directions readable from the one table.
--   · vocabulary=files / data=DB (law 3): this is DATA (instance projection rows). The type + cascade
--     VOCABULARY stays in files. Generated artifacts are never migrated — always regenerated.
--   · schema-additive (constitution rule 2) · fail-loud.
--
-- INTERIM EDGE HOME — PENDING L4: the generated_from↔generates edge pair lives here for now. When L4's
-- edge store (ledger.edge + edge_kinds/ registry) lands, RE-HOME these edges onto it (declare the
-- 'generated-from' kind with its 'generates' inverse in edge_kinds/, one grammar) and keep this table as
-- the artifact PAYLOAD store only. Breadcrumb per IMPLEMENTATION-GUIDE §L3.
--
-- IDEMPOTENT: safe to re-apply (IF NOT EXISTS everywhere).
-- REVERSAL: DROP VIEW IF EXISTS container.generated_from_edge;
--           DROP TABLE IF EXISTS container.generated_artifact;

begin;

-- prerequisite guard (fail loud, no half-apply): schema `container` must exist (0013).
do $guard$
begin
  if not exists (select 1 from information_schema.schemata where schema_name = 'container') then
    raise exception '0019_type_registry: schema `container` absent — apply 0013_container.sql first (fail loud, no half-apply).';
  end if;
end
$guard$;

create table if not exists container.generated_artifact (
  address      text primary key,                          -- law 1: 'type://<type>/face/<cascade>'
  type_id      text not null,                             -- the generated_from edge (artifact → type)
  cascade_id   text not null,                             -- which cascade derived it
  target       text not null,                             -- the system it projects into
  payload      jsonb not null default '{}'::jsonb,        -- the derived face content
  generated_at timestamptz not null default now()
);

create index if not exists generated_artifact_type_idx on container.generated_artifact(type_id);
create index if not exists generated_artifact_cascade_idx on container.generated_artifact(cascade_id);

-- law 4: both directions readable from the one table — generates is the composed reverse, never stored twice.
create or replace view container.generated_from_edge as
  select address        as from_addr,                     -- the artifact
         'generated-from'::text as kind,
         'type://' || type_id  as to_addr,                -- its source type
         'generates'::text     as inverse,                -- the equal-and-opposite (type → artifact), composed
         cascade_id, target, generated_at
  from container.generated_artifact;

comment on table container.generated_artifact is
  'L3 REGISTRY: the DERIVED artifact projection (generate_all fans out here, one-way file→DB). type_id = the '
  'generated_from edge; `generates` is composed at read (law 4). INTERIM edge home PENDING L4''s edge store.';

commit;
