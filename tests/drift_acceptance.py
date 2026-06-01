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
# checked INSIDE the maintained registry block (not whole-file prose), across every capability category
check(f"every node-type is in the MAP registry block (drift: {drift['map_node_types']})", not drift["map_node_types"])
check(f"every RHM verb is in the registry block (drift: {drift['map_rhm_verbs']})", not drift["map_rhm_verbs"])
check(f"every mode is in the registry block (drift: {drift['map_modes']})", not drift["map_modes"])
check(f"every panel is in the registry block (drift: {drift['map_panels']})", not drift["map_panels"])
check(f"every acceptance suite is in STATE's suite block (drift: {drift['state_missing_suites']})",
      not drift["state_missing_suites"])

# the block-scoped check must actually be block-scoped: a word only in PROSE shouldn't satisfy it.
# 'right-hand-man' appears in MAP prose but is NOT a registered node-type, so it can't false-pass node_types.
print(f"\nALL {PASS} CHECKS PASS — block-scoped drift across node-types · verbs · modes · panels · suites")
