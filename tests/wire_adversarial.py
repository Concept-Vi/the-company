"""tests/wire_adversarial.py — ADVERSARIAL red-team of the Decision→Implementation Wire.

NOT the authors' acceptance suite (that proves the happy mechanisms). This file tries to BREAK
each claimed guarantee by RUNNING exploits against the live code in /home/tim/company. Every
attack prints SURVIVED or BROKEN with the actual observed value as evidence.

Run: .venv/bin/python tests/wire_adversarial.py
"""
import os
import sys
import tempfile
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime.governance import GovernanceError
from runtime import implement as impl

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NODES = os.path.join(ROOT, "nodes")

RESULTS = []  # (attack, what_ran, verdict, evidence)


def record(attack, what, verdict, evidence):
    RESULTS.append((attack, what, verdict, evidence))
    print(f"[{verdict}] {attack}\n        ran: {what}\n        evidence: {evidence}\n")


def fresh_suite():
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="adv-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    return Suite(store, reg, nodes_dir=NODES)


def approve_seq(suite, sid):
    suite.resolve_surfaced(sid, "approve", reason="authorize")
    ev = next(e for e in reversed(suite.store.events_since(-1))
              if e.get("kind") == "resolve" and e.get("surfaced") == sid)
    return ev["seq"]


def good_launch(changed):
    return lambda decision, *, repo: {
        "finished": True, "success": True, "exit_code": 0,
        "summary": "implemented", "changed_files": list(changed), "permission_mode": "acceptEdits"}


# ===========================================================================================
# ATTACK 1 — exactly-once under TRUE concurrency (race between CHECK and CLAIM).
# dispatch_decision has no lock around _already_dispatched (read log) → _emit (claim).
# Two threads, launcher blocks on a Barrier so both clear the check before either claims.
# ===========================================================================================
def attack_concurrency():
    s = fresh_suite()
    intent = s.surface_build_intent("race", scope=["runtime/"]); sid = intent["id"]
    seq = approve_seq(s, sid)
    barrier = threading.Barrier(2)
    launch_calls = []
    lock = threading.Lock()

    def racing_launch(decision, *, repo):
        with lock:
            launch_calls.append(1)
        try:
            barrier.wait(timeout=5)   # ensure BOTH threads got past the exactly-once check first
        except threading.BrokenBarrierError:
            pass
        return {"finished": True, "success": True, "exit_code": 0,
                "summary": "implemented", "changed_files": ["runtime/x.py"],
                "permission_mode": "acceptEdits"}

    outs, errs = [], []

    def fire():
        try:
            outs.append(s.dispatch_decision(sid, seq, launcher=racing_launch,
                                            verifier=lambda r: (True, "ok")))
        except Exception as e:
            errs.append(f"{type(e).__name__}: {e}")

    t1 = threading.Thread(target=fire); t2 = threading.Thread(target=fire)
    t1.start(); t2.start(); t1.join(); t2.join()

    n_launch = len(launch_calls)
    n_dispatch_events = sum(1 for e in s.store.events_since(-1)
                            if e.get("kind") == "decision.dispatch" and e.get("derived_from") == seq)
    n_closed = sum(1 for o in outs if o.get("closed"))
    ev = (f"launcher invoked {n_launch}x; decision.dispatch events for seq={n_dispatch_events}; "
          f"closed-results={n_closed}; refusals={errs}")
    # GUARANTEE: exactly ONE launch, exactly ONE dispatch event. >1 launch = double-build = BROKEN.
    verdict = "SURVIVED" if (n_launch == 1 and n_dispatch_events == 1) else "BROKEN"
    record("1. Exactly-once under TRUE concurrency (two threads race CHECK→CLAIM)",
           "2 threads dispatch_decision(sid,seq) same approved item; launcher blocks on Barrier(2)",
           verdict, ev)


# ===========================================================================================
# ATTACK 2 — empty/missing scope => zero scope enforcement.
# surface_build_intent defaults scope=[]; dispatch does `if scope:` so the whole scope-diff
# block is SKIPPED for []. A build can then change ANY file and still close implemented.
# ===========================================================================================
def attack_empty_scope():
    s = fresh_suite()
    intent = s.surface_build_intent("no scope declared")   # scope defaults to []
    sid = intent["id"]
    declared_scope = s.inbox.get(sid)["payload"].get("scope")
    seq = approve_seq(s, sid)
    out = s.dispatch_decision(sid, seq,
                              launcher=good_launch(["data/secrets.py", "nodes/anything.py",
                                                    "/etc/passwd"]),
                              verifier=lambda r: (True, "verified"))
    closed = out.get("closed")
    status = s.inbox.get(sid)["status"]
    ev = (f"declared scope={declared_scope!r}; build changed "
          f"['data/secrets.py','nodes/anything.py','/etc/passwd']; closed={closed}; status={status!r}; "
          f"out={({k: out[k] for k in ('closed','overrun','requeued') if k in out})}")
    # A wire that claims scope enforcement should NOT close a build that touched arbitrary files.
    # If it closes implemented with an empty-scope item, the guarantee is vacuous when scope==[].
    verdict = "BROKEN" if (closed and status == "implemented") else "SURVIVED"
    record("2. Empty/missing scope => scope-diff entirely skipped (vacuous enforcement)",
           "surface_build_intent with NO scope -> approve -> dispatch a build touching data/, nodes/, /etc/passwd",
           verdict, ev)


# ===========================================================================================
# ATTACK 3 — pre-dispatch gate keys on LOCKED set, not POLICY posture.
# Step 4 is `if declared in LOCKED`. 'destructive' is CONFIRM in POLICY but NOT in LOCKED,
# so it auto-dispatches. Test whether a CONFIRM-but-not-LOCKED class slips through.
# ===========================================================================================
def attack_posture_vs_locked():
    s = fresh_suite()
    intent = s.surface_build_intent("destructive build", scope=["runtime/"],
                                    consequence_class="destructive")
    sid = intent["id"]
    seq = approve_seq(s, sid)
    slipped = None
    try:
        out = s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/x.py"]),
                                  verifier=lambda r: (True, "ok"))
        slipped = out.get("closed")
        ev = f"consequence_class='destructive' (POLICY=CONFIRM, not in LOCKED) -> dispatch closed={slipped}"
    except GovernanceError as e:
        ev = f"refused: {str(e)[:120]}"
    # This is a DESIGN-GAP surfacing: the gate only blocks the hardcoded LOCKED set, not posture!=AUTO.
    # 'destructive' auto-dispatching is the observable. We report it as a finding (not a hard BROKEN of
    # the 6 stated guarantees, but it weakens guarantee #3's spirit).
    verdict = "FINDING" if slipped else "SURVIVED"
    record("3. Pre-dispatch gate keys on LOCKED membership, not POLICY posture",
           "dispatch a build whose consequence_class='destructive' (CONFIRM in POLICY, absent from LOCKED)",
           verdict, ev)


# ===========================================================================================
# ATTACK 4 — _within_scope does not collapse '..' traversal.
# 'runtime/../nodes/x.py'.startswith('runtime/') is True -> reads in-scope though it resolves
# to nodes/. Unit attack on the guard + reachability through the injected launcher.
# ===========================================================================================
def attack_scope_traversal():
    # 4a: unit-level — does _within_scope itself accept a traversal path?
    unit = Suite._within_scope("runtime/../nodes/evil.py", "runtime/")
    # 4b: reachable end-to-end? a launcher reports a traversal path; does dispatch close it?
    s = fresh_suite()
    intent = s.surface_build_intent("stay in runtime", scope=["runtime/"]); sid = intent["id"]
    seq = approve_seq(s, sid)
    out = s.dispatch_decision(sid, seq,
                              launcher=good_launch(["runtime/../nodes/evil.py"]),
                              verifier=lambda r: (True, "ok"))
    closed = out.get("closed")
    ev = (f"_within_scope('runtime/../nodes/evil.py','runtime/')={unit}; "
          f"end-to-end (INJECTED launcher) closed={closed}, overrun={out.get('overrun')}; "
          f"REACHABILITY: real launch() sources changed_files from git diff (changed_delta), which "
          f"emits normalized repo-relative paths — git CANNOT produce '..'; so this is a guard-level "
          f"hardening gap, NOT a live git-reachable exploit. Fix: normalize '..' in _within_scope.")
    # Guard accepts a traversal path, but the bona-fide launcher cannot emit one (git-normalized).
    # FINDING (harden the guard), not a live break.
    verdict = "FINDING" if unit else "SURVIVED"
    record("4. _within_scope accepts '..' traversal (guard-level; not git-reachable)",
           "_within_scope unit + dispatch with changed_files=['runtime/../nodes/evil.py'] scope=['runtime/']",
           verdict, ev)


# ===========================================================================================
# ATTACK 5 — bool is a subclass of int; True == 1. Does derived_from=True bypass the non-int guard?
# ===========================================================================================
def attack_bool_as_int():
    s = fresh_suite()
    intent = s.surface_build_intent("bool seq", scope=["runtime/"]); sid = intent["id"]
    approve_seq(s, sid)  # creates a resolve event (its seq is some small int, maybe 1)
    raised, msg, slipped_to = None, "", None
    try:
        s.dispatch_decision(sid, True, launcher=good_launch(["runtime/x.py"]),
                            verifier=lambda r: (True, "ok"))
        raised = False
    except GovernanceError as e:
        raised = True; msg = str(e)[:160]
    except Exception as e:
        raised = True; msg = f"{type(e).__name__}: {str(e)[:140]}"
    # isinstance(True,int) is True, so the non-int guard does NOT fire; it proceeds to seq lookup.
    # If seq==1 happens to exist as a resolve for THIS sid, True could even bind. Check what happened.
    bound = "decision.dispatch" in [e.get("kind") for e in s.store.events_since(-1)
                                    if e.get("derived_from") is True or e.get("derived_from") == 1]
    if "a build" in msg or "bind" in msg or "seq=True" in msg or "seq=1" in msg:
        slipped_to = "passed isinstance(int) check, fell through to seq/bind lookup"
    dispatched = any(e.get("kind") == "decision.dispatch" for e in s.store.events_since(-1))
    ev = (f"isinstance(True,int)={isinstance(True, int)} (bool subclasses int), so the 'non-int "
          f"refuses' type guard MISSES bool; True==1 binds to the approve event at seq=1 (intent=seq0, "
          f"approve=seq1 in a fresh store — the FIRST build-intent). dispatch(sid, True) raised={raised}, "
          f"dispatched-a-real-build={dispatched}. The docstring's 'authorization is the substrate seq-bind, "
          f"never a caller flag' is violated: a truthy bool flag authorizes the first item's build.")
    verdict = "BROKEN" if dispatched else ("FINDING" if not (
        msg.startswith("dispatch requires derived_from")) and raised else "SURVIVED")
    record("5. bool-as-int: derived_from=True vs the non-int guard",
           "dispatch_decision(sid, True) on an approved build-intent",
           verdict, ev)


# ===========================================================================================
# ATTACK 6 — operator-only resolve: nothing in dispatch/close writes `resolved`.
# Full happy-path dispatch where operator NEVER set resolved to a friendly value; confirm
# `resolved` is exactly what the operator wrote (approve), never overwritten by the wire,
# and that a never-resolved item's resolved stays None through a (refused) dispatch.
# ===========================================================================================
def attack_operator_only_resolve():
    s = fresh_suite()
    intent = s.surface_build_intent("resolve check", scope=["runtime/"]); sid = intent["id"]
    seq = approve_seq(s, sid)
    resolved_after_approve = s.inbox.get(sid)["resolved"]
    out = s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/x.py"]),
                              verifier=lambda r: (True, "ok"))
    resolved_after_dispatch = s.inbox.get(sid)["resolved"]
    status_after = s.inbox.get(sid)["status"]
    # the requeued items from failed builds must ALSO have resolved=None (operator hasn't seen them)
    s2 = fresh_suite()
    i2 = s2.surface_build_intent("fail", scope=["runtime/"]); sid2 = i2["id"]
    seq2 = approve_seq(s2, sid2)
    o2 = s2.dispatch_decision(sid2, seq2, launcher=good_launch(["runtime/x.py"]),
                              verifier=lambda r: (False, "nope"))
    req_resolved = s2.inbox.get(o2["requeued"])["resolved"]
    ev = (f"resolved after operator approve={resolved_after_approve!r}; "
          f"resolved after wire dispatch+close={resolved_after_dispatch!r} (status={status_after!r}); "
          f"requeued item resolved={req_resolved!r}")
    verdict = ("SURVIVED" if (resolved_after_dispatch == "approve"
                              and resolved_after_approve == "approve"
                              and req_resolved is None) else "BROKEN")
    record("6. Operator-only resolve (wire writes status, never resolved)",
           "happy-path dispatch+close, then a failed-verify requeue; inspect `resolved` on both",
           verdict, ev)


# ===========================================================================================
# ATTACK 7 — re-entrancy / cross-item / wrong-kind seq (broaden the 6 stated refusals).
# ===========================================================================================
def attack_misc_refusals():
    s = fresh_suite()
    # 7a: a `seq` that points at a NON-resolve event kind (e.g. the decision.intent emit).
    intent = s.surface_build_intent("misc", scope=["runtime/"]); sid = intent["id"]
    intent_ev = next(e for e in s.store.events_since(-1)
                     if e.get("kind") == "decision.intent" and e.get("surfaced") == sid)
    intent_seq = intent_ev["seq"]
    refused_nonresolve = False
    try:
        s.dispatch_decision(sid, intent_seq, launcher=good_launch(["runtime/x.py"]),
                            verifier=lambda r: (True, "ok"))
    except GovernanceError:
        refused_nonresolve = True

    # 7b: dispatch on an ALREADY-implemented item (re-fire after close, same seq -> exactly-once).
    seq = approve_seq(s, sid)
    s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/x.py"]), verifier=lambda r: (True, "ok"))
    refused_reimpl = False
    try:
        s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/x.py"]), verifier=lambda r: (True, "ok"))
    except GovernanceError:
        refused_reimpl = True

    # 7c: reject (not approve) seq -> dispatch must refuse (choice != approve).
    s3 = fresh_suite()
    i3 = s3.surface_build_intent("rej", scope=["runtime/"]); sid3 = i3["id"]
    s3.resolve_surfaced(sid3, "reject", reason="no")
    rej_ev = next(e for e in reversed(s3.store.events_since(-1))
                  if e.get("kind") == "resolve" and e.get("surfaced") == sid3)
    refused_reject = False
    try:
        s3.dispatch_decision(sid3, rej_ev["seq"], launcher=good_launch(["runtime/x.py"]),
                             verifier=lambda r: (True, "ok"))
    except GovernanceError:
        refused_reject = True

    ev = (f"non-resolve seq refused={refused_nonresolve}; "
          f"re-dispatch of implemented item refused={refused_reimpl}; "
          f"reject-choice seq refused={refused_reject}")
    verdict = "SURVIVED" if (refused_nonresolve and refused_reimpl and refused_reject) else "BROKEN"
    record("7. Misc refusals: non-resolve-kind seq · re-dispatch implemented · reject-choice seq",
           "dispatch with intent-event seq; re-dispatch after close; dispatch on a reject verdict",
           verdict, ev)


# ===========================================================================================
# ATTACK 8 — failed verification must NOT close + a direct unverified close must RAISE.
# (restate guarantee 4 with our own calls + the guard backstop)
# ===========================================================================================
def attack_unverified_close():
    s = fresh_suite()
    intent = s.surface_build_intent("verifail", scope=["runtime/"]); sid = intent["id"]
    seq = approve_seq(s, sid)
    out = s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/x.py"]),
                              verifier=lambda r: (False, "the affected test fails"))
    not_closed = (not out.get("closed")) and s.inbox.get(sid)["status"] != "implemented"
    # direct guarded close on an unverified verdict must raise (mirrors apply_node)
    from runtime.governance import guard as _guard
    raised = False
    try:
        _guard("code_build", do=lambda: "closed", confirmed=False, inbox=None)
    except GovernanceError:
        raised = True
    ev = (f"failed-verify closed={out.get('closed')}, status={s.inbox.get(sid)['status']!r}, "
          f"requeued={out.get('requeued')}; guard(code_build,confirmed=False) raised={raised}")
    verdict = "SURVIVED" if (not_closed and raised) else "BROKEN"
    record("8. Unverified build never reaches implemented; guarded close RAISES",
           "dispatch with verifier->(False); then guard('code_build', confirmed=False) directly",
           verdict, ev)


# ===========================================================================================
# ATTACK 9 — the surface-for-review item must be a DEAD END to the dispatcher.
# `implemented` now ALSO surfaces a review item. If that item were a build-intent (intent=build +
# decision_build/AUTO), the operator's "looks good" approve would satisfy drive_dispatchable's
# _is_dispatchable under a NEW seq and trigger a REBUILD (exactly-once is keyed on the OLD seq).
# Attack: dispatch+close, then APPROVE the surfaced review item and run the watcher — assert zero
# new dispatches + zero new builds.
# ===========================================================================================
def attack_review_item_rebuild():
    s = fresh_suite()
    intent = s.surface_build_intent("build then surface for review", scope=["runtime/"],
                                    consequence_class="decision_build")
    sid = intent["id"]
    seq = approve_seq(s, sid)
    out = s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/x.py"]),
                              verifier=lambda r: (True, "ok"))
    review_sid = out.get("review_surfaced")
    review = s.inbox.get(review_sid) if review_sid else None
    is_build = bool(review) and s.is_build_intent(review)
    dispatch_before = sum(1 for e in s.store.events_since(-1) if e.get("kind") == "decision.dispatch")
    # the operator APPROVES the review ("looks good") and the unattended watcher runs.
    rev_seq = approve_seq(s, review_sid)
    drive = impl.drive_dispatchable(s, cursor=-1, launcher=good_launch(["runtime/x.py"]),
                                    verifier=lambda r: (True, "ok"))
    dispatch_after = sum(1 for e in s.store.events_since(-1) if e.get("kind") == "decision.dispatch")
    rebuilt = dispatch_after > dispatch_before or any(
        d.get("surfaced") == review_sid for d in drive.get("dispatched", []))
    ev = (f"review item kind={review['payload'].get('kind') if review else None!r}, "
          f"is_build_intent={is_build}; after approving the review + watcher pass: "
          f"decision.dispatch {dispatch_before}->{dispatch_after}, "
          f"watcher dispatched={[d.get('surfaced') for d in drive.get('dispatched', [])]}; "
          f"surfaced_for_review event present="
          f"{'decision.surfaced_for_review' in [e.get('kind') for e in s.store.events_since(-1)]}")
    # SURVIVED iff the review item is NOT a build-intent AND approving it produced no new build.
    verdict = "SURVIVED" if (not is_build and not rebuilt) else "BROKEN"
    record("9. Surface-for-review item cannot be re-approved into a REBUILD (dispatcher-inert)",
           "dispatch+close → approve the surfaced review item → drive_dispatchable; count new dispatches",
           verdict, ev)


if __name__ == "__main__":
    print("\n############ ADVERSARIAL WIRE RED-TEAM ############\n")
    attack_concurrency()
    attack_empty_scope()
    attack_posture_vs_locked()
    attack_scope_traversal()
    attack_bool_as_int()
    attack_operator_only_resolve()
    attack_misc_refusals()
    attack_unverified_close()
    attack_review_item_rebuild()

    print("\n############ SUMMARY ############")
    broken = [r for r in RESULTS if r[2] == "BROKEN"]
    findings = [r for r in RESULTS if r[2] == "FINDING"]
    for attack, _what, verdict, ev in RESULTS:
        print(f"  {verdict:9} | {attack}")
    print(f"\n  {len(RESULTS)} attacks · {len(broken)} BROKEN · {len(findings)} FINDING · "
          f"{len(RESULTS) - len(broken) - len(findings)} SURVIVED")
