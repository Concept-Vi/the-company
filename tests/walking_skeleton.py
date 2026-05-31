"""Stage 0 acceptance — the walking skeleton (headless half).

Proves the spine end-to-end through the REAL store + REAL scheduler, no AI:
  1. reactive firing      — uppercase fires only after constant resolves
  2. correct result       — "hello" -> "HELLO" at its address
  3. memoise / re-run      — re-running with no change re-executes NOTHING
  4. change-propagation    — change one node's config -> it + downstream re-run, only those
  5. resume after restart  — a fresh process over the same store skips completed work

Run: python3 tests/walking_skeleton.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.shapes import NodeInstance, Edge, Graph   # noqa: E402
from store.fs_store import FsStore                        # noqa: E402
from runtime import scheduler                             # noqa: E402
from nodes import constant, uppercase                     # noqa: E402

NODE_TYPES = {"constant": constant, "uppercase": uppercase}
STORE_DIR = "/tmp/company-skeleton-store"


def build_graph(value):
    return Graph(
        id="demo",
        nodes=[
            NodeInstance(id="src", type="constant", config={"value": value}),
            NodeInstance(id="up", type="uppercase"),
        ],
        edges=[Edge(from_node="src", from_port="value", to_node="up", to_port="text")],
    )


def output_of(store, node_id):
    cas = store.head(f"run://demo/{node_id}")
    return store.get_content(cas) if cas else None


def main():
    shutil.rmtree(STORE_DIR, ignore_errors=True)   # clean slate
    store = FsStore(STORE_DIR)
    g = build_graph("hello")
    ok = True

    # 1+2: first run — both fire, correct result, dependency respected
    r1 = scheduler.run(g, store, NODE_TYPES)
    ok &= _check("reactive firing + result",
                 r1["ran"] == {"src", "up"} and not r1["stuck"]
                 and output_of(store, "up") == "HELLO")

    # 3: re-run, nothing changed -> nothing re-executes (pure memo hits)
    r2 = scheduler.run(g, store, NODE_TYPES)
    ok &= _check("memoise: unchanged re-run executes nothing",
                 r2["ran"] == set() and r2["skipped"] == {"src", "up"})

    # 4: change the source value -> src re-runs (new sig), up re-runs (new input)
    g2 = build_graph("world")
    r3 = scheduler.run(g2, store, NODE_TYPES)
    ok &= _check("change-propagation: only affected nodes re-run",
                 r3["ran"] == {"src", "up"} and output_of(store, "up") == "WORLD")

    # 5: resume — a brand-new store object (fresh 'process') over the same dir skips done work
    store_fresh = FsStore(STORE_DIR)
    r4 = scheduler.run(g2, store_fresh, NODE_TYPES)
    ok &= _check("resume after restart: completed work is skipped",
                 r4["ran"] == set() and r4["skipped"] == {"src", "up"}
                 and output_of(store_fresh, "up") == "WORLD")

    print("\n" + ("✅ WALKING SKELETON (headless) PASSED" if ok else "❌ FAILED"))
    return 0 if ok else 1


def _check(label, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")
    return cond


if __name__ == "__main__":
    sys.exit(main())
