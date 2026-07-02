-- 0020_board_projection.sql — ④ THE CONTAINER · L6 BOARD (organ-studies/BOARD.md §3)
--
-- The DERIVED Postgres projection of the board. The file-per-item store
-- (channel-memory/noticeboard/<id>.md, resolved by the ONE resolver) is the SYSTEM OF RECORD; THIS table
-- is a one-way DERIVED read side for dashboards/counts/RLS (A2's real strength) — regenerated from the
-- files, never a second primary. This polarity is the family's own failure dictating it: A1's board
-- projected INTO the project row went stale (128 vs the live 279) exactly because the projection was
-- treated as a store. Here the derive is re-runnable (ops/migrate_board_from_cvi.py --slice project):
-- delete the rows + re-derive reproduces identical counts (C6.4). A row here with no source .md is a
-- ghost (the derive only ever writes rows it read from a file).
--
-- LAWS CARRIED:
--   · files author, the DB is a derived projection (law 3): vocabulary=files (item_types/), data lands as
--     files first (the pour writes .md), THIS table is the derived read.
--   · text address = identity (law 1): board_items.address (board://<id>) is the identity, NOT NULL UNIQUE.
--   · scope + author are ADDRESSES (law 6): both are text address columns; author_type dissolves.
--   · reverses composed/indexed, never stored (law 4): the authored_by reverse is the derived
--     _authored_by_index.json beside the files (the engine's O(1) reverse) + here an index on author.
--   · schema-additive (constitution rule 2): a NEW table in the existing `container` schema; nothing edited.
--
-- IDEMPOTENT: CREATE TABLE/INDEX IF NOT EXISTS — applies clean twice, and clean on a scratch DB carrying
--   0013_container.sql. TRANSACTION SAFETY: ONE transaction (BEGIN…COMMIT) with a fail-loud prerequisite
--   guard at the top — an unmet prerequisite rolls the whole thing back (no half-apply).
-- REVERSAL: DROP TABLE IF EXISTS container.board_items;

BEGIN;

-- ── PREREQUISITE GUARD (fail loud, no half-apply) — the projection lives in schema `container` (0013). ──
do $guard$
begin
  if not exists (select 1 from information_schema.schemata where schema_name = 'container') then
    raise exception 'expected schema container (0013_container.sql); previously n/a; fix: apply 0013_container.sql first';
  end if;
end
$guard$;

-- ── the DERIVED board projection (one row per file-per-item board record) ──────────────────────────────
create table if not exists container.board_items (
  id             text primary key,                        -- the flat item id (== the .md basename)
  address        text not null unique,                    -- board://<id> — text address = identity (law 1)
  type           text not null,                           -- a registry ref (item_types/<type>.py)
  source         text,                                    -- a registry ref (source_types/<source>.py)
  state          text not null,                           -- the item's current lifecycle state
  scope          text not null default 'global',          -- an ADDRESS: project://… | channel://… | global
  author         text,                                    -- an ADDRESS: operator://tim | session://… | agent://…
  title          text,
  channel        text,                                    -- legacy field (kept; scope derives from it)
  author_session text,                                    -- legacy field (kept; author derives from it)
  thread         text,
  links          jsonb  not null default '[]'::jsonb,     -- typed edges [{kind,target}] (pins live here too)
  history        jsonb  not null default '[]'::jsonb,     -- the append-only provenance ledger
  extra          jsonb  not null default '{}'::jsonb,     -- the open long-tail keys (root_cause, workaround…)
  body           text,
  created_at     timestamptz,
  updated_at     timestamptz,
  derived_at     timestamptz not null default now(),      -- when this row was last derived from its file
  source_meta    jsonb                                    -- pour provenance (cloud post_id, project_id, …)
);

-- dashboards/counts/reverse-lookup read paths (the projection's whole reason to exist)
create index if not exists board_items_scope_idx  on container.board_items (scope);
create index if not exists board_items_type_idx   on container.board_items (type);
create index if not exists board_items_state_idx  on container.board_items (state);
create index if not exists board_items_author_idx on container.board_items (author);   -- the reverse, DB-side
create index if not exists board_items_links_idx  on container.board_items using gin (links);

COMMIT;
