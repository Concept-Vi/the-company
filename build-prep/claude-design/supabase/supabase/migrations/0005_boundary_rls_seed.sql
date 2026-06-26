-- 0005_boundary_rls_seed.sql — the boundary principal RLS + the seed shared channel.
-- Lead's resolution: the company-side boundary authenticates as a DEDICATED least-
-- privilege principal (NOT the service-role master key), scoped by RLS to INSERT + SELECT
-- on channel_posts + the collab tables. The policy keys off a STABLE custom claim on the
-- principal — app_metadata.role='company_boundary' — read via auth.jwt(), NOT a hardcoded
-- uid (the uid differs local vs prod; the claim doesn't, so this one migration is portable).

-- ── the boundary principal's RLS scoping ──────────────────────────────────────────
-- The principal is an authenticated Supabase user with app_metadata.role='company_boundary'.
-- These policies grant it INSERT + SELECT on the shared-slice tables. service_role still
-- bypasses RLS (the Edge Function's audited writes); anon stays read-only where 0001-0004
-- already set it. This NARROWS the boundary principal to exactly the shared slice.

-- helper: is the caller the boundary principal? (app_metadata.role == 'company_boundary')
create or replace function public.is_company_boundary() returns boolean as $$
  select coalesce((auth.jwt() -> 'app_metadata' ->> 'role'), '') = 'company_boundary'
$$ language sql stable;

-- channel_posts: the boundary principal may INSERT (publish outbound) + SELECT (read CD's posts back in)
drop policy if exists "channel_posts boundary insert" on public.channel_posts;
create policy "channel_posts boundary insert" on public.channel_posts
    for insert to authenticated with check (public.is_company_boundary());
drop policy if exists "channel_posts boundary select" on public.channel_posts;
create policy "channel_posts boundary select" on public.channel_posts
    for select to authenticated using (public.is_company_boundary());

-- collab-data: the boundary principal may INSERT (publish the shared-data slice) + SELECT
-- (read CD's submissions back in) on dna_tokens / design_seeds / design_submissions.
drop policy if exists "dna_tokens boundary write" on public.dna_tokens;
create policy "dna_tokens boundary write" on public.dna_tokens
    for insert to authenticated with check (public.is_company_boundary());
drop policy if exists "dna_tokens boundary select" on public.dna_tokens;
create policy "dna_tokens boundary select" on public.dna_tokens
    for select to authenticated using (public.is_company_boundary());

drop policy if exists "design_seeds boundary write" on public.design_seeds;
create policy "design_seeds boundary write" on public.design_seeds
    for insert to authenticated with check (public.is_company_boundary());
drop policy if exists "design_seeds boundary select" on public.design_seeds;
create policy "design_seeds boundary select" on public.design_seeds
    for select to authenticated using (public.is_company_boundary());

drop policy if exists "design_submissions boundary write" on public.design_submissions;
create policy "design_submissions boundary write" on public.design_submissions
    for insert to authenticated with check (public.is_company_boundary());
drop policy if exists "design_submissions boundary select" on public.design_submissions;
create policy "design_submissions boundary select" on public.design_submissions
    for select to authenticated using (public.is_company_boundary());

-- channels: the boundary principal may SELECT (read the shared-channel registry) + UPDATE
-- (bump posts/last_activity + status). It may NOT create channels (the company decides that).
drop policy if exists "channels boundary select" on public.channels;
create policy "channels boundary select" on public.channels
    for select to authenticated using (public.is_company_boundary());
drop policy if exists "channels boundary update" on public.channels;
create policy "channels boundary update" on public.channels
    for update to authenticated using (public.is_company_boundary());

-- ── SEED: the shared design channel (CD's home) + grant it to the claude-design client ──
insert into public.channels (id, kind, name, purpose, mode, status, members, shared)
values ('design', 'channel', 'design',
        'The shared home channel — Tim, the design-relevant sessions, and Claude Design meet here. Face Pipeline coordination + design submits.',
        'direct', 'active', '[]'::jsonb, true)
on conflict (id) do nothing;

-- add 'design' to the claude-design client row's channels (per-client scoping on top of shared)
update public.clients
   set channels = array(select distinct unnest(channels || array['design']))
 where id = 'claude-design';
-- ── privileges: grant INSERT/UPDATE to authenticated so the RLS boundary policies can ──
-- gate them (RLS filters; it does NOT confer privileges). Without these the boundary
-- principal (an authenticated user) has only SELECT and its INSERTs 403 despite the
-- policy. The policy restricts to is_company_boundary(); the grant lets it through.
grant insert, update, delete on public.channel_posts to authenticated;
grant insert, update on public.dna_tokens, public.design_seeds, public.design_submissions to authenticated;
grant update on public.channels to authenticated;
