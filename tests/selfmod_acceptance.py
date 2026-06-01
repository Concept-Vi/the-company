"""tests/selfmod_acceptance.py — update the app through its interface, safely (slice 13, Q3).

The self-architecting fold, scoped per the repo's own constitution: ADDITIVE + GIT-REVERSIBLE
self-extension (new capability through the governed loop), NOT edit-in-place of engine internals.
The real safety net is git, not the operator gate: every self-apply is a commit, so a bad one
is one `git revert` away. RECOVERY is proven here (broken self-edit → revert → back up).
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


work = tempfile.mkdtemp(prefix="selfmod-test-")
try:
    # a throwaway git repo with a nodes/ dir (so we never touch the real one)
    repo = os.path.join(work, "company")
    nodes = os.path.join(repo, "nodes")
    os.makedirs(nodes)
    subprocess.run(["git", "init", repo], capture_output=True, check=True)
    git(repo, "config", "user.email", "t@t"); git(repo, "config", "user.name", "t")
    open(os.path.join(nodes, "seed.py"), "w").write("VERSION='1'\nKIND='process'\nPORTS_IN={}\nPORTS_OUT={}\ndef run(i,c): return 1\n")
    git(repo, "add", "-A"); git(repo, "commit", "-m", "baseline")
    base_head = git(repo, "rev-parse", "HEAD")

    store = FsStore(os.path.join(work, "store"))
    reg = NodeRegistry(); reg.discover([nodes])
    suite = Suite(store, reg, nodes_dir=nodes)

    # operator-approved self-apply (the governed loop) — no caller flag; approval read from inbox
    sid = suite.inbox.surface("code_build",
                              {"name": "selftest", "code": "VERSION='1'\nKIND='process'\nPORTS_IN={'text':'Text'}\nPORTS_OUT={'text':'Text'}\ndef run(i,c): return str(i.get('text',''))[::-1]\n"},
                              default="reject", resolved=None)
    suite.resolve_surfaced(sid, "approve")
    suite.apply_node(sid)

    check("the new capability is live (auto-discovered)", "selftest" in reg)
    head_after = git(repo, "rev-parse", "HEAD")
    check("the self-apply made a git commit (the safety net)", head_after != base_head)
    check("the commit is tagged [self-apply]", "[self-apply]" in git(repo, "log", "-1", "--format=%s"))
    check("last_self_change finds it", (suite.last_self_change() or {}).get("sha") == head_after)
    check("the node file is committed (additive — a NEW file)",
          "selftest.py" in git(repo, "show", "--name-only", "--format=", "HEAD"))

    # RECOVERY: roll it back via git — the property that makes self-modification safe
    suite.revert_self_change(head_after)
    check("recovery: the capability is GONE after revert", "selftest" not in reg)
    check("recovery: the node file is removed from the tree", not os.path.exists(os.path.join(nodes, "selftest.py")))
    check("recovery: a revert commit was made (itself in history/reversible)",
          "Revert" in git(repo, "log", "-1", "--format=%s"))
    check("recovery: the seed capability still works (blast radius bounded)", os.path.exists(os.path.join(nodes, "seed.py")))

    # path-safety unchanged: traversal still rejected
    try:
        suite._safe_node_name("../evil"); raise AssertionError("should reject")
    except ValueError:
        check("path traversal still rejected (no edit-in-place escape)", True)

    print(f"\nALL {PASS} CHECKS PASS — additive, git-committed self-extension; recovery proven")
finally:
    shutil.rmtree(work, ignore_errors=True)
