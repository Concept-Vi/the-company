-- 0021_circuit_marks.sql — L5 CIRCUIT stage 1: the MARK BACKING's DB home (ledger session; number per ④'s
-- handoff). Idempotent, additive-only.
--
-- ④'s cross-study integration decision (THE-CONTAINER v3): "marks get one home — the ONE mark API
-- (store.append_mark/marks_for) is the seam; its backing store moves to the DB beside the rows whose state
-- it composes (shadow-then-flip)". Circuit state (intent claims/leases/terminals), keeper decisions, and
-- container records ALL compose from marks and must be queryable beside them.
--
-- Shape mirrors the FsStore API exactly (open-record preserved): target + mark_type are the two indexed
-- retrieval keys (the API's own docstrings: "a clean SQL WHERE target=X / mark_type=X"); everything else
-- of the record rides in body jsonb (a mark-pass may carry any extra fields without a schema edit).
-- The mark VOCABULARY stays in mark_types/ files (vocabulary=files, data=DB — law 3).

create schema if not exists container;

create table if not exists container.mark (
    mark_id   bigint generated always as identity primary key,
    ts        timestamptz not null default now(),
    target    text not null,           -- the address the mark is ON (intent://…, proposal://…, code://…)
    mark_type text not null,           -- opaque id from the mark_types/ file registry (validated in the Suite lane)
    body      jsonb not null default '{}'::jsonb   -- the WHOLE record minus ts/target/mark_type (open-record)
);
create index if not exists mark_target_idx      on container.mark (target, ts);
create index if not exists mark_type_idx        on container.mark (mark_type, ts);
create index if not exists mark_target_type_idx on container.mark (target, mark_type);

comment on table container.mark is
'L5: the ONE mark store''s DB home (shadow-then-flip from .data/store/marks.jsonl). Append-only; state is a
FOLD over marks including the clock (compose_state) — never a mutated status column. target+mark_type are
the retrieval keys; body preserves the open record.';

-- per-root isolation (same law as ledger.embedding's __root_* namespaces): the canonical .data/store
-- root writes ns='' ; any other root (test/tmp stores) gets an automatic __root_<hash> namespace, so a
-- temp store's marks never leak into (or read) the production thread.
alter table container.mark add column if not exists ns text not null default '';
create index if not exists mark_ns_idx on container.mark (ns);
