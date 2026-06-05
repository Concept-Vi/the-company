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
# COMPANY_WIRE_PERMISSION — the SECOND of the wire's two deliberate graduation switches (wire-bridge §3).
# The DEFAULT is "plan" (SAFE-BY-DEFAULT): a plan-mode `claude -p` run is read-only — it changes NOTHING,
# so even if the production trigger (the first switch) fires, NOTHING self-modifies. acceptEdits is OPT-IN
# ONLY, via this env var; it is NEVER the default. `permission_mode()` reads the env at CALL time (not at
# import) so a runtime `COMPANY_WIRE_PERMISSION=acceptEdits` is honoured without a process restart and a
# test can monkeypatch the env; the module-level PERMISSION_MODE remains for back-compat (the import-time
# snapshot of the default — DO NOT rely on it for the live posture, use permission_mode()).
PERMISSION_MODE = os.environ.get("COMPANY_WIRE_PERMISSION", "plan")  # plan | acceptEdits — import-time snapshot
CONCURRENCY_CAP = int(os.environ.get("COMPANY_WIRE_CONCURRENCY", "3"))  # W7: max concurrent claude -p
CLAUDE_BIN = os.environ.get("COMPANY_CLAUDE_BIN", "claude")
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def permission_mode() -> str:
    """The LIVE permission posture (call-time read of COMPANY_WIRE_PERMISSION; default "plan").
    Call-time (not the import-time PERMISSION_MODE constant) so a deliberately-set env var flips the
    posture WITHOUT a process restart, and so the safe default ("plan", read-only, no self-modify)
    holds for every run that does not OPT IN. Use this — not the constant — for the live posture."""
    return os.environ.get("COMPANY_WIRE_PERMISSION", "plan")


def wire_armed() -> bool:
    """The PRODUCTION-TRIGGER arming gate (L2): is the live loop deliberately armed to SELF-MODIFY?
    True ONLY when the operator has deliberately opted in via COMPANY_WIRE_PERMISSION=acceptEdits.

    This is the gate that keeps the resolve→dispatch production trigger INERT BY DEFAULT (🔒
    built-not-armed). With the default `plan` posture this returns False, so the trigger
    (Suite.resolve_surfaced, when an operator approves a build-intent) does NOT fire a dispatch — the
    system is SAFE-BY-DEFAULT, exactly as before L2. acceptEdits is the deliberate, env-gated opt-in
    that arms the live circuit; the lead fires the one-shot proof under it (NOT this worker). A `plan`
    posture, even if the trigger DID fire, would change nothing (read-only) — so this gate + the
    plan-default are the two layers that together guarantee no autonomous self-modification by default.

    NOTE: the wire suites (wire_loop_acceptance / wire_adversarial) call drive_dispatchable DIRECTLY
    with the env unset → wire_armed() is False → resolve_surfaced does NOT also fire, so those suites'
    single explicit dispatch stays exactly-one (no double-launch). The trigger only adds a SECOND path
    when deliberately armed."""
    return permission_mode() == "acceptEdits"


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


# The self-description files a build is ALWAYS allowed to touch (H8): H7 INSTRUCTS the build to update
# them as part of the change, so they legitimately appear in `changed_files` and must NOT read as a
# scope overrun. The factual blocks regenerate via Suite.refresh_self_description (the system's own
# write, not the build's), the prose the build updates by integration — either way these are upkeep,
# not out-of-scope wandering. The touched module's own AGENTS.md is covered by the declared scope dir.
SELF_DESCRIPTION_FILES = ("AGENTS.md", "MAP.md", "STATE.md")


# The STANDARDS the dispatched build must meet. This is NOT a self-review instruction — self-review is
# the weakest kind, and a headless `claude -p` can't drive a browser to check a surface anyway. It
# carries the BAR the work must meet (H7 — the FULL standard, so the builder INTEGRATES, not just
# writes code); the reviewing is a SEPARATE stage (a review pass + the operator via the RHM organ).
# AI-operated is NOT review-free. The wire's verify (H1/H2) ENFORCES the last two bullets after the
# build (affected acceptance suites + drift must be GREEN, or the build does not close), so this is the
# bar AND the gate, not a hope.
STANDARDS_BLOCK = (
    "\n\nThis is part of an AI-operated but REVIEWED system — it is NOT review-free. Build to this bar:\n"
    "- Any operator-facing surface this change touches or exposes MUST be built ON THE DESIGN SYSTEM "
    "(its components + design tokens — NEVER hardcoded values or bespoke one-offs) and brought to the "
    "product UI/UX bar as part of the change (a backend-only change still updates the surface that "
    "exposes it). A surface change CANNOT auto-close — it surfaces for a design review.\n"
    "- Update the self-description as part of the change: AGENTS.md / MAP.md / STATE.md and the touched "
    "module's AGENTS.md — keep them current and true (the factual blocks regenerate via "
    "Suite.refresh_self_description; the prose you update by integration). This is checked: the build "
    "does NOT close if the drift-check goes red.\n"
    "- Keep the tests + the drift-check GREEN: a build that breaks ANY affected acceptance suite (or "
    "leaves drift red) does NOT close — it surfaces back with the failing suite as the reason. So make "
    "the relevant `tests/*.py` pass and refresh the self-description as part of the change.\n"
    "- Do NOT review your own work as the final word — a SEPARATE review pass + a design-critic + the "
    "operator (via the RHM walkthrough organ) will review the result. Implement to the bar; the review "
    "is a later stage.")


def build_instruction(decision: dict) -> str:
    """Build the work instruction from the recorded decision (its payload). The decision IS the
    authorization (W2) and carries the declared scope (W4) — the instruction tells Claude Code
    WHAT to build and WHERE it is allowed to touch, so a well-behaved run stays in scope. It ALSO
    carries the STANDARDS_BLOCK: the bar the work must meet (UI/UX bar for operator-facing surfaces,
    self-description updated as part of the change, a SEPARATE review pass + the operator will review).
    It does NOT ask the build to review itself — reviewing is a separate stage (AI-operated ≠ review-free)."""
    payload = decision.get("payload", {}) if isinstance(decision, dict) else {}
    spec = payload.get("spec") or payload.get("instruction") or payload.get("why") or ""
    scope = payload.get("scope") or payload.get("target_scope") or []
    scope_line = ""
    if scope:
        scope_line = ("\n\nYou are authorized to change ONLY these paths (the operator approved "
                      "exactly this scope): " + ", ".join(scope) +
                      ". Do NOT touch anything outside that scope.")
    return (f"Implement the following approved change in the 'company' repo. "
            f"Read AGENTS.md / MAP.md / STATE.md first.\n\n{spec}{scope_line}{STANDARDS_BLOCK}")


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
    # call-time live posture (default "plan" = read-only/no self-modify) unless an explicit mode is
    # passed; permission_mode() honours a deliberately-set COMPANY_WIRE_PERMISSION without a restart.
    mode = permission_mode if permission_mode is not None else globals()["permission_mode"]()
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


# =============================================================================================
# §W6 — the UNATTENDED trigger (the watcher increment). §W7 — the concurrency cap + loud defer.
# =============================================================================================
# This is the CALLER, not the verb. The governed dispatch (`suite.dispatch_decision`) is DONE in
# suite.py (committed): seq-bind authorization, exactly-once via the per-seq lock + decision.dispatch
# event, the posture==AUTO pre-gate, the deny-all empty scope, the guarded close. This watcher reads
# DISPATCHABLE approvals from the substrate and drives them with NO human re-prompt — closing the
# circuit. It NEVER resolves (operator-only): it READS verdicts + WRITES dispatches/statuses only.
#
# Exactly-once does NOT rest on this cursor — the `decision.dispatch` event keyed on the resolve `seq`
# is the durable guarantee (suite.py:_already_dispatched). The cursor is a COARSE guard only, so a
# crash/re-fire never double-launches (dispatch_decision refuses a second). A dispatch that crashed
# mid-flight (the claim event emitted, but no terminal event) is therefore NOT silently lost — it is
# re-SURFACED loud (a dead end is a silent failure; this law forbids it), never silently re-launched.

# the terminal-event kinds dispatch_decision emits for a resolve seq (suite.py): a successful close
# (`decision.implemented`) or any non-closing outcome (`decision.verify` — verify-fail / scope-overrun
# / launch-fail re-queue). A `decision.dispatch` claim with NEITHER terminal = mid-flight or crashed.
_TERMINAL_KINDS = ("decision.implemented", "decision.verify")


def _is_dispatchable(suite, ev) -> bool:
    """A resolve verdict is auto-dispatchable iff (deterministic — no confidence): the operator
    APPROVED it, the item is a BUILD-INTENT (the §W2 discriminator), and its DECLARED consequence
    class has posture==AUTO (the only class that auto-runs; CONFIRM/SURFACE/LOCKED surface for the
    operator). Mirrors dispatch_decision's own gates so the watcher pre-filters identically — but
    dispatch_decision still enforces them (no-bypass: the substrate is the authority, not this read)."""
    from runtime.governance import posture, AUTO
    if ev.get("kind") != "resolve" or ev.get("choice") != "approve":
        return False
    sid = ev.get("surfaced")
    item = suite.inbox.get(sid) if sid else None
    if not item or not suite.is_build_intent(item):
        return False
    declared = (item.get("payload") or {}).get("consequence_class", "decision_build")
    return posture(declared) == AUTO


def resurface_crashed(suite) -> list[str]:
    """§W7 (the WIRE-BE worker's flag): a dispatch that emitted its `decision.dispatch` claim but
    reached NO terminal event (`decision.implemented`/`decision.verify` for that same `derived_from`)
    launched and then died mid-flight (process crash, timeout that wasn't caught, host restart).
    dispatch_decision CORRECTLY refuses to re-launch it (exactly-once — the claim event is durable),
    so it must be RE-SURFACED loud, never silently dropped (no silent dead end — Tim's law). One new
    responsive review item per crashed dispatch, idempotently (a `decision.crashed` marker keyed on
    the seq means we already re-surfaced it — so this is itself exactly-once and re-running is safe).
    Returns the list of new review-item ids surfaced this pass (empty when nothing crashed)."""
    events = suite.store.events_since(-1)
    dispatched, terminated, already = {}, set(), set()
    for e in events:
        df = e.get("derived_from")
        if df is None:
            continue
        k = e.get("kind")
        if k == "decision.dispatch":
            dispatched[df] = e               # the claim — carries surfaced sid + scope + class
        elif k in _TERMINAL_KINDS:
            terminated.add(df)
        elif k == "decision.crashed":
            already.add(df)                  # already re-surfaced this crashed dispatch
    crashed = [df for df in dispatched if df not in terminated and df not in already]
    new_items = []
    for df in sorted(crashed):
        claim = dispatched[df]
        orig_sid = claim.get("surfaced")
        orig = suite.inbox.get(orig_sid) or {}
        payload = dict(orig.get("payload") or {})
        payload.update({
            "requeued_from": orig_sid, "intent": "build", "derived_from": df,
            "why": (f"dispatch crashed mid-flight: a build was claimed (decision.dispatch, "
                    f"seq={df}) but reached NO terminal status (no implemented/verify event). "
                    f"It will NOT auto-re-launch (exactly-once); re-surfaced for the operator."),
            "crashed_dispatch": True,
        })
        new_sid = suite.inbox.surface_review(payload, origin="responsive")
        # a durable marker so a later pass does not re-surface the same crash again (exactly-once
        # for the re-surface itself — keyed on the crashed dispatch's derived_from).
        suite._emit("decision.crashed",
                    f"crashed/mid-flight dispatch (seq={df}, item={orig_sid}) re-surfaced loud → {new_sid} "
                    f"(no terminal event found; not re-launched — exactly-once)",
                    surfaced=new_sid, requeued_from=orig_sid, derived_from=df, crashed=True)
        new_items.append(new_sid)
    return new_items


def drive_dispatchable(suite, *, cursor: int = -1, launcher=None, verifier=None,
                       suite_runner=None, critic=None, cap: int | None = None,
                       repo: str | None = None) -> dict:
    """§W6 — the unattended trigger. ONE bounded watcher pass: read every resolve verdict since the
    cursor, dispatch the auto-dispatchable build-intent approves (up to the §W7 CONCURRENCY_CAP), and
    surface — loud — anything deferred or crashed. NO human re-prompt anywhere: the operator's
    /api/resolve wrote the verdict; this READS it and drives the governed verb. The watcher NEVER
    calls resolve/resolve_surfaced (operator-only resolve preserved) — it writes dispatches + the
    `status` lane only, all through dispatch_decision (which writes status, never `resolved`).

    Sequence:
      0. RE-SURFACE crashed mid-flight dispatches (loud; never a silent dead end).
      1. read resolve_verdicts_since(cursor) — ALL verdicts (approve + negative) in seq order.
      2. select the auto-dispatchable approves (build-intent + posture==AUTO); the rest are NOT this
         watcher's job (negative verdicts route via requeue elsewhere; non-AUTO classes surface).
      3. enforce the cap: dispatch the first `cap`; DEFER the remainder — surface each deferred one
         loud (event + a returned list), NEVER silently truncate (Tim's no-silent-failure law). The
         deferred verdicts are re-read next pass (the cursor only advances past CONSUMED seqs).
      4. advance the cursor to the max seq we CONSUMED (dispatched or terminally handled), so a
         deferred verdict is re-offered next pass. Exactly-once is the event log, not the cursor —
         so even a coarse/duplicated cursor can never double-launch.

    cap/launcher/verifier/repo are injectable (tests + a future standalone daemon supply them); the
    DEFAULT cap is implement.CONCURRENCY_CAP and the default launcher/verifier are dispatch_decision's
    own (the real `claude -p` round-trip + the change-set verifier). A single dispatch that fails to
    LAUNCH is already a loud re-queue inside dispatch_decision (it returns requeued, never raises for
    a LaunchError) — counted here as handled, not crashed.

    Returns: {dispatched:[...], deferred:[...], crashed_resurfaced:[...], cursor:<new>, cap:<n>}.
    """
    cap = CONCURRENCY_CAP if cap is None else cap
    if cap < 0:
        raise ValueError(f"concurrency cap must be >= 0, got {cap} (fail loud — no unbounded launch)")

    # 0 — crashed mid-flight first, so a crashed item is re-surfaced BEFORE we consider new work.
    crashed_resurfaced = resurface_crashed(suite)

    # 1 — every resolve verdict newer than the cursor, in seq order (oldest-first from events_since).
    verdicts = [e for e in suite.resolve_verdicts_since(cursor)]
    verdicts.sort(key=lambda e: e.get("seq", 0))

    dispatched, deferred = [], []
    new_cursor = cursor
    launched = 0
    for ev in verdicts:
        seq = ev.get("seq")
        sid = ev.get("surfaced")
        if not _is_dispatchable(suite, ev):
            # NOT this watcher's responsibility (negative verdict, non-build-intent, or a non-AUTO
            # class that must surface for the operator). It is CONSUMED — advancing past it is safe:
            # the operator/another path owns it, and dispatch is event-guarded regardless.
            new_cursor = max(new_cursor, seq)
            continue
        # already dispatched? (a re-fire over the same approve, or a restart) — the event log is the
        # guarantee; skip without burning a launch slot, and consume the cursor past it.
        if suite._already_dispatched(seq):
            new_cursor = max(new_cursor, seq)
            continue
        if launched >= cap:
            # §W7 — CAP reached. DEFER loud: do NOT dispatch, do NOT advance the cursor past it (so it
            # is re-offered next pass), surface what we deferred (event + return value). No silent
            # truncation. (We keep scanning to ENUMERATE every deferred verdict for the loud surface.)
            deferred.append({"surfaced": sid, "seq": seq})
            suite._emit("decision.deferred",
                        f"build-intent approve (item={sid}, seq={seq}) DEFERRED — concurrency cap "
                        f"{cap} reached this pass; will dispatch a later pass (no silent truncation)",
                        surfaced=sid, derived_from=seq, cap=cap, deferred=True)
            continue
        # under the cap → DISPATCH (the governed verb does bind-check + exactly-once + gate + launch +
        # verify + close-or-surface). A LaunchError is turned into a loud re-queue INSIDE the verb (it
        # returns {requeued,...,launched:False}), so this call does not raise for a crashed launch.
        out = suite.dispatch_decision(sid, seq, launcher=launcher, verifier=verifier,
                                      suite_runner=suite_runner, critic=critic, repo=repo)
        dispatched.append({"surfaced": sid, "seq": seq, "result": out})
        launched += 1
        new_cursor = max(new_cursor, seq)

    return {"dispatched": dispatched, "deferred": deferred,
            "crashed_resurfaced": crashed_resurfaced, "cursor": new_cursor, "cap": cap}
