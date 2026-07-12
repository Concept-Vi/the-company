-- 002_ltree_address.sql — the containment axis becomes NATIVE (Tim's catch: ltree was already installed).
-- ctx.unit gains `address ltree` — the canonical, indexed, operator-bearing form of the containment path
-- (address_path text stays as the display face; both derive from the same parent chain in the trigger).
-- ltree labels are [A-Za-z0-9_], dot-separated → sanitize: '-'→'_', '/'→'.'.

alter table ctx.unit add column if not exists address ltree;

create or replace function ctx._ltree_label(t text) returns text language sql immutable as
$$ select regexp_replace(replace(t, '-', '_'), '[^A-Za-z0-9_]', '', 'g') $$;

-- rewrite the insert trigger: derive BOTH faces from the parent
create or replace function ctx.unit_before_insert() returns trigger language plpgsql as $$
declare
  t ctx.unit_type;
  parent ctx.unit;
  lbl text;
begin
  select * into t from ctx.unit_type where type = new.type;
  if not found then
    raise exception 'ctx: unknown unit type "%" — register it in ctx.unit_type first (loud, never a silent default)', new.type;
  end if;
  if not (t.states ? new.state) then
    raise exception 'ctx: "%" is not a declared state of type "%" (declared: %)', new.state, new.type, t.states;
  end if;
  lbl := ctx._ltree_label(left(new.id::text, 8));
  if new.parent_id is not null then
    select * into parent from ctx.unit where id = new.parent_id;
    if not found then raise exception 'ctx: parent % not found', new.parent_id; end if;
    new.address_path := parent.address_path || '/' || left(new.id::text, 8);
    new.address := parent.address || lbl::ltree;
  else
    if new.address_path is null or new.address_path = '' then
      raise exception 'ctx: a ROOT unit must supply its own address_path (it is the frame)';
    end if;
    new.address := ctx._ltree_label(new.address_path)::ltree;
  end if;
  return new;
end $$;

-- backfill existing rows (parents before children — order by path depth)
update ctx.unit u set address = sub.addr from (
  with recursive w(id, addr) as (
    select id, ctx._ltree_label(address_path)::ltree from ctx.unit where parent_id is null
    union all
    select c.id, w.addr || ctx._ltree_label(left(c.id::text,8))::ltree
    from ctx.unit c join w on c.parent_id = w.id
  ) select * from w
) sub where u.id = sub.id;

alter table ctx.unit alter column address set not null;
create index if not exists unit_address_gist on ctx.unit using gist (address);
