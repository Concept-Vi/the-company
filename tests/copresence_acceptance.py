"""tests/copresence_acceptance.py — co-presence (slice 4, G1+H1).

Two planes, one state (context-05): a click on the canvas updates the conversation's context.
The RHM's context, given the operator's current selection (focus), gains the SHARED PERCEPTUAL
FIELD — the focused node's full detail (output/config), which the base context deliberately
withholds. So "what am I looking at?" becomes answerable. Proven offline (context-builder);
the live answer is proven by use.
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


store_dir = tempfile.mkdtemp(prefix="copres-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "copres"
    suite.create_node(g, "constant", config={"value": "SECRET-PAYLOAD-42"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")
    suite.run(g)

    # WITHOUT focus: base context lists nodes but NOT their values (privacy of detail)
    base = suite._chat_context(g)
    check("base context lists the node", "c" in base and "constant" in base)
    check("base context does NOT expose the node's value", "SECRET-PAYLOAD-42" not in base)

    # WITH focus (operator selected 'c' on the canvas): co-presence grants the focused detail
    focused = suite._chat_context(g, focus={"selected": ["c"]})
    check("focus context flags the operator's current selection", "CURRENT FOCUS" in focused)
    check("focus context exposes the SELECTED node's value (shared perceptual field)",
          "SECRET-PAYLOAD-42" in focused)
    check("focus context names the selected node", "c (" in focused or "· c " in focused)

    # selecting a different node shifts what the RHM sees (context = consequence of what you're doing)
    focused_u = suite._chat_context(g, focus={"selected": ["u"]})
    check("selecting a different node changes the focus detail",
          "u (" in focused_u and "SECRET-PAYLOAD-42".upper() in focused_u)   # u's output is the uppercased value

    # a bogus selection is ignored (no crash, no fabrication)
    safe = suite._chat_context(g, focus={"selected": ["does-not-exist"]})
    check("a non-existent selection is ignored safely", "CURRENT FOCUS" not in safe)

    print(f"\nALL {PASS} CHECKS PASS — co-presence: the operator's selection is in the RHM's perceptual field")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
