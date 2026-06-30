#!/usr/bin/env python3
"""ops/extraction_audit_run.py — drive the extraction_audit role over the ledger's CODE files (Tim 2026-06-30).

The full pass: for every code file, build the audit input (file kind + the per-kind CONTRACT + the
CONSOLIDATED extraction the ledger holds + the file content), fan it through the LIVE cognition engine
(POST /api/cognition/run_items — the resident 4B, no-think via the role's thinking=False), and land each
file's structured findings in Supabase `ledger.coverage_findings` so the failure classes are queryable in
aggregate. NOT a sample — completeness is the point.

In-system: the model runs through the engine's own run_items endpoint (not a bespoke model call). This
driver only assembles inputs (from the ledger) + persists outputs (to the ledger) — the data plumbing the
MCP-tool-per-call surface can't loop by hand.

Run:  python3 ops/extraction_audit_run.py --limit 20         # a measured first batch
      python3 ops/extraction_audit_run.py                     # the full code-file pass
"""
from __future__ import annotations
import argparse, json, os, subprocess, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PG = {"h": "127.0.0.1", "p": "15432", "u": "postgres", "d": "postgres", "pw": "postgres"}
BRIDGE = os.environ.get("COMPANY_BRIDGE", "http://127.0.0.1:8770") + "/api/cognition/run_items"
ROOTS = {"company": REPO, "counterpart-design": "/home/tim/repos/counterpart/design",
         "claude-ds": os.path.join(REPO, "design", "claude-ds")}
CODE_EXTS = (".py", ".js", ".jsx", ".ts", ".tsx")

# per-kind CONTRACT — what the extractor is SUPPOSED to capture (stated as INTENT; the role treats it as
# examples, not a closed list, so contract blind-spots surface too). file-type → rules (the registry shape
# Tim described: ext matches a type, rules resolve into the prompt).
CONTRACTS = {
    ".py":  "functions (incl. nested, async, methods), classes, all imports, module-level constants "
            "(UPPER or _UPPER names), and registry-dict rows (UPPER = {...}).",
    ".js":  "functions (incl. arrow + nested), classes, exports, React components, hooks, imports, "
            "and module-level constants.",
    ".jsx": "functions (incl. arrow + nested), React components, classes, exports, hooks, imports, "
            "and module-level constants.",
    ".ts":  "functions, classes, types, interfaces, enums, exports, imports, and module-level constants.",
    ".tsx": "functions, React components, classes, types, interfaces, enums, exports, hooks, imports, "
            "and module-level constants.",
}


def _psql(sql: str) -> str:
    return subprocess.run(["psql", "-h", PG["h"], "-p", PG["p"], "-U", PG["u"], "-d", PG["d"], "-tAc", sql],
                          capture_output=True, text=True, env={**os.environ, "PGPASSWORD": PG["pw"]}).stdout


_TABLE_DDL = ("create table if not exists ledger.coverage_findings(entry_id uuid primary key, project text, "
              "path text, file_kind text, complete bool, findings jsonb, kind_seen text, run_addr text, "
              "ts timestamptz default now());")


def _ensure_table():
    _psql(_TABLE_DDL + " select 1;")


def _files(limit: int, resume: bool = True) -> list:
    lim = f"limit {int(limit)}" if limit else ""
    ext_in = ",".join(f"$q${e}$q$" for e in CODE_EXTS)
    skip = "and e.entry_id not in (select entry_id from ledger.coverage_findings)" if resume else ""
    rows = _psql(
        f"select e.entry_id||chr(9)||e.project||chr(9)||e.path||chr(9)||e.ext||chr(9)||"
        f"coalesce(e.imports::text,'[]')||chr(9)||coalesce(e.signals::text,'{{}}')||chr(9)||"
        f"coalesce((select string_agg(coalesce(s.symbol_kind,'?')||' '||s.name, ', ' order by s.line_start) "
        f"  from ledger.symbol s where s.run_id=e.run_id and s.parent_path=e.path),'') "
        f"from ledger.entry e join ledger.latest_run r using(run_id) "
        f"where e.node_type='file' and e.what_it_does is not null and coalesce(e.interp_model,'') not like 'excluded:%' "
        f"and e.ext in ({ext_in}) {skip} order by e.project, e.path {lim}").splitlines()
    out = []
    for r in rows:
        f = r.split("\t")
        if len(f) >= 7:
            out.append({"entry_id": f[0], "project": f[1], "path": f[2], "ext": f[3],
                        "imports": f[4], "signals": f[5], "symbols": f[6]})
    return out


# the resident AWQ serves a 16384-token context; budget the FILE content well under it (prompt + contract +
# extraction + the schema-constrained output all share the window). ~3.7 chars/token → ~40k chars ≈ 11k tok.
_MAX_CONTENT_CHARS = 40000


def _utterance(it: dict) -> str | None | str:
    try:
        content = open(os.path.join(ROOTS.get(it["project"], REPO), it["path"]), errors="replace").read()
    except Exception:
        return None
    if len(content) > _MAX_CONTENT_CHARS:
        return "__OVERSIZE__"     # honest skip — recorded as oversize, NOT silently truncated (no-partial law)
    imps = ", ".join(str(i.get("target", i) if isinstance(i, dict) else i) for i in json.loads(it["imports"])) or "(none)"
    captured = it["symbols"] or "(none)"
    return (f"FILE_KIND: {it['ext'].lstrip('.')}\n"
            f"CONTRACT (what the extractor should capture): {CONTRACTS.get(it['ext'], 'all named symbols/definitions.')}\n"
            f"CAPTURED (the consolidated symbols + imports the extractor persisted): {captured}\n"
            f"CAPTURED IMPORTS: {imps}\n"
            f"EXTRACTION COUNTS (the extractor's own tallies): {it['signals']}\n\n"
            f"--- FILE {it['project']}/{it['path']} ---\n{content}")


def _run_one(it: dict) -> dict | None:
    utt = _utterance(it)
    if utt is None:
        return None
    if utt == "__OVERSIZE__":
        return {**it, "_status": "ok", "complete": False,
                "findings": [{"discrepancy_type": "other", "name": "", "symbol_kind": "",
                              "location": "", "detail": "file exceeds the model context window — audit skipped; "
                              "needs chunking (recorded, not silently passed)"}],
                "kind_seen": "oversize", "run_addr": ""}
    body = json.dumps({"role": "extraction_audit", "items": [utt], "max_tokens": 900}).encode()
    req = urllib.request.Request(BRIDGE, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=240) as r:
            d = json.loads(r.read())
        res = d.get("resolved", {}).get("0")
        if not isinstance(res, dict):
            return {**it, "_status": "bad-output"}
        return {**it, "_status": "ok", "complete": bool(res.get("complete")),
                "findings": res.get("findings", []), "kind_seen": res.get("kind_seen", ""),
                "run_addr": d.get("addresses", {}).get("0", "")}
    except Exception as e:
        return {**it, "_status": f"err:{str(e)[:80]}"}


def _persist(results: list):
    import csv
    scratch = os.environ.get("CLAUDE_JOB_DIR", "/tmp")
    csvp, sqlp = os.path.join(scratch, "cf.csv"), os.path.join(scratch, "cf.sql")
    with open(csvp, "w", newline="") as fh:
        w = csv.writer(fh)
        for r in results:
            if r and r.get("_status") == "ok":
                w.writerow([r["entry_id"], r["project"], r["path"], r["ext"].lstrip("."),
                            "t" if r["complete"] else "f", json.dumps(r["findings"]),
                            r.get("kind_seen", ""), r.get("run_addr", "")])
    open(sqlp, "w").write(
        "create table if not exists ledger.coverage_findings(entry_id uuid primary key, project text, "
        "path text, file_kind text, complete bool, findings jsonb, kind_seen text, run_addr text, ts timestamptz default now());\n"
        "create temp table _cf(entry_id uuid, project text, path text, file_kind text, complete bool, "
        "findings jsonb, kind_seen text, run_addr text);\n"
        f"\\copy _cf from '{csvp}' with (format csv)\n"
        "insert into ledger.coverage_findings(entry_id,project,path,file_kind,complete,findings,kind_seen,run_addr) "
        "select entry_id,project,path,file_kind,complete,findings,kind_seen,run_addr from _cf "
        "on conflict (entry_id) do update set complete=excluded.complete, findings=excluded.findings, "
        "kind_seen=excluded.kind_seen, run_addr=excluded.run_addr, ts=now();\n")
    r = subprocess.run(["psql", "-h", PG["h"], "-p", PG["p"], "-U", PG["u"], "-d", PG["d"],
                        "-v", "ON_ERROR_STOP=1", "-f", sqlp], capture_output=True, text=True,
                       env={**os.environ, "PGPASSWORD": PG["pw"]})
    return r.stdout.strip() or r.stderr.strip()[:300]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=6)   # GPU-bound: moderate beats swamping (24→timeouts)
    ap.add_argument("--no-resume", action="store_true")
    a = ap.parse_args()
    _ensure_table()                                          # so resume-skip + persist work on first run
    files = _files(a.limit, resume=not a.no_resume)
    print(f"auditing {len(files)} code files (resume on) | concurrency={a.concurrency} | engine={BRIDGE}", flush=True)
    import time
    t0 = time.time()
    chunk, done, ok_total, flag_total, err_total = [], 0, 0, 0, 0
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = [ex.submit(_run_one, it) for it in files]
        for fut in as_completed(futs):
            r = fut.result(); done += 1
            if r and r.get("_status") == "ok":
                ok_total += 1; flag_total += (not r["complete"]); chunk.append(r)
            else:
                err_total += 1
            if len(chunk) >= 30:                             # incremental flush — crash-safe + queryable mid-run
                _persist(chunk); chunk = []
            if done % 20 == 0:
                print(f"  {done}/{len(files)}  ok={ok_total} flagged={flag_total} err={err_total}  {time.time()-t0:.0f}s", flush=True)
    if chunk:
        print("final persist:", _persist(chunk))
    print(f"\nDONE: {ok_total}/{len(files)} ok | {flag_total} flagged | {err_total} err | {time.time()-t0:.0f}s", flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
