"""tests/drift_acceptance.py — the map self-maintains (PoLR-3).

Tim asked for a path-of-least-resistance that *maintains* — not a doc that rots in 20 hours.
This makes drift FAIL LOUD: every registered node-type, RHM verb, and core subsystem must be
reflected in MAP.md. If a future change adds a capability but not its map entry, this test fails
— the reflective fold enforced, no silent rot.
"""
import os, sys, tempfile

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


store = FsStore(os.path.join(tempfile.mkdtemp(prefix="drift-"), "store"))
reg = NodeRegistry(); reg.discover([NODES])
suite = Suite(store, reg, nodes_dir=NODES)   # nodes_dir = real → repo_root = real → reads the real MAP.md

drift = suite.map_drift()
check(f"every registered node-type is in MAP.md (drift: {drift['node_types']})", not drift["node_types"])
check(f"every RHM verb is in MAP.md (drift: {drift['rhm_verbs']})", not drift["rhm_verbs"])
check(f"every core subsystem is in MAP.md (drift: {drift['surfaces']})", not drift["surfaces"])

print(f"\nALL {PASS} CHECKS PASS — the map describes the system; drift would fail loud")
