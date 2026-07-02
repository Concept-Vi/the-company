-- 0013_container.sql — ④ THE CONTAINER (the-one-system, L1-SPINE): schema `container` beside `ledger`.
-- (The COMPLETION-CRITERIA named this 0012_container.sql; 0012 was already taken by
--  0012_ledger_interpretive.sql when this lane landed — same location, same pattern, next free number.)
--
-- The rebuilt SPINE (organ-studies/SPINE.md §4): Side A's ontology (Space=ownership frame ·
-- Project=unit-of-world, a top-level address · Scope=authored shelf · Resource=authored unit) on
-- Side B's physics (text address = identity; containment derived; one grammar; one resolver; fail-loud).
--
-- LAWS CARRIED:
--   · text address = IDENTITY (law 1): resources/scopes carry address TEXT NOT NULL UNIQUE (the ci_*
--     lesson — mandatory, one grammar). projects.address is a GENERATED column ('project://'||key) so it
--     can never be hand-placed or drift (derive-never-place, enforced by the DB itself). NO ltree column
--     is carried at all — A's disease was ltree-as-authored-identity (NULL/stale/doubled); a derived
--     ltree index MAY be added later by a fold if a real query needs it (SPINE §4 allows max ONE).
--   · actors are ADDRESSES (law 6): members.principal + resources.created_by are principal ADDRESSES
--     (operator://tim, agent://vi). The principal TABLE is L2's (full identity model); these columns
--     attach to it by address when L2 lands — schema-additive, nothing here breaks.
--   · authored vs derived are provenance faces (law 8): container.* rows are the AUTHORED half;
--     the ledger's scan-derived containment stays in ledger.entry/edge. Same law, two provenances.
--   · schema-additive (constitution rule 2): the ledger gains NULLABLE project_id FKs; the bare text
--     `project` label STAYS on every row (never break).
--
-- IDEMPOTENT: safe to re-apply (IF NOT EXISTS everywhere; ADD COLUMN IF NOT EXISTS).
-- TRANSACTION SAFETY: the whole migration is ONE transaction (BEGIN…COMMIT) with a fail-loud
--   prerequisite guard at the very top — an unmet prerequisite or any mid-apply error ROLLS THE WHOLE
--   THING BACK (no half-apply, no orphan container schema without its ledger FK target).
-- REVERSAL: DROP SCHEMA container CASCADE;
--           ALTER TABLE ledger.entry  DROP COLUMN IF EXISTS project_id;
--           ALTER TABLE ledger.run    DROP COLUMN IF EXISTS project_id;
--           ALTER TABLE ledger.coverage_findings DROP COLUMN IF EXISTS project_id;
--           DROP FUNCTION IF EXISTS container.ledger_backfill_project_id() CASCADE;
-- Data lands via ops/migrate_container_from_cvi.py (idempotent, reconciliation-reported, never
-- mutates cvi_mine) + ops/backwrite_fusion_record.py (the C1.6 back-write moment).

begin;

-- ── PREREQUISITE GUARD (fail loud, no half-apply) — container.projects is the FK target the ledger's
-- additive project_id points at; without schema `ledger` this migration has nothing to weld to.
do $guard$
begin
  if not exists (select 1 from information_schema.schemata where schema_name = 'ledger') then
    raise exception 'expected schema ledger (0011_ledger.sql); previously n/a; fix: apply 0011_ledger.sql first';
  end if;
end
$guard$;

create schema if not exists container;

-- ── Space — the OWNERSHIP/MEMBERSHIP frame (who holds this and who may act; NOT where content lives).
-- Tim decided: ONE Space (the cloud's 14 unnamed personal + ~11 duplicate default-project spaces were
-- the disease; the migration mints exactly one and writes the rest excluded-with-reason).
create table if not exists container.spaces (
  space_id      uuid primary key default gen_random_uuid(),
  space_key     text not null unique,
  kind          text not null default 'operator',       -- open vocabulary (operator|client|...)
  owner         text,                                   -- a principal ADDRESS (operator://tim)
  status        text not null default 'active',
  description   text,
  source_system text,                                   -- transplant provenance (e.g. 'cvi_mine')
  source_uuid   uuid,                                   -- the original cloud uuid, if migrated
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);

-- ── Project — the UNIT-OF-WORLD, a top-level address (NORTH-STAR verbatim). The join of ALL lanes:
-- ledger label · recollection scale node · container row · design-repo root. project_key is the ONE
-- join key across lanes; `address` is DERIVED (generated column) so the cloud's computed-at-read /
-- stored-but-ignored split can never recur — there is exactly one form and the DB derives it.
create table if not exists container.projects (
  project_id    uuid primary key default gen_random_uuid(),
  space_id      uuid not null references container.spaces(space_id),
  project_key   text not null unique,
  address       text generated always as ('project://' || project_key) stored,
  project_type  text,                                   -- design|meta|operations|research|... (open)
  root_path     text,                                   -- absorbs ops/ledger_interpret.py PROJECT_ROOTS
                                                        -- (the dict dies as code, lives as data — C1.5;
                                                        --  mechanically fixes the missing-`platforms` defect)
  keeper_role   text,                                   -- a registered cognition ROLE id (L7 binds it)
  status        text not null default 'active',
  phase         text,
  description   text,
  entry_points  jsonb not null default '[]'::jsonb,
  decorators    text[] not null default '{}',           -- the one lane the cloud actually queried by
  tags          text[] not null default '{}',
  source_system text,
  source_uuid   uuid,
  source_meta   jsonb,                                  -- verbatim source facts NOT structurally adopted
                                                        -- (cloud ltree paths, keeper_agent-as-found, …) —
                                                        -- dead-stuff-carries-intention: kept legible, never lost
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now()
);
create unique index if not exists projects_address_uq on container.projects (address);

-- ── Scope — a named, AUTHORED sub-container (curated shelf: decisions/, patterns/). Explicitly distinct
-- from DERIVED containment (directories/sessions — the ledger's): both are `contains`, differing by
-- PROVENANCE, never by mechanism (law 8). scope_key may repeat across parents once nesting is real;
-- identity is the UNIQUE address (project://<key>/<scope-path>), never a hand-kept path column.
create table if not exists container.scopes (
  scope_id        uuid primary key default gen_random_uuid(),
  project_id      uuid not null references container.projects(project_id) on delete cascade,
  parent_scope_id uuid references container.scopes(scope_id),
  scope_key       text not null,
  scope_type      text not null default 'folder',       -- folder|registry|... (open)
  address         text not null unique,                 -- project://<project-key>/<scope-path>
  description     text,
  decorators      text[] not null default '{}',
  tags            text[] not null default '{}',
  source_system   text,
  source_uuid     uuid,
  source_meta     jsonb,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index if not exists scopes_project_idx on container.scopes (project_id);

-- ── Resource — an AUTHORED content unit (the ABOUT layer; the ledger entry is the derived IS layer).
-- address TEXT NOT NULL UNIQUE = the ci_* lesson (mandatory, one grammar). The cloud's dead
-- embedding vector(384) column is NOT reproduced — resources embed through the ONE pipeline
-- (ledger.embedding) when they embed at all. uri_refs finally gets to point at code:// / exchange://
-- addresses; referenced_by is COMPOSED AT READ, never stored (law 4).
create table if not exists container.resources (
  resource_id     uuid primary key default gen_random_uuid(),
  project_id      uuid not null references container.projects(project_id) on delete cascade,
  scope_id        uuid references container.scopes(scope_id),
  resource_key    text not null,
  resource_type   text not null,                        -- document|note|pattern|decision|law|... (open; L3 types)
  address         text not null unique,                 -- project://<project-key>/<scope-path>/<resource-key>
  title           text,
  content         jsonb,
  content_hash    text,
  version         int not null default 1,
  version_history jsonb not null default '[]'::jsonb,
  decorators      text[] not null default '{}',
  tags            text[] not null default '{}',
  uri_refs        text[] not null default '{}',         -- typed pointers OUT (code://…, exchange://…)
  provenance      jsonb,                                 -- back-write stamp {source_doc, commit_sha, …}
  created_by      text,                                  -- a principal ADDRESS
  source_system   text,
  source_uuid     uuid,
  source_meta     jsonb,
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index if not exists resources_project_idx on container.resources (project_id);
create index if not exists resources_scope_idx   on container.resources (scope_id);
create index if not exists resources_type_idx    on container.resources (resource_type);

-- ── Members — ONE membership edge type across all containers (law 7). principal is an ADDRESS
-- (operator://tim, agent://vi, agent://ci-keeper-agent); L2's principal table attaches to it later.
create table if not exists container.members (
  member_id     uuid primary key default gen_random_uuid(),
  project_id    uuid not null references container.projects(project_id) on delete cascade,
  member_type   text not null check (member_type in ('operator','human','agent','client')),
  principal     text not null,                          -- a principal ADDRESS (law 6)
  role          text not null default 'member',
  source_system text,
  source_uuid   uuid,
  created_at    timestamptz not null default now(),
  unique (project_id, principal, role)
);

-- ── Exclusions — every curation writes excluded-with-reason (standing rule / law 8 of the criteria).
-- The migration's excluded cloud rows land HERE (queryable beside what landed), as well as in the
-- printed reconciliation report. cvi_mine itself is never touched.
create table if not exists container.exclusions (
  exclusion_id  uuid primary key default gen_random_uuid(),
  source_system text not null,                          -- 'cvi_mine'
  source_table  text not null,                          -- 'projects' | 'spaces' | 'project_scopes' | …
  source_uuid   uuid,
  source_key    text,                                   -- the human-legible key (project_key, space_key…)
  reason        text not null,
  excluded_at   timestamptz not null default now(),
  unique (source_system, source_table, source_uuid)
);

-- ── The ledger joins the spine — ADDITIVE nullable FKs; the bare text label STAYS (rule 2).
-- ADOPTION: ledger.coverage_findings existed on the live DB only via ops/extraction_audit_run.py's ad-hoc
-- `create table if not exists` (an UNTRACKED table — no migration home; found by this lane's scratch-DB
-- idempotency proof). Its exact live DDL is adopted HERE so a fresh checkout reproduces the live schema
-- (registry-is-truth: the migrations dir is the schema's registry). Idempotent both ways.
create table if not exists ledger.coverage_findings (
  entry_id  uuid primary key,
  project   text,
  path      text,
  file_kind text,
  complete  boolean,
  findings  jsonb,
  kind_seen text,
  run_addr  text,
  ts        timestamptz default now()
);
alter table ledger.entry             add column if not exists project_id uuid references container.projects(project_id);
alter table ledger.run               add column if not exists project_id uuid references container.projects(project_id);
alter table ledger.coverage_findings add column if not exists project_id uuid references container.projects(project_id);
create index if not exists entry_project_id_idx on ledger.entry (project_id);

-- ── BACKFILL DECAY CURE — the one-shot ops backfill sets project_id for EXISTING rows; without this a
-- NEW ledger row arriving with a bare `project` label but no project_id would rot the 100% coverage.
-- This BEFORE INSERT trigger keeps the join self-maintaining: a known label resolves its project_id from
-- the registry (container.projects); an UNKNOWN label is LEFT NULL + a NOTICE names it (derive-never-
-- invent — a label is never fabricated into a project row). Idempotent: CREATE OR REPLACE + guarded
-- (DROP IF EXISTS → CREATE) triggers on all three label-bearing tables.
create or replace function container.ledger_backfill_project_id() returns trigger as $fn$
declare pid uuid;
begin
  if new.project_id is null and new.project is not null then
    select project_id into pid from container.projects where project_key = new.project;
    if pid is not null then
      new.project_id := pid;                       -- known label → resolve from the registry
    else
      raise notice 'ledger backfill: unknown project label % — project_id left NULL (no container.projects '
                   'row; derive-never-invent). fix: create_project(%) or apply the curation.',
                   new.project, new.project;
    end if;
  end if;
  return new;
end
$fn$ language plpgsql;

drop trigger if exists trg_backfill_project_id on ledger.entry;
create trigger trg_backfill_project_id before insert on ledger.entry
  for each row execute function container.ledger_backfill_project_id();
drop trigger if exists trg_backfill_project_id on ledger.run;
create trigger trg_backfill_project_id before insert on ledger.run
  for each row execute function container.ledger_backfill_project_id();
drop trigger if exists trg_backfill_project_id on ledger.coverage_findings;
create trigger trg_backfill_project_id before insert on ledger.coverage_findings
  for each row execute function container.ledger_backfill_project_id();

commit;
