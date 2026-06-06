"""tests/journey_recording_acceptance.py — L9 · reverse journey-recording (§21.7#2-reverse, fidelity ISSUE-5).

The FORWARD resolve is done (present_current + resolveUiTarget drive the view TO an address). The
REVERSE was dropped: no code captured a free click-path through addresses as an ordered journey. The
review-session organ records REVIEW sessions (item-ids walked with a cursor), NOT navigation. L9 adds a
PARALLEL, DISTINCT object — a journey-record: an explicit start → each indicate appends a step → stop
finalizes; the ordered addressed path is then replayable (the FE steps through it via the preserved
forward resolver). This suite proves:

  1. start → append an ordered sequence of ui:// addresses → stop ⇒ the record holds the ordered path.
  2. the journey is retrievable + replayable (the ordered addresses come back IN ORDER, by id).
  3. a malformed address in a step FAILS LOUD (the S0 grammar gate, reusing parse_ui_address).
  4. the review-session organ (start_session / present_current / next) STILL WORKS UNCHANGED — the
     journey is a DISTINCT object, it does not repurpose or overload the review organ.
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


store_dir = tempfile.mkdtemp(prefix="journey-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # --- 1. start → append an ordered path → stop ----------------------------------------------------
    started = suite.start_journey()
    jid = started["id"]
    check("start_journey returns a journey id", isinstance(jid, str) and jid.strip() != "")
    check("a fresh journey is open (not done) with no steps", started.get("done") is False and started.get("steps") == [])

    path = ["ui://chrome/inbox", "ui://canvas/*", "ui://toolbar/run", "ui://chrome/chat"]
    for addr in path:
        suite.append_journey_step(jid, addr)
    stopped = suite.stop_journey(jid)
    check("stop_journey finalizes the journey (done)", stopped.get("done") is True)
    check("the record holds the ordered path",
          [s["address"] for s in stopped["steps"]] == path)
    check("each step is an OPEN dict carrying a ts (the {ts,**} convention)",
          all("address" in s and "ts" in s for s in stopped["steps"]))

    # --- 2. retrievable + replayable (ordered addresses come back in order, by id) -------------------
    loaded = suite.get_journey(jid)
    check("get_journey retrieves the SAME ordered path by id",
          [s["address"] for s in loaded["steps"]] == path)
    replay = suite.replay_journey(jid)
    check("replay_journey returns the ordered addresses (the walkthrough vocabulary)",
          replay["addresses"] == path)
    check("replay carries the journey id (so the FE steps through it via resolveUiTarget)",
          replay.get("journey") == jid)

    # --- 3. a malformed address in a step FAILS LOUD (the S0 gate, parse_ui_address) -----------------
    j2 = suite.start_journey()["id"]
    raised = False
    try:
        suite.append_journey_step(j2, "not a ui address")
    except Exception:
        raised = True
    check("a malformed step address fails loud (S0 grammar gate)", raised)
    # the bad step was rejected — the journey stays clean (no junk step persisted)
    check("the rejected step was NOT persisted (fail-loud, never a junk step)",
          suite.get_journey(j2)["steps"] == [])

    # appending to a finalized journey fails loud (no silent no-op)
    closed = False
    try:
        suite.append_journey_step(jid, "ui://chrome/inbox")
    except Exception:
        closed = True
    check("appending to a stopped journey fails loud (no silent no-op)", closed)

    # --- 4. the review-session organ STILL WORKS UNCHANGED (distinct object, no overload) ------------
    # build a review item the session organ can walk (a surfaced output), then drive start/present/next.
    g = "journey-preserve"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="src")
    suite.create_node(g, "uppercase", node_id="up")
    suite.connect(g, "src", "value", "up", "text")
    suite.run(g)
    surfaced = suite.surface_output(g, "up")
    item_id = surfaced["id"]
    session = suite.start_session([item_id], mode="walkthrough")
    check("review-session organ: start_session presents the first step (UNCHANGED)",
          session.get("item") == item_id and session.get("done") is False)
    cur = suite.present_current(session["session"])
    check("review-session organ: present_current returns the cursor step (UNCHANGED)",
          cur.get("item") == item_id and cur.get("ui_target") == f"ui://review/{item_id}")
    advanced = suite.next(session["session"])
    check("review-session organ: next advances the cursor to done (UNCHANGED)",
          advanced.get("done") is True and advanced.get("cursor") == 1)
    # the journey object is genuinely DISTINCT — a journey id is not a session id and vice versa.
    check("a journey id is NOT a review-session (distinct stores, distinct objects)",
          suite.store.load_session(jid) is None)

    print(f"\nALL {PASS} CHECKS PASS — L9 reverse journey-recording: ordered click-path captured, "
          f"replayable, S0-gated, review organ preserved.")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
