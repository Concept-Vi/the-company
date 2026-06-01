"""tests/layers_acceptance.py — provenance layers (I4, context-13 "Layers").

Layers are a DATA property, not just visual: each node carries a provenance layer derived
from its node-type's ORIGIN — 'authored' (the origin hand-built the type) vs 'system'
(a role/the brain wrote it). Suite.state() surfaces it so the canvas can toggle a layer to
"see what a role changed". The brain tags every node it writes (propose_node injects ORIGIN).
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


store_dir = tempfile.mkdtemp(prefix="layers-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # brain-written node-types are tagged ORIGIN='system'; hand-built ones default 'authored'
    check("system-derived type carries ORIGIN='system' (wordcount)",
          getattr(reg["wordcount"], "ORIGIN", "authored") == "system")
    check("hand-built type defaults to authored (constant)",
          getattr(reg["constant"], "ORIGIN", "authored") == "authored")

    g = "layers-test"
    suite.create_node(g, "constant", config={"value": "hi"}, node_id="c")
    suite.create_node(g, "wordcount", node_id="w")
    st = suite.state(g)
    by = {n["id"]: n for n in st["nodes"]}
    check("authored node tagged layer='authored'", by["c"]["layer"] == "authored")
    check("system-derived node tagged layer='system'", by["w"]["layer"] == "system")

    # the brain TAGS what it writes — future-proofs provenance (propose_node injects ORIGIN)
    from runtime.suite import _tag_system_origin
    tagged = _tag_system_origin("VERSION='1'\ndef run(inputs, config):\n    return 1\n")
    check("brain injects ORIGIN='system' into written modules", "ORIGIN = 'system'" in tagged)
    check("injection is idempotent (not doubled)",
          _tag_system_origin(tagged).count("ORIGIN = 'system'") == 1)

    print(f"\nALL {PASS} CHECKS PASS — provenance layers are a data property, surfaced per node")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
