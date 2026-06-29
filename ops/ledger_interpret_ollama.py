#!/usr/bin/env python3
"""ops/ledger_interpret_ollama.py — LOCAL interpretive producer (kimi-k2.7-code via ollama). ZERO Claude tokens.

Companion producer to the Opus workflow: SAME v2 JSON contract, SAME scratch out/ dir, so ledger_interpret.py
`ingest` absorbs its output identically. Drives the bulk of the interpretive pass on the Company's own model
(kimi-k2.7-code:cloud) off the Claude session limit — Opus is reserved for the biggest/most-complex files.

v2 contract (vs v1): NO "uniquely" (atomic can't know it — `contribution` is neutral, file-local); ADDS the
per-symbol layer (does + description for each deterministic symbol) and the self-extending fields
(suggested_fields, proposed_edge_kinds). Producer-agnostic: the same prompt/contract is what a Codex pack uses.

Run:  python3 ops/ledger_interpret_ollama.py --wave build-prep/the-one-system/interpret/wave-NNN [--concurrency 4]
"""
from __future__ import annotations
import argparse, glob, json, os, re, subprocess, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLLAMA = os.environ.get("COMPANY_OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.environ.get("COMPANY_INTERP_MODEL", "kimi-k2.7-code:cloud")
PGCONF = {"host": os.environ.get("COMPANY_LEDGER_PGHOST", "127.0.0.1"),
          "port": os.environ.get("COMPANY_LEDGER_PGPORT", "15432"),
          "user": os.environ.get("COMPANY_LEDGER_PGUSER", "postgres"),
          "db": os.environ.get("COMPANY_LEDGER_PGDB", "postgres"),
          "pw": os.environ.get("COMPANY_LEDGER_PGPASSWORD", "postgres")}
# NO truncation (Tim 2026-06-29): a cap makes an oversize read SILENT and STATIC. Send the WHOLE file; if it
# exceeds the model's context the call FAILS LOUD (recorded as a fail) — visible + recoverable, never partial.


def _symbols_for(project: str, path: str) -> list:
    """The deterministic symbols of this file (code_id, name, kind, signature, line) — so the model describes
    each. Read from the ledger's latest run for that project."""
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    sql = ("select sy.code_id||'\t'||sy.name||'\t'||coalesce(sy.symbol_kind,'')||'\t'||coalesce(sy.signature,'') "
           "from ledger.symbol sy join ledger.latest_run r using(run_id) "
           f"where r.project=$q${project}$q$ and sy.parent_path=$q${path}$q$ order by sy.line_start limit 120")
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", PGCONF["db"], "-tA", "-F", "\t", "-c", sql], capture_output=True, text=True, env=env)
    out = []
    for ln in r.stdout.splitlines():
        parts = ln.split("\t")
        if len(parts) >= 2:
            out.append({"code_id": parts[0], "name": parts[1], "kind": parts[2] if len(parts) > 2 else "",
                        "signature": parts[3] if len(parts) > 3 else ""})
    return out


def _prompt(project: str, path: str, src: str, symbols: list) -> str:
    symlist = "\n".join(f"  - {s['code_id']} | {s['kind']} | {s['signature'] or s['name']}" for s in symbols[:120])
    sympart = (f"\n\nThis file's DETERMINISTIC SYMBOLS (describe EACH in the symbols[] output, keyed by code_id):\n{symlist}"
               if symbols else "\n\n(No code symbols in this file — symbols[] = [].)")
    return f"""You add the INTERPRETIVE layer for a ledger of code/design substrates. NEUTRAL, file-local, NO ranking.

FILE: {project}/{path}
--- BEGIN FILE ---
{src}
--- END FILE ---{sympart}

Output ONE JSON object, nothing else (no markdown fence, no prose). EXACT keys:
{{"project":"{project}","path":"{path}","model":"{MODEL}","prompt_version":"v2-full",
 "what_it_does":"<plain factual: what THIS file does, as the content shows>",
 "observations":["<notable things actually in this file>"],
 "standouts":["<the few most signal things, or []>"],
 "conventions":["<patterns it follows or breaks>"],
 "concerns":["<file-local smells only; or []>"],
 "notes":"<one-line 'if briefing someone on this file' remark>",
 "questions":["<unclear FROM THIS FILE ALONE, as questions; or []>"],
 "purpose_vs_actual":"<does stated purpose match what it does? or 'n/a'>",
 "apparent_themes":["<themes/principles it embodies>"],
 "intention_signals":"<what it seems to be TRYING to do / the idea behind it — inferred>",
 "novelty":"<what's distinct/unusual here, or 'n/a'>",
 "contribution":"<NEUTRAL: what this file contributes that a fused system would KEEP. Fusion has no winner — describe the contribution, never rank, never say better/canonical/basis.>",
 "summary_for_embedding":"<one dense factual sentence — 'what is this'>",
 "intention_for_embedding":"<one sentence — 'what was this for'>",
 "suggested_fields":["<a ledger FIELD that 'wants to exist' you couldn't place a fact into; or []>"],
 "proposed_edge_kinds":["<a relationship kind not captured by imports/calls/references/contains/extends; or []>"],
 "symbols":[{{"code_id":"<exact code_id from the list>","does":"<factual one-line>","description":"<richer 1-3 sentence read of this symbol>"}}]}}

RULES: describe only what's in the file; NO cross-file claims (duplication/clusters/which-wins are computed later by query); NEVER ranking words; tight arrays; VALID JSON ONLY (double quotes, no trailing commas)."""


def _call_ollama(prompt: str) -> str:
    body = json.dumps({"model": MODEL, "prompt": prompt, "stream": False,
                       "options": {"temperature": 0.2}, "format": "json"}).encode()
    req = urllib.request.Request(f"{OLLAMA}/api/generate", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.loads(r.read().decode())["response"]


def _extract_json(text: str) -> dict | None:
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    m = re.search(r"\{.*\}", text, re.S)   # salvage the outermost object
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            return None
    return None


def process_one(item: dict, out_dir: str) -> tuple[str, bool, str]:
    proj, path, root = item["project"], item["path"], item["root"]
    out_path = os.path.join(out_dir, proj, path + ".json")
    if os.path.exists(out_path):
        return path, True, "exists"
    abs_path = os.path.join(root, path)
    try:
        with open(abs_path, "rb") as f:
            raw = f.read()
        src = raw.decode("utf-8", errors="replace")
    except Exception as e:
        return path, False, f"read:{e}"
    syms = _symbols_for(proj, path)
    try:
        resp = _call_ollama(_prompt(proj, path, src, syms))
    except Exception as e:
        return path, False, f"ollama:{e}"
    rec = _extract_json(resp)
    if not rec or not rec.get("what_it_does"):
        return path, False, "bad-json"
    rec["project"], rec["path"] = proj, path           # enforce identity (don't trust the model)
    rec.setdefault("model", MODEL); rec.setdefault("prompt_version", "v2-full")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(rec, f)
    return path, True, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", required=True)
    ap.add_argument("--concurrency", type=int, default=4)
    a = ap.parse_args()
    items = []
    for bf in sorted(glob.glob(os.path.join(a.wave, "alloc", "batch-*.json"))):
        items.extend(json.load(open(bf)))
    out_dir = os.path.join(a.wave, "out")
    os.makedirs(out_dir, exist_ok=True)
    ok = fail = skip = 0
    fails = []
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = {ex.submit(process_one, it, out_dir): it for it in items}
        for fut in as_completed(futs):
            path, good, why = fut.result()
            if good and why == "exists":
                skip += 1
            elif good:
                ok += 1
            else:
                fail += 1; fails.append(f"{path}: {why}")
            if (ok + fail + skip) % 25 == 0:
                print(f"  {ok+fail+skip}/{len(items)}  ok={ok} fail={fail} skip={skip}", flush=True)
    print(json.dumps({"wave": a.wave, "model": MODEL, "total": len(items), "ok": ok, "fail": fail,
                      "skip": skip, "fails": fails[:20]}, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
