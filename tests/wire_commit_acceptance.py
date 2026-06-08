"""tests/wire_commit_acceptance.py — the wire's GIT CHECKPOINT (Tim's safety mandate before arming).

Proves: every autonomous build the wire ACCEPTS (verified + in-scope + FORM-ok) is committed as a
SINGLE revertible `[self-build]` git commit BEFORE the close marks it `implemented` — so the build is
always one `git revert <sha>` away from undone. A build that fails any gate, is out of scope, can't be
committed, or is empty (plan-mode) does NOT commit and does NOT close.

This is MODEL-FREE + REPO-SAFE: the `claude -p` launcher AND the git committer are INJECTED stubs, so
no real subprocess + no real commit touches the live /home/tim/company repo. The store is a fresh temp
dir per suite (FsStore under tempfile.mkdtemp) — never the live store.

Covered:
  (i)   a verified + in-scope build COMMITS exactly its changed_delta paths with a [self-build] message
        + records the sha (on the item, the decision.implemented event, the review item, the return).
  (ii)  a build that FAILS a verify gate, or is OUT OF SCOPE, does NOT commit (committer never called;
        status not implemented; re-surfaced).
  (iii) a COMMIT FAILURE (committer returns None) fails loud: re-surfaced as a retryable build-intent
        via a decision.verify terminal event (NOT a novel kind → not read as crashed); never implemented.
  (iv)  pre-existing UNRELATED dirty files are NOT in the build's commit (the committer is handed ONLY
        the build's changed_delta — the concurrent-writer isolation, asserted on the staged paths).
  (v)   plan-mode (unarmed) yields an empty delta → the critic vetoes it upstream → not implemented +
        committer never called; and even a forced empty delta at the checkpoint surfaces back (no empty
        commit). The default permission posture is "plan" (read-only) — confirmed unchanged.
  + the real default committer (_self_build_commit) reuses _git_self_commit with the [self-build] prefix
    (path-scoped add) — verified by a fake-repo round-trip (a temp git repo, NOT the live one).

Run: .venv/bin/python tests/wire_commit_acceptance.py
"""
import os
import subprocess
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
    store = FsStore(os.path.join(tempfile.mkdtemp(prefix="wire-commit-"), "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    return Suite(store, reg, nodes_dir=NODES)


def approve_seq(suite, sid):
    suite.resolve_surfaced(sid, "approve", reason="authorize this build")
    ev = next(e for e in reversed(suite.store.events_since(-1))
              if e.get("kind") == "resolve" and e.get("surfaced") == sid)
    return ev["seq"]


def good_launch(changed):
    return lambda decision, *, repo: {
        "finished": True, "success": True, "exit_code": 0,
        "summary": "implemented the thing", "changed_files": list(changed),
        "permission_mode": "acceptEdits"}


class RecordingCommitter:
    """A stub `committer(paths, msg) -> sha|None`: records every call (paths + msg) so the test can
    assert WHAT was staged (the build's changed_delta, NOT the concurrent writer's dirty files) and
    the [self-build] message shape, returning a deterministic fake sha — no real git on the live repo.
    `sha=None` simulates a commit FAILURE (case iii)."""
    def __init__(self, sha="a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0"):
        self.calls = []
        self._sha = sha

    def __call__(self, paths, msg):
        self.calls.append({"paths": list(paths), "msg": msg})
        return self._sha


# =============================================================================================
print("\n=== (i) verified + in-scope build → COMMITS exactly changed_delta with [self-build] + records sha ===")
s = fresh_suite()
intent = s.surface_build_intent("Add a git-safe revertible thing to the wire", scope=["runtime/"],
                                consequence_class="decision_build")
sid = intent["id"]
seq = approve_seq(s, sid)
committer = RecordingCommitter()
delta = ["runtime/implement.py", "runtime/suite.py"]
out = s.dispatch_decision(sid, seq,
                          launcher=good_launch(delta),
                          verifier=lambda r: (True, "verified by use"),
                          committer=committer)
check("dispatch closed on a verified build (status=implemented)", out["closed"] and out["status"] == "implemented")
check("the committer was called EXACTLY once (one checkpoint per accepted build)", len(committer.calls) == 1)
call = committer.calls[0]
check("the committer was handed EXACTLY the build's changed_delta paths (not git add -A)",
      sorted(call["paths"]) == sorted(delta))
check("the commit message carries the sid + intent summary",
      call["msg"].startswith(f"{sid}:") and "revertible thing" in call["msg"])
check("the close returned the checkpoint sha", out.get("commit") == committer._sha)
check("the sha is recorded on the build item", s.inbox.get(sid).get("commit") == committer._sha)
# the sha rides the events + the review item so a revert path can find it without re-deriving.
impl_ev = next(e for e in s.store.events_since(-1) if e.get("kind") == "decision.implemented")
check("the decision.implemented event carries the checkpoint sha (commit=...)", impl_ev.get("commit") == committer._sha)
review = s.inbox.get(out["review_surfaced"])
check("the surfaced review item carries the checkpoint sha + a `git revert` hint",
      review["payload"].get("commit") == committer._sha
      and f"git revert {committer._sha}" in review["payload"].get("why", ""))
# the [self-build] prefix is applied by the DEFAULT committer; here the stub records the raw msg, and
# the prefix is proven separately below against a fake repo.


# =============================================================================================
print("\n=== (iv) concurrent-writer isolation: a pre-existing dirty file is NOT in the build's commit ===")
# The build's changed_delta (from launch()'s baseline_snapshot diff) already EXCLUDES pre-existing dirty
# files (proven in wire_acceptance.py at the changed_delta level). Here we prove the CHECKPOINT commits
# ONLY that delta: the committer is handed the build's delta, never the concurrent writer's dirty paths.
s = fresh_suite()
intent = s.surface_build_intent("isolate the delta", scope=["runtime/"],
                                consequence_class="decision_build")
sid = intent["id"]
seq = approve_seq(s, sid)
committer = RecordingCommitter()
# the build changed ONLY runtime/x.py; design/blueprint/concurrent.json is a concurrent writer's dirty
# file — it is NOT in changed_files (the launcher reports git ground truth = the build's delta).
out = s.dispatch_decision(sid, seq,
                          launcher=good_launch(["runtime/x.py"]),
                          verifier=lambda r: (True, "ok"),
                          committer=committer)
staged = committer.calls[0]["paths"]
check("the committer staged ONLY the build's file", staged == ["runtime/x.py"])
check("the concurrent writer's dirty design/blueprint file is NOT in the commit",
      not any("design/blueprint" in p for p in staged))


# =============================================================================================
print("\n=== (ii-a) a build that FAILS verification does NOT commit (committer never called) ===")
s = fresh_suite()
intent = s.surface_build_intent("a build that fails", scope=["runtime/"]); sid = intent["id"]
seq = approve_seq(s, sid)
committer = RecordingCommitter()
out = s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/x.py"]),
                          verifier=lambda r: (False, "the affected test fails"),
                          committer=committer)
check("a failed verification does NOT close the item", not out.get("closed") and s.inbox.get(sid)["status"] != "implemented")
check("the committer was NEVER called on a verify-fail (no commit before the gates pass)", committer.calls == [])
check("a new responsive review item carries the failure reason", out.get("requeued"))


# =============================================================================================
print("\n=== (ii-b) an OUT-OF-SCOPE build does NOT commit (committer never called) ===")
s = fresh_suite()
intent = s.surface_build_intent("stay in runtime/", scope=["runtime/"]); sid = intent["id"]
seq = approve_seq(s, sid)
committer = RecordingCommitter()
out = s.dispatch_decision(sid, seq,
                          launcher=good_launch(["runtime/ok.py", "nodes/sneaky.py"]),
                          verifier=lambda r: (True, "verified"),
                          committer=committer)
check("a scope overrun does NOT close the item", not out.get("closed") and out.get("overrun") == ["nodes/sneaky.py"])
check("the committer was NEVER called on a scope overrun (commit is AFTER the scope-diff)", committer.calls == [])


# =============================================================================================
print("\n=== (iii) a COMMIT FAILURE fails loud: re-surfaced, NOT implemented, terminal event = decision.verify ===")
s = fresh_suite()
intent = s.surface_build_intent("a build whose checkpoint fails", scope=["runtime/"]); sid = intent["id"]
seq = approve_seq(s, sid)
fail_committer = RecordingCommitter(sha=None)   # the commit fails (None)
out = s.dispatch_decision(sid, seq, launcher=good_launch(["runtime/x.py"]),
                          verifier=lambda r: (True, "verified"),
                          committer=fail_committer)
check("a commit failure does NOT close the item (a build that can't be checkpointed is not safe-closed)",
      not out.get("closed") and s.inbox.get(sid)["status"] != "implemented")
check("the committer WAS called (it tried) and reported failure", len(fail_committer.calls) == 1)
check("the build is re-surfaced as a retryable item carrying the checkpoint-failure reason",
      out.get("requeued") and out.get("checkpoint_failed"))
req = s.inbox.get(out["requeued"])
check("the re-queued item is a retryable build-intent with checkpoint_failed + a why",
      s.is_build_intent(req) and req["payload"].get("checkpoint_failed")
      and "git checkpoint FAILED" in req["payload"].get("why", ""))
# CRITICAL: the commit-fail event MUST be a recognized terminal kind (decision.verify), else
# resurface_crashed would read the decision.dispatch claim as crashed-mid-flight and double-surface it.
kinds = [e.get("kind") for e in s.store.events_since(-1)]
check("the commit-fail emitted a decision.verify (terminal) event — not a novel kind",
      "decision.verify" in kinds and "decision.dispatch" in kinds)
# prove it is NOT seen as crashed: resurface_crashed finds nothing to re-surface for this seq.
crashed = impl.resurface_crashed(s)
check("resurface_crashed does NOT treat the commit-failed dispatch as crashed (terminal event present)",
      crashed == [])


# =============================================================================================
print("\n=== (v-a) a forced EMPTY change-set at the checkpoint surfaces back (no empty commit) ===")
s = fresh_suite()
intent = s.surface_build_intent("empty build", scope=["runtime/"]); sid = intent["id"]
seq = approve_seq(s, sid)
committer = RecordingCommitter()
# inject a verifier that passes on an EMPTY change-set (bypasses the default critic that would veto it),
# so we reach the checkpoint with nothing to commit — it must surface back, never create an empty commit.
out = s.dispatch_decision(sid, seq, launcher=good_launch([]),
                          verifier=lambda r: (True, "verified (but empty)"),
                          committer=committer)
check("an empty change-set at checkpoint does NOT close", not out.get("closed") and s.inbox.get(sid)["status"] != "implemented")
check("the committer was NEVER called on an empty delta (no empty checkpoint commit)", committer.calls == [])
check("the empty build is re-surfaced loud", out.get("requeued"))

print("\n=== (v-b) plan-mode (the unarmed default) → empty delta → critic veto → not implemented ===")
# The DEFAULT permission posture is "plan" (read-only) — confirmed unchanged. A real plan-mode run
# changes NOTHING → empty changed_files → the DEFAULT critic vetoes it (success + empty = no-op), so it
# never reaches the close/commit. We exercise the DEFAULT verify path (no injected verifier) with an
# empty-delta launch + the default critic, and assert: not closed + committer never called.
check("the wire's live permission posture defaults to 'plan' (unarmed/read-only) — unchanged",
      impl.permission_mode() == "plan" and impl.wire_armed() is False)
s = fresh_suite()
intent = s.surface_build_intent("a plan-mode (read-only) run changes nothing", scope=["runtime/"]); sid = intent["id"]
seq = approve_seq(s, sid)
committer = RecordingCommitter()
# no injected verifier → the DEFAULT _wire_verify runs → the default critic vetoes an empty change-set.
out = s.dispatch_decision(sid, seq, launcher=good_launch([]), committer=committer)
check("a plan-mode (empty-delta) build does NOT close (critic vetoes the no-op upstream)",
      not out.get("closed") and s.inbox.get(sid)["status"] != "implemented")
check("the committer was NEVER called for a plan-mode build (no change → no checkpoint)", committer.calls == [])


# =============================================================================================
print("\n=== default committer (_self_build_commit) reuses _git_self_commit w/ [self-build] (fake repo, NOT live) ===")
# Prove the REAL default committer applies the [self-build] prefix + is path-scoped (git add <paths>),
# against a THROWAWAY git repo — never the live /home/tim/company repo.
tmp_repo = tempfile.mkdtemp(prefix="wire-commit-fakerepo-")
subprocess.run(["git", "-C", tmp_repo, "init", "-q"], check=True)
subprocess.run(["git", "-C", tmp_repo, "config", "user.email", "t@e.st"], check=True)
subprocess.run(["git", "-C", tmp_repo, "config", "user.name", "test"], check=True)
open(os.path.join(tmp_repo, "seed.txt"), "w").write("seed\n")
subprocess.run(["git", "-C", tmp_repo, "add", "seed.txt"], check=True)
subprocess.run(["git", "-C", tmp_repo, "commit", "-qm", "seed"], check=True)
# the build changed built.py; concurrent.json is a concurrent writer's UNSTAGED dirty file.
open(os.path.join(tmp_repo, "built.py"), "w").write("built by the wire\n")
open(os.path.join(tmp_repo, "concurrent.json"), "w").write("a concurrent writer's dirty file\n")
# point a Suite's _repo_root at the fake repo (a fresh suite whose nodes_dir is under the fake repo so
# _repo_root resolves there) — we only exercise _self_build_commit, no dispatch.
fake_nodes = os.path.join(tmp_repo, "nodes"); os.makedirs(fake_nodes, exist_ok=True)
sfake = Suite(FsStore(os.path.join(tempfile.mkdtemp(prefix="wire-commit-fakestore-"), "store")),
              NodeRegistry(), nodes_dir=fake_nodes)
sha = sfake._self_build_commit(["built.py"], "intent-1: add the built thing")
check("_self_build_commit returns a sha (the checkpoint committed)", bool(sha) and len(sha) == 40)
subj = subprocess.run(["git", "-C", tmp_repo, "log", "-1", "--format=%s"],
                      capture_output=True, text=True).stdout.strip()
check("the commit subject is prefixed [self-build] (DISTINCT from [self-apply])",
      subj == "[self-build] intent-1: add the built thing")
# path-scoped: ONLY built.py is in the commit; the concurrent dirty file stayed UNCOMMITTED.
files = subprocess.run(["git", "-C", tmp_repo, "show", "--name-only", "--format=", sha],
                       capture_output=True, text=True).stdout.split()
check("the commit contains ONLY the build's file (path-scoped add)", files == ["built.py"])
check("the concurrent writer's dirty file was NOT committed (still untracked)",
      "concurrent.json" not in files)
still_dirty = subprocess.run(["git", "-C", tmp_repo, "status", "--porcelain"],
                             capture_output=True, text=True).stdout
check("the concurrent dirty file remains uncommitted after the checkpoint (isolation holds)",
      "concurrent.json" in still_dirty)
# REVERTIBLE: the [self-build] commit reverts via the same prefix-agnostic git path.
rproc = subprocess.run(["git", "-C", tmp_repo, "revert", "--no-edit", sha], capture_output=True, text=True)
check("the [self-build] checkpoint is git-revertible (`git revert <sha>` succeeds)", rproc.returncode == 0)
check("after revert the built file is gone (the build is undone)",
      not os.path.exists(os.path.join(tmp_repo, "built.py")))


print(f"\nALL {PASS} CHECKS PASS — the wire's accepted-build close is GIT-SAFE: every verified + in-scope "
      f"build is committed as a SINGLE revertible [self-build] commit (exactly its changed_delta, "
      f"path-scoped so the concurrent writer's dirty files are never swept in), the sha is recorded "
      f"(item + event + review), a commit failure / empty delta / failed-gate / out-of-scope build NEVER "
      f"commits and NEVER marks implemented (re-surfaced loud via a decision.verify terminal event), and "
      f"the plan-mode (unarmed) default is unchanged.")
