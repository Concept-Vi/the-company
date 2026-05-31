"""mcp_face/server.py — the agent face (C7). FastMCP exposing the generic verbs over the
shared Suite. Same brain + same substrate as the UI bridge (runtime.suite.Suite). See mcp_face/AGENTS.md.

(Dir is `mcp_face`, not `mcp`, to avoid colliding with the installed `mcp` SDK package.)
Verbs are GENERIC over node-type — adding a node-type adds zero tools.
"""
from __future__ import annotations
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP          # the SDK (site-packages)
from store.fs_store import FsStore
from runtime.registry import NodeRegistry
from runtime.suite import Suite
from fabric import config as fcfg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUITE = Suite(FsStore(fcfg.STORE_DIR),
              NodeRegistry().discover([os.path.join(ROOT, "nodes")]))

mcp = FastMCP("company")


@mcp.tool()
def list_types() -> list:
    """List every registered node-type (process · content · presentation)."""
    return SUITE.list_types()


@mcp.tool()
def object_info() -> dict:
    """The full node-type library (ports · render-set · config) for rendering/composition."""
    return SUITE.object_info()


@mcp.tool()
def list_by_type(output_type: str) -> list:
    """Type-graph query: which node-types PRODUCE a given port-type."""
    return SUITE.list_by_type(output_type)


@mcp.tool()
def list_graphs() -> list:
    """List all graphs (canvases) in the substrate."""
    return SUITE.list_graphs()


@mcp.tool()
def create_node(graph: str, type: str, config: dict = {}, node_id: str = "") -> str:
    """Add a node of `type` to `graph` (GENERIC — works for any registered type). Returns its id."""
    return SUITE.create_node(graph, type, dict(config), node_id or None)


@mcp.tool()
def connect(graph: str, from_node: str, from_port: str, to_node: str, to_port: str) -> str:
    """Wire from_node.from_port -> to_node.to_port in `graph`."""
    SUITE.connect(graph, from_node, from_port, to_node, to_port)
    return "ok"


@mcp.tool()
def set_config(graph: str, node: str, config: dict) -> str:
    """Update a node's config in `graph`."""
    SUITE.set_config(graph, node, dict(config))
    return "ok"


@mcp.tool()
def run_graph(graph: str, branch: str = "main") -> dict:
    """Run `graph`; returns which nodes ran vs were cached (memo)."""
    r = SUITE.run(graph, branch=branch)
    return {"ran": sorted(r["ran"]), "cached": sorted(r["skipped"]), "stuck": r["stuck"]}


@mcp.tool()
def get_state(graph: str) -> dict:
    """Current state of `graph`: nodes, statuses, outputs, addresses."""
    return SUITE.state(graph)


@mcp.tool()
def get_results(graph: str) -> dict:
    """The output of each node in `graph`."""
    return SUITE.results(graph)


if __name__ == "__main__":
    mcp.run(transport="stdio")
