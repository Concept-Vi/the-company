"""tests/wire_loop_acceptance.py — the UNATTENDED trigger (Group W · W6/W7 · scenario S8 part 1 + 7).

Proves the WIRE-LOOP seam: a recorded operator decision is implemented with NO human re-prompt.
The WIRE-BE backend (`suite.dispatch_decision`) is DONE; this proves the CALLER —
`runtime/implement.drive_dispatchable` (the watcher pass) + `resurface_crashed` — closes the circuit:

  surface a build-intent → operator approve (simulating /api/resolve) → run the watcher step
  (NO other human action) → the item reaches status=implemented, EXACTLY ONE dispatch.

S8 parts covered here (deterministic, no confidence value):
  1. Happy path UNATTENDED: approve → drive_dispatchable (no re-prompt) → status=implemented; the
     operator `resolved` field was written ONLY by the operator approve (operator-only preserved).
  7. Concurrency cap: N>cap approves → exactly `cap` dispatched this pass, the remainder DEFERRED
     loud (a decision.deferred event + the returned deferred list); a SECOND pass drains the rest;
     no silent truncation; no verdict double-launched.
  + Crashed-mid-flight: a decision.dispatch claim with NO terminal event → re-surfaced LOUD (a new
    responsive review item + a decision.crashed marker), never silently dropped, never re-launched
    (exactly-once); the re-surface is itself idempotent across passes.
  + Exactly-once across passes: re-running drive_dispatchable over the same approve does NOT re-launch
    (the decision.dispatch event is the guarantee, not the cursor).
  + Operator-only: the watcher NEVER writes `resolved` — only the `status` lane.

Run: .venv/bin/python tests/wire_loop_acceptance.py
"""
import os
import sys
import tempfile

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
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="wireloop-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    return Suite(store, reg, nodes_dir=NODES)


def operator_approve(suite, sid):
    """Simulate the OPERATOR's /api/resolve approve (the ONLY terminal-verdict writer) and return the
    resolve event's unique seq — the watcher reads this from the substrate, no re-prompt."""
    suite.resolve_surfaced(sid, "approve", reason="authorize this build")
    ev = next(e for e in reversed(suite.store.events_since(-1))
              if e.get("kind") == "resolve" and e.get("surfaced") == sid)
    return ev["seq"]


# an injected launcher/verifier = a deterministic "Claude Code result" so no real session is burned.
def good_launch(changed):
    return lambda decision, *, repo: {
        "finished": True, "success": True, "exit_code": 0,
        "summary": "implemented", "changed_files": list(changed), "permission_mode": "acceptEdits"}


def ok_verify(_r):
    return (True, "verified by use")


print("\n=== S8.1 — UNATTENDED happy path: approve → watcher (NO re-prompt) → implemented ===")
s = fresh_suite()
intent = s.surface_build_intent("add a reversible thing", scope=["runtime/"],
                                consequence_class="decision_build")
sid = intent["id"]
seq = operator_approve(s, sid)          # the ONLY human action: the operator's approve.
# the watcher pass — NO further human action. It reads the verdict from the substrate and drives it.
out = impl.drive_dispatchable(s, cursor=-1,
                              launcher=good_launch(["runtime/implement.py"]),
                              verifier=ok_verify)
check("watcher dispatched exactly the one approved build-intent", len(out["dispatched"]) == 1)
check("the dispatched item reached status=implemented (unattended)", s.inbox.get(sid)["status"] == "implemented")
check("the watcher's own dispatch result closed", out["dispatched"][0]["result"]["closed"])
ndispatch = sum(1 for e in s.store.events_since(-1)
                if e.get("kind") == "decision.dispatch" and e.get("derived_from") == seq)
check("EXACTLY ONE decision.dispatch event for the resolve seq", ndispatch == 1)
check("operator `resolved` field was written ONLY by the operator approve (watcher never wrote it)",
      s.inbox.get(sid)["resolved"] == "approve")
check("watcher advanced the cursor past the consumed verdict", out["cursor"] >= seq)


print("\n=== exactly-once across passes: a SECOND watcher pass does NOT re-launch ===")
# re-run the watcher from the SAME cursor (-1) — the decision.dispatch event (not the cursor) must
# refuse a second launch of the same approve.
out2 = impl.drive_dispatchable(s, cursor=-1, launcher=good_launch(["runtime/implement.py"]),
                               verifier=ok_verify)
check("second pass dispatched NOTHING (exactly-once on the event log, not the cursor)",
      len(out2["dispatched"]) == 0)
ndispatch2 = sum(1 for e in s.store.events_since(-1)
                 if e.get("kind") == "decision.dispatch" and e.get("derived_from") == seq)
check("STILL exactly one decision.dispatch after a re-run", ndispatch2 == 1)


print("\n=== S8.7 — concurrency cap: N>cap → cap dispatched, remainder DEFERRED loud ===")
s = fresh_suite()
CAP = 2
N = 5
sids, seqs = [], []
for i in range(N):
    it = s.surface_build_intent(f"build {i}", scope=["runtime/"], consequence_class="decision_build")
    sids.append(it["id"])
    seqs.append(operator_approve(s, it["id"]))
out = impl.drive_dispatchable(s, cursor=-1, cap=CAP,
                              launcher=good_launch(["runtime/x.py"]), verifier=ok_verify)
check(f"exactly {CAP} dispatched in the first pass (cap respected)", len(out["dispatched"]) == CAP)
check(f"the remaining {N - CAP} are DEFERRED (visibly queued, not silently dropped)",
      len(out["deferred"]) == N - CAP)
deferred_events = [e for e in s.store.events_since(-1) if e.get("kind") == "decision.deferred"]
check("each deferred verdict surfaced a loud decision.deferred event (no silent truncation)",
      len(deferred_events) == N - CAP)
implemented_1 = sum(1 for x in sids if s.inbox.get(x)["status"] == "implemented")
check(f"after pass 1, exactly {CAP} items are implemented", implemented_1 == CAP)
# the cursor did NOT advance past a deferred verdict → next pass re-offers them.
check("cursor stayed at/below the first deferred seq (deferred verdicts re-offered next pass)",
      out["cursor"] < seqs[CAP])
# drain the rest across subsequent passes (the unattended loop fires again).
out_b = impl.drive_dispatchable(s, cursor=out["cursor"], cap=CAP,
                                launcher=good_launch(["runtime/x.py"]), verifier=ok_verify)
out_c = impl.drive_dispatchable(s, cursor=out_b["cursor"], cap=CAP,
                                launcher=good_launch(["runtime/x.py"]), verifier=ok_verify)
implemented_all = sum(1 for x in sids if s.inbox.get(x)["status"] == "implemented")
check("all N items eventually implemented across passes (nothing silently lost)", implemented_all == N)
total_dispatch = sum(1 for e in s.store.events_since(-1) if e.get("kind") == "decision.dispatch")
check("exactly N decision.dispatch events total (none double-launched under the cap)", total_dispatch == N)


print("\n=== crashed mid-flight → re-surfaced LOUD (never silently dropped, never re-launched) ===")
s = fresh_suite()
intent = s.surface_build_intent("a build that will crash mid-flight", scope=["runtime/"],
                                consequence_class="decision_build")
sid = intent["id"]
seq = operator_approve(s, sid)
# Simulate a crash AFTER the durable claim but BEFORE any terminal event: emit the decision.dispatch
# claim ourselves (exactly what dispatch_decision does first) + set the item presented, then DIE.
s._emit("decision.dispatch", "claimed then crashed (simulated host death before terminal)",
        surfaced=sid, derived_from=seq, consequence_class="decision_build", scope=["runtime/"])
s.inbox.set_status(sid, "presented")
# a fresh watcher pass: it must NOT re-launch (exactly-once) but MUST re-surface loud.
out = impl.drive_dispatchable(s, cursor=-1, launcher=good_launch(["runtime/x.py"]), verifier=ok_verify)
check("the crashed dispatch was re-surfaced loud (one new responsive review item)",
      len(out["crashed_resurfaced"]) == 1)
req = s.inbox.get(out["crashed_resurfaced"][0])
check("the re-surfaced item carries the crash reason (no silent dead end)",
      "crashed mid-flight" in (req["payload"].get("why", "")) and req["payload"].get("crashed_dispatch"))
ndispatch = sum(1 for e in s.store.events_since(-1)
                if e.get("kind") == "decision.dispatch" and e.get("derived_from") == seq)
check("the crashed dispatch was NOT re-launched (still exactly one decision.dispatch — exactly-once)",
      ndispatch == 1)
crashed_markers = [e for e in s.store.events_since(-1) if e.get("kind") == "decision.crashed"]
check("a durable decision.crashed marker was written (idempotent re-surface)", len(crashed_markers) == 1)
# a SECOND pass must NOT re-surface the same crash again (the marker makes it exactly-once).
out2 = impl.drive_dispatchable(s, cursor=out["cursor"], launcher=good_launch(["runtime/x.py"]),
                               verifier=ok_verify)
check("a second pass does NOT re-surface the same crash (marker → exactly-once re-surface)",
      len(out2["crashed_resurfaced"]) == 0)


print("\n=== operator-only + non-AUTO surfacing (watcher never resolves; never auto-runs CONFIRM) ===")
s = fresh_suite()
# a LOCKED-class build-intent the operator approved: the watcher must NOT dispatch it (it surfaces).
locked = s.surface_build_intent("touch source data", scope=["data/"], consequence_class="source_data")
lsid = locked["id"]
operator_approve(s, lsid)
out = impl.drive_dispatchable(s, cursor=-1, launcher=good_launch(["data/x.py"]), verifier=ok_verify)
check("the watcher did NOT auto-dispatch a non-AUTO (LOCKED) class", len(out["dispatched"]) == 0)
check("the LOCKED item did NOT reach implemented (left for the operator)",
      s.inbox.get(lsid)["status"] != "implemented")
check("the watcher never wrote `resolved` beyond the operator's own approve",
      s.inbox.get(lsid)["resolved"] == "approve")
# a non-build-intent approve (a plain criterion) is also not the watcher's auto-dispatch job.
plain = s.inbox.surface_review({"some": "review"}, origin="responsive")
operator_approve(s, plain)
out2 = impl.drive_dispatchable(s, cursor=-1, launcher=good_launch(["runtime/x.py"]), verifier=ok_verify)
check("a non-build-intent approve is not auto-dispatched (the discriminator holds)",
      not any(d["surfaced"] == plain for d in out2["dispatched"]))


print(f"\nALL {PASS} CHECKS PASS — the UNATTENDED trigger (W6) closes the circuit: a recorded "
      f"operator approve is implemented with NO human re-prompt; the §W7 cap is respected + the "
      f"remainder deferred loud; a crashed mid-flight dispatch is re-surfaced loud, never re-launched "
      f"(exactly-once); operator-only resolve is preserved (the watcher writes status, never resolved).")
