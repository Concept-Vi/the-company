#!/usr/bin/env python3
"""ops/ledger_interpret_codex.py — Codex interpretive producer (ChatGPT plan, off the Claude limit).

Third producer in the producer-agnostic pipeline (beside Opus-workflow + kimi-ollama): SAME v2 JSON contract,
writes to a wave out/ dir the driver's `ingest` absorbs identically. Uses `codex exec --output-last-message`
for clean JSON. Reuses the prompt + symbol-fetch + json-extraction from ledger_interpret_ollama (one contract).

Lane: by default works a single PROJECT (e.g. counterpart-design) so it doesn't collide with the kimi driver
working `company`. Idempotent anyway (ingest is last-wins), so overlap wastes a call, never corrupts.

Run:  python3 ops/ledger_interpret_codex.py --project counterpart-design --limit 200 [--concurrency 2]
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)
from ops.ledger_interpret_ollama import _prompt, _symbols_for, _extract_json, PGCONF, MAX_FILE_CHARS  # one contract


def _resolve_codex() -> str:
    """Resolve the codex binary through the SOURCE REGISTRY (the platform's executable_locator) — so this
    producer is a genuine registry CONSUMER, not a hardcoded path. Falls back to PATH if the registry/row
    isn't importable (e.g. a trimmed checkout), fail-loud if neither finds it."""
    try:
        from introspection.platforms import PlatformRegistry
        from introspection import discover as _D
        return _D.resolve_executable(PlatformRegistry().discover(["platforms"]).get("codex-cli"))
    except Exception:
        import shutil
        exe = shutil.which("codex")
        if not exe:
            raise RuntimeError("codex not resolvable via registry or PATH — install/login codex first")
        return exe


CODEX = _resolve_codex()
PROJECT_ROOTS = {"company": REPO, "counterpart-design": "/home/tim/repos/counterpart/design",
                 "claude-ds": os.path.join(REPO, "design", "claude-ds")}
WAVE_DIR = os.path.join(REPO, "build-prep", "the-one-system", "interpret", "wave-codex")


def _todo(project: str, limit: int) -> list:
    env = {**os.environ, "PGPASSWORD": PGCONF["pw"]}
    sql = (f"select e.path from ledger.entry e join ledger.latest_run r using(run_id) "
           f"where r.project=$q${project}$q$ and e.node_type='file' and e.coverage_state='deterministic' "
           f"and e.what_it_does is null order by e.path limit {int(limit)}")
    r = subprocess.run(["psql", "-h", PGCONF["host"], "-p", PGCONF["port"], "-U", PGCONF["user"],
                        "-d", PGCONF["db"], "-tAc", sql], capture_output=True, text=True, env=env)
    return [ln for ln in r.stdout.splitlines() if ln]


def process_one(project: str, path: str) -> tuple[str, bool, str]:
    root = PROJECT_ROOTS[project]
    out_path = os.path.join(WAVE_DIR, "out", project, path + ".json")
    if os.path.exists(out_path):
        return path, True, "exists"
    try:
        with open(os.path.join(root, path), "rb") as f:
            raw = f.read()
        src = raw.decode("utf-8", errors="replace")
    except Exception as e:
        return path, False, f"read:{e}"
    truncated = len(src) > MAX_FILE_CHARS
    if truncated:
        src = src[:MAX_FILE_CHARS]
    syms = _symbols_for(project, path)
    prompt = _prompt(project, path, src, truncated, syms) + "\n\nOutput ONLY the JSON object."
    with tempfile.TemporaryDirectory() as td:
        last = os.path.join(td, "last.txt")
        try:
            r = subprocess.run([CODEX, "exec", "--skip-git-repo-check", "-o", last, "-"],
                               input=prompt, capture_output=True, text=True, timeout=300,
                               cwd=td, env={**os.environ, "PATH": os.environ.get("PATH", "")})
        except subprocess.TimeoutExpired:
            return path, False, "codex-timeout"
        text = ""
        if os.path.exists(last):
            text = open(last).read()
        if not text:
            text = r.stdout
    rec = _extract_json(text)
    if not rec or not rec.get("what_it_does"):
        return path, False, "bad-json"
    rec["project"], rec["path"] = project, path
    rec["model"] = "codex"; rec["prompt_version"] = "v2-full"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(rec, f)
    return path, True, "ok"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", default="counterpart-design")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--concurrency", type=int, default=2)
    a = ap.parse_args()
    paths = _todo(a.project, a.limit)
    os.makedirs(os.path.join(WAVE_DIR, "out"), exist_ok=True)
    print(f"codex producer: {len(paths)} files from {a.project}", flush=True)
    ok = fail = skip = 0; fails = []
    with ThreadPoolExecutor(max_workers=a.concurrency) as ex:
        futs = {ex.submit(process_one, a.project, p): p for p in paths}
        for fut in as_completed(futs):
            path, good, why = fut.result()
            if good and why == "exists": skip += 1
            elif good: ok += 1
            else: fail += 1; fails.append(f"{path}: {why}")
            if (ok+fail+skip) % 10 == 0:
                print(f"  {ok+fail+skip}/{len(paths)} ok={ok} fail={fail}", flush=True)
    print(json.dumps({"project": a.project, "ok": ok, "fail": fail, "skip": skip, "fails": fails[:15]}, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
