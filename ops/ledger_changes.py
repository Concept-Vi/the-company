#!/usr/bin/env python3
"""ops/ledger_changes.py — the change-detection FORM (Tim 2026-06-29).

"What has changed or been added since the last ingestion?" — so passes can be re-run on ONLY the new/changed
files (paired with carry-forward, which keeps the interpretation of the unchanged). Compares the current tree
against the ledger's recorded per-file source_hash (the ingestion fingerprint):
  • added     — in the tree now, not in the ledger
  • changed   — present in both, hash differs
  • deleted   — in the ledger, gone from the tree
  • unchanged — same hash (carry forward — do NOT re-run)

Deterministic, no model, GPU-free. A standing Company operation (reflects into ops): run it any time to see
drift; feed added+changed into a selective re-extract + re-interpret. NO confidence — just sets + counts.

Run:
  python3 ops/ledger_changes.py --project company
  python3 ops/ledger_changes.py --all
  python3 ops/ledger_changes.py --all --emit build-prep/the-one-system/interpret/changes.json
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from ops.ledger_build import enumerate_files, _read, EXCLUDE_PREFIXES, _psql

PROJECT_ROOTS = {"company": REPO, "counterpart-design": "/home/tim/repos/counterpart/design",
                 "claude-ds": os.path.join(REPO, "design", "claude-ds")}


def _ledger_hashes(project: str) -> dict:
    """{rel_path: source_hash} from the project's LATEST run (latest_run is one row per project — no purpose
    filter; the run's purpose is 'one-system-ledger', NOT the per-entry coverage_state)."""
    rid = _psql(f"select run_id from ledger.latest_run where project=$q${project}$q$").strip()
    if not rid:
        return {}
    out = _psql(f"select path||chr(31)||coalesce(source_hash,'') from ledger.entry "
                f"where run_id=$q${rid}$q$ and node_type='file'")
    h = {}
    for ln in out.splitlines():
        if chr(31) in ln:
            p, hsh = ln.split(chr(31), 1)
            h[p] = hsh
    return h


import re as _re
# data-artifact predicate — mirrors the exclusion classifier. We DON'T read/hash these (lean: avoids hashing
# the 45MB dump + thousands of archive files, which helped wedge Docker twice). They hash to '' like the ledger.
_DATA_EXT = (".jsonl", ".ndjson")
_DATA_PATH = _re.compile(r"migration-pending/wizard-run|channel-memory/scans/|\.temp/pgdelta|catalog-local-migrations"
                         r"|build-prep/the-one-system/interpret/|build-prep/the-one-system/discovery/")


def _is_data_artifact(rel: str) -> bool:
    return rel.endswith(_DATA_EXT) or bool(_DATA_PATH.search(rel))


def _current_hashes(root: str, exclude_prefixes: tuple) -> dict:
    """{rel_path: sha256} over the tree at `root` NOW — mirrors ledger_build.current_hashes (excluded → '').
    Skips reading excluded prefixes AND data artifacts (lean — never reads the big data dumps)."""
    files, _ = enumerate_files(root)
    h = {}
    for rec in files:
        rel = rec["rel_path"]
        if any(rel.startswith(p) for p in exclude_prefixes) or _is_data_artifact(rel):
            h[rel] = ""
            continue
        src, raw = _read(rec["abs_path"], rel)
        h[rel] = "" if src is None else hashlib.sha256(raw).hexdigest()
    return h


def detect(project: str, purpose: str = "") -> dict:
    prev = _ledger_hashes(project)
    root = PROJECT_ROOTS.get(project, REPO)
    # company applies its scratch/data/claude-ds exclusions; the other roots have their files at top level.
    excl = tuple(p for p, _ in EXCLUDE_PREFIXES) if project == "company" else ()
    cur = _current_hashes(root, excl)
    # only report IN-SCOPE (interpretable) files — data artifacts + excluded prefixes (.recollection churn,
    # scratch) are not re-run targets, so their constant turnover is noise, not signal.
    def in_scope(p: str) -> bool:
        return not _is_data_artifact(p) and not any(p.startswith(x) for x in excl)
    added = sorted(p for p in cur if p not in prev and in_scope(p))
    deleted = sorted(p for p in prev if p not in cur and in_scope(p))
    changed = sorted(p for p in cur if p in prev and cur[p] != prev[p] and cur[p] and prev[p] and in_scope(p))
    unchanged = sum(1 for p in cur if p in prev and cur[p] == prev[p])
    return {"project": project, "root": root,
            "counts": {"added": len(added), "changed": len(changed), "deleted": len(deleted),
                       "unchanged": unchanged, "ledger_total": len(prev), "tree_total": len(cur)},
            "added": added, "changed": changed, "deleted": deleted}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--purpose", default="deterministic")
    ap.add_argument("--emit", default="")
    ap.add_argument("--show", type=int, default=15, help="how many paths to print per bucket")
    a = ap.parse_args()
    projects = list(PROJECT_ROOTS) if a.all else ([a.project] if a.project else [])
    if not projects:
        print("need --project <id> or --all"); return 2
    forms = []
    for proj in projects:
        f = detect(proj, a.purpose)
        forms.append(f)
        c = f["counts"]
        print(f"\n=== {proj} === added={c['added']} changed={c['changed']} deleted={c['deleted']} "
              f"unchanged={c['unchanged']} (ledger {c['ledger_total']} / tree {c['tree_total']})")
        for bucket in ("added", "changed", "deleted"):
            for p in f[bucket][:a.show]:
                print(f"   [{bucket[0].upper()}] {p}")
            if len(f[bucket]) > a.show:
                print(f"   … +{len(f[bucket]) - a.show} more {bucket}")
    if a.emit:
        json.dump({"forms": forms}, open(os.path.join(REPO, a.emit), "w"), indent=1)
        print(f"\nwrote {a.emit}")
    total_dirty = sum(f["counts"]["added"] + f["counts"]["changed"] for f in forms)
    print(f"\nTOTAL needing re-run (added+changed): {total_dirty}")


if __name__ == "__main__":
    raise SystemExit(main())
