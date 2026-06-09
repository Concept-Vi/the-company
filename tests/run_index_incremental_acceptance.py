#!/usr/bin/env python3
"""tests/run_index_incremental_acceptance.py — E2 (SUITE-2 lane): the run index is INCREMENTAL.

`list_runs`/`find_runs` USED to re-read + re-filter the WHOLE op.run event log on EVERY call (O(events),
caught at scale). E2 makes the projection incremental: hold the projected rows + a high-water seq, and on
each call read ONLY `events_since(high_water)` (the new tail) — the op.run log STAYS the source of truth
(no parallel store, no fs_store edit), the cache is a pure derived projection.

PROOF BY USE (the teeth — not "it returns the same answer", but "it does NOT full-reparse"):
  1. correctness: the incremental cache returns EXACTLY the same rows a full cold scan would (we compare
     against a freshly-constructed Suite over the same store).
  2. INCREMENTAL: a 2nd call after one new run reads only the DELTA from the log, not all events — proven
     by spying on `events_since` and asserting the cursor it is called with ADVANCES (it is NOT -1 the 2nd
     time). A full-reparse would always pass -1 (read everything); the incremental fold passes the held
     high-water.
  3. total_records keeps the pre-E2 EVENT-count semantics (a fan event = N rows but ONE record).
  4. cross-PROCESS-shape: a SECOND Suite over the SAME store dir (a sibling process's view) rebuilds the
     full index from the shared log (it never sees the first Suite's in-RAM cache).
"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from runtime.suite import Suite
from runtime.registry import NodeRegistry

PASS = 0
def check(label, cond):
    global PASS
    mark = "ok " if cond else "XX "
    print(f"  {mark} {label}")
    if not cond:
        raise SystemExit(f"FAIL: {label}")
    PASS += 1


def _suite(root):
    store = FsStore(root)
    reg = NodeRegistry().discover([os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes")])
    return Suite(store, reg)


def _seed_run(suite, turn, role, addr):
    """Emit one op.run ENGINE_RUN_OP record the way the engine does (one-emit-per-fan, addresses list)."""
    suite.emit_run_record("cognition.run_role", 5, run_op="generate", turn_id=turn, role=role,
                          addresses=[addr])


with tempfile.TemporaryDirectory() as root:
    suite = _suite(root)

    print("[1] correctness — the incremental cache == a full cold scan")
    _seed_run(suite, "t1", "ground", "run://t1/ground")
    _seed_run(suite, "t2", "recall", "run://t2/recall")
    # the op.run log also carries NON-engine telemetry (voice.client etc.) — the index must ignore it
    suite.emit_run_record("voice.client", 3, step="vad")
    incremental = suite.list_runs(limit=999)["runs"]
    cold = _suite(root).list_runs(limit=999)["runs"]   # a fresh Suite folds the whole log from scratch
    check("1 incremental rows == cold-scan rows (same addresses, newest-first)",
          [r["address"] for r in incremental] == [r["address"] for r in cold])
    check("1 the index IGNORES non-engine op.run records (voice.client absent)",
          all(r["op"] in suite.ENGINE_RUN_OPS for r in incremental))
    check("1 both seeded runs discovered", {"run://t1/ground", "run://t2/recall"} <=
          {r["address"] for r in incremental})

    print("\n[2] INCREMENTAL — a 2nd call reads only the DELTA, not the whole log (the teeth)")
    # spy on events_since: record the cursor it is called with on each invocation.
    calls = []
    orig = suite.events_since
    def spy(seq):
        calls.append(seq)
        return orig(seq)
    suite.events_since = spy
    suite.list_runs(limit=999)                                  # call A — folds from the held high-water
    hw_after_A = suite._run_index_hw
    _seed_run(suite, "t3", "ground", "run://t3/ground")         # one NEW run appended
    suite.list_runs(limit=999)                                  # call B — must read ONLY past hw_after_A
    check("2 the fold is incremental: call B's events_since cursor == the high-water after call A "
          "(NOT -1 / a full re-read)", len(calls) >= 2 and calls[1] == hw_after_A)
    check("2 the new run was picked up by the incremental fold",
          "run://t3/ground" in {r["address"] for r in suite.list_runs(limit=999)["runs"]})
    suite.events_since = orig

    print("\n[3] total_records keeps EVENT-count semantics (a fan = N rows, ONE record)")
    suite2 = _suite(os.path.join(root, "sub"))
    os.makedirs(os.path.join(root, "sub"), exist_ok=True)
    # a single fan event with 3 addresses → 3 rows but ONE record
    suite2.emit_run_record("cognition.run_items", 9, run_op="generate", turn_id="f1", role="digest",
                           addresses=["run://f1/digest/0", "run://f1/digest/1", "run://f1/digest/2"])
    res = suite2.list_runs(limit=999)
    check("3 a 3-address fan projects to 3 discovered rows", len(res["runs"]) == 3)
    check("3 total_records counts the ONE underlying event (not the 3 rows)", res["total_records"] == 1)

    print("\n[4] cross-PROCESS shape — a sibling Suite rebuilds from the shared log")
    sibling = _suite(root)                                       # a 2nd Suite over the SAME store dir
    sib_rows = sibling.list_runs(limit=999)["runs"]
    check("4 the sibling Suite sees ALL runs (incl. t3) from the shared log, not the first Suite's RAM",
          {"run://t1/ground", "run://t2/recall", "run://t3/ground"} <=
          {r["address"] for r in sib_rows})

print(f"\nALL {PASS} CHECKS PASS — the run index is INCREMENTAL (delta-fold, not full-reparse), "
      f"correctness-equal to a cold scan, event-count total_records, cross-process-rebuildable.")
