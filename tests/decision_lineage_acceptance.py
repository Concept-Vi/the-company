"""tests/decision_lineage_acceptance.py — an audit must not silently truncate (fail-loud).

decision_view reconstructs a decision's full trajectory from the event log. It used to read
recent_events(999) — a NEWEST-first last-999 WINDOW — so a long-lived decision whose lineage is
buried under more than 999 newer events would silently TRUNCATE: the early proposed/framed events
fall outside the window and vanish from the audit, with no signal that anything was dropped. That
is exactly the silent truncation the fail-loud law forbids, and it was INCONSISTENT with
session_view, which reads the whole tail (events_since(-1)).

This proves decision_view now reads the FULL relevant history (the same way session_view does):
a decision whose lineage spans > 999 events is returned WHOLE, in order, nothing clipped.
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


store_dir = tempfile.mkdtemp(prefix="lineage-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # A decision is surfaced, then framed — the EARLY part of its lineage.
    sid = suite.inbox.surface("code_build", {"name": "longlived", "code": "x"}, default="reject", resolved=None)
    suite._emit("grow", "brain proposed 'longlived' — surfaced", node_name="longlived", surfaced=sid)
    suite._emit("frame", "framed the 'longlived' decision for the operator", surfaced=sid)

    # Now bury that lineage under FAR more than the old 999-event window: 1200 unrelated events.
    # Under the old recent_events(999) read, the two early events above would fall OUTSIDE the
    # newest-999 window and silently disappear from the audit.
    for i in range(1200):
        suite._emit("noise", f"unrelated activity #{i}")    # not tagged with surfaced=sid

    # The LATE part of the same decision's lineage: it is resolved with a reason (the why).
    suite.resolve_surfaced(sid, "reject", reason="superseded by a better design")

    total_events = len(store.events_since(-1))
    check("the log is deeper than the old 999 window (so truncation WOULD have bitten)",
          total_events > 999)

    view = suite.decision_view(sid)
    kinds = [e["kind"] for e in view["trajectory"]]

    # The WHOLE lineage is present — the early events the old window would have dropped survive.
    check("the EARLY 'grow' event survives (not truncated by a window)", "grow" in kinds)
    check("the EARLY 'frame' event survives (not truncated by a window)", "frame" in kinds)
    check("the LATE 'resolve' event is present", "resolve" in kinds)

    # Only this decision's events — the filter is on `surfaced`, the noise is excluded.
    check("only THIS decision's events are in the view (noise excluded)",
          all(e.get("surfaced") == sid for e in view["trajectory"]))

    # In order: proposed before framed before resolved — a faithful, whole trajectory.
    check("the trajectory is in chronological order (proposed → framed → resolved)",
          kinds.index("grow") < kinds.index("frame") < kinds.index("resolve"))

    # The reason (the why) rides in the trajectory — the audit carries the reasoning, whole.
    reason_ev = next(e for e in view["trajectory"] if e["kind"] == "resolve")
    check("the resolve reason rides in the (untruncated) trajectory",
          "superseded" in reason_ev.get("reason", ""))

    # The whole lineage survives end-to-end: the earliest event (grow, seq near the very start, far
    # outside any newest-999 window) AND the latest (resolve) both appear — proving the read spans the
    # FULL tail, behaviourally, exactly as session_view does. (No docstring assertions; behaviour only.)
    seqs = [e.get("seq", -1) for e in view["trajectory"]]
    first_kind = view["trajectory"][seqs.index(min(seqs))]["kind"]
    check("the FULL span is returned — earliest event is the proposal, not a mid-window clip",
          first_kind == "grow")

    print(f"\nALL {PASS} CHECKS PASS — decision_view reads the full lineage; a >999-event decision is "
          f"returned whole (no silent truncation; consistent with session_view)")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
