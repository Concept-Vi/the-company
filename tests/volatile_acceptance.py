"""tests/volatile_acceptance.py — VOLATILE nodes are never memo-frozen (red-team F1 fix).

A node that reads EXTERNAL state (filesystem/network) has a constant memo signature when it has
no input ports — so the memo gate would cache its first-run output forever, even as the source
changes (the codebase/source nodes serving STALE answers). VOLATILE=True opts such a node out of
the memo gate: it always re-runs. Pure nodes still memo-cache (the gate is intact for them).
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from nodes import codebase as cb

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


work = tempfile.mkdtemp(prefix="volatile-test-")
try:
    store = FsStore(os.path.join(work, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    check("codebase node declares VOLATILE", getattr(cb, "VOLATILE", False) is True)

    # a codebase node over a throwaway root that we MUTATE between runs
    src = os.path.join(work, "src"); os.makedirs(src)
    open(os.path.join(src, "AGENTS.md"), "w").write("alpha")
    g = "vol"
    suite.create_node(g, "codebase", config={"root": src, "globs": ["*.md"]}, node_id="cb")
    suite.run(g)
    out1 = suite.results(g)["cb"]
    check("first run reads 'alpha'", "alpha" in out1)

    # change the external source, run again — must NOT be the frozen first output
    open(os.path.join(src, "NEW.md"), "w").write("beta-new-content")
    r2 = suite.run(g)
    out2 = suite.results(g)["cb"]
    check("volatile node RE-RAN (not memo-skipped)", "cb" in r2["ran"] and "cb" not in r2["skipped"])
    check("re-read picks up the new content (no stale freeze)", "beta-new-content" in out2)

    # a PURE pipeline still memo-caches (the gate is intact where it's sound)
    suite.create_node(g, "constant", config={"value": "hi"}, node_id="k")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "k", "value", "u", "text")
    suite.run(g)
    r4 = suite.run(g)                                     # second run, nothing changed
    check("pure node memo-caches on an unchanged re-run", "u" in r4["skipped"])

    print(f"\nALL {PASS} CHECKS PASS — volatile nodes re-run; pure nodes still memo-cache")
finally:
    shutil.rmtree(work, ignore_errors=True)
