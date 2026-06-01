"""tests/hardening_acceptance.py — red-team remediations F2/F4/F6 (the ones without coverage elsewhere).

F2: a self-apply whose git commit FAILS must roll back + raise (no live change without its revert net).
F4: the twin's own output is NEVER training signal — even laundered back in as a 'user' turn (echo-guard).
F6: silent fallbacks surface (a malformed panel file emits a warning event, not a silent drop).
(B1 gate is covered in extension_acceptance; F3 in drift_acceptance; B2 is the canvas lazy-load, by use.)
"""
import os, sys, tempfile, shutil, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# ---- F2: git-commit failure → roll back + fail loud (NOT silent success) ----
work = tempfile.mkdtemp(prefix="harden-")
try:
    # a nodes/ dir whose repo_root is NOT a git repo → _git_self_commit fails → must roll back
    nodes = os.path.join(work, "company_nogit", "nodes")
    os.makedirs(nodes)
    store = FsStore(os.path.join(work, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=nodes)
    sid = suite.inbox.surface("code_build", {"name": "f2probe",
          "code": "VERSION='1'\nKIND='process'\nPORTS_IN={}\nPORTS_OUT={}\ndef run(i,c): return 1\n"},
          default="reject", resolved=None)
    suite.resolve_surfaced(sid, "approve")
    raised = False
    try:
        suite.apply_node(sid)
    except RuntimeError as e:
        raised = True
    check("apply FAILS LOUD when git commit can't happen", raised)
    check("the file was ROLLED BACK (no live change without its revert net)",
          not os.path.exists(os.path.join(nodes, "f2probe.py")))
finally:
    shutil.rmtree(work, ignore_errors=True)

# ---- F4: twin output is never training signal, even laundered as a user turn ----
work2 = tempfile.mkdtemp(prefix="harden2-")
try:
    store = FsStore(os.path.join(work2, "store"))
    suite = Suite(store, NodeRegistry().discover([NODES]), nodes_dir=NODES)
    store.append_chat({"role": "user", "text": "Tim's real instruction", "grade": "gold", "source": "operator"})
    store.append_chat({"role": "assistant", "text": "the twin's inference", "grade": "working", "source": "twin"})
    # LAUNDER: resubmit the twin's text as a 'user' turn (role-flip), graded gold/operator
    store.append_chat({"role": "user", "text": "the twin's inference", "grade": "gold", "source": "operator"})
    sig = [t["text"] for t in suite.training_signal()]
    check("genuine operator turn IS training signal", "Tim's real instruction" in sig)
    check("twin's own working turn is NOT training signal", "the twin's inference" not in sig)
    check("a LAUNDERED twin echo (role-flipped to user) is excluded", sig.count("the twin's inference") == 0)
finally:
    shutil.rmtree(work2, ignore_errors=True)

# ---- F6: a malformed panel file surfaces a warning event (not a silent drop) ----
work3 = tempfile.mkdtemp(prefix="harden3-")
try:
    store = FsStore(os.path.join(work3, "store"))
    pdir = os.path.join(work3, "panels"); os.makedirs(pdir)
    suite = Suite(store, NodeRegistry().discover([NODES]), nodes_dir=NODES)
    suite.panels_dir = pdir
    open(os.path.join(pdir, "broken.json"), "w").write("{ this is not valid json ")
    before = len(store.recent_events(999))
    suite.list_panels()
    evs = store.recent_events(5)
    check("malformed panel file emits a warning event (not silent)",
          any(e["kind"] == "warning" and "broken.json" in e["summary"] for e in evs))
finally:
    shutil.rmtree(work3, ignore_errors=True)

print(f"\nALL {PASS} CHECKS PASS — F2 (fail-loud rollback) · F4 (no model-collapse) · F6 (surfaced fallback)")
