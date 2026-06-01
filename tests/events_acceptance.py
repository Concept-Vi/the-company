"""tests/events_acceptance.py — the event log (I2 "event log" surface).

Captured trajectory (context-13): an append-only activity stream so the operator can see
what happened and it PERSISTS across sessions. The store gains an append-only events log;
the Suite emits an event on every action (run · create · connect · delete · grow · approve).
Newest-first read powers the canvas event-log panel and the presence dial.
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


store_dir = tempfile.mkdtemp(prefix="events-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))

    # --- store layer: append-only, newest-first, bounded read ---
    store.append_event({"kind": "test", "summary": "first"})
    store.append_event({"kind": "test", "summary": "second"})
    store.append_event({"kind": "test", "summary": "third"})
    recent = store.recent_events(limit=2)
    check("recent_events returns newest-first", recent[0]["summary"] == "third")
    check("recent_events respects the limit", len(recent) == 2)
    check("events are stamped with a monotonic seq", recent[0]["seq"] > recent[1]["seq"])
    check("events carry a timestamp", "ts" in recent[0] and recent[0]["ts"])

    # --- persistence across a fresh store handle (continuity) ---
    store2 = FsStore(os.path.join(store_dir, "store"))
    check("events persist across sessions", store2.recent_events(limit=10)[0]["summary"] == "third")

    # --- Suite emits an event per action ---
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store2, reg, nodes_dir=NODES)
    before = len(store2.recent_events(limit=999))
    g = "events-graph"
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c")
    suite.create_node(g, "uppercase", node_id="u")
    suite.connect(g, "c", "value", "u", "text")
    suite.run(g)
    suite.delete_node(g, "u")
    after = store2.recent_events(limit=999)
    kinds = [e["kind"] for e in after[: len(after) - before]]
    check("create_node emitted an event", "create" in kinds)
    check("connect emitted an event", "connect" in kinds)
    check("run emitted an event", "run" in kinds)
    check("delete emitted an event", "delete" in kinds)
    run_ev = next(e for e in after if e["kind"] == "run")
    check("run event records what ran", "ran" in run_ev and run_ev.get("graph") == g)

    # --- now-view + presence derive live from state/inbox/log ---
    now = suite.now(g)
    check("now-view reports the graph", now["graph"] == g)
    check("now-view counts nodes", now["nodes_total"] == 1)   # u was deleted; c remains
    check("now-view counts resolved", now["nodes_resolved"] == 1)
    check("presence reads 'ready · all resolved' when nothing pending", now["presence"].startswith("ready"))
    check("now-view surfaces the last event", now["last_event"] is not None)

    print(f"\nALL {PASS} CHECKS PASS — event log + now-view + presence, surfaced newest-first")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
