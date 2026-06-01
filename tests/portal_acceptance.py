"""tests/portal_acceptance.py — portals: one artefact, many live views (I4, context-13).

A portal is a first-class node that is RESOLVED BY REFERENCE, never computed and never
wired by dataflow. The scheduler skips it; state() fills its output live from
get_content(head(config.ref)) on every read. The decisive property is LIVE: change the
source and re-read → the portal reflects the new content (a window, not a copy/snapshot).
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


store_dir = tempfile.mkdtemp(prefix="portal-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    check("portal node-type discovered", "portal" in reg)
    check("portal declares reference-resolution",
          getattr(reg["portal"], "RESOLVE", "compute") == "reference")

    g = "portal-test"
    suite.create_node(g, "constant", config={"value": "v1"}, node_id="src")
    # portal is a live window onto the source's address — NOT wired by an edge
    suite.create_node(g, "portal", config={"ref": f"run://{g}/src"}, node_id="win")

    # 1. scheduler runs src, SKIPS the portal cleanly (does not choke, does not fire run())
    result = suite.run(g)
    check("source computed", "src" in result["ran"])
    check("portal not fired (run() never called) — processed, not stuck", "win" not in result["stuck"])

    # 2. portal resolves the source's content live (window, not empty)
    st = suite.state(g)
    win = next(n for n in st["nodes"] if n["id"] == "win")
    check("portal shows the source's content", win["output"] == "v1")
    src = next(n for n in st["nodes"] if n["id"] == "src")
    check("portal points at the SAME content-hash as the source", win["content_hash"] == src["content_hash"])

    # 3. THE decisive property — change the source, re-run, re-read: portal reflects new content
    suite.set_config(g, "src", {"value": "v2-CHANGED"})
    suite.run(g)
    st2 = suite.state(g)
    win2 = next(n for n in st2["nodes"] if n["id"] == "win")
    check("portal is LIVE — reflects changed source (window, not snapshot)", win2["output"] == "v2-CHANGED")

    # 4. a portal with a dangling/empty ref resolves to None (no crash, no fake content)
    suite.create_node(g, "portal", config={"ref": f"run://{g}/nonexistent"}, node_id="empty")
    st3 = suite.state(g)
    empt = next(n for n in st3["nodes"] if n["id"] == "empty")
    check("portal with empty ref resolves to None (no fabrication)", empt["output"] is None)

    print(f"\nALL {PASS} CHECKS PASS — portals are live reference-resolved views")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
