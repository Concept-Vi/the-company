-- 0017_identity.sql — ④ THE CONTAINER (the-one-system, L2-IDENTITY): the ONE principal model.
-- (Migrations 0013=④ SPINE · 0014-0016 RESERVED for the ledger/supersession session (ch-lp5ecuvo) ·
--  0018=L4 GRAPH · 0019=L3 REGISTRY. This lane takes 0017, the next free non-reserved number.)
--
-- The rebuilt TENANCY organ (organ-studies/TENANCY.md §3): "A: who belongs · B: how it's checked ·
-- C: how an outsider is contracted in" braided into ONE identity model on Side B's physics.
--
-- LAWS CARRIED:
--   · ONE principal model (law 7): kinds {operator, human, agent, client} — an OPEN vocabulary (no hard
--     CHECK; extends by ADDING a value, the grants.py principal_type pattern). Exactly ONE operator (Tim).
--   · authentication is an EDGE TO identity (law 7): principal_auth(principal_id, auth_user_id) — a
--     credential is a FK-less edge to a principal, NEVER identity itself. Humans/clients have one+ auth
--     users; most agents none. Fixes A's partiality (space_members FK auth.users can't hold agents)
--     WITHOUT breaking it — additive.
--   · actors are ADDRESSES (law 6): principal.address is GENERATED (kind || '://' || handle) so it can
--     never be hand-placed or drift — it is exactly the address L1's container.members.principal carries
--     (operator://tim, agent://vi), so members FK-join to it by the existing string.
--   · delegation is FIRST-CLASS + finally wired to enforcement (law 7): grantee is a principal FK (not
--     A's bare 'vi:global' text); the ceiling (max_autonomy L0-L5 + window + scopes) is read by the
--     runtime guard (runtime/governance.guard, L5 of the auth stack).
--   · reverses composed at read (law 4): referenced_by / who-can-see is a READ (may()/access_of()),
--     never a stored duplicate.
--   · schema-additive (constitution rule 2): every table is NEW; container.members gains a NULLABLE
--     principal_id FK (the L1 address column STAYS — nothing L1 breaks; container_acceptance stays green).
--
-- Tim's identity correction (THE-CONTAINER v3 DECISIONS): v.i@conceptv.com.au is VI's OWN email (VI has
--   an email), t.geldard@ is Tim's MAIN. So: operator://tim (t.geldard@ primary login) + agent://vi
--   (v.i@ AND vi@system.local attach to it — one agent, two logins) + a standing acts-for delegation
--   operator://tim -> agent://vi ("I am both" = the creator relationship, expressed as delegation, NOT
--   identity-merge). The env OPERATOR_USER_ID currently = v.i@'s uuid (ebe5f9c7) — the remote gate's
--   remap runs shadow-then-flip and the FLIP is needs-tim (mcp_face/remote.py; C2.2).
--
-- IDEMPOTENT: safe to re-apply (IF NOT EXISTS everywhere; seed via ON CONFLICT; ADD COLUMN IF NOT EXISTS).
-- TRANSACTION SAFETY: ONE transaction (BEGIN..COMMIT) with a fail-loud prerequisite guard at the top —
--   an unmet prerequisite or any mid-apply error ROLLS THE WHOLE THING BACK (no half-apply).
-- REVERSAL: DROP TABLE IF EXISTS container.delegation_evidence, container.delegation,
--             container.principal_auth, container.uuid_rewrite_map, container.principal CASCADE;
--           ALTER TABLE container.members DROP COLUMN IF EXISTS principal_id;
-- Data lands via ops/migrate_identity_from_cvi.py (the 15 cloud users → principals + uuid rewrite map +
--   the 13-duplicate delegation collapse + the L5 grant; idempotent, reconciliation-reported, never
--   mutates cvi_mine).

begin;

-- ── PREREQUISITE GUARD (fail loud, no half-apply) — L2 builds additively on L1's schema `container`.
do $guard$
begin
  if not exists (select 1 from information_schema.schemata where schema_name = 'container') then
    raise exception 'expected schema container (0013_container.sql, ④ L1-SPINE); previously n/a; '
                    'fix: apply 0013_container.sql first (psql -f build-prep/claude-design/supabase/'
                    'supabase/migrations/0013_container.sql)';
  end if;
end
$guard$;

-- ── Principal — the ONE identity model. kind is OPEN (no hard CHECK; the vocabulary is
-- {operator, human, agent, client}, extended by ADDING a value — the grants.py principal_type law).
-- address is DERIVED (generated column) = kind || '://' || handle, so it is exactly the ADDRESS L1's
-- container.members.principal already carries (operator://tim, agent://vi) — actors are addresses (law 6).
create table if not exists container.principal (
  principal_id  uuid primary key default gen_random_uuid(),
  kind          text not null,                          -- operator|human|agent|client (OPEN — extend by value)
  handle        text not null,                          -- the address local part (tim, vi, ci-keeper-agent)
  address       text generated always as (kind || '://' || handle) stored,
  display       text,
  status        text not null default 'active',
  metadata      jsonb not null default '{}'::jsonb,
  source_system text,                                   -- 'identity_seed' | 'cvi_mine' | ...
  source_uuid   uuid,                                   -- the original cloud auth.users uuid, if migrated
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  unique (kind, handle)
);
create unique index if not exists principal_address_uq on container.principal (address);
create index if not exists principal_kind_idx on container.principal (kind);

-- ── Principal_auth — AUTHENTICATION IS AN EDGE TO IDENTITY (never identity itself). A principal may
-- hold zero (most agents) or many (a human with several logins; the vi agent with v.i@ + vi@system.local)
-- auth users. auth_user_id is a SOFT reference to the identity provider's user id (cvi_mine.auth.users /
-- Supabase GoTrue) — NOT a hard FK, because those auth.users live in the cloud/cvi provider, not
-- necessarily on this DB. is_primary marks the login OPERATOR_USER_ID resolves to (C2.2).
create table if not exists container.principal_auth (
  auth_edge_id  uuid primary key default gen_random_uuid(),
  principal_id  uuid not null references container.principal(principal_id) on delete cascade,
  auth_user_id  uuid not null,                          -- the provider's user id (soft ref; provider below)
  provider      text not null default 'supabase',
  is_primary    boolean not null default false,
  source_system text,
  created_at    timestamptz not null default now(),
  unique (principal_id, auth_user_id)
);
create unique index if not exists principal_auth_user_uq on container.principal_auth (auth_user_id);

-- ── Delegation — FIRST-CLASS (A's table, grantee resolved to a principal FK, finally wired to
-- enforcement). container_address NULL = global (A's space=NULL). max_autonomy L0-L5 is the CEILING the
-- runtime guard reads (stricter of class posture and this). `confirmed` marks the one canonical grant the
-- 13 duplicate historical grants collapse INTO (C2.5). kind: acts_for (the creator relationship, authored
-- by the seed) | historical (migrated from cvi). The unique index coalesces NULL container_address so a
-- second (delegator, grantee, global) can't sneak a duplicate past NULL<>NULL (Postgres NULL-distinctness).
create table if not exists container.delegation (
  delegation_id     uuid primary key default gen_random_uuid(),
  delegator         uuid not null references container.principal(principal_id),
  grantee           uuid not null references container.principal(principal_id),
  container_address text,                               -- NULL = global (A's space=NULL)
  scopes            text[] not null default '{}',       -- normalized scope-grammar tokens (scope_grammar/)
  max_autonomy      text not null default 'L3' check (max_autonomy in ('L0','L1','L2','L3','L4','L5')),
  valid_from        timestamptz not null default now(),
  valid_to          timestamptz,
  status            text not null default 'active' check (status in ('active','suspended','revoked')),
  confirmed         boolean not null default false,     -- the collapsed canonical grant is confirmed (C2.5)
  kind              text not null default 'acts_for',   -- acts_for (authored) | historical (migrated)
  source_system     text,
  source_uuid       uuid,
  created_at        timestamptz not null default now(),
  updated_at        timestamptz not null default now()
);
create unique index if not exists delegation_uq
  on container.delegation (delegator, grantee, coalesce(container_address, ''));
create index if not exists delegation_grantee_idx on container.delegation (grantee);

-- ── Delegation_evidence — the 13 duplicate historical grants collapse to ONE confirmed delegation with
-- 13 EVIDENCE entries (C2.5); each preserves its source cvi row (dead-stuff-carries-intention: the
-- system-wide "every user delegated to vi" pattern is kept legible, never lost).
create table if not exists container.delegation_evidence (
  evidence_id        uuid primary key default gen_random_uuid(),
  delegation_id      uuid not null references container.delegation(delegation_id) on delete cascade,
  source_system      text not null,                     -- 'cvi_mine'
  source_table       text not null default 'delegations',
  source_uuid        uuid,                              -- the cvi delegation_id
  source_delegator   uuid,                              -- the cvi user_id (the original grantor)
  source_grantee     text,                              -- 'vi:global' (A's bare text)
  source_scopes      text[],
  source_max_autonomy text,
  source_valid_from  timestamptz,
  note               text,
  created_at         timestamptz not null default now(),
  unique (delegation_id, source_uuid)
);

-- ── Uuid_rewrite_map — the old cloud auth.users uuid → the principal it becomes (C2.3). Every subsequent
-- pour (L5 circuit, L6 board) rewrites created_by/owner/granted_by columns THROUGH this map. disposition
-- records the landing (operator|agent|human|archived); an archived (no-email test-debris) uuid maps to a
-- NULL principal_id WITH its reason (excluded-with-reason).
create table if not exists container.uuid_rewrite_map (
  old_uuid          uuid primary key,                   -- the cvi_mine auth.users id
  principal_id      uuid references container.principal(principal_id),  -- NULL for archived
  principal_address text,                               -- convenience mirror (operator://tim, ...)
  disposition       text not null,                      -- operator|agent|human|archived
  reason            text,
  source_system     text not null default 'cvi_mine',
  created_at        timestamptz not null default now()
);

-- ── Membership joins the principal model — L1's container.members IS the ONE membership edge (law 7);
-- L2 makes it the full edge ADDITIVELY (the L1 `principal` address column + project_id STAY untouched;
-- nothing L1 built breaks — container_acceptance stays green). principal_id = the resolved FK (backfilled
-- by the address join below); scopes/role_definition_id/granted_by/granted_at/revoked_at complete A's
-- richest membership shape (organ-studies/TENANCY.md §3.2), all nullable/defaulted so existing rows read
-- exactly as before.
alter table container.members add column if not exists principal_id       uuid references container.principal(principal_id);
alter table container.members add column if not exists scopes             text[] not null default '{}';
alter table container.members add column if not exists role_definition_id uuid;
alter table container.members add column if not exists granted_by         text;   -- a principal ADDRESS (law 6)
alter table container.members add column if not exists granted_at         timestamptz not null default now();
alter table container.members add column if not exists revoked_at         timestamptz;

-- ══ THE OPERATOR SEED (C2.1) — registry-authored, NEVER an env default. Idempotent (ON CONFLICT). ══════
-- ONE operator principal (Tim) + the vi AGENT principal + the two internal agent principals L1's
-- container.members already reference (ci-keeper-agent, keeper) so members.principal_id backfills 100%
-- from the SQL alone. The cloud HUMANS (grant/phil/scott/nick) + the archives land via the migrate script.
insert into container.principal (kind, handle, display, status, metadata, source_system) values
  ('operator', 'tim', 'Tim Geldard', 'active',
   '{"note":"the ONE operator — founder/CEO; identity IS the boundary (remote.py). t.geldard@ primary login."}'::jsonb,
   'identity_seed'),
  ('agent', 'vi', 'Vi', 'active',
   '{"note":"the autonomous system principal — vi:global == vi@system.local, finally ONE row. v.i@ is VIs OWN email."}'::jsonb,
   'identity_seed'),
  ('agent', 'ci-keeper-agent', 'CI Keeper Agent', 'active', '{}'::jsonb, 'identity_seed'),
  ('agent', 'keeper', 'Keeper', 'active', '{}'::jsonb, 'identity_seed')
on conflict (kind, handle) do nothing;

-- principal_auth: authentication edges (C2.1). t.geldard@ (554e223d) is the operator's PRIMARY login;
-- v.i@ (ebe5f9c7) AND vi@system.local (…0001) both attach to the ONE vi agent (Tim's correction).
insert into container.principal_auth (principal_id, auth_user_id, provider, is_primary, source_system)
select p.principal_id, '554e223d-e431-41ce-8913-1a7d8d81d321'::uuid, 'supabase', true, 'identity_seed'
  from container.principal p where p.address = 'operator://tim'
on conflict (principal_id, auth_user_id) do nothing;
insert into container.principal_auth (principal_id, auth_user_id, provider, is_primary, source_system)
select p.principal_id, 'ebe5f9c7-4d66-4717-835f-afc96088facb'::uuid, 'supabase', true, 'identity_seed'
  from container.principal p where p.address = 'agent://vi'
on conflict (principal_id, auth_user_id) do nothing;
insert into container.principal_auth (principal_id, auth_user_id, provider, is_primary, source_system)
select p.principal_id, '00000000-0000-0000-0000-000000000001'::uuid, 'supabase', false, 'identity_seed'
  from container.principal p where p.address = 'agent://vi'
on conflict (principal_id, auth_user_id) do nothing;

-- the standing acts-for delegation operator://tim -> agent://vi (C2.1). The creator "I am both"
-- relationship expressed as DELEGATION, not identity-merge. L5 = full autonomy (Tim's own agent acting
-- for him; the historical super-user power v.i@ held, now correctly framed as the operator delegating).
-- The migrate script CONFIRMS this row + attaches the 13 historical-grant evidence entries (C2.5).
insert into container.delegation (delegator, grantee, container_address, scopes, max_autonomy,
                                  status, kind, source_system)
select o.principal_id, v.principal_id, null,
       array['read','write','create:intent','create:proposal','create:agent_workflow',
             'deploy:langgraph','manage:user_agents']::text[],
       'L5', 'active', 'acts_for', 'identity_seed'
  from container.principal o, container.principal v
 where o.address = 'operator://tim' and v.address = 'agent://vi'
on conflict (delegator, grantee, coalesce(container_address, '')) do nothing;

-- backfill container.members.principal_id from the address (the L1 edge joins the L2 model). Idempotent.
update container.members m
   set principal_id = p.principal_id
  from container.principal p
 where p.address = m.principal and m.principal_id is null;

-- seed the uuid_rewrite_map for the THREE seeded logins (the migrate script adds the humans + archives).
insert into container.uuid_rewrite_map (old_uuid, principal_id, principal_address, disposition, reason)
select '554e223d-e431-41ce-8913-1a7d8d81d321'::uuid, p.principal_id, 'operator://tim', 'operator',
       't.geldard@conceptv.com.au — Tims MAIN account → the ONE operator principal (primary login).'
  from container.principal p where p.address = 'operator://tim'
on conflict (old_uuid) do nothing;
insert into container.uuid_rewrite_map (old_uuid, principal_id, principal_address, disposition, reason)
select 'ebe5f9c7-4d66-4717-835f-afc96088facb'::uuid, p.principal_id, 'agent://vi', 'agent',
       'v.i@conceptv.com.au — VIs OWN email (Tims correction) → the vi AGENT principal, NOT the operator.'
  from container.principal p where p.address = 'agent://vi'
on conflict (old_uuid) do nothing;
insert into container.uuid_rewrite_map (old_uuid, principal_id, principal_address, disposition, reason)
select '00000000-0000-0000-0000-000000000001'::uuid, p.principal_id, 'agent://vi', 'agent',
       'vi@system.local — the reserved Vi entity; vi:global == vi@system.local, one agent, second login.'
  from container.principal p where p.address = 'agent://vi'
on conflict (old_uuid) do nothing;

commit;
