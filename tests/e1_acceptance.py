"""E1 acceptance — the typed spine + all contracts compose, with the store hardened.

Asserts the stage's acceptance:
  - store: put/get/exists/set_ref/head round-trip
  - provenance lineage walks back to source
  - memo: re-run skips
  - every contract (C1–C8) imports and its key models validate / functions work

Run: .venv/bin/python tests/e1_acceptance.py
"""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from contracts.address import Provenance, run_address                 # C1
from contracts.node_type import NodeType, Ports                       # C2
from contracts.node_record import NodeInstance, Edge, Graph, ExecNode  # C3
from contracts import resolver                                        # C4 (Protocol)
from contracts.object_info import build_object_info                   # C5
from runtime.compile import compile as compile_graph                  # C5
from runtime import context_variables as cv                           # C6
from contracts import tools                                           # C7
from contracts import bridge_msgs as bm                               # C8
from store.fs_store import FsStore
from runtime import scheduler
from nodes import constant, uppercase

NODE_TYPES = {"constant": constant, "uppercase": uppercase}
STORE_DIR = "/tmp/company-e1-store"
ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def main():
    shutil.rmtree(STORE_DIR, ignore_errors=True)
    store = FsStore(STORE_DIR)

    # C4 store: round-trips + Protocol conformance
    cas = store.put_content({"hi": 1})
    check("store round-trip (put/get/exists)",
          store.get_content(cas) == {"hi": 1} and store.exists(cas))
    store.set_ref("run://t/x", cas)
    check("store ref (set/head)", store.head("run://t/x") == cas)
    check("FsStore conforms to Resolver Protocol", isinstance(store, resolver.Resolver))

    # run the demo chain
    g = Graph(id="demo", nodes=[
        NodeInstance(id="src", type="constant", config={"value": "hello"}),
        NodeInstance(id="up", type="uppercase"),
    ], edges=[Edge(from_node="src", from_port="value", to_node="up", to_port="text")])
    r1 = scheduler.run(g, store, NODE_TYPES)
    check("chain ran; result HELLO",
          r1["ran"] == {"src", "up"}
          and store.get_content(store.head("run://demo/up")) == "HELLO")

    # provenance lineage walks to source
    lin = store.lineage("run://demo/up")
    src_prov = store.provenance("run://demo/src")
    check("lineage walks up -> src (and src is source: no inputs)",
          "run://demo/src" in lin and src_prov is not None and src_prov.inputs == [])

    # memo: re-run skips
    r2 = scheduler.run(g, store, NODE_TYPES)
    check("memo: re-run executes nothing", r2["ran"] == set() and r2["skipped"] == {"src", "up"})

    # C1 helpers
    check("C1 run_address", run_address("g", "n").startswith("run://g/n@main")
          and Provenance(address="a", content_hash="c", produced_by="a").schema_ver == 1)

    # C2 + C5 object_info
    nt = NodeType(name="extract", kind="process",
                  ports=Ports(inputs={"sessions": "SessionList"}, outputs={"decisions": "DecisionList"}))
    oi = build_object_info({"extract": nt})
    check("C5 object_info serializes a NodeType",
          "extract" in oi and oi["extract"]["render_set"] and oi["extract"]["ports"]["inputs"])

    # C5 compile: workflow -> execution with address-refs
    execs = compile_graph(g)
    up = next(e for e in execs if e.id == "up")
    check("C5 compile -> ExecNodes; input is an address-ref",
          len(execs) == 2 and up.inputs.get("text") == "run://demo/src" and isinstance(up, ExecNode))

    # C6 context resolves per turn
    ctx = cv.TurnContext(graph=g, selection=["up"], recent=[])
    res = cv.resolve_context(ctx, ["selection", "run_state", "recall_slice"])
    check("C6 context-variables resolve (recall empty until corpus exists)",
          set(res) == {"selection", "run_state", "recall_slice"} and res["recall_slice"] == [])

    # C7 generic tools: registry well-formed, no per-type tool
    from pydantic import BaseModel
    allnames = " ".join(tools.TOOLS).lower()
    check("C7 tools are generic verbs (registry valid; no per-node-type tool)",
          len(tools.TOOLS) >= 20
          and all(issubclass(t.params_model, BaseModel) for t in tools.TOOLS.values())
          and "extract" not in allnames and "document" not in allnames)

    # C8 bridge messages round-trip; errors are representable (fail loud)
    rt = bm.ActionResponse.model_validate_json(bm.err("1", "boom").model_dump_json())
    check("C8 bridge msgs round-trip; error survives the wire",
          rt.ok is False and rt.error == "boom")

    print("\n" + ("✅ E1 ACCEPTANCE PASSED — typed spine + C1–C8 compose" if ok else "❌ E1 FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
