#!/usr/bin/env python3
"""ops/build_file_meta.py — L9 time axis: populate ledger.file_meta from git history (run-INDEPENDENT).

The TIME axis kept dying because it was captured as file_meta on run-scoped ledger.entry rows (present only
in 3 dead runs — B·R1). The cure (migration 0014) is a run-independent ledger.file_meta table keyed
(project, path); this populates it by walking git log ONCE per project and aggregating per path:
  created_at       = the file's OLDEST commit (its birth)
  last_modified_at = its NEWEST commit
  change_count     = distinct commits that touched it
  first/last_commit = the bounding shas
So "what changed after T" is one indexed predicate, and unit_latest's file_created_at/modified/change_count
legs light up — supersession-proof by construction (no run_id anywhere).

Renames: git log without --follow lists a renamed file under both paths (v1 accepts this; --follow per-file
is O(files) subprocesses — too slow at 18k). A rename-map pass is a noted refinement, not silent loss.

Run:  .venv/bin/python ops/build_file_meta.py [--project company] [--repo .]
Incremental follow-on (the heartbeat job): walk only commits since the last-loaded sha per project.
"""
from __future__ import annotations
import argparse
import os
import subprocess

REPO_DEFAULT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
      "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
      "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
      "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
      "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}


def _dq(s: str) -> str:
    i = 0
    while True:
        t = f"$fm{i}$"
        if t not in s:
            return f"{t}{s}{t}"
        i += 1


def _psql(sql: str, timeout: int = 300) -> str:
    # pass SQL on STDIN (not -c) so large batch statements never hit the arg-list limit
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-tA"], input=sql, capture_output=True, text=True,
                       timeout=timeout, env={**os.environ, "PGPASSWORD": PG["pw"]})
    if r.returncode != 0:
        raise RuntimeError(f"file_meta psql failed: {(r.stderr or '').strip()[:300]}")
    return r.stdout.strip()


def walk_git(repo: str) -> dict:
    """One `git log` pass → {path: {created_at, last_modified_at, change_count, first_commit, last_commit}}.
    git log is newest→oldest, so the FIRST time we see a path is its last_modified, the LAST is its created."""
    out = subprocess.run(["git", "-C", repo, "log", "--no-merges", "--name-only",
                          "--format=%x01%H%x02%aI", "HEAD"], capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        raise RuntimeError(f"git log failed in {repo}: {out.stderr.strip()[:200]}")
    agg: dict[str, dict] = {}
    sha = ts = None
    for line in out.stdout.splitlines():
        if line.startswith("\x01"):                              # a commit header: \x01<sha>\x02<iso-date>
            rest = line[1:]
            sha, _, ts = rest.partition("\x02")
            continue
        path = line.strip()
        if not path or sha is None:
            continue
        m = agg.get(path)
        if m is None:                                            # first sighting = NEWEST commit (log is desc)
            agg[path] = {"last_modified_at": ts, "last_commit": sha,
                         "created_at": ts, "first_commit": sha, "change_count": 1}
        else:                                                    # later sightings are OLDER → move created back
            m["created_at"] = ts
            m["first_commit"] = sha
            m["change_count"] += 1
    return agg


def load_file_meta(project: str, repo: str) -> dict:
    agg = walk_git(repo)
    if not agg:
        return {"project": project, "paths": 0, "note": "git log empty"}
    # batch upsert via a VALUES list (chunked); on-conflict updates (a re-walk refreshes)
    rows = list(agg.items())
    n = 0
    CHUNK = 500
    for i in range(0, len(rows), CHUNK):
        vals = []
        for path, m in rows[i:i + CHUNK]:
            addr = f"code://{project}/{path}"
            vals.append(f"({_dq(project)},{_dq(path)},{_dq(addr)},{_dq(m['created_at'])}::timestamptz,"
                        f"{_dq(m['last_modified_at'])}::timestamptz,{m['change_count']},"
                        f"{_dq(m['first_commit'])},{_dq(m['last_commit'])},'git',now())")
        _psql(f"insert into ledger.file_meta (project,path,address,created_at,last_modified_at,change_count,"
              f"first_commit,last_commit,temporal_source,updated_at) values {','.join(vals)} "
              f"on conflict (project,path) do update set created_at=excluded.created_at, "
              f"last_modified_at=excluded.last_modified_at, change_count=excluded.change_count, "
              f"first_commit=excluded.first_commit, last_commit=excluded.last_commit, updated_at=now()")
        n += len(vals)
    return {"project": project, "paths": n,
            "total_in_table": int(_psql("select count(*) from ledger.file_meta")),
            "matched_entries": int(_psql(
                "select count(*) from ledger.file_meta fm "
                f"where exists (select 1 from ledger.entry_latest e where e.project={_dq(project)} "
                "and e.path=fm.path)"))}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="company")
    ap.add_argument("--repo", default=REPO_DEFAULT)
    a = ap.parse_args()
    res = load_file_meta(a.project, a.repo)
    print(f"file_meta loaded: {res}")


if __name__ == "__main__":
    raise SystemExit(main())
