-- 0023_keeper.sql — ④ THE CONTAINER (the-one-system, L7-KEEPER): the keeper CONFIG RUNGS' DB home.
-- (Migrations 0013=④ SPINE · 0014-0016 ledger/supersession · 0017=L2 IDENTITY · 0018=L4 GRAPH ·
--  0019=L3 REGISTRY · 0020=L6 BOARD · 0021=L5 CIRCUIT marks · 0022 RESERVED for the ledger session's
--  scale-drill. This lane takes 0023, the next free non-reserved number — confirmed by `ls migrations/`.)
--
-- The rebuilt KEEPER organ (organ-studies/KEEPER.md §4): the tending AI is NOT a new primitive — it is a
-- COMPOSITION of four existing addresses: a member EDGE (L1, written at project birth) + a CAST
-- (cast_for_mode('keeper'), roles/ files) + CONFIG RUNGS (this table) + a PERSONA record (a config rung).
--
-- THIS FILE lands only the CONFIG-RUNGS half — the parametrization. Per KEEPER.md §4.2 the cloud's
-- `keeper_agent_config {space_id, project_id, scope_key, config_key, config_value, override_level}` is
-- RE-EXPRESSED here: override_level (0=global,1=space,2=project,3=scope) WAS containment depth in
-- disguise, so the (space/project/scope) coordinate collapses to ONE `address_prefix` string and the row
-- IS a rung on the ONE ladder (runtime/resolver.py ladder slot-kind). ci_resolve_keeper_config's
-- `ORDER BY override_level DESC LIMIT 1` == the ladder's longest-prefix-wins. NO second resolver: the
-- runtime reads these rows into a {"ladder":"address","rungs":{...}} invariant and resolves via resolve().
--
-- LAWS CARRIED:
--   · ONE ladder mechanism (law): rungs are DATA; resolution is the ONE pure resolver (reuse-don't-parallel).
--   · vocabulary=files / data=DB (law 3): config_key names + persona/role VOCABULARY stay in files
--     (roles/, the keeper self-model); the rung VALUES per address live here as DATA.
--   · schema-additive (constitution rule 2): a NEW table in the existing `container` schema; nothing edited.
--   · fail-loud + breadcrumbs: an absent rung with no universal/default fails loud AT RESOLVE (the ladder
--     slot), never a silent wrong rung — this table just holds the values.
--   · the address IS the level (KEEPER.md §4.2): address_prefix '' = universal (cloud L0);
--     'space://<k>' = space (L1); 'project://<k>' = project (L2); 'project://<k>#<scope>' = scope (L3).
--
-- THE 4 CLOUD ROWS carry over VERBATIM (source: cvi_mine.keeper_agent_config, 4 rows, READ-ONLY):
--   · initialization_procedure  L0 → rung ''                          (universal)
--   · navigation_capabilities   L0 → rung ''                          (universal)
--   · creation_capabilities     L0 → rung ''                          (universal)
--   · domain_expertise          L2 → rung 'project://ci-processing'   (cloud project_id
--       c3fa018d-0d06-4820-b648-a95dd6902ca3 == container.projects.source_uuid → project_key ci-processing;
--       resolved from container.projects at seed time, NEVER hand-mapped — derive-never-invent).
--
-- IDEMPOTENT: safe to re-apply (IF NOT EXISTS; seed via ON CONFLICT DO NOTHING keyed on the PK).
-- TRANSACTION SAFETY: ONE transaction (BEGIN..COMMIT) with a fail-loud prerequisite guard at the top —
--   an unmet prerequisite or any mid-apply error ROLLS THE WHOLE THING BACK (no half-apply).
-- REVERSAL: DROP TABLE IF EXISTS container.config_rung;

begin;

-- ── PREREQUISITE GUARD (fail loud, no half-apply) — L7 builds additively on L1's schema `container`.
do $guard$
begin
  if not exists (select 1 from information_schema.schemata where schema_name = 'container') then
    raise exception 'expected schema container (0013_container.sql, ④ L1-SPINE); previously n/a; '
                    'fix: apply 0013_container.sql first (psql -f build-prep/claude-design/supabase/'
                    'supabase/migrations/0013_container.sql)';
  end if;
  -- domain_expertise seeds at project://ci-processing — that project must exist (it landed in L1's
  -- migration). If it is absent the seed below would silently no-op the deepest rung, so fail loud here.
  if not exists (select 1 from container.projects where project_key = 'ci-processing') then
    raise exception 'expected container.projects row project_key=ci-processing (L1 migration); previously n/a; '
                    'fix: run ops/migrate_container_from_cvi.py (L1-SPINE) first';
  end if;
end
$guard$;

-- ── container.config_rung — the keeper config LADDER as rows. One row = one rung of one config_key.
-- (address_prefix, config_key) is the PK: exactly one value per config_key per containment rung, which is
-- what longest-prefix resolution needs (no duplicate-depth ambiguity — the cloud's UNIQUE per
-- (space,project,scope,key) re-expressed on the address). config_value rides jsonb (open-record, so a
-- flags dict / a steps list / a persona blob all fit without a schema edit).
create table if not exists container.config_rung (
    address_prefix text not null,            -- the rung's containment address: '' = universal;
                                             --   'space://<k>' | 'project://<k>' | 'project://<k>#<scope>'
    config_key     text not null,            -- the parameter name (vocabulary is declared in files/roles)
    config_value   jsonb not null,           -- the value AT this rung (open-record)
    source_meta    jsonb not null default '{}'::jsonb,  -- provenance (cloud override_level/ids — dead-stuff-carries-intention)
    updated_at     timestamptz not null default now(),
    primary key (address_prefix, config_key)
);
create index if not exists config_rung_key_idx on container.config_rung (config_key);

comment on table container.config_rung is
'L7-KEEPER: keeper config as LADDER RUNGS (KEEPER.md §4.2). (address_prefix, config_key) → config_value.
address_prefix '''' = universal (cloud override_level 0); project://<k> = project (2); project://<k>#<s> =
scope (3). The runtime reads these into a {"ladder":"address","rungs":{...}} invariant and resolves via the
ONE resolver (runtime/resolver.resolve) — longest-prefix-wins, walk-up, fail-loud below. ci_resolve_keeper_config
(ORDER BY override_level DESC LIMIT 1) re-expressed as data + the ladder slot. The 4 cloud rows carry over verbatim.';

-- ── SEED the 4 cloud rows VERBATIM (config_value copied byte-for-byte from cvi_mine.keeper_agent_config).
-- Universal rungs (override_level 0 → address_prefix '').
insert into container.config_rung (address_prefix, config_key, config_value, source_meta) values
  ('', 'initialization_procedure',
   '{"steps": ["load_project_context", "index_resources_by_decorator", "build_knowledge_map", "check_active_issues", "identify_priorities"]}'::jsonb,
   '{"cloud_override_level": 0, "source": "cvi_mine.keeper_agent_config"}'::jsonb),
  ('', 'navigation_capabilities',
   '{"search_resources": true, "traverse_hierarchy": true, "filter_by_decorator": true, "cross_project_search": true}'::jsonb,
   '{"cloud_override_level": 0, "source": "cvi_mine.keeper_agent_config"}'::jsonb),
  ('', 'creation_capabilities',
   '{"create_projects": true, "create_resources": true, "create_workflows": true, "annotate_entities": true}'::jsonb,
   '{"cloud_override_level": 0, "source": "cvi_mine.keeper_agent_config"}'::jsonb)
on conflict (address_prefix, config_key) do nothing;

-- The KEEPER's GLOBAL PERSONA (a keeper self-model default — NOT a cloud keeper_agent_config row; the
-- cloud held persona as vi_shared.vi_persona, a THIRD articulation both sides lacked, KEEPER.md §5). Landed
-- as a UNIVERSAL rung so agent://keeper/persona resolves everywhere and a deeper project rung OVERRIDES it
-- (C7.5). The VOCABULARY (what a persona says) is authored data; a richer persona may later be sourced from
-- vi_shared.vi_persona (ore). config_key='persona'.
insert into container.config_rung (address_prefix, config_key, config_value, source_meta) values
  ('', 'persona',
   '{"name": "Keeper", "voice": "a steady tending intelligence — plain, grounded, at the operator''s altitude", "stance": "I tend one project: I know what it holds, what is in flight, and I answer from its own ledger, never invention. I flag what I cannot ground.", "version": 1}'::jsonb,
   '{"source": "keeper self-model default (L7); overridable per project by a deeper rung; may later source vi_shared.vi_persona"}'::jsonb)
on conflict (address_prefix, config_key) do nothing;

-- domain_expertise (override_level 2, cloud project_id c3fa018d… ) → the project rung. The address_prefix
-- is DERIVED from container.projects (source_uuid match) so it is never hand-typed / cannot drift.
insert into container.config_rung (address_prefix, config_key, config_value, source_meta)
select p.address,
       'domain_expertise',
       '{"specializations": ["pipeline_composition", "langgraph_integration", "schema_design", "pattern_detection", "embedding_strategies", "mcp_tool_design"]}'::jsonb,
       jsonb_build_object('cloud_override_level', 2,
                          'cloud_project_id', 'c3fa018d-0d06-4820-b648-a95dd6902ca3',
                          'source', 'cvi_mine.keeper_agent_config')
from container.projects p
where p.source_uuid = 'c3fa018d-0d06-4820-b648-a95dd6902ca3'
on conflict (address_prefix, config_key) do nothing;

commit;
