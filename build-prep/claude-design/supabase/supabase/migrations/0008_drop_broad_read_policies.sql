-- 0008_drop_broad_read_policies.sql — C-1 (adversarial review CRITICAL fix).
-- The broad placeholder `using(true)` SELECT policies shipped in 0003/0004 OR-widen PAST
-- the scoped 0005/0006 policies (Postgres ORs all matching permissive policies) — so a
-- design_client (AND anyone holding the public anon key via PostgREST) could READ every
-- channel/post/submission incl. internal/non-granted. This drops the broad policies so the
-- SCOPED 0005/0006 policies (boundary + design_client-granted) are authoritative, and
-- revokes anon SELECT on the shared tables (anon gets nothing; the public anon key can't
-- read the shared slice). Applied to prod by the lead; kept here as the canonical, idempotent
-- drop so any applier (incl. a fresh `supabase db reset` if 0003/0004 source weren't fixed)
-- lands scoped. 0003/0004 SOURCE are also fixed to not ship the broad policies in the first
-- place — this migration is the belt-and-suspenders for already-applied environments.

-- drop the broad 0003 read policies (channels + channel_posts)
drop policy if exists "channels read for authenticated" on public.channels;
drop policy if exists "channels read for anon" on public.channels;
drop policy if exists "channel_posts read for authenticated" on public.channel_posts;
drop policy if exists "channel_posts read for anon" on public.channel_posts;

-- drop the broad 0004 read policies (collab-data)
drop policy if exists "dna_tokens read for authenticated" on public.dna_tokens;
drop policy if exists "design_seeds read for authenticated" on public.design_seeds;
drop policy if exists "design_submissions read for authenticated" on public.design_submissions;

-- revoke anon SELECT on the shared tables (the public anon key must not read the slice;
-- authenticated SELECT survives via the scoped 0005/0006 boundary/design_client policies)
revoke select on public.channels, public.channel_posts from anon;
revoke select on public.dna_tokens, public.design_seeds, public.design_submissions from anon;

-- sanity: confirm no broad using(true) SELECT policy remains on the shared tables
do $$
declare
  bad text;
begin
  select string_agg(pol.tablename || ':' || pol.policyname, ', ')
    into bad
    from pg_policies pol
   where pol.schemaname = 'public'
     and pol.policyname in (
       'channels read for authenticated','channels read for anon',
       'channel_posts read for authenticated','channel_posts read for anon',
       'dna_tokens read for authenticated','design_seeds read for authenticated',
       'design_submissions read for authenticated')
     and pol.qual = 'true';
  if bad is not null then
    raise exception 'C-1: broad using(true) SELECT policy still present: %', bad;
  end if;
end $$;