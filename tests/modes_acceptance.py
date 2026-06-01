"""tests/modes_acceptance.py — RHM modes / the presence dial (slice 2, D1-D3).

The mode IS a node (context-05): the operator's presence preference is a node config in the
`system` graph, switched by the SAME verbs (create_node/set_config), persisted in the store.
Each mode changes REAL behavior — 'off' disables the RHM entirely (no model call); the active
modes inject a distinct behavioral directive. Proven offline here (off short-circuits before the
model); the directive's stylistic effect is shown by use.
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


store_dir = tempfile.mkdtemp(prefix="modes-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    check("rhm_mode is a discovered node-type", "rhm_mode" in reg)
    check("there are 8 modes", len(suite.MODES) == 8)
    check("default mode is valid", suite.get_mode() in suite.MODES)

    # switching a mode is editing a node parameter via the existing verbs
    suite.set_mode("focus")
    check("set_mode persists (get_mode)", suite.get_mode() == "focus")
    sysg = store.load_graph(suite.SYSTEM_GRAPH)
    moden = next((n for n in sysg.nodes if n.id == suite.MODE_NODE), None)
    check("the mode IS a node in the system graph", moden is not None and moden.type == "rhm_mode")
    check("the mode is that node's config parameter", moden.config.get("mode") == "focus")

    suite.set_mode("decide-for-me")
    check("re-switching edits the same node", suite.get_mode() == "decide-for-me")
    suite2 = Suite(FsStore(os.path.join(store_dir, "store")), reg, nodes_dir=NODES)
    check("mode persists across sessions", suite2.get_mode() == "decide-for-me")

    try:
        suite.set_mode("nonsense"); raise AssertionError("should have raised")
    except ValueError:
        check("unknown mode is rejected (fail loud)", True)

    # each active mode carries a real behavioral directive; off is special
    check("every active mode has a non-empty directive",
          all(suite._mode_directive(m) for m in suite.MODES if m != "off"))

    # 'off' DISABLES the RHM — returns canned reply WITHOUT calling the model (works offline)
    suite.set_mode("off")
    r = suite.chat("are you there?", "any-graph")
    check("off → RHM returns the off reply (no model call)", "off" in r["reply"].lower())
    check("off → no action taken", r["action"] is None)
    check("off → reports the mode", r.get("mode") == "off")
    check("off → the turn is still logged", store.chat_history(1)[0]["text"].lower().find("off") >= 0)

    print(f"\nALL {PASS} CHECKS PASS — modes are nodes; switching is editing a parameter; off disables")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
