"""tests/agency_acceptance.py — symmetric agency + NL→graph (slice 5, G2+G3).

Two planes, one state (context-05), write direction: the RHM can do what the operator can on
the canvas — compose a typed pipeline (add nodes + wire them) via the `build` verb. build is
AUTO (create_node + connect — reversible, exactly the operator's palette/wire), and the whitelist
stays {run, propose, build}: still NO path to apply/delete/file-write. NL→graph is proven by use.
"""
import os, sys, tempfile, shutil, json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite

NODES = os.path.join(ROOT, "nodes")
PASS = 0


def check(label, cond):
    global PASS
    assert cond, f"FAIL: {label}"
    PASS += 1
    print(f"  ok  {label}")


store_dir = tempfile.mkdtemp(prefix="agency-test-")
try:
    store = FsStore(os.path.join(store_dir, "store"))
    reg = NodeRegistry(); reg.discover([NODES])
    suite = Suite(store, reg, nodes_dir=NODES)
    g = "agency"

    # NATIVE-TOOL-CALL path (the one the live chat() uses): a `build` tool_call → action dict via the
    # SAME _json_obj_to_action the chat loop feeds each tool_call through. The model supplies the typed
    # pipeline as the tool's `steps` argument (a JSON list); the args envelope is a JSON STRING as the
    # API returns it. (Was: the retired `ACTION: build <json>` prose-parse + ACTION-line stripping.)
    steps = [{"as": "a", "type": "constant", "config": {"value": "hi"}},
             {"as": "b", "type": "uppercase"}, {"wire": "a.value -> b.text"}]
    act = suite._json_obj_to_action(
        {"name": "build", "arguments": json.dumps({"steps": steps})}, "build")
    check("build tool_call → action dict with the 3 steps", act["verb"] == "build" and len(act["steps"]) == 3)

    # dispatch build → composes the pipeline on the canvas (symmetric agency)
    r = suite._dispatch_rhm_action(act, g)
    check("build created the nodes", r["did"] == "build" and len(r["nodes"]) == 2)
    gg = suite._load(g)
    check("two nodes exist on the graph", len(gg.nodes) == 2)
    check("the wire was made (by local 'as' names → real ids)", len(gg.edges) == 1)

    # the built pipeline actually RUNS and produces the right result (it's real, not a stub)
    suite.run(g)
    st = {n["id"]: n for n in suite.state(g)["nodes"]}
    up = next(n for n in st.values() if n["type"] == "uppercase")
    check("the RHM-built pipeline computes correctly (hi → HI)", up["output"] == "HI")

    # build is AUTO — no surfaced approval gate was created (it's reversible composition)
    check("build did NOT surface an approval (it's AUTO)", len(suite.list_surfaced()) == 0)

    # THE invariant still holds: build only adds/wires; apply/delete/write remain unreachable
    snap = set(os.listdir(NODES))
    check("apply still refused", suite._dispatch_rhm_action({"verb": "apply", "id": "x"}, g)["did"] == "none")
    check("delete still refused", suite._dispatch_rhm_action({"verb": "delete", "node": "a"}, g)["did"] == "none")
    check("no node file written by refused verbs", set(os.listdir(NODES)) == snap)

    # a malformed build fails loud (no silent half-build claim)
    bad = suite._dispatch_rhm_action({"verb": "build", "steps": [{"type": "nonexistent_type"}]}, g)
    check("build with an unknown type reports an error (no silent success)", "error" in bad)

    print(f"\nALL {PASS} CHECKS PASS — symmetric agency: RHM composes runnable pipelines; gate intact")
finally:
    shutil.rmtree(store_dir, ignore_errors=True)
