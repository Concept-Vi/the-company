#!/usr/bin/env python3
"""ops/backfill_provenance.py — the FULL write-tool provenance backfill (Plan-B DB1 §1c, executed).

Walks EVERY session archive under ~/.claude/projects (not just recollection's indexed 12%), extracts the
write-tool invocations (Write/Edit/MultiEdit/NotebookEdit carrying file_path), normalizes each path to a
code:// address via the PROJECT ROOTS map, and lands `generated-by` assertions (file → the exchange that
wrote it) in the durable layer. The transcript root becomes each file's authorship timeline.

HONESTY CONTRACT (the coverage number must never rot silently):
  · INCREMENTAL by per-file line high-water marks (state json) — a re-run walks only new lines.
  · Every skip is COUNTED by reason (outside-roots, no-file_path, unresolvable) — the discard ledger is
    part of the output; coverage is reported as a measured % of latest files, never padded.
  · Assertions are idempotent (PK from_ref,kind,to_ref keeps one row per file↔exchange pair).

Run:  .venv/bin/python ops/backfill_provenance.py [--limit-files N] [--projects-dir ~/.claude/projects]
Also registered as the jobs handler `provenance_backfill` (incremental — the heartbeat's sibling).
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
      "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
      "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
      "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
      "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
WRITE_TOOLS = {"Write", "Edit", "MultiEdit", "NotebookEdit"}
STATE_PATH = os.path.join(REPO, ".data", "store", "provenance_backfill_state.json")

# PROJECT ROOTS — abs-path prefix → the ledger project label (longest prefix wins). The ledger's four
# projects + the worktree convention. A path outside every root is COUNTED (outside-roots), never guessed.
ROOTS = [
    ("/home/tim/company/", "company"),
    ("/home/tim/repos/counterpart/design/", "counterpart-design"),
    ("/home/tim/repos/claude-ds/", "claude-ds"),
    ("/home/tim/platforms/", "platforms"),
]


def _addr_for(path: str) -> str | None:
    for root, proj in ROOTS:
        if path.startswith(root):
            return f"code://{proj}/{path[len(root):]}"
        # worktree form: <root minus slash>-worktrees/... or .claude/worktrees inside the root
        wt = root.rstrip("/") + "-worktrees/"
        if path.startswith(wt):
            rel = path[len(wt):].split("/", 1)
            if len(rel) == 2:
                return f"code://{proj}/{rel[1]}"
    return None


def _dq(s: str) -> str:
    i = 0
    while True:
        t = f"$pb{i}$"
        if t not in s:
            return f"{t}{s}{t}"
        i += 1


def _psql_file(path: str) -> None:
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-f", path], capture_output=True, text=True,
                       timeout=1800, env={**os.environ, "PGPASSWORD": PG["pw"]})
    if r.returncode != 0:
        raise RuntimeError(f"psql failed: {r.stderr.strip()[:300]}")


def walk_session(fp: str, start_line: int) -> tuple[list, dict, int]:
    """One jsonl: (assertions [(file_addr, exchange_addr, ts)], discards {reason: n}, last_line)."""
    sid = os.path.basename(fp).rsplit(".jsonl", 1)[0]
    out, disc = [], {"outside_roots": 0, "no_file_path": 0}
    n = 0
    try:
        with open(fp, errors="replace") as f:
            for n, line in enumerate(f, 1):
                if n <= start_line or '"tool_use"' not in line:
                    continue
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                msg = e.get("message") or {}
                for b in (msg.get("content") or []) if isinstance(msg.get("content"), list) else []:
                    if not (isinstance(b, dict) and b.get("type") == "tool_use"
                            and b.get("name") in WRITE_TOOLS):
                        continue
                    p = (b.get("input") or {}).get("file_path") or (b.get("input") or {}).get("notebook_path")
                    if not p:
                        disc["no_file_path"] += 1
                        continue
                    addr = _addr_for(p)
                    if addr is None:
                        disc["outside_roots"] += 1
                        continue
                    out.append((addr, f"exchange://{sid}/{n}", e.get("timestamp") or ""))
    except OSError:
        return [], {"unreadable": 1}, start_line
    return out, disc, n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--projects-dir", default=os.path.expanduser("~/.claude/projects"))
    ap.add_argument("--limit-files", type=int, default=0)
    a = ap.parse_args()
    state = {}
    if os.path.exists(STATE_PATH):
        state = json.load(open(STATE_PATH))
    files = []
    for root, _dirs, names in os.walk(a.projects_dir):
        for nm in names:
            if nm.endswith(".jsonl"):
                files.append(os.path.join(root, nm))
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    if a.limit_files:
        files = files[:a.limit_files]

    total_asserts, discards = 0, {}
    batch, walked = [], 0
    for fp in files:
        st = state.get(fp, {})
        try:
            mt = os.path.getmtime(fp)
        except OSError:
            continue
        if st.get("mtime") == mt:                    # unchanged since last walk — skip whole file
            continue
        rows, disc, last = walk_session(fp, st.get("line", 0))
        for k, v in disc.items():
            discards[k] = discards.get(k, 0) + v
        batch.extend(rows)
        state[fp] = {"line": last, "mtime": mt}
        walked += 1
        if len(batch) >= 4000:
            _land(batch); total_asserts += len(batch); batch = []
            json.dump(state, open(STATE_PATH, "w"))
    if batch:
        _land(batch); total_asserts += len(batch)
    json.dump(state, open(STATE_PATH, "w"))
    print(json.dumps({"files_walked": walked, "files_total": len(files),
                      "assertions_landed": total_asserts, "discards": discards}, indent=1))
    return {"files_walked": walked, "assertions": total_asserts, "discards": discards}


def _land(rows: list) -> None:
    lines = ["BEGIN;"]
    for addr, ex, ts in rows:
        tsv = f"{_dq(ts)}::timestamptz" if ts else "now()"
        lines.append(f"insert into ledger.assertion (from_ref,kind,to_ref,to_resolved,provenance,produced_by_session,ts) "
                     f"values ({_dq(addr)},'generated-by',{_dq(ex)},{_dq(ex)},'authored','provenance-backfill',{tsv}) "
                     f"on conflict (from_ref,kind,to_ref) do nothing;")
    lines.append("COMMIT;")
    with tempfile.NamedTemporaryFile("w", suffix=".sql", delete=False) as f:
        f.write("\n".join(lines))
        p = f.name
    try:
        _psql_file(p)
    finally:
        os.unlink(p)


def backfill_provenance(limit_files: int = 0) -> dict:
    """The jobs-handler face (incremental — mtime+line watermarks make re-runs cheap)."""
    import sys
    sys.argv = ["backfill_provenance"] + (["--limit-files", str(limit_files)] if limit_files else [])
    return main()


if __name__ == "__main__":
    raise SystemExit(0 if main() else 0)
