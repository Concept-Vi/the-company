"""tests/trajectory_acceptance.py — trajectory as training signal (slice 8, I1-I2).

Persist the PATH, not the endpoint (context-05): the why, the order, the rejections. The event
log is the captured trajectory; a DECISION becomes a VIEW derived from it — proposed → resolved
(with the operator's reason) — replayable + auditable. The endpoint without its why is brittle;
the trajectory carries the reasoning that generalises (and is the twin's richest training signal).
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


store_dir = tempfile.mkdtemp(prefix="traj-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # a decision is surfaced, framed, then resolved WITH A REASON (the why)
    sid = suite.inbox.surface("code_build", {"name": "demo", "code": "x"}, default="reject", resolved=None)
    suite._emit("grow", "brain wrote a 'demo' node — surfaced", node_name="demo", surfaced=sid)
    suite.resolve_surfaced(sid, "reject", reason="we already have wordcount; redundant")

    # I1 — the reason (the why) is captured, not just the endpoint
    d = suite.inbox.get(sid)
    check("the endpoint is captured", d["resolved"] == "reject")
    check("the WHY is captured (not just the endpoint)", d.get("reason", "").startswith("we already"))

    # I2 — the decision is a VIEW derived from the event log: its ordered trajectory
    view = suite.decision_view(sid)
    kinds = [e["kind"] for e in view["trajectory"]]
    check("decision view reconstructs the path from the log", "grow" in kinds and "resolve" in kinds)
    check("the trajectory is in order (proposed before resolved)",
          kinds.index("grow") < kinds.index("resolve"))
    reason_ev = next(e for e in view["trajectory"] if e["kind"] == "resolve")
    check("the reason rides in the trajectory", "redundant" in reason_ev.get("reason", ""))

    # replay — the whole path, oldest-first (the training signal)
    rp = suite.replay(50)
    check("replay returns the path oldest-first", rp[0]["seq"] < rp[-1]["seq"])

    print(f"\nALL {PASS} CHECKS PASS — trajectory captured (path + why); decisions are views over the log")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
