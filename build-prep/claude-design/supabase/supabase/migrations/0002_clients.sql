-- 0002_clients.sql — the CLIENT REGISTRY (Tim's naming call). ONE place a client's
-- remote-MCP policy lives: allowed_tools (posture + per-tool op-allow-list + scope),
-- approval_mode, channels. The Edge Function gate + the Python gateway BOTH resolve a
-- client's policy from here at call time (registry-is-truth; the gateway owns no private
-- allow-list). Claude Design is the first row; any future client is another row.
--
-- This is the Supabase home of the data that was remote_exposure.json — the config-into-
-- company fold. remote_exposure.json's posture/tool data becomes a client row's
-- allowed_tools jsonb (or a shared posture registry the rows reference, later).
create table if not exists public.clients (
    id            text primary key,            -- the client id, e.g. 'claude-design'
    label         text not null,
    allowed_tools jsonb not null default '{}'::jsonb,  -- {tool: {remote_posture, allowed, scope}}
    scopes        text[] not null default '{}',        -- scopes this client may be issued
    approval_mode text not null default 'operator-gate',  -- how its scope is approved
    channels      text[] not null default '{}',        -- channels it may join
    posture       text not null default 'safe',        -- default posture if a tool omits one
    status        text not null default 'active',      -- active | disabled
    created_at   timestamptz not null default now(),
    updated_at   timestamptz not null default now()
);
comment on table public.clients is
    'The client registry — each remote-MCP client''s policy (allowed_tools/scopes/approval/channels). '
    'Resolved by the Edge Function gate + the Python gateway at call time (registry-is-truth).';
comment on column public.clients.allowed_tools is
    '{tool_name: {remote_posture: safe|design|consent|hazard|locked, allowed: [ops]|null, scope: read|write}}. '
    'A tool NOT present, or with posture not in {safe,design}, is NOT exposed (fail-closed).';
grant all on public.clients to service_role, postgres;
grant select on public.clients to anon, authenticated;

-- Seed Claude Design as the first client (its policy = the current remote_exposure.json
-- allow-list, folded in). Fail-closed: only safe + design tools, tight per-tool op-lists.
insert into public.clients (id, label, allowed_tools, scopes, approval_mode, channels, posture, status)
values (
  'claude-design',
  'Claude Design (Anthropic) — the Face Pipeline inlet',
  '{
    "object_info":        {"remote_posture": "safe",   "allowed": null,           "scope": "read"},
    "list_by_type":       {"remote_posture": "safe",   "allowed": null,           "scope": "read"},
    "list_graphs":        {"remote_posture": "safe",   "allowed": null,           "scope": "read"},
    "cognition_info":     {"remote_posture": "safe",   "allowed": null,           "scope": "read"},
    "capabilities":       {"remote_posture": "safe",   "allowed": null,           "scope": "read"},
    "corpus":             {"remote_posture": "safe",   "allowed": ["list","find","read","query"], "scope": "read"},
    "instrument":         {"remote_posture": "safe",   "allowed": null,           "scope": "read"},
    "chat":               {"remote_posture": "safe",   "allowed": null,           "scope": "read"},
    "operator":           {"remote_posture": "safe",   "allowed": ["rules"],      "scope": "read"},
    "sessions":           {"remote_posture": "safe",   "allowed": ["list","inbox","watch","describe","search","timeline"], "scope": "read"},
    "channels":           {"remote_posture": "safe",   "allowed": ["list","describe","history","edges"], "scope": "read"},
    "cc_board":           {"remote_posture": "safe",   "allowed": null,           "scope": "read"},
    "marks":              {"remote_posture": "safe",   "allowed": ["target","type","findings"], "scope": "read"},
    "cc_channel":         {"remote_posture": "design", "allowed": ["send"],       "scope": "write"},
    "claude_design":      {"remote_posture": "design", "allowed": ["ingest_bundle","submit_seed","walk_decision"], "scope": "write"}
  }'::jsonb,
  array['company:design:read', 'company:design:write'],
  'operator-gate',
  array['design-pipeline'],
  'safe',
  'active'
)
on conflict (id) do nothing;