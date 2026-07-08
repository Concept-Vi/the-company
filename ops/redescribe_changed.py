#!/usr/bin/env python3
"""ops/redescribe_changed.py — M3: 're-describe changed files' as ONE job body (the worked generative
example of the potentials loop). The chain in one handler:

  1. SELECT the changed set — files whose git last_modified_at (durable file_meta) is newer than their
     durable description's interp_at (or that have no description at all). Deterministic set-work.
  2. DESCRIBE each via the ONE interpret pipeline (ops/ledger_interpret_ollama's prompt + model — kimi
     by default; reuse-never-fork), writing straight into ledger.interpretation keyed (address,
     source_hash) — the durable home, so nothing can strand it.
  3. The desc embedding space picks the new text up on its next build (the armed scale/build jobs).

Registered as the jobs handler `redescribe_changed` (params: since?, cap). Incremental by construction:
a file whose description is newer than its last change is skipped. Every skip/failure counted.

Run: .venv/bin/python ops/redescribe_changed.py [--cap 20] [--project company]
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "ops"))

PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
      "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
      "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
      "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
      "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}


def _dq(s: str) -> str:
    i = 0
    while True:
        t = f"$rd{i}$"
        if t not in str(s):
            return f"{t}{s}{t}"
        i += 1


def _psql(sql: str) -> str:
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-tA"], input=sql, capture_output=True, text=True,
                       timeout=300, env={**os.environ, "PGPASSWORD": PG["pw"]})
    if r.returncode != 0:
        raise RuntimeError(f"redescribe psql failed: {r.stderr.strip()[:250]}")
    return r.stdout.strip()


def changed_set(project: str, cap: int) -> list:
    """Files whose content changed after their durable description (or never described): the honest
    selector, from the DURABLE tables only (file_meta time × interpretation freshness)."""
    out = _psql(f"""
        select e.path, e.address, coalesce(e.source_hash,'')
        from ledger.unit_latest e
        join ledger.file_meta fm on fm.project = e.project and fm.path = e.path
        left join ledger.interpretation i on i.address = e.address and i.source_hash = coalesce(e.source_hash,'')
        where e.project = {_dq(project)} and e.node_type = 'file'
          and e.ext in ('.py','.ts','.tsx','.js','.jsx','.md')
          and coalesce(e.coverage_state,'') <> 'excluded'
          and (i.address is null or fm.last_modified_at > coalesce(i.interp_at, 'epoch'::timestamptz))
        order by fm.last_modified_at desc limit {int(cap)}""")
    rows = []
    for l in out.splitlines():
        if l.count("|") >= 2:
            p, addr, h = l.split("|", 2)
            rows.append({"path": p, "address": addr, "source_hash": h})
    return rows


def describe_one(item: dict, project: str) -> dict | None:
    """One file through the ONE interpret pipeline (prompt + model + json-extraction reused verbatim)."""
    import ledger_interpret_ollama as lio
    ap = os.path.join(REPO, item["path"])
    if not os.path.isfile(ap):
        return None
    src = open(ap, errors="replace").read()
    if len(src) > 180_000:                     # the pipeline's own bounded-read law: flag, never truncate
        return {"_skip": "oversize (chunking lane)"}
    raw = lio._call_ollama(lio._prompt(project, item["path"], src, []))   # the ONE prompt (symbols lane separate)
    rec = lio._extract_json(raw)
    return rec if isinstance(rec, dict) and rec.get("what_it_does") else None


def redescribe_changed(project: str = "company", cap: int = 20) -> dict:
    """The jobs-handler face: select → describe → land durably → report with denominators."""
    items = changed_set(project, int(cap))
    if not items:
        return {"changed": 0, "described": 0, "note": "nothing newer than its description — current"}
    ok, failed, skipped = 0, [], 0
    for it in items:
        try:
            rec = describe_one(it, project)
        except Exception as e:
            failed.append(f"{it['path']}: {type(e).__name__}: {str(e)[:80]}")
            continue
        if rec is None:
            skipped += 1
            continue
        if rec.get("_skip"):
            skipped += 1
            continue
        cols = {"what_it_does": rec.get("what_it_does"), "kind": rec.get("kind"),
                "purpose_doc": rec.get("purpose_doc"), "contribution": rec.get("contribution"),
                "interp_model": rec.get("model") or "kimi-k2.7-code:cloud",
                "interp_prompt_version": rec.get("prompt_version") or "v2-full",
                "produced_by_session": "job:redescribe_changed"}
        sets = ", ".join(f"{k} = {_dq(v)}" for k, v in cols.items() if v)
        _psql(f"insert into ledger.interpretation (address, source_hash, what_it_does, interp_at) "
              f"values ({_dq(it['address'])}, {_dq(it['source_hash'])}, {_dq(rec['what_it_does'])}, now()) "
              f"on conflict (address, source_hash) do update set {sets}, interp_at = now()")
        ok += 1
    return {"changed": len(items), "described": ok, "skipped": skipped,
            "failed": failed[:6], "failed_n": len(failed)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="company")
    ap.add_argument("--cap", type=int, default=20)
    a = ap.parse_args()
    print(json.dumps(redescribe_changed(a.project, a.cap), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
