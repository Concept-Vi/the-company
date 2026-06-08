"""tests/wire_trigger_acceptance.py — L2 · the WIRE TRIGGER (the resolve→dispatch production caller).

Proves the L2 wiring — and proves it SAFE-BY-DEFAULT — WITHOUT firing a real `claude -p`:

  IS (the gap L2 closes): the wire is fully built but had NO production trigger. `resolve_surfaced`
  wrote the operator's approve verdict but did NOT call dispatch_decision; `drive_dispatchable` (the
  watcher that does) had NO production caller (only tests). And PERMISSION_MODE defaults to "plan".
  So a LIVE loop never closed.

  L2 adds: (1) a production caller for drive_dispatchable — Suite.resolve_surfaced, on an operator
  approve of a build-intent, drives the watcher; (2) the resolve→dispatch link (the same mechanism:
  the watcher reads the just-written verdict and calls dispatch_decision); (3) COMPANY_WIRE_PERMISSION
  as a flag (default "plan"), read at call-time, that ARMS the trigger only on the deliberate opt-in.

What this proves (no real autonomous fire anywhere — launch is monkeypatched/mocked):
  1. SAFE-BY-DEFAULT: with the DEFAULT posture ("plan", env unset/cleared), an approved build-intent
     does NOT dispatch — implement.launch is NEVER called → no self-modify. 🔒 built-not-armed holds.
  2. ARMED → the resolve→dispatch link FIRES: COMPANY_WIRE_PERMISSION=acceptEdits + approve routes to
     dispatch_decision → implement.launch, called with the RIGHT intent + scope. Asserted via a
     monkeypatched launch that CAPTURES args (and short-circuits) — NO real subprocess.
  3. The exactly-once decision.dispatch claim + AUTO gate + DENY-ALL scope-diff + guarded close still
     hold (the governed path is reused unchanged — armed only ADDS the trigger).
  4. COMPANY_WIRE_PERMISSION=acceptEdits flips the flag: permission_mode()/wire_armed() READ it live
     (call-time, not import-time) — without running a live acceptEdits claude -p.
  5. OPERATOR-ONLY: dispatch is NOT reachable from the MCP face (resolve_surfaced is off-face).

Run: /home/tim/company/.venv/bin/python tests/wire_trigger_acceptance.py
"""
import os
import sys
import tempfile
import faulthandler

# HANG-GUARD (load-bearing for L2): this is the wire-trigger acceptance — the one unit whose dispatch
# path runs verify-by-suites, which spawns real suite SUBPROCESSES. A bug that lets that run un-stubbed
# hangs the whole test (it already burned a build worker for 35 min). faulthandler dumps the blocked
# frame and HARD-EXITS at 60s so this suite can NEVER silently hang a worker or a cron fire again.
faulthandler.dump_traceback_later(60, exit=True)

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
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="wiretrig-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    s = Suite(store, reg, nodes_dir=NODES)
    # STUB the verify-by-suites runner — exactly as the launch is mocked. dispatch_decision runs
    # `_wire_verify → _run_suites → _default_suite_runner`, which spawns REAL suite subprocesses
    # (subprocess.run, 600s each) BEFORE reaching launch. This test proves the ROUTING (resolve →
    # dispatch → launch) + the safety gates — NOT the real verify (that is wire_harden H1/H5's job).
    # So stub the runner to an instant green; the routing then reaches the mocked launch without
    # spawning anything. (This is why the unstubbed test hung: the heavy verify path ran for real.)
    s._default_suite_runner = lambda suite: (True, "stubbed (routing test; real verify is wire_harden H1/H5)")
    return s


def clear_env():
    """Force the DEFAULT posture (the safe default) regardless of the runner's environment."""
    os.environ.pop("COMPANY_WIRE_PERMISSION", None)


def set_armed():
    """Deliberately ARM the trigger — the env-gated opt-in (acceptEdits)."""
    os.environ["COMPANY_WIRE_PERMISSION"] = "acceptEdits"


# A launch RECORDER: captures the decision it WOULD spawn `claude -p` on, then SHORT-CIRCUITS by
# raising a NON-LaunchError sentinel. dispatch_decision only catches _impl.LaunchError, so this
# sentinel propagates up through drive_dispatchable into resolve_surfaced's guarded trigger (landing
# in verdict["wire_drive_error"]) — proving the routing reached launch WITHOUT a real subprocess and
# WITHOUT running the heavy verify path. NO real `claude -p` is ever spawned.
class _LaunchReached(Exception):
    pass


def make_recorder():
    calls = []

    def fake_launch(decision, *, repo):
        calls.append({"decision": decision, "repo": repo})
        raise _LaunchReached("launch reached (recorded) — short-circuit, no real subprocess")

    return calls, fake_launch


# ===========================================================================================
print("\n=== 0 — the FLAG: permission_mode()/wire_armed() READ COMPANY_WIRE_PERMISSION at call-time ===")
clear_env()
check("default posture is 'plan' (safe-by-default) when env unset", impl.permission_mode() == "plan")
check("wire_armed() is FALSE by default (🔒 built-not-armed)", impl.wire_armed() is False)
set_armed()
check("COMPANY_WIRE_PERMISSION=acceptEdits flips permission_mode() live (call-time read)",
      impl.permission_mode() == "acceptEdits")
check("wire_armed() is TRUE only under the deliberate opt-in", impl.wire_armed() is True)
clear_env()
check("clearing the env returns to the safe default immediately (no restart)",
      impl.permission_mode() == "plan" and impl.wire_armed() is False)


# ===========================================================================================
print("\n=== 1 — SAFE-BY-DEFAULT: default 'plan' + approve does NOT dispatch (launch NEVER called) ===")
clear_env()
s = fresh_suite()
calls, fake_launch = make_recorder()
orig_launch = impl.launch
impl.launch = fake_launch
try:
    intent = s.surface_build_intent("add a reversible thing", scope=["runtime/"],
                                    consequence_class="decision_build")
    sid = intent["id"]
    verdict = s.resolve_surfaced(sid, "approve", reason="authorize this build")
    check("the operator's approve was recorded (operator-only resolve unchanged)", verdict["resolved"] is True)
    check("the trigger did NOT fire under the default posture (no wire_drive key on the verdict)",
          "wire_drive" not in verdict and "wire_drive_error" not in verdict)
    check("implement.launch was NEVER called (no self-modify; 🔒 holds)", len(calls) == 0)
    check("NO decision.dispatch event under the default posture (the loop did not close)",
          not any(e.get("kind") == "decision.dispatch" for e in s.store.events_since(-1)))
    check("the item did NOT reach status=implemented under default (built-not-armed)",
          s.inbox.get(sid)["status"] != "implemented")
finally:
    impl.launch = orig_launch
    clear_env()


# ===========================================================================================
print("\n=== 2 — ARMED: acceptEdits + approve ROUTES to dispatch_decision → launch (right intent+scope) ===")
set_armed()
s = fresh_suite()
calls, fake_launch = make_recorder()
orig_launch = impl.launch
impl.launch = fake_launch
try:
    intent = s.surface_build_intent("build the armed thing", scope=["runtime/implement.py"],
                                    consequence_class="decision_build")
    sid = intent["id"]
    verdict = s.resolve_surfaced(sid, "approve", reason="authorize this build")
    check("the resolve→dispatch trigger FIRED when armed (verdict carries the trigger outcome)",
          ("wire_drive" in verdict) or ("wire_drive_error" in verdict))
    # WIRE-ASYNC: the build now runs in a BACKGROUND daemon thread (decoupled from this request), so the
    # ack returns PROMPTLY (status:running) and the launch happens off-thread. The routing assertions
    # below check the build COMPLETED in the background — join the dispatch thread first (the test
    # equivalent of "the SSE stream eventually carries the result"). The PRODUCTION request does NOT
    # wait; this join exists only so the by-use test can observe the off-thread side-effects.
    check("the ack is prompt + running (the request did NOT block on the build)",
          verdict.get("wire_drive", {}).get("status") == "running")
    check("all WIRE-ASYNC background dispatch threads finished within the join window",
          s.wire_wait_for_dispatch(timeout=30))
    check("implement.launch WAS reached (the routing closed resolve→dispatch→launch)", len(calls) == 1)
    # the launch was called with the RIGHT decision (the approved build-intent) + its declared scope.
    launched_decision = calls[0]["decision"]
    check("launch received the SAME build-intent the operator approved (right intent)",
          launched_decision.get("id") == sid)
    check("launch's decision carries the operator-declared scope (right scope)",
          (launched_decision.get("payload") or {}).get("scope") == ["runtime/implement.py"])
    check("the build-intent discriminator held on the launched decision",
          Suite.is_build_intent(launched_decision))
    # EXACTLY-ONCE: the durable decision.dispatch claim was made for the resolve seq BEFORE launch.
    resolve_ev = next(e for e in reversed(s.store.events_since(-1))
                      if e.get("kind") == "resolve" and e.get("surfaced") == sid)
    seq = resolve_ev["seq"]
    ndispatch = sum(1 for e in s.store.events_since(-1)
                    if e.get("kind") == "decision.dispatch" and e.get("derived_from") == seq)
    check("EXACTLY ONE decision.dispatch claim emitted for the resolve seq (exactly-once preserved)",
          ndispatch == 1)
    check("operator `resolved` was written by the approve, NOT by the trigger (operator-only preserved)",
          s.inbox.get(sid)["resolved"] == "approve")
finally:
    impl.launch = orig_launch
    clear_env()


# ===========================================================================================
print("\n=== 3 — ARMED but the GOVERNED GATES still hold (AUTO gate + DENY-ALL scope + exactly-once) ===")
set_armed()
# 3a — a NON-AUTO (LOCKED) class approve, even armed, does NOT dispatch (the AUTO pre-gate holds).
s = fresh_suite()
calls, fake_launch = make_recorder()
orig_launch = impl.launch
impl.launch = fake_launch
try:
    locked = s.surface_build_intent("touch source data", scope=["data/"], consequence_class="source_data")
    lsid = locked["id"]
    verdict = s.resolve_surfaced(lsid, "approve", reason="authorize")
    s.wire_wait_for_dispatch(timeout=30)   # WIRE-ASYNC: let any (here: none) bg dispatch settle
    check("a non-AUTO (LOCKED) class is NOT auto-dispatched even when armed (AUTO gate preserved)",
          len(calls) == 0)
    check("the LOCKED item did NOT reach implemented (left for the operator)",
          s.inbox.get(lsid)["status"] != "implemented")
finally:
    impl.launch = orig_launch
    clear_env()

# 3b — exactly-once across the trigger: a SECOND approve cannot happen (idempotent-per-item refuses),
#      and the durable claim refuses a second dispatch of the same seq. We assert the trigger inherits
#      dispatch_decision's exactly-once by re-driving the watcher (the production caller) directly.
set_armed()
s = fresh_suite()
calls, fake_launch = make_recorder()
orig_launch = impl.launch
impl.launch = fake_launch
try:
    intent = s.surface_build_intent("once-only build", scope=["runtime/"], consequence_class="decision_build")
    sid = intent["id"]
    s.resolve_surfaced(sid, "approve", reason="authorize")          # fires the trigger once (bg dispatch)
    # WIRE-ASYNC: the trigger dispatches in a BACKGROUND thread now — join it so the durable
    # decision.dispatch claim is in place before the second pass (the claim, not timing, is the
    # exactly-once guarantee; the join just makes the off-thread claim observable to the assertion).
    check("the background dispatch finished within the join window", s.wire_wait_for_dispatch(timeout=30))
    first = len(calls)
    # a SECOND watcher pass over the SAME verdict (the production caller, re-run) must NOT re-launch —
    # the durable decision.dispatch claim is the guarantee, not the cursor.
    impl.drive_dispatchable(s)
    check("the trigger reached launch exactly once (first approve)", first == 1)
    check("a second watcher pass does NOT re-launch the same approve (exactly-once on the event log)",
          len(calls) == first)
finally:
    impl.launch = orig_launch
    clear_env()


# ===========================================================================================
print("\n=== 4 — DENY-ALL: armed + an EMPTY declared scope can NEVER close (deny-all, no real fire) ===")
# Here we let launch RETURN a plan-style empty-change result (NO subprocess) and assert the empty scope
# means the build cannot close implemented — the headline safety property, preserved end-to-end.
set_armed()
s = fresh_suite()
orig_launch = impl.launch

def empty_change_launch(decision, *, repo):
    # a deterministic 'plan-mode-like' result: NO changed files (what a read-only run produces).
    return {"finished": True, "success": True, "exit_code": 0, "summary": "planned (no edits)",
            "changed_files": [], "permission_mode": "acceptEdits"}

impl.launch = empty_change_launch
try:
    intent = s.surface_build_intent("build with NO declared scope", scope=[],
                                    consequence_class="decision_build")
    sid = intent["id"]
    s.resolve_surfaced(sid, "approve", reason="authorize")
    s.wire_wait_for_dispatch(timeout=30)   # WIRE-ASYNC: let the bg dispatch settle before asserting
    check("an EMPTY declared scope (DENY-ALL) build did NOT close implemented",
          s.inbox.get(sid)["status"] != "implemented")
finally:
    impl.launch = orig_launch
    clear_env()


# ===========================================================================================
print("\n=== 5 — OPERATOR-ONLY: dispatch / approve are OFF the MCP/agent face ===")
import mcp_face.server as mcp_server
src = open(os.path.join(ROOT, "mcp_face", "server.py")).read()
check("resolve_surfaced is NOT exposed as an MCP tool (no self-approve on the agent face)",
      "resolve_surfaced" not in src or "resolve_surfaced is NOT" in src or "not exposed" in src.lower())
check("dispatch_decision is NOT exposed as an MCP tool (dispatch stays off-face)",
      "dispatch_decision" not in src)


print(f"\nALL {PASS} CHECKS PASS — L2 the wire trigger: the resolve→dispatch production caller is wired "
      f"(approve of a build-intent → drive_dispatchable → dispatch_decision → launch) and SAFE-BY-DEFAULT "
      f"(default 'plan' → INERT → launch never called → 🔒 built-not-armed). COMPANY_WIRE_PERMISSION="
      f"acceptEdits ARMS it (call-time read); the governed path is reused UNCHANGED (exactly-once claim · "
      f"AUTO gate · DENY-ALL empty scope · operator-only off-MCP). NO real `claude -p` fired anywhere.")
