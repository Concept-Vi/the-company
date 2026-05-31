"""E2 — the real runtime: compile in the run path, larger/branching graphs,
and pause / retry / branch as addressing operations.

TDD: written before the E2 scheduler changes exist. Expected RED until E2 is built.
Run: .venv/bin/python tests/e2_runtime.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.node_record import NodeInstance, Edge, Graph
from store.fs_store import FsStore
from runtime import scheduler
from nodes import constant, uppercase, join

NODE_TYPES = {"constant": constant, "uppercase": uppercase, "join": join}
STORE = "/tmp/company-e2-store"
ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def fanin(a="A", b="B"):
    # c1 ─┐
    #     join → joined
    # c2 ─┘
    return Graph(id="g2", nodes=[
        NodeInstance(id="c1", type="constant", config={"value": a}),
        NodeInstance(id="c2", type="constant", config={"value": b}),
        NodeInstance(id="j", type="join"),
    ], edges=[
        Edge(from_node="c1", from_port="value", to_node="j", to_port="a"),
        Edge(from_node="c2", from_port="value", to_node="j", to_port="b"),
    ])


def out(store, nid, branch="main"):
    addr = f"run://g2/{nid}" if branch == "main" else f"run://g2/{nid}@{branch}"
    cas = store.head(addr)
    return store.get_content(cas) if cas else None


def main():
    shutil.rmtree(STORE, ignore_errors=True)
    store = FsStore(STORE)
    g = fanin("A", "B")

    # 1: fan-in fires reactively; join only after BOTH constants resolve; correct result
    r = scheduler.run(g, store, NODE_TYPES)
    check("fan-in: all three ran, join after both inputs resolved, result 'A|B'",
          r["ran"] == {"c1", "c2", "j"} and not r["stuck"] and out(store, "j") == "A|B")

    # 2: compile is in the run path (the run produced an execution form)
    check("compile() is wired into the run path",
          r.get("compiled") == 3)   # 3 ExecNodes were compiled+executed

    # 3: change-propagation exact on the bigger graph — change c1 only
    g2 = fanin("X", "B")
    r2 = scheduler.run(g2, store, NODE_TYPES)
    check("change-propagation: only c1 + j re-run; c2 cached",
          r2["ran"] == {"c1", "j"} and r2["skipped"] == {"c2"} and out(store, "j") == "X|B")

    # 4: pause — hold 'j'; c1/c2 run, j held, joined not produced; then resume completes
    shutil.rmtree(STORE, ignore_errors=True); store = FsStore(STORE)
    rp = scheduler.run(g, store, NODE_TYPES, pause={"j"})
    check("pause: held node not run; upstream did; output absent",
          "j" not in rp["ran"] and {"c1", "c2"} <= rp["ran"] and out(store, "j") is None)
    rr = scheduler.run(g, store, NODE_TYPES)   # resume (no pause)
    check("resume: held node completes, upstream skipped (memo)",
          rr["ran"] == {"j"} and rr["skipped"] == {"c1", "c2"} and out(store, "j") == "A|B")

    # 5: retry — force re-run of j; c1/c2 cached, j re-runs
    rt = scheduler.run(g, store, NODE_TYPES, force={"j"})
    check("retry (force): j re-runs, inputs cached",
          rt["ran"] == {"j"} and rt["skipped"] == {"c1", "c2"})

    # 6: branch — run a changed graph on @exp; @main and @exp coexist, different outputs
    gx = fanin("A", "Z")
    scheduler.run(gx, store, NODE_TYPES, branch="exp")
    check("branch: @main and @exp coexist with different outputs",
          out(store, "j", "main") == "A|B" and out(store, "j", "exp") == "A|Z")

    print("\n" + ("✅ E2 RUNTIME PASSED" if ok else "❌ E2 (expected RED until built)"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
