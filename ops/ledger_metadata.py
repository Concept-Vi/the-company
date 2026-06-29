#!/usr/bin/env python3
"""ops/ledger_metadata.py — per-file METADATA enrichment (Tim 2026-06-29).

Adds the metadata Tim named — when created, when last changed, how OFTEN changed (frequency), size in bytes
AND characters — plus per-file-type measures. All of it is FACTS / TIMESTAMPS / COUNTS (no confidence, G16).
The temporal trio (created / last-changed / change-count) comes from GIT HISTORY — recorded fact, not inference.

Stored in a `file_meta` jsonb column on ledger.entry. Deterministic, no model, GPU-free. A standing Company
operation (reflects into ops): re-runnable; git is mined ONE pass per repo (cheap — ~0.3s/1982 commits).

  universal : created_at · last_modified_at · change_count · author_count · size_bytes · char_count · line_count
  code      : + symbol_count · import_count
  markdown  : + word_count · heading_count · link_count · has_frontmatter
  css       : + rule_count
  svg       : + has_viewbox  (dims live in signals already)

Run:  python3 ops/ledger_metadata.py            # all real (non-excluded) files
"""
from __future__ import annotations
import json, os, re, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PG = {"host": "127.0.0.1", "port": "15432", "user": "postgres", "db": "postgres", "pw": "postgres"}
# project -> (git repo root, path prefix inside that repo)
GIT_MAP = {"company": (REPO, ""), "claude-ds": (REPO, "design/claude-ds/"),
           "counterpart-design": ("/home/tim/repos/counterpart/design", "")}
ROOTS = {"company": REPO, "counterpart-design": "/home/tim/repos/counterpart/design",
         "claude-ds": os.path.join(REPO, "design", "claude-ds")}


def _psql(sql: str, inp: str | None = None) -> str:
    return subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                           "-tAc", sql] if inp is None else
                          ["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"], "-c", sql],
                          input=inp, capture_output=True, text=True, env={**os.environ, "PGPASSWORD": PG["pw"]}).stdout


def git_temporal(repo: str) -> dict:
    """ONE reverse-chron pass over HEAD → {gitpath: {created, last_modified, change_count, authors:set}}.
    git log is newest-first: first sight of a path = last_modified; keep overwriting created → ends oldest."""
    out = subprocess.run(["git", "-C", repo, "log", "--format=C\t%aI\t%an", "--name-only", "HEAD"],
                         capture_output=True, text=True).stdout
    meta, date, author = {}, None, None
    for ln in out.splitlines():
        if ln.startswith("C\t"):
            _, date, author = ln.split("\t", 2)
        elif ln.strip():
            m = meta.get(ln)
            if m is None:
                meta[ln] = {"created_at": date, "last_modified_at": date, "change_count": 1, "authors": {author}}
            else:
                m["created_at"] = date            # reverse-chron → last write is the oldest = created
                m["change_count"] += 1
                m["authors"].add(author)
    return meta


_HEAD = re.compile(r"^#{1,6}\s", re.M)
_LINK = re.compile(r"\[\[[^\]]+\]\]|\]\(")          # wikilinks + markdown links


def per_type(ext: str, text: str) -> dict:
    e = ext.lower()
    if e == ".md":
        return {"word_count": len(text.split()), "heading_count": len(_HEAD.findall(text)),
                "link_count": len(_LINK.findall(text)), "has_frontmatter": text.lstrip().startswith("---")}
    if e == ".css":
        return {"rule_count": text.count("{")}
    if e == ".svg":
        return {"has_viewbox": "viewBox" in text}
    return {}


def main():
    # 0. ensure the column exists
    _psql("alter table ledger.entry add column if not exists file_meta jsonb;", inp="")
    # 1. git temporal per repo (cheap, one pass)
    git = {}
    for repo in {GIT_MAP[p][0] for p in GIT_MAP}:
        git[repo] = git_temporal(repo)
        print(f"git-mined {repo}: {len(git[repo])} paths", flush=True)
    # 2. the real (non-excluded) file rows + their ledger-side counts
    rows = _psql(
        "select e.entry_id||chr(9)||e.project||chr(9)||e.path||chr(9)||coalesce(e.ext,'')||chr(9)||"
        "coalesce(e.size_bytes,0)||chr(9)||coalesce(e.line_count,0)||chr(9)||"
        "coalesce(jsonb_array_length(e.imports),0)||chr(9)||"
        "coalesce((select count(*) from ledger.symbol s where s.run_id=e.run_id and s.parent_path=e.path),0) "
        "from ledger.entry e join ledger.latest_run r using(run_id) "
        "where e.node_type='file' and e.coverage_state='deterministic' "
        "and coalesce(e.interp_model,'') not like 'excluded:%'").splitlines()
    print(f"enriching {len(rows)} files", flush=True)
    out_lines = []
    miss_git = 0
    for r in rows:
        f = r.split("\t")
        if len(f) < 8:
            continue
        eid, proj, path, ext, size, lines, imp, syms = f
        repo, prefix = GIT_MAP.get(proj, (REPO, ""))
        gmeta = git.get(repo, {}).get(prefix + path)
        meta = {"size_bytes": int(size), "line_count": int(lines)}
        # char_count + per-type (read the file once)
        try:
            text = open(os.path.join(ROOTS.get(proj, REPO), path), "r", errors="replace").read()
            meta["char_count"] = len(text)
            meta.update(per_type(ext, text))
        except Exception:
            pass
        if int(syms):
            meta["symbol_count"] = int(syms)
        if int(imp):
            meta["import_count"] = int(imp)
        if gmeta:
            meta.update({"created_at": gmeta["created_at"], "last_modified_at": gmeta["last_modified_at"],
                         "change_count": gmeta["change_count"], "author_count": len(gmeta["authors"]),
                         "temporal_source": "git"})
        else:
            miss_git += 1
            try:
                meta["last_modified_at"] = subprocess.run(
                    ["stat", "-c", "%y", os.path.join(ROOTS.get(proj, REPO), path)],
                    capture_output=True, text=True).stdout.strip() or None
            except Exception:
                pass
            meta["temporal_source"] = "fs-fallback (untracked)"
        out_lines.append(f"{eid}\t{json.dumps(meta)}")
    print(f"git-matched {len(out_lines)-miss_git}/{len(out_lines)} (untracked→fs-fallback: {miss_git})", flush=True)
    # 3. bulk write: CSV (safe for JSON's backslashes) + \copy + ONE update join, in one psql -f session.
    import csv
    scratch = os.environ.get("CLAUDE_JOB_DIR", "/tmp")
    csvp, sqlp = os.path.join(scratch, "fm.csv"), os.path.join(scratch, "fm.sql")
    with open(csvp, "w", newline="") as fh:
        w = csv.writer(fh)
        for ln in out_lines:
            eid, meta = ln.split("\t", 1)
            w.writerow([eid, meta])
    open(sqlp, "w").write(
        "create temp table _fm(entry_id uuid, file_meta jsonb);\n"
        f"\\copy _fm from '{csvp}' with (format csv);\n"
        "update ledger.entry e set file_meta=_fm.file_meta from _fm where e.entry_id=_fm.entry_id;\n")
    r = subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                        "-v", "ON_ERROR_STOP=1", "-f", sqlp],
                       capture_output=True, text=True, env={**os.environ, "PGPASSWORD": PG["pw"]})
    print(r.stdout.strip() or r.stderr.strip()[:300])
    # 4. verify
    n = _psql("select count(*) from ledger.entry where file_meta is not null").strip()
    print(f"file_meta written: {n}")


if __name__ == "__main__":
    raise SystemExit(main())
