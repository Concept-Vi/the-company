#!/usr/bin/env python3
"""ops/ledger_coverage_audit.py — independent COVERAGE audit of the deterministic extraction (Tim 2026-06-29).

The deterministic extractors fail SILENTLY: if the parser misses a symbol that's plainly in the file, nothing
records the gap (F2 — JS/TS symbols — was an instance). This is the cross-check: a LOCAL 4B reads the actual
file (the answer key) + what the extractor produced, and reports what's MISSING. Aggregate → a blind-spot map
by language → fix the extractor → cheap re-run (carry-forward). The 4B here is an AUDITOR against ground truth,
never an opinion-maker.

TWO PASSES (while we work it out):
  • with-contract   — CONFORMANCE: "of what we INTEND to extract, what did we miss?"
  • without-contract — DISCOVERY:   "what's in the file worth extracting that we never specified?"
  The DIFF (without-flags the with-pass doesn't raise) = candidate NEW contract items. Read the without-pass
  at the aggregate/pattern level (noisier — nothing constrains it).

NO confidence (G16): a file's result is TAGS + COUNTS — coverage_state tag ('clean' / 'flagged' / 'oversize')
+ a count of flagged items. Never a score.

Destined to become a standing Company operation (see build-prep/the-one-system/LEDGER-ENRICHMENT-PLAN.md):
written as a reusable pass, model/endpoint = data.

Run:
  python3 ops/ledger_coverage_audit.py --sample-per-language 8 --pass with --concurrency 32
  python3 ops/ledger_coverage_audit.py --project company --pass without --concurrency 32 --limit 200
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOTS = {"company": REPO, "counterpart-design": "/home/tim/repos/counterpart/design",
                 "claude-ds": os.path.join(REPO, "design", "claude-ds")}
PG = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
      "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
      "user": "postgres", "db": "postgres", "pw": "postgres"}
MODEL_URL = os.environ.get("COMPANY_AUDIT_URL", "http://127.0.0.1:8000/v1/chat/completions")
MODEL = os.environ.get("COMPANY_AUDIT_MODEL", "cyankiwi/Qwen3.5-4B-AWQ-4bit")
MAX_CTX = int(os.environ.get("COMPANY_AUDIT_MAX_CTX", "16384"))     # the 4B's max_model_len
CHARS_PER_TOK = 3.5                                                  # rough budget so we don't overflow ctx

# What the deterministic extractor INTENDS to capture (the contract — for the with-contract pass).
CONTRACT = ("The extractor captures, per file: every function / method / class definition (name + signature), "
            "including ones nested inside other functions or control-flow blocks; import statements; and "
            "module-level constant / dict assignments. It does NOT capture: local variables inside a function "
            "body, lambdas, comments, or string literals.")


def _psql(sql: str) -> str:
    return subprocess.run(["psql", "-h", PG["host"], "-p", PG["port"], "-U", PG["user"], "-d", PG["db"],
                           "-tAc", sql], capture_output=True, text=True,
                          env={**os.environ, "PGPASSWORD": PG["pw"]}).stdout


def _fetch_items(where: str, limit: int) -> list:
    """ONE batched query (lean — no per-file DB hammering): file + its deterministic symbols/imports."""
    sql = (
        "select json_agg(row_to_json(t)) from ("
        "  select e.project, e.path, e.language, e.size_bytes, e.ext,"
        "    coalesce(e.imports::text,'[]') imports,"
        "    coalesce((select json_agg(json_build_object('name',s.name,'kind',s.symbol_kind,'sig',s.signature) "
        "              order by s.line_start) from ledger.symbol s "
        "              where s.run_id=e.run_id and s.parent_path=e.path)::text,'[]') symbols"
        f"  from ledger.entry e join ledger.latest_run r using(run_id) where {where} limit {int(limit)}"
        ") t")
    out = _psql(sql).strip()
    return json.loads(out) if out and out != "" else []


def _sample_per_language(n: int) -> list:
    """A stratified sample: up to n interpreted files per language (the cheap first pass)."""
    langs = [l for l in _psql(
        "select distinct language from ledger.entry e join ledger.latest_run r using(run_id) "
        "where node_type='file' and language is not null and what_it_does is not null").splitlines() if l]
    items = []
    for lang in langs:
        where = (f"e.node_type='file' and e.language=$q${lang}$q$ and e.what_it_does is not null "
                 f"and e.coverage_state='deterministic'")
        items += _fetch_items(where + " order by random()", n)
    return items


def _prompt(item: dict, contract: bool) -> str:
    syms = json.loads(item["symbols"]); imps = json.loads(item["imports"])
    symlist = "\n".join(f"  - {s.get('kind','?')} {s.get('name','?')} {s.get('sig') or ''}".rstrip()
                        for s in syms) or "  (none extracted)"
    implist = ", ".join(str(i.get("target", i) if isinstance(i, dict) else i) for i in imps) or "(none)"
    root = PROJECT_ROOTS.get(item["project"], REPO)
    try:
        src = open(os.path.join(root, item["path"]), "rb").read().decode("utf-8", errors="replace")
    except Exception as e:
        return ""    # unreadable → caller skips
    budget = int(MAX_CTX * CHARS_PER_TOK) - 2500 - len(symlist)
    if len(src) > budget:                                          # too big for the 4B's window → mark oversize
        return "__OVERSIZE__"
    rule = (f"\nWhat the extractor is SUPPOSED to capture:\n{CONTRACT}\n"
            "List ONLY things that fit that contract but are missing.") if contract else (
            "\nList anything a code map should arguably contain that is missing — even kinds the current "
            "extractor may not target (you are helping us discover what to capture).")
    return f"""You audit a code/document extractor for COMPLETENESS. Below is a file and the symbols+imports the
extractor pulled from it. Compare against the ACTUAL file and report what it MISSED.{rule}

FILE: {item['project']}/{item['path']}  (language: {item.get('language')})
--- EXTRACTED SYMBOLS ---
{symlist}
--- EXTRACTED IMPORTS ---
{implist}
--- BEGIN FILE ---
{src}
--- END FILE ---

Output ONE JSON object, nothing else:
{{"missing":[{{"name":"<symbol/import in the file but NOT in the extracted lists>","kind":"<function|method|class|import|other>","line_hint":"<where, roughly>"}}],
  "notes":"<one line; or ''>"}}
If nothing is missing, output {{"missing":[],"notes":"complete"}}. Be precise — only flag things genuinely in the file and genuinely absent from the lists."""


def _call(prompt: str) -> str:
    body = json.dumps({"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                       "max_tokens": 1200, "temperature": 0}).encode()
    req = urllib.request.Request(MODEL_URL, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read())["choices"][0]["message"]["content"]


def _extract_json(text: str) -> dict | None:
    i, j = text.find("{"), text.rfind("}")
    if i < 0 or j < 0:
        return None
    try:
        return json.loads(text[i:j + 1])
    except Exception:
        return None


def audit_one(item: dict, contract: bool) -> dict:
    p = _prompt(item, contract)
    base = {"project": item["project"], "path": item["path"], "language": item.get("language")}
    if p == "":
        return {**base, "tag": "unreadable", "count": 0, "missing": []}
    if p == "__OVERSIZE__":
        return {**base, "tag": "oversize", "count": 0, "missing": []}   # honest: too big for the 4B window
    try:
        rec = _extract_json(_call(p))
    except Exception as e:
        return {**base, "tag": "error", "count": 0, "missing": [], "err": str(e)[:120]}
    if rec is None:
        return {**base, "tag": "bad-json", "count": 0, "missing": []}
    miss = [m for m in rec.get("missing", []) if isinstance(m, dict)]
    return {**base, "tag": "clean" if not miss else "flagged", "count": len(miss),
            "missing": miss, "notes": rec.get("notes", "")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample-per-language", type=int, default=0)
    ap.add_argument("--project", default="")
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--pass", dest="cpass", choices=["with", "without"], default="with")
    ap.add_argument("--concurrency", type=int, default=32)
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    contract = (a.cpass == "with")
    if a.sample_per_language:
        items = _sample_per_language(a.sample_per_language)
    elif a.project:
        items = _fetch_items(f"e.node_type='file' and e.project=$q${a.project}$q$ and e.what_it_does is not null "
                             f"and e.coverage_state='deterministic' order by e.path", a.limit)
    else:
        print("need --sample-per-language N or --project <id>"); return 2
    print(f"auditing {len(items)} files | pass={a.cpass} | concurrency={a.concurrency} | model={MODEL}", flush=True)
    results = []
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = [ex.submit(audit_one, it, contract) for it in items]
        for k, fut in enumerate(as_completed(futs), 1):
            results.append(fut.result())
            if k % 25 == 0:
                print(f"  {k}/{len(items)}", flush=True)
    # aggregate by language (tags + counts — the blind-spot map)
    by_lang = defaultdict(lambda: defaultdict(int))
    for r in results:
        by_lang[r["language"]][r["tag"]] += 1
        by_lang[r["language"]]["flagged_items"] += r["count"]
    report = {"pass": a.cpass, "model": MODEL, "n": len(results),
              "by_language": {k: dict(v) for k, v in by_lang.items()},
              "results": results}
    out = a.out or f"build-prep/the-one-system/interpret/coverage-audit-{a.cpass}.json"
    json.dump(report, open(os.path.join(REPO, out), "w"), indent=1)
    print("\n=== BLIND-SPOT MAP (tags + counts, by language) ===")
    for lang, tags in sorted(by_lang.items(), key=lambda x: -x[1].get("flagged", 0)):
        print(f"  {lang:<12} {dict(tags)}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    raise SystemExit(main())
