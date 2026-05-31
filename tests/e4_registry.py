"""E4 — the live node-type registry (C2/S4/C5). TDD: RED before runtime/registry.py exists.

Acceptance: node-types are DISCOVERED (not a hardcoded dict); the registry is a queryable
type-graph; /object_info is served from it; and DROPPING A NEW NODE FILE makes it appear,
be queryable, and run — with NO edit to the runtime. That is the self-extending property.
Run: .venv/bin/python tests/e4_registry.py
"""
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.node_record import NodeInstance, Edge, Graph
from store.fs_store import FsStore
from runtime import scheduler
from runtime.registry import NodeRegistry

NODES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes")
ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def main():
    reg = NodeRegistry()
    reg.discover([NODES_DIR])

    # discovered the existing library
    check("discovers the node library (constant, uppercase, join, pair, llm)",
          {"constant", "uppercase", "join", "pair", "llm"} <= set(reg.types))

    # queryable type-graph: what produces 'Text'?
    producers = set(reg.produces("Text"))
    check("type-graph query: produces('Text') incl uppercase/join/pair",
          {"uppercase", "join", "pair"} <= producers)

    # object_info served from the registry (C5), with C2 fields
    oi = reg.object_info()
    check("object_info has C2 fields per type",
          "llm" in oi and "render_set" in oi["llm"] and "ports" in oi["llm"])

    # registry is usable AS node_types for the runtime (dict-like)
    store = FsStore(tempfile.mkdtemp())
    g = Graph(id="r", nodes=[
        NodeInstance(id="c", type="constant", config={"value": "hi"}),
        NodeInstance(id="u", type="uppercase"),
    ], edges=[Edge(from_node="c", from_port="value", to_node="u", to_port="text")])
    res = scheduler.run(g, store, reg)        # pass the registry where node_types went
    check("runtime runs a graph via the registry",
          res["ran"] == {"c", "u"} and store.get_content(store.head("run://r/u")) == "HI")

    # ⭐ drop a NEW node file -> appears + queryable + runs, with NO runtime edit
    tmp = tempfile.mkdtemp()
    with open(os.path.join(tmp, "shout.py"), "w") as f:
        f.write('VERSION="1"\nKIND="process"\nPORTS_IN={"text":"Text"}\nPORTS_OUT={"text":"Text"}\n'
                'def run(inputs, config):\n    return str(inputs.get("text",""))+"!!!"\n')
    reg2 = NodeRegistry()
    reg2.discover([NODES_DIR, tmp])
    check("new node 'shout' self-registers + is queryable",
          "shout" in reg2.types and "shout" in reg2.produces("Text"))
    store2 = FsStore(tempfile.mkdtemp())
    g2 = Graph(id="s", nodes=[
        NodeInstance(id="c", type="constant", config={"value": "go"}),
        NodeInstance(id="s", type="shout"),
    ], edges=[Edge(from_node="c", from_port="value", to_node="s", to_port="text")])
    res2 = scheduler.run(g2, store2, reg2)
    check("new node runs with NO runtime edit (-> 'go!!!')",
          "s" in res2["ran"] and store2.get_content(store2.head("run://s/s")) == "go!!!")

    print("\n" + ("✅ E4 REGISTRY PASSED" if ok else "❌ RED (registry not built)"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
