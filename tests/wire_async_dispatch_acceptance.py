"""tests/wire_async_dispatch_acceptance.py — WIRE-ASYNC · the build dispatch is DECOUPLED from the
approving HTTP request (the standalone-daemon decoupling the wire's own comments anticipated).

THE BUG (diagnosed, reproduced live): POST /api/resolve → Suite.resolve_surfaced called the wire's
drive_dispatchable → dispatch_decision → implement.launch SYNCHRONOUSLY, and launch runs a BLOCKING
`claude -p` subprocess (up to DEFAULT_TIMEOUT_S=900s). So the ENTIRE build ran INSIDE the approve HTTP
request. If the approving client connection dropped (a curl timeout, a UI fetch timeout, a phone
backgrounding) the request thread's result-handling was lost and the build orphaned as a 'crashed'
dispatch (a decision.dispatch claim with NO terminal event) — never re-launched (exactly-once).

THE FIX (proved here): resolve_surfaced writes the operator verdict SYNCHRONOUSLY (the consent record
is durable immediately), then hands the build EXECUTION to a BACKGROUND daemon thread
(Suite._drive_dispatchable_bg) and RETURNS PROMPTLY with an ack {wire_drive:{dispatched:[sid],
status:"running"}}. The background thread runs the SAME governed drive_dispatchable → dispatch_decision
path (per-seq lock + durable claim + AUTO gate + launch + verify + [self-build] commit + guarded close +
surface-for-review — REUSED, never re-implemented), completes + emits its terminal event + commits +
surfaces via the SAME event log → the SSE stream delivers it to the UI INDEPENDENT of the connection.

What this proves (model-free; injected FAKE runner — NEVER a real `claude -p`; no live store/commit):
  (i)   PROMPT RETURN: resolve approve of an armed build-intent RETURNS BEFORE a SLOW runner finishes
        (a barrier proves the runner is still mid-flight when resolve has already returned).
  (ii)  THE BUILD STILL COMPLETES in the background: after resolve returned, the bg thread reaches the
        terminal event (decision.implemented) + the [self-build] commit (the injected committer ran)
        + the surfaced review item — all AFTER the resolve returned.
  (iii) CLIENT DISCONNECT does NOT orphan the build: we DISCARD the verdict (simulate the client
        dropping after the ack) and the bg thread STILL completes (terminal event present, no orphan).
  (iv)  EXACTLY-ONCE STILL HOLDS: two concurrent approves of the SAME seq → ONE decision.dispatch claim
        (the per-seq lock + the durable claim inside dispatch_decision, regardless of which thread runs).
  (v)   A BACKGROUND-THREAD EXCEPTION emits a FAIL-LOUD decision.verify (no silent thread death).
  (vi)  CONCURRENCY CAP respected: with cap=1 and 2 dispatchable approves driven in ONE bg pass, the
        first dispatches, the second is DEFERRED loud (decision.deferred), nothing double-launched.

Run: /home/tim/company/.venv/bin/python tests/wire_async_dispatch_acceptance.py
"""
import os
import sys
import time
import tempfile
import threading
import faulthandler

# HANG-GUARD: the dispatch path can reach verify-by-suites (real subprocesses) if a verifier is not
# injected. We inject a fast verifier everywhere, but keep the guard: dump + hard-exit at 90s so this
# suite can NEVER silently hang a worker (the threads are daemon=True, so a hang means a real bug).
faulthandler.dump_traceback_later(90, exit=True)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import implement as impl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def fresh_suite():
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="wireasync-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    s = Suite(store, reg, nodes_dir=NODES)
    # NEUTRALIZE the wire's git CHECKPOINT in tests (it commits each accepted build on the LIVE repo).
    # We RECORD the committer calls so test (ii) can prove the [self-build] commit ran in the bg thread.
    s._committer_calls = []
    def _fake_commit(paths, msg):
        s._committer_calls.append({"paths": list(paths), "msg": msg})
        return "0" * 40
    s._self_build_commit = _fake_commit
    # STUB the verify-by-suites runner so the heavy default verify (real subprocesses) never fires; we
    # inject a fast verifier per dispatch too, but this guards the unconditional refresh/form path.
    s._default_suite_runner = lambda suite: (True, "stubbed (async-dispatch test; verify is wire_harden's job)")
    return s


def arm():
    os.environ["COMPANY_WIRE_PERMISSION"] = "acceptEdits"


def disarm():
    os.environ.pop("COMPANY_WIRE_PERMISSION", None)


def events(s):
    return s.store.events_since(-1)


def has_event(s, kind, **match):
    for e in events(s):
        if e.get("kind") != kind:
            continue
        if all(e.get(k) == v for k, v in match.items()):
            return True
    return False


def resolve_seq(s, sid):
    ev = next(e for e in reversed(events(s)) if e.get("kind") == "resolve" and e.get("surfaced") == sid)
    return ev["seq"]


# ============================================================================================
# (i) PROMPT RETURN — resolve returns BEFORE a SLOW runner finishes (the build is off-thread).
# ============================================================================================
print("\n=== (i) PROMPT RETURN: armed approve returns BEFORE the slow build runner finishes ===")
arm()
s = fresh_suite()
runner_started = threading.Event()
release_runner = threading.Event()
runner_finished = threading.Event()


def slow_launch(decision, *, repo):
    """A SLOW fake `claude -p`: signals it started, then BLOCKS until released — so we can prove the
    resolve call returned WHILE the build is still mid-flight (decoupled). No real subprocess."""
    runner_started.set()
    release_runner.wait(timeout=30)
    runner_finished.set()
    return {"finished": True, "success": True, "exit_code": 0, "summary": "implemented",
            "changed_files": ["runtime/implement.py"], "permission_mode": "acceptEdits"}


orig_launch = impl.launch
impl.launch = slow_launch
try:
    intent = s.surface_build_intent("a backgrounded build", scope=["runtime/implement.py"],
                                    consequence_class="decision_build")
    sid = intent["id"]
    t0 = time.monotonic()
    verdict = s.resolve_surfaced(sid, "approve", reason="authorize",
                                 )  # injects nothing → uses impl.launch (slow) in the bg thread
    elapsed = time.monotonic() - t0
    # the runner must have STARTED (bg thread is live) but NOT finished (it is blocked on the barrier).
    started_ok = runner_started.wait(timeout=10)
    check("the background build runner STARTED (the bg thread is driving the dispatch)", started_ok)
    check("resolve RETURNED while the runner is STILL mid-flight (decoupled, not blocked on the build)",
          not runner_finished.is_set())
    check("resolve returned PROMPTLY (well under the runner's block) — the request did not block",
          elapsed < 5.0)
    check("the ack reports the build RUNNING in the background ({dispatched:[sid], status:'running'})",
          verdict.get("wire_drive") == {"dispatched": [sid], "status": "running"})
    check("the operator `resolved` field WAS written synchronously (consent record durable immediately)",
          s.inbox.get(sid)["resolved"] == "approve")
    # now release the runner and let the bg thread complete.
    release_runner.set()
    check("the bg dispatch thread completed after release", s.wire_wait_for_dispatch(timeout=30))
finally:
    impl.launch = orig_launch
    disarm()


# ============================================================================================
# (ii) THE BUILD STILL COMPLETES in the background AFTER the resolve returned.
# ============================================================================================
print("\n=== (ii) THE BUILD COMPLETES IN THE BACKGROUND: terminal event + [self-build] commit, AFTER resolve ===")
arm()
s = fresh_suite()


def good_launch(decision, *, repo):
    return {"finished": True, "success": True, "exit_code": 0, "summary": "implemented",
            "changed_files": ["runtime/implement.py"], "permission_mode": "acceptEdits"}


orig_launch = impl.launch
impl.launch = good_launch
try:
    intent = s.surface_build_intent("complete-in-bg build", scope=["runtime/implement.py"],
                                    consequence_class="decision_build")
    sid = intent["id"]
    verdict = s.resolve_surfaced(sid, "approve", reason="authorize")
    # at the instant resolve returned, the build has NOT necessarily closed yet (it's off-thread).
    check("resolve returned with a running ack (the build is NOT closed synchronously)",
          verdict.get("wire_drive", {}).get("status") == "running")
    # JOIN the bg thread — the build completes INDEPENDENTLY of this request.
    check("the bg dispatch thread completed", s.wire_wait_for_dispatch(timeout=30))
    seq = resolve_seq(s, sid)
    check("a decision.dispatch CLAIM was emitted for the resolve seq (the governed path ran in the bg)",
          has_event(s, "decision.dispatch", derived_from=seq))
    check("the TERMINAL decision.implemented event was emitted (the build CLOSED in the background)",
          has_event(s, "decision.implemented", derived_from=seq))
    check("the item reached status=implemented (closed by the bg thread, not the request)",
          s.inbox.get(sid)["status"] == "implemented")
    check("the [self-build] git CHECKPOINT ran in the bg thread (the injected committer was called)",
          len(s._committer_calls) == 1 and "runtime/implement.py" in s._committer_calls[0]["paths"])
    check("the build was SURFACED FOR REVIEW in the bg (decision.surfaced_for_review event present)",
          has_event(s, "decision.surfaced_for_review"))
finally:
    impl.launch = orig_launch
    disarm()


# ============================================================================================
# (iii) CLIENT DISCONNECT does NOT orphan the build — discard the verdict, the bg thread completes.
# ============================================================================================
print("\n=== (iii) CLIENT DISCONNECT: discard the ack (client drops) → the bg build STILL completes, no orphan ===")
arm()
s = fresh_suite()
orig_launch = impl.launch
impl.launch = good_launch
try:
    intent = s.surface_build_intent("survive-disconnect build", scope=["runtime/implement.py"],
                                    consequence_class="decision_build")
    sid = intent["id"]
    # simulate the client dropping right after the ack: we call resolve and THROW AWAY the verdict
    # (the bridge would have sent it, but the connection is gone). The bg thread is unaffected.
    s.resolve_surfaced(sid, "approve", reason="authorize")
    del intent  # the request context is gone; only the bg thread remains
    check("the bg dispatch thread completed regardless of the (dropped) client", s.wire_wait_for_dispatch(timeout=30))
    seq = resolve_seq(s, sid)
    check("the build CLOSED (decision.implemented) despite the client disconnect — NOT orphaned",
          has_event(s, "decision.implemented", derived_from=seq))
    # an ORPHAN is a decision.dispatch claim with NO terminal event. Prove there is none.
    dispatched_seqs = {e.get("derived_from") for e in events(s) if e.get("kind") == "decision.dispatch"}
    terminal_seqs = {e.get("derived_from") for e in events(s)
                     if e.get("kind") in ("decision.implemented", "decision.verify")}
    orphans = dispatched_seqs - terminal_seqs
    check("ZERO orphaned dispatches (every decision.dispatch claim has a terminal event)", not orphans)
    check("the item reached status=implemented (the disconnect did not lose the result)",
          s.inbox.get(sid)["status"] == "implemented")
finally:
    impl.launch = orig_launch
    disarm()


# ============================================================================================
# (iv) EXACTLY-ONCE — two CONCURRENT approves of the SAME seq → ONE dispatch claim.
# ============================================================================================
# resolve_surfaced refuses a SECOND terminal verdict per item (idempotent-per-item), so two concurrent
# *resolve_surfaced* calls would have one raise. The exactly-once guarantee we must prove is at the
# DISPATCH layer: two concurrent dispatch passes over the SAME approved seq → one claim. We drive that
# directly via two background dispatch threads racing on the same seq (the production trigger spawns one
# such thread per approve; the guarantee is that even two cannot double-launch).
print("\n=== (iv) EXACTLY-ONCE: two concurrent bg dispatch passes over the SAME seq → ONE decision.dispatch ===")
arm()
s = fresh_suite()
launch_count = {"n": 0}
launch_lock = threading.Lock()
race_barrier = threading.Barrier(2)


def counting_launch(decision, *, repo):
    # synchronize both threads to maximize the race window over the check→claim section.
    try:
        race_barrier.wait(timeout=10)
    except threading.BrokenBarrierError:
        pass
    with launch_lock:
        launch_count["n"] += 1
    return {"finished": True, "success": True, "exit_code": 0, "summary": "implemented",
            "changed_files": ["runtime/implement.py"], "permission_mode": "acceptEdits"}


orig_launch = impl.launch
impl.launch = counting_launch
try:
    intent = s.surface_build_intent("race build", scope=["runtime/implement.py"],
                                    consequence_class="decision_build")
    sid = intent["id"]
    s.resolve_surfaced(sid, "approve", reason="authorize")   # writes the ONE approve verdict (+ 1 bg thread)
    # spawn a SECOND bg dispatch pass over the same already-written verdict to force the race (the
    # production trigger spawns one; we add a racing twin to prove two cannot double-launch).
    s._drive_dispatchable_bg(sid=sid)
    # the barrier needs BOTH threads to reach launch to trip; if exactly-once works, only ONE thread
    # reaches launch, so the barrier times out (10s) for the loser — that is the CORRECT outcome.
    check("both bg dispatch passes finished", s.wire_wait_for_dispatch(timeout=40))
    seq = resolve_seq(s, sid)
    ndispatch = sum(1 for e in events(s) if e.get("kind") == "decision.dispatch" and e.get("derived_from") == seq)
    check("EXACTLY ONE decision.dispatch claim for the seq (the second pass refused — exactly-once)",
          ndispatch == 1)
    check("the launcher ran AT MOST once (no double-launch of a real build)", launch_count["n"] <= 1)
finally:
    impl.launch = orig_launch
    disarm()


# ============================================================================================
# (v) A BACKGROUND-THREAD EXCEPTION emits a FAIL-LOUD decision.verify (no silent thread death).
# ============================================================================================
print("\n=== (v) FAIL-LOUD: a bg dispatch thread exception emits a decision.verify (no silent death) ===")
arm()
s = fresh_suite()


def exploding_drive(*a, **k):
    raise RuntimeError("simulated catastrophic failure inside the dispatch path")


# patch drive_dispatchable on the module the bg thread imports, so the WHOLE bg pass raises (not just
# launch — launch errors are already a loud re-queue inside dispatch_decision; here we prove the
# OUTER guard catches an UNEXPECTED exception too, the silent-thread-death case).
orig_drive = impl.drive_dispatchable
impl.drive_dispatchable = exploding_drive
try:
    intent = s.surface_build_intent("explode build", scope=["runtime/implement.py"],
                                    consequence_class="decision_build")
    sid = intent["id"]
    verdict = s.resolve_surfaced(sid, "approve", reason="authorize")
    check("resolve still returned a running ack even though the bg pass will explode",
          verdict.get("wire_drive", {}).get("status") == "running")
    check("the bg dispatch thread finished (it did NOT hang on the exception)", s.wire_wait_for_dispatch(timeout=30))
    check("a FAIL-LOUD decision.verify (verify_passed=False) was emitted for the dead thread "
          "(no silent death → no orphan)",
          has_event(s, "decision.verify", surfaced=sid, verify_passed=False))
finally:
    impl.drive_dispatchable = orig_drive
    disarm()


# ============================================================================================
# (vi) CONCURRENCY CAP — cap=1, two dispatchable approves in ONE bg pass → 1 dispatched, 1 deferred.
# ============================================================================================
print("\n=== (vi) CONCURRENCY CAP: cap=1 over two dispatchable approves → 1 dispatched, 1 DEFERRED loud ===")
arm()
s = fresh_suite()
orig_launch = impl.launch
impl.launch = good_launch
try:
    i1 = s.surface_build_intent("cap build A", scope=["runtime/implement.py"], consequence_class="decision_build")
    i2 = s.surface_build_intent("cap build B", scope=["runtime/suite.py"], consequence_class="decision_build")
    # write BOTH operator approves synchronously (each fires its own bg trigger, but we will drive a
    # SINGLE capped pass explicitly to make the cap deterministic — the trigger's per-approve thread
    # would each carry the full cap; the cap property is about ONE pass over multiple verdicts).
    disarm()  # avoid the per-approve auto-trigger firing extra passes while we set up
    s.resolve_surfaced(i1["id"], "approve", reason="authorize")
    s.resolve_surfaced(i2["id"], "approve", reason="authorize")
    arm()
    # drive ONE capped bg pass over BOTH verdicts.
    th = s._drive_dispatchable_bg(sid=None, cap=1)
    check("the capped bg dispatch pass finished", s.wire_wait_for_dispatch(timeout=30))
    ndispatch = sum(1 for e in events(s) if e.get("kind") == "decision.dispatch")
    check("EXACTLY ONE build dispatched this pass (the cap=1 was respected)", ndispatch == 1)
    check("the OTHER approve was DEFERRED LOUD (a decision.deferred event — no silent truncation)",
          has_event(s, "decision.deferred"))
finally:
    impl.launch = orig_launch
    disarm()


# ============================================================================================
# (vii) HONEST ACK — a non-AUTO build-intent approve reports status='surfaced' (NOT 'running'),
#       with an EMPTY dispatched list. The bg pass filters it out (it surfaces for the operator);
#       claiming it was 'dispatched/running' would be pretending success (rule 4).
# ============================================================================================
print("\n=== (vii) HONEST ACK: an armed non-AUTO build-intent approve reports 'surfaced', NOT 'running' ===")
arm()
s = fresh_suite()
orig_launch = impl.launch
impl.launch = good_launch
try:
    locked = s.surface_build_intent("touch source data", scope=["data/"], consequence_class="source_data")
    lsid = locked["id"]
    verdict = s.resolve_surfaced(lsid, "approve", reason="authorize")
    s.wire_wait_for_dispatch(timeout=30)
    wd = verdict.get("wire_drive", {})
    check("the ack does NOT falsely claim 'running' for a non-AUTO build-intent (rule 4 — no pretend)",
          wd.get("status") == "surfaced")
    check("the ack's dispatched list is EMPTY for the non-AUTO build-intent (it was NOT dispatched)",
          wd.get("dispatched") == [])
    check("the non-AUTO build-intent was NOT dispatched (no decision.dispatch event)",
          not has_event(s, "decision.dispatch"))
    check("the non-AUTO build-intent did NOT reach implemented (left for the operator)",
          s.inbox.get(lsid)["status"] != "implemented")
finally:
    impl.launch = orig_launch
    disarm()


print(f"\nALL {PASS} CHECKS PASS — WIRE-ASYNC: the build dispatch is DECOUPLED from the approving request. "
      f"POST /api/resolve approve writes the operator verdict synchronously then hands the build to a "
      f"BACKGROUND daemon thread and returns a prompt running-ack; the build COMPLETES + emits its "
      f"terminal event + commits + surfaces via the SAME event log/SSE stream INDEPENDENT of the client "
      f"connection (a disconnect no longer orphans it). EXACTLY-ONCE (the per-seq lock + durable claim "
      f"inside dispatch_decision), the gates, the [self-build] commit, fail-loud-on-thread-exception, and "
      f"the concurrency cap are ALL preserved. NO real `claude -p`, NO live store, NO live commit.")
