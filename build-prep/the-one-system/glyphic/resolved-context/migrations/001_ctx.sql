-- 001_ctx.sql — the RESOLVED-CONTEXT substrate (C1, GUIDE §C1)
-- ONE recursive conversation-unit schema. Tim's two binding corrections are the foundation:
--   (1) scale-relative units: sentence⊂message⊂session⊂project — ONE table, no privileged level;
--       the address is the containment path.
--   (2) state is an AXIS with consequences: type-declared lifecycles (registry rows, fail-loud
--       like cc_board) + pg_notify on transitions so the DATA layer fires behavior.
-- Purely ADDITIVE beside ledger.* (coordinated on chan-provider-registry-a3d23aae). Reversible:
--   drop schema ctx cascade;

create schema if not exists ctx;

-- ---------------------------------------------------------------------------
-- The TYPE registry — lifecycles are DATA. Adding a type/state = an INSERT.
-- ---------------------------------------------------------------------------
create table if not exists ctx.unit_type (
  type        text primary key,
  description text not null,
  states      jsonb not null,   -- ["draft","open",...]
  transitions jsonb not null    -- {"draft":["open"], "open":["answered","superseded","parked"], ...}
);

create table if not exists ctx.unit (
  id           uuid primary key default gen_random_uuid(),
  parent_id    uuid references ctx.unit(id),
  type         text not null references ctx.unit_type(type),
  state        text not null,
  address_path text not null,
  body         text,
  meta         jsonb not null default '{}',
  ts           timestamptz not null default now()
);
create index if not exists unit_parent_idx  on ctx.unit(parent_id);
create index if not exists unit_state_idx   on ctx.unit(state);
create index if not exists unit_address_idx on ctx.unit(address_path text_pattern_ops);

create table if not exists ctx.edge_kind (
  kind        text primary key,
  description text not null
);

create table if not exists ctx.unit_edge (
  from_id uuid not null references ctx.unit(id),
  to_id   uuid not null references ctx.unit(id),
  kind    text not null references ctx.edge_kind(kind),
  ts      timestamptz not null default now(),
  primary key (from_id, to_id, kind)
);

-- ---------------------------------------------------------------------------
-- INSERT guard: state must be a declared state of the type; address_path derives
-- from the parent (containment) unless a root supplies its own.
-- ---------------------------------------------------------------------------
create or replace function ctx.unit_before_insert() returns trigger language plpgsql as $$
declare
  t ctx.unit_type;
  parent ctx.unit;
begin
  select * into t from ctx.unit_type where type = new.type;
  if not found then
    raise exception 'ctx: unknown unit type "%" — register it in ctx.unit_type first (loud, never a silent default)', new.type;
  end if;
  if not (t.states ? new.state) then
    raise exception 'ctx: "%" is not a declared state of type "%" (declared: %)', new.state, new.type, t.states;
  end if;
  if new.parent_id is not null then
    select * into parent from ctx.unit where id = new.parent_id;
    if not found then
      raise exception 'ctx: parent % not found', new.parent_id;
    end if;
    -- containment address: parent path / short-id (first 8 of the uuid)
    new.address_path := parent.address_path || '/' || left(new.id::text, 8);
  elsif new.address_path is null or new.address_path = '' then
    raise exception 'ctx: a ROOT unit must supply its own address_path (it is the frame)';
  end if;
  return new;
end $$;
drop trigger if exists unit_before_insert on ctx.unit;
create trigger unit_before_insert before insert on ctx.unit
  for each row execute function ctx.unit_before_insert();

-- ---------------------------------------------------------------------------
-- STATE transitions: enforced from the type's registry row (illegal → loud
-- exception naming the legal set), then FIRED via pg_notify — the state axis
-- has consequences at the data layer.
-- ---------------------------------------------------------------------------
create or replace function ctx.unit_state_transition() returns trigger language plpgsql as $$
declare
  t ctx.unit_type;
  legal jsonb;
begin
  if new.state is distinct from old.state then
    select * into t from ctx.unit_type where type = new.type;
    legal := coalesce(t.transitions -> old.state, '[]'::jsonb);
    if not (legal ? new.state) then
      raise exception 'ctx: illegal transition "%"->"%" for type "%". Legal from "%": % (the registry-declared lifecycle is the only truth)',
        old.state, new.state, new.type, old.state, legal;
    end if;
    perform pg_notify('ctx_state', json_build_object(
      'id', new.id, 'type', new.type, 'old', old.state, 'new', new.state,
      'address', new.address_path)::text);
  end if;
  return new;
end $$;
drop trigger if exists unit_state_transition on ctx.unit;
create trigger unit_state_transition before update of state on ctx.unit
  for each row execute function ctx.unit_state_transition();

-- ---------------------------------------------------------------------------
-- Seed types (lifecycles as data) + edge kinds. Idempotent upserts.
-- ---------------------------------------------------------------------------
insert into ctx.unit_type (type, description, states, transitions) values
 ('session', 'a whole conversation/session frame',
  '["active","closed"]', '{"active":["closed"],"closed":["active"]}'),
 ('message', 'one turn inside a session',
  '["present"]', '{}'),
 ('block',   'a bounded idea-unit inside a message (scale-relative: any focus level)',
  '["draft","open","answered","superseded","parked"]',
  '{"draft":["open"],"open":["answered","superseded","parked"],"parked":["open"],"answered":["superseded"],"superseded":[]}'),
 ('comment', 'an annotation attached at a unit''s address',
  '["present","resolved"]', '{"present":["resolved"]}')
on conflict (type) do update set description = excluded.description,
  states = excluded.states, transitions = excluded.transitions;

insert into ctx.edge_kind (kind, description) values
 ('references',  'from mentions/uses to'),
 ('builds_on',   'from extends to''s idea'),
 ('supersedes',  'from replaces to (to should move to state superseded)'),
 ('answers',     'from resolves the question/openness of to'),
 ('comments_on', 'from is an annotation attached at to''s address')
on conflict (kind) do nothing;
