"""tests/state_types_acceptance.py — the STATE-TYPE REGISTRY (Possibility Space Block 19, smallest-first).

Node "state" is a REGISTERED, single-source set — not a hardcoded enum scattered through state().
The derivation reads its status-ids from one declared registry (`Suite.NODE_STATES`), and the registry
is exposed through `capabilities().node_states` so the surface renders from it (registry-is-truth)
instead of hardcoding the vocabulary.

Two faces of the proof:
  Step A (no behaviour change) — the four EXISTING statuses (idle/ran/cached/stuck) derive EXACTLY as
    before for COMPUTE nodes (RESOLVE='compute'); the other acceptance suites staying green is the
    by-construction proof, this suite pins the per-status cases directly too.
  Step B (additive) — reference-resolved nodes (RESOLVE='reference', i.e. portals) report `live`
    (the ref resolves to content) or `empty` (None/dangling/unresolved ref) — NOT idle/cached. A portal
    used to FLIP idle↔cached across run-vs-reload; that flip is structurally GONE (both paths agree).

Executing nodes are UNAFFECTED — scoped by `applies_to` (resolve-mode 'compute').
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


def status_of(st, nid):
    return next(n for n in st["nodes"] if n["id"] == nid)["status"]


store_dir = tempfile.mkdtemp(prefix="statetypes-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)

    # ---- (4) capabilities().node_states lists all states with applies_to + means ----
    cap = suite.capabilities()
    check("capabilities() exposes node_states", "node_states" in cap)
    ns = cap["node_states"]
    ids = {s["id"] for s in ns}
    check("node_states includes the four compute statuses + the two reference statuses",
          {"idle", "ran", "cached", "stuck", "live", "empty"} <= ids)
    for s in ns:
        check(f"node_state {s['id']!r} carries means + applies_to + label",
              bool(s.get("means")) and bool(s.get("applies_to")) and "label" in s)
    # applies_to is scoped by resolve-mode: the four executing statuses are compute-scoped,
    # the two new ones reference-scoped.
    by_id = {s["id"]: s for s in ns}
    for sid in ("idle", "ran", "cached", "stuck"):
        check(f"{sid!r} applies_to compute (executing nodes)", "compute" in by_id[sid]["applies_to"])
    for sid in ("live", "empty"):
        check(f"{sid!r} applies_to reference (portals)", "reference" in by_id[sid]["applies_to"])

    # ---- (1) the four EXISTING statuses derive UNCHANGED (compute nodes) ----
    g = "compute-graph"
    # idle: a node that has never run and holds no result
    suite.create_node(g, "constant", config={"value": "hello"}, node_id="c1")
    suite.create_node(g, "uppercase", node_id="up")  # has a required input port, unwired → stuck on run
    st0 = suite.state(g)
    check("compute node with no result reports idle (unchanged)", status_of(st0, "c1") == "idle")

    # ran + cached: run once → ran; run again with no config change → cached (memo hit)
    suite.delete_node(g, "up")  # drop the unwired node so the first run is clean
    r1 = suite.run(g)
    st_fresh = suite.state(g, result=r1)
    check("compute node fires → ran (fresh-result path, unchanged)", status_of(st_fresh, "c1") == "ran")
    r2 = suite.run(g)
    st_cached = suite.state(g, result=r2)
    check("compute node memo-hit → cached (fresh-result path, unchanged)", status_of(st_cached, "c1") == "cached")
    # reload (no result) → a node whose output address resolves reports cached (unchanged)
    st_reload = suite.state(g)
    check("compute node on reload (resolved address) → cached (unchanged)", status_of(st_reload, "c1") == "cached")

    # stuck: a node whose required input never resolved on the last run
    gs = "stuck-graph"
    suite.create_node(gs, "uppercase", node_id="orphan")  # uppercase needs an input; none wired → stuck
    rs = suite.run(gs)
    check("scheduler reports the orphan stuck", "orphan" in rs.get("stuck", []))
    st_stuck = suite.state(gs, result=rs)
    check("compute node with unresolved input → stuck (fresh-result path, unchanged)",
          status_of(st_stuck, "orphan") == "stuck")
    st_stuck_reload = suite.state(gs)  # no result → derived from last run event
    check("stuck survives reload (backend-authoritative, unchanged)",
          status_of(st_stuck_reload, "orphan") == "stuck")

    # ---- (2) a portal whose ref resolves reports `live`, NOT cached/idle ----
    gp = "portal-graph"
    suite.create_node(gp, "constant", config={"value": "source-content"}, node_id="src")
    suite.create_node(gp, "portal", config={"ref": f"run://{gp}/src"}, node_id="win")
    rp = suite.run(gp)
    st_p_fresh = suite.state(gp, result=rp)
    check("portal with a resolving ref → live (NOT idle) on the fresh-result path",
          status_of(st_p_fresh, "win") == "live")
    check("portal still shows the source content live",
          next(n for n in st_p_fresh["nodes"] if n["id"] == "win")["output"] == "source-content")
    st_p_reload = suite.state(gp)
    check("portal with a resolving ref → live (NOT cached) on the reload path",
          status_of(st_p_reload, "win") == "live")

    # ---- (3) a portal with a dangling/None ref reports `empty` ----
    suite.create_node(gp, "portal", config={"ref": f"run://{gp}/does-not-exist"}, node_id="dangling")
    suite.create_node(gp, "portal", config={"ref": ""}, node_id="noref")
    st_e = suite.state(gp)
    check("portal with a dangling ref → empty", status_of(st_e, "dangling") == "empty")
    check("portal with a None/empty ref → empty", status_of(st_e, "noref") == "empty")
    check("empty portal output is None (no fabrication)",
          next(n for n in st_e["nodes"] if n["id"] == "noref")["output"] is None)

    # ---- (5) the idle↔cached flip-on-reload for a portal is GONE ----
    # The flip lived BETWEEN paths (fresh-result → idle, reload → cached). Cross-path agreement is the
    # proof it is gone: run, read the post-run (fresh-result) status AND the reload status — both `live`,
    # and a SECOND reload is still `live` (stable, no flip).
    rflip = suite.run(gp)
    s_fresh = status_of(suite.state(gp, result=rflip), "win")
    s_reload1 = status_of(suite.state(gp), "win")
    s_reload2 = status_of(suite.state(gp), "win")
    check("portal status is STABLE 'live' across fresh-result + two reloads (no idle↔cached flip)",
          s_fresh == s_reload1 == s_reload2 == "live")

    print(f"\nALL {PASS} CHECKS PASS — node-states are a registered single-source set; "
          f"portals report live/empty, the four executing statuses are unchanged, the flip is gone")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
