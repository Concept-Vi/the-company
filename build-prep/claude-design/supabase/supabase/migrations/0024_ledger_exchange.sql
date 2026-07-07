-- 0024_ledger_exchange.sql — THE RECOLLECTION MOVE (ledger session; number per ④'s map: 0024+ mine).
-- Idempotent, additive-only. Plan-B DB1's design executed: transcript provenance becomes WORLD-FACT in
-- the one store — run-EXEMPT, append-only (the class of table the supersession disease can never touch).
--
-- WHAT MOVES (from .recollection/conversation-index/db.sqlite, which REMAINS the immutable source-of-record;
-- reads move here):
--   · exchanges (8,224) — WITH FULL user+assistant TEXT (69MB; pg TOASTs the big rows): a semantic hit on a
--     conversation can finally SHOW ITS WORDS from the one store, and generated-by edges get a real target.
--   · links (23,608) — the mechanical conversation graph (contains/precedes/produced_by/references) → the
--     durable edge layer (ledger.assertion, provenance='derived') under ④'s ONE edge grammar (kinds
--     registered in edge_kinds/ as exchange-*; absorb-never-reject).
--   · tool_calls (52,694) — every tool invocation with input/result; file_path surfaced as a stored
--     generated column (the write-tool provenance backfill's substrate).

create table if not exists ledger.exchange (
    address        text primary key,            -- exchange://<session_id>/<line_start>
    sqlite_id      text,                        -- the recollection md5 key (reconciliation join)
    session_id     text,
    project        text,
    ts             timestamptz,
    line_start     integer,
    line_end       integer,
    archive_path   text,                        -- the jsonl the text came from (re-derivation pointer)
    parent_uuid    text,
    is_sidechain   boolean default false,
    harness        text,
    model          text,
    cwd            text,
    git_branch     text,
    user_text      text,
    assistant_text text,
    fts            tsvector generated always as (to_tsvector('english',
                       left(coalesce(user_text,''), 200000) || ' ' ||
                       left(coalesce(assistant_text,''), 200000))) stored
);
create index if not exists exchange_session_idx on ledger.exchange (session_id, line_start);
create index if not exists exchange_ts_idx      on ledger.exchange (ts);
create index if not exists exchange_fts_idx     on ledger.exchange using gin (fts);
create index if not exists exchange_sqlite_idx  on ledger.exchange (sqlite_id);

create table if not exists ledger.tool_call (
    call_id          text primary key,          -- the recollection id
    exchange_address text,                      -- exchange://<sid>/<line>
    tool_name        text,
    tool_input       jsonb,
    tool_result      text,
    is_error         boolean default false,
    ts               timestamptz,
    file_path        text generated always as (tool_input->>'file_path') stored
);
create index if not exists tool_call_exchange_idx on ledger.tool_call (exchange_address);
create index if not exists tool_call_file_idx     on ledger.tool_call (file_path) where file_path is not null;
create index if not exists tool_call_name_idx     on ledger.tool_call (tool_name);

comment on table ledger.exchange is
'The transcript root, in the one store: every indexed conversation exchange WITH ITS TEXT (run-exempt
world-fact; sqlite stays the immutable source-of-record). generated-by edges resolve here; semantic hits on
exchange:// show their words; FTS joins the lexical axis.';
comment on table ledger.tool_call is
'Every tool invocation of the indexed sessions (input/result/error), keyed to its exchange. file_path is a
stored generated column — the substrate for the full write-tool provenance backfill.';
