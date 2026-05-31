"""SELF-GROWTH — the system writes itself a new capability from a request, and runs it.

The "direct its growth" half of the first purpose: build-dispatch, GOVERNED correctly:
  - the agent PROPOSES (brain writes a node) -> surfaced as a CONFIRM decision (not applied);
  - the agent CANNOT self-approve (apply without operator approval fails loud);
  - path-traversal names are rejected (no write outside the node library);
  - the OPERATOR approves (a channel the agent doesn't have) -> apply writes + auto-discovers;
  - the self-written capability RUNS correctly.
Live (real model). Writes to a TEMP nodes dir (not the repo), so the proof has no side effects.
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
from runtime import governance as gov, scheduler
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

    # path-traversal names are rejected up front (no model call, no write)
    traversed = False
    try:
        suite.propose_node("../runtime/scheduler", "malicious")
    except ValueError:
        traversed = True
    check("path-traversal node name rejected (can't escape the library / clobber modules)",
          traversed and not os.path.exists(os.path.join(ROOT, "runtime", "scheduler.py.tmp")))

    # 1: the agent PROPOSES — brain writes the node, surfaced (NOT applied)
    prop = suite.propose_node("reverse", "return the input string reversed (e.g. 'abc' -> 'cba')")
    check("brain wrote a node + it was surfaced for the operator (not applied)",
          "def run" in prop["code"] and "reverse" not in reg.types and prop["id"])

    # 2: the agent CANNOT self-approve — apply without operator approval fails loud
    blocked = False
    try:
        suite.apply_node(prop["id"])
    except gov.GovernanceError:
        blocked = True
    check("agent cannot self-approve: apply before operator approval fails loud",
          blocked and "reverse" not in reg.types)

    # 3: the OPERATOR approves (a channel the agent doesn't have on the MCP face)
    suite.resolve_surfaced(prop["id"], "approve")
    suite.apply_node(prop["id"])
    check("after OPERATOR approval: new capability written + auto-discovered", "reverse" in reg.types)

    # 4: the self-written capability RUNS correctly
    store2 = FsStore(tempfile.mkdtemp())
    g = Graph(id="sg", nodes=[
        NodeInstance(id="c", type="constant", config={"value": "hello"}),
        NodeInstance(id="r", type="reverse"),
    ], edges=[Edge(from_node="c", from_port="value", to_node="r", to_port="text")])
    res = scheduler.run(g, store2, reg)
    out = store2.get_content(store2.head("run://sg/r")) if store2.head("run://sg/r") else None
    check("the self-written node RUNS correctly ('hello' -> 'olleh')",
          "r" in res["ran"] and out == "olleh")
    print(f"      (agent proposed 'reverse'; operator approved; it ran: 'hello' -> {out!r})")

    print("\n" + ("✅ SELF-GROWTH PROVEN — system grows its own capability from a request, governed"
                  if ok else "❌ SELF-GROWTH FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
