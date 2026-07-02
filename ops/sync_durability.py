#!/usr/bin/env python3
"""ops/sync_durability.py — L9 SUPERSESSION: keep the durable side-tables fresh (the-one-system substrate).

The cure (migration 0014) put enrichment in run-INDEPENDENT tables keyed by content/provenance so a rebuild
can't strand it. This is the SYNC that keeps them current: it upserts ledger.interpretation from the newest
enrichment on ledger.entry (per canonical address+source_hash) and ledger.assertion from the authored-
provenance edges — idempotent, freshness-guarded (newer interp overwrites; older never clobbers).

WHY a sync, not a producer-edit: interpretation is written by the model interpret pass, assertion edges by
the recollection/provenance producer — separate producers. One idempotent sync run after any of them (and by
the heartbeat job on change — L10 binds this to ④'s CIRCUIT/tick) keeps the durable read (unit_latest /
edge_unified) true, without threading the write through every producer. Self-healing: a missed sync is
caught by the next (watermark-free — it always recomputes the latest, cheap via the indexes).

Run:  .venv/bin/python ops/sync_durability.py            # sync both
      .venv/bin/python ops/sync_durability.py --interpretation | --assertion
Import: sync_durability() — called at the tail of ledger_build.load_run + by the durability heartbeat job.
"""
from __future__ import annotations
import argparse
import os
import subprocess

PG = {
    "host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
    "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
    "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
    "db":   os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
    "pw":   os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres"),
}
# the authored-provenance edge kinds (run-independent) that live durably in ledger.assertion — NOT scanned
# facts. Additive: a new authored kind is added here + handed to ④'s L4 edge_kinds registry (it absorbs).
AUTHORED_KINDS = ("generated-by", "authored_by")


def _psql(sql: str, *, want_rows: bool = False, timeout: int = 120) -> str:
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-tAc", sql], capture_output=True, text=True,
                       timeout=timeout, env={**os.environ, "PGPASSWORD": PG["pw"]})
    if r.returncode != 0:
        raise RuntimeError(f"sync_durability psql failed: {(r.stderr or '').strip()[:300]}")
    return r.stdout.strip()


# The interp columns carried to the durable table (all of them; the ones absent from the stale entry_latest
# view still exist on the base entry table, which this reads directly).
_INTERP_COLS = ("kind", "purpose_doc", "what_it_does", "purpose_vs_actual", "novelty", "intention_signals",
                "contribution", "summary_for_embedding", "intention_for_embedding", "inputs", "outputs",
                "observations", "standouts", "conventions", "concerns", "questions", "apparent_themes",
                "interp_model", "interp_prompt_version", "produced_by_session", "interp_at")


def sync_interpretation() -> int:
    """Upsert the newest enrichment per (address, source_hash) from ledger.entry into ledger.interpretation.
    FRESHNESS-GUARDED: on conflict, overwrite ONLY when the incoming interp_at is newer (a rebuild with an
    older/blank interp can never clobber a good description — the exact stranding this cures)."""
    src_cols = ["prompt_version" if c == "interp_prompt_version" else c for c in _INTERP_COLS]
    ins_cols = ", ".join(("address", "source_hash", *_INTERP_COLS))
    sel_cols = ", ".join(("address", "coalesce(source_hash,'')", *src_cols))
    updates = ", ".join(f"{c}=excluded.{c}" for c in _INTERP_COLS)
    before = _psql("select count(*) from ledger.interpretation")
    _psql(f"""
        insert into ledger.interpretation ({ins_cols})
        select distinct on (address, coalesce(source_hash,'')) {sel_cols}
          from ledger.entry
          where address is not null and coalesce(what_it_does,'') <> ''
          order by address, coalesce(source_hash,''), interp_at desc nulls last, extracted_at desc nulls last
        on conflict (address, source_hash) do update set {updates}
          where excluded.interp_at is not null
            and (ledger.interpretation.interp_at is null or excluded.interp_at >= ledger.interpretation.interp_at)
    """)
    after = _psql("select count(*) from ledger.interpretation")
    return int(after) - int(before)


def sync_assertion() -> int:
    """Upsert authored-provenance edges (run-independent) from ledger.edge into ledger.assertion. Single-
    direction (reverses are composed at read from the kind's declared inverse — ④'s shared law, never stored).
    ONE GRAMMAR both sides: every kind is validated against ④'s L4 registry (ledger.validate_edge_kind —
    RAISES with the authoring breadcrumb on an unregistered kind; absorb-never-reject means the fix is to
    author the edge_kinds/<id>.py row, never to drop the edge)."""
    for k in AUTHORED_KINDS:
        _psql(f"select ledger.validate_edge_kind('{k}')")      # fail-loud BEFORE writing any row
    kinds = ", ".join(f"'{k}'" for k in AUTHORED_KINDS)
    before = _psql("select count(*) from ledger.assertion")
    _psql(f"""
        insert into ledger.assertion (from_ref, kind, to_ref, to_resolved, provenance, produced_by_session, ts)
        select distinct on (from_ref, kind, to_raw)
               from_ref, kind, to_raw, to_resolved, 'authored', produced_by_session, extracted_at
          from ledger.edge
          where kind in ({kinds})
          order by from_ref, kind, to_raw, extracted_at desc nulls last
        on conflict (from_ref, kind, to_ref) do update
          set to_resolved = coalesce(excluded.to_resolved, ledger.assertion.to_resolved),
              ts = greatest(ledger.assertion.ts, excluded.ts)
    """)
    after = _psql("select count(*) from ledger.assertion")
    return int(after) - int(before)


def sync_durability(*, interpretation: bool = True, assertion: bool = True) -> dict:
    """Keep both durable tables fresh. Best-effort per table (a failure is raised loud, never silent)."""
    out = {}
    if interpretation:
        out["interpretation_added"] = sync_interpretation()
    if assertion:
        out["assertion_added"] = sync_assertion()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interpretation", action="store_true")
    ap.add_argument("--assertion", action="store_true")
    a = ap.parse_args()
    both = not (a.interpretation or a.assertion)
    res = sync_durability(interpretation=both or a.interpretation, assertion=both or a.assertion)
    print(f"durability sync: {res}"
          f"  (interpretation rows: {_psql('select count(*) from ledger.interpretation')}, "
          f"assertion rows: {_psql('select count(*) from ledger.assertion')})")


if __name__ == "__main__":
    raise SystemExit(main())
