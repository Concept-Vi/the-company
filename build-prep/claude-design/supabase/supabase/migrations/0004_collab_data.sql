-- 0004_collab_data.sql — the SHARED COLLAB-DATA tables (the Face Pipeline inlet + context).
-- Reusable + model-independent (lead's split: this stands regardless of the channel-sync
-- sequencing decision). Supabase-side only — NO company-side sync wired here.
--
-- Tim's goal: Claude Design PARTICIPATES, everyone on the SAME DATA. The collab data is
-- the Face Pipeline's inlet (board://item-c0a2d591): Claude Design reads context (the seed
-- + DNA tokens) and SUBMITS a design (the export bundle). Both sides read/write the SAME
-- rows. The Edge Function serves these authed + client-registry-scoped + RLS-gated.
--
-- Stage mapping (board://item-c0a2d591's 6-stage pipeline): ① INGEST lands the export bundle
-- HERE (design_submissions); ② TAG / ③ COMPOSE / ④ VALIDATE / ⑤ RECONCILE / ⑥ REGISTER
-- are company-side steps that READ from these tables and write their results back (into
-- shared tables or company registries). This migration owns the INLET + the context reads.

-- ── DNA tokens: the design-token library Claude Design snaps styles to ───────────────
create table if not exists public.dna_tokens (
    id          text primary key,            -- the token slot, e.g. '--acc' / '--sp-2'
    group_id    text not null,               -- group: surface|signal|ink|node-type|type|living|shape
    value       text not null,               -- the current value (hex/scale/etc.)
    note        text not null default '',     -- what it governs (legibility)
    updated_at  timestamptz not null default now(),
    updated_by  text not null default 'system'
);
comment on table public.dna_tokens is
    'The DNA design-token library — Claude Design snaps styles to these slots. The shared '
    'identity layer (token name owned by the system; value is the aesthetic).';

-- ── design_seeds: a partial description + DNA reference that seeds Claude Design ─────
create table if not exists public.design_seeds (
    id                   uuid primary key default gen_random_uuid(),
    label                text not null,
    partial_description  text not null,       -- the half-description Tim reacts to (seed-react loop)
    dna_ref              text,                -- a DNA variant/branch id (nullable)
    target_area          text,                -- which surface/area the seed is for
    created_by           text not null,       -- session id or 'claude-design'
    status               text not null default 'open',  -- open | designed | translated | registered
    created_at           timestamptz not null default now(),
    updated_at           timestamptz not null default now()
);
comment on table public.design_seeds is
    'A seed: the partial description + DNA that starts Claude Design halfway (the seed-react '
    'loop). The INLET input. Both sides read; the operator/lead creates; Claude Design reacts.';

-- ── design_submissions: the INLET — Claude Design''s export bundle (stage ① INGEST) ────
create table if not exists public.design_submissions (
    id              uuid primary key default gen_random_uuid(),
    seed_id         uuid references public.design_seeds(id) on delete set null,
    submitted_by    text not null,             -- 'claude-design' (the client_id) for design posts
    bundle          jsonb not null,            -- the framework-neutral HTML/CSS export tree
    readme          text not null default '',   -- the export's README/notes
    status          text not null default 'ingested',  -- ingested | tagged | composed | validated | reconciled | registered
    ingest_notes    text not null default '',   -- stage-① parse notes (company-side writes)
    created_at      timestamptz not null default now()
);
create index if not exists design_submissions_seed_idx on public.design_submissions (seed_id);
create index if not exists design_submissions_status_idx on public.design_submissions (status);
comment on table public.design_submissions is
    'The Face Pipeline INLET — Claude Design''s export bundle lands here (stage ① INGEST). '
    'The company translate pipeline reads from here; status tracks ①→⑥.';

-- ── Realtime: publish all three so either side sees changes live ─────────────────────
do $$ begin
  alter publication supabase_realtime add table public.dna_tokens, public.design_seeds, public.design_submissions;
exception when duplicate_table then null;
end; $$;

-- ── RLS + grants ─────────────────────────────────────────────────────────────────────
-- service_role bypasses RLS (the Edge Function's audited writes; company-side writes too).
-- authenticated get SELECT (the scoped 0005/0006 boundary/design_client policies gate WHICH
-- rows); anon gets NOTHING on collab-data (C-1: a broad using(true) policy would OR-widen
-- past the scoped design_client policy). Claude Design's writes go through the Edge Function
-- (service_role), scoped by the client-registry posture, NOT direct client writes.
alter table public.dna_tokens enable row level security;
alter table public.design_seeds enable row level security;
alter table public.design_submissions enable row level security;
grant all on public.dna_tokens, public.design_seeds, public.design_submissions to service_role, postgres;
grant select on public.dna_tokens, public.design_seeds, public.design_submissions to authenticated;
-- (no anon grant; no broad using(true) SELECT policy — the scoped 0006 design_client policy
--  is authoritative: design_client reads dna_tokens/design_seeds via is_design_client(), its
--  own submissions via submitted_by=client_id.)

create extension if not exists pgcrypto;