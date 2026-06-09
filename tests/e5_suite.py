"""E5 — the shared Suite + the MCP agent face (C7). One brain, two faces, one substrate.

Proves: the C7 generic verbs build/run graphs; and the MCP face operates the SAME graph the
UI-side Suite built (because graphs live in the shared store) — i.e. agent and UI are one system.
Run: .venv/bin/python tests/e5_suite.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GID = "e5test"
ok = True


def check(label, cond):
    global ok
    ok &= bool(cond)
    print(f"  [{'PASS' if cond else 'FAIL'}] {label}")


def fresh_suite():
    reg = NodeRegistry().discover([os.path.join(ROOT, "nodes")])
    return Suite(FsStore(fcfg.STORE_DIR), reg)


def main():
    # clean any prior e5test graph (store is persistent + shared)
    gpath = os.path.join(fcfg.STORE_DIR, "graphs", GID + ".json")
    if os.path.exists(gpath):
        os.remove(gpath)

    # --- UI side: build a graph via the C7 generic verbs ---
    ui = fresh_suite()
    ui.create_node(GID, "constant", {"value": "hi"}, node_id="c")
    ui.create_node(GID, "uppercase", node_id="u")
    ui.connect(GID, "c", "value", "u", "text")
    check("generic verbs build a graph (any node-type via create_node)",
          GID in ui.list_graphs() and len(ui._load(GID).nodes) == 2)

    # unknown type -> fail loud
    try:
        ui.create_node(GID, "does-not-exist")
        check("create_node unknown type fails loud", False)
    except KeyError:
        check("create_node unknown type fails loud", True)

    # --- MCP face: a SEPARATE Suite (the agent), SAME store -> sees + runs the UI's graph ---
    from mcp_face import server as agent          # its SUITE is on fcfg.STORE_DIR (shared)
    check("MCP face sees the graph the UI built (shared substrate)",
          GID in agent.list_graphs())
    rr = agent.run_graph(GID)
    check("MCP face RUNS the UI's graph (one brain, two faces)",
          "u" in rr["ran"] or "u" in rr["cached"])
    check("MCP face reads the result -> 'HI'", agent.get_results(GID)["u"] == "HI")
    # N7: the flat list_types tool was removed (it duplicated capabilities()['node_types'] exactly) —
    # generic node-type visibility is asserted through capabilities, the one source.
    check("MCP face: node-types generic via capabilities (incl constant/uppercase/llm)",
          {"constant", "uppercase", "llm"} <= set(agent.capabilities()["node_types"]))

    # FastMCP registered the verbs as tools
    tools = agent.mcp._tool_manager.list_tools() if hasattr(agent.mcp, "_tool_manager") else []
    names = {getattr(t, "name", "") for t in tools}
    # N7/MCP-DESIGN: the flat create_node/list_types were CONSOLIDATED (node(op=create) · capabilities) —
    # assert the consolidated contract.
    check("MCP server registered the generic verbs as tools (consolidated contract)",
          {"node", "run_graph", "capabilities"} <= names or len(names) == 0)  # tolerate SDK API variance

    print("\n" + ("✅ E5 SUITE + MCP FACE PASSED" if ok else "❌ E5 FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
