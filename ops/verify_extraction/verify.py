#!/usr/bin/env python3
"""verify.py — repeatable, reliable extraction-completeness verifier for the ledger.

Ground-truths every code file's symbols against a REAL parse tree — python `ast` for .py, the TypeScript
compiler API (via ts_symbols.js) for js/jsx/ts/tsx — and set-diffs the result against `ledger.symbol`.
So it reports, per language and per file, exactly which function-like symbols the deterministic extractor
genuinely MISSED. This is the trustworthy counterpart to the 4B coverage-audit dragnet, which was shown to
over-flag where extraction works (py) and only be reliable where it is blind (jsx): see
build-prep/the-one-system/DETERMINISTIC-PASS-GAP-ANALYSIS.md.

Compares LEAF names (last dotted component) as sets — conservative: it will not invent misses, and may
slightly UNDER-count (a same-leaf-name symbol masks a miss; exotic component patterns undercounted). So the
per-language miss counts are a reliable FLOOR, not a ceiling.

Usage:
  python ops/verify_extraction/verify.py                       # company, per-language summary
  python ops/verify_extraction/verify.py --list-misses         # + per-file miss lists
  python ops/verify_extraction/verify.py --project claude-ds
"""
from __future__ import annotations
import argparse, ast, json, os, subprocess, collections

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HERE = os.path.dirname(os.path.abspath(__file__))
PG = ["psql", "-h", "127.0.0.1", "-p", "15432", "-U", "postgres", "-d", "postgres", "-tAc"]


def psql(sql: str) -> str:
    return subprocess.run(PG + [sql], capture_output=True, text=True,
                          env={**os.environ, "PGPASSWORD": "postgres"}).stdout


def find_typescript() -> str | None:
    for d in ("canvas/app", "surface/app", "recollection"):
        p = os.path.join(REPO, d, "node_modules")
        if os.path.isdir(os.path.join(p, "typescript")):
            return p
    return None


def py_leaf_names(path: str) -> set | None:
    try:
        tree = ast.parse(open(path, errors="replace").read())
    except Exception:
        return None  # unparseable — report separately, never silently pass
    return {n.name for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))}


def frontend_leaf_names(paths: list, tsmods: str) -> dict:
    proc = subprocess.run(["node", os.path.join(HERE, "ts_symbols.js"), tsmods],
                          input="\n".join(paths), capture_output=True, text=True)
    res = {}
    for line in proc.stdout.splitlines():
        try:
            d = json.loads(line)
        except Exception:
            continue
        res[d["file"]] = {x.split(".")[-1] for x in d.get("names", [])}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="company")
    ap.add_argument("--list-misses", action="store_true")
    a = ap.parse_args()

    # ledger leaf-names per file (the kinds the extractor stores)
    led = collections.defaultdict(set)
    for l in psql(f"select parent_path||chr(9)||name from ledger.symbol_latest s "
                  f"join ledger.entry_latest e on e.path=s.parent_path and e.project='{a.project}' "
                  f"where s.symbol_kind in ('function','method','component','class','type')").splitlines():
        if chr(9) in l:
            p, n = l.split(chr(9), 1)
            led[p].add(n.split(".")[-1])

    # EXCLUDE files the extractor deliberately did not deep-parse (coverage_state='excluded' — e.g. a
    # vendored/separate-project subtree). Counting them as "misses" is false — they were never in scope.
    files = [l for l in psql(f"select path from ledger.entry_latest where project='{a.project}' "
             f"and node_type='file' and ext in ('.py','.js','.jsx','.ts','.tsx') "
             f"and coalesce(coverage_state,'') <> 'excluded'").splitlines() if l]
    on_disk = [f for f in files if os.path.isfile(os.path.join(REPO, f))]

    tsmods = find_typescript()
    fe = [f for f in on_disk if not f.endswith(".py")]
    fe_names = frontend_leaf_names([os.path.join(REPO, f) for f in fe], tsmods) if (fe and tsmods) else {}

    # ext -> [files, complete, files_with_miss, total_misses, unparseable, void(0-ledger-but-gt>0)]
    stat = collections.defaultdict(lambda: [0, 0, 0, 0, 0, 0])
    miss_detail = collections.defaultdict(list)
    for f in on_disk:
        ext = f[f.rfind("."):]
        gt = py_leaf_names(os.path.join(REPO, f)) if ext == ".py" else fe_names.get(os.path.join(REPO, f))
        s = stat[ext]
        s[0] += 1
        if gt is None:
            s[4] += 1
            continue
        misses = gt - led.get(f, set())
        if not led.get(f) and gt:
            s[5] += 1
        if not misses:
            s[1] += 1
        else:
            s[2] += 1
            s[3] += len(misses)
            miss_detail[f] = sorted(misses)

    print(f"project={a.project}  typescript={'found' if tsmods else 'MISSING (frontend skipped)'}\n")
    print(f"{'ext':6} {'files':>6} {'complete':>9} {'miss_files':>11} {'misses':>7} {'unparse':>8} {'void':>5}")
    for ext in sorted(stat):
        s = stat[ext]
        print(f"{ext:6} {s[0]:6} {s[1]:9} {s[2]:11} {s[3]:7} {s[4]:8} {s[5]:5}")
    print(f"\nTOTAL real function-like misses: {sum(s[3] for s in stat.values())}")

    if a.list_misses:
        print("\n=== per-file misses (ground-truth symbols absent from the ledger) ===")
        for f in sorted(miss_detail, key=lambda k: -len(miss_detail[k])):
            print(f"  {f}  (+{len(miss_detail[f])}): {', '.join(miss_detail[f][:20])}")


if __name__ == "__main__":
    raise SystemExit(main())
