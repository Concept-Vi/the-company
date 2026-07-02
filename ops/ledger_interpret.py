#!/usr/bin/env python3
"""ops/ledger_interpret.py — the MODEL (interpretive) layer over the ledger. Companion to ledger_build.py.

The deterministic layer extracted facts; THIS adds what only a deep read gives — per file:
what_it_does · observations · standouts · conventions · concerns · notes · questions · purpose_vs_actual ·
apparent_themes · intention_signals · novelty · contribution (NEUTRAL — what it UNIQUELY brings to a fused
system, NO ranking) · summary_for_embedding · intention_for_embedding; and per public symbol: does · description.

SAFE-BY-DESIGN (the wedge lesson): model agents NEVER touch the DB. They read the original file + its
deterministic ledger facts and EMIT one JSON per file to a scratch dir. A SINGLE SERIAL ingest step then
UPDATEs the ledger. A completeness GATE (deterministic files with what_it_does IS NULL) drives a WAVE LOOP:
each wave processes a bounded slice, checkpoints to the DB, and the gate re-drives — so session/token limits
never force a partial; a killed wave loses nothing (done rows are committed; the gate skips them).

Subcommands:
  queue   --wave-bytes N --wave-files N   → write the next wave's batch lists to scratch; print the batch count
  ingest  --wave <dir>                    → serial-ingest a wave's emitted JSON into the ledger
  gate                                    → print remaining-unprocessed counts per project (the loop condition)
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRATCH = os.path.join(REPO, "build-prep", "the-one-system", "interpret")
PGCONF = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
          "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
          "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
          "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
          "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
# project → the filesystem root its paths are relative to (so an agent can open the original file).
# ④ THE CONTAINER (L1-SPINE, 2026-07-02): the hardcoded dict DIED AS CODE, LIVES AS DATA —
# container.projects.root_path (schema `container`, 0013_container.sql; landed by
# ops/migrate_container_from_cvi.py --slice spine). The dict below had a LIVE DEFECT: `platforms`
# (1,028 ledger entries) was absent, so its root silently defaulted to REPO. The registry read fixes
# that mechanically (registry-is-truth; the SPINE study's C1.5).
# -- PROJECT_ROOTS = {"company": REPO,                                          # pre-container path —
# --                  "counterpart-design": "/home/tim/repos/counterpart/design", # commented out, not
# --                  "claude-ds": os.path.join(REPO, "design", "claude-ds")}     # deleted (Tim's rule);
# -- expected container.projects.root_path (schema container, Postgres 127.0.0.1:15432); previously this
# -- dict; fix/restore: re-run ops/migrate_container_from_cvi.py --slice spine (or un-comment to fall back).
_PROJECT_ROOTS_CACHE: dict | None = None


def project_roots() -> dict:
    """project → root_path, read from container.projects (the registry; PROJECT_ROOTS's successor).
    Cached per process (the queue loop calls it per row). FAIL-LOUD if the container schema is absent —
    never a silent empty dict (an empty root map would silently mis-root every batch)."""
    global _PROJECT_ROOTS_CACHE
    if _PROJECT_ROOTS_CACHE is None:
        rows = _rows("select project_key, root_path from container.projects where root_path is not null")
        if not rows:
            raise RuntimeError(
                "project_roots: no container.projects rows with root_path — expected schema `container` "
                f"(Postgres {PGCONF['host']}:{PGCONF['port']}, 0013_container.sql); previously the "
                "hardcoded PROJECT_ROOTS dict above (commented out); fix: .venv/bin/python "
                "ops/migrate_container_from_cvi.py --slice spine")
        _PROJECT_ROOTS_CACHE = {k: r for k, r in rows}
    return _PROJECT_ROOTS_CACHE


def _psql(sql: str) -> str:
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", PGCONF["db"], "-v", "ON_ERROR_STOP=1", "-tA", "-F", "\t", "-c", sql],
                       capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"psql failed: {r.stderr.strip()}")
    return r.stdout


def _rows(sql: str):
    out = _psql(sql)
    return [ln.split("\t") for ln in out.splitlines() if ln]


def gate() -> dict:
    rows = _rows("select r.project, count(*) filter (where e.what_it_does is null), count(*) "
                 "from ledger.entry e join ledger.latest_run r using(run_id) "
                 "where e.node_type='file' and e.coverage_state='deterministic' group by r.project order by 1")
    out = {}
    for proj, todo, total in rows:
        out[proj] = {"remaining": int(todo), "total": int(total), "done": int(total) - int(todo)}
    return out


def queue(wave_bytes: int, wave_files: int, max_batches: int) -> dict:
    """Pull the next slice of unprocessed files, byte+count-bounded per batch, write batch lists to a wave dir."""
    rows = _rows(
        "select r.project, e.path, coalesce(e.size_bytes,0) "
        "from ledger.entry e join ledger.latest_run r using(run_id) "
        "where e.node_type='file' and e.coverage_state='deterministic' and e.what_it_does is null "
        "order by r.project, e.path")
    if not rows:
        return {"batches": 0, "files": 0, "wave_dir": None}
    # allocate into byte/count-bounded batches, grouped by project (so an agent's batch is one root)
    batches, cur, cur_b, cur_proj = [], [], 0, None
    def flush():
        nonlocal cur, cur_b
        if cur:
            batches.append(cur); cur, cur_b = [], 0
    for proj, path, sz in rows:
        sz = int(sz)
        if proj != cur_proj:
            flush(); cur_proj = proj
        if cur and (cur_b + sz > wave_bytes or len(cur) >= wave_files):
            flush()
        cur.append({"project": proj, "path": path, "root": project_roots().get(proj, REPO)}); cur_b += sz
        if len(batches) >= max_batches:
            break
    flush()
    batches = batches[:max_batches]
    # find next wave number
    os.makedirs(SCRATCH, exist_ok=True)
    # numeric-suffix waves only — a non-numeric lane dir (e.g. `wave-codex` from the codex producer)
    # must NOT break the next-number computation (int('codex') ValueError → killed the driver, 2026-06-28).
    existing = []
    for d in glob.glob(os.path.join(SCRATCH, "wave-*")):
        if os.path.isdir(d):
            suf = os.path.basename(d).split("-", 1)[1]
            if suf.isdigit():
                existing.append(int(suf))
    wn = (max(existing) + 1) if existing else 1
    wave_dir = os.path.join(SCRATCH, f"wave-{wn:03d}")
    os.makedirs(os.path.join(wave_dir, "alloc"), exist_ok=True)
    os.makedirs(os.path.join(wave_dir, "out"), exist_ok=True)
    nfiles = 0
    for i, b in enumerate(batches, 1):
        with open(os.path.join(wave_dir, "alloc", f"batch-{i:03d}.json"), "w") as f:
            json.dump(b, f)
        nfiles += len(b)
    return {"batches": len(batches), "files": nfiles, "wave_dir": wave_dir}


def ingest(wave_dir: str) -> dict:
    """Serial-ingest a wave's emitted per-file JSON into the ledger (UPDATE entry + symbol). One file at a time."""
    out_dir = os.path.join(wave_dir, "out")
    # os.walk (NOT glob '*.json' — glob silently skips DOTFILES like .gitignore.json, leaving them uningested)
    files = sorted(os.path.join(dp, fn) for dp, _, fns in os.walk(out_dir) for fn in fns if fn.endswith(".json"))
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    ok, bad = 0, 0
    ENTRY_FIELDS = ["what_it_does", "observations", "standouts", "conventions", "concerns", "notes",
                    "questions", "purpose_vs_actual", "apparent_themes", "intention_signals", "novelty",
                    "contribution", "summary_for_embedding", "intention_for_embedding",
                    "suggested_fields", "proposed_edge_kinds"]
    JSONB = {"observations", "standouts", "conventions", "concerns", "questions", "apparent_themes",
             "suggested_fields", "proposed_edge_kinds"}
    sql_lines = ["BEGIN;"]
    for jf in files:
        try:
            rec = json.load(open(jf))
            proj, path = rec["project"], rec["path"]
        except Exception:
            bad += 1; continue
        sets = [f"interp_model={_dq(rec.get('model','opus'))}", "interp_at=now()",
                f"interp_prompt_version={_dq(rec.get('prompt_version','v2-full'))}"]
        for k in ENTRY_FIELDS:
            v = rec.get(k)
            if v is None:
                continue
            if k in JSONB:
                sets.append(f"{k}={_dq(json.dumps(v))}::jsonb")
            else:
                sets.append(f"{k}={_dq(str(v))}")
        sql_lines.append(
            f"update ledger.entry e set {', '.join(sets)} from ledger.latest_run r "
            f"where e.run_id=r.run_id and r.project={_dq(proj)} and e.path={_dq(path)};")
        for s in rec.get("symbols", []):
            ss = []
            if s.get("does"): ss.append(f"does={_dq(s['does'])}")
            if s.get("description"): ss.append(f"description={_dq(s['description'])}")
            if s.get("summary_for_embedding"): ss.append(f"summary_for_embedding={_dq(s['summary_for_embedding'])}")
            if ss and s.get("code_id"):
                ss.append("interp_at=now()")
                sql_lines.append(f"update ledger.symbol sy set {', '.join(ss)} from ledger.latest_run r "
                                 f"where sy.run_id=r.run_id and r.project={_dq(proj)} and sy.code_id={_dq(s['code_id'])};")
        ok += 1
    sql_lines.append("COMMIT;")
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", PGCONF["db"], "-v", "ON_ERROR_STOP=1"],
                       input="\n".join(sql_lines), capture_output=True, text=True, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"ingest transaction failed (rolled back): {r.stderr.strip()[:400]}")
    return {"ingested_files": ok, "bad": bad}


def _esc(s: str) -> str:
    return str(s).replace("'", "''")


def _dq(s: str) -> str:
    """Postgres dollar-quote with a UNIQUE tag guaranteed absent from the text — so content containing
    `$$` (e.g. a Postgres DO $$...$$ block quoted inside an interpretive field) can't break the SQL."""
    s = str(s)
    i = 0
    while True:
        tag = f"$q{i}$"
        if tag not in s:
            return f"{tag}{s}{tag}"
        i += 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["queue", "ingest", "gate"])
    ap.add_argument("--wave-bytes", type=int, default=60000)
    ap.add_argument("--wave-files", type=int, default=8)
    ap.add_argument("--max-batches", type=int, default=40)
    ap.add_argument("--wave", default="")
    a = ap.parse_args()
    if a.cmd == "gate":
        print(json.dumps(gate(), indent=2))
    elif a.cmd == "queue":
        print(json.dumps(queue(a.wave_bytes, a.wave_files, a.max_batches), indent=2))
    elif a.cmd == "ingest":
        print(json.dumps(ingest(a.wave), indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
