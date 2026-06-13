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


print(f"\n{'PASS' if FAIL == 0 else 'FAIL'} — {PASS} passed, {FAIL} failed")
sys.exit(0 if FAIL == 0 else 1)
