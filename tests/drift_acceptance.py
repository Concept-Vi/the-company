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

drift = suite.doc_drift()
check(f"every registered node-type is in MAP.md (drift: {drift['map_node_types']})", not drift["map_node_types"])
check(f"every RHM verb is in MAP.md (drift: {drift['map_rhm_verbs']})", not drift["map_rhm_verbs"])
check(f"every core subsystem is in MAP.md (drift: {drift['map_surfaces']})", not drift["map_surfaces"])
check(f"every acceptance suite is reflected in STATE.md (drift: {drift['state_missing_suites']})",
      not drift["state_missing_suites"])

print(f"\nALL {PASS} CHECKS PASS — MAP.md + STATE.md describe the system; drift would fail loud")
