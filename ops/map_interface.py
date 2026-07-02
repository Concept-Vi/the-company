#!/usr/bin/env python3
"""ops/map_interface.py — the ③ MAPPING WAVE (WORLD-INTERFACE-CHARTER step 1), run through the Company's
own model layer (kimi-cloud via ollama — zero GPU, the interpret-producer pattern, REUSE-DON'T-FORK).

Maps the existing interface bones BEFORE the design wave imagines their replacement: every file of the two
front-ends + the projection/scale engine gets a pointed, bounded mapping read → structured JSON per file →
a synthesis doc. Per the model-envelope law (deterministic-work-to-code): the model is asked POINTED
questions about ONE file at a time, never open-exhaustive-over-large; oversize files get the ledger's
symbol inventory + head slice instead of a truncated dump (never silent truncation).

Output: build-prep/the-one-system/interface-map/out/<path>.json  (+ MAP-SYNTHESIS input)
Run:    .venv/bin/python ops/map_interface.py [--limit N] [--concurrency 4]
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "ops"))
import ledger_interpret_ollama as _lio  # noqa: E402 — the ONE ollama pipeline home
_call_ollama, _extract_json, PGCONF = _lio._call_ollama, _lio._extract_json, _lio.PGCONF

OUT = os.path.join(REPO, "build-prep", "the-one-system", "interface-map", "out")
MODEL = os.environ.get("MAP_MODEL", "kimi-k2.7-code:cloud")
_lio.MODEL = MODEL                     # the shared pipeline calls whatever this names (kimi-cloud default)
MAX_WHOLE = 90_000            # chars — above this, map from the symbol inventory + head (never truncate silently)

# The mapping targets (the charter's mapping-wave scope): the two FE apps + the engine + the live seams.
TARGET_SQL = """
select e.path from ledger.entry_latest e
where e.project='company' and e.node_type='file'
  and e.ext in ('.py','.ts','.tsx','.js','.jsx','.css')
  and (e.path like 'canvas/app/src/%' or e.path like 'surface/app/src/%'
       or e.path like 'surface/app/public/gallery/%'
       or e.path in ('runtime/projection.py','runtime/scale.py','runtime/bridge.py'))
  and coalesce(e.coverage_state,'') <> 'excluded'
order by e.path
"""

PROMPT = """You are mapping ONE file of an interface codebase that will be REDESIGNED (its concepts kept,
its form rebuilt). Nothing here is in active use; nothing owes compatibility. Map what IS, precisely —
your map feeds the redesign. Answer ONLY from the file content (and the symbol inventory if given).

Return STRICT JSON (no markdown, no commentary) with exactly these fields:
{"role": "<one sentence: what this file IS in the interface architecture>",
 "capabilities": ["<each real capability/feature implemented here, short>"],
 "substance": "substantial|partial|placeholder",
 "substance_why": "<one sentence of evidence>",
 "interactions_present": ["<user interactions actually wired>"],
 "interactions_missing": ["<obvious gaps/stubs/TODOs in interaction>"],
 "performance_risks": ["<concrete perf hazards visible in the code, if any>"],
 "reuse_verdict": "keep|adapt|replace",
 "reuse_why": "<one sentence>",
 "decomposition_hints": ["<if this file should split, along which seams>"]}

FILE: {path}
{body}"""


def _psql(sql: str) -> str:
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    return subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                           "-d", PGCONF["db"], "-tAc", sql], capture_output=True, text=True, env=env).stdout


def _body_for(path: str) -> tuple[str, str]:
    """(body, mode) — the whole file when it fits; else the ledger symbol inventory + a head slice
    (bounded + pointed, never a silent truncation — the mode is recorded in the output)."""
    ap = os.path.join(REPO, path)
    src = open(ap, errors="replace").read()
    if len(src) <= MAX_WHOLE:
        return f"--- CONTENT ---\n{src}", "whole"
    symbols = _psql(
        "select coalesce(symbol_kind,'?')||' '||name||' (lines '||coalesce(line_start,0)||'-'||coalesce(line_end,0)||')' "
        f"from ledger.symbol_latest where parent_path=$q${path}$q$ order by line_start limit 400")
    return (f"--- FILE TOO LARGE ({len(src)} chars) — SYMBOL INVENTORY (from the ledger) + HEAD ---\n"
            f"SYMBOLS:\n{symbols}\n--- HEAD (first {MAX_WHOLE // 3} chars) ---\n{src[:MAX_WHOLE // 3]}"), "symbols+head"


def map_one(path: str) -> tuple[str, bool, str]:
    out_path = os.path.join(OUT, path + ".json")
    if os.path.exists(out_path):
        return path, True, "exists"
    try:
        body, mode = _body_for(path)
        raw = _call_ollama(PROMPT.replace("{path}", path).replace("{body}", body))
        rec = _extract_json(raw)
        if not isinstance(rec, dict) or "reuse_verdict" not in rec:
            return path, False, "bad-json"
        rec["_path"], rec["_mode"], rec["_model"] = path, mode, MODEL
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        json.dump(rec, open(out_path, "w"), indent=1)
        return path, True, "ok"
    except Exception as e:  # recorded per file, never silently dropped
        return path, False, f"{type(e).__name__}: {str(e)[:120]}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--concurrency", type=int, default=4)
    a = ap.parse_args()
    paths = [p for p in _psql(TARGET_SQL).splitlines() if p and os.path.isfile(os.path.join(REPO, p))]
    if a.limit:
        paths = paths[:a.limit]
    os.makedirs(OUT, exist_ok=True)
    print(f"mapping {len(paths)} interface files via {MODEL}", flush=True)
    ok = fail = skip = 0
    fails = []
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = [ex.submit(map_one, p) for p in paths]
        for f in as_completed(futs):
            p, good, why = f.result()
            if good and why == "exists":
                skip += 1
            elif good:
                ok += 1
            else:
                fail += 1
                fails.append(f"{p}: {why}")
            if (ok + fail + skip) % 25 == 0:
                print(f"  {ok + fail + skip}/{len(paths)} ok={ok} fail={fail} skip={skip}", flush=True)
    print(json.dumps({"total": len(paths), "ok": ok, "fail": fail, "skip": skip, "fails": fails}, indent=1), flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
