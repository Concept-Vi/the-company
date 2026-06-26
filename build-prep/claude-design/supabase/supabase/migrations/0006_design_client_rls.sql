-- 0006_design_client_rls.sql — the CD-client RLS layer (gate 2 of the two-gates model).
-- Lead's model: CD writes via the Edge Function using the CD USER's own JWT (forwarded),
-- so Supabase RLS is the second gate (gate 1 = the client-registry posture the Edge Function
-- checks before writing). service_role is reserved for audit + client-registry lookup only.
--
-- The CD user carries app_metadata.client_id = 'claude-design' (its registry row id). RLS
-- ties every write to THAT client_id: a design_client can only INSERT a channel_post whose
-- from_session = its client_id (can't forge another client's posts), only into a channel
-- that is shared AND listed in its clients.channels row; can only INSERT a design_submission
-- whose submitted_by = its client_id. Reads: shared channels listed in its row + their posts
-- + the collab context (dna_tokens/design_seeds read-mostly). This is the per-client scoping
-- the Edge Function can't enforce alone — RLS holds it at the row.

-- helper: the caller's client_id (from app_metadata.client_id)
create or replace function public.client_id() returns text as $$
  select coalesce((auth.jwt() -> 'app_metadata' ->> 'client_id'), '')
$$ language sql stable;

-- helper: is the caller a design_client (app_metadata.role = 'design_client')?
create or replace function public.is_design_client() returns boolean as $$
  select coalesce((auth.jwt() -> 'app_metadata' ->> 'role'), '') = 'design_client'
$$ language sql stable;

-- helper: is `chan` a shared channel granted to the caller's client row?
-- SECURITY DEFINER + a fixed search_path: this reads public.clients + public.channels as a
-- SYSTEM fact (is the channel shared + granted?), NOT under the caller's RLS — querying
-- channels inside a channels policy would recurse infinitely. SECURITY DEFINER runs it as
-- the owner (bypassing RLS) so the internal lookups don't re-enter the policy.
create or replace function public.channel_granted(chan text) returns boolean
language sql stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.clients c
     where c.id = public.client_id()
       and c.status = 'active'
       and chan = any(c.channels)
       and exists (select 1 from public.channels where id = chan and shared = true)
  )
$$;
-- FORCE security definer (CREATE OR REPLACE does NOT change the security attribute of an
-- existing function; without this an upgraded env keeps INVOKER → RLS recursion on the
-- channels policy → stack-depth-exceeded. This ALTER guarantees definer on every apply.)
alter function public.channel_granted(text) security definer;
alter function public.channel_granted(text) set search_path = public;

-- ── channel_posts: a design_client may INSERT only its own posts into a granted shared channel ──
drop policy if exists "channel_posts client insert" on public.channel_posts;
create policy "channel_posts client insert" on public.channel_posts
    for insert to authenticated
    with check (public.is_design_client()
                and from_session = public.client_id()
                and public.channel_granted(channel_id));
-- a design_client may SELECT posts in its granted shared channels
drop policy if exists "channel_posts client select" on public.channel_posts;
create policy "channel_posts client select" on public.channel_posts
    for select to authenticated
    using (public.is_design_client() and public.channel_granted(channel_id));

-- ── channels: a design_client may SELECT only its granted shared channels ───────────
drop policy if exists "channels client select" on public.channels;
create policy "channels client select" on public.channels
    for select to authenticated
    using (public.is_design_client() and public.channel_granted(id));

-- ── design_submissions: a design_client may INSERT its own + SELECT its own ─────────
drop policy if exists "design_submissions client insert" on public.design_submissions;
create policy "design_submissions client insert" on public.design_submissions
    for insert to authenticated
    with check (public.is_design_client() and submitted_by = public.client_id());
drop policy if exists "design_submissions client select" on public.design_submissions;
create policy "design_submissions client select" on public.design_submissions
    for select to authenticated
    using (public.is_design_client() and submitted_by = public.client_id());

-- ── dna_tokens + design_seeds: read-mostly context — design_client may SELECT ───────
drop policy if exists "dna_tokens client select" on public.dna_tokens;
create policy "dna_tokens client select" on public.dna_tokens
    for select to authenticated using (public.is_design_client());
drop policy if exists "design_seeds client select" on public.design_seeds;
create policy "design_seeds client select" on public.design_seeds
    for select to authenticated using (public.is_design_client());

-- privileges: design_client (authenticated) already has SELECT (0001-0004) + INSERT/UPDATE
-- (0005 grants to authenticated). No new grants needed — RLS gates which rows.