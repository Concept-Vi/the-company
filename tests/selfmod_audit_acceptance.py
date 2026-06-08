"""tests/selfmod_audit_acceptance.py — the self-modification AUDIT LEDGER + safe revert (hardening).

Hardens the self-modification subsystem along four verified findings — each proven here by USE
against a throwaway git repo (mirrors selfmod_acceptance.py's harness, so the real repo is never
touched):

  1. AUDIT LOG — `self_change_log(limit=N)` lists the multi-entry self-apply history (sha · subject
     · timestamp · changed_files), not just the single latest. (Was: only last_self_change().)
  2. REVERT-RECURSION — a `git revert` of a self-apply has subject `Revert "[self-apply] ..."`,
     which STILL matches `--grep=[self-apply]`. So last_self_change() used to return the REVERT as
     if it were a change ("revert the revert"). FIXED: a revert is tagged + EXCLUDED from
     last_self_change(), which now reflects the true last *change*, never an undo.
  3. NON-TIP REVERT IS FAIL-LOUD-HANDLED — revert_self_change(sha) of a non-tip commit can CONFLICT.
     It used to run `git revert` with check=True → raised mid-revert, leaving the repo dirty. FIXED:
     conflict-aware — detects the conflict, `git revert --abort`s cleanly, raises a LEGIBLE error;
     the repo is left CLEAN (never mid-revert), and HEAD is unchanged.
  4. DIFF SURFACED — every self-change record carries `changed_files` (git ground truth), so the
     log shows WHICH files each change touched (feeds #1).

The adversarial cases (#2 revert-a-revert, #3 conflicting non-tip revert) are tested EXPLICITLY.
"""
import os, sys, tempfile, shutil, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, check=True).stdout.strip()


def _node_code(suffix=""):
    return ("VERSION='1'\nKIND='process'\nPORTS_IN={'text':'Text'}\nPORTS_OUT={'text':'Text'}\n"
            f"def run(i,c): return str(i.get('text',''))  # {suffix}\n")


def _apply(suite, name, code):
    """Drive ONE governed self-apply (surface → operator approve → apply_node), returning the sha."""
    sid = suite.inbox.surface("code_build", {"name": name, "code": code}, default="reject", resolved=None)
    suite.resolve_surfaced(sid, "approve")
    suite.apply_node(sid)
    return git(suite._repo_root, "rev-parse", "HEAD")


work = tempfile.mkdtemp(prefix="selfmod-audit-test-")
try:
    repo = os.path.join(work, "company")
    nodes = os.path.join(repo, "nodes")
    os.makedirs(nodes)
    subprocess.run(["git", "init", repo], capture_output=True, check=True)
    git(repo, "config", "user.email", "t@t"); git(repo, "config", "user.name", "t")
    open(os.path.join(nodes, "seed.py"), "w").write(
        "VERSION='1'\nKIND='process'\nPORTS_IN={}\nPORTS_OUT={}\ndef run(i,c): return 1\n")
    git(repo, "add", "-A"); git(repo, "commit", "-m", "baseline")

    store = FsStore(os.path.join(work, "store"))
    reg = NodeRegistry(); reg.discover([nodes])
    suite = Suite(store, reg, nodes_dir=nodes)

    # --- apply THREE self-changes (so the log is genuinely multi-entry) ---
    sha_a = _apply(suite, "audit_alpha", _node_code("alpha"))
    sha_b = _apply(suite, "audit_beta", _node_code("beta"))
    sha_c = _apply(suite, "audit_gamma", _node_code("gamma"))
    check("three distinct self-apply commits exist", len({sha_a, sha_b, sha_c}) == 3)

    # ========== FINDING #1 + #4: the audit log (multi-entry) carries changed_files ==========
    log = suite.self_change_log(limit=10)
    check("self_change_log returns a list", isinstance(log, list))
    real_changes = [e for e in log if not e.get("is_revert")]
    check("the log lists MULTIPLE self-changes (not just the latest)", len(real_changes) >= 3)
    shas_in_log = {e["sha"] for e in log}
    check("all three applied changes appear in the log", {sha_a, sha_b, sha_c} <= shas_in_log)
    newest = real_changes[0]
    check("each record carries sha + subject + timestamp", bool(newest.get("sha")) and
          bool(newest.get("subject")) and bool(newest.get("ts")))
    check("#4: each record carries changed_files (the diff manifest)", "changed_files" in newest
          and isinstance(newest["changed_files"], list))
    # the gamma change added nodes/audit_gamma.py — it must show in that record's changed_files
    gamma_rec = next(e for e in log if e["sha"] == sha_c)
    check("#4: changed_files names the file the change actually touched",
          any("audit_gamma.py" in f for f in gamma_rec["changed_files"]))

    # ========== ADVERSARIAL (body-mention): a non-self-apply commit that MENTIONS [self-apply] ==========
    # `git log --grep=[self-apply] --fixed-strings` matches the whole MESSAGE (subject AND body). But a
    # genuine self-apply is SUBJECT-prefixed `[self-apply]` (what _git_self_commit writes). A plain
    # feature/doc commit whose BODY merely mentions the string is NOT a self-change and must NOT pollute
    # the ledger (it would make last_self_change point at a non-self-apply commit). Classify by SUBJECT.
    open(os.path.join(nodes, "decoy.py"), "w").write(_node_code("decoy"))
    git(repo, "add", "-A")
    git(repo, "commit", "-m", "ordinary feature commit\n\nthis body talks about [self-apply] commits but is NOT one")
    decoy_sha = git(repo, "rev-parse", "HEAD")
    log_decoy = suite.self_change_log(limit=20)
    check("body-only [self-apply] mention is NOT in the ledger (subject-classified, not body-matched)",
          decoy_sha not in {e["sha"] for e in log_decoy})
    check("last_self_change does NOT return the body-mention decoy (it is not a self-apply)",
          (suite.last_self_change() or {}).get("sha") != decoy_sha)
    check("last_self_change still returns the true tip self-apply (gamma) past the decoy",
          (suite.last_self_change() or {}).get("sha") == sha_c)

    # ========== FINDING #2: revert-recursion — a revert is distinguished, not mistaken for a change ==========
    # last_self_change BEFORE any revert = the true tip change (gamma)
    check("last_self_change is the true last CHANGE (gamma) before any revert",
          (suite.last_self_change() or {}).get("sha") == sha_c)

    # revert the TIP self-change (gamma). This creates a `Revert "[self-apply] ..."` commit, which
    # STILL contains [self-apply] and so still matches --grep=[self-apply] (the recursion trap).
    suite.revert_self_change(sha_c)
    revert_subj = git(repo, "log", "-1", "--format=%s")
    check("the revert commit subject is a Revert of a [self-apply]", revert_subj.startswith('Revert "[self-apply]'))

    # THE ADVERSARIAL CASE (D9): last_self_change must NOT return the revert (it is an UNDO, not a
    # change) AND must NOT return the change the revert UNDID (gamma no longer STANDS). NB git semantics:
    # `git revert` does NOT delete the original commit — it ADDS a revert commit on top, so gamma's
    # `[self-apply]` commit is still IN history. The old contract returned gamma's original (newest
    # non-revert). D9 sharpens it: gamma was REVERTED, so it no longer stands — last_self_change skips
    # BOTH the revert AND gamma, returning the newest STILL-STANDING change (beta).
    lsc = suite.last_self_change() or {}
    check("#2: last_self_change does NOT return the revert (no 'revert the revert')",
          not lsc.get("subject", "").startswith('Revert "'))
    check("D9: last_self_change SKIPS the reverted change (gamma no longer stands)",
          lsc.get("sha") != sha_c)
    check("D9: last_self_change returns the newest STILL-STANDING change (beta, the one before gamma)",
          lsc.get("sha") == sha_b)
    check("#2: that record is correctly tagged a change, not an undo", lsc.get("is_revert") is False)
    # the revert IS still in the audit log, but tagged as a revert (distinctly surfaced, not hidden)
    log2 = suite.self_change_log(limit=10)
    check("#2: the revert appears in the log but is tagged is_revert=True",
          any(e.get("is_revert") for e in log2))
    check("#2: a real change in the log is tagged is_revert=False",
          any(not e.get("is_revert") for e in log2))

    # ========== FINDING #3: a conflicting NON-TIP revert is handled fail-loud (repo left clean) ==========
    # Build a deterministic modify/delete conflict: change X adds nodes/conflict_me.py; a LATER tip
    # commit modifies that same file. Reverting X (delete the file) conflicts with the later edit.
    sha_x = _apply(suite, "conflict_me", _node_code("v1"))
    # tip edit of the same file the revert-of-X would try to delete → modify/delete conflict
    open(os.path.join(nodes, "conflict_me.py"), "a").write("# later edit makes revert conflict\n")
    git(repo, "add", "-A"); git(repo, "commit", "-m", "later edit of conflict_me (not a self-apply)")
    head_before = git(repo, "rev-parse", "HEAD")

    raised = False
    try:
        suite.revert_self_change(sha_x)          # non-tip + conflicting → must fail LOUD, not leave a mess
    except Exception as e:
        raised = True
        err_text = f"{type(e).__name__}: {e}"
    check("#3: a conflicting non-tip revert RAISES (fail loud, not silent)", raised)
    check("#3: the error is legible (names the sha / conflict)", raised and (sha_x[:8] in err_text
          or "conflict" in err_text.lower()))
    porcelain = git(repo, "rev-parse", "HEAD") and subprocess.run(
        ["git", "-C", repo, "status", "--porcelain"], capture_output=True, text=True, check=True).stdout.strip()
    check("#3: the repo is left CLEAN (no mid-revert state, no dirty tree)", porcelain == "")
    check("#3: HEAD is unchanged (the failed revert created no commit)",
          git(repo, "rev-parse", "HEAD") == head_before)

    # ========== CHECKPOINT STREAM: the operator-initiated THIRD reversible stream ==========
    # `checkpoint(paths, label)` mints a `[checkpoint]` commit of EXACTLY the named paths — a third
    # reversible stream beside [self-apply] + [self-build]. It must be VISIBLE in the SAME ledger
    # (stream-tagged 'checkpoint') and undone through the SAME prefix-agnostic revert_self_change — no
    # parallel git path, no parallel ledger. Path-scoped (rule 10: parallel sessions on main) with
    # three fail-loud guards. Placed LAST so its commits don't perturb the gamma-is-tip assertions above.
    cp_file = os.path.join(nodes, "checkpoint_target.py")
    open(cp_file, "w").write(_node_code("checkpoint-target"))    # a working-tree change, not yet committed
    cp = suite.checkpoint(["nodes/checkpoint_target.py"], "before experiment")
    check("checkpoint returns a sha tagged the 'checkpoint' stream",
          bool(cp.get("sha")) and cp.get("stream") == "checkpoint")
    cp_subj = git(repo, "log", "-1", "--format=%s")
    check("the checkpoint commit subject is prefixed [checkpoint]", cp_subj.startswith("[checkpoint] "))
    log_cp = suite.self_change_log(limit=20)
    cp_rec = next((e for e in log_cp if e["sha"] == cp["sha"]), None)
    check("the checkpoint appears in the SAME audit ledger (not a parallel log)", cp_rec is not None)
    check("the checkpoint record is stream-tagged 'checkpoint'", cp_rec and cp_rec.get("stream") == "checkpoint")
    check("the checkpoint record names the file it checkpointed (changed_files)",
          cp_rec and any("checkpoint_target.py" in f for f in cp_rec["changed_files"]))
    lsc_cp = suite.last_self_change() or {}
    check("last_self_change returns the checkpoint as the newest still-standing change (any stream)",
          lsc_cp.get("sha") == cp["sha"])
    check("last_self_change carries the stream tag", lsc_cp.get("stream") == "checkpoint")

    # fail-loud guards — a checkpoint that is unsafe (whole-tree / escaping) or empty (commits nothing) RAISES
    def _refused(fn):
        try:
            fn(); return False
        except Exception:
            return True
    check("checkpoint REFUSES a whole-tree/empty path-set (rule 10 footgun: would sweep a parallel session)",
          _refused(lambda: suite.checkpoint([], "nope")))
    check("checkpoint REFUSES a path escaping the repo root (rule 8: a wrong scope is a wrong checkpoint)",
          _refused(lambda: suite.checkpoint(["../outside.py"], "nope")))
    check("checkpoint REFUSES an empty delta — committing nothing is not a restore point (rule 4)",
          _refused(lambda: suite.checkpoint(["nodes/seed.py"], "no changes here")))   # seed.py unchanged

    # REVERT the checkpoint through the SAME operator path → the revert-recursion guard, GENERALIZED to
    # the new stream: the reverted checkpoint must drop out of last_self_change (no 'revert the revert').
    suite.revert_self_change(cp["sha"])
    cp_revert_subj = git(repo, "log", "-1", "--format=%s")
    check("the checkpoint reverts via the SAME revert_self_change (subject Revert \"[checkpoint] ...\")",
          cp_revert_subj.startswith('Revert "[checkpoint]'))
    lsc_after = suite.last_self_change() or {}
    check("after revert, last_self_change EXCLUDES the reverted checkpoint (generalized revert-recursion)",
          lsc_after.get("sha") != cp["sha"] and not lsc_after.get("subject", "").startswith('Revert "'))

    print(f"\nALL {PASS} CHECKS PASS — audit ledger + changed_files; revert-a-revert distinguished; "
          "conflicting non-tip revert fail-loud + repo clean; operator [checkpoint] stream "
          "(mint → same ledger → same revert, fail-loud guards)")
finally:
    shutil.rmtree(work, ignore_errors=True)
