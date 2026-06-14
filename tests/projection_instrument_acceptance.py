"""projection_instrument_acceptance — THE TEETH for THE UNIVERSAL PROJECTION (Tim Geldard's
equation). The regression floor for `runtime/projection.py:project` + `BindingRegistry`.

WHY this test exists (read this before changing it):
  · There is a NAME COLLISION in the tree. `runtime/projections.py` + `tests/projections_acceptance.py`
    test an UNRELATED registry (the corpus DESCRIPTION-LENS registry — what/topics/principles/...). The
    INSTRUMENT (`runtime/projection.py`, singular) had NO test, so it could look green while broken.
    This file is that missing floor. Do NOT merge the two.
  · The instrument is a VARIABLE engine — "nothing hardcoded or fixed is valid, only what occupies that
    variable" (Tim, 2026-06-13). So the invariants here are about the SHAPE OF THE MATH (the lock
    x = 2π/n, even division, r∈[0,1], θ inside its wedge, data-driven sectors), NOT about any fixed
    sector list. A test that pinned "7 sectors" would re-introduce the very hardcode Tim deleted.
  · Later groups (G2 grid, G3 time-freeze, G6 semantic radius, G10 angle-from-a-registry) all CHANGE
    project()'s output. This suite is what guarantees those changes don't silently break the geometry —
    it guards the invariants that must hold ACROSS every change. So it deliberately does NOT assert the
    honest stubs that are SUPPOSED to change (rings:4, radius=time): freezing a stub would make the floor
    fight the next build. It asserts only what must stay true forever.

Run:  ./.venv/bin/python tests/projection_instrument_acceptance.py
"""
import copy
import math
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from runtime.projection import BindingRegistry, project, TAU

PASS = 0
FAIL = 0
EPS = 1e-6


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  {detail}")


# ---- fixtures: synthetic events (the instrument is a pure read over events the store already holds) ----
NOW = datetime(2026, 6, 13, 12, 0, 0, tzinfo=timezone.utc)


def ev(seq, kind, age_s, address="root/a/b"):
    t = NOW - timedelta(seconds=age_s)
    return {"seq": seq, "kind": kind, "ts": t.isoformat(), "address": address,
            "summary": f"event-{seq}-{kind}"}


def wedge_of(result, point):
    """The [from,to] wedge of the sector this point landed in (looked up by the point's sector id)."""
    for s in result["sectors"]:
        if s["id"] == point["sector"]:
            return s["from"], s["to"]
    return None


REAL = BindingRegistry().discover()  # the real bindings/ dir


# === 1 · the angle/radius/depth FLOOR holds for the data-driven default (raw) ===
print("=== 1 · the floor: r∈[0,1], θ inside its wedge, even division (raw, data-driven) ===")
events = [ev(i, k, age) for i, (k, age) in enumerate([
    ("chat", 10), ("chat", 300), ("op.run", 60), ("op.run", 5),
    ("error", 1200), ("decision.make", 90), ("corpus.record", 7200),
])]
raw = REAL.get("raw")
res = project(events, binding=raw, now=NOW, registry=REAL)

check("raw is data-driven: n == count of DISTINCT kinds (no hardcoded sector list)",
      res["n"] == len({e["kind"] for e in events}),
      f"n={res['n']}, distinct kinds={len({e['kind'] for e in events})}")
check("every point r ∈ [0,1]",
      all(0.0 - EPS <= p["r"] <= 1.0 + EPS for p in res["points"]),
      f"out-of-range rs: {[p['r'] for p in res['points'] if not (0 <= p['r'] <= 1)]}")
check("the oldest event sits at the rim (max r == 1.0)",
      abs(max(p["r"] for p in res["points"]) - 1.0) < 1e-4)
inside = all((lambda w: w and (w[0] - EPS <= p["theta"] <= w[1] + EPS))(wedge_of(res, p))
             for p in res["points"])
check("every point θ falls INSIDE its own sector wedge [from,to]", inside)
widths = [round(s["to"] - s["from"], 5) for s in res["sectors"]]
check("the lock x=2π/n: every sector width == 2π/n (even re-division)",
      widths and all(abs(w - TAU / res["n"]) < 1e-4 for w in widths),
      f"widths={widths}, 2π/n={TAU / res['n']:.5f}")
check("sector wedges tile the circle: first.from==0, last.to==2π, contiguous",
      res["sectors"] and abs(res["sectors"][0]["from"]) < 1e-6
      and abs(res["sectors"][-1]["to"] - TAU) < 1e-4
      and all(abs(res["sectors"][i]["to"] - res["sectors"][i + 1]["from"]) < 1e-6
              for i in range(len(res["sectors"]) - 1)))
check("order_by=count: sectors are ordered by descending frequency (data-driven order)",
      res["sectors"][0]["id"] in ("chat", "op.run"),  # the two count==2 kinds lead
      f"first sector={res['sectors'][0]['id']}")
check("depth is read from the address path segments (root/a/b → 2)",
      all(p["depth"] == 2 for p in res["points"]),
      f"depths={sorted({p['depth'] for p in res['points']})}")


# === 2 · NO HARDCODE: change the data → n changes (the variable engine, proven) ===
print("\n=== 2 · the variable engine: n follows the data, never a fixed list ===")
three = project([ev(i, k, 10) for i, k in enumerate(["a", "b", "c"])], binding=raw, now=NOW, registry=REAL)
five = project([ev(i, k, 10) for i, k in enumerate(["a", "b", "c", "d", "e"])], binding=raw, now=NOW, registry=REAL)
check("3 distinct kinds → n==3", three["n"] == 3, f"n={three['n']}")
check("5 distinct kinds → n==5 (re-divides; nothing frozen)", five["n"] == 5, f"n={five['n']}")
check("re-division stays even at n=5 (width==2π/5 each)",
      all(abs((s["to"] - s["from"]) - TAU / 5) < 1e-4 for s in five["sectors"]))


# === 3 · kind-group lens: the '*' remainder catches EVERYTHING (no point falls off the wheel) ===
print("\n=== 3 · the grouped lens: declared sectors + the '*' field remainder ===")
grouped = REAL.get("grouped")
gevents = [
    ev(0, "corpus.record", 10),     # → memory
    ev(1, "chat", 20),              # → conversation
    ev(2, "op.run", 30),           # → operations
    ev(3, "error", 40),            # → signals
    ev(4, "decision.make", 50),    # → decisions
    ev(5, "zzz_never_declared", 60),  # → field (the '*' remainder — the honest catch-all)
    ev(6, "another_unknown", 70),  # → field
]
gres = project(gevents, binding=grouped, now=NOW, registry=REAL)
by_seq = {p["seq"]: p for p in gres["points"]}
check("a corpus.* kind lands in 'memory'", by_seq[0]["sector"] == "memory", by_seq[0]["sector"])
check("a chat kind lands in 'conversation'", by_seq[1]["sector"] == "conversation", by_seq[1]["sector"])
check("an error kind lands in 'signals'", by_seq[3]["sector"] == "signals", by_seq[3]["sector"])
check("an UNDECLARED kind lands in the '*' remainder 'field' (nothing falls off)",
      by_seq[5]["sector"] == "field" and by_seq[6]["sector"] == "field",
      f"{by_seq[5]['sector']}, {by_seq[6]['sector']}")
check("EVERY grouped point still lands in a real sector (total accounted)",
      all(p["sector"] in {s["id"] for s in gres["sectors"]} for p in gres["points"]))
check("the grouped lens still obeys the floor: r∈[0,1] AND θ in-wedge",
      all(0 - EPS <= p["r"] <= 1 + EPS for p in gres["points"])
      and all((lambda w: w and w[0] - EPS <= p["theta"] <= w[1] + EPS)(wedge_of(gres, p))
              for p in gres["points"]))


# === 4 · the PURE-READ floor: project() never mutates its inputs (the instrument's law) ===
print("\n=== 4 · pure read: inputs are not mutated, no consequential verb ===")
src = [ev(i, k, age) for i, (k, age) in enumerate([("chat", 10), ("op.run", 20), ("error", 30)])]
snapshot = copy.deepcopy(src)
_ = project(src, binding=raw, now=NOW, registry=REAL)
check("the input events list is byte-for-byte unchanged after project()", src == snapshot)


# === 5 · limit + empty are handled (edge floors) ===
print("\n=== 5 · edges: limit and empty ===")
many = [ev(i, "chat", 100 - i) for i in range(5)]
lim = project(many, binding=raw, now=NOW, limit=2, registry=REAL)
check("limit=2 over 5 events → exactly 2 points", lim["count"] == 2, f"count={lim['count']}")
empty = project([], binding=raw, now=NOW, registry=REAL)
check("empty events → count 0, n>=1, no crash", empty["count"] == 0 and empty["n"] >= 1)


# === 6 · default binding: no binding id → the data-driven raw default (no privileged hardcode) ===
print("\n=== 6 · the default resolves to the data-driven raw binding ===")
dflt = project(events, binding=None, now=NOW, registry=REAL)
check("binding=None resolves to a kind/data-driven default (angle_from=='kind')",
      dflt["binding"]["angle_from"] == "kind", dflt["binding"])
check("the registry advertises the declared bindings (raw, grouped, time-of-day all present)",
      {"raw", "grouped", "time-of-day"} <= {b["id"] for b in dflt["bindings"]},
      {b["id"] for b in dflt["bindings"]})


# === 7 · BindingRegistry discovery is FAIL-LOUD on a malformed row (registry-is-truth) ===
print("\n=== 7 · discovery fails loud on a bad binding row ===")


def discovery_raises(filename, content):
    d = tempfile.mkdtemp(prefix="badbind_")
    with open(os.path.join(d, filename), "w", encoding="utf-8") as f:
        f.write(content)
    try:
        BindingRegistry().discover((d,))
        return False
    except ValueError:
        return True
    except Exception:
        return False


check("a file with NO BINDING dict → ValueError",
      discovery_raises("nobind.py", "X = 1\n"))
check("a BINDING missing a required field → ValueError",
      discovery_raises("missing.py", "BINDING = {'id': 'missing', 'label': 'x'}\n"))
check("a BINDING whose id != filename stem → ValueError",
      discovery_raises("mismatch.py",
                       "BINDING = {'id': 'other', 'label': 'x', 'angle_from': 'kind', 'radius_from': 'time'}\n"))


def discovery_ok():
    d = tempfile.mkdtemp(prefix="goodbind_")
    with open(os.path.join(d, "ok.py"), "w", encoding="utf-8") as f:
        f.write("BINDING = {'id': 'ok', 'label': 'OK', 'angle_from': 'kind', 'radius_from': 'time'}\n")
    reg = BindingRegistry().discover((d,))
    return reg.get("ok")["id"] == "ok"


check("a well-formed binding row discovers cleanly (happy path)", discovery_ok())


# === 8 · the TIME SCRUBBER (Group 3): now= moves the centre into the past; only ts≤now is projected ===
print("\n=== 8 · the time scrubber (now=) projects only the past relative to the centre ===")
scrub_events = [ev(0, "chat", 50), ev(1, "chat", 200), ev(2, "op.run", 300)]
# scrub the centre back to NOW-100s → the age-50 event is now in the FUTURE (excluded); 200/300 remain.
scrubbed = project(scrub_events, binding=raw, now=NOW - timedelta(seconds=100), registry=REAL)
seqs = {p["seq"] for p in scrubbed["points"]}
check("scrubbing now back EXCLUDES events stamped after the new centre (the future)",
      0 not in seqs, f"seqs={sorted(seqs)} (seq 0 @ age 50s should fall after now=NOW-100s)")
check("events at-or-before the scrubbed centre remain", {1, 2} <= seqs, f"seqs={sorted(seqs)}")
check("the scrubbed projection still obeys the floor (r∈[0,1])",
      all(0 - EPS <= p["r"] <= 1 + EPS for p in scrubbed["points"]))
check("the reported `now` is the scrubbed centre, not wall-clock",
      scrubbed["now"].startswith((NOW - timedelta(seconds=100)).isoformat()[:19]), scrubbed["now"])


# === 9 · the RELATIVE ADDRESS CENTRE (Group 3): center= → radius is structural tree-distance ===
print("\n=== 9 · the address centre (center=) re-projects radius as tree-distance (structural) ===")
ac_events = [
    ev(0, "x", 10, address="ui://a/b"),     # AT the centre → tree-distance 0
    ev(1, "x", 20, address="ui://a/b/c"),   # child  → 1
    ev(2, "x", 30, address="ui://a/x"),     # sibling → 2
    ev(3, "x", 40, address="ui://z"),       # far    → 3
]
ac = project(ac_events, binding=raw, now=NOW, center="ui://a/b", registry=REAL)
by = {p["seq"]: p for p in ac["points"]}
check("center= is reported AND radius_from flips to 'address'",
      ac["center"] == "ui://a/b" and ac["binding"]["radius_from"] == "address",
      f"center={ac['center']} radius_from={ac['binding']['radius_from']}")
check("the event AT the centre address sits at r==0 (the origin)", abs(by[0]["r"]) < 1e-6, f"r={by[0]['r']}")
check("radius grows with tree-distance (centre < child < sibling ≤ far)",
      by[0]["r"] < by[1]["r"] < by[2]["r"] <= by[3]["r"],
      f"rs={[round(by[s]['r'], 3) for s in (0, 1, 2, 3)]}")
check("every address-centred r stays in [0,1]", all(0 - EPS <= p["r"] <= 1 + EPS for p in ac["points"]))
check("center absent → falls back to the temporal centre (radius_from='time', center=='now')",
      (lambda d: d["binding"]["radius_from"] == "time" and d["center"] == "now")(
          project(ac_events, binding=raw, now=NOW, registry=REAL)))


# === 10 · the SQUARE / STRUCTURE half (Group 2): dyadic (i,j) cell + m/2 rings from the address hierarchy ===
print("\n=== 10 · the structural grid: dyadic (i,j) cell per point + rings == grid/2 (seed §1) ===")
from runtime.projection import _grid_cell
ge = [ev(i, "x", 10, address=a) for i, a in enumerate(
    ["ui://a", "ui://a/b", "ui://a/b/c", "ui://a/b/c/d", "run://x/y/z", ""])]
gp = project(ge, binding=raw, now=NOW, registry=REAL)
gm = gp["grid"]
check("the grid resolution m is a power of 2 (the dyadic subdivision), >=1",
      gm >= 1 and (gm & (gm - 1)) == 0, f"grid={gm}")
check("rings == m/2 (the seed relationship; the rings:4 stub is GONE)",
      gp["rings"] == max(gm // 2, 1), f"rings={gp['rings']} grid={gm}")
check("EVERY point carries a dyadic cell {i,j,d}, bounded 0<=i,j<2^d (a parent cell contains its children)",
      all(0 <= p["cell"]["i"] < (1 << p["cell"]["d"]) and 0 <= p["cell"]["j"] < (1 << p["cell"]["d"])
          and p["cell"]["d"] >= 0 for p in gp["points"]),
      f"cells={[p['cell'] for p in gp['points']]}")
check("cell depth tracks address nesting, capped at 4 (deeper path → deeper d)",
      max(p["cell"]["d"] for p in gp["points"]) == 4
      and {p["cell"]["d"] for p in gp["points"]} >= {0, 1, 2, 3, 4},
      f"depths={sorted({p['cell']['d'] for p in gp['points']})}")
check("the cell is deterministic + scheme-agnostic (ui://a/b→d2, run://x/y/z→d3, ''→(0,0,0))",
      _grid_cell("ui://a/b") == _grid_cell("ui://a/b") and _grid_cell("ui://a/b")[2] == 2
      and _grid_cell("run://x/y/z")[2] == 3 and _grid_cell("") == (0, 0, 0))
check("nesting is containment: a child's MSB quadrant == its parent's cell (parent contains child)",
      (lambda P, C: C[2] == P[2] + 1 and (C[0] >> 1) == P[0] and (C[1] >> 1) == P[1])
      (_grid_cell("ui://a/b"), _grid_cell("ui://a/b/c")))


# === 11 · GROUP 10 — the event→row edge + angle-from-a-registry + order-from-edges ===
print("=== 11 · the event→row edge, angle_from=<registry>, order_by=edge (Group 10) ===")
from runtime.projection import _singular, _row_of, _toposort

check("_singular depluralizes (the event→row field convention): projections→projection, mark_types→mark_type",
      _singular("projections") == "projection" and _singular("mark_types") == "mark_type"
      and _singular("relation_types") == "relation_type" and _singular("roles") == "role")
check("the event→row edge reads the singular field (op.run→role, corpus.record→projection)",
      _row_of({"kind": "op.run", "role": "repo_digest"}, "roles") == "repo_digest"
      and _row_of({"kind": "corpus.record", "projection": "topics"}, "projections") == "topics")
check("the event→row edge reads a GRAPH's node (connect→from_node), None when no row is named",
      _row_of({"kind": "connect", "from_node": "c", "to_node": "u"}, "graph") == "c"
      and _row_of({"kind": "chat"}, "roles") is None)

# angle_from=<registry>: sectors = the rows PRESENT in the data + an honest '—' remainder for unmapped events
g10_evs = [ev(i, "corpus.record", 10, "x") | {"projection": p}
           for i, p in enumerate(["topics", "topics", "principles", "worldview"])]
g10_evs.append(ev(99, "chat", 5))            # no projection → the remainder
B_reg = {"id": "byp", "label": "by projection", "angle_from": "projections", "radius_from": "time", "order_by": "count"}
r_reg = project(g10_evs, binding=B_reg, now=NOW, sector_ids=["topics", "principles", "worldview", "repo"], registry=REAL)
sids = [s["id"] for s in r_reg["sectors"]]
check("angle_from=<registry>: sectors are the PRESENT rows (count order) + an honest '—' remainder",
      sids == ["topics", "principles", "worldview", "—"], f"sectors={sids}")
check("angle_from=<registry>: an event maps to the sector of the row its edge names (a topics event → topics)",
      next(p for p in r_reg["points"] if p["seq"] == 0)["sector"] == "topics")
check("angle_from=<registry>: an event naming no row lands in the '—' remainder (never forced)",
      next(p for p in r_reg["points"] if p["seq"] == 99)["sector"] == "—")

# order_by=edge: topological over REAL directed edges, STABLE, and edge-respecting; cycle-safe; no-edge→count
ids4, edges4 = ["c", "b", "a", "d"], [("a", "b"), ("b", "c")]   # a→b→c, d free
topo = _toposort(ids4, edges4, key=lambda r: r)
check("order_by=edge: _toposort respects every directed edge (a before b before c)",
      topo.index("a") < topo.index("b") < topo.index("c") and "d" in topo)
check("order_by=edge: _toposort is STABLE (same inputs → same order)",
      _toposort(ids4, edges4, key=lambda r: r) == topo)
check("order_by=edge: a CYCLE is cycle-safe (all rows present, no infinite loop / drop)",
      sorted(_toposort(["a", "b"], [("a", "b"), ("b", "a")], key=lambda r: r)) == ["a", "b"])
B_edge = {"id": "bpe", "label": "edge", "angle_from": "projections", "radius_from": "time", "order_by": "edge"}
r_edge = project(g10_evs, binding=B_edge, now=NOW, sector_ids=["topics", "principles", "worldview"],
                 sector_edges=[("worldview", "topics"), ("topics", "principles")], registry=REAL)
esids = [s["id"] for s in r_edge["sectors"] if s["id"] != "—"]
check("order_by=edge: sectors arranged by the real edges (worldview→topics→principles), alphabetical retired",
      esids == ["worldview", "topics", "principles"], f"edge-order={esids}")
r_noedge = project(g10_evs, binding=B_edge, now=NOW, sector_ids=["topics", "principles", "worldview"],
                   sector_edges=[], registry=REAL)
check("order_by=edge with NO edges → honest fallback to count (never a fabricated sequence)",
      [s["id"] for s in r_noedge["sectors"] if s["id"] != "—"] == ["topics", "principles", "worldview"])
check("Group 10 is ADDITIVE: the data-driven 'kind' default is unchanged (sector_ids ignored when angle_from=kind)",
      [s["id"] for s in project(events, binding=raw, now=NOW, sector_ids=["x"], registry=REAL)["sectors"]]
      == [s["id"] for s in res["sectors"]])

print("=== 12 · the CONNECTIONS — edges surfaced for drawing + whole_set + bidir (Group 10 / Tim 2026-06-14) ===")
# THE CONNECTIONS IN THE REGISTRIES: the directional typed edges are SURFACED in the output (directed
# sector-index pairs) so the surface can DRAW them as chords, not merely order by them.
B_conn = {"id": "bconn", "label": "conn", "angle_from": "projections", "radius_from": "time", "order_by": "edge"}
r_conn = project(g10_evs, binding=B_conn, now=NOW, sector_ids=["topics", "principles", "worldview"],
                 sector_edges=[("worldview", "topics"), ("topics", "principles")], registry=REAL)
_sidx = {s["id"]: i for i, s in enumerate(r_conn["sectors"])}
check("edges are surfaced as DIRECTED sector-index pairs (the connections, for drawing the chords)",
      {(_sidx.get("worldview"), _sidx.get("topics")), (_sidx.get("topics"), _sidx.get("principles"))}
      == {(e["from"], e["to"]) for e in r_conn["edges"]}, f"edges={r_conn['edges']}")
check("a non-edge binding surfaces NO edges (additive: `edges` defaults empty)",
      project(events, binding=raw, now=NOW, registry=REAL)["edges"] == [])
# whole_set — render the WHOLE registry's rows (its STRUCTURE), not only the rows present in event data
B_whole = {"id": "bwhole", "label": "whole", "angle_from": "projections", "radius_from": "time",
           "order_by": "count", "whole_set": True}
w_ids = [s["id"] for s in project(g10_evs, binding=B_whole, now=NOW,
         sector_ids=["topics", "principles", "worldview", "ghost"], registry=REAL)["sectors"]]
check("whole_set: ALL candidate rows render — even a row NO event touched (the registry structure)",
      "ghost" in w_ids and all(x in w_ids for x in ("topics", "principles", "worldview")), f"ids={w_ids}")
check("whole_set: NO '—' remainder (the set IS the whole registry; nothing is outside it)", "—" not in w_ids)
# bidir — a REAL mutual edge (A→B AND B→A) is flagged, rendered AS a cycle (nonsequential is valid), not dropped
r_bidir = project(g10_evs, binding=B_conn, now=NOW, sector_ids=["topics", "principles"],
                  sector_edges=[("topics", "principles"), ("principles", "topics")], registry=REAL)
check("a mutual edge (A→B and B→A) is flagged `bidir` (a cycle rendered as a cycle, not flattened/dropped)",
      len(r_bidir["edges"]) == 2 and all(e.get("bidir") for e in r_bidir["edges"]))
# edges only between PRESENT sectors; a self-loop is dropped (a chord to itself is not a connection)
r_self = project(g10_evs, binding=B_conn, now=NOW, sector_ids=["topics", "principles"],
                 sector_edges=[("topics", "topics"), ("topics", "missing")], registry=REAL)
check("edges drop self-loops and edges to absent rows (only real connections between present sectors)",
      r_self["edges"] == [])
# whole_set point-drop: an event mapping to NO rendered row is DROPPED (not piled into the last sector — the
# connections view is the registry's rows + edges, never a dump of unmappable events).
g10_plus = g10_evs + [{"seq": 9001, "ts": NOW.isoformat(), "kind": "op.run", "op": "x"}]  # an event with no projection → no row
r_drop = project(g10_plus, binding=B_whole, now=NOW,
                 sector_ids=["topics", "principles", "worldview"], registry=REAL)
check("whole_set: an event mapping to NO row is DROPPED (not piled into the last sector)",
      all(p["sector"] in ("topics", "principles", "worldview") for p in r_drop["points"])
      and len(r_drop["points"]) == len([e for e in g10_evs if e.get("projection") in ("topics", "principles", "worldview")]),
      f"points={len(r_drop['points'])}")

print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
