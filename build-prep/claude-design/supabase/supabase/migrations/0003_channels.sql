-- 0003_channels.sql — CHANNELS as the SHARED MEETING GROUND in Supabase.
-- Tim's re-anchor: Claude Design PARTICIPATES in the company channels; everyone works on
-- the SAME DATA; Supabase is the neutral shared room; ZERO box exposure (the company box
-- reaches OUTBOUND to Supabase like the audit table; Claude Design reaches Supabase from
-- Anthropic's side; nobody connects into Tim's machine).
--
-- This mirrors the existing company channel fabric shape (agent_sessions/channels.jsonl:
-- id/kind/name/purpose/mode/coordinator/status/members/origin/created/last_activity) +
-- the mail-leaf post shape (frm/to/thread/text/ts) so fork's company-fabric → Supabase
-- sync lands clean. SCHEMA IS PROVISIONAL pending fork's confirm/adjust.
--
-- Participation model: the Edge Function writes a channel_post (Claude Design) → Supabase
-- Realtime delivers it to company sessions subscribed to the same Supabase → a company
-- session replies (writes a channel_post) → Realtime delivers it back to Claude Design.
-- RLS gates each side to the rows its role may touch.

create table if not exists public.channels (
    id            text primary key,            -- the channel id (matches agent_sessions/channels.jsonl)
    kind          text not null default 'channel',  -- channel | gathering
    name          text not null,
    purpose       text not null default '',
    mode          text not null default 'direct',   -- direct | conducted
    coordinator   text,                          -- conducting session id (conducted mode)
    status        text not null default 'active',  -- active | archived | dispersed | promoted
    members       jsonb not null default '[]'::jsonb,  -- [{session, participation}]
    origin        jsonb,                         -- {parent, promoted_to, ...} (nullable)
    posts         integer not null default 0,    -- denormalised post count (maintained by trigger)
    shared        boolean not null default false,  -- OPT-IN: false=internal (never leaves the box),
                                                   --   true=publishes to Supabase + client-eligible
    created_at    timestamptz not null default now(),
    last_activity timestamptz not null default now()
);
comment on table public.channels is
    'The shared channel registry — the company channel fabric + Claude Design meet here '
    '(Supabase is the neutral room). Mirrors agent_sessions/channels.jsonl. '
    'shared=false = internal (stays in the box); shared=true = publishes + client-eligible.';
comment on column public.channels.shared is
    'OPT-IN visibility (fail-closed): a channel is INTERNAL unless explicitly shared=true. '
    'Per-client scoping on top: a shared channel must also be listed in the client''s row '
    '(clients.channels) to be visible to that client. Two levels = registry-is-truth.';

create table if not exists public.channel_posts (
    id            uuid primary key default gen_random_uuid(),
    channel_id    text not null references public.channels(id) on delete cascade,
    from_session  text not null,                -- the actor id: a company session id, or 'claude-design'
    sender_kind   text not null default 'session',  -- session | client  (tags the origin so the
                                                   --   injector + company sessions know it's the design peer)
    to_session    text,                          -- addressed recipient (nullable = broadcast to the channel)
    thread        text not null default '',     -- the conversation thread id
    kind          text not null default 'message',  -- message | reply | system | decision-card | …
    text          text not null,
    created_at    timestamptz not null default now()
);
create index if not exists channel_posts_channel_idx on public.channel_posts (channel_id, created_at);
create index if not exists channel_posts_thread_idx on public.channel_posts (thread, created_at);
create index if not exists channel_posts_sender_idx on public.channel_posts (sender_kind, from_session);
comment on table public.channel_posts is
    'The shared channel exchange — a post by either side (company session or Claude Design). '
    'Realtime delivers each insert to the other side. Mirrors the mail-leaf post shape. '
    'sender_kind tags the origin so the company injector skips self-origin + tags CD posts.';

-- keep channels.posts + last_activity in sync on insert
create or replace function public._bump_channel_on_post() returns trigger as $$
begin
    update public.channels
       set posts = (select count(*) from public.channel_posts where channel_id = new.channel_id),
           last_activity = new.created_at
     where id = new.channel_id;
    return new;
end; $$ language plpgsql;
drop trigger if exists channel_posts_bump on public.channel_posts;
create trigger channel_posts_bump after insert on public.channel_posts
    for each row execute function public._bump_channel_on_post();

-- ── Realtime: publish both tables so either side sees changes live ──────────────
-- Supabase Realtime: add tables to the realtime publication (supabase_realtime).
do $$ begin
  alter publication supabase_realtime add table public.channels, public.channel_posts;
exception when duplicate_table then null;
end; $$;

-- ── RLS + grants ────────────────────────────────────────────────────────────────
-- service_role bypasses RLS (the Edge Function uses it for audited writes; the company
-- fabric's outbound sync uses it too). authenticated gets SELECT (the scoped 0005/0006
-- boundary/design_client policies gate WHICH rows); writes go through the Edge Function
-- (service_role) or the boundary principal. NO anon SELECT — the public anon key must not
-- read the shared slice (C-1: a broad using(true) anon policy would OR-widen past scoped).
alter table public.channels enable row level security;
alter table public.channel_posts enable row level security;
grant all on public.channels, public.channel_posts to service_role, postgres;
grant select on public.channels, public.channel_posts to authenticated;
-- (no anon grant; no broad using(true) SELECT policy — the scoped 0005/0006 policies are
--  authoritative. Realtime delivery to the boundary principal works via the 0005 SELECT
--  policy; design_client reads via the 0006 granted-channel policy.)

-- gen_random_uuid() needs pgcrypto
create extension if not exists pgcrypto;