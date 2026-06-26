-- 0001_connector_audit.sql — the mandatory audit table for the remote MCP gateway.
-- Every remote tool call logs here (who / scope / tool / outcome). Audit-write failure
-- ⇒ the call fails loud (mandatory-audit guard, lead ruling). Local dev ground first;
-- the prod table lives in Tim's Supabase project behind the custom domain.
create table if not exists public.connector_audit (
    id          text primary key,           -- the call_id (uuid)
    ts          timestamptz not null default now(),
    subject     text not null,              -- the authed principal (sub claim)
    scope       text not null,              -- company:design:read | :write
    tool        text not null,              -- the tool name
    args_preview text,                       -- truncated args
    outcome     text not null,              -- OK | DENY | TEACHING-ERROR | DISPATCH-ERROR
    detail      text
);
create index if not exists connector_audit_ts_idx on public.connector_audit (ts desc);
create index if not exists connector_audit_tool_idx on public.connector_audit (tool);
create index if not exists connector_audit_outcome_idx on public.connector_audit (outcome);
comment on table public.connector_audit is
    'Mandatory audit log for the remote MCP gateway (Claude Design connector).';

-- Grants: the gateway writes via the service_role key (bypasses RLS); the operator UI
-- reads via authenticated/anon. Grant ALL to service_role + SELECT to the read roles.
-- (RLS stays OFF for this table — it is an append-only system audit log, not user data;
--  access is gated by the role in the JWT, not row policies.)
grant all on public.connector_audit to service_role, postgres;
grant select on public.connector_audit to anon, authenticated;