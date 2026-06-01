"""tests/show_acceptance.py — attention-direction (slice 11, Q2).

The RHM can SHOW the operator things: a `show` verb is a VIEW directive (drives the camera /
highlights nodes) — it resolves targets against the live graph and mutates NOTHING. The camera
move is proven by use; here we prove parsing, target-resolution, and that it's non-mutating.
"""
import os, sys, tempfile, shutil

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


store_dir = tempfile.mkdtemp(prefix="show-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "show"
    suite.create_node(g, "constant", config={"value": "x"}, node_id="a")
    suite.create_node(g, "uppercase", node_id="b")

    check("show is a whitelisted verb", "show" in suite.RHM_VERBS)
    shown, act = suite._parse_rhm_action("Here it is.\nACTION: show a, b")
    check("parses ACTION: show <ids>", act["verb"] == "show" and act["targets"] == ["a", "b"])

    before = suite._load(g)
    r = suite._dispatch_rhm_action(act, g)
    check("show returns the resolved targets", r["did"] == "show" and set(r["targets"]) == {"a", "b"})
    after = suite._load(g)
    check("show mutates NOTHING (same nodes, same edges)",
          [n.id for n in after.nodes] == [n.id for n in before.nodes] and len(after.edges) == len(before.edges))

    bad = suite._dispatch_rhm_action({"verb": "show", "targets": ["ghost"]}, g)
    check("show with no real target is refused (points at nothing → nothing)", bad["did"] == "none")

    mix = suite._dispatch_rhm_action({"verb": "show", "targets": ["a", "ghost"]}, g)
    check("show resolves only real targets", mix["targets"] == ["a"])

    print(f"\nALL {PASS} CHECKS PASS — attention-direction: show moves the view, resolves targets, mutates nothing")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
