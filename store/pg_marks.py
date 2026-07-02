"""store/pg_marks.py — the mark backing on SUPABASE (L5 CIRCUIT stage 1; migration 0021).

The ONE mark API's DB home: FsStore.append_mark/marks_for/marks_by_type/all_marks delegate here
(shadow-then-flip complete 2026-07-02; 114 historical marks backfilled + read-equal verified; the
marks.jsonl write/read paths commented out at their call sites per the no-fallback rule).

Shape: target + mark_type + ts as columns (the two retrieval keys + order); the REST of the open record
in body jsonb — a mark-pass may carry any extra fields with no schema edit, exactly as the jsonl did.
Reads reconstruct the original record: {ts, target, mark_type, **body} — byte-compatible with the old
file rows (verified over all 114). Fail-loud: an unreachable DB RAISES with the breadcrumb — a mark that
lands nowhere (or a silently-empty fold) is the black-hole class the store forbids.
"""
from __future__ import annotations
import json
import os
import subprocess

PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
      "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
      "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
      "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
      "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
BREADCRUMB = ("mark store = container.mark (Supabase {h}:{p}, migration 0021_circuit_marks.sql; was "
              ".data/store/marks.jsonl pre-2026-07-02). If the table is missing, re-apply the migration."
              ).format(h=PG["host"], p=PG["port"])


def _dq(s: str) -> str:
    i = 0
    while True:
        t = f"$mk{i}$"
        if t not in s:
            return f"{t}{s}{t}"
        i += 1


def _psql(sql: str) -> str:
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-tA"], input=sql, capture_output=True, text=True,
                       timeout=60, env={**os.environ, "PGPASSWORD": PG["pw"]})
    if r.returncode != 0:
        raise RuntimeError(f"mark store failed: {(r.stderr or '').strip()[:250]} — {BREADCRUMB}")
    return r.stdout


def append_mark_db(rec: dict, *, ns: str = "") -> None:
    """Land one mark (the FULL open record incl. ts/target/mark_type) in container.mark. RAISES on failure.
    `ns` = the store root's namespace ('' = the canonical root; __root_<hash> = a test/tmp root)."""
    body = {k: v for k, v in rec.items() if k not in ("ts", "target", "mark_type")}
    _psql(f"insert into container.mark (ts, target, mark_type, body, ns) values "
          f"({_dq(rec['ts'])}::timestamptz, {_dq(rec['target'])}, {_dq(rec['mark_type'])}, "
          f"{_dq(json.dumps(body))}::jsonb, {_dq(ns)})")


def marks_where(*, target: str | None = None, mark_type: str | None = None, ns: str = "") -> list[dict]:
    """Marks filtered by target and/or mark_type (or ALL when neither), oldest-first, reconstructed to the
    original open-record shape {ts, target, mark_type, **body}. Empty → [] (additive default). Scoped to
    the store root's `ns` (per-root isolation on the one global table)."""
    conds = [f"ns = {_dq(ns)}"]
    if target is not None:
        conds.append(f"target = {_dq(target)}")
    if mark_type is not None:
        conds.append(f"mark_type = {_dq(mark_type)}")
    where = ("where " + " and ".join(conds)) if conds else ""
    out = _psql("select json_build_object('ts', to_char(ts at time zone 'utc', 'YYYY-MM-DD\"T\"HH24:MI:SS.US+00:00'),"
                "'target', target, 'mark_type', mark_type)::text || '|' || body::text "
                f"from container.mark {where} order by ts, mark_id")
    rows = []
    for l in out.splitlines():
        if "|" not in l:
            continue
        head, _, body = l.partition("|")
        h = json.loads(head)
        b = json.loads(body)
        rows.append({"ts": h["ts"], "target": h["target"], "mark_type": h["mark_type"], **b})
    return rows
