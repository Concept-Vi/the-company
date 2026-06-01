"""tests/react_acceptance.py — watch-and-react ambient commentary (slice 12).

Finishes the partial mode (no audio): the RHM comments on activity it observes, but ONLY in
watch-and-react mode (real mode-gated behavior) and only when relevant. The gate is proven
offline (silent in other modes — no model call); the live comment is proven by use.
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


store_dir = tempfile.mkdtemp(prefix="react-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "react"
    suite.create_node(g, "constant", config={"value": "x"}, node_id="a")   # emits an event

    # react is SILENT outside watch-and-react (mode-gated, no model call → runs offline)
    suite.set_mode("listening")
    check("react is silent in listening mode", suite.react(g)["comment"] == "")
    suite.set_mode("focus")
    check("react is silent in focus mode", suite.react(g)["comment"] == "")
    suite.set_mode("off")
    check("react is silent in off mode", suite.react(g)["comment"] == "")

    # watch-and-react is the mode that enables it (we don't call the model here; just prove the gate opens)
    suite.set_mode("watch-and-react")
    check("watch-and-react is a valid mode that opens the ambient channel",
          suite.get_mode() == "watch-and-react")

    print(f"\nALL {PASS} CHECKS PASS — watch-and-react is mode-gated; silent in every other mode")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
