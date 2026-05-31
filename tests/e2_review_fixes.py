"""Regression tests for the 3 findings from the E2 adversarial review.

TDD: written to FAIL on the buggy E2 runtime (reproduce the bugs), then drive the fix.
  B1 — memo sig must capture port->input binding (non-commutative node)
  B2 — memo-skip path must still write provenance (lineage to source)
  S1 — a node with a declared-but-unwired input must NOT fire (it waits)
Run: .venv/bin/python tests/e2_review_fixes.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.node_record import NodeInstance, Edge, Graph
from store.fs_store import FsStore
from runtime import scheduler
from nodes import constant, uppercase, pair

NT = {"constant": constant, "uppercase": uppercase, "pair": pair}
STORE = "/tmp/company-e2fix-store"
ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def pair_graph(av, bv):
    return Graph(id="gp", nodes=[
        NodeInstance(id="ca", type="constant", config={"value": av}),
        NodeInstance(id="cb", type="constant", config={"value": bv}),
        NodeInstance(id="p", type="pair"),
    ], edges=[
        Edge(from_node="ca", from_port="value", to_node="p", to_port="a"),
        Edge(from_node="cb", from_port="value", to_node="p", to_port="b"),
    ])


def out(store, addr):
    cas = store.head(addr)
    return store.get_content(cas) if cas else None


def main():
    # B1 — swapped ports, same content set, must NOT memo-collide
    shutil.rmtree(STORE, ignore_errors=True); store = FsStore(STORE)
    scheduler.run(pair_graph("X", "Y"), store, NT)
    check("B1: first run a=X,b=Y -> 'X>Y'", out(store, "run://gp/p") == "X>Y")
    scheduler.run(pair_graph("Y", "X"), store, NT)   # a=Y, b=X — same hashes, swapped ports
    check("B1: swapped a=Y,b=X -> 'Y>X' (memo must be port-aware)",
          out(store, "run://gp/p") == "Y>X")

    # B2 — a branch resolved entirely via memo must still have provenance + lineage
    shutil.rmtree(STORE, ignore_errors=True); store = FsStore(STORE)
    g = pair_graph("X", "Y")
    scheduler.run(g, store, NT, branch="main")
    scheduler.run(g, store, NT, branch="exp")        # all memo hits, never executes
    prov = store.provenance("run://gp/p@exp")
    lin = store.lineage("run://gp/p@exp")
    check("B2: memo-resolved branch node has provenance",
          prov is not None and prov.inputs == ["run://gp/ca@exp", "run://gp/cb@exp"])
    check("B2: lineage walks @exp node back to its sources",
          "run://gp/ca@exp" in lin and "run://gp/cb@exp" in lin)

    # S1 — a declared-but-unwired input must NOT fire (it waits / stuck), no empty output
    shutil.rmtree(STORE, ignore_errors=True); store = FsStore(STORE)
    lone = Graph(id="gl", nodes=[NodeInstance(id="u", type="uppercase")], edges=[])
    r = scheduler.run(lone, store, NT)
    check("S1: unwired-input node does not run (stuck), produces no output",
          "u" not in r["ran"] and "u" in r["stuck"] and out(store, "run://gl/u") is None)

    print("\n" + ("✅ E2 REVIEW-FIXES PASSED" if ok else "❌ RED (reproduces the review's findings)"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
