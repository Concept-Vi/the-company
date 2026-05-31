"""SELF-GROWTH — the system writes itself a new capability from a request, and runs it.

The "direct its growth" half of the first purpose: build-dispatch. The brain writes a new
node module; governance gates the apply (code_build = CONFIRM); on confirm it's written +
auto-discovered; then it RUNS. Proven end-to-end. Live (real model). Writes to a TEMP nodes
dir (not the repo) so the proof has no side effects.
Run: .venv/bin/python tests/self_growth.py
"""
import os
import sys
import tempfile
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.node_record import NodeInstance, Edge, Graph
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from runtime import governance as gov
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_NODES = os.path.join(ROOT, "nodes")
ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def main():
    try:
        urllib.request.urlopen(fcfg.OLLAMA_DIRECT.replace("/v1", "") + "/v1/models", timeout=4)
    except Exception:
        print("  [FAIL] ollama not reachable — cannot run the live self-growth test")
        return 1

    tmp_nodes = tempfile.mkdtemp()
    reg = NodeRegistry().discover([BASE_NODES])
    suite = Suite(FsStore(tempfile.mkdtemp()), reg, nodes_dir=tmp_nodes)

    # 1: the system PROPOSES a new node (the brain writes it)
    prop = suite.propose_node("reverse", "return the input string reversed (e.g. 'abc' -> 'cba')")
    check("brain wrote a node module (has run() + ports)",
          "def run" in prop["code"] and "PORTS_OUT" in prop["code"])

    # 2: applying is CONFIRM-gated (code_build) — without confirmation it fails loud + surfaces
    gated = False
    try:
        suite.apply_node("reverse", prop["code"], confirmed=False)
    except gov.GovernanceError:
        gated = True
    check("apply is CONFIRM-gated (surfaced, not silently applied)",
          gated and "reverse" not in reg.types and len(suite.list_surfaced()) >= 1)

    # 3: on confirmation, the system writes the node into itself + auto-discovers it
    suite.apply_node("reverse", prop["code"], confirmed=True)
    check("on confirm: new capability written + auto-discovered", "reverse" in reg.types)

    # 4: the self-written capability RUNS correctly
    store2 = FsStore(tempfile.mkdtemp())
    g = Graph(id="sg", nodes=[
        NodeInstance(id="c", type="constant", config={"value": "hello"}),
        NodeInstance(id="r", type="reverse"),
    ], edges=[Edge(from_node="c", from_port="value", to_node="r", to_port="text")])
    from runtime import scheduler
    res = scheduler.run(g, store2, reg)
    out = store2.get_content(store2.head("run://sg/r")) if store2.head("run://sg/r") else None
    check("the self-written node RUNS correctly ('hello' -> 'olleh')",
          "r" in res["ran"] and out == "olleh")
    print(f"      (system wrote node 'reverse'; ran it: 'hello' -> {out!r})")

    print("\n" + ("✅ SELF-GROWTH PROVEN — the system grew its own capability from a request"
                  if ok else "❌ SELF-GROWTH FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
