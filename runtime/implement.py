"""runtime/implement.py — the launch round-trip (Group W · §W1).

The connector's external surface: turn a work instruction into a *governed, launched,
verified* implementation job by running Claude Code headlessly and capturing a STRUCTURED
result (changed files / success / summary) — never scraped text.

This is a thin, testable unit. It does ONE thing: spawn `claude -p`, capture the JSON
result + stderr + exit, and return a result dict. Governance (who may dispatch), exactly-once
(the `decision.dispatch` event), verification (W3) and closure (W4) all live in suite.py — this
file is just the channel.

Design (from the plan-reviewed Synthesis Round 2 + Guide §W1):
  - Invocation: `claude -p "<instruction>" --output-format json --add-dir <repo>
    --permission-mode plan` — start read-only/safe (`plan`); graduate to `acceptEdits`
    ONLY behind a config flag (PERMISSION_MODE), after governance + the round-trip are proven.
  - Result: structured JSON. Caller learns finished / success / changed files / summary.
  - FAIL LOUD on non-JSON output (a non-JSON stdout is an unparseable result — never pretend
    success). Capture stderr + exit code.
  - Bounded wall-clock timeout (a config CONSTANT — never relayed to Tim as a duration).
  - Injectable / dry-run: a `runner` callable can be supplied so tests don't burn a real
    session every run; the DEFAULT runner is the real subprocess, so the path supports a real
    round-trip end-to-end (W1's verification).
  - Ground truth for changed files is `git diff` over the repo (not the model's self-report),
    so W4's scope-diff can't be fooled by an inaccurate JSON summary — also injectable.
"""
from __future__ import annotations

import json
import os
import subprocess


# --- config constants (NOT time estimates relayed to Tim — internal wall-clock ceilings) ---
DEFAULT_TIMEOUT_S = 900                 # subprocess wall-clock ceiling (a fixed cap, fail loud past it)
PERMISSION_MODE = os.environ.get("COMPANY_WIRE_PERMISSION", "plan")  # plan | acceptEdits — graduate via env flag
CONCURRENCY_CAP = int(os.environ.get("COMPANY_WIRE_CONCURRENCY", "3"))  # W7: max concurrent claude -p
CLAUDE_BIN = os.environ.get("COMPANY_CLAUDE_BIN", "claude")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class LaunchError(RuntimeError):
    """A dispatch failed loud: non-JSON output, a timeout, a crash, a non-zero exit with no
    parseable result. NEVER swallowed — W7 turns this into a loud re-queue, never a silent no-op."""


def _git_dirty_paths(repo: str, runner) -> list[str]:
    """Every uncommitted path in the tree right now: `git diff --name-only HEAD` (tracked changes)
    + `git ls-files --others --exclude-standard` (untracked). Raw tree state — NOT a build's delta."""
    tracked = runner(["git", "-C", repo, "diff", "--name-only", "HEAD"])
    untracked = runner(["git", "-C", repo, "ls-files", "--others", "--exclude-standard"])
    paths = set()
    for chunk in (getattr(tracked, "stdout", "") or "", getattr(untracked, "stdout", "") or ""):
        for line in chunk.splitlines():
            line = line.strip()
            if line:
                paths.add(line)
    return sorted(paths)


def _content_snapshot(repo: str, paths: list[str]) -> dict:
    """A content fingerprint (path → sha256 | None-if-absent) of the given paths — so the delta
    measures what a build actually CHANGED, not merely what is dirty. This closes the dangerous
    false-negative: a build that edits an ALREADY-DIRTY file (in both before/after path sets) is
    caught because its CONTENT hash moved, where a path-set delta would silently drop it."""
    import hashlib
    snap = {}
    for p in paths:
        full = os.path.join(repo, p)
        try:
            with open(full, "rb") as f:
                snap[p] = hashlib.sha256(f.read()).hexdigest()
        except (FileNotFoundError, IsADirectoryError, OSError):
            snap[p] = None
    return snap


def changed_delta(repo: str = REPO_ROOT, *, before: dict, runner=None) -> list[str]:
    """Ground truth for what a BUILD actually changed (W4 scope-diff source): compare a content
    snapshot taken AFTER the run against the `before` snapshot captured at dispatch time. A path is
    in the delta if its content hash moved (incl. created/deleted) OR it is newly dirty/untracked.
    This rests on the repo's own record across the run, NOT the model's JSON self-report, and is
    correct on a DIRTY tree (other lanes' pre-existing changes are in `before` too, so they cancel).
    `runner` injectable for tests."""
    run = runner or (lambda args: subprocess.run(
        args, cwd=repo, capture_output=True, text=True, check=False))
    after_paths = _git_dirty_paths(repo, run)
    # union of before+after paths, so a build that REVERTED a file (present before, gone after) shows.
    universe = sorted(set(after_paths) | set(before.keys()))
    after = _content_snapshot(repo, universe)
    return sorted(p for p in universe if before.get(p) != after.get(p))


def baseline_snapshot(repo: str = REPO_ROOT, runner=None) -> dict:
    """Capture the pre-build content baseline (the dirty paths' content hashes) so changed_delta can
    measure only THIS build's change. Taken in launch() immediately before the runner fires."""
    run = runner or (lambda args: subprocess.run(
        args, cwd=repo, capture_output=True, text=True, check=False))
    return _content_snapshot(repo, _git_dirty_paths(repo, run))


def build_instruction(decision: dict) -> str:
    """Build the work instruction from the recorded decision (its payload). The decision IS the
    authorization (W2) and carries the declared scope (W4) — the instruction tells Claude Code
    WHAT to build and WHERE it is allowed to touch, so a well-behaved run stays in scope."""
    payload = decision.get("payload", {}) if isinstance(decision, dict) else {}
    spec = payload.get("spec") or payload.get("instruction") or payload.get("why") or ""
    scope = payload.get("scope") or payload.get("target_scope") or []
    scope_line = ""
    if scope:
        scope_line = ("\n\nYou are authorized to change ONLY these paths (the operator approved "
                      "exactly this scope): " + ", ".join(scope) +
                      ". Do NOT touch anything outside that scope.")
    return (f"Implement the following approved change in the 'company' repo. "
            f"Read AGENTS.md / MAP.md / STATE.md first.\n\n{spec}{scope_line}")


def _default_runner(instruction: str, *, repo: str, permission_mode: str, timeout_s: int) -> dict:
    """The REAL round-trip: spawn `claude -p ... --output-format json`, parse JSON, fail loud on
    non-JSON / timeout / crash. Returns the structured result dict the launcher contract expects."""
    cmd = [CLAUDE_BIN, "-p", instruction, "--output-format", "json",
           "--add-dir", repo, "--permission-mode", permission_mode]
    try:
        proc = subprocess.run(cmd, cwd=repo, capture_output=True, text=True, timeout=timeout_s)
    except subprocess.TimeoutExpired as e:
        raise LaunchError(
            f"claude -p exceeded the {timeout_s}s wall-clock cap (fail loud, re-queue) — "
            f"stderr: {(e.stderr or '')[:500]!r}") from e
    except FileNotFoundError as e:
        raise LaunchError(f"claude binary {CLAUDE_BIN!r} not found — cannot dispatch (fail loud)") from e
    if not proc.stdout.strip():
        raise LaunchError(f"claude -p produced NO stdout (exit={proc.returncode}); "
                          f"stderr: {proc.stderr[:500]!r} — non-JSON, fail loud")
    try:
        parsed = json.loads(proc.stdout)
    except json.JSONDecodeError as e:
        raise LaunchError(
            f"claude -p stdout was NOT valid JSON (exit={proc.returncode}) — refusing to pretend "
            f"success; first 500 chars: {proc.stdout[:500]!r}; stderr: {proc.stderr[:300]!r}") from e
    # The CLI's JSON wrapper carries is_error / result / subtype; normalize to the launcher contract.
    is_error = bool(parsed.get("is_error")) or proc.returncode != 0
    summary = parsed.get("result") or parsed.get("summary") or ""
    return {
        "finished": True,
        "success": not is_error,
        "exit_code": proc.returncode,
        "summary": summary if isinstance(summary, str) else json.dumps(summary),
        "raw": parsed,
        "stderr": proc.stderr[:2000],
    }


def launch(decision: dict, *, repo: str = REPO_ROOT, permission_mode: str | None = None,
           timeout_s: int = DEFAULT_TIMEOUT_S, runner=None, diff_runner=None) -> dict:
    """Run one implementation job from a recorded decision (W1).

    Sequence: build instruction → spawn (bounded) → parse JSON → snapshot the ACTUAL changed
    paths from git → return a result dict for W3 (verify) / W4 (close-or-surface) / W5 (record).

    `runner(instruction, *, repo, permission_mode, timeout_s) -> result-dict` is INJECTABLE so
    tests can supply a deterministic result (dry-run) without burning a real session; the DEFAULT
    is the real `claude -p` subprocess, so the path supports a real round-trip. FAILS LOUD
    (LaunchError) on a bad round-trip — never returns a fabricated success.

    Returns: {finished, success, exit_code, summary, changed_files, permission_mode, ...}.
    Note: changed_files is GIT ground truth (not the model's self-report) — W4's scope-diff
    rests on the repo's own record.
    """
    mode = permission_mode or PERMISSION_MODE
    run = runner or _default_runner
    instruction = build_instruction(decision)
    # Capture the pre-build content baseline FIRST (the tree may already be dirty — other lanes,
    # prior edits). changed_delta then measures ONLY what this run changed, correct on a dirty tree.
    before = baseline_snapshot(repo=repo, runner=diff_runner)
    result = run(instruction, repo=repo, permission_mode=mode, timeout_s=timeout_s)
    if not isinstance(result, dict):
        raise LaunchError(f"launch runner returned {type(result).__name__}, expected a result dict — "
                          f"fail loud (no fabricated success)")
    # ACTUAL changed paths = the content delta across the run (ground truth, not the model's JSON
    # self-report). A `plan`-mode run changes nothing → empty delta → W4's scope-diff has nothing to
    # chew; a real change-making run needs acceptEdits. A test may inject changed_files to bypass git.
    result.setdefault("changed_files", changed_delta(repo=repo, before=before, runner=diff_runner))
    result["permission_mode"] = mode
    return result
