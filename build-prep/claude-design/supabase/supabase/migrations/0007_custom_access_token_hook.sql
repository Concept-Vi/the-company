-- 0007_custom_access_token_hook.sql — STAGED (no prod action; part of the flip runbook).
-- How the real Claude Design OAuth-flow JWT gets the design_client claims so 0006 RLS
-- gates it like local. The Custom Access Token Hook (Supabase Auth) runs before a token is
-- issued and can add/modify claims keyed on the authentication method + the OAuth client_id.
-- This is the ONE place that stamps ALL the connector claims — role, client_id, scope —
-- AND the resource-bound `aud` (item B: cross-resource replay defense), so the EF's AUDIENCE
-- can be set to the MCP resource and a token minted for the "Vi" client can't be replayed
-- against another resource.
--
-- MECHANISM:
--   • the "Vi" OAuth client (Tim's dashboard step 4) issues a client_id; store it on the
--     claude-design client row (clients.oauth_client_id) — registry-is-truth (the hook reads
--     it, never hardcoded).
--   • the hook: when event.authentication_method like 'oauth%' AND event.claims.client_id
--     matches the claude-design client's oauth_client_id → stamp:
--       claims.role := 'design_client'                       (is_design_client() RLS)
--       claims.app_metadata.role := 'design_client'
--       claims.app_metadata.client_id := 'claude-design'     (client_id() + EF clientId)
--       claims.app_metadata.scope := 'company:design:write'  (scopeFromClaims)
--       claims.aud := clients.mcp_url (the MCP resource)     (item B: resource-bound aud)
--   • tokens NOT from the Vi client (password login, other OAuth, anon) are returned
--     UNTOUCHED (aud stays 'authenticated', no design_client claims) — so the hook is
--     strictly additive for the connector, no blast radius on other auth.
--
-- WIRING (dashboard step, Tim/lead): Authentication > Hooks > Custom Access Token Hook →
-- select public.custom_access_token_hook. The function existing is not enough; it must be
-- selected as the active hook.
--
-- ORDER vs the flip: step 4 (create the Vi OAuth client → client_id) must land BEFORE the
-- hook is useful — then UPDATE clients SET oauth_client_id=<Vi client_id> WHERE id=
-- 'claude-design'. Until then the hook matches nothing (safe no-op).

alter table public.clients
    add column if not exists oauth_client_id text,
    add column if not exists mcp_url        text,
    add column if not exists bind_aud       boolean not null default false;

comment on column public.clients.oauth_client_id is
    'The OAuth 2.1 client_id Tim creates in the dashboard (the "Vi" client). The custom '
    'access-token hook matches on this to stamp design_client claims.';
comment on column public.clients.mcp_url is
    'The MCP resource URL (the resource-bound `aud`). The hook stamps claims.aud = mcp_url '
    'ONLY when bind_aud=true (the item-B fast-follow, coordinated with the EF AUDIENCE env).';
comment on column public.clients.bind_aud is
    'Off for v1: the hook leaves aud="authenticated" so the EF (AUDIENCE default '
    '"authenticated") validates. The item-B fast-follow sets bind_aud=true AND the EF '
    'AUDIENCE env = mcp_url TOGETHER (a resource-bound audience blocks cross-resource '
    'token replay). Never set one without the other.';

-- the connector claims, stamped only for the Vi OAuth client's tokens
create or replace function public.custom_access_token_hook(event jsonb)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  auth_method text := coalesce(event ->> 'authentication_method', '');
  claims      jsonb := coalesce(event -> 'claims', '{}'::jsonb);
  tok_client  text := coalesce(claims ->> 'client_id', '');
  vi_client   text;
  mcp_url     text;
  bind_aud    boolean;
begin
  -- only OAuth-flow tokens are candidates; everything else returns untouched
  if auth_method not ilike 'oauth%' then
    return jsonb_build_object('claims', claims);
  end if;

  -- registry-is-truth: the Vi client_id + the MCP resource URL + the bind_aud flag live on the row
  select c.oauth_client_id, c.mcp_url, coalesce(c.bind_aud, false)
    into vi_client, mcp_url, bind_aud
    from public.clients c
   where c.id = 'claude-design' and c.status = 'active';

  -- no Vi client registered yet, or this token isn't from it → untouched (safe no-op)
  if vi_client is null or vi_client = '' or tok_client is null or tok_client <> vi_client then
    return jsonb_build_object('claims', claims);
  end if;

  -- stamp the design_client claims (0006 RLS reads app_metadata.role + app_metadata.client_id).
  -- NOTE: nested jsonb_set('{app_metadata,role}') does not create the parent on this PG; use a
  -- single-level app_metadata MERGE (preserves any existing app_metadata the user carries).
  claims := jsonb_set(claims, '{role}', to_jsonb('design_client'::text), true);
  claims := jsonb_set(claims, '{app_metadata}',
    coalesce(claims -> 'app_metadata', '{}'::jsonb)
      || jsonb_build_object('role', 'design_client',
                            'client_id', 'claude-design',
                            'scope', 'company:design:write'),
    true);
  -- item B (FAST-FOLLOW, gated): stamp the resource-bound aud ONLY when bind_aud=true.
  -- v1 leaves bind_aud=false so aud stays "authenticated" and the EF (AUDIENCE default
  -- "authenticated") validates. The fast-follow flips bind_aud=true AND sets the EF AUDIENCE
  -- env = mcp_url TOGETHER (never one without the other, or auth breaks).
  if bind_aud and mcp_url is not null and mcp_url <> '' then
    claims := jsonb_set(claims, '{aud}', to_jsonb(mcp_url), true);
  end if;

  return jsonb_build_object('claims', claims);
end;
$$;
comment on function public.custom_access_token_hook is
    'Stamps design_client claims + resource-bound aud on tokens minted via the Vi OAuth '
    'client (matched by claims.client_id == clients.oauth_client_id for claude-design). '
    'Strictly additive for the connector; all other tokens pass through untouched.';

-- the hook needs to read clients; it's SECURITY DEFINER (runs as owner) so it can. Grant
-- execute to the auth role (Supabase Auth invokes it as the authenticator role).
grant execute on function public.custom_access_token_hook(jsonb) to anon, authenticated, service_role, postgres;