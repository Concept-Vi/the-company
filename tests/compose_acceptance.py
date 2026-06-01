"""tests/compose_acceptance.py — on-canvas composition backend (the verbs the palette/wire/delete UI calls).

Proves Suite.connect type-checks (accepts compatible, REJECTS mismatched) and delete_node removes
node + its edges. The existing node library is all Text/Any, so we drop a temp Number-typed node to
exercise the rejection path that no real node can currently trigger.
"""
import os, sys, tempfile, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
TMP_NODE = os.path.join(NODES, "tmpnum.py")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


# temp Number-typed node so a real type mismatch exists in the registry
with open(TMP_NODE, "w") as f:
    f.write("VERSION='1'\nKIND='content'\nPORTS_IN={}\nPORTS_OUT={'n':'Number'}\n"
            "def run(inputs, config):\n    return 42\n")

store_dir = tempfile.mkdtemp(prefix="compose-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    check("tmpnum (Number) + wordcount (Text) discovered",
          "tmpnum" in reg and "wordcount" in reg)

    g = "compose-test"
    suite.create_node(g, "tmpnum", node_id="num")
    suite.create_node(g, "wordcount", node_id="wc")
    suite.create_node(g, "uppercase", node_id="up")

    # 1. type MISMATCH is rejected (Number -> Text), fail loud
    raised = False
    try:
        suite.connect(g, "num", "n", "wc", "text")
    except ValueError as e:
        raised = True
        print(f"      (rejected as expected: {e})")
    check("connect rejects Number -> Text mismatch", raised)
    check("rejected edge was NOT persisted", len(suite._load(g).edges) == 0)

    # 2. compatible wire (Text -> Text) is accepted
    suite.connect(g, "wc", "text", "up", "text")
    edges = suite._load(g).edges
    check("connect accepts Text -> Text", len(edges) == 1
          and edges[0].from_node == "wc" and edges[0].to_node == "up")

    # 3. delete_node removes the node AND its incident edges
    suite.delete_node(g, "wc")
    g2 = suite._load(g)
    check("delete_node removed the node", all(n.id != "wc" for n in g2.nodes))
    check("delete_node removed incident edges", len(g2.edges) == 0)
    check("delete_node left unrelated nodes", any(n.id == "up" for n in g2.nodes))

    print(f"\nALL {PASS} CHECKS PASS — compose backend verified (accept · reject · delete)")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
    if os.path.exists(TMP_NODE):
        os.remove(TMP_NODE)
