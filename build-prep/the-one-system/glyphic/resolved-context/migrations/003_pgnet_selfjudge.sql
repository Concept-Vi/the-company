-- 003_pgnet_selfjudge.sql — the DATA LAYER CALLS COGNITION (Tim's state-axis correction, full conclusion).
-- pg_net (installed): on INSERT of a judgeable unit, the DATABASE ITSELF fires the ctx_salience judge via
-- the bridge (async http). The response lands in net._http_response; ctx.sweep_verdicts() folds it into
-- unit.meta.verdict; pg_cron runs the sweep every minute. Insert a thought → it gets judged → the ledger
-- fills — no agent in the loop. Fail-loud: failed judge calls stay visible in ctx.judge_call (status).

create table if not exists ctx.judge_call (
  request_id bigint primary key,
  unit_id    uuid not null references ctx.unit(id),
  role       text not null default 'ctx_salience',
  ts         timestamptz not null default now(),
  status     text not null default 'sent'      -- sent | landed | failed
);

create or replace function ctx.unit_self_judge() returns trigger language plpgsql as $$
declare
  req bigint;
begin
  -- judge only content-bearing units (skip resolver logs etc.)
  if new.body is null or new.type not in ('block','message','session','comment') then
    return new;
  end if;
  select net.http_post(
    url  := 'http://host.docker.internal:8770/api/cognition/run_role',
    body := jsonb_build_object('role','ctx_salience','utterance', left(new.body, 4000))
  ) into req;
  insert into ctx.judge_call (request_id, unit_id) values (req, new.id);
  return new;
end $$;
drop trigger if exists unit_self_judge on ctx.unit;
create trigger unit_self_judge after insert on ctx.unit
  for each row execute function ctx.unit_self_judge();

-- fold landed responses into the units (idempotent; loud rows for failures)
create or replace function ctx.sweep_verdicts() returns int language plpgsql as $$
declare
  n int := 0;
  r record;
begin
  for r in
    select jc.request_id, jc.unit_id, resp.status_code, resp.content
    from ctx.judge_call jc join net._http_response resp on resp.id = jc.request_id
    where jc.status = 'sent'
  loop
    if r.status_code = 200 and (r.content::jsonb ? 'output') then
      update ctx.unit set meta = jsonb_set(meta, '{verdict}',
        (r.content::jsonb->'output') || jsonb_build_object('judged_by','ctx_salience','via','pg_net'))
        where id = r.unit_id;
      update ctx.judge_call set status = 'landed' where request_id = r.request_id;
      n := n + 1;
    else
      update ctx.judge_call set status = 'failed' where request_id = r.request_id;  -- visible, never silent
    end if;
  end loop;
  return n;
end $$;

-- every minute: fold verdicts (pg_cron)
select cron.schedule('ctx-sweep-verdicts', '* * * * *', $$select ctx.sweep_verdicts()$$)
where not exists (select 1 from cron.job where jobname = 'ctx-sweep-verdicts');
