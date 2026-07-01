#!/usr/bin/env python3
"""ops/ledger_interpret_producer.py — the ONE source-driven interpretive producer (collapses the parallel
ledger_interpret_ollama.py + ledger_interpret_codex.py into a single backend-parameterised tool).

The duplication being killed (Tim 2026-06-28): there were 3 near-identical producers (kimi/ollama, codex,
the Opus workflow) differing only in WHICH MODEL is called. The model/backend is DATA, not a file. This
producer holds the ONE pipeline (read file + its ledger symbols → v2 prompt → model → JSON to the wave
out/ dir the ingest reads) and dispatches the model call by `--backend`:
  • ollama  — kimi-k2.7-code (or any ollama model) via the HTTP API (zero Claude tokens).
  • codex   — `codex exec` via the SOURCE REGISTRY's resolved binary (ChatGPT plan; a real registry consumer).
(The Opus path stays the Workflow fan-out — a different execution model, not a CLI producer.)

REUSE-DON'T-FORK: the prompt/symbols/json-extract/contract are imported from ledger_interpret_ollama (the
single home of the v2 contract); this module adds only the backend dispatch + the two run-modes. Same wave
out/ contract → ledger_interpret.py `ingest` absorbs it identically regardless of backend.

Run:
  python3 ops/ledger_interpret_producer.py --wave <dir> --backend ollama --concurrency 5
  python3 ops/ledger_interpret_producer.py --project counterpart-design --backend codex --limit 120 --concurrency 3
"""
from __future__ import annotations
import argparse, glob, json, os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
# the ONE v2 contract + helpers (single home — reuse, never re-spell)
from ops.ledger_interpret_ollama import (_prompt, _symbols_for, _extract_json, _call_ollama, PGCONF)

PROJECT_ROOTS = {"company": REPO, "counterpart-design": "/home/tim/repos/counterpart/design",
                 "claude-ds": os.path.join(REPO, "design", "claude-ds")}


# ── backends (the only thing that differs by model) ──────────────────────────────────────────────
def _backend_ollama(prompt: str, model: str) -> str:
    return _call_ollama(prompt)              # uses COMPANY_INTERP_MODEL / the ollama default


class TerminalBackendError(RuntimeError):
    """A backend failure that RETRYING CANNOT FIX — out of credits, expired/invalid auth, revoked key — as
    opposed to a transient rate-limit. The producer aborts the whole run LOUD on this so a driver HOLDS the
    lane (surfaces it to a human) instead of hammering a dead account forever. (Tim 2026-06-28: the codex
    lane mislabelled 'out of credits' as 'rate-limited' and infinite-backed-off, producing 120 silent
    bad-json failures per pass — fail loud, distinguish permanent from transient.)"""


# stderr/stdout signatures from the backend that mean HUMAN ACTION REQUIRED, not "wait and retry".
_CODEX_TERMINAL = ("out of credits", "add credits", "insufficient_quota", "exceeded your current quota",
                   "invalid api key", "incorrect api key", "unauthorized")


def _backend_codex(prompt: str, model: str) -> str:
    import subprocess, tempfile
    from ops.ledger_interpret_codex import _resolve_codex   # registry-resolved binary (a real consumer)
    with tempfile.TemporaryDirectory() as td:
        last = os.path.join(td, "last.txt")
        proc = subprocess.run([_resolve_codex(), "exec", "--skip-git-repo-check", "-o", last, "-"],
                              input=prompt + "\n\nOutput ONLY the JSON object.", capture_output=True,
                              text=True, timeout=300, cwd=td)
        if os.path.exists(last):
            out = open(last).read()
            if out.strip():
                return out
        # No usable output — inspect what codex actually said (previously SWALLOWED → looked like bad-json).
        diag = ((proc.stderr or "") + "\n" + (proc.stdout or "")).strip()
        low = diag.lower()
        if any(sig in low for sig in _CODEX_TERMINAL):
            tail = diag.splitlines()[-1][:200] if diag else "credits/auth"
            raise TerminalBackendError(f"codex: {tail}")
        return ""                  # transient/unknown → empty (→ bad-json → no-progress → driver backoff)


BACKENDS = {"ollama": _backend_ollama, "codex": _backend_codex}


def process_one(item: dict, out_dir: str, backend: str, model: str) -> tuple[str, bool, str]:
    proj, path, root = item["project"], item["path"], item["root"]
    out_path = os.path.join(out_dir, proj, path + ".json")
    if os.path.exists(out_path):
        return path, True, "exists"
    try:
        raw = open(os.path.join(root, path), "rb").read()
        src = raw.decode("utf-8", errors="replace")
    except Exception as e:
        return path, False, f"read:{e}"
    syms = _symbols_for(proj, path)
    try:
        resp = BACKENDS[backend](_prompt(proj, path, src, syms), model)
    except TerminalBackendError:
        raise                                    # human-action-required → abort the whole run (caught in main)
    except Exception as e:
        return path, False, f"{backend}:{e}"
    rec = _extract_json(resp)
    if not rec or not rec.get("what_it_does"):
        return path, False, "bad-json"
    rec["project"], rec["path"] = proj, path
    rec.setdefault("model", model or backend); rec.setdefault("prompt_version", "v2-full")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump(rec, open(out_path, "w"))
    return path, True, "ok"


def _items_from_wave(wave: str) -> list:
    items = []
    for bf in sorted(glob.glob(os.path.join(wave, "alloc", "batch-*.json"))):
        items.extend(json.load(open(bf)))
    return items


# the STRUCTURE exts worth interpreting — code + real docs. NOT the .json/.jsonl/.txt DATA noise (the
# ingest-boundary problem: 5650 .json data files would otherwise burn the whole model budget describing
# noise before reaching the code). An env override widens it if ever needed.
_INTERP_EXTS = os.environ.get("INTERP_EXTS", ".py,.ts,.tsx,.js,.jsx,.md,.sh,.sql,.html,.css").split(",")


def _items_from_project(project: str, limit: int) -> list:
    import subprocess
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    ext_in = ",".join(f"$q${e.strip()}$q$" for e in _INTERP_EXTS)
    sql = (f"select e.path from ledger.entry e join ledger.latest_run r using(run_id) "
           f"where r.project=$q${project}$q$ and e.node_type='file' and e.coverage_state='deterministic' "
           f"and e.ext in ({ext_in}) and e.what_it_does is null order by e.path limit {int(limit)}")
    out = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                          "-d", PGCONF["db"], "-tAc", sql], capture_output=True, text=True, env=env).stdout
    root = PROJECT_ROOTS.get(project, REPO)
    return [{"project": project, "path": p, "root": root} for p in out.splitlines() if p]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wave", default="")
    ap.add_argument("--project", default="")
    ap.add_argument("--backend", choices=list(BACKENDS), default="ollama")
    ap.add_argument("--model", default="")
    ap.add_argument("--limit", type=int, default=120)
    ap.add_argument("--concurrency", type=int, default=5)
    a = ap.parse_args()
    if a.wave:
        items, out_dir = _items_from_wave(a.wave), os.path.join(a.wave, "out")
    elif a.project:
        wd = os.path.join(REPO, "build-prep", "the-one-system", "interpret", f"wave-{a.backend}")
        items, out_dir = _items_from_project(a.project, a.limit), os.path.join(wd, "out")
    else:
        print("need --wave <dir> or --project <id>"); return 2
    os.makedirs(out_dir, exist_ok=True)
    ok = fail = skip = 0; fails = []
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = [ex.submit(process_one, it, out_dir, a.backend, a.model) for it in items]
        try:
            for fut in as_completed(futs):
                path, good, why = fut.result()
                if good and why == "exists": skip += 1
                elif good: ok += 1
                else: fail += 1; fails.append(f"{path}: {why}")
                if (ok+fail+skip) % 25 == 0:
                    print(f"  {ok+fail+skip}/{len(items)} ok={ok} fail={fail} skip={skip}", flush=True)
        except TerminalBackendError as e:
            for f in futs:
                f.cancel()
            print(json.dumps({"held": True, "backend": a.backend, "reason": str(e),
                              "note": "HUMAN ACTION REQUIRED (credits/auth) — NOT a transient rate limit. "
                                      "The lane should HOLD (stop), not backoff-retry."}, indent=2), flush=True)
            return 3
    print(json.dumps({"backend": a.backend, "total": len(items), "ok": ok, "fail": fail, "skip": skip,
                      "fails": fails}, indent=2))   # ALL fails visible — no [:15] cap (Tim: failures belong in the report, never silently dropped)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
