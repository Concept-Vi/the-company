-- 0012_ledger_interpretive.sql — columns for the Opus interpretive layer (the model pass over the ledger).
-- Idempotent. The structural cols already exist (0011); these add the interpretive-TEXT fields produced by the
-- model: `contribution` (what this file UNIQUELY contributes to a fused system — NEUTRAL, no ranking) + the two
-- embedding-TEXT faces. Vectors themselves land in a later step when the embedder (:8001) is up.

alter table ledger.entry  add column if not exists contribution text;
alter table ledger.entry  add column if not exists summary_for_embedding text;
alter table ledger.entry  add column if not exists intention_for_embedding text;
alter table ledger.entry  add column if not exists interp_model text;          -- which model wrote the interp
alter table ledger.entry  add column if not exists interp_at timestamptz;

alter table ledger.symbol add column if not exists summary_for_embedding text;
alter table ledger.symbol add column if not exists interp_model text;
alter table ledger.symbol add column if not exists interp_at timestamptz;

-- the interpretive completeness gate reads this: a deterministic file with what_it_does IS NULL is unprocessed.
create index if not exists entry_interp_gate on ledger.entry (run_id, coverage_state) where what_it_does is null;
