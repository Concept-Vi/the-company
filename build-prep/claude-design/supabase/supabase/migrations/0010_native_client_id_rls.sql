-- 0010_native_client_id_rls.sql — GO NATIVE (shared-project safety: zero blast radius on
-- the 16 live OAuth connectors). The Custom Access Token Hook is DROPPED from the claims path
-- (left inert / staged for item-B aud-binding only). is_design_client()/client_id() read the
-- OAuth token's NATIVE server-set top-level `client_id` (claims.client_id — server-set by the
-- OAuth 2.1 server from the VERIFIED client, not user-forgeable, NOT a hook stamp) and match it
-- to clients.oauth_client_id for the claude-design row.
--
-- KEY MAPPING: the native client_id is the Vi OAuth CLIENT id (e.g. "vi-…"). The RLS uses the
-- client ROW id ('claude-design') for from_session/submitted_by scoping. So client_id() returns
-- the ROW id of the client whose oauth_client_id = the native client_id (→ 'claude-design'),
-- NOT the native client id itself. The EF mirrors this: it looks the row up by oauth_client_id
-- and writes from_session/submitted_by = the row id.
--
-- UNCHANGED: the boundary principal (0005) is_company_boundary() reads app_metadata.role
-- 'company_boundary' set AT USER CREATION (a password-login service principal — no OAuth, no
-- native client_id). Clean split: CD = native client_id; boundary = app_metadata-at-creation.

-- client_id(): the client ROW id whose oauth_client_id matches the token's native client_id.
-- SECURITY DEFINER so the clients lookup bypasses RLS (clients has no RLS, but be explicit +
-- stable under any future clients RLS). Returns '' if no active client matches.
create or replace function public.client_id() returns text
language sql stable
security definer
set search_path = public
as $$
  select c.id
    from public.clients c
   where c.oauth_client_id = coalesce(auth.jwt() ->> 'client_id', '')
     and c.status = 'active'
   limit 1
$$;
alter function public.client_id() security definer;
alter function public.client_id() set search_path = public;
comment on function public.client_id() is
    'The client ROW id (e.g. claude-design) whose oauth_client_id matches the OAuth token''s '
    'NATIVE server-set client_id (claims.client_id). Empty if no active client matches.';

-- is_design_client(): the caller is an active client (its native client_id matches a row).
-- Replaces the 0006 app_metadata.role check (no hook stamps role now).
create or replace function public.is_design_client() returns boolean
language sql stable
security definer
set search_path = public
as $$
  select exists (
    select 1 from public.clients c
     where c.oauth_client_id = coalesce(auth.jwt() ->> 'client_id', '')
       and c.status = 'active'
  )
$$;
alter function public.is_design_client() security definer;
alter function public.is_design_client() set search_path = public;
comment on function public.is_design_client() is
    'True if the token''s NATIVE client_id matches an active client row (no hook — the OAuth '
    'server sets client_id from the verified client). Replaces the 0006 app_metadata.role check.';

-- channel_granted() (0009 made it SECURITY DEFINER) uses client_id() — it now resolves via the
-- native client_id. No change to channel_granted itself; it picks up the new client_id().
-- The 0006 design_client policies (channel_posts insert from_session=client_id(), design_submissions
-- submitted_by=client_id(), channel_granted) all reference these functions → they now gate on the
-- native client_id, no hook.