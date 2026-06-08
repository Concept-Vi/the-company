"""tests/wire_acceptance.py — the Decision→Implementation Wire (Group W · scenario S8).

Makes the wire RUNNABLE + verifies its mechanisms deterministically (no real `claude -p` burned —
the launcher + verifier are injected; the launch PATH is exercised separately in dry-run). The LEAD
does the authoritative S8 by-use + adversarial verification against a live system; this proves the
backend mechanisms hold so that run can start.

S8 parts covered here (deterministic):
  1. Happy path: build-intent surfaced → operator approve → dispatch (injected build) → verify →
     status=implemented AND surfaced-for-review (a decision.surfaced_for_review event + a dispatcher-
     inert `build_result_review` item carrying the diff); events narrate dispatch→implemented; operator
     `resolved` written ONLY by resolve_surfaced (operator-only preserved). `implemented` is NOT a
     silent terminal — AI-operated is not review-free; approving the review item never rebuilds.
  2. Governed refusals (no confidence value, all deterministic):
       - forged/missing seq · bind mismatch (wrong sid / wrong choice) · non-build-intent approve ·
         already-dispatched (exactly-once) · LOCKED declared class never auto-dispatches.
  3. Bad implementation caught: a build that fails verification → NOT closed; a new responsive review
     item carries the reason (surface_review directly, not requeue_from_verdict).
  5. Exactly-once under stress: two overlapping dispatches of the same approved decision → second
     refuses (the decision.dispatch event keyed on the resolve seq).
  6. Scope overrun caught: a build that changes paths outside declared scope → NOT closed; surfaces back.
  + W4 Hole 4: the guarded close RAISES on an unverified verdict (mirrors apply_node).
  + W1: the launcher round-trip parses injected JSON, fails loud on non-JSON, and uses git ground truth.

Run: .venv/bin/python tests/wire_acceptance.py
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime.governance import GovernanceError
from runtime import implement as impl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def raises(label, fn, exc=GovernanceError):
    try:
        fn()
    except exc:
        check(label, True)
        return
    except Exception as e:
        assert False, f"FAIL: {label} — raised {type(e).__name__} not {exc.__name__}: {e}"
    assert False, f"FAIL: {label} — did NOT raise {exc.__name__}"


def fresh_suite():
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="wire-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    s = Suite(store, reg, nodes_dir=NODES)
    # NEUTRALIZE the wire's git CHECKPOINT in tests (it now commits each accepted build): the real
    # default `_self_build_commit` would `git commit` on the LIVE repo. Override the instance method
    # with a no-op that returns a fake 40-hex sha — isolates EVERY dispatch in this suite at once (the
    # checkpoint mechanism itself is proven in wire_commit_acceptance.py). Production is untouched.
    s._self_build_commit = lambda paths, msg: "0" * 40
    return s


def approve_seq(suite, sid):
    """Operator approves (the ONLY terminal-verdict writer) → return the resolve event's unique seq."""
    suite.resolve_surfaced(sid, "approve", reason="authorize this build")
    ev = next(e for e in reversed(suite.store.events_since(-1))
              if e.get("kind") == "resolve" and e.get("surfaced") == sid)
    return ev["seq"]


# an injected launcher = a deterministic "Claude Code result" so no real session is burned.
def good_launch(changed):
    return lambda decision, *, repo: {
        "finished": True, "success": True, "exit_code": 0,
        "summary": "implemented", "changed_files": list(changed), "permission_mode": "acceptEdits"}


def bad_launch(decision, *, repo):
    return {"finished": True, "success": False, "exit_code": 1,
            "summary": "failed", "changed_files": [], "permission_mode": "acceptEdits"}


print("\n=== W1 — launcher round-trip (injected runner; real path supported) ===")
# the launch() unit parses an injected runner result + records permission mode; no real session.
res = impl.launch({"payload": {"spec": "x", "scope": ["runtime/"]}},
                  repo=ROOT,
                  runner=lambda instr, *, repo, permission_mode, timeout_s: {
                      "finished": True, "success": True, "exit_code": 0, "summary": "ok",
                      "changed_files": ["runtime/x.py"]},
                  diff_runner=lambda args: type("R", (), {"stdout": ""})())
check("launch parses an injected result + tags permission_mode", res["success"] and "permission_mode" in res)
# a runner that emulates non-JSON stdout → LaunchError (fail loud, no fabricated success).
def nonjson_runner(instr, *, repo, permission_mode, timeout_s):
    raise impl.LaunchError("non-JSON stdout")
raises("launch fails loud on a bad round-trip (LaunchError)",
       lambda: impl.launch({"payload": {}}, repo=ROOT, runner=nonjson_runner,
                           diff_runner=lambda a: type("R", (), {"stdout": ""})()),
       exc=impl.LaunchError)
# instruction carries the declared scope so a well-behaved run stays in it.
instr = impl.build_instruction({"payload": {"spec": "add a thing", "scope": ["runtime/x.py"]}})
check("build_instruction injects the declared scope", "runtime/x.py" in instr and "ONLY" in instr)
# the instruction carries the STANDARDS (AI-operated but REVIEWED) — not a self-review instruction.
check("build_instruction carries the standards: reviewed-not-review-free + UI/UX bar + self-description",
      all(s in instr for s in ("REVIEWED", "self-description", "UI/UX bar"))
      and "separate review pass" in instr.lower())


print("\n=== W4 source — changed_delta is correct on a DIRTY tree (real content snapshots) ===")
# Build a temp repo dir with real files; drive changed_delta with a controlled diff_runner so the
# "dirty path set" is deterministic, while content hashes come from the real files we mutate.
tmp = tempfile.mkdtemp(prefix="wire-delta-")
open(os.path.join(tmp, "dirty.py"), "w").write("preexisting from another lane\n")   # already dirty
open(os.path.join(tmp, "target.py"), "w").write("v1\n")                              # the build will edit
# diff_runner: both files are reported dirty (as git would on a dirty tree).
def diff_runner(args):
    if "diff" in args:
        return type("R", (), {"stdout": "dirty.py\ntarget.py\n"})()
    return type("R", (), {"stdout": ""})()   # no untracked
before = impl.baseline_snapshot(repo=tmp, runner=diff_runner)
# the "build" edits ONLY target.py (and leaves the pre-existing dirty.py untouched).
open(os.path.join(tmp, "target.py"), "w").write("v2 — built\n")
delta = impl.changed_delta(repo=tmp, before=before, runner=diff_runner)
check("changed_delta reports the built file", "target.py" in delta)
check("changed_delta EXCLUDES a pre-existing dirty file the build didn't touch (no false overrun)",
      "dirty.py" not in delta)
# the dangerous case: a build that edits an ALREADY-DIRTY file must still be caught (content moved).
before2 = impl.baseline_snapshot(repo=tmp, runner=diff_runner)
open(os.path.join(tmp, "dirty.py"), "w").write("now ALSO edited by the build\n")
delta2 = impl.changed_delta(repo=tmp, before=before2, runner=diff_runner)
check("changed_delta CATCHES a build that edits an already-dirty file (content-hash, not path-set)",
      "dirty.py" in delta2)


print("\n=== S8.1 — happy path: approve → dispatch → verify → implemented AND surfaced-for-review ===")
s = fresh_suite()
intent = s.surface_build_intent("add a reversible thing", scope=["runtime/"],
                                consequence_class="decision_build")
sid = intent["id"]
check("build-intent carries intent=build + declared scope + class", s.is_build_intent(s.inbox.get(sid)))
seq = approve_seq(s, sid)
out = s.dispatch_decision(sid, seq,
                          launcher=good_launch(["runtime/implement.py"]),
                          verifier=lambda r: (True, "verified by use"))
check("dispatch closed on a verified build (status=implemented)", out["closed"] and out["status"] == "implemented")
check("the item's status lane is 'implemented'", s.inbox.get(sid)["status"] == "implemented")
check("operator `resolved` field was written ONLY by the operator approve (not by code)",
      s.inbox.get(sid)["resolved"] == "approve")
kinds = [e.get("kind") for e in s.store.events_since(-1)]
check("events narrate dispatch→implemented (W5)",
      "decision.dispatch" in kinds and "decision.implemented" in kinds)
# THE CONCEPTUAL CORRECTION — `implemented` is NOT a silent terminal: it ALSO surfaces a review item.
check("a decision.surfaced_for_review event was emitted (implemented ≠ silent close)",
      "decision.surfaced_for_review" in kinds)
review_sid = out.get("review_surfaced")
check("the close returned the surfaced review item's id", bool(review_sid))
review = s.inbox.get(review_sid)
check("the review item carries the changed-files diff + result summary + derived_from + review_of",
      review["payload"].get("changed_files") == ["runtime/implement.py"]
      and review["payload"].get("review_of") == sid
      and review["payload"].get("derived_from") == seq
      and "summary" in review["payload"])
check("the review item is a live escalation (resolved=None) for the OPERATOR to resolve",
      review.get("resolved") is None and review.get("status") == "inbox")
# CRITICAL: the success-review item must NOT be a build-intent — else approving it (the operator's
# 'looks good') would satisfy the dispatcher under a NEW seq and trigger a REBUILD (exactly-once is
# keyed on the OLD seq). It is a distinct, dispatcher-inert `build_result_review`.
check("the surfaced review item is NOT a build-intent (approving it reviews, never rebuilds)",
      s.is_build_intent(review) is False and review["payload"].get("kind") == "build_result_review")
# exactly-once intact: surfacing the review is part of the ONE dispatch, not a second decision.dispatch.
ndispatch = sum(1 for e in s.store.events_since(-1)
                if e.get("kind") == "decision.dispatch" and e.get("derived_from") == seq)
check("surfacing the review did NOT emit a second decision.dispatch (exactly-once intact)", ndispatch == 1)


print("\n=== S8.2 — governed refusals (deterministic, no confidence) ===")
s = fresh_suite()
intent = s.surface_build_intent("a build", scope=["runtime/"]); sid = intent["id"]
seq = approve_seq(s, sid)
raises("forged/missing seq refuses", lambda: s.dispatch_decision(sid, 999999))
raises("non-int derived_from refuses", lambda: s.dispatch_decision(sid, "approve"))
# bind mismatch: a real seq but for a DIFFERENT item.
intent2 = s.surface_build_intent("other", scope=["nodes/"]); sid2 = intent2["id"]
seq2 = approve_seq(s, sid2)
raises("bind mismatch (seq of another item) refuses", lambda: s.dispatch_decision(sid, seq2))
# non-build-intent approve: a plain review item the operator approved is not dispatchable.
plain = s.inbox.surface_review({"some": "review"}, origin="responsive")
pseq = approve_seq(s, plain)
raises("a non-build-intent approve refuses (the discriminator)", lambda: s.dispatch_decision(plain, pseq))
# LOCKED declared class never auto-dispatches.
locked = s.surface_build_intent("touch source data", scope=["data/"],
                                consequence_class="source_data")
lsid = locked["id"]; lseq = approve_seq(s, lsid)
raises("a LOCKED declared class never auto-dispatches", lambda: s.dispatch_decision(lsid, lseq))
check("a LOCKED refusal did NOT close the item", s.inbox.get(lsid)["status"] != "implemented")


print("\n=== S8.5 — exactly-once under stress (two overlapping fires) ===")
s = fresh_suite()
intent = s.surface_build_intent("once", scope=["runtime/"]); sid = intent["id"]
seq = approve_seq(s, sid)
first = s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/implement.py"]),
                            verifier=lambda r: (True, "ok"))
check("first dispatch ran", first["closed"])
raises("second dispatch of the same resolve seq REFUSES (decision.dispatch keyed on seq)",
       lambda: s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/implement.py"]),
                                   verifier=lambda r: (True, "ok")))
ndispatch = sum(1 for e in s.store.events_since(-1) if e.get("kind") == "decision.dispatch"
                and e.get("derived_from") == seq)
check("exactly ONE decision.dispatch event for the resolve seq", ndispatch == 1)


print("\n=== S8.3 — bad implementation caught (not closed; re-queued with reason) ===")
s = fresh_suite()
intent = s.surface_build_intent("a build that fails", scope=["runtime/"]); sid = intent["id"]
seq = approve_seq(s, sid)
out = s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/implement.py"]),
                          verifier=lambda r: (False, "the affected test fails"))
check("a failed verification does NOT close the item", not out.get("closed") and s.inbox.get(sid)["status"] != "implemented")
check("a new responsive review item carries the failure reason", "requeued" in out and out["requeued"])
req = s.inbox.get(out["requeued"])
check("the re-queued item carries the why", "verification failed" in (req["payload"].get("why", "")))


print("\n=== S8.3b — a build that itself fails to LAUNCH → loud re-queue (W7) ===")
s = fresh_suite()
intent = s.surface_build_intent("a build that crashes", scope=["runtime/"]); sid = intent["id"]
seq = approve_seq(s, sid)
def crash_launch(decision, *, repo):
    raise impl.LaunchError("timeout / crash")
out = s.dispatch_decision(sid, seq, launcher=crash_launch, verifier=lambda r: (True, "ok"))
check("a launch failure re-queues loud (never a silent no-op)", out.get("requeued") and not out["launched"])
check("the launch-failure item is not closed", s.inbox.get(sid)["status"] != "implemented")


print("\n=== S8.6 — scope overrun caught (not closed; surfaced back) ===")
s = fresh_suite()
intent = s.surface_build_intent("stay in runtime/", scope=["runtime/"]); sid = intent["id"]
seq = approve_seq(s, sid)
out = s.dispatch_decision(sid, seq,
                          launcher=good_launch(["runtime/ok.py", "nodes/sneaky.py"]),
                          verifier=lambda r: (True, "verified"))
check("a scope overrun does NOT close the item", not out.get("closed"))
check("the overrun is reported + re-queued", out.get("overrun") == ["nodes/sneaky.py"] and out.get("requeued"))


print("\n=== W4 Hole 4 — the close is guarded; an unverified close RAISES ===")
# the guard backstop: code_build is CONFIRM-posture, so confirmed=False (unverified) RAISES rather
# than silently writing `implemented`. We drive the guard directly to prove the floor.
from runtime.governance import guard as _guard
raises("guard('code_build', confirmed=False) RAISES (unverified close cannot write implemented)",
       lambda: _guard("code_build", do=lambda: "closed", confirmed=False, inbox=None))


print(f"\nALL {PASS} CHECKS PASS — the Decision→Implementation Wire backend (Group W) holds "
      f"its mechanisms: bind · discriminator · exactly-once · LOCKED pre-gate · verify-or-requeue · "
      f"scope-diff · guarded close that ALSO surfaces-for-review (implemented ≠ silent terminal; the "
      f"review item is dispatcher-inert so approving it never rebuilds). (Operator-only resolve "
      f"preserved; no confidence value anywhere.)")
