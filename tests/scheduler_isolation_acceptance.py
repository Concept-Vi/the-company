"""Acceptance — per-node error isolation in the scheduler, hardening FIX 2.

Prior code called mod.run(...) with NO try/except: one node raising aborted the WHOLE run, and the
declared node_record Status "failed" was never emitted (unreachable). This proves:
  1. one node's run() raising does NOT abort the run — independent ready nodes STILL run;
  2. the raising node is reported in result["failed"] with its error message captured (fail-loud);
  3. the failed node writes NO output ref (downstream inputs never resolve);
  4. its downstream stays unresolved → classified `stuck`, NOT mis-reported as ran/failed;
  5. the failure is SURFACED on the run result (a `failed` map) so callers can act — containment,
     not silent swallowing;
  6. a graph with NO failures behaves EXACTLY as before (failed == {}, ran/skipped unchanged).

Built on the REAL store + REAL scheduler, no AI. Inline node-types (module-shaped objects) so we can
declare a deterministically-raising type alongside a passing one in the same graph.

Run: python3 tests/scheduler_isolation_acceptance.py
"""
import os
import shutil
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.shapes import NodeInstance, Edge, Graph   # noqa: E402
from store.fs_store import FsStore                        # noqa: E402
from runtime import scheduler                             # noqa: E402

STORE_DIR = "/tmp/company-scheduler-isolation-store"


# --- inline node-types (a module-shaped object satisfies the scheduler's getattr access) ---
def _const(value):
    return types.SimpleNamespace(
        VERSION="1", PORTS_IN={}, PORTS_OUT={"value": "Any"},
        run=lambda inputs, config, _v=value: _v,
    )

GOOD = types.SimpleNamespace(   # passes input straight through (one input port)
    VERSION="1", PORTS_IN={"text": "Text"}, PORTS_OUT={"out": "Text"},
    run=lambda inputs, config: str(inputs.get("text", "")) + "!",
)

def _boom(inputs, config):
    raise RuntimeError("node deliberately exploded")

BOOM = types.SimpleNamespace(   # always raises in run()
    VERSION="1", PORTS_IN={"text": "Text"}, PORTS_OUT={"out": "Text"},
    run=_boom,
)

DOWNSTREAM = types.SimpleNamespace(   # downstream of BOOM — its input never resolves
    VERSION="1", PORTS_IN={"text": "Text"}, PORTS_OUT={"out": "Text"},
    run=lambda inputs, config: "should-never-run",
)

NODE_TYPES = {
    "src_a": _const("alpha"),     # feeds the independent GOOD branch
    "src_b": _const("beta"),      # feeds the BOOM branch
    "good": GOOD,
    "boom": BOOM,
    "downstream": DOWNSTREAM,
}


def build_graph():
    # Two independent branches:
    #   src_a -> good            (must complete)
    #   src_b -> boom -> downstream   (boom fails; downstream waits forever)
    return Graph(
        id="iso",
        nodes=[
            NodeInstance(id="src_a", type="src_a"),
            NodeInstance(id="src_b", type="src_b"),
            NodeInstance(id="good", type="good"),
            NodeInstance(id="boom", type="boom"),
            NodeInstance(id="downstream", type="downstream"),
        ],
        edges=[
            Edge(from_node="src_a", from_port="value", to_node="good", to_port="text"),
            Edge(from_node="src_b", from_port="value", to_node="boom", to_port="text"),
            Edge(from_node="boom", from_port="out", to_node="downstream", to_port="text"),
        ],
    )


def output_of(store, node_id):
    cas = store.head(f"run://iso/{node_id}")
    return store.get_content(cas) if cas else None


def _check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    return cond


def main():
    shutil.rmtree(STORE_DIR, ignore_errors=True)
    store = FsStore(STORE_DIR)
    g = build_graph()
    ok = True

    # The run must COMPLETE (not raise) even though `boom` raises inside run().
    raised = None
    try:
        r = scheduler.run(g, store, NODE_TYPES)
    except Exception as e:                       # noqa: BLE001 — the whole point is it must NOT raise
        raised = e
        r = None
    ok &= _check("run COMPLETES despite a node raising (no propagated abort)", raised is None)

    if r is not None:
        # 1: the independent branch STILL ran to completion.
        ok &= _check("independent node ran (src_a, good)",
                     {"src_a", "good"} <= r["ran"] and output_of(store, "good") == "alpha!")

        # 2: the raising node is reported FAILED with its error captured (fail-loud, legible).
        f = r.get("failed", {})
        ok &= _check("boom is in result['failed'] with its error captured",
                     "boom" in f and "RuntimeError" in f["boom"] and "exploded" in f["boom"])

        # 3: the failed node wrote NO output ref.
        ok &= _check("failed node wrote NO output ref", output_of(store, "boom") is None)

        # 4: failed node appears ONLY in `failed` — not ran/skipped/stuck.
        ok &= _check("failed node not in ran/skipped/stuck",
                     "boom" not in r["ran"] and "boom" not in r["skipped"]
                     and "boom" not in r["stuck"])

        # 5: downstream-of-failed stays UNRESOLVED → classified stuck (its input never resolved).
        ok &= _check("downstream of failed is stuck + unresolved",
                     "downstream" in r["stuck"] and output_of(store, "downstream") is None)

        # 6: src_b (feeds boom) ran fine — only boom itself failed.
        ok &= _check("upstream of the failing node still ran", "src_b" in r["ran"])

    # 7: a graph with NO failures behaves EXACTLY as before — failed is empty, normal sets intact.
    shutil.rmtree(STORE_DIR, ignore_errors=True)
    store2 = FsStore(STORE_DIR)
    clean = Graph(
        id="clean",
        nodes=[NodeInstance(id="s", type="src_a"), NodeInstance(id="g", type="good")],
        edges=[Edge(from_node="s", from_port="value", to_node="g", to_port="text")],
    )
    rc = scheduler.run(clean, store2, {"src_a": _const("hi"), "good": GOOD})
    ok &= _check("non-failing run: failed is empty + ran is full + no stuck",
                 rc["failed"] == {} and rc["ran"] == {"s", "g"} and not rc["stuck"])

    print("\n" + ("✅ SCHEDULER ISOLATION PASSED" if ok else "❌ FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
