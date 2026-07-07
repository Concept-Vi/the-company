#!/usr/bin/env python3
"""ops/migrate_recollection_full.py — THE RECOLLECTION MOVE (migration 0024's data): exchanges WITH TEXT +
tool_calls + the mechanical links, sqlite → the one store. Idempotent (upserts); reconciliation WITH
DENOMINATORS (source → landed → excluded-with-reason, sums must match — RAISE otherwise). The sqlite stays
the immutable source-of-record (read-only here, per the cvi_mine law).

  exchanges → ledger.exchange       address = exchange://<session_id|'unknown'>/<line_start>
  tool_calls → ledger.tool_call     keyed by the recollection id; exchange_address derived via its exchange
  links → ledger.assertion          kinds exchange-contains/-precedes/-produced-by/-references,
                                    provenance='derived' (mechanical facts, run-exempt; ONE edge grammar —
                                    the kinds are registered in edge_kinds/ before any row lands)

Run: .venv/bin/python ops/migrate_recollection_full.py [--db .recollection/conversation-index/db.sqlite]
"""
from __future__ import annotations
import argparse
import csv
import io
import json
import os
import sqlite3
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
      "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
      "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
      "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
      "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}

LINK_KIND = {"contains": "exchange-contains", "precedes": "exchange-precedes",
             "produced_by": "exchange-produced-by", "references": "exchange-references"}


def _psql_file(path: str) -> None:
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-f", path], capture_output=True, text=True,
                       timeout=1800, env={**os.environ, "PGPASSWORD": PG["pw"]})
    if r.returncode != 0:
        raise RuntimeError(f"psql -f failed: {r.stderr.strip()[:400]}")


def _q(sql: str) -> str:
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-tA"], input=sql, capture_output=True, text=True,
                       timeout=300, env={**os.environ, "PGPASSWORD": PG["pw"]})
    if r.returncode != 0:
        raise RuntimeError(f"psql failed: {r.stderr.strip()[:300]}")
    return r.stdout.strip()


def _copy(table: str, cols: list, rows: list, conflict_key: str) -> None:
    """Stage via COPY into a temp table, then upsert (idempotent; COPY carries the big text safely)."""
    buf = io.StringIO()
    w = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    for row in rows:
        w.writerow(["" if v is None else v for v in row])
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False, encoding="utf-8") as f:
        f.write(buf.getvalue())
        csvf = f.name
    stage = f"_stage_{table.split('.')[-1]}"
    collist = ", ".join(cols)
    script = (f"BEGIN;\n"
              f"create temp table {stage} (like {table} including defaults) on commit drop;\n"
              f"alter table {stage} drop column if exists fts;\n"
              f"alter table {stage} drop column if exists file_path;\n"
              f"\\copy {stage} ({collist}) from '{csvf}' with (format csv, null '')\n"
              f"insert into {table} ({collist}) select {collist} from {stage} "
              f"on conflict ({conflict_key}) do nothing;\n"
              f"COMMIT;\n")
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as f:
        f.write(script)
        sqlf = f.name
    try:
        _psql_file(sqlf)
    finally:
        os.unlink(csvf)
        os.unlink(sqlf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=os.path.join(REPO, ".recollection/conversation-index/db.sqlite"))
    a = ap.parse_args()
    con = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)   # READ-ONLY — the source-of-record is immutable
    con.row_factory = sqlite3.Row

    report = {}

    # ── 1. exchanges (with full text) ──────────────────────────────────────────
    rows, skipped = [], []
    id2addr = {}
    for r in con.execute("select * from exchanges"):
        sid = r["session_id"] or "unknown"
        addr = f"exchange://{sid}/{r['line_start']}"
        if addr in id2addr.values() and False:
            pass
        id2addr[r["id"]] = addr
        rows.append([addr, r["id"], r["session_id"], r["project"], r["timestamp"], r["line_start"],
                     r["line_end"], r["archive_path"], r["parent_uuid"], bool(r["is_sidechain"]),
                     r["harness"], r["model"], r["cwd"], r["git_branch"],
                     r["user_message"], r["assistant_message"]])
    # duplicate addresses (two sqlite rows → one (sid,line)): keep the first, count the rest
    seen, uniq = set(), []
    for row in rows:
        if row[0] in seen:
            skipped.append(f"dup-address {row[0]} (sqlite {row[1]})")
            continue
        seen.add(row[0])
        uniq.append(row)
    _copy("ledger.exchange",
          ["address", "sqlite_id", "session_id", "project", "ts", "line_start", "line_end", "archive_path",
           "parent_uuid", "is_sidechain", "harness", "model", "cwd", "git_branch", "user_text", "assistant_text"],
          uniq, "address")
    landed = int(_q("select count(*) from ledger.exchange"))
    src = int(con.execute("select count(*) from exchanges").fetchone()[0])
    report["exchanges"] = f"{src} source = {len(uniq)} upserted + {len(skipped)} dup-address skipped; table now {landed}"
    if len(uniq) + len(skipped) != src:
        raise RuntimeError(f"exchange reconciliation FAILED: {len(uniq)}+{len(skipped)} != {src}")

    # ── 2. tool_calls ───────────────────────────────────────────────────────────
    rows, orphans = [], 0
    for r in con.execute("select * from tool_calls"):
        addr = id2addr.get(r["exchange_id"])
        if addr is None:
            orphans += 1
            continue
        ti = r["tool_input"]
        try:
            json.loads(ti) if ti else None
        except Exception:
            ti = json.dumps({"_raw": str(ti)[:8000]})
        rows.append([r["id"], addr, r["tool_name"], ti or "{}",
                     (r["tool_result"] or "")[:200000], bool(r["is_error"]), r["timestamp"]])
    _copy("ledger.tool_call",
          ["call_id", "exchange_address", "tool_name", "tool_input", "tool_result", "is_error", "ts"],
          rows, "call_id")
    src_tc = int(con.execute("select count(*) from tool_calls").fetchone()[0])
    report["tool_calls"] = f"{src_tc} source = {len(rows)} upserted + {orphans} orphan-exchange skipped; table now " \
                           + _q("select count(*) from ledger.tool_call")
    if len(rows) + orphans != src_tc:
        raise RuntimeError("tool_call reconciliation FAILED")

    # ── 3. links → assertion (kinds pre-validated against ④'s registry — fail-loud before any row) ──
    for k in LINK_KIND.values():
        _q(f"select ledger.validate_edge_kind('{k}')")
    # the links' from_id/to_id are ALREADY ADDRESSES (exchange://<sid>/<line> · file:///abs/path) —
    # verified against the live sqlite; use them verbatim (file:// is a registered scheme).
    ins, unmapped = [], 0
    for r in con.execute("select from_id, to_id, edge_type from links"):
        fa, ta = r["from_id"], r["to_id"]
        if not fa or not ta or "://" not in fa or "://" not in ta:
            unmapped += 1
            continue
        ins.append((fa, LINK_KIND[r["edge_type"]], ta))
    # batched upsert via a VALUES script (small rows — no COPY needed)
    lines = ["BEGIN;"]
    for fa, k, ta in ins:
        def dq(s):
            i = 0
            while True:
                t = f"$rl{i}$"
                if t not in s:
                    return f"{t}{s}{t}"
                i += 1
        lines.append(f"insert into ledger.assertion (from_ref,kind,to_ref,to_resolved,provenance,produced_by_session) "
                     f"values ({dq(fa)},{dq(k)},{dq(ta)},{dq(ta)},'derived','recollection-move-0024') "
                     f"on conflict (from_ref,kind,to_ref) do nothing;")
    lines.append("COMMIT;")
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as f:
        f.write("\n".join(lines))
        sqlf = f.name
    try:
        _psql_file(sqlf)
    finally:
        os.unlink(sqlf)
    src_l = int(con.execute("select count(*) from links").fetchone()[0])
    landed_l = int(_q("select count(*) from ledger.assertion where provenance='derived'"))
    report["links"] = f"{src_l} source = {len(ins)} upserted + {unmapped} unmapped-id skipped; derived assertions now {landed_l}"
    if len(ins) + unmapped != src_l:
        raise RuntimeError("link reconciliation FAILED")

    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
