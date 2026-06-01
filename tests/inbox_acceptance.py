"""tests/inbox_acceptance.py — inbox lanes + COA drillability (slice 6, F1-F2, C2-C3).

Chief-of-staff triage (context-05): surfaced decisions sort into lanes — live escalations
(pending, need the operator), resolved-for-you (already handled, audit), batched (pending
grouped by theme). The decision-compiler keeps the raw payload DRILLABLE under a value-framing.
Lane classification is deterministic (proven here); the COA value-framing is proven by use.
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


store_dir = tempfile.mkdtemp(prefix="inbox-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # surface decisions in different states
    e1 = suite.inbox.surface("code_build", {"name": "a", "code": "x"}, default="reject", resolved=None)
    e2 = suite.inbox.surface("code_build", {"name": "b", "code": "y"}, default="reject", resolved=None)
    r1 = suite.inbox.surface("spend", {"amount": 1}, default="proceed", resolved="proceed")
    suite.inbox.resolve(e2, "approve")     # operator handles one

    lanes = suite.inbox_lanes()
    ids_escalation = {d["id"] for d in lanes["live_escalations"]}
    ids_resolved = {d["id"] for d in lanes["resolved_for_you"]}
    check("pending decision is a live escalation", e1 in ids_escalation)
    check("operator-resolved decision moves to resolved-for-you", e2 in ids_resolved)
    check("auto-proceeded SURFACE decision is in resolved-for-you", r1 in ids_resolved)
    check("counts are reported", lanes["counts"]["escalations"] == 1 and lanes["counts"]["resolved"] == 2)

    # batching groups pending decisions by theme (when 2+); here only 1 pending remains → no batch
    check("no batch when a theme has <2 pending", "code_build" not in lanes["batched"])
    # add another pending code_build → now a batch of 2
    suite.inbox.surface("code_build", {"name": "c", "code": "z"}, default="reject", resolved=None)
    lanes2 = suite.inbox_lanes()
    check("a theme with 2+ pending forms a batch", len(lanes2["batched"].get("code_build", [])) == 2)

    # drillability (F2): the raw payload is reachable from the surfaced decision
    d = suite.inbox.get(e1)
    check("raw payload is drillable (code preserved under the value layer)", d["payload"]["code"] == "x")

    print(f"\nALL {PASS} CHECKS PASS — inbox triaged into lanes; raw decision stays drillable")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
